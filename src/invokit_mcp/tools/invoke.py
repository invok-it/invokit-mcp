"""Invocation tool — invoke an AI agent tool via the invok.it transparent proxy."""

from __future__ import annotations

import json

from invokit_mcp.server import mcp, get_client


@mcp.tool()
async def invoke_tool(
    tool_slug: str,
    arguments: dict | None = None,
    version: str | None = None,
) -> str:
    """Invoke a tool on the invok.it marketplace via transparent proxy.

    Requires an API key (INVOKIT_API_KEY environment variable).
    The tool's response is returned directly.

    Args:
        tool_slug: The tool's slug identifier (e.g. "send-email-via-sendgrid").
        arguments: JSON arguments to pass to the tool as the request body.
        version: Specific tool version to invoke (e.g. "1.0.0"). Uses latest if omitted.
    """
    client = get_client()

    path = f"/v1/invoke/{tool_slug}"
    if version:
        path = f"/v1/invoke/{tool_slug}/{version}"

    result = await client.post(
        path,
        json_body=arguments or {},
        require_auth=True,
        raw_response=True,
    )

    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        return json.dumps(result, indent=2)

    return str(result)
