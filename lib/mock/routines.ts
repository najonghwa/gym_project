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
  who?: string;                // 이런 분께 추천
  schedule?: string;           // 주간 구성 요약
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
    target: "하체", equipment: "바벨", level: "중급", muscles: ["legs", "glutes"], exercises: ["back_squat", "leg_press", "rdl", "leg_ext", "leg_curl", "lunge", "calf_raise"], who: "스쿼트 후 머신으로 대퇴사두·햄스트링·둔근을 각각 조져주는 전형적인 하체 볼륨 데이. 상체는 유지만 하고 4주간 하체에 올인합니다.", schedule: "주 3회 모두 하체 — 스쿼트 중량일 / 머신 볼륨일 / 펌핑·보조일 순환", likes: 42, weeks: 4, daysPerWeek: 3, durationMin: 50, kcal: "300~420" },
  { id: "st55", badge: "ST", title: "스트롱리프트 5×5", desc: "초보 근력의 정석 A/B 루틴",
    overview: "헬스장이 처음이라 뭘 해야 할지 모르겠다면 여기서 시작하세요. 딱 5가지 운동을 5세트×5회 — 단순하지만 전 세계에서 가장 검증된 초보 근력 프로그램이에요.",
    target: "전신", equipment: "바벨", level: "초급", muscles: ["legs", "chest", "back"], exercises: ["back_squat", "bench_press", "seated_row", "db_shoulder_press", "deadlift"], who: "헬스 처음 3~6개월, 뭘 해야 할지 모르는 분. 5×5로 매번 2.5kg씩 늘리는 게 전부라 초보가 가장 빨리 강해집니다.", schedule: "A일(스쿼트·벤치·로우) / B일(스쿼트·프레스·데드) 번갈아 주 3회", likes: 128, weeks: 12, daysPerWeek: 3, durationMin: 45, kcal: "250~380" },
  { id: "ppl", badge: "PP", title: "PPL 6일 분할", desc: "밀·당·다리 주 2바퀴 고볼륨",
    overview: "미는 날·당기는 날·다리 날을 일주일에 두 바퀴 도는 고볼륨 분할. 부위당 주 2회 자극으로 성장 속도가 빠르지만, 주 6회 출석과 충분한 수면이 필요해요.",
    target: "전신", equipment: "머신+바벨", level: "중급", muscles: ["chest", "back", "legs", "shoulders"], exercises: ["bench_press", "incline_press", "lateral_raise", "pushdown", "pullup", "seated_row", "back_squat", "rdl"], who: "볼륨을 늘리고 싶은 중급자. 미는 날·당기는 날·다리 날로 나눠 한 부위를 주 2번씩 치는 검증된 분할입니다.", schedule: "월 Push / 화 Pull / 수 Legs → 목금토 반복, 일 휴식", likes: 96, weeks: 12, daysPerWeek: 6, durationMin: 65, kcal: "400~550" },
  { id: "quickfit", badge: "QF", title: "30분 전신 서킷", desc: "바쁜 날을 위한 머신 서킷",
    overview: "점심시간에 후딱 치고 나오는 머신 위주 서킷. 세팅이 빠른 머신만 써서 옷 갈아입는 시간 포함 40분 안에 끝나요. 바쁜 주간의 비상용 플랜으로도 좋아요.",
    target: "상체", equipment: "머신", level: "초급", muscles: ["chest", "back", "shoulders"], exercises: ["lat_pulldown", "leg_press", "db_bench", "seated_row", "plank"], who: "점심시간·바쁜 날용. 머신 위주 서킷이라 세팅 시간이 없고 30분에 전신을 한 바퀴 돕니다.", schedule: "주 5회 가능 — 매회 같은 5종목을 쉬는 시간 짧게 서킷으로", likes: 61, weeks: 4, daysPerWeek: 5, durationMin: 30, kcal: "180~260" },
  { id: "arms", badge: "AR", title: "팔 집중 6주", desc: "이두·삼두 집중 펌핑",
    overview: "여름 대비 팔 특화 6주. 이두·삼두를 다양한 각도로 조지는 펌핑 위주 구성이라 초보도 부담 없어요. 기존 루틴에 주 2회 얹어서 쓰는 걸 추천!",
    target: "팔", equipment: "덤벨", level: "중급", muscles: ["biceps", "triceps"], exercises: ["barbell_curl", "db_curl", "pushdown", "dips", "face_pull"], who: "팔 크기가 고민인 분. 이두·삼두를 주 2회 집중적으로 — 나머지 요일은 평소 루틴을 유지하면서 얹는 프로그램입니다.", schedule: "주 2회(예: 화·금) 팔 전용일 — 이두 2종 + 삼두 2종 + 후면어깨", likes: 55, weeks: 6, daysPerWeek: 2, durationMin: 35, kcal: "200~280" },
  // ── 유명 프로그램 (구버전 10종 복원) ──
  { id: "ss", badge: "SS", title: "스타팅 스트렝스", desc: "마크 리피토의 교과서 3×5",
    overview: "미국 초보 근력의 바이블. 스쿼트를 매 세션 하며 3세트×5회로 기본기를 다져요. 5×5보다 세트가 적어 회복이 쉬워 진짜 처음이라면 여기부터.",
    target: "전신", equipment: "바벨", level: "초급", muscles: ["legs", "chest", "back"], exercises: ["back_squat", "bench_press", "deadlift", "db_shoulder_press", "pullup"], who: "마크 리피토의 교과서. 스트롱리프트보다 세트가 적어(3×5) 회복이 쉽고, 초보 근력 기준으로 가장 검증된 프로그램.", schedule: "A일(스쿼트·프레스·데드) / B일(스쿼트·벤치·파워클린 대체) 주 3회", likes: 87, weeks: 12, daysPerWeek: 3, durationMin: 40, kcal: "230~350" },
  { id: "phul", badge: "PH", title: "PHUL 4일 분할", desc: "힘의 날 + 펌핑의 날 반반",
    overview: "상체 힘/하체 힘/상체 펌핑/하체 펌핑 — 주 4회. 앞의 이틀은 무겁게 적은 횟수, 뒤의 이틀은 가볍게 많은 횟수로 근력과 크기를 동시에 잡아요.",
    target: "전신", equipment: "바벨+머신", level: "중급", muscles: ["chest", "back", "legs", "shoulders"], exercises: ["back_squat", "deadlift", "bench_press", "seated_row", "leg_press", "incline_press", "lat_pulldown", "db_curl"], who: "근력과 근비대 둘 다 원하는 중급자. 앞 이틀은 무겁게(파워), 뒤 이틀은 가볍고 많이(펌핑) — 반반 설계입니다.", schedule: "월 상체파워 / 화 하체파워 / 목 상체펌핑 / 금 하체펌핑", likes: 74, weeks: 12, daysPerWeek: 4, durationMin: 60, kcal: "350~480" },
  { id: "gvt", badge: "GV", title: "GVT 10×10 (독일식 볼륨)", desc: "한 운동 10세트×10회, 벌크의 클래식",
    overview: "부위별 대표 운동 하나를 10세트×10회(휴식 60초). 무게는 10회 최대치의 60%로 가볍게 시작하는 게 포인트 — 6주만 해도 옷핏이 달라져요. 마지막 3세트는 지옥이 정상.",
    target: "전신", equipment: "바벨", level: "고급", muscles: ["chest", "back", "legs"], exercises: ["back_squat", "bench_press", "seated_row", "db_shoulder_press", "leg_curl", "lateral_raise"], who: "정체기 온 중·상급자용 쇼크 요법. 한 종목을 10세트×10회 — 지루하지만 볼륨 증가엔 이만한 게 없습니다.", schedule: "주 4회, 하루 메인 1종목 10×10 + 보조 2종목", likes: 45, weeks: 6, daysPerWeek: 4, durationMin: 55, kcal: "400~520" },
  { id: "five31", badge: "53", title: "5/3/1 (짐 웬들러)", desc: "4주 파도로 끝없이 강해지기",
    overview: "매주 메인 리프트 강도가 파도처럼 바뀌어요: 5·5·5 → 3·3·3 → 5·3·1 → 디로드. 이 4주 사이클을 반복하며 매 사이클 기록을 갱신하는 장기 근력 프로그램. 마지막 세트는 한계까지(AMRAP)!",
    target: "전신", equipment: "바벨", level: "중급", muscles: ["shoulders", "legs", "chest", "back"], exercises: ["back_squat", "bench_press", "deadlift", "db_shoulder_press", "pullup", "dips"], who: "짐 웬들러의 명작. 4주 파도(5회→3회→1회→디로드)로 천천히, 하지만 끝없이 강해지는 장기 프로그램.", schedule: "주 4회 — 스쿼트일/벤치일/데드일/프레스일 + 각날 보조운동", likes: 69, weeks: 16, daysPerWeek: 4, durationMin: 50, kcal: "300~430" },
  { id: "texas", badge: "TX", title: "텍사스 메소드", desc: "볼륨 → 회복 → 금요일 신기록",
    overview: "월요일은 많이(5×5 볼륨), 수요일은 가볍게(회복), 금요일은 무겁게 신기록 도전. 5×5로 정체가 왔을 때 다음 단계로 좋은 중급자 프로그램이에요.",
    target: "전신", equipment: "바벨", level: "중급", muscles: ["legs", "chest", "shoulders"], exercises: ["back_squat", "bench_press", "deadlift", "db_shoulder_press", "seated_row"], who: "초보 프로그램 졸업자. 월요일 볼륨으로 자극 → 수요일 가볍게 회복 → 금요일 5회 신기록 도전 구조입니다.", schedule: "월 볼륨(5×5 90%) / 수 회복(80%) / 금 신기록(1×5)", likes: 38, weeks: 12, daysPerWeek: 3, durationMin: 55, kcal: "320~450" },
  { id: "bro", badge: "BR", title: "브로 스플릿 5분할", desc: "하루 한 부위, 헬스장의 클래식",
    overview: "가슴/등/어깨/하체/팔을 하루 하나씩 조지는 전통 보디빌딩 방식. 부위당 볼륨이 커서 펌핑 맛이 확실하고, 한 부위는 일주일을 쉬어 회복 걱정이 없어요.",
    target: "전신", equipment: "바벨+머신", level: "중급", muscles: ["chest", "back", "shoulders", "legs", "biceps"], exercises: ["bench_press", "cable_fly", "lat_pulldown", "db_shoulder_press", "lateral_raise", "back_squat", "barbell_curl", "pushdown"], who: "하루 한 부위만 조지는 클래식 보디빌딩 분할. 부위당 볼륨이 많아 펌핑감이 확실합니다.", schedule: "월 가슴 / 화 등 / 수 어깨 / 목 하체 / 금 팔", likes: 91, weeks: 8, daysPerWeek: 5, durationMin: 60, kcal: "380~500" },
  { id: "arnold", badge: "AN", title: "아놀드 스플릿", desc: "아놀드의 3분할 × 주 2바퀴",
    overview: "가슴·등 / 어깨·팔 / 하체를 일주일에 두 바퀴 도는 고볼륨 분할. 부위당 주 2회 자극 — 아놀드를 미스터 올림피아로 만든 방식. 주 6회 출석과 밥·잠이 절반입니다.",
    target: "전신", equipment: "바벨+덤벨", level: "고급", muscles: ["chest", "back", "shoulders", "biceps", "legs"], exercises: ["bench_press", "incline_press", "pullup", "seated_row", "db_shoulder_press", "lateral_raise", "barbell_curl", "pushdown"], who: "아놀드가 실제로 쓰던 3분할×주2회. 볼륨이 상당해서 회복 관리가 되는 상급자에게 맞습니다.", schedule: "가슴·등 / 어깨·팔 / 하체 3분할을 월~토 두 바퀴", likes: 63, weeks: 8, daysPerWeek: 6, durationMin: 70, kcal: "450~600" },
  { id: "smolov", badge: "SM", title: "스모로프 Jr (벤치 특화)", desc: "3주 만에 벤치 +5~10kg",
    overview: "3주 동안 벤치프레스만 주 4회 — 6×6, 7×5, 8×4, 10×3으로 매일 다른 세트 구성. 짧고 혹독한 러시아식 단기 특화. 고급자용이며 어깨가 아프면 바로 중단, 끝나고 1주는 꼭 가볍게!",
    target: "상체", equipment: "바벨", level: "고급", muscles: ["chest", "triceps"], exercises: ["bench_press", "incline_press", "dips", "pushdown", "face_pull"], who: "벤치 정체 뚫기 특화. 3주간 벤치 빈도를 주 4회로 끌어올려 단기간에 5~10kg 증량을 노립니다.", schedule: "주 4회 벤치(6×6→10×3 등 파도) + 보조 삼두·어깨", likes: 29, weeks: 3, daysPerWeek: 4, durationMin: 45, kcal: "280~380" },
  // ── 추가 유명 프로그램 (웹 리서치) ──
  { id: "upperlower", badge: "UL", title: "상·하체 4분할", desc: "부위당 주 2회, 가장 무난한 분할",
    overview: "한 주를 상체·하체로 나눠 각 부위를 주 2번씩 자극해요. 볼륨과 회복의 균형이 가장 좋아서 오래 지속하기 좋은, 실패 없는 중급 4분할입니다.",
    target: "전신", equipment: "바벨+머신", level: "중급", muscles: ["chest", "back", "legs", "shoulders"], exercises: ["back_squat", "rdl", "leg_press", "bench_press", "seated_row", "db_shoulder_press", "lat_pulldown", "calf_raise"], who: "초보 프로그램을 졸업한 중급자. 부위당 주 2회로 성장 자극은 충분하면서 회복도 되는 가장 무난한 선택.", schedule: "월 상체 / 화 하체 / 목 상체 / 금 하체", likes: 112, weeks: 12, daysPerWeek: 4, durationMin: 55, kcal: "350~480" },
  { id: "fullbody3", badge: "FB", title: "전신 3분할", desc: "주 3회, 매번 전신 — 초보·바쁜 사람",
    overview: "한 세션에 전신을 다 치는 방식. 큰 운동을 자주 반복해 폼과 근력이 가장 빨리 늘어요. 주 2~3회밖에 못 오는 분에게 최고의 가성비 루틴.",
    target: "전신", equipment: "바벨+머신", level: "초급", muscles: ["legs", "chest", "back"], exercises: ["back_squat", "bench_press", "seated_row", "db_shoulder_press", "rdl", "plank"], who: "헬스 입문자, 주 2~3회만 가능한 분. 매 세션 전신을 돌려 부족한 빈도를 채웁니다.", schedule: "주 3회(월·수·금) 매번 전신 — 하체·밀기·당기기·코어", likes: 134, weeks: 8, daysPerWeek: 3, durationMin: 50, kcal: "280~400" },
  { id: "phat", badge: "PT", title: "PHAT 파워빌딩", desc: "레인 노튼 — 파워 2일 + 펌핑 3일",
    overview: "레인 노튼 박사의 파워빌딩. 앞 2일은 무겁게(파워 3~5회), 뒤 3일은 부위별 고볼륨(펌핑 8~20회). 근력과 크기를 동시에 잡는 상급자용 5일 프로그램.",
    target: "전신", equipment: "바벨+머신", level: "고급", muscles: ["chest", "back", "legs", "shoulders"], exercises: ["back_squat", "deadlift", "bench_press", "seated_row", "leg_press", "incline_press", "lat_pulldown", "lateral_raise", "db_curl", "pushdown"], who: "힘도 크기도 놓치기 싫은 상급자. 주 5회를 소화하고 회복 관리가 되는 분에게 맞아요.", schedule: "월 상체파워 / 화 하체파워 / 목 등·어깨 / 금 하체 / 토 가슴·팔", likes: 98, weeks: 12, daysPerWeek: 5, durationMin: 65, kcal: "420~560" },
  { id: "madcow", badge: "MC", title: "매드카우 5×5", desc: "스트롱리프트 다음 단계 · 주간 파동",
    overview: "5×5가 정체됐을 때 넘어가는 중급 근력 프로그램. 무겁게→가볍게→중간(HLM) 주 3회로 돌리고, 금요일에 세트마다 무게를 올려 신기록에 도전해요.",
    target: "전신", equipment: "바벨", level: "중급", muscles: ["legs", "chest", "back"], exercises: ["back_squat", "bench_press", "seated_row", "incline_press", "deadlift"], who: "스트롱리프트 선형진행이 막힌 중급자. 주간 파동으로 회복을 주며 계속 강해집니다.", schedule: "월 헤비 / 수 라이트 / 금 미디엄(신기록) — 램핑 5×5", likes: 76, weeks: 12, daysPerWeek: 3, durationMin: 55, kcal: "320~450" },
  { id: "supersquat", badge: "SQ", title: "슈퍼 스쿼트 20렙", desc: "한 세트 20회 스쿼트 · 전설의 벌크",
    overview: "한 세트 20회 스쿼트로 몸 전체를 뒤흔드는 전설의 벌크 프로그램. 6주만 버티면 체중과 근육이 확 늘어요. 숨쉬기 스쿼트는 정신력 싸움 — 각오가 필요합니다.",
    target: "하체", equipment: "바벨", level: "고급", muscles: ["legs", "glutes", "chest"], exercises: ["back_squat", "leg_press", "rdl", "bench_press", "pullup", "calf_raise"], who: "마르고 체중이 안 느는 하드게이너, 정체기 돌파용. 20렙 스쿼트를 버틸 각오가 있다면.", schedule: "주 3회 — 20렙 스쿼트 1세트 + 상체 보조, 매 세션 2.5kg 증량", likes: 54, weeks: 6, daysPerWeek: 3, durationMin: 45, kcal: "400~550" },
  { id: "icf", badge: "IC", title: "ICF 5×5", desc: "아이스크림 피트니스 · 초보 보디빌딩",
    overview: "스트롱리프트에 팔·보조 운동을 더한 초보 보디빌딩 5×5. 근력과 함께 팔·등 디테일까지 챙겨서, 근력만이 아니라 보기 좋은 몸을 원하는 초보에게 딱이에요.",
    target: "전신", equipment: "바벨+덤벨", level: "초급", muscles: ["chest", "back", "legs", "biceps"], exercises: ["back_squat", "bench_press", "seated_row", "barbell_curl", "pushdown", "lat_pulldown", "db_shoulder_press", "calf_raise"], who: "근력만이 아니라 팔·등 디테일도 원하는 초보. SL보다 종목이 많아 지루하지 않아요.", schedule: "A일/B일 번갈아 주 3회 — 5×5 메인 + 컬·푸시다운 3×8 보조", likes: 89, weeks: 12, daysPerWeek: 3, durationMin: 50, kcal: "300~430" },
  // ── 무난한 부위 분할 (3·4·5분할) ──
  { id: "split3", badge: "3분", title: "3분할 루틴", desc: "가슴·등 / 어깨·팔 / 하체 — 부담 없는 부위 분할",
    overview: "몸을 세 그룹으로 나눠 주 3회. 부위별로 충분히 집중하면서도 주 3회라 부담이 적어, 전신 루틴을 졸업한 초·중급이 처음 분할을 시작하기 가장 무난한 구성이에요.",
    target: "전신", equipment: "바벨+머신", level: "중급", muscles: ["chest", "back", "legs", "shoulders"], exercises: ["bench_press", "seated_row", "db_shoulder_press", "barbell_curl", "back_squat", "rdl"], who: "전신 루틴을 졸업하고 부위 분할을 처음 시작하는 분. 주 3회로 회복 부담 없이 부위 집중을 맛봅니다.", schedule: "월 가슴·등 / 수 어깨·팔 / 금 하체", likes: 118, weeks: 12, daysPerWeek: 3, durationMin: 55, kcal: "320~450" },
  { id: "split4", badge: "4분", title: "4분할 루틴", desc: "가슴 / 등 / 어깨·팔 / 하체 — 부위별 집중",
    overview: "가슴·등·어깨팔·하체를 각각 하루씩 담당해요. 부위당 볼륨을 넉넉히 실어 근비대에 유리한, 헬스장에서 가장 흔하고 검증된 4분할입니다.",
    target: "전신", equipment: "바벨+머신", level: "중급", muscles: ["chest", "back", "shoulders", "legs"], exercises: ["bench_press", "incline_press", "lat_pulldown", "seated_row", "db_shoulder_press", "lateral_raise", "back_squat", "leg_press"], who: "부위별로 파고들고 싶은 중급자. 주 4회 규칙적으로 올 수 있으면 성장 자극이 확실해요.", schedule: "월 가슴 / 화 등 / 목 어깨·팔 / 금 하체", likes: 126, weeks: 12, daysPerWeek: 4, durationMin: 60, kcal: "360~500" },
  { id: "split5", badge: "5분", title: "5분할 루틴", desc: "가슴 / 등 / 어깨 / 팔 / 하체 — 부위당 최대 볼륨",
    overview: "하루 한 부위만 집중하는 클래식 5분할. 부위당 볼륨이 가장 많아 펌핑감이 확실하고, 주 5회 규칙적으로 나오는 사람에게 최고의 근비대 구성이에요.",
    target: "전신", equipment: "바벨+머신", level: "중급", muscles: ["chest", "back", "shoulders", "biceps", "legs"], exercises: ["bench_press", "cable_fly", "lat_pulldown", "seated_row", "db_shoulder_press", "lateral_raise", "barbell_curl", "pushdown", "back_squat", "leg_curl"], who: "부위 하나에 몰아서 조지고 싶은 중급 이상. 주 5회 소화 가능하고 각 부위를 주 1회로 충분히 회복하는 분.", schedule: "월 가슴 / 화 등 / 수 어깨 / 목 팔 / 금 하체", likes: 103, weeks: 8, daysPerWeek: 5, durationMin: 60, kcal: "380~520" },
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
