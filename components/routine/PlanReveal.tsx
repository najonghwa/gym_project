"use client";
// 생성된 플랜 리빌 — Day 카드 stagger + 카드별 AI교체 / 전체 AI다시 (스펙 P1-6)
import { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { fadeUp, staggerContainer } from "@/lib/motion";
import { PillButton } from "@/components/ui/PillButton";
import { ColorInitialBadge } from "@/components/ui/ColorInitialBadge";
import { RecoveryStrip } from "@/components/ui/RecoveryStrip";
import { byId } from "@/lib/mock/exercises";
import { getMockRecovery } from "@/lib/mock/recovery";
import { ALT_DAYS, GENERATED_PLAN, type PlanDay } from "@/lib/mock/routines";
import { MUSCLE_KR } from "@/lib/recovery";

export function PlanReveal({ onRetry }: { onRetry: () => void }) {
  const reduce = useReducedMotion();
  const [days, setDays] = useState<PlanDay[]>(GENERATED_PLAN);
  const recovery = getMockRecovery();
  const recOf = (m: string) => recovery.find((r) => r.muscle === m)?.pct ?? 1;

  const replaceDay = (day: string) =>
    setDays((prev) => prev.map((d) => (d.day === day && ALT_DAYS[day] ? ALT_DAYS[day] : d)));

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <div>
          <div className="lab">이번 주 플랜 READY</div>
          <h3 className="font-display text-[22px]">주 {days.length}회 · 벌크업 루틴 완성! 🎉</h3>
        </div>
        <PillButton variant="ghost" className="!px-4 !py-2 !text-[12.5px]" onClick={onRetry}>
          🎲 AI 다시
        </PillButton>
      </div>

      <motion.div
        className="space-y-3"
        variants={reduce ? undefined : staggerContainer}
        initial={reduce ? false : "hidden"}
        animate="show"
      >
        {days.map((d, i) => (
          <motion.div
            key={d.day + d.title}
            variants={reduce ? undefined : fadeUp}
            className="rounded-3xl border border-white/[0.06] bg-card p-4"
          >
            <div className="flex items-center gap-3">
              <ColorInitialBadge text={d.day} seed={i} />
              <div className="min-w-0 flex-1">
                <b className="block text-[15px]">{d.title}</b>
                <span className="text-[11.5px] text-white/50">
                  {d.muscles.map((m) => MUSCLE_KR[m]).join(" · ")}
                </span>
              </div>
              <button
                className="rounded-full border border-white/15 bg-white/5 px-3 py-1.5 text-[11.5px] font-bold text-white/70"
                onClick={() => replaceDay(d.day)}
              >
                🔄 AI 교체
              </button>
            </div>
            {/* Working Muscles 회복 스트립 */}
            <div className="mt-3">
              <RecoveryStrip items={d.muscles.map((m) => ({ muscle: m, recoveryPct: recOf(m) }))} />
            </div>
            {/* 운동 미리보기 row */}
            <div className="mt-2 flex gap-1.5 overflow-x-auto">
              {d.exercises.map((id) => {
                const ex = byId(id);
                return ex ? (
                  <span key={id} className="shrink-0 rounded-xl border border-white/10 bg-white/[0.04] px-2.5 py-1.5 text-[11.5px]">
                    {ex.em} {ex.name}
                  </span>
                ) : null;
              })}
            </div>
          </motion.div>
        ))}
      </motion.div>
      <PillButton className="mt-4 w-full">이 플랜으로 시작 🚀</PillButton>
    </div>
  );
}
