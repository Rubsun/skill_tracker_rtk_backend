from typing import Protocol


from skill_tracker.db_access.models import Task, TaskStatusEnum
from skill_tracker.services.user_service import UserGateway
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class TaskCreateDTO:
    title: str
    description: Optional[str]
    employee_id: UUID
    manager_id: UUID
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
    manager_id: UUID
    employee_id: UUID
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
        self, caller, skip: int = 0, limit: int = 10
    ) -> tuple[list[Task], int]:
        raise NotImplementedError

    async def update(
        self, task_id: UUID, task_update: TaskUpdateDTO
    ) -> Task:
        raise NotImplementedError

    async def delete(self, task_id: UUID) -> bool:
        raise NotImplementedError



class OnlyManagerCanCreateTaskError(Exception):
    pass


class OnlyManagerCanUpdateTaskError(Exception):
    pass


class OnlyManagerCanDeleteTaskError(Exception):
    pass


class OnlyEmployeeCanBeAttachedToTask(Exception):
    pass


class TaskService:
    def __init__(self, repository: TaskGateway, user_repository: UserGateway):
        self.repository = repository
        self.user_repository = user_repository

    async def create_task(
        self, caller, task: TaskCreateDTO
    ) -> TaskDTO:
        if caller.role != "manager" and not caller.is_superuser:
            raise OnlyManagerCanCreateTaskError("Only managers can create tasks")

        employee = await self.user_repository.get_user(task.employee_id)
        if not employee:
            raise ValueError("Employee not found")

        if employee.role == "manager":
            raise OnlyEmployeeCanBeAttachedToTask

        db_task = await self.repository.create(task)
        return TaskDTO(
            title=db_task.title,
            description=db_task.description,
            status=db_task.status,
            progress=db_task.progress,
            employee_id=db_task.employee_id,
            deadline=db_task.deadline,
            created_at=db_task.created_at,
            id=db_task.id,
            manager_id=task.manager_id
        )

    async def get_task(self, task_id: UUID) -> Optional[TaskDTO]:
        task = await self.repository.get(task_id)
        if not task:
            raise ValueError("Task not found")

        return TaskDTO(title=task.title, description=task.description, status=task.status, progress=task.progress, manager_id=task.manager_id, employee_id=task.employee_id, deadline=task.deadline, created_at=task.created_at, id=task.id)

    async def get_tasks(
        self,
        caller,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[int, list[TaskDTO]]:
        tasks, total = await self.repository.get_all(caller, skip=skip, limit=limit)
        return (
            total,
            [
                TaskDTO(
                    title=task.title,
                    description=task.description,
                    status=task.status,
                    progress=task.progress,
                    employee_id=task.employee_id,
                    manager_id=task.manager_id,
                    deadline=task.deadline,
                    created_at=task.created_at,
                    id=task.id
                ) for task in tasks
            ]
        )

    async def update_task(self, caller, task_id: UUID, task_update: TaskUpdateDTO) -> TaskDTO:
        db_task = await self.repository.get(task_id)
        if not db_task:
            raise ValueError("Task not found")

        if db_task.manager_id != caller.id:
            raise PermissionError("Can not update others person task")

        if caller.role != "manager" and not caller.is_superuser:
            raise OnlyManagerCanUpdateTaskError("Only managers can update task")

        update_task = await self.repository.update(task_id, task_update)
        return TaskDTO(title=update_task.title, description=update_task.description, status=update_task.status,
                       progress=update_task.progress, employee_id=update_task.employee_id, deadline=update_task.deadline,
                       created_at=update_task.created_at, id=update_task.id, manager_id=update_task.manager_id)

    async def delete_task(self, caller, task_id: UUID) -> bool:
        db_task = await self.repository.get(task_id)
        if not db_task:
            raise ValueError("Task not found")

        if db_task.manager_id != caller.id:
            raise PermissionError("Can not delete others person task")

        if caller.role != "manager" and not caller.is_superuser:
            raise OnlyManagerCanDeleteTaskError("Only managers can delete task")

        is_deleted = await self.repository.delete(task_id)
        return is_deleted
