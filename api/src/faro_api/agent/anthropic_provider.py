"""Anthropic (Claude) provider — the primary production path."""

import json
from collections.abc import AsyncIterator
from typing import Any

from faro_api.agent.errors import describe_provider_failure
from faro_api.agent.provider import (
    AgentEvent,
    ChatOptions,
    Done,
    LLMProvider,
    Message,
    TextDelta,
    ToolCallRequest,
)


def _to_anthropic_messages(messages: list[Message]) -> list[dict[str, Any]]:
    """Neutral protocol → Anthropic Messages API format.

    Assistant tool calls become ``tool_use`` blocks; tool results become
    ``tool_result`` blocks inside a user message.
    """
    out: list[dict[str, Any]] = []
    for msg in messages:
        role, content = msg["role"], msg.get("content", "")
        if role == "assistant" and msg.get("tool_calls"):
            blocks: list[dict[str, Any]] = []
            if content:
                blocks.append({"type": "text", "text": content})
            blocks.extend(
                {
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["arguments"],
                }
                for tc in msg["tool_calls"]
            )
            out.append({"role": "assistant", "content": blocks})
        elif role == "tool":
            out.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg["tool_call_id"],
                            "content": content,
                        }
                    ],
                }
            )
        else:
            out.append({"role": role, "content": content})
    return out


class AnthropicProvider(LLMProvider):
    """Claude via the official SDK, streaming, with tool use."""

    name = "anthropic"

    def __init__(self, api_key: str, model: str) -> None:
        import anthropic  # local import: optional dependency path

        self.model = model
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def stream_chat(
        self, messages: list[Message], options: ChatOptions
    ) -> AsyncIterator[AgentEvent]:
        tools = [
            {"name": t.name, "description": t.description, "input_schema": t.parameters}
            for t in options.tools
        ]
        try:
            async with self._client.messages.stream(
                model=self.model,
                system=options.system,
                messages=_to_anthropic_messages(messages),  # type: ignore[arg-type]
                tools=tools,  # type: ignore[arg-type]
                max_tokens=options.max_tokens,
                # NOTE: `options.temperature` is deliberately NOT forwarded here.
                # The anthropic SDK dropped `temperature` from the Messages
                # parameter surface in 1.x, so passing it raises TypeError at
                # call time (and mypy --strict flags it). Numeric fidelity on
                # this path comes from the tool-only system-prompt contract and
                # the grounding checker, not from sampling temperature.
                # ChatOptions.temperature is still honoured by the Ollama
                # provider, whose own API continues to accept it.
            ) as stream:
                async for event in stream:
                    if event.type == "text":
                        yield TextDelta(event.text)
                final = await stream.get_final_message()
        except Exception as exc:  # provider boundary
            # This is the only thing the user sees when the copilot fails, so it
            # names the provider, keeps the useful part of its message, redacts
            # anything key-shaped, and says what to do. See agent/errors.py.
            yield Done(
                stop_reason="error",
                error=describe_provider_failure(self.name, self.model, exc),
            )
            return

        for block in final.content:
            if block.type == "tool_use":
                args = (
                    block.input if isinstance(block.input, dict) else json.loads(str(block.input))
                )
                yield ToolCallRequest(id=block.id, name=block.name, arguments=args)

        yield Done(stop_reason="tool_use" if final.stop_reason == "tool_use" else "end")
