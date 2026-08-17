"use client";
// 뱃지/PR 축하 모달 — confetti + 마스코트 cheer + 금속 뱃지 (스펙 P2-11)
import { Icon, IconName } from "@/components/ui/Icon";
import { useEffect } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import confetti from "canvas-confetti";
import { ShibaFlex } from "@/components/mascot/ShibaPoses";
import { LottieMascot } from "@/components/mascot/LottieMascot";
import { PillButton } from "@/components/ui/PillButton";

export function AchievementModal({
  open,
  title,
  desc,
  icon = "medal",
  onClose,
}: {
  open: boolean;
  title: string;
  desc: string;
  icon?: IconName;
  onClose: () => void;
}) {
  const reduce = useReducedMotion();

  useEffect(() => {
    if (open && !reduce) {
      confetti({ particleCount: 120, spread: 80, origin: { y: 0.6 }, colors: ["#c8ff00", "#f59e0b", "#ffffff"] });
    }
  }, [open, reduce]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[70] grid place-items-center bg-black/80 p-6 backdrop-blur-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            initial={reduce ? false : { scale: 0.8, y: 24 }}
            animate={{ scale: 1, y: 0 }}
            exit={reduce ? undefined : { scale: 0.9, opacity: 0 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="w-full max-w-xs rounded-2xl border border-gold/40 bg-card p-6 text-center"
          >
            <div className="flex justify-center"><LottieMascot name="celebrate" size={116} fallback={<ShibaFlex size={110} />} /></div>
            {/* 금속 뱃지 */}
            <motion.div
              initial={reduce ? false : { rotateY: 90 }}
              animate={{ rotateY: 0 }}
              transition={{ delay: 0.25, duration: 0.5 }}
              className="mx-auto mt-2 grid h-20 w-20 place-items-center rounded-full border-[3px] border-gold bg-gold/15 text-gold"
            >
              <Icon name={icon} size={36} strokeWidth={1.9} />
            </motion.div>
            <div className="lab mt-4">달성</div>
            <h3 className="mt-1 font-display text-[24px]">{title}</h3>
            <p className="mt-1 text-[13px] text-white/55">{desc}</p>
            <PillButton className="mt-5 w-full" onClick={onClose}>계속</PillButton>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
