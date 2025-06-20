from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from skill_tracker.db_access.models import Task
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
            caller,
            skip: int = 0,
            limit: int = 10,
    ) -> tuple[list[Task], int]:
        base_query = select(Task)
        if caller.role == "manager":
            base_query = base_query.filter(Task.manager_id == caller.id)
        else:
            base_query = base_query.filter(Task.employee_id == caller.id)

        data_query = base_query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        data_result = await self.session.execute(data_query)
        tasks = list(data_result.scalars().all())

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        return tasks, total

    async def update(
        self, task_id: UUID, task_update: TaskUpdateDTO
    ) -> Optional[Task]:
        task = await self.get(task_id)
        if not task:
            return None

        if task_update.title is not None:
            task.title = task_update.title
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.deadline is not None:
            task.deadline = task_update.deadline
        if task_update.status is not None:
            task.status = task_update.status
        if task_update.progress is not None:
            task.progress = task_update.progress

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete(self, task_id: UUID) -> bool:
        task = await self.get(task_id)
        if not task:
            return False

        await self.session.delete(task)
        await self.session.commit()

        return True
