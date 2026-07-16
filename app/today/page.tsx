"use client";
// 헬스 홈 — 하루 타임라인(브리핑/운동/리워드) + 기록 대시보드(KPI·월별·주간 볼륨)
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
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
import { BottomSheet } from "@/components/ui/BottomSheet";
import { SettingsSheet } from "@/components/settings/SettingsSheet";
import { ColorInitialBadge } from "@/components/ui/ColorInitialBadge";
import { EXERCISES, itemsFromExercises } from "@/lib/mock/exercises";
import { EXPLORE } from "@/lib/mock/routines";
import { MUSCLE_KR, type Muscle } from "@/lib/recovery";

const S_DAYS = ["일", "월", "화", "수", "목", "금", "토"];

// 타임라인 노드 — 세로 연결선으로 카드들을 하나의 흐름으로 (스텝 번호 칩)
function Node({
  icon, label, last = false, children,
}: { icon: string; label: string; last?: boolean; children: ReactNode }) {
  return (
    <div className="relative pl-11 pb-5">
      {!last && (
        <span className="absolute bottom-0 left-[15px] top-10 w-px bg-white/[0.08]" />
      )}
      <span className="grid absolute left-0 top-0 h-8 w-8 place-items-center rounded-lg border border-white/10 bg-card text-[11px] font-bold tabular-nums text-volt">
        {icon}
      </span>
      <div className="lab mb-2 pt-2">{label}</div>
      <div className="rounded-xl border border-white/[0.06] bg-card p-4">{children}</div>
    </div>
  );
}

export default function TodayPage() {
  const { user, ready, login, signup, logout, saveToday, setActiveRoutine, setPrimaryMode, today } = useUser();
  const [items, setItems] = useState<TodayItem[]>(getMockToday);
  const [openId, setOpenId] = useState<string | null>(null);
  const [celebrated, setCelebrated] = useState(false);
  const [showBadge, setShowBadge] = useState(false);
  const [showRoutinePick, setShowRoutinePick] = useState(false);
  const [showAddEx, setShowAddEx] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
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

  // 진행 중 루틴 전체 진행률 — 적용일 이후 운동한 날 / (주차×주당횟수)
  const routineProg = useMemo(() => {
    const r = EXPLORE.find((x) => x.id === user?.v2?.activeRoutineId);
    if (!r || !user) return null;
    const start = user.v2?.routineStart;
    const total = r.weeks * r.daysPerWeek;
    const done = Object.entries(user.v2?.workouts ?? {}).filter(([d, w]) =>
      (!start || d >= start) && (w.items as TodayItem[]).some((it) => it.sets.some((s) => s.done))
    ).length;
    const week = start
      ? Math.max(1, Math.min(r.weeks, Math.floor((Date.now() - new Date(start + "T00:00:00").getTime()) / (7 * 864e5)) + 1))
      : Math.min(r.weeks, Math.floor(done / r.daysPerWeek) + 1);
    return { title: r.title, week, weeks: r.weeks, done: Math.min(done, total), total, pct: Math.min(100, Math.round((done / total) * 100)) };
  }, [user]);

  // 기록 대시보드 — 날짜별 완료 세트(구버전+v2 합산) → 월별 횟수·주간 볼륨
  const gymDash = useMemo(() => {
    if (!user) return null;
    const map = new Map<string, number>();
    Object.entries(user.workouts ?? {}).forEach(([d, w]) => {
      if ((w.doneSets ?? 0) > 0) map.set(d, (map.get(d) ?? 0) + (w.doneSets ?? 0));
    });
    Object.entries(user.v2?.workouts ?? {}).forEach(([d, w]) => {
      const done = (w.items as TodayItem[]).reduce((s, it) => s + it.sets.filter((x) => x.done).length, 0);
      if (done) map.set(d, (map.get(d) ?? 0) + done);
    });
    const now = new Date();
    const y = now.getFullYear();
    const monthly = Array.from({ length: 12 }, (_, i) => ({
      m: `${i + 1}월`,
      n: [...map.keys()].filter((d) => d.startsWith(`${y}-${String(i + 1).padStart(2, "0")}`)).length,
      isNow: i === now.getMonth(),
    }));
    // 주간 세트 볼륨 (최근 8주, 월요일 시작)
    const mon0 = new Date(now); mon0.setDate(now.getDate() - ((now.getDay() + 6) % 7)); mon0.setHours(0, 0, 0, 0);
    const weekly = Array.from({ length: 8 }, (_, i) => {
      const start = new Date(mon0); start.setDate(mon0.getDate() - (7 - i) * 7);
      return { w: `${start.getMonth() + 1}/${start.getDate()}`, sets: 0, isNow: i === 7 };
    });
    map.forEach((sets, d) => {
      const dt = new Date(d + "T00:00:00");
      const wk = new Date(dt); wk.setDate(dt.getDate() - ((dt.getDay() + 6) % 7)); wk.setHours(0, 0, 0, 0);
      const diffW = Math.round((mon0.getTime() - wk.getTime()) / (7 * 864e5));
      if (diffW >= 0 && diffW < 8) weekly[7 - diffW].sets += sets;
    });
    const totalSets = [...map.values()].reduce((s, n) => s + n, 0);
    const thisMonth = monthly[now.getMonth()].n;
    // 최근 운동 5건 (v2는 운동명 포함)
    const recent = [...map.entries()].sort((a, b) => (a[0] < b[0] ? 1 : -1)).slice(0, 5).map(([d, sets]) => {
      const v2day = user.v2?.workouts?.[d];
      const names = v2day
        ? (v2day.items as TodayItem[]).filter((it) => it.sets.some((s) => s.done)).map((it) => byId(it.exerciseId)?.name ?? "").filter(Boolean)
        : [];
      return { date: d, sets, names };
    });
    // 이번 주(최근 7일) 부위별 세트
    const cutoff = new Date(now); cutoff.setDate(now.getDate() - 6); cutoff.setHours(0, 0, 0, 0);
    const byMuscle = new Map<Muscle, number>();
    Object.entries(user.v2?.workouts ?? {}).forEach(([d, w]) => {
      if (new Date(d + "T00:00:00") < cutoff) return;
      (w.items as TodayItem[]).forEach((it) => {
        const done = it.sets.filter((s) => s.done).length;
        if (!done) return;
        const m = byId(it.exerciseId)?.contrib[0].muscle;
        if (m) byMuscle.set(m, (byMuscle.get(m) ?? 0) + done);
      });
    });
    const weekMuscles = [...byMuscle.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5);
    const maxMuscle = Math.max(1, ...weekMuscles.map(([, n]) => n));
    return { monthly, weekly, totalSets, thisMonth, recent, weekMuscles, maxMuscle };
  }, [user]);

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
      <main className="lg:pt-10">
        <LoginCard onLogin={login} onSignup={signup} />
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl lg:max-w-6xl lg:pt-10">
      {/* 페이지 헤더 */}
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="font-display text-[26px] leading-tight tracking-tight">Workout</h1>
          <p className="mt-0.5 text-[12.5px] text-white/45">
            {new Date().getMonth() + 1}월 {new Date().getDate()}일 {S_DAYS[new Date().getDay()]}요일 · {String(user.id)}
          </p>
        </div>
        <button
          onClick={() => setShowSettings(true)}
          className="mt-1 grid h-10 w-10 place-items-center rounded-lg border border-white/10 bg-card text-[16px]"
          aria-label="설정"
        >
          ⚙️
        </button>
      </div>

      {/* ── 기록 대시보드 (러닝 탭과 같은 카드 패턴) — 상단 배치 ── */}
      {gymDash && (
        <section className="mb-6 space-y-3">
          <div className="grid grid-cols-3 gap-2 lg:grid-cols-6">
            <StatChip label="총 운동" value={stats?.sessions ?? 0} unit="회" tone="volt" />
            <StatChip label="이번 달" value={gymDash.thisMonth} unit="회" tone="mute" />
            <StatChip label="연속" value={stats?.streak ?? 0} unit="일" tone={stats && stats.streak > 0 ? "volt" : "mute"} />
            <StatChip label="4주 출석률" value={stats?.att ?? 0} unit="%" tone={stats && stats.att >= 70 ? "volt" : "gold"} />
            <StatChip label="총 세트" value={gymDash.totalSets} unit="세트" tone="mute" />
            <StatChip label="레벨" value={`Lv${stats?.level ?? 1}`} tone="gold" />
          </div>

          <div className="grid gap-3 lg:grid-cols-2">
            {/* 월별 운동 횟수 */}
            <div className="rounded-xl border border-white/[0.06] bg-card p-4">
              <b className="text-[15px] font-extrabold">월별 운동 횟수</b>
              <p className="text-[11.5px] text-white/45">{new Date().getFullYear()}년 · 운동한 날 기준</p>
              <div className="mt-2 h-36">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={gymDash.monthly} margin={{ top: 6, right: 0, left: -26 }}>
                    <XAxis dataKey="m" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 8.5 }} axisLine={false} tickLine={false} interval={0} />
                    <YAxis tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} allowDecimals={false} />
                    <Tooltip
                      cursor={{ fill: "rgba(255,255,255,0.04)" }}
                      contentStyle={{ background: "#0d1526", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }}
                      formatter={(v) => [`${Number(v ?? 0)}회`, "운동"]}
                    />
                    <Bar dataKey="n" radius={[3, 3, 0, 0]} isAnimationActive={false}>
                      {gymDash.monthly.map((x, i) => (
                        <Cell key={i} fill={x.isNow ? "#ff9432" : "rgba(255,255,255,0.18)"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 주간 세트 볼륨 */}
            <div className="rounded-xl border border-white/[0.06] bg-card p-4">
              <b className="text-[15px] font-extrabold">주간 세트 볼륨</b>
              <p className="text-[11.5px] text-white/45">최근 8주 · 완료한 세트 합계</p>
              <div className="mt-2 h-36">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={gymDash.weekly} margin={{ top: 6, right: 0, left: -26 }}>
                    <XAxis dataKey="w" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} interval={0} />
                    <YAxis tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} allowDecimals={false} />
                    <Tooltip
                      cursor={{ fill: "rgba(255,255,255,0.04)" }}
                      contentStyle={{ background: "#0d1526", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }}
                      formatter={(v) => [`${Number(v ?? 0)}세트`, "볼륨"]}
                    />
                    <Bar dataKey="sets" radius={[3, 3, 0, 0]} isAnimationActive={false}>
                      {gymDash.weekly.map((x, i) => (
                        <Cell key={i} fill={x.isNow ? "#ff9432" : "rgba(255,255,255,0.18)"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </section>
      )}

      <div className="lg:grid lg:grid-cols-3 lg:gap-6">
      <div className="lg:col-span-2">
      {/* ── 하나로 이어지는 하루 타임라인 ── */}
      <div className="lab mb-2">오늘 TODAY</div>
      <Node icon="01" label="오늘 브리핑 BRIEFING">
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

            {/* 진행 중 루틴 전체 진행률 */}
            {routineProg ? (
              <div className="mt-3 rounded-lg border border-white/[0.08] bg-white/[0.03] p-3">
                <div className="flex items-baseline justify-between">
                  <b className="text-[12.5px]">📋 {routineProg.title}</b>
                  <span className="text-[11px] text-white/45">
                    {routineProg.week}주차 <span className="text-white/25">/ {routineProg.weeks}주</span>
                  </span>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/[0.07]">
                  <div className="h-full rounded-full bg-volt" style={{ width: `${routineProg.pct}%` }} />
                </div>
                <div className="mt-1.5 flex justify-between text-[10.5px] text-white/45">
                  <span>세션 <b className="text-white/70">{routineProg.done}</b>/{routineProg.total}회 완료</span>
                  <b className="text-volt">{routineProg.pct}%</b>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setShowRoutinePick(true)}
                className="mt-3 flex w-full items-center justify-between rounded-lg border border-white/[0.08] bg-white/[0.03] p-3 text-[12px] font-bold text-white/55"
              >
                진행할 루틴을 골라보세요 <span className="text-volt">→</span>
              </button>
            )}
          </div>
        </div>
      </Node>

      <Node icon="02" label="오늘의 운동 WORKOUT">
        <div className="mb-2 flex gap-1.5">
          <button
            onClick={() => setShowRoutinePick(true)}
            className="rounded-lg border border-white/15 bg-white/5 px-3 py-1.5 text-[11.5px] font-bold text-white/70"
          >
            📋 루틴 변경
          </button>
          <button
            onClick={() => setShowAddEx(true)}
            className="rounded-lg border border-white/15 bg-white/5 px-3 py-1.5 text-[11.5px] font-bold text-white/70"
          >
            ➕ 운동 추가
          </button>
        </div>
        <TodayWorkoutCard embedded items={items} onToggleSet={toggleSet} onOpenExercise={setOpenId} />
      </Node>

      <Node icon="03" label={doneSets >= totalSets && totalSets > 0 ? "결과 RESULT" : "리워드 REWARD"} last>
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
          <p className="mt-3 rounded-lg bg-volt/10 px-3.5 py-2.5 text-center text-[13px] font-bold text-volt">
            오늘 운동 완료! 연속 기록이 이어집니다 🎉
          </p>
        )}
      </Node>
      </div>

      {/* ── 우측 요약 컬럼 ── */}
      <aside className="space-y-3 lg:pt-7">
        <div className="rounded-xl border border-white/[0.06] bg-card p-4">
          <b className="text-[15px] font-extrabold">최근 운동</b>
          {gymDash?.recent.length ? (
            <div className="mt-1.5 divide-y divide-white/[0.06]">
              {gymDash.recent.map((r) => (
                <div key={r.date} className="flex items-center gap-2.5 py-2.5">
                  <span className="w-12 shrink-0 text-[12px] tabular-nums text-white/50">{r.date.slice(5).replace("-", ".")}</span>
                  <span className="min-w-0 flex-1 truncate text-[12.5px] font-medium text-white/80">
                    {r.names.length ? r.names.slice(0, 3).join(" · ") : "운동 기록"}
                  </span>
                  <b className="shrink-0 text-[12px] text-volt">{r.sets}세트</b>
                </div>
              ))}
            </div>
          ) : (
            <p className="py-5 text-center text-[12.5px] text-white/40">아직 운동 기록이 없어요</p>
          )}
        </div>

        <div className="rounded-xl border border-white/[0.06] bg-card p-4">
          <b className="text-[15px] font-extrabold">이번 주 부위별 세트</b>
          {gymDash?.weekMuscles.length ? (
            <div className="mt-2.5 space-y-2">
              {gymDash.weekMuscles.map(([m, n]) => (
                <div key={m} className="flex items-center gap-2.5">
                  <span className="w-14 shrink-0 text-[12px] font-bold text-white/60">{MUSCLE_KR[m]}</span>
                  <div className="h-3 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
                    <div className="h-full rounded-full bg-volt" style={{ width: `${(n / gymDash.maxMuscle) * 100}%` }} />
                  </div>
                  <b className="w-11 shrink-0 text-right text-[12px] tabular-nums">{n}세트</b>
                </div>
              ))}
            </div>
          ) : (
            <p className="py-5 text-center text-[12.5px] text-white/40">이번 주 완료한 세트가 없어요</p>
          )}
        </div>

        {/* 이번 주 요일 스트립 — 리워드 카드와 별개로 사이드에서 상시 확인 */}
        <div className="rounded-xl border border-white/[0.06] bg-card p-4">
          <b className="text-[15px] font-extrabold">이번 주</b>
          <div className="mt-3">
            <WeekStrip days={week} target={`총 ${stats?.sessions ?? 0}회 · Lv${stats?.level ?? 1}`} />
          </div>
        </div>
      </aside>
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
        title="오늘 운동 완료!"
        desc={`${totalSets}세트 모두 완료 — 연속 기록 +1 🔥`}
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
                className={`flex w-full items-center gap-3 rounded-lg border p-3 text-left ${
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
              className="flex w-full items-center gap-3 rounded-lg border border-white/10 bg-white/[0.03] p-3 text-left"
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

      <SettingsSheet
        open={showSettings}
        onClose={() => setShowSettings(false)}
        primaryMode={user.v2?.primaryMode ?? "gym"}
        onChangeMode={setPrimaryMode}
        onLogout={logout}
      />
    </main>
  );
}
