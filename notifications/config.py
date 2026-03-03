from functools import lru_cache

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "recruitment-notifications"
    debug: bool = False

    main_api_base_url: AnyHttpUrl = "http://api:8000"
    managers_new_responses_path: str = "/internal/managers/new-responses"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def managers_new_responses_url(self) -> str:
        return f"{self.main_api_base_url.rstrip('/')}{self.managers_new_responses_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()

