"use client";
// "플랜 유저 vs 일반" 성장 비교 — Gymwork 2.1x 패턴을 볼트 톤으로
import { motion, useReducedMotion } from "framer-motion";

const W = 340, H = 170, padX = 16, padT = 30, padB = 26;
// 지수형 성장(플랜) vs 완만(일반)
const PLAN = [0, 1.2, 2.8, 5.2, 10.8];
const AVG = [0, 1.4, 2.6, 3.9, 5.1];
const MAX = 11;

const x = (i: number) => padX + (i / (PLAN.length - 1)) * (W - padX * 2 - 52);
const y = (v: number) => H - padB - (v / MAX) * (H - padB - padT);
const path = (vals: number[]) =>
  vals.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ");

export function GrowthCompare({ compact = false }: { compact?: boolean }) {
  const reduce = useReducedMotion();
  return (
    <div>
      <div className="flex items-end justify-between">
        <div>
          <div className="lab">GYM&RUN 플랜 유저 성장</div>
          <div className="text-[11px] text-white/40">12주 근성장 시뮬레이션 (데모)</div>
        </div>
        <span className="font-display text-[34px] leading-none text-volt">2.1x</span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className={`w-full ${compact ? "max-h-40" : ""}`}>
        {[0.25, 0.5, 0.75, 1].map((g) => (
          <line key={g} x1={padX} x2={W - padX} y1={y(MAX * g)} y2={y(MAX * g)} stroke="rgba(255,255,255,0.06)" />
        ))}
        {/* 일반 */}
        <motion.path
          d={path(AVG)} fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth={3} strokeLinecap="round"
          initial={reduce ? false : { pathLength: 0 }}
          whileInView={{ pathLength: 1 }} viewport={{ once: true }}
          transition={{ duration: 1 }}
        />
        {/* 플랜 */}
        <motion.path
          d={path(PLAN)} fill="none" stroke="#c8ff00" strokeWidth={4} strokeLinecap="round"
          initial={reduce ? false : { pathLength: 0 }}
          whileInView={{ pathLength: 1 }} viewport={{ once: true }}
          transition={{ duration: 1.2 }}
        />
        {/* 끝점 pill */}
        <motion.g
          initial={reduce ? false : { opacity: 0, scale: 0.7 }}
          whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }}
          transition={{ delay: 1.1, type: "spring", stiffness: 260 }}
        >
          <rect x={x(4) + 4} y={y(PLAN[4]) - 11} width={52} height={20} rx={10} fill="#c8ff00" />
          <text x={x(4) + 30} y={y(PLAN[4]) + 3} fontSize={10.5} fontWeight={800} textAnchor="middle" fill="#000">+10.8%</text>
          <rect x={x(4) + 4} y={y(AVG[4]) - 10} width={48} height={19} rx={9.5} fill="rgba(255,255,255,0.18)" />
          <text x={x(4) + 28} y={y(AVG[4]) + 3} fontSize={10} fontWeight={700} textAnchor="middle" fill="rgba(255,255,255,0.75)">+5.1%</text>
          <text x={x(4) + 4} y={y(AVG[4]) - 15} fontSize={9} fill="rgba(255,255,255,0.4)">일반 리프터</text>
        </motion.g>
        {["1주", "4주", "8주", "12주"].map((t, i) => (
          <text
            key={t}
            x={padX + (i / 3) * (W - padX * 2 - 52)}
            y={H - 8} fontSize={9.5} fill="rgba(255,255,255,0.35)" textAnchor="middle"
          >
            {t}
          </text>
        ))}
      </svg>
      {!compact && (
        <p className="text-center text-[11.5px] leading-relaxed text-white/40">
          회복도·볼륨을 반영한 플랜을 따라가면 같은 시간에 <b className="text-volt">2배 이상</b> 성장해요
        </p>
      )}
    </div>
  );
}
