from contextlib import suppress
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import Response
from redis.asyncio import Redis
from starlette.websockets import WebSocket

from skill_tracker.services.task_service import TaskService, CanNotMarkAsReadException
from skill_tracker.cache import cache
from skill_tracker.metrics import (
    CREATE_TASK_METHOD_DURATION,
    GET_ALL_TASKS_METHOD_DURATION,
    measure_latency,
)
from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict


class TaskBase(BaseModel):
    title: str
    text: str

class TaskCreate(TaskBase):
    user_id: UUID4

class TaskUpdate(BaseModel):
    read_at: Optional[datetime] = None

class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    created_at: datetime
    read_at: Optional[datetime]
    category: Optional[str]
    confidence: Optional[float]
    processing_status: str


class ManytasksResponse(BaseModel):
    total: int
    results: list[TaskResponse]


router = APIRouter(route_class=DishkaRoute)


@router.post("/tasks/", response_model=TaskResponse)
@measure_latency(CREATE_TASK_METHOD_DURATION)
async def create_task(
        task: TaskCreate,
        service: FromDishka[TaskService]
):
    db_task = await service.create_task(task)
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=db_task.model_dump_json(indent=4)
    )


@router.get("/tasks/")
@measure_latency(GET_ALL_TASKS_METHOD_DURATION)
@cache(ttl=10)
async def get_tasks(
        service: FromDishka[TaskService],
        redis_client: FromDishka[Redis],  # noqa
        user_id: UUID | None = None,
        skip: int = 0,
        limit: int = 10,
        status_: str | None = None,
):
    res = await service.get_tasks(skip=skip, limit=limit, status=status_, user_id=user_id)
    return res


@router.get("/tasks/{task_id}", response_model=TaskResponse)
@cache(ttl=10)
async def get_task(
        task_id: UUID,
        redis_client: FromDishka[Redis],  # noqa
        service: FromDishka[TaskService]
):
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")
    return task


@router.post("/tasks/{task_id}/mark-as-read", response_model=TaskResponse)
async def mark_task_as_read(
        task_id: UUID,
        service: FromDishka[TaskService]
):
    try:
        task = await service.mark_as_read(task_id)
    except CanNotMarkAsReadException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")
    return task


@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        user_id: str = Query(...),
):
    await websocket.accept()
    if user_id not in websocket_connections:
        websocket_connections[user_id] = []
    websocket_connections[user_id].append(websocket)

    try:
        while True:
            # Держим соединение открытым
            await websocket.receive_text()
    except Exception as e:
        print(e)
        websocket_connections[user_id].remove(websocket)
        if not websocket_connections[user_id]:
            del websocket_connections[user_id]
    finally:
        with suppress(RuntimeError):
            await websocket.close()


websocket_connections = {}
