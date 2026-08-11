"use client";
// 브랜드 마스코트 — 바벨 스쿼트하는 시바견 (자체 제작 SVG 애니메이션)
// 외곽선은 부위마다 긋지 않고 ink 필터로 실루엣 하나만 두름 → 이어붙인 느낌 제거
import { useId } from "react";
import { DARK, VOLT, ShibaDefs, ShibaFace, ShibaTail, Limb } from "./shiba";

export function ShibaLifter({ size = 120, animate = true }: { size?: number; animate?: boolean }) {
  const uid = useId().replace(/:/g, "");
  const sq = `sq-${uid}`; // 스쿼트 바운스
  const pl = `pl-${uid}`; // 바 휨(whip)

  return (
    <svg width={size} height={size} viewBox="0 0 200 190" fill="none" aria-label="운동하는 시바견 마스코트" role="img">
      <style>{`
        @keyframes ${sq} {
          0%{transform:translateY(-6px) scaleY(1.03)}
          30%{transform:translateY(24px) scaleY(0.9)}
          50%{transform:translateY(24px) scaleY(0.9)}
          72%{transform:translateY(-6px) scaleY(1.05)}
          82%{transform:translateY(-11px) scaleY(1.06)}
          100%{transform:translateY(-6px) scaleY(1.03)}
        }
        @keyframes ${pl} { 0%,100%{transform:translateY(-1.5px)} 45%{transform:translateY(2px)} }
        @media (prefers-reduced-motion: reduce){ .${sq},.${pl}{animation:none!important} }
      `}</style>

      <ShibaDefs u={uid} lx={34} ly={22} lw={132} lh={158} ink={2.4} />
      <defs>
        <linearGradient id={`mt-${uid}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#e4e4ec" /><stop offset="50%" stopColor="#a1a1aa" /><stop offset="100%" stopColor="#6b6b74" />
        </linearGradient>
        {/* 원판 옆면 — 원기둥처럼 왼쪽에 하이라이트가 지나가는 금속 셰이딩 */}
        <linearGradient id={`ir-${uid}`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#6d6d79" /><stop offset="28%" stopColor="#9a9aa8" />
          <stop offset="58%" stopColor="#45454f" /><stop offset="100%" stopColor="#1b1b21" />
        </linearGradient>
      </defs>

      {/* 밝은 원형 배경 — 검은 화면에서 실루엣 살리기 */}
      <circle cx="100" cy="96" r="90" fill={`url(#bgg-${uid})`} />
      <circle cx="100" cy="96" r="90" fill="none" stroke={VOLT} strokeWidth="2.5" opacity="0.35" />
      <ellipse cx="100" cy="180" rx="52" ry="9" fill="#000" opacity="0.22" />

      {/* ── 스쿼트 바운스 그룹 (바벨까지 함께 움직임) ── */}
      <g className={animate ? sq : undefined}
        style={{ transformOrigin: "100px 160px", animation: animate ? `${sq} 2s ease-in-out infinite` : undefined }}>

        {/* 바벨 (금속은 별도 외곽선 유지) */}
        <rect x="6" y="69.75" width="188" height="7.5" rx="3.75" fill={`url(#mt-${uid})`} stroke={DARK} strokeWidth="2" />
        {[31.5, 163].map((x) => (
          <rect key={x} x={x} y="66.5" width="5.5" height="14" rx="2" fill={`url(#mt-${uid})`} stroke={DARK} strokeWidth="1.6" />
        ))}
        {/* 원판 — 정면에서 보면 옆면(두꺼운 판). 무거운 판이 안쪽 */}
        {[
          { x: 22, w: 9, h: 38 }, { x: 11, w: 8.5, h: 29 },
          { x: 169, w: 9, h: 38 }, { x: 180.5, w: 8.5, h: 29 },
        ].map((p) => (
          <g key={p.x} style={{ transformOrigin: `${p.x + p.w / 2}px 73.5px`, animation: animate ? `${pl} 2s ease-in-out infinite` : undefined }}>
            <rect x={p.x} y={73.5 - p.h / 2} width={p.w} height={p.h} rx="3.2"
              fill={`url(#ir-${uid})`} stroke={DARK} strokeWidth="2" />
          </g>
        ))}

        {/* ── 시바 본체: 이 그룹 전체에 외곽선 하나 ── */}
        <g filter={`url(#ink-${uid})`}>
          <ShibaTail x={130} y={150} s={1.05} u={uid} />

          {/* 뒷다리 + 크림색 발 */}
          <ellipse cx="82" cy="156" rx="14" ry="19" fill={`url(#fur-${uid})`} />
          <ellipse cx="118" cy="156" rx="14" ry="19" fill={`url(#fur-${uid})`} />
          <ellipse cx="80" cy="170" rx="12" ry="7.5" fill={`url(#crm-${uid})`} />
          <ellipse cx="120" cy="170" rx="12" ry="7.5" fill={`url(#crm-${uid})`} />

          {/* 몸통 */}
          <ellipse cx="100" cy="126" rx="36" ry="33" fill={`url(#fur-${uid})`} />
          {/* 다리가 몸통에 드리우는 그늘 */}
          <ellipse cx="82" cy="150" rx="15" ry="10" fill={`url(#ao-${uid})`} />
          <ellipse cx="118" cy="150" rx="15" ry="10" fill={`url(#ao-${uid})`} />
          {/* 배 (경계만 살짝 흐려 털이 이어지듯) */}
          <ellipse cx="100" cy="130" rx="26" ry="26" fill={`url(#crm-${uid})`} filter={`url(#soft-${uid})`} opacity="0.28" />
          <ellipse cx="100" cy="130" rx="23" ry="24" fill={`url(#crm-${uid})`} />

          {/* 앞다리 — 바를 잡음 */}
          <Limb d="M72 110 Q54 98 54 78" u={uid} w={12} />
          <Limb d="M128 110 Q146 98 146 78" u={uid} w={12} />
          <circle cx="54" cy="74" r="9" fill={`url(#crm-${uid})`} />
          <circle cx="146" cy="74" r="9" fill={`url(#crm-${uid})`} />

          {/* 머리가 몸통에 드리우는 그림자 */}
          <ellipse cx="100" cy="101" rx="24" ry="7" fill={DARK} opacity="0.22" filter={`url(#soft-${uid})`} />
          <ShibaFace cx={100} cy={72} r={27} u={uid} />
        </g>
      </g>
    </svg>
  );
}
