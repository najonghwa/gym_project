"use client";
// 마스코트 "볼트" — 볼트 컬러의 심플·귀여운 덤벨 캐릭터 (스펙 §2-1)
// Lottie 자산 확보 전 폴백: 상태별 정적 SVG + framer-motion (스펙 허용)
import { motion, useReducedMotion, type TargetAndTransition } from "framer-motion";

export type MascotState = "idle" | "cheer" | "think" | "tired" | "sad" | "talk";

// 상태별 움직임
const MOTION: Record<MascotState, TargetAndTransition> = {
  idle:  { y: [0, -4, 0], transition: { duration: 2.2, repeat: Infinity, ease: "easeInOut" } },
  cheer: { y: [0, -14, 0], rotate: [0, -6, 6, 0], transition: { duration: 0.55, repeat: Infinity, repeatDelay: 0.25 } },
  think: { rotate: [0, 4, 0, -4, 0], transition: { duration: 2.6, repeat: Infinity, ease: "easeInOut" } },
  tired: { y: [0, 2, 0], transition: { duration: 3, repeat: Infinity, ease: "easeInOut" } },
  sad:   { y: [0, 1.5, 0], transition: { duration: 3.2, repeat: Infinity, ease: "easeInOut" } },
  talk:  { y: [0, -3, 0], transition: { duration: 1.6, repeat: Infinity, ease: "easeInOut" } },
};

export function Mascot({ state = "idle", size = 96 }: { state?: MascotState; size?: number }) {
  const reduce = useReducedMotion();
  const cheerArms = state === "cheer";
  const droop = state === "tired" || state === "sad";

  // 눈/입 상태
  const eyes =
    state === "tired" ? (
      <>
        <line x1="38" y1="46" x2="46" y2="46" stroke="#050505" strokeWidth="3" strokeLinecap="round" />
        <line x1="58" y1="46" x2="66" y2="46" stroke="#050505" strokeWidth="3" strokeLinecap="round" />
      </>
    ) : state === "cheer" ? (
      <>
        <path d="M37 46 q5 -6 10 0" stroke="#050505" strokeWidth="3" fill="none" strokeLinecap="round" />
        <path d="M57 46 q5 -6 10 0" stroke="#050505" strokeWidth="3" fill="none" strokeLinecap="round" />
      </>
    ) : (
      <>
        <circle cx="42" cy="46" r="3.6" fill="#050505" />
        <circle cx="62" cy="46" r="3.6" fill="#050505" />
      </>
    );

  const mouth =
    state === "cheer" || state === "talk" ? (
      <path d="M44 56 q8 9 16 0" stroke="#050505" strokeWidth="3.2" fill="none" strokeLinecap="round" />
    ) : state === "sad" ? (
      <path d="M45 61 q7 -6 14 0" stroke="#050505" strokeWidth="3.2" fill="none" strokeLinecap="round" />
    ) : state === "tired" ? (
      <ellipse cx="52" cy="58" rx="4" ry="5" fill="#050505" />
    ) : (
      <path d="M46 57 q6 5 12 0" stroke="#050505" strokeWidth="3.2" fill="none" strokeLinecap="round" />
    );

  return (
    <motion.div
      style={{ width: size, height: size }}
      animate={reduce ? undefined : MOTION[state]}
      aria-label={`마스코트 (${state})`}
    >
      <svg viewBox="0 0 104 104" width="100%" height="100%">
        {/* 팔 = 미니 덤벨 (cheer면 위로) */}
        <g stroke="#a3cc00" strokeWidth="6" strokeLinecap="round">
          <line x1="16" y1={cheerArms ? 30 : droop ? 72 : 58} x2="28" y2={droop ? 66 : 54} />
          <line x1="88" y1={cheerArms ? 30 : droop ? 72 : 58} x2="76" y2={droop ? 66 : 54} />
        </g>
        <g fill="#3f4a00">
          <rect x="10" y={cheerArms ? 22 : droop ? 66 : 51} width="10" height="14" rx="3" />
          <rect x="84" y={cheerArms ? 22 : droop ? 66 : 51} width="10" height="14" rx="3" />
        </g>
        {/* 몸통 (볼트색 블롭) */}
        <ellipse cx="52" cy="54" rx="30" ry="32" fill="#ccff00" />
        <ellipse cx="52" cy="54" rx="30" ry="32" fill="none" stroke="#a3cc00" strokeWidth="2" />
        {/* 헤어(번개 꼭지) */}
        <path d="M50 22 l8 -10 -3 8 7 -3 -9 11z" fill="#ccff00" stroke="#a3cc00" strokeWidth="1.5" />
        {/* 얼굴 */}
        {eyes}
        {mouth}
        {/* 볼터치 */}
        <circle cx="34" cy="55" r="3.5" fill="#a3cc00" opacity="0.55" />
        <circle cx="70" cy="55" r="3.5" fill="#a3cc00" opacity="0.55" />
        {/* 상태 소품 */}
        {state === "think" && (
          <g fill="#ccff00">
            <circle cx="86" cy="24" r="3" /><circle cx="93" cy="16" r="4.5" /><circle cx="80" cy="30" r="2" />
          </g>
        )}
        {state === "tired" && <ellipse cx="76" cy="34" rx="4" ry="6" fill="#38bdf8" opacity="0.9" />}
        {state === "sad" && <ellipse cx="63" cy="54" rx="2.5" ry="4.5" fill="#38bdf8" opacity="0.9" />}
      </svg>
    </motion.div>
  );
}
