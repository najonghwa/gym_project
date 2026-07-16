"use client";
// 내비 — 모바일: 하단 7탭 / 데스크탑: 좌측 사이드바
import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/today", em: "🏋️", t: "헬스" },
  { href: "/run", em: "🏃", t: "러닝" },
  { href: "/calendar", em: "📅", t: "달력" },
  { href: "/analysis", em: "📊", t: "분석" },
  { href: "/routine", em: "📋", t: "루틴" },
  { href: "/ranking", em: "🏆", t: "랭킹" },
  { href: "/gym", em: "🗺️", t: "헬스장" },
];

export function TabBar() {
  const path = usePathname();
  const isOn = (href: string) => path === href || (href === "/today" && path === "/");

  return (
    <>
      {/* 모바일 하단 탭 */}
      <nav
        className="fixed bottom-0 left-1/2 z-40 w-full max-w-md -translate-x-1/2 border-t border-white/10 bg-black/90 backdrop-blur-xl lg:hidden"
        style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
      >
        <div className="flex">
          {TABS.map((tab) => {
            const on = isOn(tab.href);
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`flex min-w-0 flex-1 flex-col items-center gap-0.5 py-2.5 ${on ? "text-volt" : "text-zinc-600"}`}
              >
                <span className={`text-[18px] leading-none ${on ? "" : "opacity-70 grayscale"}`}>{tab.em}</span>
                <span className="text-[9.5px] font-bold">{tab.t}</span>
                <span className={`h-1 w-1 rounded-full ${on ? "bg-volt" : "bg-transparent"}`} />
              </Link>
            );
          })}
        </div>
      </nav>

      {/* 데스크탑 좌측 사이드바 */}
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-56 flex-col border-r border-white/[0.08] bg-[#0a111f] lg:flex">
        <Link href="/today" className="flex items-center px-5 pb-2 pt-6 font-display text-[20px] tracking-tight">
          FitPlan<span className="text-volt">.</span>
        </Link>
        <nav className="mt-4 flex flex-1 flex-col gap-0.5 px-3">
          {TABS.map((tab) => {
            const on = isOn(tab.href);
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-[14px] font-bold transition ${
                  on ? "bg-white/[0.07] text-zinc-50" : "text-zinc-500 hover:bg-white/[0.04] hover:text-zinc-200"
                }`}
              >
                {on && <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-volt" />}
                <span className={`text-[16px] leading-none ${on ? "" : "opacity-70 grayscale"}`}>{tab.em}</span>
                {tab.t}
              </Link>
            );
          })}
        </nav>
        <div className="px-5 pb-5 text-[10.5px] text-white/25">헬스 · 러닝 통합 대시보드</div>
      </aside>
    </>
  );
}
