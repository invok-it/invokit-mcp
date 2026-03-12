"""Discovery tools — search and browse tools, skills, apps, MCP servers, and categories."""

from __future__ import annotations

import json

from invokit_mcp.server import mcp, get_client


# ------------------------------------------------------------------
#  Formatters
# ------------------------------------------------------------------

def _fmt_tool_summary(t: dict) -> str:
    lines = [f"## {t.get('name', '?')} ({t.get('slug', '?')})"]
    pub = t.get("publisher")
    if pub:
        verified = " [Verified]" if t.get("verified") else ""
        lines[0] += f" by {pub.get('name', '?')}{verified}"
    lines.append(t.get("capability_summary", ""))
    q = t.get("quality") or {}
    if q.get("quality_score") is not None:
        lines.append(
            f"Quality: {q['quality_score']}/100 | "
            f"Latency: {q.get('avg_latency_ms', '?')}ms | "
            f"Success: {q.get('success_rate', '?')}%"
        )
    cats = t.get("categories") or []
    if cats:
        lines.append("Categories: " + ", ".join(c.get("name", c.get("slug", "")) for c in cats))
    tags = t.get("tags") or []
    if tags:
        lines.append("Tags: " + ", ".join(tags))
    return "\n".join(lines)


def _fmt_tool_detail(t: dict) -> str:
    lines = [f"# {t.get('name', '?')} ({t.get('slug', '?')})"]
    pub = t.get("publisher")
    if pub:
        lines.append(f"Publisher: {pub.get('name', '?')}")
    lines.append(f"Status: {t.get('status', '?')} | Verified: {t.get('verified', False)}")
    lines.append("")
    lines.append("## Description")
    lines.append(t.get("capability_description", t.get("capability_summary", "")))
    if t.get("description"):
        lines.append("")
        lines.append(t["description"])

    q = t.get("quality") or {}
    if q.get("quality_score") is not None:
        lines.append("")
        lines.append("## Quality")
        lines.append(
            f"Score: {q['quality_score']}/100 | "
            f"Success: {q.get('success_rate', '?')}% | "
            f"Latency: {q.get('avg_latency_ms', '?')}ms"
        )

    cats = t.get("categories") or []
    if cats:
        lines.append("")
        lines.append("## Categories")
        lines.append(", ".join(c.get("name", c.get("slug", "")) for c in cats))

    tags = t.get("tags") or []
    if tags:
        lines.append("")
        lines.append("## Tags")
        lines.append(", ".join(tags))

    versions = t.get("versions") or []
    if versions:
        lines.append("")
        lines.append(f"## Versions ({len(versions)})")
        for v in versions[:5]:
            latest = " [latest]" if v.get("is_latest") else ""
            lines.append(f"- v{v.get('version', '?')} ({v.get('status', '?')}){latest}")
            lines.append(f"  Endpoint: {v.get('endpoint_method', 'POST')} {v.get('endpoint_url', 'N/A')}")
            if v.get("input_schema"):
                lines.append(f"  Input schema: {json.dumps(v['input_schema'], indent=2)}")
            if v.get("output_schema"):
                lines.append(f"  Output schema: {json.dumps(v['output_schema'], indent=2)}")
            pricing = v.get("pricing")
            if pricing:
                lines.append(f"  Pricing: {json.dumps(pricing)}")
        if len(versions) > 5:
            lines.append(f"  ... and {len(versions) - 5} more versions")

    return "\n".join(lines)


def _fmt_skill_summary(s: dict) -> str:
    lines = [f"## {s.get('name', '?')} ({s.get('slug', '?')})"]
    lines.append(s.get("capability_summary", s.get("summary", "")))
    lines.append(f"Pricing: {s.get('pricing_type', 'free')} | Tools: {s.get('tool_count', 0)}")
    cats = s.get("categories") or []
    if cats:
        lines.append("Categories: " + ", ".join(c.get("name", c.get("slug", "")) for c in cats))
    tags = s.get("tags") or []
    if tags:
        lines.append("Tags: " + ", ".join(tags))
    return "\n".join(lines)


def _fmt_skill_detail(s: dict) -> str:
    lines = [f"# {s.get('name', '?')} ({s.get('slug', '?')})"]
    lines.append(f"Pricing: {s.get('pricing_type', 'free')}")
    if s.get("price"):
        lines[-1] += f" (${s['price']})"
    lines.append(f"Status: {s.get('status', '?')} | Verified: {s.get('verified', False)}")
    lines.append("")
    lines.append("## Description")
    lines.append(s.get("capability_description", s.get("summary", "")))
    if s.get("description"):
        lines.append("")
        lines.append(s["description"])
    bindings = s.get("tool_bindings") or []
    if bindings:
        lines.append("")
        lines.append(f"## Tool Bindings ({len(bindings)})")
        for b in bindings:
            lines.append(f"- {b.get('tool_name', b.get('tool_slug', '?'))} (order: {b.get('execution_order', '?')})")
            if b.get("role_description"):
                lines.append(f"  Role: {b['role_description']}")
    if s.get("input_schema"):
        lines.append("")
        lines.append("## Input Schema")
        lines.append(json.dumps(s["input_schema"], indent=2))
    if s.get("output_schema"):
        lines.append("")
        lines.append("## Output Schema")
        lines.append(json.dumps(s["output_schema"], indent=2))
    return "\n".join(lines)


def _fmt_app_summary(a: dict) -> str:
    lines = [f"## {a.get('name', '?')} ({a.get('slug', '?')})"]
    lines.append(a.get("capability_summary", ""))
    lines.append(f"Pricing: {a.get('pricing_type', 'free')} | Steps: {a.get('step_count', 0)}")
    cats = a.get("categories") or []
    if cats:
        lines.append("Categories: " + ", ".join(c.get("name", c.get("slug", "")) for c in cats))
    return "\n".join(lines)


def _fmt_app_detail(a: dict) -> str:
    lines = [f"# {a.get('name', '?')} ({a.get('slug', '?')})"]
    lines.append(f"Pricing: {a.get('pricing_type', 'free')}")
    lines.append(f"Status: {a.get('status', '?')} | Verified: {a.get('verified', False)}")
    lines.append("")
    lines.append("## Description")
    lines.append(a.get("capability_description", a.get("capability_summary", "")))
    if a.get("description"):
        lines.append("")
        lines.append(a["description"])
    steps = a.get("steps") or []
    if steps:
        lines.append("")
        lines.append(f"## Execution Steps ({len(steps)})")
        for s in steps:
            lines.append(f"{s.get('execution_order', '?')}. {s.get('tool_slug', '?')}")
            if s.get("description"):
                lines.append(f"   {s['description']}")
    if a.get("input_schema"):
        lines.append("")
        lines.append("## Input Schema")
        lines.append(json.dumps(a["input_schema"], indent=2))
    if a.get("output_schema"):
        lines.append("")
        lines.append("## Output Schema")
        lines.append(json.dumps(a["output_schema"], indent=2))
    return "\n".join(lines)


def _fmt_mcp_summary(m: dict) -> str:
    lines = [f"## {m.get('name', '?')} ({m.get('slug', '?')})"]
    lines.append(m.get("description", ""))
    lines.append(f"Publisher: {m.get('publisher_name', '?')} | Installs: {m.get('install_count', 0)}")
    transports = m.get("transport_types") or []
    if transports:
        lines.append("Transports: " + ", ".join(transports))
    tags = m.get("tags") or []
    if tags:
        lines.append("Tags: " + ", ".join(tags))
    return "\n".join(lines)


def _fmt_mcp_detail(m: dict) -> str:
    lines = [f"# {m.get('name', '?')} ({m.get('slug', '?')})"]
    lines.append(f"Publisher: {m.get('publisher_name', '?')}")
    lines.append(f"Status: {m.get('status', '?')} | Verified: {m.get('verified', False)} | Installs: {m.get('install_count', 0)}")
    lines.append(f"Tools: {m.get('tool_count', 0)} | Resources: {m.get('resource_count', 0)} | Prompts: {m.get('prompt_count', 0)}")
    lines.append("")
    lines.append("## Description")
    lines.append(m.get("description", ""))
    if m.get("homepage"):
        lines.append(f"Homepage: {m['homepage']}")
    versions = m.get("versions") or []
    if versions:
        lines.append("")
        lines.append(f"## Versions ({len(versions)})")
        for v in versions:
            latest = " [latest]" if v.get("is_latest") else ""
            lines.append(f"- v{v.get('version', '?')}{latest}")
            lines.append(f"  Transports: {', '.join(v.get('supported_transports', []))}")
            lines.append(f"  Capabilities: {', '.join(v.get('capabilities', []))}")
            env_vars = v.get("environment_vars") or []
            if env_vars:
                lines.append(f"  Env vars: {', '.join(env_vars)}")
    return "\n".join(lines)


# ------------------------------------------------------------------
#  Tools
# ------------------------------------------------------------------

@mcp.tool()
async def search_tools(
    query: str,
    category: str | None = None,
    min_quality_score: float | None = None,
    max_price_per_call: float | None = None,
    page: int = 1,
    per_page: int = 10,
) -> str:
    """Search the invok.it marketplace for AI agent tools using natural language.

    Args:
        query: Natural language search query (e.g. "send email", "image recognition").
        category: Filter by category slug (use list_categories to see available ones).
        min_quality_score: Minimum quality score (0-100).
        max_price_per_call: Maximum price per API call in USD.
        page: Page number for pagination.
        per_page: Results per page (max 100).
    """
    client = get_client()
    body: dict = {"query": query, "page": page, "per_page": per_page}
    filters: dict = {}
    if category:
        filters["categories"] = [category]
    if min_quality_score is not None:
        filters["min_quality_score"] = min_quality_score
    if max_price_per_call is not None:
        filters["max_price_per_call"] = max_price_per_call
    if filters:
        body["filters"] = filters

    result = await client.post("/v1/tools/search", json_body=body)
    if isinstance(result, str):
        return result

    tools = result if isinstance(result, list) else []
    if not tools:
        return f"No tools found for query: \"{query}\""

    parts = [f"Found {len(tools)} tool(s) for \"{query}\":\n"]
    for t in tools:
        parts.append(_fmt_tool_summary(t))
        parts.append("---")
    return "\n".join(parts)


@mcp.tool()
async def get_tool(slug: str) -> str:
    """Get full details for a specific tool by its slug.

    Args:
        slug: The tool's unique identifier (e.g. "send-email-via-sendgrid").
    """
    client = get_client()
    result = await client.get(f"/v1/tools/{slug}")
    if isinstance(result, str):
        return result
    return _fmt_tool_detail(result)


@mcp.tool()
async def list_categories() -> str:
    """List all tool categories with counts of tools, skills, apps, and MCP servers."""
    client = get_client()
    result = await client.get("/v1/categories")
    if isinstance(result, str):
        return result

    cats = result if isinstance(result, list) else []
    if not cats:
        return "No categories found."

    lines = ["# Categories\n"]
    for c in cats:
        counts = []
        if c.get("tool_count"):
            counts.append(f"{c['tool_count']} tools")
        if c.get("skill_count"):
            counts.append(f"{c['skill_count']} skills")
        if c.get("app_count"):
            counts.append(f"{c['app_count']} apps")
        if c.get("mcp_server_count"):
            counts.append(f"{c['mcp_server_count']} MCP servers")
        count_str = f" ({', '.join(counts)})" if counts else ""
        desc = f" — {c['description']}" if c.get("description") else ""
        lines.append(f"- **{c.get('name', '?')}** (`{c.get('slug', '?')}`){count_str}{desc}")
    return "\n".join(lines)


@mcp.tool()
async def search_skills(
    query: str | None = None,
    category: str | None = None,
    pricing_type: str | None = None,
    tags: str | None = None,
    page: int = 1,
    per_page: int = 10,
) -> str:
    """Search for skills (multi-tool workflows) on invok.it.

    Args:
        query: Natural language search query (e.g. "pdf to summary", "data pipeline", "content moderation").
        category: Filter by category slug.
        pricing_type: Filter by "free" or "paid".
        tags: Comma-separated tags to filter by.
        page: Page number.
        per_page: Results per page.
    """
    client = get_client()
    params = {"query": query, "category": category, "pricing_type": pricing_type,
              "tags": tags, "page": page, "per_page": per_page}
    result = await client.get("/v1/skills/search", params=params)
    if isinstance(result, str):
        return result

    skills = result if isinstance(result, list) else []
    if not skills:
        return "No skills found."

    parts = [f"Found {len(skills)} skill(s):\n"]
    for s in skills:
        parts.append(_fmt_skill_summary(s))
        parts.append("---")
    return "\n".join(parts)


@mcp.tool()
async def get_skill(slug: str) -> str:
    """Get full details for a specific skill by its slug.

    Args:
        slug: The skill's unique identifier.
    """
    client = get_client()
    result = await client.get(f"/v1/skills/{slug}")
    if isinstance(result, str):
        return result
    return _fmt_skill_detail(result)


@mcp.tool()
async def search_apps(
    query: str | None = None,
    category: str | None = None,
    pricing_type: str | None = None,
    tags: str | None = None,
    page: int = 1,
    per_page: int = 10,
) -> str:
    """Search for apps (deterministic step pipelines) on invok.it.

    Args:
        query: Natural language search query (e.g. "document processing", "image analysis pipeline", "ETL workflow").
        category: Filter by category slug.
        pricing_type: Filter by "free" or "paid".
        tags: Comma-separated tags to filter by.
        page: Page number.
        per_page: Results per page.
    """
    client = get_client()
    params = {"query": query, "category": category, "pricing_type": pricing_type,
              "tags": tags, "page": page, "per_page": per_page}
    result = await client.get("/v1/apps/search", params=params)
    if isinstance(result, str):
        return result

    apps = result if isinstance(result, list) else []
    if not apps:
        return "No apps found."

    parts = [f"Found {len(apps)} app(s):\n"]
    for a in apps:
        parts.append(_fmt_app_summary(a))
        parts.append("---")
    return "\n".join(parts)


@mcp.tool()
async def get_app(slug: str) -> str:
    """Get full details for a specific app by its slug.

    Args:
        slug: The app's unique identifier.
    """
    client = get_client()
    result = await client.get(f"/v1/apps/{slug}")
    if isinstance(result, str):
        return result
    return _fmt_app_detail(result)


@mcp.tool()
async def search_mcp_servers(
    query: str | None = None,
    tags: str | None = None,
    transport: str | None = None,
    page: int = 1,
    per_page: int = 10,
) -> str:
    """Search for MCP servers on the invok.it marketplace.

    Args:
        query: Text search query.
        tags: Comma-separated tags to filter by.
        transport: Filter by transport type ("stdio", "sse", "streamable-http").
        page: Page number.
        per_page: Results per page.
    """
    client = get_client()
    params = {"query": query, "tags": tags, "transport_type": transport,
              "page": page, "per_page": per_page}
    result = await client.get("/v1/mcp-servers/search", params=params)
    if isinstance(result, str):
        return result

    servers = result if isinstance(result, list) else []
    if not servers:
        return "No MCP servers found."

    parts = [f"Found {len(servers)} MCP server(s):\n"]
    for m in servers:
        parts.append(_fmt_mcp_summary(m))
        parts.append("---")
    return "\n".join(parts)


@mcp.tool()
async def get_mcp_server(slug: str) -> str:
    """Get full details for a specific MCP server by its slug.

    Args:
        slug: The MCP server's unique identifier.
    """
    client = get_client()
    result = await client.get(f"/v1/mcp-servers/{slug}")
    if isinstance(result, str):
        return result
    return _fmt_mcp_detail(result)


@mcp.tool()
async def get_mcp_server_config(
    slug: str,
    format: str = "claude",
) -> str:
    """Generate client configuration for installing an MCP server.

    Returns ready-to-use config JSON for the specified client.

    Args:
        slug: The MCP server's unique identifier.
        format: Target client format — "claude", "cursor", "vscode", or "generic".
    """
    client = get_client()
    result = await client.get(f"/v1/mcp-servers/{slug}/config", params={"format": format})
    if isinstance(result, str):
        return result

    lines = [f"# MCP Server Config for {format}\n"]
    lines.append("## Configuration")
    lines.append("```json")
    lines.append(json.dumps(result.get("config", {}), indent=2))
    lines.append("```")
    if result.get("instructions"):
        lines.append("")
        lines.append("## Instructions")
        lines.append(result["instructions"])
    next_steps = result.get("next_steps") or []
    if next_steps:
        lines.append("")
        lines.append("## Next Steps")
        for step in next_steps:
            lines.append(f"- {step}")
    return "\n".join(lines)
