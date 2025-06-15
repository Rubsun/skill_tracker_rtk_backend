from typing import Protocol


from skill_tracker.db_access.models import Task, TaskStatusEnum
from skill_tracker.services.user_service import UserGateway
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from loguru import logger


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
            logger.warning(f"User {caller.id} denied: Only managers can create tasks")
            raise OnlyManagerCanCreateTaskError("Only managers can create tasks")

        employee = await self.user_repository.get_user(task.employee_id)
        if not employee:
            logger.error(f"Employee {task.employee_id} not found")
            raise ValueError("Employee not found")

        if employee.role == "manager":
            logger.error(f"Cannot assign task to manager {employee.id}")
            raise OnlyEmployeeCanBeAttachedToTask("Manager cant attach manager to task")

        db_task = await self.repository.create(task)
        logger.info(f"Task created successfully with ID: {db_task.id}")
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
        logger.info(f"Fetching task with ID: {task_id}")
        task = await self.repository.get(task_id)
        if not task:
            logger.warning(f"Task {task_id} not found")
            raise ValueError("Task not found")

        logger.info(f"Task {task_id} retrieved successfully")
        return TaskDTO(title=task.title, description=task.description, status=task.status, progress=task.progress, manager_id=task.manager_id, employee_id=task.employee_id, deadline=task.deadline, created_at=task.created_at, id=task.id)

    async def get_tasks(
        self,
        caller,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[int, list[TaskDTO]]:
        logger.info(f"User {caller.id} fetching tasks (skip={skip}, limit={limit})")
        tasks, total = await self.repository.get_all(caller, skip=skip, limit=limit)
        logger.info(f"Retrieved {len(tasks)} tasks, total: {total}")
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
        logger.info(f"User {caller.id} attempting to update task {task_id}")
        db_task = await self.repository.get(task_id)
        if not db_task:
            logger.warning(f"Task {task_id} not found")
            raise ValueError("Task not found")

        if caller.role == "employee" and not caller.is_superuser:
            if db_task.employee_id != caller.id:
                logger.warning(f"User {caller.id} denied: Cannot update task {task_id} owned by {db_task.manager_id}")
                raise PermissionError("Can not update others person task")

            allowed_fields = {"status", "progress"}
            for field, value in task_update.__dict__.items():
                if value is not None and field not in allowed_fields:
                    logger.error(f"User {caller.id} denied: Cannot update {field}")
                    raise PermissionError("Employees can update only status or progress")

        elif caller.role != "manager" and not caller.is_superuser:
            logger.warning(f"User {caller.id} denied: Only managers can update tasks")
            raise OnlyManagerCanUpdateTaskError

        update_task = await self.repository.update(task_id, task_update)
        logger.info(f"Task {task_id} updated successfully")
        return TaskDTO(title=update_task.title, description=update_task.description, status=update_task.status,
                       progress=update_task.progress, employee_id=update_task.employee_id, deadline=update_task.deadline,
                       created_at=update_task.created_at, id=update_task.id, manager_id=update_task.manager_id)

    async def delete_task(self, caller, task_id: UUID) -> bool:
        logger.info(f"User {caller.id} attempting to delete task {task_id}")
        db_task = await self.repository.get(task_id)
        if not db_task:
            logger.warning(f"Task {task_id} not found")
            raise ValueError("Task not found")

        if db_task.manager_id != caller.id:
            logger.warning(f"User {caller.id} denied: Cannot delete task {task_id} owned by {db_task.manager_id}")
            raise PermissionError("Can not delete others person task")

        if caller.role != "manager" and not caller.is_superuser:
            logger.warning(f"User {caller.id} denied: Only managers can delete tasks")
            raise OnlyManagerCanDeleteTaskError("Only managers can delete task")

        is_deleted = await self.repository.delete(task_id)
        logger.info(f"Task {task_id} deleted: {is_deleted}")
        return is_deleted
