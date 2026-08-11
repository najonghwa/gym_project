"use client";
// 시바견 마스코트 공통 — 색 / 조명 / 얼굴 / 말린 꼬리
//
// 고급스러운 3D 느낌의 핵심 3가지:
//  1) 외곽선을 부위마다 긋지 않고 실루엣 하나로 통합 (ink 필터의 dilate)
//     → 팔·다리·얼굴 경계에 선이 안 생겨 "이어붙인 느낌"이 사라짐
//  2) 그라데이션을 userSpaceOnUse로 깔아 캐릭터 전체가 하나의 광원을 공유
//     → 부위마다 하이라이트가 리셋되지 않고 빛이 몸을 타고 흐름
//  3) 겹치는 부위에 부드러운 그림자(cast shadow / AO)를 넣어 깊이를 만듦
// 외부 라이선스 없음(자체 제작 SVG)

export const DARK = "#2b1d12";   // 실루엣 외곽선·눈·코
export const VOLT = "#c8ff00";   // 브랜드 포인트 (헤드밴드에만)
const AO = "#6b3d10";            // 접합부 그늘

// lx,ly~lw,lh = 광원이 흐르는 범위(캐릭터 전체를 덮도록). ink = 외곽선 두께
export function ShibaDefs({
  u, lx = 10, ly = 4, lw = 100, lh = 112, ink = 2.1,
}: { u: string; lx?: number; ly?: number; lw?: number; lh?: number; ink?: number }) {
  const x2 = lx + lw, y2 = ly + lh;
  const lin = (id: string, stops: [string, string][]) => (
    <linearGradient id={`${id}-${u}`} gradientUnits="userSpaceOnUse" x1={lx} y1={ly} x2={x2} y2={y2}>
      {stops.map(([o, c]) => <stop key={o} offset={o} stopColor={c} />)}
    </linearGradient>
  );
  return (
    <defs>
      {/* 캐릭터 전체가 공유하는 단일 광원 (좌상단 → 우하단) */}
      {lin("fur", [["0%", "#fbd196"], ["34%", "#e8a75c"], ["68%", "#c07d31"], ["100%", "#8a5115"]])}
      {lin("crm", [["0%", "#ffffff"], ["36%", "#fdf4e3"], ["72%", "#e7d3b0"], ["100%", "#bfa476"]])}
      {lin("ear", [["0%", "#f7d0b6"], ["100%", "#ab6f47"]])}
      {lin("vg", [["0%", "#eaff96"], ["50%", "#c8ff00"], ["100%", "#7c9f00"]])}
      <radialGradient id={`bgg-${u}`} cx="50%" cy="38%" r="75%">
        <stop offset="0%" stopColor="#353541" /><stop offset="100%" stopColor="#1c1c23" />
      </radialGradient>
      {/* 위쪽 반사광 */}
      <radialGradient id={`shn-${u}`}>
        <stop offset="0%" stopColor="#fff" stopOpacity="0.4" /><stop offset="100%" stopColor="#fff" stopOpacity="0" />
      </radialGradient>
      {/* 접합부 그늘 */}
      <radialGradient id={`ao-${u}`}>
        <stop offset="0%" stopColor={AO} stopOpacity="0.6" /><stop offset="100%" stopColor={AO} stopOpacity="0" />
      </radialGradient>
      {/* 부드러운 그림자용 블러 */}
      <filter id={`soft-${u}`} x="-45%" y="-45%" width="190%" height="190%">
        <feGaussianBlur stdDeviation="2.4" />
      </filter>
      {/* 실루엣 하나로 감싸는 외곽선 — 부위별 stroke 대신 이걸 그룹에 건다 */}
      <filter id={`ink-${u}`} x="-14%" y="-14%" width="128%" height="128%" colorInterpolationFilters="sRGB">
        <feMorphology in="SourceAlpha" operator="dilate" radius={ink} result="sw" />
        <feFlood floodColor={DARK} />
        <feComposite in2="sw" operator="in" result="ink" />
        <feMerge><feMergeNode in="ink" /><feMergeNode in="SourceGraphic" /></feMerge>
      </filter>
    </defs>
  );
}

// 팔·다리 — 몸 위에 겹치므로 부드러운 그림자를 깔아 분리한다(외곽선 대신)
export function Limb({ d, u, w = 11 }: { d: string; u: string; w?: number }) {
  return (
    <>
      <path d={d} stroke={AO} strokeWidth={w + 1} strokeLinecap="round" fill="none"
        opacity="0.5" filter={`url(#soft-${u})`} transform="translate(2.5 2.5)" />
      <path d={d} stroke={`url(#fur-${u})`} strokeWidth={w} strokeLinecap="round" fill="none" />
    </>
  );
}

// 말린 꼬리 — 시바의 상징
export function ShibaTail({ x, y, s = 1, flip = false, u }: { x: number; y: number; s?: number; flip?: boolean; u: string }) {
  const d = "M0 0 C 16 -2 26 -12 23 -25 C 21 -35 9 -39 1 -32";
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <path d={d} stroke={`url(#fur-${u})`} strokeWidth="13" fill="none" strokeLinecap="round" />
      <circle cx="1" cy="-32" r="6.4" fill={`url(#crm-${u})`} />
    </g>
  );
}

// 시바 얼굴 — (cx,cy) 중심, r 반지름. band=헤드밴드, sleepy=감은 눈
export function ShibaFace({
  cx, cy, r, u, band = true, sleepy = false,
}: { cx: number; cy: number; r: number; u: string; band?: boolean; sleepy?: boolean }) {
  const fur = `url(#fur-${u})`;
  const cream = `url(#crm-${u})`;
  const ear = (dir: 1 | -1) => (
    <g key={dir}>
      <path d={`M${cx + dir * r * 0.86} ${cy - r * 0.44} L${cx + dir * r * 0.72} ${cy - r * 1.3} L${cx + dir * r * 0.22} ${cy - r * 0.78} Z`}
        fill={fur} strokeLinejoin="round" />
      <path d={`M${cx + dir * r * 0.76} ${cy - r * 0.52} L${cx + dir * r * 0.68} ${cy - r * 1.12} L${cx + dir * r * 0.34} ${cy - r * 0.74} Z`}
        fill={`url(#ear-${u})`} strokeLinejoin="round" />
    </g>
  );
  const eye = (dir: 1 | -1) => {
    const x = cx + dir * r * 0.4;
    const y = cy - r * 0.08;
    return sleepy ? (
      <path key={dir} d={`M${x - r * 0.13} ${y} q${r * 0.13} ${r * 0.15} ${r * 0.26} 0`}
        stroke={DARK} strokeWidth={r * 0.055} fill="none" strokeLinecap="round" />
    ) : (
      <g key={dir}>
        <ellipse cx={x} cy={y} rx={r * 0.115} ry={r * 0.145} fill={DARK} />
        <circle cx={x - r * 0.035} cy={y - r * 0.04} r={r * 0.038} fill="#fff" />
      </g>
    );
  };
  return (
    <>
      {ear(-1)}{ear(1)}
      {/* 머리 */}
      <ellipse cx={cx} cy={cy} rx={r * 1.04} ry={r * 0.95} fill={fur} />
      {/* 귀가 머리에 드리우는 그늘 */}
      <ellipse cx={cx - r * 0.6} cy={cy - r * 0.6} rx={r * 0.3} ry={r * 0.18} fill={`url(#ao-${u})`} opacity="0.7" />
      <ellipse cx={cx + r * 0.6} cy={cy - r * 0.6} rx={r * 0.3} ry={r * 0.18} fill={`url(#ao-${u})`} opacity="0.7" />
      {/* 이마 반사광 */}
      <ellipse cx={cx - r * 0.32} cy={cy - r * 0.42} rx={r * 0.44} ry={r * 0.26} fill={`url(#shn-${u})`} />
      {/* 우라지로(크림 마스크) — 경계만 살짝 흐려 털이 이어지듯, 무늬 자체는 또렷하게 */}
      <g filter={`url(#soft-${u})`} opacity="0.26">
        <ellipse cx={cx - r * 0.62} cy={cy + r * 0.26} rx={r * 0.34} ry={r * 0.3} fill={cream} />
        <ellipse cx={cx + r * 0.62} cy={cy + r * 0.26} rx={r * 0.34} ry={r * 0.3} fill={cream} />
        <ellipse cx={cx} cy={cy + r * 0.34} rx={r * 0.46} ry={r * 0.36} fill={cream} />
      </g>
      <ellipse cx={cx - r * 0.62} cy={cy + r * 0.26} rx={r * 0.3} ry={r * 0.26} fill={cream} />
      <ellipse cx={cx + r * 0.62} cy={cy + r * 0.26} rx={r * 0.3} ry={r * 0.26} fill={cream} />
      <ellipse cx={cx} cy={cy + r * 0.34} rx={r * 0.42} ry={r * 0.32} fill={cream} />
      {/* 주둥이가 튀어나와 보이도록 — 콧대 반사광 + 주둥이 위쪽 그늘 */}
      <ellipse cx={cx} cy={cy + r * 0.1} rx={r * 0.32} ry={r * 0.14} fill={`url(#ao-${u})`} opacity="0.55" />
      <ellipse cx={cx - r * 0.03} cy={cy + r * 0.1} rx={r * 0.12} ry={r * 0.2} fill={`url(#shn-${u})`} />
      {/* 눈 위 크림 점 (시바 눈썹) */}
      <ellipse cx={cx - r * 0.4} cy={cy - r * 0.34} rx={r * 0.15} ry={r * 0.1} fill={cream} opacity="0.85" />
      <ellipse cx={cx + r * 0.4} cy={cy - r * 0.34} rx={r * 0.15} ry={r * 0.1} fill={cream} opacity="0.85" />
      {eye(-1)}{eye(1)}
      {/* 코 */}
      <ellipse cx={cx} cy={cy + r * 0.22} rx={r * 0.14} ry={r * 0.11} fill={DARK} />
      <ellipse cx={cx - r * 0.05} cy={cy + r * 0.19} rx={r * 0.045} ry={r * 0.03} fill="#fff" opacity="0.45" />
      {/* 입 — 시바 특유의 방긋 미소 */}
      <path
        d={`M${cx} ${cy + r * 0.33} L${cx} ${cy + r * 0.41} M${cx - r * 0.28} ${cy + r * 0.41} Q${cx - r * 0.14} ${cy + r * 0.54} ${cx} ${cy + r * 0.41} Q${cx + r * 0.14} ${cy + r * 0.54} ${cx + r * 0.28} ${cy + r * 0.41}`}
        stroke={DARK} strokeWidth={r * 0.055} fill="none" strokeLinecap="round" strokeLinejoin="round"
      />
      {/* 턱 아래 그늘 */}
      <ellipse cx={cx} cy={cy + r * 0.84} rx={r * 0.6} ry={r * 0.16} fill={`url(#ao-${u})`} opacity="0.75" />
      {band && (
        <>
          {/* 헤드밴드가 이마에 드리우는 그림자 */}
          <path
            d={`M${cx - r * 0.95} ${cy - r * 0.38} Q${cx} ${cy - r * 0.78} ${cx + r * 0.95} ${cy - r * 0.38} L${cx + r * 0.95} ${cy - r * 0.5} Q${cx} ${cy - r * 0.9} ${cx - r * 0.95} ${cy - r * 0.5} Z`}
            fill={AO} opacity="0.45" filter={`url(#soft-${u})`}
          />
          <path
            d={`M${cx - r * 0.95} ${cy - r * 0.45} Q${cx} ${cy - r * 0.85} ${cx + r * 0.95} ${cy - r * 0.45} L${cx + r * 0.95} ${cy - r * 0.7} Q${cx} ${cy - r * 1.05} ${cx - r * 0.95} ${cy - r * 0.7} Z`}
            fill={`url(#vg-${u})`} stroke="#7c9f00" strokeWidth={r * 0.03} opacity="0.98"
          />
          <rect x={cx - r * 1.02} y={cy - r * 0.74} width={r * 0.17} height={r * 0.26} rx={r * 0.06} fill={`url(#vg-${u})`} />
        </>
      )}
    </>
  );
}
