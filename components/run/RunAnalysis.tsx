"use client";
// 러닝 상세 분석 5카드 — 분석 탭 러닝 세그먼트용 (모니터링은 러닝 탭, 디테일은 여기)
import { useMemo } from "react";
import {
  Line, LineChart, Scatter, ScatterChart, ResponsiveContainer, Tooltip, XAxis, YAxis, ZAxis,
} from "recharts";
import { AnalysisCard } from "@/components/analysis/AnalysisCard";

type Run = { date: string; km: number; paceSec?: number | null };
const paceStr = (sec?: number | null) =>
  sec ? `${Math.floor(sec / 60)}'${String(Math.round(sec % 60)).padStart(2, "0")}"` : "—";

export function RunAnalysis({ runs }: { runs: Run[] }) {
  const anal = useMemo(() => {
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
    const bestDow = dow.filter((d) => d.avg).sort((a, b) => a.avg! - b.avg!)[0];
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
    return { count: runs.length, scatter, buckets, maxBucket, dow, bestDow, zones, maxZone, monthlyPace };
  }, [runs]);

  return (
    <div className="grid gap-3 lg:grid-cols-2">
      {/* 페이스 × 거리 산점도 */}
      <AnalysisCard question="거리가 길어지면 페이스가 얼마나 떨어질까?">
        {anal.scatter.length >= 3 ? (
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 8, right: 10, left: -8 }}>
                <XAxis dataKey="km" name="거리" unit="km" type="number"
                  tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} />
                <YAxis dataKey="sec" name="페이스" type="number" reversed domain={["dataMin - 15", "dataMax + 15"]}
                  tickFormatter={(v) => paceStr(Number(v))}
                  tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} width={44} />
                <ZAxis range={[70, 71]} />
                <Tooltip
                  contentStyle={{ background: "#121212", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }}
                  formatter={(v, n) => (n === "페이스" ? [`${paceStr(Number(v))}/km`, n] : [`${v}km`, n])}
                />
                <Scatter data={anal.scatter} fill="#c8ff00" fillOpacity={0.85} isAnimationActive={false} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="py-4 text-center text-[12.5px] text-white/40">페이스 기록이 3개 이상 쌓이면 나와요 · 위로 갈수록 빠름</p>
        )}
      </AnalysisCard>

      {/* 거리 분포 */}
      <AnalysisCard question="나는 주로 몇 km를 달릴까?">
        {anal.count > 0 ? (
          <>
            <div className="space-y-2">
              {anal.buckets.map((b) => (
                <div key={b.l} className="flex items-center gap-2.5">
                  <span className="w-14 shrink-0 text-[11.5px] font-bold text-white/60">{b.l}</span>
                  <div className="h-3.5 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
                    <div className="h-full rounded-full bg-volt" style={{ width: `${(b.n / anal.maxBucket) * 100}%` }} />
                  </div>
                  <b className="w-9 shrink-0 text-right text-[12px] tabular-nums">{b.n}회</b>
                </div>
              ))}
            </div>
            <p className="mt-2.5 text-[11.5px] text-white/45">
              총 {anal.count}회 — 편한 거리에 머물러 있다면 가끔 한 구간 위를 노려보세요
            </p>
          </>
        ) : (
          <p className="py-4 text-center text-[12.5px] text-white/40">아직 기록이 없어요</p>
        )}
      </AnalysisCard>

      {/* 요일별 평균 페이스 */}
      <AnalysisCard question="어느 요일에 제일 잘 달릴까?">
        <div className="grid grid-cols-7 gap-1.5">
          {anal.dow.map((d) => (
            <div
              key={d.l}
              className={`rounded-lg border py-2.5 text-center ${
                anal.bestDow && d.l === anal.bestDow.l ? "border-volt/60 bg-volt/10" : "border-white/[0.06] bg-white/[0.03]"
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
        {anal.bestDow && (
          <p className="mt-2.5 text-center text-[12px] text-white/55">
            <b className="text-volt">{anal.bestDow.l}요일</b>에 가장 빨라요 ({paceStr(anal.bestDow.avg)}) — 중요한 러닝은 이날에!
          </p>
        )}
      </AnalysisCard>

      {/* 페이스 존 분포 */}
      <AnalysisCard question="나는 주로 어떤 페이스로 달릴까?">
        {anal.zones.some((z) => z.n > 0) ? (
          <div className="space-y-2">
            {anal.zones.map((z) => (
              <div key={z.l} className="flex items-center gap-2.5">
                <span className="w-24 shrink-0 text-[11.5px] font-bold tabular-nums text-white/60">{z.l}</span>
                <div className="h-3.5 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
                  <div className="h-full rounded-full bg-volt" style={{ width: `${(z.n / anal.maxZone) * 100}%` }} />
                </div>
                <b className="w-9 shrink-0 text-right text-[12px] tabular-nums">{z.n}회</b>
              </div>
            ))}
          </div>
        ) : (
          <p className="py-4 text-center text-[12.5px] text-white/40">페이스가 있는 기록이 아직 없어요</p>
        )}
      </AnalysisCard>

      {/* 월별 평균 페이스 */}
      <AnalysisCard question="달이 갈수록 빨라지고 있을까?">
        {anal.monthlyPace.length >= 2 ? (
          <div className="h-44">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={anal.monthlyPace} margin={{ top: 8, right: 8, left: -8 }}>
                <XAxis dataKey="m" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} />
                <YAxis
                  reversed domain={["dataMin - 15", "dataMax + 15"]}
                  tickFormatter={(v) => paceStr(Number(v))}
                  tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} width={44}
                />
                <Tooltip
                  contentStyle={{ background: "#121212", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }}
                  formatter={(v) => [`${paceStr(Number(v))}/km`, "평균 페이스"]}
                />
                <Line type="monotone" dataKey="sec" stroke="#c8ff00" strokeWidth={2.5} dot={{ r: 3, fill: "#c8ff00" }} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="py-4 text-center text-[12.5px] text-white/40">두 달 이상 기록이 쌓이면 추이가 나와요 · 위로 갈수록 빠름</p>
        )}
      </AnalysisCard>
    </div>
  );
}
