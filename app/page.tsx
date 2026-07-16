"use client";
// 첫 화면 — 주 종목(v2.primaryMode)에 따라 헬스/러닝으로 이동
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    let mode: "gym" | "run" = "gym";
    try {
      const db = JSON.parse(localStorage.getItem("gymrun_v1") || "{}");
      mode = db.users?.[db.currentId]?.v2?.primaryMode ?? "gym";
    } catch { /* 기본값 */ }
    router.replace(mode === "run" ? "/run" : "/today");
  }, [router]);
  return null;
}
