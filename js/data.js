// 회사 헬스장 데이터 — 장비 / 평면도 좌표 / 운동 스타일 / 분할 정의
// 실제 회사 헬스장 정보를 받으면 ZONES / FLOOR / EQUIP_INFO / EXERCISES 만 교체하면 됩니다.
window.DATA = (function () {

  const MUSCLE_KR = {
    chest: "가슴", back: "등", shoulders: "어깨", biceps: "이두", triceps: "삼두",
    quads: "허벅지앞", hamstrings: "허벅지뒤", glutes: "엉덩이", calves: "종아리",
    core: "코어", cardio: "유산소",
  };

  const ZONES = [
    { id: "A", name: "프리웨이트존", desc: "파워랙 / 벤치 / 덤벨 / 바벨", color: "#34d399" },
    { id: "B", name: "머신존", desc: "웨이트 머신 8대", color: "#60a5fa" },
    { id: "C", name: "케이블존", desc: "케이블 머신", color: "#c084fc" },
    { id: "D", name: "유산소존", desc: "트레드밀 / 사이클 / 로잉", color: "#fbbf24" },
    { id: "E", name: "코어존", desc: "매트 / 코어기구", color: "#f87171" },
  ];

  // ── 평면도(SVG viewBox 0 0 400 310) — 구역 사각형 ──
  const FLOOR_ZONES = [
    { id: "A", x: 8,   y: 8,   w: 184, h: 158 },
    { id: "B", x: 200, y: 8,   w: 192, h: 118 },
    { id: "C", x: 200, y: 134, w: 192, h: 74 },
    { id: "D", x: 200, y: 216, w: 192, h: 86 },
    { id: "E", x: 8,   y: 174, w: 184, h: 128 },
  ];

  // ── 평면도 장비 배치 (eq = EXERCISES.equipment 와 동일 문자열) ──
  const FLOOR = [
    { eq: "파워랙",           zone: "A", x: 45,  y: 46,  icon: "🏗️" },
    { eq: "벤치프레스대",      zone: "A", x: 100, y: 46,  icon: "🛏️" },
    { eq: "풀업바",           zone: "A", x: 155, y: 46,  icon: "🙌" },
    { eq: "덤벨세트",          zone: "A", x: 45,  y: 105, icon: "🏋️" },
    { eq: "바벨/벤치",         zone: "A", x: 100, y: 105, icon: "➖" },
    { eq: "EZ바",             zone: "A", x: 155, y: 105, icon: "〰️" },
    { eq: "딥스대",           zone: "A", x: 100, y: 145, icon: "🇭" },
    { eq: "레그프레스 머신",    zone: "B", x: 228, y: 44,  icon: "🦵" },
    { eq: "랫풀다운 머신",     zone: "B", x: 272, y: 44,  icon: "⬇️" },
    { eq: "체스트프레스 머신",  zone: "B", x: 316, y: 44,  icon: "🫸" },
    { eq: "시티드로우 머신",    zone: "B", x: 360, y: 44,  icon: "🚣" },
    { eq: "레그익스텐션 머신",  zone: "B", x: 228, y: 96,  icon: "🦿" },
    { eq: "레그컬 머신",       zone: "B", x: 272, y: 96,  icon: "🪝" },
    { eq: "숄더프레스 머신",    zone: "B", x: 316, y: 96,  icon: "🙆" },
    { eq: "카프레이즈 머신",    zone: "B", x: 360, y: 96,  icon: "🦶" },
    { eq: "케이블 머신",       zone: "C", x: 252, y: 172, icon: "🔗" },
    { eq: "케이블 크로스오버",  zone: "C", x: 336, y: 172, icon: "✖️" },
    { eq: "트레드밀",          zone: "D", x: 228, y: 258, icon: "🏃" },
    { eq: "사이클",           zone: "D", x: 272, y: 258, icon: "🚴" },
    { eq: "로잉머신",          zone: "D", x: 316, y: 258, icon: "🛶" },
    { eq: "일립티컬",          zone: "D", x: 360, y: 258, icon: "⛷️" },
    { eq: "매트",             zone: "E", x: 50,  y: 235, icon: "🧘" },
    { eq: "캡틴체어",          zone: "E", x: 105, y: 235, icon: "🪑" },
    { eq: "앱롤러",           zone: "E", x: 158, y: 235, icon: "🛞" },
  ];

  // ── 장비 정보(평면도에서 눌렀을 때) ──
  const EQUIP_INFO = {
    "파워랙":          { desc: "스쿼트·데드리프트 등 바벨 운동의 본진. 안전바가 있어 혼자서도 안전하게.", tip: "안전바를 가슴 아래 높이로 맞추면 실패해도 다치지 않아요." },
    "벤치프레스대":     { desc: "가슴 운동의 대표 장비. 바벨을 눕혀서 밀어 올립니다.", tip: "어깨를 뒤로 모으고(견갑 고정) 발로 바닥을 단단히 눌러요." },
    "풀업바":          { desc: "턱걸이용 철봉. 맨몸 등 운동의 왕.", tip: "안 되면 밴드를 걸거나 점프해서 버티며 내려오는 것부터." },
    "덤벨세트":        { desc: "2~40kg 덤벨. 프레스·로우·컬 등 못 하는 운동이 없는 만능 도구.", tip: "쓰고 나면 제자리에! 다음 사람과 미래의 나를 위해." },
    "바벨/벤치":       { desc: "루마니안 데드리프트·힙쓰러스트 등 바벨 프리 운동 공간.", tip: "허리가 굽지 않게, 엉덩이를 뒤로 미는 느낌으로." },
    "EZ바":           { desc: "물결 모양 바. 손목 부담 없이 컬·삼두 운동.", tip: "팔꿈치를 몸통에 고정하면 이두에 자극이 집중돼요." },
    "딥스대":          { desc: "평행봉. 삼두·가슴 하부를 만드는 맨몸 운동 기구.", tip: "몸을 앞으로 기울이면 가슴, 세우면 삼두에 더 자극." },
    "레그프레스 머신":  { desc: "앉아서 발판을 미는 하체 머신. 스쿼트보다 허리 부담이 적어요.", tip: "무릎을 완전히 펴서 잠그지 말고 살짝 남겨두세요." },
    "랫풀다운 머신":    { desc: "위에서 바를 당겨 넓은 등을 만드는 머신.", tip: "팔이 아니라 겨드랑이로 당긴다는 느낌으로." },
    "체스트프레스 머신": { desc: "앉아서 미는 가슴 머신. 벤치프레스 입문용으로 최고.", tip: "가슴을 펴고 어깨가 앞으로 말리지 않게." },
    "시티드로우 머신":  { desc: "앉아서 당기는 등 머신. 등 중앙 두께를 만들어요.", tip: "허리를 세우고 팔꿈치를 뒤로 끝까지." },
    "레그익스텐션 머신": { desc: "앉아서 다리를 펴는 허벅지 앞(대퇴사두) 집중 머신.", tip: "올릴 때 1초 멈추면 자극이 두 배." },
    "레그컬 머신":     { desc: "다리를 접는 허벅지 뒤(햄스트링) 집중 머신.", tip: "반동 없이 천천히 — 특히 내릴 때." },
    "숄더프레스 머신":  { desc: "앉아서 위로 미는 어깨 머신.", tip: "허리를 과하게 젖히지 말고 코어에 힘." },
    "카프레이즈 머신":  { desc: "발끝으로 서며 종아리를 단련.", tip: "맨 위에서 1초, 맨 아래에서 스트레칭 1초." },
    "케이블 머신":     { desc: "도르레 케이블. 푸시다운·로우·컬 등 다용도.", tip: "케이블은 장력이 일정해서 마무리 운동에 딱이에요." },
    "케이블 크로스오버": { desc: "양쪽 케이블을 모아 가슴 안쪽을 조각하는 장비.", tip: "팔을 모을 때 가슴을 쥐어짠다는 느낌으로 1초 정지." },
    "트레드밀":        { desc: "러닝머신. 걷기부터 인터벌까지.", tip: "경사 5~10%로 빠르게 걷기만 해도 훌륭한 유산소." },
    "사이클":          { desc: "실내 자전거. 무릎 부담이 적은 유산소.", tip: "안장 높이는 페달 최하단에서 무릎이 살짝 굽는 정도." },
    "로잉머신":        { desc: "노 젓기. 전신 유산소 + 등 근육까지.", tip: "다리→몸통→팔 순서로 당기는 게 정석." },
    "일립티컬":        { desc: "관절 충격 없는 전신 유산소 머신.", tip: "손잡이를 밀고 당기면 상체 운동도 같이." },
    "매트":           { desc: "스트레칭·플랭크·크런치 공간.", tip: "운동 전 동적, 운동 후 정적 스트레칭." },
    "캡틴체어":        { desc: "팔을 걸치고 다리를 들어 올리는 복근 기구.", tip: "반동 없이 골반을 말아 올리는 느낌으로." },
    "앱롤러":          { desc: "바퀴를 밀며 코어 전체를 단련하는 소도구.", tip: "허리가 꺾이면 안 돼요. 무릎 대고 짧게부터." },
  };

  // ── 운동 목록 ──
  //  em=아이콘, pat=동작 애니메이션 패턴(anim.js), how=수행 순서(간단)
  const EXERCISES = [
    // 가슴
    { id: "bench_press", name: "바벨 벤치프레스", zone: "A", equipment: "벤치프레스대", category: "strength", kind: "reps", met: 5.0, primary: ["chest"], secondary: ["triceps", "shoulders"], big3: "bench", em: "🏋️", pat: "bench",
      how: ["벤치에 누워 어깨를 뒤로 모으고 발로 바닥을 단단히", "바를 가슴 중앙까지 천천히 내리고", "가슴으로 밀어 올리기 (팔꿈치 잠그지 않기)"] },
    { id: "incline_db_press", name: "인클라인 덤벨프레스", zone: "A", equipment: "덤벨세트", category: "strength", kind: "reps", met: 5.0, primary: ["chest"], secondary: ["shoulders", "triceps"], em: "💪", pat: "bench",
      how: ["벤치를 30~45도로 세우고 덤벨을 가슴 위로", "팔꿈치를 45도로 벌리며 천천히 내리고", "가슴 윗부분으로 모아 올리기"] },
    { id: "chest_press_m", name: "체스트프레스 머신", zone: "B", equipment: "체스트프레스 머신", category: "strength", kind: "reps", met: 4.5, primary: ["chest"], secondary: ["triceps"], em: "🫸", pat: "bench",
      how: ["손잡이가 가슴 높이에 오게 시트 조절", "가슴을 펴고 앞으로 밀기", "천천히 되돌아오기 (무게가 쿵 하지 않게)"] },
    { id: "cable_fly", name: "케이블 크로스오버", zone: "C", equipment: "케이블 크로스오버", category: "strength", kind: "reps", met: 4.0, primary: ["chest"], secondary: ["shoulders"], em: "🦅", pat: "fly",
      how: ["양쪽 손잡이를 잡고 한 발 앞으로", "팔을 약간 굽힌 채 앞으로 모으기", "가슴을 쥐어짜듯 1초 정지 후 천천히 벌리기"] },
    // 등
    { id: "deadlift", name: "데드리프트", zone: "A", equipment: "파워랙", category: "strength", kind: "reps", met: 6.0, primary: ["back", "hamstrings", "glutes"], secondary: ["core"], big3: "deadlift", em: "🏋️", pat: "hinge",
      how: ["발 중간 위에 바, 정강이 가까이 서기", "허리를 편 채 엉덩이를 뒤로 빼며 바 잡기", "다리로 바닥을 밀며 일어서기 (허리로 들지 않기)"] },
    { id: "pullup", name: "풀업(턱걸이)", zone: "A", equipment: "풀업바", category: "strength", kind: "reps", met: 5.0, primary: ["back"], secondary: ["biceps"], em: "🙌", pat: "pulldown",
      how: ["어깨너비보다 넓게 바를 잡고 매달리기", "가슴을 바 쪽으로 당겨 올리기", "천천히 내려오기 (뚝 떨어지지 않게)"] },
    { id: "lat_pulldown", name: "랫풀다운", zone: "B", equipment: "랫풀다운 머신", category: "strength", kind: "reps", met: 4.5, primary: ["back"], secondary: ["biceps"], em: "⬇️", pat: "pulldown",
      how: ["무릎 패드를 허벅지에 맞추고 넓게 잡기", "가슴을 펴고 바를 쇄골 쪽으로 당기기", "겨드랑이로 당긴다는 느낌, 천천히 올리기"] },
    { id: "seated_row_m", name: "시티드 로우", zone: "B", equipment: "시티드로우 머신", category: "strength", kind: "reps", met: 4.5, primary: ["back"], secondary: ["biceps"], em: "🚣", pat: "row",
      how: ["가슴 패드에 몸을 붙이고 손잡이 잡기", "팔꿈치를 뒤로 끝까지 당기기", "등 중앙을 조인 뒤 천천히 풀기"] },
    { id: "db_row", name: "덤벨 로우", zone: "A", equipment: "덤벨세트", category: "strength", kind: "reps", met: 5.0, primary: ["back"], secondary: ["biceps"], em: "🐝", pat: "row",
      how: ["한 손과 무릎을 벤치에 대고 등 평평하게", "덤벨을 골반 쪽으로 당겨 올리기", "천천히 내리기, 반대쪽도 동일하게"] },
    { id: "cable_row", name: "케이블 로우", zone: "C", equipment: "케이블 머신", category: "strength", kind: "reps", met: 4.5, primary: ["back"], secondary: ["biceps"], em: "🔗", pat: "row",
      how: ["앉아서 허리를 세우고 손잡이 잡기", "팔꿈치를 몸통 옆으로 당기기", "어깨가 으쓱 올라가지 않게 주의"] },
    // 어깨
    { id: "db_shoulder_press", name: "덤벨 숄더프레스", zone: "A", equipment: "덤벨세트", category: "strength", kind: "reps", met: 5.0, primary: ["shoulders"], secondary: ["triceps"], em: "🙆", pat: "ohp",
      how: ["덤벨을 귀 옆 높이로 들기", "머리 위로 밀어 올려 팔 펴기", "천천히 귀 옆까지 내리기"] },
    { id: "shoulder_press_m", name: "숄더프레스 머신", zone: "B", equipment: "숄더프레스 머신", category: "strength", kind: "reps", met: 4.5, primary: ["shoulders"], secondary: ["triceps"], em: "🙆", pat: "ohp",
      how: ["손잡이가 어깨 높이에 오게 시트 조절", "위로 밀어 올리기 (허리 젖히지 않기)", "천천히 내리기"] },
    { id: "lateral_raise", name: "레터럴 레이즈", zone: "A", equipment: "덤벨세트", category: "strength", kind: "reps", met: 3.5, primary: ["shoulders"], secondary: [], em: "🕊️", pat: "raise",
      how: ["가벼운 덤벨을 몸 옆에 들기", "팔을 약간 굽힌 채 어깨 높이까지 올리기", "새가 날갯짓하듯 천천히 내리기"] },
    { id: "face_pull", name: "페이스풀", zone: "C", equipment: "케이블 머신", category: "strength", kind: "reps", met: 4.0, primary: ["shoulders"], secondary: ["back"], em: "🎯", pat: "row",
      how: ["로프를 얼굴 높이로 세팅", "얼굴 쪽으로 당기며 팔꿈치를 벌리기", "어깨 뒤쪽을 조이는 느낌으로"] },
    // 삼두
    { id: "cable_pushdown", name: "케이블 푸시다운", zone: "C", equipment: "케이블 머신", category: "strength", kind: "reps", met: 4.0, primary: ["triceps"], secondary: [], em: "⤵️", pat: "tridown",
      how: ["팔꿈치를 몸통에 고정하고 바 잡기", "팔꿈치만 움직여 아래로 펴기", "천천히 되돌리기"] },
    { id: "lying_tri_ext", name: "라잉 트라이셉스", zone: "A", equipment: "EZ바", category: "strength", kind: "reps", met: 4.0, primary: ["triceps"], secondary: [], em: "💀", pat: "bench",
      how: ["벤치에 누워 바를 이마 위로", "팔꿈치를 고정한 채 이마 쪽으로 내리기", "삼두 힘으로 다시 펴기"] },
    { id: "dips", name: "딥스", zone: "A", equipment: "딥스대", category: "strength", kind: "reps", met: 5.0, primary: ["triceps"], secondary: ["chest", "shoulders"], em: "🇭", pat: "dip",
      how: ["평행봉을 잡고 팔을 편 채 몸 띄우기", "팔꿈치를 굽혀 몸을 내리기", "팔을 펴며 올라오기 (몸 세우면 삼두, 기울이면 가슴)"] },
    // 이두
    { id: "barbell_curl", name: "바벨 컬", zone: "A", equipment: "EZ바", category: "strength", kind: "reps", met: 3.5, primary: ["biceps"], secondary: [], em: "💪", pat: "curl",
      how: ["어깨너비로 바를 잡고 서기", "팔꿈치를 고정한 채 감아올리기", "반동 없이 천천히 내리기"] },
    { id: "db_curl", name: "덤벨 컬", zone: "A", equipment: "덤벨세트", category: "strength", kind: "reps", met: 3.5, primary: ["biceps"], secondary: [], em: "💪", pat: "curl",
      how: ["덤벨을 양손에 들고 손바닥 앞으로", "한쪽씩 또는 동시에 감아올리기", "내릴 때 더 천천히 (2초)"] },
    { id: "cable_curl", name: "케이블 컬", zone: "C", equipment: "케이블 머신", category: "strength", kind: "reps", met: 3.5, primary: ["biceps"], secondary: [], em: "🔗", pat: "curl",
      how: ["케이블을 최하단에 걸고 바 잡기", "팔꿈치 고정, 감아올리기", "장력을 느끼며 천천히 내리기"] },
    // 하체
    { id: "back_squat", name: "바벨 백스쿼트", zone: "A", equipment: "파워랙", category: "strength", kind: "reps", met: 6.0, primary: ["quads", "glutes"], secondary: ["hamstrings", "core"], big3: "squat", em: "🏋️", pat: "squat",
      how: ["바를 어깨 뒤(승모근 위)에 얹고 랙에서 나오기", "의자에 앉듯 엉덩이를 뒤로·아래로", "허벅지가 바닥과 평행할 때까지 → 일어서기"] },
    { id: "leg_press", name: "레그프레스", zone: "B", equipment: "레그프레스 머신", category: "strength", kind: "reps", met: 5.0, primary: ["quads", "glutes"], secondary: ["hamstrings"], em: "🦵", pat: "legext",
      how: ["발판에 어깨너비로 발 올리기", "무릎이 가슴 쪽으로 오게 내리고", "발바닥 전체로 밀기 (무릎 완전히 잠그지 않기)"] },
    { id: "leg_ext", name: "레그 익스텐션", zone: "B", equipment: "레그익스텐션 머신", category: "strength", kind: "reps", met: 4.0, primary: ["quads"], secondary: [], em: "🦿", pat: "legext",
      how: ["발목 패드에 발을 걸고 앉기", "다리를 앞으로 쭉 펴기", "맨 위에서 1초 정지 후 천천히 내리기"] },
    { id: "db_lunge", name: "덤벨 런지", zone: "A", equipment: "덤벨세트", category: "strength", kind: "reps", met: 5.0, primary: ["quads", "glutes"], secondary: ["hamstrings"], em: "🚶", pat: "lunge",
      how: ["덤벨을 양손에 들고 한 발 크게 앞으로", "뒷무릎이 바닥 가까이 가게 내려가기", "앞발 뒤꿈치로 밀며 일어나기"] },
    { id: "romanian_dl", name: "루마니안 데드리프트", zone: "A", equipment: "바벨/벤치", category: "strength", kind: "reps", met: 5.5, primary: ["hamstrings", "glutes"], secondary: ["back"], em: "🍑", pat: "hinge",
      how: ["바를 허벅지 앞에 들고 서기", "무릎을 살짝 굽힌 채 엉덩이를 뒤로", "허벅지 뒤가 당기면 엉덩이 힘으로 올라오기"] },
    { id: "leg_curl", name: "레그 컬", zone: "B", equipment: "레그컬 머신", category: "strength", kind: "reps", met: 4.0, primary: ["hamstrings"], secondary: [], em: "🪝", pat: "legcurl",
      how: ["발목 뒤에 패드가 오게 세팅", "다리를 엉덩이 쪽으로 접기", "반동 없이 천천히 펴기"] },
    { id: "hip_thrust", name: "힙 쓰러스트", zone: "A", equipment: "바벨/벤치", category: "strength", kind: "reps", met: 5.0, primary: ["glutes"], secondary: ["hamstrings"], em: "🍑", pat: "hipthrust",
      how: ["등 상부를 벤치에 대고 바를 골반 위에", "엉덩이를 위로 밀어 올려 몸 일직선", "맨 위에서 엉덩이 꽉 조이고 내리기"] },
    { id: "calf_raise_m", name: "카프레이즈", zone: "B", equipment: "카프레이즈 머신", category: "strength", kind: "reps", met: 4.0, primary: ["calves"], secondary: [], em: "🦶", pat: "calf",
      how: ["발끝을 발판에 걸고 서기", "발끝으로 최대한 높이 올라가기", "뒤꿈치를 아래로 내려 종아리 늘리기"] },
    // 코어
    { id: "plank", name: "플랭크", zone: "E", equipment: "매트", category: "strength", kind: "time", met: 3.5, primary: ["core"], secondary: [], em: "🧱", pat: "plank",
      how: ["팔꿈치와 발끝으로 몸 지탱", "머리~발끝 일직선 유지 (엉덩이 들리거나 처지지 않게)", "배에 힘 주고 버티기"] },
    { id: "crunch", name: "크런치", zone: "E", equipment: "매트", category: "strength", kind: "reps", met: 3.5, primary: ["core"], secondary: [], em: "🌙", pat: "crunch",
      how: ["누워서 무릎 세우고 손은 가슴 위", "배를 접듯 어깨만 들어 올리기", "목이 아니라 복근으로! 천천히 내리기"] },
    { id: "hanging_leg_raise", name: "행잉 레그레이즈", zone: "E", equipment: "캡틴체어", category: "strength", kind: "reps", met: 4.0, primary: ["core"], secondary: [], em: "🦵", pat: "crunch",
      how: ["팔걸이에 팔을 얹고 몸 띄우기", "다리를 모아 배꼽 높이까지 올리기", "반동 없이 천천히 내리기"] },
    { id: "ab_rollout", name: "앱 롤아웃", zone: "E", equipment: "앱롤러", category: "strength", kind: "reps", met: 4.0, primary: ["core"], secondary: [], em: "🛞", pat: "plank",
      how: ["무릎 대고 롤러를 잡기", "허리가 꺾이지 않는 범위까지 앞으로 밀기", "복근 힘으로 되돌아오기"] },
    // 유산소
    { id: "treadmill", name: "트레드밀(러닝)", zone: "D", equipment: "트레드밀", category: "cardio", kind: "time", met: 8.5, primary: ["cardio"], secondary: [], em: "🏃", pat: "run",
      how: ["가볍게 걷기로 3분 워밍업", "대화 가능한 속도로 페이스 유지", "마지막 2분은 걷기로 쿨다운"] },
    { id: "bike", name: "사이클", zone: "D", equipment: "사이클", category: "cardio", kind: "time", met: 7.0, primary: ["cardio"], secondary: [], em: "🚴", pat: "bike",
      how: ["안장 높이: 페달 최하단에서 무릎 살짝 굽게", "일정한 리듬으로 페달링", "저항을 올려 강도 조절"] },
    { id: "rowing", name: "로잉머신", zone: "D", equipment: "로잉머신", category: "cardio", kind: "time", met: 7.0, primary: ["cardio"], secondary: ["back"], em: "🛶", pat: "rowm",
      how: ["다리로 밀고 → 몸 젖히고 → 팔 당기기", "되돌아갈 땐 역순 (팔→몸→다리)", "리듬이 중요! 힘은 다리에서 70%"] },
    { id: "elliptical", name: "일립티컬", zone: "D", equipment: "일립티컬", category: "cardio", kind: "time", met: 5.0, primary: ["cardio"], secondary: [], em: "⛷️", pat: "run",
      how: ["발판에 발을 올리고 손잡이 잡기", "페달을 부드럽게 돌리기", "손잡이를 밀고 당기면 상체도 운동"] },
  ];

  const BY_ID = {};
  EXERCISES.forEach((e) => (BY_ID[e.id] = e));

  // ── 추구하는 스타일 ──
  const STYLES = [
    { id: "bulk", emoji: "🍚", name: "벌크업", easy: "체중 늘리며 근육·힘 최대로 키우기",
      long: "잘 먹으면서 무겁게 — 근육량을 빠르게 늘리는 대신 약간의 체지방도 감수해요.",
      sets: 4, reps: "6-10", rest: 120, cardio: 0, big3Boost: true, surplus: "충분히 먹기(칼로리 +)" },
    { id: "lean", emoji: "🥗", name: "린매스업", easy: "군살 없이 천천히 근육 늘리기",
      long: "체지방은 최대한 유지하면서 근육만 조금씩 — 깔끔한 몸을 원할 때.",
      sets: 4, reps: "8-12", rest: 90, cardio: 5, big3Boost: false, surplus: "살짝 더 먹기(칼로리 +조금)" },
    { id: "cut", emoji: "🔥", name: "다이어트(컷)", easy: "체지방 빼서 날렵하게",
      long: "근육은 지키면서 체지방을 빼는 게 목표 — 유산소를 곁들여요.",
      sets: 3, reps: "12-15", rest: 60, cardio: 20, big3Boost: false, surplus: "적게 먹기(칼로리 −)" },
    { id: "power", emoji: "🏋️", name: "파워리프팅", easy: "스쿼트·벤치·데드 3대 힘 최대로",
      long: "3대 운동 중량을 올리는 데 집중 — 무겁게 적은 횟수, 충분한 휴식.",
      sets: 5, reps: "3-5", rest: 180, cardio: 0, big3Boost: true, surplus: "잘 먹기(칼로리 +)" },
    { id: "tone", emoji: "✨", name: "토닝/바디프로필", easy: "탄탄한 라인 만들기",
      long: "적당한 근육과 낮은 체지방으로 선명한 라인 — 중간 반복 + 약간의 유산소.",
      sets: 3, reps: "12-15", rest: 60, cardio: 15, big3Boost: false, surplus: "유지~살짝 적게" },
    { id: "health", emoji: "🧘", name: "체력·건강", easy: "건강하게 체력 기르기",
      long: "무리 없이 전신을 골고루 — 가볍게 시작해 습관 만들기.",
      sets: 3, reps: "10-15", rest: 60, cardio: 15, big3Boost: false, surplus: "균형 있게" },
  ];
  const STYLE_BY_ID = {};
  STYLES.forEach((s) => (STYLE_BY_ID[s.id] = s));

  // ── 분할 정의 ──
  const SPLITS = {
    fullbody: { name: "전신(풀바디)", easy: "하루에 온몸을 골고루",
      long: "매 운동일마다 상체·하체를 다 건드려요. 주 2~3회로도 빠짐없이 자극할 수 있어 초보에게 최고.",
      pattern: ["full"] },
    upper_lower: { name: "상하체 2분할", easy: "상체 날 / 하체 날로 나눠서",
      long: "하루는 상체(가슴·등·어깨·팔), 다음은 하체(다리·엉덩이). 주 4회에 잘 맞아요.",
      pattern: ["upper", "lower"] },
    ppl: { name: "밀당다리 3분할 (PPL)", easy: "미는 날 / 당기는 날 / 다리 날",
      long: "가슴·어깨·삼두(미는 근육) → 등·이두(당기는 근육) → 하체. 주 3회 또는 6회(2바퀴)에 좋아요.",
      pattern: ["push", "pull", "legs"] },
    bro: { name: "부위별 5분할", easy: "가슴/등/어깨/다리/팔 하루 한 부위",
      long: "한 부위를 그날 집중 공략. 운동량이 많아 주 5회 이상 꾸준한 중·고급자에게 맞아요.",
      pattern: ["chest_day", "back_day", "shoulder_day", "leg_day", "arm_day"] },
  };

  const DAY_TYPES = {
    full: { kr: "전신", muscles: ["quads", "chest", "back", "shoulders", "hamstrings", "core"] },
    upper: { kr: "상체", muscles: ["chest", "back", "shoulders", "biceps", "triceps", "chest", "back"] },
    lower: { kr: "하체", muscles: ["quads", "hamstrings", "glutes", "quads", "calves", "core"] },
    push: { kr: "미는 날(가슴·어깨·삼두)", muscles: ["chest", "shoulders", "chest", "triceps", "shoulders", "triceps"] },
    pull: { kr: "당기는 날(등·이두)", muscles: ["back", "back", "back", "biceps", "biceps", "core"] },
    legs: { kr: "다리 날", muscles: ["quads", "hamstrings", "glutes", "quads", "calves", "core"] },
    chest_day: { kr: "가슴", muscles: ["chest", "chest", "chest", "chest", "triceps"] },
    back_day: { kr: "등", muscles: ["back", "back", "back", "back", "biceps"] },
    shoulder_day: { kr: "어깨", muscles: ["shoulders", "shoulders", "shoulders", "shoulders", "core"] },
    leg_day: { kr: "하체", muscles: ["quads", "hamstrings", "glutes", "quads", "calves", "core"] },
    arm_day: { kr: "팔(이두·삼두)", muscles: ["biceps", "triceps", "biceps", "triceps", "biceps", "core"] },
  };

  function levelFromMonths(m) {
    if (m < 6) return "beginner";
    if (m < 24) return "intermediate";
    return "advanced";
  }
  const LEVEL_KR = { beginner: "초보", intermediate: "중급", advanced: "고급" };

  return {
    MUSCLE_KR, ZONES, FLOOR_ZONES, FLOOR, EQUIP_INFO, EXERCISES, BY_ID,
    STYLES, STYLE_BY_ID, SPLITS, DAY_TYPES, levelFromMonths, LEVEL_KR,
    byId: (id) => BY_ID[id],
    inMuscle: (m) => EXERCISES.filter((e) => e.primary.includes(m)),
    zoneById: (id) => ZONES.find((z) => z.id === id),
  };
})();
