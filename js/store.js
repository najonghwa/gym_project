// 저장소 — 브라우저 localStorage (서버 없음, Vercel 정적 배포용).
// 데이터는 사용하는 그 기기(폰/PC)에 저장됩니다.
// 랭킹·공유루틴의 '동료' 데이터는 데모용 예시 — 서버(Supabase 등) 연동 시 실제 데이터로 교체.
window.STORE = (function () {
  const KEY = "gym_web_v2";

  function loadAll() {
    let db;
    try { db = JSON.parse(localStorage.getItem(KEY)) || null; } catch (e) { db = null; }
    if (!db) db = { users: {}, current: null, shared: null };
    if (!db.shared) { db.shared = seedShared(); save(db); }
    return db;
  }
  function save(db) { localStorage.setItem(KEY, JSON.stringify(db)); }
  const uid = (id) => id.trim().toLowerCase();

  // ── 서버(Supabase) 동기화: 저장할 때마다 뒤에서 살짝 업로드 ──
  let pushTimer = null;
  function schedulePush(u) {
    if (!window.SUPA || !window.SUPA.enabled || !u) return;
    clearTimeout(pushTimer);
    pushTimer = setTimeout(() => window.SUPA.pushUser(u, fullStats(u)), 700);
  }
  // 랭킹용 요약(헬스 + 러닝)
  function fullStats(u) {
    const st = stats(u);
    const cons = u.routine ? consistency28(u, u.routine.days || 3) : { pct: 0 };
    const rst = window.RUN ? window.RUN.stats(u.runs || []) : {};
    return { att: cons.pct, streak: st.streak, sessions: st.sessions, xp: st.xp, level: st.level,
      weekKm: rst.weekKm || 0, monthKm: rst.monthKm || 0, totalKm: rst.totalKm || 0 };
  }

  // ── 사용자 ──
  function getUser(id) { return loadAll().users[uid(id)] || null; }
  function login(id) {
    const db = loadAll(); const k = uid(id);
    if (!db.users[k]) db.users[k] = { id: id.trim(), created: today(), profile: null, routine: null, workouts: {}, customs: [], runs: [], runProfile: null, runPlan: null };
    db.current = k; save(db);
    return db.users[k];
  }
  function currentId() { return loadAll().current; }
  function logout() { const db = loadAll(); db.current = null; save(db); }
  function update(id, fields) {
    const db = loadAll(); const k = uid(id);
    if (!db.users[k]) return null;
    Object.assign(db.users[k], fields); save(db);
    schedulePush(db.users[k]);
    return db.users[k];
  }
  // 서버에서 내려받은 데이터로 통째 교체(같은 아이디를 다른 기기에서 쓸 때)
  function replaceUser(id, data) {
    const db = loadAll(); const k = uid(id);
    db.users[k] = Object.assign({ id: id.trim() }, data, { id: data.id || id.trim() });
    save(db);
    return db.users[k];
  }

  // ── 운동 기록 ──
  function saveWorkout(id, date, w) {
    const db = loadAll(); const k = uid(id);
    if (!db.users[k]) return null;
    db.users[k].workouts = db.users[k].workouts || {};
    db.users[k].workouts[date] = w; save(db);
    schedulePush(db.users[k]);
    return db.users[k];
  }
  function deleteWorkout(id, date) {
    const db = loadAll(); const k = uid(id);
    if (db.users[k] && db.users[k].workouts) { delete db.users[k].workouts[date]; save(db); schedulePush(db.users[k]); }
    return db.users[k];
  }

  // ── 러닝 기록 ──
  function saveRun(id, run) {
    const db = loadAll(); const k = uid(id);
    const u = db.users[k]; if (!u) return null;
    u.runs = u.runs || [];
    u.runs.push(Object.assign({ rid: "r" + Date.now() }, run));
    u.runs.sort((a, b) => (a.date < b.date ? -1 : 1));
    save(db); schedulePush(u);
    return u;
  }
  function deleteRun(id, rid) {
    const db = loadAll(); const k = uid(id);
    const u = db.users[k]; if (!u) return null;
    u.runs = (u.runs || []).filter((r) => r.rid !== rid);
    save(db); schedulePush(u);
    return u;
  }

  // ── 커스텀 루틴 ──
  function saveCustom(id, custom) {
    const db = loadAll(); const k = uid(id);
    const u = db.users[k]; if (!u) return null;
    u.customs = u.customs || [];
    const i = u.customs.findIndex((c) => c.cid === custom.cid);
    if (i >= 0) u.customs[i] = custom; else u.customs.push(custom);
    save(db); schedulePush(u); return u;
  }
  function deleteCustom(id, cid) {
    const db = loadAll(); const k = uid(id);
    const u = db.users[k]; if (!u) return null;
    u.customs = (u.customs || []).filter((c) => c.cid !== cid);
    save(db); schedulePush(u); return u;
  }

  // ── 공유 루틴(업로드) ──
  function sharedList() { return loadAll().shared || []; }
  function shareRoutine(custom, author) {
    const db = loadAll();
    db.shared.unshift({
      sid: "s" + Date.now(), name: custom.name, author, likes: 0, demo: false,
      days: custom.days, weeks: custom.weeks || 0, ts: today(),
    });
    save(db); return db.shared;
  }
  function likeShared(sid) {
    const db = loadAll();
    const s = db.shared.find((x) => x.sid === sid);
    if (s) { s.likes = (s.likes || 0) + 1; save(db); }
    return db.shared;
  }

  // 공유 루틴 시드(데모) — 서버 연동 전 예시
  function seedShared() {
    return [
      { sid: "seed1", name: "3대 중량 올리기 파워 루틴", author: "민준(개발팀)", likes: 24, demo: true, ts: "2026-06-30",
        days: [
          { name: "스쿼트 데이", items: [{ exId: "back_squat", sets: 5, reps: "3-5" }, { exId: "leg_press", sets: 4, reps: "6-8" }, { exId: "leg_curl", sets: 3, reps: "10" }, { exId: "plank", sets: 3, reps: "60초" }] },
          { name: "벤치 데이", items: [{ exId: "bench_press", sets: 5, reps: "3-5" }, { exId: "incline_db_press", sets: 4, reps: "8" }, { exId: "dips", sets: 3, reps: "10" }, { exId: "cable_pushdown", sets: 3, reps: "12" }] },
          { name: "데드 데이", items: [{ exId: "deadlift", sets: 5, reps: "3-5" }, { exId: "lat_pulldown", sets: 4, reps: "8-10" }, { exId: "seated_row_m", sets: 3, reps: "10" }, { exId: "barbell_curl", sets: 3, reps: "12" }] },
        ] },
      { sid: "seed2", name: "점심시간 30분 스피드 루틴", author: "서연(인사팀)", likes: 18, demo: true, ts: "2026-07-02",
        days: [
          { name: "상체 콤보", items: [{ exId: "chest_press_m", sets: 3, reps: "12" }, { exId: "lat_pulldown", sets: 3, reps: "12" }, { exId: "shoulder_press_m", sets: 3, reps: "12" }, { exId: "treadmill", sets: 1, reps: "10분" }] },
          { name: "하체 콤보", items: [{ exId: "leg_press", sets: 3, reps: "12" }, { exId: "leg_curl", sets: 3, reps: "12" }, { exId: "calf_raise_m", sets: 3, reps: "15" }, { exId: "bike", sets: 1, reps: "10분" }] },
        ] },
      { sid: "seed3", name: "여름 대비 컷팅 루틴", author: "지훈(영업팀)", likes: 31, demo: true, ts: "2026-07-05",
        days: [
          { name: "전신 서킷 A", items: [{ exId: "back_squat", sets: 3, reps: "15" }, { exId: "db_row", sets: 3, reps: "15" }, { exId: "db_shoulder_press", sets: 3, reps: "15" }, { exId: "crunch", sets: 3, reps: "20" }, { exId: "treadmill", sets: 1, reps: "20분" }] },
          { name: "전신 서킷 B", items: [{ exId: "db_lunge", sets: 3, reps: "15" }, { exId: "lat_pulldown", sets: 3, reps: "15" }, { exId: "cable_fly", sets: 3, reps: "15" }, { exId: "plank", sets: 3, reps: "45초" }, { exId: "rowing", sets: 1, reps: "15분" }] },
        ] },
    ];
  }

  // ── 랭킹 데모 동료(서버 연동 전 예시) ──
  const DEMO_RANK = [
    { id: "민준(개발팀)", att: 93, streak: 12, sessions: 41, xp: 3120, demo: true },
    { id: "서연(인사팀)", att: 88, streak: 9, sessions: 35, xp: 2660, demo: true },
    { id: "지훈(영업팀)", att: 81, streak: 5, sessions: 33, xp: 2410, demo: true },
    { id: "하은(재무팀)", att: 75, streak: 7, sessions: 28, xp: 2050, demo: true },
    { id: "도윤(생산팀)", att: 69, streak: 3, sessions: 24, xp: 1780, demo: true },
    { id: "수아(품질팀)", att: 63, streak: 2, sessions: 21, xp: 1520, demo: true },
    { id: "현우(구매팀)", att: 50, streak: 0, sessions: 16, xp: 1150, demo: true },
  ];

  // ── 날짜 ──
  function today() { return fmt(new Date()); }
  function fmt(d) {
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }

  // ── 통계 ──
  const BADGES = [
    { id: "first", name: "🎉 첫 발걸음", desc: "첫 운동 완료" },
    { id: "streak3", name: "🔥 3일 연속", desc: "3일 연속 운동" },
    { id: "week", name: "📅 일주일 개근", desc: "7일 연속 운동" },
    { id: "s10", name: "💪 10회 달성", desc: "누적 10회" },
    { id: "s50", name: "🏆 헬창의 길", desc: "누적 50회" },
    { id: "perfect", name: "⭐ 완벽한 하루", desc: "계획 100% 달성" },
    { id: "kcal5000", name: "🔥 5,000kcal", desc: "누적 5,000kcal" },
    { id: "maker", name: "🛠️ 루틴 장인", desc: "나만의 루틴 만들기" },
  ];

  function stats(user) {
    const w = user.workouts || {};
    const dates = Object.keys(w).filter((d) => (w[d].doneSets || 0) > 0).sort();
    const sessions = dates.length;
    let totalKcal = 0, totalSets = 0, anyPerfect = false;
    dates.forEach((d) => { totalKcal += w[d].kcal || 0; totalSets += w[d].doneSets || 0; if ((w[d].scorePct || 0) >= 100) anyPerfect = true; });

    const xp = totalSets * 5 + dates.filter((d) => (w[d].scorePct || 0) >= 100).length * 30;
    const lvl = Math.floor(Math.sqrt(xp / 100)) + 1;
    const curFloor = 100 * (lvl - 1) ** 2, nextAt = 100 * lvl ** 2;

    const dateSet = new Set(dates);
    const streak = calcStreak(dateSet);
    const best = bestStreak(dates);

    const got = [];
    if (sessions >= 1) got.push("first");
    if (best >= 3) got.push("streak3");
    if (best >= 7) got.push("week");
    if (sessions >= 10) got.push("s10");
    if (sessions >= 50) got.push("s50");
    if (anyPerfect) got.push("perfect");
    if (totalKcal >= 5000) got.push("kcal5000");
    if ((user.customs || []).length > 0) got.push("maker");

    return {
      sessions, totalKcal: Math.round(totalKcal), totalSets,
      xp, level: lvl, toNext: Math.max(0, nextAt - xp),
      progressPct: Math.round((xp - curFloor) / Math.max(1, nextAt - curFloor) * 100),
      streak, best, badges: got, badgeDefs: BADGES,
    };
  }

  function calcStreak(dateSet) {
    if (!dateSet.size) return 0;
    let cur = new Date();
    const has = (d) => dateSet.has(fmt(d));
    if (!has(cur)) { cur.setDate(cur.getDate() - 1); if (!has(cur)) return 0; }
    let n = 0;
    while (has(cur)) { n++; cur.setDate(cur.getDate() - 1); }
    return n;
  }
  function bestStreak(dates) {
    if (!dates.length) return 0;
    const ds = dates.map((s) => new Date(s + "T00:00:00")).sort((a, b) => a - b);
    let best = 1, cur = 1;
    for (let i = 1; i < ds.length; i++) {
      const diff = Math.round((ds[i] - ds[i - 1]) / 86400000);
      if (diff === 1) { cur++; best = Math.max(best, cur); } else if (diff > 1) cur = 1;
    }
    return best;
  }

  function consistency28(user, plannedPerWeek) {
    const w = user.workouts || {};
    const cutoff = new Date(); cutoff.setDate(cutoff.getDate() - 28);
    let n = 0;
    Object.keys(w).forEach((d) => {
      if ((w[d].doneSets || 0) > 0 && new Date(d + "T00:00:00") >= cutoff) n++;
    });
    const planned = plannedPerWeek * 4;
    return { done: n, planned, pct: planned ? Math.min(100, Math.round(n / planned * 100)) : 0,
      ratio: planned ? Math.min(1, n / planned) : 0 };
  }

  // 랭킹: 데모 동료 + 이 기기의 실제 사용자들
  function ranking() {
    const db = loadAll();
    const rows = DEMO_RANK.slice();
    Object.keys(db.users).forEach((k) => {
      const u = db.users[k];
      if (!u.routine) return;
      const st = stats(u);
      const cons = consistency28(u, u.routine.days || 3);
      rows.push({ id: u.id, att: cons.pct, streak: st.streak, sessions: st.sessions, xp: st.xp, demo: false });
    });
    return rows;
  }

  return {
    login, logout, getUser, currentId, update, replaceUser,
    saveWorkout, deleteWorkout, saveRun, deleteRun,
    stats, fullStats, consistency28, today, fmt,
    saveCustom, deleteCustom, sharedList, shareRoutine, likeShared, ranking,
  };
})();
