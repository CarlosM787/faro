# Cobra — bilingual estimates & invoices for Spanish-speaking service pros

Phone-first PWA: the worker uses the app in Spanish, the customer receives a professional estimate/invoice in English or Spanish. Freemium ($10/mo Pro) + future payment processing. Local-first, no backend in MVP.

## Read these before doing anything

1. [docs/PRD.md](docs/PRD.md) — what to build (MVP) and what NOT to build yet
2. [docs/TECH-NOTES.md](docs/TECH-NOTES.md) — stack, bilingual document engine, data model
3. [docs/RESEARCH.md](docs/RESEARCH.md) — market evidence and monetization logic
4. [docs/KICKOFF-PROMPT.md](docs/KICKOFF-PROMPT.md) — intended first task

(An earlier consumer-budgeting plan is archived in docs/archive/mi-presupuesto/ — do not build it.)

## Hard rules

- **Two language dimensions, never conflated**: `uiLanguage` (worker, default es) vs per-client `docLanguage` (document rendering). Every user-facing string through i18next, en + es in the same commit.
- **No silent machine translation.** Line items are bilingual by structure (price-list) or fall back to the Spanish the user typed.
- **Money is integer cents.** No floating-point money math, ever.
- **Stay inside MVP scope** (PRD): no backend, no Stripe, no real billing, no scheduling/crew features.
- Phone-first: 375px design width, touch targets ≥ 44px, estimate creation ≤ 5 min thumb-only.
- Documents must look professional — the rendered estimate/invoice is the product.

## Workflow

- Not yet a git repo — `git init`, commit in small working increments.
- After each feature: dev server at mobile viewport; create one EN-client and one ES-client document and compare; refresh to confirm persistence.
- Vitest tests for money math, totals, document numbering, and bilingual rendering.

## Status

- [x] Research + planning (2026-07-07)
- [ ] Scaffold (Vite + React + TS + Tailwind + i18next + Dexie + PWA)
- [ ] Onboarding + trade-seeded bilingual price-list
- [ ] Clients (with per-client document language)
- [ ] Estimate builder
- [ ] Document rendering (printable, professional, EN/ES)
- [ ] WhatsApp-first sharing
- [ ] Invoices + convert-from-estimate + mark-as-paid
- [ ] Dashboard
- [ ] Free-tier limit (local) + upgrade placeholder
