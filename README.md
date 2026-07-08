<p align="center">
  <img src="brand/logo-wordmark.svg" alt="Faro — AI Portfolio Copilot" width="380">
</p>

# Faro — AI Portfolio Copilot

**Institutional-grade portfolio analytics computed from first principles, explained by an AI copilot that can't make numbers up.** Fully bilingual (English / Español). Self-hosted, free to run.

> ⚠️ Faro is an **educational tool, not an investment adviser**. It never executes trades, never links to brokerages, and refuses to give personalized investment advice — a deliberate compliance boundary. See [docs/legal/](docs/legal/).

## Why this exists

The #1 failure mode of LLM finance apps is hallucinated numbers. Faro demonstrates the architecture that fixes it: **a deterministic, unit-tested quant engine underneath; an LLM agent on top whose *only* source of numbers is calling that engine's tools.** Every figure in every answer traces to a computation.

## Architecture

```
web (React + TS + Tailwind)  ──►  api (FastAPI, Python 3.12)
                                   ├── routers/    REST + SSE chat
                                   ├── agent/      LLM tool-use loop · guardrails · EN/ES prompts
                                   │                 Claude (primary) ⇄ Ollama (free fallback) — env-only switch
                                   ├── quant/      ★ pure numpy/pandas · formulas documented · reference-tested
                                   ├── data/       yfinance + parquet cache (+ fallback provider)
                                   └── db/         SQLite + SQLAlchemy
```

## Quick start

```bash
git clone <repo-url> faro && cd faro
cp .env.example .env          # optional: add ANTHROPIC_API_KEY for Claude
docker compose up --build     # app → http://localhost:3000
```

No key? The copilot runs on a local model via [Ollama](https://ollama.com) (`ollama pull qwen2.5:7b`). Everything else — market data (yfinance), SQLite, Docker — is free.

## Status

| Milestone | State |
|---|---|
| Scaffold (api + web + Docker + CI) | ✅ |
| Data pipeline (yfinance + cache + seed) | ✅ |
| Quant engine (returns/vol/Sharpe/Sortino) | ✅ |
| Quant engine (beta/alpha/VaR/CVaR/drawdown/correlation) | ✅ |
| Portfolio CRUD + dashboard | ⬜ |
| LLM provider layer + tool-use agent + chat | ⬜ |
| Scenario engine + page | ⬜ |
| Daily digest | ⬜ |
| Recruiter-grade README + demo | ⬜ |

## Development

```bash
# API
cd api && pip install -e ".[dev]"
uvicorn faro_api.main:app --reload       # http://localhost:8000
ruff check . && mypy && pytest

# Web
cd web && npm install
npm run dev                              # http://localhost:5173 (proxies /api → :8000)
npm run check:i18n                       # en ⇄ es key parity
```

## Bilingual by design

Every user-facing string ships in English **and** neutral Latin-American Spanish in the same commit (CI enforces key parity). The copilot answers in your selected language.

---

Built by an MSF graduate (University of Arizona) & Raytheon engineer. · [faroquant.com](https://faroquant.com)
