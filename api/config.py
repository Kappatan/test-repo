from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "recruitment-main-api"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str = "postgresql+psycopg://app:app@postgres:5432/recruitment"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    rabbitmq_queue: str = "hh.responses"
    rabbitmq_enabled: bool = True
    rabbitmq_reconnect_delay_seconds: int = Field(default=5, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
