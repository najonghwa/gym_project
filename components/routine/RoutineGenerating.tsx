"use client";
// AI 루틴 생성 로더 — 마스코트 think + 원형 게이지 + 캡션 로테이션 (스펙 P1-6)
import { useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { GEN_CAPTIONS } from "@/lib/mock/routines";

export function RoutineGenerating({ onDone }: { onDone: () => void }) {
  const reduce = useReducedMotion();
  const [pct, setPct] = useState(0);
  const [ci, setCi] = useState(0);

  useEffect(() => {
    const t = setInterval(() => {
      setPct((p) => {
        const next = Math.min(100, p + Math.round(4 + Math.random() * 9));
        if (next >= 100) { clearInterval(t); setTimeout(onDone, 500); }
        return next;
      });
    }, reduce ? 60 : 220);
    const c = setInterval(() => setCi((i) => (i + 1) % GEN_CAPTIONS.length), 1200);
    return () => { clearInterval(t); clearInterval(c); };
  }, [onDone, reduce]);

  const R = 52, C = 2 * Math.PI * R;

  return (
    <div className="flex flex-col items-center gap-4 rounded-xl border border-white/[0.06] bg-card px-6 py-10">
      <div className="relative">
        <svg width={140} height={140} viewBox="0 0 140 140" className="-rotate-90">
          <circle cx={70} cy={70} r={R} stroke="rgba(255,255,255,0.08)" strokeWidth={8} fill="none" />
          <circle
            cx={70} cy={70} r={R} stroke="#ff9432" strokeWidth={8} fill="none" strokeLinecap="round"
            strokeDasharray={C} strokeDashoffset={C * (1 - pct / 100)}
            style={{ transition: "stroke-dashoffset .25s ease" }}
          />
        </svg>
        <div className="absolute inset-0 grid place-items-center">
          <span className="font-display text-[30px]">{pct}<span className="text-[14px] text-white/50">%</span></span>
        </div>
      </div>
      <div className="text-center">
        <div className="font-display text-[30px] leading-none">
          {pct}<span className="text-[16px] text-white/55">%</span>
        </div>
        <div className="lab mt-1">AI 루틴 생성 중</div>
      </div>
      <AnimatePresence mode="wait">
        <motion.p
          key={ci}
          initial={reduce ? false : { opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={reduce ? undefined : { opacity: 0, y: -8 }}
          className="text-[13px] text-white/55"
        >
          {GEN_CAPTIONS[ci]}
        </motion.p>
      </AnimatePresence>
    </div>
  );
}
