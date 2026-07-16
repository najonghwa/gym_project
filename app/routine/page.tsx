"use client";
// 루틴 탭 — 내 루틴(저장·적용) + AI 생성 리빌 + Explore
import { useState } from "react";
import { useRouter } from "next/navigation";
import { PillButton } from "@/components/ui/PillButton";
import { ColorInitialBadge } from "@/components/ui/ColorInitialBadge";
import { RoutineGenerating } from "@/components/routine/RoutineGenerating";
import { PlanReveal } from "@/components/routine/PlanReveal";
import { ExploreSection } from "@/components/routine/ExploreSection";
import { EXPLORE, type ExploreRoutine } from "@/lib/mock/routines";
import { itemsFromExercises } from "@/lib/mock/exercises";
import { useUser } from "@/lib/useUser";

type Phase = "idle" | "generating" | "reveal";

export default function RoutinePage() {
  const router = useRouter();
  const { user, toggleSaveRoutine, setActiveRoutine, saveToday } = useUser();
  const [phase, setPhase] = useState<Phase>("idle");

  const savedIds = user?.v2?.savedRoutines ?? [];
  const activeId = user?.v2?.activeRoutineId;
  const savedRoutines = EXPLORE.filter((r) => savedIds.includes(r.id));

  // 루틴 적용 = 오늘 운동을 그 루틴 구성으로 교체 + 사용 중 표시
  const apply = (r: ExploreRoutine) => {
    saveToday(itemsFromExercises(r.exercises));
    setActiveRoutine(r.id);
    router.push("/today");
  };

  return (
    <main className="space-y-6 lg:mx-auto lg:max-w-2xl lg:pt-10">
      {/* 내 루틴 (저장한 것들) */}
      <section>
        <div className="lab mb-2">MY ROUTINES 내 루틴</div>
        {savedRoutines.length === 0 ? (
          <div className="rounded-xl border border-dashed border-white/15 bg-white/[0.02] px-5 py-6 text-center">
            <p className="text-[13px] text-white/50">
              아직 저장한 루틴이 없어요.<br />아래에서 💾 저장하면 여기 모여요.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {savedRoutines.map((r, i) => {
              const active = r.id === activeId;
              return (
                <div
                  key={r.id}
                  className={`flex items-center gap-3 rounded-xl border p-3.5 ${
                    active ? "border-volt/50 bg-volt/[0.06]" : "border-white/[0.06] bg-card"
                  }`}
                >
                  <ColorInitialBadge text={r.badge} seed={i} />
                  <div className="min-w-0 flex-1">
                    <b className="block truncate text-[14.5px]">
                      {r.title}
                      {active && <span className="ml-1.5 rounded bg-volt px-1.5 py-0.5 text-[9.5px] font-extrabold text-black">사용 중</span>}
                    </b>
                    <span className="text-[11.5px] text-white/45">{r.weeks}주 · 주 {r.daysPerWeek}회 · {r.level}</span>
                  </div>
                  {!active && (
                    <button
                      onClick={() => apply(r)}
                      className="shrink-0 rounded-full bg-volt px-3.5 py-2 text-[12px] font-extrabold text-black"
                    >
                      오늘 적용
                    </button>
                  )}
                  <button
                    onClick={() => { toggleSaveRoutine(r.id); if (active) setActiveRoutine(null); }}
                    className="shrink-0 px-1 text-[13px] text-white/35"
                    aria-label="저장 해제"
                  >✕</button>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* AI 생성 */}
      {phase === "idle" && (
        <section className="flex flex-col items-center gap-3 rounded-xl border border-white/[0.06] bg-card px-6 py-8 text-center">
          <h2 className="font-display text-[24px] leading-snug">
            이번 주 루틴,<br /><span className="text-volt">AI가 짜드릴까요?</span>
          </h2>
          <p className="text-[12.5px] text-white/55">목표·회복도·헬스장 장비를 반영해서 요일별로 구성해요.</p>
          <PillButton className="mt-2 w-full" onClick={() => setPhase("generating")}>✨ AI 루틴 만들기</PillButton>
        </section>
      )}
      {phase === "generating" && <RoutineGenerating onDone={() => setPhase("reveal")} />}
      {phase === "reveal" && <PlanReveal onRetry={() => setPhase("generating")} />}

      <ExploreSection savedIds={savedIds} onToggleSave={toggleSaveRoutine} onApply={apply} />
    </main>
  );
}
