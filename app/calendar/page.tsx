"use client";
// 달력 — 구버전(gym_web) 기록 + 신버전(v2) 기록 통합 (헬스% + 러닝km)
import { useMemo, useState } from "react";
import { LoginCard } from "@/components/auth/LoginCard";
import { useUser } from "@/lib/useUser";
import type { TodayItem } from "@/lib/mock/exercises";

const fmt = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

export default function CalendarPage() {
  const { user, ready, login, signup } = useUser();
  const [cursor, setCursor] = useState(() => new Date());

  const cells = useMemo(() => {
    if (!user) return [];
    const y = cursor.getFullYear(), m = cursor.getMonth();
    const startDow = new Date(y, m, 1).getDay();
    const daysIn = new Date(y, m + 1, 0).getDate();
    const legacy = user.workouts ?? {};
    const v2 = user.v2?.workouts ?? {};
    const runsBy: Record<string, number> = {};
    (user.runs ?? []).forEach((r) => { runsBy[r.date] = (runsBy[r.date] ?? 0) + r.km; });
    const todayS = fmt(new Date());

    const out: { day?: number; pct?: number | null; km?: number; isToday?: boolean }[] = [];
    for (let i = 0; i < startDow; i++) out.push({});
    for (let d = 1; d <= daysIn; d++) {
      const k = fmt(new Date(y, m, d));
      let pct: number | null = null;
      if (v2[k]) {
        const its = v2[k].items as TodayItem[];
        const total = its.reduce((s, it) => s + it.sets.length, 0);
        const done = its.reduce((s, it) => s + it.sets.filter((x) => x.done).length, 0);
        if (done > 0) pct = Math.round((done / Math.max(1, total)) * 100);
      } else if ((legacy[k]?.doneSets ?? 0) > 0) {
        pct = legacy[k].scorePct ?? 0;
      }
      out.push({
        day: d, pct,
        km: runsBy[k] ? Math.round(runsBy[k] * 10) / 10 : undefined,
        isToday: k === todayS,
      });
    }
    return out;
  }, [user, cursor]);

  if (!ready) return null;
  if (!user)
    return <main className="lg:pt-10"><LoginCard onLogin={login} onSignup={signup} /></main>;

  const gymDays = cells.filter((c) => c.pct != null).length;
  const runKm = cells.reduce((s, c) => s + (c.km ?? 0), 0);

  return (
    <main className="lg:mx-auto lg:max-w-2xl lg:pt-10">
      <div className="mb-3 flex items-center justify-between">
        <button
          className="h-10 w-10 rounded-full border border-white/10 bg-white/5 font-bold"
          onClick={() => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() - 1, 1))}
        >‹</button>
        <h2 className="font-display text-[24px]">{cursor.getFullYear()}년 {cursor.getMonth() + 1}월</h2>
        <button
          className="h-10 w-10 rounded-full border border-white/10 bg-white/5 font-bold"
          onClick={() => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1))}
        >›</button>
      </div>

      <div className="rounded-xl border border-white/[0.06] bg-card p-3.5">
        <div className="grid grid-cols-7 gap-1.5">
          {["일", "월", "화", "수", "목", "금", "토"].map((d, i) => (
            <div key={d} className={`py-1 text-center text-[10px] font-bold ${i === 0 ? "text-danger/70" : "text-white/35"}`}>{d}</div>
          ))}
          {cells.map((c, i) =>
            c.day ? (
              <div
                key={i}
                className={`flex h-[54px] flex-col items-start gap-[3px] overflow-hidden rounded-xl border p-1.5 ${
                  c.pct != null && c.pct >= 100 ? "border-volt/50 bg-volt/10"
                  : c.pct != null ? "border-gold/40 bg-gold/10"
                  : c.km ? "border-sky-500/40 bg-sky-500/10"
                  : "border-white/[0.05] bg-white/[0.02]"
                } ${c.isToday ? "ring-2 ring-gold" : ""}`}
              >
                <span className={`text-[10px] leading-none ${c.pct != null || c.km ? "font-extrabold" : "text-white/30"}`}>{c.day}</span>
                {c.pct != null && (
                  <span className={`text-[8.5px] font-bold leading-none ${c.pct >= 100 ? "text-volt" : "text-gold"}`}>🏋️{c.pct}%</span>
                )}
                {c.km && <span className="text-[8.5px] font-bold leading-none text-sky-400">🏃{c.km}k</span>}
              </div>
            ) : (
              <div key={i} />
            )
          )}
        </div>
        <div className="mt-3 flex justify-between text-[12px] text-white/50">
          <span>헬스 <b className="text-zinc-100">{gymDays}일</b> · 러닝 <b className="text-zinc-100">{Math.round(runKm * 10) / 10}km</b></span>
          <span className="flex items-center gap-3 text-[10.5px]">
            <span className="flex items-center gap-1"><i className="h-2 w-2 rounded-sm bg-volt/60" />100%</span>
            <span className="flex items-center gap-1"><i className="h-2 w-2 rounded-sm bg-gold/60" />부분</span>
            <span className="flex items-center gap-1"><i className="h-2 w-2 rounded-sm bg-sky-400/60" />러닝</span>
          </span>
        </div>
      </div>
      <p className="mt-3 text-[11.5px] text-white/35">구버전 헬스 가이드에서 쌓은 기록도 그대로 보여요.</p>
    </main>
  );
}
