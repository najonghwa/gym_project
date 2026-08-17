"use client";
// 온보딩 키트 — 진행바 / 주횟수 슬라이더 / 라이브 BMI 게이지 (스펙 P1-8)
import { motion, useReducedMotion } from "framer-motion";
import CountUp from "react-countup";

// ── 진행바 (볼트 채움) ──
export function ProgressBar({ pct }: { pct: number }) {
  const reduce = useReducedMotion();
  return (
    <div className="h-2 overflow-hidden rounded-full bg-white/10">
      <motion.div
        className="h-full rounded-full bg-volt"
        initial={reduce ? false : { width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 0.4 }}
      />
    </div>
  );
}

// ── 주횟수 dot 슬라이더 + 추천 문구 ──
export function FrequencySlider({
  stops,
  value,
  recommend,
  onChange,
  preview,
}: {
  stops: number[];
  value: number;
  recommend: number;
  onChange: (v: number) => void;
  preview?: (v: number) => string; // 러닝: 목표 심박 등 라이브 프리뷰
}) {
  const reduce = useReducedMotion();
  return (
    <div>
      <div className="relative mx-2 flex items-center justify-between">
        <div className="absolute left-0 right-0 top-1/2 h-1 -translate-y-1/2 rounded-full bg-white/10" />
        {stops.map((s) => (
          <button
            key={s}
            onClick={() => onChange(s)}
            className="relative z-10 flex flex-col items-center gap-1.5 py-2"
            aria-label={`주 ${s}회`}
          >
            <motion.span
              animate={reduce ? undefined : { scale: value === s ? 1.35 : 1 }}
              className={`grid h-6 w-6 place-items-center rounded-full text-[10px] font-extrabold ${
                value === s ? "bg-volt text-black" : "bg-white/15 text-white/50"
              }`}
            >
              {s}
            </motion.span>
            {s === recommend && (
              <span className={`text-[9px] font-bold ${value === s ? "text-volt" : "text-white/35"}`}>추천</span>
            )}
          </button>
        ))}
      </div>
      <p className="mt-1 text-center text-[13px] font-bold text-volt">
        주 {value}회{value === recommend ? " — 딱 좋아요" : value > recommend ? " — 의욕 넘치는데요?!" : " — 가볍게 시작!"}
      </p>
      {preview && <p className="mt-0.5 text-center text-[11.5px] text-white/50">{preview(value)}</p>}
    </div>
  );
}

// ── 라이브 BMI 게이지 (색 세그먼트 + 마커 + 카운트업) ──
const SEGMENTS = [
  { to: 18.5, color: "#38bdf8", label: "저체중" },
  { to: 23, color: "#c8ff00", label: "정상" },
  { to: 25, color: "#f59e0b", label: "과체중" },
  { to: 35, color: "#ef4444", label: "비만" },
];
const MIN = 14, MAX = 35;

export function LiveGauge({ heightCm, weightKg }: { heightCm: number; weightKg: number }) {
  const reduce = useReducedMotion();
  const bmi = weightKg / Math.pow(heightCm / 100, 2);
  const clamped = Math.min(MAX, Math.max(MIN, bmi));
  const pos = ((clamped - MIN) / (MAX - MIN)) * 100;
  const seg = SEGMENTS.find((s) => bmi < s.to) ?? SEGMENTS.at(-1)!;

  return (
    <div>
      <div className="flex items-baseline justify-center gap-2">
        <span className="font-display text-[44px] leading-none" style={{ color: seg.color }}>
          {reduce ? bmi.toFixed(1) : <CountUp end={bmi} decimals={1} duration={0.6} preserveValue />}
        </span>
        <span className="text-[13px] font-bold" style={{ color: seg.color }}>BMI · {seg.label}</span>
      </div>
      <div className="relative mt-3">
        <div className="flex h-3 overflow-hidden rounded-full">
          {SEGMENTS.map((s, i) => {
            const from = i === 0 ? MIN : SEGMENTS[i - 1].to;
            return (
              <div key={s.label} style={{ width: `${((s.to - from) / (MAX - MIN)) * 100}%`, background: s.color, opacity: 0.75 }} />
            );
          })}
        </div>
        <motion.div
          className="absolute -top-1.5 h-6 w-1.5 rounded-full bg-white shadow"
          animate={{ left: `${pos}%` }}
          transition={reduce ? { duration: 0 } : { type: "spring", stiffness: 150, damping: 18 }}
          style={{ translateX: "-50%" }}
        />
      </div>
      <div className="mt-1.5 flex justify-between text-[9.5px] text-white/35">
        <span>저체중</span><span>정상</span><span>과체중</span><span>비만</span>
      </div>
    </div>
  );
}
