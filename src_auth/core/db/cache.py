import json
from abc import ABC, abstractmethod
from typing import Any

import redis.asyncio as aioredis
from redis.exceptions import ConnectionError, TimeoutError

from src_auth.core.config.settings import settings
from src_auth.core.db.exceptions import SaveRedisCacheError
from src_auth.utils.backoff import Backoff

pool = aioredis.ConnectionPool.from_url(settings.redis_base_url, max_connections=10)
client = aioredis.Redis(connection_pool=pool)


CacheDataType = dict[str, str | int | list[str] | None | bool] | str | int


class CacheClientInterface(ABC):
    @abstractmethod
    async def set_cache(self, key: str, data: CacheDataType, ttl: int) -> None:
        pass

    @abstractmethod
    async def get_cache(self, key: str) -> CacheDataType | None:
        pass

    @abstractmethod
    async def delete_cache(self, key: str) -> int:
        pass

    @abstractmethod
    def build_cache_key(self, prefix: str, *key_args: Any) -> str:  # noqa: ANN401
        pass


RETRY_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    SaveRedisCacheError,
)


class RedisCacheClient(CacheClientInterface):
    def __init__(self, client: aioredis.Redis) -> None:
        self.client = client

    @Backoff(RETRY_EXCEPTIONS)
    async def set_cache(
        self,
        key: str,
        data: CacheDataType,
        ttl: int,
    ) -> None:
        if isinstance(data, dict):
            data = json.dumps(data)

        is_saved = await self.client.set(key, data, ex=ttl)
        if not is_saved:
            raise SaveRedisCacheError("Failed to save data to Redis cache.")

    @Backoff(RETRY_EXCEPTIONS)
    async def get_cache(self, key: str) -> CacheDataType | None:
        raw_data = await self.client.get(key)
        if not raw_data:
            return None

        json_str = raw_data.decode("utf-8")
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return json_str

    @Backoff(RETRY_EXCEPTIONS)
    async def delete_cache(self, key: str) -> int:
        return await self.client.delete(key)

    def build_cache_key(self, prefix: str, *key_args: Any) -> str:  # noqa: ANN401
        key = ":".join(map(str, key_args))
        return f"{prefix}:{key}"


def get_redis_client() -> CacheClientInterface:
    return RedisCacheClient(client)
