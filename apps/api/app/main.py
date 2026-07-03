from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.adapters.db.session import init_database
from app.adapters.redis_client import close_redis
from app.adapters.storage.s3 import check_storage, create_s3_client, ensure_bucket
from app.api.middleware import CorrelationIdMiddleware
from app.api.routes import agent, documents, health, itinerary, travel, trips
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("api_starting", env=settings.app_env, version=__version__)

    try:
        await init_database()
        logger.info("database_ready", url=settings.database_url.split("://")[0])
    except Exception as exc:  # noqa: BLE001
        logger.warning("database_init_failed", error=str(exc))

    if settings.storage_backend.lower() == "local":
        ok = await check_storage(settings)
        logger.info("storage_ready", backend="local", ok=ok)
    else:
        try:
            client = create_s3_client(settings)
            ensure_bucket(client, settings.s3_bucket)
            await check_storage(settings)
            logger.info("storage_ready", bucket=settings.s3_bucket)
        except Exception as exc:  # noqa: BLE001 — startup should not crash on storage
            logger.warning("storage_bootstrap_failed", error=str(exc))

    yield

    await close_redis()
    logger.info("api_stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="AI Travel Planner API",
        version=__version__,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(CorrelationIdMiddleware)

    app.include_router(health.router)
    app.include_router(trips.router)
    app.include_router(travel.router)
    app.include_router(documents.router)
    app.include_router(agent.router)
    app.include_router(itinerary.router)

    return app


app = create_app()
