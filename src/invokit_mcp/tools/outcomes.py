"""Outcome tool — submit quality feedback after invoking a tool."""

from __future__ import annotations

from invokit_mcp.server import mcp, get_client


@mcp.tool()
async def submit_outcome(
    slug: str,
    invocation_id: str,
    agent_id: str = "mcp-client",
    semantic_accuracy: float | None = None,
    output_usefulness: float | None = None,
    task_completion: bool | None = None,
    feedback_text: str | None = None,
) -> str:
    """Submit quality feedback after invoking a tool.

    This closes the feedback loop: search → invoke → report outcome.
    Outcomes improve quality scores and help other agents choose better tools.

    Requires an API key (INVOKIT_API_KEY environment variable).

    Args:
        slug: The tool's slug identifier that was invoked.
        invocation_id: The invocation ID from invoke_tool's response metadata.
        agent_id: A stable identifier for your agent (default: "mcp-client"). Use a custom value like "my-chatbot-v2" to track feedback by agent.
        semantic_accuracy: How accurately did the output match the expected result? 0.0 = completely wrong, 0.5 = partially correct, 1.0 = perfect.
        output_usefulness: How useful was the output for your task? 0.0 = useless, 0.5 = somewhat helpful, 1.0 = exactly what was needed.
        task_completion: Did the tool complete the intended task?
        feedback_text: Optional free-text feedback (max 2000 chars).
    """
    client = get_client()

    body: dict = {
        "invocation_id": invocation_id,
        "agent_id": agent_id,
    }
    if semantic_accuracy is not None:
        body["semantic_accuracy"] = semantic_accuracy
    if output_usefulness is not None:
        body["output_usefulness"] = output_usefulness
    if task_completion is not None:
        body["task_completion"] = task_completion
    if feedback_text is not None:
        body["feedback_text"] = feedback_text

    result = await client.post(
        f"/v1/tools/{slug}/outcome",
        json_body=body,
        require_auth=True,
    )

    if isinstance(result, str):
        return result

    return (
        f"Outcome submitted successfully.\n"
        f"Outcome ID: {result.get('id', '?')}\n"
        f"Invocation: {result.get('invocation_id', invocation_id)}"
    )
