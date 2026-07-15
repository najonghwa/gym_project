// 난이도 ▪▪▪▫▫ (스펙 §2-3)
export function LevelDots({ level }: { level: 1 | 2 | 3 | 4 | 5 }) {
  return (
    <span className="inline-flex items-center gap-0.5" aria-label={`난이도 ${level}/5`}>
      {[1, 2, 3, 4, 5].map((i) => (
        <span
          key={i}
          className={`h-1.5 w-1.5 rounded-[2px] ${i <= level ? "bg-volt" : "bg-white/15"}`}
        />
      ))}
      <span className="ml-1 text-[10px] text-white/55">Lv{level}</span>
    </span>
  );
}
