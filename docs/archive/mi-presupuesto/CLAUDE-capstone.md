# Mi Presupuesto — bilingual (EN/ES) budget tracker · MSF capstone project

Simple, free, offline-first envelope-budgeting PWA for English/Spanish households: cash income, irregular income, remittance tracking. No bank sync, no accounts, no backend in MVP.

**Context:** this is the owner's Master of Science in Finance capstone — a working app plus a written thesis. Academic credibility matters as much as polish; the thesis-support features in ACADEMIC.md are in scope. Monetization is NOT a goal (a commercial pivot, "Cobra", is archived in docs/archive/cobra/ and may be referenced in the paper's future-work section — do not build it).

## Read these before doing anything

1. [docs/PRD.md](docs/PRD.md) — MVP scope and non-goals
2. [docs/ACADEMIC.md](docs/ACADEMIC.md) — feature→finance-concept map and the 4 thesis-support features (in scope)
3. [docs/TECH-NOTES.md](docs/TECH-NOTES.md) — stack, i18n rules, data model
4. [docs/RESEARCH.md](docs/RESEARCH.md) — market evidence
5. [docs/KICKOFF-PROMPT.md](docs/KICKOFF-PROMPT.md) — intended first task

## Hard rules

- **Every user-facing string goes through i18next**, en + es in the same commit. Never hardcode UI text. Spanish = neutral Latin American, informal "tú", plain language.
- **Money is integer cents.** No floating-point money math, ever.
- **Financial formulas must be correct and documented** — the FV/savings projections, emergency-fund ratio, and income-volatility (coefficient of variation) calculations will be described in a thesis; implement them cleanly in a `src/lib/finance/` module with unit tests, so the code can be cited/excerpted in the paper.
- **Stay inside scope**: PRD MVP + ACADEMIC.md thesis-support features. No backend, no auth, no bank linking, no payments.
- Mobile-first: 375px design width, touch targets ≥ 44px, add-expense ≤ 3 taps; offline-first PWA.

## Workflow

- Not yet a git repo — `git init`, commit in small working increments (a clean history also documents the build for the paper).
- After each feature: dev server at mobile viewport, toggle EN⇄ES, refresh to confirm persistence.
- Vitest tests required for all money math and everything in `src/lib/finance/`.

## Status

- [x] Research + planning (2026-07-07)
- [ ] Scaffold (Vite + React + TS + Tailwind + i18next + Dexie + PWA)
- [ ] Onboarding flow (language → income → starter envelopes)
- [ ] Envelopes + quick expense entry
- [ ] Accounts (cash/card)
- [ ] Irregular income mode (+ income-volatility stat, ACADEMIC #4)
- [ ] Remittance envelope + yearly total (+ fee awareness, ACADEMIC #2)
- [ ] Emergency-fund adequacy indicator (ACADEMIC #1)
- [ ] Savings-goal projection (ACADEMIC #3)
- [ ] Month view
- [ ] CSV export
