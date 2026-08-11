"use client";
// 마스코트 추가 포즈 — 러닝 / 플렉스(자랑) / 휴식. ShibaLifter·ShibaCoach와 세트
// 5종이 각각 다른 축으로 움직인다: 리프트=수직, 코치=수평, 러너=대각, 플렉스=회전, 휴식=호흡
// 외곽선은 부위마다 긋지 않고 ink 필터로 실루엣 하나만 두름
import { useId } from "react";
import { DARK, VOLT, ShibaDefs, ShibaFace, ShibaTail, Limb } from "./shiba";

// 러닝 시바 — 다리 교차 + 대각 이동
export function ShibaRunner({ size = 96, animate = true }: { size?: number; animate?: boolean }) {
  const u = useId().replace(/:/g, "");
  const bob = `rb-${u}`, la = `la-${u}`, lb = `lb-${u}`;
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none" role="img" aria-label="달리는 시바견">
      <style>{`
        @keyframes ${bob}{0%{transform:translate(-2px,1px) rotate(-2deg)}25%{transform:translate(2px,-5px) rotate(1deg)}50%{transform:translate(-2px,1px) rotate(-2deg)}75%{transform:translate(2px,-5px) rotate(1deg)}100%{transform:translate(-2px,1px) rotate(-2deg)}}
        @keyframes ${la}{0%,49%{opacity:1}50%,100%{opacity:0}}
        @keyframes ${lb}{0%,49%{opacity:0}50%,100%{opacity:1}}
        @keyframes spd-${u}{0%{opacity:.2;transform:translateX(4px)}50%{opacity:.9;transform:translateX(-4px)}100%{opacity:.2;transform:translateX(4px)}}
        @media(prefers-reduced-motion:reduce){.${bob},.${la},.${lb},[class*="spd-"]{animation:none!important}}
      `}</style>
      <ShibaDefs u={u} lx={26} ly={16} lw={70} lh={94} />
      <circle cx="60" cy="60" r="58" fill={`url(#bgg-${u})`} />
      <circle cx="60" cy="60" r="58" fill="none" stroke={VOLT} strokeWidth="1.8" opacity="0.35" />
      <ellipse cx="60" cy="112" rx="26" ry="5" fill="#000" opacity="0.2" />
      {/* 스피드 라인 (외곽선 대상 아님) */}
      <g stroke={VOLT} strokeWidth="3" strokeLinecap="round" style={{ animation: animate ? `spd-${u} .5s linear infinite` : undefined }}>
        <line x1="6" y1="52" x2="24" y2="52" /><line x1="2" y1="66" x2="18" y2="66" /><line x1="10" y1="80" x2="26" y2="80" />
      </g>

      <g filter={`url(#ink-${u})`}>
        <g className={animate ? bob : undefined} style={{ transformOrigin: "60px 80px", animation: animate ? `${bob} .46s ease-in-out infinite` : undefined }}>
          <ShibaTail x={78} y={80} s={0.72} u={u} />
          {/* 다리 A */}
          <g className={animate ? la : undefined} style={{ animation: animate ? `${la} .5s steps(1) infinite` : undefined }}>
            <Limb d="M54 84 L44 104" u={u} />
            <Limb d="M66 84 L78 96" u={u} />
          </g>
          {/* 다리 B */}
          <g className={animate ? lb : undefined} style={{ opacity: animate ? 0 : 1, animation: animate ? `${lb} .5s steps(1) infinite` : undefined }}>
            <Limb d="M54 84 L64 104" u={u} />
            <Limb d="M66 84 L54 98" u={u} />
          </g>
          {/* 몸통 (기울임) */}
          <ellipse cx="60" cy="74" rx="24" ry="20" fill={`url(#fur-${u})`} transform="rotate(-10 60 74)" />
          <ellipse cx="60" cy="76" rx="16" ry="14" fill={`url(#crm-${u})`} transform="rotate(-10 60 74)" filter={`url(#soft-${u})`} opacity="0.28" />
          <ellipse cx="60" cy="76" rx="14" ry="12" fill={`url(#crm-${u})`} transform="rotate(-10 60 74)" />
          {/* 앞발 (펌핑) */}
          <Limb d="M44 66 L30 58" u={u} w={10} />
          <Limb d="M76 66 L88 74" u={u} w={10} />
          {/* 머리가 몸에 드리우는 그림자 */}
          <ellipse cx="60" cy="62" rx="17" ry="5" fill={DARK} opacity="0.22" filter={`url(#soft-${u})`} />
          <g transform="rotate(-8 60 44)"><ShibaFace cx={60} cy={44} r={22} u={u} /></g>
        </g>
      </g>
    </svg>
  );
}

// 플렉스 시바 — 양팔 자랑, 몸통 좌우 회전
export function ShibaFlex({ size = 104, animate = true }: { size?: number; animate?: boolean }) {
  const u = useId().replace(/:/g, "");
  const fx = `fx-${u}`;
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none" role="img" aria-label="자랑하는 시바견">
      <style>{`
        @keyframes ${fx}{0%,100%{transform:rotate(-7deg) scaleX(1)}50%{transform:rotate(7deg) scaleX(1.02)}}
        @keyframes fl-${u}{0%,100%{transform:rotate(-14deg) scale(1)}50%{transform:rotate(4deg) scale(1.12)}}
        @keyframes fr-${u}{0%,100%{transform:rotate(4deg) scale(1.12)}50%{transform:rotate(-14deg) scale(1)}}
        @keyframes spk-${u}{0%,100%{opacity:0;transform:scale(.4)}50%{opacity:1;transform:scale(1.1)}}
        @media(prefers-reduced-motion:reduce){.${fx},[class*="fl-"],[class*="fr-"],[class*="spk-"]{animation:none!important}}
      `}</style>
      <ShibaDefs u={u} lx={24} ly={14} lw={74} lh={102} />
      <circle cx="60" cy="60" r="58" fill={`url(#bgg-${u})`} />
      <circle cx="60" cy="60" r="58" fill="none" stroke={VOLT} strokeWidth="1.8" opacity="0.35" />
      <ellipse cx="60" cy="114" rx="30" ry="5" fill="#000" opacity="0.2" />
      {/* 반짝임 별 (외곽선 대상 아님) */}
      <g fill={VOLT}>
        <path d="M18 40 l2 5 5 2 -5 2 -2 5 -2 -5 -5 -2 5 -2Z" style={{ transformOrigin: "20px 47px", animation: animate ? `spk-${u} 1.6s ease-in-out infinite` : undefined }} />
        <path d="M100 34 l1.6 4 4 1.6 -4 1.6 -1.6 4 -1.6 -4 -4 -1.6 4 -1.6Z" style={{ transformOrigin: "101px 40px", animation: animate ? `spk-${u} 1.6s ease-in-out .8s infinite` : undefined }} />
      </g>

      <g filter={`url(#ink-${u})`}>
        <g className={animate ? fx : undefined} style={{ transformOrigin: "60px 106px", animation: animate ? `${fx} 1.8s ease-in-out infinite` : undefined }}>
          <ShibaTail x={84} y={92} s={0.85} u={u} />
          {/* 뒷다리 */}
          <ellipse cx="48" cy="100" rx="12" ry="15" fill={`url(#fur-${u})`} />
          <ellipse cx="72" cy="100" rx="12" ry="15" fill={`url(#fur-${u})`} />
          {/* 몸통 */}
          <ellipse cx="60" cy="82" rx="28" ry="24" fill={`url(#fur-${u})`} />
          <ellipse cx="48" cy="96" rx="12" ry="8" fill={`url(#ao-${u})`} />
          <ellipse cx="72" cy="96" rx="12" ry="8" fill={`url(#ao-${u})`} />
          <ellipse cx="60" cy="85" rx="19" ry="19" fill={`url(#crm-${u})`} filter={`url(#soft-${u})`} opacity="0.28" />
          <ellipse cx="60" cy="85" rx="17" ry="17" fill={`url(#crm-${u})`} />
          {/* 알통 자랑 앞발 (좌우 번갈아 펌프) */}
          <g style={{ transformOrigin: "40px 68px", animation: animate ? `fl-${u} .9s ease-in-out infinite` : undefined }}>
            <Limb d="M42 70 Q28 62 34 46" u={u} w={13} />
            <circle cx="35" cy="44" r="9.5" fill={`url(#crm-${u})`} />
          </g>
          <g style={{ transformOrigin: "80px 68px", animation: animate ? `fr-${u} .9s ease-in-out infinite` : undefined }}>
            <Limb d="M78 70 Q92 62 86 46" u={u} w={13} />
            <circle cx="85" cy="44" r="9.5" fill={`url(#crm-${u})`} />
          </g>
          {/* 머리가 몸에 드리우는 그림자 */}
          <ellipse cx="60" cy="68" rx="19" ry="5" fill={DARK} opacity="0.22" filter={`url(#soft-${u})`} />
          <ShibaFace cx={60} cy={44} r={24} u={u} />
        </g>
      </g>
    </svg>
  );
}

// 휴식 시바 — 앉아서 숨 고르기(호흡 scale) + 땀
export function ShibaRest({ size = 88, animate = true }: { size?: number; animate?: boolean }) {
  const u = useId().replace(/:/g, "");
  const br = `br-${u}`, dr = `dr-${u}`;
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none" role="img" aria-label="쉬는 시바견">
      <style>{`
        @keyframes ${br}{0%,100%{transform:scale(1,1)}45%{transform:scale(1.05,0.96)}}
        @keyframes head-${u}{0%,100%{transform:rotate(-2deg) translateY(0)}45%{transform:rotate(6deg) translateY(3px)}}
        @keyframes ${dr}{0%{transform:translateY(-4px) scale(.6);opacity:0}20%{opacity:1}85%{opacity:1}100%{transform:translateY(20px) scale(1);opacity:0}}
        @media(prefers-reduced-motion:reduce){.${br},.${dr},[class*="head-"]{animation:none!important}}
      `}</style>
      <ShibaDefs u={u} lx={22} ly={16} lw={78} lh={98} />
      <circle cx="60" cy="60" r="58" fill={`url(#bgg-${u})`} />
      <circle cx="60" cy="60" r="58" fill="none" stroke={VOLT} strokeWidth="1.8" opacity="0.35" />
      <ellipse cx="60" cy="112" rx="34" ry="6" fill="#000" opacity="0.2" />

      <g filter={`url(#ink-${u})`}>
        <g className={animate ? br : undefined} style={{ transformOrigin: "60px 108px", animation: animate ? `${br} 1.8s ease-in-out infinite` : undefined }}>
          <ShibaTail x={86} y={104} s={0.8} u={u} />
          {/* 앉은 뒷다리 */}
          <ellipse cx="40" cy="102" rx="18" ry="10" fill={`url(#fur-${u})`} />
          <ellipse cx="80" cy="102" rx="18" ry="10" fill={`url(#fur-${u})`} />
          {/* 몸통 */}
          <ellipse cx="60" cy="84" rx="30" ry="24" fill={`url(#fur-${u})`} />
          <ellipse cx="40" cy="97" rx="16" ry="7" fill={`url(#ao-${u})`} />
          <ellipse cx="80" cy="97" rx="16" ry="7" fill={`url(#ao-${u})`} />
          <ellipse cx="60" cy="88" rx="20" ry="18" fill={`url(#crm-${u})`} filter={`url(#soft-${u})`} opacity="0.28" />
          <ellipse cx="60" cy="88" rx="18" ry="16" fill={`url(#crm-${u})`} />
          {/* 늘어진 앞발 */}
          <Limb d="M34 80 Q26 92 32 100" u={u} />
          <Limb d="M86 80 Q94 92 88 100" u={u} />
          {/* 머리 (지쳐서 까딱 · 감은 눈) */}
          <g style={{ transformOrigin: "60px 68px", animation: animate ? `head-${u} 1.8s ease-in-out infinite` : undefined }}>
            <ellipse cx="60" cy="70" rx="19" ry="5" fill={DARK} opacity="0.22" filter={`url(#soft-${u})`} />
            <ShibaFace cx={60} cy={46} r={24} u={u} sleepy />
          </g>
        </g>
      </g>

      {/* 땀방울 2개 (외곽선 대상 아님) */}
      <path d="M84 38 q4 6 0 8 q-4 -2 0 -8Z" fill="#7dd3fc" style={{ transformOrigin: "84px 42px", animation: animate ? `${dr} 1.6s ease-in infinite` : undefined }} />
      <path d="M34 42 q3.4 5 0 7 q-3.4 -2 0 -7Z" fill="#7dd3fc" style={{ transformOrigin: "34px 45px", animation: animate ? `${dr} 1.6s ease-in .8s infinite` : undefined }} />
    </svg>
  );
}
