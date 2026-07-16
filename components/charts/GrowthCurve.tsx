"use client";
// Before/After 성장 곡선 — volt→gold 채움, path draw, 2선 비교 (스펙 P2-12)
import { motion, useReducedMotion } from "framer-motion";
import { GROWTH } from "@/lib/mock/routines";

// 위쪽에 라벨 공간(padTop) 확보 — AFTER 텍스트 잘림 방지
function makeY(H: number, padTop: number, padBottom: number) {
  const max = Math.max(...GROWTH.withPlan);
  return (v: number) => H - padBottom - (v / max) * (H - padBottom - padTop);
}
function toPath(vals: number[], W: number, padX: number, y: (v: number) => number) {
  const x = (i: number) => padX + (i / (vals.length - 1)) * (W - padX * 2);
  return vals.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ");
}

export function GrowthCurve() {
  const reduce = useReducedMotion();
  const W = 340, H = 170, padX = 18, padTop = 34, padBottom = 18;
  const y = makeY(H, padTop, padBottom);
  const planPath = toPath(GROWTH.withPlan, W, padX, y);
  const noPath = toPath(GROWTH.withoutPlan, W, padX, y);
  const endY = y(GROWTH.withPlan.at(-1)!);
  const endYNo = y(GROWTH.withoutPlan.at(-1)!);

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
        <defs>
          <linearGradient id="growth" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#c8ff00" />
            <stop offset="100%" stopColor="#f59e0b" />
          </linearGradient>
        </defs>
        {/* 계획 없음 (회색 점선) */}
        <motion.path
          d={noPath} fill="none" stroke="rgba(255,255,255,0.25)" strokeWidth={2} strokeDasharray="4 5"
          initial={reduce ? false : { pathLength: 0 }}
          whileInView={{ pathLength: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1.1, ease: "easeOut" }}
        />
        {/* 계획 있음 (volt→gold) */}
        <motion.path
          d={planPath} fill="none" stroke="url(#growth)" strokeWidth={3.5} strokeLinecap="round"
          initial={reduce ? false : { pathLength: 0 }}
          whileInView={{ pathLength: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1.3, ease: "easeOut" }}
        />
        {/* Before / After 핀 */}
        <motion.g
          initial={reduce ? false : { scale: 0, opacity: 0 }}
          whileInView={{ scale: 1, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 1.2, type: "spring", stiffness: 300 }}
        >
          <circle cx={padX} cy={y(0)} r={5} fill="#c8ff00" />
          <circle cx={W - padX} cy={endY} r={6} fill="#f59e0b" />
          <text x={padX + 8} y={y(0) - 8} fontSize={10} fill="rgba(255,255,255,0.6)">BEFORE</text>
          <text x={W - padX - 12} y={endY - 12} fontSize={11} fill="#f59e0b" textAnchor="end" fontWeight={700}>AFTER +{GROWTH.withPlan.at(-1)}%</text>
          <text x={W - padX - 12} y={endYNo - 10} fontSize={9} fill="rgba(255,255,255,0.35)" textAnchor="end">계획 없이 +{GROWTH.withoutPlan.at(-1)}%</text>
        </motion.g>
      </svg>
      <p className="mt-1 text-center text-[12px] text-white/55">
        플랜을 따라간 8주 vs 대충 한 8주 — <b className="text-gold">3배</b> 차이
      </p>
    </div>
  );
}
