/** Locale-aware number & date formatting via Intl, driven by the active language. */

import i18n from "../i18n";
import { localeFor } from "../languages";

const locale = () => localeFor(i18n.resolvedLanguage ?? "en");

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

/** Format an ISO date/timestamp in the active locale's conventions. */
export const fmtDate = (value: string | number | Date): string =>
  new Date(value).toLocaleDateString(locale());
