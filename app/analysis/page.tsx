"use client";
// 분석 탭 — P0-1 RecoveryMap + P0-3 PRChart
import { useMemo } from "react";
import { RecoveryMap } from "@/components/recovery/RecoveryMap";
import { PRChart } from "@/components/charts/PRChart";
import { getMockRecovery } from "@/lib/mock/recovery";

export default function AnalysisPage() {
  const recovery = useMemo(() => getMockRecovery(), []);
  return (
    <main className="space-y-4 lg:grid lg:grid-cols-2 lg:gap-4 lg:space-y-0 lg:pt-16">
      <div className="rounded-3xl border border-white/[0.06] bg-card p-4">
        <RecoveryMap data={recovery} />
      </div>
      <div className="rounded-3xl border border-white/[0.06] bg-card p-4">
        <div className="lab mb-3">PR 기록 — 바벨 벤치프레스</div>
        <PRChart />
      </div>
      {/* TODO(P1-5): AnalysisCard 질문형 카드(볼륨 그룹막대 / peer 레이더) */}
    </main>
  );
}
