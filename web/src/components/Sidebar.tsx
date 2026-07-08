import { useTranslation } from "react-i18next";
import { NavLink } from "react-router-dom";

import { LangToggle } from "./LangToggle";

const links = [
  { to: "/", key: "nav.dashboard", icon: "📊" },
  { to: "/chat", key: "nav.chat", icon: "💬" },
  { to: "/scenarios", key: "nav.scenarios", icon: "⚡" },
  { to: "/digest", key: "nav.digest", icon: "📰" },
  { to: "/settings", key: "nav.settings", icon: "⚙️" },
] as const;

export function Sidebar() {
  const { t } = useTranslation();
  return (
    <aside className="flex w-56 flex-col border-r border-navy-800 bg-navy-900 p-4">
      <div className="mb-8 flex items-center gap-3 px-2">
        <img src="/logo-icon.svg" alt="" className="h-9 w-9 rounded-lg" />
        <div>
          <div className="font-display text-lg font-bold leading-tight">
            faro<span className="text-beam">quant</span>
          </div>
          <div className="text-[11px] uppercase tracking-wider text-muted">{t("app.tagline")}</div>
        </div>
      </div>
      <nav className="flex flex-col gap-1">
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === "/"}
            className={({ isActive }) =>
              `rounded-lg px-3 py-2 text-sm transition-colors ${
                isActive ? "bg-navy-800 text-beam" : "text-muted hover:bg-navy-800 hover:text-ink"
              }`
            }
          >
            <span className="mr-2" aria-hidden>
              {l.icon}
            </span>
            {t(l.key)}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto px-2">
        <LangToggle />
      </div>
    </aside>
  );
}
