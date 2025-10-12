from dataclasses import Field

from sqlalchemy import URL

from domain.base import BaseModel


class DatabaseConfig(BaseModel):
    engine: str = Field(alias="DB_ENGINE")
    host: str = Field(alias="DB_HOST")
    name: str = Field(alias="DB_NAME")
    driver: str = Field(alias="DB_DRIVER")
    trusted_connection: str = Field(alias="DB_TRUSTED_CONNECTION")

    def build_url(self) -> URL:
        return URL.create(
            self.engine,
            host=self.host,
            database=self.name,
            query={
                "driver": self.driver,
                "trusted_connection": self.trusted_connection,
            },
        )
