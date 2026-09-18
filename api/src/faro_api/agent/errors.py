"""Provider failure messages the user can act on.

A provider failure reaches the UI as the `error` field of the SSE `done` event,
so it is the *only* thing the user sees when the copilot cannot answer. Three
rules follow from that:

1. **Say what to do.** A raw exception string is a dead end: "[WinError 10061]
   No connection could be made" does not tell anyone to start Ollama. Every
   message here ends in an action.
2. **No tracebacks, no secrets.** One line, provider and model named, the useful
   part of the provider's own message kept, and anything key-shaped redacted
   before it leaves the process.
3. **Never disguise which model answered.** These helpers describe failures;
   they never substitute a different provider. Provider choice happens once, in
   `loop.get_provider()`, and a failure is reported against the provider that
   actually failed — a silent fallback would change what an answer *means*.

This module deliberately imports no SDK: it classifies by exception type name
and message text, so it stays dependency-free and unit-testable offline.
"""

import re

# Key-shaped values that must never be echoed back to a client. Anthropic keys
# are the realistic case here; the others are cheap insurance.
_SECRET_PATTERNS = (
    re.compile(r"sk-ant-[A-Za-z0-9_\-]+"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)\b(api[-_]?key|authorization|x-api-key)\b\s*[:=]\s*\S+"),
)

_MAX_DETAIL = 300  # keep the provider's own message, drop essay-length dumps


def redact(text: str) -> str:
    """Replace key-shaped substrings with a placeholder."""
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("<redacted>", text)
    return text


def _detail(exc: Exception) -> str:
    """The provider's own message: one line, trimmed, redacted."""
    raw = " ".join(str(exc).split())  # collapse newlines/indentation
    if not raw:
        raw = type(exc).__name__
    if len(raw) > _MAX_DETAIL:
        raw = raw[:_MAX_DETAIL].rstrip() + "…"
    return redact(raw)


def _anthropic_action(exc: Exception) -> str:
    """What the user should do, inferred from the failure's shape."""
    name = type(exc).__name__.lower()
    text = str(exc).lower()

    if "authentication" in name or "permissiondenied" in name or "401" in text:
        return (
            "Check ANTHROPIC_API_KEY in .env — or remove it to use the free local "
            "Ollama model instead."
        )
    if "ratelimit" in name or "429" in text:
        return "You are being rate limited; wait a moment and ask again."
    if "notfound" in name or "404" in text:
        return (
            "The configured model may not be available to this key — check "
            "ANTHROPIC_MODEL (currently the app's default is a Claude Sonnet model)."
        )
    if "overloaded" in name or "529" in text or "500" in text:
        return "Anthropic is having trouble on their side; retry shortly."
    if isinstance(exc, TypeError) or "unexpected keyword" in text:
        # The failure this module was written for: an SDK whose parameter
        # surface moved underneath us. It is a dependency problem, not a
        # credential or network problem, and it needs saying out loud.
        return (
            "This looks like an installed-SDK mismatch rather than a key or network "
            'problem — reinstall the pinned dependencies with: pip install -e ".[dev]"'
        )
    if "connect" in name or "timeout" in name or "connection" in text:
        return "Check your network connection and try again."
    return 'Retry; if it persists, reinstall dependencies with: pip install -e ".[dev]"'


def _ollama_action(exc: Exception, model: str) -> str:
    text = str(exc).lower()
    if "404" in text or "not found" in text:
        return f"The model is not installed locally — run: ollama pull {model}"
    if "timeout" in text or "timed out" in text:
        return (
            "The local model did not answer in time; a smaller model or a warmer "
            "start usually fixes it."
        )
    # Connection refused is by far the most common keyless failure.
    return (
        "Ollama does not appear to be running — start it (`ollama serve`), then "
        f"make sure the model is installed: ollama pull {model}. "
        "In Docker, set OLLAMA_HOST=0.0.0.0 so the container can reach it."
    )


def describe_provider_failure(provider: str, model: str, exc: Exception) -> str:
    """One actionable line for the SSE `done` event's `error` field.

    Shape: ``<what failed> — <provider's own message> <what to do>``
    """
    action = _anthropic_action(exc) if provider == "anthropic" else _ollama_action(exc, model)
    label = "Claude" if provider == "anthropic" else "Ollama"
    return f"{label} ({model}) could not complete the answer — {_detail(exc)}. {action}"
