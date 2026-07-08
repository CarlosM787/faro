import { useState } from "react";
import { useTranslation } from "react-i18next";

import { api, type PortfolioOut, type PositionIn } from "../../lib/api";

interface Props {
  portfolio: PortfolioOut;
  onClose: () => void;
  onChanged: () => void;
}

const EMPTY: PositionIn = { ticker: "", shares: 0, cost_basis: 0, purchase_date: "" };

/** Modal editor for positions — add, update, delete. */
export function PortfolioEditor({ portfolio, onClose, onChanged }: Props) {
  const { t } = useTranslation("dashboard");
  const [draft, setDraft] = useState<PositionIn>(EMPTY);
  const [busy, setBusy] = useState(false);

  const run = async (fn: () => Promise<unknown>) => {
    setBusy(true);
    try {
      await fn();
      onChanged();
    } finally {
      setBusy(false);
    }
  };

  const valid = draft.ticker.trim() && draft.shares > 0 && draft.cost_basis > 0 && draft.purchase_date;

  return (
    <div className="fixed inset-0 z-20 flex items-center justify-center bg-navy-950/80 p-4" role="dialog" aria-modal>
      <div className="w-full max-w-2xl rounded-2xl border border-navy-800 bg-navy-900 p-6 shadow-2xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold">{t("editor.title")} — {portfolio.name}</h2>
          <button onClick={onClose} className="rounded px-2 text-muted hover:text-ink" aria-label={t("editor.cancel")}>✕</button>
        </div>

        <table className="tabular w-full text-sm">
          <thead className="text-left text-xs uppercase tracking-wider text-muted">
            <tr>
              <th className="pb-2">{t("editor.ticker")}</th>
              <th className="pb-2">{t("editor.shares")}</th>
              <th className="pb-2">{t("editor.costBasis")}</th>
              <th className="pb-2">{t("editor.purchaseDate")}</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {portfolio.positions.map((p) => (
              <tr key={p.id} className="border-t border-navy-800">
                <td className="py-2 font-semibold">{p.ticker}</td>
                <td>{p.shares}</td>
                <td>${p.cost_basis}</td>
                <td>{p.purchase_date}</td>
                <td className="text-right">
                  <button
                    disabled={busy}
                    onClick={() => void run(() => api.deletePosition(portfolio.id, p.id))}
                    className="rounded px-2 py-1 text-xs text-loss hover:bg-navy-800"
                  >
                    {t("editor.delete")}
                  </button>
                </td>
              </tr>
            ))}
            {/* add row */}
            <tr className="border-t border-navy-800">
              <td className="py-2 pr-2">
                <input
                  className="w-20 rounded border border-navy-800 bg-navy-950 px-2 py-1 uppercase"
                  value={draft.ticker}
                  onChange={(e) => setDraft({ ...draft, ticker: e.target.value })}
                  placeholder="NVDA"
                />
              </td>
              <td className="pr-2">
                <input
                  type="number" min="0" step="any"
                  className="w-24 rounded border border-navy-800 bg-navy-950 px-2 py-1"
                  value={draft.shares || ""}
                  onChange={(e) => setDraft({ ...draft, shares: Number(e.target.value) })}
                />
              </td>
              <td className="pr-2">
                <input
                  type="number" min="0" step="any"
                  className="w-28 rounded border border-navy-800 bg-navy-950 px-2 py-1"
                  value={draft.cost_basis || ""}
                  onChange={(e) => setDraft({ ...draft, cost_basis: Number(e.target.value) })}
                />
              </td>
              <td className="pr-2">
                <input
                  type="date"
                  className="rounded border border-navy-800 bg-navy-950 px-2 py-1"
                  value={draft.purchase_date}
                  onChange={(e) => setDraft({ ...draft, purchase_date: e.target.value })}
                />
              </td>
              <td className="text-right">
                <button
                  disabled={!valid || busy}
                  onClick={() =>
                    void run(async () => {
                      await api.addPosition(portfolio.id, { ...draft, ticker: draft.ticker.toUpperCase() });
                      setDraft(EMPTY);
                    })
                  }
                  className="rounded bg-beam px-3 py-1 text-xs font-semibold text-navy-950 disabled:opacity-40"
                >
                  {t("editor.add")}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
