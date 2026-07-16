"use client";
// GPS 라이브 러닝 — 권한 요청 → 실시간 거리/페이스 → 종료 시 runs에 저장 (durSec/route 포함)
import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { PillButton } from "@/components/ui/PillButton";
import { LoginCard } from "@/components/auth/LoginCard";
import { useUser } from "@/lib/useUser";

type Pt = { lat: number; lng: number; t: number };
type Phase = "idle" | "live" | "paused" | "done";

const EARTH = 6371000;
function hav(a: Pt, b: Pt) {
  const toR = (x: number) => (x * Math.PI) / 180;
  const dLat = toR(b.lat - a.lat), dLng = toR(b.lng - a.lng);
  const s = Math.sin(dLat / 2) ** 2 + Math.cos(toR(a.lat)) * Math.cos(toR(b.lat)) * Math.sin(dLng / 2) ** 2;
  return 2 * EARTH * Math.asin(Math.sqrt(s));
}
const fmtT = (s: number) => {
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), ss = Math.floor(s % 60);
  return (h ? `${h}:` : "") + `${String(m).padStart(h ? 2 : 1, "0")}:${String(ss).padStart(2, "0")}`;
};
const paceStr = (sec: number | null) =>
  sec && isFinite(sec) ? `${Math.floor(sec / 60)}'${String(Math.round(sec % 60)).padStart(2, "0")}"` : "—'——\"";

export default function LiveRunPage() {
  const router = useRouter();
  const { user, ready, login, signup, saveRun, today } = useUser();
  const [phase, setPhase] = useState<Phase>("idle");
  const [distM, setDistM] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [curPace, setCurPace] = useState<number | null>(null);
  const [gpsOk, setGpsOk] = useState(false); // 첫 위치 수신 여부
  const [err, setErr] = useState("");

  const phaseRef = useRef<Phase>("idle");
  const watchRef = useRef<number | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const lastRef = useRef<Pt | null>(null);
  const distRef = useRef(0);
  const winRef = useRef<{ t: number; d: number }[]>([]); // 최근 이동 버퍼(현재 페이스용)
  const routeRef = useRef<number[][]>([]); // [lat, lng, 경과초] — 구간 페이스 계산용
  const startRef = useRef(0);
  const pausedMsRef = useRef(0);
  const pauseAtRef = useRef(0);
  const wakeRef = useRef<{ release: () => Promise<void> } | null>(null);

  phaseRef.current = phase;

  // 화면 꺼짐 방지 (지원 브라우저만)
  const acquireWake = useCallback(async () => {
    try {
      const nav = navigator as Navigator & { wakeLock?: { request: (t: "screen") => Promise<{ release: () => Promise<void> }> } };
      wakeRef.current = (await nav.wakeLock?.request("screen")) ?? null;
    } catch { /* 미지원/거부 — 진행에는 지장 없음 */ }
  }, []);

  useEffect(() => {
    const onVis = () => {
      if (document.visibilityState === "visible" && phaseRef.current === "live") acquireWake();
    };
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, [acquireWake]);

  // 트래킹 중 이탈 방지
  useEffect(() => {
    const guard = (e: BeforeUnloadEvent) => {
      if (phaseRef.current === "live" || phaseRef.current === "paused") e.preventDefault();
    };
    window.addEventListener("beforeunload", guard);
    return () => window.removeEventListener("beforeunload", guard);
  }, []);

  const onPos = useCallback((p: GeolocationPosition) => {
    setGpsOk(true);
    if (phaseRef.current !== "live") return;
    const { latitude: lat, longitude: lng, accuracy } = p.coords;
    if (accuracy > 35) return; // 오차 큰 포인트 버림
    const pt: Pt = { lat, lng, t: p.timestamp || Date.now() };
    const last = lastRef.current;
    if (last) {
      const d = hav(last, pt);
      const dt = (pt.t - last.t) / 1000;
      if (dt <= 0) return;
      if (d / dt > 8.5) return; // 30km/h 초과 = GPS 튐
      if (d >= 2) {
        distRef.current += d;
        setDistM(distRef.current);
        winRef.current.push({ t: pt.t, d });
        // 경로: 마지막 저장점에서 15m 이상 이동 시 [lat, lng, 경과초] 기록
        const route = routeRef.current;
        const lastR = route[route.length - 1];
        if (!lastR || hav({ lat: lastR[0], lng: lastR[1], t: 0 }, pt) >= 15) {
          const tSec = Math.max(0, Math.round((pt.t - startRef.current - pausedMsRef.current) / 1000));
          route.push([Math.round(lat * 1e5) / 1e5, Math.round(lng * 1e5) / 1e5, tSec]);
          if (route.length > 2000) routeRef.current = route.filter((_, i) => i % 2 === 0);
        }
      }
    } else {
      routeRef.current.push([Math.round(lat * 1e5) / 1e5, Math.round(lng * 1e5) / 1e5,
        Math.max(0, Math.round((pt.t - startRef.current - pausedMsRef.current) / 1000))]);
    }
    lastRef.current = pt;
    // 현재 페이스: 최근 45초 이동량
    const now = pt.t;
    winRef.current = winRef.current.filter((x) => now - x.t <= 45000);
    const wd = winRef.current.reduce((s, x) => s + x.d, 0);
    setCurPace(wd >= 15 ? 45 / (wd / 1000) : null);
  }, []);

  const start = useCallback(() => {
    if (!("geolocation" in navigator)) return setErr("이 브라우저는 GPS를 지원하지 않아요.");
    setErr("");
    startRef.current = Date.now();
    pausedMsRef.current = 0;
    distRef.current = 0;
    lastRef.current = null;
    winRef.current = [];
    routeRef.current = [];
    setDistM(0); setElapsed(0); setCurPace(null); setGpsOk(false);
    setPhase("live");
    acquireWake();
    watchRef.current = navigator.geolocation.watchPosition(onPos, (e) => {
      setPhase("idle");
      setErr(e.code === 1
        ? "위치 권한이 꺼져 있어요. 브라우저 설정에서 위치 허용 후 다시 시작해 주세요."
        : "위치를 가져오지 못했어요. 하늘이 보이는 곳에서 다시 시도해 주세요.");
    }, { enableHighAccuracy: true, maximumAge: 1000, timeout: 15000 });
    timerRef.current = setInterval(() => {
      if (phaseRef.current === "live")
        setElapsed(Math.floor((Date.now() - startRef.current - pausedMsRef.current) / 1000));
    }, 1000);
  }, [acquireWake, onPos]);

  const pause = () => { pauseAtRef.current = Date.now(); lastRef.current = null; winRef.current = []; setCurPace(null); setPhase("paused"); };
  const resume = () => { pausedMsRef.current += Date.now() - pauseAtRef.current; setPhase("live"); acquireWake(); };

  const stopAll = useCallback(() => {
    if (watchRef.current != null) navigator.geolocation.clearWatch(watchRef.current);
    if (timerRef.current) clearInterval(timerRef.current);
    wakeRef.current?.release().catch(() => {});
    wakeRef.current = null;
  }, []);
  useEffect(() => stopAll, [stopAll]); // 언마운트 정리

  const finish = () => {
    if (phase === "paused") pausedMsRef.current += Date.now() - pauseAtRef.current;
    setElapsed(Math.floor((Date.now() - startRef.current - pausedMsRef.current) / 1000));
    stopAll();
    setPhase("done");
  };

  const km = Math.round((distM / 1000) * 100) / 100;
  const avgPace = km > 0.05 ? Math.round(elapsed / km) : null;

  const save = () => {
    saveRun({ date: today(), km, paceSec: avgPace, durSec: elapsed, route: routeRef.current });
    router.push("/run");
  };

  if (!ready) return null;
  if (!user) return <main className="lg:pt-10"><LoginCard onLogin={login} onSignup={signup} /></main>;

  return (
    <main className="mx-auto flex min-h-[78vh] max-w-md flex-col lg:pt-10">
      <h1 className="font-display text-[26px] leading-tight tracking-tight">Live Run</h1>
      <p className="mt-0.5 text-[12.5px] text-white/45">GPS로 거리·페이스 자동 기록</p>

      {/* 대시보드 숫자 */}
      <div className="mt-6 rounded-2xl border border-white/[0.06] bg-card p-6 text-center">
        <div className="lab">거리</div>
        <div className="font-display text-[64px] leading-none text-volt tabular-nums">
          {km.toFixed(2)}<span className="text-[20px] text-white/40"> km</span>
        </div>
        <div className="mt-5 grid grid-cols-3 gap-2">
          {([["시간", fmtT(elapsed)], ["현재 페이스", paceStr(curPace)], ["평균 페이스", paceStr(avgPace)]] as const).map(([l, v]) => (
            <div key={l} className="rounded-lg bg-white/[0.05] py-3">
              <div className="font-display text-[19px] leading-none tabular-nums">{v}</div>
              <div className="mt-1.5 text-[9.5px] text-white/45">{l}</div>
            </div>
          ))}
        </div>
        {(phase === "live" || phase === "paused") && (
          <p className="mt-4 text-[11.5px] text-white/40">
            {gpsOk ? (phase === "paused" ? "⏸ 일시정지 중" : "📡 GPS 기록 중 — 화면을 켠 상태로 유지해 주세요") : "📡 GPS 신호 잡는 중…"}
          </p>
        )}
      </div>

      {err && <p className="mt-3 rounded-lg border border-danger/30 bg-danger/10 p-3 text-[12.5px] text-danger">{err}</p>}

      {/* 컨트롤 */}
      <div className="mt-auto pt-6">
        {phase === "idle" && (
          <>
            <PillButton className="w-full !py-4 !text-[16px]" onClick={start}>▶ 러닝 시작</PillButton>
            <p className="mt-2.5 text-center text-[11px] text-white/35">
              시작할 때 위치 권한을 요청해요 · 위치 정보는 러닝 기록에만 사용됩니다
            </p>
            <button className="mt-3 w-full py-2 text-[12.5px] font-bold text-white/40" onClick={() => router.push("/run")}>
              ← 러닝 대시보드로
            </button>
          </>
        )}
        {phase === "live" && (
          <div className="grid grid-cols-2 gap-2.5">
            <button className="rounded-lg border border-white/15 bg-white/[0.06] py-4 text-[15px] font-extrabold" onClick={pause}>⏸ 일시정지</button>
            <button className="rounded-lg bg-danger py-4 text-[15px] font-extrabold text-white" onClick={finish}>■ 종료</button>
          </div>
        )}
        {phase === "paused" && (
          <div className="grid grid-cols-2 gap-2.5">
            <PillButton className="!py-4" onClick={resume}>▶ 계속</PillButton>
            <button className="rounded-lg bg-danger py-4 text-[15px] font-extrabold text-white" onClick={finish}>■ 종료</button>
          </div>
        )}
        {phase === "done" && (
          <>
            <div className="rounded-2xl border border-volt/30 bg-volt/[0.07] p-4 text-center">
              <b className="text-[15px]">🏁 수고했어요!</b>
              <p className="mt-1 text-[13px] text-white/60">
                {km.toFixed(2)}km · {fmtT(elapsed)} · 평균 {paceStr(avgPace)}/km
              </p>
              {km <= 0.05 && <p className="mt-1 text-[11.5px] text-gold">거리가 너무 짧아 기록으로 남기기 어려워요</p>}
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2.5">
              <button
                className="rounded-lg border border-white/15 py-4 text-[14px] font-bold text-white/50"
                onClick={() => { if (window.confirm("이 러닝을 저장하지 않고 버릴까요?")) router.push("/run"); }}
              >
                폐기
              </button>
              <PillButton className="!py-4" onClick={save}>저장 ✅</PillButton>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
