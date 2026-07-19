"use client";
// 코치 판다 — 머리+헤드밴드+호루라기 (앱 전반 안내 캐릭터). 가벼운 bob 애니메이션
import { useId } from "react";

const BLACK = "#1c1c1e";
const WHITE = "#fafafa";
const VOLT = "#c8ff00";

export function PandaCoach({ size = 72, animate = true }: { size?: number; animate?: boolean }) {
  const uid = useId().replace(/:/g, "");
  const bob = `bob-${uid}`;
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none" role="img" aria-label="코치 판다">
      <style>{`
        @keyframes ${bob}{0%,100%{transform:translateY(0) rotate(-1deg)}50%{transform:translateY(-3px) rotate(1deg)}}
        @media (prefers-reduced-motion:reduce){.${bob}{animation:none!important}}
      `}</style>
      <ellipse cx="60" cy="112" rx="30" ry="5" fill="#000" opacity="0.16" />
      <g className={animate ? bob : undefined} style={{ transformOrigin: "60px 70px", animation: animate ? `${bob} 2.6s ease-in-out infinite` : undefined }}>
        {/* 어깨/몸 */}
        <ellipse cx="60" cy="102" rx="30" ry="22" fill={BLACK} />
        <ellipse cx="60" cy="106" rx="19" ry="16" fill={WHITE} />
        {/* 호루라기 줄 + 호루라기 */}
        <path d="M44 92 Q60 104 76 92" stroke={VOLT} strokeWidth="3" fill="none" />
        <g transform="rotate(12 60 102)">
          <rect x="54" y="98" width="12" height="8" rx="3" fill={VOLT} stroke={BLACK} strokeWidth="1.6" />
          <circle cx="66" cy="102" r="2.4" fill={BLACK} />
        </g>
        {/* 귀 */}
        <circle cx="38" cy="40" r="14" fill={BLACK} />
        <circle cx="82" cy="40" r="14" fill={BLACK} />
        <circle cx="38" cy="38" r="5" fill="#000" opacity="0.5" />
        <circle cx="82" cy="38" r="5" fill="#000" opacity="0.5" />
        {/* 머리 */}
        <circle cx="60" cy="58" r="31" fill={WHITE} stroke={BLACK} strokeWidth="2.5" />
        {/* 눈 패치 */}
        <ellipse cx="47" cy="60" rx="9.5" ry="12" fill={BLACK} transform="rotate(-18 47 60)" />
        <ellipse cx="73" cy="60" rx="9.5" ry="12" fill={BLACK} transform="rotate(18 73 60)" />
        <circle cx="48" cy="58" r="4" fill={WHITE} /><circle cx="72" cy="58" r="4" fill={WHITE} />
        <circle cx="49" cy="59" r="2" fill="#000" /><circle cx="71" cy="59" r="2" fill="#000" />
        {/* 코·미소(친근한 코치) */}
        <ellipse cx="60" cy="70" rx="3.6" ry="2.8" fill="#000" />
        <path d="M60 73 Q60 78 54 78 M60 73 Q60 78 66 78" stroke="#000" strokeWidth="1.7" fill="none" strokeLinecap="round" />
        {/* 눈썹(코치다운 자신감) */}
        <path d="M40 47 L52 50 M80 47 L68 50" stroke="#000" strokeWidth="2" strokeLinecap="round" />
        {/* 헤드밴드 */}
        <path d="M30 44 Q60 33 90 44 L90 38 Q60 26 30 38 Z" fill={VOLT} stroke={BLACK} strokeWidth="2" />
        <rect x="27" y="37" width="6" height="8" rx="2" fill={VOLT} stroke={BLACK} strokeWidth="1.4" />
      </g>
    </svg>
  );
}

// 코치 말풍선 — 판다 + 대사 (앱 전반 재사용)
export function CoachBubble({
  children, size = 64, tone = "default", className = "",
}: {
  children: React.ReactNode;
  size?: number;
  tone?: "default" | "volt";
  className?: string;
}) {
  return (
    <div className={`flex items-start gap-3 ${className}`}>
      <div className="shrink-0"><PandaCoach size={size} /></div>
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
