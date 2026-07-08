interface Props {
  label: string;
  value: string;
  info: string;
  tone?: "neutral" | "good" | "bad";
}

/** Metric card with an accessible ⓘ tooltip explaining the metric bilingually. */
export function MetricCard({ label, value, info, tone = "neutral" }: Props) {
  const toneClass =
    tone === "good" ? "text-teal" : tone === "bad" ? "text-loss" : "text-ink";
  return (
    <div className="rounded-xl border border-navy-800 bg-navy-900 p-5">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted">
        {label}
        <span className="group relative cursor-help" tabIndex={0} aria-label={info}>
          <span className="text-muted/70">ⓘ</span>
          <span className="pointer-events-none absolute left-1/2 top-6 z-10 hidden w-64 -translate-x-1/2 rounded-lg border border-navy-800 bg-navy-950 p-3 text-[11px] font-normal normal-case leading-snug tracking-normal text-ink shadow-xl group-hover:block group-focus:block">
            {info}
          </span>
        </span>
      </div>
      <div className={`tabular mt-2 font-display text-3xl font-bold ${toneClass}`}>{value}</div>
    </div>
  );
}
