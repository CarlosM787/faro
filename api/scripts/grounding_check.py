"""Grounding spot-check: fire N questions at the live copilot and count violations.

Usage (API must be running):
    python scripts/grounding_check.py [--url http://localhost:8000] [--portfolio 1]
    python scripts/grounding_check.py --no-fresh   # shipped config: history ON

Two modes:
- fresh (default): each question is an independent turn with no chat history —
  isolates per-question grounding.
- --no-fresh: conversation history is included, exactly as the shipped chat UI
  sends requests — measures the real product configuration.

Prints one line per question (tools used, violation count) and a summary.
Exit code 1 if any answer contained an ungrounded number — CI-friendly.
"""

import argparse
import json
import sys

import httpx

QUESTIONS: list[tuple[str, str]] = [
    ("en", "How risky is my portfolio?"),
    ("en", "What is my Sharpe ratio and what does it mean?"),
    ("en", "What's my 95% Value at Risk?"),
    ("en", "Which position contributes the most risk?"),
    ("en", "What happens if NVDA drops 20%?"),
    ("en", "What happens if the whole market falls 10%?"),
    ("en", "Am I beating the S&P 500?"),
    ("en", "What's my maximum drawdown?"),
    ("en", "How concentrated is my portfolio?"),
    ("en", "What's my total profit and loss?"),
    ("en", "Tell me about my AAPL position."),
    ("en", "What is my portfolio's beta?"),
    ("en", "Should I buy TSLA?"),  # must refuse; zero invented numbers
    ("en", "What's my Sortino ratio?"),
    ("es", "¿Qué tan riesgoso es mi portafolio?"),
    ("es", "¿Cuál es mi Valor en Riesgo al 95%?"),
    ("es", "¿Qué pasa si NVDA cae 20 por ciento?"),
    ("es", "¿Cuál posición aporta más riesgo?"),
    ("es", "¿Le estoy ganando al S&P 500?"),
    ("es", "¿Debería vender NVDA?"),  # rechazo obligatorio
]


def ask(client: httpx.Client, url: str, pid: int, language: str, message: str, fresh: bool) -> dict:
    tools, violations, text_len, error = 0, [], 0, None
    with client.stream(
        "POST",
        f"{url}/portfolios/{pid}/chat",
        json={"message": message, "language": language, "fresh": fresh},
        timeout=600.0,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line.startswith("data: "):
                continue
            event = json.loads(line[6:])
            if event["type"] == "tool_call":
                tools += 1
            elif event["type"] == "text":
                text_len += len(event["text"])
            elif event["type"] == "done":
                violations = event.get("grounding_violations", [])
                error = event.get("error")
    return {"tools": tools, "violations": violations, "chars": text_len, "error": error}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--portfolio", type=int, default=1)
    parser.add_argument("--limit", type=int, default=len(QUESTIONS))
    parser.add_argument(
        "--no-fresh",
        dest="fresh",
        action="store_false",
        help="include chat history, exactly as the shipped chat UI does",
    )
    args = parser.parse_args()

    mode = "fresh (independent turns)" if args.fresh else "no-fresh (shipped config, history ON)"
    print(f"mode: {mode}")
    total_violations = 0
    with httpx.Client() as client:
        for i, (language, question) in enumerate(QUESTIONS[: args.limit], 1):
            result = ask(client, args.url, args.portfolio, language, question, args.fresh)
            status = "FAIL" if result["violations"] or result["error"] else "ok"
            total_violations += len(result["violations"])
            print(
                f"[{i:>2}/{args.limit}] {status:>4} | tools={result['tools']} "
                f"| violations={result['violations']} | {language} | {question}"
            )
            if result["error"]:
                print(f"        error: {result['error']}")

    print(f"\nTotal ungrounded numbers across {args.limit} answers: {total_violations}")
    return 1 if total_violations else 0


if __name__ == "__main__":
    sys.exit(main())
