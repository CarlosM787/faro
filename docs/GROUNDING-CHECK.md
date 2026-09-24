# Grounding spot-check — "unsupported numbers are detected and surfaced," measured

**What this is:** a repeatable eval (`api/scripts/grounding_check.py`) that fires 20 portfolio questions at the live copilot — 14 English, 6 Spanish, including two "should I buy/sell?" refusal probes — then extracts every numeric token from each answer and verifies it traces to a tool result. Any unmatched number is a violation; exit code is non-zero if any answer contains one. Raw run logs are committed under [eval-logs/](eval-logs/).

**Model under test:** `qwen2.5:7b` via Ollama — deliberately the *weakest* link in the stack. Whether Claude (the primary provider) follows the "always re-call the tool" instruction more reliably is **untested**; this eval stress-tests the guardrail against a small local model that often doesn't.

**The honest headline:** in *both* modes below, **every flagged figure is surfaced to the user** — an amber warning under the chat message and the digest (not just a server log). Every number the checker flags is shown to the user. That is the claim, and it holds regardless of pass rate. The checker has blind spots, listed [below](#blind-spots).

## Two modes — and why the gap matters

The eval runs in two configurations (`--fresh` default, `--no-fresh`):

| Mode | What it measures | Local 7B result (Dockerized, 2026-07-08) |
|---|---|---|
| **fresh** (history OFF) | Per-answer grounding integrity — each question is an independent turn, so there is no earlier answer to copy from | **18/20 answers fully clean** (4 flagged numbers total). Both advice traps refused; all Spanish answers clean. |
| **no-fresh** (history ON — the shipped chat config) | The real multi-turn experience | **3/20 clean (139 flagged numbers).** The 7B model, once history is present, recites earlier numbers *without re-calling tools* (`tools=0` on most turns). The checker flags every one. |

**Read that gap carefully — it's the most useful thing this eval found.** The strict rule "a number must trace to a tool call *this* turn" means a weak model that answers from conversational memory gets flagged wholesale. Two takeaways:

1. **The safety mechanism works exactly as designed.** In the noisy no-fresh case, the product does not silently emit 139 unverified numbers — it flags all of them in the UI. Honest-by-construction beats a good-looking demo.
2. **Model choice changes how often you see warnings.** On the local 7B model, multi-turn chat is noisy: frequent, correct warnings. Whether Claude re-calls tools more reliably is untested. The same harness measures it: set `ANTHROPIC_API_KEY`, start the API, and run `python api/scripts/grounding_check.py` and `python api/scripts/grounding_check.py --no-fresh`.

## Iteration history (fresh mode) — how the checker earned trust

| Run | Ungrounded | What it caught → what changed |
|---|---|---|
| 1 | **28** | Model recited from history without re-calling tools → prompt hardened + `fresh` flag added. A real fabricated `$12,345.67` "profit" with **zero** tool calls ([eval-logs/run1-fresh.txt](eval-logs/run1-fresh.txt), Q10) → correctly flagged; the catch *is* the fix. "S&P 500" flagged as `500` → index names added to the trivial-token list. |
| 2 | **4** | Drawdown quoted "17.95%" vs tool's `-0.1795` — sign+percent form added to the matcher. Model *derived* the benchmark return from α and β → `compare_to_benchmark` now returns it explicitly. |
| 3–4 (Docker) | **3–4** | 18/20 clean on the containerized stack; residuals are the 7B doing freelance arithmetic (e.g. "≈85% diversified" off HHI) — flagged, as designed. |

## September 2026 re-run: three runs per mode

Same 20 questions, same `qwen2.5:7b` (Ollama, Q4_K_M, temperature 0.2), code at `bccdafc`, run locally on 2026-09-24. Each mode was run **three times** because one run of a sampled model is noisy. Logs: [eval-logs/run7-2026-09-24-*.txt](eval-logs/).

| Run | fresh: clean answers | fresh: flagged | no-fresh: clean answers | no-fresh: flagged | no-fresh answers with no tool call |
|---|---|---|---|---|---|
| 1 | 20/20 | 0 | 7/20 | 59 | 10/20 (all flagged) |
| 2 | 19/20 | 1 | 8/20 | 87 | 12/20 (all flagged) |
| 3 | 20/20 | 0 | 9/20 | 97 | 11/20 (10 flagged) |
| **Total** | **59/60** | **1** | **24/60** | **243** | **33/60 (32 flagged)** |

**Where the 243 flagged numbers came from.** Chat history stores the text of earlier answers, not their tool outputs, so a number the model repeats without a new tool call can only have come from an earlier answer. Comparing each flagged number (with the checker's own matching rules) against the earlier answers the model could see:

| | Count | Share |
|---|---|---|
| Same value appeared in an earlier answer that passed the check | 62 | 26% |
| Same value appeared only in an earlier flagged answer | 66 | 27% |
| No source anywhere in the visible conversation | 115 | 47% |

So the flags aren't only the checker being strict about repeated, correct values: about half had no source in the conversation at all.

**Compared with July:** better than the single July no-fresh run (3/20 clean, 139 flagged), but the English and Spanish system prompts haven't changed since then and the market data has. Three runs of 20 questions is a small sample; **treat the difference as noise**, not as an improvement.

## Blind spots

The checker proves that a number **traces to this turn's tool output**. It does not prove the answer is right. Specifically:

- **Everyday numbers are never flagged:** 0, 1, 2, 3, 4, 5, 10, 20, 50, 95, 99, 100, 252 and 500 (`_TRIVIAL` in `agent/guardrails.py`), plus any value from 1900 to 2100, which is treated as a year. "5%" or "$2,000" can't be flagged.
- **Loose matching:** a number matches if it equals a tool number as-is, sign-flipped, ×100 or ÷100, within 1% (or 0.005). An invented number can pass by landing near a real one.
- **Right number, wrong meaning:** it doesn't check that a traced number is attached to the right metric. In the recorded demo ([DEMO.md](DEMO.md)), a Spanish answer passed the check while describing 95% VaR as the loss "in the worst scenario". A one-day 95% VaR is expected to be exceeded on about 1 day in 20.
- **Words aren't checked:** calling a Sharpe ratio "moderate" or a portfolio "safe" passes, because only numbers are checked.
- **Tool calls aren't forced:** the copilot is told to call tools every turn, but no `tool_choice` is set. With history on, the local model often answers from memory, and the checker catches that afterwards.

## Reproduce

```bash
# API running (docker compose -p faro up, or uvicorn), then:
cd api
python scripts/grounding_check.py              # fresh mode (per-answer integrity)
python scripts/grounding_check.py --no-fresh    # shipped config (history on)
python scripts/grounding_check.py --limit 5     # quick pass
```

Raw outputs from the runs above are in [eval-logs/](eval-logs/).
