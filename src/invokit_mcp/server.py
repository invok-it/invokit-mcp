"""invokit-mcp server — FastMCP instance and entry point."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from invokit_mcp.client import InvokitClient

mcp = FastMCP(
    "invokit",
    instructions=(
        "Search, evaluate, and invoke AI agent tools from the invok.it marketplace.\n\n"
        "Resource types:\n"
        "- Tools: Individual API endpoints (e.g. text summarizer, image generator)\n"
        "- Skills: Multi-tool workflows that chain tools together\n"
        "- Apps: Deterministic pipelines that run multiple steps in one call\n"
        "- MCP Servers: Model Context Protocol servers you can install in Claude/Cursor/VS Code\n\n"
        "Recommended workflow:\n"
        "1. search_tools — find tools matching your task\n"
        "2. get_tool_quality — evaluate reliability (overall 0-100 score with signal breakdown)\n"
        "3. check_usage — verify you have remaining API quota\n"
        "4. invoke_tool — call the tool (returns output + invocation metadata)\n"
        "5. submit_outcome — report quality feedback using the invocation ID\n\n"
        "If a tool fails or its circuit breaker is open, use get_tool_alternatives "
        "to find a replacement. For detailed latency percentiles and raw metrics, "
        "use get_tool_metrics."
    ),
)

# Singleton API client — created on first use
_client: InvokitClient | None = None


def get_client() -> InvokitClient:
    """Return the shared API client (lazy-initialised)."""
    global _client
    if _client is None:
        _client = InvokitClient()
    return _client


# Import tool modules so their @mcp.tool() decorators register
import invokit_mcp.tools.discovery  # noqa: E402, F401
import invokit_mcp.tools.invoke  # noqa: E402, F401
import invokit_mcp.tools.quality  # noqa: E402, F401
import invokit_mcp.tools.platform  # noqa: E402, F401
import invokit_mcp.tools.usage  # noqa: E402, F401
import invokit_mcp.tools.outcomes  # noqa: E402, F401


def main() -> None:
    """Console-script entry point (stdio transport)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
