"""Platform tool — get invok.it platform capabilities and info."""

from __future__ import annotations

import json

from invokit_mcp.server import mcp, get_backend


@mcp.tool()
async def get_manifest() -> str:
    """Get the invok.it platform manifest — capabilities, endpoints, auth methods, and rate limits."""
    backend = get_backend()
    result = await backend.get("/v1/manifest")
    if isinstance(result, str):
        return result

    lines = [f"# {result.get('platform', 'invok.it')} Platform Manifest"]
    lines.append(f"Version: {result.get('version', '?')}")

    caps = result.get("capabilities") or []
    if caps:
        lines.append("")
        lines.append("## Capabilities")
        for c in caps:
            lines.append(f"- {c}")

    auth = result.get("auth_methods") or []
    if auth:
        lines.append("")
        lines.append("## Authentication Methods")
        for a in auth:
            lines.append(f"- {a}")

    auth_inst = result.get("auth_instructions")
    if auth_inst:
        lines.append("")
        lines.append("## Auth Instructions")
        lines.append(json.dumps(auth_inst, indent=2))

    endpoints = result.get("endpoints") or []
    if endpoints:
        lines.append("")
        lines.append(f"## Endpoints ({len(endpoints)})")
        for ep in endpoints:
            lines.append(f"- {ep.get('method', '?')} {ep.get('path', '?')} — {ep.get('description', '')}")

    filters = result.get("search_filters") or []
    if filters:
        lines.append("")
        lines.append("## Search Filters")
        lines.append(", ".join(filters))

    rate_limits = result.get("rate_limits")
    if rate_limits:
        lines.append("")
        lines.append("## Rate Limits")
        lines.append(json.dumps(rate_limits, indent=2))

    return "\n".join(lines)
