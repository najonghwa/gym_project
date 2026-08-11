"use client";
// 코치 시바 — 호루라기를 든 안내 캐릭터. 좌우로 왔다갔다(sway) + 앞발 흔들기
import { useId } from "react";
import { DARK, VOLT, ShibaDefs, ShibaFace, ShibaTail } from "./shiba";

export function ShibaCoach({ size = 72, animate = true }: { size?: number; animate?: boolean }) {
  const uid = useId().replace(/:/g, "");
  const bob = `bob-${uid}`;
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none" role="img" aria-label="코치 시바견">
      <style>{`
        @keyframes ${bob}{0%,100%{transform:translateX(-5px) rotate(-4deg)}50%{transform:translateX(5px) rotate(4deg)}}
        @keyframes point-${uid}{0%,100%{transform:rotate(6deg)}30%{transform:rotate(-30deg)}60%{transform:rotate(-18deg)}}
        @keyframes ring-${uid}{0%{r:6;opacity:.9}70%,100%{r:17;opacity:0}}
        @media (prefers-reduced-motion:reduce){.${bob},[class*="point-"],[class*="ring-"]{animation:none!important}}
      `}</style>

      <ShibaDefs u={uid} />
      {/* 밝은 원형 배경 */}
      <circle cx="60" cy="60" r="58" fill={`url(#bgg-${uid})`} />
      <circle cx="60" cy="60" r="58" fill="none" stroke={VOLT} strokeWidth="1.8" opacity="0.35" />
      <ellipse cx="60" cy="112" rx="30" ry="5" fill="#000" opacity="0.2" />

      {/* 가리키는 앞발 + 손에 든 호루라기 (삑! 소리 링) */}
      <g style={{ transformOrigin: "42px 96px", animation: animate ? `point-${uid} 1.1s ease-in-out infinite` : undefined }}>
        <path d="M42 96 Q26 88 22 74" stroke={DARK} strokeWidth="11" strokeLinecap="round" fill="none" />
        <path d="M42 96 Q26 88 22 74" stroke={`url(#fur-${uid})`} strokeWidth="7.5" strokeLinecap="round" fill="none" />
        <circle cx="21" cy="72" r="6" fill={`url(#crm-${uid})`} stroke={DARK} strokeWidth="1.6" />
        {/* 호루라기 (손에 쥔) */}
        <rect x="12" y="63" width="11" height="7" rx="3" fill={`url(#vg-${uid})`} stroke={DARK} strokeWidth="1.4" />
        <circle cx="14" cy="66.5" r="1.6" fill={DARK} />
        {/* 삑 소리 퍼짐 */}
        <circle cx="18" cy="66" r="6" fill="none" stroke={VOLT} strokeWidth="1.6"
          style={{ animation: animate ? `ring-${uid} 1.1s ease-out infinite` : undefined }} />
      </g>

      <g className={animate ? bob : undefined} style={{ transformOrigin: "60px 104px", animation: animate ? `${bob} 2.4s ease-in-out infinite` : undefined }}>
        {/* 말린 꼬리 */}
        <ShibaTail x={84} y={110} s={0.78} u={uid} />
        {/* 어깨/몸 */}
        <ellipse cx="60" cy="102" rx="30" ry="22" fill={`url(#fur-${uid})`} stroke={DARK} strokeWidth="2" />
        <ellipse cx="60" cy="106" rx="19" ry="16" fill={`url(#crm-${uid})`} />
        {/* 머리 */}
        <ShibaFace cx={60} cy={58} r={31} u={uid} />
      </g>
    </svg>
  );
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
      <div className={`relative mt-1.5 flex-1 rounded-2xl rounded-tl-sm border p-3 text-[13px] leading-relaxed ${
        tone === "volt" ? "border-volt/30 bg-volt/[0.07] text-white/85" : "border-white/10 bg-white/[0.04] text-white/75"
      }`}>
        {/* 말풍선 꼬리 */}
        <span className={`absolute -left-1.5 top-3 h-3 w-3 rotate-45 border-b border-l ${tone === "volt" ? "border-volt/30 bg-volt/[0.07]" : "border-white/10 bg-white/[0.04]"}`} />
        {children}
      </div>
    </div>
  );
}
