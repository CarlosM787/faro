/** Typed client for the Faro API (same-origin /api, proxied in dev & Docker). */

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!resp.ok) throw new Error(`${resp.status} ${await resp.text()}`);
  return resp.status === 204 ? (undefined as T) : ((await resp.json()) as T);
}

// --- types mirroring the FastAPI response models ---

export interface PositionOut {
  id: number;
  ticker: string;
  shares: number;
  cost_basis: number;
  purchase_date: string;
}

export interface PortfolioOut {
  id: number;
  name: string;
  base_currency: string;
  positions: PositionOut[];
}

export interface PositionMetrics {
  ticker: string;
  shares: number;
  last_price: number;
  value: number;
  cost: number;
  pnl: number;
  pnl_pct: number;
  weight: number;
  beta: number;
  risk_contribution: number;
}

export interface FullMetrics {
  value: number;
  cost: number;
  pnl: number;
  pnl_pct: number;
  day_change_pct: number;
  annual_return: number;
  annual_volatility: number;
  sharpe: number;
  sortino: number;
  benchmark: string;
  beta: number;
  alpha: number;
  var_hist_95: number;
  var_hist_99: number;
  var_param_95: number;
  var_param_99: number;
  cvar_95: number;
  max_drawdown: number;
  hhi: number;
  top_weight: number;
  positions: PositionMetrics[];
  correlation_tickers: string[];
  correlation: number[][];
  risk_free_rate: number;
  window_start: string;
  window_end: string;
  as_of: string;
  stale: boolean;
}

export interface Series {
  dates: string[];
  portfolio: number[];
  benchmark?: number[] | null;
}

export interface PositionIn {
  ticker: string;
  shares: number;
  cost_basis: number;
  purchase_date: string;
}

// --- endpoints ---

export const api = {
  listPortfolios: () => request<PortfolioOut[]>("/portfolios"),
  getPortfolio: (id: number) => request<PortfolioOut>(`/portfolios/${id}`),
  createPortfolio: (name: string) =>
    request<PortfolioOut>("/portfolios", { method: "POST", body: JSON.stringify({ name }) }),
  getMetrics: (id: number) => request<FullMetrics>(`/portfolios/${id}/metrics`),
  getSeries: (id: number, kind: "value" | "drawdown" | "benchmark") =>
    request<Series>(`/portfolios/${id}/series?kind=${kind}`),
  addPosition: (id: number, body: PositionIn) =>
    request<PositionOut>(`/portfolios/${id}/positions`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  updatePosition: (id: number, posId: number, body: PositionIn) =>
    request<PositionOut>(`/portfolios/${id}/positions/${posId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  deletePosition: (id: number, posId: number) =>
    request<void>(`/portfolios/${id}/positions/${posId}`, { method: "DELETE" }),
};
