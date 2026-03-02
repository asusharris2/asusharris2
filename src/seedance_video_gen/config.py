from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    fal_api_key: str = Field(..., alias="FAL_API_KEY")
    fal_model: str = Field(default="fal-ai/seedance/v2", alias="FAL_MODEL")
    fal_base_url: str = Field(default="https://fal.run", alias="FAL_BASE_URL")
    request_timeout_seconds: float = Field(default=30.0, alias="REQUEST_TIMEOUT_SECONDS")
    poll_interval_seconds: float = Field(default=2.0, alias="POLL_INTERVAL_SECONDS")
    max_poll_seconds: float = Field(default=600.0, alias="MAX_POLL_SECONDS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
