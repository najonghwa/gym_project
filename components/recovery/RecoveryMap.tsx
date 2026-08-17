"use client";
// P0-1 근육 회복도 바디맵 — front/back 토글 + 리스트 + 마스코트 반응
import { useMemo, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { BodySvg, REGION_VIEW } from "./BodySvg";
import { MuscleSheet } from "./MuscleSheet";
import { fadeUp, staggerContainer } from "@/lib/motion";
import {
  MUSCLE_KR, daysAgoLabel, recoveryColor,
  type Muscle, type MuscleRecovery,
} from "@/lib/recovery";

export function RecoveryMap({ data }: { data: MuscleRecovery[] }) {
  const reduce = useReducedMotion();
  const [view, setView] = useState<"front" | "back">("front");
  const [sel, setSel] = useState<MuscleRecovery | null>(null);

  const byMuscle = useMemo(() => {
    const m = new Map<Muscle, MuscleRecovery>();
    data.forEach((d) => m.set(d.muscle, d));
    return m;
  }, [data]);

  const colorOf = (m: Muscle) => recoveryColor(byMuscle.get(m)?.pct ?? 1);
  const avg = data.reduce((s, d) => s + d.pct, 0) / Math.max(1, data.length);
  const freshOnes = data.filter((d) => d.pct >= 0.95);
  const redOnes = data.filter((d) => d.pct < 0.5);
  const mascotState = redOnes.length >= 3 ? "tired" : avg >= 0.85 ? "cheer" : "idle";

  const sorted = [...data].sort((a, b) => b.pct - a.pct);

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <div>
          <div className="lab">근육 회복도</div>
          <div className="mt-1 text-[12.5px] text-white/55">
            평균 <b className="text-stone-100">{Math.round(avg * 100)}%</b>
            {freshOnes.length > 0 && (
              <span className="ml-1.5 text-volt">
                · {freshOnes.map((f) => MUSCLE_KR[f.muscle]).join("·")} 회복 완료
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-1 rounded-lg border border-white/10 bg-white/5 p-1">
          {(["front", "back"] as const).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`rounded-full px-3.5 py-1.5 text-[12px] font-bold ${
                view === v ? "bg-volt text-black" : "text-white/55"
              }`}
            >
              {v === "front" ? "앞" : "뒤"}
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-4">
        {/* 바디맵 */}
        <div className="h-56 w-36 shrink-0">
          <BodySvg
            view={view}
            colorOf={colorOf}
            onSelect={(m) => setSel(byMuscle.get(m) ?? null)}
          />
        </div>

        {/* 부위 리스트 (stagger) */}
        <motion.div
          className="min-w-0 flex-1 space-y-1.5"
          variants={reduce ? undefined : staggerContainer}
          initial={reduce ? false : "hidden"}
          animate="show"
        >
          {sorted.map((d) => (
            <motion.button
              key={d.muscle}
              variants={reduce ? undefined : fadeUp}
              onClick={() => {
                setView(REGION_VIEW[d.muscle]);
                setSel(d);
              }}
              className="flex w-full items-center gap-2.5 rounded-xl bg-white/[0.04] px-3 py-2 text-left"
            >
              <span
                className="h-3 w-3 shrink-0 rounded-full"
                style={{ background: recoveryColor(d.pct) }}
              />
              <span className="flex-1 truncate text-[13px] font-bold">
                {MUSCLE_KR[d.muscle]}
              </span>
              <span className="text-[11.5px] tabular-nums text-white/55">
                {Math.round(d.pct * 100)}% · {daysAgoLabel(d.lastTrainedAt)}
              </span>
            </motion.button>
          ))}
        </motion.div>
      </div>

      {/* 마스코트 코멘트 */}
      <div className="mt-3 flex items-center gap-2.5 rounded-lg bg-white/[0.04] px-3.5 py-2.5">
        
        <p className="text-[12.5px] leading-relaxed text-white/70">
          {mascotState === "cheer"
            ? "전부 회복됐어요. 오늘은 어느 부위든 괜찮습니다"
            : mascotState === "tired"
            ? "빨간 부위가 많아요 — 오늘은 가볍게 or 회복된 부위만!"
            : freshOnes.length
            ? `${MUSCLE_KR[freshOnes[0].muscle]} 운동하기 좋은 날이에요!`
            : "골고루 회복 중 — 초록 부위부터 공략!"}
        </p>
      </div>

      <MuscleSheet data={sel} onClose={() => setSel(null)} />
    </div>
  );
}
