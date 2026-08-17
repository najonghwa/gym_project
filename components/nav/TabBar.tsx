"use client";
// 내비 — 상단 헤더바(로고+유저칩) / 모바일: 하단 7탭 / 데스크탑: 좌측 사이드바(볼트 필 활성)
import Link from "next/link";
import { usePathname } from "next/navigation";
import { computeStats, useUser } from "@/lib/useUser";
import { Icon, IconName } from "@/components/ui/Icon";

const TABS: { href: string; ic: IconName; t: string }[] = [
  { href: "/today", ic: "dumbbell", t: "헬스" },
  { href: "/run", ic: "run", t: "러닝" },
  { href: "/analysis", ic: "chart", t: "분석" },
  { href: "/routine", ic: "clipboard", t: "루틴" },
  { href: "/ranking", ic: "trophy", t: "랭킹" },
  { href: "/gym", ic: "map", t: "헬스장" },
];

export function TabBar() {
  const path = usePathname();
  const { user } = useUser();
  const level = user ? computeStats(user).level : null;
  const isOn = (href: string) => path === href || (href === "/today" && path === "/");

  return (
    <>
      {/* 상단 헤더바 */}
      <header className="fixed inset-x-0 top-0 z-40 flex h-12 items-center justify-between border-b border-white/[0.06] bg-[#0b0908]/90 px-4 backdrop-blur-xl lg:px-5">
        <Link href="/today" className="font-display text-[19px] tracking-tight">
          FitPlan<span className="text-volt">.</span>
        </Link>
        {user && (
          <span className="flex items-center gap-2">
            <span className="text-[12.5px] font-bold text-white/70">{String(user.id)}</span>
            <span className="rounded-full bg-volt px-2.5 py-1 text-[11px] font-extrabold text-black">Lv{level}</span>
          </span>
        )}
      </header>

      {/* 모바일 하단 탭 — 활성 탭은 볼트 필 캡슐 */}
      <nav
        className="fixed bottom-0 left-1/2 z-40 w-full max-w-md -translate-x-1/2 border-t border-white/10 bg-[#0b0908]/90 backdrop-blur-xl sm:max-w-2xl lg:hidden"
        style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
      >
        <div className="flex px-1.5 py-1.5">
          {TABS.map((tab) => {
            const on = isOn(tab.href);
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`flex min-w-0 flex-1 flex-col items-center gap-1 rounded-xl py-2 ${
                  on ? "bg-volt/10 text-volt" : "text-stone-500"
                }`}
              >
                <Icon name={tab.ic} size={21} strokeWidth={on ? 2 : 1.7} />
                <span className={`text-[10px] ${on ? "font-bold" : "font-semibold"}`}>{tab.t}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* 데스크탑 좌측 사이드바 — 활성 탭 = 볼트 필 */}
      <aside className="fixed bottom-0 left-0 top-12 z-40 hidden w-56 flex-col border-r border-white/[0.06] bg-[#100d0a] lg:flex">
        <nav className="mt-5 flex flex-1 flex-col gap-1.5 px-3.5">
          {TABS.map((tab) => {
            const on = isOn(tab.href);
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-[14px] transition ${
                  on
                    ? "bg-volt font-extrabold text-black"
                    : "font-semibold text-stone-400 hover:bg-white/[0.04] hover:text-stone-100"
                }`}
              >
                <Icon name={tab.ic} size={19} strokeWidth={on ? 2 : 1.7} />
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
