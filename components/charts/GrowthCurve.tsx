"use client";
// Before/After 성장 곡선 — volt→gold 채움, path draw, 2선 비교 (스펙 P2-12)
import { motion, useReducedMotion } from "framer-motion";
import { GROWTH } from "@/lib/mock/routines";

function toPath(vals: number[], W: number, H: number, pad: number) {
  const max = Math.max(...GROWTH.withPlan);
  const x = (i: number) => pad + (i / (vals.length - 1)) * (W - pad * 2);
  const y = (v: number) => H - pad - (v / max) * (H - pad * 2);
  return vals.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ");
}

export function GrowthCurve() {
  const reduce = useReducedMotion();
  const W = 340, H = 150, pad = 16;
  const planPath = toPath(GROWTH.withPlan, W, H, pad);
  const noPath = toPath(GROWTH.withoutPlan, W, H, pad);
  const max = Math.max(...GROWTH.withPlan);
  const endY = H - pad - (GROWTH.withPlan.at(-1)! / max) * (H - pad * 2);
  const endYNo = H - pad - (GROWTH.withoutPlan.at(-1)! / max) * (H - pad * 2);

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
        <defs>
          <linearGradient id="growth" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#ccff00" />
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
          <circle cx={pad} cy={H - pad} r={5} fill="#ccff00" />
          <circle cx={W - pad} cy={endY} r={6} fill="#f59e0b" />
          <text x={pad + 8} y={H - pad - 6} fontSize={10} fill="rgba(255,255,255,0.6)">BEFORE</text>
          <text x={W - pad - 8} y={endY - 10} fontSize={10} fill="#f59e0b" textAnchor="end" fontWeight={700}>AFTER +{GROWTH.withPlan.at(-1)}%</text>
          <text x={W - pad - 8} y={endYNo - 8} fontSize={9} fill="rgba(255,255,255,0.35)" textAnchor="end">계획 없이 +{GROWTH.withoutPlan.at(-1)}%</text>
        </motion.g>
      </svg>
      <p className="mt-1 text-center text-[12px] text-white/55">
        플랜을 따라간 8주 vs 대충 한 8주 — <b className="text-gold">3배</b> 차이
      </p>
    </div>
  );
}
