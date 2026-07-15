// 회복도 mock — 부위별 마지막 훈련 시각 (스펙 P0-1)
// TODO(supabase): workouts 테이블에서 부위별 마지막 세션으로 대체
import { Muscle, MuscleRecovery, recoveryPct } from "@/lib/recovery";

const hoursAgo = (h: number) => new Date(Date.now() - h * 36e5).toISOString();

const LAST: Record<Muscle, string> = {
  chest: hoursAgo(20),      // 어제 벤치 — 아직 빨강~골드
  triceps: hoursAgo(20),
  shoulders: hoursAgo(45),  // 이틀 전 — 거의 회복
  back: hoursAgo(70),       // 3일 전 — 완전 회복 직전
  biceps: hoursAgo(70),
  legs: hoursAgo(96),       // 4일 전 — 싱싱함
  glutes: hoursAgo(96),
  abs: hoursAgo(8),         // 오늘 아침 — 빨강
};

export function getMockRecovery(): MuscleRecovery[] {
  return (Object.keys(LAST) as Muscle[]).map((m) => ({
    muscle: m,
    lastTrainedAt: LAST[m],
    pct: recoveryPct(m, LAST[m]),
  }));
}
