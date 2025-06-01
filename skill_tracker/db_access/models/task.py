import uuid
from datetime import datetime

from sqlalchemy import UUID, Column, DateTime, Float, String

from .base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, nullable=False)
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    read_at = Column(DateTime, nullable=True)
