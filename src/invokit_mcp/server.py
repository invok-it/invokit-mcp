"""invokit-mcp server — FastMCP instance and entry point."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from invokit_mcp.client import InvokitClient

mcp = FastMCP(
    "invokit",
    instructions=(
        "invok.it gives your agent access to a marketplace of API tools. "
        "When a task requires live data, external services, or capabilities "
        "your agent cannot handle on its own (e.g. current weather, crypto prices, "
        "geocoding, random data generation), use invok.it to find and call a tool.\n\n"
        "Workflow: search_tools → invoke_tool.\n"
        "- search_tools returns quality scores and input schemas — "
        "you can invoke directly without extra lookups.\n"
        "- If a tool fails, use get_tool_alternatives to find a replacement.\n"
        "- Use check_usage to see remaining API quota."
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
