"use client";
// 레이더 — 부위 밸런스(축마다 값%) / peer 비교(잠긴 값 ??/100 티저) (스펙 P1-5, Planfit 스타일)
import { useState } from "react";
import {
  PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer,
} from "recharts";
import { useReducedMotion } from "framer-motion";

const PERIODS = ["주", "월", "년", "전체"] as const;

function PeriodPills({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <div className="mx-auto flex w-fit gap-1 rounded-lg border border-white/10 bg-white/5 p-1">
      {PERIODS.map((p) => (
        <button
          key={p}
          onClick={() => onChange(p)}
          className={`rounded-full px-4 py-1.5 text-[12px] font-bold ${
            value === p ? "bg-white text-black" : "text-white/50"
          }`}
        >
          {p}
        </button>
      ))}
    </div>
  );
}

// 축 라벨: 부위명 + 값 (Planfit처럼 "가슴 82%" / 잠기면 "??%")
type TickProps = {
  payload?: { value: string };
  x?: number | string;
  y?: number | string;
  textAnchor?: "end" | "inherit" | "middle" | "start";
};
function makeTick(valueOf: (part: string) => string, color: (part: string) => string) {
  return function Tick({ payload, x, y, textAnchor }: TickProps) {
    const part = payload?.value ?? "";
    return (
      <g>
        <text x={x} y={y} dy={-4} textAnchor={textAnchor} fill="rgba(255,255,255,0.65)" fontSize={11.5}>
          {part}
        </text>
        <text x={x} y={y} dy={11} textAnchor={textAnchor} fill={color(part)} fontSize={11.5} fontWeight={800}>
          {valueOf(part)}
        </text>
      </g>
    );
  };
}

export function BalanceRadar({ data }: { data: { part: string; me: number }[] }) {
  const reduce = useReducedMotion();
  const [period, setPeriod] = useState<string>("주");
  const weakest = [...data].sort((a, b) => a.me - b.me)[0];
  const valueOf = (part: string) => `${data.find((d) => d.part === part)?.me ?? 0}%`;
  return (
    <div>
      <div className="h-60">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="62%" margin={{ top: 24, bottom: 24, left: 24, right: 24 }}>
            <PolarGrid stroke="rgba(255,255,255,0.08)" />
            <PolarAngleAxis
              dataKey="part"
              tick={makeTick(valueOf, (p) => (p === weakest.part ? "#f59e0b" : "#c8ff00"))}
            />
            <Radar dataKey="me" stroke="#c8ff00" fill="#c8ff00" fillOpacity={0.28} animationDuration={reduce ? 0 : 700} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-1"><PeriodPills value={period} onChange={setPeriod} /></div>
      <p className="mt-2.5 text-center text-[12.5px] text-white/55">
        <b className="text-gold">{weakest.part}</b>가 제일 부족해요 — 이번 주 공략 추천!
      </p>
    </div>
  );
}

// 표준(권장 가이드) 대비 비교 — "잘하고 있는지"의 기준선
export function StandardRadar({ data }: { data: { part: string; me: number; peer: number }[] }) {
  const reduce = useReducedMotion();
  const valueOf = (part: string) => {
    const row = data.find((d) => d.part === part);
    return `${row?.me ?? 0}/${row?.peer ?? 0}`;
  };
  const below = data.filter((d) => d.me < d.peer);
  return (
    <div>
      <div className="h-60">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="60%" margin={{ top: 24, bottom: 24, left: 28, right: 28 }}>
            <PolarGrid stroke="rgba(255,255,255,0.08)" />
            <PolarAngleAxis
              dataKey="part"
              tick={makeTick(valueOf, (p) => {
                const row = data.find((d) => d.part === p);
                return row && row.me >= row.peer ? "#c8ff00" : "#f59e0b";
              })}
            />
            <Radar name="권장 기준" dataKey="peer" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.1}
              strokeDasharray="5 4" animationDuration={reduce ? 0 : 700} />
            <Radar name="나" dataKey="me" stroke="#c8ff00" fill="#c8ff00" fillOpacity={0.28}
              animationDuration={reduce ? 0 : 700} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex items-center justify-center gap-4 text-[11.5px]">
        <span className="flex items-center gap-1.5"><i className="h-2.5 w-2.5 rounded-sm bg-volt" />내 점수</span>
        <span className="flex items-center gap-1.5"><i className="h-2.5 w-2.5 rounded-sm border border-gold bg-gold/20" />권장 기준</span>
      </div>
      <p className="mt-2 text-center text-[12px] text-white/50">
        {below.length === 0
          ? "전 항목 기준 이상 — 아주 잘하고 있어요! 🎉"
          : <><b className="text-gold">{below.map((d) => d.part).join("·")}</b>{"이(가) 기준보다 낮아요 — 다음 주 포인트!"}</>}
      </p>
      <p className="mt-1 text-center text-[10.5px] text-white/30">기준: 주 3~4회 운동 직장인 권장 가이드 (데모)</p>
    </div>
  );
}
