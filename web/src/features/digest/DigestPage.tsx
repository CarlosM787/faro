import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { api, type PortfolioOut } from "../../lib/api";

interface DigestResult {
  markdown: string;
  provider: string;
  error?: string | null;
}

/** Minimal markdown rendering: headings + bold + bullets (no extra deps). */
function renderLine(line: string, i: number) {
  const bold = (s: string) =>
    s.split(/\*\*(.+?)\*\*/g).map((part, j) => (j % 2 ? <strong key={j}>{part}</strong> : part));
  if (line.startsWith("### ") || line.startsWith("## ") || line.startsWith("# "))
    return (
      <h3 key={i} className="mt-4 font-display text-base font-bold text-beam">
        {line.replace(/^#+\s*/, "")}
      </h3>
    );
  if (/^\s*[-*•]\s+/.test(line))
    return (
      <li key={i} className="ml-5 list-disc text-sm leading-relaxed">
        {bold(line.replace(/^\s*[-*•]\s+/, ""))}
      </li>
    );
  if (!line.trim()) return <div key={i} className="h-2" />;
  return (
    <p key={i} className="text-sm leading-relaxed">
      {bold(line)}
    </p>
  );
}

export function DigestPage() {
  const { t, i18n } = useTranslation("digest");
  const [portfolio, setPortfolio] = useState<PortfolioOut | null>(null);
  const [result, setResult] = useState<DigestResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    void api.listPortfolios().then((ps) => setPortfolio(ps[0] ?? null));
  }, []);

  const generate = async () => {
    if (!portfolio || busy) return;
    setBusy(true);
    setFailed(false);
    try {
      const resp = await fetch(`/api/portfolios/${portfolio.id}/digest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language: i18n.resolvedLanguage ?? "en" }),
      });
      if (!resp.ok) throw new Error(`${resp.status}`);
      const data = (await resp.json()) as DigestResult;
      if (data.error || !data.markdown) throw new Error(data.error ?? "empty");
      setResult(data);
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t("title")}</h1>
        <p className="text-sm text-muted">{t("subtitle")}</p>
      </div>

      <button
        onClick={() => void generate()}
        disabled={busy || !portfolio}
        className="rounded-lg bg-beam px-6 py-3 text-sm font-semibold text-navy-950 disabled:opacity-40"
      >
        {busy ? t("generating") : t("generate")}
      </button>

      {failed && <p className="text-sm text-loss">{t("error")}</p>}

      {result ? (
        <article className="rounded-xl border border-navy-800 bg-navy-900 p-6">
          {result.markdown.split("\n").map(renderLine)}
          <p className="mt-4 text-[11px] text-muted/70">
            {t("provider", { name: result.provider })}
          </p>
        </article>
      ) : (
        !failed && !busy && <p className="text-sm text-muted">{t("empty")}</p>
      )}
    </div>
  );
}
