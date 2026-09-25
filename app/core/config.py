"""Application configuration loaded from environment variables."""

import json
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(
        ...,
        description="PostgreSQL connection URL.",
    )
    jwt_secret: str = Field(
        ...,
        validation_alias="JWT_SECRET",
        description="Secret key for signing JWT tokens.",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        validation_alias="JWT_ALGORITHM",
        description="JWT signing algorithm.",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
        description="Access token lifetime in minutes.",
    )
    refresh_token_expire_days: int = Field(
        default=7,
        validation_alias="REFRESH_TOKEN_EXPIRE_DAYS",
        description="Refresh token lifetime in days.",
    )
    auth_strategy: str = Field(
        default="jwt",
        validation_alias="AUTH_STRATEGY",
        description="Authentication strategy identifier.",
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
        ],
        validation_alias="CORS_ORIGINS",
        description="Allowed CORS origins.",
    )
    environment: str = Field(
        default="development",
        validation_alias="ENVIRONMENT",
        description="Runtime environment name.",
    )
    klaviyo_api_key: str = Field(
        default="",
        validation_alias="KLAVIYO_API_KEY",
        description="Klaviyo API key for transactional email.",
    )
    klaviyo_api_base_url: str = Field(
        default="https://a.klaviyo.com",
        validation_alias="KLAVIYO_API_BASE_URL",
        description="Klaviyo API base URL.",
    )
    klaviyo_api_revision: str = Field(
        default="2024-10-15",
        validation_alias="KLAVIYO_API_REVISION",
        description="Klaviyo API revision header value.",
    )
    frontend_reset_url: str = Field(
        default="http://localhost:3000/reset-password",
        validation_alias="FRONTEND_RESET_URL",
        description="Frontend URL for password reset links.",
    )
    password_reset_token_expire_minutes: int = Field(
        default=60,
        validation_alias="PASSWORD_RESET_TOKEN_EXPIRE_MINUTES",
        description="Password reset token lifetime in minutes.",
    )
    rate_limit_default: str = Field(
        default="100/minute",
        validation_alias="RATE_LIMIT_DEFAULT",
        description="Default rate limit for API endpoints.",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        """Parse CORS origins from JSON string or list."""
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                return json.loads(stripped)
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: str) -> str:
        """Ensure JWT secret is non-empty."""
        if not value or not value.strip():
            raise ValueError("JWT_SECRET must be set and non-empty.")
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
