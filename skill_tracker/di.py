import os
import uuid
from collections.abc import AsyncGenerator

from dishka import Provider, Scope, make_async_container, provide
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from skill_tracker.config import Config, load_config
from skill_tracker.db_access.models import User
from skill_tracker.db_access.repositories.comment_repository import CommentRepository
from skill_tracker.db_access.repositories.task_repository import TaskRepository
from skill_tracker.db_access.repositories.user_repository import UserRepository
from skill_tracker.services.comment_service import CommentGateway, CommentService
from skill_tracker.services.task_service import TaskGateway, TaskService
from skill_tracker.services.user_service import UserGateway, UserManager, UserService


def config_provider() -> Provider:
    provider = Provider()

    cfg_path = os.getenv('SKILL_TRACKER_CONFIG_PATH', './configs/app.toml')
    provider.provide(lambda: load_config(cfg_path), scope=Scope.APP, provides=Config)
    return provider



class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self, cfg: Config) -> AsyncEngine:
        return create_async_engine(cfg.db.uri, echo=True)

    @provide(scope=Scope.APP)
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(
            self,
            sessionmaker: async_sessionmaker
    ) -> AsyncGenerator[AsyncSession, None, None]:
        async with sessionmaker() as session:
            yield session


class TaskProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_task_gateway(self, session: AsyncSession) -> TaskGateway:
        return TaskRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_task_service(
            self,
            repository: TaskGateway,
            user_repository: UserGateway,
    ) -> TaskService:
        return TaskService(repository, user_repository)


class UserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_user_gateway(self, session: AsyncSession) -> UserGateway:
        return UserRepository(session)

    @provide(scope=Scope.APP)
    async def get_strategy(self, cfg: Config) -> JWTStrategy[User, uuid.UUID]:
        return JWTStrategy(secret=cfg.auth.secret, lifetime_seconds=3600)

    @provide(scope=Scope.APP)
    async def get_auth_backend(self, strategy: JWTStrategy[User, uuid.UUID]) -> AuthenticationBackend[User, uuid.UUID]:
        return AuthenticationBackend(
            name="jwt",
            transport=BearerTransport(tokenUrl="/api/v1/auth/jwt/login"),
            get_strategy=lambda: strategy,
        )

    @provide(scope=Scope.REQUEST)
    def get_user_manager(self, cfg: Config, repository: UserGateway) -> UserManager:
        return UserManager(repository.get_user_db(), cfg.auth.secret)

    @provide(scope=Scope.REQUEST)
    async def get_fastapi_users(
            self,
            user_manager: UserManager,
            auth_backend: AuthenticationBackend[User, uuid.UUID],
    ) -> FastAPIUsers[User, uuid.UUID]:
        return FastAPIUsers[User, uuid.UUID](
            lambda: user_manager,
            auth_backends=[auth_backend]
        )

    @provide(scope=Scope.REQUEST)
    def get_user_service(
            self,
            repository: UserGateway,
            fastapi_users: FastAPIUsers[User, uuid.UUID]
    ) -> UserService:
        return UserService(repository, fastapi_users)


class CommentProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_comment_gateway(self, session: AsyncSession) -> CommentGateway:
        return CommentRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_task_service(
            self,
            repository: CommentGateway,
            task_repository: TaskGateway,
    ) -> CommentService:
        return CommentService(repository, task_repository)


def setup_di():
    return make_async_container(
        config_provider(),
        DatabaseProvider(),
        TaskProvider(),
        UserProvider(),
        CommentProvider(),
    )
