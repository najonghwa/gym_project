"use client";
// 러닝 탭 — P1-8 성향 진단 온보딩 (진행바 + 슬라이더 + 라이브 게이지 + 마스코트 반응)
import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Mascot } from "@/components/mascot/Mascot";
import { PillButton } from "@/components/ui/PillButton";
import { ProgressBar, FrequencySlider, LiveGauge } from "@/components/onboarding/OnboardKit";

const GOALS = [
  { id: "fun", em: "🌿", t: "기분전환·건강" },
  { id: "loss", em: "🔥", t: "체중 감량" },
  { id: "k10", em: "🏃", t: "10K 도전" },
  { id: "full", em: "🏆", t: "풀코스 마라톤" },
];

// 목표 심박 프리뷰 (220-나이 기준, 이지런 60~70%)
const hrPreview = (age: number) => {
  const max = 220 - age;
  return `이지런 목표 심박 ${Math.round(max * 0.6)}~${Math.round(max * 0.7)}bpm`;
};

export default function RunPage() {
  const [step, setStep] = useState(0);
  const [goal, setGoal] = useState<string | null>(null);
  const [freq, setFreq] = useState(3);
  const [age, setAge] = useState(30);
  const [height, setHeight] = useState(172);
  const [weight, setWeight] = useState(70);

  const TOTAL = 3;
  const mascotLine =
    step === 0
      ? goal
        ? `${GOALS.find((g) => g.id === goal)?.t}! 좋은 선택이에요 👍`
        : "어떤 러닝을 하고 싶어요?"
      : step === 1
      ? freq >= 5
        ? "주 " + freq + "회?! 기대되는데요!"
        : "꾸준함이 페이스를 만들어요"
      : "몸 정보로 심박존을 맞춰드려요";

  return (
    <main className="space-y-4 lg:mx-auto lg:max-w-md lg:pt-16">
      <div className="flex items-center gap-3">
        <ProgressBar pct={((step + 1) / TOTAL) * 100} />
        <span className="lab shrink-0">{step + 1}/{TOTAL}</span>
      </div>

      {/* 마스코트 반응 말풍선 */}
      <div className="flex items-end gap-3">
        <Mascot state="talk" size={72} />
        <AnimatePresence mode="wait">
          <motion.div
            key={mascotLine}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            className="flex-1 rounded-3xl rounded-bl-md border border-white/[0.06] bg-card px-4 py-3"
          >
            <p className="text-[13.5px] font-medium">{mascotLine}</p>
          </motion.div>
        </AnimatePresence>
      </div>

      <section className="rounded-3xl border border-white/[0.06] bg-card p-5">
        {step === 0 && (
          <>
            <h2 className="font-display text-[22px]">러닝 목표는?</h2>
            <div className="mt-4 grid grid-cols-2 gap-2.5">
              {GOALS.map((g) => (
                <button
                  key={g.id}
                  onClick={() => setGoal(g.id)}
                  className={`rounded-2xl border p-4 text-left transition ${
                    goal === g.id ? "border-volt bg-volt/10" : "border-white/10 bg-white/[0.03]"
                  }`}
                >
                  <div className="text-[22px]">{g.em}</div>
                  <b className="mt-1 block text-[13.5px]">{g.t}</b>
                </button>
              ))}
            </div>
          </>
        )}
        {step === 1 && (
          <>
            <h2 className="font-display text-[22px]">일주일에 몇 번 뛸까요?</h2>
            <div className="mt-6">
              <FrequencySlider
                stops={[2, 3, 4, 5, 6]}
                value={freq}
                recommend={3}
                onChange={setFreq}
                preview={() => hrPreview(age)}
              />
            </div>
          </>
        )}
        {step === 2 && (
          <>
            <h2 className="font-display text-[22px]">몸 정보 (라이브 계산)</h2>
            <div className="mt-4 grid grid-cols-3 gap-2">
              {([["나이", age, setAge, "세"], ["키", height, setHeight, "cm"], ["몸무게", weight, setWeight, "kg"]] as const).map(
                ([label, val, set, unit]) => (
                  <label key={label} className="block">
                    <span className="lab">{label}</span>
                    <div className="mt-1 flex items-center gap-1">
                      <input
                        type="number"
                        value={val}
                        onChange={(e) => set(Number(e.target.value) || 0)}
                        className="w-full rounded-xl border border-white/10 bg-white/[0.05] px-2 py-2.5 text-center text-[14px] font-bold outline-none focus:border-volt"
                      />
                      <span className="text-[10px] text-white/40">{unit}</span>
                    </div>
                  </label>
                )
              )}
            </div>
            <div className="mt-5">
              <LiveGauge heightCm={height || 170} weightKg={weight || 65} />
            </div>
            <p className="mt-3 text-center text-[11.5px] text-white/45">{hrPreview(age || 30)}</p>
          </>
        )}
      </section>

      <div className="flex gap-2">
        {step > 0 && (
          <PillButton variant="ghost" className="flex-1" onClick={() => setStep(step - 1)}>이전</PillButton>
        )}
        <PillButton
          className="flex-[2]"
          disabled={step === 0 && !goal}
          onClick={() => (step < TOTAL - 1 ? setStep(step + 1) : alert("플랜 생성은 Supabase 연동 단계에서! (mock)"))}
        >
          {step === TOTAL - 1 ? "러닝 플랜 만들기 ⚡" : "다음"}
        </PillButton>
      </div>
      {/* TODO(supabase): 기존 gym_web 러닝 플랜 생성/기록/랭킹 이관 */}
    </main>
  );
}
