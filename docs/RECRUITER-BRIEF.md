# Faro — Recruiter Brief

*A one- to two-page explanation of Faro for job applications and interviews. For the full technical README, see [README.md](../README.md); for the honest eval, [GROUNDING-CHECK.md](GROUNDING-CHECK.md).*

**Live:** [faroquant.com](https://faroquant.com) · **Code:** [github.com/CarlosM787/faro](https://github.com/CarlosM787/faro) · **Run it:** `git clone` → `docker compose up` → localhost:3000

---

## What Faro is

Faro is an **open-source, self-hosted, bilingual (English/Spanish) AI portfolio-analytics app.** You enter your holdings; a deterministic quant engine computes institutional-grade risk metrics (Sharpe, Value-at-Risk, beta, drawdown, and more), and an AI copilot lets you ask about them in plain English or Spanish. It runs free on your own machine, with or without an API key. It is an **educational tool** — no trade execution, no brokerage linking, no personalized investment advice.

## Why it's relevant to fintech engineering

Every fintech is now racing to put an LLM in front of financial data (Robinhood's Cortex is the flagship example). The hard part isn't the chatbot — it's **trust**: what stops the model from stating a number it made up? Faro is a concrete, working answer to exactly that problem, built with the correctness discipline of a defense-industry engineer and the domain grounding of a finance graduate. It demonstrates the competencies these roles screen for: quantitative correctness, LLM tool-use architecture, guardrail engineering, honest evaluation, and full-stack + DevOps delivery.

## The technical problem it solves

The #1 failure mode of LLM finance apps is **hallucinated numbers** — confident, fluent, and invented. Faro's answer is architectural, in three layers:

1. **A deterministic quant engine** — every metric implemented from its documented formula in pure `numpy`/`pandas`, unit-tested against hand-computed references *and* independent libraries.
2. **An AI copilot that can only call tools** — the LLM's sole source of numbers is a set of typed tools that dispatch into that engine. The dashboard and the copilot share one service layer, so they can never disagree.
3. **A grounding checker on every reply** — it extracts each number from the answer and verifies it traces to a tool result *from that turn*. Anything unsupported is **detected and surfaced** as a visible in-app warning.

> The claim is deliberately narrow and testable: **"unsupported numbers are detected and surfaced"** — *not* "the model can't hallucinate." That honesty is the point.

## What I personally built

The entire system — solo:

- The **quant engine** from first principles (including an inverse-normal CDF hand-written via Acklam's approximation rather than importing `scipy`, then validated against `scipy` to 1e-8).
- The **grounding checker** and the agent's five-tool interface into the shared service layer.
- A **provider-agnostic LLM layer** (Anthropic Claude primary, local Ollama fallback) switchable by one environment variable.
- A **fully bilingual** React dashboard, streaming copilot, scenario lab, and daily digest — EN/ES paired in every commit, CI-enforced.
- A **public two-mode eval** with committed raw logs, the whole thing Dockerized, CI-green, and deployed to a live site over HTTPS.

## What makes it different from a normal dashboard

A normal dashboard shows numbers. Faro adds a natural-language layer **and refuses to let that layer lie**: every figure the AI states is checked against a real computation, and the app tells you out loud when one isn't. It also draws a clear compliance boundary (educational-only, no advice, no trading) and does it all bilingually — details that matter in regulated, multi-market fintech.

## How the AI grounding system works (in one paragraph)

The copilot receives typed tools, not raw data. When you ask "how risky am I?", it calls `get_metric`/`get_portfolio_summary`, the tools run the tested quant functions, and the model answers **from the tool outputs**. A post-response checker then tokenizes every number in the reply and matches it against that turn's tool results (accounting for percentages, sign flips, comma grouping, rounding). Unmatched numbers are flagged in the SSE response and rendered as an amber warning under the message. The eval runs this 20 questions deep, in two languages, in two modes — and publishes the results, flattering and unflattering alike.

## How to run / evaluate it in five minutes

```bash
git clone https://github.com/CarlosM787/faro.git && cd faro
docker compose up --build        # → http://localhost:3000 (seeded demo portfolio)
```

Then, to judge the engineering:

- **The math:** [`api/src/faro_api/quant/`](https://github.com/CarlosM787/faro/tree/main/api/src/faro_api/quant) + [`api/tests/`](https://github.com/CarlosM787/faro/tree/main/api/tests) — first-principles metrics, tested two ways.
- **The guardrail:** [`api/src/faro_api/agent/guardrails.py`](https://github.com/CarlosM787/faro/blob/main/api/src/faro_api/agent/guardrails.py) — the grounding checker.
- **The honesty:** [`docs/GROUNDING-CHECK.md`](GROUNDING-CHECK.md) + [`docs/eval-logs/`](eval-logs/) — two-mode eval with raw logs, including the fabricated `$12,345.67` the checker caught.

**Honest eval headline:** on a deliberately weak local 7B model, **18/20** answers were fully grounded in per-answer mode; in multi-turn mode the weak model recites from history and gets flagged wholesale (**139** figures) — *every one surfaced to the user*, never hidden. A frontier model is expected to produce far fewer flags (measuring the Claude-vs-local gap with a real key is the documented next step). The safety property holds regardless of the score.

## Suggested resume bullets

- Built an open-source, self-hosted **AI portfolio-analytics app** (FastAPI · React/TS · Docker) pairing a deterministic quant engine with an LLM copilot; MIT-licensed, live at faroquant.com, runs free with no API key.
- Implemented **8+ institutional risk metrics** (Sharpe, Sortino, beta, Jensen's alpha, historical & parametric VaR, CVaR, max drawdown, risk contributions) from first principles in pure `numpy`/`pandas`; **68 unit tests**, `mypy --strict`, CI green.
- Engineered an **LLM grounding checker** that verifies every number in each answer against quant-engine tool outputs and **surfaces unsupported figures in-app**; published a **two-mode bilingual eval** with committed logs.
- Designed a **provider-agnostic LLM layer** (Claude primary, local Ollama fallback) switchable by one env var with zero code changes.
- Delivered a **fully bilingual (EN/ES)** product with CI-enforced locale parity and a live HTTPS landing site; enforced a compliance boundary (no trading, no brokerage linking, no personalized advice).

## Interview talking points

Short, honest answers ready for the questions this project invites:

- **"How do you stop an LLM from hallucinating numbers?"** You don't *stop* it — you make it structurally hard and then *catch* what slips through. The model's only numeric source is typed tools over a tested engine, and a post-response checker verifies every number against that turn's tool output. The honest claim is "unsupported numbers are detected and surfaced," and it's measured, not assumed.
- **"Why detection instead of prevention?"** No one can promise a language model will never produce a bad number. What the architecture *can* do is flag an unsupported number in the UI rather than show it silently — a testable property, and the eval is what tests it.
- **The eval story (my favorite):** I ran it in the shipped multi-turn config and the weak local model scored 3/20 with 139 flagged figures — far worse than the flattering per-answer 18/20. I put *both* in the repo with raw logs, because the safety story is about what the user sees, not the score. That's the difference between a demo and a system you'd trust.
- **A real bug I found by testing like a user:** the chat page crashed to blank on modern Chrome because a concise-body `useEffect` returned the Promise from `scrollIntoView`, which React tried to call as a cleanup function. It was invisible until I loaded `/chat` in an actual browser instead of curl — a reminder that end-to-end verification catches what unit tests don't.
- **Correctness discipline:** I hand-wrote the inverse-normal CDF (Acklam's approximation) instead of importing `scipy`, then tested it against `scipy` to 1e-8. Every quant metric is validated two independent ways.
- **Architecture judgment:** the dashboard and the copilot read the *same* service layer — one engine, two consumers — so the chart and the chat can't disagree. The LLM provider swaps (Claude ⇄ local Ollama) with one env var and zero code changes.
- **Knowing what not to build:** no trade execution, no brokerage linking, no "should I buy?" answers, no intraday data — each a deliberate compliance/scope decision. Drawing that boundary is engineering judgment, not a limitation.

---

*Faro is an educational analytics tool, not an investment adviser. Nothing it produces is investment advice.*
