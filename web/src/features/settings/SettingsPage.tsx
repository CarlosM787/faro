import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { IconArrowUpRight } from "../../components/icons";
import { LangToggle } from "../../components/LangToggle";

const LEGAL = [
  { key: "settings.privacy", file: "Faro-Privacy-Policy.pdf" },
  { key: "settings.terms", file: "Faro-Terms-of-Use.pdf" },
  { key: "settings.disclaimer", file: "Faro-Investment-Disclaimer.pdf" },
] as const;

const LINKS = [
  { key: "settings.source", href: "https://github.com/CarlosM787/faro" },
  { key: "settings.website", href: "https://faroquant.com" },
] as const;

interface Health {
  version: string;
  llm_provider: "anthropic" | "ollama";
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mt-6 rounded-xl border border-navy-800 bg-navy-900 p-6">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-muted">{title}</h2>
      {children}
    </section>
  );
}

export function SettingsPage() {
  const { t } = useTranslation();
  const [health, setHealth] = useState<Health | null>(null);

  useEffect(() => {
    void fetch("/api/health")
      .then((r) => r.json())
      .then((h: Health) => setHealth(h))
      .catch(() => setHealth(null));
  }, []);

  return (
    <div className="max-w-xl">
      <h1 className="text-2xl font-bold">{t("settings.title")}</h1>

      <Section title={t("settings.language")}>
        <LangToggle />
      </Section>

      <Section title={t("settings.provider")}>
        {health ? (
          <>
            <p className="text-sm text-ink">
              {health.llm_provider === "anthropic"
                ? t("settings.providerAnthropic")
                : t("settings.providerOllama")}
            </p>
            <p className="mt-1 text-xs text-muted">{t("settings.providerHint")}</p>
          </>
        ) : (
          <p className="text-sm text-muted">{t("common.loading")}</p>
        )}
      </Section>

      <Section title={t("settings.legal")}>
        <ul className="space-y-2 text-sm">
          {LEGAL.map((d) => (
            <li key={d.file}>
              <a
                className="inline-flex items-center gap-1.5 text-teal hover:underline"
                href={`/legal/${d.file}`}
                target="_blank"
                rel="noreferrer"
              >
                {t(d.key)} <IconArrowUpRight className="h-3.5 w-3.5" />
              </a>
            </li>
          ))}
        </ul>
      </Section>

      <Section title={t("settings.about")}>
        <p className="text-sm leading-relaxed text-muted">{t("settings.aboutText")}</p>
        <ul className="mt-3 space-y-2 text-sm">
          {LINKS.map((l) => (
            <li key={l.href}>
              <a
                className="inline-flex items-center gap-1.5 text-teal hover:underline"
                href={l.href}
                target="_blank"
                rel="noreferrer"
              >
                {t(l.key)} <IconArrowUpRight className="h-3.5 w-3.5" />
              </a>
            </li>
          ))}
        </ul>
        {health && <p className="mt-3 text-xs text-muted/70">{t("settings.version", { version: health.version })}</p>}
      </Section>
    </div>
  );
}
