// 유명 트레이닝 프로그램 — 우리 헬스장 장비(data.js의 운동 id)로 재구성한 버전
// it = {exId, sets, reps, rest(초)}  · waves = 주차별 반복 라벨(있으면 주기 표시)
window.PROGRAMS = (function () {

  const PROGRAMS = [
    {
      id: "stronglifts", name: "스트롱리프트 5×5", emoji: "🔩",
      weeks: 12, daysPerWeek: 3, level: "초급~중급", goal: "근력",
      easy: "세계에서 가장 유명한 초보 근력 프로그램",
      desc: "딱 5가지 운동을 5세트×5회씩. A/B 두 루틴을 번갈아 주 3회. 매 세션 무게를 조금씩(2.5kg) 올리는 게 핵심 — 단순한데 확실하게 강해져요.",
      tip: "5회×5세트가 전부 성공하면 다음 세션에 무게 +2.5kg. 실패하면 같은 무게 유지.",
      week: [
        { name: "A 루틴", items: [
          { exId: "back_squat", sets: 5, reps: "5", rest: 180 },
          { exId: "bench_press", sets: 5, reps: "5", rest: 180 },
          { exId: "db_row", sets: 5, reps: "5", rest: 180 },
        ] },
        { name: "B 루틴", items: [
          { exId: "back_squat", sets: 5, reps: "5", rest: 180 },
          { exId: "db_shoulder_press", sets: 5, reps: "5", rest: 180 },
          { exId: "deadlift", sets: 1, reps: "5", rest: 180 },
        ] },
      ],
    },
    {
      id: "ppl", name: "PPL 6일 분할", emoji: "🔁",
      weeks: 12, daysPerWeek: 6, level: "중급", goal: "근비대+근력",
      easy: "레딧에서 가장 사랑받는 밀·당·다리 프로그램",
      desc: "미는 날(가슴·어깨·삼두) → 당기는 날(등·이두) → 다리 날을 일주일에 두 바퀴. 볼륨이 많아 성장이 빠르지만 주 6회 출석이 필요해요.",
      tip: "주 6회가 부담이면 주 3회(한 바퀴)로 시작해도 좋아요.",
      week: [
        { name: "Push (미는 날)", items: [
          { exId: "bench_press", sets: 5, reps: "5", rest: 180 },
          { exId: "db_shoulder_press", sets: 3, reps: "8-12", rest: 90 },
          { exId: "incline_db_press", sets: 3, reps: "8-12", rest: 90 },
          { exId: "cable_pushdown", sets: 3, reps: "8-12", rest: 90 },
          { exId: "lateral_raise", sets: 3, reps: "15", rest: 60 },
        ] },
        { name: "Pull (당기는 날)", items: [
          { exId: "deadlift", sets: 1, reps: "5", rest: 180 },
          { exId: "lat_pulldown", sets: 3, reps: "8-12", rest: 90 },
          { exId: "seated_row_m", sets: 3, reps: "8-12", rest: 90 },
          { exId: "face_pull", sets: 3, reps: "15", rest: 60 },
          { exId: "barbell_curl", sets: 3, reps: "8-12", rest: 60 },
        ] },
        { name: "Legs (다리 날)", items: [
          { exId: "back_squat", sets: 5, reps: "5", rest: 180 },
          { exId: "romanian_dl", sets: 3, reps: "8-12", rest: 120 },
          { exId: "leg_press", sets: 3, reps: "8-12", rest: 90 },
          { exId: "leg_curl", sets: 3, reps: "8-12", rest: 90 },
          { exId: "calf_raise_m", sets: 5, reps: "15", rest: 60 },
        ] },
      ],
    },
    {
      id: "phul", name: "PHUL 4일 분할", emoji: "⚖️",
      weeks: 12, daysPerWeek: 4, level: "중급", goal: "근력+근비대",
      easy: "힘의 날 + 펌핑의 날을 반반 섞은 균형 프로그램",
      desc: "상체 힘 / 하체 힘 / 상체 펌핑 / 하체 펌핑 — 주 4회. 앞의 이틀은 무겁게 적은 횟수, 뒤의 이틀은 가볍게 많은 횟수로 근력과 크기를 동시에.",
      tip: "힘의 날(Power)은 휴식 길게(3분), 펌핑의 날(Hypertrophy)은 짧게(1분~90초).",
      week: [
        { name: "상체 힘 (Power)", items: [
          { exId: "bench_press", sets: 4, reps: "3-5", rest: 180 },
          { exId: "db_row", sets: 4, reps: "3-5", rest: 180 },
          { exId: "db_shoulder_press", sets: 3, reps: "6-8", rest: 120 },
          { exId: "lat_pulldown", sets: 3, reps: "6-8", rest: 120 },
          { exId: "barbell_curl", sets: 3, reps: "8-10", rest: 90 },
        ] },
        { name: "하체 힘 (Power)", items: [
          { exId: "back_squat", sets: 4, reps: "3-5", rest: 180 },
          { exId: "deadlift", sets: 3, reps: "3-5", rest: 180 },
          { exId: "leg_press", sets: 4, reps: "10", rest: 120 },
          { exId: "leg_curl", sets: 4, reps: "10", rest: 90 },
          { exId: "calf_raise_m", sets: 4, reps: "12", rest: 60 },
        ] },
        { name: "상체 펌핑 (Hyper)", items: [
          { exId: "incline_db_press", sets: 4, reps: "10-12", rest: 90 },
          { exId: "cable_fly", sets: 4, reps: "12", rest: 60 },
          { exId: "seated_row_m", sets: 4, reps: "10-12", rest: 90 },
          { exId: "lateral_raise", sets: 4, reps: "12-15", rest: 60 },
          { exId: "db_curl", sets: 4, reps: "12", rest: 60 },
          { exId: "lying_tri_ext", sets: 4, reps: "12", rest: 60 },
        ] },
        { name: "하체 펌핑 (Hyper)", items: [
          { exId: "db_lunge", sets: 4, reps: "10-12", rest: 90 },
          { exId: "romanian_dl", sets: 4, reps: "10-12", rest: 90 },
          { exId: "leg_ext", sets: 4, reps: "15", rest: 60 },
          { exId: "leg_curl", sets: 4, reps: "15", rest: 60 },
          { exId: "calf_raise_m", sets: 4, reps: "15", rest: 60 },
        ] },
      ],
    },
    {
      id: "gvt", name: "GVT 10×10 (독일식 볼륨)", emoji: "🇩🇪",
      weeks: 6, daysPerWeek: 4, level: "중~고급", goal: "근비대(벌크)",
      easy: "한 운동을 10세트×10회 — 미친 볼륨으로 몸을 키우는 클래식",
      desc: "부위별 대표 운동 하나를 10세트×10회(60초 휴식). 무게는 10회 가능한 최대치의 60% 정도로 가볍게 시작하는 게 포인트. 6주만 해도 옷이 달라져요.",
      tip: "10×10은 처음엔 꼭 가벼운 무게로! 마지막 3세트가 지옥 같으면 정상이에요.",
      week: [
        { name: "가슴 · 등", items: [
          { exId: "bench_press", sets: 10, reps: "10", rest: 60 },
          { exId: "db_row", sets: 10, reps: "10", rest: 60 },
          { exId: "cable_fly", sets: 3, reps: "12", rest: 60 },
          { exId: "face_pull", sets: 3, reps: "12", rest: 60 },
        ] },
        { name: "하체 · 복근", items: [
          { exId: "back_squat", sets: 10, reps: "10", rest: 60 },
          { exId: "leg_curl", sets: 10, reps: "10", rest: 60 },
          { exId: "calf_raise_m", sets: 3, reps: "15", rest: 60 },
          { exId: "crunch", sets: 3, reps: "20", rest: 45 },
        ] },
        { name: "어깨", items: [
          { exId: "db_shoulder_press", sets: 10, reps: "10", rest: 60 },
          { exId: "lateral_raise", sets: 3, reps: "15", rest: 60 },
          { exId: "face_pull", sets: 3, reps: "15", rest: 60 },
        ] },
        { name: "팔", items: [
          { exId: "barbell_curl", sets: 10, reps: "10", rest: 60 },
          { exId: "cable_pushdown", sets: 10, reps: "10", rest: 60 },
          { exId: "hanging_leg_raise", sets: 3, reps: "15", rest: 60 },
        ] },
      ],
    },
    {
      id: "five31", name: "5/3/1 (짐 웬들러)", emoji: "🌊",
      weeks: 16, daysPerWeek: 4, level: "중급", goal: "근력(장기)",
      easy: "4주 파도를 타며 천천히, 그러나 끝없이 강해지는 프로그램",
      desc: "매주 메인 리프트의 강도가 파도처럼 바뀌어요: 5·5·5 → 3·3·3 → 5·3·1 → 가볍게(디로드). 이 4주 사이클을 반복하며 매 사이클 기록을 갱신합니다.",
      tip: "마지막 세트는 '할 수 있는 만큼 최대한(AMRAP)'! 거기서 기록이 자랍니다.",
      waves: ["5·5·5 주", "3·3·3 주", "5·3·1 주", "디로드(가볍게) 주"],
      week: [
        { name: "어깨(OHP) 날", items: [
          { exId: "db_shoulder_press", sets: 3, reps: "5/3/1", rest: 180 },
          { exId: "dips", sets: 5, reps: "10", rest: 90 },
          { exId: "lateral_raise", sets: 5, reps: "12", rest: 60 },
        ] },
        { name: "데드리프트 날", items: [
          { exId: "deadlift", sets: 3, reps: "5/3/1", rest: 180 },
          { exId: "leg_curl", sets: 5, reps: "10", rest: 90 },
          { exId: "hanging_leg_raise", sets: 5, reps: "10", rest: 60 },
        ] },
        { name: "벤치 날", items: [
          { exId: "bench_press", sets: 3, reps: "5/3/1", rest: 180 },
          { exId: "db_row", sets: 5, reps: "10", rest: 90 },
          { exId: "cable_pushdown", sets: 5, reps: "12", rest: 60 },
        ] },
        { name: "스쿼트 날", items: [
          { exId: "back_squat", sets: 3, reps: "5/3/1", rest: 180 },
          { exId: "leg_press", sets: 5, reps: "10", rest: 90 },
          { exId: "crunch", sets: 5, reps: "15", rest: 60 },
        ] },
      ],
    },
    {
      id: "ss", name: "스타팅 스트렝스", emoji: "📗",
      weeks: 12, daysPerWeek: 3, level: "초급", goal: "근력(기초)",
      easy: "마크 리피토의 교과서 — 미국 초보 근력의 바이블",
      desc: "스쿼트를 매 세션 하며 3세트×5회로 기본기를 다지는 프로그램. 5×5보다 세트가 적어 회복이 쉬워요. A/B 루틴을 번갈아 주 3회.",
      tip: "무게보다 자세! 처음 2주는 빈 바로 자세 연습을 해도 아깝지 않아요.",
      week: [
        { name: "A 루틴", items: [
          { exId: "back_squat", sets: 3, reps: "5", rest: 180 },
          { exId: "bench_press", sets: 3, reps: "5", rest: 180 },
          { exId: "deadlift", sets: 1, reps: "5", rest: 180 },
        ] },
        { name: "B 루틴", items: [
          { exId: "back_squat", sets: 3, reps: "5", rest: 180 },
          { exId: "db_shoulder_press", sets: 3, reps: "5", rest: 180 },
          { exId: "db_row", sets: 3, reps: "5", rest: 120 },
        ] },
      ],
    },
    {
      id: "texas", name: "텍사스 메소드", emoji: "🤠",
      weeks: 12, daysPerWeek: 3, level: "중급", goal: "근력(정체 돌파)",
      easy: "볼륨 → 회복 → 신기록, 일주일이 한 사이클",
      desc: "월요일은 많이(볼륨), 수요일은 가볍게(회복), 금요일은 무겁게 신기록 도전(강도). 5×5로 정체가 왔을 때 다음 단계로 좋은 프로그램.",
      tip: "금요일 강도일의 1세트가 이 프로그램의 전부 — 앞 이틀은 그날을 위한 준비예요.",
      week: [
        { name: "볼륨 데이", items: [
          { exId: "back_squat", sets: 5, reps: "5", rest: 180 },
          { exId: "bench_press", sets: 5, reps: "5", rest: 180 },
          { exId: "romanian_dl", sets: 3, reps: "8", rest: 120 },
        ] },
        { name: "회복 데이 (가볍게)", items: [
          { exId: "back_squat", sets: 2, reps: "5 (80%)", rest: 120 },
          { exId: "db_shoulder_press", sets: 3, reps: "5", rest: 120 },
          { exId: "pullup", sets: 3, reps: "10", rest: 90 },
          { exId: "crunch", sets: 3, reps: "15", rest: 60 },
        ] },
        { name: "강도 데이 (신기록!)", items: [
          { exId: "back_squat", sets: 1, reps: "5 (최대)", rest: 300 },
          { exId: "bench_press", sets: 1, reps: "5 (최대)", rest: 300 },
          { exId: "deadlift", sets: 1, reps: "5 (최대)", rest: 300 },
        ] },
      ],
    },
    {
      id: "bro", name: "브로 스플릿 5분할", emoji: "😎",
      weeks: 8, daysPerWeek: 5, level: "중급", goal: "근비대(클래식)",
      easy: "하루 한 부위 집중 — 헬스장의 클래식",
      desc: "가슴/등/어깨/하체/팔을 하루 하나씩 조지는 전통 보디빌딩 방식. 부위당 볼륨이 커서 펌핑 맛이 확실해요.",
      tip: "한 부위를 일주일에 한 번만 치기 때문에 그날 확실히 조져야(!) 해요.",
      week: [
        { name: "가슴", items: [
          { exId: "bench_press", sets: 4, reps: "8-12", rest: 120 },
          { exId: "incline_db_press", sets: 4, reps: "8-12", rest: 90 },
          { exId: "chest_press_m", sets: 3, reps: "10-12", rest: 90 },
          { exId: "cable_fly", sets: 3, reps: "12-15", rest: 60 },
        ] },
        { name: "등", items: [
          { exId: "deadlift", sets: 3, reps: "5", rest: 180 },
          { exId: "lat_pulldown", sets: 4, reps: "8-12", rest: 90 },
          { exId: "seated_row_m", sets: 4, reps: "10", rest: 90 },
          { exId: "face_pull", sets: 3, reps: "15", rest: 60 },
        ] },
        { name: "어깨", items: [
          { exId: "db_shoulder_press", sets: 4, reps: "8-12", rest: 120 },
          { exId: "shoulder_press_m", sets: 3, reps: "10", rest: 90 },
          { exId: "lateral_raise", sets: 4, reps: "12-15", rest: 60 },
          { exId: "face_pull", sets: 3, reps: "15", rest: 60 },
        ] },
        { name: "하체", items: [
          { exId: "back_squat", sets: 4, reps: "8-10", rest: 180 },
          { exId: "leg_press", sets: 4, reps: "10-12", rest: 120 },
          { exId: "leg_ext", sets: 3, reps: "12", rest: 60 },
          { exId: "leg_curl", sets: 3, reps: "12", rest: 60 },
          { exId: "calf_raise_m", sets: 4, reps: "15", rest: 60 },
        ] },
        { name: "팔", items: [
          { exId: "barbell_curl", sets: 4, reps: "10", rest: 90 },
          { exId: "cable_pushdown", sets: 4, reps: "10", rest: 90 },
          { exId: "db_curl", sets: 3, reps: "12", rest: 60 },
          { exId: "lying_tri_ext", sets: 3, reps: "12", rest: 60 },
          { exId: "dips", sets: 3, reps: "10", rest: 90 },
        ] },
      ],
    },
    {
      id: "arnold", name: "아놀드 스플릿", emoji: "🦾",
      weeks: 8, daysPerWeek: 6, level: "중~고급", goal: "근비대(고볼륨)",
      easy: "아놀드 슈워제네거가 했던 3분할 ×2바퀴",
      desc: "가슴·등 / 어깨·팔 / 하체를 일주일에 두 바퀴. 부위당 주 2회 자극 + 미친 볼륨으로 아놀드가 미스터 올림피아를 만든 방식.",
      tip: "주 6회는 진짜 힘들어요. 잠과 밥이 프로그램의 절반입니다.",
      week: [
        { name: "가슴 · 등", items: [
          { exId: "bench_press", sets: 4, reps: "8-12", rest: 120 },
          { exId: "incline_db_press", sets: 3, reps: "10", rest: 90 },
          { exId: "pullup", sets: 4, reps: "10", rest: 90 },
          { exId: "db_row", sets: 3, reps: "10", rest: 90 },
          { exId: "cable_fly", sets: 3, reps: "12", rest: 60 },
        ] },
        { name: "어깨 · 팔", items: [
          { exId: "db_shoulder_press", sets: 4, reps: "8-12", rest: 120 },
          { exId: "lateral_raise", sets: 4, reps: "12", rest: 60 },
          { exId: "barbell_curl", sets: 4, reps: "10", rest: 60 },
          { exId: "lying_tri_ext", sets: 4, reps: "10", rest: 60 },
          { exId: "dips", sets: 3, reps: "10", rest: 90 },
        ] },
        { name: "하체 · 코어", items: [
          { exId: "back_squat", sets: 4, reps: "8-12", rest: 180 },
          { exId: "romanian_dl", sets: 3, reps: "10", rest: 120 },
          { exId: "db_lunge", sets: 3, reps: "12", rest: 90 },
          { exId: "calf_raise_m", sets: 4, reps: "15", rest: 60 },
          { exId: "crunch", sets: 4, reps: "20", rest: 45 },
        ] },
      ],
    },
    {
      id: "smolov", name: "스모로프 Jr (벤치 특화)", emoji: "🚀",
      weeks: 3, daysPerWeek: 4, level: "고급", goal: "벤치 중량 급상승",
      easy: "3주 만에 벤치프레스를 폭발시키는 러시아식 단기 특화",
      desc: "3주 동안 벤치프레스만 주 4회 — 6×6, 7×5, 8×4, 10×3으로 매일 다른 세트 구성. 짧고 혹독하지만 벤치 기록이 5~10kg 뛰는 걸로 유명해요.",
      tip: "고급자용! 어깨가 아프면 바로 중단하세요. 3주 끝나고 1주는 꼭 가볍게.",
      week: [
        { name: "6세트 × 6회 (70%)", items: [
          { exId: "bench_press", sets: 6, reps: "6", rest: 180 },
          { exId: "face_pull", sets: 3, reps: "15", rest: 60 },
        ] },
        { name: "7세트 × 5회 (75%)", items: [
          { exId: "bench_press", sets: 7, reps: "5", rest: 180 },
          { exId: "cable_row", sets: 3, reps: "12", rest: 60 },
        ] },
        { name: "8세트 × 4회 (80%)", items: [
          { exId: "bench_press", sets: 8, reps: "4", rest: 180 },
          { exId: "face_pull", sets: 3, reps: "15", rest: 60 },
        ] },
        { name: "10세트 × 3회 (85%)", items: [
          { exId: "bench_press", sets: 10, reps: "3", rest: 180 },
          { exId: "cable_pushdown", sets: 3, reps: "12", rest: 60 },
        ] },
      ],
    },
  ];

  // 프로그램 → 앱 루틴 형식으로 변환
  function toRoutine(pg, today) {
    const D = window.DATA;
    return {
      style: "power", styleName: pg.name, level: "intermediate",
      days: pg.daysPerWeek, split: "program", splitName: pg.name,
      programWeeks: pg.weeks, startDate: today, programId: pg.id,
      summary: `${pg.emoji} ${pg.name} · 주 ${pg.daysPerWeek}회 · ${pg.weeks}주`,
      week: pg.week.map((d, i) => ({
        day: i + 1, type: "program", typeKr: d.name,
        items: d.items.map((it) => {
          const ex = D.byId(it.exId) || {};
          return { exId: it.exId, name: ex.name || it.exId, zone: ex.zone || "?",
            equipment: ex.equipment || "", target: (ex.primary || []).map((m) => D.MUSCLE_KR[m]),
            kind: ex.kind || "reps", sets: it.sets, reps: it.reps, rest: it.rest || 90 };
        }),
      })),
    };
  }

  return { LIST: PROGRAMS, byId: (id) => PROGRAMS.find((p) => p.id === id), toRoutine };
})();
