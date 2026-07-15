// 공용 framer-motion variants (스펙 §2-2)
// 진입 200–400ms, easing [0.22,1,0.36,1], 리스트는 stagger
import type { Variants } from "framer-motion";

export const EASE = [0.22, 1, 0.36, 1] as const;

export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: EASE } },
};

export const popIn: Variants = {
  hidden: { opacity: 0, scale: 0.85 },
  show: { opacity: 1, scale: 1, transition: { duration: 0.3, ease: EASE } },
};

export const staggerContainer: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06, delayChildren: 0.05 } },
};

// 바텀시트 슬라이드
export const sheetUp: Variants = {
  hidden: { y: "100%" },
  show: { y: 0, transition: { duration: 0.3, ease: EASE } },
  exit: { y: "100%", transition: { duration: 0.22, ease: EASE } },
};
