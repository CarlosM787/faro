/**
 * Single source of truth for the languages Faro's UI ships in.
 *
 * `code`   — i18next language key and the value sent to the copilot/digest API.
 * `label`  — endonym (the language's own name), shown in the picker.
 * `locale` — BCP-47 tag used for Intl number/date formatting.
 *
 * English + Spanish are the maintained, hand-written pair (CLAUDE.md hard rule);
 * the others share the same key set so the i18n architecture scales past two.
 */
export interface Language {
  code: string;
  label: string;
  locale: string;
}

export const LANGUAGES: Language[] = [
  { code: "en", label: "English", locale: "en-US" },
  { code: "es", label: "Español", locale: "es-MX" },
  { code: "pt", label: "Português", locale: "pt-BR" },
  { code: "fr", label: "Français", locale: "fr-FR" },
  { code: "de", label: "Deutsch", locale: "de-DE" },
];

export const LANGUAGE_CODES = LANGUAGES.map((l) => l.code);

export const localeFor = (code: string): string =>
  LANGUAGES.find((l) => l.code === code)?.locale ?? "en-US";

export const languageFor = (code: string): Language =>
  LANGUAGES.find((l) => l.code === code) ?? LANGUAGES[0];
