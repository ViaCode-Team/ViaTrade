
from pydantic_settings import BaseSettings
from sqlalchemy import URL


class DatabaseConfig(BaseSettings):
    DB_ENGINE: str
    DB_HOST: str
    DB_NAME: str
    DB_DRIVER: str
    DB_TRUSTED_CONNECTION: str

    def build_url(self) -> str:
        return str(
            URL.create(
                drivername=self.DB_ENGINE,
                username=None,
                password=None,
                host=self.DB_HOST,
                database=self.DB_NAME,
                query={"driver": self.DB_DRIVER, "trusted_connection": self.DB_TRUSTED_CONNECTION}
            )
        )
