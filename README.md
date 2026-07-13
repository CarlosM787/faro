<p align="center">
  <img src="brand/logo-wordmark.svg" alt="Faro — AI Portfolio Copilot" width="380">
</p>

# Faro — AI Portfolio Copilot

[![CI](https://github.com/CarlosM787/faro/actions/workflows/ci.yml/badge.svg)](https://github.com/CarlosM787/faro/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Site: faroquant.com](https://img.shields.io/badge/site-faroquant.com-2DD4BF)](https://faroquant.com)

**Faro is an open-source, self-hosted, bilingual (EN/ES) portfolio-analytics app: a deterministic quant engine computes institutional-grade risk metrics from first principles, and an AI copilot explains them — but the copilot can only get numbers by calling the engine's tools, and a grounding checker flags any figure in its answers that doesn't trace to a computation.** Educational tool, not an investment adviser.

### Links

| | |
|---|---|
| 🌐 **Live site** | **[faroquant.com](https://faroquant.com)** (GitHub Pages, HTTPS) |
| 💻 **Source** | **[github.com/CarlosM787/faro](https://github.com/CarlosM787/faro)** (MIT) |
| 🐳 **Run it locally** | `git clone` → `docker compose up --build` → **http://localhost:3000** (seeded demo portfolio, no API key required — [full steps ↓](#run-it-locally-docker)) |

**📚 Docs:** [Recruiter brief](docs/RECRUITER-BRIEF.md) · [Grounding eval (two-mode, with logs)](docs/GROUNDING-CHECK.md) · [Changelog / build diary](docs/CHANGELOG.md) · [Project handoff](docs/PROJECT-HANDOFF.md) · [Legal (EN/ES)](docs/legal/)

> ⚠️ **Educational tool, not an investment adviser.** Faro never executes trades, never links to brokerages, and is **instructed to refuse personalized investment advice, with educational-only disclaimers throughout** — a deliberate compliance boundary. Bilingual legal docs: [docs/legal/](docs/legal/).

---

## See it

![Faro dashboard — portfolio value, risk metric cards, performance vs SPY, allocation, drawdown chart, correlation heatmap](docs/screenshots/dashboard.png)

<p align="center"><em>The copilot answering in Spanish, citing benchmark returns straight from the <code>compare_to_benchmark</code> tool — every figure traceable to a computation:</em></p>

![Faro copilot answering in Spanish, grounded in tool output](docs/screenshots/copilot.png)

<p align="center"><em>…and the whole point, in one screenshot: when the model states a number it didn't compute this turn, the app says so — out loud, in the UI:</em></p>

![Faro flagging a number that could not be traced to a tool result](docs/screenshots/copilot-grounding-warning.png)

---

## Why this project exists

I'm a Master of Science in Finance graduate (University of Arizona) and an engineer at Raytheon, and I built Faro as a **work sample for fintech engineering roles**. The industry is racing to put LLM chatbots in front of financial data (Robinhood's Cortex being the flagship example), and the question that kept nagging me was: *what actually stops the model from making a number up?* For most products the honest answer is "a system prompt and hope." Faro is my attempt at a better answer — built in public, with the code and the eval as the deliverable.

**The repo itself is the portfolio piece.** Code quality, tests, architecture, and honest documentation are meant to matter as much as the features.

## The core engineering problem

The #1 failure mode of LLM finance apps is **hallucinated numbers** — a confident, fluent, professionally-worded figure that the model simply invented. Faro's answer is architectural, in three layers, and the order matters:

1. **A deterministic quant engine** computes every metric from its documented formula (pure `numpy`/`pandas`, unit-tested).
2. **An AI copilot that can only call tools** — its *sole* sanctioned source of numbers is a set of typed tools that dispatch into that engine.
3. **A grounding checker on every reply** extracts each number from the answer and verifies it traces to a tool result *from that turn*. Anything unsupported is **detected and surfaced** — rendered as a visible warning in the UI, not silently shipped.

> **Claim discipline (important):** Faro does **not** claim "the LLM cannot hallucinate" — no one can honestly promise that. The claim is narrower and testable: **unsupported numbers are detected and surfaced.** That claim is measured by a public eval (below), not assumed.

The dashboard and the copilot call the **same service layer** — one engine, two consumers — so the charts and the chat can never disagree.

## Architecture

```
web (React 18 + TS + Tailwind + Recharts, i18next EN/ES)
 │  REST + SSE (same-origin /api)
 ▼
api (FastAPI · Python 3.12 · mypy strict)
 ├── routers/     portfolios · metrics · series · scenarios · chat (SSE) · digest
 ├── agent/       provider-agnostic LLM layer ── Claude (primary) ⇄ Ollama (free fallback)
 │                tool schemas · EN/ES system prompts · grounding checker · loop
 ├── services/    ★ single computation path shared by REST and agent tools
 ├── quant/       ★ pure numpy/pandas · every formula documented · reference-tested
 ├── data/        yfinance → Stooq fallback · on-disk cache · offline degradation
 └── db/          SQLite + SQLAlchemy 2.0 (Decimal at the boundary)
```

**Request → number, end to end:** the React UI calls the FastAPI layer → a **service** runs the pure **quant** functions → the agent exposes those same services as **tools** → the LLM answers only from tool outputs → the **grounding checker** verifies every number in the reply before it reaches the user.

## Key features

- **Dashboard** — value & P/L, Sharpe · VaR · beta · max-drawdown cards with plain-language tooltips, performance vs SPY, allocation donut, drawdown chart, correlation heatmap, and a positions table with per-position beta and share of total risk.
- **Copilot** — streaming chat, **visible tool-call chips** showing which computations backed each answer, per-portfolio history, suggested questions, and an amber warning under any reply containing an unsupported number.
- **Scenario lab** — compounding price shocks (per-ticker or market-wide) with per-position impact; the same engine the agent's scenario tool uses.
- **Daily digest** — one-click brief (movers, risk contributors, upcoming earnings), narrated by the LLM from computed facts only, grounding-checked like the chat.
- **Fully bilingual (EN/ES)** — every user-facing string ships in English and neutral Latin-American Spanish in the same commit (CI-enforced locale key parity). The copilot and digest answer in the selected language; currency/dates format per locale via `Intl`.
- **Installable web app** — a web-app manifest lets you add Faro to a home screen or desktop from the browser. **There is no offline service worker** — the backend runs on your own machine anyway; this is a deliberate self-hosted choice, not a full offline PWA.

## Quant metrics — formulas, not black boxes

`quant/` is pure (arrays in, numbers out, no I/O) and implements every metric from its documented formula. Each has two layers of tests: **hand-computed references** on tiny fixtures (derivations in the test comments) and **cross-checks vs independent implementations** (`quantstats`/`scipy` — dev-dependencies only, never imported by the engine).

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

## LLM grounding & the public eval

The copilot has exactly five typed tools — `get_portfolio_summary`, `get_metric`, `get_position_detail`, `run_price_shock_scenario`, `compare_to_benchmark` — that dispatch into the same services the dashboard uses. Guardrails:

1. **System-prompt contract** — numbers only from tools; educational, never advice; cite the metric; answer in the user's language.
2. **Grounding checker** (`agent/guardrails.py`) — after every reply, numeric tokens are matched against this turn's tool outputs (handling percentages, sign flips, comma grouping, rounding). Violations are returned in the SSE `done` event and rendered as a **visible amber warning** under the message (and on digests).
3. **Advice refusal** — "Should I buy TSLA?" is met with an educational reframe built from the portfolio's actual computed data. **This is prompt-level behavior, exercised in the eval — not a hard code-level classifier;** the disclaimers are the backstop.

**The eval is public, honest, and runs in two modes** — full write-up and committed raw logs in **[docs/GROUNDING-CHECK.md](docs/GROUNDING-CHECK.md)** and [docs/eval-logs/](docs/eval-logs/). Model under test: `qwen2.5:7b` via Ollama — deliberately the *weakest* link, to stress the guardrail.

| Mode | What it measures | Local 7B result (committed logs) |
|---|---|---|
| **`--fresh`** (per-answer integrity) | each question is an independent turn, forcing a tool call | **18 / 20 answers fully clean** — the 2 that weren't contained 4 ungrounded figures total, each surfaced. Both advice traps refused; all Spanish answers clean. |
| **`--no-fresh`** (shipped multi-turn config) | the real chat experience with history on | **3 / 20 clean, 139 figures flagged.** Once history is present, the weak 7B model recites earlier numbers *without re-calling tools* — and the checker flags **every one** in the UI. |

**That gap is the most useful thing the eval found, and it's reported on purpose, not hidden.** A weak local model in multi-turn chat is *safe but noisy* — not one of those 139 numbers reaches the user unlabeled. On a frontier model like Claude (the primary provider), tool-calling discipline is far stronger, so the flags are expected to be far fewer — but **that Claude-vs-local comparison has not been run yet** (it needs a real key and is the documented next step), so no number is quoted for it here. The eval is the **per-provider regression harness** built to measure exactly this — run it against whatever provider you configure. The claim — *unsupported numbers are detected and surfaced* — holds in **both** modes, regardless of pass rate.

## Compliance boundary

A deliberate, stated-in-product line:

- **No trade execution.** **No brokerage linking.** **No personalized investment advice** (instructed to refuse; educational-only disclaimers throughout).
- **No intraday data** — daily bars are the right resolution for this kind of analytics.
- Bilingual legal docs (privacy, terms, investment disclaimer) live in [docs/legal/](docs/legal/) and are linked in-app and on the site.

## Tech stack

| Layer | Choices |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Recharts, i18next (EN/ES), SSE streaming |
| **API** | FastAPI, Python 3.12, Pydantic, `mypy --strict`, SSE for chat/digest |
| **Quant** | pure `numpy` / `pandas` (no black-box quant libs in the engine) |
| **Data** | `yfinance` → Stooq fallback provider, on-disk cache, graceful offline degradation |
| **DB** | SQLite + SQLAlchemy 2.0 (Decimal at the boundary) |
| **LLM** | provider-agnostic — Anthropic **Claude** (`claude-sonnet-5`) primary when `ANTHROPIC_API_KEY` is set; local **Ollama** (`qwen2.5:7b`) as the $0 keyless fallback; a scripted fake provider in tests/CI |
| **Infra** | Docker Compose, GitHub Actions CI, GitHub Pages (site) |

**LLM switching is env-only:** set `ANTHROPIC_API_KEY` for Claude, leave it unset for Ollama — zero code changes. Everything else in the stack is free by design.

## Run it locally (Docker)

```bash
git clone https://github.com/CarlosM787/faro.git && cd faro
cp .env.example .env             # optional: add ANTHROPIC_API_KEY to use Claude
docker compose up --build        # → http://localhost:3000  (API at :8000, docs at :8000/docs)
```

A seeded demo portfolio loads on first run. **No API key needed:** install [Ollama](https://ollama.com), run `ollama pull qwen2.5:7b`, and the copilot works locally for $0. Market data (yfinance) is cached on disk and **keeps working offline after the first successful load**; SQLite and Docker are free.

> **Docker + Ollama note:** if chat can't reach the local model from inside the container, make Ollama listen on all interfaces — set `OLLAMA_HOST=0.0.0.0` before starting Ollama, then restart it.

### Development

```bash
cd api && pip install -e ".[dev]"
uvicorn faro_api.main:app --reload      # http://localhost:8000 (OpenAPI docs at /docs)
ruff check . && mypy && pytest          # 68 tests

cd web && npm install
npm run dev                             # http://localhost:5173 (proxies /api)
npm run check:i18n && npm run build     # EN ⇄ ES key parity is CI-enforced
```

## Tests & quality gates

Every commit is held to the same gates CI enforces:

- **68 unit tests** (`pytest`) — quant metrics checked against hand-computed references *and* independent libraries; service/agent/grounding tests.
- **`mypy --strict`** clean across the API.
- **`ruff`** lint + format clean.
- **i18n parity** — EN/ES locale keys must match (`npm run check:i18n`); no hardcoded UI strings.
- **`npm run build`** clean.
- **GitHub Actions CI** green on every push; **Docker Compose** runs from a clean clone.
- **Grounding eval** (`scripts/grounding_check.py`) is a runnable regression harness, exits non-zero on any ungrounded number.

## Known limitations

Stated plainly, because honesty is part of the point:

- **Grounding is detection, not prevention.** The checker *surfaces* unsupported numbers; it does not stop the model from generating them. On a weak local 7B model in multi-turn chat, that means frequent (correct) warnings — *safe but noisy*. A frontier model produces far fewer.
- **Advice refusal is prompt-level**, exercised in the eval — not a hard code-level classifier.
- **Free daily-bar data only** (yfinance + Stooq fallback), so no intraday and occasional staleness; the UI flags when the backup provider is in use.
- **Single-user, local** — no auth or multi-tenant support (a deliberate scope choice for a self-hosted tool).
- **Installable web app, not a full offline PWA** — there is no service worker.
- The headline eval numbers are on the **local 7B model**; the Claude-vs-local comparison with a real key is a documented next step.

## What recruiters & hiring managers should evaluate

Built as a work sample — here's where to look and what each choice demonstrates:

| Look at | What it shows |
|---|---|
| [`api/src/faro_api/quant/`](https://github.com/CarlosM787/faro/tree/main/api/src/faro_api/quant) + [`api/tests/`](https://github.com/CarlosM787/faro/tree/main/api/tests) | Quant implemented from first principles and tested two independent ways — financial correctness, not library glue. |
| [`api/src/faro_api/agent/guardrails.py`](https://github.com/CarlosM787/faro/blob/main/api/src/faro_api/agent/guardrails.py) | The grounding checker — the mechanism that makes "detected and surfaced" a *testable* claim. |
| [`docs/GROUNDING-CHECK.md`](docs/GROUNDING-CHECK.md) + [`docs/eval-logs/`](docs/eval-logs/) | A public, two-mode eval with iteration history and raw logs — including the fabricated `$12,345.67` the checker caught. Honesty over a flattering demo. |
| `agent/` provider layer | Provider-agnostic design (Claude ⇄ Ollama) switched by one env var — pragmatic, cost-aware architecture. |
| Git history + CI | Small, well-messaged commits; green CI; Docker-from-clean-clone. Production discipline. |

**The tell:** the project reports its *unflattering* multi-turn number (3/20, 139 flags) alongside the flattering one, because the safety story is about what the user sees, not the score.

## Resume-ready bullets

- Built an open-source, self-hosted **AI portfolio-analytics app** (FastAPI · React/TS · Docker Compose) pairing a deterministic quant engine with an LLM copilot; **MIT-licensed, live at faroquant.com**, runs free with no API key.
- Implemented **8+ institutional risk metrics** (Sharpe, Sortino, beta, Jensen's alpha, historical & parametric VaR, CVaR, max drawdown, risk contributions) from first principles in pure `numpy`/`pandas`, incl. an **inverse-normal CDF hand-written** (Acklam) and validated against `scipy` to 1e-8; **68 unit tests**, `mypy --strict`, CI green.
- Engineered an **LLM grounding checker** that verifies every number in each answer against the quant engine's tool outputs and **surfaces unsupported figures as in-app warnings**; published a **two-mode bilingual eval** (18/20 answers clean in per-answer mode on a local 7B model) with committed run logs.
- Designed a **provider-agnostic LLM layer** (Anthropic Claude primary, local Ollama fallback) switchable by a single environment variable with **zero code changes**.
- Shipped a **fully bilingual (EN/ES)** UI + copilot with **CI-enforced locale parity**, and a live GitHub Pages landing site over HTTPS; enforced a compliance boundary (no trade execution, no brokerage linking, no personalized advice).

## What I'd build next

Fama-French 3-factor exposure (regression is one `quant/` function away) · a Claude-vs-local grounding benchmark with a real key · options analytics (Black-Scholes + Greeks) · scheduled digest emails · multi-user auth.

---

Built by an MSF graduate (University of Arizona) & Raytheon engineer · [faroquant.com](https://faroquant.com) · [github.com/CarlosM787/faro](https://github.com/CarlosM787/faro)
