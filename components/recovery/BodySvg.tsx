"use client";
// 회복도 바디맵 — 실제 근육 모양 SVG (front/back), 부위 클릭
// Gymwork 스타일 참고: 근육별 형태 + 회복색(볼트→골드→레드) 채색
import { motion, useReducedMotion } from "framer-motion";
import type { Muscle } from "@/lib/recovery";

const SIL = "#2a2a2e";   // 실루엣
const LINE = "#0c0c0d";  // 근육 사이 골

// 오른쪽 절반 path + 좌우 미러 (몸 중심 x=100, viewBox 0 0 200 340)
function Mirror({ d, fill, onClick }: { d: string; fill: string; onClick?: () => void }) {
  const common = {
    d, fill, stroke: LINE, strokeWidth: 1.4,
    style: { transition: "fill .6s", cursor: onClick ? "pointer" : undefined },
    onClick,
  };
  return (
    <>
      <path {...common} />
      <path {...common} transform="translate(200,0) scale(-1,1)" />
    </>
  );
}

// ── 실루엣 (공통) ──
function Silhouette() {
  return (
    <g fill={SIL}>
      <ellipse cx={100} cy={24} rx={15} ry={19} />
      <rect x={91} y={40} width={18} height={16} rx={5} />
      {/* 몸통 */}
      <path d="M100 52 L58 62 Q52 66 53 76 L60 118 Q62 132 70 142 L74 176 Q76 190 84 196 L100 200 Z" />
      <path d="M100 52 L58 62 Q52 66 53 76 L60 118 Q62 132 70 142 L74 176 Q76 190 84 196 L100 200 Z" transform="translate(200,0) scale(-1,1)" />
      {/* 팔 */}
      <path d="M58 64 Q46 72 44 92 L38 150 Q36 166 40 176 L50 174 Q54 160 54 146 L60 100 Q62 80 62 70 Z" />
      <path d="M58 64 Q46 72 44 92 L38 150 Q36 166 40 176 L50 174 Q54 160 54 146 L60 100 Q62 80 62 70 Z" transform="translate(200,0) scale(-1,1)" />
      <ellipse cx={42} cy={186} rx={7} ry={10} />
      <ellipse cx={158} cy={186} rx={7} ry={10} />
      {/* 다리 */}
      <path d="M84 196 Q78 240 80 268 L82 312 Q83 322 88 326 L100 326 L100 198 Z" />
      <path d="M84 196 Q78 240 80 268 L82 312 Q83 322 88 326 L100 326 L100 198 Z" transform="translate(200,0) scale(-1,1)" />
      <ellipse cx={91} cy={332} rx={11} ry={6} />
      <ellipse cx={109} cy={332} rx={11} ry={6} />
    </g>
  );
}

// 근육 정의: view별 (오른쪽 절반 path, 미러 자동)
const FRONT: { m: Muscle; d: string }[] = [
  // 어깨 (전면 삼각근)
  { m: "shoulders", d: "M60 62 Q48 68 46 84 Q52 92 62 88 Q68 80 66 68 Q64 62 60 62 Z" },
  // 가슴 (대흉근)
  { m: "chest", d: "M99 66 L68 70 Q62 84 66 98 Q74 110 90 112 Q98 112 99 108 Z" },
  // 이두
  { m: "biceps", d: "M48 92 Q44 108 46 124 Q52 130 58 124 Q60 108 58 96 Q52 88 48 92 Z" },
  // 전완 (front)
  { m: "biceps", d: "M42 132 Q38 150 40 168 Q45 172 49 166 Q52 150 50 136 Q46 128 42 132 Z" },
  // 복근 (6팩 + 외복사근)
  { m: "abs", d: "M99 116 L84 118 Q82 128 84 136 L99 137 Z" },
  { m: "abs", d: "M99 141 L84 140 Q83 150 85 158 L99 159 Z" },
  { m: "abs", d: "M99 163 L85 162 Q86 176 92 186 L99 188 Z" },
  { m: "abs", d: "M80 118 Q74 130 76 148 Q78 160 82 168 Q84 150 82 134 Q81 124 80 118 Z" },
  // 대퇴사두
  { m: "legs", d: "M86 202 Q78 226 80 252 Q84 266 92 268 Q98 262 98 244 Q98 218 94 204 Q90 198 86 202 Z" },
  // 전경골근(정강이)
  { m: "legs", d: "M84 276 Q81 294 83 312 Q87 318 91 312 Q93 296 91 280 Q88 272 84 276 Z" },
];

const BACK: { m: Muscle; d: string }[] = [
  // 승모근
  { m: "back", d: "M99 46 L78 58 Q86 72 92 92 Q97 98 99 96 Z" },
  // 광배근 (날개)
  { m: "back", d: "M97 100 Q80 98 70 92 Q66 108 72 126 Q80 142 92 148 Q97 140 97 126 Z" },
  // 기립근 (허리)
  { m: "back", d: "M99 150 L91 150 Q89 162 91 176 L99 178 Z" },
  // 후면 어깨
  { m: "shoulders", d: "M62 60 Q50 66 48 82 Q54 90 63 86 Q68 76 66 66 Q64 60 62 60 Z" },
  // 삼두
  { m: "triceps", d: "M48 90 Q43 108 45 126 Q51 132 57 126 Q60 108 57 94 Q52 84 48 90 Z" },
  // 전완 (back)
  { m: "triceps", d: "M41 134 Q37 152 39 168 Q44 173 48 167 Q51 150 49 136 Q45 128 41 134 Z" },
  // 둔근
  { m: "glutes", d: "M98 182 Q84 180 78 190 Q76 206 84 214 Q94 218 98 212 Z" },
  // 햄스트링
  { m: "legs", d: "M86 220 Q80 244 82 266 Q88 274 94 268 Q98 248 96 228 Q92 216 86 220 Z" },
  // 종아리 (비복근)
  { m: "legs", d: "M83 278 Q79 296 82 312 Q88 320 93 312 Q96 294 92 280 Q87 270 83 278 Z" },
];

export function BodySvg({
  view,
  colorOf,
  onSelect,
}: {
  view: "front" | "back";
  colorOf: (m: Muscle) => string;
  onSelect: (m: Muscle) => void;
}) {
  const reduce = useReducedMotion();
  const parts = view === "front" ? FRONT : BACK;
  return (
    <svg viewBox="0 0 200 340" className="h-full w-full">
      <Silhouette />
      <motion.g
        key={view}
        initial={reduce ? false : { opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.55 }}
      >
        {parts.map((p, i) => (
          <Mirror key={`${view}-${i}`} d={p.d} fill={colorOf(p.m)} onClick={() => onSelect(p.m)} />
        ))}
      </motion.g>
    </svg>
  );
}

// 부위 → 잘 보이는 뷰 (리스트 클릭 시 자동 전환용)
export const REGION_VIEW: Record<Muscle, "front" | "back"> = {
  chest: "front", shoulders: "front", biceps: "front", abs: "front", legs: "front",
  back: "back", triceps: "back", glutes: "back",
};
