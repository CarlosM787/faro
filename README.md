<p align="center">
  <img src="brand/logo-wordmark.svg" alt="Faro — AI Portfolio Copilot" width="380">
</p>

# Faro — AI Portfolio Copilot

[![CI](https://github.com/CarlosM787/faro/actions/workflows/ci.yml/badge.svg)](https://github.com/CarlosM787/faro/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Institutional-grade portfolio analytics computed from first principles, explained by an AI copilot that has to show its work.** Every number the copilot states is checked against the deterministic quant engine's tool outputs — unsupported figures are detected and flagged, not silently shipped. Fully bilingual (English / Español). Self-hosted; runs free without any API key. Installable to your home screen or desktop (web-app manifest).

**Website: [faroquant.com](https://faroquant.com)** · Live CI · MIT

> ⚠️ Faro is an **educational tool, not an investment adviser**. It never executes trades, never links to brokerages, and is instructed to refuse personalized investment advice (a behavior exercised in the public eval), with educational disclaimers throughout — a deliberate compliance boundary. Legal docs (EN/ES): [docs/legal/](docs/legal/).

![Faro dashboard — portfolio value, risk metric cards, performance vs SPY, correlation heatmap](docs/screenshots/dashboard.png)

<p align="center"><em>The copilot, in Spanish, citing benchmark returns straight from the <code>compare_to_benchmark</code> tool — every figure traceable to a computation:</em></p>

![Faro copilot answering in Spanish, grounded in tool output](docs/screenshots/copilot.png)

## The thesis

The #1 failure mode of LLM finance apps is **hallucinated numbers**. Faro demonstrates the architecture that fixes it:

> A deterministic, unit-tested quant engine underneath; an LLM agent on top whose **only** sanctioned source of numbers is calling that engine's tools. A post-response **grounding checker** verifies every figure in every answer against the tool outputs and flags any that don't trace to a computation (see `agent/guardrails.py` and `scripts/grounding_check.py` — the claim is *detected and surfaced*, and it's measured, not assumed).

The dashboard and the copilot call the **same service layer** — one engine, two consumers — so their numbers can never disagree.

## Architecture

```
web (React 18 + TS + Tailwind + Recharts, i18next EN/ES)
 │  REST + SSE (same-origin /api)
 ▼
api (FastAPI · Python 3.12 · mypy strict)
 ├── routers/     portfolios · metrics · series · scenarios · chat (SSE) · digest
 ├── agent/       provider-agnostic LLM layer ── Claude (primary) ⇄ Ollama (free fallback)
 │                tool schemas · EN/ES system prompts · grounding guardrail · loop
 ├── services/    ★ single computation path shared by REST and agent tools
 ├── quant/       ★ pure numpy/pandas · every formula documented · reference-tested
 ├── data/        yfinance → Stooq fallback · parquet cache · offline degradation
 └── db/          SQLite + SQLAlchemy 2.0 (Decimal at the boundary)
```

**LLM switching is env-only.** Set `ANTHROPIC_API_KEY` → Claude (`claude-sonnet-5`). Leave it unset → local [Ollama](https://ollama.com) (`qwen2.5:7b`). Zero code changes; tests/CI use a scripted fake provider and need neither.

## Quant engine — formulas, not black boxes

`quant/` is pure (arrays in, numbers out, no I/O) and implements every metric from its documented formula. Each has two layers of tests: **hand-computed references** on tiny fixtures (derivations in test comments) and **cross-checks vs independent implementations** (quantstats/scipy — dev-dependencies only, never imported by the engine).

| Metric | Implementation | Cross-check |
|---|---|---|
| Returns (simple/log), annualized return & vol | `P_t/P_{t-1}−1`, `ln(P_t/P_{t-1})`, geometric ^252, σ·√252 (ddof=1) | quantstats |
| Sharpe (1966) / Sortino (1991) | excess-return mean over (downside) deviation, geometric rf de-annualization | quantstats |
| Beta / Jensen's alpha (1968) | `Cov(r_p,r_b)/Var(r_b)`; `α = R_p − [R_f + β(R_b−R_f)]` | scipy.linregress |
| Historical VaR / CVaR | empirical quantile; tail mean | numpy quantile |
| Parametric VaR | `−(μ + z·σ)`, inverse-normal CDF **implemented from first principles** (Acklam 2003) | scipy.stats.norm |
| Max drawdown + series | `min(P/cummax(P) − 1)` | quantstats |
| Correlation, HHI, top weight | Pearson matrix; `Σw²` | numpy manual |
| Risk contributions | Euler decomposition `w_i·Cov(r_i,r_p)/σ_p²` | property test: Σ = 1 |

## The copilot

Five tools — `get_portfolio_summary`, `get_metric`, `get_position_detail`, `run_price_shock_scenario`, `compare_to_benchmark` — dispatch into the same services the dashboard uses. Guardrails:

1. **System prompt contract**: numbers only from tools; educational, never advice; cite metrics; answer in the user's language (EN/ES).
2. **Grounding checker**: after every reply, numeric tokens are matched against tool outputs; violations are returned in the SSE `done` event and rendered as a visible amber warning under the message (and on digests). The eval runs in two modes — `--fresh` (per-answer integrity: 18/20 on the local 7B model) and `--no-fresh` (the shipped multi-turn config, where a weak local model recites from history and gets flagged wholesale — every figure surfaced, never hidden). Full write-up with real numbers and committed run logs: [docs/GROUNDING-CHECK.md](docs/GROUNDING-CHECK.md). Reproduce: `python scripts/grounding_check.py [--no-fresh]`.
3. **Advice refusal**: "Should I buy TSLA?" → a compliant educational reframe using the portfolio's actual computed data. (Prompt-level behavior verified in the eval — not a hard code-level guarantee; the disclaimers are the backstop.)
4. Tool-call chips in the chat UI show exactly which computations backed each answer.

## Quick start

```bash
git clone https://github.com/CarlosM787/faro.git && cd faro
cp .env.example .env             # optional: add ANTHROPIC_API_KEY for Claude
docker compose up --build       # → http://localhost:3000  (seeded demo portfolio)
```

No key? Install [Ollama](https://ollama.com), run `ollama pull qwen2.5:7b`, and the copilot works locally for $0. Everything else is free by design: yfinance market data (on-disk cache; keeps working offline after the first successful load), SQLite, Docker.

> Docker + Ollama note: if chat can't reach the local model from inside Docker, make Ollama listen on all interfaces — set the `OLLAMA_HOST=0.0.0.0` environment variable before starting Ollama, then restart it.

### Development

```bash
cd api && pip install -e ".[dev]"
uvicorn faro_api.main:app --reload      # http://localhost:8000 (docs at /docs)
ruff check . && mypy && pytest          # 68 tests

cd web && npm install
npm run dev                             # http://localhost:5173 (proxies /api)
npm run check:i18n && npm run build     # en ⇄ es key parity is CI-enforced
```

## Bilingual by design

Every user-facing string ships in English **and** neutral Latin-American Spanish in the same commit (CI enforces locale key parity). The copilot and daily digest respond in the selected language. Currency/dates format per locale via `Intl`.

## Feature tour

- **Dashboard** — value/P&L, Sharpe·VaR·beta·drawdown cards with plain-language tooltips, performance vs SPY, allocation, drawdown chart, correlation heatmap, positions with per-position beta and risk share.
- **Copilot** — streaming chat, tool-call chips, per-portfolio history, suggested questions.
- **Scenarios** — compounding price shocks (per-ticker or market-wide), per-position impact; same engine as the agent's scenario tool.
- **Daily digest** — one-click Cortex-style brief: movers, risk contributors, upcoming earnings — narrated by the LLM from computed facts only, grounding-checked.
- **Installable web app** — a manifest lets you add Faro to any home screen or desktop straight from the browser (no offline service worker — the backend runs on your machine anyway); a deliberate platform choice over a native app.

## Deliberate boundaries

No trade execution. No brokerage linking. No personalized advice. No intraday data (daily bars are right for analytics). Educational disclaimers throughout, bilingual legal docs linked in-app.

## What I'd build next

Fama-French 3-factor exposure (regression is one `quant/` function away) · agent eval harness benchmarking grounding accuracy across models · options analytics (Black-Scholes + Greeks) · scheduled digest emails · multi-user auth.

## Status

| Milestone | State |
|---|---|
| Scaffold (api + web + Docker + CI) | ✅ |
| Data pipeline (yfinance + cache + seed) | ✅ |
| Quant engine (returns/vol/Sharpe/Sortino) | ✅ |
| Quant engine (beta/alpha/VaR/CVaR/drawdown/correlation) | ✅ |
| Portfolio CRUD + dashboard | ✅ |
| LLM provider layer + tool-use agent + chat | ✅ |
| Scenario engine + page | ✅ |
| Daily digest | ✅ |
| Grounding spot-check + ship polish | ✅ |

---

Built by an MSF graduate (University of Arizona) & Raytheon engineer · [faroquant.com](https://faroquant.com) · [github.com/CarlosM787/faro](https://github.com/CarlosM787/faro)
