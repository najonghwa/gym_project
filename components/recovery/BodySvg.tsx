"use client";
// 회복도 바디맵 SVG — front/back, 부위 클릭 (스펙 P0-1)
import { motion, useReducedMotion } from "framer-motion";
import type { Muscle } from "@/lib/recovery";

type Shape =
  | ["c", number, number, number]
  | ["e", number, number, number, number]
  | ["r", number, number, number, number, number];

// 회색 실루엣 (공통)
const BODY: Shape[] = [
  ["c", 50, 13, 8], ["r", 46, 20, 8, 7, 2], ["r", 36, 26, 28, 47, 9],
  ["r", 26, 29, 9, 25, 4.5], ["r", 65, 29, 9, 25, 4.5],
  ["r", 25, 55, 8, 23, 4], ["r", 67, 55, 8, 23, 4],
  ["r", 38, 72, 24, 13, 5],
  ["r", 38, 84, 11, 35, 5], ["r", 51, 84, 11, 35, 5],
  ["r", 39, 119, 9, 33, 4], ["r", 52, 119, 9, 33, 4],
];

// 부위 → 표시 뷰 + 도형들
const REGION: Record<Muscle, { view: "front" | "back"; shapes: Shape[] }> = {
  chest:     { view: "front", shapes: [["e", 43, 36, 6.5, 5], ["e", 57, 36, 6.5, 5]] },
  shoulders: { view: "front", shapes: [["c", 30.5, 32, 5], ["c", 69.5, 32, 5]] },
  biceps:    { view: "front", shapes: [["e", 30.5, 42, 4, 8], ["e", 69.5, 42, 4, 8]] },
  abs:       { view: "front", shapes: [["r", 42, 45, 16, 26, 4]] },
  legs:      { view: "front", shapes: [["e", 43.5, 100, 5, 14], ["e", 56.5, 100, 5, 14], ["e", 43.5, 130, 4.5, 11], ["e", 56.5, 130, 4.5, 11]] },
  back:      { view: "back", shapes: [["r", 38, 29, 24, 20, 6], ["e", 50, 55, 11, 12]] },
  triceps:   { view: "back", shapes: [["e", 30.5, 44, 4, 8], ["e", 69.5, 44, 4, 8]] },
  glutes:    { view: "back", shapes: [["c", 44, 78, 6.5], ["c", 56, 78, 6.5]] },
};

function shapeEl(s: Shape, key: string, fill: string, props?: object) {
  if (s[0] === "c") return <circle key={key} cx={s[1]} cy={s[2]} r={s[3]} fill={fill} {...props} />;
  if (s[0] === "e") return <ellipse key={key} cx={s[1]} cy={s[2]} rx={s[3]} ry={s[4]} fill={fill} {...props} />;
  return <rect key={key} x={s[1]} y={s[2]} width={s[3]} height={s[4]} rx={s[5]} fill={fill} {...props} />;
}

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
  const muscles = (Object.keys(REGION) as Muscle[]).filter((m) => REGION[m].view === view);
  return (
    <svg viewBox="0 0 100 158" className="h-full w-full">
      {BODY.map((s, i) => shapeEl(s, `b${i}`, "#27272a"))}
      {muscles.map((m) => (
        <motion.g
          key={`${view}-${m}`}
          className="cursor-pointer"
          initial={reduce ? false : { opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          onClick={() => onSelect(m)}
        >
          {REGION[m].shapes.map((s, i) =>
            shapeEl(s, `${m}${i}`, colorOf(m), { style: { transition: "fill .6s" } })
          )}
        </motion.g>
      ))}
    </svg>
  );
}

export const REGION_VIEW: Record<Muscle, "front" | "back"> = Object.fromEntries(
  (Object.keys(REGION) as Muscle[]).map((m) => [m, REGION[m].view])
) as Record<Muscle, "front" | "back">;
