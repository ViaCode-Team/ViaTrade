from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from sqlalchemy.engine import URL

from infrastructure.config.database import DatabaseConfig
from infrastructure.config.redis import RedisConfig


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="forbid"
    )

    app_mode: str = Field(alias="APP_MODE")
    analyzer_mode: str = Field(alias="ANALYZER_MODE")
    secret_key: str = Field(alias="SECRET_KEY")
    db: DatabaseConfig
    redis: RedisConfig
