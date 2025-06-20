import enum
from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class TaskStatusEnum(str, enum.Enum):
    pending = "pending"
    inprogress = "inprogress"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    employee_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))
    manager_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[TaskStatusEnum] = mapped_column(Enum(TaskStatusEnum), nullable=False, default=TaskStatusEnum.pending)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    comments: Mapped[List['Comment']] = relationship('Comment', back_populates='task', cascade="all, delete-orphan")  # noqa

    __table_args__ = (
        CheckConstraint('progress >= 0 AND progress <= 100', name='chk_progress_range'),
    )
