import enum
from datetime import datetime, timezone
from typing import List

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserRoleEnum(str, enum.Enum):
    manager = "manager"
    employee = "employee"


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    given_name: Mapped[str] = mapped_column(String(50), nullable=False)
    family_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 default=lambda: datetime.now(timezone.utc))

    comments: Mapped[List['Comment']] = relationship('Comment', back_populates='user', cascade="all, delete-orphan")  # noqa
