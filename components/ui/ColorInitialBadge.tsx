// 루틴 이니셜 뱃지 — 볼트/골드/틸 로테이션 (스펙 P2-9)
const TONES = [
  "bg-volt text-black",
  "bg-gold text-black",
  "bg-teal-400 text-black",
  "bg-sky-400 text-black",
];

export function ColorInitialBadge({ text, seed = 0 }: { text: string; seed?: number }) {
  return (
    <span
      className={`grid h-11 w-11 shrink-0 place-items-center rounded-lg font-display text-[15px] ${TONES[seed % TONES.length]}`}
    >
      {text}
    </span>
  );
}
