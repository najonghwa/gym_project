"use client";
// 마스코트 추가 포즈 — 러닝 / 플렉스(자랑) / 휴식. 기존 PandaLifter·PandaCoach와 세트
import { useId } from "react";

const BLACK = "#1c1c1e";
const WHITE = "#fafafa";
const VOLT = "#c8ff00";

// 공통 판다 얼굴 (cx,cy 중심, r 반지름)
function Face({ cx, cy, r, band = true }: { cx: number; cy: number; r: number; band?: boolean }) {
  const ex = r * 0.42;
  return (
    <>
      <circle cx={cx - r * 0.72} cy={cy - r * 0.78} r={r * 0.44} fill={BLACK} />
      <circle cx={cx + r * 0.72} cy={cy - r * 0.78} r={r * 0.44} fill={BLACK} />
      <circle cx={cx} cy={cy} r={r} fill={WHITE} stroke={BLACK} strokeWidth={r * 0.08} />
      <ellipse cx={cx - ex} cy={cy + r * 0.05} rx={r * 0.3} ry={r * 0.38} fill={BLACK} transform={`rotate(-18 ${cx - ex} ${cy})`} />
      <ellipse cx={cx + ex} cy={cy + r * 0.05} rx={r * 0.3} ry={r * 0.38} fill={BLACK} transform={`rotate(18 ${cx + ex} ${cy})`} />
      <circle cx={cx - ex} cy={cy} r={r * 0.11} fill="#000" />
      <circle cx={cx + ex} cy={cy} r={r * 0.11} fill="#000" />
      <ellipse cx={cx} cy={cy + r * 0.4} rx={r * 0.12} ry={r * 0.09} fill="#000" />
      {band && <path d={`M${cx - r * 0.95} ${cy - r * 0.45} Q${cx} ${cy - r * 0.85} ${cx + r * 0.95} ${cy - r * 0.45} L${cx + r * 0.95} ${cy - r * 0.7} Q${cx} ${cy - r * 1.05} ${cx - r * 0.95} ${cy - r * 0.7} Z`} fill={VOLT} stroke={BLACK} strokeWidth={r * 0.06} />}
    </>
  );
}

// 러닝 판다 — 다리 교차 + bob
export function PandaRunner({ size = 96, animate = true }: { size?: number; animate?: boolean }) {
  const u = useId().replace(/:/g, "");
  const bob = `rb-${u}`, la = `la-${u}`, lb = `lb-${u}`;
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none" role="img" aria-label="달리는 판다">
      <style>{`
        @keyframes ${bob}{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
        @keyframes ${la}{0%,49%{opacity:1}50%,100%{opacity:0}}
        @keyframes ${lb}{0%,49%{opacity:0}50%,100%{opacity:1}}
        @media(prefers-reduced-motion:reduce){.${bob},.${la},.${lb}{animation:none!important}}
      `}</style>
      <ellipse cx="60" cy="112" rx="26" ry="5" fill="#000" opacity="0.16" />
      {/* 스피드 라인 */}
      <g stroke={VOLT} strokeWidth="3" strokeLinecap="round" opacity="0.7">
        <line x1="6" y1="52" x2="24" y2="52" /><line x1="2" y1="66" x2="18" y2="66" /><line x1="10" y1="80" x2="26" y2="80" />
      </g>
      <g className={animate ? bob : undefined} style={{ transformOrigin: "60px 60px", animation: animate ? `${bob} .5s ease-in-out infinite` : undefined }}>
        {/* 다리 A */}
        <g className={animate ? la : undefined} style={{ animation: animate ? `${la} .5s steps(1) infinite` : undefined }}>
          <path d="M54 84 L44 104" stroke={BLACK} strokeWidth="11" strokeLinecap="round" />
          <path d="M66 84 L78 96" stroke={BLACK} strokeWidth="11" strokeLinecap="round" />
        </g>
        {/* 다리 B */}
        <g className={animate ? lb : undefined} style={{ opacity: animate ? 0 : 1, animation: animate ? `${lb} .5s steps(1) infinite` : undefined }}>
          <path d="M54 84 L64 104" stroke={BLACK} strokeWidth="11" strokeLinecap="round" />
          <path d="M66 84 L54 98" stroke={BLACK} strokeWidth="11" strokeLinecap="round" />
        </g>
        {/* 몸통 (기울임) */}
        <ellipse cx="60" cy="74" rx="24" ry="20" fill={BLACK} transform="rotate(-10 60 74)" />
        <ellipse cx="60" cy="76" rx="15" ry="13" fill={WHITE} transform="rotate(-10 60 74)" />
        {/* 팔 (펌핑) */}
        <path d="M44 66 L30 58" stroke={BLACK} strokeWidth="10" strokeLinecap="round" />
        <path d="M76 66 L88 74" stroke={BLACK} strokeWidth="10" strokeLinecap="round" />
        {/* 머리 */}
        <g transform="rotate(-8 60 44)"><Face cx={60} cy={44} r={22} /></g>
      </g>
    </svg>
  );
}

// 플렉스 판다 — 양팔 이두 자랑
export function PandaFlex({ size = 104, animate = true }: { size?: number; animate?: boolean }) {
  const u = useId().replace(/:/g, "");
  const fx = `fx-${u}`;
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none" role="img" aria-label="자랑하는 판다">
      <style>{`
        @keyframes ${fx}{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}
        @media(prefers-reduced-motion:reduce){.${fx}{animation:none!important}}
      `}</style>
      <ellipse cx="60" cy="114" rx="30" ry="5" fill="#000" opacity="0.16" />
      {/* 다리 */}
      <ellipse cx="48" cy="100" rx="12" ry="15" fill={BLACK} />
      <ellipse cx="72" cy="100" rx="12" ry="15" fill={BLACK} />
      {/* 몸통 */}
      <ellipse cx="60" cy="82" rx="28" ry="24" fill={BLACK} />
      <ellipse cx="60" cy="85" rx="18" ry="18" fill={WHITE} />
      {/* 이두 자랑 팔 (V자로 위로 + pulse) */}
      <g className={animate ? fx : undefined} style={{ transformOrigin: "36px 60px", animation: animate ? `${fx} 1.3s ease-in-out infinite` : undefined }}>
        <path d="M42 70 Q28 62 34 46" stroke={BLACK} strokeWidth="13" strokeLinecap="round" fill="none" />
        <circle cx="35" cy="44" r="9.5" fill={BLACK} />
        <path d="M28 58 q-3 -5 2 -8" stroke={BLACK} strokeWidth="6" strokeLinecap="round" fill="none" />
        <circle cx="35" cy="42" r="3" fill={VOLT} opacity="0.6" />
      </g>
      <g className={animate ? fx : undefined} style={{ transformOrigin: "84px 60px", animation: animate ? `${fx} 1.3s ease-in-out infinite` : undefined }}>
        <path d="M78 70 Q92 62 86 46" stroke={BLACK} strokeWidth="13" strokeLinecap="round" fill="none" />
        <circle cx="85" cy="44" r="9.5" fill={BLACK} />
        <path d="M92 58 q3 -5 -2 -8" stroke={BLACK} strokeWidth="6" strokeLinecap="round" fill="none" />
        <circle cx="85" cy="42" r="3" fill={VOLT} opacity="0.6" />
      </g>
      {/* 머리 (활짝 웃음) */}
      <Face cx={60} cy={44} r={24} />
      <path d="M52 56 Q60 64 68 56" stroke="#000" strokeWidth="2" fill="none" strokeLinecap="round" />
    </svg>
  );
}

// 휴식 판다 — 땀 흘리며 앉아 숨 고르기
export function PandaRest({ size = 88, animate = true }: { size?: number; animate?: boolean }) {
  const u = useId().replace(/:/g, "");
  const br = `br-${u}`, dr = `dr-${u}`;
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none" role="img" aria-label="쉬는 판다">
      <style>{`
        @keyframes ${br}{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.05)}}
        @keyframes ${dr}{0%{transform:translateY(0);opacity:1}80%{opacity:1}100%{transform:translateY(14px);opacity:0}}
        @media(prefers-reduced-motion:reduce){.${br},.${dr}{animation:none!important}}
      `}</style>
      <ellipse cx="60" cy="112" rx="34" ry="6" fill="#000" opacity="0.16" />
      <g className={animate ? br : undefined} style={{ transformOrigin: "60px 100px", animation: animate ? `${br} 2.4s ease-in-out infinite` : undefined }}>
        {/* 앉은 다리 */}
        <ellipse cx="40" cy="102" rx="18" ry="10" fill={BLACK} />
        <ellipse cx="80" cy="102" rx="18" ry="10" fill={BLACK} />
        {/* 몸통 */}
        <ellipse cx="60" cy="84" rx="30" ry="24" fill={BLACK} />
        <ellipse cx="60" cy="88" rx="19" ry="17" fill={WHITE} />
        {/* 늘어진 팔 */}
        <path d="M34 80 Q26 92 32 100" stroke={BLACK} strokeWidth="11" strokeLinecap="round" fill="none" />
        <path d="M86 80 Q94 92 88 100" stroke={BLACK} strokeWidth="11" strokeLinecap="round" fill="none" />
        {/* 머리 */}
        <Face cx={60} cy={46} r={24} />
        {/* 지친 눈(반쯤) */}
        <path d="M48 44 h6 M66 44 h6" stroke="#000" strokeWidth="2" strokeLinecap="round" />
      </g>
      {/* 땀방울 */}
      <path className={animate ? dr : undefined} d="M84 40 q4 6 0 8 q-4 -2 0 -8Z" fill="#7dd3fc"
        style={{ transformOrigin: "84px 44px", animation: animate ? `${dr} 1.8s ease-in infinite` : undefined }} />
    </svg>
  );
}
