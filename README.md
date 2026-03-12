# invokit-mcp

Official MCP server for [invok.it](https://invok.it) — the API marketplace for AI agents.

Search, evaluate, and invoke AI tools directly from Claude Desktop, Cursor, VS Code, or any MCP-compatible client.

## Installation

### Using uvx (recommended, no install needed)

```bash
uvx invokit-mcp
```

### Using pip

```bash
pip install invokit-mcp
```

### Using uv

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
      "command": "uvx",
      "args": ["invokit-mcp"],
      "env": {
        "INVOKIT_API_KEY": "ik-your-api-key"
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
      "command": "uvx",
      "args": ["invokit-mcp"],
      "env": {
        "INVOKIT_API_KEY": "ik-your-api-key"
      }
    }
  }
}
```

### VS Code

Add to your VS Code settings (`.vscode/mcp.json`):

```json
{
  "mcpServers": {
    "invokit": {
      "command": "uvx",
      "args": ["invokit-mcp"],
      "env": {
        "INVOKIT_API_KEY": "ik-your-api-key"
      }
    }
  }
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `INVOKIT_API_KEY` | For invocation | Your `ik-` API key from [invok.it](https://invok.it/dashboard/api-keys). Not needed for search/discovery. |

## Available Tools (17)

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

### Quality & Feedback
| Tool | Description |
|------|-------------|
| `get_tool_quality` | Quality score breakdown (success rate, schema honesty, latency) |
| `get_tool_metrics` | Performance metrics (latency percentiles, error rate, uptime) |
| `get_tool_alternatives` | Find type-compatible alternative tools |
| `submit_outcome` | Submit quality feedback after invoking a tool (improves rankings) |

### Platform
| Tool | Description |
|------|-------------|
| `check_usage` | Check your current API quota, usage, and remaining calls |
| `get_manifest` | Platform capabilities, endpoints, and rate limits |

### Recommended Workflow

```
search_tools → get_tool_quality → invoke_tool → submit_outcome
```

1. **Search** for tools matching your task
2. **Evaluate** quality scores to pick the best tool
3. **Check** your usage quota with `check_usage`
4. **Invoke** the tool
5. **Submit** quality feedback via `submit_outcome` to improve rankings
