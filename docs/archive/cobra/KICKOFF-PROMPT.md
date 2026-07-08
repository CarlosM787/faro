# Kickoff prompt for Opus

Copy-paste this as the first message in a new Claude Code session (Opus selected) in this folder:

---

Read CLAUDE.md, docs/PRD.md, and docs/TECH-NOTES.md, then use plan mode to produce a step-by-step implementation plan for the Cobra MVP — milestones ordered so the app is runnable and demoable after every milestone. Pay special attention to the bilingual document engine (uiLanguage vs per-client docLanguage) since it's the core differentiator. After I approve the plan, implement milestone 1: git init, scaffold Vite + React + TypeScript + Tailwind + i18next + Dexie + PWA, set up en/es locale files, and build onboarding (language → business info → trade selection seeding the bilingual price-list). Verify at a 375px viewport, confirm the EN⇄ES UI toggle switches every string, and commit.

---

Tip: after milestone 1, prompt one milestone at a time: "Implement the next unchecked item in CLAUDE.md's Status list, verify per TECH-NOTES checklist, and commit."
