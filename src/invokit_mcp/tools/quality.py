"""Quality and metrics tools — evaluate tool reliability before invoking."""

from __future__ import annotations

from invokit_mcp.server import mcp, get_backend


@mcp.tool()
async def get_tool_quality(
    slug: str,
    period: str = "all_time",
) -> str:
    """Get the quality score breakdown for a tool — an overall 0-100 score with
    primary signals (success rate, schema honesty, latency consistency) and
    secondary signals. Use this to evaluate whether a tool is reliable enough to use.

    For detailed latency percentiles and raw performance data, use get_tool_metrics instead.

    Args:
        slug: The tool's slug identifier.
        period: Time period — "hour", "day", "week", "month", or "all_time".
    """
    backend = get_backend()
    result = await backend.get(f"/v1/tools/{slug}/quality", params={"period": period})
    if isinstance(result, str):
        return result

    lines = [f"# Quality Report: {result.get('tool_slug', slug)}"]
    lines.append(f"Period: {result.get('period', period)}")

    score = result.get("quality_score")
    lines.append(f"Overall Score: {score}/100" if score is not None else "Overall Score: N/A (insufficient data)")

    primary = result.get("primary_signals") or {}
    lines.append("")
    lines.append("## Primary Signals")
    lines.append(f"- Success Rate: {_pct(primary.get('success_rate'))}")
    lines.append(f"- Schema Honesty: {_pct(primary.get('schema_honesty_score'))}")
    lines.append(f"- Latency Consistency: {_pct(primary.get('latency_consistency'))}")

    secondary = result.get("secondary_signals") or {}
    lines.append("")
    lines.append("## Secondary Signals")
    lines.append(f"- Avg Latency: {_ms(secondary.get('avg_latency_ms'))}")
    lines.append(f"- p50 / p95 / p99: {_ms(secondary.get('p50_latency_ms'))} / {_ms(secondary.get('p95_latency_ms'))} / {_ms(secondary.get('p99_latency_ms'))}")
    lines.append(f"- Error Rate: {_pct(secondary.get('error_rate'))}")
    lines.append(f"- Uptime: {_pct(secondary.get('uptime_percentage'))}")
    lines.append(f"- Total Invocations: {secondary.get('total_invocations', 0)}")
    lines.append(f"- Unique Agents: {secondary.get('unique_agents', 0)}")

    return "\n".join(lines)


@mcp.tool()
async def get_tool_metrics(
    slug: str,
    period: str = "all_time",
) -> str:
    """Get raw performance metrics for a tool — invocation counts, latency percentiles
    (p50/p95/p99), error rate, and uptime. Use this for detailed performance analysis.

    For a simple reliability check with an overall score, use get_tool_quality instead.

    Args:
        slug: The tool's slug identifier.
        period: Time period — "hour", "day", "week", "month", or "all_time".
    """
    backend = get_backend()
    result = await backend.get(f"/v1/tools/{slug}/metrics", params={"period": period})
    if isinstance(result, str):
        return result

    lines = [f"# Metrics: {result.get('tool_slug', slug)}"]
    lines.append(f"Period: {result.get('period', period)}")
    lines.append(f"Total Invocations: {result.get('total_invocations', 0)}")
    lines.append(f"Unique Agents: {result.get('unique_agents', 0)}")
    lines.append(f"Success Rate: {_pct(result.get('success_rate'))}")
    lines.append(f"Error Rate: {_pct(result.get('error_rate'))}")
    lines.append(f"Avg Latency: {_ms(result.get('avg_latency_ms'))}")
    lines.append(f"p50 / p95 / p99: {_ms(result.get('p50_latency_ms'))} / {_ms(result.get('p95_latency_ms'))} / {_ms(result.get('p99_latency_ms'))}")
    lines.append(f"Uptime: {_pct(result.get('uptime_percentage'))}")
    lines.append(f"Quality Score: {result.get('quality_score', 'N/A')}/100")

    return "\n".join(lines)


@mcp.tool()
async def get_tool_alternatives(
    slug: str,
    limit: int = 5,
) -> str:
    """Find type-compatible alternative tools from the same category.

    Useful when a tool's circuit breaker is open or you want to compare options.

    Args:
        slug: The tool's slug identifier.
        limit: Maximum number of alternatives to return (default 5).
    """
    backend = get_backend()
    result = await backend.get(f"/v1/tools/{slug}/alternatives", params={"limit": limit})
    if isinstance(result, str):
        return result

    alts = result.get("alternatives") or [] if isinstance(result, dict) else []
    if not alts:
        return f"No alternatives found for tool \"{slug}\"."

    lines = [f"# Alternatives for {result.get('tool_slug', slug)}\n"]
    for a in alts:
        compat = a.get("compatibility")
        compat_str = f" | Compatibility: {compat:.0%}" if compat is not None else ""
        lines.append(f"## {a.get('name', '?')} ({a.get('tool_slug', '?')})")
        lines.append(a.get("capability_summary", ""))
        lines.append(f"Quality: {a.get('quality_score', 'N/A')}/100{compat_str}")
        lines.append(f"Invoke: POST {a.get('invoke_url', 'N/A')}")
        lines.append("---")
    return "\n".join(lines)


# ------------------------------------------------------------------
#  Helpers
# ------------------------------------------------------------------

def _pct(val) -> str:
    if val is None:
        return "N/A"
    return f"{val}%"


def _ms(val) -> str:
    if val is None:
        return "N/A"
    return f"{val}ms"
