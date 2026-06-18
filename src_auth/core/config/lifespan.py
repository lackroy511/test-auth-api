import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src_auth.core.config.logger import configure_logging
from src_auth.core.db.cache import client as redis_client
from src_auth.core.db.sql_alch import engine as sql_alch_engine
from src_auth.core.db.sql_alch import sessionmaker
from src_auth.utils.init_db import init_db

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    try:
        log.info("Auth API is starting...")
        configure_logging()

        async with sessionmaker() as session:
            async with session.begin():
                log.info("Database initializing...")
                await init_db(session)

        yield
    finally:
        log.info("Auth API is shutting down...")
        await redis_client.close()
        await sql_alch_engine.dispose()
