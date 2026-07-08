# Tech Notes — Cobra

Defaults for the implementing session (Opus). Push back in the plan if something better fits, but keep the MVP dependency-light and local-first.

## Stack (MVP)

- **Vite + React + TypeScript**, **PWA** (vite-plugin-pwa) — installable, offline-capable, phone-first.
- **Tailwind CSS** — mobile-first; touch targets ≥ 44px; design at 375px.
- **i18next + react-i18next** — two dimensions of language, keep them separate:
  - `uiLanguage` (worker's app language, default **es**)
  - per-client `docLanguage` (language documents render in)
- **Dexie (IndexedDB)** — local-first persistence; UUIDs + timestamps on all records for future sync.
- **PDF**: render the document as a print-styled HTML route and use the browser print-to-PDF flow (or `react-to-print`) for MVP — avoid heavy PDF libs until needed. The shareable artifact for MVP is the printable page + PDF.
- **Sharing**: Web Share API (files + text) with WhatsApp-prefilled message; clipboard fallback.
- **No backend in MVP.** Shareable *hosted* links, Stripe, and subscriptions all come in v0.2 with a small backend (suggest Cloudflare Workers or similar later — don't build now).

## The bilingual document engine (core differentiator — get this right)

- Price-list items store **both** names: `{ nameEs, nameEn, defaultPriceCents }`. Seeded per trade from bundled bilingual templates (landscaping, cleaning, handyman, painting).
- Custom line items: user enters Spanish; `nameEn` is optional — if empty, document falls back to `nameEs` (never machine-translate silently).
- Document chrome (headers "Estimate/Presupuesto", "Total", "Valid until", payment instructions, status labels) is fully translated via i18next using the **client's** `docLanguage`, independent of `uiLanguage`.
- Currency/dates via `Intl.NumberFormat`/`Intl.DateTimeFormat` per document language. USD only for MVP.
- Spanish = neutral Latin American, informal "tú" in UI; documents use formal/professional register.

## Data model sketch

```
Business  { id, name, trade, phone, logoDataUrl?, uiLanguage, paymentInstructions }
PriceItem { id, nameEs, nameEn, defaultPriceCents, sortOrder }
Client    { id, name, phone, address?, docLanguage: 'en'|'es' }
Document  { id, kind: 'estimate'|'invoice', clientId, number, status,
            lineItems: [{ nameEs, nameEn?, qty, priceCents }],
            notes?, photos?: dataUrl[], validUntil?, issuedAt, paidAt?,
            paidMethod?: 'cash'|'zelle'|'check'|'card', sourceEstimateId? }
Counter   { estimateSeq, invoiceSeq }   // human-friendly numbering: EST-001, INV-001
```

- **Money as integer cents. Never floats.**
- Document totals computed, never stored redundantly without recompute on render.

## Project conventions

- `src/features/<feature>/`: onboarding, price-list, clients, documents, dashboard, settings.
- Locale files: `src/locales/{en,es}/*.json`; **zero hardcoded user-facing strings** — both languages in the same commit, always.
- Trade price-list seeds: `src/data/priceLists/<trade>.ts` (bilingual).
- Vitest + RTL; test money math, document totals, numbering, and the ES/EN rendering of the same document.

## Verification checklist per milestone

1. 375px viewport, no horizontal scroll, thumb-reachable primary actions.
2. Create the same estimate for an EN client and an ES client — chrome fully switches, line items show the right names.
3. Print-preview the document — looks professional on one page.
4. Refresh + airplane mode — data persists, creation flows still work.
