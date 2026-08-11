"use client";
// 시바견 마스코트 공통 — 색 / 3D 셰이딩 / 얼굴 / 말린 꼬리
// 5종 포즈(리프트·코치·러너·플렉스·휴식)가 이 파일을 함께 씀. 외부 라이선스 없음(자체 제작 SVG)

export const DARK = "#2b1d12";   // 윤곽·눈·코
export const VOLT = "#c8ff00";   // 브랜드 포인트 (헤드밴드에만)

// 좌상단 광원 기준 그라데이션 — uid로 id 충돌 방지
export function ShibaDefs({ u }: { u: string }) {
  return (
    <defs>
      <radialGradient id={`fur-${u}`} cx="34%" cy="26%" r="86%">
        <stop offset="0%" stopColor="#f8c47f" /><stop offset="48%" stopColor="#e09a4f" /><stop offset="100%" stopColor="#a4611d" />
      </radialGradient>
      <radialGradient id={`crm-${u}`} cx="34%" cy="26%" r="86%">
        <stop offset="0%" stopColor="#ffffff" /><stop offset="52%" stopColor="#fdf4e4" /><stop offset="100%" stopColor="#dbc59f" />
      </radialGradient>
      <radialGradient id={`ear-${u}`} cx="42%" cy="30%" r="80%">
        <stop offset="0%" stopColor="#f7d5bd" /><stop offset="100%" stopColor="#c1855f" />
      </radialGradient>
      <radialGradient id={`vg-${u}`} cx="35%" cy="25%" r="85%">
        <stop offset="0%" stopColor="#efff9e" /><stop offset="55%" stopColor="#c8ff00" /><stop offset="100%" stopColor="#8db500" />
      </radialGradient>
      <radialGradient id={`bgg-${u}`} cx="50%" cy="38%" r="75%">
        <stop offset="0%" stopColor="#353541" /><stop offset="100%" stopColor="#1c1c23" />
      </radialGradient>
      <radialGradient id={`shn-${u}`}>
        <stop offset="0%" stopColor="#fff" stopOpacity="0.5" /><stop offset="100%" stopColor="#fff" stopOpacity="0" />
      </radialGradient>
    </defs>
  );
}

// 말린 꼬리 — 시바의 상징. (x,y)에서 시작해 위로 한 바퀴 말림
export function ShibaTail({ x, y, s = 1, flip = false, u }: { x: number; y: number; s?: number; flip?: boolean; u: string }) {
  const d = "M0 0 C 16 -2 26 -12 23 -25 C 21 -35 9 -39 1 -32";
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <path d={d} stroke={DARK} strokeWidth="17" fill="none" strokeLinecap="round" />
      <path d={d} stroke={`url(#fur-${u})`} strokeWidth="13" fill="none" strokeLinecap="round" />
      <circle cx="1" cy="-32" r="6.4" fill={`url(#crm-${u})`} stroke={DARK} strokeWidth="1.6" />
    </g>
  );
}

// 시바 얼굴 — (cx,cy) 중심, r 반지름. band=헤드밴드, sleepy=감은 눈
export function ShibaFace({
  cx, cy, r, u, band = true, sleepy = false,
}: { cx: number; cy: number; r: number; u: string; band?: boolean; sleepy?: boolean }) {
  const fur = `url(#fur-${u})`;
  const cream = `url(#crm-${u})`;
  // 귀 — 바깥 삼각형 / 안쪽 삼각형 (dir: -1 왼쪽, 1 오른쪽)
  const ear = (dir: 1 | -1) => (
    <g key={dir}>
      <path
        d={`M${cx + dir * r * 0.86} ${cy - r * 0.44} L${cx + dir * r * 0.72} ${cy - r * 1.3} L${cx + dir * r * 0.22} ${cy - r * 0.78} Z`}
        fill={fur} stroke={DARK} strokeWidth={r * 0.07} strokeLinejoin="round"
      />
      <path
        d={`M${cx + dir * r * 0.76} ${cy - r * 0.52} L${cx + dir * r * 0.68} ${cy - r * 1.12} L${cx + dir * r * 0.34} ${cy - r * 0.74} Z`}
        fill={`url(#ear-${u})`} strokeLinejoin="round"
      />
    </g>
  );
  // 눈 (dir: -1 왼쪽, 1 오른쪽)
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
      <ellipse cx={cx} cy={cy} rx={r * 1.04} ry={r * 0.95} fill={fur} stroke={DARK} strokeWidth={r * 0.07} />
      <ellipse cx={cx - r * 0.34} cy={cy - r * 0.44} rx={r * 0.46} ry={r * 0.27} fill={`url(#shn-${u})`} />
      {/* 우라지로(배쪽 크림) — 볼 + 주둥이가 이어져 시바 특유의 마스크 */}
      <ellipse cx={cx - r * 0.62} cy={cy + r * 0.26} rx={r * 0.32} ry={r * 0.28} fill={cream} />
      <ellipse cx={cx + r * 0.62} cy={cy + r * 0.26} rx={r * 0.32} ry={r * 0.28} fill={cream} />
      <ellipse cx={cx} cy={cy + r * 0.34} rx={r * 0.44} ry={r * 0.34} fill={cream} />
      {/* 눈 위 크림 점 (시바 눈썹) */}
      <ellipse cx={cx - r * 0.4} cy={cy - r * 0.34} rx={r * 0.15} ry={r * 0.1} fill={cream} opacity="0.9" />
      <ellipse cx={cx + r * 0.4} cy={cy - r * 0.34} rx={r * 0.15} ry={r * 0.1} fill={cream} opacity="0.9" />
      {eye(-1)}{eye(1)}
      {/* 코 */}
      <ellipse cx={cx} cy={cy + r * 0.22} rx={r * 0.14} ry={r * 0.11} fill={DARK} />
      <ellipse cx={cx - r * 0.05} cy={cy + r * 0.19} rx={r * 0.045} ry={r * 0.03} fill="#fff" opacity="0.45" />
      {/* 입 — 시바 특유의 방긋 미소 */}
      <path
        d={`M${cx} ${cy + r * 0.33} L${cx} ${cy + r * 0.41} M${cx - r * 0.28} ${cy + r * 0.41} Q${cx - r * 0.14} ${cy + r * 0.54} ${cx} ${cy + r * 0.41} Q${cx + r * 0.14} ${cy + r * 0.54} ${cx + r * 0.28} ${cy + r * 0.41}`}
        stroke={DARK} strokeWidth={r * 0.055} fill="none" strokeLinecap="round" strokeLinejoin="round"
      />
      {band && (
        <>
          <path
            d={`M${cx - r * 0.95} ${cy - r * 0.45} Q${cx} ${cy - r * 0.85} ${cx + r * 0.95} ${cy - r * 0.45} L${cx + r * 0.95} ${cy - r * 0.7} Q${cx} ${cy - r * 1.05} ${cx - r * 0.95} ${cy - r * 0.7} Z`}
            fill={`url(#vg-${u})`} stroke={DARK} strokeWidth={r * 0.06}
          />
          <rect x={cx - r * 1.02} y={cy - r * 0.74} width={r * 0.17} height={r * 0.26} rx={r * 0.06}
            fill={`url(#vg-${u})`} stroke={DARK} strokeWidth={r * 0.05} />
        </>
      )}
    </>
  );
}
