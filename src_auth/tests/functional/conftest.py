import asyncio
from typing import AsyncGenerator, Awaitable, Callable

import pytest
import redis.asyncio as aioredis
from aiohttp import ClientSession
from alembic import command
from alembic.config import Config
from pytest_asyncio import fixture as async_fixture
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src_auth.tests.functional.settings import test_settings

MakeRequestType = Callable[..., Awaitable[tuple[dict, int, dict]]]


# http fixtures
@async_fixture
def make_request(aiohttp_session: ClientSession) -> MakeRequestType:
    async def inner(
        method: str,
        path: str,
        params: dict | None = None,
        data: dict | None = None,
        cookies: dict | None = None,
    ) -> tuple[dict, int, dict]:
        url = test_settings.auth_api_base_url + path

        request_method = getattr(aiohttp_session, method.lower(), None)
        if request_method is None:
            raise ValueError(f"Unsupported HTTP method: {method}")

        kwargs = {
            "headers": {
                "X-Request-Id": "Test-Request-ID-1234567890",
            },
        }
        if params:
            kwargs["params"] = params
        if data is not None:
            kwargs["json"] = data
        if cookies is not None:
            kwargs["cookies"] = cookies

        async with request_method(url, **kwargs) as response:
            body = await response.json()
            status = response.status
            cookies = response.cookies

        await asyncio.sleep(0.02)
        return body, status, cookies

    return inner


@async_fixture(scope="session")
async def aiohttp_session() -> AsyncGenerator[ClientSession, None]:
    session = ClientSession()
    yield session
    await session.close()


# redis client fixture
@async_fixture
async def redis_connection(
    redis_client: aioredis.Redis,
) -> AsyncGenerator[aioredis.Redis, None]:
    await redis_client.flushall()
    yield redis_client


@async_fixture(scope="session")
async def redis_client() -> AsyncGenerator[aioredis.Redis, None]:
    pool = aioredis.ConnectionPool.from_url(
        test_settings.redis_base_url,
        max_connections=2,
    )
    client = aioredis.Redis(connection_pool=pool)
    yield client
    await client.aclose()


# db session fixture
@async_fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as connection:
        async_session = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
        )
        async with async_session() as session:
            yield session


@async_fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(test_settings.db_url, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def apply_migrations() -> None:
    alembic_cfg = Config(test_settings.base_dir / "alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_settings.db_url)
    command.upgrade(alembic_cfg, "head")
