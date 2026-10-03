"""Tests for BSMBearerAuth."""

import pytest
import respx
import httpx
from bsm_mcp.auth import BSMBearerAuth


@pytest.mark.asyncio
async def test_bsm_bearer_auth_flow():
    base_url = "http://test-bsm:8000"
    auth = BSMBearerAuth(base_url=base_url, username="admin", password="password123")

    with respx.mock(base_url=base_url) as respx_mock:
        # Mock auth endpoint
        respx_mock.post("/auth/token").respond(
            200,
            json={"access_token": "mock-jwt-token-12345", "token_type": "bearer"},
        )
        # Mock API endpoint
        api_route = respx_mock.get("/api/application/system_and_app_info").respond(
            200, json={"version": "4.0.0"}
        )

        async with httpx.AsyncClient(base_url=base_url, auth=auth) as client:
            resp = await client.get("/api/application/system_and_app_info")
            assert resp.status_code == 200
            assert resp.json() == {"version": "4.0.0"}

        # Verify Authorization header was sent with the bearer token
        assert api_route.called
        assert api_route.calls.last.request.headers["Authorization"] == "Bearer mock-jwt-token-12345"
