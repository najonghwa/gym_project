"use client";
// 분석 탭 — 헬스 코치 리포트 + 러닝 상세 분석 (세그먼트)
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Big3Card } from "@/components/analysis/Big3Card";
import { RecoveryMap } from "@/components/recovery/RecoveryMap";
import { PRChart } from "@/components/charts/PRChart";
import { RunAnalysis } from "@/components/run/RunAnalysis";
import { CoachBubble, PandaCoach } from "@/components/mascot/PandaCoach";
import { LoginCard } from "@/components/auth/LoginCard";
import { getMockRecovery } from "@/lib/mock/recovery";
import { EXPLORE } from "@/lib/mock/routines";
import { computeStats, useUser } from "@/lib/useUser";
import { coachReport } from "@/lib/coach";

type Run = { date: string; km: number; paceSec?: number | null };


// 섹션 헤더 — 볼트 틱 + 번호
function Sec({ n, title, sub }: { n: string; title: string; sub?: string }) {
  return (
    <div className="mb-2.5 flex items-center gap-2.5">
      <span className="grid h-6 w-6 shrink-0 place-items-center rounded-md bg-volt/15 font-display text-[12px] text-volt">{n}</span>
      <div>
        <h2 className="font-display text-[16px] leading-none tracking-tight">{title}</h2>
        {sub && <p className="mt-0.5 text-[11px] text-white/40">{sub}</p>}
      </div>
    </div>
  );
}

const Card = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <div className={`rounded-2xl border border-white/[0.06] bg-card p-4 ${className}`}>{children}</div>
);

// 부위별 볼륨 바 — MEV/MRV 존 마커 + 상태 색 (코치 리포트 시그니처)
function VolumeBar({ row }: { row: ReturnType<typeof coachReport>["muscleVol"][number] }) {
  const scale = Math.max(row.mrv * 1.2, row.sets, 1);
  const fillColor = row.status === "low" ? "#f59e0b" : row.status === "high" ? "#ef4444" : "#c8ff00";
  const statusKr = row.status === "low" ? "부족" : row.status === "high" ? "과다" : "최적";
  return (
    <div className="flex items-center gap-2.5">
      <span className="w-11 shrink-0 text-[12px] font-bold text-white/65">{row.kr}</span>
      <div className="relative h-4 flex-1 overflow-hidden rounded-md bg-white/[0.05]">
        {/* MEV~MRV 최적 존 */}
        <div className="absolute inset-y-0 bg-white/[0.05]" style={{ left: `${(row.mev / scale) * 100}%`, width: `${((row.mrv - row.mev) / scale) * 100}%` }} />
        {/* 채움 */}
        <div className="absolute inset-y-0 left-0 rounded-r-sm" style={{ width: `${(row.sets / scale) * 100}%`, background: fillColor, opacity: 0.85 }} />
        {/* MEV·MRV 눈금 */}
        <span className="absolute inset-y-0 w-px bg-white/25" style={{ left: `${(row.mev / scale) * 100}%` }} />
        <span className="absolute inset-y-0 w-px bg-white/25" style={{ left: `${(row.mrv / scale) * 100}%` }} />
      </div>
      <b className="w-10 shrink-0 text-right text-[12px] tabular-nums">{row.sets}</b>
      <span
        className="w-9 shrink-0 text-right text-[10.5px] font-bold"
        style={{ color: fillColor }}
      >
        {statusKr}
      </span>
    </div>
  );
}

export default function AnalysisPage() {
  const router = useRouter();
  const { user, ready, login, signup, saveBig3 } = useUser();
  const [mode, setMode] = useState<"gym" | "run">("gym");
  const recovery = useMemo(() => getMockRecovery(), []);
  const st = useMemo(() => (user ? computeStats(user) : null), [user]);

  const weekTarget = useMemo(
    () => EXPLORE.find((x) => x.id === user?.v2?.activeRoutineId)?.daysPerWeek ?? 4,
    [user]
  );
  const rep = useMemo(() => (user ? coachReport(user, weekTarget) : null), [user, weekTarget]);

  if (!ready) return null;
  if (!user) return <main className="lg:pt-10"><LoginCard onLogin={login} onSignup={signup} /></main>;
  if (!rep) return null;

  const verdictMap = {
    progress: { t: "잘 늘고 있어요", d: "중량·볼륨이 상승 중 — 진행성 과부하가 작동하고 있어요", c: "#c8ff00", em: "📈" },
    hold: { t: "유지 구간이에요", d: "큰 변화 없이 볼륨을 지키는 중 — 다음 주 살짝 올려볼까요?", c: "#f59e0b", em: "➡️" },
    decline: { t: "볼륨이 줄었어요", d: "지난주보다 훈련량이 감소 — 회복 주간이거나 점검이 필요해요", c: "#ef4444", em: "📉" },
    nodata: { t: "데이터를 모으는 중", d: "이번 주 기록이 쌓이면 진행 상태를 평가해 드려요", c: "#a1a1aa", em: "⏳" },
  }[rep.verdict];

  const noteStyle = { good: "border-volt/30 bg-volt/[0.06]", warn: "border-danger/30 bg-danger/[0.06]", tip: "border-white/10 bg-white/[0.03]" };
  const noteIcon = { good: "✅", warn: "⚠️", tip: "💡" };

  const ratioBar = (a: number, b: number, la: string, lb: string) => {
    const tot = a + b || 1;
    return (
      <div>
        <div className="flex justify-between text-[11.5px] font-bold">
          <span className="text-volt">{la} {a}</span>
          <span className="text-white/50">{lb} {b}</span>
        </div>
        <div className="mt-1 flex h-3 overflow-hidden rounded-full bg-white/[0.06]">
          <div className="bg-volt" style={{ width: `${(a / tot) * 100}%` }} />
          <div className="bg-white/25" style={{ width: `${(b / tot) * 100}%` }} />
        </div>
      </div>
    );
  };

  const runs = (user.runs ?? []) as Run[];

  return (
    <main className="mx-auto max-w-3xl space-y-5 lg:max-w-5xl lg:pt-10">
      {/* 헤더 — 코치 판다 소개 */}
      <div>
        <div className="lab mb-2">COACH REPORT · {new Date().getMonth() + 1}월 {Math.ceil(new Date().getDate() / 7)}주차</div>
        <CoachBubble tone="volt" size={72}>
          <b className="text-white">{String(user.id)}님, 코치예요.</b> {mode === "run"
            ? "이번 달 러닝을 뜯어봤어요 — 거리·페이스·꾸준함까지 아래에 정리했어요."
            : "이번 주 훈련을 코치 눈으로 봤어요. 볼륨·진행·밸런스를 아래에서 짚어줄게요."}
        </CoachBubble>
      </div>

      {/* 헬스 / 러닝 세그먼트 */}
      <div className="grid grid-cols-2 gap-1 rounded-lg border border-white/10 bg-white/5 p-1">
        {(["gym", "run"] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`rounded-md py-2.5 text-[14px] font-bold ${mode === m ? "bg-volt text-black" : "text-white/50"}`}
          >
            {m === "gym" ? "헬스 리포트" : "러닝 분석"}
          </button>
        ))}
      </div>

      {mode === "run" ? (
        <section className="space-y-5">
          <RunAnalysis runs={runs} />
        </section>
      ) : (
      <>
      {/* 1. 이번 주 요약 */}
      <section>
        <Sec n="1" title="이번 주 요약" sub="THIS WEEK" />
        <div className="grid grid-cols-2 gap-2.5 lg:grid-cols-4">
          <Card className="!p-3.5">
            <div className="lab">세션</div>
            <div className="mt-1 flex items-end gap-1">
              <span className="font-display text-[30px] leading-none">{rep.weekSessions}</span>
              <span className="pb-1 text-[12px] text-white/45">/ {rep.weekTarget}회</span>
            </div>
          </Card>
          <Card className="!p-3.5">
            <div className="lab">순응도</div>
            <div className="mt-1 flex items-end gap-1">
              <span className={`font-display text-[30px] leading-none ${rep.adherence >= 100 ? "text-volt" : rep.adherence >= 60 ? "" : "text-gold"}`}>{rep.adherence}</span>
              <span className="pb-1 text-[12px] text-white/45">%</span>
            </div>
          </Card>
          <Card className="!p-3.5">
            <div className="lab">주간 볼륨</div>
            <div className="mt-1 flex items-end gap-1">
              <span className="font-display text-[26px] leading-none tabular-nums">{rep.weekTonnage.toLocaleString()}</span>
              <span className="pb-1 text-[12px] text-white/45">kg</span>
            </div>
            {rep.tonnageDelta != null && (
              <div className={`mt-0.5 text-[11px] font-bold ${rep.tonnageDelta >= 0 ? "text-volt" : "text-danger"}`}>
                {rep.tonnageDelta >= 0 ? "▲" : "▼"} {Math.abs(rep.tonnageDelta)}% vs 지난주
              </div>
            )}
          </Card>
          <Card className="!p-3.5">
            <div className="lab">연속</div>
            <div className="mt-1 flex items-end gap-1">
              <span className={`font-display text-[30px] leading-none ${(st?.streak ?? 0) > 0 ? "text-volt" : "text-white/30"}`}>{st?.streak ?? 0}</span>
              <span className="pb-1 text-[12px] text-white/45">일 🔥</span>
            </div>
          </Card>
        </div>
      </section>

      {/* 2. 진행 평가 */}
      <section>
        <Sec n="2" title="진행 평가" sub="이번 주, 나아지고 있나요?" />
        <Card>
          <div className="flex items-start gap-3">
            <span className="text-[30px] leading-none">{verdictMap.em}</span>
            <div className="min-w-0">
              <b className="text-[17px] font-extrabold" style={{ color: verdictMap.c }}>{verdictMap.t}</b>
              <p className="mt-0.5 text-[12.5px] leading-relaxed text-white/60">{verdictMap.d}</p>
            </div>
          </div>
          {rep.e1rmTop.length > 0 && (
            <>
              <div className="lab mb-2 mt-4">주요 종목 추정 1RM · 지난주 대비</div>
              <div className="space-y-1.5">
                {rep.e1rmTop.map((e) => (
                  <div key={e.id} className="flex items-center gap-2.5">
                    <span className="min-w-0 flex-1 truncate text-[13px] font-bold text-white/80">{e.name}</span>
                    <b className="text-[14px] tabular-nums">{e.cur}<span className="text-[10px] text-white/40">kg</span></b>
                    <span className={`w-14 text-right text-[11.5px] font-bold ${e.deltaPct == null ? "text-white/30" : e.deltaPct > 0 ? "text-volt" : e.deltaPct < 0 ? "text-danger" : "text-white/40"}`}>
                      {e.deltaPct == null ? "신규" : `${e.deltaPct > 0 ? "▲" : e.deltaPct < 0 ? "▼" : "―"} ${Math.abs(e.deltaPct)}%`}
                    </span>
                  </div>
                ))}
              </div>
              <p className="mt-2 text-[10.5px] text-white/35">추정 1RM = 중량 × (1 + 횟수/30) · 실제 1RM 테스트 없이 근력 추세를 봅니다</p>
            </>
          )}
        </Card>
      </section>

      {/* 3. 부위별 볼륨 진단 — 시그니처 */}
      <section>
        <Sec n="3" title="부위별 볼륨 진단" sub="이번 주 세트 수를 근거 기반 권장 범위와 비교" />
        <Card>
          {rep.muscleVol.some((m) => m.sets > 0) ? (
            <>
              <div className="space-y-2.5">
                {rep.muscleVol.map((m) => <VolumeBar key={m.muscle} row={m} />)}
              </div>
              <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-white/[0.06] pt-3 text-[10.5px] text-white/45">
                <span className="flex items-center gap-1.5"><i className="h-2.5 w-2.5 rounded-sm bg-gold" />부족 (MEV 미만)</span>
                <span className="flex items-center gap-1.5"><i className="h-2.5 w-2.5 rounded-sm bg-volt" />최적 (MEV~MRV)</span>
                <span className="flex items-center gap-1.5"><i className="h-2.5 w-2.5 rounded-sm bg-danger" />과다 (MRV 초과)</span>
                <span className="text-white/30">| 세로선 = 최소·최대 권장선</span>
              </div>
              {rep.weakest && (
                <button
                  onClick={() => router.push("/routine")}
                  className="mt-3 flex w-full items-center justify-between rounded-lg border border-gold/30 bg-gold/[0.07] px-3.5 py-2.5 text-[12.5px] font-bold text-gold"
                >
                  <span>가장 부족한 부위: {rep.weakest.kr} — 보강 루틴 받기</span>
                  <span>→</span>
                </button>
              )}
            </>
          ) : (
            <p className="py-6 text-center text-[12.5px] text-white/40">이번 주 완료한 세트가 아직 없어요 — 오늘 운동을 기록하면 진단이 나와요</p>
          )}
        </Card>
      </section>

      {/* 4. 밸런스 */}
      <section>
        <Sec n="4" title="밸런스" sub="근육 균형 — 한쪽으로 치우치면 부상 위험" />
        <div className="grid gap-2.5 lg:grid-cols-2">
          <Card>
            <div className="lab mb-2">밀기 vs 당기기</div>
            {rep.pushSets + rep.pullSets > 0
              ? ratioBar(rep.pushSets, rep.pullSets, "밀기", "당기기")
              : <p className="py-2 text-center text-[12px] text-white/40">기록 없음</p>}
            <p className="mt-2 text-[10.5px] text-white/40">이상적 비율 약 1:1 — 어깨 건강의 핵심</p>
          </Card>
          <Card>
            <div className="lab mb-2">상체 vs 하체</div>
            {rep.upperSets + rep.lowerSets > 0
              ? ratioBar(rep.upperSets, rep.lowerSets, "상체", "하체")
              : <p className="py-2 text-center text-[12px] text-white/40">기록 없음</p>}
            <p className="mt-2 text-[10.5px] text-white/40">하체를 거르지 않는 게 장기 성장의 비결</p>
          </Card>
        </div>
      </section>

      {/* 5. 근력 추이 */}
      <section>
        <Sec n="5" title="근력 추이" sub="종목별 기록과 3대 목표" />
        <div className="grid gap-2.5 lg:grid-cols-2 lg:items-start">
          <Card><PRChart selectable /></Card>
          <Card><Big3Card big3={user.big3} onSave={saveBig3} /></Card>
        </div>
      </section>

      {/* 6. 회복 & 빈도 */}
      <section>
        <Sec n="6" title="회복 & 빈도" sub="부위별 회복 상태와 이번 주 자극 빈도" />
        <div className="grid gap-2.5 lg:grid-cols-2 lg:items-start">
          <Card><RecoveryMap data={recovery} /></Card>
          <Card>
            <div className="lab mb-2">이번 주 부위별 빈도 <span className="font-normal normal-case text-white/35">— 주 2회가 성장에 최적</span></div>
            {rep.freq.length ? (
              <div className="space-y-2">
                {rep.freq.map((f) => (
                  <div key={f.muscle} className="flex items-center gap-2.5">
                    <span className="w-11 shrink-0 text-[12px] font-bold text-white/65">{f.kr}</span>
                    <div className="flex gap-1">
                      {Array.from({ length: Math.max(3, f.timesPerWeek) }, (_, i) => (
                        <span key={i} className={`h-2.5 w-6 rounded-sm ${i < f.timesPerWeek ? "bg-volt" : "bg-white/[0.08]"}`} />
                      ))}
                    </div>
                    <b className="ml-auto text-[12px] tabular-nums">주 {f.timesPerWeek}회</b>
                  </div>
                ))}
              </div>
            ) : (
              <p className="py-4 text-center text-[12px] text-white/40">이번 주 기록이 쌓이면 표시돼요</p>
            )}
          </Card>
        </div>
      </section>

      {/* 7. 코치 코멘트 — 판다 코치가 정리 (출석 달력은 헬스 홈으로) */}
      <section>
        <Sec n="7" title="코치 코멘트" sub="데이터 기반 이번 주 실행 제안" />
        <div className="flex items-start gap-3">
          <div className="hidden shrink-0 sm:block"><PandaCoach size={64} /></div>
          <div className="flex-1 space-y-2">
            {rep.notes.map((note, i) => (
              <div key={i} className={`flex items-start gap-2.5 rounded-lg border p-3 ${noteStyle[note.tone]}`}>
                <span className="text-[14px] leading-none">{noteIcon[note.tone]}</span>
                <p className="text-[12.5px] leading-relaxed text-white/80">{note.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      </>
      )}
    </main>
  );
}
