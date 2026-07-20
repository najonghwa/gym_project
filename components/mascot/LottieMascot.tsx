"use client";
// Lottie 마스코트 — /public/lottie/<name>.json 있으면 재생, 없으면 판다 SVG 폴백
// 사용자가 LottieFiles에서 고른 무료 애니메이션(상업 OK)을 public/lottie/에 넣으면 자동 교체
import { useEffect, useRef, useState } from "react";
import Lottie from "lottie-react";

export function LottieMascot({
  name, size = 120, fallback, loop = true,
}: {
  name: string;
  size?: number;
  fallback: React.ReactNode; // Lottie 없을 때(로딩·미제공) 보여줄 판다
  loop?: boolean;
}) {
  const [data, setData] = useState<object | null>(null);
  const [failed, setFailed] = useState(false);
  const tried = useRef(false);

  useEffect(() => {
    tried.current = false;
    setData(null); setFailed(false);
    let alive = true;
    fetch(`/lottie/${name}.json`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => { if (alive) setData(d); })
      .catch(() => { if (alive) setFailed(true); });
    return () => { alive = false; };
  }, [name]);

  if (data && !failed) {
    return <Lottie animationData={data} loop={loop} style={{ width: size, height: size }} />;
  }
  // 로딩 중·파일 없음 → 판다 폴백 (레이아웃 유지)
  return <span style={{ display: "inline-flex", width: size, height: size, alignItems: "center", justifyContent: "center" }}>{fallback}</span>;
}
