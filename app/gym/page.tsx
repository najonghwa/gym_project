"use client";
// 헬스장 — SVG 평면도 + 장비 클릭 → 정보 + 내 사용 기록 시트
import { useMemo, useState } from "react";
import { BottomSheet } from "@/components/ui/BottomSheet";
import { EQUIP_INFO, FLOOR, FLOOR_ZONES, ZONES } from "@/lib/data/gym";
import { byId, EXERCISES, type Exercise, type TodayItem } from "@/lib/mock/exercises";
import { ExThumb } from "@/components/ui/ExThumb";
import { ExerciseInfoSheet } from "@/components/workout/ExerciseInfoSheet";
import { useUser } from "@/lib/useUser";

export default function GymPage() {
  const { user } = useUser();
  const [sel, setSel] = useState<string | null>(null);
  const [exInfo, setExInfo] = useState<Exercise | null>(null);
  const relatedExs = useMemo(() => (sel ? EXERCISES.filter((e) => e.equipment === sel) : []), [sel]);
  const info = sel ? EQUIP_INFO[sel] : null;
  const item = sel ? FLOOR.find((f) => f.eq === sel) : null;
  const zone = item ? ZONES.find((z) => z.id === item.zone) : null;

  // 이 장비로 한 내 기록 — 장비명↔운동 equipment 매칭
  const history = useMemo(() => {
    if (!sel || !user) return null;
    const ids = new Set(EXERCISES.filter((e) => e.equipment === sel).map((e) => e.id));
    if (ids.size === 0) return null; // 유산소·소도구 등 매핑 없는 장비
    const rows: { date: string; name: string; maxKg: number; reps: number; sets: number }[] = [];
    Object.entries(user.v2?.workouts ?? {}).forEach(([d, w]) => {
      (w.items as TodayItem[]).forEach((it) => {
        if (!ids.has(it.exerciseId)) return;
        const done = it.sets.filter((s) => s.done);
        if (!done.length) return;
        const maxKg = Math.max(0, ...done.map((s) => s.weightKg ?? 0));
        const top = done.find((s) => (s.weightKg ?? 0) === maxKg);
        rows.push({ date: d, name: byId(it.exerciseId)?.name ?? it.exerciseId, maxKg, reps: top?.reps ?? 0, sets: done.length });
      });
    });
    rows.sort((a, b) => (a.date < b.date ? 1 : -1));
    const sessions = new Set(rows.map((r) => r.date)).size;
    const bestKg = Math.max(0, ...rows.map((r) => r.maxKg));
    const totalSets = rows.reduce((s, r) => s + r.sets, 0);
    // 날짜별 최고 중량 추이 (최근 8일)
    const byDate = new Map<string, number>();
    [...rows].reverse().forEach((r) => byDate.set(r.date, Math.max(byDate.get(r.date) ?? 0, r.maxKg)));
    const trend = [...byDate.entries()].slice(-8);
    const maxTrend = Math.max(1, ...trend.map(([, k]) => k));
    return { rows: rows.slice(0, 6), sessions, bestKg, totalSets, trend, maxTrend };
  }, [sel, user]);

  return (
    <main className="lg:max-w-none lg:pt-10">
      <div className="lab mb-1">FLOOR MAP 헬스장 평면도</div>
      <h2 className="font-display text-[26px]">장비를 눌러보세요</h2>
      <p className="mt-0.5 text-[12px] text-white/45">설명과 사용 팁이 나와요 · 현재는 예시 배치</p>

      <div className="mt-4 rounded-2xl border border-white/[0.06] bg-card p-3">
        <svg viewBox="0 0 400 310" className="w-full rounded-lg bg-black/40">
          {FLOOR_ZONES.map((fz) => {
            const z = ZONES.find((x) => x.id === fz.id)!;
            return (
              <g key={fz.id}>
                <rect x={fz.x} y={fz.y} width={fz.w} height={fz.h} rx={10}
                  fill={`${z.color}0d`} stroke={`${z.color}55`} strokeWidth={1.2} />
                <text x={fz.x + 8} y={fz.y + 16} fontSize={9} fontWeight={800} fill={z.color}>
                  {fz.id} · {z.name}
                </text>
              </g>
            );
          })}
          {FLOOR.map((f) => {
            const z = ZONES.find((x) => x.id === f.zone)!;
            return (
              <g key={f.eq} className="cursor-pointer" onClick={() => setSel(f.eq)}>
                <rect x={f.x - 19} y={f.y - 15} width={38} height={30} rx={7}
                  fill="#1a1a1a" stroke={`${z.color}88`} strokeWidth={1} />
                <text x={f.x} y={f.y + 1} fontSize={12} textAnchor="middle">{f.icon}</text>
                <text x={f.x} y={f.y + 11} fontSize={5.2} textAnchor="middle" fill="#9ca3af">{f.eq}</text>
              </g>
            );
          })}
          <rect x={178} y={300} width={44} height={8} rx={3} fill="#3f3f46" />
          <text x={200} y={297} fontSize={7} textAnchor="middle" fill="#9ca3af">🚪 입구</text>
        </svg>
        <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1.5">
          {ZONES.map((z) => (
            <span key={z.id} className="flex items-center gap-1.5 text-[11.5px] text-white/55">
              <i className="inline-block h-2.5 w-2.5 rounded-sm" style={{ background: z.color }} />
              {z.id} {z.name}
            </span>
          ))}
        </div>
      </div>

      {/* 구역별 장비 칩 */}
      <div className="mt-4 space-y-3">
        {ZONES.map((z) => (
          <div key={z.id}>
            <div className="text-[12.5px] font-bold" style={{ color: z.color }}>{z.id}구역 · {z.name}</div>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {FLOOR.filter((f) => f.zone === z.id).map((f) => (
                <button
                  key={f.eq}
                  onClick={() => setSel(f.eq)}
                  className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-[12px] font-bold text-white/70 active:scale-95"
                >
                  {f.icon} {f.eq}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      <BottomSheet open={!!sel} onClose={() => setSel(null)}>
        {item && info && zone && (
          <>
            <div className="flex items-center gap-3.5">
              <div className="grid h-14 w-14 place-items-center rounded-lg border border-white/10 bg-white/[0.05] text-3xl">{item.icon}</div>
              <div>
                <h3 className="text-lg font-extrabold">{item.eq}</h3>
                <span className="text-[12px] font-bold" style={{ color: zone.color }}>{zone.id}구역 · {zone.name}</span>
              </div>
            </div>
            <p className="mt-3 text-[14px] leading-relaxed">{info.desc}</p>
            <div className="mt-3 rounded-lg border border-gold/40 bg-gold/10 p-3 text-[13px] leading-relaxed">
              💡 <b>팁</b> — {info.tip}
            </div>

            {/* 이 장비로 하는 운동 — 클릭하면 애니메이션+하는 방법 */}
            {relatedExs.length > 0 && (
              <>
                <div className="lab mb-2 mt-5">이 장비로 하는 운동 <span className="font-normal normal-case text-white/35">— 누르면 하는 방법</span></div>
                <div className="grid grid-cols-2 gap-1.5">
                  {relatedExs.map((ex) => (
                    <button key={ex.id} onClick={() => setExInfo(ex)} className="flex items-center gap-2 rounded-lg bg-white/[0.04] p-1.5 text-left">
                      <ExThumb ex={ex} size={34} />
                      <span className="min-w-0 flex-1 truncate text-[12px] font-bold text-white/75">{ex.name}</span>
                      <span className="shrink-0 pr-1 text-[11px] text-white/30">›</span>
                    </button>
                  ))}
                </div>
              </>
            )}

            {/* 이 장비로 한 내 기록 */}
            {history && (
              <>
                <div className="lab mb-2 mt-5">이 장비로 한 내 기록</div>
                {history.sessions === 0 ? (
                  <p className="rounded-lg bg-white/[0.04] p-3.5 text-center text-[12.5px] text-white/40">
                    아직 이 장비로 운동한 기록이 없어요
                  </p>
                ) : (
                  <>
                    <div className="grid grid-cols-3 gap-2">
                      {([[`${history.sessions}회`, "사용한 날"], [`${history.totalSets}세트`, "총 세트"], [history.bestKg ? `${history.bestKg}kg` : "—", "최고 중량"]] as const).map(([v, l]) => (
                        <div key={l} className="rounded-lg bg-white/[0.05] py-2.5 text-center">
                          <div className="font-display text-[16px] leading-none tabular-nums">{v}</div>
                          <div className="mt-1 text-[9.5px] text-white/45">{l}</div>
                        </div>
                      ))}
                    </div>

                    {/* 날짜별 최고 중량 추이 */}
                    {history.bestKg > 0 && history.trend.length >= 2 && (
                      <div className="mt-3 rounded-lg bg-white/[0.04] p-3">
                        <div className="text-[10.5px] font-bold text-white/45">날짜별 최고 중량 (kg)</div>
                        <div className="mt-2 flex items-end gap-1.5" style={{ height: 72 }}>
                          {history.trend.map(([d, kg]) => (
                            <div key={d} className="flex min-w-0 flex-1 flex-col items-center justify-end gap-1">
                              <span className="text-[9px] font-bold tabular-nums text-volt">{kg}</span>
                              <div className="w-full rounded-t-[3px] bg-volt/80" style={{ height: `${Math.max(8, (kg / history.maxTrend) * 44)}px` }} />
                              <span className="text-[8.5px] tabular-nums text-white/35">{d.slice(5).replace("-", ".")}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 최근 세션 */}
                    <div className="mt-3 divide-y divide-white/[0.06]">
                      {history.rows.map((r, i) => (
                        <div key={`${r.date}-${r.name}-${i}`} className="flex items-center gap-2.5 py-2">
                          <span className="w-12 shrink-0 text-[11.5px] tabular-nums text-white/50">{r.date.slice(5).replace("-", ".")}</span>
                          <span className="min-w-0 flex-1 truncate text-[12.5px] font-bold text-white/80">{r.name}</span>
                          <span className="shrink-0 text-[12px] tabular-nums text-white/60">
                            {r.maxKg > 0 ? <><b className="text-volt">{r.maxKg}kg</b> × {r.reps}회 · </> : ""}{r.sets}세트
                          </span>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </>
            )}
          </>
        )}
      </BottomSheet>

      <ExerciseInfoSheet exercise={exInfo} onClose={() => setExInfo(null)} />
    </main>
  );
}
