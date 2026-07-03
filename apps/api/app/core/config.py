from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_CONFIG_PATH = Path(__file__).resolve()
_API_DIR = _CONFIG_PATH.parents[2]
# Host checkout: apps/api/app/core/config.py → repo root is parents[4].
# Docker image: /app/app/core/config.py → only parents[0..3] exist.
_REPO_ROOT = _CONFIG_PATH.parents[4] if len(_CONFIG_PATH.parents) > 4 else _API_DIR
_ENV_FILES = (
    str(_API_DIR / ".env"),
    str(_REPO_ROOT / ".env"),
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="info", alias="LOG_LEVEL")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    # Host-local default: SQLite (no Docker). Docker Compose overrides to Postgres.
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/travel.db",
        alias="DATABASE_URL",
    )
    # Empty = Redis optional (host-local). Docker sets redis://redis:6379/0
    redis_url: str = Field(default="", alias="REDIS_URL")

    storage_backend: str = Field(default="local", alias="STORAGE_BACKEND")
    local_storage_path: str = Field(default="./data/uploads", alias="LOCAL_STORAGE_PATH")

    s3_endpoint: str = Field(default="http://localhost:9000", alias="S3_ENDPOINT")
    s3_access_key: str = Field(default="minioadmin", alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="minioadmin", alias="S3_SECRET_KEY")
    s3_bucket: str = Field(default="travel-docs", alias="S3_BUCKET")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")

    use_mock_providers: bool = Field(default=True, alias="USE_MOCK_PROVIDERS")
    use_mock_llm: bool = Field(default=True, alias="USE_MOCK_LLM")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")

    auth_disabled: bool = Field(default=True, alias="AUTH_DISABLED")
    dev_user_id: str = Field(default="dev-user", alias="DEV_USER_ID")
    dev_user_email: str = Field(default="demo@example.com", alias="DEV_USER_EMAIL")
    clerk_secret_key: str | None = Field(default=None, alias="CLERK_SECRET_KEY")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def redis_enabled(self) -> bool:
        return bool(self.redis_url.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
