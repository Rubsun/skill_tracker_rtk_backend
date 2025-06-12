import uuid

from fastapi_users.db import SQLAlchemyUserDatabase
from skill_tracker.db_access.models import User
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def get_user_db(self):
        return SQLAlchemyUserDatabase[User, uuid.UUID](self.session, User)
