from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="info", alias="LOG_LEVEL")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    database_url: str = Field(
        default="postgresql+asyncpg://travel:travel@localhost:5432/travel_planner",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    s3_endpoint: str = Field(default="http://localhost:9000", alias="S3_ENDPOINT")
    s3_access_key: str = Field(default="minioadmin", alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="minioadmin", alias="S3_SECRET_KEY")
    s3_bucket: str = Field(default="travel-docs", alias="S3_BUCKET")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")

    use_mock_providers: bool = Field(default=True, alias="USE_MOCK_PROVIDERS")

    auth_disabled: bool = Field(default=True, alias="AUTH_DISABLED")
    dev_user_id: str = Field(default="dev-user", alias="DEV_USER_ID")
    dev_user_email: str = Field(default="demo@example.com", alias="DEV_USER_EMAIL")
    clerk_secret_key: str | None = Field(default=None, alias="CLERK_SECRET_KEY")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
