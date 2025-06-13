from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status, Depends

from dishka import AsyncContainer

from skill_tracker.db_access.models import TaskStatusEnum
from skill_tracker.services.task_service import TaskService, OnlyManagerCanCreateTaskError, TaskCreateDTO, TaskUpdateDTO, OnlyManagerCanUpdateTaskError, OnlyManagerCanDeleteTaskError, OnlyEmployeeCanBeAttachedToTask
from skill_tracker.metrics import (
    CREATE_TASK_METHOD_DURATION,
    GET_ALL_TASKS_METHOD_DURATION,
    measure_latency,
)
from fastapi_users import FastAPIUsers
from datetime import datetime
from typing import Optional
from skill_tracker.db_access.models import User

from pydantic import BaseModel, ConfigDict, FutureDatetime, Field


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    deadline: Optional[FutureDatetime] = None
    employee_id: UUID
    status: Optional[TaskStatusEnum] = TaskStatusEnum.pending
    progress: Optional[int] = Field(0, ge=0, le=100)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[FutureDatetime] = None
    status: Optional[TaskStatusEnum] = None
    progress: Optional[int] = Field(None, ge=0, le=100)


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    manager_id: UUID
    employee_id: UUID
    created_at: datetime
    deadline: datetime
    status: TaskStatusEnum
    progress: int


async def get_tasks_controller(container: AsyncContainer) -> APIRouter:
    router = APIRouter(route_class=DishkaRoute, tags=["tasks"], prefix="/api/v1")
    fastapi_users = await container.get(FastAPIUsers[User, UUID])


    @router.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
    @measure_latency(CREATE_TASK_METHOD_DURATION)
    async def create_task(
            task: TaskCreate,
            service: FromDishka[TaskService],
            user: User = Depends(fastapi_users.current_user(active=True))
    ):
        try:
            db_task = await service.create_task(
                caller=user,
                task=TaskCreateDTO(
                    title=task.title,
                    description=task.description,
                    employee_id=task.employee_id,
                    manager_id=user.id,
                    deadline=task.deadline,
                    status=task.status,
                    progress=task.progress
                )
            )
        except OnlyManagerCanCreateTaskError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except OnlyEmployeeCanBeAttachedToTask as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        return db_task

    @router.get("/tasks/{task_id}", response_model=TaskResponse)
    async def get_task(
            task_id: UUID,
            service: FromDishka[TaskService],
            user: User = Depends(fastapi_users.current_user(active=True))
    ):
        try:
            task = await service.get_task(task_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        return task

    @router.get("/tasks/")
    @measure_latency(GET_ALL_TASKS_METHOD_DURATION)
    async def get_tasks(
            service: FromDishka[TaskService],
            skip: int = 0,
            limit: int = 10,
            user: User = Depends(fastapi_users.current_user(active=True))
    ):
        res = await service.get_tasks(caller=user, skip=skip, limit=limit)
        return res


    @router.put("/tasks/{task_id}", response_model=TaskResponse)
    async def update_task(
            task_id: UUID,
            task_update: TaskUpdate,
            service: FromDishka[TaskService],
            user: User = Depends(fastapi_users.current_user(active=True))
    ):
        try:
            db_task = await service.update_task(user, task_id, TaskUpdateDTO(title=task_update.title, description=task_update.description, deadline=task_update.deadline, status=task_update.status, progress=task_update.progress))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except OnlyManagerCanUpdateTaskError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

        return db_task

    @router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_task(
            task_id: UUID,
            service: FromDishka[TaskService],
            user: User = Depends(fastapi_users.current_user(active=True))
    ):
        try:
            is_deleted = await service.delete_task(user, task_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except OnlyManagerCanDeleteTaskError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

        return None

    return router
