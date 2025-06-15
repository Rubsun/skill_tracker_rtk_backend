from datetime import datetime
from typing import Optional
from uuid import UUID

from dishka import AsyncContainer, FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_users import FastAPIUsers
from pydantic import BaseModel, ConfigDict

from skill_tracker.db_access.models import User
from skill_tracker.services.comment_service import CommentCreateDTO, CommentService, CommentUpdateDTO


class CommentCreate(BaseModel):
    text: str
    task_id: UUID


class CommentUpdate(BaseModel):
    text: Optional[str] = None


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    created_at: datetime
    task_id: UUID
    user_id: UUID


async def get_comments_controller(container: AsyncContainer) -> APIRouter:
    router = APIRouter(route_class=DishkaRoute, tags=["comments"], prefix="/api/v1")
    fastapi_users = await container.get(FastAPIUsers[User, UUID])


    @router.post("/comments/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
    async def create_comment(
            comment: CommentCreate,
            service: FromDishka[CommentService],
            user: User = Depends(fastapi_users.current_user(active=True))
    ):
        try:
            db_comment = await service.create_comment(
                comment=CommentCreateDTO(
                    text=comment.text,
                    task_id=comment.task_id,
                    user_id=user.id,
                )
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        return db_comment

    @router.get("/comments/{comment_id}", response_model=CommentResponse)
    async def get_comment(
            comment_id: UUID,
            service: FromDishka[CommentService],
            user: User = Depends(fastapi_users.current_user(active=True))
    ):
        try:
            comment = await service.get_comment(comment_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        return comment

    @router.get("/comments/")
    async def get_comments(
            service: FromDishka[CommentService],
            task_id: UUID | None = None,
            skip: int = 0,
            limit: int = 10,
            user: User = Depends(fastapi_users.current_user(active=True))
    ):
        res = await service.get_comments(skip=skip, limit=limit, task_id=task_id)
        return res


    @router.put("/comment/{comment_id}", response_model=CommentResponse)
    async def update_comment(
            comment_id: UUID,
            comment_update: CommentUpdate,
            service: FromDishka[CommentService],
            user: User = Depends(fastapi_users.current_user(active=True)),
    ):
        try:
            db_comment = await service.update_comment(user, comment_id, CommentUpdateDTO(
                text=comment_update.text
            ))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

        return db_comment


    @router.delete("/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_comment(
            comment_id: UUID,
            service: FromDishka[CommentService],
            user: User = Depends(fastapi_users.current_user(active=True))
    ):
        try:
            await service.delete_comment(user, comment_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

        return None

    return router
