import type { Metadata, Viewport } from "next";
import "./globals.css";
import "leaflet/dist/leaflet.css";
import { TabBar } from "@/components/nav/TabBar";

export const metadata: Metadata = {
  title: "FitPlan — 헬스·러닝 대시보드",
  description: "회사 헬스장 맞춤 루틴 · 러닝 분석 · 기록 · 랭킹",
};

export const viewport: Viewport = {
  themeColor: "#070c16",
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
      <body className="min-h-full bg-bg text-zinc-50 antialiased">
        <div className="lg:pl-56">
          <div className="mx-auto min-h-screen max-w-md px-4 pb-28 pt-4 lg:max-w-6xl lg:px-10 lg:pb-10">
            {children}
          </div>
        </div>
        <TabBar />
      </body>
    </html>
  );
}
