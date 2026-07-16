"use client";
// 바텀시트 — 오버레이 + 아래에서 슬라이드 업 (스펙 §1 형태)
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";
import { sheetUp } from "@/lib/motion";

export function BottomSheet({
  open,
  onClose,
  children,
  tall = false,
}: {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  tall?: boolean; // 화면 거의 전체
}) {
  const reduce = useReducedMotion();
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 z-50 bg-black/70 backdrop-blur-[2px]"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className={`fixed bottom-0 left-1/2 z-[60] w-full max-w-md -translate-x-1/2 overflow-y-auto rounded-t-2xl border-x border-t border-white/10 bg-card lg:max-w-lg ${
              tall ? "top-6" : "max-h-[85vh]"
            }`}
            variants={reduce ? undefined : sheetUp}
            initial={reduce ? { y: 0 } : "hidden"}
            animate="show"
            exit={reduce ? undefined : "exit"}
            style={{ x: "-50%" }}
          >
            <button
              className="sticky top-0 z-10 flex w-full justify-center bg-card/95 pb-1 pt-3 backdrop-blur"
              onClick={onClose}
              aria-label="닫기"
            >
              <span className="h-1.5 w-10 rounded-full bg-white/15" />
            </button>
            <div className="px-5 pb-8">{children}</div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
