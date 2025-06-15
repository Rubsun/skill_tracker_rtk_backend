from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Comment(Base):
    __tablename__ = 'comments'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    task_id: Mapped[UUID] = mapped_column(ForeignKey('tasks.id', ondelete="CASCADE"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    task: Mapped['Task'] = relationship('Task', back_populates='comments')  # noqa
    user: Mapped['User'] = relationship('User', back_populates='comments')  # noqa
