"use client";
// 브랜드 마스코트 — 바벨 스쿼트하는 시바견 (자체 제작 SVG 애니메이션)
// 상업 사용 안전(외부 라이선스 없음) · 오프라인 동작 · prefers-reduced-motion 존중
import { useId } from "react";
import { DARK, VOLT, ShibaDefs, ShibaFace, ShibaTail } from "./shiba";

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

      <ShibaDefs u={uid} />
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

      {/* 그림자 */}
      <ellipse cx="100" cy="180" rx="52" ry="9" fill="#000" opacity="0.22" />

      {/* ── 스쿼트 바운스 그룹 (바벨까지 함께 움직임) ── */}
      <g className={animate ? sq : undefined}
        style={{ transformOrigin: "100px 160px", animation: animate ? `${sq} 2s ease-in-out infinite` : undefined }}>

        {/* 바벨 바 (몸 뒤) */}
        <rect x="6" y="69.75" width="188" height="7.5" rx="3.75" fill={`url(#mt-${uid})`} stroke={DARK} strokeWidth="2" />
        {/* 조임쇠(칼라) — 원판과 앞발 사이 */}
        {[31.5, 163].map((x) => (
          <rect key={x} x={x} y="66.5" width="5.5" height="14" rx="2" fill={`url(#mt-${uid})`} stroke={DARK} strokeWidth="1.6" />
        ))}
        {/* 좌우 원판 — 정면에서 보면 원판은 옆면(두꺼운 판)으로 보인다.
            무거운 판이 안쪽, 가벼운 판이 바깥쪽(실제 끼우는 순서) */}
        {[
          { x: 22, w: 9, h: 38 }, { x: 11, w: 8.5, h: 29 },       // 왼쪽 안/바깥
          { x: 169, w: 9, h: 38 }, { x: 180.5, w: 8.5, h: 29 },   // 오른쪽 안/바깥
        ].map((p) => (
          <g key={p.x} style={{ transformOrigin: `${p.x + p.w / 2}px 73.5px`, animation: animate ? `${pl} 2s ease-in-out infinite` : undefined }}>
            <rect x={p.x} y={73.5 - p.h / 2} width={p.w} height={p.h} rx="3.2"
              fill={`url(#ir-${uid})`} stroke={DARK} strokeWidth="2" />
          </g>
        ))}

        {/* 말린 꼬리 (몸 뒤 오른쪽) */}
        <ShibaTail x={130} y={150} s={1.05} u={uid} />

        {/* 뒷다리 + 크림색 발 */}
        <ellipse cx="82" cy="156" rx="14" ry="19" fill={`url(#fur-${uid})`} stroke={DARK} strokeWidth="2" />
        <ellipse cx="118" cy="156" rx="14" ry="19" fill={`url(#fur-${uid})`} stroke={DARK} strokeWidth="2" />
        <ellipse cx="80" cy="170" rx="12" ry="7.5" fill={`url(#crm-${uid})`} stroke={DARK} strokeWidth="2" />
        <ellipse cx="120" cy="170" rx="12" ry="7.5" fill={`url(#crm-${uid})`} stroke={DARK} strokeWidth="2" />

        {/* 몸통 (크림 배 + 황갈 윤곽) */}
        <ellipse cx="100" cy="126" rx="36" ry="33" fill={`url(#fur-${uid})`} stroke={DARK} strokeWidth="2" />
        <ellipse cx="100" cy="130" rx="24" ry="24" fill={`url(#crm-${uid})`} />

        {/* 앞다리 — 바를 잡음 (팔꿈치 벌리고 어깨 바깥을 그립) */}
        <path d="M72 110 Q54 98 54 78" stroke={DARK} strokeWidth="16" strokeLinecap="round" fill="none" />
        <path d="M128 110 Q146 98 146 78" stroke={DARK} strokeWidth="16" strokeLinecap="round" fill="none" />
        <path d="M72 110 Q54 98 54 78" stroke={`url(#fur-${uid})`} strokeWidth="12" strokeLinecap="round" fill="none" />
        <path d="M128 110 Q146 98 146 78" stroke={`url(#fur-${uid})`} strokeWidth="12" strokeLinecap="round" fill="none" />
        <circle cx="54" cy="74" r="9" fill={`url(#crm-${uid})`} stroke={DARK} strokeWidth="2" />
        <circle cx="146" cy="74" r="9" fill={`url(#crm-${uid})`} stroke={DARK} strokeWidth="2" />

        {/* 머리 — 바가 앞발·머리 사이로 이어져 보이도록 지름을 줄임 */}
        <ShibaFace cx={100} cy={72} r={27} u={uid} />
      </g>
    </svg>
  );
}
