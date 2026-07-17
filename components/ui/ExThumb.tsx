"use client";
// 운동 썸네일 — 통일된 픽토그램(포즈 A 정지 컷, 굵은 라인 + 볼트 바)
// 실사(free-exercise-db)는 배경·모델이 제각각이라 폐기, 패턴 없으면 이모지 폴백
import type { MotionPattern } from "@/lib/mock/exercises";
import { POSES } from "@/lib/poses";

export function ExThumb({
  ex, size = 34, rounded = "rounded-lg",
}: {
  ex: { name: string; em: string; pattern?: MotionPattern; frames?: [string, string] | string[] };
  size?: number;
  rounded?: string;
}) {
  const pose = ex.pattern ? POSES[ex.pattern]?.a : null;
  if (!pose) {
    return (
      <span
        className={`grid shrink-0 place-items-center bg-white/[0.07] ${rounded}`}
        style={{ width: size, height: size, fontSize: size * 0.5 }}
      >
        {ex.em}
      </span>
    );
  }
  return (
    <span
      className={`grid shrink-0 place-items-center border border-white/[0.07] bg-white/[0.05] ${rounded}`}
      style={{ width: size, height: size }}
      title={ex.name}
    >
      <svg viewBox="0 0 120 120" width={size * 0.82} height={size * 0.82} aria-hidden>
        <g stroke="#d4d4d8" strokeWidth={9} strokeLinecap="round" fill="none">
          <circle cx={pose.h[0]} cy={pose.h[1]} r={11} fill="#d4d4d8" stroke="none" />
          {pose.l.map((L, i) => (
            <line key={i} x1={L[0]} y1={L[1]} x2={L[2]} y2={L[3]} />
          ))}
          {pose.bench && <line x1={pose.bench[0]} y1={pose.bench[1]} x2={pose.bench[2]} y2={pose.bench[3]} stroke="#52525b" strokeWidth={10} />}
          {pose.bar && <line x1={pose.bar[0]} y1={pose.bar[1]} x2={pose.bar[2]} y2={pose.bar[3]} stroke="#c8ff00" strokeWidth={11} />}
        </g>
      </svg>
    </span>
  );
}
