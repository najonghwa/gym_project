"use client";
// 러닝 탭 — Strava식 풀 대시보드 (KPI·월별·목표 도넛·PB·페이스·히트맵·AI 코치) + 기록 입력
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Bar, BarChart, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { useReducedMotion } from "framer-motion";
import { StatChip } from "@/components/ui/StatChip";
import { PillButton } from "@/components/ui/PillButton";
import { BottomSheet } from "@/components/ui/BottomSheet";
import { LoginCard } from "@/components/auth/LoginCard";
import { SettingsSheet } from "@/components/settings/SettingsSheet";
import { RunDetailSheet } from "@/components/run/RunDetailSheet";
import { allBests } from "@/lib/runmath";
import { useUser } from "@/lib/useUser";

type Run = { rid?: string; date: string; km: number; paceSec?: number | null; durSec?: number; route?: [number, number][] };

const paceStr = (sec?: number | null) =>
  sec ? `${Math.floor(sec / 60)}'${String(Math.round(sec % 60)).padStart(2, "0")}"` : "—";
const fmtDate = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const r1 = (x: number) => Math.round(x * 10) / 10;

// ── 통계 계산 ──
function calc(runs: Run[]) {
  const now = new Date();
  const y = now.getFullYear();
  const total = r1(runs.reduce((s, r) => s + r.km, 0));
  const yearKm = r1(runs.filter((r) => r.date.startsWith(String(y))).reduce((s, r) => s + r.km, 0));
  const monthKm = r1(
    runs.filter((r) => r.date.startsWith(`${y}-${String(now.getMonth() + 1).padStart(2, "0")}`))
      .reduce((s, r) => s + r.km, 0)
  );
  const paced = runs.filter((r) => r.paceSec);
  const avgPace = paced.length ? Math.round(paced.reduce((s, r) => s + r.paceSec!, 0) / paced.length) : null;
  const bestPace = paced.length ? Math.min(...paced.map((r) => r.paceSec!)) : null;
  const bestPaceRun = paced.find((r) => r.paceSec === bestPace);
  const longest = runs.length ? Math.max(...runs.map((r) => r.km)) : 0;
  const longestRun = runs.find((r) => r.km === longest);

  // 월별 (올해 12개월)
  const monthly = Array.from({ length: 12 }, (_, i) => ({
    m: `${i + 1}월`,
    km: r1(
      runs.filter((r) => r.date.startsWith(`${y}-${String(i + 1).padStart(2, "0")}`))
        .reduce((s, r) => s + r.km, 0)
    ),
    isNow: i === now.getMonth(),
  }));

  // 월 최다 / 주 최다
  const byMonth = new Map<string, number>();
  runs.forEach((r) => { const k = r.date.slice(0, 7); byMonth.set(k, (byMonth.get(k) ?? 0) + r.km); });
  const bestMonth = [...byMonth.entries()].sort((a, b) => b[1] - a[1])[0];

  const weekKey = (ds: string) => {
    const d = new Date(ds + "T00:00:00");
    d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
    return fmtDate(d);
  };
  const byWeek = new Map<string, number>();
  runs.forEach((r) => { const k = weekKey(r.date); byWeek.set(k, (byWeek.get(k) ?? 0) + 1); });
  const bestWeek = [...byWeek.entries()].sort((a, b) => b[1] - a[1])[0];

  // 요일×주 히트맵 (최근 12주, 월=0행)
  const mon0 = new Date(now); mon0.setDate(now.getDate() - ((now.getDay() + 6) % 7)); mon0.setHours(0, 0, 0, 0);
  const heat: number[][] = Array.from({ length: 7 }, () => Array(12).fill(0));
  runs.forEach((r) => {
    const d = new Date(r.date + "T00:00:00");
    const dow = (d.getDay() + 6) % 7;
    const diffW = Math.round((mon0.getTime() - new Date(weekKey(r.date) + "T00:00:00").getTime()) / (7 * 864e5));
    if (diffW >= 0 && diffW < 12) heat[dow][11 - diffW] += r.km;
  });

  // AI 코치: 최근 4주 vs 이전 4주 / 페이스 추세 / 10% 룰
  const kmIn = (from: number, to: number) =>
    r1(
      runs.filter((r) => { const t = new Date(r.date + "T00:00:00").getTime(); return t >= from && t < to; })
        .reduce((s, r) => s + r.km, 0)
    );
  const nowT = now.getTime();
  const last4 = kmIn(nowT - 28 * 864e5, nowT + 864e5);
  const prev4 = kmIn(nowT - 56 * 864e5, nowT - 28 * 864e5);
  const mileageDelta = prev4 > 0 ? Math.round(((last4 - prev4) / prev4) * 100) : null;
  const recent = paced.slice(-5), before = paced.slice(-10, -5);
  const avg = (xs: Run[]) => (xs.length ? xs.reduce((s, r) => s + r.paceSec!, 0) / xs.length : null);
  const paceNow = avg(recent), pacePrev = avg(before);
  const paceTrend = paceNow && pacePrev ? Math.round(pacePrev - paceNow) : null; // +면 빨라짐(초/km)
  const nextTarget = r1(Math.max(last4 / 4, 3) * 1.1);

  return {
    count: runs.length, total, yearKm, monthKm, avgPace, bestPace, bestPaceRun,
    longest: r1(longest), longestRun, monthly, bestMonth, bestWeek, heat,
    last4, mileageDelta, paceTrend, nextTarget,
    paceSeries: paced.slice(-20).map((r) => ({ d: r.date.slice(5), sec: r.paceSec! })),
  };
}

const GOALS = [100, 200, 300, 500, 1000];

export default function RunPage() {
  const router = useRouter();
  const reduce = useReducedMotion();
  const { user, ready, login, signup, logout, saveRun, deleteRun, setRunGoal, setPrimaryMode, today } = useUser();
  const [showLog, setShowLog] = useState(false);
  const [showGoal, setShowGoal] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [fDate, setFDate] = useState(() => fmtDate(new Date()));
  const [fKm, setFKm] = useState("");
  const [fMin, setFMin] = useState("");
  const [fSec, setFSec] = useState("");

  const runs = useMemo(() => (user?.runs ?? []) as Run[], [user]);
  const s = useMemo(() => calc(runs), [runs]);
  const bests = useMemo(() => allBests(runs), [runs]);
  const [detail, setDetail] = useState<Run | null>(null);
  const goal = user?.v2?.runGoalKm ?? 300;
  const goalPct = Math.min(100, Math.round((s.yearKm / goal) * 100));

  if (!ready) return null;
  if (!user) return <main className="lg:pt-20"><LoginCard onLogin={login} onSignup={signup} /></main>;

  const submitLog = () => {
    const km = parseFloat(fKm);
    if (!km || km <= 0 || fDate > today()) return;
    const pace = (parseInt(fMin) || 0) * 60 + (parseInt(fSec) || 0);
    saveRun({ date: fDate, km: Math.round(km * 100) / 100, paceSec: pace > 0 ? pace : null });
    setFKm(""); setFMin(""); setFSec("");
    setShowLog(false);
  };

  const R = 44, C = 2 * Math.PI * R;

  return (
    <main className="mx-auto max-w-2xl space-y-4 lg:max-w-4xl lg:pt-24">
      {/* 헤더 */}
      <div className="flex items-end justify-between">
        <div>
          <div className="lab">RUN DASHBOARD</div>
          <h1 className="font-display text-[26px] leading-tight tracking-tight">러닝</h1>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSettings(true)}
            className="grid h-10 w-10 place-items-center rounded-lg border border-white/10 bg-card text-[16px]"
            aria-label="설정"
          >
            ⚙️
          </button>
          <button
            onClick={() => setShowLog(true)}
            className="rounded-lg border border-white/15 bg-white/[0.06] px-4 py-2.5 text-[13px] font-extrabold"
          >
            ✍️ 수동 기록
          </button>
        </div>
      </div>

      {/* GPS 라이브 러닝 시작 */}
      <button
        onClick={() => router.push("/run/live")}
        className="flex w-full items-center gap-3 rounded-xl border border-volt/30 bg-gradient-to-r from-volt/15 to-transparent p-4 text-left active:scale-[0.99]"
      >
        <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-volt text-[19px]">📡</span>
        <span className="min-w-0 flex-1">
          <b className="block text-[15.5px]">GPS 러닝 시작</b>
          <span className="text-[11.5px] text-white/50">폰 위치로 거리·페이스 자동 기록 — 시작/일시정지/종료</span>
        </span>
        <span className="font-display text-[20px] text-volt">▶</span>
      </button>

      {/* KPI 스트립 */}
      <div className="grid grid-cols-3 gap-2 lg:grid-cols-6">
        <StatChip label="총 러닝" value={s.count} unit="회" tone="volt" />
        <StatChip label="총 거리" value={s.total} unit="km" tone="volt" />
        <StatChip label="이번 달" value={s.monthKm} unit="km" tone="gold" />
        <StatChip label="평균 페이스" value={paceStr(s.avgPace)} unit="/km" tone="mute" />
        <StatChip label="최고 페이스" value={paceStr(s.bestPace)} unit="/km" tone="danger" />
        <StatChip label="최장 거리" value={s.longest} unit="km" tone="mute" />
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        {/* 월별 러닝 거리 */}
        <section className="rounded-xl border border-white/[0.06] bg-card p-4 lg:col-span-3">
          <b className="text-[15px] font-extrabold">월별 러닝 거리</b>
          <p className="text-[11.5px] text-white/45">{new Date().getFullYear()}년 · 이번 달 강조</p>
          <div className="mt-2 h-44">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={s.monthly} margin={{ top: 14 }}>
                <XAxis dataKey="m" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 8.5 }} axisLine={false} tickLine={false} interval={0} />
                <Tooltip
                  cursor={{ fill: "rgba(255,255,255,0.04)" }}
                  contentStyle={{ background: "#0d1526", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }}
                  formatter={(v) => [`${v}km`, ""]}
                />
                <Bar dataKey="km" radius={[4, 4, 0, 0]} animationDuration={reduce ? 0 : 600}>
                  {s.monthly.map((m, i) => (
                    <Cell key={i} fill={m.isNow ? "#ff9432" : "rgba(255,148,50,0.45)"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* 올해 목표 도넛 */}
        <section className="rounded-xl border border-white/[0.06] bg-card p-4 lg:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <b className="text-[15px] font-extrabold">올해 누적 목표</b>
              <p className="text-[11.5px] text-white/45">{s.yearKm} / {goal} km</p>
            </div>
            <button className="text-[11.5px] font-bold text-white/45" onClick={() => setShowGoal(true)}>
              목표 ✎
            </button>
          </div>
          <div className="mt-2 flex justify-center">
            <div className="relative">
              <svg width={130} height={130} viewBox="0 0 110 110" className="-rotate-90">
                <circle cx={55} cy={55} r={R} stroke="rgba(255,255,255,0.08)" strokeWidth={9} fill="none" />
                <circle
                  cx={55} cy={55} r={R} stroke={goalPct >= 100 ? "#2dd4a0" : "#ff9432"} strokeWidth={9}
                  fill="none" strokeLinecap="round"
                  strokeDasharray={C} strokeDashoffset={C * (1 - goalPct / 100)}
                  style={{ transition: "stroke-dashoffset .8s ease" }}
                />
              </svg>
              <div className="absolute inset-0 grid place-items-center text-center">
                <div>
                  <div className="font-display text-[28px] leading-none">
                    {goalPct}<span className="text-[13px] text-white/50">%</span>
                  </div>
                  <div className="mt-0.5 text-[9.5px] text-white/40">남은 {r1(Math.max(0, goal - s.yearKm))}km</div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        {/* 개인 최고 기록 */}
        <section className="rounded-xl border border-white/[0.06] bg-card p-4 lg:col-span-2">
          <b className="text-[15px] font-extrabold">
            개인 최고 기록 <span className="text-[10px] font-normal text-white/40">Personal Best</span>
          </b>
          <div className="mt-2.5 divide-y divide-white/[0.06]">
            {[
              ["🏁 최장 거리", s.longestRun ? `${s.longest}km` : "—", s.longestRun?.date ?? ""],
              ["⚡ 최고 페이스", paceStr(s.bestPace), s.bestPaceRun?.date ?? ""],
              ["📅 월 최다", s.bestMonth ? `${r1(s.bestMonth[1])}km` : "—", s.bestMonth?.[0] ?? ""],
              ["🔁 주 최다", s.bestWeek ? `${s.bestWeek[1]}회` : "—", s.bestWeek ? s.bestWeek[0] + " 주" : ""],
            ].map(([l, v, d]) => (
              <div key={l as string} className="flex items-center justify-between py-2.5">
                <span className="text-[13px] text-white/70">{l}</span>
                <span className="text-right">
                  <b className="font-display text-[15px] text-gold">{v}</b>
                  <span className="ml-1.5 text-[10px] text-white/35">{d}</span>
                </span>
              </div>
            ))}
          </div>

          {/* 거리별 최고 페이스 — 전체 기록에서 자동 계산 (GPS=구간, 수동=평균 기준) */}
          <div className="lab mt-4 mb-1.5">거리별 최고 페이스</div>
          <div className="grid grid-cols-2 gap-2">
            {bests.map((b) => (
              <div key={b.m} className="rounded-lg bg-white/[0.05] px-3.5 py-2.5">
                <div className="flex items-baseline justify-between">
                  <span className="text-[12px] font-bold text-white/55">{b.m / 1000}km</span>
                  <b className={`font-display text-[15px] tabular-nums ${b.paceSec ? "text-gold" : "text-white/25"}`}>
                    {b.paceSec ? paceStr(b.paceSec) : "도전!"}
                  </b>
                </div>
                <div className="mt-0.5 text-right text-[9px] text-white/35">
                  {b.date ? `${b.gps ? "📡" : "✍️"} ${b.date}` : `${b.m / 1000}km 이상 뛰면 기록돼요`}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 페이스 발전 흐름 */}
        <section className="rounded-xl border border-white/[0.06] bg-card p-4 lg:col-span-3">
          <b className="text-[15px] font-extrabold">페이스 발전 흐름</b>
          <p className="text-[11.5px] text-white/45">최근 {s.paceSeries.length}회 · 위로 갈수록 빠름</p>
          <div className="mt-2 h-40">
            {s.paceSeries.length >= 2 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={s.paceSeries} margin={{ top: 8, right: 8, left: -8 }}>
                  <XAxis dataKey="d" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} />
                  <YAxis
                    reversed domain={["dataMin - 15", "dataMax + 15"]}
                    tickFormatter={(v) => paceStr(Number(v))}
                    tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} width={44}
                  />
                  <Tooltip
                    contentStyle={{ background: "#0d1526", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }}
                    formatter={(v) => [paceStr(Number(v)) + "/km", ""]}
                  />
                  <Line
                    type="monotone" dataKey="sec" stroke="#ff9432" strokeWidth={2.5}
                    dot={{ r: 3, fill: "#ff9432" }} animationDuration={reduce ? 0 : 700}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="grid h-full place-items-center text-[12.5px] text-white/35">
                페이스 기록이 2개 이상 쌓이면 그래프가 나와요
              </p>
            )}
          </div>
        </section>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        {/* 요일 히트맵 (최근 12주) */}
        <section className="rounded-xl border border-white/[0.06] bg-card p-4 lg:col-span-3">
          <b className="text-[15px] font-extrabold">러닝 빈도 히트맵</b>
          <p className="text-[11.5px] text-white/45">최근 12주 · 요일별 달린 거리</p>
          <div className="mt-3 flex gap-1.5">
            <div className="flex flex-col justify-between py-0.5 text-[9px] text-white/35">
              {["월", "수", "금", "일"].map((d) => <span key={d}>{d}</span>)}
            </div>
            <div className="grid flex-1 grid-cols-12 gap-1">
              {Array.from({ length: 12 }, (_, w) => (
                <div key={w} className="flex flex-col gap-1">
                  {Array.from({ length: 7 }, (_, d) => {
                    const km = s.heat[d][w];
                    return (
                      <div
                        key={d}
                        title={km ? `${r1(km)}km` : ""}
                        className="aspect-square rounded-[3px]"
                        style={{
                          background: km > 0
                            ? `rgba(255,148,50,${Math.min(1, 0.3 + km / 8)})`
                            : "rgba(255,255,255,0.05)",
                        }}
                      />
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
          <div className="mt-2 flex items-center justify-end gap-1.5 text-[9.5px] text-white/35">
            적음 <i className="h-2 w-2 rounded-[2px]" style={{ background: "rgba(255,148,50,0.35)" }} />
            <i className="h-2 w-2 rounded-[2px]" style={{ background: "rgba(255,148,50,0.65)" }} />
            <i className="h-2 w-2 rounded-[2px]" style={{ background: "rgba(255,148,50,1)" }} /> 많음
          </div>
        </section>

        {/* AI 코치 어드바이스 */}
        <section className="rounded-xl border border-indigo-400/25 bg-indigo-950/25 p-4 lg:col-span-2">
          <b className="text-[15px] font-extrabold">🤖 러닝 AI 코치 어드바이스</b>
          <p className="text-[11px] text-white/45">최근 기록 기반 맞춤 피드백</p>
          <div className="mt-3 space-y-2.5">
            <div className="rounded-lg bg-white/[0.05] p-3">
              <div className="text-[11px] font-bold text-indigo-300">최근 4주 마일리지</div>
              <p className="mt-1 text-[12.5px] leading-relaxed text-white/75">
                4주간 <b className="text-volt">{s.last4}km</b>
                {s.mileageDelta !== null
                  ? <> — 이전 4주 대비 <b className={s.mileageDelta >= 0 ? "text-volt" : "text-danger"}>{s.mileageDelta >= 0 ? "+" : ""}{s.mileageDelta}%</b></>
                  : " — 비교할 이전 기록이 아직 없어요"}
              </p>
            </div>
            <div className="rounded-lg bg-white/[0.05] p-3">
              <div className="text-[11px] font-bold text-indigo-300">페이스 진단</div>
              <p className="mt-1 text-[12.5px] leading-relaxed text-white/75">
                {s.paceTrend === null
                  ? "페이스 기록이 더 쌓이면 추세를 알려드릴게요."
                  : s.paceTrend > 3
                  ? <>최근 5회 평균이 <b className="text-volt">{s.paceTrend}초/km 빨라졌어요</b> — 좋은 흐름!</>
                  : s.paceTrend < -3
                  ? <>페이스가 {Math.abs(s.paceTrend)}초/km 느려졌어요 — 회복 주간일 수 있어요, 무리 금지.</>
                  : "페이스를 안정적으로 유지 중이에요."}
              </p>
            </div>
            <div className="rounded-lg bg-white/[0.05] p-3">
              <div className="text-[11px] font-bold text-indigo-300">🎯 향후 4주 추천</div>
              <p className="mt-1 text-[12.5px] leading-relaxed text-white/75">
                주당 <b className="text-gold">{s.nextTarget}km</b> 수준으로 10% 이내에서 서서히 올려보세요.
              </p>
            </div>
          </div>
        </section>
      </div>

      {/* 최근 기록 (삭제 가능) */}
      <section className="rounded-xl border border-white/[0.06] bg-card p-4">
        <b className="text-[15px] font-extrabold">최근 기록</b>
        <p className="text-[11.5px] text-white/45">기록을 누르면 지도·구간 페이스가 나와요 · ✕로 삭제</p>
        {runs.length === 0 ? (
          <p className="py-5 text-center text-[12.5px] text-white/35">아직 기록이 없어요 — 첫 러닝을 저장해 보세요!</p>
        ) : (
          <div className="mt-1.5 divide-y divide-white/[0.06]">
            {[...runs].reverse().slice(0, 10).map((r, i) => (
              <div key={r.rid ?? `${r.date}-${r.km}-${i}`} className="flex items-center gap-3 py-2.5">
                <button onClick={() => setDetail(r)} className="flex min-w-0 flex-1 items-center gap-3 text-left">
                  <span title={r.route ? "GPS 기록" : "수동 기록"} className="shrink-0 text-[12px]">{r.route ? "📡" : "✍️"}</span>
                  <span className="w-[76px] shrink-0 text-[12.5px] text-white/55">{r.date}</span>
                  <b className="text-[14px]">{r.km}km</b>
                  <span className="text-[12px] text-white/45">{paceStr(r.paceSec)}/km</span>
                  <span className="ml-auto text-[11px] text-white/25">›</span>
                </button>
                <button
                  onClick={() => {
                    if (window.confirm(`${r.date} · ${r.km}km 기록을 삭제할까요?`)) deleteRun(r);
                  }}
                  className="grid h-7 w-7 shrink-0 place-items-center rounded-full text-[13px] text-white/30 hover:bg-white/5 hover:text-danger"
                  aria-label="기록 삭제"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
        {runs.length > 10 && <p className="mt-2 text-[10.5px] text-white/30">최근 10개만 표시 · 전체 {runs.length}개</p>}
      </section>

      {/* 기록 입력 시트 */}
      <BottomSheet open={showLog} onClose={() => setShowLog(false)}>
        <h3 className="text-lg font-extrabold">러닝 기록</h3>
        <p className="mt-0.5 text-[12px] text-white/50">과거 날짜도 소급 입력 OK</p>
        <div className="mt-4 space-y-3">
          <label className="block">
            <span className="lab">날짜</span>
            <input
              type="date" value={fDate} max={today()} onChange={(e) => setFDate(e.target.value)}
              className="mt-1 w-full rounded-lg border border-white/10 bg-white/[0.04] px-4 py-3 outline-none [color-scheme:dark] focus:border-volt"
            />
          </label>
          <div className="grid grid-cols-2 gap-2.5">
            <label className="block">
              <span className="lab">거리 (km)</span>
              <input
                type="number" step="0.1" inputMode="decimal" placeholder="5.0" value={fKm}
                onChange={(e) => setFKm(e.target.value)}
                className="mt-1 w-full rounded-lg border border-white/10 bg-white/[0.04] px-4 py-3 text-center outline-none placeholder:text-white/25 focus:border-volt"
              />
            </label>
            <label className="block">
              <span className="lab">페이스 (분&apos;초&quot;/km)</span>
              <div className="mt-1 flex items-center gap-1.5">
                <input
                  type="number" inputMode="numeric" placeholder="6" value={fMin} onChange={(e) => setFMin(e.target.value)}
                  className="w-full rounded-lg border border-white/10 bg-white/[0.04] px-2 py-3 text-center outline-none placeholder:text-white/25 focus:border-volt"
                />
                <span className="text-white/40">&apos;</span>
                <input
                  type="number" inputMode="numeric" placeholder="30" value={fSec} onChange={(e) => setFSec(e.target.value)}
                  className="w-full rounded-lg border border-white/10 bg-white/[0.04] px-2 py-3 text-center outline-none placeholder:text-white/25 focus:border-volt"
                />
                <span className="text-white/40">&quot;</span>
              </div>
            </label>
          </div>
        </div>
        <PillButton className="mt-5 w-full" onClick={submitLog}>저장 ✅</PillButton>
      </BottomSheet>

      {/* 목표 변경 시트 */}
      <BottomSheet open={showGoal} onClose={() => setShowGoal(false)}>
        <h3 className="text-lg font-extrabold">올해 목표 거리</h3>
        <div className="mt-4 grid grid-cols-5 gap-2">
          {GOALS.map((g) => (
            <button
              key={g}
              onClick={() => { setRunGoal(g); setShowGoal(false); }}
              className={`rounded-xl border py-3 font-display text-[15px] ${
                goal === g ? "border-volt bg-volt/15 text-volt" : "border-white/10 bg-white/[0.04]"
              }`}
            >
              {g}
            </button>
          ))}
        </div>
        <p className="mt-3 text-[11.5px] text-white/40">단위: km · 연간 누적 기준</p>
      </BottomSheet>

      <SettingsSheet
        open={showSettings}
        onClose={() => setShowSettings(false)}
        primaryMode={user.v2?.primaryMode ?? "gym"}
        onChangeMode={setPrimaryMode}
        onLogout={logout}
      />

      <RunDetailSheet run={detail} onClose={() => setDetail(null)} onDelete={(r) => deleteRun(r as Run)} />
    </main>
  );
}
