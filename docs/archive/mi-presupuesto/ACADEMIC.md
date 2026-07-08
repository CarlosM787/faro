# Academic Mapping — Mi Presupuesto as an MSF Capstone/Thesis

*Purpose: this project doubles as a Master of Science in Finance deliverable (written thesis/capstone paper). This doc maps app features to finance literature so the paper and the build reinforce each other. The implementing session should treat the "thesis-support" features below as in-scope alongside the PRD.*

## Suggested thesis framing

**Working title:** "Mobile-First Financial Inclusion: Designing a Bilingual Budgeting Tool for Cash-Based and Irregular-Income Households"

**Research question:** Can purpose-built digital tools address the budgeting failures that mainstream fintech creates for underbanked, bilingual, irregular-income households — and which financial-theory mechanisms (mental accounting, income smoothing, remittance-cost transparency) do the heavy lifting?

## Feature → finance-concept map

| App feature | Finance concept / literature anchor | Paper section |
|---|---|---|
| Envelope budgeting | **Mental accounting** (Thaler, 1985; 1999 — Nobel 2017); self-control and commitment devices | Behavioral finance |
| Cash-first design | **"Pain of paying"** — cash payers recall spending more accurately (Journal of Consumer Research, 2017); payment-form effects on consumption | Behavioral finance |
| Irregular-income mode (budget off lowest month, buffer envelope) | **Consumption smoothing** under income volatility; precautionary savings (Friedman's permanent income hypothesis as the classical frame; gig-economy income volatility studies) | Household cash-flow management |
| Buffer / "Colchón" envelope | **Emergency-fund adequacy**; liquidity constraints in low-income households (JPMorgan Chase Institute income-volatility research is a strong citable source) | Household cash-flow management |
| Remittance envelope + yearly totals + fee awareness | **Remittance economics** — World Bank Remittance Prices Worldwide database; Consumer Reports on remittance-app fee opacity; cost of remittances vs. SDG 10.c 3% target | Remittance economics |
| Bilingual per-user design | **Financial inclusion / access barriers** (Brookings on Latino fintech adoption; CFPB Spanish-language initiatives; FDIC unbanked/underbanked household surveys) | Financial inclusion |
| Savings goals with projections | **Time value of money** — goal-based saving with simple FV math surfaced to the user | Application of core finance |
| No bank-linking / local-first privacy | **Trust as adoption barrier** among immigrant communities; data-privacy economics | Financial inclusion |

## Thesis-support features (add to build scope — small but citable)

These are cheap to build and give the paper concrete artifacts:

1. **Emergency-fund adequacy indicator** — months-of-expenses covered by the buffer envelope, with the standard 3–6 month guidance. (One derived metric + one UI element.)
2. **Remittance cost awareness** — user optionally logs the fee paid per remittance; app shows annual fees paid and % cost vs. the World Bank 3% benchmark.
3. **Savings-goal projection** — "at $X/month you reach your $Y goal in N months," simple FV/annuity math, shown bilingually.
4. **Income-volatility stat** — coefficient of variation on the user's logged monthly income, driving the suggested budget baseline (lowest vs. average month). Directly quotable in the methodology chapter.

## Suggested paper structure

1. Introduction & motivation (financial inclusion gap, Mint shutdown / pricing of incumbents)
2. Literature review (mental accounting, income volatility, remittance costs, inclusion barriers)
3. Market analysis (from [RESEARCH.md](RESEARCH.md) — competitor table, Reddit pain-point synthesis)
4. Design methodology (personas → feature mapping above; design principles as testable hypotheses)
5. Implementation (architecture summary from [TECH-NOTES.md](TECH-NOTES.md); bilingual i18n approach)
6. Evaluation (usability walkthrough; the MVP success criteria in [PRD.md](PRD.md) as evaluation rubric; small user test with 3–5 bilingual users if the program allows)
7. Limitations & future work (the archived monetization analysis in [archive/cobra/](archive/cobra/RESEARCH.md) makes an honest "commercial viability" section)

## Citations to pull (verify current URLs when writing)

- Thaler, R. (1985) "Mental Accounting and Consumer Choice"; (1999) "Mental Accounting Matters"
- World Bank — Remittance Prices Worldwide (remittanceprices.worldbank.org)
- JPMorgan Chase Institute — income volatility reports
- FDIC National Survey of Unbanked and Underbanked Households
- Brookings — "Latinos and the future of finance" (linked in RESEARCH.md)
- Consumer Reports — remittance app costs/transparency (linked in RESEARCH.md)
- CFPB Spanish-language financial resources (linked in RESEARCH.md)
