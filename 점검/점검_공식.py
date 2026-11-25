# -*- coding: utf-8 -*-
"""공식 검산과 이상 상황 반응 시험(v117~) — 점검.py가 불러 쓴다.

1) 공식 검산: 시뮬레이터 안의 식 함수(window.__dt.fn)를 시험점에서 불러, 여기서 따로 계산한 값(증기표·닫힌 식)과 견준다.
   만든 쪽 코드와 따로 떨어진 계산이어야 하므로, 여기 식은 시뮬레이터 코드를 베끼지 않고 교과서 식·표에서 다시 적었다.
2) 이상 상황: 레시피 초류 구간(10 h)에서 원인 하나를 걸고 30분 뒤 상태가 물리적으로 맞는 쪽으로 움직였는지 숫자로 본다.
   기준은 '방향과 대략의 크기'다(시뮬레이터 값 그대로를 기준으로 삼지 않는다).
"""
import json, math

R_GAS = 8.314462

# ---------- 페이지 안에서 재는 식 ----------
JS_FN = r"""(()=>{const D=window.__dt,F=D.fn,P=D.PR,p=D.CUR,subs=[p.A,p.B,p.Cs];
const Mv=P.y[0]*p.A.MW+P.y[1]*p.B.MW,Tv=P.Tbub+273.15;
const lt=[1,3,10,30].map(W=>{const o=F.lineTop(p,W/3600,Mv,Tv);return {W,Ptop:o.Ptop,Pch:o.Pch,Pexit:o.Pexit,f:o.f,Re:o.Re};});
return JSON.stringify({steamT:[50,100,120,150,180,200],steam:[50,100,120,150,180,200].map(T=>F.steamLam(T)),pvT:[60,84,100,120],pv:[60,84,100,120].map(T=>F.bubbleP([0,1,0],subs,T)),tbP:[0.05,0.1,0.5,1,5],tb:[0.05,0.1,0.5,1,5].map(x=>F.bubbleT([0,1,0],subs,x)),
headEll:F.headA({head:'ell',R:0.35}),headFlat:F.headA({head:'flat',R:0.35}),frIn:[[500,0],[2000,0],[1e5,6e-4],[1e6,1e-5]],fr:[[500,0],[2000,0],[1e5,6e-4],[1e6,1e-5]].map(([Re,rr])=>F.fChurchill(Re,rr)),lt,Mv,Tv,aSon:P.aSon,gam:P.gamV,Pcond:P.Pcond,Dpipe:p.Dpipe,Lpipe:p.Lpipe,
antB:p.B.antoine,hvapB:p.B.hvap,MWB:p.B.MW,
st:{Pstill:P.Pstill,Ptop:P.Ptop,Tmean:P.Tmean,Tbub:P.Tbub,TheadEq:P.TheadEq,xD:P.xD,vdot:P.vdot,pvLiq:F.bubbleP(P.x,subs,P.Tmean),tTop:F.bubbleT([P.xD,1-P.xD,0],subs,P.Ptop),lam:P.lam,Q:P.Q,Qloss:P.Qloss,Qcool:P.Qcool,Lcol:P.Lcol,Lwarm:P.Lwarm,m:P.m,cp:P.mix.cp,vFrTop:P.vFrTop,vpassRaw:P.vpassRaw,
 ltNow:F.lineTop(p,(P.vpassRaw||0)/3600,Mv,Tv).Ptop}})})()"""

JS_UI117 = r"""(async()=>{const D=window.__dt,zz=(ms)=>new Promise(r=>setTimeout(r,ms));
const tags=[...document.querySelectorAll('.dcs-tag')].filter(e=>!e.hidden).map(e=>e.dataset.n);
const kb=(k)=>document.querySelectorAll('#drawer .row[data-kind="'+k+'"]').length;
const kinds={est:kb('est'),hard:kb('hard'),meas:kb('meas'),op:kb('op'),dwg:kb('dwg')};
const kc=document.querySelectorAll('#kconst li').length,kch=document.querySelectorAll('#kconst li[data-kind=hard]').length,hasF=!!document.querySelector('.kfilter button[data-kf=hard]');
if(!document.getElementById('valves').classList.contains('showadv'))document.getElementById('vAdv').click();
const bt=document.getElementById('abBtn');bt.click();await zz(300);
const g=document.getElementById('abPanel'),st=g.parentElement.getBoundingClientRect(),r=g.getBoundingClientRect();
const n=g.querySelectorAll('.abp-list button').length,inside=r.left>=st.left-1&&r.right<=st.right+1&&r.top>=st.top-1&&r.bottom<=st.bottom+1&&r.width>50;
const t0=document.getElementById('Tcw').value;g.querySelector('button[data-ab=c1hot]').click();await zz(600);
const t1=document.getElementById('Tcw').value,cur1=D.CUR.Tcw,lab1=bt.textContent;
g.querySelector('button[data-ab=c1cold]').click();await zz(600);const t2=document.getElementById('Tcw').value,on2=Object.keys(D.AB.on);
g.querySelector('button[data-ab=all]').click();await zz(600);const t3=document.getElementById('Tcw').value,cur3=D.CUR.Tcw,lab3=bt.textContent;
const ops=(D.PR.ops||[]).slice(-6).map(o=>o.text);g.querySelector('button[data-ab=x]').click();
return JSON.stringify({tags,kinds,kc,kch,hasF,n,inside,t0,t1,cur1,lab1,t2,on2,t3,cur3,lab3,ops,hid:g.hidden})})()"""

SNAP = r"""(()=>{const D=window.__dt,P=D.PR,p=D.CUR,f=P.fr||{};const r=(x,n=3)=>x==null||!isFinite(x)?null:+(+x).toFixed(n);
return JSON.stringify({t_h:r(P.t/3600,2),st:P.rcp?P.rcp.st:null,MV:r((p.jOpen||0)*100,1),Tpot:r(P.Tmean,2),Tbub:r(P.Tbub,2),Ttop:r(P.Thead,2),Tbot:r(P.Tbot!=null?P.Tbot:P.T1out,1),Tsat:r(P.Tsat,2),
Pstill:r(P.Pstill,4),Ptop:r(P.Ptop,4),Pcond:r(P.Pcond,4),Ppump:r(P.Ppump,4),V:r(P.vdot,3),R:r(P.Rkg,3),D:r(P.Dkg,3),back:r(P.backKg,3),n2:r((f.n2||0)*P.vdot,4),lost:r((f.lost||0)*P.vdot,5),c1:r(P.c1,4),c2:r(P.c2,4),s1:r(P.slip1,6),s2:r(P.slip2,6),
Tw1:r(P.Tw1out,2),Tw2:r(P.Tw2out,2),cap1:r(P.cap1,1),Qc:r(P.Qc,1),Pset:p.P,tIns:p.tIns,Q:r(P.Q,0),Qloss:r(P.Qloss,0),Qcool:r(P.Qcool,1),flood:r(P.flood,3),subR:r(P.subR,3),xD:r(P.xD*100,4),m:r(P.m,2),lam:r(P.lam,0),UA1:p.UA1,mcw:p.mcw,Tcw:p.Tcw,Tcw2:p.Tcw2,Tamb:p.Tamb,leak:p.leak,
boil:P.Tmean>=P.Tbub-0.3,on:Object.keys(D.AB.on),stopped:!!P.stopped})})()"""

# 이상 상황: (열쇠, 이름, 건 뒤 본 시각[h])
AB_CASES = [("c1hot", "1차 N-Brine 온도 상승", 0.5), ("c1cold", "1차 N-Brine 과냉", 0.5), ("c2hot", "2차 L-Brine 온도 상승", 0.5), ("cwlow", "냉매 유량 부족", 0.5),
            ("steam", "스팀 개도 과다", 0.5), ("rhigh", "환류 과다", 0.5), ("rlow", "환류 부족", 0.5), ("leak", "진공 리크 증가", 0.5), ("pump", "진공 배기 능력 저하", 0.5), ("pstop", "진공 펌프 정지", 0.5),
            ("cold", "외기 한파", 0.5), ("bare", "단열 손상", 0.5), ("preg", "스팀 레귤레이터 고장", 0.5)]   # v135 계산 쪽: 이상 상황 13번째(밸브 앞 스팀 압력 1.96 → 7 bar(g), 가정)

def scenarios(scen, tag, BOOT, jump, SHOTS):
    rec = BOOT + [["eval", "window.__dt.opSetMode('recipe');1"], ["wait", 1500]]
    S = [scen("공식 검산", rec + jump(10) + [["wait", 1500], tag("fn", JS_FN), tag("ui117", JS_UI117), ["shot", str(SHOTS / "상황_고르기.png")]])]
    for (k, name, dt) in AB_CASES:   # 상황마다 새 배치(앞 상황의 여파가 섞이지 않게)
        a = rec + jump(10) + [["wait", 1200], tag("ab_" + k + "_0", SNAP), ["eval", f"window.__dt.ab('{k}');1"], ["wait", 800]] + jump(10 + dt) + [["wait", 1200], tag("ab_" + k + "_1", SNAP),
             ["eval", f"window.__dt.ab('{k}');1"], ["wait", 800]] + jump(10 + 2 * dt) + [["wait", 1200], tag("ab_" + k + "_2", SNAP)]
        S.append(scen("이상 상황 " + name, a))
    return S

# ---------- 따로 계산 ----------
STEAM = {50: 2382.0, 100: 2256.4, 120: 2202.1, 150: 2113.7, 180: 2014.2, 200: 1939.7}   # 포화 증기 증발열 kJ/kg (IAPWS-IF97 증기표)
def colebrook(Re, rr):
    f = 0.02
    for _ in range(60): f = 1 / (-2 * math.log10(rr / 3.7 + 2.51 / (Re * math.sqrt(f)))) ** 2
    return f

def judge(g, add):
    d = g("공식 검산", "fn")
    if d:
        e = max(abs(v / 1000 / STEAM[T] - 1) for T, v in zip(d["steamT"], d["steam"]))
        add("I1", "스팀 증발열 = 증기표(50~200 ℃ 여섯 점)", e < 0.005, f"최대 차 {e * 100:.2f} %", "< 0.5 %")
        a = d["antB"]; A_, B_, C_ = a["A"], a["B"], a.get("C", 273.15)
        e = max(abs(v / 10 ** (A_ - B_ / (T + C_)) - 1) for T, v in zip(d["pvT"], d["pv"])); p84 = d["pv"][1]
        # v141: 상수 A는 현장 기록 맞춤값 12.41(사용자 결정 2026-11-24, 입력칸 pvA). 문헌 한 점(84 ℃ 0.1 torr)은 옛 A 11.87의 기준이라 참고 줄로 남긴다
        add("I2", "CpHf 증기압 = 앙투안 식 직접 계산 · 상수 A = 현장 기록 맞춤값 12.41(B 4597)", e < 0.005 and abs(A_ - 12.41) < 1e-6 and abs(B_ - 4597) < 1e-6, f"최대 차 {e * 100:.3f} % · A {A_} · B {B_}", "< 0.5 % · A 12.41 · B 4597")
        t01 = B_ / (A_ - math.log10(0.1)) - C_
        add("I2", "참고: 제조사 SDS 한 점(84 ℃ 0.1 torr)과의 차 — A 12.41은 내부 온도 · 증발을 현장 기록에 맞춘 값이라 SDS 점과 어긋난다(사용자 확인 대기)", None, f"84 ℃ {p84:.4f} torr · 0.1 torr가 되는 온도 {t01:.1f} ℃(SDS 84 ℃와 {84 - t01:.1f} ℃ 차)", "-")
        e = max(abs(v - (B_ / (A_ - math.log10(P)) - C_)) for P, v in zip(d["tbP"], d["tb"]))
        add("I3", "끓는점 = 증기압 식의 역(0.05~5 torr)", e < 0.05, f"최대 차 {e:.3f} ℃", "< 0.05 ℃")
        ecc = math.sqrt(0.75); ex = math.pi * 0.35 ** 2 * (1 + 0.25 / ecc * math.atanh(ecc))
        add("I4", "2:1 타원 경판 겉넓이 = 편구면 반쪽 식, 평바닥 = πR²", abs(d["headEll"] / ex - 1) < 0.003 and abs(d["headFlat"] / (math.pi * 0.35 ** 2) - 1) < 1e-6, f"{d['headEll']:.4f} / {ex:.4f} m²", "차 < 0.3 %")
        ref = [64 / 500, 64 / 2000, colebrook(1e5, 6e-4), colebrook(1e6, 1e-5)]; errs = [abs(v / r - 1) for v, r in zip(d["fr"], ref)]
        add("I5", "관 마찰계수: 층류 64/Re, 난류 Colebrook", errs[0] < 0.01 and errs[1] < 0.01 and errs[2] < 0.03 and errs[3] < 0.03, " · ".join(f"{v:.4f}/{r:.4f}" for v, r in zip(d["fr"], ref)), "층류 < 1 % · 난류 < 3 %")
        Mk = d["Mv"] / 1000; RT = R_GAS * d["Tv"]; aI = math.sqrt(d["gam"] * RT / Mk); Ap = math.pi * d["Dpipe"] ** 2 / 4
        e1 = abs(d["aSon"] / aI - 1); e2 = max(abs(o["Pch"] / (o["W"] / 3600 / (0.95 * d["aSon"] * Ap) * RT / Mk / 133.322) - 1) for o in d["lt"])
        add("I6", "증기 음속 √(γRT/M), 초킹 압력 G·RT/(M·0.95a)", e1 < 0.005 and e2 < 0.005 and 1 < d["gam"] < 1.1, f"음속 {d['aSon']:.1f} m/s(차 {e1 * 100:.2f} %) · γ {d['gam']:.4f} · 초킹 압력 차 {e2 * 100:.2f} %", "< 0.5 % · 1 < γ < 1.1")
        res = []
        for o in d["lt"]:
            G = o["W"] / 3600 / Ap; Kp = RT * G * G / Mk / 133.322 ** 2
            rhs = o["Pexit"] ** 2 + Kp * (o["f"] * d["Lpipe"] / d["Dpipe"] + 2 * math.log(max(1, o["Ptop"] / o["Pexit"]))); res.append(abs(o["Ptop"] ** 2 / rhs - 1))
        add("I7", "증기관 압력: 등온 압축성 식의 잔차(1·3·10·30 kg/h)", max(res) < 0.005 and all(o["Pexit"] >= d["Pcond"] * 0.999 for o in d["lt"]), f"최대 잔차 {max(res) * 100:.3f} % · 꼭대기 압력 {[round(o['Ptop'], 3) for o in d['lt']]} torr", "< 0.5 %")
        if abs(C_ - 273.15) < 1e-6:
            lamI = R_GAS * B_ * math.log(10)
            hv = d["hvapB"] * d["MWB"]   # 물질 자료의 증발열은 J/g
            add("I8", "증발열 = 증기압 기울기(Clausius–Clapeyron) R·B·ln10", abs(hv / lamI - 1) < 0.02, f"{hv / 1000:.1f} / {lamI / 1000:.1f} kJ/mol", "차 < 2 %")
        s = d["st"]
        add("I9", "끓는 액의 증기압 = 정제기 압력(평형 풀이)", abs(s["pvLiq"] / s["Pstill"] - 1) < 0.01, f"{s['pvLiq']:.4f} / {s['Pstill']:.4f} torr", "차 < 1 %")
        add("I10", "탑 평형 온도 = 꼭대기 압력에서 꼭대기 조성의 끓는점", abs(s["TheadEq"] - s["tTop"]) < 0.5, f"{s['TheadEq']:.2f} / {s['tTop']:.2f} ℃", "차 < 0.5 ℃")
        add("I11", "꼭대기 압력 = 증기관 식에 꼭대기 증기량을 넣은 값", abs(s["Ptop"] / s["ltNow"] - 1) < 0.02, f"{s['Ptop']:.4f} / {s['ltNow']:.4f} torr (꼭대기 증기 {s['vpassRaw']:.2f} kg/h)", "차 < 2 %")
        qc = s["Lcol"] * s["lam"] / 3600
        add("I12", "컬럼 벽 손실 응축량 × 증발열 = 벽 손실", abs(qc / s["Qcool"] - 1) < 0.1 if s["Qcool"] else False, f"{qc:.0f} / {s['Qcool']:.0f} W", "차 < 10 %")
        bal = s["Q"] - s["Qloss"] - s["lam"] * s["vdot"] / 3600
        add("I13", "스팀 입열 − 열손실 − 증발 = 액을 데우는 몫(작아야)", abs(bal) < 0.25 * s["Q"], f"{bal:.0f} W (입열 {s['Q']:.0f} W의 {bal / s['Q'] * 100:.0f} %)", "입열의 25 % 안")
    u = g("공식 검산", "ui117")
    if u:
        need = ["PICH071 탱크 압력", "PIH093 펌프 쪽 압력", "TICH364 N-Brine 입구", "TIH353 L-Brine 입구"]; miss = [n for n in need if n not in u["tags"]]
        add("J1", "값 상자: 정제기 쪽(PICH071)·펌프 쪽 압력, N-Brine(TICH364)·L-Brine(TIH353) 입구 온도", not miss, "모두 있음" if not miss else "없음: " + ", ".join(miss), "네 개 모두")
        add("J2", "입력칸 구분에 '추정'(데이터로도 정하기 힘든 값)과 거르기 버튼", u["kinds"]["hard"] >= 5 and u["kinds"]["est"] >= 10 and u["hasF"], f"추정 {u['kinds']['hard']}칸 · 가정 {u['kinds']['est']}칸 · 측정 {u['kinds']['meas']}칸 · 버튼 {'있음' if u['hasF'] else '없음'}", "추정 ≥ 5 · 가정 ≥ 10 · 버튼")
        add("J3", "식 안에 든 물성·상수 목록(입력칸 없는 값)", u["kc"] >= 8 and u["kch"] >= 5, f"{u['kc']}줄(추정 {u['kch']})", "≥ 8줄 · 추정 ≥ 5")
        add("J4", "이상 상황 목록", u["n"] == len(AB_CASES), f"{u['n']}가지", f"{len(AB_CASES)}가지")
        add("J5", "이상 상황 창이 3D 화면 안", bool(u["inside"]), "안" if u["inside"] else "밖으로 나감", "안")
        add("J6", "상황을 걸면 입력칸·계산값이 같이 바뀜(N-Brine 95 ℃)", u["t1"] == "95" and abs(u["cur1"] - 95) < 1e-6 and "1개" in u["lab1"], f"입력 {u['t1']} · 계산 {u['cur1']} · 버튼 '{u['lab1']}'", "95 · 95 · 1개 적용 중")
        add("J7", "같은 값을 바꾸는 상황은 하나만", u["t2"] == "5" and u["on2"] == ["c1cold"], f"입력 {u['t2']} · 켜진 상황 {u['on2']}", "5 · 과냉만")
        add("J8", "모두 되돌리기 → 처음 값", u["t3"] == u["t0"] and abs(u["cur3"] - float(u["t0"])) < 1e-6 and u["lab3"] == "상황 고르기", f"입력 {u['t3']}(처음 {u['t0']}) · 계산 {u['cur3']} · 버튼 '{u['lab3']}'", "처음 값 · '상황 고르기'")
        add("J9", "운전 기록에 건 것·되돌린 것이 남음", sum("이상 상황" in t for t in u["ops"]) >= 3, " / ".join(u["ops"][-3:]), "3줄 이상")
    judge_ab(g, add)

def judge_ab(g, add):
    for (k, name, dt) in AB_CASES:
        a, b, c = (g("이상 상황 " + name, f"ab_{k}_{i}") for i in (0, 1, 2))
        if not (a and b and c): continue
        ok, val, crit = CRIT[k](a, b, c)
        add("K-" + k, f"이상 상황: {name}(30분 뒤)", bool(ok), val, crit)
        back = c["on"] == [] and all(abs((c[x] if c[x] is not None else -999) - (a[x] if a[x] is not None else -999)) < 1e-9 for x in ("Tcw", "Tcw2", "mcw", "Tamb", "leak", "tIns"))
        add("K-" + k + "-u", f"되돌리기: {name}", back, "입력이 처음 값으로" if back else f"남음 {c['on']}", "입력 처음 값")

f2 = lambda x: "–" if x is None else f"{x:.2f}"
def _c1hot(a, b, c):
    top = b["V"] - b["back"]
    return (b["c1"] < 0.05 and b["R"] < 0.3 * a["R"] and b["n2"] > 0.7 * top and abs(b["Pcond"] / a["Pcond"] - 1) < 0.2 and c["c1"] > 0.95 and c["R"] > 0.8 * a["R"],
            f"1차 응축 비율 {f2(a['c1'])} → {f2(b['c1'])} · 환류 {f2(a['R'])} → {f2(b['R'])} kg/h · 2차 응축 {f2(b['n2'])} kg/h(꼭대기 증기 {f2(top)}) · 펌프 쪽 압력 {a['Pcond']:.3f} → {b['Pcond']:.3f}",
            "1차 응축 < 5 % · 환류 < 30 % · 2차가 꼭대기 증기의 70 % 넘게 · 압력 ±20 % · 되돌리면 복귀")
def _c1cold(a, b, c):
    return (b["Tbot"] < 15 and b["subR"] > 1.5 * a["subR"] and b["c1"] > 0.99 and abs(b["V"] / a["V"] - 1) < 0.2,
            f"응축액 출구 {a['Tbot']} → {b['Tbot']} ℃ · 과냉 몫 cp·ΔT/λ {a['subR']} → {b['subR']} · 증발 {f2(a['V'])} → {f2(b['V'])} kg/h", "출구 < 15 ℃ · 과냉 몫 1.5배 넘게 · 증발 ±20 %")
def _c2hot(a, b, c):
    return (b["c1"] > 0.99 and (b["lost"] or 0) < 0.01 and abs(b["V"] / a["V"] - 1) < 0.15 and abs(b["Pcond"] / a["Pcond"] - 1) < 0.2,
            f"1차 응축 {f2(b['c1'])} · 진공펌프로 {b['lost']:.5f} kg/h · 증발 {f2(a['V'])} → {f2(b['V'])} · 압력 {a['Pcond']:.3f} → {b['Pcond']:.3f}", "1차가 다 응축하는 동안은 영향 거의 없음(펌프로 < 0.01 kg/h, 증발·압력 ±15~20 %)")
def _cwlow(a, b, c):
    Cw = b["mcw"] / 3600 * 4186; cap = (1 - math.exp(-b["UA1"] / Cw)) * Cw * max(0, b["Tsat"] - b["Tcw"]); load = b["Qc"] / b["c1"] if b["c1"] else None
    c1i = min(1, cap / load) if load else None
    return (abs(b["cap1"] / cap - 1) < 0.03 and c1i is not None and abs(b["c1"] - c1i) < 0.03 and b["c1"] < 0.9 and b["n2"] > 0.3 and b["Tw1"] > a["Tw1"] + 10,
            f"1차 능력 {b['cap1']:.0f} W(따로 계산 {cap:.0f}) · 응축 비율 {f2(b['c1'])}(따로 {f2(c1i)}) · 2차로 {f2(b['n2'])} kg/h · 냉매 출구 {a['Tw1']} → {b['Tw1']} ℃",
            "능력 = ε·C·(T포화 − T냉매) ±3 % · 응축 비율 = 능력/부하 ±0.03 · 2차로 넘어감 · 냉매 출구 +10 ℃")
def _steam(a, b, c):
    return (b["MV"] == 70 and b["V"] > 1.5 * a["V"] and b["Pstill"] > 1.5 * a["Pstill"] and b["Tpot"] > a["Tpot"] + 5 and (b["D"] > 2 * a["D"] or (abs(b["D"] - a["D"]) <= 0.05 * max(a["D"], 0.1) and b["R"] > 2 * a["R"])) and b["flood"] > a["flood"] and c["MV"] < b["MV"] - 5,   # v142: 유출 고정(D)이면 늘어난 응축액은 환류(나머지)로 간다
            f"증발 {f2(a['V'])} → {f2(b['V'])} kg/h · 정제기 압력 {a['Pstill']:.2f} → {b['Pstill']:.2f} torr · 내부 {a['Tpot']:.1f} → {b['Tpot']:.1f} ℃ · 유출 {f2(a['D'])} → {f2(b['D'])} · 환류 {f2(a['R'])} → {f2(b['R'])} · 범람 비 {a['flood']} → {b['flood']} · 되돌린 뒤 개도 {b['MV']} → {c['MV']} %",
            "증발 1.5배 · 압력 1.5배 · 내부 +5 ℃ · 유출 2배 넘게(환류 고정) 또는 유출 설정 그대로 · 환류 2배 넘게(유출 고정 — 환류가 나머지) · 되돌리면 개도가 내려오기 시작(30분에 5 %p 넘게)")
def _preg(a, b, c):   # v135: 밸브 앞 스팀 압력이 오르면 같은 개도에서 스팀이 는다(임계 흐름 ∝ 절대 압력) — 입열 · 증발이 늘고, 되돌리면 입열이 다시 준다
    return (b["Q"] > 1.5 * a["Q"] and b["V"] > 1.15 * a["V"] and b["Tpot"] >= a["Tpot"] and c["Q"] < b["Q"],
            f"입열 {a['Q']:.0f} → {b['Q']:.0f} W · 증발 {f2(a['V'])} → {f2(b['V'])} kg/h · 내부 {a['Tpot']:.1f} → {b['Tpot']:.1f} ℃ · 되돌린 뒤 입열 {c['Q']:.0f} W",
            "입열 1.5배 넘게 · 증발 1.15배 넘게 · 되돌리면 입열이 준다")
def _rhigh(a, b, c):
    return ((b["R"] > 1.3 * a["R"] or (a["D"] - b["D"] > 0 and b["R"] - a["R"] >= 0.8 * (a["D"] - b["D"]))) and b["D"] < 0.6 * a["D"] and b["MV"] >= a["MV"] - 0.5 and c["R"] < 1.15 * a["R"],   # v142: 유출 고정이면 환류는 나머지 — 유출이 준 만큼 는다(응축액 전부여도 1.3배가 안 될 수 있다)
            f"환류 {f2(a['R'])} → {f2(b['R'])} kg/h · 유출 {f2(a['D'])} → {f2(b['D'])} kg/h · 스팀 개도 {a['MV']} → {b['MV']} %", "환류 1.3배 넘게(환류 고정) 또는 유출이 준 양의 80 % 넘게 환류가 늚(유출 고정 — 환류가 나머지) · 유출 60 % 밑 · 스팀은 같거나 더 열림")
def _rlow(a, b, c):
    return (b["R"] < 0.4 * a["R"] and b["D"] > 1.2 * a["D"] and b["xD"] < a["xD"],
            f"환류 {f2(a['R'])} → {f2(b['R'])} kg/h · 유출 {f2(a['D'])} → {f2(b['D'])} kg/h · 유출의 가벼운 성분 {a['xD']} → {b['xD']} mol%", "환류 40 % 밑 · 유출 1.2배 넘게 · 가벼운 성분 농축 줄어듦")
def _leak(a, b, c):
    ka = (a["Pcond"] - a["Pset"]) / a["leak"]; kb = (b["Pcond"] - b["Pset"]) / b["leak"]
    dt = b["t_h"] - a["t_h"]; lost = a["m"] - b["m"]; usual = a["D"] * dt      # 그동안 정제기에서 빠진 양 · 평소 유출이면 빠졌을 양
    tsat = lambda P: 4597 / (11.87 - math.log10(P)) - 273.15                    # CpHf 증기압식의 역(따로 계산). 증기압식을 바꾸면 여기도 바꾼다
    if b["V"] > 0.05: state = b["Pstill"] > b["Ptop"] > b["Pcond"] and abs(b["Tpot"] - tsat(b["Pstill"])) < 0.3   # 다시 끓고 있으면: 압력은 정제기 > 꼭대기 > 펌프 쪽, 액 온도 = 그 압력의 끓는점
    else: state = b["Tpot"] < b["Tbub"]                                           # 아직 멈춰 있으면: 액 온도 < 끓는점
    return (b["Pcond"] > 5 * a["Pcond"] and abs(kb / ka - 1) < 0.35 and lost < 0.2 * usual and b["Tpot"] > a["Tpot"] and state and c["Pcond"] < 1.5 * a["Pcond"] and c["V"] > 0.5 * a["V"],
            f"펌프 쪽 압력 {a['Pcond']:.3f} → {b['Pcond']:.3f} torr((P − 설정)/리크 = {ka:.3f} → {kb:.3f} min) · 30분 동안 정제기에서 빠진 양 {lost:.2f} kg(평소 유출이면 {usual:.2f}) · 내부 {a['Tpot']:.1f} → {b['Tpot']:.1f} ℃(정제기 압력 {b['Pstill']:.2f} torr의 끓는점 {tsat(b['Pstill']):.1f}) · 30분 뒤 증발 {f2(b['V'])} kg/h · 되돌린 뒤 증발 {f2(c['V'])}",
            "압력 5배 넘게, 오른 양은 리크에 비례(±35 %) · 30분 동안 빠진 양이 평소 유출의 20 % 밑 · 액이 새 끓는점까지 데워진 뒤에만 다시 끓음(±0.3 ℃) · 되돌리면 다시 끓음")
def _pump(a, b, c):
    ka = a["Pcond"] - a["Pset"]; kb = b["Pcond"] - b["Pset"]; ri = 1 / 0.03   # 유효 배기 속도가 3 %면 리크가 올리는 압력은 1/0.03배
    return (b["Pcond"] > 3 * a["Pcond"] and abs(kb / ka / ri - 1) < 0.35 and abs(b["V"] / a["V"] - 1) < 0.15 and b["Ptop"] > b["Pcond"],
            f"펌프 쪽 압력 {a['Pcond']:.3f} → {b['Pcond']:.3f} torr(설정 위로 오른 양 {kb / ka:.0f}배, 따로 계산 {ri:.0f}배) · 꼭대기 압력 {b['Ptop']:.3f} torr · 증발 {f2(a['V'])} → {f2(b['V'])} kg/h",
            "압력 3배 넘게(오른 양 = 1/개도 ±35 %) · 꼭대기 압력이 그보다 높은 동안(증기관 초킹) 증발은 ±15 %")
def _pstop(a, b, c):
    exp = a["Pcond"] + a["leak"] * 30   # 닫힌 계: 리크(mmHg/min) × 30분
    return (abs(b["Pcond"] / exp - 1) < 0.2 and b["V"] < 0.2 * a["V"] and b["Tpot"] > a["Tpot"] and c["V"] > 0.5 * a["V"],
            f"펌프 쪽 압력 {a['Pcond']:.3f} → {b['Pcond']:.3f} torr(리크 × 30분 = {exp:.2f}) · 증발 {f2(a['V'])} → {f2(b['V'])} kg/h · 내부 {a['Tpot']:.1f} → {b['Tpot']:.1f} ℃ · 되돌린 뒤 증발 {f2(c['V'])}",
            "압력 = 처음 + 리크 × 시간 ±20 % · 끓음 멈춤 · 되돌리면 다시 끓음")
def _cold(a, b, c):
    ri = (b["Tpot"] - b["Tamb"]) / (a["Tpot"] - a["Tamb"]); rs = b["Qloss"] / a["Qloss"]
    return (abs(rs / ri - 1) < 0.1 and b["Qcool"] > 1.15 * a["Qcool"] and b["back"] > 1.1 * a["back"],
            f"탱크 열손실 {a['Qloss']:.0f} → {b['Qloss']:.0f} W({rs:.2f}배, 온도 차 비 {ri:.2f}) · 컬럼 벽 손실 {a['Qcool']} → {b['Qcool']} W · 컬럼 안 응축 {f2(a['back'])} → {f2(b['back'])} kg/h", "열손실 ∝ (내부 − 외기) ±10 % · 컬럼 안 응축 1.1배 넘게")
def _bare(a, b, c):
    U = lambda t: 1 / (t / 1000 / 0.04 + 1 / 10); ri = U(b["tIns"]) / U(a["tIns"]) * (b["Tpot"] - b["Tamb"]) / (a["Tpot"] - a["Tamb"]); rs = b["Qloss"] / a["Qloss"]
    return (abs(rs / ri - 1) < 0.1 and b["back"] > 1.5 * a["back"],
            f"탱크 열손실 {a['Qloss']:.0f} → {b['Qloss']:.0f} W({rs:.2f}배, 따로 계산 {ri:.2f}배) · 컬럼 안 응축 {f2(a['back'])} → {f2(b['back'])} kg/h", "열손실 = 1/(t/k + 1/10) 비 ±10 % · 컬럼 안 응축 1.5배 넘게")
CRIT = {"c1hot": _c1hot, "c1cold": _c1cold, "c2hot": _c2hot, "cwlow": _cwlow, "steam": _steam, "rhigh": _rhigh, "rlow": _rlow, "leak": _leak, "pump": _pump, "pstop": _pstop, "cold": _cold, "bare": _bare, "preg": _preg}
