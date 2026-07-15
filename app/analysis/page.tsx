"use client";
// 분석 탭 — 질문형 카드 + CTA 실동작 + 3대 챌린지 + 표준 기준 비교
import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { AnalysisCard } from "@/components/analysis/AnalysisCard";
import { Big3Card } from "@/components/analysis/Big3Card";
import { RecoveryMap } from "@/components/recovery/RecoveryMap";
import { PRChart } from "@/components/charts/PRChart";
import { VolumeGroupedBar } from "@/components/charts/VolumeGroupedBar";
import { BalanceRadar, StandardRadar } from "@/components/charts/RadarCompare";
import { getMockRecovery } from "@/lib/mock/recovery";
import { BALANCE_RADAR, PEER_RADAR } from "@/lib/mock/routines";
import { useUser } from "@/lib/useUser";

export default function AnalysisPage() {
  const router = useRouter();
  const { user, saveBig3 } = useUser();
  const recovery = useMemo(() => getMockRecovery(), []);

  return (
    <main className="space-y-4 lg:grid lg:grid-cols-2 lg:items-start lg:gap-4 lg:space-y-0 lg:pt-24">
      <div className="rounded-3xl border border-white/[0.06] bg-card p-4 lg:col-span-2">
        <RecoveryMap data={recovery} />
      </div>

      <AnalysisCard question="이번 주 볼륨, 지난주보다 늘었을까?" cta="오늘 세트 기록하러 가기" onCta={() => router.push("/today")}>
        <VolumeGroupedBar />
      </AnalysisCard>

      <AnalysisCard question="내 몸, 골고루 크고 있을까?" cta="부족한 부위 루틴 받기" onCta={() => router.push("/routine")}>
        <BalanceRadar data={BALANCE_RADAR} />
      </AnalysisCard>

      <AnalysisCard question="권장 기준 대비, 나는 잘하고 있을까?" cta="랭킹에서 순위 보기" onCta={() => router.push("/ranking")}>
        <StandardRadar data={PEER_RADAR} />
      </AnalysisCard>

      <AnalysisCard question="내 기록, 자라고 있을까?">
        <PRChart selectable />
      </AnalysisCard>

      <AnalysisCard question="3대 500, 어디까지 왔을까?">
        <Big3Card big3={user?.big3} onSave={saveBig3} />
      </AnalysisCard>
    </main>
  );
}
