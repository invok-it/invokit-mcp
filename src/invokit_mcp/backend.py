"""Backend protocol — abstraction for how MCP tools access the invok.it platform.

Two implementations exist:

- ``HttpBackend`` (this package): makes HTTP calls via httpx — used in
  standalone / stdio mode when the MCP server runs outside the platform.
- A direct backend (closed-source platform): calls the service layer
  without HTTP — used when the MCP server is embedded in the platform.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from invokit_mcp.client import InvokeResult

__all__ = ["Backend", "InvokeResult"]


@runtime_checkable
class Backend(Protocol):
    """Interface that MCP tool handlers use to access the invok.it platform.

    Every method mirrors the HTTP-level operations the tool handlers need.
    Return conventions:

    - On success: ``dict``, ``list``, or ``InvokeResult``
    - On failure: a plain ``str`` starting with ``"Error"``
    """

    @property
    def has_api_key(self) -> bool:
        """True when authentication credentials are available."""
        ...

    async def get(
        self,
        path: str,
        *,
        params: dict | None = None,
        require_auth: bool = False,
    ) -> dict | list | str:
        ...

    async def post(
        self,
        path: str,
        *,
        json_body: dict | None = None,
        params: dict | None = None,
        require_auth: bool = False,
        raw_response: bool = False,
    ) -> dict | list | str:
        ...

    async def invoke(
        self,
        path: str,
        json_body: dict | None = None,
    ) -> InvokeResult | str:
        ...

    async def delete(
        self,
        path: str,
        *,
        require_auth: bool = False,
    ) -> dict | list | str:
        ...
