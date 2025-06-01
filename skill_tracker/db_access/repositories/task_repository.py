from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from skill_tracker.db_access.models.task import Task
from skill_tracker.services.task_service import TaskCreateDTO, TaskGateway, TaskUpdateDTO


class TaskRepository(TaskGateway):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task: TaskCreateDTO) -> Task:
        db_task = Task(**task.__dict__)
        self.session.add(db_task)
        await self.session.commit()
        await self.session.refresh(db_task)
        return db_task

    async def get(self, task_id: UUID) -> Optional[Task]:
        result = await self.session.execute(
            select(Task).filter(Task.id == task_id)
        )
        return result.scalars().first()

    async def get_all(
            self,
            skip: int = 0,
            limit: int = 10,
            user_id: Optional[UUID] = None
    ) -> tuple[list[Task], int]:
        base_query = select(Task)
        if user_id:
            base_query = base_query.filter(Task.user_id == user_id)

        data_query = base_query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        data_result = await self.session.execute(data_query)
        tasks = list(data_result.scalars().all())

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        return tasks, total

    async def update(
        self, task: Task, task_update: TaskUpdateDTO
    ) -> Task:
        task.read_at = task_update.read_at
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update_status(
        self, task_id: UUID, status: str
    ) -> Optional[Task]:
        task = await self.get(task_id)
        if not task:
            return None
        task.processing_status = status
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update_analysis(
        self,
        task_id: UUID,
        category: str,
        confidence: float,
        status: str
    ) -> Optional[Task]:
        task = await self.get(task_id)
        if not task:
            return None
        task.category = category
        task.confidence = confidence
        task.processing_status = status
        await self.session.commit()
        await self.session.refresh(task)
        return task
