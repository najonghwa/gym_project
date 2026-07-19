"use client";
// 러닝 상세 분석 — 분석 탭 러닝 세그먼트 (모니터링은 러닝 탭, 디테일은 여기)
import { useMemo } from "react";
import {
  Bar, BarChart, Cell, Line, LineChart, Scatter, ScatterChart, ResponsiveContainer, Tooltip, XAxis, YAxis, ZAxis,
} from "recharts";
import { StatChip } from "@/components/ui/StatChip";
import { allBests } from "@/lib/runmath";

type Run = { rid?: string; date: string; km: number; paceSec?: number | null; durSec?: number; route?: number[][] };
const paceStr = (sec?: number | null) =>
  sec ? `${Math.floor(sec / 60)}'${String(Math.round(sec % 60)).padStart(2, "0")}"` : "—";
const r1 = (x: number) => Math.round(x * 10) / 10;

// 서술형 타이틀 카드 (질문형 폐기)
function Card({ title, sub, children }: { title: string; sub?: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-card p-4">
      <b className="text-[14.5px] font-extrabold">{title}</b>
      {sub && <p className="mt-0.5 text-[11.5px] text-white/45">{sub}</p>}
      <div className="mt-3">{children}</div>
    </div>
  );
}

export function RunAnalysis({ runs }: { runs: Run[] }) {
  const bests = useMemo(() => allBests(runs), [runs]);
  const a = useMemo(() => {
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
      return { l, avg: xs.length ? Math.round(xs.reduce((s2, r) => s2 + r.paceSec!, 0) / xs.length) : null, n: xs.length };
    });
    const bestDow = dow.filter((d) => d.avg).sort((x, y) => x.avg! - y.avg!)[0];
    const zones = [
      { l: `5'00" 미만`, min: 0, max: 300 }, { l: `5'00"~5'30"`, min: 300, max: 330 },
      { l: `5'30"~6'00"`, min: 330, max: 360 }, { l: `6'00"~6'30"`, min: 360, max: 390 },
      { l: `6'30" 이상`, min: 390, max: 99999 },
    ].map((z) => ({ l: z.l, n: paced.filter((r) => r.paceSec! >= z.min && r.paceSec! < z.max).length }));
    const maxZone = Math.max(1, ...zones.map((z) => z.n));
    const yy = new Date().getFullYear();
    const monthlyPace = Array.from({ length: 12 }, (_, i) => {
      const xs = paced.filter((r) => r.date.startsWith(`${yy}-${String(i + 1).padStart(2, "0")}`));
      return { m: `${i + 1}월`, sec: xs.length ? Math.round(xs.reduce((s2, r) => s2 + r.paceSec!, 0) / xs.length) : null };
    }).filter((x) => x.sec != null);

    // 주간 러닝 거리 (최근 8주)
    const now = new Date();
    const mon0 = new Date(now); mon0.setDate(now.getDate() - ((now.getDay() + 6) % 7)); mon0.setHours(0, 0, 0, 0);
    const weekly = Array.from({ length: 8 }, (_, i) => {
      const st = new Date(mon0); st.setDate(mon0.getDate() - (7 - i) * 7);
      return { w: `${st.getMonth() + 1}/${st.getDate()}`, km: 0, isNow: i === 7 };
    });
    runs.forEach((r) => {
      const d = new Date(r.date + "T00:00:00");
      const wk = new Date(d); wk.setDate(d.getDate() - ((d.getDay() + 6) % 7)); wk.setHours(0, 0, 0, 0);
      const diff = Math.round((mon0.getTime() - wk.getTime()) / (7 * 864e5));
      if (diff >= 0 && diff < 8) weekly[7 - diff].km = r1(weekly[7 - diff].km + r.km);
    });

    // 요약
    const total = r1(runs.reduce((s, r) => s + r.km, 0));
    const avgPace = paced.length ? Math.round(paced.reduce((s, r) => s + r.paceSec!, 0) / paced.length) : null;
    const bestPace = paced.length ? Math.min(...paced.map((r) => r.paceSec!)) : null;
    const longest = runs.length ? Math.max(...runs.map((r) => r.km)) : 0;
    const yearKm = r1(runs.filter((r) => r.date.startsWith(String(yy))).reduce((s, r) => s + r.km, 0));

    return { count: runs.length, scatter, buckets, maxBucket, dow, bestDow, zones, maxZone, monthlyPace, weekly, total, avgPace, bestPace, longest, yearKm };
  }, [runs]);

  if (a.count === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-white/15 bg-white/[0.02] px-6 py-10 text-center">
        <p className="text-[13px] text-white/50">아직 러닝 기록이 없어요.<br />러닝 탭에서 첫 기록을 남기면 상세 분석이 채워집니다.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 요약 스트립 */}
      <div className="grid grid-cols-3 gap-2 lg:grid-cols-6">
        <StatChip label="총 러닝" value={a.count} unit="회" tone="volt" />
        <StatChip label="총 거리" value={a.total} unit="km" tone="mute" />
        <StatChip label="올해" value={a.yearKm} unit="km" tone="mute" />
        <StatChip label="평균 페이스" value={paceStr(a.avgPace)} tone="mute" />
        <StatChip label="최고 페이스" value={paceStr(a.bestPace)} tone="gold" />
        <StatChip label="최장 거리" value={a.longest} unit="km" tone="gold" />
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        {/* 거리별 최고 페이스 (PB) — 항상 뭔가 보임 */}
        <Card title="거리별 최고 페이스" sub="구간별 나의 개인 기록 (PB)">
          <div className="grid grid-cols-2 gap-2">
            {bests.map((b) => (
              <div key={b.m} className="rounded-lg bg-white/[0.05] px-3 py-2.5">
                <div className="flex items-baseline justify-between">
                  <span className="text-[12px] font-bold text-white/55">{b.m / 1000}km</span>
                  <b className={`font-display text-[15px] tabular-nums ${b.paceSec ? "text-gold" : "text-white/25"}`}>
                    {b.paceSec ? paceStr(b.paceSec) : "도전!"}
                  </b>
                </div>
                <div className="mt-0.5 text-right text-[9px] text-white/35">
                  {b.date ? `${b.gps ? "📡" : "✍️"} ${b.date}` : `${b.m / 1000}km 이상 뛰면 기록`}
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* 주간 러닝 거리 */}
        <Card title="주간 러닝 거리" sub="최근 8주 · 주별 합계 (km)">
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={a.weekly} margin={{ top: 6, right: 0, left: -26 }}>
                <XAxis dataKey="w" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 8.5 }} axisLine={false} tickLine={false} interval={0} />
                <YAxis tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: "rgba(255,255,255,0.04)" }}
                  contentStyle={{ background: "#121212", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }}
                  formatter={(v) => [`${Number(v ?? 0)}km`, "거리"]} />
                <Bar dataKey="km" radius={[3, 3, 0, 0]} isAnimationActive={false}>
                  {a.weekly.map((x, i) => <Cell key={i} fill={x.isNow ? "#c8ff00" : "rgba(255,255,255,0.18)"} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* 거리 분포 */}
        <Card title="거리 분포" sub={`총 ${a.count}회 · 주로 달리는 거리대`}>
          <div className="space-y-2">
            {a.buckets.map((b) => (
              <div key={b.l} className="flex items-center gap-2.5">
                <span className="w-14 shrink-0 text-[11.5px] font-bold text-white/60">{b.l}</span>
                <div className="h-3.5 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
                  <div className="h-full rounded-full bg-volt" style={{ width: `${(b.n / a.maxBucket) * 100}%` }} />
                </div>
                <b className="w-9 shrink-0 text-right text-[12px] tabular-nums">{b.n}회</b>
              </div>
            ))}
          </div>
        </Card>

        {/* 페이스 존 분포 */}
        <Card title="페이스 존 분포" sub="어느 속도대에서 주로 달리는지">
          {a.zones.some((z) => z.n > 0) ? (
            <div className="space-y-2">
              {a.zones.map((z) => (
                <div key={z.l} className="flex items-center gap-2.5">
                  <span className="w-24 shrink-0 text-[11.5px] font-bold tabular-nums text-white/60">{z.l}</span>
                  <div className="h-3.5 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
                    <div className="h-full rounded-full bg-volt" style={{ width: `${(z.n / a.maxZone) * 100}%` }} />
                  </div>
                  <b className="w-9 shrink-0 text-right text-[12px] tabular-nums">{z.n}회</b>
                </div>
              ))}
            </div>
          ) : <p className="py-4 text-center text-[12.5px] text-white/40">페이스가 있는 기록이 아직 없어요</p>}
        </Card>

        {/* 요일별 평균 페이스 */}
        <Card title="요일별 평균 페이스" sub="가장 잘 달리는 요일 찾기">
          <div className="grid grid-cols-7 gap-1.5">
            {a.dow.map((d) => (
              <div key={d.l} className={`rounded-lg border py-2.5 text-center ${a.bestDow && d.l === a.bestDow.l ? "border-volt/60 bg-volt/10" : "border-white/[0.06] bg-white/[0.03]"}`}>
                <div className="text-[10px] text-white/45">{d.l}</div>
                <div className={`mt-1 text-[11px] font-extrabold tabular-nums ${d.avg ? "" : "text-white/20"}`}>{d.avg ? paceStr(d.avg) : "·"}</div>
                {d.n > 0 && <div className="text-[8.5px] text-white/35">{d.n}회</div>}
              </div>
            ))}
          </div>
          {a.bestDow && <p className="mt-2.5 text-center text-[12px] text-white/55"><b className="text-volt">{a.bestDow.l}요일</b>에 가장 빨라요 ({paceStr(a.bestDow.avg)})</p>}
        </Card>

        {/* 페이스 vs 거리 */}
        <Card title="페이스 vs 거리" sub="거리가 길어질 때 페이스 변화 · 위로 갈수록 빠름">
          {a.scatter.length >= 3 ? (
            <div className="h-44">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 8, right: 10, left: -8 }}>
                  <XAxis dataKey="km" name="거리" unit="km" type="number" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} />
                  <YAxis dataKey="sec" name="페이스" type="number" reversed domain={["dataMin - 15", "dataMax + 15"]} tickFormatter={(v) => paceStr(Number(v))} tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} width={44} />
                  <ZAxis range={[70, 71]} />
                  <Tooltip contentStyle={{ background: "#121212", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }} formatter={(v, n) => (n === "페이스" ? [`${paceStr(Number(v))}/km`, n] : [`${v}km`, n])} />
                  <Scatter data={a.scatter} fill="#c8ff00" fillOpacity={0.85} isAnimationActive={false} />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          ) : <p className="py-4 text-center text-[12.5px] text-white/40">페이스 기록이 3개 이상 쌓이면 나와요</p>}
        </Card>

        {/* 월별 평균 페이스 추이 */}
        <Card title="월별 페이스 추이" sub="달이 갈수록 빨라지는지 · 위로 갈수록 빠름">
          {a.monthlyPace.length >= 2 ? (
            <div className="h-44">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={a.monthlyPace} margin={{ top: 8, right: 8, left: -8 }}>
                  <XAxis dataKey="m" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} />
                  <YAxis reversed domain={["dataMin - 15", "dataMax + 15"]} tickFormatter={(v) => paceStr(Number(v))} tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} width={44} />
                  <Tooltip contentStyle={{ background: "#121212", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }} formatter={(v) => [`${paceStr(Number(v))}/km`, "평균 페이스"]} />
                  <Line type="monotone" dataKey="sec" stroke="#c8ff00" strokeWidth={2.5} dot={{ r: 3, fill: "#c8ff00" }} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : <p className="py-4 text-center text-[12.5px] text-white/40">두 달 이상 기록이 쌓이면 추이가 나와요</p>}
        </Card>
      </div>
    </div>
  );
}
