"""Async HTTP client for the invok.it API."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import httpx

from invokit_mcp import __version__


@dataclass
class InvokeResult:
    """Result of a tool invocation, containing both the tool output and platform metadata."""

    body: str
    metadata: dict[str, str] = field(default_factory=dict)


class InvokitClient:
    """Thin httpx wrapper that handles auth, errors, and ResponseEnvelope unwrapping."""

    def __init__(self) -> None:
        base_url = os.environ.get("INVOKIT_API_BASE_URL", "https://api.invok.it")
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
    # Invoke (returns body + platform headers)
    # ------------------------------------------------------------------

    async def invoke(
        self,
        path: str,
        json_body: dict | None = None,
    ) -> InvokeResult | str:
        """Make an invoke request and return both the tool result and platform metadata.

        Unlike the standard request methods, this captures platform response
        headers (X-Invocation-Id, latency, circuit breaker status, etc.)
        alongside the tool's raw output.
        """
        if not self._has_api_key:
            return (
                "Error: This action requires authentication. "
                "Set the INVOKIT_API_KEY environment variable with your ik- API key."
            )

        try:
            resp = await self._client.request("POST", path, json=json_body or {})
        except httpx.HTTPError as exc:
            return f"Error: Could not reach the invok.it API — {exc}"

        if resp.status_code >= 400:
            return self._format_error(resp)

        # Capture platform metadata from response headers
        metadata: dict[str, str] = {}
        platform_headers = [
            "X-Invocation-Id",
            "X-Marketplace-Latency-Ms",
            "X-Marketplace-Tool-Version",
            "X-Circuit-Breaker-Status",
            "X-Quota-Charged",
        ]
        for header in platform_headers:
            value = resp.headers.get(header)
            if value:
                metadata[header] = value

        # Parse response body
        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            body = json.dumps(resp.json(), indent=2)
        else:
            body = resp.text

        return InvokeResult(body=body, metadata=metadata)

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
            code = err.get("code", "UNKNOWN")
            msg = err.get("message", resp.text)
            suggestion = err.get("suggestion")
            severity = err.get("severity")
            retry_after = err.get("retry_after")

            parts = [f"Error ({resp.status_code}) [{code}]: {msg}"]
            if suggestion:
                parts.append(f"Suggestion: {suggestion}")
            if severity == "transient" and retry_after:
                parts.append(f"Retry after: {retry_after}s")

            # Surface alternative tools (e.g. on 503 circuit breaker open)
            alternatives = body.get("alternatives") or []
            if alternatives:
                parts.append("")
                parts.append("Alternative tools you can try:")
                for alt in alternatives:
                    slug = alt.get("tool_slug", "?")
                    name = alt.get("name", "")
                    score = alt.get("quality_score")
                    label = f"- {slug}"
                    if name:
                        label += f" ({name})"
                    if score is not None:
                        label += f" — quality: {score}/100"
                    parts.append(label)
                parts.append("\nUse invoke_tool with one of these alternatives.")

            return "\n".join(parts)
        except Exception:
            return f"Error ({resp.status_code}): {resp.text}"
