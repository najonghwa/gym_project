"use client";
// 브랜드 마스코트 — 바벨 스쿼트하는 판다 (자체 제작 SVG 애니메이션, 블랙+볼트)
// 상업 사용 안전(외부 라이선스 없음) · 오프라인 동작 · prefers-reduced-motion 존중
import { useId } from "react";

const BLACK = "#1c1c1e";
const WHITE = "#fafafa";
const VOLT = "#c8ff00";
const BAR = "#a1a1aa";

export function PandaLifter({ size = 120, animate = true }: { size?: number; animate?: boolean }) {
  const uid = useId().replace(/:/g, "");
  const sq = `sq-${uid}`; // 스쿼트 바운스
  const pl = `pl-${uid}`; // 원판 회전

  return (
    <svg width={size} height={size} viewBox="0 0 200 190" fill="none" aria-label="운동하는 판다 마스코트" role="img">
      <style>{`
        @keyframes ${sq} {
          0%{transform:translateY(-6px) scaleY(1.03)}
          30%{transform:translateY(24px) scaleY(0.9)}
          50%{transform:translateY(24px) scaleY(0.9)}
          72%{transform:translateY(-6px) scaleY(1.05)}
          82%{transform:translateY(-11px) scaleY(1.06)}
          100%{transform:translateY(-6px) scaleY(1.03)}
        }
        @keyframes ${pl} { from{transform:rotate(0)} to{transform:rotate(360deg)} }
        @media (prefers-reduced-motion: reduce){ .${sq},.${pl}{animation:none!important} }
      `}</style>

      {/* 3D 렌더 느낌 셰이딩 — 좌상단 광원 기준 그라데이션 */}
      <defs>
        <radialGradient id={`hg-${uid}`} cx="35%" cy="28%" r="80%">
          <stop offset="0%" stopColor="#ffffff" /><stop offset="55%" stopColor="#f1f1f5" /><stop offset="100%" stopColor="#c4c4cf" />
        </radialGradient>
        <radialGradient id={`bk-${uid}`} cx="35%" cy="25%" r="85%">
          <stop offset="0%" stopColor="#46464f" /><stop offset="50%" stopColor="#26262c" /><stop offset="100%" stopColor="#0d0d11" />
        </radialGradient>
        <radialGradient id={`vg-${uid}`} cx="35%" cy="25%" r="85%">
          <stop offset="0%" stopColor="#efff9e" /><stop offset="55%" stopColor="#c8ff00" /><stop offset="100%" stopColor="#8db500" />
        </radialGradient>
        <radialGradient id={`bgg-${uid}`} cx="50%" cy="38%" r="75%">
          <stop offset="0%" stopColor="#353541" /><stop offset="100%" stopColor="#1c1c23" />
        </radialGradient>
        <radialGradient id={`shn-${uid}`}>
          <stop offset="0%" stopColor="#fff" stopOpacity="0.55" /><stop offset="100%" stopColor="#fff" stopOpacity="0" />
        </radialGradient>
        <linearGradient id={`mt-${uid}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#e4e4ec" /><stop offset="50%" stopColor="#a1a1aa" /><stop offset="100%" stopColor="#6b6b74" />
        </linearGradient>
      </defs>
      {/* 밝은 원형 배경 — 검은 화면에서 판다 실루엣 살리기 */}
      <circle cx="100" cy="96" r="90" fill={`url(#bgg-${uid})`} />
      <circle cx="100" cy="96" r="90" fill="none" stroke={VOLT} strokeWidth="2.5" opacity="0.35" />

      {/* 그림자 */}
      <ellipse cx="100" cy="180" rx="52" ry="9" fill="#000" opacity="0.22" />

      {/* ── 스쿼트 바운스 그룹 (바벨까지 함께 움직임) ── */}
      <g className={animate ? sq : undefined}
        style={{ transformOrigin: "100px 160px", animation: animate ? `${sq} 2s ease-in-out infinite` : undefined }}>

        {/* 바벨 바 (몸 뒤) */}
        <rect x="18" y="70" width="164" height="7" rx="3.5" fill={`url(#mt-${uid})`} stroke={BLACK} strokeWidth="2" />
        {/* 좌우 원판 (회전) */}
        {[36, 164].map((cx) => (
          <g key={cx} style={{ transformOrigin: `${cx}px 73px`, animation: animate ? `${pl} 3.2s linear infinite` : undefined }}>
            <circle cx={cx} cy="73" r="26" fill={`url(#vg-${uid})`} stroke={BLACK} strokeWidth="3" />
            <circle cx={cx} cy="73" r="9" fill="#e6ffa1" stroke={BLACK} strokeWidth="2" />
            {[0, 60, 120].map((a) => (
              <line key={a} x1={cx} y1="73" x2={cx + 26 * Math.cos((a * Math.PI) / 180)} y2={73 + 26 * Math.sin((a * Math.PI) / 180)}
                stroke={BLACK} strokeWidth="2" opacity="0.35" />
            ))}
          </g>
        ))}

        {/* 다리 */}
        <ellipse cx="80" cy="158" rx="15" ry="20" fill={BLACK} stroke="#3a3a42" strokeWidth="1.5" />
        <ellipse cx="120" cy="158" rx="15" ry="20" fill={BLACK} stroke="#3a3a42" strokeWidth="1.5" />
        <ellipse cx="78" cy="172" rx="13" ry="8" fill={BLACK} stroke="#3a3a42" strokeWidth="1.5" />
        <ellipse cx="122" cy="172" rx="13" ry="8" fill={BLACK} stroke="#3a3a42" strokeWidth="1.5" />

        {/* 몸통 (흰 배 + 검은 윤곽) */}
        <ellipse cx="100" cy="128" rx="40" ry="36" fill={`url(#bk-${uid})`} stroke="#3a3a42" strokeWidth="1.5" />
        <ellipse cx="100" cy="132" rx="27" ry="27" fill={`url(#hg-${uid})`} />

        {/* 팔 — 바를 잡음 */}
        <path d="M64 108 Q46 92 40 76" stroke={BLACK} strokeWidth="15" strokeLinecap="round" />
        <path d="M136 108 Q154 92 160 76" stroke={BLACK} strokeWidth="15" strokeLinecap="round" />
        <circle cx="40" cy="74" r="9" fill={BLACK} />
        <circle cx="160" cy="74" r="9" fill={BLACK} />

        {/* 귀 */}
        <circle cx="74" cy="52" r="16" fill={`url(#bk-${uid})`} />
        <circle cx="126" cy="52" r="16" fill={`url(#bk-${uid})`} />
        <circle cx="74" cy="50" r="6" fill="#000" opacity="0.5" />
        <circle cx="126" cy="50" r="6" fill="#000" opacity="0.5" />

        {/* 머리 + 광택 */}
        <circle cx="100" cy="70" r="35" fill={`url(#hg-${uid})`} stroke={BLACK} strokeWidth="2.5" />
        <ellipse cx="88" cy="52" rx="17" ry="10" fill={`url(#shn-${uid})`} />

        {/* 눈 패치 */}
        <ellipse cx="85" cy="72" rx="11" ry="14" fill={BLACK} transform="rotate(-18 85 72)" />
        <ellipse cx="115" cy="72" rx="11" ry="14" fill={BLACK} transform="rotate(18 115 72)" />
        {/* 눈 — 세로로 살짝 긴 흰 눈 + 작은 동공 */}
        <ellipse cx="86" cy="72" rx="4.2" ry="5" fill={WHITE} />
        <ellipse cx="114" cy="72" rx="4.2" ry="5" fill={WHITE} />
        <circle cx="86" cy="72.8" r="2.5" fill="#1c1c1e" />
        <circle cx="114" cy="72.8" r="2.5" fill="#1c1c1e" />
        {/* 눈 하이라이트(반짝) */}
        <circle cx="85.2" cy="71.9" r="0.9" fill="#fff" /><circle cx="113.2" cy="71.9" r="0.9" fill="#fff" />
        {/* 코·입 (방긋) */}
        <ellipse cx="100" cy="85" rx="4" ry="3" fill="#1c1c1e" />
        <path d="M100 88 Q94 93 89 89 M100 88 Q106 93 111 89" stroke="#1c1c1e" strokeWidth="1.8" fill="none" strokeLinecap="round" />

        {/* 헤드밴드 (볼트) */}
        <path d="M66 55 Q100 44 134 55 L134 49 Q100 37 66 49 Z" fill={`url(#vg-${uid})`} stroke={BLACK} strokeWidth="2" />
        <rect x="63" y="48" width="7" height="9" rx="2" fill={`url(#vg-${uid})`} stroke={BLACK} strokeWidth="1.5" />
      </g>
    </svg>
  );
}
