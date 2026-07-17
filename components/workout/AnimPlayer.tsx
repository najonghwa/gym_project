"use client";
// 동작 플레이어 — 2포즈 픽토그램 교차 애니메이션 + 재생/일시정지 + 속도 (스펙 P0-2)
// 실사 크로스페이드는 배경·모델이 제각각이라 폐기 → 통일된 픽토그램으로 일원화
import { useState } from "react";
import { useReducedMotion } from "framer-motion";
import { LevelDots } from "@/components/ui/LevelDots";
import type { MotionPattern } from "@/lib/mock/exercises";
import { POSES, type Pose } from "@/lib/poses";

function PoseG({ p, cls, dur }: { p: Pose; cls: "poseA" | "poseB"; dur: number }) {
  return (
    <g
      stroke="#d4d4d8"
      strokeWidth={4.5}
      strokeLinecap="round"
      fill="none"
      style={{ animation: `${cls} ${dur}s infinite` }}
    >
      <circle cx={p.h[0]} cy={p.h[1]} r={8} fill="#d4d4d8" stroke="none" />
      {p.l.map((L, i) => (
        <line key={i} x1={L[0]} y1={L[1]} x2={L[2]} y2={L[3]} />
      ))}
      {p.bench && <line x1={p.bench[0]} y1={p.bench[1]} x2={p.bench[2]} y2={p.bench[3]} stroke="#52525b" strokeWidth={5.5} />}
      {p.bar && <line x1={p.bar[0]} y1={p.bar[1]} x2={p.bar[2]} y2={p.bar[3]} stroke="#c8ff00" strokeWidth={5.5} />}
    </g>
  );
}

export function AnimPlayer({
  pattern,
  level,
}: {
  pattern: MotionPattern;
  level: 1 | 2 | 3 | 4 | 5;
  frames?: [string, string]; // 하위 호환용 — 더 이상 사용하지 않음
}) {
  const reduce = useReducedMotion();
  const [playing, setPlaying] = useState(!reduce);
  const [speed, setSpeed] = useState<1 | 0.5>(1);
  const pt = POSES[pattern];
  const dur = 1.6 / speed;

  return (
    <div className="rounded-lg border border-white/[0.06] bg-white/[0.03] p-2">
      <style>{`
        @keyframes poseA { 0%,42%{opacity:1} 50%,92%{opacity:0} 100%{opacity:1} }
        @keyframes poseB { 0%,42%{opacity:0} 50%,92%{opacity:1} 100%{opacity:0} }
      `}</style>
      <div className="relative h-40 overflow-hidden rounded-2xl">
        {/* 은은한 바닥선 — 픽토그램 무대 */}
        <svg viewBox="0 0 120 120" className="h-full w-full">
          <line x1={14} y1={114} x2={106} y2={114} stroke="rgba(255,255,255,0.1)" strokeWidth={2} strokeLinecap="round" />
          {playing ? (
            <>
              <PoseG p={pt.a} cls="poseA" dur={dur} />
              <PoseG p={pt.b} cls="poseB" dur={dur} />
            </>
          ) : (
            <PoseG p={pt.a} cls="poseA" dur={9999} />
          )}
        </svg>
      </div>
      <div className="flex items-center justify-between px-1 pb-1">
        <LevelDots level={level} />
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setSpeed(speed === 1 ? 0.5 : 1)}
            className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[11px] font-bold text-white/70"
          >
            {speed}x
          </button>
          <button
            onClick={() => setPlaying(!playing)}
            className="grid h-8 w-8 place-items-center rounded-lg bg-volt text-[13px] text-black"
            aria-label={playing ? "일시정지" : "재생"}
          >
            {playing ? "⏸" : "▶"}
          </button>
        </div>
      </div>
    </div>
  );
}
