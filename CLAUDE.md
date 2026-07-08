# Faro — AI Portfolio Copilot · hiring portfolio project ("mini-Cortex")

**Brand:** Faro / faroquant (see [brand/BRAND.md](brand/BRAND.md) — palette, fonts, logos in brand/). Domain faroquant.com verified available 2026-07-07 (register manually). Landing page draft: [website/index.html](website/index.html). Launch article draft: [docs/SUBSTACK-ARTICLE.md](docs/SUBSTACK-ARTICLE.md). Use the brand palette/fonts for the app UI.

Self-hosted AI portfolio analytics: FastAPI quant engine (metrics from first principles), React dashboard, and a Claude agent that answers portfolio questions **only** by calling the quant engine's tools. Built to showcase the owner (MSF graduate + Raytheon engineer) to fintech employers like Robinhood — **the repo is the deliverable**: code quality, tests, README, and architecture matter as much as features.

## Read these before doing anything

1. [docs/PRD.md](docs/PRD.md) — MVP scope, success criteria, non-goals
2. [docs/TECH-NOTES.md](docs/TECH-NOTES.md) — stack, architecture layering, quant-correctness and guardrail rules
3. [docs/RESEARCH.md](docs/RESEARCH.md) — career rationale (what hiring managers must see)
4. [docs/KICKOFF-PROMPT.md](docs/KICKOFF-PROMPT.md) — intended first task

(Two earlier product plans — a budgeting capstone and a bilingual invoicing app — are archived in docs/archive/. Do not build them.)

## Hard rules

- **Fully bilingual EN/ES**: every user-facing string in the app goes through i18next with en + es in the same commit; clean one-tap language toggle in the UI (persisted; default from browser locale). The copilot answers in the user's selected language. Spanish = neutral Latin American. The website (website/index.html) already implements this pattern — match it. Legal docs (privacy, terms, disclaimer) exist bilingually in docs/legal/ (Word + PDF); link them in the app footer/settings.

- **`quant/` is pure and first-principles**: numpy/pandas only, no I/O, every function documented with its formula and unit-tested against independently computed reference values. No quant black-box libs in the engine (cross-checking in tests is fine).
- **The agent never invents numbers**: all figures come from tool calls into the quant engine. Guardrails per TECH-NOTES (advice refusal, grounding check, disclaimer).
- **No trade execution, no brokerage linking, no personalized investment advice** — deliberate compliance boundary, stated in the app and README.
- **Production discipline**: typed (mypy clean), ruff-formatted, pytest + CI green at every commit, Docker Compose runs from clean clone.
- **LLM strategy**: provider-agnostic layer. **Anthropic API (Claude) is primary** when `ANTHROPIC_API_KEY` is set; **Ollama is the $0 fallback** used for tests/CI and keyless replication. Switching = env only, zero code changes. Everything else in the stack stays free (yfinance, SQLite, Docker).
- **Secrets via env only**; app works fully without any key.
- Free data only (yfinance + cache + fallback provider interface); handle staleness gracefully.

## Workflow

- Not yet a git repo — `git init` first; small, working, well-messaged commits (hiring managers read history).
- After each milestone: run the TECH-NOTES verification checklist (clean-clone Docker run, tests, agent-vs-dashboard number match, advice refusal, offline cache).
- Keep the README current as features land — it's part of every milestone, not an afterthought.

## Status

- [x] Research + planning (2026-07-07)
- [x] Scaffold: repo, FastAPI + React + Docker Compose + CI skeleton (2026-07-08)
- [x] Data pipeline: yfinance provider + cache + seed demo portfolio (2026-07-08)
- [x] Quant engine: returns/vol/Sharpe/Sortino (+ tests) (2026-07-08)
- [ ] Quant engine: beta/alpha, VaR/CVaR, max drawdown, correlations, concentration (+ tests)
- [ ] Portfolio CRUD + dashboard (value, allocation, metric cards, charts)
- [ ] LLM provider layer (Ollama default, Anthropic optional) + tool-use agent + chat UI (streaming, guardrails)
- [ ] Scenario engine + page (price shocks; shared with agent tools)
- [ ] Daily digest generation
- [ ] Recruiter-grade README + live demo deployment
