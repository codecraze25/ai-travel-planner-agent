from __future__ import annotations

from typing import Any

from app.core.config import Settings, get_settings

_redis: Any | None = None


def get_redis(settings: Settings | None = None) -> Any:
    global _redis
    cfg = settings or get_settings()
    if not cfg.redis_enabled:
        raise RuntimeError("Redis is not configured")
    if _redis is None:
        from redis.asyncio import Redis

        _redis = Redis.from_url(cfg.redis_url, decode_responses=True)
    return _redis


async def check_redis(settings: Settings | None = None) -> bool:
    cfg = settings or get_settings()
    if not cfg.redis_enabled:
        # Host-local mode: Redis is optional; report healthy when disabled.
        return True
    try:
        client = get_redis(cfg)
        return bool(await client.ping())
    except Exception:
        return False


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None
