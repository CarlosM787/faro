# Faro — Project Handoff (canonical)

*The single source of truth for continuing Faro in a new AI session (Opus / Fable / ChatGPT / any Claude Code model) or by a human. Read this first, then [CLAUDE.md](../CLAUDE.md) and [README.md](../README.md). Last updated: 2026-07-13.*

---

## 1. Current status

Faro is a **shipped, live MVP** plus a recruiter-grade documentation layer.

- Core app (quant engine, dashboard, copilot, scenarios, digest) — **built, tested, running.**
- Website [faroquant.com](https://faroquant.com) — **live, HTTPS, recruiter-facing redesign deployed** (real screenshots, "for hiring managers" section, honest two-mode eval stat).
- Docs — README rewritten recruiter-grade; this handoff + [RECRUITER-BRIEF.md](RECRUITER-BRIEF.md) + [CHANGELOG.md](CHANGELOG.md) created; [GROUNDING-CHECK.md](GROUNDING-CHECK.md) reflects the honest two-mode eval; [SUBSTACK-ARTICLE.md](SUBSTACK-ARTICLE.md) drafted and claim-checked (not yet published).
- CI **green**; working tree expected clean on `main`.

**Open user tasks (Carlos):** add `ANTHROPIC_API_KEY` and re-run the eval on Claude; publish the Substack article; optional demo GIF / OG social image.

## 2. Live URLs & locations

| What | Where |
|---|---|
| Live site | https://faroquant.com (GitHub Pages, HTTPS) |
| Repo | https://github.com/CarlosM787/faro (remote `origin`, branch `main`) |
| Local app | http://localhost:3000 (web) · http://localhost:8000 (API, docs at `/docs`) |
| Local folder | `C:\Users\moral\OneDrive\Desktop\Finance App` |
| Dev servers | `.claude/launch.json` — `api` :8000, `web` :5173, `site` :4173 |

## 3. Local Docker commands

```bash
# from the repo root
docker compose up --build            # build + run; web → :3000, api → :8000
docker compose -p faro up            # named project (used in acceptance runs)
docker compose down                  # stop

# without Docker (dev):
cd api && uvicorn faro_api.main:app --reload     # :8000
cd web && npm run dev                            # :5173 (proxies /api)
```

Optional `ANTHROPIC_API_KEY` in `.env` selects Claude; unset → local Ollama (`ollama pull qwen2.5:7b`). If chat can't reach Ollama from inside Docker, set `OLLAMA_HOST=0.0.0.0` before starting Ollama.

## 4. Deployment flow

- **Website:** push to `main` touching `website/**` (or legal PDFs / the workflow) → `.github/workflows/pages.yml` copies `website/*` + `docs/legal/*.pdf` into `_site/` and deploys to GitHub Pages (~17s). **Push = live deploy to faroquant.com.** There is no staging — verify locally first (`site` launch config, :4173).
- **CI:** `.github/workflows/ci.yml` runs on every push to `main` (api: ruff + mypy + pytest; web: i18n parity + build). Keep it green.
- The site copy is a **single self-contained file** `website/index.html` with a JS `T = { en, es }` dictionary injected at runtime — WebFetch (no JS) can't see the rendered text; verify with a JS-capable browser.

## 5. Core architecture

```
web (React 18 + TS + Tailwind + Recharts, i18next EN/ES)
 │  REST + SSE (same-origin /api)
 ▼
api (FastAPI · Python 3.12 · mypy strict)
 ├── routers/     portfolios · metrics · series · scenarios · chat (SSE) · digest
 ├── agent/       provider-agnostic LLM layer (Claude ⇄ Ollama) · tools · prompts · guardrails · loop
 ├── services/    ★ single computation path shared by REST and agent tools
 ├── quant/       ★ pure numpy/pandas · documented formulas · reference-tested
 ├── data/        yfinance → Stooq fallback · on-disk cache · offline degradation
 └── db/          SQLite + SQLAlchemy 2.0
```

The dashboard and the copilot read the **same `services/` layer**; the copilot's five tools are thin wrappers over it. The grounding checker (`agent/guardrails.py`) verifies every number in a reply against that turn's tool outputs.

## 6. Non-negotiable invariants (violating any is a regression)

1. **`quant/` stays pure** numpy/pandas, no I/O; every formula documented; hand-computed **and** cross-check tests. `pytest` stays 100% (currently **68 tests**).
2. **The agent's only numeric source is its five tools.** The grounding checker flags unsupported numbers. Claim it as **"unsupported numbers are detected and surfaced"** — **never** "the model can't hallucinate."
3. **Bilingual EN/ES in the same commit** — CI enforces locale key parity; no hardcoded JSX strings. (The website's `T` dict has no CI check — keep EN/ES paired manually.)
4. **Claude primary / Ollama keyless fallback, switched by env only.** Tests/CI use a fake provider — never require a key or a running model.
5. **No trade execution, no brokerage linking, no personalized advice.** Educational disclaimers stay.
6. **Quality gates before every commit:** ruff + `mypy --strict` + pytest (api), `check:i18n` + build (web). Small conventional commits; push (CI + Pages auto-run).

## 7. What is verified

- **68 pytest tests** pass; `mypy --strict` clean; ruff clean; i18n parity clean; web build clean; **CI green** on recent pushes.
- **Docker** runs from clean clone; app reachable at :3000, API at :8000.
- **Grounding eval, two modes, committed logs** ([docs/eval-logs/](eval-logs/)): fresh **18/20** answers clean (4 flagged figures); no-fresh (shipped) **3/20** clean, **139** flagged — every flag surfaced in the UI.
- **Grounding warnings render in the UI** — chat and digest (verified with a live capture, [docs/screenshots/copilot-grounding-warning.png](screenshots/copilot-grounding-warning.png)).
- **Advice refusal** works at the prompt level — both eval trap questions refused with an educational reframe (fresh mode).
- **Website live** over HTTPS; all sections render EN/ES; screenshots serve 200; "20/20" overclaim removed.
- **The `$12,345.67` hook is real** — `docs/eval-logs/run1-fresh.txt` Q10: `tools=0 | violations=[12345.67]`.

## 8. What is NOT verified / uncertain

- **Claude (real key) grounding numbers** — the headline eval is on the local 7B model. The Claude-vs-local comparison has **not** been run; add `ANTHROPIC_API_KEY` and re-run `python api/scripts/grounding_check.py --no-fresh`, then record it in GROUNDING-CHECK.md.
- **A flagged digest live** — the digest grounding-warning path is code-verified but was not forced to fire in a live capture.
- **Stooq fallback banner in the wild** — only shows when the backup provider actually serves (normally cache/yfinance answer first).
- **Substack article** — claim-checked but **not published**; do a final human voice pass first.

## 9. Known limitations

- Grounding is **detection, not prevention** — weak local model in multi-turn chat is *safe but noisy* (frequent correct warnings).
- Advice refusal is **prompt-level**, not a code-level classifier.
- Free **daily-bar** data only (no intraday); occasional staleness; backup provider is split-adjusted only.
- **Single-user, local**; no auth/multi-tenant.
- **Installable web app, not a full offline PWA** (no service worker).

## 10. What not to break

- **Don't push unverified website changes** — push is an instant public deploy.
- **Don't touch app code/tests without re-running the gates** — CI must stay green.
- **Don't desync EN/ES** in either `web/src/locales/*` or the website `T` dict.
- **Don't reintroduce retired overclaims:** "20/20", "PWA"/full-offline, "cannot hallucinate", "hard-enforced advice refusal".
- **Don't add unrelated app features** in documentation/packaging mode (current phase) unless required to fix a public claim.
- **Don't commit large binaries into the Pages deploy path** unintentionally (`website/**` is what deploys).

## 11. Next roadmap

**Near-term (packaging):** publish Substack (after voice pass); optional 30s demo GIF for the README hero; OG social-preview image.
**Product (only if returning to feature work):** Fama-French 3-factor exposure · Claude-vs-local grounding benchmark documented · options analytics (Black-Scholes + Greeks) · scheduled digest emails · multi-user auth.

## 12. How to continue safely

1. Read this file → CLAUDE.md → README.md. Run `git status` / `git log` to confirm the real tree state before assuming anything (two AI sessions have worked in this folder concurrently before).
2. Make the smallest change that satisfies the request; keep EN/ES paired; keep claims matched to shipped code and the committed eval.
3. Run the relevant gates: UI change → check EN⇄ES; agent change → `python api/scripts/grounding_check.py --limit 5` against a running stack; data-layer change → full `pytest`.
4. Verify **before** pushing (push = deploy). Small conventional commit. Update README/CLAUDE.md Status and this handoff's "current status" when something lands.

## 13. Continuation prompts (copy-paste)

For a **new AI session (Opus / Fable / ChatGPT / Claude Code)**:

> Read `docs/PROJECT-HANDOFF.md`, then `CLAUDE.md` and `README.md`. Run `git status` and `git log --oneline -8` to confirm the real tree state before assuming anything. We are in documentation/recruiter-packaging mode — do not add app features. Then continue from the next open task in section 1 or the roadmap in section 11. Preserve the non-negotiable invariants in section 6; keep every public claim matched to the shipped app and the committed eval; keep EN/ES paired; do not push without my say-so.

For a **claim/accuracy audit**:

> Read `docs/PROJECT-HANDOFF.md` section 6–9. Grep the repo docs and `website/index.html` for overclaims: "cannot hallucinate", "guarantees", "20/20", "PWA"/offline, "prevents hallucinations", hard advice enforcement. For each hit, fix it or explain why it's acceptable. Report a diff summary; commit only if clean; do not push.

For **resuming the one open eval task**:

> With `ANTHROPIC_API_KEY` set and the stack running, run `python api/scripts/grounding_check.py --no-fresh`, then record the Claude result next to the local-7B numbers in `docs/GROUNDING-CHECK.md`. This closes the only unverified public claim. Do not change any other eval numbers.

## 14. What Carlos should do next — checklist

**Manual tests to run (5–10 min):**
- [ ] `docker compose up --build` → open http://localhost:3000; confirm dashboard loads with the seeded portfolio.
- [ ] Open the Copilot, ask 2–3 follow-up questions; confirm the **amber grounding warning fires** on the local model (it will, in multi-turn) and that tool-call chips show.
- [ ] Toggle **EN ⇄ ES** in the app; confirm the copilot answers in the selected language.
- [ ] Ask "Should I buy TSLA?" → confirm an educational reframe, not a recommendation.
- [ ] Visit https://faroquant.com; eyeball the two screenshots in place and the EN⇄ES toggle.

**Screenshots / GIFs still needed:**
- [ ] *(optional)* a 15–30s **demo GIF** for the README hero and Substack (copilot answering + a tool-call chip + a grounding warning).
- [ ] *(optional)* an **OG social-preview image** (1200×630) for nicer link unfurls on LinkedIn/Substack.
- Current three screenshots (dashboard, Spanish copilot, grounding warning) exist and are wired into the README and site.

**Substack:** publish-ready and claim-checked, **not published.** Do one human voice pass, export the wordmark to PNG (Substack rejects SVG), then publish. Hook = the real `$12,345.67` catch (verified in `run1-fresh.txt`).

**GitHub / LinkedIn sharing:** ready. The repo README is the front door; pin the repo; a LinkedIn post can reuse the RECRUITER-BRIEF's opening + a screenshot.

**Should Opus review again?** Worth one pass **after** you (a) run the Claude eval and paste the number into GROUNDING-CHECK.md, and (b) do the Substack voice pass — so the review sees final numbers and final copy.

**Push status:** the documentation commits are **local only** (unpushed) unless you've since pushed. Review the diff, then `git push origin main` (docs-only → CI runs and passes; the live site is untouched because Pages only deploys `website/**`).

---

*Resume line for an interrupted session: "Read docs/PROJECT-HANDOFF.md, then continue from the next open task in section 1 or the roadmap in section 11."*
