"use client";
// P0-4 오늘 탭 홈 — MascotBubble + Streak + WeekStrip + TodayWorkout + MiniStats
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { WeekStrip, type DayCell } from "@/components/today/WeekStrip";
import { TodayWorkoutCard } from "@/components/today/TodayWorkoutCard";
import { ExerciseSheet } from "@/components/workout/ExerciseSheet";
import { AchievementModal } from "@/components/celebrate/AchievementModal";
import { dailyQuote } from "@/lib/mock/quotes";
import { byId, getMockToday, type TodayItem } from "@/lib/mock/exercises";
import { getMockRecovery } from "@/lib/mock/recovery";
import { computeStats, useUser, weekCells } from "@/lib/useUser";
import { LoginCard } from "@/components/auth/LoginCard";
import { BottomSheet } from "@/components/ui/BottomSheet";
import { ColorInitialBadge } from "@/components/ui/ColorInitialBadge";
import { EXERCISES, itemsFromExercises } from "@/lib/mock/exercises";
import { EXPLORE } from "@/lib/mock/routines";

const S_DAYS = ["일", "월", "화", "수", "목", "금", "토"];

// 타임라인 노드 — 세로 연결선으로 카드들을 하나의 흐름으로
function Node({
  icon, label, last = false, children,
}: { icon: string; label: string; last?: boolean; children: ReactNode }) {
  return (
    <div className="relative pl-12 pb-5">
      {!last && (
        <span className="absolute bottom-0 left-[17px] top-11 w-px bg-gradient-to-b from-volt/40 via-white/10 to-white/10" />
      )}
      <span className="absolute left-0 top-0 grid h-9 w-9 place-items-center rounded-full border border-volt/40 bg-card text-[15px]">
        {icon}
      </span>
      <div className="lab mb-2 pt-2">{label}</div>
      <div className="rounded-3xl border border-white/[0.06] bg-card p-4">{children}</div>
    </div>
  );
}

export default function TodayPage() {
  const { user, ready, login, signup, saveToday, setActiveRoutine, today } = useUser();
  const [items, setItems] = useState<TodayItem[]>(getMockToday);
  const [openId, setOpenId] = useState<string | null>(null);
  const [celebrated, setCelebrated] = useState(false);
  const [showBadge, setShowBadge] = useState(false);
  const [showRoutinePick, setShowRoutinePick] = useState(false);
  const [showAddEx, setShowAddEx] = useState(false);
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
    <main className="mx-auto max-w-2xl lg:pt-24">
      {/* 인사 헤더 */}
      <div className="mb-5">
        <div className="lab">{S_DAYS[new Date().getDay()]}요일 · TODAY</div>
        <h1 className="font-display text-[30px] leading-tight">
          {String(user.id)}님, <span className="text-volt">오늘도 갑시다</span>
        </h1>
      </div>

      {/* ── 하나로 이어지는 하루 타임라인 ── */}
      <Node icon="☀️" label="오늘 브리핑 BRIEFING">
        <div className="flex items-start gap-3">
          <div className="min-w-0 flex-1">
            <p className="text-[13.5px] font-medium leading-relaxed">💬 {quote}</p>
            <div className="mt-2.5 flex flex-wrap gap-1.5">
              <span className="rounded-full bg-white/[0.06] px-2.5 py-1 text-[11.5px] font-bold">
                ⏱️ 예상 <b className="text-volt">{estMin}분</b>
              </span>
              <span className="rounded-full bg-white/[0.06] px-2.5 py-1 text-[11.5px] font-bold">
                ⚡ 컨디션 <b className={condition >= 80 ? "text-volt" : condition >= 50 ? "text-gold" : "text-danger"}>{condition}%</b>
              </span>
              <span className="rounded-full bg-white/[0.06] px-2.5 py-1 text-[11.5px] font-bold">
                🏋️ {items.length}종목 · {totalSets}세트
              </span>
            </div>
          </div>
        </div>
      </Node>

      <Node icon="🏋️" label="오늘의 운동 WORKOUT">
        <div className="mb-2 flex gap-1.5">
          <button
            onClick={() => setShowRoutinePick(true)}
            className="rounded-full border border-white/15 bg-white/5 px-3 py-1.5 text-[11.5px] font-bold text-white/70"
          >
            📋 루틴 변경
          </button>
          <button
            onClick={() => setShowAddEx(true)}
            className="rounded-full border border-white/15 bg-white/5 px-3 py-1.5 text-[11.5px] font-bold text-white/70"
          >
            ➕ 운동 추가
          </button>
        </div>
        <TodayWorkoutCard embedded items={items} onToggleSet={toggleSet} onOpenExercise={setOpenId} />
      </Node>

      <Node icon="🏁" label={doneSets >= totalSets && totalSets > 0 ? "오늘의 결과 RESULT" : "오늘 끝나면 REWARD"} last>
        <div className="flex items-end gap-3">
          <div>
            <div className="text-[11px] text-white/45">연속 운동</div>
            <div className="flex items-end gap-1.5">
              <span className="font-display text-[38px] leading-none text-white/35">{stats?.streak ?? 0}</span>
              <span className="pb-1 font-display text-[20px] text-white/35">→</span>
              <span className="font-display text-[38px] leading-none text-volt">{(stats?.streak ?? 0) + (doneSets >= totalSets && totalSets > 0 ? 0 : 1)}</span>
              <span className="pb-1 text-[13px] font-bold text-white/55">일 🔥</span>
            </div>
          </div>
          <div className="ml-auto text-right text-[11.5px] text-white/45">
            4주 출석률 <b className="text-zinc-100">{stats?.att ?? 0}%</b>
          </div>
        </div>
        <div className="mt-4">
          <WeekStrip days={week} target={`총 ${stats?.sessions ?? 0}회 · Lv${stats?.level ?? 1}`} />
        </div>
        {doneSets >= totalSets && totalSets > 0 && (
          <p className="mt-3 rounded-2xl bg-volt/10 px-3.5 py-2.5 text-center text-[13px] font-bold text-volt">
            오늘 몫 완료! 내일 스트릭이 이어집니다 🎉
          </p>
        )}
      </Node>

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

      {/* 루틴 변경 시트 — 저장한 루틴 우선, 나머지 추천 */}
      <BottomSheet open={showRoutinePick} onClose={() => setShowRoutinePick(false)}>
        <h3 className="text-lg font-extrabold">오늘 운동, 어떤 루틴으로?</h3>
        <p className="mt-0.5 text-[12px] text-white/50">체크한 세트는 초기화돼요.</p>
        <div className="mt-4 space-y-2">
          {[...EXPLORE].sort((a, b) =>
            Number((user.v2?.savedRoutines ?? []).includes(b.id)) - Number((user.v2?.savedRoutines ?? []).includes(a.id))
          ).map((r, i) => {
            const saved = (user.v2?.savedRoutines ?? []).includes(r.id);
            const active = user.v2?.activeRoutineId === r.id;
            return (
              <button
                key={r.id}
                onClick={() => {
                  updateItems(itemsFromExercises(r.exercises));
                  setActiveRoutine(r.id);
                  setShowRoutinePick(false);
                }}
                className={`flex w-full items-center gap-3 rounded-2xl border p-3 text-left ${
                  active ? "border-volt/50 bg-volt/[0.06]" : "border-white/10 bg-white/[0.03]"
                }`}
              >
                <ColorInitialBadge text={r.badge} seed={i} />
                <span className="min-w-0 flex-1">
                  <b className="block truncate text-[14px]">
                    {r.title}
                    {active && <span className="ml-1.5 rounded bg-volt px-1.5 py-0.5 text-[9px] font-extrabold text-black">사용 중</span>}
                    {saved && !active && <span className="ml-1.5 text-[10px] text-volt">💾 저장됨</span>}
                  </b>
                  <span className="text-[11px] text-white/45">{r.exercises.length}종목 · {r.level}</span>
                </span>
              </button>
            );
          })}
        </div>
      </BottomSheet>

      {/* 운동 추가 시트 */}
      <BottomSheet open={showAddEx} onClose={() => setShowAddEx(false)}>
        <h3 className="text-lg font-extrabold">오늘 운동 추가</h3>
        <p className="mt-0.5 text-[12px] text-white/50">오늘 목록에만 추가돼요.</p>
        <div className="mt-4 space-y-2">
          {EXERCISES.filter((ex) => !items.some((it) => it.exerciseId === ex.id)).map((ex) => (
            <button
              key={ex.id}
              onClick={() => {
                updateItems([...items, ...itemsFromExercises([ex.id])]);
                setShowAddEx(false);
              }}
              className="flex w-full items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-3 text-left"
            >
              <span className="text-[20px]">{ex.em}</span>
              <span className="min-w-0 flex-1">
                <b className="block text-[14px]">{ex.name}</b>
                <span className="text-[11px] text-white/45">{ex.zone}구역 · {ex.equipment}</span>
              </span>
              <span className="text-[12px] font-bold text-volt">추가 +</span>
            </button>
          ))}
          {EXERCISES.every((ex) => items.some((it) => it.exerciseId === ex.id)) && (
            <p className="py-4 text-center text-[13px] text-white/40">모든 운동이 이미 오늘 목록에 있어요 💪</p>
          )}
        </div>
      </BottomSheet>
    </main>
  );
}
