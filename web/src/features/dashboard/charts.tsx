import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { FullMetrics, Series } from "../../lib/api";
import { fmtPct } from "../../lib/format";

const BEAM = "#FFB020";
const MUTED = "#8B98AC";
const GRID = "#1E2A44";
const DONUT = ["#FFB020", "#2DD4BF", "#7C9EF5", "#F87171", "#C084FC", "#4ADE80", "#F472B6", "#94A3B8"];

const axisProps = { stroke: MUTED, fontSize: 11, tickLine: false, axisLine: { stroke: GRID } };
const tooltipStyle = {
  backgroundColor: "#0B1220",
  border: `1px solid ${GRID}`,
  borderRadius: 8,
  fontSize: 12,
};

export function PerformanceChart({ series, benchmark, portfolioLabel }: {
  series: Series;
  benchmark: string;
  portfolioLabel: string;
}) {
  const data = series.dates.map((d, i) => ({
    date: d,
    portfolio: series.portfolio[i],
    benchmark: series.benchmark?.[i] ?? null,
  }));
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="date" {...axisProps} minTickGap={60} />
        <YAxis {...axisProps} domain={["auto", "auto"]} />
        <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: MUTED }} />
        <Line type="monotone" dataKey="portfolio" name={portfolioLabel} stroke={BEAM} dot={false} strokeWidth={2} />
        <Line type="monotone" dataKey="benchmark" name={benchmark} stroke={MUTED} dot={false} strokeWidth={1.5} strokeDasharray="5 3" />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function DrawdownChart({ series }: { series: Series }) {
  const data = series.dates.map((d, i) => ({ date: d, dd: series.portfolio[i] }));
  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="date" {...axisProps} minTickGap={60} />
        <YAxis {...axisProps} tickFormatter={(v: number) => fmtPct(v, 0)} />
        <Tooltip
          contentStyle={tooltipStyle}
          labelStyle={{ color: MUTED }}
          formatter={(v) => fmtPct(Number(v))}
        />
        <Area type="monotone" dataKey="dd" stroke="#F87171" fill="#F87171" fillOpacity={0.25} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function AllocationDonut({ metrics }: { metrics: FullMetrics }) {
  const data = metrics.positions.map((p) => ({ name: p.ticker, value: p.weight }));
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2} strokeWidth={0}>
          {data.map((_, i) => (
            <Cell key={i} fill={DONUT[i % DONUT.length]} />
          ))}
        </Pie>
        <Tooltip contentStyle={tooltipStyle} formatter={(v) => fmtPct(Number(v))} />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function CorrelationHeatmap({ metrics }: { metrics: FullMetrics }) {
  const tickers = metrics.correlation_tickers;
  const cell = (v: number) => {
    // teal for positive, red for negative, intensity ∝ |ρ|
    const alpha = Math.min(Math.abs(v), 1);
    return v >= 0 ? `rgba(45, 212, 191, ${alpha * 0.85})` : `rgba(248, 113, 113, ${alpha * 0.85})`;
  };
  return (
    <div className="overflow-x-auto">
      <table className="tabular text-[11px]">
        <thead>
          <tr>
            <th />
            {tickers.map((t) => (
              <th key={t} className="px-1 pb-1 font-semibold text-muted">{t}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tickers.map((row, i) => (
            <tr key={row}>
              <td className="pr-2 font-semibold text-muted">{row}</td>
              {tickers.map((col, j) => (
                <td key={col} className="p-0.5">
                  <div
                    className="flex h-9 w-12 items-center justify-center rounded text-navy-950"
                    style={{ backgroundColor: cell(metrics.correlation[i][j]) }}
                    title={`${row}·${col}: ${metrics.correlation[i][j].toFixed(2)}`}
                  >
                    {metrics.correlation[i][j].toFixed(2)}
                  </div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
