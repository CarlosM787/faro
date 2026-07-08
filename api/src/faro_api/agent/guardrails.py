"""Grounding check: numbers in the reply must trace to tool results.

Post-response verification (docs/TECH-NOTES.md guardrail #2): extract numeric
tokens from the assistant's final text and check each against the numbers the
tools actually returned. Violations are logged (and surfaced in dev) — this is
the measurable claim: unsupported numbers are detected and surfaced.
"""

import contextlib
import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Comma-grouped form must contain ≥1 comma, else plain digits (so "2024" stays whole).
_NUMBER = re.compile(r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+(?:\.\d+)?")
# Numbers that appear in normal prose/formatting, not as data claims
# (counts, confidence levels, trading days, and index names like "S&P 500"):
_TRIVIAL = {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 10.0, 20.0, 50.0, 95.0, 99.0, 100.0, 252.0, 500.0}


def _collect_numbers(value: Any, out: set[float]) -> None:
    if isinstance(value, bool):
        return
    if isinstance(value, int | float):
        out.add(round(float(value), 6))
    elif isinstance(value, dict):
        for v in value.values():
            _collect_numbers(v, out)
    elif isinstance(value, list):
        for v in value:
            _collect_numbers(v, out)
    elif isinstance(value, str):
        with contextlib.suppress(json.JSONDecodeError, ValueError):
            _collect_numbers(json.loads(value), out)
            return
        # Formatted values ("0.16%", "$3,100.00", "-2.34%") are still sources.
        for token in _NUMBER.findall(value):
            out.add(round(float(token.replace(",", "")), 6))


def _matches(candidate: float, sources: set[float]) -> bool:
    """A reply number is grounded if it matches a tool number in any common
    presentation: as-is, percentage (×/÷100), sign-flipped (drawdowns/losses
    are quoted positive), or any combination, with rounding tolerance."""
    forms = {
        candidate,
        -candidate,
        candidate / 100.0,
        -candidate / 100.0,
        candidate * 100.0,
        -candidate * 100.0,
    }
    for form in forms:
        for source in sources:
            if abs(form - source) <= max(0.005, abs(source) * 0.01):  # rounding tolerance
                return True
    return False


def check_grounding(reply_text: str, tool_results: list[str]) -> list[float]:
    """Return the list of UNGROUNDED numbers found in the reply (empty = clean)."""
    sources: set[float] = set()
    for result in tool_results:
        _collect_numbers(result, sources)

    violations: list[float] = []
    for token in _NUMBER.findall(reply_text):
        value = float(token.replace(",", ""))
        if abs(value) in _TRIVIAL or (1900 <= value <= 2100):  # years
            continue
        if not _matches(value, sources):
            violations.append(value)

    if violations:
        logger.warning("GROUNDING VIOLATION: %s not found in tool results", violations)
    return violations
