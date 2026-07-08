# Substack post #1 — ready to paste

*How to publish: New post → paste the Title and Subtitle into their fields, then the body below. Insert images where marked. Suggested publication name: **Faro Quant** (tagline: "Building an open-source AI portfolio copilot, in public.")*

---

**TITLE:** I'm Building a Robinhood-Cortex-Style AI Portfolio Copilot — Free, Open Source, and It Can't Hallucinate

**SUBTITLE:** An MSF grad and defense engineer's build-in-public project: real quant finance, a tool-grounded AI agent, and a $0 stack anyone can replicate.

---

**[IMAGE: brand/logo-wordmark.svg — the Faro wordmark]**

The most dangerous thing an AI can do in finance isn't giving bad advice. It's giving you a **number it made up** — confidently, fluently, and wrapped in a professional tone.

That's the problem I'm setting out to solve in public, with a project called **Faro** (Spanish for *lighthouse*): an open-source AI portfolio copilot where the AI is *architecturally incapable* of inventing figures.

## Who I am, and why this project

I'm a Master of Science in Finance graduate (University of Arizona) and a working engineer at Raytheon. I've spent my career where correctness isn't optional — and I want to bring that discipline to the intersection everyone's racing toward: **AI × personal finance**.

Robinhood's Cortex, launched to Gold subscribers, shows where the industry is going: AI portfolio digests, plain-English market research, natural-language tools. I'm building the same core idea as a self-hosted, transparent, free alternative — partly because I want it for my own portfolio, and partly because the best way to show you understand a system is to build one.

## What Faro does

You enter your holdings. Faro then:

1. **Computes institutional-grade risk analytics from first principles** — Sharpe and Sortino ratios, alpha and beta against the S&P 500, historical *and* parametric Value-at-Risk, CVaR, maximum drawdown, correlation structure, concentration. Every formula implemented by hand in a pure Python module, documented, and unit-tested against independently computed reference values. No black-box quant libraries in the engine.
2. **Explains it all through an AI copilot** — ask *"How risky is my portfolio?"* or *"What happens if NVDA drops 20%?"* and an LLM agent answers in plain English.

Here's the architectural trick, and the whole thesis of the project:

> **The agent's only source of numbers is the quant engine.** It answers by calling tested functions — `get_metric`, `run_price_shock_scenario` — and reasoning over their outputs. Every figure in every answer is traceable to a computation. If it didn't come from a tool call, it doesn't get said.

This pattern — deterministic engine underneath, LLM as the reasoning-and-language layer on top — is, I believe, the only responsible way to put AI in front of financial data. It's also exactly how production fintech AI is built.

## The $0 constraint

Everything runs free, on your own machine:

- **Market data:** Yahoo Finance daily bars, cached locally. No key.
- **Database:** SQLite. **Hosting:** Docker on your PC.
- **The AI:** a local open-source model via Ollama by default — with a provider layer that switches to Claude by setting a single environment variable. No code changes.

The acceptance test I've set for myself: *fresh clone → `docker compose up` → working app with a demo portfolio, in under five minutes, with zero paid keys or accounts.* If you can't replicate it, I haven't shipped it.

## What Faro deliberately won't do

No trade execution. No brokerage linking. No "should I buy?" answers — the copilot refuses and instead shows you *how to evaluate the question yourself* (your position is X% of the portfolio, its beta is Y, it contributes Z% of your VaR…). Educational analytics, not investment advice. Drawing that line clearly is a feature, not a limitation.

## It's built — and the eval caught real hallucinations

The MVP is done: a 56-test quant engine (every metric hand-verified *and* cross-checked against independent implementations), a bilingual dashboard, scenario engine, daily digests, and the tool-grounded copilot running on either Claude or a free local model.

The best part is what the **grounding eval** found. I wrote a 20-question spot-check (English + Spanish, including "should I buy?" traps) that extracts every number from the copilot's answers and verifies each one traces to a tool result. First run against a small local model: **28 ungrounded numbers** — including a completely fabricated "$12,345.67 profit" and answers recycled from chat history without re-computing. Each failure led to a concrete fix: prompt hardening, independent-turn evaluation, richer tool outputs so the model never needs to derive figures itself. That loop — measure, catch, fix, re-measure — is the whole point of the architecture. A vibe-checked chatbot would have shipped those hallucinations.

## What's coming in this newsletter

- **Post 2:** Implementing VaR two ways — and proving both correct (including writing an inverse-normal CDF from scratch)
- **Post 3:** Teaching a local LLM to use quant tools (and every way it went wrong)
- **Post 4:** The grounding eval — how I caught my copilot inventing $12,345.67
- **Post 5:** Ship it — Docker, CI, and the 5-minute replication test

The code is public on GitHub.

**[IMAGE: screenshot of the dashboard — add after milestone 5]**

If you're into quant finance, AI engineering, or watching someone build a fintech product with defense-industry paranoia about correctness — subscribe and follow along.

*Faro is an educational tool, not an investment adviser. Nothing in this newsletter is investment advice.*

---

*End of post. Before publishing: replace the GitHub link placeholder once the repo is public, export logo-wordmark.svg to PNG for Substack (it doesn't take SVG), and set the post's social preview image to the logo.*
