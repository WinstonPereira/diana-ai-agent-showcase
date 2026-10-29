"""
ILLUSTRATIVE SNIPPET — Tool dispatch pattern with result verification.

This file is NOT part of DIANA's functional codebase. It is a generic example
of the engineering pattern used: the model emits tool calls, the dispatcher
executes them, and a structured result is returned to the model. The agent may
only claim success when `ok == True`.

This is the core of the "honest tool results" pattern.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable


@dataclass
class ToolResult:
    """Structured result of any tool."""

    ok: bool
    result: Any = None
    error: str | None = None
    explained: dict[str, Any] = field(default_factory=dict)

    def to_model_payload(self) -> dict[str, Any]:
        """Payload sent back to the LLM — never hides failures."""
        return {
            "ok": self.ok,
            "result": self.result if self.ok else None,
            "error": self.error,
        }


class ToolRegistry:
    """Catalogue of tools available to the LLM."""

    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Awaitable[ToolResult]]] = {}

    def register(self, name: str, fn: Callable[..., Awaitable[ToolResult]]) -> None:
        self._tools[name] = fn

    def schemas(self) -> list[dict[str, Any]]:
        """JSON schemas sent to the LLM in function-calling format."""
        return [
            {"type": "function", "function": {"name": name}}
            for name in self._tools
        ]

    async def dispatch(self, name: str, args: dict[str, Any]) -> ToolResult:
        """Executes a tool and ALWAYS returns a ToolResult — never raises to the LLM."""
        fn = self._tools.get(name)
        if fn is None:
            return ToolResult(
                ok=False,
                error=f"Tool '{name}' not found in registry.",
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
                error=f"Invalid arguments for '{name}': {exc}",
                explained={"can_autofix": True, "severity": "low"},
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                ok=False,
                error=f"Failure in '{name}': {exc}",
                explained={"can_autofix": True, "severity": "medium"},
            )
