from dataclasses import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from infrastructure.config.database import DatabaseConfig
from infrastructure.config.redis import RedisConfig


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="_")

    app_mode: str = Field(alias="APP_MODE")       # dev / product
    data_mode: str = Field(alias="DATA_MODE")     # fake / real
    db: DatabaseConfig = DatabaseConfig()         # nested config
    redis: RedisConfig = RedisConfig()            # nested config