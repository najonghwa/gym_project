"use client";
// 운동 정보 시트 — 애니메이션 + 하는 방법 + 팁 (루틴·헬스장 등 어디서든 운동 그림 클릭 시)
import { BottomSheet } from "@/components/ui/BottomSheet";
import { AnimPlayer } from "@/components/workout/AnimPlayer";
import type { Exercise } from "@/lib/mock/exercises";

export function ExerciseInfoSheet({
  exercise, onClose,
}: {
  exercise: Exercise | null;
  onClose: () => void;
}) {
  return (
    <BottomSheet open={!!exercise} onClose={onClose}>
      {exercise && (
        <>
          <h3 className="text-lg font-extrabold">{exercise.name}</h3>
          <p className="mt-0.5 text-[12px] text-white/50">
            {exercise.zone}구역 · {exercise.equipment} · 휴식 {exercise.restSec}초
          </p>

          <div className="mt-3">
            <AnimPlayer pattern={exercise.pattern} level={exercise.level} exId={exercise.id} />
          </div>

          <div className="lab mb-2 mt-4">하는 방법</div>
          <ol className="space-y-2">
            {exercise.howto.map((h, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <span className="grid h-5 w-5 shrink-0 place-items-center rounded-full bg-volt/15 text-[11px] font-extrabold text-volt">
                  {i + 1}
                </span>
                <span className="text-[13.5px] leading-relaxed text-white/80">{h}</span>
              </li>
            ))}
          </ol>

          <div className="mt-4 rounded-lg border border-gold/40 bg-gold/10 p-3 text-[13px] leading-relaxed">
            <b>팁</b> — {exercise.tip}
          </div>
        </>
      )}
    </BottomSheet>
  );
}
