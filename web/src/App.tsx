import { Route, Routes } from "react-router-dom";

import { Disclaimer } from "./components/Disclaimer";
import { Sidebar } from "./components/Sidebar";
import { ChatPage } from "./features/chat/ChatPage";
import { DashboardPage } from "./features/dashboard/DashboardPage";
import { DigestPage } from "./features/digest/DigestPage";
import { ScenariosPage } from "./features/scenarios/ScenariosPage";
import { SettingsPage } from "./features/settings/SettingsPage";

export default function App() {
  return (
    <div className="flex min-h-screen flex-col lg:flex-row">
      <Sidebar />
      <div className="flex min-h-screen flex-1 flex-col">
        <main className="flex-1 p-4 sm:p-6 lg:p-10">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/scenarios" element={<ScenariosPage />} />
            <Route path="/digest" element={<DigestPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
        <Disclaimer />
      </div>
    </div>
  );
}
