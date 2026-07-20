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

      {/* 밝은 원형 배경 — 검은 화면에서 판다 실루엣 살리기 */}
      <circle cx="100" cy="96" r="90" fill="#26262e" />
      <circle cx="100" cy="96" r="90" fill="none" stroke={VOLT} strokeWidth="2.5" opacity="0.35" />

      {/* 그림자 */}
      <ellipse cx="100" cy="180" rx="52" ry="9" fill="#000" opacity="0.22" />

      {/* ── 스쿼트 바운스 그룹 (바벨까지 함께 움직임) ── */}
      <g className={animate ? sq : undefined}
        style={{ transformOrigin: "100px 160px", animation: animate ? `${sq} 2s ease-in-out infinite` : undefined }}>

        {/* 바벨 바 (몸 뒤) */}
        <rect x="18" y="70" width="164" height="7" rx="3.5" fill={BAR} stroke={BLACK} strokeWidth="2" />
        {/* 좌우 원판 (회전) */}
        {[36, 164].map((cx) => (
          <g key={cx} style={{ transformOrigin: `${cx}px 73px`, animation: animate ? `${pl} 3.2s linear infinite` : undefined }}>
            <circle cx={cx} cy="73" r="26" fill={VOLT} stroke={BLACK} strokeWidth="3" />
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
        <ellipse cx="100" cy="128" rx="40" ry="36" fill={BLACK} stroke="#3a3a42" strokeWidth="1.5" />
        <ellipse cx="100" cy="132" rx="27" ry="27" fill={WHITE} />

        {/* 팔 — 바를 잡음 */}
        <path d="M64 108 Q46 92 40 76" stroke={BLACK} strokeWidth="15" strokeLinecap="round" />
        <path d="M136 108 Q154 92 160 76" stroke={BLACK} strokeWidth="15" strokeLinecap="round" />
        <circle cx="40" cy="74" r="9" fill={BLACK} />
        <circle cx="160" cy="74" r="9" fill={BLACK} />

        {/* 귀 */}
        <circle cx="74" cy="52" r="16" fill={BLACK} />
        <circle cx="126" cy="52" r="16" fill={BLACK} />
        <circle cx="74" cy="50" r="6" fill="#000" opacity="0.5" />
        <circle cx="126" cy="50" r="6" fill="#000" opacity="0.5" />

        {/* 머리 */}
        <circle cx="100" cy="70" r="35" fill={WHITE} stroke={BLACK} strokeWidth="2.5" />

        {/* 눈 패치 */}
        <ellipse cx="85" cy="72" rx="11" ry="14" fill={BLACK} transform="rotate(-18 85 72)" />
        <ellipse cx="115" cy="72" rx="11" ry="14" fill={BLACK} transform="rotate(18 115 72)" />
        {/* 눈 */}
        <circle cx="86" cy="70" r="4.5" fill={WHITE} />
        <circle cx="114" cy="70" r="4.5" fill={WHITE} />
        <circle cx="87" cy="71" r="2.2" fill="#000" />
        <circle cx="113" cy="71" r="2.2" fill="#000" />
        {/* 코·입 (결연한 표정) */}
        <ellipse cx="100" cy="84" rx="4" ry="3" fill="#000" />
        <path d="M100 87 Q100 92 95 93" stroke="#000" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <path d="M100 87 Q100 92 105 93" stroke="#000" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        {/* 눈썹 (집중) */}
        <path d="M78 58 L92 62" stroke="#000" strokeWidth="2.2" strokeLinecap="round" />
        <path d="M122 58 L108 62" stroke="#000" strokeWidth="2.2" strokeLinecap="round" />

        {/* 헤드밴드 (볼트) */}
        <path d="M66 55 Q100 44 134 55 L134 49 Q100 37 66 49 Z" fill={VOLT} stroke={BLACK} strokeWidth="2" />
        <rect x="63" y="48" width="7" height="9" rx="2" fill={VOLT} stroke={BLACK} strokeWidth="1.5" />
      </g>
    </svg>
  );
}
