# Session handoff prompt — for Opus (or any Claude Code model)

*The original build kickoff prompt served its purpose (MVP shipped 2026-07-08). This file is now the **continuation prompt**: paste it into any new Claude Code session — Opus is fine and conserves premium-model usage — to pick up exactly where things stand.*

---

You are continuing work on Faro, a SHIPPED open-source project in this folder. Read CLAUDE.md first — it has the hard rules and the current Status checklist — then README.md. Key facts: repo is live at github.com/CarlosM787/faro (CI green, keep it green), website live at faroquant.com (auto-deploys from website/ via .github/workflows/pages.yml on push), app runs via `docker compose -p faro up` at localhost:3000, dev servers via .claude/launch.json (api :8000, web :5173, site :4173).

Non-negotiable invariants — violating any of these is a regression:
1. quant/ stays pure numpy/pandas, every formula documented, hand-computed + cross-check tests (pytest must stay at 100% pass; currently 68 tests).
2. The agent's only numeric source is its five tools; the grounding checker flags unsupported numbers. Claim it accurately: "unsupported numbers are detected and surfaced" — NEVER "the model can't hallucinate."
3. Every user-facing string bilingual EN/ES in the same commit (CI enforces locale key parity; also no hardcoded JSX strings).
4. Claude primary / Ollama keyless fallback, switched by env only. Tests/CI use FakeProvider — never require a key or a running model.
5. No trade execution, no brokerage linking, no personalized advice. Educational-tool disclaimers stay.
6. Quality gates before every commit: ruff + mypy strict + pytest (api/), check:i18n + build (web/). Small conventional commits; update README/CLAUDE.md Status as things land; push (CI + Pages deploy automatically).

Verification habits: after UI changes check EN⇄ES both; after agent changes run `python api/scripts/grounding_check.py --limit 5` against a running stack; after data-layer changes re-run the full pytest suite.

Likely next tasks (check CLAUDE.md Status for what's still unchecked): README screenshots/GIF, enable Enforce-HTTPS on GitHub Pages when the cert is issued, re-run the full grounding eval with a real ANTHROPIC_API_KEY and document the Claude-vs-local comparison in docs/GROUNDING-CHECK.md, publish docs/SUBSTACK-ARTICLE.md, then the "What I'd build next" list in README (Fama-French factors first).

---

*Resume line for an interrupted session: "Read CLAUDE.md and README.md, then continue from the next unchecked Status item."*
