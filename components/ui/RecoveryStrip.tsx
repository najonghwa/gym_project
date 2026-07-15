"use client";
// 가로 스크롤 부위별 회복%+기여% (스펙 P2-9 — Working Muscles)
import { MUSCLE_KR, recoveryColor, type Muscle } from "@/lib/recovery";

export function RecoveryStrip({
  items,
}: {
  items: { muscle: Muscle; recoveryPct: number; contribPct?: number }[];
}) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1">
      {items.map((it) => (
        <div
          key={it.muscle}
          className="flex shrink-0 items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] py-1.5 pl-1.5 pr-3"
        >
          <span
            className="grid h-7 w-7 place-items-center rounded-full text-[10px] font-extrabold text-black"
            style={{ background: recoveryColor(it.recoveryPct) }}
          >
            {Math.round(it.recoveryPct * 100)}
          </span>
          <span className="text-[12px] font-bold">{MUSCLE_KR[it.muscle]}</span>
          {it.contribPct != null && (
            <span className="text-[10.5px] text-white/45">기여 {it.contribPct}%</span>
          )}
        </div>
      ))}
    </div>
  );
}
