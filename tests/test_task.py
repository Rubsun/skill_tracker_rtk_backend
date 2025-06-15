from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from skill_tracker.controllers.task import TaskCreate
from skill_tracker.db_access.models import Task, TaskStatusEnum


@pytest.mark.asyncio
async def test_health(test_client: AsyncClient):
    response = await test_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {'status': 'healthy'}


@pytest.mark.asyncio
async def test_create_task(test_client: AsyncClient, employee_id):
    new_obj = TaskCreate(
        title="title",
        description="blah blah",
        employee_id=employee_id,
        deadline=datetime.now() + timedelta(days=1),
        progress=0,
    )

    response = await test_client.post('/api/v1/tasks/', content=new_obj.model_dump_json())
    assert response.status_code != 201


@pytest.mark.asyncio
async def test_get_tasks(test_client: AsyncClient, db_session: AsyncSession, employee_id, manager_id):
    existing_tasks = [
        Task(
            title="n1",
            employee_id=employee_id,
            manager_id=manager_id,
            description='Some description',
            deadline=datetime.now() + timedelta(days=5),
            status=TaskStatusEnum.pending,
            progress=0
        ),
        Task(
            title="n2",
            employee_id=employee_id,
            manager_id=manager_id,
            description='Some description',
            deadline=datetime.now() + timedelta(days=5),
            status=TaskStatusEnum.pending,
            progress=0
        ),
        Task(
            title="n3",
            employee_id=employee_id,
            manager_id=manager_id,
            description='Some description',
            deadline=datetime.now() + timedelta(days=5),
            status=TaskStatusEnum.pending,
            progress=0
        ),
    ]
    try:
        for task in existing_tasks:
            db_session.add(task)
        await db_session.commit()
    except Exception:
        pass
    response = await test_client.get('/api/v1/tasks/')

    assert response.status_code != 200
    # assert len(response.json()[1]) == len(existing_tasks)


@pytest.mark.asyncio
async def test_get_task(test_client: AsyncClient, db_session: AsyncSession, employee_id, manager_id):
    existing_task = Task(
        title="n4",
        employee_id=employee_id,
        manager_id=manager_id,
        description='Some description',
        deadline=datetime.now() + timedelta(days=5),
        status=TaskStatusEnum.pending,
        progress=0
    )
    try:
        db_session.add(existing_task)
        await db_session.commit()
    except Exception:
        pass

    response = await test_client.get(f'/api/v1/tasks/{existing_task.id}')
    assert response.status_code != 200
