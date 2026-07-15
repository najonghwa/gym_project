"use client";
// 3대 챌린지 — 스쿼트+벤치+데드 합계 목표 (구버전 big3 데이터 그대로 사용)
import { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import confetti from "canvas-confetti";
import { BottomSheet } from "@/components/ui/BottomSheet";
import { PillButton } from "@/components/ui/PillButton";
import { Mascot } from "@/components/mascot/Mascot";
import type { UserData } from "@/lib/supa";

const GOALS = [200, 250, 300, 350, 400, 500];

export function Big3Card({
  big3,
  onSave,
}: {
  big3: UserData["big3"];
  onSave: (goal: number, log?: { s: number; b: number; d: number }) => void;
}) {
  const reduce = useReducedMotion();
  const [open, setOpen] = useState(false);
  const [goal, setGoal] = useState(big3?.goal ?? 300);
  const [s, setS] = useState(big3?.logs?.at(-1)?.s ?? 0);
  const [b, setB] = useState(big3?.logs?.at(-1)?.b ?? 0);
  const [d, setD] = useState(big3?.logs?.at(-1)?.d ?? 0);

  const last = big3?.logs?.at(-1);
  const total = last ? Math.round((last.s + last.b + last.d) * 10) / 10 : 0;
  const pct = last && big3 ? Math.min(100, Math.round((total / big3.goal) * 100)) : 0;
  const first = big3?.logs?.[0];
  const grow = first && last ? Math.round((total - (first.s + first.b + first.d)) * 10) / 10 : 0;

  const save = () => {
    if (!s && !b && !d) return;
    onSave(goal, { s, b, d });
    setOpen(false);
    if (!reduce && s + b + d >= goal)
      confetti({ particleCount: 120, spread: 80, origin: { y: 0.6 }, colors: ["#ccff00", "#f59e0b", "#fff"] });
  };

  return (
    <>
      {!last ? (
        <div className="text-center">
          <div className="flex justify-center"><Mascot state="talk" size={64} /></div>
          <p className="mt-2 text-[13px] leading-relaxed text-white/60">
            스쿼트+벤치+데드 합계로 도전!<br />
            <span className="text-[11.5px] text-white/40">3대 300 = 헬린이 졸업 · 400 = 중수 · 500 = 헬창 인증</span>
          </p>
          <PillButton className="mt-4 w-full !py-3" onClick={() => setOpen(true)}>🏆 도전 시작</PillButton>
        </div>
      ) : (
        <div>
          <div className="flex items-end gap-2">
            <span className="font-display text-[46px] leading-[0.85] text-gold">{total}</span>
            <span className="pb-1 text-[13px] font-bold text-white/55">
              / {big3!.goal}kg {grow > 0 && <span className="text-volt">(+{grow} 성장)</span>}
            </span>
            <button className="ml-auto pb-1 text-[12px] font-bold text-white/45" onClick={() => setOpen(true)}>
              📏 측정 기록
            </button>
          </div>
          <div className="relative mt-3 h-4 overflow-hidden rounded-full bg-white/10">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-amber-500 to-amber-300"
              initial={reduce ? false : { width: 0 }}
              whileInView={{ width: `${pct}%` }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
            />
            <span className={`absolute inset-0 grid place-items-center text-[10.5px] font-extrabold ${pct > 45 ? "text-amber-950" : "text-white/60"}`}>
              {pct}%
            </span>
          </div>
          <div className="mt-3 grid grid-cols-3 gap-2">
            {([["스쿼트 SQ", last.s], ["벤치 BP", last.b], ["데드 DL", last.d]] as const).map(([l, v]) => (
              <div key={l} className="rounded-2xl bg-white/[0.05] py-2.5 text-center">
                <div className="font-display text-[18px] leading-none">{v}<span className="text-[10px] text-white/40">kg</span></div>
                <div className="mt-1 text-[9.5px] text-white/45">{l}</div>
              </div>
            ))}
          </div>
          <p className="mt-2 text-[10.5px] text-white/35">마지막 측정 {last.date} · 4~8주마다 재측정 추천</p>
        </div>
      )}

      {/* 측정/목표 시트 */}
      <BottomSheet open={open} onClose={() => setOpen(false)}>
        <h3 className="text-lg font-extrabold">🏆 3대 측정 기록</h3>
        <p className="mt-0.5 text-[12.5px] text-white/50">오늘 잰 최고 무게(1RM)를 적어주세요.</p>
        <div className="lab mb-1.5 mt-4">목표 합계</div>
        <div className="grid grid-cols-3 gap-2">
          {GOALS.map((g) => (
            <button
              key={g}
              onClick={() => setGoal(g)}
              className={`rounded-xl border py-2.5 font-display text-[16px] ${
                goal === g ? "border-gold bg-gold/15 text-gold" : "border-white/10 bg-white/[0.04]"
              }`}
            >
              {g}
            </button>
          ))}
        </div>
        <div className="mt-4 space-y-2.5">
          {([["🏋️ 스쿼트", s, setS], ["🛏️ 벤치프레스", b, setB], ["⬆️ 데드리프트", d, setD]] as const).map(([l, v, set]) => (
            <div key={l} className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3">
              <span className="flex-1 text-[14px] font-bold">{l}</span>
              <input
                type="number" step={2.5} inputMode="decimal" value={v || ""}
                onChange={(e) => set(Number(e.target.value) || 0)}
                className="w-24 rounded-lg border border-white/10 bg-card px-2 py-2 text-center outline-none focus:border-volt"
              />
              <span className="text-[12px] text-white/45">kg</span>
            </div>
          ))}
        </div>
        <PillButton className="mt-5 w-full" onClick={save}>저장 ✅</PillButton>
      </BottomSheet>
    </>
  );
}
