import uuid

from dishka import AsyncContainer, Scope
from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from skill_tracker.config import Config
from skill_tracker.db_access.models import User
from skill_tracker.depends_stub import Stub
from skill_tracker.services.user_service import UserGateway, UserManager


async def get_user_manager(container: AsyncContainer = Depends(Stub(AsyncContainer))) -> UserManager:
    cfg = await container.get(Config)
    async with container(scope=Scope.REQUEST) as request_container:
        repository = await request_container.get(UserGateway)
        return UserManager(repository.get_user_db(), cfg.auth.secret)


async def get_strategy(container: AsyncContainer = Depends(Stub(AsyncContainer))) -> JWTStrategy[User, uuid.UUID]:
    cfg = await container.get(Config)
    return JWTStrategy(secret=cfg.auth.secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="/api/v1/auth/jwt/login"),
    get_strategy=get_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    auth_backends=[auth_backend]
)
