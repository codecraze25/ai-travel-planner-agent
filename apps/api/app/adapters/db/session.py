from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


def _database_url() -> str:
    settings = get_settings()
    url = settings.database_url
    if not url.startswith("sqlite"):
        return url
    # Resolve relative SQLite paths against apps/api so cwd does not matter.
    prefix = "sqlite+aiosqlite:///"
    if url.startswith(prefix):
        db_path = url[len(prefix) :]
        if db_path and db_path != ":memory:" and not Path(db_path).is_absolute():
            api_root = Path(__file__).resolve().parents[3]
            absolute = (api_root / db_path).resolve()
            absolute.parent.mkdir(parents=True, exist_ok=True)
            return f"{prefix}{absolute.as_posix()}"
    return url


settings = get_settings()
_db_url = _database_url()

_connect_args: dict[str, object] = {}
if _db_url.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_async_engine(
    _db_url,
    pool_pre_ping=not _db_url.startswith("sqlite"),
    echo=settings.app_env == "local",
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_database() -> None:
    """Create tables for host-local SQLite (Docker uses Alembic migrations)."""
    if not settings.database_url.startswith("sqlite"):
        return
    from app.adapters.db import models as _models  # noqa: F401 — register models
    from app.adapters.db.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def check_database() -> bool:
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
