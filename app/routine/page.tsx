"use client";
// 루틴 탭 — 내 루틴(저장·적용) + 맞춤 추천(13종 점수화) + Explore
import { useState } from "react";
import { useRouter } from "next/navigation";
import { PillButton } from "@/components/ui/PillButton";
import { ColorInitialBadge } from "@/components/ui/ColorInitialBadge";
import { CoachBubble } from "@/components/mascot/PandaCoach";
import { RoutineGenerating } from "@/components/routine/RoutineGenerating";
import { ExploreSection } from "@/components/routine/ExploreSection";
import { ExThumb } from "@/components/ui/ExThumb";
import { ExerciseInfoSheet } from "@/components/workout/ExerciseInfoSheet";
import { EXPLORE, type ExploreRoutine } from "@/lib/mock/routines";
import { byId, itemsFromExercises, type Exercise } from "@/lib/mock/exercises";
import { useUser } from "@/lib/useUser";

type Phase = "idle" | "ask" | "generating" | "result";
type Goal = "strength" | "size" | "fit" | "lower" | "arms";

const GOALS: { v: Goal; t: string; d: string }[] = [
  { v: "strength", t: "💪 힘 키우기", d: "3대 중량 늘리기" },
  { v: "size", t: "🫄 몸 키우기", d: "근육 크기·벌크업" },
  { v: "fit", t: "🔥 다이어트·체력", d: "짧고 자주, 전신" },
  { v: "lower", t: "🦵 하체 보강", d: "하체 위주로" },
  { v: "arms", t: "🦾 팔 보강", d: "이두·삼두 위주로" },
];
const EXPS = ["초급", "중급", "고급"] as const;
const DAYS = [2, 3, 4, 6];

// 프로그램 점수화 — 목표/경력/주당 횟수 매칭
const GOAL_FIT: Record<Goal, string[]> = {
  strength: ["st55", "ss", "madcow", "five31", "texas", "smolov"],
  size: ["phat", "ppl", "gvt", "bro", "arnold", "phul", "icf"],
  fit: ["fullbody3", "upperlower", "quickfit", "ppl"],
  lower: ["legday", "supersquat"],
  arms: ["arms"],
};
const LV = { 초급: 0, 중급: 1, 고급: 2 } as const;

function recommend(goal: Goal, exp: (typeof EXPS)[number], days: number) {
  return EXPLORE.map((r) => {
    let score = 0;
    const reasons: string[] = [];
    if (GOAL_FIT[goal].includes(r.id)) {
      score += GOAL_FIT[goal].indexOf(r.id) === 0 ? 5 : 4;
      reasons.push(GOALS.find((g) => g.v === goal)!.t.slice(2).trim() + "에 잘 맞는 프로그램");
    }
    const lvGap = Math.abs(LV[r.level] - LV[exp]);
    if (lvGap === 0) { score += 3; reasons.push(`${exp}자에게 딱 맞는 난이도`); }
    else if (lvGap === 1) score += 1;
    else score -= 3;
    const dGap = Math.abs(r.daysPerWeek - days);
    if (dGap === 0) { score += 3; reasons.push(`주 ${days}회 계획과 일치`); }
    else if (dGap === 1) { score += 1; reasons.push(`주 ${r.daysPerWeek}회로 계획과 비슷`); }
    else score -= 2;
    return { r, score: score + r.likes / 1000, reasons };
  })
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);
}

export default function RoutinePage() {
  const router = useRouter();
  const { user, toggleSaveRoutine, setActiveRoutine, saveToday } = useUser();
  const [phase, setPhase] = useState<Phase>("idle");
  const [goal, setGoal] = useState<Goal | null>(null);
  const [exp, setExp] = useState<(typeof EXPS)[number] | null>(null);
  const [days, setDays] = useState<number | null>(null);
  const [exInfo, setExInfo] = useState<Exercise | null>(null);
  const recs = goal && exp && days ? recommend(goal, exp, days) : [];

  const savedIds = user?.v2?.savedRoutines ?? [];
  const activeId = user?.v2?.activeRoutineId;
  const savedRoutines = EXPLORE.filter((r) => savedIds.includes(r.id));

  // 루틴 적용 = 오늘 운동을 그 루틴 구성으로 교체 + 사용 중 표시
  const apply = (r: ExploreRoutine) => {
    saveToday(itemsFromExercises(r.exercises));
    setActiveRoutine(r.id);
    router.push("/today");
  };

  return (
    <main className="space-y-6 lg:max-w-none lg:pt-10">
      {/* 내 루틴 (저장한 것들) */}
      <section>
        <div className="lab mb-2">MY ROUTINES 내 루틴</div>
        {savedRoutines.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-white/15 bg-white/[0.02] px-5 py-6 text-center">
            <p className="text-[13px] text-white/50">
              아직 저장한 루틴이 없어요.<br />아래에서 💾 저장하면 여기 모여요.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {savedRoutines.map((r, i) => {
              const active = r.id === activeId;
              return (
                <div
                  key={r.id}
                  className={`flex items-center gap-3 rounded-2xl border p-3.5 ${
                    active ? "border-volt/50 bg-volt/[0.06]" : "border-white/[0.06] bg-card"
                  }`}
                >
                  {(() => { const fe = byId(r.exercises[0]); return fe ? <ExThumb ex={fe} size={48} rounded="rounded-xl" /> : <ColorInitialBadge text={r.badge} seed={i} />; })()}
                  <div className="min-w-0 flex-1">
                    <b className="block truncate text-[14.5px]">
                      {r.title}
                      {active && <span className="ml-1.5 rounded bg-volt px-1.5 py-0.5 text-[9.5px] font-extrabold text-black">사용 중</span>}
                    </b>
                    <span className="text-[11.5px] text-white/45">{r.weeks}주 · 주 {r.daysPerWeek}회 · {r.level}</span>
                  </div>
                  {!active && (
                    <button
                      onClick={() => apply(r)}
                      className="shrink-0 rounded-full bg-volt px-3.5 py-2 text-[12px] font-extrabold text-black"
                    >
                      오늘 적용
                    </button>
                  )}
                  <button
                    onClick={() => { toggleSaveRoutine(r.id); if (active) setActiveRoutine(null); }}
                    className="shrink-0 px-1 text-[13px] text-white/35"
                    aria-label="저장 해제"
                  >✕</button>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* 맞춤 추천 — 판다 코치가 골라줌 */}
      {phase === "idle" && (
        <section className="rounded-2xl border border-white/[0.06] bg-card p-5">
          <CoachBubble tone="volt" size={72}>
            어떤 루틴을 할지 모르겠어요? <b className="text-white">세 가지만 답하면</b> {EXPLORE.length}개 프로그램 중에서 딱 맞는 걸 골라줄게요.
          </CoachBubble>
          <PillButton className="mt-3 w-full" onClick={() => setPhase("ask")}>✨ 코치에게 루틴 추천받기</PillButton>
        </section>
      )}

      {phase === "ask" && (
        <section className="rounded-2xl border border-white/[0.06] bg-card p-5">
          <b className="text-[16px] font-extrabold">세 가지만 알려주세요</b>

          <div className="lab mb-1.5 mt-4">1. 목표가 뭐예요?</div>
          <div className="grid grid-cols-2 gap-1.5 sm:grid-cols-3 lg:grid-cols-5">
            {GOALS.map((g) => (
              <button
                key={g.v}
                onClick={() => setGoal(g.v)}
                className={`rounded-lg border p-2.5 text-left ${goal === g.v ? "border-volt bg-volt/10" : "border-white/10 bg-white/[0.03]"}`}
              >
                <div className={`text-[13px] font-extrabold ${goal === g.v ? "text-volt" : ""}`}>{g.t}</div>
                <div className="mt-0.5 text-[10.5px] text-white/45">{g.d}</div>
              </button>
            ))}
          </div>

          <div className="lab mb-1.5 mt-4">2. 헬스 경력은?</div>
          <div className="grid grid-cols-3 gap-1.5">
            {EXPS.map((e) => (
              <button
                key={e}
                onClick={() => setExp(e)}
                className={`rounded-lg border py-2.5 text-[13px] font-bold ${exp === e ? "border-volt bg-volt/10 text-volt" : "border-white/10 bg-white/[0.03]"}`}
              >
                {e === "초급" ? "1년 미만" : e === "중급" ? "1~3년" : "3년 이상"}
              </button>
            ))}
          </div>

          <div className="lab mb-1.5 mt-4">3. 주에 몇 번 올 수 있어요?</div>
          <div className="grid grid-cols-4 gap-1.5">
            {DAYS.map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`rounded-lg border py-2.5 text-[13px] font-bold ${days === d ? "border-volt bg-volt/10 text-volt" : "border-white/10 bg-white/[0.03]"}`}
              >
                {d === 6 ? "5~6회" : `${d}회`}
              </button>
            ))}
          </div>

          <PillButton
            className="mt-5 w-full py-4"
            disabled={!goal || !exp || !days}
            onClick={() => setPhase("generating")}
          >
            추천 받기 →
          </PillButton>
        </section>
      )}

      {phase === "generating" && <RoutineGenerating onDone={() => setPhase("result")} />}

      {phase === "result" && recs.length > 0 && (
        <section className="space-y-3">
          <div className="lab">추천 결과 — {EXPLORE.length}개 중 이 3개가 잘 맞아요</div>

          {/* 1순위 */}
          <div className="rounded-2xl border border-volt/40 bg-volt/[0.05] p-4">
            <div className="flex items-start gap-3">
              {(() => { const fe = byId(recs[0].r.exercises[0]); return fe ? <ExThumb ex={fe} size={52} rounded="rounded-xl" /> : <ColorInitialBadge text={recs[0].r.badge} seed={0} />; })()}
              <div className="min-w-0 flex-1">
                <span className="rounded bg-volt px-1.5 py-0.5 text-[9.5px] font-extrabold text-black">BEST</span>
                <b className="mt-1 block text-[16px]">{recs[0].r.title}</b>
                <span className="text-[11.5px] text-white/50">
                  {recs[0].r.weeks}주 · 주 {recs[0].r.daysPerWeek}회 · 회당 ~{recs[0].r.durationMin}분 · {recs[0].r.level}
                </span>
              </div>
            </div>
            <div className="mt-2.5 flex flex-wrap gap-1.5">
              {recs[0].reasons.map((why) => (
                <span key={why} className="rounded-full bg-volt/15 px-2.5 py-1 text-[11px] font-bold text-volt">✓ {why}</span>
              ))}
            </div>
            {recs[0].r.who && <p className="mt-2.5 text-[12.5px] leading-relaxed text-white/65">{recs[0].r.who}</p>}
            {recs[0].r.schedule && (
              <p className="mt-2 rounded-lg bg-white/[0.06] px-2.5 py-2 text-[12px] font-bold text-white/75">📆 {recs[0].r.schedule}</p>
            )}
            <div className="mt-2.5 flex items-center gap-1.5 overflow-x-auto">
              {recs[0].r.exercises.map((id) => {
                const ex = byId(id);
                return ex ? (
                  <button key={id} onClick={() => setExInfo(ex)} aria-label={`${ex.name} 정보`}>
                    <ExThumb ex={ex} size={32} />
                  </button>
                ) : null;
              })}
            </div>
            <PillButton className="mt-3 w-full" onClick={() => apply(recs[0].r)}>이 루틴으로 시작 ✅</PillButton>
          </div>

          {/* 2·3순위 */}
          {recs.slice(1).map(({ r, reasons }, i) => (
            <div key={r.id} className="flex items-center gap-3 rounded-2xl border border-white/[0.06] bg-card p-3.5">
              {(() => { const fe = byId(r.exercises[0]); return fe ? <ExThumb ex={fe} size={44} rounded="rounded-xl" /> : <ColorInitialBadge text={r.badge} seed={i + 1} />; })()}
              <div className="min-w-0 flex-1">
                <b className="block truncate text-[14px]">{r.title}</b>
                <span className="text-[11px] text-white/45">
                  주 {r.daysPerWeek}회 · {r.level}{reasons[0] ? ` · ${reasons[0]}` : ""}
                </span>
              </div>
              <button
                onClick={() => apply(r)}
                className="shrink-0 rounded-full border border-white/15 bg-white/5 px-3.5 py-2 text-[12px] font-bold"
              >
                시작
              </button>
            </div>
          ))}

          <button
            onClick={() => { setGoal(null); setExp(null); setDays(null); setPhase("ask"); }}
            className="w-full py-2 text-[12.5px] font-bold text-white/40"
          >
            ← 조건 바꿔서 다시 추천받기
          </button>
        </section>
      )}

      <ExploreSection savedIds={savedIds} onToggleSave={toggleSaveRoutine} onApply={apply} />

      <ExerciseInfoSheet exercise={exInfo} onClose={() => setExInfo(null)} />
    </main>
  );
}
