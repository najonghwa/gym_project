"use client";
// 코치 시바 — 가리키는 안내 캐릭터 (three.js 사전 렌더 PNG + CSS 모션)
import { MascotImg } from "./MascotImg";

export function ShibaCoach({ size = 72, animate = true }: { size?: number; animate?: boolean }) {
  return <MascotImg kind="coach" label="코치 시바견" size={size} animate={animate} />;
}

// 코치 말풍선 — 마스코트 + 대사 (avatar로 다른 포즈 지정 가능)
export function CoachBubble({
  children, size = 64, tone = "default", className = "", avatar,
}: {
  children: React.ReactNode;
  size?: number;
  tone?: "default" | "volt";
  className?: string;
  avatar?: React.ReactNode; // 지정 안 하면 코치 시바
}) {
  return (
    <div className={`flex items-start gap-3 ${className}`}>
      <div className="shrink-0">{avatar ?? <ShibaCoach size={size} />}</div>
      <div className={`relative mt-1.5 flex-1 rounded-xl rounded-tl-sm border p-3 text-[13px] leading-relaxed ${
        tone === "volt" ? "border-volt/30 bg-volt/[0.07] text-white/85" : "border-white/10 bg-white/[0.04] text-white/75"
      }`}>
        {/* 말풍선 꼬리 */}
        <span className={`absolute -left-1.5 top-3 h-3 w-3 rotate-45 border-b border-l ${tone === "volt" ? "border-volt/30 bg-volt/[0.07]" : "border-white/10 bg-white/[0.04]"}`} />
        {children}
      </div>
    </div>
  );
}
