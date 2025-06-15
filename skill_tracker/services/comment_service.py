from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol
from uuid import UUID

from loguru import logger

from skill_tracker.db_access.models import Comment
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
        logger.info(f"User {comment.user_id} creating comment for task {comment.task_id}")
        task_to_comment = await self.task_repository.get(comment.task_id)
        if not task_to_comment:
            logger.warning(f"Task {comment.task_id} not found")
            raise ValueError("Task not found")

        db_comment = await self.repository.create(comment)
        logger.info(f"Comment created with ID: {db_comment.id}")
        return CommentDTO(id=db_comment.id, text=db_comment.text, created_at=db_comment.created_at, task_id=db_comment.task_id, user_id=db_comment.user_id)

    async def get_comment(self, comment_id: UUID) -> Optional[CommentDTO]:
        logger.info(f"Fetching comment with ID: {comment_id}")
        comment = await self.repository.get(comment_id)
        if not comment:
            logger.warning(f"Comment {comment_id} not found")
            raise ValueError("Comment not found")

        logger.info(f"Comment {comment_id} retrieved successfully")
        return CommentDTO(id=comment.id, text=comment.text, created_at=comment.created_at, task_id=comment.task_id, user_id=comment.user_id)

    async def get_comments(
        self,
        skip: int = 0,
        limit: int = 10,
        task_id: Optional[UUID] = None,
    ) -> tuple[int, list[CommentDTO]]:
        logger.info(f"Fetching comments (skip={skip}, limit={limit}, task_id={task_id})")
        comments, total = await self.repository.get_all(skip=skip, limit=limit, task_id=task_id)
        logger.info(f"Retrieved {len(comments)} comments, total: {total}")
        return total, [CommentDTO(id=comment.id, text=comment.text, created_at=comment.created_at, task_id=comment.task_id, user_id=comment.user_id) for comment in comments]

    async def update_comment(self, caller, comment_id: UUID, comment_update: CommentUpdateDTO) -> CommentDTO:
        logger.info(f"User {caller.id} updating comment {comment_id}")
        db_comment = await self.repository.get(comment_id)
        if not db_comment:
            logger.warning(f"Comment {comment_id} not found")
            raise ValueError("Comment not found")

        if caller.id != db_comment.user_id:
            logger.warning(f"User {caller.id} denied: Cannot update comment {comment_id}")
            raise PermissionError("Can not update others person comment")

        update_comment = await self.repository.update(comment_id, comment_update)
        logger.info(f"Comment {comment_id} updated successfully")

        return CommentDTO(id=update_comment.id, text=update_comment.text, created_at=update_comment.created_at, task_id=update_comment.task_id, user_id=update_comment.user_id)

    async def delete_comment(self, caller, comment_id: UUID) -> bool:
        logger.info(f"User {caller.id} deleting comment {comment_id}")
        db_comment = await self.repository.get(comment_id)
        if not db_comment:
            logger.warning(f"Comment {comment_id} not found")
            raise ValueError("Comment not found")

        if caller.id != db_comment.user_id:
            logger.warning(f"User {caller.id} denied: Cannot delete comment {comment_id}")
            raise PermissionError("Can not delete others person comment")

        is_deleted = await self.repository.delete(comment_id)
        logger.info(f"Comment {comment_id} deleted: {is_deleted}")
        return is_deleted
