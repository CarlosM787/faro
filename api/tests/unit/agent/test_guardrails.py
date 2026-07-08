"""Grounding checker: reply numbers must trace to tool results."""

import json

from faro_api.agent.guardrails import check_grounding

TOOL_RESULT = json.dumps({"metric": "sharpe", "value": 0.5485, "var_hist_95": 0.0162})


def test_grounded_reply_passes() -> None:
    reply = "Your Sharpe ratio is 0.55, and your 95% VaR is 1.62% per day."
    assert check_grounding(reply, [TOOL_RESULT]) == []


def test_hallucinated_number_is_caught() -> None:
    reply = "Your Sharpe ratio is 0.55 and your portfolio gained 37.8% last month."
    violations = check_grounding(reply, [TOOL_RESULT])
    assert 37.8 in violations


def test_percentage_and_sign_forms_are_grounded() -> None:
    # 0.0162 in tool results may legitimately appear as 1.62 (%), or negative
    reply = "You could lose about 1.62% — that is the Value at Risk."
    assert check_grounding(reply, [TOOL_RESULT]) == []


def test_trivial_numbers_and_years_ignored() -> None:
    reply = "Over the last 2 years (2024 to 2026), on 95% of days, 100% of positions..."
    assert check_grounding(reply, [TOOL_RESULT]) == []


def test_no_tools_any_number_flagged() -> None:
    assert check_grounding("You gained 12.34% this year!", []) == [12.34]
