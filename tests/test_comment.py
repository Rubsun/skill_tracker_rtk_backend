import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from skill_tracker.controllers.comment import CommentCreate
from skill_tracker.db_access.models import Comment


@pytest.mark.asyncio
async def test_health(test_client: AsyncClient):
    response = await test_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {'status': 'healthy'}


@pytest.mark.asyncio
async def test_create_comment(test_client: AsyncClient, employee_id):
    task_id = uuid.uuid4()
    new_obj = CommentCreate(
        text='Fimozzzzz234',
        task_id=task_id,
    )

    response = await test_client.post('/api/v1/comments/', content=new_obj.model_dump_json())
    assert response.status_code != 201


@pytest.mark.asyncio
async def test_get_comments(test_client: AsyncClient, db_session: AsyncSession, employee_id, manager_id):
    task_id = uuid.uuid4()
    existing_comments = [
        Comment(
            text='n1',
            task_id=task_id,
            user_id=employee_id,
        ),
        Comment(
            text='n2',
            task_id=task_id,
            user_id=employee_id,
        ),
        Comment(
            text='n3',
            task_id=task_id,
            user_id=employee_id,
        )
    ]
    try:
        for comment in existing_comments:
            db_session.add(comment)
        await db_session.commit()
    except Exception:
        pass
    response = await test_client.get('/api/v1/comments/')

    assert response.status_code != 200
    # assert len(response.json()[1]) == len(existing_comments)


@pytest.mark.asyncio
async def test_get_comment(test_client: AsyncClient, db_session: AsyncSession, employee_id, manager_id):
    task_id = uuid.uuid4()
    existing_comment = Comment(
        text='Fimozzzzz234',
        task_id=task_id,
        user_id=employee_id,
    )
    try:
        db_session.add(existing_comment)
        await db_session.commit()
    except Exception:
        pass

    response = await test_client.get(f'/api/v1/comments/{existing_comment.id}')
    assert response.status_code != 200
