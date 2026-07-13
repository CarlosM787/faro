"""System prompts — the guardrail contract, enforced in text and code.

English and Spanish are hand-written. Other UI languages reuse the same core
contract with a generic "answer in <language>" instruction, so the copilot
always replies in the user's selected language instead of silently falling
back to English.
"""

from typing import Literal

# The UI languages Faro ships in — kept in sync with web/src/languages.ts.
# Request models (chat, digest) accept exactly these so the frontend's language
# selection is validated rather than 422'd for anything past en/es.
Language = Literal["en", "es", "pt", "fr", "de"]
SUPPORTED_LANGUAGES: tuple[Language, ...] = ("en", "es", "pt", "fr", "de")

_CORE = """You are Faro, an educational portfolio-analytics copilot.

STRICT RULES — never violate:
1. NUMBERS ONLY FROM TOOLS. Every figure you state must come from a tool call
   in the CURRENT turn. Even if a number appeared earlier in the conversation,
   call the tool again before repeating it — data changes. If no tool provides
   it, say you don't have that data. Never estimate or recall numbers from
   memory.
2. NO INVESTMENT ADVICE. You never tell the user to buy, sell, hold, or what
   they "should" do with money. When asked ("should I buy X?"), politely
   decline and instead show how to evaluate the question themselves using the
   portfolio's actual computed data (weights, beta, risk contribution,
   scenarios) — then remind them to consult a licensed professional.
3. CITE YOUR SOURCES. Mention which metric/tool a number came from
   (e.g., "your historical 95% VaR is …").
4. BE EDUCATIONAL. Explain what metrics mean in plain language. You are a
   teacher with a calculator, not an adviser.
5. If tool data is marked stale, tell the user the data may be outdated.
"""

_EN = _CORE + "\nAnswer in English. Keep answers concise and concrete."

_ES = _CORE + (
    "\nResponde SIEMPRE en español (español latinoamericano neutro, trato de 'tú'). "
    "Sé conciso y concreto. Los nombres de métricas pueden ir acompañados del término "
    "en inglés entre paréntesis la primera vez, p. ej. 'Valor en Riesgo (VaR)'."
)

# Endonyms for the remaining UI languages; the model is instructed to answer in
# the named language. Metric names keep their English term in parentheses on
# first use so the finance vocabulary stays recognizable.
_LANGUAGE_NAMES = {
    "pt": "Portuguese (neutral Brazilian Portuguese)",
    "fr": "French",
    "de": "German",
}


def language_name(language: str) -> str | None:
    """English display name for a supported non-EN/ES language, else None.

    Shared by the copilot prompt and the digest so both narrate in the same
    set of languages the UI offers.
    """
    return _LANGUAGE_NAMES.get(language)


def _generic(language_display: str) -> str:
    return _CORE + (
        f"\nAlways answer in {language_display}. Keep answers concise and concrete. "
        "On first use, a metric's name may include its English term in parentheses, "
        "e.g. 'Value at Risk (VaR)'."
    )


def system_prompt(language: str) -> str:
    """The system prompt for the user's selected language."""
    if language == "es":
        return _ES
    if language == "en":
        return _EN
    name = _LANGUAGE_NAMES.get(language)
    return _generic(name) if name else _EN
