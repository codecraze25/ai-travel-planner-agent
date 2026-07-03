from __future__ import annotations

from typing import Any

from redis.asyncio import Redis

from app.core.config import Settings, get_settings

_redis: Redis[Any] | None = None


def get_redis(settings: Settings | None = None) -> Redis[Any]:
    global _redis
    if _redis is None:
        cfg = settings or get_settings()
        _redis = Redis.from_url(cfg.redis_url, decode_responses=True)
    return _redis


async def check_redis(settings: Settings | None = None) -> bool:
    try:
        client = get_redis(settings)
        return bool(await client.ping())
    except Exception:
        return False


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None
