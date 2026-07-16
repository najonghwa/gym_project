"use client";
// 사용자 훅 — id+PIN 로그인(구 gym_web 규칙 호환), localStorage 캐시 + Supabase 동기화
import { useCallback, useEffect, useRef, useState } from "react";
import { getOAuthEmail, pullUser, pushUser, type UserData } from "./supa";
import type { TodayItem } from "./mock/exercises";

const KEY = "gymrun_v1";

interface LocalDB {
  currentId: string | null;
  users: Record<string, UserData>;
}

function loadDB(): LocalDB {
  if (typeof window === "undefined") return { currentId: null, users: {} };
  try { return JSON.parse(localStorage.getItem(KEY) || "") as LocalDB; }
  catch { return { currentId: null, users: {} }; }
}
function saveDB(db: LocalDB) {
  localStorage.setItem(KEY, JSON.stringify(db));
}
const uid = (id: string) => id.trim().toLowerCase();
const today = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};

// ── 통계 (랭킹 stats 호환: att/streak/sessions/xp + 러닝 km) ──
export function computeStats(u: UserData) {
  const legacy = u.workouts ?? {};
  const v2 = u.v2?.workouts ?? {};
  const dates = new Set<string>();
  let totalSets = 0;
  Object.entries(legacy).forEach(([d, w]) => {
    if ((w.doneSets ?? 0) > 0) { dates.add(d); totalSets += w.doneSets ?? 0; }
  });
  Object.entries(v2).forEach(([d, w]) => {
    const done = (w.items as TodayItem[]).reduce((s, it) => s + it.sets.filter((x) => x.done).length, 0);
    if (done > 0) { dates.add(d); totalSets += done; }
  });
  const sessions = dates.size;
  // streak: 오늘/어제부터 연속
  let streak = 0;
  const cur = new Date();
  const has = (d: Date) => dates.has(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`);
  if (!has(cur)) cur.setDate(cur.getDate() - 1);
  while (has(cur)) { streak++; cur.setDate(cur.getDate() - 1); }
  // 4주 출석률
  const cutoff = new Date(); cutoff.setDate(cutoff.getDate() - 28);
  const recent = [...dates].filter((d) => new Date(d + "T00:00:00") >= cutoff).length;
  const perWeek = (u.routine?.days as number) || 4;
  const att = Math.min(100, Math.round((recent / (perWeek * 4)) * 100));
  const xp = totalSets * 5;
  // 러닝(구버전 기록 유지)
  const runs = u.runs ?? [];
  const now = Date.now();
  const km = (msBack: number) =>
    Math.round(runs.filter((r) => now - new Date(r.date + "T00:00:00").getTime() <= msBack)
      .reduce((s, r) => s + r.km, 0) * 10) / 10;
  return {
    att, streak, sessions, xp,
    level: Math.floor(Math.sqrt(xp / 100)) + 1,
    weekKm: km(7 * 864e5), monthKm: km(30 * 864e5),
    totalKm: Math.round(runs.reduce((s, r) => s + r.km, 0) * 10) / 10,
  };
}

// 이번 주(월~일) 요일별 달성%
export function weekCells(u: UserData) {
  const labels = ["월", "화", "수", "목", "금", "토", "일"];
  const now = new Date();
  const mon = new Date(now); mon.setDate(now.getDate() - ((now.getDay() + 6) % 7));
  const todayS = today();
  return labels.map((label, i) => {
    const d = new Date(mon); d.setDate(mon.getDate() + i);
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    const v2w = u.v2?.workouts?.[key];
    let pct: number | null = null;
    if (v2w) {
      const items = v2w.items as TodayItem[];
      const total = items.reduce((s, it) => s + it.sets.length, 0);
      const done = items.reduce((s, it) => s + it.sets.filter((x) => x.done).length, 0);
      pct = total ? Math.round((done / total) * 100) : null;
    } else if (u.workouts?.[key]?.scorePct != null) {
      pct = u.workouts[key].scorePct!;
    } else if (key > todayS) {
      pct = null;
    } else if ((u.workouts?.[key]?.doneSets ?? 0) === 0 && !v2w) {
      pct = key === todayS ? null : 0;
    }
    return { label, pct, isToday: key === todayS };
  });
}

export function useUser() {
  const [user, setUser] = useState<UserData | null>(null);
  const [ready, setReady] = useState(false);
  const pushTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const db = loadDB();
    if (db.currentId && db.users[db.currentId]) {
      setUser(db.users[db.currentId]);
      setReady(true);
      return;
    }
    // Google OAuth 복귀 감지 → 이메일 앞부분을 아이디로 자동 로그인/가입
    getOAuthEmail().then(async (email) => {
      if (email) {
        const id = email.split("@")[0];
        const server = await pullUser(id);
        const u: UserData = server
          ? { ...server, id, oauth: "google" }
          : { id, oauth: "google", created: today(), v2: { workouts: {} } };
        const db2 = loadDB();
        db2.users[uid(id)] = u; db2.currentId = uid(id); saveDB(db2);
        setUser(u);
        pushUser(uid(id), u, computeStats(u));
      }
      setReady(true);
    });
  }, []);

  const persist = useCallback((u: UserData) => {
    const db = loadDB();
    const k = uid(String(u.id));
    db.users[k] = u; db.currentId = k;
    saveDB(db);
    setUser({ ...u });
    // debounce 서버 푸시
    if (pushTimer.current) clearTimeout(pushTimer.current);
    pushTimer.current = setTimeout(() => pushUser(k, u, computeStats(u)), 800);
  }, []);

  const login = useCallback(async (id: string, pin: string): Promise<string | null> => {
    const server = await pullUser(id);
    const db = loadDB();
    const local = db.users[uid(id)];
    const base = server ?? local;
    if (!base) return "등록되지 않은 아이디예요. '처음이에요'에서 만들 수 있어요.";
    if (base.pin && base.pin !== pin) return "PIN이 일치하지 않아요.";
    const u: UserData = { ...base, id: id.trim(), pin: base.pin || pin };
    persist(u);
    return null;
  }, [persist]);

  const signup = useCallback(async (id: string, pin: string, primaryMode: "gym" | "run" = "gym"): Promise<string | null> => {
    const server = await pullUser(id);
    const db = loadDB();
    if (server || db.users[uid(id)]) return "이미 사용 중인 아이디예요.";
    persist({ id: id.trim(), pin, created: today(), v2: { workouts: {}, primaryMode } });
    return null;
  }, [persist]);

  // 주 종목(첫 화면) 변경 — 설정 시트에서 사용
  const setPrimaryMode = useCallback((mode: "gym" | "run") => {
    setUser((prev) => {
      if (!prev) return prev;
      const u: UserData = { ...prev, v2: { ...prev.v2, primaryMode: mode } };
      persist(u);
      return u;
    });
  }, [persist]);

  const logout = useCallback(() => {
    const db = loadDB(); db.currentId = null; saveDB(db);
    setUser(null);
  }, []);

  // 오늘 운동 저장 (v2 네임스페이스 — 구버전 데이터 보존)
  const saveToday = useCallback((items: TodayItem[]) => {
    setUser((prev) => {
      if (!prev) return prev;
      const u: UserData = {
        ...prev,
        v2: { ...prev.v2, workouts: { ...prev.v2?.workouts, [today()]: { items } } },
      };
      persist(u);
      return u;
    });
  }, [persist]);

  // 루틴 저장/적용 (v2.savedRoutines / v2.activeRoutineId)
  const toggleSaveRoutine = useCallback((id: string) => {
    setUser((prev) => {
      if (!prev) return prev;
      const cur = (prev.v2?.savedRoutines as string[] | undefined) ?? [];
      const next = cur.includes(id) ? cur.filter((x) => x !== id) : [...cur, id];
      const u: UserData = { ...prev, v2: { ...prev.v2, savedRoutines: next } };
      persist(u);
      return u;
    });
  }, [persist]);

  const setActiveRoutine = useCallback((id: string | null) => {
    setUser((prev) => {
      if (!prev) return prev;
      const u: UserData = {
        ...prev,
        v2: { ...prev.v2, activeRoutineId: id ?? undefined, routineStart: id ? today() : undefined },
      };
      persist(u);
      return u;
    });
  }, [persist]);

  // 러닝 기록 추가 (구버전 runs와 같은 형태 — 데이터 호환, GPS는 durSec/route 추가)
  const saveRun = useCallback((run: { date: string; km: number; paceSec: number | null; durSec?: number; route?: number[][] }) => {
    setUser((prev) => {
      if (!prev) return prev;
      const runs = [...(prev.runs ?? []), { rid: "r" + Date.now(), ...run }];
      runs.sort((a, b) => (a.date < b.date ? -1 : 1));
      const u: UserData = { ...prev, runs };
      persist(u);
      return u;
    });
  }, [persist]);

  // 러닝 기록 삭제 (rid 우선, 없으면 날짜+거리 첫 매치)
  const deleteRun = useCallback((target: { rid?: string; date: string; km: number }) => {
    setUser((prev) => {
      if (!prev) return prev;
      const runs = [...(prev.runs ?? [])];
      const idx = runs.findIndex((r) =>
        target.rid ? r.rid === target.rid : r.date === target.date && r.km === target.km
      );
      if (idx < 0) return prev;
      runs.splice(idx, 1);
      const u: UserData = { ...prev, runs };
      persist(u);
      return u;
    });
  }, [persist]);

  // 연간 목표 거리
  const setRunGoal = useCallback((km: number) => {
    setUser((prev) => {
      if (!prev) return prev;
      const u: UserData = { ...prev, v2: { ...prev.v2, runGoalKm: km } };
      persist(u);
      return u;
    });
  }, [persist]);

  // 러닝 성향 프로필 (진단 결과)
  const saveRunProfile = useCallback((profile: Record<string, unknown>) => {
    setUser((prev) => {
      if (!prev) return prev;
      const u: UserData = { ...prev, runProfile: { ...prev.runProfile, ...profile } };
      persist(u);
      return u;
    });
  }, [persist]);

  // 3대 측정 기록 (구버전 big3와 같은 형태 — 데이터 호환)
  const saveBig3 = useCallback((goal: number, log?: { s: number; b: number; d: number }) => {
    setUser((prev) => {
      if (!prev) return prev;
      const old = (prev.big3 as { goal: number; logs: { date: string; s: number; b: number; d: number }[] } | undefined);
      const logs = (old?.logs ?? []).filter((l) => !log || l.date !== today());
      if (log) logs.push({ date: today(), ...log });
      const u: UserData = { ...prev, big3: { goal, logs } };
      persist(u);
      return u;
    });
  }, [persist]);

  return {
    user, ready, login, signup, logout, saveToday,
    toggleSaveRoutine, setActiveRoutine, saveBig3,
    saveRun, deleteRun, setRunGoal, saveRunProfile, setPrimaryMode, today,
  };
}
