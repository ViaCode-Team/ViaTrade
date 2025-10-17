from application.base.repository import BaseRepository
from application.interface.icache import ICache
from domain.entity.base import BaseModel


class RepositoryFacade[T: BaseModel]:
    def __init__(self, repo: BaseRepository[T], cache: ICache, ttl: int = 60) -> None:
        self.repo = repo
        self.cache = cache
        self.ttl = ttl

    def _key(self, suffix: str) -> str:
        return f"{self.repo.model.__name__}:{suffix}"

    async def get_by_id(self, obj_id: int) -> T | None:
        key = self._key(f"id:{obj_id}")
        cached = await self.cache.get(key)
        if cached:
            return cached

        obj = await self.repo.get_by_id(obj_id)
        if obj:
            await self.cache.set(key, obj, ttl=self.ttl)
        return obj

    async def get_all(self) -> list[T]:
        key = self._key("all")
        cached = await self.cache.get(key)
        if cached:
            return cached

        objs = await self.repo.get_all()
        await self.cache.set(key, objs, ttl=self.ttl)
        return objs

    async def add(self, obj: T) -> T:
        result = await self.repo.add(obj)
        await self.cache.delete(self._key("all"))
        return result

    async def update(self, obj_id: int, **kwargs) -> T | None:
        result = await self.repo.update(obj_id, **kwargs)
        await self.cache.delete(self._key(f"id:{obj_id}"))
        await self.cache.delete(self._key("all"))
        return result

    async def delete(self, obj_id: int) -> None:
        await self.repo.delete(obj_id)
        await self.cache.delete(self._key(f"id:{obj_id}"))
        await self.cache.delete(self._key("all"))
