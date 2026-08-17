"use client";
// 루틴 Explore — 필터 칩 + 테마 카드 + 저장/좋아요 (스펙 P1-7)
import { useMemo, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { fadeUp, staggerContainer } from "@/lib/motion";
import { ColorInitialBadge } from "@/components/ui/ColorInitialBadge";
import { BottomSheet } from "@/components/ui/BottomSheet";
import { PillButton } from "@/components/ui/PillButton";
import { byId, type Exercise } from "@/lib/mock/exercises";
import { ExThumb } from "@/components/ui/ExThumb";
import { ExerciseInfoSheet } from "@/components/workout/ExerciseInfoSheet";
import { EXPLORE, FILTER, type ExploreRoutine } from "@/lib/mock/routines";

function ChipRow({
  label, options, value, onChange,
}: { label: string; options: string[]; value: string; onChange: (v: string) => void }) {
  return (
    <div className="flex items-center gap-1.5 overflow-x-auto">
      <span className="lab shrink-0 !text-[9px]">{label}</span>
      {options.map((o) => (
        <button
          key={o}
          onClick={() => onChange(o)}
          className={`shrink-0 rounded-full border px-3 py-1.5 text-[11.5px] font-bold ${
            value === o ? "border-volt bg-volt text-black" : "border-white/15 bg-white/5 text-white/55"
          }`}
        >
          {o}
        </button>
      ))}
    </div>
  );
}

export function ExploreSection({
  savedIds = [],
  onToggleSave,
  onApply,
}: {
  savedIds?: string[];
  onToggleSave?: (id: string) => void;
  onApply?: (r: ExploreRoutine) => void;
}) {
  const reduce = useReducedMotion();
  const [level, setLevel] = useState("전체");
  const [likes, setLikes] = useState<Record<string, boolean>>({});
  const [detail, setDetail] = useState<ExploreRoutine | null>(null);
  const [exInfo, setExInfo] = useState<Exercise | null>(null); // 운동 그림 클릭 → 정보+애니메이션
  const isSaved = (id: string) => savedIds.includes(id);

  const list = useMemo(
    () => EXPLORE.filter((r) => level === "전체" || r.level === level),
    [level]
  );

  return (
    <section>
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-display text-[20px]">루틴 둘러보기 EXPLORE</h3>
        <span className="text-[11px] text-white/40">{list.length}개</span>
      </div>
      <ChipRow label="난이도" options={FILTER.level} value={level} onChange={setLevel} />

      <motion.div
        className="mt-3 grid gap-3 lg:grid-cols-2 lg:items-start"
        variants={reduce ? undefined : staggerContainer}
        initial={reduce ? false : "hidden"}
        animate="show"
      >
        {list.map((r, i) => (
          <motion.div
            key={r.id}
            variants={reduce ? undefined : fadeUp}
            className="rounded-2xl border border-white/[0.06] bg-card p-4"
          >
            <div className="flex items-start gap-3">
              <ColorInitialBadge text={r.badge} seed={i} />
              <button className="min-w-0 flex-1 text-left" onClick={() => setDetail(r)}>
                <b className="block text-[15px]">{r.title} <span className="text-[10px] text-white/35">자세히 ›</span></b>
                <span className="text-[12px] text-white/50">{r.desc}</span>
                <div className="mt-1.5 flex flex-wrap gap-1">
                  {[`${r.weeks}주`, `주 ${r.daysPerWeek}회`, `회당 ~${r.durationMin}분`, r.level].map((c) => (
                    <span key={c} className="rounded-md border border-white/10 bg-white/[0.05] px-1.5 py-0.5 text-[10.5px] text-white/55">{c}</span>
                  ))}
                </div>
              </button>
              {/* 좋아요 하트 pop */}
              <motion.button
                whileTap={reduce ? undefined : { scale: 1.4 }}
                onClick={() => setLikes((p) => ({ ...p, [r.id]: !p[r.id] }))}
                className={`text-[13px] font-bold ${likes[r.id] ? "text-danger" : "text-white/40"}`}
              >
                {r.likes + (likes[r.id] ? 1 : 0)}
              </motion.button>
            </div>
            {/* 구성 운동 픽토그램 — 클릭하면 정보+애니메이션 */}
            <div className="mt-3 flex items-center gap-1.5 overflow-x-auto">
              {r.exercises.map((id) => {
                const ex = byId(id);
                return ex ? (
                  <button key={id} onClick={() => setExInfo(ex)} aria-label={`${ex.name} 정보`}>
                    <ExThumb ex={ex} size={34} />
                  </button>
                ) : null;
              })}
            </div>
            <button
              onClick={() => onToggleSave?.(r.id)}
              className={`mt-3 w-full rounded-full py-2.5 text-[13px] font-extrabold transition ${
                isSaved(r.id) ? "bg-volt text-black" : "border border-white/15 bg-white/5 text-stone-100"
              }`}
            >
              {isSaved(r.id) ? "저장됨" : "저장하기"}
            </button>
          </motion.div>
        ))}
      </motion.div>

      {/* 루틴 상세 (Planfit 'About this Plan' 패턴) */}
      <BottomSheet open={!!detail} onClose={() => setDetail(null)} tall>
        {detail && (
          <>
            <div className="flex items-center gap-3">
              <ColorInitialBadge text={detail.badge} seed={0} />
              <div>
                <span className="rounded-md bg-volt/15 px-1.5 py-0.5 text-[10px] font-bold text-volt">{detail.level}</span>
                <h3 className="mt-1 font-display text-[22px] leading-tight">{detail.title}</h3>
              </div>
            </div>

            <div className="lab mb-1.5 mt-5">이 프로그램은</div>
            <p className="text-[13.5px] leading-relaxed text-white/75">{detail.overview}</p>

            {detail.who && (
              <>
                <div className="lab mb-1.5 mt-4">이런 분께</div>
                <p className="text-[13px] leading-relaxed text-white/65">{detail.who}</p>
              </>
            )}
            {detail.schedule && (
              <>
                <div className="lab mb-1.5 mt-4">주간 구성</div>
                <p className="rounded-lg bg-white/[0.05] px-3 py-2.5 text-[13px] font-bold leading-relaxed text-white/80">{detail.schedule}</p>
              </>
            )}

            <div className="lab mb-1.5 mt-5">루틴 소개</div>
            <div className="grid grid-cols-2 gap-2">
              {[
                ["빈도", `주 ${detail.daysPerWeek}회`],
                ["운동", `${Math.max(detail.exercises.length, 4)}~${Math.max(detail.exercises.length, 4) + 2}개`],
                ["⏱️ 소요", `${detail.durationMin}분`],
                ["칼로리", `${detail.kcal} kcal`],
              ].map(([l, v]) => (
                <div key={l} className="rounded-lg bg-white/[0.05] px-3 py-3 text-center">
                  <div className="text-[10.5px] text-white/45">{l}</div>
                  <div className="mt-1 font-display text-[17px]">{v}</div>
                </div>
              ))}
            </div>

            <div className="lab mb-1.5 mt-5">구성 운동 {detail.exercises.length}가지 <span className="font-normal normal-case text-white/35">— 누르면 하는 방법</span></div>
            <div className="grid grid-cols-2 gap-1.5">
              {detail.exercises.map((id) => {
                const ex = byId(id);
                return ex ? (
                  <button key={id} onClick={() => setExInfo(ex)} className="flex items-center gap-2 rounded-lg bg-white/[0.04] p-1.5 text-left">
                    <ExThumb ex={ex} size={30} />
                    <span className="min-w-0 flex-1 truncate text-[12px] font-bold text-white/75">{ex.name}</span>
                    <span className="shrink-0 pr-1 text-[11px] text-white/30">›</span>
                  </button>
                ) : null;
              })}
            </div>

            <PillButton
              className="mt-6 w-full py-4"
              onClick={() => {
                if (!isSaved(detail.id)) onToggleSave?.(detail.id);
                onApply?.(detail);
                setDetail(null);
              }}
            >
              이 플랜으로 오늘 운동 구성 ✅
            </PillButton>
          </>
        )}
      </BottomSheet>

      <ExerciseInfoSheet exercise={exInfo} onClose={() => setExInfo(null)} />
    </section>
  );
}
