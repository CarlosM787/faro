import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { api, type PortfolioOut } from "../../lib/api";
import { fmtCurrency, fmtPct } from "../../lib/format";

interface ShockRow {
  ticker: string;
  pct: number;
}

interface ScenarioResult {
  value_before: number;
  value_after: number;
  impact: number;
  impact_pct: number;
  positions: { ticker: string; value_before: number; value_after: number; impact: number }[];
}

export function ScenariosPage() {
  const { t } = useTranslation("scenarios");
  const [portfolio, setPortfolio] = useState<PortfolioOut | null>(null);
  const [shocks, setShocks] = useState<ShockRow[]>([{ ticker: "*", pct: -10 }]);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    void api.listPortfolios().then((ps) => setPortfolio(ps[0] ?? null));
  }, []);

  const tickers = [...new Set(portfolio?.positions.map((p) => p.ticker) ?? [])].sort();

  const run = async () => {
    if (!portfolio || shocks.length === 0) return;
    setBusy(true);
    setError(false);
    try {
      const resp = await fetch(`/api/portfolios/${portfolio.id}/scenarios`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ shocks }),
      });
      if (!resp.ok) throw new Error(`${resp.status}`);
      setResult((await resp.json()) as ScenarioResult);
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  };

  const maxImpact = Math.max(1, ...(result?.positions.map((p) => Math.abs(p.impact)) ?? []));
  const copilotPrompt = shocks
    .map((s) => `${s.ticker === "*" ? "market" : s.ticker} ${s.pct}%`)
    .join(", ");

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t("title")}</h1>
        <p className="text-sm text-muted">{t("subtitle")}</p>
      </div>

      {/* shock builder */}
      <div className="space-y-3 rounded-xl border border-navy-800 bg-navy-900 p-5">
        {shocks.map((shock, i) => (
          <div key={i} className="flex flex-wrap items-center gap-3">
            <select
              value={shock.ticker}
              onChange={(e) =>
                setShocks(shocks.map((s, j) => (j === i ? { ...s, ticker: e.target.value } : s)))
              }
              className="rounded-lg border border-navy-800 bg-navy-950 px-3 py-2 text-sm"
            >
              <option value="*">{t("market")}</option>
              {tickers.map((tk) => (
                <option key={tk} value={tk}>
                  {tk}
                </option>
              ))}
            </select>
            <label className="flex items-center gap-2 text-sm text-muted">
              {t("shockLabel")}
              <input
                type="range"
                min={-50}
                max={50}
                step={1}
                value={shock.pct}
                onChange={(e) =>
                  setShocks(
                    shocks.map((s, j) => (j === i ? { ...s, pct: Number(e.target.value) } : s)),
                  )
                }
                className="w-40 accent-beam"
              />
              <span className={`tabular w-14 font-semibold ${shock.pct < 0 ? "text-loss" : "text-teal"}`}>
                {shock.pct > 0 ? "+" : ""}
                {shock.pct}%
              </span>
            </label>
            {shocks.length > 1 && (
              <button
                onClick={() => setShocks(shocks.filter((_, j) => j !== i))}
                className="text-xs text-muted hover:text-loss"
              >
                {t("remove")} ✕
              </button>
            )}
          </div>
        ))}
        <div className="flex gap-3 pt-1">
          <button
            onClick={() => setShocks([...shocks, { ticker: tickers[0] ?? "*", pct: -20 }])}
            className="rounded-lg border border-navy-800 px-4 py-2 text-sm text-muted hover:text-ink"
          >
            + {t("addShock")}
          </button>
          <button
            onClick={() => void run()}
            disabled={busy || !portfolio}
            className="rounded-lg bg-beam px-6 py-2 text-sm font-semibold text-navy-950 disabled:opacity-40"
          >
            {busy ? t("running") : t("run")}
          </button>
        </div>
      </div>

      {error && <p className="text-sm text-loss">{t("error")}</p>}

      {result ? (
        <>
          {/* headline result */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {(
              [
                ["before", fmtCurrency(result.value_before), "text-ink"],
                ["after", fmtCurrency(result.value_after), "text-ink"],
                [
                  "impact",
                  `${fmtCurrency(result.impact)} (${fmtPct(result.impact_pct)})`,
                  result.impact < 0 ? "text-loss" : "text-teal",
                ],
              ] as const
            ).map(([key, value, tone]) => (
              <div key={key} className="rounded-xl border border-navy-800 bg-navy-900 p-5">
                <div className="text-xs font-semibold uppercase tracking-wider text-muted">
                  {t(key)}
                </div>
                <div className={`tabular mt-2 font-display text-2xl font-bold ${tone}`}>{value}</div>
              </div>
            ))}
          </div>

          {/* per-position impact bars */}
          <div className="rounded-xl border border-navy-800 bg-navy-900 p-5">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted">
              {t("perPosition")}
            </h2>
            <div className="space-y-2">
              {result.positions.map((p) => (
                <div key={p.ticker} className="flex items-center gap-3 text-sm">
                  <span className="w-12 font-semibold">{p.ticker}</span>
                  <div className="h-5 flex-1 rounded bg-navy-950">
                    <div
                      className={`h-5 rounded ${p.impact < 0 ? "bg-loss/70" : "bg-teal/70"}`}
                      style={{ width: `${(Math.abs(p.impact) / maxImpact) * 100}%` }}
                    />
                  </div>
                  <span className={`tabular w-28 text-right ${p.impact < 0 ? "text-loss" : p.impact > 0 ? "text-teal" : "text-muted"}`}>
                    {fmtCurrency(p.impact)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <Link to="/chat" className="inline-block text-sm text-teal hover:underline">
            💬 {t("askCopilot")} ({copilotPrompt})
          </Link>
        </>
      ) : (
        !error && <p className="text-sm text-muted">{t("empty")}</p>
      )}
    </div>
  );
}
