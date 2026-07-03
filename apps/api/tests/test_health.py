from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Correlation-ID" in response.headers


@pytest.mark.asyncio
async def test_health_uses_incoming_correlation_id(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"X-Correlation-ID": "test-cid-123"})
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == "test-cid-123"


@pytest.mark.asyncio
async def test_ready_all_healthy(client: AsyncClient) -> None:
    with (
        patch("app.api.routes.health.check_database", new=AsyncMock(return_value=True)),
        patch("app.api.routes.health.check_redis", new=AsyncMock(return_value=True)),
        patch("app.api.routes.health.check_storage", new=AsyncMock(return_value=True)),
    ):
        response = await client.get("/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"] == {"database": True, "redis": True, "storage": True}


@pytest.mark.asyncio
async def test_ready_degraded_when_dependency_down(client: AsyncClient) -> None:
    with (
        patch("app.api.routes.health.check_database", new=AsyncMock(return_value=True)),
        patch("app.api.routes.health.check_redis", new=AsyncMock(return_value=False)),
        patch("app.api.routes.health.check_storage", new=AsyncMock(return_value=True)),
    ):
        response = await client.get("/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["redis"] is False
