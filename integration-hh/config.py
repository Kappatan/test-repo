from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "recruitment-integration-hh"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8001

    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    rabbitmq_queue: str = "hh.responses"

    hh_webhook_api_key: str = Field(
        default="change-me",
        description="Shared secret for X-API-Key validation.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

