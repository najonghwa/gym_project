"use client";
// 레이더 — 부위 밸런스(축마다 값%) / peer 비교(잠긴 값 ??/100 티저) (스펙 P1-5, Planfit 스타일)
import { useState } from "react";
import {
  PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer,
} from "recharts";
import { useReducedMotion } from "framer-motion";
import { PillButton } from "@/components/ui/PillButton";

const PERIODS = ["주", "월", "년", "전체"] as const;

function PeriodPills({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <div className="mx-auto flex w-fit gap-1 rounded-full border border-white/10 bg-white/5 p-1">
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
              tick={makeTick(valueOf, (p) => (p === weakest.part ? "#f59e0b" : "#ccff00"))}
            />
            <Radar dataKey="me" stroke="#ccff00" fill="#ccff00" fillOpacity={0.28} animationDuration={reduce ? 0 : 700} />
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

export function PeerRadar({ data }: { data: { part: string; me: number; peer: number }[] }) {
  const reduce = useReducedMotion();
  const [unlocked, setUnlocked] = useState(false);
  // 잠금 상태: 내 점수는 보이고, 비교 기준(/100)은 ??로 티저
  const valueOf = (part: string) => {
    const row = data.find((d) => d.part === part);
    return unlocked ? `${row?.me ?? 0}/${row?.peer ?? 0}` : `${row?.me ?? 0}/??`;
  };
  return (
    <div>
      <div className="relative h-60">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="60%" margin={{ top: 24, bottom: 24, left: 28, right: 28 }}>
            <PolarGrid stroke="rgba(255,255,255,0.08)" />
            <PolarAngleAxis
              dataKey="part"
              tick={makeTick(valueOf, () => (unlocked ? "#ccff00" : "rgba(255,255,255,0.45)"))}
            />
            <Radar name="나" dataKey="me" stroke="#ccff00" fill="#ccff00" fillOpacity={0.28} animationDuration={reduce ? 0 : 700} />
            {unlocked && (
              <Radar name="동료 평균" dataKey="peer" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.15} animationDuration={reduce ? 0 : 700} />
            )}
          </RadarChart>
        </ResponsiveContainer>
        {!unlocked && (
          <div className="absolute inset-x-0 bottom-0 flex justify-center">
            <PillButton className="!py-2 !text-[13px]" onClick={() => setUnlocked(true)}>
              🔓 동료 평균과 비교하기
            </PillButton>
          </div>
        )}
      </div>
      <div className="mt-2 flex items-center justify-center gap-4 text-[11.5px]">
        <span className="flex items-center gap-1.5"><i className="h-2.5 w-2.5 rounded-sm bg-volt" />내 점수</span>
        <span className="flex items-center gap-1.5">
          <i className="h-2.5 w-2.5 rounded-sm bg-gold" />같은 목표 동료 평균{unlocked ? "" : " (??)"}
        </span>
      </div>
    </div>
  );
}
