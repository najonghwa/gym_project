"use client";
// 레이더 — 부위 밸런스 / peer 비교(잠긴 값 ?? 티저) (스펙 P1-5)
import { useState } from "react";
import {
  PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer,
} from "recharts";
import { useReducedMotion } from "framer-motion";
import { PillButton } from "@/components/ui/PillButton";

export function BalanceRadar({ data }: { data: { part: string; me: number }[] }) {
  const reduce = useReducedMotion();
  const weakest = [...data].sort((a, b) => a.me - b.me)[0];
  return (
    <div>
      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="75%">
            <PolarGrid stroke="rgba(255,255,255,0.08)" />
            <PolarAngleAxis dataKey="part" tick={{ fill: "rgba(255,255,255,0.55)", fontSize: 11 }} />
            <Radar dataKey="me" stroke="#ccff00" fill="#ccff00" fillOpacity={0.25} animationDuration={reduce ? 0 : 700} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-center text-[12.5px] text-white/55">
        <b className="text-gold">{weakest.part}</b>가 제일 부족해요 — 이번 주 공략 추천!
      </p>
    </div>
  );
}

export function PeerRadar({ data }: { data: { part: string; me: number; peer: number }[] }) {
  const reduce = useReducedMotion();
  const [unlocked, setUnlocked] = useState(false);
  return (
    <div className="relative">
      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="75%">
            <PolarGrid stroke="rgba(255,255,255,0.08)" />
            <PolarAngleAxis dataKey="part" tick={{ fill: "rgba(255,255,255,0.55)", fontSize: 11 }} />
            <Radar name="나" dataKey="me" stroke="#ccff00" fill="#ccff00" fillOpacity={0.25} animationDuration={reduce ? 0 : 700} />
            {unlocked && (
              <Radar name="동료 평균" dataKey="peer" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.15} animationDuration={reduce ? 0 : 700} />
            )}
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex items-center justify-center gap-4 text-[11.5px]">
        <span className="flex items-center gap-1.5"><i className="h-2.5 w-2.5 rounded-sm bg-volt" />나</span>
        <span className="flex items-center gap-1.5">
          <i className="h-2.5 w-2.5 rounded-sm bg-gold" />동료 평균 {unlocked ? "" : "??"}
        </span>
      </div>
      {!unlocked && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 rounded-2xl bg-black/40 backdrop-blur-[3px]">
          <span className="font-display text-[22px]">동료 평균은 ??</span>
          <PillButton className="!py-2 !text-[13px]" onClick={() => setUnlocked(true)}>
            🔓 비교 보기
          </PillButton>
        </div>
      )}
    </div>
  );
}
