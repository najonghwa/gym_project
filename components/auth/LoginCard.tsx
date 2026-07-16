"use client";
// id + PIN 로그인/가입 (구 gym_web 계정 그대로 사용 가능)
import { useState } from "react";
import { PillButton } from "@/components/ui/PillButton";
import { GrowthCompare } from "@/components/charts/GrowthCompare";
import { signInWithGoogle } from "@/lib/supa";

export function LoginCard({
  onLogin,
  onSignup,
}: {
  onLogin: (id: string, pin: string) => Promise<string | null>;
  onSignup: (id: string, pin: string, primaryMode?: "gym" | "run") => Promise<string | null>;
}) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [id, setId] = useState("");
  const [pin, setPin] = useState("");
  const [primary, setPrimary] = useState<"gym" | "run">("gym");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  const go = async () => {
    if (!id.trim()) return setMsg("아이디를 입력하세요.");
    if (!/^\d{4}$/.test(pin)) return setMsg("PIN은 숫자 4자리예요.");
    setBusy(true); setMsg(mode === "login" ? "확인 중…" : "아이디 확인 중…");
    const err = await (mode === "login" ? onLogin(id, pin) : onSignup(id, pin, primary));
    setBusy(false);
    setMsg(err ?? "");
  };

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-sm flex-col justify-center">
      <h1 className="text-center font-display text-[34px] tracking-tight">
        FitPlan<span className="text-volt">.</span>
      </h1>
      <p className="mt-1.5 text-center text-[12.5px] text-white/45">
        헬스 · 러닝 통합 대시보드 — 기존 아이디 그대로
      </p>
      <div className="mt-6 grid grid-cols-2 gap-1 rounded-lg border border-white/10 bg-white/5 p-1">
        {(["login", "signup"] as const).map((m) => (
          <button
            key={m}
            onClick={() => { setMode(m); setMsg(""); }}
            className={`rounded-md py-2.5 text-[14px] font-bold ${mode === m ? "bg-volt text-black" : "text-white/50"}`}
          >
            {m === "login" ? "로그인" : "처음이에요"}
          </button>
        ))}
      </div>
      <input
        value={id} onChange={(e) => setId(e.target.value)}
        placeholder="아이디" autoComplete="off"
        className="mt-4 w-full rounded-lg border border-white/10 bg-card px-4 py-4 text-center outline-none placeholder:text-white/30 focus:border-volt"
      />
      <input
        value={pin} onChange={(e) => setPin(e.target.value)}
        type="password" inputMode="numeric" maxLength={4} placeholder="PIN 4자리"
        onKeyDown={(e) => e.key === "Enter" && go()}
        className="mt-2.5 w-full rounded-lg border border-white/10 bg-card px-4 py-4 text-center tracking-[8px] outline-none placeholder:tracking-normal placeholder:text-white/30 focus:border-volt"
      />

      {/* 가입 시 주 종목 선택 → 첫 화면 결정 (설정에서 변경 가능) */}
      {mode === "signup" && (
        <div className="mt-4">
          <div className="lab mb-1.5">주로 하는 운동 <span className="font-normal text-white/35">— 첫 화면으로 설정돼요</span></div>
          <div className="grid grid-cols-2 gap-2">
            {([["gym", "🏋️", "헬스 위주", "웨이트 · 루틴 · 3대"], ["run", "🏃", "러닝 위주", "거리 · 페이스 · 목표"]] as const).map(([v, em, t, d]) => (
              <button
                key={v}
                onClick={() => setPrimary(v)}
                className={`rounded-lg border p-3.5 text-left ${
                  primary === v ? "border-volt bg-volt/10" : "border-white/10 bg-card"
                }`}
              >
                <div className="text-[20px]">{em}</div>
                <div className={`mt-1 text-[14px] font-extrabold ${primary === v ? "text-volt" : ""}`}>{t}</div>
                <div className="mt-0.5 text-[10.5px] text-white/40">{d}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      <PillButton className="mt-4 w-full py-4" onClick={go} disabled={busy}>
        {mode === "login" ? "로그인" : "아이디 만들기"}
      </PillButton>

      {/* 소셜 로그인 */}
      <div className="my-4 flex items-center gap-3">
        <span className="h-px flex-1 bg-white/10" />
        <span className="text-[11px] text-white/35">또는</span>
        <span className="h-px flex-1 bg-white/10" />
      </div>
      <button
        onClick={async () => {
          setMsg("Google로 이동 중…");
          const err = await signInWithGoogle();
          if (err) setMsg("Google 로그인 미설정 — 관리자에게 문의 (" + err.slice(0, 40) + ")");
        }}
        className="flex w-full items-center justify-center gap-2.5 rounded-lg border border-white/15 bg-white py-3.5 text-[14.5px] font-bold text-black active:scale-[0.98]"
      >
        <svg width="18" height="18" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.27-4.74 3.27-8.1z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.1a6.6 6.6 0 0 1 0-4.2V7.06H2.18a11 11 0 0 0 0 9.88l3.66-2.84z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15A11 11 0 0 0 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
        </svg>
        Google로 계속하기
      </button>
      <p className="mt-3 h-5 text-center text-[13px] text-danger">{msg}</p>

      {/* 가입 소구: 일반 대비 성장 비교 */}
      {mode === "signup" && (
        <div className="mt-4 rounded-2xl border border-white/[0.06] bg-card p-4">
          <GrowthCompare />
        </div>
      )}
    </div>
  );
}
