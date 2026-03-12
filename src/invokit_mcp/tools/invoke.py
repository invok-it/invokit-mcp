"""Invocation tool — invoke an AI agent tool via the invok.it transparent proxy."""

from __future__ import annotations

from invokit_mcp.client import InvokeResult
from invokit_mcp.server import mcp, get_client


@mcp.tool()
async def invoke_tool(
    slug: str,
    arguments: dict | None = None,
    version: str | None = None,
) -> str:
    """Invoke a tool on the invok.it marketplace via transparent proxy.

    Requires an API key (INVOKIT_API_KEY environment variable).

    Check the tool's input_schema first (via get_tool) to know what arguments
    to pass. The response includes the tool's output along with platform
    metadata (latency, tool version, invocation ID if available).

    After receiving the result, use submit_outcome to provide quality feedback
    on the tool. This helps improve tool rankings for all agents.

    On failure, error responses include an error code (e.g. CIRCUIT_OPEN,
    RATE_LIMIT_EXCEEDED, TOOL_NOT_FOUND), a suggestion for resolution, and
    alternative tools when available (on 503). Use this information to
    automatically recover — switch to an alternative tool or retry after
    the suggested delay.

    Args:
        slug: The tool's slug identifier (e.g. "send-email-via-sendgrid").
        arguments: JSON arguments matching the tool's input_schema (use get_tool to see the schema).
        version: Specific tool version to invoke (e.g. "1.0.0"). Uses latest if omitted.
    """
    client = get_client()

    path = f"/v1/invoke/{slug}"
    if version:
        path = f"/v1/invoke/{slug}/{version}"

    result = await client.invoke(path, json_body=arguments or {})

    if isinstance(result, str):
        return result

    assert isinstance(result, InvokeResult)

    lines = ["# Tool Output\n", result.body]

    if result.metadata:
        lines.append("\n\n---\n## Invocation Metadata")
        invocation_id = result.metadata.get("X-Invocation-Id")
        if invocation_id:
            lines.append(f"Invocation ID: {invocation_id}")
            lines.append("(Pass this to submit_outcome to provide quality feedback)")
        latency = result.metadata.get("X-Marketplace-Latency-Ms")
        if latency:
            lines.append(f"Latency: {latency}ms")
        tool_version = result.metadata.get("X-Marketplace-Tool-Version")
        if tool_version:
            lines.append(f"Tool Version: {tool_version}")
        cb_status = result.metadata.get("X-Circuit-Breaker-Status")
        if cb_status:
            lines.append(f"Circuit Breaker: {cb_status}")

    return "\n".join(lines)
