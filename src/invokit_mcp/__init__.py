"""invokit-mcp — MCP server for the invok.it AI agent tool marketplace."""

__version__ = "0.1.0"

from invokit_mcp.backend import Backend
from invokit_mcp.client import HttpBackend, InvokeResult, InvokitClient
from invokit_mcp.server import get_backend, set_backend, set_backend_for_request, get_client

__all__ = [
    "Backend",
    "HttpBackend",
    "InvokeResult",
    "get_backend",
    "set_backend",
    "set_backend_for_request",
    # Backward-compat
    "InvokitClient",
    "get_client",
]
