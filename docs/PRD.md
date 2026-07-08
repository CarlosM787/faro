# PRD — "Copiloto" AI Portfolio Copilot (working name)

Self-hosted AI portfolio analytics: enter your holdings → institutional-grade risk metrics computed from first principles → a Claude-powered agent that answers plain-English questions **using those metrics as tools**, plus Cortex-style daily digests. A hiring portfolio piece — see [RESEARCH.md](RESEARCH.md) for the career rationale.

## Audience

- **Primary**: engineering/quant hiring managers reading the repo and clicking the live demo. The README, tests, and architecture are as much "the product" as the UI.
- **Secondary**: the owner's real use — analyzing his own portfolio.

## MVP feature list (v0.1)

1. **Portfolio input** — add positions (ticker, shares, cost basis, purchase date). Multiple named portfolios. SQLite persistence. Demo seed portfolio so reviewers see a populated app instantly.
2. **Market data pipeline** — daily OHLCV via yfinance with on-disk caching and a fallback provider; graceful staleness handling (works offline with cached data).
3. **Quant engine** (`quant/` module — the MSF showcase). Each metric implemented from the documented formula with unit tests against hand-computed/reference values:
   - Returns (simple, log, time-weighted), annualized return & volatility
   - Sharpe & Sortino ratios (configurable risk-free rate)
   - Beta and alpha vs. benchmark (SPY default)
   - Historical & parametric (variance–covariance) VaR and CVaR at 95/99%
   - Maximum drawdown & drawdown series
   - Correlation matrix; portfolio concentration (HHI, top-position weight)
   - Position-level contribution to risk/return
4. **Dashboard (React)** — portfolio value & P/L, allocation donut, risk metric cards, drawdown & performance charts vs. benchmark, correlation heatmap.
5. **AI Copilot chat** (the AI showcase) — LLM agent with **tool-use only** access to the quant engine; **Claude (Anthropic API) as the primary model**, Ollama as the free keyless fallback for tests and replication (see TECH-NOTES):
   - Tools: `get_portfolio_summary`, `get_metric` (any metric above), `get_position_detail`, `run_price_shock_scenario` (e.g. "NVDA −20%", "market −10%"), `compare_to_benchmark`
   - Answers must cite the computed numbers it retrieved; the agent never invents figures
   - Refuses personalized financial advice ("should I buy X?") with a friendly educational reframe
   - Streaming responses; conversation history per portfolio
6. **Daily digest** (Cortex-style) — one-click generated brief: what moved the portfolio, biggest risk contributors, notable metric changes, upcoming earnings dates for holdings.
7. **Scenario page** — UI for the same shock scenarios the agent uses (shared code path — one engine, two consumers).
8. **Compliance guardrails** — persistent "educational tool, not investment advice" disclaimer; no execution, no recommendations.
9. **Recruiter-grade README** — architecture diagram, formula documentation with test references, screenshots/GIF, live demo link, "what I'd build next."

## v0.2+ (not in MVP — do not build yet)

- Factor exposure (Fama-French 3-factor regression) — strong MSF flex, first thing after MVP
- Custom natural-language screeners/indicators (Legends-style)
- Options analytics (Black-Scholes pricing, Greeks on holdings)
- Agent evals harness (grounding accuracy benchmark) — great blog-post material
- Multi-user auth (demo is single-user)
- Scheduled digest emails

## Explicit non-goals

- Trade execution or brokerage account linking (compliance line — state it in the README as a deliberate decision)
- Personalized investment advice of any kind
- Real-time/intraday data, HFT anything
- Crypto (unless trivially free via the same data path)
- Monetization

## Success criteria for MVP

- Every quant metric has a unit test against an independently computed reference value; CI green.
- The agent answers "how risky is my portfolio?" with actual computed VaR/vol/beta values traceable to tool calls — zero hallucinated numbers in a 20-question spot check.
- "Should I sell NVDA?" gets a compliant refusal + educational alternative.
- Fresh clone → `docker compose up` → working app with seed portfolio in under 5 minutes; chat works with `ANTHROPIC_API_KEY` in `.env` (primary) **or** with no key at all via local Ollama (fallback), so anyone can replicate it free.
- README alone convinces a technical reader the owner understands both the finance and the engineering.
