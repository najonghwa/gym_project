"use client";
// id + PIN 로그인/가입 (구 gym_web 계정 그대로 사용 가능)
import { useState } from "react";
import { Mascot } from "@/components/mascot/Mascot";
import { PillButton } from "@/components/ui/PillButton";

export function LoginCard({
  onLogin,
  onSignup,
}: {
  onLogin: (id: string, pin: string) => Promise<string | null>;
  onSignup: (id: string, pin: string) => Promise<string | null>;
}) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [id, setId] = useState("");
  const [pin, setPin] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  const go = async () => {
    if (!id.trim()) return setMsg("아이디를 입력하세요.");
    if (!/^\d{4}$/.test(pin)) return setMsg("PIN은 숫자 4자리예요.");
    setBusy(true); setMsg(mode === "login" ? "확인 중…" : "아이디 확인 중…");
    const err = await (mode === "login" ? onLogin(id, pin) : onSignup(id, pin));
    setBusy(false);
    setMsg(err ?? "");
  };

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-sm flex-col justify-center">
      <div className="flex justify-center"><Mascot state="talk" size={96} /></div>
      <h1 className="mt-2 text-center font-display text-[34px] leading-tight">
        오늘도 <span className="text-volt">한 세트</span> 더.
      </h1>
      <p className="mt-1 text-center text-[12.5px] text-white/50">
        기존 헬스 가이드 아이디로 그대로 로그인돼요
      </p>
      <div className="mt-6 grid grid-cols-2 gap-1 rounded-full border border-white/10 bg-white/5 p-1">
        {(["login", "signup"] as const).map((m) => (
          <button
            key={m}
            onClick={() => { setMode(m); setMsg(""); }}
            className={`rounded-full py-2.5 text-[14px] font-bold ${mode === m ? "bg-volt text-black" : "text-white/50"}`}
          >
            {m === "login" ? "로그인" : "처음이에요"}
          </button>
        ))}
      </div>
      <input
        value={id} onChange={(e) => setId(e.target.value)}
        placeholder="아이디" autoComplete="off"
        className="mt-4 w-full rounded-2xl border border-white/10 bg-card px-4 py-4 text-center outline-none placeholder:text-white/30 focus:border-volt"
      />
      <input
        value={pin} onChange={(e) => setPin(e.target.value)}
        type="password" inputMode="numeric" maxLength={4} placeholder="PIN 4자리"
        onKeyDown={(e) => e.key === "Enter" && go()}
        className="mt-2.5 w-full rounded-2xl border border-white/10 bg-card px-4 py-4 text-center tracking-[8px] outline-none placeholder:tracking-normal placeholder:text-white/30 focus:border-volt"
      />
      <PillButton className="mt-4 w-full py-4" onClick={go} disabled={busy}>
        {mode === "login" ? "로그인" : "아이디 만들기"}
      </PillButton>
      <p className="mt-3 h-5 text-center text-[13px] text-danger">{msg}</p>
    </div>
  );
}
