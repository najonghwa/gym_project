"use client";
// 질문형 분석 카드 — 질문 헤드라인 → 차트 → CTA (스펙 P1-5, Planfit 공식)
import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";
import { fadeUp } from "@/lib/motion";
import { PillButton } from "@/components/ui/PillButton";

export function AnalysisCard({
  question,
  children,
  cta,
  onCta,
}: {
  question: string;
  children: ReactNode;
  cta?: string;
  onCta?: () => void;
}) {
  const reduce = useReducedMotion();
  return (
    <motion.section
      variants={reduce ? undefined : fadeUp}
      initial={reduce ? false : "hidden"}
      whileInView="show"
      viewport={{ once: true, margin: "-40px" }}
      className="rounded-3xl border border-white/[0.06] bg-card p-4"
    >
      <h3 className="font-display text-[20px] leading-snug">{question}</h3>
      <div className="mt-3">{children}</div>
      {cta && (
        <PillButton variant="ghost" className="mt-3 w-full !py-2.5 !text-[13px]" onClick={onCta}>
          {cta}
        </PillButton>
      )}
    </motion.section>
  );
}
