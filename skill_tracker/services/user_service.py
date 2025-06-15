from typing import Optional, Protocol
from uuid import UUID

from fastapi import Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas
from loguru import logger
from pydantic import BaseModel, Field

from skill_tracker.db_access.models import User, UserRoleEnum


class MainUser(BaseModel):
    given_name: str = Field(..., min_length=1, max_length=50)
    family_name: str = Field(..., min_length=1, max_length=100)
    role: UserRoleEnum


class UserRead(MainUser, schemas.BaseUser[UUID]):
    pass


class UserCreate(MainUser, schemas.BaseUserCreate):
    pass


class UserUpdate(MainUser, schemas.BaseUserUpdate):
    pass


class OnlyManagerCanGetEmployeesError(Exception):
    pass


class UserGateway(Protocol):
    def get_user_db(self):
        raise NotImplementedError

    async def get_employees(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[User], int]:
        raise NotImplementedError

    async def get_user(self, user_id: UUID) -> Optional[User]:
        raise NotImplementedError


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    def __init__(self, db, secret: str):
        super().__init__(db)
        self.reset_password_token_secret = secret
        self.verification_token_secret = secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"Verification requested for user {user.id}. Verification token: {token}")


class UserService:
    def __init__(self, repository: UserGateway, fastapi_users: FastAPIUsers[User, UUID]):
        self.repository = repository
        self.fastapi_users = fastapi_users

    async def get_employees(
        self,
        caller,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[int, list[User]]:
        logger.info(f"User {caller.id} requesting employees (skip={skip}, limit={limit})")
        if caller.role != "manager" and not caller.is_superuser:
            logger.warning(f"User {caller.id} denied: Only managers can get employees")
            raise OnlyManagerCanGetEmployeesError("Only managers can get employees")

        employees, total = await self.repository.get_employees(skip=skip, limit=limit)
        logger.info(f"Retrieved {len(employees)} employees, total: {total}")
        return total, [employee for employee in employees]
