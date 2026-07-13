"""The copilot must answer in the user's selected UI language, not silently
fall back to English for the non-EN/ES languages the picker now offers."""

import pytest

from faro_api.agent.prompts import _CORE, system_prompt


def test_english_and_spanish_are_hand_written() -> None:
    assert "Answer in English" in system_prompt("en")
    assert "español" in system_prompt("es")


@pytest.mark.parametrize(
    ("code", "name"),
    [("pt", "Portuguese"), ("fr", "French"), ("de", "German")],
)
def test_additional_languages_get_an_answer_in_instruction(code: str, name: str) -> None:
    prompt = system_prompt(code)
    assert f"Always answer in {name}" in prompt
    # The guardrail contract must be present in every language.
    assert _CORE in prompt


def test_unknown_language_falls_back_to_english() -> None:
    assert system_prompt("xx") == system_prompt("en")


@pytest.mark.parametrize("code", ["en", "es", "pt", "fr", "de", "xx"])
def test_every_prompt_keeps_the_numbers_only_from_tools_rule(code: str) -> None:
    assert "NUMBERS ONLY FROM TOOLS" in system_prompt(code)
    assert "NO INVESTMENT ADVICE" in system_prompt(code)
