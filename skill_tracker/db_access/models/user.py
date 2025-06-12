from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from .base import Base

from typing import List
from sqlalchemy import (
    String, Enum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

import enum


class UserRoleEnum(str, enum.Enum):
    manager = "manager"
    employee = "employee"


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    given_name: Mapped[str] = mapped_column(String(50), nullable=False)
    family_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum), nullable=False)

    comments: Mapped[List['Comment']] = relationship('Comment', back_populates='user', cascade="all, delete-orphan")
