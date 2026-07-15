"use client";
// 주간 스트립 — 요일칸 달성% (스펙 P0-4)
import { motion, useReducedMotion } from "framer-motion";
import { fadeUp, staggerContainer } from "@/lib/motion";

export interface DayCell {
  label: string;      // 월/화/...
  pct: number | null; // null = 미래·휴식
  isToday?: boolean;
}

export function WeekStrip({ days, target }: { days: DayCell[]; target: string }) {
  const reduce = useReducedMotion();
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between">
        <span className="lab">이번 주 WEEK</span>
        <span className="text-[11px] font-bold text-white/55">🎯 {target}</span>
      </div>
      <motion.div
        className="grid grid-cols-7 gap-1.5"
        variants={reduce ? undefined : staggerContainer}
        initial={reduce ? false : "hidden"}
        animate="show"
      >
        {days.map((d, i) => (
          <motion.div
            key={i}
            variants={reduce ? undefined : fadeUp}
            className={`flex h-14 flex-col items-center justify-center gap-0.5 rounded-xl border ${
              d.isToday
                ? "border-volt/60 bg-volt/10"
                : d.pct === null
                ? "border-white/[0.06] bg-white/[0.03]"
                : d.pct >= 100
                ? "border-volt/40 bg-volt/10"
                : d.pct > 0
                ? "border-gold/40 bg-gold/10"
                : "border-white/[0.06] bg-white/[0.03]"
            }`}
          >
            <span className={`text-[10px] font-bold ${d.isToday ? "text-volt" : "text-white/40"}`}>
              {d.label}
            </span>
            {d.pct !== null && d.pct > 0 ? (
              <span className={`text-[12px] font-extrabold tabular-nums ${d.pct >= 100 ? "text-volt" : "text-gold"}`}>
                {d.pct}%
              </span>
            ) : (
              <span className="text-[12px] text-white/20">·</span>
            )}
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
