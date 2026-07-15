"use client";
// pill 버튼 — volt(주요) / ghost(보조)  (스펙 §1 형태)
import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

export function PillButton({
  variant = "volt",
  className = "",
  children,
  onClick,
  disabled,
}: {
  variant?: "volt" | "ghost";
  className?: string;
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}) {
  const reduce = useReducedMotion();
  const base =
    "min-h-11 rounded-full px-5 py-3 text-[15px] font-extrabold transition disabled:opacity-40";
  const look =
    variant === "volt"
      ? "bg-volt text-black shadow-lg shadow-volt/10"
      : "border border-white/15 bg-white/5 text-zinc-100";
  return (
    <motion.button
      whileTap={reduce ? undefined : { scale: 0.96 }}
      className={`${base} ${look} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </motion.button>
  );
}
