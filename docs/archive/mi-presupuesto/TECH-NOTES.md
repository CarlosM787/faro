# Tech Notes — recommended stack & architecture

Recommendations for the implementing session (Opus). These are defaults, not law — push back in the plan if something better fits, but keep the MVP dependency-light.

## Stack (MVP)

- **Vite + React + TypeScript** — fast dev loop, huge ecosystem.
- **PWA** (vite-plugin-pwa) — installable on phones, offline-first. This replaces native apps for MVP.
- **i18next + react-i18next** — mature i18n; namespaced JSON files `src/locales/en/*.json` and `src/locales/es/*.json`.
- **Dexie (IndexedDB)** for data; falls back gracefully, survives refresh, handles CSV export easily.
- **Zustand** (or React context if simpler) for state.
- **Tailwind CSS** — fast mobile-first styling. Big touch targets (44px+), dark mode later.
- **No backend for MVP.** Shared household (v0.2) will need one — design the data model so records have UUIDs and timestamps to make future sync feasible.

## i18n rules (important — this is the product's core differentiator)

- **Zero hardcoded user-facing strings.** Everything through `t()` from day one; retrofitting is how bilingual apps end up half-translated.
- Use **ICU/plural-aware keys** (i18next handles this) — Spanish pluralization and gender matter.
- **Currency & dates via `Intl.NumberFormat` / `Intl.DateTimeFormat`** with the user's locale. Support USD first; MXN and others later.
- Spanish should be **neutral Latin American Spanish**, informal "tú", plain language (target: someone with no financial-jargon background). E.g. "envelope" → "sobre", "buffer" → "colchón".
- Language stored per user profile in local settings; default from `navigator.language`; instant toggle without reload.

## Data model sketch

```
Settings   { id, language: 'en'|'es', currency, incomeMode: 'fixed'|'variable' }
Account    { id, name, type: 'cash'|'card', balance }
Envelope   { id, name, icon, monthlyBudget, kind: 'normal'|'remittance'|'buffer'|'savings', sortOrder }
Transaction{ id, amountCents, envelopeId, accountId, date, note?, type: 'expense'|'income'|'transfer' }
IncomeEntry{ id, monthISO, amountCents }   // for irregular-income suggestions
```

- **Store money as integer cents.** Never floats.
- All ids are UUIDs; all records carry `createdAt`/`updatedAt` (future sync).

## Project conventions

- `src/features/<feature>/` folder structure (onboarding, envelopes, transactions, accounts, settings).
- Vitest + React Testing Library; test money math and the irregular-income calculator thoroughly.
- Keep bundle small: no moment.js, no lodash, no component libraries unless justified.

## Verification checklist per milestone

1. `npm run dev` renders on a 375px viewport without horizontal scroll.
2. Toggle language — every visible string switches.
3. Refresh — data persists.
4. Airplane-mode test (offline) — app still loads and accepts entries.
