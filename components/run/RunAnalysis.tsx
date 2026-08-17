"use client";
// 러닝 상세 분석 — 분석 탭 러닝 세그먼트 (러닝 탭=모니터링, 여기=디테일 분석 전부)
import { useMemo, useState } from "react";
import {
  Bar, BarChart, Cell, ComposedChart, Line, LineChart, Scatter, ScatterChart, ResponsiveContainer, Tooltip, XAxis, YAxis, ZAxis,
} from "recharts";
import { StatChip } from "@/components/ui/StatChip";
import { ShibaRest } from "@/components/mascot/ShibaPoses";
import { allBests } from "@/lib/runmath";
import { Icon } from "@/components/ui/Icon";

type Run = { rid?: string; date: string; km: number; paceSec?: number | null; durSec?: number; route?: number[][] };
const paceStr = (sec?: number | null) =>
  sec ? `${Math.floor(sec / 60)}'${String(Math.round(sec % 60)).padStart(2, "0")}"` : "—";
const r1 = (x: number) => Math.round(x * 10) / 10;

function Card({ title, sub, children, className = "" }: { title: string; sub?: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={`rounded-xl border border-white/[0.07] bg-card p-4 ${className}`}>
      <b className="text-[14.5px] font-extrabold">{title}</b>
      {sub && <p className="mt-0.5 text-[11.5px] text-white/45">{sub}</p>}
      <div className="mt-3">{children}</div>
    </div>
  );
}

export function RunAnalysis({ runs }: { runs: Run[] }) {
  const [distTab, setDistTab] = useState<"dist" | "zone">("dist");
  const bests = useMemo(() => allBests(runs), [runs]);
  const a = useMemo(() => {
    const now = new Date();
    const y = now.getFullYear();
    const paced = runs.filter((r) => r.paceSec);
    const scatter = paced.map((r) => ({ km: r.km, sec: r.paceSec! }));

    // 요약
    const total = r1(runs.reduce((s, r) => s + r.km, 0));
    const yearKm = r1(runs.filter((r) => r.date.startsWith(String(y))).reduce((s, r) => s + r.km, 0));
    const avgPace = paced.length ? Math.round(paced.reduce((s, r) => s + r.paceSec!, 0) / paced.length) : null;
    const bestPace = paced.length ? Math.min(...paced.map((r) => r.paceSec!)) : null;
    const longest = runs.length ? Math.max(...runs.map((r) => r.km)) : 0;

    // 거리 분포·존·요일·월별페이스
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
    const bestDow = dow.filter((d) => d.avg).sort((x, z) => x.avg! - z.avg!)[0];
    const zones = [
      { l: `5'00" 미만`, min: 0, max: 300 }, { l: `5'00"~5'30"`, min: 300, max: 330 },
      { l: `5'30"~6'00"`, min: 330, max: 360 }, { l: `6'00"~6'30"`, min: 360, max: 390 },
      { l: `6'30" 이상`, min: 390, max: 99999 },
    ].map((z) => ({ l: z.l, n: paced.filter((r) => r.paceSec! >= z.min && r.paceSec! < z.max).length }));
    const maxZone = Math.max(1, ...zones.map((z) => z.n));
    const monthlyPace = Array.from({ length: 12 }, (_, i) => {
      const xs = paced.filter((r) => r.date.startsWith(`${y}-${String(i + 1).padStart(2, "0")}`));
      return { m: `${i + 1}월`, sec: xs.length ? Math.round(xs.reduce((s2, r) => s2 + r.paceSec!, 0) / xs.length) : null };
    }).filter((x) => x.sec != null);

    // 월별 거리 + 올해 누적
    const monthly = Array.from({ length: 12 }, (_, i) => ({
      m: `${i + 1}월`,
      km: r1(runs.filter((r) => r.date.startsWith(`${y}-${String(i + 1).padStart(2, "0")}`)).reduce((s, r) => s + r.km, 0)),
      isNow: i === now.getMonth(),
    }));
    let acc = 0;
    const cum = monthly.map((m, i) => (i <= now.getMonth() ? ((acc = r1(acc + m.km)), { m: m.m, km: acc }) : { m: m.m, km: null as number | null }));

    // 주 시작 키
    const wkStart = (ds: string) => { const d = new Date(ds + "T00:00:00"); d.setDate(d.getDate() - ((d.getDay() + 6) % 7)); d.setHours(0, 0, 0, 0); return d.getTime(); };
    const mon0 = new Date(now); mon0.setDate(now.getDate() - ((now.getDay() + 6) % 7)); mon0.setHours(0, 0, 0, 0);

    // 주간 거리 12주 + 히트맵 12주
    const weekly = Array.from({ length: 12 }, (_, i) => {
      const st = new Date(mon0); st.setDate(mon0.getDate() - (11 - i) * 7);
      return { w: `${st.getMonth() + 1}/${st.getDate()}`, km: 0, isNow: i === 11 };
    });
    runs.forEach((r) => {
      const diff = Math.round((mon0.getTime() - wkStart(r.date)) / (7 * 864e5));
      if (diff >= 0 && diff < 12) weekly[11 - diff].km = r1(weekly[11 - diff].km + r.km);
    });

    // 페이스 발전 흐름 (최근 20회)
    const paceSeries = paced.slice(-20).map((r) => ({ d: r.date.slice(5), sec: r.paceSec! }));

    // AI 코치 — 최근 4주 vs 이전 4주 / 페이스 추세 / 10% 룰
    const kmIn = (from: number, to: number) => r1(runs.filter((r) => { const t = new Date(r.date + "T00:00:00").getTime(); return t >= from && t < to; }).reduce((s, r) => s + r.km, 0));
    const nowT = now.getTime();
    const last4 = kmIn(nowT - 28 * 864e5, nowT + 864e5);
    const prev4 = kmIn(nowT - 56 * 864e5, nowT - 28 * 864e5);
    const mileageDelta = prev4 > 0 ? Math.round(((last4 - prev4) / prev4) * 100) : null;
    const rc = paced.slice(-5), bf = paced.slice(-10, -5);
    const avg = (xs: Run[]) => (xs.length ? xs.reduce((s, r) => s + r.paceSec!, 0) / xs.length : null);
    const pN = avg(rc), pP = avg(bf);
    const paceTrend = pN && pP ? Math.round(pP - pN) : null;
    const nextTarget = r1(Math.max(last4 / 4, 3) * 1.1);

    // 월별 막대 + 누적 선을 한 차트에 넣기 위한 합침 (값 자체는 monthly·cum 그대로)
    const monthlyCombo = monthly.map((m, i) => ({ m: m.m, km: m.km, isNow: m.isNow, cum: cum[i].km }));
    const thisMonthKm = monthly[now.getMonth()].km;

    return {
      count: runs.length, total, yearKm, avgPace, bestPace, longest,
      monthlyCombo, thisMonthKm,
      buckets, maxBucket, dow, bestDow, zones, maxZone, monthlyPace,
      scatter, monthly, cum, weekly, paceSeries,
      last4, mileageDelta, paceTrend, nextTarget,
    };
  }, [runs]);

  if (a.count === 0) {
    return (
      <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-white/15 bg-white/[0.02] px-6 py-8 text-center">
        <ShibaRest size={92} />
        <p className="text-[13px] text-white/50">아직 러닝 기록이 없어요.<br />러닝 탭에서 첫 기록을 남기면 상세 분석이 채워집니다.</p>
      </div>
    );
  }

  const axis = { fill: "rgba(255,255,255,0.4)", fontSize: 9 } as const;
  const tip = { background: "#121212", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 } as const;

  return (
    <div className="space-y-4">
      {/* 요약 — 러닝 탭에 이미 있는 총 거리·최장 거리는 빼고, 분석에서만 의미 있는 값만 */}
      <div className="grid grid-cols-3 gap-2">
        <StatChip label="평균 페이스" value={paceStr(a.avgPace)} tone="mute" />
        <StatChip label="최고 페이스" value={paceStr(a.bestPace)} tone="gold" />
        <StatChip label="최근 4주" value={a.last4} unit="km" tone="volt" />
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        {/* 월별 거리 + 올해 누적 — 같은 축의 이야기라 한 장에 합침 (막대=월별, 선=누적) */}
        <Card title="월별 거리와 누적" sub={`${new Date().getFullYear()}년 · 막대 월 합계 / 선 누적 (km)`} className="lg:col-span-2">
          <div className="h-44">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={a.monthlyCombo} margin={{ top: 6, right: 4, left: -24 }}>
                <XAxis dataKey="m" tick={{ ...axis, fontSize: 8.5 }} axisLine={false} tickLine={false} interval={0} />
                <YAxis yAxisId="l" tick={axis} axisLine={false} tickLine={false} />
                <YAxis yAxisId="r" orientation="right" tick={axis} axisLine={false} tickLine={false} width={34} />
                <Tooltip
                  cursor={{ fill: "rgba(255,255,255,0.04)" }} contentStyle={tip}
                  formatter={(v, n) => [`${Number(v ?? 0)}km`, n === "cum" ? "누적" : "월 거리"]}
                />
                <Bar yAxisId="l" dataKey="km" radius={[3, 3, 0, 0]} isAnimationActive={false}>
                  {a.monthlyCombo.map((x, i) => <Cell key={i} fill={x.isNow ? "#c8ff00" : "rgba(255,255,255,0.18)"} />)}
                </Bar>
                <Line yAxisId="r" type="monotone" dataKey="cum" stroke="#f59e0b" strokeWidth={2.2} dot={false} connectNulls={false} isAnimationActive={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
          <p className="mt-2 text-[11px] text-white/40">
            올해 누적 <b className="text-gold tabular-nums">{a.yearKm}km</b> · 이번 달 <b className="text-volt tabular-nums">{a.thisMonthKm}km</b>
          </p>
        </Card>

        {/* 주간 러닝 거리 */}
        <Card title="주간 러닝 거리" sub="최근 12주 · 주별 합계 (km)">
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={a.weekly} margin={{ top: 6, right: 0, left: -26 }}>
                <XAxis dataKey="w" tick={{ ...axis, fontSize: 8 }} axisLine={false} tickLine={false} interval={1} />
                <YAxis tick={axis} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: "rgba(255,255,255,0.04)" }} contentStyle={tip} formatter={(v) => [`${Number(v ?? 0)}km`, "거리"]} />
                <Bar dataKey="km" radius={[3, 3, 0, 0]} isAnimationActive={false}>
                  {a.weekly.map((x, i) => <Cell key={i} fill={x.isNow ? "#c8ff00" : "rgba(255,255,255,0.18)"} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* 페이스 발전 흐름 */}
        <Card title="페이스 발전 흐름" sub={`최근 ${a.paceSeries.length}회 · 위로 갈수록 빠름`}>
          {a.paceSeries.length >= 2 ? (
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={a.paceSeries} margin={{ top: 8, right: 8, left: -8 }}>
                  <XAxis dataKey="d" tick={axis} axisLine={false} tickLine={false} />
                  <YAxis reversed domain={["dataMin - 15", "dataMax + 15"]} tickFormatter={(v) => paceStr(Number(v))} tick={axis} axisLine={false} tickLine={false} width={44} />
                  <Tooltip contentStyle={tip} formatter={(v) => [`${paceStr(Number(v))}/km`, "페이스"]} />
                  <Line type="monotone" dataKey="sec" stroke="#c8ff00" strokeWidth={2.5} dot={{ r: 2.5, fill: "#c8ff00" }} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : <p className="py-4 text-center text-[12.5px] text-white/40">기록이 2회 이상 쌓이면 나와요</p>}
        </Card>

        {/* 거리별 최고 페이스 (PB) */}
        <Card title="거리별 최고 페이스" sub="구간별 나의 개인 기록 (PB)">
          <div className="grid grid-cols-2 gap-2">
            {bests.map((b) => (
              <div key={b.m} className="rounded-lg bg-white/[0.05] px-3 py-2.5">
                <div className="flex items-baseline justify-between">
                  <span className="text-[12px] font-bold text-white/55">{b.m / 1000}km</span>
                  <b className={`font-display text-[15px] tabular-nums ${b.paceSec ? "text-gold" : "text-white/25"}`}>{b.paceSec ? paceStr(b.paceSec) : "도전!"}</b>
                </div>
                <div className="mt-0.5 text-right text-[9px] text-white/35">{b.date ? `${b.date}` : `${b.m / 1000}km 이상 뛰면 기록`}</div>
              </div>
            ))}
          </div>
        </Card>

        {/* 거리 분포 + 페이스 존 — 둘 다 "주로 어디에 몰려 있나"라 한 장에서 전환 */}
        <Card title="주로 달리는 구간" sub={`총 ${a.count}회`}>
          <div className="mb-3 grid grid-cols-2 gap-1 rounded-lg border border-white/10 bg-white/[0.04] p-1">
            {([["dist", "거리대"], ["zone", "페이스대"]] as const).map(([v, l]) => (
              <button
                key={v}
                onClick={() => setDistTab(v)}
                className={`rounded-md py-1.5 text-[12.5px] font-bold ${distTab === v ? "bg-volt text-black" : "text-white/50"}`}
              >
                {l}
              </button>
            ))}
          </div>
          {distTab === "dist" ? (
            <div className="space-y-2">
              {a.buckets.map((b) => (
                <div key={b.l} className="flex items-center gap-2.5">
                  <span className="w-14 shrink-0 text-[11.5px] font-bold text-white/60">{b.l}</span>
                  <div className="h-3.5 flex-1 overflow-hidden rounded-full bg-white/[0.06]"><div className="h-full rounded-full bg-volt" style={{ width: `${(b.n / a.maxBucket) * 100}%` }} /></div>
                  <b className="w-9 shrink-0 text-right text-[12px] tabular-nums">{b.n}회</b>
                </div>
              ))}
            </div>
          ) : a.zones.some((z) => z.n > 0) ? (
            <div className="space-y-2">
              {a.zones.map((z) => (
                <div key={z.l} className="flex items-center gap-2.5">
                  <span className="w-24 shrink-0 text-[11.5px] font-bold tabular-nums text-white/60">{z.l}</span>
                  <div className="h-3.5 flex-1 overflow-hidden rounded-full bg-white/[0.06]"><div className="h-full rounded-full bg-volt" style={{ width: `${(z.n / a.maxZone) * 100}%` }} /></div>
                  <b className="w-9 shrink-0 text-right text-[12px] tabular-nums">{z.n}회</b>
                </div>
              ))}
            </div>
          ) : <p className="py-4 text-center text-[12.5px] text-white/40">페이스가 있는 기록이 아직 없어요</p>}
        </Card>

        {/* 세부 차트 — 매번 볼 필요는 없어 접어둔다 (펼치면 그대로) */}
        <details className="group rounded-xl border border-white/[0.07] bg-card lg:col-span-2">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-3 p-4">
            <span className="text-[13.5px] font-extrabold">세부 차트</span>
            <span className="flex min-w-0 items-center gap-2 text-[11.5px] text-white/40">
              <span className="truncate">요일별 · 거리별 페이스 · 월별 추이</span>
              <Icon name="chevronRight" size={15} className="shrink-0 transition-transform group-open:rotate-90" />
            </span>
          </summary>
          <div className="grid gap-3 border-t border-white/[0.07] p-4 lg:grid-cols-2">
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
                  <XAxis dataKey="km" name="거리" unit="km" type="number" tick={axis} axisLine={false} tickLine={false} />
                  <YAxis dataKey="sec" name="페이스" type="number" reversed domain={["dataMin - 15", "dataMax + 15"]} tickFormatter={(v) => paceStr(Number(v))} tick={axis} axisLine={false} tickLine={false} width={44} />
                  <ZAxis range={[70, 71]} />
                  <Tooltip contentStyle={tip} formatter={(v, n) => (n === "페이스" ? [`${paceStr(Number(v))}/km`, n] : [`${v}km`, n])} />
                  <Scatter data={a.scatter} fill="#c8ff00" fillOpacity={0.85} isAnimationActive={false} />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          ) : <p className="py-4 text-center text-[12.5px] text-white/40">페이스 기록이 3개 이상 쌓이면 나와요</p>}
        </Card>

        {/* 월별 페이스 추이 */}
        <Card title="월별 페이스 추이" sub="달이 갈수록 빨라지는지 · 위로 갈수록 빠름">
          {a.monthlyPace.length >= 2 ? (
            <div className="h-44">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={a.monthlyPace} margin={{ top: 8, right: 8, left: -8 }}>
                  <XAxis dataKey="m" tick={axis} axisLine={false} tickLine={false} />
                  <YAxis reversed domain={["dataMin - 15", "dataMax + 15"]} tickFormatter={(v) => paceStr(Number(v))} tick={axis} axisLine={false} tickLine={false} width={44} />
                  <Tooltip contentStyle={tip} formatter={(v) => [`${paceStr(Number(v))}/km`, "평균 페이스"]} />
                  <Line type="monotone" dataKey="sec" stroke="#c8ff00" strokeWidth={2.5} dot={{ r: 3, fill: "#c8ff00" }} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : <p className="py-4 text-center text-[12.5px] text-white/40">두 달 이상 기록이 쌓이면 추이가 나와요</p>}
        </Card>
          </div>
        </details>

        {/* 주간 마일리지 진단 — 앱 팔레트 유지(별도 색으로 격리하지 않음) */}
        <div className="rounded-xl border border-white/[0.07] bg-card p-4 lg:col-span-2">
          <b className="text-[14.5px] font-extrabold">주간 마일리지 진단</b>
          <p className="mt-0.5 text-[11.5px] text-white/45">최근 기록 기반 맞춤 피드백</p>
          <div className="mt-3 grid gap-2 lg:grid-cols-3">
            <div className="rounded-lg bg-white/[0.05] p-3">
              <div className="lab">최근 4주</div>
              <p className="mt-1 text-[12.5px] leading-relaxed text-white/75">
                최근 4주 <b className="text-gold">{a.last4}km</b>{" "}
                {a.mileageDelta == null ? "— 비교할 이전 기록이 더 필요해요."
                  : a.mileageDelta > 15 ? <>— 이전보다 <b className="text-danger">{a.mileageDelta}%</b> 급증. 부상 위험, 주 10% 이내로.</>
                  : a.mileageDelta >= 0 ? <>— 이전보다 <b className="text-volt">{a.mileageDelta}%</b> 증가. 좋은 페이스예요.</>
                  : <>— 이전보다 {Math.abs(a.mileageDelta)}% 감소. 회복 주간일 수 있어요.</>}
              </p>
            </div>
            <div className="rounded-lg bg-white/[0.05] p-3">
              <div className="lab">페이스 추세</div>
              <p className="mt-1 text-[12.5px] leading-relaxed text-white/75">
                {a.paceTrend == null ? "기록이 더 쌓이면 추세를 알려드릴게요."
                  : a.paceTrend > 3 ? <>최근 <b className="text-volt">{a.paceTrend}초/km</b> 빨라졌어요 — 좋아요!</>
                  : a.paceTrend < -3 ? <>페이스가 {Math.abs(a.paceTrend)}초/km 느려졌어요 — 회복 주간일 수 있어요.</>
                  : "페이스를 안정적으로 유지 중이에요."}
              </p>
            </div>
            <div className="rounded-lg bg-white/[0.05] p-3">
              <div className="lab">다음 4주 권장</div>
              <p className="mt-1 text-[12.5px] leading-relaxed text-white/75">
                주당 <b className="text-gold">{a.nextTarget}km</b> 수준으로 10% 이내에서 서서히 올려보세요.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
