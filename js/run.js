// 러닝 — 성향 진단 → 주간 러닝 플랜 생성 / 기록 통계 / 타입 설명
window.RUN = (function () {

  // ── 러닝 타입(쉬운 설명 + 목표 심박 %범위) ──
  //  hr = 최대심박(220-나이) 대비 목표 구간
  const TYPES = {
    easy:     { kr: "이지런",  emoji: "🙂", color: "#34d399", hr: [0.60, 0.70],
      easy: "편안한 속도로 달리기", guide: "옆 사람과 대화할 수 있는 속도. 러닝의 기본, 가장 많이 하는 훈련." },
    long:     { kr: "장거리(LSD)", emoji: "🐢", color: "#60a5fa", hr: [0.60, 0.70],
      easy: "천천히, 길게", guide: "평소보다 느리게 대신 멀리. 지구력의 뼈대를 만드는 주 1회 핵심 훈련." },
    tempo:    { kr: "템포런",  emoji: "😤", color: "#fbbf24", hr: [0.80, 0.88],
      easy: "약간 힘든 속도 유지", guide: "'힘들지만 버틸 만한' 속도로 20~40분. 레이스 페이스를 끌어올려요." },
    interval: { kr: "인터벌",  emoji: "⚡", color: "#f87171", hr: [0.88, 0.95],
      easy: "빠르게-쉬엄쉬엄 반복", guide: "400~800m 빠르게 + 조깅 회복을 4~8회 반복. 스피드와 심폐를 확 올려요." },
    sprint:   { kr: "단거리(스프린트)", emoji: "💨", color: "#c084fc", hr: [0.90, 0.97],
      easy: "짧고 폭발적으로", guide: "100~200m 전력의 80~90% × 6~10회. 폼과 순발력 훈련." },
    recovery: { kr: "회복런",  emoji: "🧘", color: "#a1a1aa", hr: [0.50, 0.60],
      easy: "아주 천천히 풀어주기", guide: "힘든 훈련 다음 날 20~30분 아주 천천히. 걷기 섞어도 OK." },
  };

  // 타입별 목표 심박수(bpm) — 최대심박 = 직접 입력값 or (220 - 나이)
  function hrRange(type, age, maxHr) {
    const t = TYPES[type];
    if (!t || !t.hr) return null;
    const max = maxHr > 0 ? maxHr : 220 - (age || 30);
    return { lo: Math.round(max * t.hr[0]), hi: Math.round(max * t.hr[1]),
      pctLo: Math.round(t.hr[0] * 100), pctHi: Math.round(t.hr[1] * 100) };
  }

  // ── 러닝 목표 ──
  const GOALS = [
    { id: "fun",  emoji: "🌿", name: "기분전환·건강", easy: "스트레스 풀고 체력 올리기" },
    { id: "loss", emoji: "🔥", name: "체중 감량", easy: "달리면서 살 빼기" },
    { id: "k5",   emoji: "🏁", name: "5K 완주/기록", easy: "5km를 완주하거나 더 빠르게" },
    { id: "k10",  emoji: "🏃", name: "10K 도전", easy: "10km 완주가 목표" },
    { id: "half", emoji: "🏅", name: "하프마라톤", easy: "21.1km에 도전" },
    { id: "full", emoji: "🏆", name: "풀코스 마라톤", easy: "42.195km 완주에 도전" },
  ];

  // ── 경험 → 레벨 ──
  const EXP = [
    { v: "new",  t: "거의 처음", d: "러닝은 처음이거나 아주 가끔" },
    { v: "some", t: "가끔 뛰는 편", d: "월 2~4회 정도" },
    { v: "reg",  t: "꾸준히 뛰는 중", d: "주 1회 이상, 6개월+" },
    { v: "pro",  t: "러너", d: "대회 경험 있음 / 주 3회+" },
  ];
  // 쉬지 않고 달릴 수 있는 거리 → 체력 지수 1~5
  const ABILITY = [
    { v: 1, t: "1km 미만" }, { v: 2, t: "1~3km" }, { v: 3, t: "3~5km" },
    { v: 4, t: "5~10km" }, { v: 5, t: "10km 이상" },
  ];

  function levelOf(p) {
    if (p.exp === "new" || p.ability <= 1) return "beginner";
    if (p.exp === "pro" || p.ability >= 4) return "advanced";
    return "intermediate";
  }
  const LEVEL_KR = { beginner: "입문", intermediate: "중급", advanced: "고급" };

  // ── 주간 플랜 생성 ──
  // p = {exp, goal, days, ability}
  function buildPlan(p) {
    const level = levelOf(p);
    const days = Math.max(2, Math.min(6, +p.days || 3));
    // 기준 거리: 이지런 km (체력 지수 기반)
    let easyKm = [1.5, 2.5, 4, 5, 6][p.ability - 1] || 3;
    let longMul = 1.6;
    if (p.goal === "half") longMul = 2.2;
    if (p.goal === "full") longMul = 2.6;      // 풀코스: 장거리 비중 최대
    if (p.goal === "k10") longMul = 1.9;
    if (p.goal === "loss") easyKm *= 1.1;      // 감량은 볼륨 약간↑ (느리게 길게)
    const longKm = Math.round(easyKm * longMul * 10) / 10;
    const speedGoal = p.goal === "k5" || p.goal === "k10" || p.goal === "half" || p.goal === "full";

    // 요일 패턴 (레벨 낮으면 강한 훈련 제외)
    const t2 = level === "beginner" ? "easy" : "tempo";
    const iv = level === "beginner" ? "easy" : "interval";
    const patterns = {
      2: ["easy", "long"],
      3: ["easy", speedGoal ? t2 : "easy", "long"],
      4: ["easy", speedGoal ? iv : t2, "recovery", "long"],
      5: ["easy", iv, "recovery", t2, "long"],
      6: ["easy", iv, "recovery", t2, level === "advanced" ? "sprint" : "easy", "long"],
    };
    const pat = patterns[days];

    const week = pat.map((type, i) => {
      let km;
      if (type === "long") km = longKm;
      else if (type === "recovery") km = Math.round(easyKm * 0.6 * 10) / 10;
      else if (type === "interval") km = Math.round(easyKm * 0.9 * 10) / 10;
      else if (type === "sprint") km = Math.round(easyKm * 0.7 * 10) / 10;
      else if (type === "tempo") km = Math.round(easyKm * 1.0 * 10) / 10;
      else km = easyKm;
      return { day: i + 1, type, kr: TYPES[type].kr, emoji: TYPES[type].emoji,
        color: TYPES[type].color, km, note: TYPES[type].guide };
    });
    const weeklyKm = Math.round(week.reduce((s, d) => s + d.km, 0) * 10) / 10;
    const goal = GOALS.find((g) => g.id === p.goal) || GOALS[0];

    return {
      level, levelKr: LEVEL_KR[level], goal: goal.id, goalName: goal.name,
      days, weeklyKm,
      summary: `${goal.name} · ${LEVEL_KR[level]} · 주 ${days}회 · 주 ${weeklyKm}km`,
      week,
    };
  }

  // ── 페이스 유틸 (초/km 저장) ──
  const paceStr = (sec) => sec ? Math.floor(sec / 60) + "'" + String(Math.round(sec % 60)).padStart(2, "0") + '"' : "-";

  // ── 기록 통계 ──
  // runs = [{rid, date, km, paceSec}]
  function stats(runs) {
    const now = new Date();
    const day7 = new Date(now); day7.setDate(day7.getDate() - 6);
    const ym = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0");
    let weekKm = 0, monthKm = 0, totalKm = 0, longest = 0, bestPace = 0;
    runs.forEach((r) => {
      const d = new Date(r.date + "T00:00:00");
      totalKm += r.km;
      if (d >= day7) weekKm += r.km;
      if (r.date.startsWith(ym)) monthKm += r.km;
      if (r.km > longest) longest = r.km;
      if (r.paceSec && r.km >= 1 && (!bestPace || r.paceSec < bestPace)) bestPace = r.paceSec;
    });
    const r1 = (x) => Math.round(x * 10) / 10;
    return { count: runs.length, weekKm: r1(weekKm), monthKm: r1(monthKm),
      totalKm: r1(totalKm), longest: r1(longest), bestPace };
  }

  // 이번 주(최근 7일) 계획 대비 달성률
  function weekScore(plan, runs) {
    if (!plan) return { pct: 0, doneKm: 0, targetKm: 0, doneCnt: 0, targetCnt: 0 };
    const st = stats(runs);
    const doneCnt = runs.filter((r) => {
      const d = new Date(r.date + "T00:00:00");
      const c = new Date(); c.setDate(c.getDate() - 6); c.setHours(0, 0, 0, 0);
      return d >= c;
    }).length;
    const pct = Math.min(100, Math.round((st.weekKm / Math.max(0.1, plan.weeklyKm)) * 100));
    return { pct, doneKm: st.weekKm, targetKm: plan.weeklyKm, doneCnt, targetCnt: plan.days };
  }

  // 랭킹 데모(서버 미연동 시 예시)
  const DEMO = [
    { id: "민준(개발팀)", weekKm: 24.5, monthKm: 82, totalKm: 517, demo: true },
    { id: "서연(인사팀)", weekKm: 18.2, monthKm: 61, totalKm: 344, demo: true },
    { id: "지훈(영업팀)", weekKm: 15.0, monthKm: 47, totalKm: 285, demo: true },
    { id: "하은(재무팀)", weekKm: 9.6, monthKm: 33, totalKm: 158, demo: true },
    { id: "도윤(생산팀)", weekKm: 6.4, monthKm: 21, totalKm: 96, demo: true },
  ];

  return { TYPES, GOALS, EXP, ABILITY, buildPlan, paceStr, stats, weekScore, DEMO, LEVEL_KR, hrRange };
})();
