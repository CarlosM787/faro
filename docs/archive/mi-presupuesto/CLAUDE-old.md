# Mi Presupuesto — bilingual (EN/ES) budget tracker

Simple, free, offline-first envelope-budgeting PWA for English/Spanish households. Built for cash income, irregular income, and remittance tracking. No bank sync, no accounts, no backend in MVP.

## Read these before doing anything

1. [docs/PRD.md](docs/PRD.md) — what to build (MVP scope) and what NOT to build yet
2. [docs/TECH-NOTES.md](docs/TECH-NOTES.md) — stack, i18n rules, data model
3. [docs/RESEARCH.md](docs/RESEARCH.md) — why these decisions were made
4. [docs/KICKOFF-PROMPT.md](docs/KICKOFF-PROMPT.md) — the intended first task

## Hard rules

- **Every user-facing string goes through i18next** with both `en` and `es` translations in the same commit. Never hardcode UI text. Spanish = neutral Latin American, informal "tú", plain language.
- **Money is integer cents.** No floating-point money math, ever.
- **Stay inside MVP scope** (PRD §MVP). No backend, no auth, no bank linking, no charts libraries unless the PRD asks for it.
- Mobile-first: design at 375px width, touch targets ≥ 44px, add-expense flow ≤ 3 taps.
- Offline-first PWA: features must work without a network after first load.

## Workflow

- The project is not yet a git repo — run `git init` and commit in small, working increments.
- After each feature: run the dev server, verify at mobile viewport, toggle EN⇄ES, refresh to confirm persistence.
- Tests (Vitest) required for money math and the irregular-income calculator.

## Status

- [x] Research + planning (2026-07-07)
- [ ] Scaffold project (Vite + React + TS + Tailwind + i18next + Dexie + PWA)
- [ ] Onboarding flow
- [ ] Envelopes + quick expense entry
- [ ] Accounts (cash/card)
- [ ] Irregular income mode
- [ ] Remittance envelope + yearly total
- [ ] Month view
- [ ] CSV export
