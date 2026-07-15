"use client";
// P0-4 오늘 탭 홈 — MascotBubble + Streak + WeekStrip + TodayWorkout + MiniStats
import { useEffect, useMemo, useState } from "react";
import { MascotBubble } from "@/components/mascot/MascotBubble";
import { StreakNumber } from "@/components/ui/StreakNumber";
import { StatChip } from "@/components/ui/StatChip";
import { WeekStrip, type DayCell } from "@/components/today/WeekStrip";
import { TodayWorkoutCard } from "@/components/today/TodayWorkoutCard";
import { ExerciseSheet } from "@/components/workout/ExerciseSheet";
import { AchievementModal } from "@/components/celebrate/AchievementModal";
import { dailyQuote } from "@/lib/mock/quotes";
import { byId, getMockToday, type TodayItem } from "@/lib/mock/exercises";
import { getMockRecovery } from "@/lib/mock/recovery";
import { computeStats, useUser, weekCells } from "@/lib/useUser";
import { LoginCard } from "@/components/auth/LoginCard";

export default function TodayPage() {
  const { user, ready, login, signup, saveToday, today } = useUser();
  const [items, setItems] = useState<TodayItem[]>(getMockToday);
  const [openId, setOpenId] = useState<string | null>(null);
  const [celebrated, setCelebrated] = useState(false);
  const [showBadge, setShowBadge] = useState(false);
  const quote = useMemo(() => dailyQuote(), []);

  // 로그인되면 오늘 저장분(서버/로컬) 복원
  const loadedFor = useMemo(() => user?.id, [user?.id]);
  useEffect(() => {
    if (!user) return;
    const saved = user.v2?.workouts?.[today()];
    if (saved?.items?.length) setItems(saved.items as TodayItem[]);
    else setItems(getMockToday()); // TODO(supabase): 루틴 기반 오늘 플랜 생성으로 대체
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loadedFor]);

  // 실데이터 스트릭/주간 스트립
  const stats = useMemo(() => (user ? computeStats(user) : null), [user, items]);
  const week: DayCell[] = useMemo(
    () => (user ? weekCells(user) : []),
    [user, items]
  );

  // P2-10 컨디션% = 회복맵 평균 연동, 예상 시간 = 세트 수 × 2.5분
  const condition = useMemo(() => {
    const rec = getMockRecovery();
    return Math.round((rec.reduce((s, r) => s + r.pct, 0) / rec.length) * 100);
  }, []);
  const totalSets = items.reduce((s, it) => s + it.sets.length, 0);
  const doneSets = items.reduce((s, it) => s + it.sets.filter((x) => x.done).length, 0);
  const estMin = Math.round(totalSets * 2.5);

  // P2-11 전체 완료 → 축하 모달 (1회)
  useEffect(() => {
    if (!celebrated && totalSets > 0 && doneSets === totalSets) {
      setCelebrated(true);
      setShowBadge(true);
    }
  }, [doneSets, totalSets, celebrated]);

  const updateItems = (next: TodayItem[]) => {
    setItems(next);
    saveToday(next); // localStorage + Supabase 저장
  };

  const toggleSet = (exerciseId: string, setIndex: number) =>
    updateItems(
      items.map((it) =>
        it.exerciseId === exerciseId
          ? { ...it, sets: it.sets.map((s, i) => (i === setIndex ? { ...s, done: !s.done } : s)) }
          : it
      )
    );

  const openItem = items.find((it) => it.exerciseId === openId) ?? null;

  // 로그인 게이트
  if (!ready) return null;
  if (!user) {
    return (
      <main className="lg:pt-20">
        <LoginCard onLogin={login} onSignup={signup} />
      </main>
    );
  }

  return (
    <main className="space-y-4 lg:grid lg:grid-cols-5 lg:items-start lg:gap-5 lg:space-y-0 lg:pt-20">
      {/* 왼쪽 컬럼 (데스크탑) / 순서대로 (모바일) */}
      <div className="space-y-4 lg:col-span-2">
        {/* P2-10 헤더 칩: 예상 소요 + 컨디션%(회복맵 연동) */}
        <div className="flex gap-2">
          <span className="flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-[12px] font-bold">
            ⏱️ 예상 <b className="text-volt">{estMin}분</b>
          </span>
          <span className="flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-[12px] font-bold">
            ⚡ 컨디션 <b className={condition >= 80 ? "text-volt" : condition >= 50 ? "text-gold" : "text-danger"}>{condition}%</b>
          </span>
        </div>

        <MascotBubble quote={quote} />

        <div className="rounded-3xl border border-white/[0.06] bg-card p-4">
          <div className="lab mb-1">연속 운동 STREAK · {String(user.id)}</div>
          <StreakNumber value={stats?.streak ?? 0} />
          <div className="mt-4">
            <WeekStrip
              days={week}
              target={`4주 출석률 ${stats?.att ?? 0}%`}
            />
          </div>
        </div>

        {/* MiniStats — 실데이터 */}
        <div className="grid grid-cols-3 gap-2">
          <StatChip icon="🏋️" label="총 운동" value={stats?.sessions ?? 0} unit="회" tone="volt" />
          <StatChip icon="⭐" label="레벨" value={`Lv${stats?.level ?? 1}`} tone="gold" />
          <StatChip icon="🏃" label="이번주 러닝" value={stats?.weekKm ?? 0} unit="km" tone="volt" />
        </div>
      </div>

      {/* 오른쪽 컬럼: 오늘의 운동 (데스크탑에서 넓게) */}
      <div className="lg:col-span-3">
        <TodayWorkoutCard items={items} onToggleSet={toggleSet} onOpenExercise={setOpenId} />
      </div>

      <ExerciseSheet
        exercise={openId ? byId(openId) ?? null : null}
        sets={openItem?.sets ?? []}
        onChange={(sets) =>
          updateItems(items.map((it) => (it.exerciseId === openId ? { ...it, sets } : it)))
        }
        onReplace={(newId) => {
          updateItems(items.map((it) => (it.exerciseId === openId ? { ...it, exerciseId: newId } : it)));
          setOpenId(newId);
        }}
        onDelete={() => updateItems(items.filter((it) => it.exerciseId !== openId))}
        onClose={() => setOpenId(null)}
      />

      <AchievementModal
        open={showBadge}
        title="오늘 완주!"
        desc={`${totalSets}세트 전부 클리어 — 스트릭 +1 🔥`}
        emoji="🏋️"
        onClose={() => setShowBadge(false)}
      />
    </main>
  );
}
