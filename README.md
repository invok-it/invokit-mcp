# invokit-mcp

MCP server for the [invok.it](https://invok.it) AI agent tool marketplace.

Search, evaluate, and invoke AI tools directly from Claude Desktop, Cursor, VS Code, or any MCP-compatible client.

## Installation

```bash
pip install invokit-mcp
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install invokit-mcp
```

## Configuration

### Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "invokit": {
      "command": "invokit-mcp",
      "env": {
        "INVOKIT_API_KEY": "ik-your-key-here"
      }
    }
  }
}
```

### Cursor

Add to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "invokit": {
      "command": "invokit-mcp",
      "env": {
        "INVOKIT_API_KEY": "ik-your-key-here"
      }
    }
  }
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `INVOKIT_API_KEY` | No* | Your ik- API key from invok.it |

*\*Required for `invoke_tool`. Discovery and quality tools work without a key.*

## Available Tools (15)

### Discovery
| Tool | Description |
|------|-------------|
| `search_tools` | Semantic search for AI agent tools |
| `get_tool` | Get full details for a tool by slug |
| `list_categories` | List all categories with counts |
| `search_skills` | Search multi-tool workflow skills |
| `get_skill` | Get skill details with tool bindings |
| `search_apps` | Search deterministic step-pipeline apps |
| `get_app` | Get app details with execution steps |
| `search_mcp_servers` | Search MCP servers |
| `get_mcp_server` | Get MCP server details |
| `get_mcp_server_config` | Generate install config for Claude/Cursor/VS Code |

### Invocation
| Tool | Description |
|------|-------------|
| `invoke_tool` | Invoke a tool via transparent proxy (requires API key) |

### Quality & Analysis
| Tool | Description |
|------|-------------|
| `get_tool_quality` | Quality score breakdown (success rate, schema honesty, latency) |
| `get_tool_metrics` | Performance metrics (latency percentiles, error rate, uptime) |
| `get_tool_alternatives` | Find type-compatible alternative tools |

### Platform
| Tool | Description |
|------|-------------|
| `get_manifest` | Platform capabilities, endpoints, and rate limits |
