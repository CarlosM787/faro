# Changelog & build diary

The real build story of Faro, newest first. This is both a changelog and a "built-in-public" diary — it records what shipped, and the engineering decisions and course-corrections behind each milestone. Dates are commit dates; see `git log` for the full history.

Format loosely follows [Keep a Changelog](https://keepachangelog.com). Faro is pre-1.0; the app was built to a working MVP in a single intense day (2026-07-08), then hardened for honesty and recruiter-readiness.

---

## 2026-07-13 — Language picker (5 UI languages)

Turned the two-button EN/ES pill into a proper language dropdown and extended the app past the mandated pair.

- **Dropdown picker** — a new accessible `LanguageMenu` (button + popover, keyboard/Escape/outside-click, `aria` listbox) replaces `LangToggle`, in the sidebar, mobile top bar, and Settings. Choice persists (localStorage) and flows to the copilot/digest.
- **Five UI languages** — English and Spanish stay the hand-written, maintained pair; **Portuguese (pt-BR), French, and German** were added, sharing the exact same key set. A single `languages.ts` is the source of truth (code · endonym · Intl locale).
- **Copilot answers in any of the five** — `system_prompt()` was made language-generic: EN/ES keep their hand-tuned prompts, the others get an "always answer in <language>" instruction over the same guardrail contract, so a non-EN/ES user no longer silently gets English. Locked in with `test_prompts.py` (11 tests).
- **Formatting follows the language** — numbers, currency, and dates now format via each language's Intl locale (e.g. `US$ 30.660,08`, `13/07/2026` in pt-BR); the hardcoded `es-MX`/`en-US` branches are gone.
- **CI parity scales** — `check-i18n.mjs` now auto-discovers every locale folder and checks each against English (both missing *and* extra keys), instead of hardcoding en⇄es.
- Note: the marketing site (`website/`) remains EN/ES; this pass is the app.

## 2026-07-13 — Product & brand professionalization pass

A design pass to make the shipped app and site feel like a real fintech product, benchmarked against the visual discipline of credible dev-tool/fintech products (restrained accent color, consistent stroke iconography, skeleton loading, no emoji chrome).

- **App: real iconography** — replaced all emoji UI chrome (nav 📊💬⚡📰⚙️, chips, links) with a small in-repo SVG stroke-icon set (`web/src/components/icons.tsx`, no icon-library dependency).
- **App: mobile layout** — the fixed desktop sidebar now collapses to a sticky top bar with horizontal nav below `lg`; verified no horizontal overflow at 375px.
- **App: state design** — skeleton loading that mirrors the dashboard layout, a styled error state with retry, real empty states (dashboard CTA to add a first position; digest explains what it generates).
- **App: grounding UX both ways** — the amber warning now has an icon treatment, and clean replies get the positive counterpart: a small "all figures traced to tool results" note when the checker found nothing to flag (live turns only — restored history is never re-claimed).
- **App: scenario presets** — one-click market-wide Correction −10% / Bear market −20% / Severe crash −35%, running the same engine.
- **App: settings grew up** — shows the active AI provider (from `/api/health`), an About section with links and the app version, and external-link icons on legal docs.
- **Website: claim precision** — the "100%" eval stat became the exact **139/139** (every *flagged* figure surfaced in-app), which is what the logs support; EN/ES labels updated to match.
- **Website: architecture section** — a bilingual "one engine, two consumers" diagram (dashboard + copilot → shared FastAPI services → quant engine + market data, grounding checker called out).
- **Website: social meta** — og:image/twitter-card wired to a new `img/og.png` composed from the real dashboard screenshot; mobile nav now collapses section links.
- All new UI copy shipped EN + ES in the same change; i18n parity and web build green.

## 2026-07-13 — Recruiter documentation pass

The docs became the deliverable.

- **README rewritten recruiter-grade** into a 16-section structure: one-line summary, live links, screenshots up top, why-it-exists, the hallucination problem, architecture, quant table, honest two-mode eval, compliance boundary, tech stack, Docker run, quality gates, known limitations, "what recruiters should evaluate", and resume bullets.
- **New [PROJECT-HANDOFF.md](PROJECT-HANDOFF.md)** — canonical source of truth for future AI/human sessions (status, URLs, invariants, verified-vs-not, what-not-to-break, roadmap, continuation prompts).
- **New [RECRUITER-BRIEF.md](RECRUITER-BRIEF.md)** — a 1–2 page explainer for job applications and interviews.
- **New CHANGELOG** (this file).
- **Claim alignment** across README, brief, and the Substack draft: the Claude-vs-local grounding gap is framed as *expected + a documented next step* (no unmeasured number quoted); advice refusal is stated as prompt-level. Eval numbers locked to the committed logs.

## 2026-07-12 — Honesty hardening + recruiter-facing website

The most important round: the QA process forced two genuine bugs into the open, and the "honest number" turned out to be a better story than the flattering one.

- **Grounding warnings now surface in the UI**, not just server logs — an amber warning renders under any chat message (and digest) containing a figure that couldn't be traced to a tool result. This closed the gap between "we detect it" and "the user sees it."
- **Two-mode eval, reported honestly.** Running the eval in the *shipped* multi-turn configuration (`--no-fresh`, conversation history on) exposed that the weak local 7B model recites earlier numbers without re-calling tools: **3/20 clean, 139 figures flagged**, versus **18/20** in per-answer (`--fresh`) mode. Both modes are committed with raw logs. The point isn't the score — it's that not one of those 139 numbers reaches the user unlabeled.
- **Fixed a real shipped crash.** The chat page blanked on modern Chrome: a concise-body `useEffect(() => endRef.current?.scrollIntoView({behavior:"smooth"}), [turns])` returned the Promise from `scrollIntoView`, which React then tried to invoke as an effect-cleanup function. Never caught earlier because `/chat` had only been exercised via curl, never a browser. Fixed with a block-body effect.
- **Claim integrity sweep** — removed the "20/20" landing-page stat (pivoted to "detection, not hope"), corrected the PWA/offline wording to "installable web app," and softened advice-refusal language to prompt-level.
- **Website upgraded for recruiters** — real dashboard + grounding-warning screenshots, a "for hiring managers" section with repo deep-links, and a two-mode honesty callout — all bilingual EN/ES.

## 2026-07-08 — MVP built and shipped (one day)

From empty repo to a live, Dockerized, bilingual app with a grounded AI copilot.

### Added
- **Scaffold** — FastAPI app factory + env-driven config + health endpoint; bilingual React shell (brand tokens, i18next, EN/ES toggle); Docker Compose, GitHub Actions CI, env template.
- **Data pipeline** — provider chain (`yfinance` → Stooq fallback), parquet on-disk cache, SQLAlchemy models, seeded demo portfolio; graceful offline degradation after first load.
- **Quant engine, from first principles** — returns/volatility/Sharpe/Sortino, then the full risk suite: historical & parametric VaR, CVaR, max drawdown, beta/Jensen's alpha, correlation, concentration (HHI), Euler risk contributions. Pure `numpy`/`pandas`, every formula documented, unit-tested against hand-computed references *and* independent libraries. The inverse-normal CDF was hand-written (Acklam) and validated against `scipy` to 1e-8.
- **Portfolio CRUD + bilingual dashboard** — metric cards with plain-language tooltips, performance vs SPY, allocation, drawdown chart, correlation heatmap, positions with per-position beta and risk share.
- **Provider-agnostic AI copilot** — Claude primary / Ollama keyless fallback (env-switched); five typed tools dispatching into the shared service layer; streaming SSE chat with visible tool-call chips.
- **Scenario lab** — compounding price shocks (per-ticker or market-wide) with per-position impact.
- **Daily digest** — one-click brief (movers, risk contributors, upcoming earnings), narrated from computed facts and grounding-checked.
- **Landing page + deploy** — recruiter-grade bilingual landing page, deployed to GitHub Pages at faroquant.com; MIT LICENSE; HTTPS enforced.

### Grounding eval — how the checker earned trust (fresh mode)
- **Run 1: 28 ungrounded numbers.** Caught the model answering from chat history without re-computing; a fabricated **`$12,345.67`** "profit" with zero tool calls (committed in [eval-logs/run1-fresh.txt](eval-logs/run1-fresh.txt), Q10: `tools=0 | violations=[12345.67]`); and false-positives of my own (checker flagged "S&P 500" as `500`). Fixes: prompt hardening, independent-turn (`--fresh`) evaluation, trivial-token list.
- **Run 2: 4.** Taught the matcher about sign-flipped percentages; discovered the model *derived* the benchmark return from α and β because the tool didn't return it — so I fixed the **tool**, not the prompt.
- **Runs 3–4 (Dockerized): 18/20 clean.** Residuals were the 7B model doing freelance arithmetic (e.g. "≈85% diversified" off HHI) — flagged, exactly as designed.

## 2026-07-07 — Planning & brand

- Research and product definition (PRD, tech notes, career rationale); brand identity (palette, fonts, logos); bilingual legal docs (privacy, terms, investment disclaimer) in EN/ES. Two earlier product concepts (a budgeting capstone and a bilingual invoicing app) were researched and deliberately **not** built — the pivot to a "mini-Cortex" is the sharper fintech-hiring story.

---

*Faro is an educational analytics tool, not an investment adviser. Nothing it produces is investment advice.*
