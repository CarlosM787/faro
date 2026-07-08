"""The agent loop: stream LLM output, execute tool calls, repeat, guard.

Yields provider-neutral events the chat router converts to SSE:
  {"type": "text", "text": ...}
  {"type": "tool_call", "name": ..., "arguments": {...}, "result": {...}}
  {"type": "done", "grounding_violations": [...], "provider": ..., "error": ...?}
"""

import json
from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Any

from faro_api.agent.anthropic_provider import AnthropicProvider
from faro_api.agent.guardrails import check_grounding
from faro_api.agent.ollama_provider import OllamaProvider
from faro_api.agent.prompts import system_prompt
from faro_api.agent.provider import (
    ChatOptions,
    Done,
    LLMProvider,
    Message,
    TextDelta,
    ToolCallRequest,
)
from faro_api.agent.tools import TOOL_DEFS, ToolExecutor
from faro_api.config import get_settings

MAX_TOOL_ROUNDS = 6  # runaway-loop cap


@lru_cache
def get_provider() -> LLMProvider:
    """Env-selected provider: Anthropic when a key exists, else local Ollama."""
    settings = get_settings()
    if settings.anthropic_api_key:
        return AnthropicProvider(api_key=settings.anthropic_api_key, model=settings.anthropic_model)
    return OllamaProvider(base_url=settings.ollama_url, model=settings.ollama_model)


async def run_agent(
    history: list[Message],
    user_message: str,
    language: str,
    executor: ToolExecutor,
    provider: LLMProvider | None = None,
) -> AsyncIterator[dict[str, Any]]:
    """One user turn: may span several LLM rounds if tools are called."""
    llm = provider or get_provider()
    options = ChatOptions(system=system_prompt(language), tools=TOOL_DEFS)
    messages: list[Message] = [*history, {"role": "user", "content": user_message}]

    reply_parts: list[str] = []
    tool_results: list[str] = []

    for _round in range(MAX_TOOL_ROUNDS):
        pending: list[ToolCallRequest] = []
        round_text: list[str] = []
        stop: Done | None = None

        async for event in llm.stream_chat(messages, options):
            if isinstance(event, TextDelta):
                round_text.append(event.text)
                reply_parts.append(event.text)
                yield {"type": "text", "text": event.text}
            elif isinstance(event, ToolCallRequest):
                pending.append(event)
            elif isinstance(event, Done):
                stop = event

        if stop is not None and stop.stop_reason == "error":
            yield {
                "type": "done",
                "provider": llm.name,
                "error": stop.error,
                "grounding_violations": [],
            }
            return

        if not pending:  # final answer reached
            break

        # Record the assistant turn (with its tool calls), then execute them.
        messages.append(
            {
                "role": "assistant",
                "content": "".join(round_text),
                "tool_calls": [
                    {"id": tc.id, "name": tc.name, "arguments": tc.arguments} for tc in pending
                ],
            }
        )
        for tc in pending:
            result = executor.execute(tc.name, tc.arguments)
            tool_results.append(result)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            yield {
                "type": "tool_call",
                "name": tc.name,
                "arguments": tc.arguments,
                "result": json.loads(result),
            }

    violations = check_grounding("".join(reply_parts), tool_results)
    yield {
        "type": "done",
        "provider": llm.name,
        "grounding_violations": violations,
    }
