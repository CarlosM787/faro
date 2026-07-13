import { useTranslation } from "react-i18next";
import { NavLink } from "react-router-dom";

import {
  IconChat,
  IconDashboard,
  IconFileText,
  IconSettings,
  IconZap,
} from "./icons";
import { LanguageMenu } from "./LanguageMenu";

const links = [
  { to: "/", key: "nav.dashboard", Icon: IconDashboard },
  { to: "/chat", key: "nav.chat", Icon: IconChat },
  { to: "/scenarios", key: "nav.scenarios", Icon: IconZap },
  { to: "/digest", key: "nav.digest", Icon: IconFileText },
  { to: "/settings", key: "nav.settings", Icon: IconSettings },
] as const;

function Logo({ compact = false }: { compact?: boolean }) {
  const { t } = useTranslation();
  return (
    <div className="flex items-center gap-3">
      <img src="/logo-icon.svg" alt="" className={compact ? "h-8 w-8 rounded-lg" : "h-9 w-9 rounded-lg"} />
      <div>
        <div className="font-display text-lg font-bold leading-tight">
          faro<span className="text-beam">quant</span>
        </div>
        {!compact && (
          <div className="text-[11px] uppercase tracking-wider text-muted">{t("app.tagline")}</div>
        )}
      </div>
    </div>
  );
}

/** App navigation: fixed left rail on desktop, sticky top bar on mobile. */
export function Sidebar() {
  const { t } = useTranslation();

  const item = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-2.5 whitespace-nowrap rounded-lg px-3 py-2 text-sm transition-colors ${
      isActive ? "bg-navy-800 text-beam" : "text-muted hover:bg-navy-800 hover:text-ink"
    }`;

  return (
    <>
      {/* desktop rail */}
      <aside className="hidden w-56 flex-col border-r border-navy-800 bg-navy-900 p-4 lg:flex">
        <div className="mb-8 px-2">
          <Logo />
        </div>
        <nav className="flex flex-col gap-1">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.to === "/"} className={item}>
              <l.Icon className="h-[18px] w-[18px] shrink-0" />
              {t(l.key)}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto px-2">
          <LanguageMenu placement="up" full />
        </div>
      </aside>

      {/* mobile top bar */}
      <header className="sticky top-0 z-20 border-b border-navy-800 bg-navy-900/95 backdrop-blur lg:hidden">
        <div className="flex items-center justify-between px-4 pt-3">
          <Logo compact />
          <LanguageMenu placement="down" align="end" />
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 py-2">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.to === "/"} className={item}>
              <l.Icon className="h-4 w-4 shrink-0" />
              {t(l.key)}
            </NavLink>
          ))}
        </nav>
      </header>
    </>
  );
}
