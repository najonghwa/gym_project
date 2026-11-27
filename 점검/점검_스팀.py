# -*- coding: utf-8 -*-
"""v138s · v139 스팀 개도 판정(점검.py가 부른다 — 장면 이름이 '스팀 개도'로 시작, --only "스팀 개도")
판정 범위는 현장 DB 분석(사내 문서) 추가분 5절 3번 표에서 정한 목표 범위만 적는다(원본 배치 값은 적지 않는다).
 ST1 승온 속도(개도 70 %, 내부 40 → 90 ℃): 투입 274 · 351 · 458 kg이 투입이 클수록 느리고, 회귀선 1/속도 = 0.00118 × 투입 + 0.388에서 ± 15 % 안(현장 기록의 흩어짐보다 조금 넓은 범위).
     추가분 표의 '1.1 ~ 1.6 K/분'은 배치 값을 둥글린 범위라 458 kg(회귀선 1.08)은 그 아래 끝에 걸린다 — 범위는 값 칸에 참고로만 적는다(v139)
 ST2 개도 레시피 재현: 시작 70 % → 내부 90 ~ 100 ℃에서 26 % → 초류 22 ~ 26.5 % → 본류 26 ~ 27 % → 끝 0 %
 ST3 운전 중 자켓 − 내부 온도: 초류 · 본류 구간 평균 ±1 ℃
 ST4 본류 개도 26 ~ 27 %일 때 증발 9 ~ 11 kg/h
 ST6 · ST7(v145) 승온 10분 뒤 자켓 85 ~ 90 ℃(액이 자켓 윗끝까지 잠기는 351 · 458 kg, 274 kg은 참고 ST6b) · 승온 중 자켓 최고 100 ~ 107 ℃(현장 DB 범위)
 승온 장면(ST1 · ST6 · ST7)은 초기 액 온도 35 ℃(v145 — 현장 DB 승온 시작 30 ~ 40 ℃의 가운데. 전에는 입력 기본값 25 ℃)
 ST5 본류 개도 26 ~ 27 %일 때 내부 98 ~ 101 ℃ — 증기압식 상수 A(v139부터 기본 12.41, 사용자 결정 2026-11-24)에 달려 있다
 참고 줄: 개도 50 %(319 kg) 승온 속도 — 현장 기록 한 건과 견준다(그 값은 사내 문서에만 둔다)
장면은 화면 조작(입력칸 · 빨리 감기)으로만 상태를 만들고 계산 상태는 읽기만 한다."""
import json

SMP = r"""(()=>{const D=window.__dt,P=D.PR,r=(v,n)=>v==null||!isFinite(v)?null:+(+v).toFixed(n);return JSON.stringify({t:r(P.t/3600,4),st:P.rcp?P.rcp.st:null,T:r(P.Tmean,3),Tj:r(P.TjEff,3),mv:r(D.CUR.jOpen*100,2),V:r(P.vdot||0,3),m:r(P.m,2),stop:!!P.stopped,kg:r(P.m0,1),Cm:D.CUR.Cmetal,heat:+document.getElementById('rcpHeatMV').value})})()"""
FIN = r"""(()=>{const D=window.__dt,P=D.PR,r=(v,n)=>v==null||!isFinite(v)?null:+(+v).toFixed(n);return JSON.stringify({hist:(P.hist||[]).map(h=>[Math.round(h.t),r(h.T,2),r(h.Th,2),r(h.Tje,2),r(h.Rf,3),r(h.Pd,3),r(h.mv,2)]),stages:(P.rcpStages||[]).map(s=>[r(s.t/3600,3),s.st]),stop:!!P.stopped,mv:r(D.CUR.jOpen*100,2),slider:+document.getElementById('jOpen').value,rule:(document.getElementById('rcpSteam')||{}).value||null,A:D.CUR.B.antoine.A})})()"""
def _set(i, v): return ["eval", "(()=>{const e=document.getElementById(%s);if(!e)return 'no';e.value=%s;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));return e.value})()" % (json.dumps(i), json.dumps(str(v)))]
def _jump(h):
    return [["eval", f"window.__dt.startJump('at',{h});1"], ["until", f"(()=>{{const D=window.__dt,P=D.PR;return !!(P&&!D.TURBO&&(P.t>={h}*3600-3||P.stopped))}})()", 900000], ["wait", 300]]
BOOTS = [["wait", 2000], ["until", "!!window.__dt&&!!window.__dt.M&&!!window.__dt.PR", 120000], ["wait", 4000], ["eval", "window.__dt.opSetMode('recipe');document.getElementById('btnCpHf').click();1"], ["wait", 2500]]
def scenarios(scen, tag):
    a = list(BOOTS) + [_set("T0", 35)]   # v145: 초기 액 온도 35 ℃(현장 DB 승온 시작 30 ~ 40 ℃ 가운데) — 승온 10분 뒤 자켓(ST6)을 현장 조건에서 견준다
    for kg, heat in ((274, 70), (351, 70), (458, 70), (319, 50)):
        a += [_set("H", kg), _set("rcpHeatMV", heat), ["wait", 1500], ["eval", "document.getElementById('btnRestart').click();1"], ["wait", 2500]]
        n, dh = (30, 0.1) if heat == 50 else (24, 0.05)   # 개도 50 %는 3 h까지(맞춘 곡선으로 약 0.3 K/분)
        for i in range(1, n + 1): a += _jump(round(dh * i, 2)) + [tag(f"h{kg}_{i:02d}", SMP)]
    a += [_set("rcpHeatMV", 70), _set("T0", 25)]
    b = list(BOOTS) + [["eval", "document.getElementById('btnRestart').click();1"], ["wait", 2500]]
    for i, h in enumerate([0.5, 1, 1.5, 2, 3, 4, 6, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110]): b += _jump(h) + [tag(f"r{i:02d}", SMP)]
    b += [["wait", 1500], tag("rfin", FIN)]
    return [scen("스팀 개도 승온", a), scen("스팀 개도 레시피", b)]

def _cross(smp, Tx):
    for a, b in zip(smp, smp[1:]):
        if a["T"] < Tx <= b["T"]: return a["t"] + (Tx - a["T"]) / (b["T"] - a["T"]) * (b["t"] - a["t"])
    return None
def judge(g, add):
    rates = {}
    for kg in (274, 351, 458, 319):
        smp = [g("스팀 개도 승온", f"h{kg}_{i:02d}") for i in range(1, 31)]; smp = [x for x in smp if x]
        t40, t90 = _cross(smp, 40), _cross(smp, 90)
        rates[kg] = 50 / ((t90 - t40) * 60) if t40 is not None and t90 is not None and t90 > t40 else None
    if all(rates[k] is not None for k in (274, 351, 458)):
        fit = {k: 1 / (0.00118 * k + 0.388) for k in (274, 351, 458)}
        ok = rates[274] > rates[351] > rates[458] and all(abs(rates[k] / fit[k] - 1) <= 0.15 for k in fit)   # v139: 1.1 ~ 1.6은 참고(다섯 배치 값을 둥글린 범위)
        add("ST1", "승온 속도(개도 70 %, 내부 40 → 90 ℃): 투입 274 · 351 · 458 kg이 투입이 클수록 느림, 회귀선 1/속도 = 0.00118 × 투입 + 0.388에서 ± 15 % 안(현장 DB — 금속 열용량 포함)",
            bool(ok), " · ".join(f"{k} kg {rates[k]:.2f} K/분(회귀선 {fit[k]:.2f})" for k in (274, 351, 458)), "줄어듦 · 회귀선 ± 15 %(DB 다섯 배치 약 1.1 ~ 1.6 K/분은 참고)")
    # v145 ST6 · ST7: 승온 중 자켓 온도(현장 DB 범위 — 사내 문서 추가분 5절 '자켓_10분뒤' 85 ~ 90 ℃ · '자켓_승온_최고' 100 ~ 107 ℃). 개도 70 % 세 투입(274 · 351 · 458 kg), 초기 액 35 ℃
    #  ST6은 액이 자켓 윗끝(635 mm)까지 잠기는 351 · 458 kg으로 판정 — 274 kg은 액면(약 530 mm)이 자켓 윗끝보다 낮아 젖은 자켓 면적이 약 15 % 작다(도면 기하). 현장 범위가 저투입 배치에도 맞는지는 배치별 값 확인 대기라 참고 ST6b
    j10, jmx = {}, {}
    for kg in (274, 351, 458):
        smp = [g("스팀 개도 승온", f"h{kg}_{i:02d}") for i in range(1, 31)]; smp = [x for x in smp if x and x.get("Tj") is not None]
        for a9, b9 in zip(smp, smp[1:]):
            if a9["t"] <= 1 / 6 <= b9["t"] and b9["t"] > a9["t"]: j10[kg] = a9["Tj"] + (1 / 6 - a9["t"]) / (b9["t"] - a9["t"]) * (b9["Tj"] - a9["Tj"]); break
        hu = [x["Tj"] for x in smp if x.get("st") == 1]
        if hu: jmx[kg] = max(hu)
    if all(k in j10 for k in (351, 458)):
        add("ST6", "승온 10분 뒤 자켓 온도(개도 70 %, 초기 액 35 ℃): 액이 자켓 윗끝(635 mm)까지 잠기는 투입 351 · 458 kg 모두 85 ~ 90 ℃(현장 DB 자켓 TIH074 범위 — v145 현장 맞춤 전열)", all(85 <= j10[k] <= 90 for k in (351, 458)),
            " · ".join(f"{k} kg {j10[k]:.1f} ℃" for k in (351, 458)), "85 ~ 90 ℃")
    if 274 in j10:
        add("ST6b", "참고: 투입 274 kg 승온 10분 뒤 자켓 — 액면이 자켓 윗끝보다 낮아 젖은 자켓 면적이 약 15 % 작아 더 뜨겁다(도면 기하). 현장 범위 85 ~ 90 ℃가 액면이 자켓 윗끝보다 낮은 저투입 배치에도 맞는지는 배치별 값 확인 대기(사용자)", None,
            f"{j10[274]:.1f} ℃", "현장 배치별 값(확인 대기)")
    if len(jmx) == 3:
        add("ST7", "승온 중 자켓 최고 온도(개도 70 %, 26 %로 바꾸기 전): 투입 274 · 351 · 458 kg 모두 100 ~ 107 ℃(현장 DB 자켓 TIH074 범위 — 전 계산 약 125 ℃, v145 현장 맞춤 전열)", all(100 <= jmx[k] <= 107 for k in jmx),
            " · ".join(f"{k} kg {jmx[k]:.1f} ℃" for k in (274, 351, 458)), "100 ~ 107 ℃")
    if rates.get(319) is not None:
        add("ST1b", "참고: 개도 50 %(319 kg) 승온 속도 — 현장 기록 한 건의 값(사내 문서)과 다름(이 맞춤 곡선의 한계, 사용자 확인)", None, f"{rates[319]:.2f} K/분", "사내 문서 값(참고)")
    r = [g("스팀 개도 레시피", f"r{i:02d}") for i in range(19)]; r = [x for x in r if x]; f = g("스팀 개도 레시피", "rfin")
    if r and f:
        st = {s: t for t, s in f["stages"]}; H = f["hist"]
        mv_at = lambda s: sorted({x["mv"] for x in r if x["st"] == s and not x["stop"]})
        heat = [x for x in r if x["st"] == 1]; cut = None
        for a, b in zip(r, r[1:]):
            if a["st"] == 1 and b["st"] == 2: cut = b; break
        # ② 시작 때 내부 온도: 기록에서 ② 시작 시각에 가장 가까운 점
        Tcut = None
        if 2 in st:
            near = min(H, key=lambda h: abs(h[0] - st[2] * 3600)) if H else None; Tcut = near[1] if near else None
        def stage_mv(s):
            t0 = st.get(s); t1 = st.get(s + 1)
            v = [h[6] for h in H if t0 is not None and h[0] >= t0 * 3600 + 60 and (t1 is None or h[0] < t1 * 3600 - 60)]
            return (min(v), max(v)) if v else (None, None)
        m1, m2, m3, m4 = stage_mv(1), stage_mv(2), stage_mv(3), stage_mv(4)
        ok = (m1[0] is not None and abs(m1[0] - 70) < 0.6 and abs(m1[1] - 70) < 0.6 and Tcut is not None and 90 <= Tcut <= 100 and m2[0] is not None and abs(m2[0] - 26) < 0.6 and abs(m2[1] - 26) < 0.6
              and m3[0] is not None and 22 - 0.01 <= m3[0] and m3[1] <= 26.5 + 0.01 and m4[0] is not None and 26 - 0.01 <= m4[0] and m4[1] <= 27 + 0.01 and f["stop"] and abs(f["mv"]) < 0.01 and f["slider"] == 0)
        add("ST2", "개도 레시피 재현(CpHf 조건 · 레시피 개도): 시작 70 % → 내부 90 ~ 100 ℃에서 26 % → 초류 22 ~ 26.5 % → 본류 26 ~ 27 % → 끝 0 %(개도 입력칸 · 계산 개도 모두)",
            bool(ok), f"① {m1} % → ② 시작 내부 {Tcut} ℃ · {m2} % → ③ {m3} % → ④ {m4} % → 끝 {f['mv']} %(입력칸 {f['slider']}) · 단계 시작 {[(s, t) for s, t in sorted(st.items())]} · 규칙 {f['rule']}", "70 → (90 ~ 100 ℃) 26 → 22 ~ 26.5 → 26 ~ 27 → 0")
        end = next((x["t"] for x in r if x["stop"]), None)
        def avg(s, fn):
            t0 = st.get(s); t1 = st.get(s + 1) if s == 3 else end
            v = [fn(h) for h in H if t0 is not None and h[0] >= (t0 + 0.5) * 3600 and (t1 is None or h[0] < t1 * 3600)]; v = [x for x in v if x is not None]
            return sum(v) / len(v) if v else None
        dT3, dT4 = avg(3, lambda h: h[3] - h[1] if h[3] is not None else None), avg(4, lambda h: h[3] - h[1] if h[3] is not None else None)
        if dT3 is not None and dT4 is not None:
            add("ST3", "운전 중 자켓 − 내부 온도: 초류 · 본류 구간 평균(구간 처음 30분 뺌)이 ±1 ℃ 안(현장 DB 운전 중 자켓 TIH074 − 내부 TICH071) — v145 자켓 전열 현장 맞춤(상관식 U × 액 온도 배율, 사용자 11-27 '현장 DB가 실제현상')", abs(dT3) <= 1 and abs(dT4) <= 1, f"초류 {dT3:+.2f} · 본류 {dT4:+.2f} ℃", "±1 ℃")
        V4, T4, mv4 = avg(4, lambda h: (h[4] or 0) + (h[5] or 0)), avg(4, lambda h: h[1]), avg(4, lambda h: h[6])
        if V4 is not None:
            add("ST4", "본류 개도 26 ~ 27 %일 때 증발(환류 + 유출) 9 ~ 11 kg/h(구간 평균)", bool(mv4 is not None and 26 - 0.01 <= mv4 <= 27 + 0.01 and 9 <= V4 <= 11), f"개도 {mv4:.1f} % · 증발 {V4:.2f} kg/h", "9 ~ 11")
            add("ST5", f"본류 개도 26 ~ 27 %일 때 내부 98 ~ 101 ℃(구간 평균) — 증기압식 상수 A {f['A']}(v139 기본 12.41 = DB 맞춤)", bool(mv4 is not None and 26 - 0.01 <= mv4 <= 27 + 0.01 and 98 <= T4 <= 101), f"개도 {mv4:.1f} % · 내부 {T4:.1f} ℃", "98 ~ 101")
