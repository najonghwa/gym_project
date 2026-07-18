"use client";
// 운동 썸네일 — ExerciseDB 통일 스타일 GIF(/public/exercises/<id>.gif) 우선, 없으면 픽토그램 폴백
import { useState } from "react";
import type { MotionPattern } from "@/lib/mock/exercises";
import { POSES } from "@/lib/poses";

export function ExThumb({
  ex, size = 34, rounded = "rounded-lg",
}: {
  ex: { id?: string; name: string; em: string; pattern?: MotionPattern; frames?: [string, string] | string[] };
  size?: number;
  rounded?: string;
}) {
  const [fail, setFail] = useState(false);

  if (ex.id && !fail) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={`/exercises/${ex.id}.gif`}
        alt={ex.name}
        title={ex.name}
        width={size}
        height={size}
        loading="lazy"
        onError={() => setFail(true)}
        className={`shrink-0 bg-white object-cover ${rounded}`}
        style={{ width: size, height: size }}
      />
    );
  }

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
        <g stroke="#fafafa" strokeWidth={13} strokeLinecap="round" fill="none">
          <circle cx={pose.h[0]} cy={pose.h[1]} r={12.5} fill="#fafafa" stroke="none" />
          {pose.l.map((L, i) => (
            <line key={i} x1={L[0]} y1={L[1]} x2={L[2]} y2={L[3]} strokeWidth={i === 0 ? 19 : 13} />
          ))}
          {pose.bench && <line x1={pose.bench[0]} y1={pose.bench[1]} x2={pose.bench[2]} y2={pose.bench[3]} stroke="#3f3f46" strokeWidth={11} />}
          {pose.bar && <line x1={pose.bar[0]} y1={pose.bar[1]} x2={pose.bar[2]} y2={pose.bar[3]} stroke="#c8ff00" strokeWidth={11} />}
        </g>
      </svg>
    </span>
  );
}
