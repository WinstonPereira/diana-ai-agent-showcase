"""
SNIPPET ILUSTRATIVO — Loop de orquestração de agente com function calling.

NÃO é o código real da DIANA. Exemplo genérico do loop central:

    1. Monta prompt de sistema (regras + memória + contexto)
    2. Envia catálogo de tools ao LLM
    3. Se o LLM pedir tool_calls → executa → devolve resultado → repete
    4. Se o LLM responder texto → extrai emoção → retorna ao frontend

O teto de iterações evita loop infinito de chamadas de ferramenta.
"""

from __future__ import annotations

from typing import Any
from tool_dispatch import ToolRegistry, ToolResult


MAX_ITERATIONS = 8


async def run_agent_turn(
    user_message: str,
    llm_client: Any,
    registry: ToolRegistry,
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
            result: ToolResult = await registry.dispatch(
                call["name"], call.get("arguments", {})
            )
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": result.to_model_payload(),
            })

    return {
        "reply_text": "Não consegui concluir em tempo hábil, amor.",
        "emotion": "thinking",
    }


def _extract_emotion(text: str) -> str:
    """Extrai a tag [EMO:xxx] do texto (controla o avatar 3D)."""
    for emo in ("happy", "excited", "surprised", "thinking", "sad", "angry"):
        if f"[EMO:{emo}]" in text:
            return emo
    return "neutral"
