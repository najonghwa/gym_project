"use client";
// PR 막대 차트 — 기본 volt, PR 막대만 gold + 🏅 (스펙 P0-3)
import { useMemo, useState } from "react";
import {
  Bar, BarChart, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis,
} from "recharts";
import { useReducedMotion } from "framer-motion";
import { getMockPR, PRRow } from "@/lib/mock/exercises";

const METRICS = [
  { id: "1rm", t: "1RM", chip: "BEST 1RM" },
  { id: "weight", t: "최고중량", chip: "MAX WEIGHT" },
  { id: "volume", t: "볼륨", chip: "MAX VOLUME" },
] as const;
type Metric = (typeof METRICS)[number]["id"];

export function PRChart({ rows }: { rows?: PRRow[] }) {
  const reduce = useReducedMotion();
  const [metric, setMetric] = useState<Metric>("1rm");
  const data = useMemo(() => rows ?? getMockPR(metric), [rows, metric]);
  const best = Math.max(...data.map((d) => d.value));
  const unit = metric === "volume" ? "kg·vol" : "kg";
  // 주의: 차트 자체에서 confetti 금지 — 마운트/전환마다 터져서 스팸이 됨.
  // 축하는 실제 이벤트(세트 완료·신기록 저장)에서만 (AchievementModal/ExerciseSheet).

  return (
    <div>
      {/* 요약 칩 + metric 전환 */}
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="rounded-xl border border-gold/40 bg-gold/10 px-3 py-1.5">
          <div className="lab !text-gold">{METRICS.find((m) => m.id === metric)!.chip}</div>
          <div className="font-display text-[20px] leading-none text-gold">
            {best.toLocaleString()}<span className="ml-0.5 text-[11px]">{unit}</span>
          </div>
        </div>
        <div className="flex gap-1 rounded-full border border-white/10 bg-white/5 p-1">
          {METRICS.map((m) => (
            <button
              key={m.id}
              onClick={() => setMetric(m.id)}
              className={`rounded-full px-3 py-1.5 text-[11.5px] font-bold ${
                metric === m.id ? "bg-volt text-black" : "text-white/55"
              }`}
            >
              {m.t}
            </button>
          ))}
        </div>
      </div>

      <div className="h-44">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 18, left: 4, right: 4 }}>
            <XAxis dataKey="date" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 10 }} axisLine={false} tickLine={false} />
            <Tooltip
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
              contentStyle={{ background: "#101010", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }}
              formatter={(v, _n, item) => [
                `${Number(v ?? 0).toLocaleString()}${unit}${(item?.payload as PRRow | undefined)?.isPR ? " 🏅 PR!" : ""}`,
                "",
              ]}
              labelStyle={{ color: "rgba(255,255,255,0.5)" }}
            />
            <Bar
              dataKey="value"
              radius={[5, 5, 0, 0]}
              animationDuration={reduce ? 0 : 600}
            >
              {data.map((d, i) => (
                <Cell key={i} fill={d.isPR ? "#f59e0b" : "#ccff00"} fillOpacity={d.isPR ? 1 : 0.75} />
              ))}
              <LabelList
                dataKey="value"
                position="top"
                content={(p) => {
                  const { x, y, width, index } = p as { x: number; y: number; width: number; index: number };
                  if (!data[index]?.isPR) return null;
                  return (
                    <text x={x + width / 2} y={y - 6} textAnchor="middle" fontSize={11}>🏅</text>
                  );
                }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-1 text-right text-[10.5px] text-white/40">🟡 골드 = PR 갱신 세션</p>
    </div>
  );
}
