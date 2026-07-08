import { useTranslation } from "react-i18next";

/** One-tap persisted EN⇄ES toggle — same pill style as the marketing site. */
export function LangToggle() {
  const { i18n } = useTranslation();
  const lang = i18n.resolvedLanguage ?? "en";
  return (
    <div className="inline-flex overflow-hidden rounded-full border border-navy-800" role="group" aria-label="Language">
      {(["en", "es"] as const).map((l) => (
        <button
          key={l}
          type="button"
          onClick={() => void i18n.changeLanguage(l)}
          className={`px-4 py-1.5 text-xs font-semibold uppercase transition-colors ${
            lang === l ? "bg-beam text-navy-950" : "text-muted hover:text-ink"
          }`}
        >
          {l}
        </button>
      ))}
    </div>
  );
}
