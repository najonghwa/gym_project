"use client";
// 브랜드 마스코트 — 바벨 스쿼트하는 시바견 (three.js 사전 렌더 PNG + CSS 모션)
import { MascotImg } from "./MascotImg";

export function ShibaLifter({ size = 120, animate = true }: { size?: number; animate?: boolean }) {
  return <MascotImg kind="lift" label="운동하는 시바견 마스코트" size={size} animate={animate} />;
}
