"""Authentication handler for Bedrock Server Manager."""

import logging
from typing import AsyncGenerator, Generator, Optional
import httpx

logger = logging.getLogger("bsm_mcp.auth")


class BSMBearerAuth(httpx.Auth):
    """Handles Bearer token authentication and automatic refresh against BSM."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        token: Optional[str] = None,
        verify_ssl: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.token = token
        self.verify_ssl = verify_ssl

    async def _fetch_token(self) -> Optional[str]:
        """Obtain a new JWT token from the /auth/token endpoint."""
        if not self.username or not self.password:
            return None

        token_url = f"{self.base_url}/auth/token"
        logger.debug("Requesting access token from %s", token_url)
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            try:
                response = await client.post(
                    token_url,
                    data={
                        "username": self.username,
                        "password": self.password,
                        "remember_me": True,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                data = response.json()
                self.token = data.get("access_token")
                logger.info("Successfully acquired BSM authentication token")
                return self.token
            except Exception as e:
                logger.warning("Failed to authenticate with BSM: %s", e)
                return None

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        """Synchronous auth flow fallback."""
        if self.token:
            request.headers["Authorization"] = f"Bearer {self.token}"
        yield request

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        """Asynchronous auth flow with automatic token acquisition and retry."""
        if not self.token and self.username and self.password:
            await self._fetch_token()

        if self.token:
            request.headers["Authorization"] = f"Bearer {self.token}"

        response = yield request

        # If unauthorized, try to refresh token and replay request once
        if response.status_code == 401 and self.username and self.password:
            logger.info("Received 401 Unauthorized; attempting to re-authenticate...")
            self.token = None
            new_token = await self._fetch_token()
            if new_token:
                request.headers["Authorization"] = f"Bearer {new_token}"
                yield request
