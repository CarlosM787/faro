"""Provider failure messages — the only thing the user sees when chat fails.

These assert the three properties that matter: the message names the provider,
it tells the user what to do, and it never carries a key-shaped value.
"""

import httpx
import pytest

from faro_api.agent.errors import describe_provider_failure, redact


class _FakeAuthError(Exception):
    """Stands in for anthropic.AuthenticationError (classified by type name)."""


class _FakeRateLimitError(Exception):
    """Stands in for anthropic.RateLimitError."""


# --------------------------------------------------------------------------
# Secret hygiene — the non-negotiable one
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "leak",
    [
        "sk-ant-api03-AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHH",
        "x-api-key: sk-ant-api03-SECRETVALUE1234567890",
        "Authorization=Bearer sk-abcdefghijklmnopqrstuvwxyz123456",
        "api_key = sk-ant-shouldnotappear",
    ],
)
def test_redact_removes_key_shaped_values(leak: str) -> None:
    cleaned = redact(leak)
    assert "sk-ant-" not in cleaned
    assert "SECRETVALUE" not in cleaned
    assert "shouldnotappear" not in cleaned
    assert "<redacted>" in cleaned


def test_provider_message_never_echoes_a_key() -> None:
    """A provider that puts the key in its exception text must not leak it."""
    exc = _FakeAuthError("invalid x-api-key: sk-ant-api03-LEAKEDKEYMATERIAL0123456789")
    message = describe_provider_failure("anthropic", "claude-sonnet-5", exc)

    assert "sk-ant-" not in message
    assert "LEAKEDKEYMATERIAL" not in message
    assert "<redacted>" in message


# --------------------------------------------------------------------------
# Actionability
# --------------------------------------------------------------------------


def test_auth_failure_points_at_the_key_and_the_free_alternative() -> None:
    message = describe_provider_failure(
        "anthropic", "claude-sonnet-5", _FakeAuthError("401 invalid api key")
    )
    assert "Claude" in message
    assert "claude-sonnet-5" in message
    assert "ANTHROPIC_API_KEY" in message
    assert "Ollama" in message  # the keyless way out is worth naming


def test_rate_limit_tells_the_user_to_wait() -> None:
    message = describe_provider_failure(
        "anthropic", "claude-sonnet-5", _FakeRateLimitError("429 too many requests")
    )
    assert "rate limited" in message.lower()


def test_sdk_mismatch_is_named_as_a_dependency_problem() -> None:
    """The regression that motivated this module.

    A moved SDK parameter surface raises TypeError. Reporting that as a bare
    Python error sends the user hunting for a key or network fault, which is
    exactly what happened when `temperature` was removed in anthropic 1.x.
    """
    exc = TypeError("AsyncMessages.stream() got an unexpected keyword argument 'temperature'")
    message = describe_provider_failure("anthropic", "claude-sonnet-5", exc)

    assert "SDK mismatch" in message or "installed-SDK mismatch" in message
    assert "pip install -e" in message
    assert "temperature" in message  # the provider's own detail is preserved


def test_ollama_connection_failure_says_how_to_start_it() -> None:
    exc = httpx.ConnectError("[WinError 10061] No connection could be made")
    message = describe_provider_failure("ollama", "qwen2.5:7b", exc)

    assert "Ollama" in message
    assert "qwen2.5:7b" in message
    assert "ollama serve" in message
    assert "ollama pull qwen2.5:7b" in message


def test_ollama_missing_model_says_to_pull_that_model() -> None:
    exc = httpx.HTTPStatusError(
        'model "qwen2.5:7b" not found, try pulling it first',
        request=httpx.Request("POST", "http://localhost:11434/api/chat"),
        response=httpx.Response(404),
    )
    message = describe_provider_failure("ollama", "qwen2.5:7b", exc)
    assert "ollama pull qwen2.5:7b" in message


# --------------------------------------------------------------------------
# Shape: one line, no traceback, bounded length
# --------------------------------------------------------------------------


def test_message_is_one_bounded_line_even_for_a_huge_exception() -> None:
    exc = RuntimeError("boom\n" + "x" * 5000)
    message = describe_provider_failure("ollama", "qwen2.5:7b", exc)

    assert "\n" not in message
    assert len(message) < 700
    assert "…" in message  # truncation is visible, not silent


def test_empty_exception_text_still_names_the_failure_type() -> None:
    message = describe_provider_failure("ollama", "qwen2.5:7b", RuntimeError())
    assert "RuntimeError" in message
