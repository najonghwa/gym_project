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
    <nav
      className="fixed bottom-0 left-1/2 z-40 w-full max-w-md -translate-x-1/2 border-t border-white/10 bg-black/90 backdrop-blur-xl lg:top-0 lg:bottom-auto lg:max-w-none lg:border-b lg:border-t-0"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      <div className="flex lg:mx-auto lg:h-16 lg:max-w-5xl lg:items-stretch lg:gap-1 lg:px-6">
        {/* 데스크탑 로고 */}
        <Link href="/today" className="hidden items-center pr-8 font-display text-[20px] tracking-tight lg:flex">
          PULSE<span className="text-volt">.</span>
        </Link>
        {TABS.map((tab) => {
          const on = path === tab.href || (tab.href === "/today" && path === "/");
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={`flex min-w-0 flex-1 flex-col items-center gap-0.5 py-2.5 lg:relative lg:max-w-none lg:flex-none lg:flex-row lg:gap-2 lg:px-4 lg:py-0 ${
                on ? "text-volt lg:text-zinc-50" : "text-zinc-600 lg:text-zinc-500 lg:hover:text-zinc-200"
              }`}
            >
              <span className={`text-[18px] leading-none lg:text-[16px] ${on ? "" : "opacity-70 grayscale"}`}>
                {tab.em}
              </span>
              <span className="text-[9.5px] font-bold lg:text-[14px]">{tab.t}</span>
              <span className={`h-1 w-1 rounded-full lg:hidden ${on ? "bg-volt" : "bg-transparent"}`} />
              {/* 데스크탑 활성 언더라인 */}
              <span className={`hidden lg:block lg:absolute lg:inset-x-3 lg:bottom-0 lg:h-[3px] lg:rounded-t-full ${on ? "lg:bg-volt" : "lg:bg-transparent"}`} />
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
