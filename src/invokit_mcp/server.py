"""invokit-mcp server — FastMCP instance and entry point."""

from __future__ import annotations

import contextvars

from mcp.server.fastmcp import FastMCP

from invokit_mcp.backend import Backend
from invokit_mcp.client import HttpBackend, auth_token_var

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

# ---------------------------------------------------------------------------
#  Backend management
# ---------------------------------------------------------------------------

# Per-request backend override (used in hosted mode where each request has
# its own authenticated DirectBackend).
_backend_var: contextvars.ContextVar[Backend | None] = contextvars.ContextVar(
    "invokit_backend", default=None
)

# Global fallback backend — defaults to HttpBackend on first use
_backend: Backend | None = None


def set_backend(backend: Backend) -> None:
    """Set the global backend instance.

    Call this at startup if you want to replace the default ``HttpBackend``.
    For per-request backends (e.g. hosted mode with per-user auth), use
    ``set_backend_for_request`` instead.
    """
    global _backend
    _backend = backend


def set_backend_for_request(backend: Backend) -> contextvars.Token:
    """Set a per-request backend override.

    Returns a token that **must** be passed to ``_backend_var.reset()``
    when the request is done.
    """
    return _backend_var.set(backend)


def get_backend() -> Backend:
    """Return the active backend.

    Resolution order:
    1. Per-request override (``_backend_var``, set by hosted middleware)
    2. Global override (``set_backend()``)
    3. Default ``HttpBackend`` (lazy-initialised)
    """
    per_request = _backend_var.get()
    if per_request is not None:
        return per_request

    global _backend
    if _backend is None:
        _backend = HttpBackend()
    return _backend


# Backward-compat alias
def get_client() -> Backend:
    """Deprecated — use ``get_backend()``."""
    return get_backend()


# ---------------------------------------------------------------------------
#  ASGI middleware: extract Bearer token from HTTP requests → contextvar
#  (used in standalone HTTP/SSE mode — the hosted backend replaces this)
# ---------------------------------------------------------------------------

class _AuthExtractMiddleware:
    """ASGI middleware that pulls the Bearer token from incoming HTTP requests
    and stores it in ``auth_token_var`` so tools can forward it to API calls.

    This is a no-op for non-HTTP scopes (e.g. stdio transport).
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:]
            ctx = auth_token_var.set(token)
            try:
                await self.app(scope, receive, send)
            finally:
                auth_token_var.reset(ctx)
            return

        await self.app(scope, receive, send)


# Monkey-patch streamable_http_app to wrap with auth middleware
_original_streamable_http_app = FastMCP.streamable_http_app


def _patched_streamable_http_app(self):
    app = _original_streamable_http_app(self)
    return _AuthExtractMiddleware(app)


FastMCP.streamable_http_app = _patched_streamable_http_app  # type: ignore[assignment]

# Also patch sse_app for SSE transport
_original_sse_app = FastMCP.sse_app


def _patched_sse_app(self):
    app = _original_sse_app(self)
    return _AuthExtractMiddleware(app)


FastMCP.sse_app = _patched_sse_app  # type: ignore[assignment]


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
