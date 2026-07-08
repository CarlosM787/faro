"""Provider-agnostic LLM interface.

The agent loop speaks only this neutral protocol; ``AnthropicProvider`` and
``OllamaProvider`` translate it. Switching providers is env-only — zero code
changes (docs/TECH-NOTES.md).
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Literal

# Neutral message dict:
#   {"role": "user"|"assistant"|"tool", "content": str,
#    "tool_calls": [ToolCall-like dicts]?  (assistant only),
#    "tool_call_id": str?  (tool role only)}
Message = dict[str, Any]


@dataclass(frozen=True)
class ToolDef:
    """Provider-neutral tool definition (JSON-schema parameters)."""

    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class TextDelta:
    text: str


@dataclass(frozen=True)
class ToolCallRequest:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class Done:
    stop_reason: Literal["end", "tool_use", "max_tokens", "error"]
    error: str | None = None


AgentEvent = TextDelta | ToolCallRequest | Done


@dataclass
class ChatOptions:
    system: str = ""
    max_tokens: int = 1024  # spend cap (TECH-NOTES cost rule)
    temperature: float = 0.2  # low: numeric fidelity over creativity
    tools: list[ToolDef] = field(default_factory=list)


class LLMProvider(ABC):
    """Interface every LLM backend implements."""

    name: str
    model: str

    @abstractmethod
    def stream_chat(
        self, messages: list[Message], options: ChatOptions
    ) -> AsyncIterator[AgentEvent]:
        """Stream a completion: text deltas, tool-call requests, then Done."""
