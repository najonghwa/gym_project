"use client";
// 루틴 고르는 중 — 짧은 대기 표시.
//
// 예전엔 Math.random()으로 진행률을 만들어 올리고 "AI 루틴 생성 중" 캡션을
// 돌렸다. 실제 계산은 routine/page.tsx에서 동기로 즉시 끝나므로 그 퍼센트는
// 아무것도 나타내지 않는 연출이었다(같은 30px 퍼센트를 두 번 표시하기도 했다).
// 진행률·캡션을 없애고 짧은 대기만 남긴다.
import { useEffect } from "react";
import { useReducedMotion } from "framer-motion";

export function RoutineGenerating({ onDone }: { onDone: () => void }) {
  const reduce = useReducedMotion();

  useEffect(() => {
    const t = setTimeout(onDone, reduce ? 0 : 320);
    return () => clearTimeout(t);
  }, [onDone, reduce]);

  return (
    <div className="rounded-xl border border-white/[0.07] bg-card p-4">
      <div className="h-3 w-24 animate-pulse rounded bg-white/[0.08]" />
      <div className="mt-4 space-y-2.5">
        {[0, 1, 2].map((i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="h-9 w-9 shrink-0 animate-pulse rounded-lg bg-white/[0.07]" />
            <div className="min-w-0 flex-1">
              <div className="h-3 w-2/5 animate-pulse rounded bg-white/[0.07]" />
              <div className="mt-1.5 h-2.5 w-3/5 animate-pulse rounded bg-white/[0.05]" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
