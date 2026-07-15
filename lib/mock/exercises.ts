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
  // ── 확장 풀 (구버전 운동 복원) ──
  { id: "deadlift", name: "데드리프트", em: "🏋️", zone: "A", equipment: "파워랙", level: 4, pattern: "squat", frames: frames("Barbell_Deadlift"), restSec: 180,
    contrib: [{ muscle: "back", pct: 40 }, { muscle: "legs", pct: 35 }, { muscle: "glutes", pct: 25 }],
    tip: "허리로 들지 말고 다리로 바닥을 밀어요.",
    howto: ["발 중간 위에 바, 정강이 가까이", "허리 편 채 엉덩이 뒤로 빼며 그립", "다리로 밀며 일어서기"] },
  { id: "pullup", name: "풀업(턱걸이)", em: "🙌", zone: "A", equipment: "풀업바", level: 4, pattern: "pulldown", frames: frames("Pullups"), restSec: 120,
    contrib: [{ muscle: "back", pct: 70 }, { muscle: "biceps", pct: 30 }],
    tip: "안 되면 밴드 보조나 네거티브(버티며 내려오기)부터.",
    howto: ["넓게 잡고 매달리기", "가슴을 바 쪽으로 당기기", "천천히 내려오기"] },
  { id: "incline_press", name: "인클라인 벤치프레스", em: "📐", zone: "A", equipment: "벤치프레스대", level: 3, pattern: "bench", frames: frames("Barbell_Incline_Bench_Press_-_Medium_Grip"), restSec: 120,
    contrib: [{ muscle: "chest", pct: 55 }, { muscle: "shoulders", pct: 30 }, { muscle: "triceps", pct: 15 }],
    tip: "가슴 윗부분(쇄골 라인)에 자극 집중.",
    howto: ["벤치 30~45도", "쇄골 쪽으로 천천히 내리고", "가슴 위로 밀어 올리기"] },
  { id: "db_bench", name: "덤벨 벤치프레스", em: "💪", zone: "A", equipment: "덤벨세트", level: 2, pattern: "bench", frames: frames("Dumbbell_Bench_Press"), restSec: 90,
    contrib: [{ muscle: "chest", pct: 60 }, { muscle: "triceps", pct: 20 }, { muscle: "shoulders", pct: 20 }],
    tip: "바벨보다 가동범위가 넓어 자극이 깊어요.",
    howto: ["덤벨을 가슴 옆까지 내리고", "가슴 위 중앙으로 모아 올리기", "팔꿈치 45도 유지"] },
  { id: "cable_fly", name: "케이블 크로스오버", em: "✖️", zone: "C", equipment: "케이블 크로스오버", level: 2, pattern: "bench", frames: frames("Cable_Crossover"), restSec: 60,
    contrib: [{ muscle: "chest", pct: 80 }, { muscle: "shoulders", pct: 20 }],
    tip: "모을 때 가슴을 쥐어짜듯 1초 정지.",
    howto: ["양쪽 손잡이 잡고 한 발 앞", "팔 약간 굽혀 앞으로 모으기", "천천히 벌리기"] },
  { id: "lateral_raise", name: "레터럴 레이즈", em: "🕊️", zone: "A", equipment: "덤벨세트", level: 1, pattern: "ohp", frames: frames("Side_Lateral_Raise"), restSec: 60,
    contrib: [{ muscle: "shoulders", pct: 90 }, { muscle: "back", pct: 10 }],
    tip: "가볍게! 어깨 높이까지만, 반동 금지.",
    howto: ["덤벨을 몸 옆에", "팔 약간 굽혀 어깨 높이까지", "새 날갯짓처럼 천천히 내리기"] },
  { id: "face_pull", name: "페이스풀", em: "🎯", zone: "C", equipment: "케이블 머신", level: 2, pattern: "row", frames: frames("Face_Pull"), restSec: 60,
    contrib: [{ muscle: "shoulders", pct: 55 }, { muscle: "back", pct: 45 }],
    tip: "어깨 건강 보험 — 매 등/어깨 날에 끼워 넣기.",
    howto: ["로프를 얼굴 높이로", "얼굴 쪽으로 당기며 팔꿈치 벌리기", "어깨 뒤쪽 조이기"] },
  { id: "pushdown", name: "케이블 푸시다운", em: "⤵️", zone: "C", equipment: "케이블 머신", level: 1, pattern: "curl", frames: frames("Triceps_Pushdown"), restSec: 60,
    contrib: [{ muscle: "triceps", pct: 95 }, { muscle: "shoulders", pct: 5 }],
    tip: "팔꿈치를 옆구리에 고정 — 움직이면 반칙.",
    howto: ["팔꿈치 몸통 고정", "아래로 쭉 펴기", "천천히 되돌리기"] },
  { id: "dips", name: "딥스", em: "🇭", zone: "A", equipment: "딥스대", level: 3, pattern: "bench", frames: frames("Dips_-_Triceps_Version"), restSec: 90,
    contrib: [{ muscle: "triceps", pct: 60 }, { muscle: "chest", pct: 30 }, { muscle: "shoulders", pct: 10 }],
    tip: "몸 세우면 삼두, 기울이면 가슴.",
    howto: ["평행봉 잡고 몸 띄우기", "팔꿈치 굽혀 내려가기", "펴며 올라오기"] },
  { id: "db_curl", name: "덤벨 컬", em: "💪", zone: "A", equipment: "덤벨세트", level: 1, pattern: "curl", frames: frames("Dumbbell_Bicep_Curl"), restSec: 60,
    contrib: [{ muscle: "biceps", pct: 90 }, { muscle: "shoulders", pct: 10 }],
    tip: "내릴 때 2초 — 네거티브가 팔을 키워요.",
    howto: ["손바닥 앞으로 덤벨 들기", "팔꿈치 고정 감아올리기", "반동 없이 천천히"] },
  { id: "leg_press", name: "레그프레스", em: "🦵", zone: "B", equipment: "레그프레스 머신", level: 2, pattern: "squat", frames: frames("Leg_Press"), restSec: 120,
    contrib: [{ muscle: "legs", pct: 70 }, { muscle: "glutes", pct: 30 }],
    tip: "무릎을 끝까지 펴서 잠그지 말 것.",
    howto: ["어깨너비로 발판에 발", "무릎이 가슴 쪽으로 오게 내리고", "발바닥 전체로 밀기"] },
  { id: "leg_ext", name: "레그 익스텐션", em: "🦿", zone: "B", equipment: "레그익스텐션 머신", level: 1, pattern: "squat", frames: frames("Leg_Extensions"), restSec: 60,
    contrib: [{ muscle: "legs", pct: 100 }],
    tip: "맨 위에서 1초 멈추면 자극 두 배.",
    howto: ["발목 패드에 발 걸고", "다리 쭉 펴기", "1초 정지 후 천천히"] },
  { id: "leg_curl", name: "레그 컬", em: "🪝", zone: "B", equipment: "레그컬 머신", level: 1, pattern: "squat", frames: frames("Seated_Leg_Curl"), restSec: 60,
    contrib: [{ muscle: "legs", pct: 85 }, { muscle: "glutes", pct: 15 }],
    tip: "햄스트링은 부상 예방의 핵심 — 빼먹지 말기.",
    howto: ["발목 뒤 패드 세팅", "엉덩이 쪽으로 접기", "반동 없이 펴기"] },
  { id: "lunge", name: "덤벨 런지", em: "🚶", zone: "A", equipment: "덤벨세트", level: 2, pattern: "squat", frames: frames("Barbell_Lunge"), restSec: 90,
    contrib: [{ muscle: "legs", pct: 60 }, { muscle: "glutes", pct: 40 }],
    tip: "앞발 뒤꿈치로 밀며 일어나기.",
    howto: ["한 발 크게 앞으로", "뒷무릎 바닥 가까이", "앞발로 밀며 복귀"] },
  { id: "rdl", name: "루마니안 데드리프트", em: "🍑", zone: "A", equipment: "바벨/벤치", level: 3, pattern: "squat", frames: frames("Romanian_Deadlift"), restSec: 120,
    contrib: [{ muscle: "legs", pct: 50 }, { muscle: "glutes", pct: 35 }, { muscle: "back", pct: 15 }],
    tip: "허벅지 뒤가 당길 때까지만 — 허리 굽히지 않기.",
    howto: ["바를 허벅지 앞에", "무릎 살짝 굽힌 채 엉덩이 뒤로", "엉덩이 힘으로 복귀"] },
  { id: "hip_thrust", name: "힙 쓰러스트", em: "🍑", zone: "A", equipment: "바벨/벤치", level: 2, pattern: "squat", frames: frames("Barbell_Hip_Thrust"), restSec: 90,
    contrib: [{ muscle: "glutes", pct: 70 }, { muscle: "legs", pct: 30 }],
    tip: "맨 위에서 엉덩이 꽉 조이고 1초.",
    howto: ["등 상부를 벤치에", "바를 골반 위에 올리고", "엉덩이를 밀어 올려 일직선"] },
  { id: "calf_raise", name: "카프레이즈", em: "🦶", zone: "B", equipment: "카프레이즈 머신", level: 1, pattern: "squat", frames: frames("Standing_Calf_Raises"), restSec: 60,
    contrib: [{ muscle: "legs", pct: 100 }],
    tip: "위에서 1초, 아래에서 스트레칭 1초.",
    howto: ["발끝을 발판에", "최대한 높이 올라가기", "뒤꿈치 내려 늘리기"] },
  { id: "plank", name: "플랭크", em: "🧱", zone: "E", equipment: "매트", level: 1, pattern: "row", frames: frames("Plank"), restSec: 45,
    contrib: [{ muscle: "abs", pct: 80 }, { muscle: "shoulders", pct: 20 }],
    tip: "엉덩이가 들리거나 처지지 않게 일직선.",
    howto: ["팔꿈치·발끝 지지", "머리~발끝 일직선", "배에 힘 주고 버티기"] },
  { id: "crunch", name: "크런치", em: "🌙", zone: "E", equipment: "매트", level: 1, pattern: "curl", frames: frames("Crunches"), restSec: 45,
    contrib: [{ muscle: "abs", pct: 100 }],
    tip: "목이 아니라 복근으로 접기.",
    howto: ["무릎 세우고 눕기", "배를 접듯 어깨만 들기", "천천히 내리기"] },
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
    deadlift: 100, pullup: 0, incline_press: 50, db_bench: 22,
    cable_fly: 15, lateral_raise: 8, face_pull: 20, pushdown: 25,
    dips: 0, db_curl: 12, leg_press: 120, leg_ext: 40, leg_curl: 35,
    lunge: 12, rdl: 60, hip_thrust: 80, calf_raise: 60, plank: 0, crunch: 0,
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
  deadlift: 130, incline_press: 60, db_bench: 28, leg_press: 160,
  hip_thrust: 100, rdl: 80, pushdown: 35, db_curl: 16,
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
