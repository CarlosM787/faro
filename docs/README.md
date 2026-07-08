# Faro — documentation index

Everything that isn't code lives here or in the two sibling folders (`brand/`, `website/`).

## Product & engineering

| Document | Purpose |
|---|---|
| [PRD.md](PRD.md) | MVP scope, success criteria, explicit non-goals |
| [TECH-NOTES.md](TECH-NOTES.md) | Stack, architecture layering, quant-correctness and guardrail rules, per-milestone verification checklist |
| [RESEARCH.md](RESEARCH.md) | Career rationale: why a "mini-Cortex" targets fintech hiring (with sources) |
| [GROUNDING-CHECK.md](GROUNDING-CHECK.md) | Results of the 20-question EN/ES anti-hallucination spot-check (repeatable via `api/scripts/grounding_check.py`) |
| [KICKOFF-PROMPT.md](KICKOFF-PROMPT.md) | The prompt that kicked off the build (kept for the build-in-public story) |

## Legal (bilingual EN/ES — Word + PDF)

| Document | Files |
|---|---|
| Privacy Policy / Política de Privacidad | [docx](legal/Faro-Privacy-Policy.docx) · [pdf](legal/Faro-Privacy-Policy.pdf) |
| Terms of Use / Términos de Uso | [docx](legal/Faro-Terms-of-Use.docx) · [pdf](legal/Faro-Terms-of-Use.pdf) |
| Investment Disclaimer / Aviso Legal | [docx](legal/Faro-Investment-Disclaimer.docx) · [pdf](legal/Faro-Investment-Disclaimer.pdf) |

The PDFs are also served by the app (Settings page) from `web/public/legal/`.

## Marketing

| Asset | Location |
|---|---|
| Brand guide (palette, fonts, voice) | [../brand/BRAND.md](../brand/BRAND.md) |
| Logos (icon + wordmark, SVG) | [../brand/](../brand/) |
| Landing page (bilingual, live) | [faroquant.com](https://faroquant.com) — source in [../website/](../website/), auto-deployed by `.github/workflows/pages.yml` on every push |
| Substack launch article (post #1 + series plan) | [SUBSTACK-ARTICLE.md](SUBSTACK-ARTICLE.md) |

## Archive

`archive/` holds two earlier product plans that were researched and deliberately not built (a bilingual budgeting capstone and an invoicing app for Spanish-speaking service pros). Kept because the pivot story is useful context.
