import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import enChat from "./locales/en/chat.json";
import enCommon from "./locales/en/common.json";
import enDashboard from "./locales/en/dashboard.json";
import enDigest from "./locales/en/digest.json";
import enScenarios from "./locales/en/scenarios.json";
import esChat from "./locales/es/chat.json";
import esCommon from "./locales/es/common.json";
import esDashboard from "./locales/es/dashboard.json";
import esDigest from "./locales/es/digest.json";
import esScenarios from "./locales/es/scenarios.json";

// Hard rule (CLAUDE.md): every user-facing string goes through i18next,
// with en + es shipped in the same commit.
void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { common: enCommon, dashboard: enDashboard, chat: enChat, scenarios: enScenarios, digest: enDigest },
      es: { common: esCommon, dashboard: esDashboard, chat: esChat, scenarios: esScenarios, digest: esDigest },
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
