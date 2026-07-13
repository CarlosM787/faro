import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { api, type PortfolioOut } from "../../lib/api";

interface ToolChip {
  name: string;
  arguments: Record<string, unknown>;
}

interface ChatTurn {
  role: "user" | "assistant";
  content: string;
  tools: ToolChip[];
  /** Numbers in the reply the grounding checker could NOT trace to a tool result. */
  violations: number[];
}

/** Parse an SSE stream of `data: {json}` lines, invoking onEvent per event. */
async function streamChat(
  portfolioId: number,
  message: string,
  language: string,
  onEvent: (e: Record<string, unknown>) => void,
): Promise<void> {
  const resp = await fetch(`/api/portfolios/${portfolioId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, language }),
  });
  if (!resp.ok || !resp.body) throw new Error(`${resp.status}`);
  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (line.startsWith("data: ")) onEvent(JSON.parse(line.slice(6)));
    }
  }
}

function ToolChipBadge({ chip, label }: { chip: ToolChip; label: string }) {
  const args = Object.entries(chip.arguments)
    .map(([k, v]) => `${k}: ${JSON.stringify(v)}`)
    .join(", ");
  return (
    <span
      className="mb-1 mr-2 inline-flex items-center gap-1 rounded-full border border-teal/40 bg-teal/10 px-3 py-1 text-[11px] text-teal"
      title={args}
    >
      📊 {label}: {chip.name}
      {args && <span className="text-teal/70">({args})</span>}
    </span>
  );
}

export function ChatPage() {
  const { t, i18n } = useTranslation("chat");
  const [portfolio, setPortfolio] = useState<PortfolioOut | null>(null);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);
  const [provider, setProvider] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    void api.listPortfolios().then((ps) => {
      const first = ps[0];
      if (!first) return;
      setPortfolio(first);
      // restore persisted history
      void fetch(`/api/portfolios/${first.id}/chat`)
        .then((r) => r.json())
        .then((rows: { role: string; content: string; tool_calls: ToolChip[] | null }[]) =>
          setTurns(
            rows.map((r) => ({
              role: r.role as "user" | "assistant",
              content: r.content,
              tools: r.tool_calls ?? [],
              violations: [],
            })),
          ),
        );
    });
    void fetch("/api/health")
      .then((r) => r.json())
      .then((h: { llm_provider: string }) => setProvider(h.llm_provider));
  }, []);

  useEffect(() => {
    // Block body is REQUIRED: in modern Chrome `scrollIntoView({behavior:"smooth"})`
    // returns a Promise. A concise-body arrow would hand that Promise back as the
    // effect's cleanup, and React would crash calling it ("not a function").
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns]);

  const send = async (text: string) => {
    if (!portfolio || busy || !text.trim()) return;
    setBusy(true);
    setFailed(false);
    setInput("");
    setTurns((prev) => [
      ...prev,
      { role: "user", content: text, tools: [], violations: [] },
      { role: "assistant", content: "", tools: [], violations: [] },
    ]);
    try {
      await streamChat(portfolio.id, text, i18n.resolvedLanguage ?? "en", (event) => {
        setTurns((prev) => {
          const next = [...prev];
          const last = { ...next[next.length - 1] };
          if (event.type === "text") last.content += event.text as string;
          if (event.type === "tool_call")
            last.tools = [
              ...last.tools,
              { name: event.name as string, arguments: event.arguments as Record<string, unknown> },
            ];
          if (event.type === "done") {
            if (event.error) setFailed(true);
            // Surface the grounding checker's findings on THIS message —
            // "unsupported numbers are detected and surfaced," literally.
            const flagged = event.grounding_violations as number[] | undefined;
            if (flagged && flagged.length > 0) last.violations = flagged;
          }
          next[next.length - 1] = last;
          return next;
        });
      });
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex h-full max-w-3xl flex-col">
      <div className="mb-4">
        <h1 className="text-2xl font-bold">{t("title")}</h1>
        <p className="text-sm text-muted">
          {t("subtitle")}
          {provider && <span className="ml-2 text-xs">· {t("provider", { name: provider })}</span>}
        </p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto pb-4">
        {turns.length === 0 && (
          <div className="flex flex-wrap gap-2">
            {(["risk", "concentration", "scenario", "benchmark"] as const).map((key) => (
              <button
                key={key}
                onClick={() => void send(t(`suggestions.${key}`))}
                className="rounded-full border border-navy-800 px-4 py-2 text-sm text-muted hover:border-beam hover:text-beam"
              >
                {t(`suggestions.${key}`)}
              </button>
            ))}
          </div>
        )}
        {turns.map((turn, i) => (
          <div key={i} className={turn.role === "user" ? "text-right" : ""}>
            {turn.tools.length > 0 && (
              <div className="mb-1">
                {turn.tools.map((chip, j) => (
                  <ToolChipBadge key={j} chip={chip} label={t("toolCall")} />
                ))}
              </div>
            )}
            <div
              className={`inline-block max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                turn.role === "user"
                  ? "bg-beam text-navy-950"
                  : "border border-navy-800 bg-navy-900 text-ink"
              }`}
            >
              {turn.content || (busy && i === turns.length - 1 ? t("thinking") : "")}
            </div>
            {turn.violations.length > 0 && (
              <p
                className="mt-1 max-w-[85%] rounded-lg border border-beam/40 bg-beam/10 px-3 py-2 text-xs text-beam"
                title={turn.violations.join(", ")}
              >
                {t("groundingWarning", { count: turn.violations.length })}
              </p>
            )}
          </div>
        ))}
        {failed && <p className="text-sm text-loss">{t("error")}</p>}
        <div ref={endRef} />
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          void send(input);
        }}
        className="mt-2 flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={t("placeholder")}
          disabled={busy}
          className="flex-1 rounded-xl border border-navy-800 bg-navy-900 px-4 py-3 text-sm outline-none focus:border-beam"
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          className="rounded-xl bg-beam px-6 py-3 text-sm font-semibold text-navy-950 disabled:opacity-40"
        >
          {t("send")}
        </button>
      </form>
      <p className="mt-2 text-center text-[11px] text-muted/70">{t("disclaimerShort")}</p>
    </div>
  );
}
