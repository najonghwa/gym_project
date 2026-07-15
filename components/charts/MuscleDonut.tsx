"use client";
// 주동/협응 기여% 도넛 (스펙 P0-2)
import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";
import { useReducedMotion } from "framer-motion";
import { MUSCLE_KR, type Muscle } from "@/lib/recovery";

const COLORS = ["#ff9432", "#f59e0b", "#38bdf8", "#a78bfa"];

export function MuscleDonut({ contrib }: { contrib: { muscle: Muscle; pct: number }[] }) {
  const reduce = useReducedMotion();
  return (
    <div className="flex items-center gap-3">
      <div className="h-28 w-28 shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={contrib}
              dataKey="pct"
              innerRadius={34}
              outerRadius={52}
              paddingAngle={3}
              stroke="none"
              animationDuration={reduce ? 0 : 700}
            >
              {contrib.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="flex-1 space-y-1.5">
        {contrib.map((c, i) => (
          <div key={c.muscle} className="flex items-center gap-2 text-[12.5px]">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ background: COLORS[i % COLORS.length] }} />
            <span className="flex-1 text-white/70">{MUSCLE_KR[c.muscle]}</span>
            <b className="tabular-nums">{c.pct}%</b>
          </div>
        ))}
      </div>
    </div>
  );
}
