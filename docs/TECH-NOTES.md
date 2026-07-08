# Tech Notes — AI Portfolio Copilot

Defaults for the implementing session. Push back in the plan if something better fits, but remember: **the repo itself is the deliverable** — hiring managers will read the code.

## Stack

- **Backend: Python 3.12 + FastAPI** — Python is the quant lingua franca; a finance employer expects the quant work in Python. Fully typed (mypy/pyright-clean), `ruff` formatted.
- **Quant: numpy + pandas only** for the metric implementations — *no* quant black-box libraries (empyrical, quantstats) in the core engine; the whole point is implementing formulas from first principles. Fine to use quantstats **in tests** as an independent cross-check.
- **Data: yfinance** primary (no API key), on-disk parquet/SQLite cache, provider interface so a fallback (Stooq/Alpha Vantage) can slot in.
- **DB: SQLite** via SQLAlchemy — zero-ops, fine for single-user demo.
- **AI: provider-agnostic LLM layer with tool use** — a thin `LLMProvider` interface with two implementations:
  - **Anthropic (primary/production)** — used when `ANTHROPIC_API_KEY` is set; default model `claude-sonnet-5`, configurable via env. This is the intended real-use path.
  - **Ollama (dev/test fallback, $0)** — local models (e.g. `qwen2.5:7b`, tool-calling capable) via the Ollama HTTP API. Used automatically when no key is set, and in automated tests/CI so the suite never needs a paid key. Keeps the clone-and-run path free for anyone replicating the repo.
  Stream responses in both. System prompt (shared) enforces: numbers only from tools, educational-not-advice boundary, cite which metrics were used. The provider abstraction is itself a résumé point — design it cleanly; switching providers must be env-only, zero code changes.
- **Frontend: React + TypeScript + Vite + Tailwind**, charts via **Recharts** (light, clean). Desktop-first (this is an analyst tool, not a phone app), responsive enough to demo on mobile.
- **Infra: Docker Compose** (api + web), **GitHub Actions CI** (ruff + mypy + pytest + frontend build), deployable to Render/Fly free tier for the live demo link.
- **Secrets**: `ANTHROPIC_API_KEY` via env/.env (gitignored), strictly optional. Never in code.
- **Cost rule**: the only paid dependency is the Anthropic API (owner's choice for production chat). Everything else stays $0 — free data (yfinance), SQLite, Docker, and Ollama as the keyless fallback so tests/CI and public replication never require a paid key. Cap Claude spend: cache aggressively, max-token limits, and default to `claude-haiku-4-5-20251001` for dev if cost matters.

## Architecture (keep this layering strict — it's the interview diagram)

```
web (React) ──► api (FastAPI)
                 ├── routers/        REST: portfolios, positions, metrics, digest, chat (SSE)
                 ├── agent/          Claude tool-use loop, tool schemas, system prompt, guardrails
                 ├── quant/          ★ pure functions, no I/O: metrics from documented formulas
                 ├── data/           providers (yfinance, fallback), cache, models
                 └── db/             SQLAlchemy models + repo layer
```

- `quant/` is **pure** (arrays in, numbers out, no network/DB) — trivially testable, excerptable in interviews.
- The agent's tools and the dashboard/scenario UI call the **same** service layer — one engine, two consumers.
- Every `quant/` function: docstring with the formula (LaTeX-ish), parameters, assumptions (e.g., 252 trading days, sample vs population std), and a reference for the test value.

## Quant correctness rules

- Log vs simple returns: be explicit everywhere; annualize with √252 for vol, 252 for returns.
- VaR: implement **both** historical and parametric; document the normality assumption caveat on parametric.
- Sharpe: excess returns over configurable risk-free rate (default: 3-month T-bill constant in config, documented).
- Tests: each metric vs. hand-computed values on a tiny fixed dataset **and** cross-checked vs. quantstats/scipy on a larger one. Tolerance-based asserts.
- Money/quantities: `Decimal` at the persistence boundary, float64 inside vectorized math (standard practice — document it).

## Agent guardrails (showcase these — they're hiring signal)

1. System prompt: educational tool; no personalized advice; must call tools for any number; if a question needs data it doesn't have, say so.
2. Tool results are the only numeric source — a post-response check (regex numbers in reply vs. numbers returned by tools) logs grounding violations; surface the log in dev mode.
3. Refusal path for advice-seeking gets a helpful reframe ("here's how to evaluate that yourself — your NVDA position is X% of the portfolio with beta Y…").
4. Rate-limit + max-tokens caps so the demo can't be abused.

## Verification checklist per milestone

1. `docker compose up` from clean clone → app with seed portfolio in <5 min.
2. `pytest` green, CI green, mypy clean.
3. Ask the copilot three metric questions → every number matches the dashboard.
4. Ask "should I buy TSLA?" → compliant educational refusal.
5. Kill the network → dashboard still renders from cached data.
