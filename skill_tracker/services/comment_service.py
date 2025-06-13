from typing import Protocol


from skill_tracker.db_access.models import Comment
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from skill_tracker.services.task_service import TaskGateway


@dataclass
class CommentCreateDTO:
    text: str
    task_id: UUID
    user_id: UUID


@dataclass
class CommentUpdateDTO:
    text: str


@dataclass
class CommentDTO:
    id: UUID
    text: str
    created_at: datetime
    task_id: UUID
    user_id: UUID


class CommentGateway(Protocol):
    async def create(self, comment: CommentCreateDTO) -> CommentDTO:
        raise NotImplementedError

    async def get(self, comment_id: UUID) -> Optional[Comment]:
        raise NotImplementedError

    async def get_all(
        self, skip: int = 0, limit: int = 10, task_id: Optional[UUID] = None
    ) -> tuple[list[Comment], int]:
        raise NotImplementedError

    async def update(
        self, comment_id: UUID, comment_update: CommentUpdateDTO
    ) -> Comment:
        raise NotImplementedError

    async def delete(self, comment_id: UUID) -> bool:
        raise NotImplementedError




class CommentService:
    def __init__(self, repository: CommentGateway, task_repository: TaskGateway):
        self.repository = repository
        self.task_repository = task_repository

    async def create_comment(
        self, comment: CommentCreateDTO
    ) -> CommentDTO:
        task_to_comment = await self.task_repository.get(comment.task_id)
        if not task_to_comment:
            raise ValueError("Task not found")

        db_comment = await self.repository.create(comment)
        return CommentDTO(id=db_comment.id, text=db_comment.text, created_at=db_comment.created_at, task_id=db_comment.task_id, user_id=db_comment.user_id)

    async def get_comment(self, comment_id: UUID) -> Optional[CommentDTO]:
        comment = await self.repository.get(comment_id)
        if not comment:
            raise ValueError("Comment not found")

        return CommentDTO(id=comment.id, text=comment.text, created_at=comment.created_at, task_id=comment.task_id, user_id=comment.user_id)

    async def get_comments(
        self,
        skip: int = 0,
        limit: int = 10,
        task_id: Optional[UUID] = None,
    ) -> tuple[int, list[CommentDTO]]:
        comments, total = await self.repository.get_all(skip=skip, limit=limit, task_id=task_id)
        return total, [CommentDTO(id=comment.id, text=comment.text, created_at=comment.created_at, task_id=comment.task_id, user_id=comment.user_id) for comment in comments]

    async def update_comment(self, caller, comment_id: UUID, comment_update: CommentUpdateDTO) -> CommentDTO:
        db_comment = await self.repository.get(comment_id)
        if not db_comment:
            raise ValueError("Comment not found")

        if caller.id != db_comment.user_id:
            raise PermissionError("Can not update others person comment")

        update_comment = await self.repository.update(comment_id, comment_update)

        return CommentDTO(id=update_comment.id, text=update_comment.text, created_at=update_comment.created_at, task_id=update_comment.task_id, user_id=update_comment.user_id)

    async def delete_comment(self, caller, comment_id: UUID) -> bool:
        db_comment = await self.repository.get(comment_id)
        if not db_comment:
            raise ValueError("Comment not found")

        if caller.id != db_comment.user_id:
            raise PermissionError("Can not delete others person comment")

        is_deleted = await self.repository.delete(comment_id)
        return is_deleted
