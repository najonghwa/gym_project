"use client";
// 분석 탭 — 헬스/러닝 분리 + 실데이터 신규 분석
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Scatter, ScatterChart, ResponsiveContainer, Tooltip, XAxis, YAxis, ZAxis,
} from "recharts";
import { AnalysisCard } from "@/components/analysis/AnalysisCard";
import { Big3Card } from "@/components/analysis/Big3Card";
import { RecoveryMap } from "@/components/recovery/RecoveryMap";
import { PRChart } from "@/components/charts/PRChart";
import { VolumeGroupedBar } from "@/components/charts/VolumeGroupedBar";
import { BalanceRadar, StandardRadar } from "@/components/charts/RadarCompare";
import { StatChip } from "@/components/ui/StatChip";
import { LoginCard } from "@/components/auth/LoginCard";
import { getMockRecovery } from "@/lib/mock/recovery";
import { byId, type TodayItem } from "@/lib/mock/exercises";
import { BALANCE_RADAR, PEER_RADAR } from "@/lib/mock/routines";
import { computeStats, useUser } from "@/lib/useUser";
import { MUSCLE_KR, type Muscle } from "@/lib/recovery";

type Run = { date: string; km: number; paceSec?: number | null };
const paceStr = (sec?: number | null) =>
  sec ? `${Math.floor(sec / 60)}'${String(Math.round(sec % 60)).padStart(2, "0")}"` : "—";

export default function AnalysisPage() {
  const router = useRouter();
  const { user, ready, login, signup, saveBig3 } = useUser();
  const [mode, setMode] = useState<"gym" | "run">("gym");
  const recovery = useMemo(() => getMockRecovery(), []);
  const st = useMemo(() => (user ? computeStats(user) : null), [user]);

  // ── 헬스 실데이터 분석 ──
  const gymExtra = useMemo(() => {
    const w = user?.v2?.workouts ?? {};
    const cutoff = new Date(); cutoff.setDate(cutoff.getDate() - 6); cutoff.setHours(0, 0, 0, 0);
    const volByMuscle = new Map<Muscle, number>();
    const freq = new Map<string, number>();
    Object.entries(w).forEach(([date, day]) => {
      (day.items as TodayItem[]).forEach((it) => {
        const done = it.sets.filter((s) => s.done).length;
        if (!done) return;
        freq.set(it.exerciseId, (freq.get(it.exerciseId) ?? 0) + done);
        if (new Date(date + "T00:00:00") >= cutoff) {
          const ex = byId(it.exerciseId);
          if (ex) {
            const m = ex.contrib[0].muscle;
            volByMuscle.set(m, (volByMuscle.get(m) ?? 0) + done);
          }
        }
      });
    });
    const weekSets = [...volByMuscle.entries()].sort((a, b) => b[1] - a[1]);
    const top5 = [...freq.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5);

    // 꾸준함 히트맵 (최근 12주 × 요일, 완료 세트 수) — 구버전 기록도 합산
    const setsByDate = new Map<string, number>();
    Object.entries(w).forEach(([date, day]) => {
      const done = (day.items as TodayItem[]).reduce((s, it) => s + it.sets.filter((x) => x.done).length, 0);
      if (done) setsByDate.set(date, (setsByDate.get(date) ?? 0) + done);
    });
    Object.entries(user?.workouts ?? {}).forEach(([date, day]) => {
      const done = day.doneSets ?? 0;
      if (done) setsByDate.set(date, (setsByDate.get(date) ?? 0) + done);
    });
    const now = new Date();
    const mon0 = new Date(now); mon0.setDate(now.getDate() - ((now.getDay() + 6) % 7)); mon0.setHours(0, 0, 0, 0);
    const heat: number[][] = Array.from({ length: 7 }, () => Array(12).fill(0));
    setsByDate.forEach((n, date) => {
      const d = new Date(date + "T00:00:00");
      const dow = (d.getDay() + 6) % 7;
      const wk = new Date(d); wk.setDate(d.getDate() - dow);
      const diffW = Math.round((mon0.getTime() - wk.getTime()) / (7 * 864e5));
      if (diffW >= 0 && diffW < 12) heat[dow][11 - diffW] += n;
    });
    const maxHeat = Math.max(1, ...heat.flat());
    const activeDays12w = heat.flat().filter((n) => n > 0).length;

    return { weekSets, top5, maxSet: Math.max(1, ...weekSets.map(([, n]) => n)), heat, maxHeat, activeDays12w };
  }, [user]);

  // ── 러닝 실데이터 분석 ──
  const runExtra = useMemo(() => {
    const runs = (user?.runs ?? []) as Run[];
    const paced = runs.filter((r) => r.paceSec);
    const scatter = paced.map((r) => ({ km: r.km, sec: r.paceSec! }));
    const buckets = [
      { l: "~3km", min: 0, max: 3 }, { l: "3~5km", min: 3, max: 5 },
      { l: "5~7km", min: 5, max: 7 }, { l: "7~10km", min: 7, max: 10 },
      { l: "10km+", min: 10, max: 999 },
    ].map((b) => ({ l: b.l, n: runs.filter((r) => r.km >= b.min && r.km < b.max).length }));
    const maxBucket = Math.max(1, ...buckets.map((b) => b.n));
    const dow = ["월", "화", "수", "목", "금", "토", "일"].map((l, i) => {
      const xs = paced.filter((r) => (new Date(r.date + "T00:00:00").getDay() + 6) % 7 === i);
      return { l, avg: xs.length ? Math.round(xs.reduce((s, r) => s + r.paceSec!, 0) / xs.length) : null, n: xs.length };
    });
    const bestDow = dow.filter((d) => d.avg).sort((a, b) => a.avg! - b.avg!)[0];
    return { count: runs.length, scatter, buckets, maxBucket, dow, bestDow };
  }, [user]);

  if (!ready) return null;
  if (!user) return <main className="lg:pt-10"><LoginCard onLogin={login} onSignup={signup} /></main>;

  const b3last = user.big3?.logs?.at(-1);
  const b3total = b3last ? Math.round((b3last.s + b3last.b + b3last.d) * 10) / 10 : 0;

  return (
    <main className="space-y-4 lg:mx-auto lg:max-w-none lg:pt-10">
      {/* 모드 전환 */}
      <div className="grid grid-cols-2 gap-1 rounded-lg border border-white/10 bg-white/5 p-1">
        {(["gym", "run"] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`rounded-md py-2.5 text-[14px] font-bold ${mode === m ? "bg-volt text-black" : "text-white/50"}`}
          >
            {m === "gym" ? "🏋️ 헬스 분석" : "🏃 러닝 분석"}
          </button>
        ))}
      </div>

      {mode === "gym" ? (
        <div className="space-y-4 lg:grid lg:grid-cols-2 lg:items-start lg:gap-4 lg:space-y-0">
          <div className="grid grid-cols-3 gap-2 lg:col-span-2 lg:grid-cols-6">
            <StatChip label="총 운동" value={st?.sessions ?? 0} unit="회" tone="volt" />
            <StatChip label="연속" value={st?.streak ?? 0} unit="일" tone={st && st.streak > 0 ? "volt" : "mute"} />
            <StatChip label="4주 출석률" value={st?.att ?? 0} unit="%" tone={st && st.att >= 70 ? "volt" : "gold"} />
            <StatChip label="총 XP" value={st?.xp ?? 0} tone="mute" />
            <StatChip label="3대 합계" value={b3last ? b3total : "—"} unit={b3last ? "kg" : ""} tone="gold" />
            <StatChip label="레벨" value={`Lv${st?.level ?? 1}`} tone="mute" />
          </div>

          <div className="rounded-2xl border border-white/[0.06] bg-card p-4 lg:col-span-2">
            <RecoveryMap data={recovery} />
          </div>

          {/* 신규: 부위별 주간 세트 (실데이터) */}
          <AnalysisCard question="이번 주, 어느 부위를 얼마나 쳤을까?" cta="오늘 세트 기록하러 가기" onCta={() => router.push("/today")}>
            {gymExtra.weekSets.length ? (
              <div className="space-y-2">
                {gymExtra.weekSets.map(([m, n]) => (
                  <div key={m} className="flex items-center gap-2.5">
                    <span className="w-16 shrink-0 text-[12px] font-bold text-white/60">{MUSCLE_KR[m]}</span>
                    <div className="h-3.5 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
                      <div className="h-full rounded-full bg-volt" style={{ width: `${(n / gymExtra.maxSet) * 100}%` }} />
                    </div>
                    <b className="w-12 shrink-0 text-right text-[12px] tabular-nums">{n}세트</b>
                  </div>
                ))}
              </div>
            ) : (
              <p className="py-4 text-center text-[12.5px] text-white/40">이번 주 완료한 세트가 아직 없어요</p>
            )}
          </AnalysisCard>

          {/* 신규: 최다 수행 운동 TOP5 (실데이터) */}
          <AnalysisCard question="내가 제일 많이 한 운동은?">
            {gymExtra.top5.length ? (
              <div className="divide-y divide-white/[0.06]">
                {gymExtra.top5.map(([id, n], i) => {
                  const ex = byId(id);
                  return (
                    <div key={id} className="flex items-center gap-3 py-2.5">
                      <span className="w-6 text-center font-display text-[15px] text-white/40">{i + 1}</span>
                      <span className="flex-1 text-[13.5px] font-bold">{ex ? `${ex.em} ${ex.name}` : id}</span>
                      <b className="text-[13px] text-volt">{n}세트</b>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="py-4 text-center text-[12.5px] text-white/40">아직 운동 기록이 없어요</p>
            )}
          </AnalysisCard>

          {/* 신규: 꾸준함 히트맵 (실데이터, 러닝 탭과 동일 패턴) */}
          <AnalysisCard question="빠짐없이 꾸준히 다니고 있을까?" cta="오늘 출석 도장 찍기" onCta={() => router.push("/today")}>
            {gymExtra.activeDays12w > 0 ? (
              <>
                <div className="space-y-1">
                  {gymExtra.heat.map((row, di) => (
                    <div key={di} className="flex items-center gap-1">
                      <span className="w-4 shrink-0 text-[9px] text-white/35">{["월", "화", "수", "목", "금", "토", "일"][di]}</span>
                      <div className="grid flex-1 grid-cols-12 gap-1">
                        {row.map((n, wi) => (
                          <div
                            key={wi}
                            className="aspect-square rounded-[4px]"
                            style={{ background: n > 0 ? `rgba(200,255,0,${0.25 + 0.75 * (n / gymExtra.maxHeat)})` : "rgba(255,255,255,0.05)" }}
                            title={n > 0 ? `${n}세트` : ""}
                          />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                <p className="mt-2.5 text-[11.5px] text-white/45">
                  최근 12주 중 <b className="text-volt">{gymExtra.activeDays12w}일</b> 운동 · 진할수록 세트가 많은 날 · 오른쪽이 이번 주
                </p>
              </>
            ) : (
              <p className="py-4 text-center text-[12.5px] text-white/40">운동한 날이 색으로 표시돼요</p>
            )}
          </AnalysisCard>

          <AnalysisCard question="이번 주 볼륨, 지난주보다 늘었을까?">
            <VolumeGroupedBar />
          </AnalysisCard>

          <AnalysisCard question="내 몸, 골고루 크고 있을까?" cta="부족한 부위 루틴 받기" onCta={() => router.push("/routine")}>
            <BalanceRadar data={BALANCE_RADAR} />
          </AnalysisCard>

          <AnalysisCard question="권장 기준 대비, 나는 잘하고 있을까?" cta="랭킹에서 순위 보기" onCta={() => router.push("/ranking")}>
            <StandardRadar data={PEER_RADAR} />
          </AnalysisCard>

          <AnalysisCard question="내 기록, 자라고 있을까?">
            <PRChart selectable />
          </AnalysisCard>

          <AnalysisCard question="3대 500, 어디까지 왔을까?">
            <Big3Card big3={user.big3} onSave={saveBig3} />
          </AnalysisCard>
        </div>
      ) : (
        <div className="space-y-4 lg:grid lg:grid-cols-2 lg:items-start lg:gap-4 lg:space-y-0">
          {/* 신규: 페이스 × 거리 산점도 */}
          <AnalysisCard question="거리가 길어지면 페이스는 얼마나 떨어질까?" cta="러닝 대시보드 보기" onCta={() => router.push("/run")}>
            {runExtra.scatter.length >= 3 ? (
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 8, right: 10, left: -6, bottom: 4 }}>
                    <XAxis
                      dataKey="km" type="number" name="거리" unit="km"
                      tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9.5 }} axisLine={false} tickLine={false}
                    />
                    <YAxis
                      dataKey="sec" type="number" reversed domain={["dataMin - 20", "dataMax + 20"]}
                      tickFormatter={(v) => paceStr(Number(v))}
                      tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} width={46}
                    />
                    <ZAxis range={[70, 71]} />
                    <Tooltip
                      contentStyle={{ background: "#121212", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }}
                      formatter={(v, name) => name === "거리" ? [`${v}km`, ""] : [paceStr(Number(v)) + "/km", ""]}
                    />
                    <Scatter data={runExtra.scatter} fill="#c8ff00" fillOpacity={0.85} />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="py-6 text-center text-[12.5px] text-white/40">
                페이스 기록 3개부터 분포가 보여요 (현재 {runExtra.scatter.length}개)
              </p>
            )}
            <p className="mt-1 text-center text-[10.5px] text-white/35">점 = 러닝 1회 · 오른쪽 위일수록 장거리를 빠르게</p>
          </AnalysisCard>

          {/* 신규: 거리 분포 */}
          <AnalysisCard question="나는 주로 몇 km를 뛸까?">
            <div className="space-y-2">
              {runExtra.buckets.map((b) => (
                <div key={b.l} className="flex items-center gap-2.5">
                  <span className="w-14 shrink-0 text-[12px] font-bold text-white/60">{b.l}</span>
                  <div className="h-3.5 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
                    <div className="h-full rounded-full bg-volt" style={{ width: `${(b.n / runExtra.maxBucket) * 100}%` }} />
                  </div>
                  <b className="w-9 shrink-0 text-right text-[12px] tabular-nums">{b.n}회</b>
                </div>
              ))}
            </div>
            <p className="mt-2.5 text-center text-[11.5px] text-white/40">
              총 {runExtra.count}회 — 편한 거리에 머물러 있다면 가끔 한 구간 위를 노려보세요
            </p>
          </AnalysisCard>

          {/* 신규: 요일별 평균 페이스 */}
          <AnalysisCard question="어느 요일에 제일 잘 달릴까?" cta="러닝 기록 추가하기" onCta={() => router.push("/run")}>
            <div className="grid grid-cols-7 gap-1.5">
              {runExtra.dow.map((d) => (
                <div
                  key={d.l}
                  className={`rounded-2xl border py-2.5 text-center ${
                    runExtra.bestDow && d.l === runExtra.bestDow.l
                      ? "border-volt/60 bg-volt/10" : "border-white/[0.06] bg-white/[0.03]"
                  }`}
                >
                  <div className="text-[10px] text-white/45">{d.l}</div>
                  <div className={`mt-1 text-[11px] font-extrabold tabular-nums ${d.avg ? "" : "text-white/20"}`}>
                    {d.avg ? paceStr(d.avg) : "·"}
                  </div>
                  {d.n > 0 && <div className="text-[8.5px] text-white/35">{d.n}회</div>}
                </div>
              ))}
            </div>
            {runExtra.bestDow && (
              <p className="mt-2.5 text-center text-[12px] text-white/55">
                <b className="text-volt">{runExtra.bestDow.l}요일</b>에 가장 빨라요 ({paceStr(runExtra.bestDow.avg)}) — 중요한 러닝은 이날에!
              </p>
            )}
          </AnalysisCard>
        </div>
      )}
    </main>
  );
}
