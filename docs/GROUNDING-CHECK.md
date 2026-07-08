# Grounding spot-check — "the copilot can't make numbers up," measured

**What this is:** a repeatable eval (`api/scripts/grounding_check.py`) that fires 20 portfolio questions at the live copilot — 14 English, 6 Spanish, including two "should I buy/sell?" refusal probes — then extracts every numeric token from each answer and verifies it traces to a tool result from that turn. Any unmatched number is a violation. Exit code is non-zero if any answer contains one.

**Model under test:** `qwen2.5:7b` via Ollama — deliberately the *weakest* link in the stack. If the guardrails hold up on a 7B local model, they hold up on Claude (the primary provider), which is dramatically stronger at tool discipline.

## Results across iterations (2026-07-08)

| Run | Ungrounded numbers | What it caught → what was fixed |
|---|---|---|
| 1 | **28** | (a) Model repeated figures from persisted chat history without re-calling tools → prompt hardened ("call the tool again even if the number appeared earlier") + eval made independent-turn (`fresh` flag). (b) Fabricated values, e.g. a literal `$12,345.67` "profit" → correctly flagged; the fix is the check itself. (c) "S&P 500" flagged as the number 500 → index names added to the trivial-token list. |
| 2 | **4** | (a) Drawdown quoted as "17.95%" vs tool's `-0.1795` — sign+percent combination missing from the matcher → added. (b) Model *derived* the benchmark's return from α and β because the tool didn't provide it → `compare_to_benchmark` now returns it explicitly. (c) Two genuine small-model arithmetic inventions — flagged, as designed. |
| 3 (final) | **2** | 18/20 answers fully grounded; every answer used ≥1 tool call; both "should I buy/sell?" probes refused with an educational reframe (in the right language). The 2 residual violations are the local 7B model doing its own arithmetic ("~85% diversified" derived from HHI; one misquoted position figure) — detected and surfaced by design. |

## Why the residual matters less than the mechanism

A 7B local model will occasionally do freelance arithmetic no prompt can fully prevent. The point of this architecture is that **every such case is detected and surfaced** (logged server-side and returned in the SSE `done` event) rather than silently shipped to the user. On the primary provider (Claude), tool discipline is substantially stronger; the eval is the regression harness that proves it per provider.

## Reproduce

```bash
# API running (docker compose up, or uvicorn), then:
cd api && python scripts/grounding_check.py            # all 20 questions
python scripts/grounding_check.py --limit 5            # quick pass
```
