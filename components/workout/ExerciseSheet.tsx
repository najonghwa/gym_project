"use client";
// P0-2 운동 상세 시트 — AnimPlayer + 도넛 + 세트 편집 + 휴식타이머 + Replace + 추이
import { useEffect, useRef, useState } from "react";
import confetti from "canvas-confetti";
import { useReducedMotion } from "framer-motion";
import { BottomSheet } from "@/components/ui/BottomSheet";
import { PillButton } from "@/components/ui/PillButton";
import { AnimPlayer } from "./AnimPlayer";
import { MuscleDonut } from "@/components/charts/MuscleDonut";
import { PRChart } from "@/components/charts/PRChart";
import { Mascot } from "@/components/mascot/Mascot";
import { alternativesFor, byId, type Exercise, type SetRow } from "@/lib/mock/exercises";

export function ExerciseSheet({
  exercise,
  sets,
  onChange,
  onReplace,
  onDelete,
  onClose,
}: {
  exercise: Exercise | null;
  sets: SetRow[];
  onChange: (sets: SetRow[]) => void;
  onReplace: (newId: string) => void;
  onDelete: () => void;
  onClose: () => void;
}) {
  const reduce = useReducedMotion();
  const [showAlt, setShowAlt] = useState(false);
  const [note, setNote] = useState("");
  const [rest, setRest] = useState<number | null>(null);
  const restRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [celebrate, setCelebrate] = useState(false);

  useEffect(() => () => { if (restRef.current) clearInterval(restRef.current); }, []);
  useEffect(() => { setShowAlt(false); setCelebrate(false); }, [exercise?.id]);

  if (!exercise) return null;
  const ex = exercise;

  const startRest = () => {
    if (restRef.current) clearInterval(restRef.current);
    setRest(ex.restSec);
    restRef.current = setInterval(() => {
      setRest((r) => {
        if (r === null || r <= 1) {
          if (restRef.current) clearInterval(restRef.current);
          return null;
        }
        return r - 1;
      });
    }, 1000);
  };

  const update = (i: number, patch: Partial<SetRow>) => {
    const next = sets.map((s, idx) => (idx === i ? { ...s, ...patch } : s));
    onChange(next);
    // 마지막 세트 완료 → confetti + Mascot cheer (운동당 1회만 — 스팸 방지)
    if (patch.done && next.every((s) => s.done)) {
      if (!celebrate) {
        setCelebrate(true);
        if (!reduce)
          confetti({ particleCount: 90, spread: 70, origin: { y: 0.75 }, colors: ["#c8ff00", "#f59e0b", "#fff"] });
      }
    } else if (patch.done) {
      startRest();
    }
  };

  const addSet = (kind: SetRow["kind"]) => {
    const last = [...sets].reverse().find((s) => s.kind === kind) ?? sets[sets.length - 1];
    onChange([...sets, { kind, weightKg: last?.weightKg ?? 20, reps: last?.reps ?? 10, done: false }]);
  };

  const group = (kind: SetRow["kind"]) =>
    sets.map((s, i) => ({ s, i })).filter(({ s }) => s.kind === kind);

  const SetLine = ({ s, i, no }: { s: SetRow; i: number; no: number }) => (
    <div className={`flex items-center gap-2 rounded-2xl px-2.5 py-2 ${s.done ? "bg-volt/10" : "bg-white/[0.04]"}`}>
      <button
        onClick={() => update(i, { done: !s.done })}
        className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg border-2 text-[13px] font-extrabold ${
          s.done ? "border-volt bg-volt text-black" : "border-white/15 text-white/40"
        }`}
        aria-label={`${no}세트 완료`}
      >
        {no}
      </button>
      {/* 중량 스테퍼 */}
      <div className="flex items-center gap-1">
        <button className="h-8 w-8 rounded-lg bg-white/[0.06] font-bold" onClick={() => update(i, { weightKg: Math.max(0, s.weightKg - 2.5) })}>−</button>
        <span className="w-14 text-center text-[13px] font-bold tabular-nums">{s.weightKg}kg</span>
        <button className="h-8 w-8 rounded-lg bg-white/[0.06] font-bold" onClick={() => update(i, { weightKg: s.weightKg + 2.5 })}>+</button>
      </div>
      {/* 횟수 스테퍼 */}
      <div className="flex items-center gap-1">
        <button className="h-8 w-8 rounded-lg bg-white/[0.06] font-bold" onClick={() => update(i, { reps: Math.max(1, s.reps - 1) })}>−</button>
        <span className="w-10 text-center text-[13px] font-bold tabular-nums">{s.reps}회</span>
        <button className="h-8 w-8 rounded-lg bg-white/[0.06] font-bold" onClick={() => update(i, { reps: s.reps + 1 })}>+</button>
      </div>
      <button
        className="ml-auto px-1 text-[14px] text-danger/80"
        onClick={() => onChange(sets.filter((_, idx) => idx !== i))}
        aria-label="세트 삭제"
      >✕</button>
    </div>
  );

  return (
    <BottomSheet open={!!exercise} onClose={onClose} tall>
      {/* 헤더 */}
      <div className="flex items-center gap-3">
        <div className="grid h-12 w-12 place-items-center rounded-lg border border-white/[0.06] bg-white/[0.04] text-2xl">{ex.em}</div>
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-lg font-extrabold">{ex.name}</h3>
          <div className="text-[12px] text-white/55">{ex.zone}구역 · {ex.equipment} · 휴식 {ex.restSec}초</div>
        </div>
      </div>

      {celebrate && (
        <div className="mt-3 flex items-center gap-3 rounded-lg border border-volt/40 bg-volt/10 px-4 py-2.5">
          <Mascot state="cheer" size={52} />
          <b className="text-[14px]">전 세트 완료! 오늘도 해냈다 🎉</b>
        </div>
      )}

      {/* 플레이어 + 도넛 */}
      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <AnimPlayer pattern={ex.pattern} level={ex.level} exId={ex.id} />
        <div className="rounded-lg border border-white/[0.06] bg-white/[0.03] p-3">
          <div className="lab mb-1">자극 기여</div>
          <MuscleDonut contrib={ex.contrib} />
        </div>
      </div>

      {/* 휴식 타이머 */}
      {rest !== null && (
        <div className="mt-3 flex items-center gap-3 rounded-lg border border-volt/50 bg-card px-4 py-2.5">
          <span className="text-[18px]">⏱️</span>
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/10">
            <div className="h-full bg-volt transition-all" style={{ width: `${(rest / ex.restSec) * 100}%` }} />
          </div>
          <b className="tabular-nums">{Math.floor(rest / 60)}:{String(rest % 60).padStart(2, "0")}</b>
          <button className="text-[12px] font-bold text-white/55" onClick={() => setRest(null)}>건너뛰기</button>
        </div>
      )}

      {/* 세트 그룹 */}
      {(["warmup", "working"] as const).map((kind) =>
        group(kind).length || kind === "working" ? (
          <div key={kind} className="mt-4">
            <div className="mb-1.5 flex items-center justify-between">
              <span className={`lab ${kind === "warmup" ? "!text-sky-400" : "!text-volt"}`}>
                {kind === "warmup" ? "웜업 세트" : "워킹 세트"}
              </span>
              <button className="text-[11.5px] font-bold text-white/55" onClick={() => addSet(kind)}>
                + 세트 추가
              </button>
            </div>
            <div className="space-y-1.5">
              {group(kind).map(({ s, i }, no) => (
                <SetLine key={i} s={s} i={i} no={no + 1} />
              ))}
            </div>
          </div>
        ) : null
      )}

      {/* 노트 + 팁 */}
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="개인 노트 (그립 넓이, 느낌 등)"
        rows={2}
        className="mt-4 w-full rounded-lg border border-white/10 bg-white/[0.04] px-3.5 py-2.5 text-[13px] outline-none placeholder:text-white/30 focus:border-volt"
      />
      <div className="mt-2 rounded-lg border border-gold/40 bg-gold/10 px-3.5 py-2.5 text-[12.5px] leading-relaxed">
        💡 <b>전문가 팁</b> — {ex.tip}
      </div>
      <ol className="mt-3 space-y-1.5">
        {ex.howto.map((h, i) => (
          <li key={i} className="flex gap-2 text-[12.5px] leading-relaxed text-white/70">
            <span className="grid h-4.5 w-4.5 shrink-0 place-items-center rounded-lg bg-volt text-[10px] font-extrabold text-black">{i + 1}</span>
            {h}
          </li>
        ))}
      </ol>

      {/* 추이 */}
      <div className="lab mb-2 mt-5">기록 추이</div>
      <PRChart />

      {/* Replace / 삭제 */}
      <div className="mt-4 flex gap-2">
        <PillButton variant="ghost" className="flex-1 !py-2.5 !text-[13px]" onClick={() => setShowAlt(!showAlt)}>
          🔄 다른 운동으로
        </PillButton>
        <PillButton variant="ghost" className="flex-1 !py-2.5 !text-[13px] !text-danger" onClick={() => { onDelete(); onClose(); }}>
          🗑 오늘 목록에서 삭제
        </PillButton>
      </div>
      {showAlt && (
        <div className="mt-2 space-y-1.5">
          {alternativesFor(ex.id).map((alt) => (
            <button
              key={alt.id}
              onClick={() => { onReplace(alt.id); setShowAlt(false); }}
              className="flex w-full items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.04] px-3.5 py-2.5 text-left"
            >
              <span>{alt.em}</span>
              <b className="text-[13.5px]">{alt.name}</b>
              <span className="ml-auto text-[11px] text-white/40">{alt.equipment}</span>
            </button>
          ))}
          {alternativesFor(ex.id).length === 0 && (
            <p className="text-[12px] text-white/40">같은 부위 대체 운동이 없어요 (mock)</p>
          )}
        </div>
      )}
    </BottomSheet>
  );
}

export { byId };
