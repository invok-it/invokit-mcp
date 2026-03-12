"""Async HTTP client for the invok.it API."""

from __future__ import annotations

import json
import httpx

from invokit_mcp import __version__


class InvokitClient:
    """Thin httpx wrapper that handles auth, errors, and ResponseEnvelope unwrapping."""

    def __init__(self) -> None:
        base_url = "https://api.invok.it"
        api_key = os.environ.get("INVOKIT_API_KEY")

        headers: dict[str, str] = {"User-Agent": f"invokit-mcp/{__version__}"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=30.0,
        )
        self._has_api_key = api_key is not None

    @property
    def has_api_key(self) -> bool:
        return self._has_api_key

    # ------------------------------------------------------------------
    # Core request
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json_body: dict | None = None,
        require_auth: bool = False,
        raw_response: bool = False,
    ) -> dict | list | str:
        """Make an API request.

        Returns unwrapped ``data`` from the ResponseEnvelope, or the full
        body when *raw_response* is True.  On error returns a descriptive
        string instead of raising.
        """
        if require_auth and not self._has_api_key:
            return (
                "Error: This action requires authentication. "
                "Set the INVOKIT_API_KEY environment variable with your ik- API key."
            )

        # Strip None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        try:
            resp = await self._client.request(method, path, params=params, json=json_body)
        except httpx.HTTPError as exc:
            return f"Error: Could not reach the invok.it API — {exc}"

        if resp.status_code >= 400:
            return self._format_error(resp)

        if raw_response:
            # invoke endpoint returns the upstream tool's raw response
            content_type = resp.headers.get("content-type", "")
            if "application/json" in content_type:
                return resp.json()
            return resp.text

        body = resp.json()
        return body.get("data", body)

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    async def get(self, path: str, *, params: dict | None = None, require_auth: bool = False):
        return await self._request("GET", path, params=params, require_auth=require_auth)

    async def post(
        self,
        path: str,
        *,
        json_body: dict | None = None,
        params: dict | None = None,
        require_auth: bool = False,
        raw_response: bool = False,
    ):
        return await self._request(
            "POST", path, json_body=json_body, params=params,
            require_auth=require_auth, raw_response=raw_response,
        )

    async def delete(self, path: str, *, require_auth: bool = False):
        return await self._request("DELETE", path, require_auth=require_auth)

    # ------------------------------------------------------------------
    # Error formatting
    # ------------------------------------------------------------------

    @staticmethod
    def _format_error(resp: httpx.Response) -> str:
        try:
            body = resp.json()
            err = body.get("error", {})
            msg = err.get("message", resp.text)
            suggestion = err.get("suggestion")
            parts = [f"Error ({resp.status_code}): {msg}"]
            if suggestion:
                parts.append(f"Suggestion: {suggestion}")
            return "\n".join(parts)
        except Exception:
            return f"Error ({resp.status_code}): {resp.text}"
