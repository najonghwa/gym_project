"use client";
// 설정 시트 — 첫 화면(주 종목) 변경 + 로그아웃 (헬스/러닝 탭 공용)
import { BottomSheet } from "@/components/ui/BottomSheet";

export function SettingsSheet({
  open, onClose, primaryMode, onChangeMode, onLogout,
}: {
  open: boolean;
  onClose: () => void;
  primaryMode: "gym" | "run";
  onChangeMode: (m: "gym" | "run") => void;
  onLogout: () => void;
}) {
  return (
    <BottomSheet open={open} onClose={onClose}>
      <h3 className="text-lg font-extrabold">⚙️ 설정</h3>
      <div className="lab mb-1.5 mt-4">앱 켜면 처음 보이는 화면</div>
      <div className="grid grid-cols-2 gap-2">
        {([["gym", "🏋️", "헬스"], ["run", "🏃", "러닝"]] as const).map(([v, em, t]) => (
          <button
            key={v}
            onClick={() => onChangeMode(v)}
            className={`rounded-lg border py-3.5 text-center ${
              primaryMode === v ? "border-volt bg-volt/10 text-volt" : "border-white/10 bg-white/[0.03]"
            }`}
          >
            <span className="text-[18px]">{em}</span>
            <b className="ml-1.5 text-[14px]">{t}</b>
          </button>
        ))}
      </div>
      <p className="mt-2 text-[11px] text-white/40">언제든 바꿀 수 있어요.</p>
      <button
        onClick={() => { onClose(); onLogout(); }}
        className="mt-5 w-full rounded-lg border border-white/10 py-3 text-[13.5px] font-bold text-white/50"
      >
        로그아웃
      </button>
    </BottomSheet>
  );
}
