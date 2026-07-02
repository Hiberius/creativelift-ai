export function StatusPill({ label }: { label: string }) {
  const normalized = label.toLowerCase();
  const tone = normalized.includes("winning")
    ? "border-mint/30 bg-mint/10 text-mint"
    : normalized.includes("running")
      ? "border-cyan/30 bg-cyan/10 text-cyan"
      : normalized.includes("inconclusive") || normalized.includes("stub")
        ? "border-yellow-400/30 bg-yellow-400/10 text-yellow-300"
        : normalized.includes("rejected") || normalized.includes("degraded")
          ? "border-red-400/30 bg-red-400/10 text-red-300"
          : "border-white/15 bg-white/7 text-slate-300";

  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-1 text-xs font-medium ${tone}`}>
      {label}
    </span>
  );
}
