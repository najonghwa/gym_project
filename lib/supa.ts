"use client";
// Supabase 클라이언트 — gym_web과 같은 프로젝트/테이블(gym_users) 공유
// anon 키는 공개 전제 키(RLS 개방, 사내 데모용)
import { createClient, SupabaseClient } from "@supabase/supabase-js";

const SUPABASE_URL = "https://zfecjthzasudouskjusm.supabase.co";
const SUPABASE_ANON_KEY =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpmZWNqdGh6YXN1ZG91c2tqdXNtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM1MzQyMTQsImV4cCI6MjA5OTExMDIxNH0.gAKb-wZTRCkumCJOHUM4j0d1vJTXiDMqqrFjJEjalcI";

let client: SupabaseClient | null = null;
function supa(): SupabaseClient {
  if (!client) client = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  return client;
}

// 사용자 데이터 (구버전 gym_web과 호환 — data jsonb 통째)
export type UserData = Record<string, unknown> & {
  id?: string;
  pin?: string;
  profile?: { days?: number; style?: string; weight?: number } & Record<string, unknown>;
  routine?: { days?: number } & Record<string, unknown>;
  workouts?: Record<string, { doneSets?: number; scorePct?: number; kcal?: number }>;
  // route: [lat, lng, 경과초?] — 경과초는 구간 페이스 계산용 (GPS 기록만)
  runs?: { rid?: string; date: string; km: number; paceSec?: number | null; durSec?: number; route?: number[][] }[];
  runProfile?: Record<string, unknown>;
  v2?: {
    workouts?: Record<string, { items: unknown[] }>;
    primaryMode?: "gym" | "run";
    routineStart?: string; // 루틴 적용 시작일 — 전체 진행률 계산용
    savedRoutines?: string[];
    activeRoutineId?: string;
    runGoalKm?: number;   // 연간 목표 거리
  };
  big3?: { goal: number; logs: { date: string; s: number; b: number; d: number }[] };
};

export async function pullUser(id: string): Promise<UserData | null> {
  try {
    const { data } = await supa()
      .from("gym_users").select("data").eq("id", id.trim().toLowerCase()).maybeSingle();
    return (data?.data as UserData) ?? null;
  } catch { return null; }
}

export async function pushUser(id: string, data: UserData, stats: Record<string, number>) {
  try {
    await supa().from("gym_users").upsert({
      id: id.trim().toLowerCase(), data, stats, updated_at: new Date().toISOString(),
    });
  } catch { /* 오프라인 무시 — 다음 저장 때 재시도 */ }
}

export interface StatRow { id: string; stats: Record<string, number> }
export async function fetchStats(): Promise<StatRow[] | null> {
  try {
    const { data } = await supa().from("gym_users").select("id, stats").limit(200);
    return (data as StatRow[]) ?? [];
  } catch { return null; }
}

// ── Google OAuth (Supabase 대시보드에서 Google provider 활성화 필요) ──
export async function signInWithGoogle(): Promise<string | null> {
  try {
    const { error } = await supa().auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: typeof window !== "undefined" ? `${location.origin}/today` : undefined },
    });
    return error ? error.message : null;
  } catch (e) {
    return e instanceof Error ? e.message : "Google 로그인 실패";
  }
}

// 현재 OAuth 세션의 이메일 (없으면 null) — 리다이렉트 복귀 시 자동 감지
export async function getOAuthEmail(): Promise<string | null> {
  try {
    const { data } = await supa().auth.getSession();
    return data.session?.user?.email ?? null;
  } catch { return null; }
}
