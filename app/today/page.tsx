"use client";
// 헬스 홈 — 하루 타임라인(브리핑/운동/리워드) + 기록 대시보드(KPI·월별·주간 볼륨)
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { fetchStats } from "@/lib/supa";
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
import { ExThumb } from "@/components/ui/ExThumb";
import { ShibaLifter } from "@/components/mascot/ShibaLifter";
import { LottieMascot } from "@/components/mascot/LottieMascot";
import { EXERCISES, itemsFromExercises } from "@/lib/mock/exercises";
import { EXPLORE } from "@/lib/mock/routines";
import { MUSCLE_KR, type Muscle } from "@/lib/recovery";

const S_DAYS = ["일", "월", "화", "수", "목", "금", "토"];

// 섹션 카드 — 볼트 틱 + 라벨 헤더 (구 번호칩 타임라인 대체)
function Node({
  label, children,
}: { icon?: string; label: string; last?: boolean; children: ReactNode }) {
  return (
    <div className="pb-4">
      <div className="mb-2 flex items-center gap-2">
        <span className="h-3.5 w-[3px] rounded-full bg-volt" />
        <span className="lab">{label}</span>
      </div>
      <div className="rounded-2xl border border-white/[0.06] bg-card p-4">{children}</div>
    </div>
  );
}

export default function TodayPage() {
  const router = useRouter();
  const { user, ready, login, signup, logout, saveToday, setActiveRoutine, setPrimaryMode, today } = useUser();
  const [rankRows, setRankRows] = useState<{ id: string; att: number }[]>([]);
  useEffect(() => {
    fetchStats().then((rows) => {
      if (!rows) return;
      setRankRows(
        rows
          .map((r) => ({ id: String(r.id), att: Number((r.stats as { att?: number } | null)?.att ?? 0) }))
          .filter((r) => r.att > 0)
          .sort((a, b) => b.att - a.att)
          .slice(0, 5)
      );
    });
  }, []);
  const [items, setItems] = useState<TodayItem[]>(getMockToday);
  const [openId, setOpenId] = useState<string | null>(null);
  const [celebrated, setCelebrated] = useState(false);
  const [showBadge, setShowBadge] = useState(false);
  const [showRoutinePick, setShowRoutinePick] = useState(false);
  const [pickDetail, setPickDetail] = useState<string | null>(null); // 루틴 시트에서 펼쳐본 루틴
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

  // 보너스 세션 — 이번 주(월~일) 운동한 날이 루틴 주당 목표를 이미 채웠는데 오늘 또 온 경우
  const bonusSession = useMemo(() => {
    const r = EXPLORE.find((x) => x.id === user?.v2?.activeRoutineId);
    if (!r || !user) return false;
    const now = new Date();
    const mon = new Date(now); mon.setDate(now.getDate() - ((now.getDay() + 6) % 7)); mon.setHours(0, 0, 0, 0);
    const todayS = today();
    // 이번 주 운동한 '오늘 이전' 날 수 (오늘은 제외 — 오늘이 초과분인지 판단)
    const daysBeforeToday = new Set<string>();
    const collect = (obj: Record<string, unknown> | undefined, hasDone: (w: unknown) => boolean) => {
      Object.entries(obj ?? {}).forEach(([d, w]) => {
        if (d >= todayS) return;
        if (new Date(d + "T00:00:00") >= mon && hasDone(w)) daysBeforeToday.add(d);
      });
    };
    collect(user.v2?.workouts, (w) => (w as { items: TodayItem[] }).items.some((it) => it.sets.some((s) => s.done)));
    collect(user.workouts, (w) => ((w as { doneSets?: number }).doneSets ?? 0) > 0);
    return daysBeforeToday.size >= r.daysPerWeek;
  }, [user, today]);

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
    // 이번 달 운동한 날짜(미니 달력용)
    const ym = `${y}-${String(now.getMonth() + 1).padStart(2, "0")}`;
    const daysThisMonth = new Set(
      [...map.keys()].filter((d) => d.startsWith(ym)).map((d) => parseInt(d.slice(8), 10))
    );
    return { monthly, weekly, totalSets, thisMonth, recent, weekMuscles, maxMuscle, daysThisMonth };
  }, [user]);

  // P2-10 컨디션% = 회복맵 평균 연동, 예상 시간 = 세트 수 × 2.5분
  const recovery = useMemo(() => getMockRecovery(), []);
  const condition = useMemo(
    () => Math.round((recovery.reduce((s, r) => s + r.pct, 0) / recovery.length) * 100),
    [recovery]
  );
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
    <main className="mx-auto max-w-2xl lg:max-w-none lg:pt-10">
      {/* 페이지 헤더 — 부제목 = 오늘의 한마디 */}
      <div className="mb-5 flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-2">
          <LottieMascot name="gym" size={54} fallback={<ShibaLifter size={54} />} />
          <div className="min-w-0">
            <div className="lab">{new Date().getMonth() + 1}월 {new Date().getDate()}일 {S_DAYS[new Date().getDay()]}요일 · {String(user.id)}</div>
            <h1 className="mt-0.5 font-display text-[26px] leading-tight tracking-tight">Workout</h1>
            <p className="mt-1 text-[13px] leading-relaxed text-white/55">💬 {quote}</p>
          </div>
        </div>
        <button
          onClick={() => setShowSettings(true)}
          className="mt-1 grid h-10 w-10 shrink-0 place-items-center rounded-full border border-white/10 bg-card text-[16px]"
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

          {/* 피처 카드 4종 — 구 GYM&RUN 대시보드 배치 */}
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {/* 연속 STREAK */}
            <div className="rounded-2xl border border-white/[0.06] bg-card p-4">
              <div className="lab">연속 STREAK</div>
              <div className="mt-1 flex items-end gap-1">
                <span className={`font-display text-[44px] leading-none ${stats && stats.streak > 0 ? "text-volt" : "text-white/30"}`}>
                  {stats?.streak ?? 0}
                </span>
                <span className="pb-1 text-[14px] font-bold text-white/55">일 🔥</span>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-1.5">
                {([[stats?.sessions ?? 0, "총 운동"], [gymDash.totalSets, "총 세트"], [`${stats?.att ?? 0}%`, "4주 출석"], [`Lv${stats?.level ?? 1}`, "레벨"]] as const).map(([v, l]) => (
                  <div key={l} className="rounded-2xl bg-white/[0.05] py-2 text-center">
                    <div className="font-display text-[15px] leading-none tabular-nums">{v}</div>
                    <div className="mt-1 text-[9.5px] text-white/45">{l}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* 루틴 진행 */}
            <div className="flex flex-col rounded-2xl border border-white/[0.06] bg-card p-4">
              <div className="lab">루틴 진행</div>
              {routineProg ? (
                <>
                  <b className="mt-1.5 truncate text-[13.5px]">📋 {routineProg.title}</b>
                  <div className="mt-1 flex items-end gap-1.5">
                    <span className="font-display text-[38px] leading-none text-volt">{routineProg.week}</span>
                    <span className="pb-1 text-[12.5px] text-white/45">/ {routineProg.weeks}주차</span>
                  </div>
                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/[0.07]">
                    <div className="h-full rounded-full bg-volt" style={{ width: `${routineProg.pct}%` }} />
                  </div>
                  <div className="mt-1.5 flex justify-between text-[10.5px] text-white/45">
                    <span>세션 {routineProg.done}/{routineProg.total}회</span><b className="text-volt">{routineProg.pct}%</b>
                  </div>
                  <button
                    onClick={() => setShowRoutinePick(true)}
                    className="mt-auto w-full rounded-full border border-white/15 bg-white/[0.05] py-2.5 text-[12.5px] font-bold text-white/80"
                  >
                    루틴 변경 →
                  </button>
                </>
              ) : (
                <>
                  <p className="mt-2 text-[12.5px] leading-relaxed text-white/60">
                    진행 중인 루틴이 없어요.<br />검증된 프로그램으로 시작해 보세요.
                  </p>
                  <button
                    onClick={() => setShowRoutinePick(true)}
                    className="mt-auto w-full rounded-full bg-volt py-3 text-[13.5px] font-extrabold text-black"
                  >
                    루틴 고르기 📋
                  </button>
                </>
              )}
            </div>

            {/* 3대 챌린지 */}
            <div className="flex flex-col rounded-2xl border border-white/[0.06] bg-card p-4">
              <div className="lab">3대 챌린지</div>
              {(() => {
                const logs = (user.big3 as { goal?: number; logs?: { s: number; b: number; d: number }[] } | undefined)?.logs;
                const last = logs?.[logs.length - 1];
                const goal = (user.big3 as { goal?: number } | undefined)?.goal ?? 300;
                if (last) {
                  const sum = Math.round((last.s + last.b + last.d) * 10) / 10;
                  const pct = Math.min(100, Math.round((sum / goal) * 100));
                  return (
                    <>
                      <div className="mt-1 flex items-end gap-1.5">
                        <span className="font-display text-[38px] leading-none text-gold">{sum}</span>
                        <span className="pb-1 text-[12.5px] text-white/45">/ {goal}kg</span>
                      </div>
                      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/[0.07]">
                        <div className="h-full rounded-full bg-gold" style={{ width: `${pct}%` }} />
                      </div>
                      <div className="mt-1.5 text-right text-[10.5px] font-bold text-gold">{pct}%</div>
                      <button
                        onClick={() => router.push("/analysis")}
                        className="mt-auto w-full rounded-full border border-white/15 bg-white/[0.05] py-2.5 text-[12.5px] font-bold text-white/80"
                      >
                        측정 기록 →
                      </button>
                    </>
                  );
                }
                return (
                  <>
                    <p className="mt-2 text-[12.5px] leading-relaxed text-white/60">
                      스쿼트+벤치+데드 합계 도전.<br />3대 300부터 시작해 볼까요?
                    </p>
                    <button
                      onClick={() => router.push("/analysis")}
                      className="mt-auto w-full rounded-full bg-volt py-3 text-[13.5px] font-extrabold text-black"
                    >
                      도전 시작 🏆
                    </button>
                  </>
                );
              })()}
            </div>

            {/* 오늘 준비 — 모니터링 */}
            <div className="flex flex-col rounded-2xl border border-white/[0.06] bg-card p-4">
              <div className="lab">오늘 준비</div>
              <div className="mt-1 flex items-end gap-1.5">
                <span className="font-display text-[38px] leading-none">{items.length}</span>
                <span className="pb-1 text-[12.5px] text-white/45">종목 · {totalSets}세트</span>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-1.5">
                <div className="rounded-2xl bg-white/[0.05] py-2 text-center">
                  <div className="font-display text-[15px] leading-none text-volt">{estMin}<span className="text-[10px] text-white/45">분</span></div>
                  <div className="mt-1 text-[9.5px] text-white/45">예상 시간</div>
                </div>
                <div className="rounded-2xl bg-white/[0.05] py-2 text-center">
                  <div className={`font-display text-[15px] leading-none ${condition >= 80 ? "text-volt" : condition >= 50 ? "text-gold" : "text-danger"}`}>{condition}<span className="text-[10px] text-white/45">%</span></div>
                  <div className="mt-1 text-[9.5px] text-white/45">컨디션</div>
                </div>
              </div>
              <div className="mt-auto pt-3 text-right text-[11px] text-white/45">누적 <b className="text-white/70">XP {stats?.xp ?? 0}</b></div>
            </div>
          </div>

          <div className="grid gap-3 lg:grid-cols-3">
            {/* 이번 달 목표 달성 도넛 */}
            <div className="rounded-2xl border border-white/[0.06] bg-card p-4">
              <b className="text-[15px] font-extrabold">이번 달 목표</b>
              <p className="text-[11.5px] text-white/45">
                {routineProg ? `주 ${EXPLORE.find((x) => x.id === user.v2?.activeRoutineId)?.daysPerWeek ?? 3}회 페이스 기준` : "주 3회 페이스 기준"}
              </p>
              {(() => {
                const perWeek = EXPLORE.find((x) => x.id === user.v2?.activeRoutineId)?.daysPerWeek ?? 3;
                const target = perWeek * 4;
                const pct = Math.min(100, Math.round((gymDash.thisMonth / target) * 100));
                const R = 40, C = 2 * Math.PI * R;
                const color = pct >= 100 ? "#2dd4a0" : "#c8ff00";
                return (
                  <div className="mt-2 flex h-36 items-center justify-center gap-5">
                    <svg width="112" height="112" viewBox="0 0 112 112">
                      <circle cx="56" cy="56" r={R} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="11" />
                      <circle
                        cx="56" cy="56" r={R} fill="none" stroke={color} strokeWidth="11" strokeLinecap="round"
                        strokeDasharray={`${(pct / 100) * C} ${C}`} transform="rotate(-90 56 56)"
                      />
                      <text x="56" y="53" textAnchor="middle" fill="#fafafa" fontSize="21" fontWeight="800">{pct}%</text>
                      <text x="56" y="70" textAnchor="middle" fill="rgba(255,255,255,0.4)" fontSize="9.5">달성</text>
                    </svg>
                    <div className="space-y-1.5 text-[12px]">
                      <div><b className="font-display text-[18px]" style={{ color }}>{gymDash.thisMonth}</b><span className="text-white/40"> / {target}회</span></div>
                      <div className="text-white/45">남은 <b className="text-white/75">{Math.max(0, target - gymDash.thisMonth)}회</b></div>
                      <div className="text-white/45">이번 주 <b className="text-white/75">{week.filter((c) => (c.pct ?? 0) > 0).length}회</b></div>
                    </div>
                  </div>
                );
              })()}
            </div>

            {/* 월별 운동 횟수 */}
            <div className="rounded-2xl border border-white/[0.06] bg-card p-4">
              <b className="text-[15px] font-extrabold">월별 운동 횟수</b>
              <p className="text-[11.5px] text-white/45">{new Date().getFullYear()}년 · 운동한 날 기준</p>
              <div className="mt-2 h-36">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={gymDash.monthly} margin={{ top: 6, right: 0, left: -26 }}>
                    <XAxis dataKey="m" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 8.5 }} axisLine={false} tickLine={false} interval={0} />
                    <YAxis tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} allowDecimals={false} />
                    <Tooltip
                      cursor={{ fill: "rgba(255,255,255,0.04)" }}
                      contentStyle={{ background: "#121212", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }}
                      formatter={(v) => [`${Number(v ?? 0)}회`, "운동"]}
                    />
                    <Bar dataKey="n" radius={[3, 3, 0, 0]} isAnimationActive={false}>
                      {gymDash.monthly.map((x, i) => (
                        <Cell key={i} fill={x.isNow ? "#c8ff00" : "rgba(255,255,255,0.18)"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 주간 세트 볼륨 */}
            <div className="rounded-2xl border border-white/[0.06] bg-card p-4">
              <b className="text-[15px] font-extrabold">주간 세트 볼륨</b>
              <p className="text-[11.5px] text-white/45">최근 8주 · 완료한 세트 합계</p>
              <div className="mt-2 h-36">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={gymDash.weekly} margin={{ top: 6, right: 0, left: -26 }}>
                    <XAxis dataKey="w" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} interval={0} />
                    <YAxis tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 9 }} axisLine={false} tickLine={false} allowDecimals={false} />
                    <Tooltip
                      cursor={{ fill: "rgba(255,255,255,0.04)" }}
                      contentStyle={{ background: "#121212", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }}
                      formatter={(v) => [`${Number(v ?? 0)}세트`, "볼륨"]}
                    />
                    <Bar dataKey="sets" radius={[3, 3, 0, 0]} isAnimationActive={false}>
                      {gymDash.weekly.map((x, i) => (
                        <Cell key={i} fill={x.isNow ? "#c8ff00" : "rgba(255,255,255,0.18)"} />
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
      <Node label="오늘의 운동 WORKOUT">
        {bonusSession && (
          <div className="mb-3">
            <span className="rounded-full bg-volt/15 px-2.5 py-1 text-[11.5px] font-bold text-volt">
              🔥 이번 주 목표 달성 — 오늘은 보너스 세션
            </span>
          </div>
        )}
        <div className="mb-2 flex flex-wrap gap-1.5">
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
          <button
            onClick={() => {
              if (items.length === 0 || window.confirm("오늘 목록을 비우고 직접 구성할까요? 체크한 세트는 초기화돼요.")) {
                updateItems([]);
                setShowAddEx(true);
              }
            }}
            className="rounded-lg border border-white/15 bg-white/5 px-3 py-1.5 text-[11.5px] font-bold text-white/70"
          >
            🧹 자유 운동
          </button>
        </div>
        {items.length === 0 ? (
          <div className="rounded-lg border border-dashed border-white/15 bg-white/[0.02] px-5 py-7 text-center">
            <p className="text-[13px] text-white/55">
              오늘은 자유 운동 — 목록이 비어 있어요.<br />한 운동이라도 기록하면 출석·통계에 똑같이 반영됩니다.
            </p>
            <button
              onClick={() => setShowAddEx(true)}
              className="mt-3 rounded-full bg-volt px-5 py-2.5 text-[13px] font-extrabold text-black"
            >
              ➕ 운동 추가하기
            </button>
          </div>
        ) : (
          <TodayWorkoutCard embedded items={items} onToggleSet={toggleSet} onOpenExercise={setOpenId} />
        )}
      </Node>

      <Node label={doneSets >= totalSets && totalSets > 0 ? "결과 RESULT" : "리워드 REWARD"} last>
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
        {/* 이번 달 미니 달력 */}
        <div className="rounded-2xl border border-white/[0.06] bg-card p-4">
          <div className="flex items-baseline justify-between">
            <b className="text-[15px] font-extrabold">{new Date().getFullYear()}년 {new Date().getMonth() + 1}월</b>
            <button onClick={() => router.push("/calendar")} className="text-[11.5px] font-bold text-white/45">달력 →</button>
          </div>
          {(() => {
            const now = new Date();
            const first = new Date(now.getFullYear(), now.getMonth(), 1);
            const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
            const pad = first.getDay(); // 일요일 시작
            const cells: (number | null)[] = [...Array(pad).fill(null), ...Array.from({ length: lastDay }, (_, i) => i + 1)];
            return (
              <div className="mt-2.5 grid grid-cols-7 gap-1 text-center">
                {["일", "월", "화", "수", "목", "금", "토"].map((d) => (
                  <span key={d} className="text-[9px] text-white/35">{d}</span>
                ))}
                {cells.map((d, i) => {
                  const worked = d != null && gymDash?.daysThisMonth.has(d);
                  const isToday = d === now.getDate();
                  return (
                    <span
                      key={i}
                      className={`grid aspect-square place-items-center rounded-lg text-[10.5px] tabular-nums ${
                        d == null ? "" : worked ? "bg-volt font-extrabold text-black" : isToday ? "border border-volt/60 text-volt" : "bg-white/[0.04] text-white/45"
                      }`}
                    >
                      {d ?? ""}
                    </span>
                  );
                })}
              </div>
            );
          })()}
        </div>

        {/* 출석률 랭킹 TOP5 */}
        <div className="rounded-2xl border border-white/[0.06] bg-card p-4">
          <div className="flex items-baseline justify-between">
            <b className="text-[15px] font-extrabold">출석률 랭킹</b>
            <button onClick={() => router.push("/ranking")} className="text-[11.5px] font-bold text-white/45">전체 →</button>
          </div>
          {rankRows.length ? (
            <div className="mt-1.5 divide-y divide-white/[0.06]">
              {rankRows.map((r, i) => {
                const me = String(user.id).toLowerCase() === r.id.toLowerCase();
                return (
                  <div key={r.id} className="flex items-center gap-2.5 py-2">
                    <span className="w-6 text-center text-[13px]">{["🥇", "🥈", "🥉"][i] ?? <b className="text-[12px] text-white/40">{i + 1}</b>}</span>
                    <span className={`min-w-0 flex-1 truncate text-[13px] font-bold ${me ? "text-volt" : "text-white/80"}`}>
                      {r.id}{me ? " (나)" : ""}
                    </span>
                    <b className="text-[13px] tabular-nums">{r.att}%</b>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="py-4 text-center text-[12.5px] text-white/40">랭킹을 불러오는 중이에요</p>
          )}
        </div>

        <div className="rounded-2xl border border-white/[0.06] bg-card p-4">
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

        <div className="rounded-2xl border border-white/[0.06] bg-card p-4">
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
        <div className="rounded-2xl border border-white/[0.06] bg-card p-4">
          <b className="text-[15px] font-extrabold">이번 주</b>
          <div className="mt-3">
            <WeekStrip days={week} target={`총 ${stats?.sessions ?? 0}회 · Lv${stats?.level ?? 1}`} />
          </div>
        </div>

        {/* 부위별 회복 상태 */}
        <div className="rounded-2xl border border-white/[0.06] bg-card p-4">
          <div className="flex items-baseline justify-between">
            <b className="text-[15px] font-extrabold">부위별 회복</b>
            <span className="text-[11px] text-white/45">컨디션 {condition}%</span>
          </div>
          <div className="mt-2.5 space-y-2">
            {[...recovery].sort((a, b) => a.pct - b.pct).slice(0, 5).map((r) => {
              const pct = Math.round(r.pct * 100);
              const full = r.pct >= 1;
              return (
                <div key={r.muscle} className="flex items-center gap-2.5">
                  <span className="w-14 shrink-0 text-[12px] font-bold text-white/60">{MUSCLE_KR[r.muscle]}</span>
                  <div className="h-3 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${Math.min(100, pct)}%`, background: full ? "#2dd4a0" : "#c8ff00" }}
                    />
                  </div>
                  <b className="w-11 shrink-0 text-right text-[12px] tabular-nums" style={{ color: full ? "#2dd4a0" : undefined }}>
                    {Math.min(100, pct)}%
                  </b>
                </div>
              );
            })}
          </div>
          <p className="mt-2 text-[10.5px] text-white/35">회복이 덜 된 부위 순 · 100%면 오늘 운동하기 좋아요</p>
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
        <p className="mt-0.5 text-[12px] text-white/50">루틴을 누르면 설명과 구성 종목을 확인할 수 있어요.</p>
        <div className="mt-4 space-y-2">
          {[...EXPLORE].sort((a, b) =>
            Number((user.v2?.savedRoutines ?? []).includes(b.id)) - Number((user.v2?.savedRoutines ?? []).includes(a.id))
          ).map((r, i) => {
            const saved = (user.v2?.savedRoutines ?? []).includes(r.id);
            const active = user.v2?.activeRoutineId === r.id;
            const expanded = pickDetail === r.id;
            return (
              <div
                key={r.id}
                className={`overflow-hidden rounded-lg border ${
                  expanded ? "border-volt/50 bg-volt/[0.04]" : active ? "border-volt/40 bg-volt/[0.06]" : "border-white/10 bg-white/[0.03]"
                }`}
              >
                <button
                  onClick={() => setPickDetail(expanded ? null : r.id)}
                  className="flex w-full items-center gap-3 p-3 text-left"
                >
                  <ColorInitialBadge text={r.badge} seed={i} />
                  <span className="min-w-0 flex-1">
                    <b className="block truncate text-[14px]">
                      {r.title}
                      {active && <span className="ml-1.5 rounded bg-volt px-1.5 py-0.5 text-[9px] font-extrabold text-black">사용 중</span>}
                      {saved && !active && <span className="ml-1.5 text-[10px] text-volt">💾 저장됨</span>}
                    </b>
                    <span className="text-[11px] text-white/45">
                      {r.weeks}주 · 주 {r.daysPerWeek}회 · 회당 ~{r.durationMin}분 · {r.level}
                    </span>
                  </span>
                  <span className={`shrink-0 text-[12px] text-white/30 transition-transform ${expanded ? "rotate-90" : ""}`}>›</span>
                </button>

                {/* 상세: 설명 + 구성 종목 + 시작 버튼 */}
                {expanded && (
                  <div className="border-t border-white/[0.06] px-3.5 pb-3.5 pt-3">
                    <p className="text-[12.5px] leading-relaxed text-white/70">{r.overview}</p>
                    {r.who && <p className="mt-2 text-[12px] leading-relaxed text-white/50">👤 {r.who}</p>}
                    {r.schedule && (
                      <p className="mt-2 rounded-lg bg-white/[0.05] px-2.5 py-2 text-[12px] font-bold text-white/70">📆 {r.schedule}</p>
                    )}
                    <div className="mt-2.5 grid grid-cols-2 gap-1.5">
                      {r.exercises.map((exId) => {
                        const ex = byId(exId);
                        return ex ? (
                          <span key={exId} className="flex items-center gap-1.5 rounded-lg bg-white/[0.05] p-1 pr-2 text-[11px] font-bold text-white/70">
                            <ExThumb ex={ex} size={26} rounded="rounded-md" />
                            <span className="min-w-0 truncate">{ex.name}</span>
                          </span>
                        ) : null;
                      })}
                    </div>
                    <button
                      onClick={() => {
                        updateItems(itemsFromExercises(r.exercises));
                        setActiveRoutine(r.id);
                        setPickDetail(null);
                        setShowRoutinePick(false);
                      }}
                      className="mt-3 w-full rounded-lg bg-volt py-2.5 text-[13.5px] font-bold text-black"
                    >
                      이 루틴으로 시작
                    </button>
                    <p className="mt-1.5 text-center text-[10.5px] text-white/35">시작하면 오늘 체크한 세트는 초기화돼요</p>
                  </div>
                )}
              </div>
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
              <ExThumb ex={ex} size={40} />
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
