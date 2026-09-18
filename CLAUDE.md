# Faro — AI Portfolio Copilot · hiring portfolio project ("mini-Cortex")

**Brand:** Faro / faroquant (see [brand/BRAND.md](brand/BRAND.md) — palette, fonts, logos in brand/). Domain faroquant.com verified available 2026-07-07 (register manually). Landing page draft: [website/index.html](website/index.html). Launch article draft: [docs/SUBSTACK-ARTICLE.md](docs/SUBSTACK-ARTICLE.md). Use the brand palette/fonts for the app UI.

Self-hosted AI portfolio analytics: FastAPI quant engine (metrics from first principles), React dashboard, and a Claude agent that answers portfolio questions **only** by calling the quant engine's tools. Built to showcase the owner (engineer, M.S. Finance) to fintech employers like Robinhood — **the repo is the deliverable**: code quality, tests, README, and architecture matter as much as features.

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
- [x] ~~User steps remaining: review + push the local commits~~ — **superseded 2026-09-17: all local commits are pushed; `main` and `origin/main` are level.**
- [x] Dependency-drift repair (2026-09-17): `anthropic` 1.x removed `temperature` from the Messages parameter surface, and the unbounded `anthropic>=0.40` let a fresh install pick it up — this had been **failing CI on `main` since 2026-09-15** (red badge on the public README) and would have broken the *first* real Claude call. Stopped forwarding `temperature` on the Anthropic path (Ollama still honours it), pinned `anthropic>=1.0,<2`, and added `tests/unit/agent/test_anthropic_provider.py` — a no-network contract test that binds the provider's actual kwargs against the installed SDK signature, so the next SDK break fails loudly in CI instead of quietly inside the provider's `except Exception` boundary. Gates: ruff + `ruff format --check` + `mypy --strict` clean, **85 tests pass**. Stale `68`/`70+ across 18 files` counts corrected to **85 across 17 files** in README, KICKOFF-PROMPT, PROJECT-HANDOFF, RECRUITER-BRIEF, and website (EN+ES).
- [x] V1 proven end to end, keyless (2026-09-17, session 2): with `ANTHROPIC_API_KEY` absent the whole product runs on local Ollama for $0 — deterministic metrics, tool-grounded copilot, EN **and** ES, advice refusal, and the grounding checker. Added `api/scripts/demo_v1.py` (one command, five questions, ends by printing what the product does *not* mean) and [docs/DEMO.md](docs/DEMO.md), which records a real transcript rather than hand-written output. The checker was observed catching a live error: the model wrote "$12,271.37 (5.83% of total value)" when the tool returned `pnl_pct` 0.5832 — a factor of ten out — and flagged `5.83`.
- [x] Provider errors made actionable (2026-09-17, session 2): `agent/errors.py` turns a provider failure into one bounded line — what failed, which model, the provider's own message, then the action — with key-shaped values redacted before they leave the process. Auth points at both the key and the free local alternative; a moved SDK surface is named as a dependency problem (the session-1 `temperature` failure mode); a dead Ollama gets `ollama serve` + the exact `ollama pull`. **No fallback-on-error:** the provider is chosen once and a failure is reported against the provider that actually failed, because answering from a 7B model while the user believes Claude answered would change what the answer means. Verified live against a dead Ollama port. Test counts now **97 across 18 files**.
- [ ] **User steps remaining (blocked on Carlos):** add `ANTHROPIC_API_KEY` to `.env`, then run the grounding eval on Claude and record it in docs/GROUNDING-CHECK.md — this is the one claim in the README still measured only on the local 7B model, and the Claude path is now verified callable. Then: publish Substack article (docs/SUBSTACK-ARTICLE.md); optional: re-capture app screenshots (they predate the icon pass), demo GIF.
