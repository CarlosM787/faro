# Kickoff prompt — paste into a fresh Claude Code session (Opus or any strong model) in this folder

## One-time setup first (you, not the model)

- [ ] **Docker Desktop** installed and running (docker.com)
- [ ] **Anthropic API key** (console.anthropic.com) saved for later — you'll put it in `.env` when the scaffold exists
- [ ] **Ollama** installed (ollama.com), then run once: `ollama pull qwen2.5:7b` (free fallback model for tests/CI)
- [ ] **Git** installed; a **GitHub account** (free)
- [ ] Register **faroquant.com** at Porkbun (~$11/yr; verified available 2026-07-07)

## The prompt — copy everything between the lines

---

Read CLAUDE.md, docs/PRD.md, docs/TECH-NOTES.md, docs/RESEARCH.md, and brand/BRAND.md carefully. They define Faro: an open-source, bilingual (EN/ES) AI portfolio copilot — a hiring-portfolio project where the repo itself (code quality, tests, CI, README) is the deliverable. The brand assets (brand/), a bilingual landing page (website/index.html), and bilingual legal documents (docs/legal/) already exist — build the app to match them.

First, in plan mode, produce a complete production plan before writing any code:

1. **Architecture & repo layout** — monorepo per TECH-NOTES (FastAPI api/ with routers, agent/, quant/, data/, db/; React+TS+Tailwind web/), Docker Compose services, GitHub Actions CI. The LLM provider layer: Anthropic (claude-sonnet-5) primary when ANTHROPIC_API_KEY is set, Ollama automatic keyless fallback for tests/CI/replication — switching is env-only, zero code changes.
2. **Bilingual design** — every user-facing string through i18next with en + es in the same commit; one-tap persisted language toggle; the copilot answers in the user's selected language; Spanish is neutral Latin American. Use the brand palette and fonts from brand/BRAND.md (navy #0B1220 background, beam #FFB020 accent, teal #2DD4BF data accent, Space Grotesk + Inter) so app and website look like one product. Describe every screen's layout (dashboard, portfolio editor, copilot chat, scenarios, digest, settings) before building.
3. **Data contracts** — SQLAlchemy models, API endpoints with request/response schemas, and the agent tool schemas (get_portfolio_summary, get_metric, get_position_detail, run_price_shock_scenario, compare_to_benchmark).
4. **Quant test plan** — for every metric in the PRD (returns, vol, Sharpe, Sortino, alpha/beta, historical & parametric VaR, CVaR, max drawdown, correlations, concentration): the formula, its reference source, and how the unit test verifies it (hand-computed small fixture + cross-check vs quantstats/scipy on a larger one).
5. **Milestone sequence** — order CLAUDE.md's Status checklist into milestones where the app is runnable and demoable after every single one; each milestone ends with tests green, mypy/ruff clean, CI green, README updated, CLAUDE.md Status checkbox ticked, and small well-messaged commits.
6. **Risk list** — the 5 most likely failure points (yfinance rate limits, Ollama tool-calling quirks, Docker-to-host-Ollama networking, i18n string drift, chart performance) with mitigations.
7. **Definition of done** — restate the PRD success criteria as a final acceptance checklist, including: the 20-question agent grounding spot-check (zero hallucinated numbers), the advice-refusal test ("should I buy TSLA?" → compliant educational reframe), the full EN⇄ES toggle sweep (no untranslated strings), and the clean-clone docker-compose-up-in-under-5-minutes test.

After I approve the plan, implement it milestone by milestone WITHOUT stopping between milestones unless you hit a decision only I can make or a real blocker: git init first, then the scaffold, then straight down the sequence. At the end of each milestone run the TECH-NOTES verification checklist, update CLAUDE.md's Status and the README, and commit. The committed code + Status list + README must always let a fresh session resume exactly where you stopped if my usage runs out.

Constraints to never violate: quant/ stays pure numpy/pandas with documented formulas and reference-value tests; the agent gets numbers ONLY from tool calls; every UI string bilingual EN/ES in the same commit; Claude primary / Ollama fallback via env only; no trade execution, no brokerage linking, no personalized financial advice; all secrets via env, never committed; link the docs/legal/ PDFs in the app's settings/footer.

---

## After the build (your part)

- Push to public GitHub; confirm the CI badge is green.
- Deploy website/ to GitHub Pages or point faroquant.com at it.
- Record a 30–60s GIF of the copilot answering a risk question in both languages; top of README.
- Résumé line: "Faro — open-source bilingual AI portfolio copilot: first-principles quant engine + tool-grounded LLM agent (Python/FastAPI/React/Claude)."
- Publish docs/SUBSTACK-ARTICLE.md as post #1.
