// 근육 회복도 계산 + 색상 (스펙 P0-1)
// 회복도 = min(1, (now - lastTrainedAt) / recoveryHours[muscle])
import { interpolateRgb } from "d3-interpolate";

export type Muscle =
  | "chest" | "back" | "shoulders" | "biceps" | "triceps"
  | "legs" | "abs" | "glutes";

export interface MuscleRecovery {
  muscle: Muscle;
  pct: number;          // 0~1 (1 = 완전 회복)
  lastTrainedAt: string; // ISO
}

export const MUSCLE_KR: Record<Muscle, string> = {
  chest: "가슴", back: "등", shoulders: "어깨", biceps: "이두",
  triceps: "삼두", legs: "하체", abs: "복근", glutes: "둔근",
};

// 대근육 72h, 소근육 48h
export const RECOVERY_HOURS: Record<Muscle, number> = {
  chest: 72, back: 72, legs: 72, glutes: 72,
  shoulders: 48, biceps: 48, triceps: 48, abs: 48,
};

export function recoveryPct(muscle: Muscle, lastTrainedAt: string, now = Date.now()): number {
  const elapsed = (now - new Date(lastTrainedAt).getTime()) / 36e5; // hours
  return Math.min(1, Math.max(0, elapsed / RECOVERY_HOURS[muscle]));
}

// danger(0) → gold(0.5) → volt(1)
// 피로(빨강) → 회복 중(주황) → 회복 완료(초록) — 액센트 오렌지와 구분되게 완료는 그린
const lowHalf = interpolateRgb("#ef4444", "#f59e0b");
const highHalf = interpolateRgb("#f59e0b", "#2dd4a0");
export function recoveryColor(pct: number): string {
  const p = Math.min(1, Math.max(0, pct));
  return p < 0.5 ? lowHalf(p * 2) : highHalf((p - 0.5) * 2);
}

export function daysAgoLabel(iso: string, now = Date.now()): string {
  const h = (now - new Date(iso).getTime()) / 36e5;
  if (h < 1) return "방금 전";
  if (h < 24) return `${Math.floor(h)}시간 전`;
  return `${Math.floor(h / 24)}일 전`;
}
