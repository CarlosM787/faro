"""Faro V1 demo — the whole product in one reproducible run, with no API key.

Answers five questions in order, using only what the app actually does today:

  1. What do I give it?      a portfolio of positions
  2. What happens?           a pure-Python engine computes the risk metrics
  3. What do I get?          a copilot answer whose every number came from a tool
  4. Why is that useful?     when the model states a number it did not compute,
                             the app says so -- out loud, in the reply
  5. What does it NOT mean?  printed at the end, deliberately

Usage (the API must be running; no key required -- Ollama is the free default):

    python -m uvicorn faro_api.main:app --port 8000      # from the repo root
    python scripts/demo_v1.py                            # then this

    python scripts/demo_v1.py --url http://localhost:8000 --portfolio 1

Exit code is 0 when the demo completed and non-zero only if the API or the
provider could not be reached. A flagged number is a *successful* demo: it is
the feature. Nothing here is investment advice, and no figure is a forecast.
"""

import argparse
import json
import sys
from typing import Any

import httpx

RULE = "=" * 78


def _h(title: str) -> None:
    print(f"\n{RULE}\n{title}\n{RULE}")


def _money(x: float) -> str:
    return f"${x:,.2f}"


def _pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def ask(url: str, portfolio: int, question: str, language: str = "en") -> dict[str, Any]:
    """One independent copilot turn. Returns the assembled answer and verdict."""
    body = {"message": question, "language": language, "fresh": True}
    text_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    done: dict[str, Any] = {}

    with (
        httpx.Client(timeout=600.0) as client,
        client.stream(
            "POST",
            f"{url}/portfolios/{portfolio}/chat",
            content=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
        ) as resp,
    ):
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line.startswith("data: "):
                continue
            event = json.loads(line[6:])
            kind = event.get("type")
            if kind == "text":
                text_parts.append(event["text"])
            elif kind == "tool_call":
                tool_calls.append(event)
            elif kind == "done":
                done = event

    return {
        "answer": "".join(text_parts).strip(),
        "tool_calls": tool_calls,
        "violations": done.get("grounding_violations", []),
        "provider": done.get("provider", "?"),
        "error": done.get("error"),
    }


def _show_turn(label: str, turn: dict[str, Any]) -> None:
    print(f"\n--- {label} ---")
    if turn["error"]:
        print(f"PROVIDER ERROR: {turn['error']}")
        return

    print(f"provider: {turn['provider']}")
    if turn["tool_calls"]:
        print("computations the copilot was allowed to use:")
        for tc in turn["tool_calls"]:
            result = json.dumps(tc.get("result"), ensure_ascii=False)
            if len(result) > 150:
                result = result[:150] + "…"
            print(f"  {tc['name']}({json.dumps(tc.get('arguments'))}) -> {result}")
    else:
        print("computations used: NONE (the copilot answered without calling a tool)")

    print(f"\nanswer:\n{turn['answer']}")

    violations = turn["violations"]
    if violations:
        print(f"\n>>> GROUNDING CHECK: {len(violations)} number(s) NOT traceable to a")
        print(f">>> computation this turn: {violations}")
        print(">>> In the app this renders as an amber warning under the reply.")
        print(">>> This is the product working, not the product failing.")
    else:
        print("\n>>> GROUNDING CHECK: every number traced to a computation. No warning.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Faro V1 demo (no API key required).")
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--portfolio", type=int, default=1)
    ap.add_argument(
        "--skip-copilot",
        action="store_true",
        help="Only show the deterministic engine (instant; no model needed).",
    )
    args = ap.parse_args()
    url = args.url.rstrip("/")

    try:
        health = httpx.get(f"{url}/health", timeout=20.0).json()
    except httpx.HTTPError as exc:
        print(f"Could not reach the API at {url} -- is it running?\n  {exc}", file=sys.stderr)
        return 2

    _h("FARO V1 DEMO")
    print(
        f"API {url}  ·  version {health.get('version')}  ·  LLM provider: "
        f"{health.get('llm_provider')}"
    )
    print("No API key is needed: with ANTHROPIC_API_KEY unset the copilot runs on a")
    print("local Ollama model for $0. Set the key and the same flow runs on Claude.")

    # ---------------------------------------------------------------- 1. input
    _h("1. WHAT YOU GIVE IT — a portfolio")
    portfolio = httpx.get(f"{url}/portfolios/{args.portfolio}", timeout=30.0).json()
    print(f"{portfolio['name']}  ({portfolio['base_currency']})")
    print(f"{'ticker':<8}{'shares':>10}{'cost basis':>14}{'purchased':>14}")
    for pos in portfolio["positions"]:
        print(
            f"{pos['ticker']:<8}{pos['shares']:>10.2f}"
            f"{_money(pos['cost_basis']):>14}{pos['purchase_date']:>14}"
        )
    print("\nThat is the whole input. No bank login, no brokerage link, no cloud account.")

    # -------------------------------------------------------------- 2. compute
    _h("2. WHAT HAPPENS — a deterministic engine computes the risk metrics")
    m = httpx.get(f"{url}/portfolios/{args.portfolio}/metrics", timeout=180.0).json()
    print(
        f"window {str(m['window_start'])[:10]} to {str(m['window_end'])[:10]}"
        f"  ·  benchmark {m['benchmark']}  ·  risk-free {_pct(m['risk_free_rate'])}"
        f"  ·  stale data: {m['stale']}"
    )
    rows = [
        ("value", _money(m["value"])),
        ("cost", _money(m["cost"])),
        ("profit / loss", f"{_money(m['pnl'])}  ({_pct(m['pnl_pct'])} on cost)"),
        ("annualized return", _pct(m["annual_return"])),
        ("annualized volatility", _pct(m["annual_volatility"])),
        ("Sharpe", f"{m['sharpe']:.4f}"),
        ("Sortino", f"{m['sortino']:.4f}"),
        ("beta vs " + m["benchmark"], f"{m['beta']:.4f}"),
        ("Jensen's alpha", _pct(m["alpha"])),
        ("VaR 95% (historical)", _pct(m["var_hist_95"])),
        ("VaR 95% (parametric)", _pct(m["var_param_95"])),
        ("CVaR 95%", _pct(m["cvar_95"])),
        ("max drawdown", _pct(m["max_drawdown"])),
        ("concentration (HHI)", f"{m['hhi']:.4f}"),
        ("largest position weight", _pct(m["top_weight"])),
    ]
    for name, value in rows:
        print(f"  {name:<26}{value}")
    print("\nEvery one of these is implemented from its documented formula in pure")
    print("numpy/pandas and unit-tested twice: against hand-computed references and")
    print("against independent libraries. The dashboard and the copilot read this")
    print("same service layer, so the chat and the charts cannot disagree.")

    if args.skip_copilot:
        _h("COPILOT SKIPPED (--skip-copilot)")
        return 0

    # -------------------------------------------------------------- 3. copilot
    _h("3. WHAT YOU GET — a copilot that may only quote the engine")
    print("The copilot has five typed tools and no other sanctioned source of numbers.")
    print("A local 7B model is slow: expect roughly a minute or two per question.")

    clean = ask(url, args.portfolio, "What is my Sharpe ratio and what does it mean?")
    _show_turn("ASKED: What is my Sharpe ratio and what does it mean?", clean)
    if clean["error"]:
        return 3

    es = ask(url, args.portfolio, "¿Cuál es mi Valor en Riesgo al 95%?", language="es")
    _show_turn("ASKED (es): ¿Cuál es mi Valor en Riesgo al 95%?", es)

    # --------------------------------------------------------------- 4. the point
    _h("4. WHY THAT IS USEFUL — the checker, on a question built to strain it")
    print("'Should I buy TSLA?' must be refused (educational tool, not an adviser),")
    print("and the reframe then restates real computed figures -- the place a small")
    print("model is most likely to get a number subtly wrong.")
    print()
    print("Whether this particular run gets flagged is NOT guaranteed: the local model")
    print("is nondeterministic, so the same question can come back clean one minute and")
    print("flagged the next. Both outcomes below are correct behaviour -- the claim is")
    print("that unsupported numbers are DETECTED, not that they always occur. For runs")
    print("where they do, see the committed logs in docs/eval-logs/ (the shipped")
    print("multi-turn configuration flagged 139 figures across 20 questions, every one")
    print("surfaced). One real example caught while building this demo: the model wrote")
    print("'$12,271.37 (5.83% of total value)' when the tool had returned pnl_pct")
    print("0.5832 -- a factor of ten out. The checker flagged 5.83.")
    trap = ask(url, args.portfolio, "Should I buy TSLA?")
    _show_turn("ASKED: Should I buy TSLA?", trap)
    if not trap["violations"] and not trap["error"]:
        print("\n(This run came back clean. Run it again to see the other case; the")
        print(" refusal above is the part that must hold every time.)")

    # ----------------------------------------------------------------- 5. limits
    _h("5. WHAT THIS DOES NOT MEAN")
    for line in (
        "Grounding is DETECTION, not prevention. The checker surfaces unsupported",
        "  numbers; it does not stop a model from generating them.",
        "A flagged number is the feature working. On a weak local model in a long",
        "  conversation, expect many (correct) warnings -- safe but noisy.",
        "None of this is investment advice, a recommendation, or a forecast. No",
        "  trade is executed, no brokerage is linked, no return is predicted.",
        "The metrics describe a PAST window of daily closes. They are not a",
        "  prediction of future risk or return, and Sharpe/VaR/beta are not claims",
        "  about profitability.",
        "Free daily-bar data only (yfinance, Stooq fallback): no intraday, and it",
        "  can be stale -- the app flags that, see 'stale data' above.",
        "Single-user and local by design: no auth, no multi-tenancy.",
    ):
        print(f"  {line}" if line.startswith("  ") else f"- {line}")

    _h("DEMO COMPLETE")
    print("Reproduce: docker compose up --build, then python scripts/demo_v1.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
