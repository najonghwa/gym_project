"use client";
// 주간 볼륨 막대 — 이번주만 볼트, 나머지 그레이 (스펙 P1-5)
import { Bar, BarChart, Cell, LabelList, ResponsiveContainer, XAxis } from "recharts";
import { useReducedMotion } from "framer-motion";
import CountUp from "react-countup";
import { VOLUME_WEEKS } from "@/lib/mock/routines";

export function VolumeGroupedBar() {
  const reduce = useReducedMotion();
  const data = VOLUME_WEEKS;
  const diff = data[2].volume - data[1].volume;
  return (
    <div>
      <div className="mb-2 flex items-baseline gap-2">
        <span className="font-display text-[28px] leading-none text-volt">
          {reduce ? data[2].volume.toLocaleString() : <CountUp end={data[2].volume} duration={1} separator="," />}
        </span>
        <span className="text-[12px] text-white/55">kg·vol</span>
        <span className={`ml-auto text-[12.5px] font-bold ${diff >= 0 ? "text-volt" : "text-danger"}`}>
          {diff >= 0 ? "▲" : "▼"} {Math.abs(diff).toLocaleString()} 지난주 대비
        </span>
      </div>
      <div className="h-36">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 16 }}>
            <XAxis dataKey="name" tick={{ fill: "rgba(255,255,255,0.45)", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Bar dataKey="volume" radius={[6, 6, 0, 0]} animationDuration={reduce ? 0 : 600}>
              {data.map((_, i) => (
                <Cell key={i} fill={i === data.length - 1 ? "#ccff00" : "rgba(255,255,255,0.18)"} />
              ))}
              <LabelList dataKey="volume" position="top" formatter={(v) => Number(v).toLocaleString()} style={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
