"use client";
// 3D 렌더 마스코트 공통 래퍼 — three.js로 미리 렌더한 PNG(public/mascots/)를
// 원형 배경 위에 올리고 포즈별 CSS 모션 + 이펙트 오버레이를 입힌다.
// 런타임에 three.js가 없으므로 번들 무게 증가 없음. 5종은 각각 다른 축으로 움직인다.
import { useId } from "react";

const VOLT = "#c8ff00";

export type MascotKind = "lift" | "coach" | "run" | "flex" | "rest";

const MOTION: Record<MascotKind, (u: string) => { kf: string; anim: string }> = {
  // 수직 — 스쿼트 바운스
  lift: (u) => ({
    kf: `@keyframes m-${u}{0%,100%{transform:translateY(-1.5%) scaleY(1.01)}30%,50%{transform:translateY(5.5%) scaleY(.95)}72%{transform:translateY(-2.5%) scaleY(1.02)}}`,
    anim: `m-${u} 2s ease-in-out infinite`,
  }),
  // 수평 — 좌우 sway
  coach: (u) => ({
    kf: `@keyframes m-${u}{0%,100%{transform:translateX(-3.5%) rotate(-3deg)}50%{transform:translateX(3.5%) rotate(3deg)}}`,
    anim: `m-${u} 2.4s ease-in-out infinite`,
  }),
  // 대각 — 달리기 바운스
  run: (u) => ({
    kf: `@keyframes m-${u}{0%,100%{transform:translate(-1.5%,1%) rotate(-1.5deg)}50%{transform:translate(1.5%,-3.5%) rotate(1deg)}}`,
    anim: `m-${u} .5s ease-in-out infinite`,
  }),
  // 회전 — 좌우로 몸 돌려 자랑
  flex: (u) => ({
    kf: `@keyframes m-${u}{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}`,
    anim: `m-${u} 1.8s ease-in-out infinite`,
  }),
  // 호흡 — 이동 없이 부풀었다 꺼짐
  rest: (u) => ({
    kf: `@keyframes m-${u}{0%,100%{transform:scale(1,1)}45%{transform:scale(1.035,.97)}}`,
    anim: `m-${u} 1.8s ease-in-out infinite`,
  }),
};

export function MascotImg({
  kind, label, size = 96, animate = true,
}: { kind: MascotKind; label: string; size?: number; animate?: boolean }) {
  const u = useId().replace(/:/g, "");
  const { kf, anim } = MOTION[kind](u);
  return (
    <div style={{ width: size, height: size }} className="relative shrink-0 select-none" role="img" aria-label={label}>
      <style>{`
        ${kf}
        @keyframes spd-${u}{0%{opacity:.15;transform:translateX(6%)}50%{opacity:.9;transform:translateX(-6%)}100%{opacity:.15;transform:translateX(6%)}}
        @keyframes spk-${u}{0%,100%{opacity:0;transform:scale(.4)}50%{opacity:1;transform:scale(1.1)}}
        @keyframes dr-${u}{0%{transform:translateY(-8%) scale(.6);opacity:0}20%{opacity:1}85%{opacity:1}100%{transform:translateY(35%) scale(1);opacity:0}}
        @media (prefers-reduced-motion:reduce){ [data-m="${u}"] *{animation:none!important} }
      `}</style>
      <div data-m={u} className="absolute inset-0">
        {/* 원형 배경 + 볼트 링 */}
        <div className="absolute inset-0 rounded-full"
          style={{ background: "radial-gradient(circle at 50% 38%, #353541 0%, #1c1c23 100%)", boxShadow: `inset 0 0 0 1.5px ${VOLT}59` }} />
        {/* 3D 렌더 본체 */}
        <img src={`/mascots/${kind}.png`} alt="" draggable={false} className="absolute"
          style={{ inset: "4%", width: "92%", height: "92%", transformOrigin: "50% 88%", animation: animate ? anim : undefined }} />
        {/* 포즈별 이펙트 오버레이 */}
        {kind === "run" && (
          <svg viewBox="0 0 100 100" className="absolute inset-0" style={{ animation: animate ? `spd-${u} .5s linear infinite` : undefined }}>
            <g stroke={VOLT} strokeWidth="2.6" strokeLinecap="round">
              <line x1="6" y1="42" x2="21" y2="42" /><line x1="2" y1="55" x2="15" y2="55" /><line x1="8" y1="68" x2="22" y2="68" />
            </g>
          </svg>
        )}
        {kind === "flex" && (
          <svg viewBox="0 0 100 100" className="absolute inset-0">
            <path d="M15 30 l1.8 4.5 4.5 1.8 -4.5 1.8 -1.8 4.5 -1.8 -4.5 -4.5 -1.8 4.5 -1.8Z" fill={VOLT}
              style={{ transformOrigin: "16.8px 36.3px", animation: animate ? `spk-${u} 1.6s ease-in-out infinite` : undefined }} />
            <path d="M84 24 l1.4 3.6 3.6 1.4 -3.6 1.4 -1.4 3.6 -1.4 -3.6 -3.6 -1.4 3.6 -1.4Z" fill={VOLT}
              style={{ transformOrigin: "85.4px 29px", animation: animate ? `spk-${u} 1.6s ease-in-out .8s infinite` : undefined }} />
          </svg>
        )}
        {kind === "rest" && (
          <svg viewBox="0 0 100 100" className="absolute inset-0">
            <path d="M72 26 q3.4 5 0 7 q-3.4 -2 0 -7Z" fill="#7dd3fc"
              style={{ transformOrigin: "72px 29px", animation: animate ? `dr-${u} 1.6s ease-in infinite` : undefined }} />
            <path d="M28 30 q3 4.4 0 6.2 q-3 -1.8 0 -6.2Z" fill="#7dd3fc"
              style={{ transformOrigin: "28px 33px", animation: animate ? `dr-${u} 1.6s ease-in .8s infinite` : undefined }} />
          </svg>
        )}
      </div>
    </div>
  );
}
