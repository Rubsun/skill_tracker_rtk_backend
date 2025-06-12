from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka import AsyncContainer, Scope
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from skill_tracker.controllers.metrics import router as metrics_router
from skill_tracker.controllers.middlewares.metrics_middleware import RequestCountMiddleware
from skill_tracker.controllers.comment import get_comments_controller
from skill_tracker.controllers.task import get_tasks_controller
from skill_tracker.controllers.user import get_users_controller
from skill_tracker.di import setup_di


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    async with container(scope=Scope.REQUEST) as request_container:
        user_router = await get_users_controller(request_container)
        task_router = await get_tasks_controller(request_container)
        comment_router = await get_comments_controller(request_container)
        app_.include_router(comment_router)
        app_.include_router(task_router)
        app_.include_router(user_router)

    yield

    await app_.container.close()


def create_app(ioc_container: AsyncContainer):
    application = FastAPI(title="RTK Service", version="1.0.0", lifespan=lifespan)

    setup_dishka(container=ioc_container, app=application)
    application.container = ioc_container

    # application.add_middleware(RequestCountMiddleware)

    application.include_router(metrics_router)

    @application.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return application


container = setup_di()
app = create_app(container)
