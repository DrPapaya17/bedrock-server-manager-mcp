"""FastMCP Server for Bedrock Server Manager automatically generated from OpenAPI."""

import json
import logging
from pathlib import Path
import sys
from typing import Any, Dict, Optional

from fastmcp import FastMCP
import httpx

from bsm_mcp.auth import BSMBearerAuth
from bsm_mcp.config import Settings, settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("bsm_mcp.server")

DEFAULT_SPEC_PATH = Path(__file__).parent / "default_openapi.json"


def load_openapi_spec(cfg: Settings) -> Dict[str, Any]:
    """
    Load the OpenAPI specification for Bedrock Server Manager.

    Priority:
    1. Custom path/URL provided in BSM_OPENAPI_PATH
    2. Live fetch from {BSM_URL}/openapi.json
    3. Fallback to bundled default_openapi.json
    """
    # 1. Custom path or URL
    if cfg.bsm_openapi_path:
        path_str = cfg.bsm_openapi_path
        if path_str.startswith("http://") or path_str.startswith("https://"):
            logger.info("Fetching custom OpenAPI specification from URL: %s", path_str)
            try:
                resp = httpx.get(path_str, timeout=cfg.bsm_timeout, verify=cfg.bsm_verify_ssl)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                logger.error("Failed to fetch OpenAPI from %s: %s", path_str, e)
                raise
        else:
            local_path = Path(path_str)
            logger.info("Loading custom OpenAPI specification from file: %s", local_path)
            if not local_path.is_file():
                raise FileNotFoundError(f"OpenAPI spec file not found: {local_path}")
            return json.loads(local_path.read_text(encoding="utf-8"))

    # 2. Live fetch from running BSM instance
    live_url = f"{cfg.bsm_url.rstrip('/')}/openapi.json"
    headers: Dict[str, str] = {}
    if cfg.bsm_token:
        headers["Authorization"] = f"Bearer {cfg.bsm_token}"

    try:
        resp = httpx.get(live_url, headers=headers, timeout=5.0, verify=cfg.bsm_verify_ssl)
        if resp.status_code == 200:
            spec = resp.json()
            logger.info("Successfully fetched live OpenAPI spec with %d paths", len(spec.get("paths", {})))
            return spec
        logger.warning(
            "BSM server responded with HTTP %d when requesting %s. Falling back to default spec.",
            resp.status_code,
            live_url,
        )
    except Exception as e:
        logger.info(
            "Could not connect to live BSM instance at %s (%s). Falling back to bundled OpenAPI spec.",
            live_url,
            e,
        )

    # 3. Bundled fallback
    if DEFAULT_SPEC_PATH.is_file():
        logger.info("Using bundled default OpenAPI specification: %s", DEFAULT_SPEC_PATH)
        return json.loads(DEFAULT_SPEC_PATH.read_text(encoding="utf-8"))

    raise RuntimeError("No OpenAPI specification available (live or bundled).")


def create_mcp_server(cfg: Optional[Settings] = None) -> FastMCP:
    """Create and configure the FastMCP instance from OpenAPI specification."""
    if cfg is None:
        cfg = settings

    spec = load_openapi_spec(cfg)

    auth = BSMBearerAuth(
        base_url=cfg.bsm_url,
        username=cfg.bsm_username,
        password=cfg.bsm_password,
        token=cfg.bsm_token,
        verify_ssl=cfg.bsm_verify_ssl,
    )

    client = httpx.AsyncClient(
        base_url=cfg.bsm_url.rstrip("/"),
        auth=auth,
        timeout=cfg.bsm_timeout,
        verify=cfg.bsm_verify_ssl,
    )

    mcp = FastMCP.from_openapi(
        openapi_spec=spec,
        client=client,
        name=cfg.server_name,
    )

    return mcp


def main() -> None:
    """CLI entrypoint for running the BSM MCP server."""
    try:
        server = create_mcp_server()
        server.run()
    except KeyboardInterrupt:
        logger.info("Shutting down BSM MCP server...")
        sys.exit(0)
    except Exception as e:
        logger.exception("Fatal error in BSM MCP server: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
