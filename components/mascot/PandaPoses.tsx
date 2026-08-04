"use client";
// 마스코트 추가 포즈 — 러닝 / 플렉스(자랑) / 휴식. 기존 PandaLifter·PandaCoach와 세트
import { useId } from "react";

const BLACK = "#1c1c1e";
const WHITE = "#fafafa";
const VOLT = "#c8ff00";

// 3D 렌더 느낌 셰이딩 — 좌상단 광원 기준 그라데이션 (컴포넌트마다 uid로 id 충돌 방지)
function ShadeDefs({ u }: { u: string }) {
  return (
    <defs>
      <radialGradient id={`hg-${u}`} cx="35%" cy="28%" r="80%">
        <stop offset="0%" stopColor="#ffffff" /><stop offset="55%" stopColor="#f1f1f5" /><stop offset="100%" stopColor="#c4c4cf" />
      </radialGradient>
      <radialGradient id={`bk-${u}`} cx="35%" cy="25%" r="85%">
        <stop offset="0%" stopColor="#46464f" /><stop offset="50%" stopColor="#26262c" /><stop offset="100%" stopColor="#0d0d11" />
      </radialGradient>
      <radialGradient id={`vg-${u}`} cx="35%" cy="25%" r="85%">
        <stop offset="0%" stopColor="#efff9e" /><stop offset="55%" stopColor="#c8ff00" /><stop offset="100%" stopColor="#8db500" />
      </radialGradient>
      <radialGradient id={`bgg-${u}`} cx="50%" cy="38%" r="75%">
        <stop offset="0%" stopColor="#353541" /><stop offset="100%" stopColor="#1c1c23" />
      </radialGradient>
      <radialGradient id={`shn-${u}`}>
        <stop offset="0%" stopColor="#fff" stopOpacity="0.55" /><stop offset="100%" stopColor="#fff" stopOpacity="0" />
      </radialGradient>
    </defs>
  );
}

// 공통 판다 얼굴 (cx,cy 중심, r 반지름) — u 지정 시 입체 셰이딩
function Face({ cx, cy, r, band = true, sleepy = false, u }: { cx: number; cy: number; r: number; band?: boolean; sleepy?: boolean; u?: string }) {
  const ex = r * 0.42;              // 눈 좌우 간격
  const ey = cy + r * 0.04;         // 눈 세로 위치
  const eye = (dir: 1 | -1) => {
    const x = cx + dir * ex;
    return (
      <g key={dir}>
        {/* 검은 눈 패치 */}
        <ellipse cx={x} cy={ey} rx={r * 0.3} ry={r * 0.38} fill={BLACK} transform={`rotate(${dir * 18} ${x} ${ey})`} />
        {sleepy ? (
          <path d={`M${x - r * 0.13} ${ey} q${r * 0.13} ${r * 0.14} ${r * 0.26} 0`} stroke={WHITE} strokeWidth={r * 0.06} fill="none" strokeLinecap="round" />
        ) : (
          <>
            {/* 자연스러운 눈 — 세로로 살짝 긴 흰 눈 + 작은 동공 + 하이라이트 */}
            <ellipse cx={x} cy={ey} rx={r * 0.13} ry={r * 0.155} fill={WHITE} />
            <circle cx={x} cy={ey + r * 0.025} r={r * 0.078} fill="#1c1c1e" />
            <circle cx={x - r * 0.025} cy={ey - r * 0.01} r={r * 0.028} fill="#fff" />
          </>
        )}
      </g>
    );
  };
  return (
    <>
      <circle cx={cx - r * 0.72} cy={cy - r * 0.78} r={r * 0.44} fill={u ? `url(#bk-${u})` : BLACK} />
      <circle cx={cx + r * 0.72} cy={cy - r * 0.78} r={r * 0.44} fill={u ? `url(#bk-${u})` : BLACK} />
      <circle cx={cx} cy={cy} r={r} fill={u ? `url(#hg-${u})` : WHITE} stroke={BLACK} strokeWidth={r * 0.08} />
      {u && <ellipse cx={cx - r * 0.33} cy={cy - r * 0.45} rx={r * 0.48} ry={r * 0.28} fill={`url(#shn-${u})`} />}
      {eye(-1)}{eye(1)}
      {/* 코 */}
      <ellipse cx={cx} cy={cy + r * 0.42} rx={r * 0.11} ry={r * 0.08} fill="#1c1c1e" />
      {/* 입 (방긋) */}
      <path d={`M${cx} ${cy + r * 0.5} q${-r * 0.12} ${r * 0.14} ${-r * 0.24} ${r * 0.04} M${cx} ${cy + r * 0.5} q${r * 0.12} ${r * 0.14} ${r * 0.24} ${r * 0.04}`} stroke="#1c1c1e" strokeWidth={r * 0.05} fill="none" strokeLinecap="round" />
      {band && <path d={`M${cx - r * 0.95} ${cy - r * 0.45} Q${cx} ${cy - r * 0.85} ${cx + r * 0.95} ${cy - r * 0.45} L${cx + r * 0.95} ${cy - r * 0.7} Q${cx} ${cy - r * 1.05} ${cx - r * 0.95} ${cy - r * 0.7} Z`} fill={u ? `url(#vg-${u})` : VOLT} stroke={BLACK} strokeWidth={r * 0.06} />}
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
        @keyframes ${bob}{0%{transform:translate(-2px,1px) rotate(-2deg)}25%{transform:translate(2px,-5px) rotate(1deg)}50%{transform:translate(-2px,1px) rotate(-2deg)}75%{transform:translate(2px,-5px) rotate(1deg)}100%{transform:translate(-2px,1px) rotate(-2deg)}}
        @keyframes ${la}{0%,49%{opacity:1}50%,100%{opacity:0}}
        @keyframes ${lb}{0%,49%{opacity:0}50%,100%{opacity:1}}
        @keyframes spd-${u}{0%{opacity:.2;transform:translateX(4px)}50%{opacity:.9;transform:translateX(-4px)}100%{opacity:.2;transform:translateX(4px)}}
        @media(prefers-reduced-motion:reduce){.${bob},.${la},.${lb},[class*="spd-"]{animation:none!important}}
      `}</style>
      <ShadeDefs u={u} />
      <circle cx="60" cy="60" r="58" fill={`url(#bgg-${u})`} />
      <circle cx="60" cy="60" r="58" fill="none" stroke={VOLT} strokeWidth="1.8" opacity="0.35" />
      <ellipse cx="60" cy="112" rx="26" ry="5" fill="#000" opacity="0.2" />
      {/* 스피드 라인 (깜빡·흐름) */}
      <g stroke={VOLT} strokeWidth="3" strokeLinecap="round" style={{ animation: animate ? `spd-${u} .5s linear infinite` : undefined }}>
        <line x1="6" y1="52" x2="24" y2="52" /><line x1="2" y1="66" x2="18" y2="66" /><line x1="10" y1="80" x2="26" y2="80" />
      </g>
      <g className={animate ? bob : undefined} style={{ transformOrigin: "60px 80px", animation: animate ? `${bob} .46s ease-in-out infinite` : undefined }}>
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
        <ellipse cx="60" cy="74" rx="24" ry="20" fill={`url(#bk-${u})`} stroke="#3a3a42" strokeWidth="1.5" transform="rotate(-10 60 74)" />
        <ellipse cx="60" cy="76" rx="15" ry="13" fill={`url(#hg-${u})`} transform="rotate(-10 60 74)" />
        {/* 팔 (펌핑) */}
        <path d="M44 66 L30 58" stroke={BLACK} strokeWidth="10" strokeLinecap="round" />
        <path d="M76 66 L88 74" stroke={BLACK} strokeWidth="10" strokeLinecap="round" />
        {/* 머리 */}
        <g transform="rotate(-8 60 44)"><Face cx={60} cy={44} r={22} u={u} /></g>
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
        @keyframes ${fx}{0%,100%{transform:rotate(-7deg) scaleX(1)}50%{transform:rotate(7deg) scaleX(1.02)}}
        @keyframes fl-${u}{0%,100%{transform:rotate(-14deg) scale(1)}50%{transform:rotate(4deg) scale(1.12)}}
        @keyframes fr-${u}{0%,100%{transform:rotate(4deg) scale(1.12)}50%{transform:rotate(-14deg) scale(1)}}
        @keyframes spk-${u}{0%,100%{opacity:0;transform:scale(.4)}50%{opacity:1;transform:scale(1.1)}}
        @media(prefers-reduced-motion:reduce){.${fx},[class*="fl-"],[class*="fr-"],[class*="spk-"]{animation:none!important}}
      `}</style>
      <ShadeDefs u={u} />
      <circle cx="60" cy="60" r="58" fill={`url(#bgg-${u})`} />
      <circle cx="60" cy="60" r="58" fill="none" stroke={VOLT} strokeWidth="1.8" opacity="0.35" />
      <ellipse cx="60" cy="114" rx="30" ry="5" fill="#000" opacity="0.2" />
      {/* 반짝임 별 */}
      <g fill={VOLT}>
        <path d="M18 40 l2 5 5 2 -5 2 -2 5 -2 -5 -5 -2 5 -2Z" style={{ transformOrigin: "20px 47px", animation: animate ? `spk-${u} 1.6s ease-in-out infinite` : undefined }} />
        <path d="M100 34 l1.6 4 4 1.6 -4 1.6 -1.6 4 -1.6 -4 -4 -1.6 4 -1.6Z" style={{ transformOrigin: "101px 40px", animation: animate ? `spk-${u} 1.6s ease-in-out .8s infinite` : undefined }} />
      </g>
      <g className={animate ? fx : undefined} style={{ transformOrigin: "60px 106px", animation: animate ? `${fx} 1.8s ease-in-out infinite` : undefined }}>
        {/* 다리 */}
        <ellipse cx="48" cy="100" rx="12" ry="15" fill={`url(#bk-${u})`} />
        <ellipse cx="72" cy="100" rx="12" ry="15" fill={`url(#bk-${u})`} />
        {/* 몸통 */}
        <ellipse cx="60" cy="82" rx="28" ry="24" fill={`url(#bk-${u})`} stroke="#3a3a42" strokeWidth="1.5" />
        <ellipse cx="60" cy="85" rx="18" ry="18" fill={`url(#hg-${u})`} />
        {/* 이두 자랑 팔 (좌우 번갈아 펌프) */}
        <g style={{ transformOrigin: "40px 68px", animation: animate ? `fl-${u} .9s ease-in-out infinite` : undefined }}>
          <path d="M42 70 Q28 62 34 46" stroke={BLACK} strokeWidth="13" strokeLinecap="round" fill="none" />
          <circle cx="35" cy="44" r="9.5" fill={BLACK} />
          <path d="M28 58 q-3 -5 2 -8" stroke={BLACK} strokeWidth="6" strokeLinecap="round" fill="none" />
        </g>
        <g style={{ transformOrigin: "80px 68px", animation: animate ? `fr-${u} .9s ease-in-out infinite` : undefined }}>
          <path d="M78 70 Q92 62 86 46" stroke={BLACK} strokeWidth="13" strokeLinecap="round" fill="none" />
          <circle cx="85" cy="44" r="9.5" fill={BLACK} />
          <path d="M92 58 q3 -5 -2 -8" stroke={BLACK} strokeWidth="6" strokeLinecap="round" fill="none" />
        </g>
        {/* 머리 (활짝 웃음) */}
        <Face cx={60} cy={44} r={24} u={u} />
      </g>
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
        @keyframes ${br}{0%,100%{transform:scale(1,1)}45%{transform:scale(1.05,0.96)}}
        @keyframes head-${u}{0%,100%{transform:rotate(-2deg) translateY(0)}45%{transform:rotate(6deg) translateY(3px)}}
        @keyframes ${dr}{0%{transform:translateY(-4px) scale(.6);opacity:0}20%{opacity:1}85%{opacity:1}100%{transform:translateY(20px) scale(1);opacity:0}}
        @media(prefers-reduced-motion:reduce){.${br},.${dr},[class*="head-"]{animation:none!important}}
      `}</style>
      <ShadeDefs u={u} />
      <circle cx="60" cy="60" r="58" fill={`url(#bgg-${u})`} />
      <circle cx="60" cy="60" r="58" fill="none" stroke={VOLT} strokeWidth="1.8" opacity="0.35" />
      <ellipse cx="60" cy="112" rx="34" ry="6" fill="#000" opacity="0.2" />
      <g className={animate ? br : undefined} style={{ transformOrigin: "60px 108px", animation: animate ? `${br} 1.8s ease-in-out infinite` : undefined }}>
        {/* 앉은 다리 */}
        <ellipse cx="40" cy="102" rx="18" ry="10" fill={`url(#bk-${u})`} />
        <ellipse cx="80" cy="102" rx="18" ry="10" fill={`url(#bk-${u})`} />
        {/* 몸통 */}
        <ellipse cx="60" cy="84" rx="30" ry="24" fill={`url(#bk-${u})`} stroke="#3a3a42" strokeWidth="1.5" />
        <ellipse cx="60" cy="88" rx="19" ry="17" fill={`url(#hg-${u})`} />
        {/* 늘어진 팔 */}
        <path d="M34 80 Q26 92 32 100" stroke={BLACK} strokeWidth="11" strokeLinecap="round" fill="none" />
        <path d="M86 80 Q94 92 88 100" stroke={BLACK} strokeWidth="11" strokeLinecap="round" fill="none" />
        {/* 머리 (지쳐서 까딱 · 감은 눈) */}
        <g style={{ transformOrigin: "60px 68px", animation: animate ? `head-${u} 1.8s ease-in-out infinite` : undefined }}>
          <Face cx={60} cy={46} r={24} sleepy u={u} />
        </g>
      </g>
      {/* 땀방울 2개 (교대로 떨어짐) */}
      <path d="M84 38 q4 6 0 8 q-4 -2 0 -8Z" fill="#7dd3fc" style={{ transformOrigin: "84px 42px", animation: animate ? `${dr} 1.6s ease-in infinite` : undefined }} />
      <path d="M34 42 q3.4 5 0 7 q-3.4 -2 0 -7Z" fill="#7dd3fc" style={{ transformOrigin: "34px 45px", animation: animate ? `${dr} 1.6s ease-in .8s infinite` : undefined }} />
    </svg>
  );
}
