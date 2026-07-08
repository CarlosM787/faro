# PRD — "Mi Presupuesto" (working name)

A simple, free, bilingual (English/Spanish) budget tracker for households — built for cash, irregular income, and remittances. Grounded in [RESEARCH.md](RESEARCH.md).

## Problem

Mainstream budgeting apps are expensive (~$100/yr), English-only, depend on flaky bank sync, and assume a single user with a fixed paycheck. Bilingual households in the US (and users in Latin America) often run on cash, gig income, and monthly remittances — and no app serves that combination.

## Target users (personas)

1. **Marisol, 46, house cleaner (Spanish-preferred).** Paid mostly in cash, income varies week to week, sends ~$200/month to family in Mexico. Wants to know "how much can I spend this week" without reading English financial jargon.
2. **Kevin, 23, her son (English-preferred).** Gig delivery driver. Helps his mom with the household budget. Wants the same shared numbers his mom sees, but in English, on his phone.
3. **Dani, 31, freelancer (bilingual).** Irregular invoices, hates YNAB's price and complexity. Wants envelope budgeting that plans off a conservative income estimate.

## Core principles

- **Free and private by default.** No bank credentials, no Plaid, no account required to start. Data lives locally; sync is opt-in later.
- **Manual entry must be FAST.** Adding an expense ≤ 5 seconds, thumb-only, works offline.
- **Every string in EN and ES from day one.** Language is a per-user setting, not an app-wide one. No machine-translated tone — natural, plain-language Spanish (Latin American neutral).
- **Cash is first-class.** A cash wallet is just another account.

## MVP feature list (v0.1)

1. **Onboarding** — pick language, add income (fixed or "it varies"), create starter envelopes from a template (Rent/Renta, Food/Comida, Transport, Sent to family/Enviado a familia, Savings/Ahorros…).
2. **Envelope budgeting** — monthly envelopes; assign money, see remaining; over-budget turns red; move money between envelopes.
3. **Quick expense entry** — amount → envelope → done. Optional note. Big number pad. Works offline (PWA).
4. **Accounts** — Cash and Card (manual balances). Transfers between them.
5. **Irregular income mode** — enter recent months' income; app suggests budgeting off the lowest/average and creates a buffer envelope ("Colchón").
6. **Remittance envelope** — built-in "Sent to family" envelope type with a monthly goal and a yearly total ("You've sent $2,400 to family this year").
7. **Month view** — simple summary: income in, spent, left to spend; per-envelope bars.
8. **Language toggle** — instant EN⇄ES switch anywhere in the app.
9. **Local persistence + export** — data in local storage/IndexedDB; CSV export.

## v0.2+ (not in MVP — do not build yet)

- Shared household: invite family members, per-user language over shared data (the key differentiator — needs a backend).
- Recurring transactions / bill reminders.
- Savings goals with progress ("Quinceañera fund").
- Simple reports (spending by category over time).
- Optional cloud sync + auth.
- Native mobile wrappers.

## Explicit non-goals

- Bank account linking / Plaid (avoids cost, privacy concerns, and the #1 reliability complaint).
- Investing, credit scores, loans, crypto.
- Ads or selling data — trust is the product for this audience.

## Success criteria for MVP

- A Spanish-only speaker can complete onboarding and log an expense with zero English on screen (and vice versa).
- Add-expense flow ≤ 5 seconds / ≤ 3 taps.
- Works fully offline after first load; data survives refresh.
- Lighthouse mobile performance ≥ 90.
