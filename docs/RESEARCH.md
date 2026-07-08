# Why this project — career-targeting rationale

*Compiled 2026-07-07. This project is a **hiring portfolio piece**, not a startup. The audience is engineering/quant hiring managers at Robinhood-style fintechs. Earlier product plans (consumer budgeting capstone, bilingual invoicing) are archived under docs/archive/ and are out of scope.*

## The target: what Robinhood-class fintechs are building

Robinhood's flagship AI product, **Cortex** (rolled out to Gold subscribers Q1 2026), does exactly what this project demonstrates in miniature:

- **Portfolio Digests** — AI-personalized summaries of a customer's holdings: top portfolio drivers, upcoming earnings/events.
- **Natural-language market research and actions** — plain-English questions answered from real-time market data and analyst research.
- **Scanner widgets & custom indicators** written via natural-language prompts (Robinhood Legends).
- **Advisor tooling** — Cortex extended to RIAs on TradePMR: AI portfolio analysis, tax insights, meeting prep.

Building a self-hosted "mini-Cortex" — **AI Portfolio Copilot** — signals: *I understand your product, your architecture (LLM agents with tool-use over quant engines), and your domain.*

## The owner's edge (what the project must showcase)

| Credential | What the project must prove | Where it shows |
|---|---|---|
| **MSF, University of Arizona** | Quant finance is implemented *correctly*, from formulas, not black-box imports | `quant/` module: Sharpe, Sortino, beta, VaR, max drawdown, correlations — each documented with the formula and unit-tested against reference values |
| **Engineer at Raytheon** | Production discipline | Typed code, tests, CI (GitHub Actions), clean layering, Docker, honest README |
| **AI skill (the differentiator in 2026 hiring)** | Agentic tool-use, not a chat wrapper | Claude agent whose *only* source of numbers is calling the quant engine's tools — grounded, non-hallucinated answers with the metric values cited |

## Why agentic tool-use is the right AI pattern to demo

The #1 failure mode of LLM finance apps is hallucinated numbers. The architecture that fixes it — the LLM calls deterministic, tested functions and reasons over their outputs — is exactly what production fintech AI teams build (and what Cortex's "sourced from trusted inputs" design implies). A candidate who can *show* this pattern working, with guardrails ("educational tool, not financial advice" + refusal to give personalized advice), demonstrates both engineering and compliance awareness. That combination is rare and hireable.

## Interview story the repo should support

1. "I built an AI portfolio analytics copilot: FastAPI quant engine, React dashboard, Claude agent with tool-use."
2. "Every metric is implemented from the formula and unit-tested — here's my VaR test against a known distribution." (MSF)
3. "The agent can't make up numbers — it must call the engine; here's the tool schema and an eval showing grounded answers." (AI engineering)
4. "CI runs the full test suite; it's Dockerized; here's the live demo link." (Raytheon rigor)
5. "I scoped out execution/advice deliberately — compliance boundary." (judgment)

## Constraints that shaped the plan

- **Free data only**: yfinance (no key) primary; Alpha Vantage/Stooq fallback. Daily bars are enough — this is analytics, not HFT.
- **No brokerage integration, no trade execution, no personalized advice** — legal/compliance line, stated in-app.
- **Total running cost: $0.** Free data, SQLite, local hosting, and a local Ollama model as the default LLM behind a provider-agnostic layer (Anthropic API optional if a key is present). The zero-cost, fully-replicable default is itself part of the portfolio story.

## Sources

- [Robinhood — Introducing Strategies, Banking, and Cortex](https://robinhood.com/us/en/newsroom/introducing-strategies-banking-and-cortex/)
- [Robinhood — Cortex Digests](https://robinhood.com/us/en/support/articles/cortex-digests/)
- [Robinhood — YES/NO event: latest AI innovations](https://robinhood.com/us/en/newsroom/robinhood-presents-yes-no-event/)
- [InvestmentNews — Cortex for RIAs on TradePMR](https://www.investmentnews.com/transformation/robinhood-brings-ai-powered-cortex-to-rias-on-tradepmr/266861)
- [Corporate Insight — Robinhood 2.0 feature review](https://corporateinsight.com/robinhood-2-0-how-the-commission-free-pioneer-is-rewriting-the-rules-again/)
