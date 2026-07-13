# Substack post #1 — FINAL, ready to publish

*How to publish: Substack → New post. Paste the Title and Subtitle into their fields, then the body below (Substack accepts pasted markdown). Insert images at the two marked spots. Suggested publication name: **Faro Quant** — tagline: "Building an open-source AI portfolio copilot, in public."*

*Before hitting publish: (1) export `brand/logo-wordmark.svg` to PNG (Substack doesn't take SVG) for the header + social preview; (2) take the dashboard screenshot for the second image slot; (3) set the post URL slug to `faro-ai-portfolio-copilot`.*

---

**TITLE:** I Built an AI Portfolio Copilot That Has to Show Its Work

**SUBTITLE:** A finance grad and defense engineer's answer to AI's biggest problem in fintech: a quant engine the LLM can't bypass, a grounding checker that catches invented numbers, and a public eval to prove it. Open source, bilingual, free to run.

---

**[IMAGE 1: Faro wordmark PNG]**

The most dangerous thing an AI can do with your money isn't giving bad advice. It's stating a **number it made up** — confidently, fluently, wrapped in a professional tone.

I know because I caught my own AI doing it. In an early eval run, I asked my copilot "what's my total profit and loss?" and it answered **$12,345.67** — without calling a single tool. A suspiciously tidy number, and pure fiction. (That exact run is committed in the repo, [`docs/eval-logs/run1-fresh.txt`](https://github.com/CarlosM787/faro), line 10: `tools=0 | violations=[12345.67]`.)

The difference is: my system *caught it automatically*. That catch — and the architecture behind it — is what this post is about.

**Faro** ([faroquant.com](https://faroquant.com) · [github.com/CarlosM787/faro](https://github.com/CarlosM787/faro)) is an open-source, self-hosted, bilingual portfolio analytics app with an AI copilot. You enter your holdings; it computes institutional-grade risk metrics and lets you interrogate them in plain English or Spanish. It's free to run, MIT-licensed, and it never executes trades or gives personalized advice — an educational tool with the compliance boundary drawn in ink.

## Who I am, and why I built this

I'm a Master of Science in Finance graduate (University of Arizona) and an engineer at Raytheon. My day job is a domain where "the number is probably right" doesn't fly. When I watched the industry race to put chatbots in front of financial data — Robinhood's Cortex being the flagship example — I kept asking the same question: *what stops the model from making things up?*

For most products, the honest answer is "a system prompt and hope." I wanted to build the better answer, in public, with receipts.

## The architecture: math first, language second, verification always

Faro is three layers, and the order matters:

**1. A deterministic quant engine.** Every metric — Sharpe, Sortino, beta, Jensen's alpha, historical *and* parametric Value-at-Risk, CVaR, max drawdown, correlations, concentration, per-position risk contributions — is implemented from its documented formula in pure numpy/pandas. No black-box quant libraries in the engine. **68 unit tests** verify each one two ways: against hand-computed references (the derivations live in the test comments) and cross-checks against independent implementations. I even wrote the inverse-normal CDF from scratch (Acklam's rational approximation) rather than import scipy — then tested it against scipy to 1e-8.

**2. An AI copilot that can only call tools.** The LLM gets exactly five typed tools — portfolio summary, any metric, position detail, price-shock scenarios, benchmark comparison — and those tools dispatch into the *same service layer the dashboard uses*. One engine, two consumers: the chat and the UI cannot disagree, because they're reading the same functions. The provider layer swaps with one environment variable: Anthropic's Claude when a key is present, a free local model via Ollama when it isn't. The app costs $0 to run.

**3. A grounding checker on every reply.** After the model answers, Faro extracts every number from the text and verifies it traces to a tool result from that turn — handling the ways humans quote figures (percentages, sign flips, comma grouping, rounding). Anything unsupported is **detected and surfaced**, not silently shipped.

Note the claim carefully: not "the AI can never hallucinate" — nobody can honestly promise that. The claim is *unsupported numbers are detected and flagged*, and that claim is testable.

## So I tested it — and published the eval

I wrote a 20-question spot-check: fourteen English, six Spanish, including trap questions like "Should I buy TSLA?" and "¿Debería vender NVDA?" (both must be refused with an educational reframe, in the right language). The script extracts every number from every answer and fails loudly on anything ungrounded.

Then I ran it against the *weakest* model in my stack — a 7-billion-parameter local model — on the theory that if the guardrails hold there, they hold anywhere. The results, iteration by iteration:

- **Run 1: 28 ungrounded numbers.** The eval caught the model answering follow-ups from chat history without re-computing, that fabricated $12,345.67, and some false-positives of my own (the checker flagged "S&P 500" as the number 500).
- **Run 2: 4.** Fixes: prompt hardening, independent-turn evaluation, teaching the checker about sign-flipped percentages, and — my favorite — discovering the model had *derived* the benchmark's return from alpha and beta because my tool didn't provide it. The fix wasn't a better prompt; it was a better tool.
- **Run 3: 2.** Both were the small model doing freelance arithmetic ("you're about 85% diversified") — exactly what the checker exists to catch.
- **Final run, fully Dockerized: 18/20 answers completely clean**, 100% tool usage, every Spanish answer grounded, both advice traps refused.

Every failure became a committed fix with a regression test. That loop — measure, catch, fix, re-measure — is the entire thesis. A vibe-checked chatbot would have shipped all 28.

But here's the finding I'm proudest of, because it's the one that could have embarrassed me. That 18/20 is *per-question* mode — each question asked cold, forcing a tool call. When I re-ran the eval in the **actual shipped configuration** (conversation history on, exactly what a real user's multi-turn chat sends), the weak 7B model fell to **3/20**: once it can see earlier numbers in the history, it happily recites them without re-calling a single tool, and my strict "must trace to a tool call *this turn*" checker flags all of them. 139 flags in one run.

I could have quietly reported only the flattering number. Instead it's in the repo, both modes, with the raw logs — because the point isn't the score, it's that **not one of those 139 numbers reaches the user unlabeled.** Every one renders as a warning in the chat. On a frontier model like Claude, which actually obeys "re-call the tool," the flags nearly vanish; on a tiny local model, multi-turn chat is *safe but noisy*. That distinction — safe vs. clean — is exactly the kind of thing a grounding checker exists to make visible instead of letting you pretend it away.

**[IMAGE 2: dashboard screenshot]**

## What using it looks like

`git clone`, `docker compose up`, open localhost. A seeded demo portfolio appears with the full risk picture: metric cards with plain-language explanations, performance vs SPY, a drawdown chart, a correlation heatmap, and a positions table showing each holding's share of total risk (NVDA in the demo is 12% of the money but 24% of the risk — the copilot will happily explain why). Ask "what happens if NVDA drops 20%?" and you watch the tool call happen — a visible chip in the chat — before the answer cites the computed impact. Flip one toggle and the whole thing, copilot included, is in Spanish.

## What I deliberately didn't build

No trade execution. No brokerage linking. No "should I buy?" answers. No intraday data. Each of those is a scoping decision with a reason — compliance, privacy, honesty about what daily-bar analytics can support — and knowing where *not* to build is the most underrated engineering skill.

## What's next in this newsletter

- **Post 2:** Implementing VaR two ways — and writing an inverse-normal CDF from scratch to avoid a black box
- **Post 3:** Teaching a 7B local model to use quant tools (and every way it went wrong)
- **Post 4:** Anatomy of the grounding checker — how it caught $12,345.67
- **Post 5:** From clean clone to running app in 5 minutes — the replication test as a design constraint

The code is public: [github.com/CarlosM787/faro](https://github.com/CarlosM787/faro). The site is [faroquant.com](https://faroquant.com). If you're into quant finance, AI engineering, or watching someone build fintech software with defense-industry paranoia about correctness — subscribe.

*Faro is an educational tool, not an investment adviser. Nothing in this newsletter is investment advice.*

---

*End of post.*
