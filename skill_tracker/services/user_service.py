from typing import Protocol

from fastapi import Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users import schemas
from pydantic import Field, BaseModel

from skill_tracker.db_access.models import User, UserRoleEnum
from typing import Optional
import uuid


class MainUser(BaseModel):
    given_name: str = Field(..., min_length=1, max_length=50)
    family_name: str = Field(..., min_length=1, max_length=100)
    role: UserRoleEnum

class UserRead(MainUser, schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(MainUser, schemas.BaseUserCreate):
    pass


class UserUpdate(MainUser, schemas.BaseUserUpdate):
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
