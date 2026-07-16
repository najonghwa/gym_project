"use client";
// 동작 플레이어 — 2포즈 스틱피겨 + 재생/일시정지 + 속도 (스펙 P0-2)
// Lottie/GIF 자산 확보 전 폴백: SVG 교차 애니메이션
import { useState } from "react";
import { useReducedMotion } from "framer-motion";
import { LevelDots } from "@/components/ui/LevelDots";
import type { MotionPattern } from "@/lib/mock/exercises";

type Pose = { h: [number, number]; l: number[][]; bar?: number[]; bench?: number[] };
const P: Record<MotionPattern, { a: Pose; b: Pose }> = {
  squat: {
    a: { h: [60, 18], l: [[60, 26, 60, 58], [60, 34, 40, 30], [60, 34, 80, 30], [60, 58, 50, 82], [50, 82, 50, 112], [60, 58, 70, 82], [70, 82, 70, 112]], bar: [26, 30, 94, 30] },
    b: { h: [60, 40], l: [[60, 48, 60, 76], [60, 56, 40, 52], [60, 56, 80, 52], [60, 76, 42, 88], [42, 88, 46, 112], [60, 76, 78, 88], [78, 88, 74, 112]], bar: [26, 52, 94, 52] },
  },
  bench: {
    a: { h: [34, 76], l: [[42, 78, 72, 78], [56, 78, 56, 52], [72, 78, 84, 96], [84, 96, 84, 112]], bar: [42, 52, 70, 52], bench: [28, 86, 78, 86] },
    b: { h: [34, 76], l: [[42, 78, 72, 78], [56, 78, 54, 66], [72, 78, 84, 96], [84, 96, 84, 112]], bar: [40, 66, 68, 66], bench: [28, 86, 78, 86] },
  },
  pulldown: {
    a: { h: [60, 24], l: [[60, 32, 60, 64], [60, 38, 46, 14], [60, 38, 74, 14], [60, 64, 78, 68], [78, 68, 78, 96], [60, 64, 44, 68], [44, 68, 44, 96]], bar: [34, 12, 86, 12] },
    b: { h: [60, 26], l: [[60, 34, 60, 64], [60, 40, 46, 42], [60, 40, 74, 42], [60, 64, 78, 68], [78, 68, 78, 96], [60, 64, 44, 68], [44, 68, 44, 96]], bar: [34, 42, 86, 42] },
  },
  curl: {
    a: { h: [56, 18], l: [[56, 26, 56, 62], [56, 34, 58, 54], [58, 54, 60, 76], [56, 62, 50, 112], [56, 62, 62, 112]], bar: [54, 78, 66, 78] },
    b: { h: [56, 18], l: [[56, 26, 56, 62], [56, 34, 58, 54], [58, 54, 74, 42], [56, 62, 50, 112], [56, 62, 62, 112]], bar: [70, 42, 78, 44] },
  },
  ohp: {
    a: { h: [60, 22], l: [[60, 30, 60, 62], [60, 38, 46, 32], [60, 38, 74, 32], [60, 62, 52, 112], [60, 62, 68, 112]], bar: [36, 30, 84, 30] },
    b: { h: [60, 24], l: [[60, 32, 60, 62], [60, 38, 47, 12], [60, 38, 73, 12], [60, 62, 52, 112], [60, 62, 68, 112]], bar: [36, 10, 84, 10] },
  },
  row: {
    a: { h: [48, 30], l: [[50, 38, 52, 70], [50, 46, 80, 52], [52, 70, 76, 74], [76, 74, 78, 100]] },
    b: { h: [44, 28], l: [[46, 36, 52, 70], [46, 44, 60, 54], [52, 70, 76, 74], [76, 74, 78, 100]] },
  },
};

function PoseG({ p, cls, dur }: { p: Pose; cls: "poseA" | "poseB"; dur: number }) {
  return (
    <g
      stroke="#d4d4d8"
      strokeWidth={3.2}
      strokeLinecap="round"
      fill="none"
      style={{ animation: `${cls} ${dur}s infinite` }}
    >
      <circle cx={p.h[0]} cy={p.h[1]} r={7} fill="#d4d4d8" stroke="none" />
      {p.l.map((L, i) => (
        <line key={i} x1={L[0]} y1={L[1]} x2={L[2]} y2={L[3]} />
      ))}
      {p.bar && <line x1={p.bar[0]} y1={p.bar[1]} x2={p.bar[2]} y2={p.bar[3]} stroke="#ff9432" strokeWidth={4} />}
      {p.bench && <line x1={p.bench[0]} y1={p.bench[1]} x2={p.bench[2]} y2={p.bench[3]} stroke="#52525b" strokeWidth={4} />}
    </g>
  );
}

export function AnimPlayer({
  pattern,
  level,
  frames,
}: {
  pattern: MotionPattern;
  level: 1 | 2 | 3 | 4 | 5;
  frames?: [string, string]; // 실사 2프레임 (있으면 우선, 스틱피겨는 폴백)
}) {
  const reduce = useReducedMotion();
  const [playing, setPlaying] = useState(!reduce);
  const [imgFail, setImgFail] = useState(false);
  const [speed, setSpeed] = useState<1 | 0.5>(1);
  const pt = P[pattern];
  const dur = 1.6 / speed;
  const useFrames = !!frames && !imgFail;
  const playState = playing ? "running" : "paused";

  return (
    <div className="rounded-lg border border-white/[0.06] bg-white/[0.03] p-2">
      <style>{`
        @keyframes poseA { 0%,42%{opacity:1} 50%,92%{opacity:0} 100%{opacity:1} }
        @keyframes poseB { 0%,42%{opacity:0} 50%,92%{opacity:1} 100%{opacity:0} }
      `}</style>
      <div className="relative h-40 overflow-hidden rounded-xl">
        {useFrames ? (
          <>
            {/* 실사 크로스페이드 — 흰 배경 사진이라 밝은 패널 위에 */}
            <div className="absolute inset-0 rounded-xl bg-white" />
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={frames![0]} alt="동작 프레임 1"
              onError={() => setImgFail(true)}
              className="absolute inset-0 h-full w-full object-contain"
              style={{ animation: `poseA ${dur}s infinite`, animationPlayState: playState }}
            />
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={frames![1]} alt="동작 프레임 2"
              onError={() => setImgFail(true)}
              className="absolute inset-0 h-full w-full object-contain"
              style={{ animation: `poseB ${dur}s infinite`, animationPlayState: playState }}
            />
          </>
        ) : (
          <svg viewBox="0 0 120 120" className="h-full w-full">
            {playing ? (
              <>
                <PoseG p={pt.a} cls="poseA" dur={dur} />
                <PoseG p={pt.b} cls="poseB" dur={dur} />
              </>
            ) : (
              <PoseG p={pt.a} cls="poseA" dur={9999} />
            )}
          </svg>
        )}
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
