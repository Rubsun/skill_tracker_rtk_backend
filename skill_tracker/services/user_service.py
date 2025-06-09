from typing import Protocol

from fastapi import Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users import schemas
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from skill_tracker.db_access.models.user import User
from typing import Optional
import uuid


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class UserGateway(Protocol):
    def get_user_db(self):
        raise NotImplementedError


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    def __init__(self, db, secret: str):
        super().__init__(db)
        self.reset_password_token_secret = secret
        self.verification_token_secret = secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


class UserService:
    def __init__(self, repository: UserGateway, fastapi_users: FastAPIUsers[User, uuid.UUID]):
        self.repository = repository
        self.fastapi_users = fastapi_users

    async def __get_user_manager(self) :
        return await self.repository.get_user_db()
