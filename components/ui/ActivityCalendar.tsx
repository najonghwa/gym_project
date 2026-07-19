"use client";
// 활동 달력 — 히트맵 대신 실제 월 달력으로 (운동한 날 = 볼트, 진할수록 많음)
const pad = (n: number) => String(n).padStart(2, "0");
const WD = ["일", "월", "화", "수", "목", "금", "토"];

export function ActivityCalendar({
  data, months = 3, color = "#c8ff00", suffix = "",
}: {
  data: Map<string, number>;
  months?: number;
  color?: string;
  suffix?: string; // 툴팁 단위 (세트/km)
}) {
  const max = Math.max(1, ...data.values());
  const now = new Date();
  const todayS = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;

  const grids = Array.from({ length: months }, (_, i) => {
    const d = new Date(now.getFullYear(), now.getMonth() - (months - 1 - i), 1);
    const y = d.getFullYear(), m = d.getMonth();
    const firstDow = new Date(y, m, 1).getDay(); // 0=일
    const lastDate = new Date(y, m + 1, 0).getDate();
    const cells: (number | null)[] = [...Array(firstDow).fill(null), ...Array.from({ length: lastDate }, (_, k) => k + 1)];
    return { y, m, cells };
  });

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {grids.map(({ y, m, cells }) => (
        <div key={`${y}-${m}`}>
          <div className="mb-1.5 text-center text-[12px] font-bold text-white/70">
            {m === 0 || (m === now.getMonth() && grids[0].m === m) ? `${y}년 ` : ""}{m + 1}월
          </div>
          <div className="grid grid-cols-7 gap-1 text-center">
            {WD.map((w, i) => (
              <span key={w} className={`text-[9px] ${i === 0 ? "text-danger/70" : i === 6 ? "text-sky-400/70" : "text-white/35"}`}>{w}</span>
            ))}
            {cells.map((day, idx) => {
              if (day == null) return <span key={idx} />;
              const key = `${y}-${pad(m + 1)}-${pad(day)}`;
              const v = data.get(key) ?? 0;
              const isToday = key === todayS;
              const op = v > 0 ? 0.28 + 0.72 * (v / max) : 0;
              return (
                <span
                  key={idx}
                  title={v > 0 ? `${key} · ${Math.round(v * 10) / 10}${suffix}` : key}
                  className={`grid aspect-square place-items-center rounded-md text-[10px] tabular-nums ${
                    v > 0 ? "font-extrabold text-black" : isToday ? "text-volt" : "text-white/45"
                  } ${isToday ? "ring-1 ring-volt" : ""}`}
                  style={{ background: v > 0 ? undefined : "rgba(255,255,255,0.04)", backgroundColor: v > 0 ? hexA(color, op) : undefined }}
                >
                  {day}
                </span>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

function hexA(hex: string, alpha: number) {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16), g = parseInt(h.slice(2, 4), 16), b = parseInt(h.slice(4, 6), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}
