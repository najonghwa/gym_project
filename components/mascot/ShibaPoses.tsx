"use client";
// 마스코트 추가 포즈 — 러닝 / 플렉스(자랑) / 휴식 (three.js 사전 렌더 PNG + CSS 모션)
// 5종이 각각 다른 축으로 움직인다: 리프트=수직, 코치=수평, 러너=대각, 플렉스=회전, 휴식=호흡
import { MascotImg } from "./MascotImg";

export function ShibaRunner({ size = 96, animate = true }: { size?: number; animate?: boolean }) {
  return <MascotImg kind="run" label="달리는 시바견" size={size} animate={animate} />;
}

export function ShibaFlex({ size = 104, animate = true }: { size?: number; animate?: boolean }) {
  return <MascotImg kind="flex" label="자랑하는 시바견" size={size} animate={animate} />;
}

export function ShibaRest({ size = 88, animate = true }: { size?: number; animate?: boolean }) {
  return <MascotImg kind="rest" label="쉬는 시바견" size={size} animate={animate} />;
}
