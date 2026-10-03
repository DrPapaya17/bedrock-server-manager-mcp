"""Configuration settings for BSM MCP Server."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """BSM MCP server configuration settings."""

    bsm_url: str = "http://localhost:8000"
    bsm_username: str = "admin"
    bsm_password: str = ""
    bsm_token: Optional[str] = None
    bsm_openapi_path: Optional[str] = None
    bsm_timeout: float = 30.0
    bsm_verify_ssl: bool = True
    server_name: str = "Bedrock Server Manager"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
