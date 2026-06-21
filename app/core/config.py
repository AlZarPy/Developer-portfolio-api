from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Developer Portfolio API"
    app_env: str = "local"
    debug: bool = False
    api_prefix: str = "/api"
    public_base_url: AnyHttpUrl | None = None

    database_url: str = "sqlite+aiosqlite:///./data/app.db"
    auto_create_tables: bool = True

    cors_origins: str = "http://localhost:8000"
    contact_rate_limit: str = "5/minute"

    log_level: str = "INFO"
    log_file: Path = Path("logs/app.log")

    ai_provider: str = "mock"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash-lite"
    ai_timeout_seconds: float = 8.0

    resend_api_key: str | None = None
    email_from: str = "Developer Portfolio <onboarding@resend.dev>"
    owner_email: str | None = None
    email_timeout_seconds: float = 8.0
    email_enabled: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def is_test(self) -> bool:
        return self.app_env.lower() == "test"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
