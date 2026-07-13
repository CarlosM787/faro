import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { LANGUAGES, languageFor } from "../languages";
import { IconCheck, IconChevronDown, IconGlobe } from "./icons";

/**
 * Accessible language picker: a compact button that opens a popover list of the
 * languages Faro ships in. Closes on outside click or Escape; the choice is
 * persisted by i18next (localStorage) and flows to the copilot/digest API.
 */
export function LanguageMenu({
  align = "start",
  placement = "down",
  full = false,
}: {
  align?: "start" | "end";
  placement?: "up" | "down";
  full?: boolean;
}) {
  const { i18n, t } = useTranslation();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const current = languageFor(i18n.resolvedLanguage ?? "en");

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const choose = (code: string) => {
    void i18n.changeLanguage(code);
    setOpen(false);
  };

  return (
    <div className={`relative ${full ? "" : "inline-block"}`} ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={t("common.language")}
        className={`flex items-center gap-2 rounded-lg border border-navy-800 bg-navy-900 px-3 py-2 text-sm text-ink transition-colors hover:border-beam/60 ${
          full ? "w-full" : ""
        }`}
      >
        <IconGlobe className="h-4 w-4 shrink-0 text-muted" />
        <span className="flex-1 text-left">{current.label}</span>
        <IconChevronDown
          className={`h-4 w-4 shrink-0 text-muted transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open && (
        <ul
          role="listbox"
          aria-label={t("common.language")}
          className={`absolute z-30 max-h-72 w-44 overflow-auto rounded-lg border border-navy-800 bg-navy-950 p-1 shadow-xl ${
            placement === "up" ? "bottom-full mb-1" : "top-full mt-1"
          } ${align === "end" ? "right-0" : "left-0"}`}
        >
          {LANGUAGES.map((l) => {
            const active = l.code === current.code;
            return (
              <li key={l.code}>
                <button
                  type="button"
                  role="option"
                  aria-selected={active}
                  onClick={() => choose(l.code)}
                  className={`flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors ${
                    active ? "bg-navy-800 text-beam" : "text-ink hover:bg-navy-800"
                  }`}
                >
                  <span className="w-6 text-left text-[11px] font-semibold uppercase text-muted">
                    {l.code}
                  </span>
                  <span className="flex-1 text-left">{l.label}</span>
                  {active && <IconCheck className="h-4 w-4 shrink-0" />}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
