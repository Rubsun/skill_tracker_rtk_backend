from uuid import UUID

from dishka import AsyncContainer, FromDishka
from skill_tracker.services.user_service import UserService, OnlyManagerCanGetEmployeesError
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend

from skill_tracker.db_access.models import User
from skill_tracker.services.user_service import UserCreate, UserRead, UserUpdate


async def get_users_controller(container: AsyncContainer) -> APIRouter:
    router = APIRouter(route_class=DishkaRoute, prefix="/api/v1")

    auth_backend = await container.get(AuthenticationBackend[User, UUID])
    fastapi_users = await container.get(FastAPIUsers[User, UUID])


    router.include_router(
        fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
    )

    router.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )

    router.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/auth",
        tags=["auth"],
    )

    router.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix="/auth",
        tags=["auth"],
    )

    router.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )

    @router.get("/employees", tags=["employees"])
    async def get_employees(
            service: FromDishka[UserService],
            skip: int = 0,
            limit: int = 10,
            user: User = Depends(fastapi_users.current_user(active=True)),
    ):
        try:
            res = await service.get_employees(caller=user, skip=skip, limit=limit)
        except OnlyManagerCanGetEmployeesError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

        return res

    @router.get("/authenticated-route")
    async def authenticated_route(
        user: User = Depends(fastapi_users.current_user(active=True)),
    ):
        return {"message": f"Hello {user.email}!"}

    return router
