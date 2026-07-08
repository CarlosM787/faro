import { useTranslation } from "react-i18next";

import { LangToggle } from "../../components/LangToggle";

const LEGAL = [
  { key: "settings.privacy", file: "Faro-Privacy-Policy.pdf" },
  { key: "settings.terms", file: "Faro-Terms-of-Use.pdf" },
  { key: "settings.disclaimer", file: "Faro-Investment-Disclaimer.pdf" },
] as const;

export function SettingsPage() {
  const { t } = useTranslation();
  return (
    <div className="max-w-xl">
      <h1 className="text-2xl font-bold">{t("settings.title")}</h1>

      <section className="mt-8 rounded-xl border border-navy-800 bg-navy-900 p-6">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-muted">
          {t("settings.language")}
        </h2>
        <LangToggle />
      </section>

      <section className="mt-6 rounded-xl border border-navy-800 bg-navy-900 p-6">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-muted">
          {t("settings.legal")}
        </h2>
        <ul className="space-y-2 text-sm">
          {LEGAL.map((d) => (
            <li key={d.file}>
              <a className="text-teal hover:underline" href={`/legal/${d.file}`} target="_blank" rel="noreferrer">
                {t(d.key)}
              </a>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
