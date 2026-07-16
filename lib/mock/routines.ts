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
  { day: "월", title: "가슴 · 삼두", muscles: ["chest", "triceps"], exercises: ["bench_press", "incline_press", "cable_fly", "pushdown", "dips"] },
  { day: "수", title: "등 · 이두", muscles: ["back", "biceps"], exercises: ["lat_pulldown", "seated_row", "pullup", "barbell_curl", "face_pull"] },
  { day: "금", title: "하체 · 코어", muscles: ["legs", "glutes", "abs"], exercises: ["back_squat", "leg_press", "rdl", "calf_raise", "plank"] },
  { day: "토", title: "어깨 · 팔", muscles: ["shoulders", "biceps", "triceps"], exercises: ["db_shoulder_press", "lateral_raise", "face_pull", "barbell_curl", "pushdown"] },
];

// 카드별 AI 교체용 대체 구성
export const ALT_DAYS: Record<string, PlanDay> = {
  "월": { day: "월", title: "가슴 · 어깨 (변형)", muscles: ["chest", "shoulders"], exercises: ["db_bench", "incline_press", "lateral_raise", "cable_fly"] },
  "수": { day: "수", title: "등 집중 (변형)", muscles: ["back"], exercises: ["pullup", "lat_pulldown", "seated_row", "face_pull"] },
  "금": { day: "금", title: "하체 볼륨 (변형)", muscles: ["legs", "glutes"], exercises: ["leg_press", "leg_ext", "leg_curl", "lunge", "calf_raise"] },
  "토": { day: "토", title: "팔 펌핑 (변형)", muscles: ["biceps", "triceps"], exercises: ["db_curl", "barbell_curl", "pushdown", "dips"] },
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
  { id: "legday", badge: "LD", title: "하체 집중 4주", desc: "스쿼트 중심 하체 볼륨 주간",
    overview: "하체가 부족하다고 느껴진다면 이 플랜. 스쿼트를 축으로 4주간 하체 볼륨을 끌어올려요. 상체는 유지 볼륨만 — 다리에 모든 에너지를 씁니다.",
    target: "하체", equipment: "바벨", level: "중급", muscles: ["legs", "glutes"], exercises: ["back_squat", "leg_press", "rdl", "leg_ext", "leg_curl", "lunge", "calf_raise"], likes: 42, weeks: 4, daysPerWeek: 3, durationMin: 50, kcal: "300~420" },
  { id: "st55", badge: "ST", title: "스트롱리프트 5×5", desc: "초보 근력의 정석 A/B 루틴",
    overview: "헬스장이 처음이라 뭘 해야 할지 모르겠다면 여기서 시작하세요. 딱 5가지 운동을 5세트×5회 — 단순하지만 전 세계에서 가장 검증된 초보 근력 프로그램이에요.",
    target: "전신", equipment: "바벨", level: "초급", muscles: ["legs", "chest", "back"], exercises: ["back_squat", "bench_press", "seated_row", "db_shoulder_press", "deadlift"], likes: 128, weeks: 12, daysPerWeek: 3, durationMin: 45, kcal: "250~380" },
  { id: "ppl", badge: "PP", title: "PPL 6일 분할", desc: "밀·당·다리 주 2바퀴 고볼륨",
    overview: "미는 날·당기는 날·다리 날을 일주일에 두 바퀴 도는 고볼륨 분할. 부위당 주 2회 자극으로 성장 속도가 빠르지만, 주 6회 출석과 충분한 수면이 필요해요.",
    target: "전신", equipment: "머신+바벨", level: "중급", muscles: ["chest", "back", "legs", "shoulders"], exercises: ["bench_press", "incline_press", "lateral_raise", "pushdown", "pullup", "seated_row", "back_squat", "rdl"], likes: 96, weeks: 12, daysPerWeek: 6, durationMin: 65, kcal: "400~550" },
  { id: "quickfit", badge: "QF", title: "30분 전신 서킷", desc: "바쁜 날을 위한 머신 서킷",
    overview: "점심시간에 후딱 치고 나오는 머신 위주 서킷. 세팅이 빠른 머신만 써서 옷 갈아입는 시간 포함 40분 안에 끝나요. 바쁜 주간의 비상용 플랜으로도 좋아요.",
    target: "상체", equipment: "머신", level: "초급", muscles: ["chest", "back", "shoulders"], exercises: ["lat_pulldown", "leg_press", "db_bench", "seated_row", "plank"], likes: 61, weeks: 4, daysPerWeek: 5, durationMin: 30, kcal: "180~260" },
  { id: "arms", badge: "AR", title: "팔 집중 6주", desc: "이두·삼두 집중 펌핑",
    overview: "여름 대비 팔 특화 6주. 이두·삼두를 다양한 각도로 조지는 펌핑 위주 구성이라 초보도 부담 없어요. 기존 루틴에 주 2회 얹어서 쓰는 걸 추천!",
    target: "팔", equipment: "덤벨", level: "중급", muscles: ["biceps", "triceps"], exercises: ["barbell_curl", "db_curl", "pushdown", "dips", "face_pull"], likes: 55, weeks: 6, daysPerWeek: 2, durationMin: 35, kcal: "200~280" },
  // ── 유명 프로그램 (구버전 10종 복원) ──
  { id: "ss", badge: "SS", title: "스타팅 스트렝스", desc: "마크 리피토의 교과서 3×5",
    overview: "미국 초보 근력의 바이블. 스쿼트를 매 세션 하며 3세트×5회로 기본기를 다져요. 5×5보다 세트가 적어 회복이 쉬워 진짜 처음이라면 여기부터.",
    target: "전신", equipment: "바벨", level: "초급", muscles: ["legs", "chest", "back"], exercises: ["back_squat", "bench_press", "deadlift", "db_shoulder_press", "pullup"], likes: 87, weeks: 12, daysPerWeek: 3, durationMin: 40, kcal: "230~350" },
  { id: "phul", badge: "PH", title: "PHUL 4일 분할", desc: "힘의 날 + 펌핑의 날 반반",
    overview: "상체 힘/하체 힘/상체 펌핑/하체 펌핑 — 주 4회. 앞의 이틀은 무겁게 적은 횟수, 뒤의 이틀은 가볍게 많은 횟수로 근력과 크기를 동시에 잡아요.",
    target: "전신", equipment: "바벨+머신", level: "중급", muscles: ["chest", "back", "legs", "shoulders"], exercises: ["back_squat", "deadlift", "bench_press", "seated_row", "leg_press", "incline_press", "lat_pulldown", "db_curl"], likes: 74, weeks: 12, daysPerWeek: 4, durationMin: 60, kcal: "350~480" },
  { id: "gvt", badge: "GV", title: "GVT 10×10 (독일식 볼륨)", desc: "한 운동 10세트×10회, 벌크의 클래식",
    overview: "부위별 대표 운동 하나를 10세트×10회(휴식 60초). 무게는 10회 최대치의 60%로 가볍게 시작하는 게 포인트 — 6주만 해도 옷핏이 달라져요. 마지막 3세트는 지옥이 정상.",
    target: "전신", equipment: "바벨", level: "고급", muscles: ["chest", "back", "legs"], exercises: ["back_squat", "bench_press", "seated_row", "db_shoulder_press", "leg_curl", "lateral_raise"], likes: 45, weeks: 6, daysPerWeek: 4, durationMin: 55, kcal: "400~520" },
  { id: "five31", badge: "53", title: "5/3/1 (짐 웬들러)", desc: "4주 파도로 끝없이 강해지기",
    overview: "매주 메인 리프트 강도가 파도처럼 바뀌어요: 5·5·5 → 3·3·3 → 5·3·1 → 디로드. 이 4주 사이클을 반복하며 매 사이클 기록을 갱신하는 장기 근력 프로그램. 마지막 세트는 한계까지(AMRAP)!",
    target: "전신", equipment: "바벨", level: "중급", muscles: ["shoulders", "legs", "chest", "back"], exercises: ["back_squat", "bench_press", "deadlift", "db_shoulder_press", "pullup", "dips"], likes: 69, weeks: 16, daysPerWeek: 4, durationMin: 50, kcal: "300~430" },
  { id: "texas", badge: "TX", title: "텍사스 메소드", desc: "볼륨 → 회복 → 금요일 신기록",
    overview: "월요일은 많이(5×5 볼륨), 수요일은 가볍게(회복), 금요일은 무겁게 신기록 도전. 5×5로 정체가 왔을 때 다음 단계로 좋은 중급자 프로그램이에요.",
    target: "전신", equipment: "바벨", level: "중급", muscles: ["legs", "chest", "shoulders"], exercises: ["back_squat", "bench_press", "deadlift", "db_shoulder_press", "seated_row"], likes: 38, weeks: 12, daysPerWeek: 3, durationMin: 55, kcal: "320~450" },
  { id: "bro", badge: "BR", title: "브로 스플릿 5분할", desc: "하루 한 부위, 헬스장의 클래식",
    overview: "가슴/등/어깨/하체/팔을 하루 하나씩 조지는 전통 보디빌딩 방식. 부위당 볼륨이 커서 펌핑 맛이 확실하고, 한 부위는 일주일을 쉬어 회복 걱정이 없어요.",
    target: "전신", equipment: "바벨+머신", level: "중급", muscles: ["chest", "back", "shoulders", "legs", "biceps"], exercises: ["bench_press", "cable_fly", "lat_pulldown", "db_shoulder_press", "lateral_raise", "back_squat", "barbell_curl", "pushdown"], likes: 91, weeks: 8, daysPerWeek: 5, durationMin: 60, kcal: "380~500" },
  { id: "arnold", badge: "AN", title: "아놀드 스플릿", desc: "아놀드의 3분할 × 주 2바퀴",
    overview: "가슴·등 / 어깨·팔 / 하체를 일주일에 두 바퀴 도는 고볼륨 분할. 부위당 주 2회 자극 — 아놀드를 미스터 올림피아로 만든 방식. 주 6회 출석과 밥·잠이 절반입니다.",
    target: "전신", equipment: "바벨+덤벨", level: "고급", muscles: ["chest", "back", "shoulders", "biceps", "legs"], exercises: ["bench_press", "incline_press", "pullup", "seated_row", "db_shoulder_press", "lateral_raise", "barbell_curl", "pushdown"], likes: 63, weeks: 8, daysPerWeek: 6, durationMin: 70, kcal: "450~600" },
  { id: "smolov", badge: "SM", title: "스모로프 Jr (벤치 특화)", desc: "3주 만에 벤치 +5~10kg",
    overview: "3주 동안 벤치프레스만 주 4회 — 6×6, 7×5, 8×4, 10×3으로 매일 다른 세트 구성. 짧고 혹독한 러시아식 단기 특화. 고급자용이며 어깨가 아프면 바로 중단, 끝나고 1주는 꼭 가볍게!",
    target: "상체", equipment: "바벨", level: "고급", muscles: ["chest", "triceps"], exercises: ["bench_press", "incline_press", "dips", "pushdown", "face_pull"], likes: 29, weeks: 3, daysPerWeek: 4, durationMin: 45, kcal: "280~380" },
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
