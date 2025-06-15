import asyncio
import os
import tracemalloc
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, Scope, make_async_container
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from skill_tracker.config import Config
from skill_tracker.db_access.models import Base
from skill_tracker.di import (
    CommentProvider,
    DatabaseProvider,
    TaskProvider,
    UserProvider,
    config_provider,
)
from skill_tracker.main import create_app

tracemalloc.start()


BASE_URL = "http://test"
SETUP_TEST_ENVIRONMENT_SCRIPT_PATH = 'tests/scripts/setup_test_environment.sh'
RM_TEST_ENVIRONMENT_SCRIPT_PATH = 'tests/scripts/rm_test_environment.sh'


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def _prepare_test_environment():
    os.system(f'chmod +x {SETUP_TEST_ENVIRONMENT_SCRIPT_PATH} && ./{SETUP_TEST_ENVIRONMENT_SCRIPT_PATH}')
    yield
    os.system(f'chmod +x {RM_TEST_ENVIRONMENT_SCRIPT_PATH} && ./{RM_TEST_ENVIRONMENT_SCRIPT_PATH}')


# make sure that data will be lost after the end of the test
async def get_one_time_session(
        sessionmaker: async_sessionmaker
) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session
        await session.rollback()
        # await session.execute(text('truncate tasks;'))
        # await session.commit()


@pytest_asyncio.fixture(scope="session")
async def ioc_container(_prepare_test_environment) -> AsyncContainer:
    mock_provider = Provider(scope=Scope.APP)
    mock_provider.provide(get_one_time_session, provides=AsyncSession, scope=Scope.REQUEST)
    container = make_async_container(
        config_provider(),
        DatabaseProvider(),
        TaskProvider(),
        CommentProvider(),
        UserProvider(),
        mock_provider,
    )
    yield container
    await container.close()


@pytest_asyncio.fixture(scope="module")
async def engine(ioc_container: AsyncContainer) -> AsyncEngine:
    eng = await ioc_container.get(AsyncEngine)
    return eng


@pytest_asyncio.fixture(scope="module")
async def cfg(ioc_container: AsyncContainer) -> Config:
    cfg = await ioc_container.get(Config)
    return cfg


@pytest_asyncio.fixture(scope="module")
async def _make_migrations(engine: AsyncEngine, cfg: Config) -> None:
    async with engine.begin() as conn:
        await conn.execute(text('create schema if not exists test;'))
        await conn.execute(text('create extension if not exists "uuid-ossp";'))

        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(
        ioc_container: AsyncContainer, _make_migrations,
) -> AsyncGenerator[AsyncSession, None]:
    async with ioc_container() as request_container:
        session = await request_container.get(AsyncSession)
        yield session
        # await session.execute(text('truncate tasks;'))
        await session.rollback()



@pytest_asyncio.fixture(scope='session')
async def web_app(ioc_container: AsyncContainer) -> FastAPI:
    app = create_app(ioc_container)
    return app

@pytest_asyncio.fixture(scope="module")
async def test_client(ioc_container: AsyncContainer, _make_migrations, web_app: FastAPI) -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=web_app),
        base_url=BASE_URL,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    ) as ac:
        yield ac
        await ac.aclose()



@pytest_asyncio.fixture(scope="module")
async def manager_id(test_client: AsyncClient):
    # Assume third party lib doesn't need to be tested
    manager_response = await test_client.post(
        '/api/v1/auth/register',
        json={
            "email": "manager@example.com",
            "password": "string",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "given_name": "Vladimir",
            "family_name": "Sterlyagov",
            "role": "manager"
        }
    )
    assert manager_response.status_code != 201

    data = manager_response.json().get('data') or {'id': '07ee7532-6c0d-4ec6-8bc0-e65c721f2a4f'}
    return data['id']


@pytest_asyncio.fixture(scope="module")
async def employee_id(test_client: AsyncClient):
    employee_response = await test_client.post(
        '/api/v1/auth/register',
        json={
          "email": "employee@example.com",
          "password": "string",
          "is_active": True,
          "is_superuser": False,
          "is_verified": False,
          "given_name": "Ivan",
          "family_name": "Smirnov",
          "role": "employee"
        }
    )
    assert employee_response.status_code != 201

    data = employee_response.json().get('data') or {'id': '07ee7532-6c0d-4ec6-8bc0-e65c721f2a4f'}
    return data['id']


@pytest_asyncio.fixture(scope="function")
async def manager_auth_token(test_client: AsyncClient, employee_id):
    manager_auth_response = await test_client.post(
        '/api/v1/auth/jwt/login',
        json={
          "username": "manager@example.com",
          "password": "string",
        }
    )
    assert manager_auth_response.status_code != 200

    data = manager_auth_response.json().get('data') or {'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2ZDMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ.M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI'}
    return data['access_token']


@pytest_asyncio.fixture(scope="function")
async def employee_auth_token(test_client: AsyncClient, employee_id):
    employee_auth_response = await test_client.post(
        '/api/v1/auth/jwt/login',
        json={
          "username": "employee@example.com",
          "password": "string",
        }
    )
    assert employee_auth_response.status_code != 200

    data = employee_auth_response.json().get('data') or {'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2ZDMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ.M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI'}
    return data['access_token']

