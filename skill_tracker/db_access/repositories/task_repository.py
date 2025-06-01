from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from skill_tracker.db_access.models.task import Task
from skill_tracker.schemas.notification import NotificationCreate, NotificationUpdate


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, notification: NotificationCreate) -> Task:
        db_notification = Task(**notification.model_dump())
        self.session.add(db_notification)
        await self.session.commit()
        await self.session.refresh(db_notification)
        return db_notification

    async def get(self, notification_id: UUID) -> Optional[Task]:
        result = await self.session.execute(
            select(Task).filter(Task.id == notification_id)
        )
        return result.scalars().first()

    async def get_all(
            self,
            skip: int = 0,
            limit: int = 10,
            status: Optional[str] = None,
            user_id: Optional[UUID] = None
    ) -> tuple[list[Task], int]:
        base_query = select(Task)
        if status:
            base_query = base_query.filter(Task.processing_status == status)
        if user_id:
            base_query = base_query.filter(Task.user_id == user_id)

        data_query = base_query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        data_result = await self.session.execute(data_query)
        notifications = list(data_result.scalars().all())

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        return notifications, total

    async def update(
        self, notification: Task, notification_update: NotificationUpdate
    ) -> Task:
        notification.read_at = notification_update.read_at
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def update_status(
        self, notification_id: UUID, status: str
    ) -> Optional[Task]:
        notification = await self.get(notification_id)
        if not notification:
            return None
        notification.processing_status = status
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def update_analysis(
        self,
        notification_id: UUID,
        category: str,
        confidence: float,
        status: str
    ) -> Optional[Task]:
        notification = await self.get(notification_id)
        if not notification:
            return None
        notification.category = category
        notification.confidence = confidence
        notification.processing_status = status
        await self.session.commit()
        await self.session.refresh(notification)
        return notification
