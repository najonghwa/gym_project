// 코치 리포트 계산 — 프로 트레이너가 회원을 모니터링하는 지표
// 근거: 순응도(1순위 KPI) · 볼륨 랜드마크(MEV/MAV/MRV, Israetel/RP) · 진행성 과부하(Epley e1RM) · 밀당/상하 밸런스
import type { UserData } from "./supa";
import type { TodayItem } from "./mock/exercises";
import { byId } from "./mock/exercises";
import { MUSCLE_KR, type Muscle } from "./recovery";

const MS_WEEK = 7 * 864e5;
const r1 = (x: number) => Math.round(x * 10) / 10;

// 부위별 주간 세트 랜드마크 (MEV=성장 최소, MAV=최적 중앙, MRV=회복 한계)
export const LANDMARK: Record<Muscle, { mev: number; mav: number; mrv: number }> = {
  chest: { mev: 10, mav: 16, mrv: 22 },
  back: { mev: 10, mav: 16, mrv: 22 },
  shoulders: { mev: 8, mav: 16, mrv: 22 },
  legs: { mev: 8, mav: 14, mrv: 20 },
  glutes: { mev: 4, mav: 10, mrv: 16 },
  biceps: { mev: 8, mav: 14, mrv: 20 },
  triceps: { mev: 8, mav: 14, mrv: 18 },
  abs: { mev: 6, mav: 12, mrv: 20 },
};

// 밸런스 그룹
const PUSH: Muscle[] = ["chest", "shoulders", "triceps"];
const PULL: Muscle[] = ["back", "biceps"];
const LOWER: Muscle[] = ["legs", "glutes"];

const wkKey = (ds: string) => {
  const d = new Date(ds + "T00:00:00");
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  d.setHours(0, 0, 0, 0);
  return d.getTime();
};
const e1rm = (kg: number, reps: number) => kg * (1 + reps / 30); // Epley

type Done = { exerciseId: string; kg: number; reps: number };

export interface CoachReport {
  hasData: boolean;
  // 이번 주 요약
  weekSessions: number;
  weekTarget: number;
  adherence: number;
  weekTonnage: number;
  tonnageDelta: number | null; // % vs 지난주
  // 진행 평가
  verdict: "progress" | "hold" | "decline" | "nodata";
  e1rmTop: { id: string; name: string; cur: number; prev: number | null; deltaPct: number | null }[];
  // 부위별 볼륨
  muscleVol: { muscle: Muscle; kr: string; sets: number; mev: number; mav: number; mrv: number; status: "low" | "ok" | "high" }[];
  weakest: { muscle: Muscle; kr: string } | null;
  // 밸런스
  pushSets: number; pullSets: number; upperSets: number; lowerSets: number;
  // 빈도 (주2회 최적)
  freq: { muscle: Muscle; kr: string; timesPerWeek: number }[];
  // 코치 코멘트
  notes: { tone: "good" | "warn" | "tip"; text: string }[];
}

export function coachReport(user: UserData, weekTarget = 4): CoachReport {
  const w = user.v2?.workouts ?? {};
  const now = Date.now();
  const thisWk = wkKey(new Date(now).toISOString().slice(0, 10));
  const lastWk = thisWk - MS_WEEK;
  const wk4 = thisWk - 3 * MS_WEEK;

  // 세션 날짜별 done 세트 수집
  const dates = new Set<string>();
  const setsThisWeek: Done[] = [];
  const setsLastWeek: Done[] = [];
  let tonThis = 0, tonLast = 0;
  // e1RM: 운동별 주차별 최고
  const e1rmByEx = new Map<string, Map<number, number>>();

  Object.entries(w).forEach(([date, day]) => {
    const wk = wkKey(date);
    let anyDone = false;
    (day.items as TodayItem[]).forEach((it) => {
      it.sets.forEach((s) => {
        if (!s.done) return;
        anyDone = true;
        const kg = s.weightKg ?? 0, reps = s.reps ?? 0;
        const d: Done = { exerciseId: it.exerciseId, kg, reps };
        if (wk === thisWk) { setsThisWeek.push(d); tonThis += kg * reps; }
        else if (wk === lastWk) { setsLastWeek.push(d); tonLast += kg * reps; }
        if (kg > 0 && reps > 0 && wk >= wk4) {
          const est = e1rm(kg, reps);
          if (!e1rmByEx.has(it.exerciseId)) e1rmByEx.set(it.exerciseId, new Map());
          const m = e1rmByEx.get(it.exerciseId)!;
          m.set(wk, Math.max(m.get(wk) ?? 0, est));
        }
      });
    });
    if (anyDone) dates.add(date);
  });

  const hasData = dates.size > 0;

  // 순응도 = 이번 주 세션 / 목표
  const weekSessions = new Set([...dates].filter((d) => wkKey(d) === thisWk)).size;
  const adherence = Math.min(100, Math.round((weekSessions / weekTarget) * 100));

  // 부위별 주간 세트 (주 운동=1세트, 보조 pct>=20=0.5세트 — fractional volume)
  const musVol = new Map<Muscle, number>();
  setsThisWeek.forEach((d) => {
    const ex = byId(d.exerciseId);
    if (!ex) return;
    ex.contrib.forEach((c, i) => {
      const val = i === 0 ? 1 : c.pct >= 20 ? 0.5 : 0;
      if (val) musVol.set(c.muscle, (musVol.get(c.muscle) ?? 0) + val);
    });
  });
  const muscleVol = (Object.keys(LANDMARK) as Muscle[]).map((muscle) => {
    const sets = Math.round((musVol.get(muscle) ?? 0) * 2) / 2;
    const { mev, mav, mrv } = LANDMARK[muscle];
    const status: "low" | "ok" | "high" = sets < mev ? "low" : sets > mrv ? "high" : "ok";
    return { muscle, kr: MUSCLE_KR[muscle], sets, mev, mav, mrv, status };
  }).sort((a, b) => b.sets - a.sets);

  // 약점 = MEV 대비 가장 부족한 (운동한 회원 기준 — 전부 0이면 null)
  const trained = muscleVol.filter((m) => m.sets > 0 || m.mev > 0);
  const weakestRow = trained.length
    ? [...muscleVol].sort((a, b) => (a.sets - a.mev) - (b.sets - b.mev))[0]
    : null;
  const weakest = weakestRow && weakestRow.sets < weakestRow.mev ? { muscle: weakestRow.muscle, kr: weakestRow.kr } : null;

  // 밸런스
  const groupSets = (ms: Muscle[]) => ms.reduce((s, m) => s + (musVol.get(m) ?? 0), 0);
  const pushSets = r1(groupSets(PUSH)), pullSets = r1(groupSets(PULL));
  const lowerSets = r1(groupSets(LOWER));
  const upperSets = r1(pushSets + pullSets);

  // 빈도 — 이번 주 각 부위를 몇 번의 서로 다른 세션에서 쳤나
  const freqMap = new Map<Muscle, Set<string>>();
  Object.entries(w).forEach(([date, day]) => {
    if (wkKey(date) !== thisWk) return;
    (day.items as TodayItem[]).forEach((it) => {
      if (!it.sets.some((s) => s.done)) return;
      const ex = byId(it.exerciseId);
      ex?.contrib.forEach((c, i) => {
        if (i === 0 || c.pct >= 30) {
          if (!freqMap.has(c.muscle)) freqMap.set(c.muscle, new Set());
          freqMap.get(c.muscle)!.add(date);
        }
      });
    });
  });
  const freq = muscleVol
    .filter((m) => (freqMap.get(m.muscle)?.size ?? 0) > 0)
    .map((m) => ({ muscle: m.muscle, kr: m.kr, timesPerWeek: freqMap.get(m.muscle)!.size }));

  // e1RM top — 이번 주에 한 운동 중 세트 많은 순 3개, prev주 대비
  const exFreqThis = new Map<string, number>();
  setsThisWeek.forEach((d) => exFreqThis.set(d.exerciseId, (exFreqThis.get(d.exerciseId) ?? 0) + 1));
  const e1rmTop = [...exFreqThis.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([id]) => {
      const m = e1rmByEx.get(id);
      const cur = m?.get(thisWk) ?? 0;
      const prev = m?.get(lastWk) ?? null;
      const deltaPct = prev && prev > 0 ? Math.round(((cur - prev) / prev) * 100) : null;
      return { id, name: byId(id)?.name ?? id, cur: Math.round(cur), prev: prev ? Math.round(prev) : null, deltaPct };
    })
    .filter((x) => x.cur > 0);

  const tonnageDelta = tonLast > 0 ? Math.round(((tonThis - tonLast) / tonLast) * 100) : null;

  // 진행 평가 — 톤수 추세 + e1RM 추세 종합
  const e1Deltas = e1rmTop.map((x) => x.deltaPct).filter((x): x is number => x != null);
  const avgE1 = e1Deltas.length ? e1Deltas.reduce((a, b) => a + b, 0) / e1Deltas.length : null;
  let verdict: CoachReport["verdict"] = "nodata";
  if (setsLastWeek.length > 0 || e1Deltas.length > 0) {
    const up = (tonnageDelta != null && tonnageDelta >= 3) || (avgE1 != null && avgE1 >= 2);
    const down = (tonnageDelta != null && tonnageDelta <= -12) && (avgE1 == null || avgE1 <= 0);
    verdict = up ? "progress" : down ? "decline" : "hold";
  } else if (hasData) verdict = "hold";

  // 코치 코멘트 — 데이터 기반 실행 제안
  const notes: CoachReport["notes"] = [];
  if (weekSessions >= weekTarget) notes.push({ tone: "good", text: `이번 주 목표(${weekTarget}회)를 달성했어요. 꾸준함이 최고의 무기예요.` });
  else if (hasData) notes.push({ tone: "tip", text: `이번 주 ${weekSessions}/${weekTarget}회 — 목표까지 ${weekTarget - weekSessions}번 남았어요.` });
  if (weakest) notes.push({ tone: "warn", text: `${weakest.kr}이(가) 주간 최소 볼륨(MEV)에 못 미쳐요. 다음 세션에 ${weakest.kr} 2~3세트를 추가해 보세요.` });
  const over = muscleVol.find((m) => m.status === "high");
  if (over) notes.push({ tone: "warn", text: `${over.kr} 볼륨이 회복 한계(MRV)를 넘었어요. 과사용 부상 위험 — 다음 주는 세트를 줄여 회복을 주세요.` });
  if (pullSets > 0 && pushSets > 0) {
    const ratio = pushSets / pullSets;
    if (ratio > 1.4) notes.push({ tone: "tip", text: `밀기가 당기기보다 많아요(${r1(ratio)} : 1). 어깨 건강을 위해 당기기(등) 볼륨을 늘려 균형을 맞추세요.` });
    else if (ratio < 0.7) notes.push({ tone: "tip", text: `당기기 위주예요. 가슴·어깨 밀기 볼륨을 보강하면 균형이 좋아져요.` });
  }
  if (verdict === "decline") notes.push({ tone: "warn", text: `이번 주 볼륨이 지난주보다 크게 줄었어요. 컨디션이 괜찮다면 강도를 회복하고, 피로하다면 계획된 디로드로 두세요.` });
  if (verdict === "progress") notes.push({ tone: "good", text: `중량·볼륨이 오르고 있어요 — 진행성 과부하가 잘 작동 중입니다. 이대로 유지하세요.` });
  if (notes.length === 0 && hasData) notes.push({ tone: "tip", text: `기록이 더 쌓이면 주간 비교와 맞춤 코멘트가 정교해져요.` });

  return {
    hasData, weekSessions, weekTarget, adherence,
    weekTonnage: Math.round(tonThis), tonnageDelta,
    verdict, e1rmTop, muscleVol, weakest,
    pushSets, pullSets, upperSets, lowerSets, freq, notes,
  };
}
