"use client";
// 오늘의 운동 카드 — 세트 인라인 체크, 탭하면 상세 시트 (스펙 P0-4)
import { motion, useReducedMotion } from "framer-motion";
import { fadeUp, staggerContainer } from "@/lib/motion";
import { byId, type TodayItem } from "@/lib/mock/exercises";

export function TodayWorkoutCard({
  items,
  onToggleSet,
  onOpenExercise,
  embedded = false,
}: {
  items: TodayItem[];
  onToggleSet: (exerciseId: string, setIndex: number) => void;
  onOpenExercise: (exerciseId: string) => void;
  embedded?: boolean; // 타임라인 노드 안에 들어갈 때 (자체 카드 테두리 없이)
}) {
  const reduce = useReducedMotion();
  const totalSets = items.reduce((s, it) => s + it.sets.length, 0);
  const doneSets = items.reduce((s, it) => s + it.sets.filter((x) => x.done).length, 0);
  const pct = totalSets ? Math.round((doneSets / totalSets) * 100) : 0;

  return (
    <div className={embedded ? "" : "rounded-2xl border border-white/[0.06] bg-card p-4"}>
      <div className="mb-3 flex items-center justify-between">
        <div>
          <div className="text-[13px] text-white/55">
            {doneSets}/{totalSets} 세트 완료
          </div>
        </div>
        <span className={`font-display text-[26px] ${pct >= 100 ? "text-volt" : ""}`}>{pct}%</span>
      </div>
      <div className="mb-3 h-2 overflow-hidden rounded-full bg-white/10">
        <motion.div
          className="h-full rounded-full bg-volt"
          initial={reduce ? false : { width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6 }}
        />
      </div>

      <motion.div
        className="space-y-2.5 lg:grid lg:grid-cols-2 lg:gap-3 lg:space-y-0"
        variants={reduce ? undefined : staggerContainer}
        initial={reduce ? false : "hidden"}
        animate="show"
      >
        {items.map((it) => {
          const ex = byId(it.exerciseId);
          if (!ex) return null;
          const workingOnly = it.sets.filter((s) => s.kind === "working");
          const allDone = it.sets.every((s) => s.done);
          return (
            <motion.div
              key={it.exerciseId}
              variants={reduce ? undefined : fadeUp}
              className={`rounded-lg border p-3 ${
                allDone ? "border-volt/50 bg-volt/[0.07]" : "border-white/[0.06] bg-white/[0.03]"
              }`}
            >
              <button className="flex w-full items-center gap-2 text-left" onClick={() => onOpenExercise(it.exerciseId)}>
                <span className="text-[18px]">{ex.em}</span>
                <span className="min-w-0 flex-1">
                  <b className="block truncate text-[14.5px]">{ex.name} <span className="text-[10px] text-white/40">ⓘ</span></b>
                  <span className="text-[11.5px] text-white/50">
                    {ex.zone}구역 · {workingOnly[0]?.weightKg ?? "-"}kg × {workingOnly[0]?.reps ?? "-"}회
                  </span>
                </span>
                <span className="text-[11px] font-bold text-white/40">
                  {it.sets.filter((s) => s.done).length}/{it.sets.length}
                </span>
              </button>
              {/* 세트 인라인 체크 */}
              <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                {it.sets.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => onToggleSet(it.exerciseId, i)}
                    className={`grid h-10 w-10 place-items-center rounded-2xl border-2 text-[12.5px] font-extrabold transition ${
                      s.done
                        ? "border-volt bg-volt text-black"
                        : s.kind === "warmup"
                        ? "border-sky-500/40 text-sky-400/70"
                        : "border-white/15 text-white/40"
                    }`}
                    aria-label={`${i + 1}세트 ${s.done ? "완료됨" : "체크"}`}
                  >
                    {s.kind === "warmup" ? "W" : i + 1 - it.sets.filter((x) => x.kind === "warmup").length}
                  </button>
                ))}
              </div>
            </motion.div>
          );
        })}
      </motion.div>
      <p className="mt-3 text-[11.5px] leading-relaxed text-white/40">
        운동 이름을 누르면 동작·세트 편집·기록 추이가 열려요. <span className="text-sky-400/70">W</span> = 웜업 세트
      </p>
    </div>
  );
}
