"use client";
// 시트 — 모바일: 아래에서 슬라이드 업 / 데스크탑: 중앙 모달 (flex 센터링, 내부 스크롤로 짤림 방지)
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
          <div className="pointer-events-none fixed inset-0 z-[60] flex items-end justify-center lg:items-center lg:p-8">
            <motion.div
              className={`pointer-events-auto relative w-full max-w-md overflow-y-auto rounded-t-2xl border-x border-t border-white/10 bg-card lg:max-w-xl lg:rounded-2xl lg:border ${
                tall ? "max-h-[calc(100vh-24px)] lg:max-h-[90vh]" : "max-h-[85vh]"
              }`}
              variants={reduce ? undefined : sheetUp}
              initial={reduce ? { y: 0 } : "hidden"}
              animate="show"
              exit={reduce ? undefined : "exit"}
            >
              {/* 모바일: 드래그 핸들 */}
              <button
                className="sticky top-0 z-10 flex w-full justify-center bg-card/95 pb-1 pt-3 backdrop-blur lg:hidden"
                onClick={onClose}
                aria-label="닫기"
              >
                <span className="h-1.5 w-10 rounded-full bg-white/15" />
              </button>
              {/* 데스크탑: 우상단 닫기 */}
              <button
                className="absolute right-4 top-4 z-10 hidden h-8 w-8 place-items-center rounded-lg text-[14px] text-white/40 hover:bg-white/5 hover:text-white lg:grid"
                onClick={onClose}
                aria-label="닫기"
              >
                ✕
              </button>
              <div className="px-5 pb-8 lg:px-6 lg:pt-6">{children}</div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
