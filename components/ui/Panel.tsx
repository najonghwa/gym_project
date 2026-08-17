// 표면 컴포넌트 — 카드 껍데기를 한 곳으로 모은다.
//
// 예전엔 모든 섹션을 똑같은 카드에 담아서 "오늘 뭘 할지"와 "작년 통계"가
// 같은 무게로 읽혔다. 위계를 3단으로 고정한다:
//   plain  … 배경에 직접 (주요 액션·히어로). 위쪽 실선 하나로만 구분
//   card   … 데이터 카드 (기본)
//   accent … 화면당 하나만. 지금 눌러야 하는 것
import type { ReactNode } from "react";

const TONE = {
  plain: "border-t border-white/[0.07] pt-4",
  card: "rounded-xl border border-white/[0.07] bg-card",
  accent: "rounded-xl border border-volt/25 bg-volt/[0.04]",
} as const;

const PAD = { none: "", sm: "p-3", md: "p-4" } as const;

export function Panel({
  tone = "card", pad = "md", className = "", children,
}: {
  tone?: keyof typeof TONE;
  pad?: keyof typeof PAD;
  className?: string;
  children: ReactNode;
}) {
  const padding = tone === "plain" ? "" : PAD[pad];
  return <div className={`${TONE[tone]} ${padding} ${className}`}>{children}</div>;
}

// 섹션 제목 — 볼트 틱을 14번 반복하면 강조가 아니라 배경 소음이 되므로 뺐다.
export function SectionTitle({
  children, sub, right,
}: { children: ReactNode; sub?: ReactNode; right?: ReactNode }) {
  return (
    <div className="mb-2.5 flex items-end justify-between gap-3">
      <div className="min-w-0">
        <h2 className="text-[14px] font-extrabold tracking-tight text-white/90">{children}</h2>
        {sub && <p className="mt-0.5 text-[11.5px] text-white/40">{sub}</p>}
      </div>
      {right && <div className="shrink-0">{right}</div>}
    </div>
  );
}

// 누적 지표 — 큰 숫자 + 작은 라벨 세트를 반복하는 대신 라벨-값 목록으로 한 번만
export function DataList({
  items,
}: { items: { label: string; value: ReactNode }[] }) {
  return (
    <dl className="divide-y divide-white/[0.06]">
      {items.map((it) => (
        <div key={it.label} className="flex items-baseline justify-between py-2.5 first:pt-0 last:pb-0">
          <dt className="text-[12.5px] text-white/50">{it.label}</dt>
          <dd className="text-[14px] font-extrabold tabular-nums">{it.value}</dd>
        </div>
      ))}
    </dl>
  );
}
