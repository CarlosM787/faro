"""The copilot must answer in the user's selected UI language, not silently
fall back to English for the non-EN/ES languages the picker now offers."""

import pytest

from faro_api.agent.prompts import (
    SUPPORTED_LANGUAGES,
    _CORE,
    language_name,
    system_prompt,
)


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


def test_language_name_only_names_the_generic_languages() -> None:
    assert language_name("pt") == "Portuguese (neutral Brazilian Portuguese)"
    assert language_name("fr") == "French"
    assert language_name("de") == "German"
    # en/es are hand-written, not driven by the name map; unknown is None.
    assert language_name("en") is None
    assert language_name("es") is None
    assert language_name("xx") is None


def test_chat_and_digest_request_models_accept_every_supported_language() -> None:
    # Regression: the request models used to hardcode Literal["en", "es"], so a
    # pt/fr/de request from the language picker 422'd before reaching the agent.
    from faro_api.routers.chat import ChatIn
    from faro_api.routers.digest import DigestIn

    for code in SUPPORTED_LANGUAGES:
        assert ChatIn(message="hi", language=code).language == code
        assert DigestIn(language=code).language == code


def test_request_models_reject_an_unsupported_language() -> None:
    from pydantic import ValidationError

    from faro_api.routers.digest import DigestIn

    with pytest.raises(ValidationError):
        DigestIn(language="jp")  # type: ignore[arg-type]
