"use client";
// KPI 칩 — 좌측 상태바 + 라벨 + 값 + 지난주 대비 ▲▼ (스펙 §2-3)
export function StatChip({
  icon,
  label,
  value,
  unit,
  delta,
  tone = "volt",
}: {
  icon?: string;
  label: string;
  value: string | number;
  unit?: string;
  delta?: number;
  tone?: "volt" | "gold" | "danger" | "mute";
}) {
  const bar =
    tone === "volt" ? "bg-volt" : tone === "gold" ? "bg-gold" : tone === "danger" ? "bg-danger" : "bg-zinc-700";
  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/[0.06] bg-white/[0.04] px-3.5 py-2.5">
      <span className={`absolute left-0 top-0 h-full w-1 ${bar}`} />
      <div className="pl-1.5">
        <div className="text-[10.5px] font-bold text-white/55">
          {icon ? `${icon} ` : ""}{label}
        </div>
        <div className="mt-0.5 flex items-baseline gap-1">
          <span className="font-display text-[22px] leading-none tabular-nums">{value}</span>
          {unit && <span className="text-[11px] text-white/55">{unit}</span>}
          {delta != null && delta !== 0 && (
            <span className={`ml-1 text-[11px] font-bold ${delta > 0 ? "text-volt" : "text-danger"}`}>
              {delta > 0 ? "▲" : "▼"}{Math.abs(delta)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
