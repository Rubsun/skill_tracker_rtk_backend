from uuid import UUID

from dishka import AsyncContainer
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend

from skill_tracker.db_access.models import User
from skill_tracker.services.user_service import UserCreate, UserRead, UserUpdate


async def get_users_controller(container: AsyncContainer) -> APIRouter:
    router = APIRouter(route_class=DishkaRoute)

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

    @router.get("/authenticated-route")
    async def authenticated_route(
        user: User = Depends(fastapi_users.current_user(active=True)),
    ):
        return {"message": f"Hello {user.email}!"}

    return router
