import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { IconAlertTriangle, IconCheckCircle, IconFileText } from "../../components/icons";
import { api, type PortfolioOut } from "../../lib/api";

interface DigestResult {
  markdown: string;
  provider: string;
  grounding_violations?: number[];
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
          {(result.grounding_violations?.length ?? 0) > 0 ? (
            <div
              className="mt-4 flex items-start gap-2 rounded-lg border border-beam/40 bg-beam/10 px-3 py-2 text-xs text-beam"
              title={result.grounding_violations?.join(", ")}
            >
              <IconAlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              <span>{t("groundingWarning", { count: result.grounding_violations?.length })}</span>
            </div>
          ) : (
            result.grounding_violations &&
            /\d/.test(result.markdown) && (
              <p className="mt-4 flex items-center gap-1.5 text-[11px] text-teal/80">
                <IconCheckCircle className="h-3 w-3 shrink-0" />
                {t("grounded")}
              </p>
            )
          )}
          <p className="mt-4 text-[11px] text-muted/70">
            {t("provider", { name: result.provider })}
          </p>
        </article>
      ) : (
        !failed &&
        !busy && (
          <div className="rounded-xl border border-dashed border-navy-800 p-8 text-center">
            <IconFileText className="mx-auto h-6 w-6 text-muted/60" />
            <p className="mt-3 text-sm text-muted">{t("empty")}</p>
            <p className="mx-auto mt-1 max-w-sm text-xs text-muted/70">{t("emptyHint")}</p>
          </div>
        )
      )}
    </div>
  );
}
