# Kickoff prompt for Opus

Copy-paste this as the first message in a new Claude Code session (Opus selected) in this folder:

---

Read CLAUDE.md, docs/PRD.md, docs/ACADEMIC.md, and docs/TECH-NOTES.md, then use plan mode to produce a step-by-step implementation plan for the Mi Presupuesto MVP — this is my Master of Science in Finance capstone, so the plan must include the four thesis-support features from ACADEMIC.md and put all financial formulas in a tested, well-documented src/lib/finance/ module I can excerpt in my paper. Order milestones so the app is runnable and demoable after every one. After I approve the plan, implement milestone 1: git init, scaffold Vite + React + TypeScript + Tailwind + i18next + Dexie + PWA, set up en/es locale files, and build the onboarding flow (language pick → income setup → starter envelopes from the bilingual template). Verify at a 375px viewport, confirm the EN⇄ES toggle switches every string, and commit.

---

Tip: after milestone 1, prompt one milestone at a time: "Implement the next unchecked item in CLAUDE.md's Status list, verify, and commit."
