/**
 * Minimal inline stroke-icon set (24×24, currentColor) so the UI chrome uses
 * consistent iconography instead of emoji. No icon library dependency.
 */
interface IconProps {
  className?: string;
}

function Svg({ className, children }: IconProps & { children: React.ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className ?? "h-4 w-4"}
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

/** Dashboard — 2×2 panel grid. */
export function IconDashboard(p: IconProps) {
  return (
    <Svg {...p}>
      <rect x="3" y="3" width="7.5" height="9" rx="1.5" />
      <rect x="13.5" y="3" width="7.5" height="5.5" rx="1.5" />
      <rect x="13.5" y="12" width="7.5" height="9" rx="1.5" />
      <rect x="3" y="15.5" width="7.5" height="5.5" rx="1.5" />
    </Svg>
  );
}

/** Copilot — chat bubble. */
export function IconChat(p: IconProps) {
  return (
    <Svg {...p}>
      <path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </Svg>
  );
}

/** Scenarios — lightning bolt (price shock). */
export function IconZap(p: IconProps) {
  return (
    <Svg {...p}>
      <path d="M13 2 3 14h8l-1 8 10-12h-8l1-8z" />
    </Svg>
  );
}

/** Digest — document with text lines. */
export function IconFileText(p: IconProps) {
  return (
    <Svg {...p}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <path d="M14 2v6h6" />
      <path d="M16 13H8" />
      <path d="M16 17H8" />
    </Svg>
  );
}

/** Settings — gear. */
export function IconSettings(p: IconProps) {
  return (
    <Svg {...p}>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </Svg>
  );
}

/** Warnings — grounding flags, stale-data banners. */
export function IconAlertTriangle(p: IconProps) {
  return (
    <Svg {...p}>
      <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <path d="M12 9v4" />
      <path d="M12 17h.01" />
    </Svg>
  );
}

/** Grounded/verified — check inside circle. */
export function IconCheckCircle(p: IconProps) {
  return (
    <Svg {...p}>
      <circle cx="12" cy="12" r="9" />
      <path d="m8.5 12 2.5 2.5 5-5" />
    </Svg>
  );
}

/** Tool-call chips — sigma, a computation. */
export function IconSigma(p: IconProps) {
  return (
    <Svg {...p}>
      <path d="M17 7V5H7l5.5 7L7 19h10v-2" />
    </Svg>
  );
}

/** External links. */
export function IconArrowUpRight(p: IconProps) {
  return (
    <Svg {...p}>
      <path d="M7 17 17 7" />
      <path d="M8 7h9v9" />
    </Svg>
  );
}

/** Metric explanations. */
export function IconInfo(p: IconProps) {
  return (
    <Svg {...p}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5" />
      <path d="M12 8h.01" />
    </Svg>
  );
}
