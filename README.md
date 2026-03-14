# invokit-mcp

Official MCP server for [invok.it](https://invok.it) — the API marketplace for AI agents.

Search, evaluate, and invoke AI tools directly from Claude Desktop, Cursor, VS Code, or any MCP-compatible client.

## Quick Start

Add the following to your MCP client configuration:

```json
{
  "mcpServers": {
    "invokit": {
      "url": "https://api.invok.it/mcp",
      "headers": {
        "Authorization": "Bearer ik-your-api-key"
      }
    }
  }
}
```

Get your API key at [invok.it/dashboard/api-keys](https://invok.it/dashboard/api-keys).

### Claude Desktop

1. Open **Settings → Developer → Edit Config**
2. Paste the config above (replace `ik-your-api-key` with your key)
3. Restart Claude Desktop

### Cursor

1. Open **Settings → MCP**
2. Click **Add new MCP server**
3. Paste the config above

### VS Code

Add to `.vscode/mcp.json` in your project:

```json
{
  "mcpServers": {
    "invokit": {
      "url": "https://api.invok.it/mcp",
      "headers": {
        "Authorization": "Bearer ik-your-api-key"
      }
    }
  }
}
```

## Available Tools (14)

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
