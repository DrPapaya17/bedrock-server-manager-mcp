"""Tests for BSM MCP Server generation."""

import asyncio
import json
import pytest
from bsm_mcp.config import Settings
from bsm_mcp.server import create_mcp_server, load_openapi_spec


def test_load_default_openapi_spec():
    cfg = Settings(bsm_url="http://non-existent-host:9999")
    spec = load_openapi_spec(cfg)
    assert "paths" in spec
    assert "/api/server/{server_name}/start" in spec["paths"]
    assert "/api/server/{server_name}/send_command" in spec["paths"]


def test_load_custom_openapi_file(tmp_path):
    custom_spec = {
        "openapi": "3.0.0",
        "info": {"title": "Custom Spec", "version": "1.0"},
        "paths": {
            "/custom/endpoint": {
                "get": {
                    "operationId": "custom_endpoint",
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
    }
    spec_file = tmp_path / "custom_openapi.json"
    spec_file.write_text(json.dumps(custom_spec), encoding="utf-8")

    cfg = Settings(bsm_openapi_path=str(spec_file))
    spec = load_openapi_spec(cfg)
    assert "/custom/endpoint" in spec["paths"]

    server = create_mcp_server(cfg)
    tools = asyncio.run(server.list_tools())
    assert any(t.name == "custom_endpoint" for t in tools)


def test_create_mcp_server_tools():
    cfg = Settings(bsm_url="http://non-existent-host:9999", server_name="Test BSM Server")
    server = create_mcp_server(cfg)
    assert server.name == "Test BSM Server"

    tools = asyncio.run(server.list_tools())
    tool_names = [t.name for t in tools]

    expected = [
        "list_all_servers",
        "get_server_status",
        "start_server",
        "stop_server",
        "restart_server",
        "send_command",
        "create_backup",
        "list_backups",
        "get_allowlist",
        "add_to_allowlist",
        "remove_from_allowlist",
        "get_permissions",
        "set_permission",
    ]

    for exp in expected:
        assert exp in tool_names, f"Expected tool '{exp}' not found in generated tools: {tool_names}"
