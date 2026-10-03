# Bedrock Server Manager MCP Server (`bsm-mcp`)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server for [Bedrock Server Manager (BSM)](https://github.com/DMedina559/bedrock-server-manager), enabling AI assistants (such as Antigravity, Claude Desktop, Cursor, and OpenHands) to manage Minecraft Bedrock Dedicated Servers via natural language.

## Features

- **OpenAPI Powered**: Automatically discovers and binds all endpoints from Bedrock Server Manager's OpenAPI specification (`/openapi.json`).
- **Dynamic Endpoint Support**: Automatically adapts to any custom endpoints added by BSM plugins or server updates.
- **Automated Authentication**: Seamlessly authenticates with BSM's `/auth/token` endpoint using JWT Bearer tokens and handles automatic token refreshing.
- **Server Lifecycle & Commands**: Start, stop, restart, run commands (`say`, `kick`, `whitelist`), monitor resource stats, manage backups, and configure allowlists.

## Quick Start

### Using `uvx` (Recommended)

No installation required. Add `bsm-mcp` directly to your MCP client configuration (e.g. `mcp_config.json` or `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "bedrock-server-manager": {
      "command": "uvx",
      "args": ["bedrock-server-manager-mcp"],
      "env": {
        "BSM_URL": "http://localhost:8000",
        "BSM_USERNAME": "admin",
        "BSM_PASSWORD": "your-password"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `BSM_URL` | Base URL of your Bedrock Server Manager web instance | `http://localhost:8000` |
| `BSM_USERNAME` | BSM user account with appropriate permissions | `admin` |
| `BSM_PASSWORD` | Password for the user account | `""` |
| `BSM_TOKEN` | Optional pre-existing JWT access token | `None` |
| `BSM_OPENAPI_PATH` | Path or URL to OpenAPI spec (if using local file) | `None` (fetches from `/openapi.json`) |
| `BSM_TIMEOUT` | Request timeout in seconds | `30.0` |
| `BSM_VERIFY_SSL` | Verify SSL certificates when connecting over HTTPS | `true` |

## Development

```bash
# Clone the repository
git clone https://github.com/DrPapaya17/bedrock-server-manager-mcp.git
cd bedrock-server-manager-mcp

# Install dependencies using uv
uv sync --all-extras

# Run the MCP server
uv run bsm-mcp
```

## License

This project is licensed under the [MIT License](LICENSE).
