"use client";
// 운동 실사 썸네일 — free-exercise-db 첫 프레임, 로드 실패 시 이모지 폴백
import { useState } from "react";

export function ExThumb({
  ex, size = 34, rounded = "rounded-lg",
}: {
  ex: { name: string; em: string; frames?: [string, string] | string[] };
  size?: number;
  rounded?: string;
}) {
  const [fail, setFail] = useState(false);
  if (!ex.frames?.[0] || fail) {
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
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={ex.frames[0]}
      alt={ex.name}
      width={size}
      height={size}
      loading="lazy"
      onError={() => setFail(true)}
      className={`shrink-0 bg-white object-cover ${rounded}`}
      style={{ width: size, height: size }}
    />
  );
}
