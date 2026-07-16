"use client";
// 부위 상세 시트 — 최근 볼륨·최고중량·추이 (스펙 P0-1)
import { BottomSheet } from "@/components/ui/BottomSheet";
import { PRChart } from "@/components/charts/PRChart";
import { MUSCLE_KR, daysAgoLabel, type MuscleRecovery } from "@/lib/recovery";

// TODO(supabase): 부위별 실제 볼륨/중량 이력으로 대체
const MOCK_SUMMARY = { weeklySets: 12, bestKg: 65, avgReps: 9 };

export function MuscleSheet({
  data,
  onClose,
}: {
  data: MuscleRecovery | null;
  onClose: () => void;
}) {
  return (
    <BottomSheet open={!!data} onClose={onClose}>
      {data && (
        <>
          <h3 className="text-lg font-extrabold">
            {MUSCLE_KR[data.muscle]}{" "}
            <span
              className={`ml-1 text-[14px] ${
                data.pct >= 0.9 ? "text-volt" : data.pct >= 0.5 ? "text-gold" : "text-danger"
              }`}
            >
              회복 {Math.round(data.pct * 100)}%
            </span>
          </h3>
          <p className="mt-0.5 text-[12.5px] text-white/55">
            마지막 훈련 {daysAgoLabel(data.lastTrainedAt)}
            {data.pct >= 1 ? " · 싱싱해요! 오늘 치기 좋은 날 💪" : data.pct < 0.5 ? " · 아직 회복 중 — 다른 부위 추천" : ""}
          </p>
          <div className="mt-4 grid grid-cols-3 gap-2">
            {[
              ["주간 세트", `${MOCK_SUMMARY.weeklySets}set`],
              ["최고 중량", `${MOCK_SUMMARY.bestKg}kg`],
              ["평균 반복", `${MOCK_SUMMARY.avgReps}회`],
            ].map(([l, v]) => (
              <div key={l} className="rounded-lg bg-white/[0.05] py-2.5 text-center">
                <div className="font-display text-[16px] leading-none">{v}</div>
                <div className="mt-1 text-[10px] text-white/55">{l}</div>
              </div>
            ))}
          </div>
          <div className="lab mb-2 mt-5">중량 추이</div>
          <PRChart />
        </>
      )}
    </BottomSheet>
  );
}
