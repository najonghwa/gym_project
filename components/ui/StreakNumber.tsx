"use client";
// 초대형 스트릭 숫자 — Black Han Sans 64px + countup (스펙 §2-3)
import CountUp from "react-countup";
import { useReducedMotion } from "framer-motion";

export function StreakNumber({ value }: { value: number }) {
  const reduce = useReducedMotion();
  return (
    <div className="flex items-end gap-2">
      <span
        className={`font-display text-[64px] leading-[0.85] ${
          value > 0 ? "text-volt" : "text-stone-700"
        }`}
      >
        {reduce ? value : <CountUp end={value} duration={1.1} />}
      </span>
      <span className="pb-1 text-[14px] font-bold text-white/55">일 연속</span>
    </div>
  );
}
