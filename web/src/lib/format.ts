/** Locale-aware number formatting (en-US / es-MX conventions via Intl). */

import i18n from "../i18n";

const locale = () => (i18n.resolvedLanguage === "es" ? "es-MX" : "en-US");

export const fmtCurrency = (v: number): string =>
  new Intl.NumberFormat(locale(), { style: "currency", currency: "USD" }).format(v);

export const fmtPct = (v: number, digits = 2): string =>
  new Intl.NumberFormat(locale(), {
    style: "percent",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(v);

export const fmtNum = (v: number, digits = 2): string =>
  new Intl.NumberFormat(locale(), {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(v);
