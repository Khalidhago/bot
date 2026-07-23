"""Integration tests for the FastAPI application."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


class TestHealth:
    async def test_health_returns_ok(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    async def test_ready_returns_ok(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"


class TestAuthEndpoints:
    async def test_register_missing_fields(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422

    async def test_login_invalid_credentials_without_db(
        self, client: AsyncClient
    ) -> None:
        # Without a DB the service will raise a 500; we just confirm the route exists
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password"},
        )
        # Route exists (not 404)
        assert response.status_code != 404
