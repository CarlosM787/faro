import { useTranslation } from "react-i18next";

/** Persistent compliance footer — required on every screen (PRD guardrails). */
export function Disclaimer() {
  const { t } = useTranslation();
  return (
    <footer className="border-t border-navy-800 bg-navy-900 px-6 py-3 text-center text-xs text-muted">
      {t("app.disclaimer")}
    </footer>
  );
}
