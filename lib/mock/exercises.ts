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
  pattern: MotionPattern;     // AnimPlayer 동작
  contrib: { muscle: Muscle; pct: number }[]; // 자극 기여% (MuscleDonut)
  tip: string;                // 전문가 한 줄
  howto: string[];
  restSec: number;
}

export type MotionPattern = "bench" | "squat" | "pulldown" | "curl" | "ohp" | "row";

export const EXERCISES: Exercise[] = [
  {
    id: "bench_press", name: "바벨 벤치프레스", em: "🏋️", zone: "A", equipment: "벤치프레스대",
    level: 3, pattern: "bench", restSec: 120,
    contrib: [{ muscle: "chest", pct: 60 }, { muscle: "triceps", pct: 20 }, { muscle: "shoulders", pct: 20 }],
    tip: "바를 내릴 때 팔꿈치가 몸통과 45도를 유지하면 어깨가 안전해요.",
    howto: ["벤치에 누워 견갑을 모으고 발로 바닥 지지", "바를 가슴 중앙까지 천천히", "가슴으로 밀어 올리기"],
  },
  {
    id: "back_squat", name: "바벨 백스쿼트", em: "🦵", zone: "A", equipment: "파워랙",
    level: 4, pattern: "squat", restSec: 150,
    contrib: [{ muscle: "legs", pct: 55 }, { muscle: "glutes", pct: 30 }, { muscle: "abs", pct: 15 }],
    tip: "무릎이 아니라 엉덩이부터 뒤로 — 의자에 앉는 느낌으로.",
    howto: ["바를 승모근 위에 얹고 랙 아웃", "엉덩이를 뒤로·아래로", "허벅지 평행까지 → 일어서기"],
  },
  {
    id: "lat_pulldown", name: "랫풀다운", em: "⬇️", zone: "B", equipment: "랫풀다운 머신",
    level: 2, pattern: "pulldown", restSec: 90,
    contrib: [{ muscle: "back", pct: 70 }, { muscle: "biceps", pct: 30 }],
    tip: "팔이 아니라 겨드랑이로 당긴다는 느낌.",
    howto: ["무릎 패드 고정, 넓게 그립", "쇄골 쪽으로 당기기", "천천히 올리기"],
  },
  {
    id: "db_shoulder_press", name: "덤벨 숄더프레스", em: "🙆", zone: "A", equipment: "덤벨세트",
    level: 2, pattern: "ohp", restSec: 90,
    contrib: [{ muscle: "shoulders", pct: 70 }, { muscle: "triceps", pct: 30 }],
    tip: "허리를 과하게 젖히지 말고 코어에 힘.",
    howto: ["덤벨을 귀 옆 높이로", "머리 위로 밀어 올리기", "천천히 내리기"],
  },
  {
    id: "barbell_curl", name: "바벨 컬", em: "💪", zone: "A", equipment: "EZ바",
    level: 1, pattern: "curl", restSec: 60,
    contrib: [{ muscle: "biceps", pct: 85 }, { muscle: "shoulders", pct: 15 }],
    tip: "내릴 때 2초 — 네거티브에 성장이 있어요.",
    howto: ["어깨너비 그립으로 서기", "팔꿈치 고정, 감아올리기", "반동 없이 천천히"],
  },
  {
    id: "seated_row", name: "시티드 로우", em: "🚣", zone: "B", equipment: "시티드로우 머신",
    level: 2, pattern: "row", restSec: 90,
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

// ── PR 차트 mock (스펙 P0-3) ──
export interface PRRow { date: string; value: number; isPR?: boolean }
export function getMockPR(metric: "1rm" | "weight" | "volume"): PRRow[] {
  const base = metric === "volume" ? 2800 : metric === "1rm" ? 72 : 60;
  const steps = [0, 2, 1, 4, 3, 6, 5, 9]; // 상승 흐름 + 굴곡
  let best = -Infinity;
  return steps.map((s, i) => {
    const value = Math.round(base + s * (metric === "volume" ? 120 : 2.5));
    const isPR = value > best;
    if (isPR) best = value;
    const d = new Date(); d.setDate(d.getDate() - (steps.length - 1 - i) * 4);
    return { date: `${d.getMonth() + 1}/${d.getDate()}`, value, isPR };
  });
}
