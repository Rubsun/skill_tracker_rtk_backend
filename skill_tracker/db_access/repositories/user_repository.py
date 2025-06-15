from typing import Optional
from uuid import UUID

from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from skill_tracker.db_access.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def get_user_db(self):
        return SQLAlchemyUserDatabase[User, UUID](self.session, User)

    async def get_employees(
            self,
            skip: int = 0,
            limit: int = 10
    ) -> tuple[list[User], int]:
        base_query = select(User).filter(User.role == "employee")
        data_query = base_query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        data_result = await self.session.execute(data_query)
        employees = list(data_result.scalars().all())

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        return employees, total

    async def get_user(self, user_id: UUID) -> Optional[User]:
        result = await self.session.execute(
            select(User).filter(User.id == user_id)
        )
        return result.scalars().first()
