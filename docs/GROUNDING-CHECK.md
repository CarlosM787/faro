# Grounding spot-check — "unsupported numbers are detected and surfaced," measured

**What this is:** a repeatable eval (`api/scripts/grounding_check.py`) that fires 20 portfolio questions at the live copilot — 14 English, 6 Spanish, including two "should I buy/sell?" refusal probes — then extracts every numeric token from each answer and verifies it traces to a tool result. Any unmatched number is a violation; exit code is non-zero if any answer contains one. Raw run logs are committed under [eval-logs/](eval-logs/).

**Model under test:** `qwen2.5:7b` via Ollama — deliberately the *weakest* link in the stack. Claude (the primary provider) follows the "always re-call the tool" instruction far more reliably; this eval stress-tests the guardrail against a model that doesn't.

**The honest headline:** in *both* modes below, **every flagged figure is surfaced to the user** — an amber warning under the chat message and the digest (not just a server log). No fabricated number is ever shown silently. That is the claim, and it holds regardless of pass rate.

## Two modes — and why the gap matters

The eval runs in two configurations (`--fresh` default, `--no-fresh`):

| Mode | What it measures | Local 7B result (Dockerized, 2026-07-08) |
|---|---|---|
| **fresh** (history OFF) | Per-answer grounding integrity — each question is an independent turn, forcing a tool call | **18/20 answers fully clean** (4 flagged numbers total). Both advice traps refused; all Spanish answers clean. |
| **no-fresh** (history ON — the shipped chat config) | The real multi-turn experience | **3/20 clean (139 flagged numbers).** The 7B model, once history is present, recites earlier numbers *without re-calling tools* (`tools=0` on most turns). The checker flags every one. |

**Read that gap carefully — it's the most useful thing this eval found.** The strict rule "a number must trace to a tool call *this* turn" means a weak model that answers from conversational memory gets flagged wholesale. Two takeaways:

1. **The safety mechanism works exactly as designed.** In the noisy no-fresh case, the product does not silently emit 139 unverified numbers — it flags all of them in the UI. Honest-by-construction beats a good-looking demo.
2. **Model choice matters for UX, not for safety.** On the local 7B model, multi-turn chat is *safe but noisy* (frequent warnings). Claude adheres to the re-call instruction and produces far fewer flags. The eval is the per-provider regression harness that proves this — run it against your configured provider.

## Iteration history (fresh mode) — how the checker earned trust

| Run | Ungrounded | What it caught → what changed |
|---|---|---|
| 1 | **28** | Model recited from history without re-calling tools → prompt hardened + `fresh` flag added. A real fabricated `$12,345.67` "profit" with **zero** tool calls ([eval-logs/run1-fresh.txt](eval-logs/run1-fresh.txt), Q10) → correctly flagged; the catch *is* the fix. "S&P 500" flagged as `500` → index names added to the trivial-token list. |
| 2 | **4** | Drawdown quoted "17.95%" vs tool's `-0.1795` — sign+percent form added to the matcher. Model *derived* the benchmark return from α and β → `compare_to_benchmark` now returns it explicitly. |
| 3–4 (Docker) | **3–4** | 18/20 clean on the containerized stack; residuals are the 7B doing freelance arithmetic (e.g. "≈85% diversified" off HHI) — flagged, as designed. |

## Reproduce

```bash
# API running (docker compose -p faro up, or uvicorn), then:
cd api
python scripts/grounding_check.py              # fresh mode (per-answer integrity)
python scripts/grounding_check.py --no-fresh    # shipped config (history on)
python scripts/grounding_check.py --limit 5     # quick pass
```

Raw outputs from the runs above are in [eval-logs/](eval-logs/).
