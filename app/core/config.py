"""Application configuration loaded from environment variables."""

import json
from functools import lru_cache
from typing import Any

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql://postgres:password@127.0.0.1:5432/marketing_cal",
        alias="DATABASE_URL",
    )
    test_database_url: str | None = Field(default=None, alias="TEST_DATABASE_URL")

    jwt_secret: str = Field(
        default="change-me-to-a-long-random-secret",
        validation_alias=AliasChoices("JWT_SECRET", "JWT_SECRET_KEY", "SECRET_KEY"),
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    auth_strategy: str = Field(default="jwt", alias="AUTH_STRATEGY")

    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="CORS_ORIGINS",
    )
    environment: str = Field(default="development", alias="ENVIRONMENT")
    rate_limit_default: str = Field(default="100/minute", alias="RATE_LIMIT_DEFAULT")

    klaviyo_api_key: str = Field(default="", alias="KLAVIYO_API_KEY")
    password_reset_token_expire_hours: int = Field(
        default=24,
        alias="PASSWORD_RESET_TOKEN_EXPIRE_HOURS",
    )
    klaviyo_max_retries: int = Field(default=3, alias="KLAVIYO_MAX_RETRIES")
    frontend_reset_url: str = Field(
        default="http://localhost:3000/reset-password",
        alias="FRONTEND_RESET_URL",
    )
    organization_name: str = Field(
        default="Marketing Content Calendar",
        alias="ORGANIZATION_NAME",
    )
    klaviyo_performance_enabled: bool = Field(
        default=False,
        alias="KLAVIYO_PERFORMANCE_ENABLED",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        """Parse CORS_ORIGINS from JSON array string or comma-separated list."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                parsed = json.loads(stripped)
                return [str(item) for item in parsed]
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
