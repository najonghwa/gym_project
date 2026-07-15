// 운동 mock — 오늘 루틴 + 상세 시트용 (스펙 P0-2)
// TODO(supabase): gym_users.data.routine 에서 로드
import type { Muscle } from "@/lib/recovery";

export interface SetRow {
  kind: "warmup" | "working";
  weightKg: number;
  reps: number;
  done: boolean;
}

export interface Exercise {
  id: string;
  name: string;
  em: string;                 // 아이콘
  zone: string;               // 헬스장 구역
  equipment: string;
  level: 1 | 2 | 3 | 4 | 5;   // 난이도 (LevelDots)
  pattern: MotionPattern;     // AnimPlayer 동작 (프레임 없을 때 폴백)
  frames?: [string, string];  // 실사 2프레임 (free-exercise-db, 퍼블릭 도메인)
  contrib: { muscle: Muscle; pct: number }[]; // 자극 기여% (MuscleDonut)
  tip: string;                // 전문가 한 줄
  howto: string[];
  restSec: number;
}

const FEDB = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises";
const frames = (slug: string): [string, string] => [`${FEDB}/${slug}/0.jpg`, `${FEDB}/${slug}/1.jpg`];

export type MotionPattern = "bench" | "squat" | "pulldown" | "curl" | "ohp" | "row";

export const EXERCISES: Exercise[] = [
  {
    id: "bench_press", name: "바벨 벤치프레스", em: "🏋️", zone: "A", equipment: "벤치프레스대",
    level: 3, pattern: "bench", frames: frames("Barbell_Bench_Press_-_Medium_Grip"), restSec: 120,
    contrib: [{ muscle: "chest", pct: 60 }, { muscle: "triceps", pct: 20 }, { muscle: "shoulders", pct: 20 }],
    tip: "바를 내릴 때 팔꿈치가 몸통과 45도를 유지하면 어깨가 안전해요.",
    howto: ["벤치에 누워 견갑을 모으고 발로 바닥 지지", "바를 가슴 중앙까지 천천히", "가슴으로 밀어 올리기"],
  },
  {
    id: "back_squat", name: "바벨 백스쿼트", em: "🦵", zone: "A", equipment: "파워랙",
    level: 4, pattern: "squat", frames: frames("Barbell_Squat"), restSec: 150,
    contrib: [{ muscle: "legs", pct: 55 }, { muscle: "glutes", pct: 30 }, { muscle: "abs", pct: 15 }],
    tip: "무릎이 아니라 엉덩이부터 뒤로 — 의자에 앉는 느낌으로.",
    howto: ["바를 승모근 위에 얹고 랙 아웃", "엉덩이를 뒤로·아래로", "허벅지 평행까지 → 일어서기"],
  },
  {
    id: "lat_pulldown", name: "랫풀다운", em: "⬇️", zone: "B", equipment: "랫풀다운 머신",
    level: 2, pattern: "pulldown", frames: frames("Wide-Grip_Lat_Pulldown"), restSec: 90,
    contrib: [{ muscle: "back", pct: 70 }, { muscle: "biceps", pct: 30 }],
    tip: "팔이 아니라 겨드랑이로 당긴다는 느낌.",
    howto: ["무릎 패드 고정, 넓게 그립", "쇄골 쪽으로 당기기", "천천히 올리기"],
  },
  {
    id: "db_shoulder_press", name: "덤벨 숄더프레스", em: "🙆", zone: "A", equipment: "덤벨세트",
    level: 2, pattern: "ohp", frames: frames("Dumbbell_Shoulder_Press"), restSec: 90,
    contrib: [{ muscle: "shoulders", pct: 70 }, { muscle: "triceps", pct: 30 }],
    tip: "허리를 과하게 젖히지 말고 코어에 힘.",
    howto: ["덤벨을 귀 옆 높이로", "머리 위로 밀어 올리기", "천천히 내리기"],
  },
  {
    id: "barbell_curl", name: "바벨 컬", em: "💪", zone: "A", equipment: "EZ바",
    level: 1, pattern: "curl", frames: frames("Barbell_Curl"), restSec: 60,
    contrib: [{ muscle: "biceps", pct: 85 }, { muscle: "shoulders", pct: 15 }],
    tip: "내릴 때 2초 — 네거티브에 성장이 있어요.",
    howto: ["어깨너비 그립으로 서기", "팔꿈치 고정, 감아올리기", "반동 없이 천천히"],
  },
  {
    id: "seated_row", name: "시티드 로우", em: "🚣", zone: "B", equipment: "시티드로우 머신",
    level: 2, pattern: "row", frames: frames("Seated_Cable_Rows"), restSec: 90,
    contrib: [{ muscle: "back", pct: 65 }, { muscle: "biceps", pct: 25 }, { muscle: "shoulders", pct: 10 }],
    tip: "허리를 세우고 팔꿈치를 뒤로 끝까지.",
    howto: ["가슴 패드에 몸 고정", "팔꿈치를 뒤로 당기기", "등 중앙 조인 후 천천히"],
  },
];

export const byId = (id: string) => EXERCISES.find((e) => e.id === id);

// 같은 주자극 부위의 대체 운동 (Replace 시트용)
export function alternativesFor(id: string): Exercise[] {
  const ex = byId(id);
  if (!ex) return [];
  const main = ex.contrib[0].muscle;
  return EXERCISES.filter((e) => e.id !== id && e.contrib[0].muscle === main);
}

// ── 오늘 루틴 mock: 운동별 세트 구성 ──
export interface TodayItem { exerciseId: string; sets: SetRow[] }

export function getMockToday(): TodayItem[] {
  const w = (weightKg: number, reps: number, kind: SetRow["kind"] = "working"): SetRow =>
    ({ kind, weightKg, reps, done: false });
  return [
    { exerciseId: "bench_press", sets: [w(40, 12, "warmup"), w(60, 8), w(65, 6), w(65, 6)] },
    { exerciseId: "db_shoulder_press", sets: [w(12, 12, "warmup"), w(18, 10), w(18, 10), w(20, 8)] },
    { exerciseId: "lat_pulldown", sets: [w(35, 12, "warmup"), w(50, 10), w(55, 8)] },
    { exerciseId: "barbell_curl", sets: [w(15, 12), w(20, 10), w(20, 10)] },
  ];
}

// 루틴(운동 id 목록) → 오늘 세트 구성 (루틴 적용용)
export function itemsFromExercises(ids: string[]): TodayItem[] {
  const BASE_KG: Record<string, number> = {
    bench_press: 60, back_squat: 80, lat_pulldown: 50,
    db_shoulder_press: 18, barbell_curl: 20, seated_row: 45,
  };
  return ids
    .map((id) => byId(id))
    .filter((ex): ex is Exercise => !!ex)
    .map((ex) => {
      const kg = BASE_KG[ex.id] ?? 20;
      return {
        exerciseId: ex.id,
        sets: [
          { kind: "warmup" as const, weightKg: Math.round(kg * 0.6 / 2.5) * 2.5, reps: 12, done: false },
          { kind: "working" as const, weightKg: kg, reps: 10, done: false },
          { kind: "working" as const, weightKg: kg, reps: 10, done: false },
          { kind: "working" as const, weightKg: kg + 2.5, reps: 8, done: false },
        ],
      };
    });
}

// ── PR 차트 mock (스펙 P0-3) — 운동별로 다른 시드 ──
export interface PRRow { date: string; value: number; isPR?: boolean }
const PR_BASE: Record<string, number> = {
  bench_press: 72, back_squat: 105, lat_pulldown: 60,
  db_shoulder_press: 26, barbell_curl: 32, seated_row: 55,
};
export function getMockPR(metric: "1rm" | "weight" | "volume", exId = "bench_press"): PRRow[] {
  const b = PR_BASE[exId] ?? 50;
  const base = metric === "volume" ? b * 38 : metric === "1rm" ? b : Math.round(b * 0.85);
  // 운동 id 해시로 굴곡 패턴 변형
  const seed = exId.split("").reduce((s, c) => s + c.charCodeAt(0), 0);
  const steps = [0, 2, 1, 4, 3, 6, 5, 9].map((v, i) => v + ((seed + i) % 3) - 1);
  let best = -Infinity;
  return steps.map((s, i) => {
    const value = Math.round(base + Math.max(0, s) * (metric === "volume" ? b * 1.6 : 2.5));
    const isPR = value > best;
    if (isPR) best = value;
    const d = new Date(); d.setDate(d.getDate() - (steps.length - 1 - i) * 4);
    return { date: `${d.getMonth() + 1}/${d.getDate()}`, value, isPR };
  });
}
