"""invokit-mcp server — FastMCP instance and entry point."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from invokit_mcp.client import InvokitClient

mcp = FastMCP(
    "invokit",
    instructions=(
        "Search, evaluate, and invoke AI agent tools from the invok.it marketplace. "
        "Discover tools, skills, apps, and MCP servers with quality signals."
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


def main() -> None:
    """Console-script entry point (stdio transport)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
