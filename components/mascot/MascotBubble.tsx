"use client";
// 말풍선 + 마스코트 (스펙 §2-1)
import { motion, useReducedMotion } from "framer-motion";
import { Mascot, MascotState } from "./Mascot";
import { fadeUp } from "@/lib/motion";

export function MascotBubble({
  quote,
  state = "talk",
}: {
  quote: string;
  state?: MascotState;
}) {
  const reduce = useReducedMotion();
  return (
    <div className="flex items-end gap-3">
      <Mascot state={state} size={84} />
      <motion.div
        variants={reduce ? undefined : fadeUp}
        initial={reduce ? false : "hidden"}
        animate="show"
        className="relative flex-1 rounded-3xl rounded-bl-md border border-white/[0.06] bg-card px-4 py-3.5"
      >
        <p className="text-[14px] font-medium leading-relaxed">💬 {quote}</p>
      </motion.div>
    </div>
  );
}
