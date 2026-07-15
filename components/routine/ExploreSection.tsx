"use client";
// 루틴 Explore — 필터 칩 + 테마 카드 + 저장/좋아요 (스펙 P1-7)
import { useMemo, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { fadeUp, staggerContainer } from "@/lib/motion";
import { ColorInitialBadge } from "@/components/ui/ColorInitialBadge";
import { byId } from "@/lib/mock/exercises";
import { EXPLORE, FILTER } from "@/lib/mock/routines";
import { MUSCLE_KR } from "@/lib/recovery";

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

export function ExploreSection() {
  const reduce = useReducedMotion();
  const [target, setTarget] = useState("전체");
  const [equipment, setEquipment] = useState("전체");
  const [level, setLevel] = useState("전체");
  const [likes, setLikes] = useState<Record<string, boolean>>({});
  const [saved, setSaved] = useState<Record<string, boolean>>({});

  const list = useMemo(
    () =>
      EXPLORE.filter(
        (r) =>
          (target === "전체" || r.target === target) &&
          (equipment === "전체" || r.equipment.includes(equipment)) &&
          (level === "전체" || r.level === level)
      ),
    [target, equipment, level]
  );

  return (
    <section>
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-display text-[20px]">루틴 둘러보기 EXPLORE</h3>
        <span className="text-[11px] text-white/40">{list.length}개</span>
      </div>
      <div className="space-y-1.5">
        <ChipRow label="부위" options={FILTER.target} value={target} onChange={setTarget} />
        <ChipRow label="장비" options={FILTER.equipment} value={equipment} onChange={setEquipment} />
        <ChipRow label="난이도" options={FILTER.level} value={level} onChange={setLevel} />
      </div>

      <motion.div
        className="mt-3 space-y-3"
        variants={reduce ? undefined : staggerContainer}
        initial={reduce ? false : "hidden"}
        animate="show"
      >
        {list.map((r, i) => (
          <motion.div
            key={r.id}
            variants={reduce ? undefined : fadeUp}
            className="rounded-3xl border border-white/[0.06] bg-card p-4"
          >
            <div className="flex items-start gap-3">
              <ColorInitialBadge text={r.badge} seed={i} />
              <div className="min-w-0 flex-1">
                <b className="block text-[15px]">{r.title}</b>
                <span className="text-[12px] text-white/50">{r.desc}</span>
                <div className="mt-1.5 flex flex-wrap gap-1">
                  {[`${r.weeks}주`, `주 ${r.daysPerWeek}회`, r.level, r.equipment].map((c) => (
                    <span key={c} className="rounded-md border border-white/10 bg-white/[0.05] px-1.5 py-0.5 text-[10.5px] text-white/55">{c}</span>
                  ))}
                </div>
              </div>
              {/* 좋아요 하트 pop */}
              <motion.button
                whileTap={reduce ? undefined : { scale: 1.4 }}
                onClick={() => setLikes((p) => ({ ...p, [r.id]: !p[r.id] }))}
                className={`text-[13px] font-bold ${likes[r.id] ? "text-danger" : "text-white/40"}`}
              >
                {likes[r.id] ? "❤️" : "🤍"} {r.likes + (likes[r.id] ? 1 : 0)}
              </motion.button>
            </div>
            {/* 부위 썸네일 + 운동 미리보기 */}
            <div className="mt-3 flex items-center gap-1.5 overflow-x-auto">
              {r.muscles.map((m) => (
                <span key={m} className="shrink-0 rounded-full bg-volt/15 px-2.5 py-1 text-[10.5px] font-bold text-volt">{MUSCLE_KR[m]}</span>
              ))}
              <span className="text-white/20">|</span>
              {r.exercises.map((id) => {
                const ex = byId(id);
                return ex ? <span key={id} className="shrink-0 text-[15px]" title={ex.name}>{ex.em}</span> : null;
              })}
            </div>
            <button
              onClick={() => setSaved((p) => ({ ...p, [r.id]: !p[r.id] }))}
              className={`mt-3 w-full rounded-full py-2.5 text-[13px] font-extrabold transition ${
                saved[r.id] ? "bg-volt text-black" : "border border-white/15 bg-white/5 text-zinc-100"
              }`}
            >
              {saved[r.id] ? "✓ 저장됨 — 내 루틴에서 확인" : "💾 저장하기"}
            </button>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}
