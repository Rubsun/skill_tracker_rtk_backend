from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from skill_tracker.db_access.models import Comment
from skill_tracker.services.comment_service import CommentCreateDTO, CommentGateway, CommentUpdateDTO


class CommentRepository(CommentGateway):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task: CommentCreateDTO) -> Comment:
        db_comment = Comment(**task.__dict__)
        self.session.add(db_comment)
        await self.session.commit()
        await self.session.refresh(db_comment)
        return db_comment

    async def get(self, comment_id: UUID) -> Optional[Comment]:
        result = await self.session.execute(
            select(Comment).filter(Comment.id == comment_id)
        )
        return result.scalars().first()

    async def get_all(
            self,
            skip: int = 0,
            limit: int = 10,
            task_id: Optional[UUID] = None
    ) -> tuple[list[Comment], int]:
        base_query = select(Comment)
        if task_id:
            base_query = base_query.filter(Comment.task_id == task_id)

        data_query = base_query.order_by(Comment.created_at.desc()).offset(skip).limit(limit)
        data_result = await self.session.execute(data_query)
        comments = list(data_result.scalars().all())

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        return comments, total

    async def update(
        self, comment_id: UUID, comment_update: CommentUpdateDTO
    ) -> Optional[Comment]:
        comment = await self.get(comment_id)
        if not comment:
            return None

        comment.text = comment_update.text

        await self.session.commit()
        await self.session.refresh(comment)

        return comment

    async def delete(self, comment_id: UUID) -> bool:
        comment = await self.get(comment_id)
        if not comment:
            return False

        await self.session.delete(comment)
        await self.session.commit()

        return True
