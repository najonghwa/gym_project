"use client";
// 루틴 탭 — P1-6 AI 생성 로더→리빌 + P1-7 Explore
import { useState } from "react";
import { Mascot } from "@/components/mascot/Mascot";
import { PillButton } from "@/components/ui/PillButton";
import { RoutineGenerating } from "@/components/routine/RoutineGenerating";
import { PlanReveal } from "@/components/routine/PlanReveal";
import { ExploreSection } from "@/components/routine/ExploreSection";

type Phase = "idle" | "generating" | "reveal";

export default function RoutinePage() {
  const [phase, setPhase] = useState<Phase>("idle");

  return (
    <main className="space-y-6 lg:pt-16">
      {phase === "idle" && (
        <section className="flex flex-col items-center gap-3 rounded-3xl border border-white/[0.06] bg-card px-6 py-8 text-center">
          <Mascot state="talk" size={88} />
          <h2 className="font-display text-[24px] leading-snug">
            이번 주 루틴,<br /><span className="text-volt">AI가 짜드릴까요?</span>
          </h2>
          <p className="text-[12.5px] text-white/55">
            목표·회복도·헬스장 장비를 반영해서 요일별로 구성해요.
          </p>
          <PillButton className="mt-2 w-full" onClick={() => setPhase("generating")}>
            ✨ AI 루틴 만들기
          </PillButton>
        </section>
      )}
      {phase === "generating" && <RoutineGenerating onDone={() => setPhase("reveal")} />}
      {phase === "reveal" && <PlanReveal onRetry={() => setPhase("generating")} />}

      <ExploreSection />
      {/* TODO(supabase): 유명 프로그램 10종 + 동료 공유 루틴 실데이터 연동 */}
    </main>
  );
}
