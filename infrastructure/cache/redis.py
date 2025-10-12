import json
from typing import Any
from redis.asyncio import Redis

from application.interface.icache import ICache


class RedisCache(ICache):
    def __init__(self, client: Redis, namespace: str = "default") -> None:
        self._client = client
        self._namespace = namespace

    def _make_key(self, key: str) -> str:
        return f"{self._namespace}:{key}"

    async def get(self, key: str) -> Any:
        value = await self._client.get(self._make_key(key))
        if value is None:
            return None
        return json.loads(value)

    async def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        data = json.dumps(value, default=str)
        await self._client.set(self._make_key(key), data, ex=ttl)

    async def delete(self, key: str) -> None:
        await self._client.delete(self._make_key(key))

    async def clear(self) -> None:
        pattern = f"{self._namespace}:*"
        keys = await self._client.keys(pattern)
        if keys:
            await self._client.delete(*keys)
