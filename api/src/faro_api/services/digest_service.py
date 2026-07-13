"""Daily digest: computed facts → LLM narrative (Cortex-style, grounded).

The LLM receives ONLY a JSON block of numbers computed by the quant engine
and is asked to narrate them — the same grounding principle as chat, checked
by the same guardrail.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

from faro_api.agent.guardrails import check_grounding
from faro_api.agent.prompts import language_name
from faro_api.agent.provider import ChatOptions, Done, LLMProvider, TextDelta
from faro_api.db.models import Position
from faro_api.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)

_PROMPT_EN = (
    "Write a short daily portfolio digest in English, using ONLY the numbers in the "
    "FACTS JSON below. Structure: a one-line headline, then sections 'What moved', "
    "'Risk check', and 'Upcoming events' (omit a section if no data). Plain, "
    "educational language; cite figures exactly as given. End with: 'Educational "
    "digest — not investment advice.'\n\nFACTS:\n"
)
_PROMPT_ES = (
    "Escribe un resumen diario breve del portafolio en español (latinoamericano neutro, "
    "trato de 'tú'), usando SOLO los números del JSON de DATOS. Estructura: un titular de "
    "una línea, luego secciones '¿Qué se movió?', 'Chequeo de riesgo' y 'Próximos "
    "eventos' (omite una sección si no hay datos). Lenguaje claro y educativo; cita las "
    "cifras exactamente como aparecen. Termina con: 'Resumen educativo — no es asesoría "
    "de inversión.'\n\nDATOS:\n"
)


def _digest_prompt(language: str) -> str:
    """Digest instruction in the user's language (mirrors the copilot's set)."""
    if language == "es":
        return _PROMPT_ES
    name = language_name(language)
    if name is None:  # en, or any unrecognized code
        return _PROMPT_EN
    return (
        f"Write a short daily portfolio digest in {name}, using ONLY the numbers in the "
        "FACTS JSON below. Structure: a one-line headline, then three sections whose titles "
        "translate to 'What moved', 'Risk check', and 'Upcoming events' (omit a section if "
        "no data). Plain, educational language; cite figures exactly as given. End with a "
        "line that translates to 'Educational digest — not investment advice.'\n\nFACTS:\n"
    )


def _upcoming_earnings(tickers: list[str]) -> list[dict[str, str]]:
    """Best-effort earnings dates via yfinance; failures are silently skipped."""
    events: list[dict[str, str]] = []
    try:
        import yfinance
    except ImportError:  # pragma: no cover
        return events
    for ticker in tickers:
        try:
            calendar = yfinance.Ticker(ticker).calendar
            dates = calendar.get("Earnings Date") if isinstance(calendar, dict) else None
            if dates:
                events.append({"ticker": ticker, "earnings_date": str(dates[0])})
        except Exception:
            continue
    return events


@dataclass(frozen=True)
class DigestResult:
    markdown: str
    facts: dict[str, Any]
    grounding_violations: list[float]
    provider: str
    error: str | None = None


class DigestService:
    """Builds the facts block and asks the LLM to narrate it."""

    def __init__(self, metrics_service: MetricsService) -> None:
        self._metrics = metrics_service

    def build_facts(
        self, positions: list[Position], include_earnings: bool = True
    ) -> dict[str, Any]:
        full = self._metrics.full_metrics(positions)
        movers = sorted(full.positions, key=lambda p: abs(p.pnl_pct), reverse=True)[:3]
        risks = sorted(full.positions, key=lambda p: p.risk_contribution, reverse=True)[:3]
        facts: dict[str, Any] = {
            "date": f"{full.window_end:%Y-%m-%d}",
            "portfolio_value": round(full.value, 2),
            "day_change_percent": f"{full.day_change_pct * 100:.2f}%",
            "total_pnl": round(full.pnl, 2),
            "total_pnl_percent": f"{full.pnl_pct * 100:.2f}%",
            "sharpe_ratio": round(full.sharpe, 2),
            "var_95_percent_daily": f"{full.var_hist_95 * 100:.2f}%",
            "beta_vs_benchmark": round(full.beta, 2),
            "benchmark": full.benchmark,
            "top_movers_since_purchase": [
                {"ticker": p.ticker, "pnl_percent": f"{p.pnl_pct * 100:.2f}%"} for p in movers
            ],
            "top_risk_contributors": [
                {"ticker": p.ticker, "share_of_risk": f"{p.risk_contribution * 100:.1f}%"}
                for p in risks
            ],
            "data_stale": full.stale,
        }
        if include_earnings:
            events = _upcoming_earnings([p.ticker for p in full.positions])
            if events:
                facts["upcoming_earnings"] = events
        return facts

    async def generate(
        self,
        positions: list[Position],
        language: str,
        provider: LLMProvider,
        include_earnings: bool = True,
    ) -> DigestResult:
        facts = self.build_facts(positions, include_earnings=include_earnings)
        facts_json = json.dumps(facts, ensure_ascii=False)
        prompt = _digest_prompt(language) + facts_json

        parts: list[str] = []
        error: str | None = None
        async for event in provider.stream_chat(
            [{"role": "user", "content": prompt}], ChatOptions(max_tokens=800)
        ):
            if isinstance(event, TextDelta):
                parts.append(event.text)
            elif isinstance(event, Done) and event.stop_reason == "error":
                error = event.error

        markdown = "".join(parts).strip()
        violations = check_grounding(markdown, [facts_json]) if markdown else []
        return DigestResult(
            markdown=markdown,
            facts=facts,
            grounding_violations=violations,
            provider=provider.name,
            error=error,
        )
