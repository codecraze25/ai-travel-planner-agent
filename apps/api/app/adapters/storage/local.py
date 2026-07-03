"""Local filesystem storage for host-local development (no MinIO/S3)."""

from __future__ import annotations

from pathlib import Path

from app.core.config import Settings, get_settings


def _root(settings: Settings | None = None) -> Path:
    cfg = settings or get_settings()
    path = Path(cfg.local_storage_path)
    if not path.is_absolute():
        api_root = Path(__file__).resolve().parents[3]
        path = api_root / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def put_object(key: str, data: bytes, content_type: str = "application/pdf") -> None:
    del content_type  # unused for local files
    path = _root() / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def get_object_bytes(key: str) -> bytes:
    path = _root() / key
    return path.read_bytes()


def delete_object(key: str) -> None:
    path = _root() / key
    if path.exists():
        path.unlink()


def presigned_put_url(key: str, expires_in: int = 900) -> str:
    del expires_in
    # Host-local mode uploads via multipart API, not presigned URLs.
    return f"local://{key}"


async def check_storage(settings: Settings | None = None) -> bool:
    try:
        root = _root(settings)
        probe = root / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except Exception:
        return False
