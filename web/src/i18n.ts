import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import enCommon from "./locales/en/common.json";
import esCommon from "./locales/es/common.json";

// Hard rule (CLAUDE.md): every user-facing string goes through i18next,
// with en + es shipped in the same commit.
void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { common: enCommon },
      es: { common: esCommon },
    },
    defaultNS: "common",
    fallbackLng: "en",
    supportedLngs: ["en", "es"],
    detection: {
      order: ["localStorage", "navigator"],
      lookupLocalStorage: "faro-lang",
      caches: ["localStorage"],
    },
    interpolation: { escapeValue: false },
  });

export default i18n;
