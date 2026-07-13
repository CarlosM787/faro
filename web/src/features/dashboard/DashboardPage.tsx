import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { IconAlertTriangle, IconInfo } from "../../components/icons";
import { api, type FullMetrics, type PortfolioOut, type Series } from "../../lib/api";
import { fmtCurrency, fmtDate, fmtNum, fmtPct } from "../../lib/format";
import { PortfolioEditor } from "../portfolio/PortfolioEditor";
import {
  AllocationDonut,
  CorrelationHeatmap,
  DrawdownChart,
  PerformanceChart,
} from "./charts";
import { MetricCard } from "./MetricCard";

function Skeleton({ className }: { className: string }) {
  return <div className={`animate-pulse rounded-xl border border-navy-800 bg-navy-900 ${className}`} />;
}

/** Mirrors the real layout so the page doesn't jump when data lands. */
function DashboardSkeleton({ header = true }: { header?: boolean }) {
  return (
    <div className="space-y-6" aria-hidden>
      {header && <Skeleton className="h-12 w-64" />}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Skeleton className="h-72 lg:col-span-2" />
        <Skeleton className="h-72" />
      </div>
    </div>
  );
}

function Panel({ title, hint, children }: { title: string; hint?: string; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-navy-800 bg-navy-900 p-5">
      <div className="mb-3">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted">{title}</h2>
        {hint && <p className="text-[11px] text-muted/70">{hint}</p>}
      </div>
      {children}
    </section>
  );
}

export function DashboardPage() {
  const { t } = useTranslation("dashboard");
  const [portfolio, setPortfolio] = useState<PortfolioOut | null>(null);
  const [metrics, setMetrics] = useState<FullMetrics | null>(null);
  const [perf, setPerf] = useState<Series | null>(null);
  const [drawdown, setDrawdown] = useState<Series | null>(null);
  const [error, setError] = useState(false);
  const [editing, setEditing] = useState(false);

  const load = useCallback(async () => {
    try {
      setError(false);
      const portfolios = await api.listPortfolios();
      const first = portfolios[0];
      if (!first) return;
      setPortfolio(first);
      if (first.positions.length === 0) {
        setMetrics(null);
        return;
      }
      const [m, p, d] = await Promise.all([
        api.getMetrics(first.id),
        api.getSeries(first.id, "benchmark"),
        api.getSeries(first.id, "drawdown"),
      ]);
      setMetrics(m);
      setPerf(p);
      setDrawdown(d);
    } catch {
      setError(true);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (error)
    return (
      <div className="mx-auto mt-16 max-w-md rounded-xl border border-loss/40 bg-loss/5 p-6 text-center">
        <IconAlertTriangle className="mx-auto h-6 w-6 text-loss" />
        <p className="mt-3 text-sm text-ink">{t("state.error")}</p>
        <button
          onClick={() => void load()}
          className="mt-4 rounded-lg border border-navy-800 px-4 py-2 text-sm text-ink hover:bg-navy-800"
        >
          {t("state.retry")}
        </button>
      </div>
    );
  if (!portfolio) return <DashboardSkeleton />;

  return (
    <div className="space-y-6">
      {/* header */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">{portfolio.name}</h1>
          {metrics && (
            <p className="text-xs text-muted">
              {t("header.asOf", { date: fmtDate(metrics.as_of) })}
            </p>
          )}
        </div>
        <button
          onClick={() => setEditing(true)}
          className="rounded-lg border border-navy-800 px-4 py-2 text-sm text-ink hover:bg-navy-800"
        >
          {t("table.edit")}
        </button>
      </div>

      {metrics?.stale && (
        <div className="flex items-start gap-2.5 rounded-lg border border-beam/40 bg-beam/10 px-4 py-2.5 text-sm text-beam">
          <IconAlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>
            {t("header.staleData", { date: fmtDate(metrics.as_of) })}
          </span>
        </div>
      )}
      {metrics?.data_sources?.includes("stooq") && (
        <div className="flex items-start gap-2.5 rounded-lg border border-beam/40 bg-beam/10 px-4 py-2.5 text-sm text-beam">
          <IconAlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{t("header.fallbackSource")}</span>
        </div>
      )}

      {!metrics ? (
        portfolio.positions.length === 0 ? (
          <div className="mx-auto mt-10 max-w-md rounded-xl border border-navy-800 bg-navy-900 p-8 text-center">
            <p className="text-sm text-muted">{t("state.empty")}</p>
            <button
              onClick={() => setEditing(true)}
              className="mt-4 rounded-lg bg-beam px-5 py-2.5 text-sm font-semibold text-navy-950"
            >
              {t("state.emptyCta")}
            </button>
          </div>
        ) : (
          <DashboardSkeleton header={false} />
        )
      ) : (
        <>
          {/* headline stats */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <MetricCard label={t("header.totalValue")} value={fmtCurrency(metrics.value)} info={t("header.totalValueInfo")} />
            <MetricCard
              label={t("header.totalPnl")}
              value={`${fmtCurrency(metrics.pnl)} (${fmtPct(metrics.pnl_pct)})`}
              info={t("header.totalPnlInfo")}
              tone={metrics.pnl >= 0 ? "good" : "bad"}
            />
            <MetricCard
              label={t("header.dayChange")}
              value={fmtPct(metrics.day_change_pct)}
              info={t("header.dayChangeInfo")}
              tone={metrics.day_change_pct >= 0 ? "good" : "bad"}
            />
          </div>

          {/* risk metric cards */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard label={t("cards.sharpe")} value={fmtNum(metrics.sharpe)} info={t("cards.sharpeInfo")} />
            <MetricCard label={t("cards.var")} value={fmtPct(metrics.var_hist_95)} info={t("cards.varInfo")} />
            <MetricCard
              label={t("cards.beta", { benchmark: metrics.benchmark })}
              value={fmtNum(metrics.beta)}
              info={t("cards.betaInfo")}
            />
            <MetricCard
              label={t("cards.maxDrawdown")}
              value={fmtPct(metrics.max_drawdown)}
              info={t("cards.maxDrawdownInfo")}
              tone="bad"
            />
          </div>

          {/* charts row 1 */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <Panel title={t("charts.performance", { benchmark: metrics.benchmark })} hint={t("charts.performanceHint")}>
                {perf && (
                  <PerformanceChart series={perf} benchmark={metrics.benchmark} portfolioLabel={t("charts.portfolio")} />
                )}
              </Panel>
            </div>
            <Panel title={t("charts.allocation")}>
              <AllocationDonut metrics={metrics} />
            </Panel>
          </div>

          {/* charts row 2 */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Panel title={t("charts.drawdown")}>{drawdown && <DrawdownChart series={drawdown} />}</Panel>
            <Panel title={t("charts.correlation")} hint={t("charts.correlationHint")}>
              <CorrelationHeatmap metrics={metrics} />
            </Panel>
          </div>

          {/* positions table */}
          <Panel title={t("table.title")}>
            <div className="overflow-x-auto">
              <table className="tabular w-full text-sm">
                <thead className="text-left text-xs uppercase tracking-wider text-muted">
                  <tr>
                    <th className="pb-2">{t("table.ticker")}</th>
                    <th className="pb-2 text-right">{t("table.shares")}</th>
                    <th className="pb-2 text-right">{t("table.price")}</th>
                    <th className="pb-2 text-right">{t("table.value")}</th>
                    <th className="pb-2 text-right">{t("table.pnl")}</th>
                    <th className="pb-2 text-right">{t("table.weight")}</th>
                    <th className="pb-2 text-right">{t("table.beta")}</th>
                    <th className="pb-2 text-right" title={t("table.riskInfo")}>
                      <span className="inline-flex cursor-help items-center gap-1">
                        {t("table.risk")} <IconInfo className="h-3 w-3 text-muted/70" />
                      </span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {metrics.positions.map((p) => (
                    <tr key={p.ticker} className="border-t border-navy-800">
                      <td className="py-2 font-semibold">{p.ticker}</td>
                      <td className="text-right">{fmtNum(p.shares, 0)}</td>
                      <td className="text-right">{fmtCurrency(p.last_price)}</td>
                      <td className="text-right">{fmtCurrency(p.value)}</td>
                      <td className={`text-right ${p.pnl >= 0 ? "text-teal" : "text-loss"}`}>
                        {fmtCurrency(p.pnl)} ({fmtPct(p.pnl_pct)})
                      </td>
                      <td className="text-right">{fmtPct(p.weight)}</td>
                      <td className="text-right">{fmtNum(p.beta)}</td>
                      <td className="text-right">{fmtPct(p.risk_contribution)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        </>
      )}

      {editing && (
        <PortfolioEditor
          portfolio={portfolio}
          onClose={() => setEditing(false)}
          onChanged={() => void load()}
        />
      )}
    </div>
  );
}
