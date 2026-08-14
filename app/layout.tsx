import type { Metadata, Viewport } from "next";
import "./globals.css";
import "leaflet/dist/leaflet.css";
import { TabBar } from "@/components/nav/TabBar";

export const metadata: Metadata = {
  title: "FitPlan — 헬스·러닝 대시보드",
  description: "회사 헬스장 맞춤 루틴 · 러닝 분석 · 기록 · 랭킹",
  appleWebApp: { capable: true, statusBarStyle: "black-translucent", title: "FitPlan" },
};

export const viewport: Viewport = {
  themeColor: "#0b0908",
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko" className="h-full">
      <head>
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"
        />
      </head>
      <body className="min-h-full bg-bg text-stone-50 antialiased">
        <div className="pt-12 lg:pl-56">
          {/* 모바일=폰 폭, 태블릿=넓게, 데스크탑=풀와이드 */}
          <div className="mx-auto min-h-screen max-w-md px-4 pb-28 pt-4 sm:max-w-2xl lg:max-w-none lg:px-10 lg:pb-10 xl:px-14">
            {children}
          </div>
        </div>
        <TabBar />
      </body>
    </html>
  );
}
