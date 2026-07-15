// 루틴 mock — 생성 리빌 + Explore (스펙 P1-6/P1-7)
// TODO(supabase): gym_shared_routines + PROGRAMS 이관
import type { Muscle } from "@/lib/recovery";

export interface PlanDay {
  day: string;                 // 월/수/...
  title: string;               // 가슴·삼두
  muscles: Muscle[];
  exercises: string[];         // exercise ids (mock/exercises.ts)
}

export const GENERATED_PLAN: PlanDay[] = [
  { day: "월", title: "가슴 · 삼두", muscles: ["chest", "triceps"], exercises: ["bench_press", "db_shoulder_press", "barbell_curl"] },
  { day: "수", title: "등 · 이두", muscles: ["back", "biceps"], exercises: ["lat_pulldown", "seated_row", "barbell_curl"] },
  { day: "금", title: "하체 · 코어", muscles: ["legs", "glutes", "abs"], exercises: ["back_squat", "seated_row"] },
  { day: "토", title: "어깨 · 팔", muscles: ["shoulders", "biceps", "triceps"], exercises: ["db_shoulder_press", "barbell_curl", "bench_press"] },
];

// 카드별 AI 교체용 대체 구성
export const ALT_DAYS: Record<string, PlanDay> = {
  "월": { day: "월", title: "가슴 · 어깨 (변형)", muscles: ["chest", "shoulders"], exercises: ["bench_press", "db_shoulder_press"] },
  "수": { day: "수", title: "등 집중 (변형)", muscles: ["back"], exercises: ["lat_pulldown", "seated_row"] },
  "금": { day: "금", title: "하체 볼륨 (변형)", muscles: ["legs", "glutes"], exercises: ["back_squat"] },
  "토": { day: "토", title: "팔 펌핑 (변형)", muscles: ["biceps", "triceps"], exercises: ["barbell_curl", "bench_press"] },
};

export const GEN_CAPTIONS = [
  "다리에 집중하는 중…",
  "휴식일 배치 중…",
  "회복도 반영하는 중…",
  "볼륨 계산하는 중…",
  "마무리 다듬는 중…",
];

// ── Explore 테마 루틴 ──
export interface ExploreRoutine {
  id: string;
  badge: string;               // 이니셜 뱃지 (LD/ST/QF)
  title: string;
  desc: string;
  target: string;              // 필터: 부위
  equipment: string;           // 필터: 장비
  level: "초급" | "중급" | "고급";
  muscles: Muscle[];
  exercises: string[];
  likes: number;
  weeks: number;
  daysPerWeek: number;
}

export const EXPLORE: ExploreRoutine[] = [
  { id: "legday", badge: "LD", title: "이번 주, 다리 집중 🔥", desc: "스쿼트 중심 하체 볼륨 주간", target: "하체", equipment: "바벨", level: "중급", muscles: ["legs", "glutes"], exercises: ["back_squat"], likes: 42, weeks: 4, daysPerWeek: 3 },
  { id: "st55", badge: "ST", title: "스트롱리프트 5×5", desc: "초보 근력의 정석 A/B 루틴", target: "전신", equipment: "바벨", level: "초급", muscles: ["legs", "chest", "back"], exercises: ["back_squat", "bench_press", "seated_row"], likes: 128, weeks: 12, daysPerWeek: 3 },
  { id: "ppl", badge: "PP", title: "PPL 6일 분할", desc: "밀·당·다리 주 2바퀴 고볼륨", target: "전신", equipment: "머신+바벨", level: "중급", muscles: ["chest", "back", "legs", "shoulders"], exercises: ["bench_press", "lat_pulldown", "back_squat"], likes: 96, weeks: 12, daysPerWeek: 6 },
  { id: "quickfit", badge: "QF", title: "점심 30분 스피드핏", desc: "바쁜 날을 위한 머신 서킷", target: "상체", equipment: "머신", level: "초급", muscles: ["chest", "back", "shoulders"], exercises: ["lat_pulldown", "seated_row", "db_shoulder_press"], likes: 61, weeks: 4, daysPerWeek: 5 },
  { id: "arms", badge: "AR", title: "소매가 터지는 팔 루틴", desc: "이두·삼두 집중 펌핑", target: "팔", equipment: "덤벨", level: "중급", muscles: ["biceps", "triceps"], exercises: ["barbell_curl", "bench_press"], likes: 55, weeks: 6, daysPerWeek: 2 },
];

export const FILTER = {
  target: ["전체", "전신", "상체", "하체", "팔"],
  equipment: ["전체", "바벨", "덤벨", "머신"],
  level: ["전체", "초급", "중급", "고급"],
};

// ── 분석 카드 mock (P1-5) ──
export const VOLUME_WEEKS = [
  { name: "2주전", volume: 4200 },
  { name: "1주전", volume: 5100 },
  { name: "이번주", volume: 5600 },
];

export const BALANCE_RADAR = [
  { part: "가슴", me: 82 },
  { part: "등", me: 74 },
  { part: "어깨", me: 55 },
  { part: "하체", me: 38 },
  { part: "팔", me: 66 },
  { part: "코어", me: 45 },
];

export const PEER_RADAR = [
  { part: "볼륨", me: 72, peer: 61 },
  { part: "빈도", me: 80, peer: 66 },
  { part: "강도", me: 58, peer: 70 },
  { part: "지구력", me: 64, peer: 55 },
  { part: "꾸준함", me: 88, peer: 62 },
];

// ── 성장 곡선 mock (P2-12) ──
export const GROWTH = {
  withPlan: [0, 8, 15, 26, 34, 47, 58, 72],   // 계획 있음
  withoutPlan: [0, 5, 8, 12, 14, 17, 19, 22], // 계획 없음
};
