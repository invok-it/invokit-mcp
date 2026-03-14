"""Usage tool — check API quota and consumption."""

from __future__ import annotations

from invokit_mcp.server import mcp, get_backend


@mcp.tool()
async def check_usage() -> str:
    """Check your current API usage, quota, and remaining calls for this month.

    Requires an API key (INVOKIT_API_KEY environment variable).
    Use this before invoking tools to ensure you have remaining quota.
    """
    backend = get_backend()
    result = await backend.get("/v1/usage", require_auth=True)
    if isinstance(result, str):
        return result

    lines = ["# API Usage"]
    lines.append(f"Tier: {result.get('tier', '?')}")
    lines.append(f"Period: {result.get('year_month', '?')}")
    lines.append(f"Monthly Quota: {result.get('monthly_quota', '?'):,}")
    lines.append(f"Used: {result.get('api_calls', 0):,}")
    lines.append(f"Remaining: {result.get('remaining', '?'):,}")
    lines.append(f"Overage Calls: {result.get('overage_calls', 0):,}")
    lines.append(f"Overage Cost: ${result.get('overage_amount', 0):.3f}")
    return "\n".join(lines)
