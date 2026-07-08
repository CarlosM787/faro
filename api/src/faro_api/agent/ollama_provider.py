"""Ollama provider — the free, keyless fallback (tests/CI/replication).

Talks to the local Ollama HTTP API (/api/chat) with streaming + tools.
Known quirk (plan risk #2): small local models occasionally emit malformed
tool calls; the agent loop retries, and CI uses a FakeProvider instead.
"""

import json
import uuid
from collections.abc import AsyncIterator
from typing import Any

import httpx

from faro_api.agent.provider import (
    AgentEvent,
    ChatOptions,
    Done,
    LLMProvider,
    Message,
    TextDelta,
    ToolCallRequest,
)


def _to_ollama_messages(system: str, messages: list[Message]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = [{"role": "system", "content": system}] if system else []
    for msg in messages:
        role, content = msg["role"], msg.get("content", "")
        if role == "assistant" and msg.get("tool_calls"):
            out.append(
                {
                    "role": "assistant",
                    "content": content,
                    "tool_calls": [
                        {"function": {"name": tc["name"], "arguments": tc["arguments"]}}
                        for tc in msg["tool_calls"]
                    ],
                }
            )
        elif role == "tool":
            out.append({"role": "tool", "content": content})
        else:
            out.append({"role": role, "content": content})
    return out


class OllamaProvider(LLMProvider):
    """Local open-source models via Ollama."""

    name = "ollama"

    def __init__(self, base_url: str, model: str) -> None:
        self.model = model
        self._base_url = base_url.rstrip("/")

    async def stream_chat(
        self, messages: list[Message], options: ChatOptions
    ) -> AsyncIterator[AgentEvent]:
        payload = {
            "model": self.model,
            "messages": _to_ollama_messages(options.system, messages),
            "stream": True,
            "options": {"temperature": options.temperature, "num_predict": options.max_tokens},
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    },
                }
                for t in options.tools
            ],
        }
        tool_calls: list[ToolCallRequest] = []
        try:
            async with (
                httpx.AsyncClient(timeout=300.0) as client,
                client.stream("POST", f"{self._base_url}/api/chat", json=payload) as resp,
            ):
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    chunk = json.loads(line)
                    message = chunk.get("message", {})
                    if text := message.get("content"):
                        yield TextDelta(text)
                    for tc in message.get("tool_calls") or []:
                        fn = tc.get("function", {})
                        args = fn.get("arguments") or {}
                        if isinstance(args, str):  # some models emit JSON strings
                            args = json.loads(args)
                        tool_calls.append(
                            ToolCallRequest(
                                id=f"call_{uuid.uuid4().hex[:8]}",
                                name=str(fn.get("name", "")),
                                arguments=args,
                            )
                        )
                    if chunk.get("done"):
                        break
        except (httpx.HTTPError, json.JSONDecodeError) as exc:
            yield Done(stop_reason="error", error=f"Ollama unavailable: {exc}")
            return

        for tc in tool_calls:
            yield tc
        yield Done(stop_reason="tool_use" if tool_calls else "end")
