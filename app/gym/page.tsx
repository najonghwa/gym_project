"use client";
// 헬스장 — SVG 평면도 + 장비 클릭 → 정보 시트 (gym_web 포팅)
import { useState } from "react";
import { BottomSheet } from "@/components/ui/BottomSheet";
import { EQUIP_INFO, FLOOR, FLOOR_ZONES, ZONES } from "@/lib/data/gym";

export default function GymPage() {
  const [sel, setSel] = useState<string | null>(null);
  const info = sel ? EQUIP_INFO[sel] : null;
  const item = sel ? FLOOR.find((f) => f.eq === sel) : null;
  const zone = item ? ZONES.find((z) => z.id === item.zone) : null;

  return (
    <main className="lg:mx-auto lg:max-w-3xl lg:pt-10">
      <div className="lab mb-1">FLOOR MAP 헬스장 평면도</div>
      <h2 className="font-display text-[26px]">장비를 눌러보세요</h2>
      <p className="mt-0.5 text-[12px] text-white/45">설명과 사용 팁이 나와요 · 현재는 예시 배치</p>

      <div className="mt-4 rounded-2xl border border-white/[0.06] bg-card p-3">
        <svg viewBox="0 0 400 310" className="w-full rounded-lg bg-black/40">
          {FLOOR_ZONES.map((fz) => {
            const z = ZONES.find((x) => x.id === fz.id)!;
            return (
              <g key={fz.id}>
                <rect x={fz.x} y={fz.y} width={fz.w} height={fz.h} rx={10}
                  fill={`${z.color}0d`} stroke={`${z.color}55`} strokeWidth={1.2} />
                <text x={fz.x + 8} y={fz.y + 16} fontSize={9} fontWeight={800} fill={z.color}>
                  {fz.id} · {z.name}
                </text>
              </g>
            );
          })}
          {FLOOR.map((f) => {
            const z = ZONES.find((x) => x.id === f.zone)!;
            return (
              <g key={f.eq} className="cursor-pointer" onClick={() => setSel(f.eq)}>
                <rect x={f.x - 19} y={f.y - 15} width={38} height={30} rx={7}
                  fill="#1a1a1a" stroke={`${z.color}88`} strokeWidth={1} />
                <text x={f.x} y={f.y + 1} fontSize={12} textAnchor="middle">{f.icon}</text>
                <text x={f.x} y={f.y + 11} fontSize={5.2} textAnchor="middle" fill="#9ca3af">{f.eq}</text>
              </g>
            );
          })}
          <rect x={178} y={300} width={44} height={8} rx={3} fill="#3f3f46" />
          <text x={200} y={297} fontSize={7} textAnchor="middle" fill="#9ca3af">🚪 입구</text>
        </svg>
        <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1.5">
          {ZONES.map((z) => (
            <span key={z.id} className="flex items-center gap-1.5 text-[11.5px] text-white/55">
              <i className="inline-block h-2.5 w-2.5 rounded-sm" style={{ background: z.color }} />
              {z.id} {z.name}
            </span>
          ))}
        </div>
      </div>

      {/* 구역별 장비 칩 */}
      <div className="mt-4 space-y-3">
        {ZONES.map((z) => (
          <div key={z.id}>
            <div className="text-[12.5px] font-bold" style={{ color: z.color }}>{z.id}구역 · {z.name}</div>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {FLOOR.filter((f) => f.zone === z.id).map((f) => (
                <button
                  key={f.eq}
                  onClick={() => setSel(f.eq)}
                  className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-[12px] font-bold text-white/70 active:scale-95"
                >
                  {f.icon} {f.eq}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      <BottomSheet open={!!sel} onClose={() => setSel(null)}>
        {item && info && zone && (
          <>
            <div className="flex items-center gap-3.5">
              <div className="grid h-14 w-14 place-items-center rounded-lg border border-white/10 bg-white/[0.05] text-3xl">{item.icon}</div>
              <div>
                <h3 className="text-lg font-extrabold">{item.eq}</h3>
                <span className="text-[12px] font-bold" style={{ color: zone.color }}>{zone.id}구역 · {zone.name}</span>
              </div>
            </div>
            <p className="mt-3 text-[14px] leading-relaxed">{info.desc}</p>
            <div className="mt-3 rounded-lg border border-gold/40 bg-gold/10 p-3 text-[13px] leading-relaxed">
              💡 <b>팁</b> — {info.tip}
            </div>
          </>
        )}
      </BottomSheet>
    </main>
  );
}
