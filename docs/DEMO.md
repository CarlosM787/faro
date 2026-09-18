# Faro V1 — the demo

One command shows the whole product, with **no API key and no paid service**.
This page records a real run: the numbers and answers below are copied from the
transcript, not written by hand.

```bash
docker compose up --build            # or: python -m uvicorn faro_api.main:app --port 8000
python api/scripts/demo_v1.py        # add --skip-copilot for the engine only (instant)
```

The script walks five questions in order and ends by printing what the product
does **not** mean. `--skip-copilot` needs nothing but the API; the full run needs
a local model (`ollama pull qwen2.5:7b`) and takes a minute or two per question.

---

## 1. What you give it

A list of positions. That is the entire input — no bank login, no brokerage
link, no cloud account, no key.

```
Demo Portfolio  (USD)
ticker      shares    cost basis     purchased
AAPL         25.00       $168.20    2024-03-15
MSFT         12.00       $402.50    2024-01-22
NVDA         18.00        $88.75    2024-05-10
KO           60.00        $59.10    2024-02-05
VZ           45.00        $40.30    2024-06-03
VTI          20.00       $252.40    2024-04-18
```

## 2. What happens

A pure `numpy`/`pandas` engine computes the risk metrics from their documented
formulas. Nothing here involves a language model.

```
window 2024-09-17 to 2026-09-17 · benchmark SPY · risk-free 4.30% · stale data: False

  value                     $33,311.37
  profit / loss             $12,271.37  (58.32% on cost)
  annualized return         18.35%
  annualized volatility     15.93%
  Sharpe                    0.8723
  Sortino                   1.3023
  beta vs SPY               0.8413
  Jensen's alpha            2.64%
  VaR 95% (historical)      1.41%
  VaR 95% (parametric)      1.58%
  CVaR 95%                  2.16%
  max drawdown              -17.98%
  concentration (HHI)       0.1904
  largest position weight   25.29%
```

Each metric has two independent test layers: hand-computed references on tiny
fixtures, and cross-checks against `quantstats`/`scipy`. The dashboard and the
copilot both read this same service layer, so the chat and the charts cannot
disagree.

## 3. What you get

The copilot may not produce a number on its own. Its only sanctioned source is
five typed tools that dispatch into the engine above — so every answer arrives
with its receipts.

```
--- ASKED: What is my Sharpe ratio and what does it mean? ---
provider: ollama
computations the copilot was allowed to use:
  get_metric({"metric": "sharpe"}) -> {"metric": "sharpe", "value": 0.872275,
                                       "window": "2024-09-17 to 2026-09-17",
                                       "risk_free_rate": 0.043}

answer:
Your Sharpe ratio is 0.872, calculated over a 2-year daily window from
September 17, 2024, to September 17, 2026. The Sharpe ratio measures the excess
return (return above the risk-free rate) per unit of deviation in an investment.
[…] A higher Sharpe ratio is generally better […] a ratio of 0.872 is considered
moderate and may vary depending on your risk tolerance and investment goals.

>>> GROUNDING CHECK: every number traced to a computation. No warning.
```

The same question in Spanish, answered in Spanish, from the same engine:

```
--- ASKED (es): ¿Cuál es mi Valor en Riesgo al 95%? ---
  get_metric({"metric": "var_hist_95"}) -> {"value": 0.014136, …}

answer:
Tu Valor en Riesgo al 95% (VaR) para el período de 2024-09-17 a 2026-09-17 es de
1.4136%. Esto significa que hay un 95% de probabilidad de que tu cartera no
experimente una pérdida superior a este valor en el peor escenario.

>>> GROUNDING CHECK: every number traced to a computation. No warning.
```

## 4. Why that is useful

Ask it for advice and it refuses, then reframes using figures it actually
computed:

```
--- ASKED: Should I buy TSLA? ---
  get_portfolio_summary({})           -> {"value": 33311.37, "pnl_pct": 0.5832, …}
  get_position_detail({"ticker":"TSLA"}) -> {"error": "TSLA is not in this portfolio", …}

answer:
I can't provide advice on whether to buy TSLA or any stock. Instead, let's look
at TSLA's current position in your portfolio and its risk contribution. […]
TSLA is not currently part of your portfolio.
```

**And when the model states a number it did not compute, the app says so.** A
real example caught while building this demo — same question, a different run:

> the model wrote `$12,271.37 (5.83% of total value)`
> the tool had returned `pnl_pct: 0.5832` → **58.32%**

A factor of ten out, phrased fluently and formatted professionally. The checker
flagged it:

```
>>> GROUNDING CHECK: 1 number(s) NOT traceable to a computation this turn: [5.83]
>>> In the app this renders as an amber warning under the reply.
```

That is the product. Not "the model never invents numbers" — no one can promise
that — but **unsupported numbers are detected and surfaced**.

> **The local model is nondeterministic**, so the advice question comes back
> clean on some runs and flagged on others. Both are correct behaviour: the
> claim is about detection, not about how often a model slips. For a systematic
> measurement see [GROUNDING-CHECK.md](GROUNDING-CHECK.md) and the committed
> logs in [eval-logs/](eval-logs/) — in the shipped multi-turn configuration a
> 7B model produced **139 flagged figures across 20 questions, every one
> surfaced**.

## 5. What this does not mean

Printed by the demo itself, because it matters more than the demo:

- **Grounding is detection, not prevention.** The checker surfaces unsupported numbers; it does not stop a model from generating them.
- **A flagged number is the feature working.** On a weak local model in a long conversation, expect many (correct) warnings — safe but noisy.
- **None of this is investment advice**, a recommendation, or a forecast. No trade is executed, no brokerage is linked, no return is predicted.
- **The metrics describe a past window of daily closes.** They are not a prediction of future risk or return, and Sharpe/VaR/beta are not claims about profitability.
- **Free daily-bar data only** (yfinance, Stooq fallback): no intraday, and it can be stale — the app flags that.
- **Single-user and local by design**: no auth, no multi-tenancy.

---

## Provider

`GET /health` reports which model is actually answering:

```json
{"status":"ok","version":"0.1.0","llm_provider":"ollama"}
```

With `ANTHROPIC_API_KEY` unset the copilot runs on a local Ollama model for $0.
Set the key and the identical flow runs on Claude — one environment variable, no
code change. **Faro never silently swaps providers:** the provider is chosen once
at startup, and if it fails you get an error naming that provider rather than a
quiet answer from a different model. A failure says what broke and what to do:

```
Ollama (qwen2.5:7b) could not complete the answer — All connection attempts
failed. Ollama does not appear to be running — start it (`ollama serve`), then
make sure the model is installed: ollama pull qwen2.5:7b. In Docker, set
OLLAMA_HOST=0.0.0.0 so the container can reach it.
```

**Not yet measured:** the headline eval numbers come from the local 7B model.
The Claude-vs-local comparison needs a real key and has not been run — see
[GROUNDING-CHECK.md](GROUNDING-CHECK.md). No figure on this page is quoted for
Claude.

*Transcript recorded 2026-09-17 against commit `56a39da`, provider `ollama`,
model `qwen2.5:7b`, on the seeded demo portfolio.*
