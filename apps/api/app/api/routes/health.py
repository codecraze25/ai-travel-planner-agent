from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.adapters.db.session import check_database
from app.adapters.redis_client import check_redis
from app.adapters.storage.s3 import check_storage
from app.core.config import get_settings

router = APIRouter(tags=["ops"])


class HealthResponse(BaseModel):
    status: str


class ReadyResponse(BaseModel):
    status: str
    checks: dict[str, bool]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness probe — process is up."""
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadyResponse)
async def ready() -> ReadyResponse:
    """Readiness probe — dependencies are reachable."""
    settings = get_settings()
    checks = {
        "database": await check_database(),
        "redis": await check_redis(settings),
        "storage": await check_storage(settings),
    }
    status = "ok" if all(checks.values()) else "degraded"
    return ReadyResponse(status=status, checks=checks)
