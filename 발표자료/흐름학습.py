# -*- coding: utf-8 -*-
"""정제 공정 계산 흐름 학습 페이지

실행:  python 흐름학습.py [점검 결과 이름]        예: python 흐름학습.py v125_최종
- 정제기의 액이 가열 → 증발 → 컬럼 → 증기 배관 → 응축 → 분배 → 진공 · 회수로 가는 순서대로, 단계마다 공식을 적용해 값을 구한다.
- 수치는 직접 입력하지 않는다. 값.json(시뮬레이터 v125, 본류 회수 중 30 h)과 점검 기록에서 읽어 계산한다(만들기.py와 같은 값).
- 내는 것: ../정제_계산_흐름_학습.html(파일 하나로 열림)
"""
import math, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "점검"))
_src = (HERE / "만들기.py").read_text(encoding="utf-8")
_head = _src.split("# ---------------------------------------------------------------- 조각")[0]      # 값 모으기 부분만 쓴다(페이지는 만들지 않음)
NS = {"__file__": str(HERE / "만들기.py")}
exec(compile(_head, "만들기.py", "exec"), NS)

from 그림 import esc, eq_html, svg_open, pin, text, leader
from 설비도 import plant
from 내용 import N, PIMS, LAW
import 틀

D, NODES, END, X, VER = NS["D"], NS["NODES"], NS["END"], NS["EXTRA"], NS["VER"]
S30 = D["snap"]["30"]; P = S30["PR"]; C = S30["CUR"]; MIX = S30["mix"]

# ---------------------------------------------------------------- 계산(시뮬레이터 식과 같은 식으로 다시 계산해 기록값과 맞춘다)
x = P["MVpct"] / 100; ms = C["mSteamMax"] * C["valveR"] ** (x - 1)
lamS = S30["fn"]["lamSteam"] / 1000; Qkw = ms * lamS / 3600
U = C["U"]; A30 = P["Q"] / (U * (P["TjEff"] - P["Tmean"])); UA = U * A30; dTj = P["Q"] / UA
lam = P["lam"] / 1000; W = (P["Q"] - P["Qloss"]) / 1000 / lam * 3600; M = X["hvap_mol"] / lam * 1000
A_, B_ = C["antB"]["A"], C["antB"]["B"]; Pst = P["Pstill"]; tsat = lambda p: B_ / (A_ - math.log10(p)) - 273.15
Tb = tsat(Pst); tcm = X["torr_cm"]; Tb1 = tsat(Pst + tcm)
back = P["backKg"]; vpass = X["vpass"]; R = P["Rkg"]; Dd = P["Dkg"]; T1 = P["T1out"]; Tsat = P["Tsat"]; cp = MIX["cp"] / 1000
sub = R * cp * (Tsat - T1) / lam; subTop = X["subTop"] * R
Nst = C["Hpack"] / C["HETP"]; wet = P["wetF"]
LD = 30 * C["nElb"] + 20 * C["nTeeR"]
Cw = C["mcw"] / 3600 * 4186; eps = 1 - math.exp(-C["UA1"] / Cw)
seal = math.pi / 4 * 0.0175 ** 2 * 1.2 * MIX["rho"]
assert abs(ms - P["steamKgh"]) < 0.01 and abs(Qkw * 1000 - P["Q"]) < 2 and abs(W - P["vdot"]) < 0.05 and abs(Tb - P["Tbub"]) < 0.05 and abs(sub - P["subR"] * R) < 0.01, "다시 계산한 값이 기록과 다르다"
# PIMS 화면 시점(초류, 정제기 371.9 kg)의 스팀 열수지
qS = PIMS["FI"] * lamS / 3600; qP = (PIMS["R"] + PIMS["D"]) * lam / 3600
Tv = C["T"]; hh = lambda m: (m / MIX["rho"] - math.pi * Tv ** 3 / 24) / (math.pi * Tv * Tv / 4)
UAp = U * (A30 + math.pi * Tv * (hh(PIMS["W"]) - hh(P["m"]))); dTneed = qS * 1000 / UAp

# ---------------------------------------------------------------- 조각
READ = {"valve": "이퀄 퍼센티지(등비율)", "steamlam": "왓슨 식", "agit": "울–그레이 상관식", "antoine": "앙투안 식('안토인 식'이라고도 함)", "bubble": "라울의 법칙",
        "hvap": "클라우지우스–클라페이롱 식", "mccabe": "맥케이브–틸레 법", "nst": "에이치이티피", "flood": "에커트 선도 · 케슬러–완캣 근사식", "dp": "키스터–길 상관식",
        "holdup": "빌레트–슐테스 식", "leq": "크레인 티피-410", "fric": "처칠 식", "ntu": "엡실론–엔티유 법", "sat": "돌턴의 분압 법칙", "sat2": "돌턴의 분압 법칙",
        "pi": "피아이 제어(비례 · 적분 제어)", "rayleigh": "레일리 식"}

def step(no, title, law, read, eqs, what, calc="", res="", nx=""):
    eqs = [eqs] if isinstance(eqs, str) else eqs
    return (f'<article class="step" id="st{no}"><div class="hd"><span class="no">{no}</span><h3>{esc(title)}</h3><span class="law">{esc(law)}</span>'
            + (f'<span class="rd">{esc(read)}</span>' if read else "") + "</div>"
            + f'<p class="what">{esc(what)}</p><div class="eqs">' + "".join(eq_html(e) for e in eqs) + "</div>"
            + (f'<div class="calc"><b>대입</b>{esc(calc)}</div>' if calc else "") + (f'<div class="res"><b>결과</b>{esc(res)}</div>' if res else "")
            + (f'<div class="nx">{esc(nx)}</div>' if nx else "") + "</article>")

def note(kind, title, body):
    lab = {"est": "가정", "fld": "현장 값과 비교", "cpt": "핵심 개념"}[kind]
    return f'<aside class="note {kind}"><b class="k">{lab} · {esc(title)}</b><span>{body}</span></aside>'

def stage(n, title, tag, summary, body):
    return (f'<section class="stg" id="s{n}"><header><span class="sn">{n}</span><h2>{esc(title)}</h2><span class="tg">{esc(tag)}</span></header>'
            f'<p class="sum">{esc(summary)}</p>{body}</section>')

# ---------------------------------------------------------------- 전체 그림: 설비 위 단계 번호
def fig_flow():
    fid = "fig-flow"; o = [svg_open(fid, 1200, 690, "정제 설비 전체 그림. 번호는 액과 증기가 지나가는 순서대로 나눈 여덟 단계다", y0=36)]
    o.append(plant(fid, level=0.57, main=0.35, fore=0.55))
    pos = {1: (32, 420, [(114, 428), (148, 510)]), 2: (378, 498, [(367, 503), (340, 514)]), 3: (112, 196, [(172, 196), (293, 196)]), 4: (410, 108, [(410, 97), (410, 77)]),
           5: (668, 214, [(657, 214), (641, 214)]), 6: (700, 306, [(689, 305), (614, 301)]), 7: (996, 248, [(989, 239), (973, 221)]), 8: (868, 520, [(858, 526), (822, 562)])}
    for nd in NODES:
        px, py, ld = pos[nd["n"]]
        o.append(leader(fid, ld, "n", of=f"s{nd['n']}"))
        o.append(f'<a href="#s{nd["n"]}" aria-label="{esc(nd["verb"])} 단계로 이동">' + pin(px, py, nd["n"], "pin link") + "</a>" + text(px + 17, py + 4.5, nd["verb"], "nlv", "start"))
    o.append("</svg>"); return "".join(o)

def loop_svg(fid, label, items, back):
    n = len(items); bw, bh, gap = 150, 50, 44; Wd = n * bw + (n - 1) * gap + 40
    o = [svg_open(fid, Wd, 150, label)]; xs = [20 + i * (bw + gap) for i in range(n)]
    for i, (x0, s) in enumerate(zip(xs, items)):
        lines = s.split("|"); o.append(f'<rect class="lpb" x="{x0}" y="20" width="{bw}" height="{bh}" rx="10"/>')
        for j, ln in enumerate(lines): o.append(text(x0 + bw / 2, 20 + bh / 2 + 5 + (j - (len(lines) - 1) / 2) * 16, ln, "lpt"))
        if i < n - 1: o.append(leader(fid, [(x0 + bw + 3, 45), (x0 + bw + gap - 3, 45)], "n", of=f"{fid}-{i}"))
    xl = xs[-1] + bw / 2; xf = xs[0] + bw / 2
    o.append(leader(fid, [(xl, 72), (xl, 110), (xf, 110), (xf, 73)], "n", dash=True, of=f"{fid}-back") + text((xl + xf) / 2, 134, back, "lpr"))
    o.append("</svg>"); return "".join(o)

# ---------------------------------------------------------------- 단계 내용
NM = {nd["n"]: nd for nd in NODES}
def tag(n): return NM[n]["tag"]

S1 = stage(1, "가열 · 자켓과 스팀", tag(1), "스팀이 컨트롤 밸브를 지나 자켓에서 응축하며 열을 내놓고, 그 열이 자켓 벽을 거쳐 액으로 전달된다.",
    step(1, "스팀 유량", LAW["valve"], READ["valve"], "m_{스팀} = m_{100%}·R^{(x − 1)}",
         "밸브 개도를 스팀 유량으로 바꾼다. 운전원이 조작하는 값은 개도뿐이므로 계산은 여기서 시작한다.",
         f"{N(C['mSteamMax'], 0)} kg/h × {N(C['valveR'], 0)}^({x:.3f} − 1)", f"{ms:.2f} kg/h (개도 {N(P['MVpct'])} %)", "→ 스팀 유량을 2단계에서 열량으로 바꾼다.")
    + step(2, "스팀 공급 열량", LAW["steamlam"], READ["steamlam"], ["Q_{최대} = m_{스팀}·λ_{스팀}", "λ_{스팀} = λ_{100℃}·[(T_{c} − T)/(T_{c} − 100)]^{0.33}"],
         "스팀 1 kg이 응축하며 내놓는 잠열을 곱해 열량으로 바꾼다. 잠열은 온도에 따라 달라 Watson 식으로 보정한다.",
         f"λ(133 ℃) = 2,256.4 × ((373.9 − 133) ÷ 273.9)^0.33 = {N(lamS, 0)} kJ/kg → {ms:.2f} kg/h × {N(lamS, 0)} kJ/kg ÷ 3,600",
         f"{Qkw:.2f} kW", "→ 공급 열량을 3단계에서 자켓 벽 너머로 전달한다.")
    + step(3, "자켓에서 액으로의 전열", LAW["jacket"] + " + " + LAW["agit"], READ["agit"], ["Q = U·A·(T_{자켓} − T_{액})", "Nu = 0.36·Re^{2/3}·Pr^{1/3}"],
         "교반 조건(80 rpm)과 액 물성으로 총괄 전열계수 U를 구하고, 공급 열량을 전달하는 데 필요한 온도 차를 구한다.",
         f"U {N(U, 0)} W/m²K(Re {N(X['Re'], 0)}) × 접액 면적 {A30:.2f} m² = {N(UA, 0)} W/K → {N(P['Q'], 0)} W ÷ {N(UA, 0)} W/K = {dTj:.1f} ℃",
         f"자켓 {N(P['TjEff'])} ℃ · 액 {N(P['Tmean'])} ℃", "→ 전달 열량을 4단계에서 증발량으로 바꾼다. 밸브가 열량을 정하고, 자켓 온도는 그 열량을 전달할 만큼만 액보다 높아진다.")
    + note("fld", "FIH071 13.5 kg/h(초류 PIMS 화면)",
           f"FIH071은 스팀 컨트롤 밸브 전단에 있다. 같은 배관이면 밸브 앞뒤의 질량 유량은 같으므로 개도 {PIMS['MV']:g} %로 조인 결과가 이미 지시값에 들어 있다. 그런데 이 양이 자켓에서 모두 응축하면 {qS:.1f} kW이고, "
           f"같은 화면의 환류 + 유출 {PIMS['R'] + PIMS['D']:.2f} kg/h를 증발시키는 데는 {qP:.2f} kW면 된다. 또 {qS:.1f} kW를 전달하려면 자켓이 액보다 약 {dTneed:.0f} ℃ 높아야 하는데(U·A {N(UAp, 0)} W/K, 정제기 {PIMS['W']} kg), "
           f"TIH074 {PIMS['Tj']} ℃는 내부 {PIMS['T']} ℃와 1 ℃ 이내다. 따라서 지시값 전부가 자켓에서 응축된다고 보기는 어렵다. 확인할 것: 유량계 측정 범위(저유량 오차), 유량계와 밸브 사이 분기, 스팀 트랩 상태, TIH074 설치 위치."))

S2 = stage(2, "증발 · 정제기 내부", tag(2), "액이 끓는점에 도달하면 남는 열이 증발에 쓰인다. 끓는점은 정제기 압력으로 정해지고, 그 압력은 증기가 빠져나가는 경로(13단계)에서 정해진다.",
    step(4, "증발량", LAW["heatbal"] + " + " + LAW["hvap"], READ["hvap"], ["W = (Q − Q_{손실}) / λ", "λ = R·B·ln10 / M"],
         "공급 열량에서 보온재를 통한 열손실을 뺀 나머지를 증발열로 나눈다. 증발열은 증기압 곡선의 기울기 B에서 나온다.",
         f"λ = 8.314 × {N(B_, 0)} × ln10 ÷ {N(M, 0)} g/mol = {N(lam, 0)} kJ/kg → ({Qkw:.3f} − {P['Qloss'] / 1000:.3f}) kW ÷ {N(lam, 0)} kJ/kg × 3,600",
         f"{W:.1f} kg/h", "→ 증기가 7단계(충전 컬럼)로 올라간다. 증발열이 물의 약 1/10이라 1 kW 미만으로도 시간당 약 10 kg이 증발한다.")
    + step(5, "끓는점", LAW["antoine"] + " + " + LAW["bubble"], READ["antoine"] + " · " + READ["bubble"], [f"log_{{10}} P_{{sat}} = {A_} − {B_:.0f}/T", "Σ x_{i}·P_{sat,i}(T) = P"],
         "정제기 압력과 증기압이 같아지는 온도를 구한다. 저비점 불순물이 미량이어서 제품의 증기압이 끓는점을 정한다.",
         f"P = {Pst:.2f} torr → T = {N(B_, 0)} ÷ ({A_} − log₁₀ {Pst:.2f}) − 273.15", f"{P['Tbub']:.1f} ℃", f"→ 압력 {Pst:.2f} torr는 13단계에서 거꾸로 정해진다.")
    + step(6, "액 깊이에 따른 끓는점", LAW["head"], "", "P(깊이) = P + ρ·g·깊이",
         "액 내부는 깊을수록 위쪽 액의 무게만큼 압력이 높아져 끓는점도 높아진다.",
         f"{N(MIX['rho'], 0)} kg/m³ × 9.81 × 0.01 m = {tcm:.2f} torr → 1 cm 아래 {Pst + tcm:.2f} torr의 끓는점 {Tb1:.1f} ℃",
         f"액면보다 {Tb1 - Tb:.1f} ℃ 높아야 끓는다", "→ 진공에서는 액면 부근에서만 끓고, 교반이 고온의 액을 액면까지 올려 준다."))

S3 = stage(3, "분리 · 충전 컬럼", tag(3), "상승하는 증기와 하강하는 환류액이 충전물 표면에서 접촉하면서 저비점 성분이 컬럼 상부에 농축된다.",
    step(7, "컬럼 벽면 응축", "열수지(벽면 열손실 ÷ 증발열)", "", "L_{벽} = Q_{벽} / λ",
         "컬럼 벽으로 빠져나가는 열만큼 증기가 응축해 정제기로 되돌아간다.",
         f"{P['Qcool']:.1f} W ÷ {N(lam, 0)} kJ/kg × 3,600", f"{back:.2f} kg/h → 컬럼 상부를 통과하는 증기 {vpass:.2f} kg/h", "→ 8단계")
    + step(8, "과냉 환류에 의한 내부 응축", LAW["subcool"], "", "ΔL = L·c_{p}·(T_{포화} − T_{환류}) / λ",
         "응축기에서 식은 환류액이 컬럼에서 가열되면서 그 열량만큼 증기를 응축시킨다.",
         f"{R:.1f} kg/h × {cp:.1f} kJ/kg·K × ({Tsat:.1f} − {T1:.1f}) ℃ ÷ {N(lam, 0)} kJ/kg", f"{sub:.2f} kg/h", "→ 내부 환류가 늘어 9단계의 환류비에 반영된다.")
    + note("est", "환류액이 가열되는 끝 온도",
           f"계산식은 끝 온도를 응축기 압력의 포화 온도({Tsat:.1f} ℃)로 둔다. 증기 배관이 초킹 상태이면 컬럼 상부({N(P['Thead'])} ℃)가 더 뜨거워, 상부 온도로 보면 내부 응축은 {subTop:.2f} kg/h가 되고 그만큼 유출이 줄어든다.")
    + step(9, "분리 정도", LAW["nst"] + " + " + LAW["mccabe"], READ["nst"] + " · " + READ["mccabe"], ["N = H_{충전} / HETP", "y_{n+1} = R/(R + 1)·x_{n} + x_{D}/(R + 1)"],
         "충전 높이를 이론단수로 바꾸고, 내부 환류비로 조작선을 그어 컬럼 상부 증기의 조성을 구한다.",
         f"{C['Hpack']:.1f} m ÷ {C['HETP']:.2f} m = {Nst:.1f}단(젖음률 {wet:.2f}을 곱하면 {Nst * wet:.2f}단) → 계산 하한 1단 · 내부 환류비 {P['Rcol']:.2f}",
         f"저비점 성분 {P['y0'] * 100:.2f} → {P['xD'] * 100:.2f} mol%", "→ 이 조성의 증기가 배관으로 가고(11단계), 유출액의 조성이 된다(22단계).")
    + step(10, "범람률 · 압력 손실 · 홀드업", LAW["flood"] + " · " + LAW["dp"] + " · " + LAW["holdup"], READ["flood"] + " · " + READ["dp"] + " · " + READ["holdup"],
         ["d = ΔP_{범람}·(F/F_{한계})^{2}·H_{충전}", "P_{정제기} = d + √(d^{2} + P_{상부}^{2})"],
         "증기 유속이 범람 한계에 얼마나 가까운지, 충전층에서 압력이 얼마나 떨어지는지, 충전층에 체류하는 액량을 구한다.",
         f"범람률 {P['flood'] * 100:.0f} % · d {X['dPack']:.2f} torr · 홀드업 {C['hold']:.2f} × {X['Vpack_L']:.2f} L × {N(MIX['rho'], 0)} kg/m³",
         f"정제기 {Pst:.2f} torr = 컬럼 상부 {P['Ptop']:.2f} + {P['dpPackC']:.2f} torr · 홀드업 {X['mHold']:.2f} kg", "→ 컬럼 상부 압력은 13단계에서 정해진다."))

S4 = stage(4, "증기 이송 · 증기 배관", tag(4), "컬럼 상부를 나온 증기가 80A 배관을 지나 1차 응축기로 간다. 고진공의 증기는 밀도가 매우 낮아 유속이 빨라지고, 배관 출구에서 음속에 도달한다.",
    step(11, "배관 상당 길이", LAW["leq"], READ["leq"], "L_{상당} = L + D·Σ(L/D)",
         "엘보와 티의 저항을 직관 길이로 환산해 더한다(L/D: 엘보 30, 직진 티 20).",
         f"{X['Lstr']:.1f} m + {C['Dpipe']:.4f} m × (30 × {C['nElb']:g} + 20 × {C['nTeeR']:g})", f"{X['Leq']:.2f} m", "→ 12단계")
    + step(12, "관 마찰계수", LAW["fric"], READ["fric"], "f = f(Re, 거칠기)",
         "층류부터 난류까지 하나의 식으로 마찰계수를 구한다.", f"Re {N(X['Re_pipe'], 0)} · 거칠기 0.046 mm ÷ 내경 {C['Dpipe'] * 1000:.1f} mm", f"f = {X['f_pipe']:.3f}", "→ 13단계")
    + step(13, "배관 압력 손실과 초킹", LAW["comp"] + " + " + LAW["choke"], "", ["P_{입구}^{2} = P_{출구}^{2} + (G^{2}RT/M)·K", "P_{출구} ≥ G·R·T / (M·0.95·a)"],
         "저압 증기는 흐르는 동안 압력이 떨어져 밀도가 낮아지고 유속이 빨라진다. 배관 출구에서 음속(마하 0.95 한계)에 도달하면 출구 압력은 더 내려가지 않는다.",
         f"음속 {X['asound']:.0f} m/s · 배관 출구 {P['Pexit']:.2f} torr(응축기 측 {P['Pcond']:.2f} torr) → 배관 입구",
         f"컬럼 상부 {P['Ptop']:.2f} torr → (10단계) 정제기 {Pst:.2f} torr → (5단계) 끓는점 {P['Tbub']:.1f} ℃", "→ 압력은 흐름과 반대 방향, 곧 응축기 쪽에서부터 정해진다.")
    + note("cpt", "진공 비등 평형",
           "증발량이 늘면 배관 · 충전층의 압력 손실이 커져 정제기 압력과 끓는점이 오르고, 끓는점이 오르면 증발이 줄어든다. 시뮬레이터는 계산 단계마다 4 · 5 · 10 · 13단계를 함께 만족하는 증발량과 압력을 구한다."))

S5 = stage(5, "응축 · 1차 응축기", tag(5) + " · 세로 BEM", "증기가 튜브 안을 내려가며 동체 쪽 N-Brine(50 ℃)에 열을 주고 응축된다. 1차 응축기는 세로 BEM형(고정 관판 · 직관)이다.",
    step(14, "응축 부하", LAW["load"], "", "Q_{부하} = W·λ", "응축기가 제거해야 할 열량을 구한다.",
         f"{vpass:.2f} kg/h × {N(lam, 0)} kJ/kg ÷ 3,600", f"{P['Qc'] / 1000:.2f} kW", "→ 15단계에서 처리 가능 열량과 비교한다.")
    + step(15, "처리 가능 열량과 응축률", LAW["ntu"], READ["ntu"], ["ε = 1 − e^{−UA/C}", "Q_{최대} = ε·C·(T_{포화} − T_{냉매})", "응축률 = min(1, Q_{최대} / Q_{부하})"],
         "냉매가 가져갈 수 있는 최대 열량을 구해 부하와 비교한다.",
         f"냉매 {N(C['mcw'], 0)} kg/h → C {N(Cw, 0)} W/K · UA {N(C['UA1'], 0)} W/K → ε {eps:.3f} · ΔT {Tsat:.1f} − {C['Tcw']:g} ℃",
         f"{P['cap1'] / 1000:.0f} kW(부하의 {P['cap1'] / P['Qc']:.0f}배) → 응축률 {P['c1'] * 100:.0f} % · 응축액 {T1:.1f} ℃", "→ 응축액이 17단계로 떨어진다.")
    + step(16, "공기 동반 증기", LAW["sat"], READ["sat"], "n_{증기} = n_{공기}·S / (1 − S),  S = P_{sat}(T_{출구}) / P",
         "유입된 공기는 응축되지 않고 통과하면서 출구 온도에서 포화되는 만큼의 증기를 동반한다.", "", f"{X['m2_gh']:.1f} g/h", "→ 2차 응축기(21단계)로 간다.")
    + note("est", "응축 부하의 증기량",
           f"응축 부하는 컬럼 상부를 통과한 증기 {vpass:.2f} kg/h로 계산하지만, 회수되는 응축액은 환류 + 유출 {R + Dd:.2f} kg/h다. 차이 {sub:.2f} kg/h는 8단계에서 컬럼 안에서 이미 응축된 양인데, 배관 · 응축기 계산에서는 빼지 않는다."))

S6 = stage(6, "분배 · 환류와 유출", tag(6), "응축액은 U자 액봉을 거쳐 환류(컬럼으로)와 유출(회수 탱크로)로 나뉜다. 스팀은 응축량이 두 설정값의 합에 맞도록 조절된다.",
    step(17, "U자 액봉", LAW["seal"], "", "m_{액봉} = (π/4)·d^{2}·L·ρ",
         "U자 구간이 액으로 채워져야 증기가 역류하지 않고 환류 · 유출이 흐르기 시작한다.",
         f"(π/4) × 0.0175² m² × 1.2 m × {N(MIX['rho'], 0)} kg/m³ = {seal:.2f} kg(15A, 길이 약 1.2 m 가정)", f"입력값 {C['holdC']:.2f} kg", "→ 18단계")
    + step(18, "환류 · 유출 분배", LAW["split"], "", "R = min(R_{설정}, W_{응축}),  D = W_{응축} − R",
         "환류를 설정값만큼 먼저 확보하고 나머지는 유출로 보낸다.",
         f"응축액 {R + Dd:.2f} kg/h = 환류 {R:.2f} + 유출 {Dd:.2f}", f"환류 {R:.1f} kg/h(약 {T1:.0f} ℃) → 컬럼 상부(8단계) · 유출 {Dd:.1f} kg/h → 본류 탱크(22단계)")
    + step(19, "스팀 제어", LAW["pi"], READ["pi"], "MV = K_{p}·e + (K_{p}/T_{i})·∫e dt,  e = (R + D)_{설정} − W_{응축}",
         "응축량이 설정값보다 작으면 밸브 개도를 높이고, 크면 낮춘다(게인 1, 적분 시간 900초).",
         f"측정 {R + Dd:.2f} kg/h · 설정 10 kg/h(환류 4 + 유출 6)", f"개도 {P['MVpct']:.1f} % 유지", "→ 1단계로 돌아간다. 현장의 제어 방식(TIC · FIC · 수동)은 확인 중이다."))

S7 = stage(7, "진공 배기 · 2차 응축기와 진공펌프", tag(7) + " · 가로 BEU", "진공펌프는 계로 유입된 공기를 배기하고, 2차 응축기(가로 BEU형 · U자관, L-Brine −22.6 ℃)는 펌프 전단에서 남은 증기를 응축시킨다.",
    step(20, "진공 압력", LAW["pump"] + " · " + LAW["tau"], "", ["P_{펌프 측} = P_{설정} + 리크·τ", "τ = V / S"],
         "유입 공기(리크)와 펌프 배기 속도가 균형을 이루는 압력을 구한다.",
         f"{C['P']:.2f} torr + {C['leak']:.2f} mmHg/min × {P['tauP']:.0f}초({P['tauP'] / 60:.2f}분)", f"펌프 측 {P['Ppump']:.3f} torr", "→ 응축기 측 압력이 13단계의 배관 출구 조건이 된다.")
    + step(21, "2차 응축기 손실", LAW["sat2"], READ["sat2"], "n_{증기} = n_{공기}·S / (1 − S),  S = P_{sat}(T_{냉매}) / P",
         "−22.6 ℃에서는 증기압이 거의 0이라 공기와 함께 빠져나가는 증기가 거의 없다.", "", f"2차 응축 {X['m2_gh']:.1f} g/h · 진공펌프 손실 {X['lost_txt']}"))

S8 = stage(8, "회수 · 회수 탱크와 순도", tag(8), "유출액이 본류 탱크에 쌓인다. 매 순간의 유출 조성이 누적되어 본류 순도가 된다.",
    step(22, "성분 누적", LAW["accum"], "", "m_{A,탱크} = ∫ D·x_{D} dt", "9단계에서 구한 유출 조성을 시간에 따라 더한다.", "",
         f"배치 종료 시 본류 {END['main']:.1f} kg(저비점 {END['wM']:.2f} %) · 초류 {END['fore']:.1f} kg({END['wF']:.2f} %) · 정제기 잔량 {END['m']:.1f} kg")
    + step(23, "순도 해석", LAW["rayleigh"], READ["rayleigh"], "x_{본류} = x_{0}·[(1 − f)^{E} − (1 − f_{2})^{E}] / (f_{2} − f)",
         "계산 결과를 농축비 E 하나로 요약하고, 초류량을 바꿨을 때를 추산한다. 시뮬레이터 계산에는 쓰지 않는다.", "",
         f"현재 결과에서 역산한 E {END['Eeff']:.1f} · 순도 99.8 %에는 E 약 10이 필요(불순물이 모두 저비점일 때)"))

LOOPS = ('<section class="stg" id="loops"><header><h2>계산이 순환하는 두 고리</h2></header>'
         '<p class="sum">단계는 한 방향으로 흐르지만, 두 곳에서 결과가 앞 단계로 되돌아간다. 시뮬레이터는 계산 단계마다 두 고리가 함께 맞는 값을 구한다.</p>'
         '<figure><div class="scroll">' + loop_svg("fig-lp1", "압력 고리: 증발량이 늘면 압력과 끓는점이 올라 증발량이 다시 줄어든다",
                                                    ["증발량 증가", "배관 · 충전층|압력 손실 증가", "정제기 압력 상승", "끓는점 상승"], "끓는점이 오르면 증발량이 줄어든다(4 ← 5 ← 10 ← 13단계)")
         + '</div><figcaption>압력 고리: 진공 비등 평형(4 · 5 · 10 · 13단계)</figcaption></figure>'
         '<figure><div class="scroll">' + loop_svg("fig-lp2", "스팀 고리: 응축량이 설정보다 작으면 스팀을 더 열어 증발량을 늘린다",
                                                    ["응축량 < 설정", "PI 제어:|개도 증가", "스팀 유량 증가", "공급 열량 증가", "증발량 증가"], "응축량이 설정값에 가까워진다(19 → 1 → 2 → 4 → 14단계)")
         + '</div><figcaption>스팀 고리: 스팀 제어(19 · 1 · 2 · 4단계)</figcaption></figure></section>')

def quiz():
    ab = D["ab"]; out = []
    def li(*xs): return "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
    a, b, c = ab["steam"]
    out.append(("스팀 밸브 개도 0.2 → 70 % 고정", li(f"증발량 {a['V']:.1f} → {b['V']:.1f} kg/h, 정제기 압력 {a['Pstill']:.2f} → {b['Pstill']:.2f} torr, 내부 온도 {a['Tpot']:.1f} → {b['Tpot']:.1f} ℃",
                f"환류는 {b['R']:.1f} kg/h로 일정해 늘어난 증기가 유출로 나간다: {a['D']:.2f} → {b['D']:.2f} kg/h", f"범람률 {a['flood'] * 100:.0f} → {b['flood'] * 100:.0f} %"),
                "1 → 2 → 4 → 13 → 5 → 18단계"))
    a, b, c = ab["c1hot"]
    out.append(("1차 응축기 N-Brine 50 → 95 ℃", li(f"응축률 {a['c1'] * 100:.0f} → {b['c1'] * 100:.0f} %(냉매가 포화 온도 {a['Tsat']:.0f} ℃보다 뜨겁다)", f"증기 {b['n2']:.1f} kg/h가 2차 응축기로 넘어간다",
                f"환류 · 유출이 0이 되어 스팀 제어가 개도를 {a['MV']:g} → {b['MV']:g} %로 높인다"), "15 → 16 → 18 → 19 → 1단계"))
    a, b, c = ab["leak"]
    out.append(("진공 리크 0.05 → 5 mmHg/min", li(f"펌프 측 압력 {a['Pcond']:.2f} → {b['Pcond']:.2f} torr", f"끓는점이 올라 액이 {b['Tpot'] - a['Tpot']:.1f} ℃ 가열될 때까지 증발이 거의 멈춘다",
                f"30분 후 증발량 {a['V']:.2f} → {b['V']:.2f} kg/h"), "20 → 13 → 10 → 5 → 4단계"))
    a, b, c = ab["rlow"]
    out.append(("환류 설정 4 → 0.8 kg/h", li(f"환류 {a['R']:.1f} → {b['R']:.1f} kg/h, 유출 {a['D']:.2f} → {b['D']:.2f} kg/h", f"유출액의 저비점 성분 {a['xD']:.2f} → {b['xD']:.2f} mol%(컬럼의 분리 효과 감소)"),
                "18 → 9 → 22단계"))
    return ('<section class="stg" id="quiz"><header><h2>입력 하나를 바꿨을 때의 변화</h2><span class="tg">이상 상황 시험 기록 · 초류 10 h에서 30분 후</span></header>'
            '<p class="sum">결과를 펼치기 전에 어느 단계부터 어떤 값이 바뀔지 먼저 따라가 본다.</p>'
            + "".join(f'<details class="qz"><summary>{esc(t)}</summary>{body}<p class="trail">따라가 볼 단계: {esc(tr)}</p></details>' for t, body, tr in out) + "</section>")

ROWS = [
    ("Antoine 식", READ["antoine"], "온도별 증기압", "진공에서 몇 ℃에 끓는지 계산하는 출발점. 끓는점 · 정제기 압력 · 증발량이 모두 이 값에서 나온다", "5"),
    ("Raoult의 법칙", READ["bubble"], "혼합액의 끓는점(기포점)과 증기 조성", "내부 온도를 계산해 현장 TICH071과 비교하고, 증기에 섞여 올라가는 저비점 불순물의 양을 구한다", "5"),
    ("Clausius–Clapeyron 식", READ["hvap"], "증발열(1 kg을 증발시키는 열량)", f"공급 열량(kW)을 증발량(kg/h)으로 환산한다({N(lam, 0)} kJ/kg)", "4"),
    ("McCabe–Thiele 법", READ["mccabe"], "컬럼 상부 증기(유출액)의 조성", "초류에 저비점 불순물이 얼마나 모이는지, 환류량을 바꾸면 분리가 얼마나 달라지는지 판단한다", "9"),
    ("Rayleigh 식", READ["rayleigh"], "회분 증류에서 본류의 평균 불순물 농도", "목표 순도(99.8 %)에 필요한 초류량을 추산한다. 시뮬레이터 계산에는 쓰지 않고 결과 해석에 쓴다", "23"),
    ("Dalton의 분압 법칙", READ["sat"], "응축기를 빠져나가는 공기에 동반되는 증기량", "진공펌프로 손실되는 제품량과, 리크가 늘 때 2차 응축기로 넘어가는 증기량을 구한다", "16 · 21"),
    ("Watson 식", READ["steamlam"], "온도별 스팀 응축 잠열", f"스팀 유량(kg/h)을 공급 열량(kW)으로 환산한다(133 ℃ 스팀 1 kg당 {N(lamS, 0)} kJ)", "2"),
    ("Churchill 식", READ["fric"], "관 마찰계수", "증기 배관 압력 손실을 구해 컬럼 상부 압력을 계산한다. 층류부터 난류까지 한 식으로 이어진다", "12"),
    ("Kister–Gill 상관식", READ["dp"], "범람점 기준 충전층 압력 손실", f"이 기준값에서 현재 유속의 충전층 압력 손실(본류 {P['dpPackC']:.2f} torr)을 구한다. 그만큼 정제기 압력과 끓는점이 높아진다", "10"),
    ("Eckert 선도 · Kessler–Wankat 근사식", READ["flood"], "충전탑의 범람 한계 유속", f"범람률(본류 {P['flood'] * 100:.0f} %)을 구해 스팀 과다 시 컬럼이 범람하는지 판단한다. 근사식은 선도를 계산식으로 옮긴 것", "10"),
    ("Billet–Schultes 식", READ["holdup"], "범람점 충전층 홀드업", f"범람에 가까워질 때 충전층 체류액이 늘어나는 정도를 구한다. 정상 운전에서는 카탈로그값 {C['hold'] * 100:.0f} %를 쓴다", "10"),
    ("Uhl–Gray 상관식", READ["agit"], "교반조 벽면의 액 측 전열계수", f"총괄 전열계수 U({N(U, 0)} W/m²K)를 구해 자켓에서 액으로 전달되는 열량을 계산한다. U 실측값이 없어 교반 속도와 물성으로 구한다", "3"),
    ("Crane TP-410", READ["leq"], "배관 부속(엘보 · 티)의 상당 길이", f"부속 저항을 직관 길이로 환산해({X['Lstr']:.1f} m → {X['Leq']:.2f} m) 마찰 손실 계산에 쓴다. 식이 아니라 부속별 저항값을 정리한 기술 자료다", "11"),
    ("ε–NTU 법", READ["ntu"] + "(유효도–전달단위수법)", "응축기의 최대 처리 열량", "1차 응축기가 증기를 전량 응축하는지 판단하고, 냉매 온도가 오르거나 유량이 줄 때 2차로 넘어가는 양을 구한다", "15"),
    ("HETP", READ["nst"] + "(이론단 상당 높이)", "이론단수(충전 높이 ÷ HETP)", f"컬럼의 분리 능력을 정한다. 이 단수가 McCabe–Thiele 계산에 들어간다({C['Hpack']:.1f} m ÷ {C['HETP']:.2f} m = {Nst:.1f}단)", "9"),
    ("Equal percentage", READ["valve"], "밸브 개도별 스팀 유량", "운전원이 조작하는 개도를 열량으로 바꾸는 첫 단계. 상수가 가정값이며, 현장 FIH071 값으로 맞추기 전에 그 지시값이 자켓 사용량인지 확인이 필요하다", "1"),
    ("PI 제어", READ["pi"], "스팀 밸브 개도", "응축량(환류 + 유출)이 설정 합계에 맞도록 스팀을 자동 조절한다. 현장 제어 방식(TIC · FIC · 수동)은 확인 중", "19"),
    ("Nu · Re · Pr", "누셀트 수 · 레이놀즈 수 · 프란틀 수", "무차원수. 차례로 대류 열전달의 크기, 흐름 상태(층류/난류), 물성으로 정해지는 열전달 특성", "교반 전열 상관식(Nu = 0.36·Re^(2/3)·Pr^(1/3))으로 전열계수를 구한다. Re는 관 마찰계수(Churchill 식)에도 쓴다", "3 · 12"),
]
TABLE = ('<section class="stg" id="names"><header><h2>공식 명칭 · 읽기 · 용도</h2></header><div class="tw"><table><tr><th>명칭</th><th>읽기</th><th>구하는 값</th><th>구하는 이유</th><th>단계</th></tr>'
         + "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td><td>{esc(d)}</td><td class=\"m\">{esc(e)}</td></tr>" for a, b, c, d, e in ROWS) + "</table></div></section>")

TOC = '<nav class="toc">' + "".join(f'<a href="#s{nd["n"]}"><i>{nd["n"]}</i>{esc(nd["verb"])}</a>' for nd in NODES) + '<a href="#loops">두 고리</a><a href="#quiz">입력 변경</a><a href="#names">공식 명칭</a></nav>'

CSS2 = r"""
.wrap { max-width:1100px; margin:0 auto; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:22px 64px; display:grid; gap:20px }
.hero { display:grid; gap:8px } .hero h1 { font-size:28px; line-height:1.25; margin:0; letter-spacing:-.01em; text-wrap:balance } .hero .lead { margin:0; color:var(--sub); max-width:76ch }
.info { display:flex; flex-wrap:wrap; gap:6px 16px; font-size:13px; color:var(--sub); background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:10px 14px }
.info b { color:var(--ink); font-weight:600 }
.toc { display:flex; flex-wrap:wrap; gap:6px } .toc a { display:inline-flex; align-items:center; gap:6px; text-decoration:none; color:var(--ink); border:1px solid var(--line); background:var(--panel); border-radius:999px; padding:3px 11px 3px 4px; font-size:13px }
.toc a i { font:700 11.5px var(--f-mono); font-style:normal; width:21px; height:21px; border-radius:50%; background:var(--ink); color:var(--panel); display:grid; place-items:center }
.toc a:not(:has(i)) { padding-left:11px } .toc a:hover { border-color:var(--ink) }
section.stg { display:grid; gap:10px; scroll-margin-top:12px; min-width:0 }
.stg > header { display:flex; flex-wrap:wrap; align-items:baseline; gap:6px 12px; padding-top:6px; border-top:1px solid var(--line) }
.stg .sn { font:700 15px var(--f-mono); width:30px; height:30px; border-radius:50%; background:var(--ink); color:var(--panel); display:grid; place-items:center; align-self:center }
.stg h2 { font-size:21px; line-height:1.3; margin:0; text-wrap:balance } .stg .tg { font:500 12px var(--f-mono); color:var(--sub) }
.stg .sum { margin:0; color:var(--sub); max-width:80ch }
.step { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:13px 16px; display:grid; gap:7px; min-width:0; scroll-margin-top:12px }
.step .hd { display:flex; flex-wrap:wrap; align-items:center; gap:4px 10px }
.step .no { font:700 12px var(--f-mono); min-width:28px; height:26px; padding:0 6px; border-radius:8px; background:var(--acc); color:var(--panel); display:grid; place-items:center }
.step h3 { font-size:16px; margin:0 } .step .law { font-size:13px; font-weight:600; color:var(--acc) } .step .rd { font-size:12.5px; color:var(--sub) }
.step .what { margin:0; font-size:14px; max-width:84ch }
.step .eqs { display:flex; flex-wrap:wrap; gap:4px 26px; padding:2px 0 } .step .eqs .eqn { color:var(--ink); font-size:17px }
.step .calc, .step .res { font:500 13px/1.6 var(--f-mono); padding:6px 10px; border-radius:8px; overflow-wrap:anywhere }
.step .calc { background:var(--soft) } .step .res { background:var(--acc-soft); font-weight:600 }
.step .calc b, .step .res b { font:600 12px var(--f-body); color:var(--sub); margin-right:10px }
.step .nx { font-size:13px; color:var(--sub) }
.note { border-radius:10px; padding:10px 14px; font-size:13.5px; border:1px solid; display:grid; gap:4px; max-width:100% }
.note .k { font-size:12.5px } .note.est { background:var(--est-soft); border-color:var(--est) } .note.est .k { color:var(--est) }
.note.fld { background:var(--db-soft); border-color:var(--db) } .note.fld .k { color:var(--db) } .note.cpt { background:var(--soft); border-color:var(--line) }
details.qz { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:10px 14px } details.qz summary { cursor:pointer; font-weight:600 }
details.qz ul { margin:8px 0 4px; padding-left:20px } details.qz li { font-size:13.5px; margin:3px 0 } .trail { margin:4px 0 0; font-size:12.5px; color:var(--acc); font-weight:600 }
.lpb { fill:var(--panel); stroke:var(--sub); stroke-width:1.3 } .lpt { fill:var(--ink); font:600 13px var(--f-body); text-anchor:middle } .lpr { fill:var(--acc); font:600 12.5px var(--f-body); text-anchor:middle }
.foot { font-size:12.5px; color:var(--sub) }
"""

def page():
    hero = ('<header class="hero"><h1>정제 공정 계산 흐름</h1>'
            '<p class="lead">정제기의 액이 스팀으로 가열되어 증발하고, 증기는 충전 컬럼에서 환류액과 접촉한 뒤 증기 배관을 지나 응축기에서 다시 액이 된다. '
            '응축액은 환류와 유출로 나뉘어 일부는 컬럼으로 되돌아가고 나머지는 회수 탱크에 쌓인다. 이 흐름을 따라 단계마다 공식을 적용해 값을 구한다.</p>'
            f'<div class="info"><span><b>기준 상태</b> 시뮬레이터 {esc(VER)} · 본류 회수 중 {P["t_h"]:.0f} h · 정제기 잔량 {P["m"]:.0f} kg · 설정 환류 4 · 유출 6 kg/h</span>'
            '<span><b>수치</b> 시뮬레이터 계산값. 증기압식의 상수 A가 가정값이어서 온도는 현장보다 14~19 ℃ 높게 나온다</span>'
            '<span><b>표시</b> 노란 상자 = 가정, 초록 상자 = 현장 값과 비교, 회색 상자 = 핵심 개념</span></div></header>')
    fig = (f'<figure><div class="scroll">{fig_flow()}</div><figcaption>번호는 아래 단계 묶음과 같다. 번호를 누르면 해당 설명으로 이동한다. '
           '1차 응축기(E-H071)는 세로 BEM형(고정 관판 · 직관), 2차 응축기(E-H072)는 가로 BEU형(U자관)이다.</figcaption></figure>')
    foot = '<p class="foot">구간별 그림 · 가정과 추정 · DB 데이터 활용은 발표자료(정제_시뮬레이터_발표자료.html)에 있다. 수치 출처: 값.json(시뮬레이터 v125)과 점검 기록(점검결과_v125_최종.json).</p>'
    body = hero + TOC + fig + S1 + S2 + S3 + S4 + S5 + S6 + S7 + S8 + LOOPS + quiz() + TABLE + foot
    return ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<title>정제 계산 흐름 학습</title>\n' + 틀.FONTS + '\n<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}' + 틀.CSS + CSS2 + "</style>\n</head>\n<body>\n"
            f'<div class="wrap">{body}</div>\n</body>\n</html>\n')

out = HERE.parent / "정제_계산_흐름_학습.html"
out.write_text(page(), encoding="utf-8", newline="\n")
print("계산 흐름 학습", out.name, out.stat().st_size, "바이트 · 단계 23")
