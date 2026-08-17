"use client";
// 러닝 기록 상세 — 경로 지도(Leaflet+Carto 다크타일) + 1km 스플릿 + 이 러닝의 거리별 최고 페이스
import { useEffect, useRef } from "react";
import type { Map as LeafletMap } from "leaflet";
import { BottomSheet } from "@/components/ui/BottomSheet";
import { splits, runBestTime, BEST_DISTS, type RunRec } from "@/lib/runmath";

const paceStr = (sec?: number | null) =>
  sec ? `${Math.floor(sec / 60)}'${String(Math.round(sec % 60)).padStart(2, "0")}"` : "—";
const fmtT = (s: number) => {
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), ss = Math.floor(s % 60);
  return (h ? `${h}:` : "") + `${String(m).padStart(h ? 2 : 1, "0")}:${String(ss).padStart(2, "0")}`;
};

export function RouteMap({ route }: { route: number[][] }) {
  const divRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<LeafletMap | null>(null);

  useEffect(() => {
    let dead = false;
    (async () => {
      const L = (await import("leaflet")).default;
      if (dead || !divRef.current || mapRef.current) return;
      const pts = route.map((p) => [p[0], p[1]] as [number, number]);
      const map = L.map(divRef.current, { zoomControl: false, attributionControl: true, dragging: true, scrollWheelZoom: false });
      L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; OpenStreetMap &copy; CARTO', maxZoom: 19,
      }).addTo(map);
      L.polyline(pts, { color: "#c8ff00", weight: 4, opacity: 0.9 }).addTo(map);
      L.circleMarker(pts[0], { radius: 6, color: "#2dd4a0", fillColor: "#2dd4a0", fillOpacity: 1 }).addTo(map); // 출발
      L.circleMarker(pts[pts.length - 1], { radius: 6, color: "#ef4444", fillColor: "#ef4444", fillOpacity: 1 }).addTo(map); // 도착
      map.fitBounds(L.latLngBounds(pts), { padding: [24, 24] });
      mapRef.current = map;
    })();
    return () => { dead = true; mapRef.current?.remove(); mapRef.current = null; };
  }, [route]);

  return <div ref={divRef} className="h-52 w-full overflow-hidden rounded-lg border border-white/10 bg-white/[0.03]" />;
}

export function RunDetailSheet({
  run, onClose, onDelete,
}: {
  run: RunRec | null;
  onClose: () => void;
  onDelete: (r: RunRec) => void;
}) {
  const sp = run ? splits(run.route) : [];
  const maxSp = Math.max(1, ...sp.map((s) => s.paceSec));
  const minSp = Math.min(...sp.map((s) => s.paceSec), Infinity);
  const bests = run ? BEST_DISTS.map((m) => ({ m, sec: runBestTime(run, m) })).filter((b) => b.sec != null) : [];

  return (
    <BottomSheet open={!!run} onClose={onClose}>
      {run && (
        <>
          <div className="flex items-baseline justify-between">
            <h3 className="text-lg font-extrabold">{run.date}</h3>
            <span className="text-[12px] text-white/45">{run.route ? "GPS 기록" : "수동 기록"}</span>
          </div>
          <div className="mt-3 grid grid-cols-3 gap-2">
            {([["거리", `${run.km}km`], ["평균 페이스", `${paceStr(run.paceSec)}/km`], ["시간", run.durSec ? fmtT(run.durSec) : "—"]] as const).map(([l, v]) => (
              <div key={l} className="rounded-lg bg-white/[0.05] py-2.5 text-center">
                <div className="font-display text-[16px] leading-none tabular-nums">{v}</div>
                <div className="mt-1 text-[9.5px] text-white/45">{l}</div>
              </div>
            ))}
          </div>

          {/* 경로 지도 */}
          {run.route && run.route.length >= 2 ? (
            <div className="mt-3"><RouteMap route={run.route} /></div>
          ) : (
            <p className="mt-3 rounded-lg bg-white/[0.04] p-3 text-center text-[12px] text-white/40">
              직접 입력한 기록에는 경로가 없어요. GPS 러닝으로 기록하면 지도가 표시됩니다.
            </p>
          )}

          {/* 1km 스플릿 */}
          {sp.length > 0 && (
            <div className="mt-4">
              <div className="lab mb-2">구간 페이스 (1km마다)</div>
              <div className="space-y-1.5">
                {sp.map((s) => (
                  <div key={s.label} className="flex items-center gap-2.5">
                    <span className="w-12 shrink-0 text-[11.5px] font-bold text-white/55">{s.label}</span>
                    <div className="h-3.5 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
                      <div
                        className={`h-full rounded-full ${s.paceSec === minSp ? "bg-gold" : "bg-volt"}`}
                        style={{ width: `${Math.max(12, (1 - (s.paceSec - minSp * 0.85) / (maxSp - minSp * 0.85 || 1)) * 100)}%` }}
                      />
                    </div>
                    <b className="w-14 shrink-0 text-right text-[12px] tabular-nums">
                      {paceStr(s.paceSec)}{s.paceSec === minSp && sp.length > 1 ? " ⚡" : ""}
                    </b>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 이 러닝의 거리별 최고 구간 */}
          {bests.length > 0 && run.route && (
            <div className="mt-4">
              <div className="lab mb-2">이 러닝의 최고 구간</div>
              <div className="grid grid-cols-2 gap-2">
                {bests.map((b) => (
                  <div key={b.m} className="flex items-baseline justify-between rounded-lg bg-white/[0.05] px-3.5 py-2.5">
                    <span className="text-[12px] font-bold text-white/55">{b.m / 1000}km</span>
                    <b className="font-display text-[15px] text-volt tabular-nums">{paceStr(Math.round(b.sec! / (b.m / 1000)))}<span className="text-[10px] text-white/40">/km</span></b>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={() => { if (window.confirm(`${run.date} · ${run.km}km 기록을 삭제할까요?`)) { onDelete(run); onClose(); } }}
            className="mt-5 w-full rounded-lg border border-danger/30 py-3 text-[13px] font-bold text-danger/80"
          >
            이 기록 삭제
          </button>
        </>
      )}
    </BottomSheet>
  );
}
