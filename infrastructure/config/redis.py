from dataclasses import Field

from domain.base import BaseModel


class RedisConfig(BaseModel):
    host: str = Field(alias="REDIS_HOST")
    port: int = Field(alias="REDIS_PORT")
    db: int = Field(alias="REDIS_DB")