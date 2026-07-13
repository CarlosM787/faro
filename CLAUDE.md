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
- **Grounding discipline**: the agent's only numeric source is tool calls into the quant engine; a grounding checker verifies every number in each reply against current-turn tool outputs and flags unsupported figures. Claim it accurately: "unsupported numbers are detected and surfaced," never "the model can never invent numbers." Guardrails per TECH-NOTES (advice refusal, grounding check, disclaimer).
- **No trade execution, no brokerage linking, no personalized investment advice** — deliberate compliance boundary, stated in the app and README.
- **Production discipline**: typed (mypy clean), ruff-formatted, pytest + CI green at every commit, Docker Compose runs from clean clone.
- **LLM strategy**: provider-agnostic layer. **Anthropic API (Claude) is primary** when `ANTHROPIC_API_KEY` is set; **Ollama is the $0 fallback** used for tests/CI and keyless replication. Switching = env only, zero code changes. Everything else in the stack stays free (yfinance, SQLite, Docker).
- **Secrets via env only**; app works fully without any key.
- Free data only (yfinance + cache + fallback provider interface); handle staleness gracefully.

## Workflow

- Small, working, well-messaged commits (hiring managers read history).
- After each milestone: run the TECH-NOTES verification checklist (clean-clone Docker run, tests, agent-vs-dashboard number match, advice refusal, offline cache).
- Keep the README current as features land — it's part of every milestone, not an afterthought.

## Status

- [x] Research + planning (2026-07-07)
- [x] Scaffold: repo, FastAPI + React + Docker Compose + CI skeleton (2026-07-08)
- [x] Data pipeline: yfinance provider + cache + seed demo portfolio (2026-07-08)
- [x] Quant engine: returns/vol/Sharpe/Sortino (+ tests) (2026-07-08)
- [x] Quant engine: beta/alpha, VaR/CVaR, max drawdown, correlations, concentration (+ tests) (2026-07-08)
- [x] Portfolio CRUD + dashboard (value, allocation, metric cards, charts) (2026-07-08)
- [x] LLM provider layer (Anthropic primary, Ollama fallback) + tool-use agent + chat UI (streaming, guardrails) (2026-07-08)
- [x] Scenario engine + page (price shocks; shared with agent tools) (2026-07-08)
- [x] Daily digest generation (2026-07-08)
- [x] Recruiter-grade README + grounding spot-check (28→4→2 across iterations; docs/GROUNDING-CHECK.md) (2026-07-08)
- [x] Docker acceptance test, GitHub push (CI green), faroquant.com DNS + Pages deploy + HTTPS enforced, installable web app (manifest), landing-page redesign + mobile verification (2026-07-08)
- [x] Honesty hardening: grounding warnings surfaced in the UI (chat + digest), honest two-mode eval (fresh 18/20 · no-fresh 3/20 / 139 flagged, committed logs), chat-crash fix, claim-integrity sweep (2026-07-12)
- [x] Recruiter website pass: real screenshots, "for hiring managers" section, two-mode honesty stat (EN/ES) (2026-07-12)
- [x] Recruiter documentation: recruiter-grade README + docs/PROJECT-HANDOFF + docs/RECRUITER-BRIEF + docs/CHANGELOG; Substack claim-aligned (2026-07-13)
- [x] Product/brand professionalization: app SVG icon set (no emoji chrome), responsive mobile nav, skeleton/empty/error states, scenario presets, settings provider+about, positive grounding note; website 139/139 claim precision + bilingual architecture section + og:image social card (2026-07-13)
- [x] Language picker: EN/ES pill → accessible dropdown; app extended to 5 UI languages (EN/ES maintained pair + PT/FR/DE) sharing one CI-checked key set; copilot prompt made language-generic; Intl locale-aware number/date formatting; `languages.ts` source of truth (2026-07-13). Website stays EN/ES.
- [ ] User steps remaining: review + push the local commits; add ANTHROPIC_API_KEY to .env then re-run the grounding eval on Claude and record it in docs/GROUNDING-CHECK.md; publish Substack article (docs/SUBSTACK-ARTICLE.md); optional: re-capture app screenshots (they predate the icon pass), demo GIF
