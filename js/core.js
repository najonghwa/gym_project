// 핵심 로직 — 분할 추천 / 루틴 생성 / 예측 / 점수 계산
window.CORE = (function () {
  const D = window.DATA;

  // ── 주당 횟수 + 레벨 → 추천 분할 ──
  function recommendSplit(days, level) {
    if (days <= 2) return "fullbody";
    if (days === 3) return level === "beginner" ? "fullbody" : "ppl";
    if (days === 4) return "upper_lower";
    if (days === 5) return "bro";
    return "ppl"; // 6회 → PPL 2바퀴
  }

  // 분할 패턴을 주당 횟수만큼 채우기
  function buildSchedule(splitId, days) {
    const pat = D.SPLITS[splitId].pattern;
    const out = [];
    for (let i = 0; i < days; i++) out.push(pat[i % pat.length]);
    return out;
  }

  // 운동시간(분) → 하루 운동 개수
  function exCountByTime(min) {
    if (min <= 30) return 4;
    if (min <= 45) return 5;
    if (min <= 60) return 6;
    return 8;
  }

  // 부위에서 아직 안 쓴 운동 하나 고르기(반복 요일이면 variant로 종목 회전)
  function pickExercise(muscle, used, variant, big3Boost) {
    let cands = D.inMuscle(muscle).filter((e) => e.category === "strength");
    cands.sort((a, b) => {
      // 파워리프팅이면 3대 운동 최우선
      const a3 = big3Boost && a.big3 ? -2 : 0;
      const b3 = big3Boost && b.big3 ? -2 : 0;
      const ac = a.primary.length >= 2 ? 0 : 1; // 복합운동 먼저
      const bc = b.primary.length >= 2 ? 0 : 1;
      return (a3 + ac) - (b3 + bc) || a.id.localeCompare(b.id);
    });
    if (!cands.length) return null;
    if (variant) {
      const k = variant % cands.length;
      cands = cands.slice(k).concat(cands.slice(0, k));
    }
    for (const e of cands) if (!used.has(e.id)) return e;
    return cands[0];
  }

  // ── 프로필 → 주간 루틴 ──
  function buildRoutine(profile) {
    const style = D.STYLE_BY_ID[profile.style] || D.STYLES[0];
    const level = profile.level || "beginner";
    const days = +profile.days || 3;
    const splitId = profile.split || recommendSplit(days, level);
    const schedule = buildSchedule(splitId, days);

    let sets = style.sets + (level === "beginner" ? -1 : level === "advanced" ? 1 : 0);
    sets = Math.max(2, sets);
    let nEx = exCountByTime(+profile.sessionMin || 60);
    if (level === "beginner") nEx = Math.max(3, nEx - 1);

    const seen = {};
    const week = schedule.map((dtype, i) => {
      const variant = (seen[dtype] = (seen[dtype] || 0)) ; seen[dtype]++;
      let muscles = D.DAY_TYPES[dtype].muscles.slice();
      if (profile.focus === "core") muscles = ["core"].concat(muscles);

      const used = new Set();
      const items = [];
      for (const m of muscles) {
        if (items.length >= nEx) break;
        const ex = pickExercise(m, used, variant, style.big3Boost);
        if (!ex) continue;
        used.add(ex.id);
        items.push({
          exId: ex.id, name: ex.name, zone: ex.zone, equipment: ex.equipment,
          target: ex.primary.map((x) => D.MUSCLE_KR[x]),
          kind: ex.kind,
          sets: ex.kind === "time" ? 1 : sets,
          reps: ex.kind === "time" ? "45-60초" : style.reps,
          rest: style.rest,
        });
      }
      if (style.cardio > 0) {
        const c = D.byId("treadmill");
        items.push({ exId: c.id, name: c.name, zone: c.zone, equipment: c.equipment,
          target: ["유산소"], kind: "time", sets: 1, reps: style.cardio + "분", rest: 0 });
      }
      return { day: i + 1, type: dtype, typeKr: D.DAY_TYPES[dtype].kr, items };
    });

    return {
      style: style.id, styleName: style.name, level, levelKr: D.LEVEL_KR[level],
      days, split: splitId, splitName: D.SPLITS[splitId].name,
      summary: `${style.name} · ${D.SPLITS[splitId].name} · 주 ${days}회`,
      week,
    };
  }

  // ── 칼로리 예측 ──
  const MIN_PER_SET = 2.5, KCAL_PER_KG_FAT = 7700;

  function exerciseKcal(item, weight, setsDone) {
    const ex = D.byId(item.exId);
    const met = ex ? ex.met : 4;
    let mins;
    if (item.kind === "time") {
      const txt = String(item.reps);
      mins = txt.includes("분") ? (parseInt(txt) || 5) : (setsDone > 0 ? 1 : 0) * 1; // 초 단위≈1분
      if (!txt.includes("분")) mins = setsDone > 0 ? 1 : 0;
    } else {
      mins = (setsDone != null ? setsDone : item.sets) * MIN_PER_SET;
    }
    return met * weight * (mins / 60);
  }

  // 계획대로 다 했을 때 세션 칼로리
  function sessionKcalPlanned(dayItems, weight) {
    return dayItems.reduce((s, it) => s + exerciseKcal(it, weight, null), 0);
  }
  // 실제 완료한 세트 기준 세션 칼로리
  function sessionKcalDone(dayItems, weight, doneMap) {
    return dayItems.reduce((s, it) => s + exerciseKcal(it, weight, doneMap[it.exId] || 0), 0);
  }

  // 주간/월간 예측
  const LEVEL_MUSCLE = { beginner: 1.0, intermediate: 0.5, advanced: 0.25 };
  const STYLE_MUSCLE = { bulk: 1.0, power: 0.9, lean: 0.8, tone: 0.5, health: 0.4, cut: 0.3 };

  // 몸무게 미입력 시 성별 평균값으로 대충 계산 (사용자가 안 넣어도 됨)
  function weightOf(profile) {
    const w = +(profile && profile.weight);
    if (w > 0) return w;
    return profile && profile.sex === "female" ? 57 : 70;
  }

  function forecast(profile, routine, consistency) {
    const weight = weightOf(profile);
    const per = routine.week.map((d) => sessionKcalPlanned(d.items, weight));
    const weekly = per.reduce((a, b) => a + b, 0);
    const weeklyFat = weekly / KCAL_PER_KG_FAT;
    const base = LEVEL_MUSCLE[routine.level] || 0.5;
    const sfac = STYLE_MUSCLE[routine.style] || 0.5;
    const sexf = profile.sex === "female" ? 0.6 : 1.0;
    const dfac = Math.min(1.2, routine.days / 4);
    const c = consistency == null ? 1 : consistency;
    const muscle = base * sfac * sexf * dfac * c;
    return {
      weight, perSession: per.map(Math.round),
      weeklyKcal: Math.round(weekly), monthlyKcal: Math.round(weekly * 4.3),
      weeklyFat: +weeklyFat.toFixed(2), monthlyFat: +(weeklyFat * 4.3).toFixed(2),
      monthlyMuscle: +muscle.toFixed(2),
    };
  }

  // ── 점수(계획 대비) ──
  // 세션 점수 = 완료세트 / 계획세트
  function sessionScore(dayItems, doneMap) {
    let planned = 0, done = 0;
    dayItems.forEach((it) => {
      planned += it.sets;
      done += Math.min(it.sets, doneMap[it.exId] || 0);
    });
    return { planned, done, pct: planned ? Math.round((done / planned) * 100) : 0 };
  }

  return {
    recommendSplit, buildSchedule, buildRoutine, exCountByTime, weightOf,
    forecast, sessionScore, sessionKcalDone, sessionKcalPlanned,
  };
})();
