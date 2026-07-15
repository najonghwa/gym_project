"use client";
// 분석 탭 — P1-5 질문형 카드 리듬 + P0-1 회복맵 + P0-3 PR + P2-12 성장곡선
import { useMemo } from "react";
import { AnalysisCard } from "@/components/analysis/AnalysisCard";
import { RecoveryMap } from "@/components/recovery/RecoveryMap";
import { PRChart } from "@/components/charts/PRChart";
import { VolumeGroupedBar } from "@/components/charts/VolumeGroupedBar";
import { BalanceRadar, PeerRadar } from "@/components/charts/RadarCompare";
import { GrowthCurve } from "@/components/charts/GrowthCurve";
import { getMockRecovery } from "@/lib/mock/recovery";
import { BALANCE_RADAR, PEER_RADAR } from "@/lib/mock/routines";

export default function AnalysisPage() {
  const recovery = useMemo(() => getMockRecovery(), []);
  return (
    <main className="space-y-4 lg:grid lg:grid-cols-2 lg:items-start lg:gap-4 lg:space-y-0 lg:pt-16">
      <div className="rounded-3xl border border-white/[0.06] bg-card p-4 lg:col-span-2">
        <RecoveryMap data={recovery} />
      </div>

      <AnalysisCard question="이번 주 볼륨, 지난주보다 늘었을까?" cta="세트 기록 보러 가기">
        <VolumeGroupedBar />
      </AnalysisCard>

      <AnalysisCard question="내 몸, 골고루 크고 있을까?" cta="부족한 부위 루틴 받기">
        <BalanceRadar data={BALANCE_RADAR} />
      </AnalysisCard>

      <AnalysisCard question="같은 목표 동료들 사이에서 나는?" cta="랭킹 전체 보기">
        <PeerRadar data={PEER_RADAR} />
      </AnalysisCard>

      <AnalysisCard question="벤치프레스, 기록이 자라고 있을까?">
        <PRChart />
      </AnalysisCard>

      <AnalysisCard question="플랜대로 8주를 가면 어떻게 될까?" cta="내 플랜 확인">
        <GrowthCurve />
      </AnalysisCard>
    </main>
  );
}
