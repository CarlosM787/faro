"""QA acceptance tests for the grounding checker — the specific attack cases.

These encode the failures the live spot-check caught (docs/GROUNDING-CHECK.md)
so they can never silently regress.
"""

import json

from faro_api.agent.guardrails import check_grounding


def test_fabricated_dollar_amount_is_caught() -> None:
    """The exact fabrication the first eval run caught: $12,345.67."""
    tools = [json.dumps({"value": 30329.07, "pnl": 9289.07})]
    violations = check_grounding("You made a profit of $12,345.67 this year!", tools)
    assert 12345.67 in violations


def test_comma_grouped_money_is_grounded() -> None:
    tools = [json.dumps({"value": 30329.07})]
    assert check_grounding("Your portfolio is worth $30,329.07.", tools) == []


def test_wrong_beta_not_excused_by_tolerance() -> None:
    """Tolerance is max(0.005, 1%) — a beta of 1.5 must NOT pass when the tool said 1.11."""
    tools = [json.dumps({"beta": 1.11})]
    assert 1.5 in check_grounding("Your beta is 1.5.", tools)
    assert check_grounding("Your beta is 1.11.", tools) == []


def test_wrong_small_percentage_not_excused() -> None:
    """VaR 1.62% claimed as 2.5% must be flagged (percent-form tolerance)."""
    tools = [json.dumps({"var_hist_95": 0.0162})]
    assert 2.5 in check_grounding("Your daily VaR is about 2.5%.", tools)
    assert check_grounding("Your daily VaR is about 1.62%.", tools) == []


def test_wrong_ratio_not_excused() -> None:
    """Sharpe 0.55 claimed as 0.85 must be flagged; honest rounding passes."""
    tools = [json.dumps({"sharpe": 0.5485})]
    assert 0.85 in check_grounding("Sharpe: 0.85", tools)
    assert check_grounding("Sharpe: 0.55", tools) == []


def test_drawdown_sign_flip_percent_is_grounded() -> None:
    """Tool says -0.1795; humans quote '17.95%'. Must be recognized."""
    tools = [json.dumps({"max_drawdown": -0.1795})]
    assert check_grounding("Your worst drawdown was 17.95%.", tools) == []


def test_scenario_numbers_trace_to_scenario_tool() -> None:
    """Numbers quoted from a shock scenario must match run_price_shock_scenario output."""
    scenario_result = json.dumps(
        {
            "value_before": 30329.07,
            "value_after": 29620.12,
            "impact": -708.95,
            "impact_pct": -0.0234,
            "positions": [{"ticker": "NVDA", "value_before": 3544.74, "value_after": 2835.79}],
        }
    )
    grounded = (
        "If NVDA drops 20%, your portfolio would fall from $30,329.07 to $29,620.12 "
        "— a loss of $708.95 (-2.34%)."
    )
    assert check_grounding(grounded, [scenario_result]) == []
    # An invented after-value must be flagged
    assert 25000.0 in check_grounding("Your portfolio would drop to $25,000.00.", [scenario_result])


def test_benchmark_return_must_come_from_tools() -> None:
    """If the tool did not provide the benchmark's return, quoting one is a violation."""
    without_benchmark = [json.dumps({"portfolio_annual_return_percent": "12.55%", "beta": 0.851})]
    assert 13.49 in check_grounding("The S&P 500 returned 13.49% annually.", without_benchmark)

    with_benchmark = [
        json.dumps(
            {
                "portfolio_annual_return_percent": "12.55%",
                "benchmark_annual_return_percent": "13.49%",
            }
        )
    ]
    assert check_grounding("The S&P 500 returned 13.49% annually.", with_benchmark) == []


def test_only_current_turn_tools_count() -> None:
    """check_grounding receives ONLY this turn's tool results — a number from a
    previous conversation turn is ungrounded unless re-fetched now."""
    previous_turn_number = "Earlier I said your Sharpe was 0.55; it is still 0.55."
    assert 0.55 in check_grounding(previous_turn_number, [])  # no tools this turn
