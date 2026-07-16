// 러닝 수학 — 1km 구간 페이스(스플릿), 거리별 최고 페이스(1/3/5/10km 롤링 구간)
export type RunRec = { rid?: string; date: string; km: number; paceSec?: number | null; durSec?: number; route?: number[][] };

const EARTH = 6371000;
function hav(aLat: number, aLng: number, bLat: number, bLng: number) {
  const toR = (x: number) => (x * Math.PI) / 180;
  const dLat = toR(bLat - aLat), dLng = toR(bLng - aLng);
  const s = Math.sin(dLat / 2) ** 2 + Math.cos(toR(aLat)) * Math.cos(toR(bLat)) * Math.sin(dLng / 2) ** 2;
  return 2 * EARTH * Math.asin(Math.sqrt(s));
}

// route([lat,lng,경과초]) → 누적 거리(m)/시간(s) 배열. 시간 없는 옛 포맷이면 null
function cumulate(route?: number[][]): { dist: number[]; time: number[] } | null {
  if (!route || route.length < 2 || route[0].length < 3) return null;
  const dist = [0], time = [route[0][2]];
  for (let i = 1; i < route.length; i++) {
    dist.push(dist[i - 1] + hav(route[i - 1][0], route[i - 1][1], route[i][0], route[i][1]));
    time.push(route[i][2]);
  }
  return { dist, time };
}

// 1km 스플릿: [{km: 1, sec}, ...] + 마지막 부분구간(0.2km 이상일 때 {km: 0.x, sec})
export function splits(route?: number[][]): { label: string; paceSec: number }[] {
  const c = cumulate(route);
  if (!c) return [];
  const out: { label: string; paceSec: number }[] = [];
  let prevT = c.time[0], prevD = 0, kmMark = 1000;
  for (let i = 1; i < c.dist.length; i++) {
    while (c.dist[i] >= kmMark) {
      // kmMark 지점 시간 선형 보간
      const f = (kmMark - c.dist[i - 1]) / (c.dist[i] - c.dist[i - 1]);
      const tAt = c.time[i - 1] + f * (c.time[i] - c.time[i - 1]);
      out.push({ label: `${kmMark / 1000}km`, paceSec: Math.round(tAt - prevT) });
      prevT = tAt; prevD = kmMark; kmMark += 1000;
    }
  }
  const lastD = c.dist[c.dist.length - 1], lastT = c.time[c.time.length - 1];
  const remM = lastD - prevD;
  if (remM >= 200) {
    out.push({
      label: `+${(remM / 1000).toFixed(1)}km`,
      paceSec: Math.round(((lastT - prevT) / remM) * 1000), // 부분구간은 km 환산 페이스
    });
  }
  return out;
}

export const BEST_DISTS = [1000, 3000, 5000, 10000] as const;

// 한 러닝 안에서 targetM를 가장 빨리 달린 구간의 소요초 (투포인터+보간)
export function bestSegment(route: number[][] | undefined, targetM: number): number | null {
  const c = cumulate(route);
  if (!c || c.dist[c.dist.length - 1] < targetM) return null;
  let best = Infinity, i = 0;
  for (let j = 1; j < c.dist.length; j++) {
    while (i + 1 < j && c.dist[j] - c.dist[i + 1] >= targetM) i++;
    const span = c.dist[j] - c.dist[i];
    if (span >= targetM) {
      const excess = span - targetM;
      const segD = c.dist[i + 1] - c.dist[i];
      const segT = c.time[i + 1] - c.time[i];
      const shave = segD > 0 ? (excess / segD) * segT : 0; // 앞쪽 잉여만큼 시간 차감
      best = Math.min(best, c.time[j] - c.time[i] - shave);
    }
  }
  return isFinite(best) ? Math.round(best) : null;
}

// 러닝 1건의 거리별 최고 소요초 — GPS면 롤링 구간, 수동이면 평균 페이스 가정
export function runBestTime(run: RunRec, targetM: number): number | null {
  const gps = bestSegment(run.route, targetM);
  if (gps != null) return gps;
  if (!run.route && run.paceSec && run.km * 1000 >= targetM) return Math.round(run.paceSec * (targetM / 1000));
  return null;
}

// 전체 기록에서 거리별 PB — {m, sec(총 소요), paceSec(/km), date, gps} (없으면 sec null)
export function allBests(runs: RunRec[]) {
  return BEST_DISTS.map((m) => {
    let best: { sec: number; date: string; gps: boolean } | null = null;
    runs.forEach((r) => {
      const t = runBestTime(r, m);
      if (t != null && (!best || t < best.sec)) best = { sec: t, date: r.date, gps: !!r.route };
    });
    const b = best as { sec: number; date: string; gps: boolean } | null;
    return { m, sec: b?.sec ?? null, paceSec: b ? Math.round(b.sec / (m / 1000)) : null, date: b?.date ?? null, gps: b?.gps ?? false };
  });
}
