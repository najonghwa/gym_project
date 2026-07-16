"use client";
// 랭킹 — Supabase gym_users.stats 실데이터 (구/신 앱 공용)
import { useEffect, useMemo, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { fadeUp, staggerContainer } from "@/lib/motion";
import { fetchStats, type StatRow } from "@/lib/supa";
import { useUser } from "@/lib/useUser";

const METRICS = [
  { id: "att", t: "출석률", unit: "%" },
  { id: "streak", t: "연속", unit: "일" },
  { id: "xp", t: "XP", unit: "" },
  { id: "weekKm", t: "러닝", unit: "km" },
] as const;

// 서버 미응답 시 데모
const DEMO: StatRow[] = [
  { id: "민준(개발팀)", stats: { att: 93, streak: 12, xp: 3120, weekKm: 24.5 } },
  { id: "서연(인사팀)", stats: { att: 88, streak: 9, xp: 2660, weekKm: 18.2 } },
  { id: "지훈(영업팀)", stats: { att: 81, streak: 5, xp: 2410, weekKm: 15 } },
  { id: "하은(재무팀)", stats: { att: 75, streak: 7, xp: 2050, weekKm: 9.6 } },
];

export default function RankingPage() {
  const reduce = useReducedMotion();
  const { user } = useUser();
  const [rows, setRows] = useState<StatRow[] | null>(null);
  const [demo, setDemo] = useState(false);
  const [metric, setMetric] = useState<(typeof METRICS)[number]["id"]>("att");

  useEffect(() => {
    fetchStats().then((r) => {
      if (r && r.length) setRows(r);
      else { setRows(DEMO); setDemo(true); }
    });
  }, []);

  const sorted = useMemo(
    () => [...(rows ?? [])].sort((a, b) => (b.stats?.[metric] ?? 0) - (a.stats?.[metric] ?? 0)),
    [rows, metric]
  );
  const me = String(user?.id ?? "").toLowerCase();
  const m = METRICS.find((x) => x.id === metric)!;

  return (
    <main className="lg:mx-auto lg:max-w-xl lg:pt-10">
      <div className="lab mb-1">RANKING 사내 랭킹 {demo && "· 예시"}</div>
      <h2 className="font-display text-[26px]">누가 제일 꾸준할까?</h2>

      <div className="mt-4 grid grid-cols-4 gap-1 rounded-lg border border-white/10 bg-white/5 p-1">
        {METRICS.map((mm) => (
          <button
            key={mm.id}
            onClick={() => setMetric(mm.id)}
            className={`rounded-full py-2 text-[12.5px] font-bold ${metric === mm.id ? "bg-volt text-black" : "text-white/50"}`}
          >
            {mm.t}
          </button>
        ))}
      </div>

      {!rows ? (
        <p className="mt-8 text-center text-[13px] text-white/40">불러오는 중…</p>
      ) : (
        <motion.div
          className="mt-4 space-y-2"
          variants={reduce ? undefined : staggerContainer}
          initial={reduce ? false : "hidden"}
          animate="show"
          key={metric}
        >
          {sorted.map((r, i) => {
            const isMe = r.id.toLowerCase() === me;
            const v = r.stats?.[metric] ?? 0;
            return (
              <motion.div
                key={r.id}
                variants={reduce ? undefined : fadeUp}
                className={`flex items-center gap-3 rounded-lg border px-4 py-3 ${
                  isMe ? "border-volt bg-volt/10" : "border-white/[0.06] bg-card"
                }`}
              >
                <span className="w-8 text-center font-display text-[17px]">
                  {["🥇", "🥈", "🥉"][i] ?? i + 1}
                </span>
                <span className="min-w-0 flex-1 truncate text-[14px] font-bold">
                  {r.id}
                  {isMe && <span className="ml-1.5 rounded bg-volt px-1.5 py-0.5 text-[10px] font-extrabold text-black">나</span>}
                </span>
                <b className={`font-display text-[17px] tabular-nums ${isMe ? "text-volt" : ""}`}>
                  {v.toLocaleString()}<span className="ml-0.5 text-[10px] text-white/40">{m.unit}</span>
                </b>
              </motion.div>
            );
          })}
        </motion.div>
      )}
      <p className="mt-4 text-[11.5px] leading-relaxed text-white/35">
        출석률 = 최근 4주 계획 대비 운동일 · 구버전 앱 사용자와 같은 랭킹을 공유해요.
      </p>
    </main>
  );
}
