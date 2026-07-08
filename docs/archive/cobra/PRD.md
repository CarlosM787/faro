# PRD — "Cobra" (working name, from *cobrar* — to get paid)

Phone-first estimates & invoices for Spanish-speaking solo service pros in the US. The worker uses the app in Spanish; the customer receives a professional document in English or Spanish. Grounded in [RESEARCH.md](RESEARCH.md).

## Problem

Solo service pros (landscapers, cleaners, handymen, painters) lose money because producing professional English-language estimates and invoices is a language barrier. Existing tools are English-only (Jobber, Joist, Square) or built for crews with office staff (SolvPro). They run their business from a phone and WhatsApp.

## Target users (personas)

1. **Luis, 38, landscaper (Spanish-preferred).** Solo, paid per job, quotes verbally and loses bids to companies with "official" paperwork. Lives on WhatsApp. Will pay $10/mo if it wins him one extra job a year.
2. **Rosa, 44, house-cleaning business (Spanish-first, some English).** 2 recurring-client lists, wants monthly invoices that look professional and reminders when clients haven't paid.
3. **The customer (English-preferred homeowner).** Not a user, but the document's audience — the estimate must look as professional as anything Jobber produces.

## Core principles

- **Spanish-first UI, English-perfect output.** The app's own UI defaults to Spanish (toggleable); documents render in the *client's* language.
- **Structural translation, not machine translation.** Line items come from a bilingual price-list; documents are assembled from translated parts, so output is always professional.
- **WhatsApp is the delivery channel.** Share as link + PDF; email is secondary.
- **Phone-first, 5-minute estimate.** From "new estimate" to "sent" in under 5 minutes, thumb-only.
- **Payments optional.** Stripe pay-link is upside; cash/Zelle/check instructions are a first-class alternative.

## MVP feature list (v0.1)

1. **Onboarding** — pick language, business name, trade (landscaping/cleaning/handyman/painting/other), phone, logo (optional). Trade choice seeds a **starter bilingual price-list**.
2. **Price-list (Mis precios)** — items with name in ES + EN and default price ("Cortar pasto / Lawn mowing — $60"). Add/edit items; custom one-off items on the fly (user types in Spanish, may edit the English line or leave as-is).
3. **Clients** — name, phone, address, **preferred document language (EN/ES)**.
4. **Estimates (Presupuestos)** — pick client, add line items from price-list, quantities, optional photos, notes, validity date. Status: draft → sent → accepted/declined.
5. **Invoices (Facturas)** — create directly or convert from an accepted estimate in one tap. Status: sent → paid/overdue. Mark-as-paid with method (cash/Zelle/check/card).
6. **Document rendering** — clean professional PDF + shareable web link, rendered in the client's language, with business branding and payment instructions.
7. **WhatsApp-first sharing** — share sheet with prefilled bilingual message; also copy-link and email.
8. **Dashboard (Inicio)** — outstanding invoices total, this month's income, estimates awaiting response.
9. **Free-tier limit** — 3 documents/month; unlimited on Pro ($10/mo). Free-tier documents carry a small "Hecho con Cobra" footer. (MVP: enforce the limit locally with a placeholder upgrade screen; real billing is v0.2.)

## v0.2+ (not in MVP — do not build yet)

- **Stripe Connect payments** ("Pay this invoice" button + application fee) — the second revenue stream.
- Real subscription billing (Stripe Billing).
- Payment reminders (auto-nudge unpaid invoices via WhatsApp template).
- Recurring invoices for cleaning clients.
- Deposits on estimates.
- Year-end income summary export (tax season).
- Cloud accounts + multi-device sync (MVP is local-first, single device).

## Explicit non-goals

- Scheduling, work orders, crew management, GPS tracking (that's SolvPro/Jobber territory).
- Accounting/bookkeeping, QuickBooks sync.
- Machine translation of free text.
- Bank feeds of any kind.

## Success criteria for MVP

- A Spanish-only speaker can go from install → sent professional English estimate in under 10 minutes, zero English required on screen.
- New estimate → sent in ≤ 5 minutes, thumb-only, on a 375px viewport.
- The generated PDF/link is indistinguishable in professionalism from a Jobber/Square document.
- Works offline for creating documents; sharing requires network.
