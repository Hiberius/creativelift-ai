from __future__ import annotations

from dataclasses import dataclass
import os
from uuid import UUID


def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "CreativeLift AI")
    app_env: str = os.getenv("APP_ENV", "development")
    environment: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    api_version: str = os.getenv("API_VERSION", "0.1.0")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./creativelift.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    cors_origins: list[str] = None  # type: ignore[assignment]
    request_body_limit_bytes: int = int(os.getenv("REQUEST_BODY_LIMIT_BYTES", "1048576"))
    api_key_pepper: str = os.getenv("API_KEY_PEPPER", "dev-pepper")
    demo_api_key: str = os.getenv("DEMO_API_KEY", "dev-api-key")
    demo_organization_id: UUID = UUID(os.getenv("DEMO_ORGANIZATION_ID", "00000000-0000-4000-8000-000000000001"))
    session_ttl_hours: int = int(os.getenv("SESSION_TTL_HOURS", "168"))
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "120"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    rate_limit_backend: str = os.getenv("RATE_LIMIT_BACKEND", "memory").lower()
    ai_provider: str = os.getenv("AI_PROVIDER", "mock")
    resource_repository_backend: str = os.getenv("RESOURCE_REPOSITORY_BACKEND", "memory").lower()
    openai_base_url: str = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "https://api.openai.com/v1")
    openai_api_key: str = os.getenv("OPENAI_COMPATIBLE_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_COMPATIBLE_MODEL", "gpt-4o-mini")

    def __post_init__(self) -> None:
        object.__setattr__(self, "cors_origins", _csv_env("CORS_ORIGINS", "http://localhost:3000"))


settings = Settings()


def get_settings() -> Settings:
    return settings
