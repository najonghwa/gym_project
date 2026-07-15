"use client";
// P0-4 오늘 탭 홈 — MascotBubble + Streak + WeekStrip + TodayWorkout + MiniStats
import { useMemo, useState } from "react";
import { MascotBubble } from "@/components/mascot/MascotBubble";
import { StreakNumber } from "@/components/ui/StreakNumber";
import { StatChip } from "@/components/ui/StatChip";
import { WeekStrip, type DayCell } from "@/components/today/WeekStrip";
import { TodayWorkoutCard } from "@/components/today/TodayWorkoutCard";
import { ExerciseSheet } from "@/components/workout/ExerciseSheet";
import { dailyQuote } from "@/lib/mock/quotes";
import { byId, getMockToday, type TodayItem } from "@/lib/mock/exercises";

// TODO(supabase): 실제 사용자 스트릭/주간 기록으로 대체
const MOCK_STREAK = 5;
const MOCK_WEEK: DayCell[] = [
  { label: "월", pct: 100 },
  { label: "화", pct: 0 },
  { label: "수", pct: 80 },
  { label: "목", pct: 100 },
  { label: "금", pct: null, isToday: true },
  { label: "토", pct: null },
  { label: "일", pct: null },
];

export default function TodayPage() {
  const [items, setItems] = useState<TodayItem[]>(getMockToday);
  const [openId, setOpenId] = useState<string | null>(null);
  const quote = useMemo(() => dailyQuote(), []);

  const toggleSet = (exerciseId: string, setIndex: number) =>
    setItems((prev) =>
      prev.map((it) =>
        it.exerciseId === exerciseId
          ? { ...it, sets: it.sets.map((s, i) => (i === setIndex ? { ...s, done: !s.done } : s)) }
          : it
      )
    );

  const openItem = items.find((it) => it.exerciseId === openId) ?? null;

  return (
    <main className="space-y-4 lg:pt-16">
      <MascotBubble quote={quote} />

      <div className="rounded-3xl border border-white/[0.06] bg-card p-4">
        <div className="lab mb-1">연속 운동 STREAK</div>
        <StreakNumber value={MOCK_STREAK} />
        <div className="mt-4">
          <WeekStrip days={MOCK_WEEK} target="주 4회 · 3/4 완료" />
        </div>
      </div>

      <TodayWorkoutCard items={items} onToggleSet={toggleSet} onOpenExercise={setOpenId} />

      {/* MiniStats (스펙 P0-4) */}
      <div className="grid grid-cols-3 gap-2">
        <StatChip icon="🎯" label="목표" value="벌크업" tone="volt" />
        <StatChip icon="⚖️" label="몸무게" value={72} unit="kg" delta={-1} tone="gold" />
        <StatChip icon="📆" label="주간 빈도" value="3/4" unit="회" delta={1} tone="volt" />
      </div>

      <ExerciseSheet
        exercise={openId ? byId(openId) ?? null : null}
        sets={openItem?.sets ?? []}
        onChange={(sets) =>
          setItems((prev) => prev.map((it) => (it.exerciseId === openId ? { ...it, sets } : it)))
        }
        onReplace={(newId) => {
          setItems((prev) =>
            prev.map((it) => (it.exerciseId === openId ? { ...it, exerciseId: newId } : it))
          );
          setOpenId(newId);
        }}
        onDelete={() => setItems((prev) => prev.filter((it) => it.exerciseId !== openId))}
        onClose={() => setOpenId(null)}
      />
    </main>
  );
}
