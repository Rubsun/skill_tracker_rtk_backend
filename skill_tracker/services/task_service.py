from typing import Protocol


from skill_tracker.db_access.models import Task, TaskStatusEnum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class TaskCreateDTO:
    title: str
    description: Optional[str]
    user_id: UUID
    deadline: Optional[datetime]
    status: Optional[TaskStatusEnum]
    progress: Optional[int]


@dataclass
class TaskUpdateDTO:
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[TaskStatusEnum] = None
    progress: Optional[int] = None


@dataclass
class TaskDTO:
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    description: Optional[str]
    deadline: Optional[datetime]
    status: TaskStatusEnum
    progress: int


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
        self, task_id: UUID, task_update: TaskUpdateDTO
    ) -> Task:
        raise NotImplementedError

    async def delete(self, task_id: UUID) -> bool:
        raise NotImplementedError




class TaskService:
    def __init__(self, repository: TaskGateway):
        self.repository = repository

    async def create_task(
        self, task: TaskCreateDTO
    ) -> TaskDTO:
        db_task = await self.repository.create(task)
        return TaskDTO(title=db_task.title, description=db_task.description, status=db_task.status, progress=db_task.progress, user_id=db_task.user_id, deadline=db_task.deadline, created_at=db_task.created_at, id=db_task.id)

    async def get_task(self, task_id: UUID) -> Optional[TaskDTO]:
        task = await self.repository.get(task_id)
        if not task:
            return None
        return TaskDTO(title=task.title, description=task.description, status=task.status, progress=task.progress, user_id=task.user_id, deadline=task.deadline, created_at=task.created_at, id=task.id)

    async def get_tasks(
        self,
        skip: int = 0,
        limit: int = 10,
        user_id: Optional[UUID] = None,
    ) -> tuple[int, list[TaskDTO]]:
        tasks, total = await self.repository.get_all(skip=skip, limit=limit, user_id=user_id)
        return total, [TaskDTO(title=n.title, description=n.description, status=n.status, progress=n.progress, user_id=n.user_id, deadline=n.deadline, created_at=n.created_at, id=n.id) for n in tasks]

    async def update_task(self, task_id: UUID, task_update: TaskUpdateDTO) -> TaskDTO:
        db_task = await self.repository.update(task_id, task_update)
        return TaskDTO(title=db_task.title, description=db_task.description, status=db_task.status,
                       progress=db_task.progress, user_id=db_task.user_id, deadline=db_task.deadline,
                       created_at=db_task.created_at, id=db_task.id)

    async def delete_task(self, task_id: UUID) -> bool:
        is_deleted = await self.repository.delete(task_id)
        return is_deleted
