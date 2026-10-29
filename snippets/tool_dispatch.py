"""
SNIPPET ILUSTRATIVO — Padrão de despacho de ferramentas com verificação de resultado.

Este arquivo NÃO faz parte do código funcional da DIANA. É um exemplo genérico
do padrão de engenharia usado: o modelo emite tool calls, o dispatcher executa,
e o resultado estruturado é devolvido ao modelo. O agente só pode afirmar
sucesso quando `ok == True`.

Este é o coração do padrão "honest tool results".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable


@dataclass
class ToolResult:
    """Resultado estruturado de qualquer ferramenta."""
    ok: bool
    result: Any = None
    error: str | None = None
    explained: dict[str, Any] = field(default_factory=dict)

    def to_model_payload(self) -> dict[str, Any]:
        """Payload que volta para o LLM — nunca esconde falhas."""
        return {
            "ok": self.ok,
            "result": self.result if self.ok else None,
            "error": self.error,
        }


class ToolRegistry:
    """Catálogo de ferramentas disponíveis para o LLM."""

    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Awaitable[ToolResult]]] = {}

    def register(self, name: str, fn: Callable[..., Awaitable[ToolResult]]) -> None:
        self._tools[name] = fn

    def schemas(self) -> list[dict[str, Any]]:
        """Schemas JSON enviados ao LLM no formato function calling."""
        return [
            {"type": "function", "function": {"name": name}}
            for name in self._tools
        ]

    async def dispatch(self, name: str, args: dict[str, Any]) -> ToolResult:
        """Executa uma tool e SEMPRE retorna ToolResult — nunca lança para o LLM."""
        fn = self._tools.get(name)
        if fn is None:
            return ToolResult(
                ok=False,
                error=f"Tool '{name}' não encontrada no registro.",
                explained={"can_autofix": False, "severity": "medium"},
            )
        try:
            result = await fn(**args)
            if not isinstance(result, ToolResult):
                return ToolResult(ok=True, result=result)
            return result
        except TypeError as exc:
            return ToolResult(
                ok=False,
                error=f"Argumentos inválidos para '{name}': {exc}",
                explained={"can_autofix": True, "severity": "low"},
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                ok=False,
                error=f"Falha em '{name}': {exc}",
                explained={"can_autofix": True, "severity": "medium"},
            )
