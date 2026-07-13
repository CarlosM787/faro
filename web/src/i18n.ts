import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import { LANGUAGE_CODES } from "./languages";
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
import deChat from "./locales/de/chat.json";
import deCommon from "./locales/de/common.json";
import deDashboard from "./locales/de/dashboard.json";
import deDigest from "./locales/de/digest.json";
import deScenarios from "./locales/de/scenarios.json";
import frChat from "./locales/fr/chat.json";
import frCommon from "./locales/fr/common.json";
import frDashboard from "./locales/fr/dashboard.json";
import frDigest from "./locales/fr/digest.json";
import frScenarios from "./locales/fr/scenarios.json";
import ptChat from "./locales/pt/chat.json";
import ptCommon from "./locales/pt/common.json";
import ptDashboard from "./locales/pt/dashboard.json";
import ptDigest from "./locales/pt/digest.json";
import ptScenarios from "./locales/pt/scenarios.json";

// Hard rule (CLAUDE.md): every user-facing string goes through i18next, with
// en + es shipped in the same commit. pt/fr/de share the same key set so the
// picker can scale past the maintained pair; CI enforces parity across all.
void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { common: enCommon, dashboard: enDashboard, chat: enChat, scenarios: enScenarios, digest: enDigest },
      es: { common: esCommon, dashboard: esDashboard, chat: esChat, scenarios: esScenarios, digest: esDigest },
      pt: { common: ptCommon, dashboard: ptDashboard, chat: ptChat, scenarios: ptScenarios, digest: ptDigest },
      fr: { common: frCommon, dashboard: frDashboard, chat: frChat, scenarios: frScenarios, digest: frDigest },
      de: { common: deCommon, dashboard: deDashboard, chat: deChat, scenarios: deScenarios, digest: deDigest },
    },
    defaultNS: "common",
    fallbackLng: "en",
    supportedLngs: LANGUAGE_CODES,
    detection: {
      order: ["localStorage", "navigator"],
      lookupLocalStorage: "faro-lang",
      caches: ["localStorage"],
    },
    interpolation: { escapeValue: false },
  });

export default i18n;
