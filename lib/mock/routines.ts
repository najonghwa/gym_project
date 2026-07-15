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
  overview: string;            // 상세 페이지 Overview
  target: string;              // 필터: 부위
  equipment: string;           // 필터: 장비
  level: "초급" | "중급" | "고급";
  muscles: Muscle[];
  exercises: string[];
  likes: number;
  weeks: number;
  daysPerWeek: number;
  durationMin: number;         // 회당 소요
  kcal: string;                // 예상 칼로리
}

export const EXPLORE: ExploreRoutine[] = [
  { id: "legday", badge: "LD", title: "이번 주, 다리 집중 🔥", desc: "스쿼트 중심 하체 볼륨 주간",
    overview: "하체가 부족하다고 느껴진다면 이 플랜. 스쿼트를 축으로 4주간 하체 볼륨을 끌어올려요. 상체는 유지 볼륨만 — 다리에 모든 에너지를 씁니다.",
    target: "하체", equipment: "바벨", level: "중급", muscles: ["legs", "glutes"], exercises: ["back_squat"], likes: 42, weeks: 4, daysPerWeek: 3, durationMin: 50, kcal: "300~420" },
  { id: "st55", badge: "ST", title: "스트롱리프트 5×5", desc: "초보 근력의 정석 A/B 루틴",
    overview: "헬스장이 처음이라 뭘 해야 할지 모르겠다면 여기서 시작하세요. 딱 5가지 운동을 5세트×5회 — 단순하지만 전 세계에서 가장 검증된 초보 근력 프로그램이에요.",
    target: "전신", equipment: "바벨", level: "초급", muscles: ["legs", "chest", "back"], exercises: ["back_squat", "bench_press", "seated_row"], likes: 128, weeks: 12, daysPerWeek: 3, durationMin: 45, kcal: "250~380" },
  { id: "ppl", badge: "PP", title: "PPL 6일 분할", desc: "밀·당·다리 주 2바퀴 고볼륨",
    overview: "미는 날·당기는 날·다리 날을 일주일에 두 바퀴 도는 고볼륨 분할. 부위당 주 2회 자극으로 성장 속도가 빠르지만, 주 6회 출석과 충분한 수면이 필요해요.",
    target: "전신", equipment: "머신+바벨", level: "중급", muscles: ["chest", "back", "legs", "shoulders"], exercises: ["bench_press", "lat_pulldown", "back_squat"], likes: 96, weeks: 12, daysPerWeek: 6, durationMin: 65, kcal: "400~550" },
  { id: "quickfit", badge: "QF", title: "점심 30분 스피드핏", desc: "바쁜 날을 위한 머신 서킷",
    overview: "점심시간에 후딱 치고 나오는 머신 위주 서킷. 세팅이 빠른 머신만 써서 옷 갈아입는 시간 포함 40분 안에 끝나요. 바쁜 주간의 비상용 플랜으로도 좋아요.",
    target: "상체", equipment: "머신", level: "초급", muscles: ["chest", "back", "shoulders"], exercises: ["lat_pulldown", "seated_row", "db_shoulder_press"], likes: 61, weeks: 4, daysPerWeek: 5, durationMin: 30, kcal: "180~260" },
  { id: "arms", badge: "AR", title: "소매가 터지는 팔 루틴", desc: "이두·삼두 집중 펌핑",
    overview: "여름 대비 팔 특화 6주. 이두·삼두를 다양한 각도로 조지는 펌핑 위주 구성이라 초보도 부담 없어요. 기존 루틴에 주 2회 얹어서 쓰는 걸 추천!",
    target: "팔", equipment: "덤벨", level: "중급", muscles: ["biceps", "triceps"], exercises: ["barbell_curl", "bench_press"], likes: 55, weeks: 6, daysPerWeek: 2, durationMin: 35, kcal: "200~280" },
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
