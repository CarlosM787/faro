import { useTranslation } from "react-i18next";
import { Route, Routes } from "react-router-dom";

import { Disclaimer } from "./components/Disclaimer";
import { Sidebar } from "./components/Sidebar";
import { SettingsPage } from "./features/settings/SettingsPage";

/** Placeholder page used until each feature milestone lands. */
function Placeholder({ titleKey }: { titleKey: string }) {
  const { t } = useTranslation();
  return (
    <div>
      <h1 className="text-2xl font-bold">{t(titleKey)}</h1>
      <p className="mt-3 text-muted">{t("common.comingSoon")}</p>
    </div>
  );
}

export default function App() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex min-h-screen flex-1 flex-col">
        <main className="flex-1 p-6 lg:p-10">
          <Routes>
            <Route path="/" element={<Placeholder titleKey="pages.dashboardTitle" />} />
            <Route path="/chat" element={<Placeholder titleKey="pages.chatTitle" />} />
            <Route path="/scenarios" element={<Placeholder titleKey="pages.scenariosTitle" />} />
            <Route path="/digest" element={<Placeholder titleKey="pages.digestTitle" />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
        <Disclaimer />
      </div>
    </div>
  );
}
