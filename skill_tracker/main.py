from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka import AsyncContainer, Scope
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from skill_tracker.controllers.comment import get_comments_controller
from skill_tracker.controllers.task import get_tasks_controller
from skill_tracker.controllers.user import get_users_controller
from skill_tracker.di import setup_di


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Lifespan started")
    async with container(scope=Scope.REQUEST) as request_container:
        user_router = await get_users_controller(request_container)
        task_router = await get_tasks_controller(request_container)
        comment_router = await get_comments_controller(request_container)
        app_.include_router(comment_router)
        app_.include_router(task_router)
        app_.include_router(user_router)

    yield

    logger.info("Lifespan ended")
    await app_.container.close()


def create_app(ioc_container: AsyncContainer):
    application = FastAPI(title="RTK Service", version="1.0.0", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_instrument_requests_inprogress=True,
        inprogress_labels=True,
        # custom_labels={"service": "skill-tracker"}
    )
    instrumentator.instrument(application).expose(app=application, endpoint="/api/v1/metrics", should_gzip=True)

    setup_dishka(container=ioc_container, app=application)
    application.container = ioc_container

    @application.get("/api/v1/health")
    async def health_check():
        logger.info("Health check requested")
        return {"status": "healthy"}

    logger.info("Application starting up")
    return application


container = setup_di()
app = create_app(container)
