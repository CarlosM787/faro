"""Anthropic provider call contract — no network, no key, no model.

The provider is the one place where Faro's own types meet a third-party SDK
surface, so these tests pin the *call* rather than the answer: a fake client
records the kwargs the provider sends, and those kwargs are then bound against
the installed SDK's real signature.

That is deliberately version-aware. `anthropic` 1.x removed `temperature` from
the Messages parameter surface; the pre-1.0 code passed it, which raised
TypeError inside the provider's `except Exception` boundary and surfaced as a
generic chat error instead of a crash — quiet, and therefore worth a test.
"""

import inspect
from collections.abc import AsyncIterator
from typing import Any, ClassVar

import pytest

from faro_api.agent.anthropic_provider import AnthropicProvider
from faro_api.agent.provider import ChatOptions, Done, Message, ToolDef


class _FakeStream:
    """Async-iterable stream that yields nothing and ends without tool use."""

    async def __aiter__(self) -> AsyncIterator[Any]:
        return
        yield  # pragma: no cover - makes this an async generator

    async def get_final_message(self) -> Any:
        class _Final:
            content: ClassVar[list[Any]] = []
            stop_reason = "end_turn"

        return _Final()


class _FakeStreamManager:
    def __init__(self, recorder: dict[str, Any], kwargs: dict[str, Any]) -> None:
        recorder.update(kwargs)

    async def __aenter__(self) -> _FakeStream:
        return _FakeStream()

    async def __aexit__(self, *exc: object) -> None:
        return None


class _FakeMessages:
    def __init__(self, recorder: dict[str, Any]) -> None:
        self._recorder = recorder

    def stream(self, **kwargs: Any) -> _FakeStreamManager:
        return _FakeStreamManager(self._recorder, kwargs)


class _FakeClient:
    def __init__(self, recorder: dict[str, Any]) -> None:
        self.messages = _FakeMessages(recorder)


def _provider(recorder: dict[str, Any]) -> AnthropicProvider:
    provider = AnthropicProvider(api_key="not-a-real-key", model="claude-sonnet-5")
    provider._client = _FakeClient(recorder)  # type: ignore[assignment]
    return provider


async def _drain(provider: AnthropicProvider, options: ChatOptions) -> list[Any]:
    messages: list[Message] = [{"role": "user", "content": "What is my Sharpe ratio?"}]
    return [event async for event in provider.stream_chat(messages, options)]


@pytest.mark.anyio
async def test_stream_kwargs_are_accepted_by_the_installed_sdk() -> None:
    """Every kwarg the provider sends must bind to the real SDK signature.

    This is the regression guard: if the SDK drops or renames a parameter we
    pass, `bind` raises here instead of failing silently at runtime behind the
    provider's exception boundary.
    """
    recorder: dict[str, Any] = {}
    await _drain(_provider(recorder), ChatOptions(system="sys", max_tokens=64))

    from anthropic.resources.messages import AsyncMessages

    signature = inspect.signature(AsyncMessages.stream)
    # `self` is bound on the real client; supply a placeholder to bind the rest.
    signature.bind(None, **recorder)


@pytest.mark.anyio
async def test_temperature_is_not_forwarded_to_anthropic() -> None:
    """`ChatOptions.temperature` is Ollama-only; Anthropic 1.x rejects it."""
    recorder: dict[str, Any] = {}
    await _drain(_provider(recorder), ChatOptions(system="sys", max_tokens=64, temperature=0.9))

    assert "temperature" not in recorder


@pytest.mark.anyio
async def test_tools_and_model_reach_the_sdk() -> None:
    """The tool contract is the agent's only numeric source — it must be sent."""
    recorder: dict[str, Any] = {}
    tool = ToolDef(
        name="get_metric",
        description="Compute one risk metric.",
        parameters={"type": "object", "properties": {}},
    )
    events = await _drain(
        _provider(recorder), ChatOptions(system="sys", max_tokens=64, tools=[tool])
    )

    assert recorder["model"] == "claude-sonnet-5"
    assert recorder["max_tokens"] == 64
    assert [t["name"] for t in recorder["tools"]] == ["get_metric"]
    # A clean run ends in Done(end), not the provider's error branch.
    assert isinstance(events[-1], Done)
    assert events[-1].stop_reason == "end"
    assert events[-1].error is None
