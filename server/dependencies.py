from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from redis.asyncio import Redis

from infrastructure.config.app import AppConfig

config = AppConfig()

engine = create_async_engine(
    config.db.build_url(),
    echo=config.app_mode == "development"
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
redis_client: Redis | None = None


async def get_session():
    async with async_session() as session:
        yield session


async def get_redis():
    return redis_client