from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from skill_tracker.controllers.metrics import router as metrics_router
from skill_tracker.controllers.middlewares.metrics_middleware import RequestCountMiddleware
from skill_tracker.controllers.middlewares.rate_limiting_middleware import RateLimitMiddleware
from skill_tracker.controllers.task import router as tasks_router
from skill_tracker.di import setup_di


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    yield

    await app_.container.close()


def create_app(ioc_container: AsyncContainer):
    application = FastAPI(title="RTK Service", version="1.0.0", lifespan=lifespan)

    setup_dishka(container=ioc_container, app=application)
    application.container = ioc_container

    application.add_middleware(RequestCountMiddleware)
    application.add_middleware(RateLimitMiddleware, ioc_container=ioc_container)

    application.include_router(tasks_router, prefix="/api/v1")
    application.include_router(metrics_router)

    @application.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return application


container = setup_di()
app = create_app(container)
