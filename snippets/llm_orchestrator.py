"""
ILLUSTRATIVE SNIPPET — Agent orchestration loop with function calling.

This is NOT DIANA's real code. Generic example of the core loop:

    1. Build the system prompt (rules + memory + context)
    2. Send the tool catalogue to the LLM
    3. If the LLM requests tool_calls -> execute -> return results -> repeat
    4. If the LLM returns text -> extract emotion -> return to frontend

The iteration cap prevents an infinite tool-calling loop.
"""

from __future__ import annotations

from typing import Any

# In a real project this comes from the dispatch module shown in
# snippets/tool_dispatch.py
# from tool_dispatch import ToolRegistry, ToolResult


MAX_ITERATIONS = 8


async def run_agent_turn(
    user_message: str,
    llm_client: Any,
    registry: Any,
    system_prompt: str,
    max_iterations: int = MAX_ITERATIONS,
) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    for _ in range(max_iterations):
        response = await llm_client.chat(
            messages=messages,
            tools=registry.schemas(),
        )

        tool_calls = response.get("tool_calls") or []
        if not tool_calls:
            return {
                "reply_text": response.get("content", ""),
                "emotion": _extract_emotion(response.get("content", "")),
            }

        messages.append({"role": "assistant", "tool_calls": tool_calls})

        for call in tool_calls:
            result = await registry.dispatch(
                call["name"], call.get("arguments", {})
            )
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": result.to_model_payload(),
            })

    return {
        "reply_text": "I couldn't finish that in time.",
        "emotion": "thinking",
    }


def _extract_emotion(text: str) -> str:
    """Extracts the [EMO:xxx] tag from the text (drives the 3D avatar)."""
    for emo in ("happy", "excited", "surprised", "thinking", "sad", "angry"):
        if f"[EMO:{emo}]" in text:
            return emo
    return "neutral"
