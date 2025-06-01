from typing import Protocol


from skill_tracker.db_access.models import Task
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class TaskCreateDTO:
    title: str
    text: str
    user_id: UUID


@dataclass
class TaskUpdateDTO:
    read_at: Optional[datetime] = None


@dataclass
class TaskDTO:
    id: UUID
    user_id: UUID
    created_at: datetime
    read_at: Optional[datetime]
    category: Optional[str]
    confidence: Optional[float]
    processing_status: str


class TaskGateway(Protocol):
    async def create(self, task: TaskCreateDTO) -> Task:
        raise NotImplementedError

    async def get(self, task_id: UUID) -> Optional[Task]:
        raise NotImplementedError

    async def get_all(
        self, skip: int = 0, limit: int = 10, user_id: Optional[UUID] = None
    ) -> tuple[list[Task], int]:
        raise NotImplementedError

    async def update(
        self, task: Task, task_update: TaskUpdateDTO
    ) -> Task:
        raise NotImplementedError




class TaskService:
    def __init__(self, repository: TaskGateway):
        self.repository = repository

    async def create_task(
        self, task: TaskCreateDTO
    ) -> TaskDTO:
        db_task = await self.repository.create(task)
        return TaskDTO(**db_task.__dict__)

    async def get_task(self, task_id: UUID) -> Optional[TaskDTO]:
        task = await self.repository.get(task_id)
        if not task:
            return None
        return TaskDTO(**task.__dict__)

    async def get_tasks(
        self,
        skip: int = 0,
        limit: int = 10,
        user_id: Optional[UUID] = None,
        status: Optional[str] = None,
    ) -> tuple[int, list[TaskDTO]]:
        tasks, total = await self.repository.get_all(skip=skip, limit=limit, user_id=user_id, status=status)
        return total, [TaskDTO(**n.__dict__) for n in tasks]


    async def mark_as_read(
        self, task_id: UUID,
    ) -> Optional[TaskDTO]:
        task_to_update = await self.repository.get(task_id)
        if not task_to_update:
            return None

        if task_to_update.read_at is not None:
            raise CanNotMarkAsReadException('task has already been marked as read')

        update_data = TaskUpdateDTO(read_at=datetime.now())
        updated_task = await self.repository.update(task_to_update, update_data)
        return TaskDTO(**updated_task.__dict__)

# business logic layer exceptions
class CanNotMarkAsReadException(Exception):
    pass
