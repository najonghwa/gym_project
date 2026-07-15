"use client";
// 하단 7탭 내비 (모바일) / 데스크탑은 상단 가로 탭
import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/today", em: "🏋️", t: "오늘" },
  { href: "/run", em: "🏃", t: "러닝" },
  { href: "/calendar", em: "📅", t: "달력" },
  { href: "/analysis", em: "📊", t: "분석" },
  { href: "/routine", em: "📋", t: "루틴" },
  { href: "/ranking", em: "🏆", t: "랭킹" },
  { href: "/gym", em: "🗺️", t: "헬스장" },
];

export function TabBar() {
  const path = usePathname();
  return (
    <nav className="fixed bottom-0 left-1/2 z-40 flex w-full max-w-md -translate-x-1/2 border-t border-white/10 bg-black/90 backdrop-blur-xl lg:top-0 lg:bottom-auto lg:max-w-none lg:justify-center lg:border-b lg:border-t-0"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      {TABS.map((tab) => {
        const on = path === tab.href || (tab.href === "/today" && path === "/");
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`flex min-w-0 flex-1 flex-col items-center gap-0.5 py-2.5 lg:max-w-28 lg:flex-row lg:justify-center lg:gap-2 ${
              on ? "text-volt" : "text-zinc-600"
            }`}
          >
            <span className={`text-[18px] leading-none ${on ? "" : "opacity-70 grayscale"}`}>
              {tab.em}
            </span>
            <span className="text-[9.5px] font-bold lg:text-[13px]">{tab.t}</span>
            <span className={`h-1 w-1 rounded-full lg:hidden ${on ? "bg-volt" : "bg-transparent"}`} />
          </Link>
        );
      })}
    </nav>
  );
}
