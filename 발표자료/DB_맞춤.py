# -*- coding: utf-8 -*-
"""DB 6배치 요약값을 시뮬레이터 식에 넣어 본 계산 — 발표자료 · 교과서 · 맞춤 안내가 읽는 숫자를 만든다.

실행:  python DB_맞춤.py [점검 결과 이름]        예: python DB_맞춤.py v130_최종
- 읽는 것: DB값.json(사내망 DB 분석 문서의 배치 표를 옮긴 것) · 값.json(시뮬레이터에서 뽑은 다섯 시점) · 점검결과_<이름>.json(배치 끝 기록)
           시험계산_기록.json(있으면. 시험계산.py가 시뮬레이터에 상수만 바꿔 넣고 돌린 기록)
- 내는 것: DB_맞춤_결과.json(문서가 읽는 숫자). 직접 실행하면 ../현장값_DB_맞춤_계산.md(사람이 읽는 표)와 ../현장_데이터_맞춤_안내.md의 10절도 다시 쓴다.
- 숫자는 손으로 옮겨 적지 않는다. DB 값은 DB값.json, 시뮬레이터 값은 기록에서 읽는다.

계산하는 것
 1. 배치 · 구간마다 증기 배관을 지나는 유량 V = 환류 + 유출(유량계 보정), 음속 한계 압력, 지금 증기압식이 주는 압력
 2. V와 내부 온도의 관계: log10 V = c − B/T (기울기 B를 DB로 다시 구해 본다)
 3. 증기 배관 식(시뮬레이터의 lineTop을 그대로 옮긴 것)에 DB의 V · 온도를 넣어 정제기 압력을 구하고, 그 압력이 내부 온도의 포화압이 되는 상수 A
 4. 시험 계산이 있으면: 시뮬레이터에 넣었을 때 본류의 (증발량, 내부 온도)가 DB 관계 위에 오는 상수(문서가 쓰는 값 A_use)
 5. 내부 온도와 탑 온도의 차가 뜻하는 압력비, 탑 온도계 자리 · 문헌 증기압과의 비교
"""
import io, json, math, pathlib, statistics as st, sys

HERE = pathlib.Path(__file__).resolve().parent
tag = next((a for a in sys.argv[1:] if not a.startswith("-")), "v130_최종")
_dbf = HERE / "DB값.json"      # 현장 데이터라 공개 저장소에는 두지 않는다(2026-11-21 사용자). 형식은 DB값_양식.json
if not _dbf.exists(): raise SystemExit("DB값.json이 없다 — 현장 데이터라 공개 저장소에는 두지 않는다. DB 배치 분석 표를 DB값_양식.json과 같은 형식으로 만들어 발표자료/에 두고 다시 돌린다.")
DBV = json.loads(_dbf.read_text(encoding="utf-8"))
VAL = json.loads((HERE / "값.json").read_text(encoding="utf-8"))
_ck = HERE.parent / "점검" / f"점검결과_{tag}.json"
if not _ck.exists(): _ck = HERE / f"점검결과_{tag}.json"
CHK = json.loads(_ck.read_text(encoding="utf-8"))
END = dict(CHK["raw"]["합침 배치 끝"]["res"]["end"]); VER = CHK.get("ver") or "v130"
_tr = HERE / "시험계산_기록.json"; TRIAL = json.loads(_tr.read_text(encoding="utf-8")) if _tr.exists() else None

S30 = VAL["snap"]["30"]; P30 = S30["PR"]; C = S30["CUR"]
A0, B0 = C["antB"]["A"], C["antB"]["B"]
MW = C["MWB"]; Mk = MW / 1000; RG = 8.314462; MM = 133.322
Dp = C["Dpipe"]; Ap = math.pi * Dp * Dp / 4; Leq = C["Lpipe"]; Lfit = C["Lfit"]; RHO = S30["mix"]["rho"]; CP = S30["mix"]["cp"]; LAM = P30["lam"]
TB_K = 238.0 + 273.15            # 시뮬레이터 물질 표의 끓는점(증기 점도 식의 ε/k = 1.15·Tb에 쓴다)

psat = lambda T, A=A0, B=B0: 10 ** (A - B / (T + 273.15))
tsat = lambda P, A=A0, B=B0: B / (A - math.log10(P)) - 273.15
mean = lambda v: sum(v) / len(v)
rng = lambda v: [min(v), max(v)]

# ---------------------------------------------------------------- 시뮬레이터 식을 옮긴 것(증기 배관 · 충전층)
def churchill(Re, rr):
    if not Re > 1: return 0.0
    a = (2.457 * math.log(1 / ((7 / Re) ** 0.9 + 0.27 * rr))) ** 16; b = (37530 / Re) ** 16
    return 8 * ((8 / Re) ** 12 + (a + b) ** -1.5) ** (1 / 12)

def mu_v(Tk):
    """증기 점도(Chapman–Enskog, 시뮬레이터와 같은 식)."""
    sigA = 0.9965 * (Mk / (RHO * 6.022e23)) ** (1 / 3) * 1e10; ts = Tk / (1.15 * TB_K)
    om = 1.16145 * ts ** -0.14874 + 0.52487 * math.exp(-0.7732 * ts) + 2.16178 * math.exp(-2.43787 * ts)
    return 2.6693e-6 * math.sqrt(MW * Tk) / (sigA * sigA * om)

def a_son(Tk):
    n = max(3, MW / 5.5); gam = 1 + 2 / (3 + 3 * n - 6)
    return math.sqrt(gam * RG * Tk / Mk)

def line_top(Wkgh, Tk, L=None, Pcond=None):
    """lineTop: 출구 초킹(마하 0.95) + 등온 압축성 마찰 + 가속 항. 압력은 torr."""
    L = Leq if L is None else L; P2 = max(0.01, P30["Pcond"] if Pcond is None else Pcond)
    W = Wkgh / 3600; RT = RG * Tk
    Pch = W / (0.95 * a_son(Tk) * Ap) * RT / Mk / MM
    Pex = max(P2, Pch); rhoE = Pex * MM * Mk / RT; u = W / (rhoE * Ap); Re = rhoE * u * Dp / mu_v(Tk)
    f = churchill(Re, 4.6e-5 / Dp); Kp = RT * W * W / (Mk * Ap * Ap) / (MM * MM)
    Pt = math.sqrt(Pex * Pex + f * (L / Dp) * Kp)
    for _ in range(8): Pt = math.sqrt(Pex * Pex + Kp * (f * (L / Dp) + 2 * math.log(max(1, Pt / max(1e-9, Pex)))))
    return dict(Pch=Pch, Pexit=Pex, Ptop=Pt, f=f, Re=Re, Kp=Kp, choked=Pch > P2 * 1.001, u=u)

# 충전층: 압력 손실 ∝ (증기 유량)²·T ÷ 압력. 비례 상수는 시뮬레이터 30 h 기록(정제기 · 컬럼 상부 압력)에서 정한다
W30 = P30["vdot"] - P30["backKg"]                    # 시뮬레이터가 증기 배관으로 보내는 양(환류 + 유출 + 과냉 환류가 응축시키는 양)
T30 = P30["Tmean"] + 273.15
_d30 = (P30["Pstill"] ** 2 - P30["Ptop"] ** 2) / (2 * P30["Pstill"])
CPK = _d30 * P30["Pstill"] / (W30 ** 2 * T30)
def p_still(Ptop, Wkgh, Tk):
    lo, hi = Ptop, Ptop * 20
    for _ in range(60):
        m = (lo + hi) / 2; d = CPK * Wkgh ** 2 * Tk / m
        if m < d + math.sqrt(d * d + Ptop * Ptop): lo = m
        else: hi = m
    return (lo + hi) / 2

_chk = line_top(W30, T30)
assert abs(_chk["Pexit"] - P30["Pexit"]) < 0.004 and abs(_chk["Ptop"] - P30["Ptop"]) < 0.02, ("옮긴 증기 배관 식이 시뮬레이터 기록과 다르다", _chk, P30["Pexit"], P30["Ptop"])
assert abs(p_still(P30["Ptop"], W30, T30) - P30["Pstill"]) < 0.003

# ---------------------------------------------------------------- 1. 배치 · 구간별 값
B_ = DBV["배치"]; kraw = DBV["FICH072_무게_적분_비"]; kmean = mean([k for k in kraw if k is not None])
kcor = [k if k is not None else round(kmean, 2) for k in kraw]
pts = []
for ph in ("초류", "본류"):
    X = DBV[ph]
    for j, b in enumerate(B_):
        D, R, T, Tj, Tt = X["D"][j], X["R"][j], X["T"][j], X["Tj"][j], X["Ttop"][j]
        V = R + D * kcor[j]; Tk = T + 273.15; TtK = Tt + 273.15
        Pson = V / 3600 / Ap * math.sqrt(RG * TtK / Mk) / MM            # 음속 한계: 관 어디서든 P ≥ G·√(RT/M)
        pts.append(dict(ph=ph, b=b, D=D, R=R, k=kcor[j], Dc=D * kcor[j], V=V, RD=R / (D * kcor[j]), T=T, Tj=Tj, Tt=Tt, dT=T - Tt, dTj=Tj - T,
                        P0=psat(T), P0t=psat(Tt), Pson=Pson, sonRatio=Pson / psat(Tt), c=math.log10(V) + B0 / Tk, VP=V / psat(T),
                        pr=10 ** (B0 * (1 / TtK - 1 / Tk))))
MAIN = [p for p in pts if p["ph"] == "본류"]; FORE = [p for p in pts if p["ph"] == "초류"]

# ---------------------------------------------------------------- 2. V와 내부 온도의 관계
xs = [1 / (p["T"] + 273.15) for p in pts]; ys = [math.log10(p["V"]) for p in pts]; n = len(pts)
xm, ym = mean(xs), mean(ys); sxx = sum((x - xm) ** 2 for x in xs); sxy = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
Bfit = -sxy / sxx; res = [y - (ym - Bfit * (x - xm)) for x, y in zip(xs, ys)]; s2 = sum(r * r for r in res) / (n - 2); Bse = math.sqrt(s2 / sxx)
cDB = mean([p["c"] for p in pts]); cSD = st.pstdev([p["c"] for p in pts])
T_of_V = lambda V: B0 / (cDB - math.log10(V)) - 273.15                   # DB 12점의 관계(기울기 B는 지금 값): 증발량 V일 때의 내부 온도
V_of_T = lambda T: 10 ** (cDB - B0 / (T + 273.15))
vp = [p["VP"] for p in pts]

# ---------------------------------------------------------------- 3. 증기 배관 식 → 정제기 압력 → 상수 A
def fit_A(L=None, extra=0.0, sel=pts):
    """점마다: 배관을 V(+ extra·환류)가 지날 때의 정제기 압력 = 내부 온도의 포화압이 되는 A."""
    out = []
    for p in sel:
        Tk = p["T"] + 273.15; W = p["V"] + extra * p["R"]
        lt = line_top(W, Tk, L); Ps = p_still(lt["Ptop"], W, Tk)
        out.append(dict(b=p["b"], ph=p["ph"], Pexit=lt["Pexit"], Ptop=lt["Ptop"], Pstill=Ps, A=math.log10(Ps) + B0 / Tk, f=lt["f"], Re=lt["Re"], Kp=lt["Kp"], choked=lt["choked"]))
    return out
FA = fit_A(); A_phys = mean([r["A"] for r in FA]); A_sd = st.pstdev([r["A"] for r in FA]); A_main = mean([r["A"] for r in FA if r["ph"] == "본류"])
for p, r in zip(pts, FA): p.update(Pexit=r["Pexit"], Ptop=r["Ptop"], Pstill=r["Pstill"], Afit=r["A"], choked=r["choked"])
assert all(r["choked"] for r in FA), "DB의 유량에서는 12점 모두 출구 초킹이어야 한다(시뮬레이터 식)"
A_half = mean([r["A"] for r in fit_A(L=Leq / 2)]); A_x15 = mean([r["A"] for r in fit_A(L=Leq * 1.5)])
# 마찰을 0으로 둔 하한: 출구 초킹 압력 + 충전층만
A_min = mean([math.log10(p_still(line_top(p["V"], p["T"] + 273.15, 0.0)["Ptop"], p["V"], p["T"] + 273.15)) + B0 / (p["T"] + 273.15) for p in pts])
PS0 = [p_still(line_top(p["V"], p["T"] + 273.15, 0.0)["Ptop"], p["V"], p["T"] + 273.15) for p in MAIN]      # 마찰을 0으로 둔 정제기 압력(본류)
# 탑 온도가 그 자리의 포화 온도라면 필요한 최소 A(음속 한계, 마찰 가정과 무관)
A_son = mean([math.log10(p["Pson"]) + B0 / (p["Tt"] + 273.15) for p in MAIN])

# ---------------------------------------------------------------- 4. 시험 계산으로 확인한 상수(문서가 쓰는 값)
# 시뮬레이터는 과냉 환류가 컬럼 안에서 응축시키는 양까지 증기 배관 유량에 넣어 계산한다. 그래서 시뮬레이터에 넣을 값은 실제로 돌려서 확인한다:
# 본류 구간의 (증발량, 내부 온도)가 DB 12점의 관계 위에 오도록, 같은 압력에서 온도 차만큼 A를 옮긴다.
def a_cal(s):
    V = s["Rmain"] + s["Dmain"]
    return s["A"] + B0 * (1 / (T_of_V(V) + 273.15) - 1 / (s["Tmain"] + 273.15))
_runs = {k: r["sum"] for k, r in TRIAL["runs"].items()} if TRIAL else {}
_cal = [a_cal(s) for k, s in _runs.items() if k != TRIAL["base"]] if TRIAL else []
A_cal = mean(_cal) if _cal else A_phys
A_use = round(A_cal, 2)
TB = _runs.get(TRIAL["base"]) if TRIAL else None; TN = _runs.get(f"{A_use:.2f}")
sub_new = TN["sub30"] if TN else max(0.0, min(0.5, CP * (tsat(P30["Pcond"], A_use) - P30["T1out"]) / LAM))
FS = fit_A(extra=sub_new)
for p, r in zip(pts, FS): p.update(PexitS=r["Pexit"], PtopS=r["Ptop"], PstillS=r["Pstill"])

# ---------------------------------------------------------------- 5. 내부 온도 − 탑 온도 → 압력비 → 탑 온도계 자리 · 문헌
def te_pos(A, extra):
    out = []
    for p in MAIN:
        Tk = p["T"] + 273.15; W = p["V"] + extra * p["R"]; Pte = psat(p["Tt"], A); lt = line_top(W, Tk)
        Lst = Dp / lt["f"] * ((Pte ** 2 - lt["Pexit"] ** 2) / lt["Kp"] - 2 * math.log(max(1.0, Pte / lt["Pexit"]))) if Pte > lt["Pexit"] else 0.0
        out.append(dict(b=p["b"], Pte=Pte, rel=Pte / lt["Pexit"], frac=(Pte - lt["Pexit"]) / (lt["Ptop"] - lt["Pexit"]), Lst=Lst, Tex=tsat(lt["Pexit"], A), Ttop=tsat(lt["Ptop"], A)))
    return out
TE = te_pos(A_use, sub_new)
pr_main = [p["pr"] for p in MAIN]; pr_fore = [p["pr"] for p in FORE]
sim_pr_exit = P30["Pstill"] / P30["Pexit"]; sim_pr_top = P30["Pstill"] / P30["Ptop"]

LIT = [dict(T=60.0, P=0.10, src="A. Sharma 외, J. Vac. Sci. Technol. A 35, 01B130 (2017)", note="전구체 용기 60 ℃에서 약 0.1 torr(공급사 제공 값으로 인용)"),
       dict(T=60.0, P=0.13, src="H. Oike 외, 東ソー研究・技術報告 68, 3 (2024)", note="버블링 온도 60 ℃에서 0.13 torr(격막 압력계로 측정)"),
       dict(T=84.0, P=0.10, src="제조사 SDS", note="지금 증기압식의 기준점")]
for l in LIT: l.update(P_old=psat(l["T"]), P_new=psat(l["T"], A_use), r_old=l["P"] / psat(l["T"]), r_new=l["P"] / psat(l["T"], A_use))
# 문헌 60 ℃ 점과 100 ℃의 증기압(이 계산)을 함께 지나는 기울기 — 기울기 B가 달라질 가능성의 크기
_Pl = mean([l["P"] for l in LIT[:2]]); B_lit = math.log10(psat(100, A_use) / _Pl) / (1 / 333.15 - 1 / 373.15)

# ---------------------------------------------------------------- 6. 시뮬레이터 기록과의 비교
stg = {s[0]: s[1] for s in END["stages"]}
SIM = dict(ver=VER, A=A0, B=B0, Tfore=END["Tfore"], Tmain=END["Tmain"], ThFore=END["ThFore"], ThMain=END["ThMain"], TjFore=END.get("TjeFore"), TjMain=END.get("TjeMain"),
           Rfore=END["Rfore"], Dfore=END["Dfore"], Rmain=END["Rmain"], Dmain=END["Dmain"], Vfore=END["Rfore"] + END["Dfore"], Vmain=END["Rmain"] + END["Dmain"], T1main=END["T1main"],
           t_tr=stg[3] - stg[2], t_boil=stg[2], t_fore=stg[4] - stg[3], t_main=END["t"] - stg[4], t_all=END["t"], feed=END["m0"], fore=END["fore"], main=END["main"], left=END["m"],
           m2=P30["m2kg"], Pstill=P30["Pstill"], Ptop=P30["Ptop"], Pexit=P30["Pexit"], Pcond=P30["Pcond"], Wpipe=W30, V30=P30["Rkg"] + P30["Dkg"], T30=P30["Tmean"], sub=P30["subR"],
           Leq=Leq, Lstr=Leq - Lfit, Dpipe=Dp * 1000, VP=(P30["Rkg"] + P30["Dkg"]) / P30["Pstill"])
DBR = dict(Tfore=rng(DBV["초류"]["T"]), Tmain=rng(DBV["본류"]["T"]), ThFore=rng(DBV["초류"]["Ttop"]), ThMain=rng(DBV["본류"]["Ttop"]), TjFore=rng(DBV["초류"]["Tj"]), TjMain=rng(DBV["본류"]["Tj"]),
           Rfore=rng(DBV["초류"]["R"]), Dfore=rng(DBV["초류"]["D"]), Rmain=rng(DBV["본류"]["R"]), Dmain=rng(DBV["본류"]["D"]), Vfore=rng([p["V"] for p in FORE]), Vmain=rng([p["V"] for p in MAIN]),
           RDfore=rng([p["RD"] for p in FORE]), RDmain=rng([p["RD"] for p in MAIN]), T1main=rng(DBV["본류"]["Tbot"]), dTmain=rng([p["dT"] for p in MAIN]), dTfore=rng([p["dT"] for p in FORE]),
           dTjMain=rng([p["dTj"] for p in MAIN]), dTjFore=rng([p["dTj"] for p in FORE]),
           t_heat=rng(DBV["승온_90도_h"]), t_tr=rng(DBV["전환류_h"]), t_fore=rng(DBV["초류_h"]), t_main=rng(DBV["본류_h"]), t_all=rng(DBV["전체_h"]),
           feed=rng(DBV["투입"]), fore=rng(DBV["초류량"]), main=rng(DBV["본류량"]), forePct=rng(DBV["초류_투입_pct"]),
           left=rng([v for v, b in zip(DBV["남은양"], B_) if b not in DBV["남은양_제외"]]), m2=DBV["범위"]["이차응축기_유입"])
DBM = dict(Tfore=mean(DBV["초류"]["T"]), Tmain=mean(DBV["본류"]["T"]), ThFore=mean(DBV["초류"]["Ttop"]), ThMain=mean(DBV["본류"]["Ttop"]), Vfore=mean([p["V"] for p in FORE]), Vmain=mean([p["V"] for p in MAIN]),
           dTmain=mean([p["dT"] for p in MAIN]), dTfore=mean([p["dT"] for p in FORE]), k=kmean)
# 승온 열량 어림(DB 문서 4-4와 같은 계산을 기록의 물성으로): 26#28
_j = B_.index("28"); hr = DBV["범위"]["승온_기울기"]; heat_kw = [DBV["투입"][_j] * CP * h / 60 / 1000 for h in hr]

OUT = dict(tag=tag, ver=VER, A0=A0, B0=B0, MW=MW, Dpipe=Dp * 1000, Leq=Leq, Lfit=Lfit, Lstr=Leq - Lfit, kmean=kmean, kcor=kcor, pts=pts,
           Bfit=Bfit, Bse=Bse, Bn=n, cDB=cDB, cSD=cSD, VPmean=mean(vp), VPsd=st.pstdev(vp), VPrng=rng(vp), Vrng=rng([p["V"] for p in pts]), Trng=rng([p["T"] for p in pts]),
           P0rng=rng([p["P0"] for p in pts]), P0_main=rng([p["P0"] for p in MAIN]), P0t_main=rng([p["P0t"] for p in MAIN]), Pson_main=rng([p["Pson"] for p in MAIN]),
           sonRatio=rng([p["sonRatio"] for p in pts]), sonRatio_main=rng([p["sonRatio"] for p in MAIN]),
           A_use=A_use, A_cal=A_cal, A_cals=_cal, sub_new=sub_new, A_phys=A_phys, A_sd=A_sd, A_main=A_main, A_rng=rng([r["A"] for r in FA]), A_half=A_half, A_x15=A_x15, A_min=A_min, A_son=A_son,
           dA_half=A_half - A_phys, dA_x15=A_x15 - A_phys, dA_min=A_min - A_phys,
           Pstill_main=rng([p["PstillS"] for p in MAIN]), Pstill_fore=rng([p["PstillS"] for p in FORE]), Ptop_main=rng([p["PtopS"] for p in MAIN]), Pexit_main=rng([p["PexitS"] for p in MAIN]), Pstill0_main=rng(PS0),
           ratio100=psat(100, A_use) / psat(100), P100_old=psat(100), P100_new=psat(100, A_use),
           pr_main=rng(pr_main), pr_main_mean=mean(pr_main), pr_fore=rng(pr_fore), pr_fore_mean=mean(pr_fore), sim_pr_exit=sim_pr_exit, sim_pr_top=sim_pr_top,
           TE=TE, TE_P=rng([t["Pte"] for t in TE]), TE_rel=rng([t["rel"] for t in TE]), TE_Lst=rng([t["Lst"] for t in TE]), TE_Tex=rng([t["Tex"] for t in TE]), TE_Ttop=rng([t["Ttop"] for t in TE]),
           LIT=LIT, B_lit=B_lit, lam_lit=RG * B_lit * math.log(10) / MW, lam_fit=RG * Bfit * math.log(10) / MW, lam0=RG * B0 * math.log(10) / MW, SIM=SIM, DBR=DBR, DBM=DBM, heat_kw=heat_kw,
           T_at_simV=T_of_V(SIM["Vmain"]), V_at=dict(T95=V_of_T(95), T98=V_of_T(98), T101=V_of_T(101)), Tboil_cond=dict(old=tsat(P30["Pcond"]), new=tsat(P30["Pcond"], A_use)))
if TRIAL:
    OUT["trial"] = TRIAL
    if TN: OUT["T_at_trialV"] = T_of_V(TN["Rmain"] + TN["Dmain"])
(HERE / "DB_맞춤_결과.json").write_text(json.dumps(OUT, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- 사람이 읽는 표(직접 실행할 때만 다시 쓴다)
def _f(x, d=1): return f"{x:,.{d}f}".replace("-", "−")
def _s(x, d=2): return f"{x:+.{d}f}".replace("-", "−")
def _r(v, d=1): return _f(v[0], d) if abs(v[1] - v[0]) < 0.5 * 10 ** -d else f"{_f(v[0], d)}~{_f(v[1], d)}"
def jo(s, a, b):
    """숫자로 끝나는 말 뒤의 조사: 끝 숫자를 읽었을 때 받침이 있으면 a, 없으면 b. '으로'는 ㄹ 받침(1 · 7 · 8)이면 b('로')."""
    d = [c for c in str(s) if c.isdigit()][-1]
    return f"{s}{a if d in ('036' if a == '으로' else '013678') else b}"

def report():
    assert TB and TN, f"시험 계산에 기준과 A = {A_use:.2f} 기록이 있어야 한다 — python 시험계산.py {A_use:.2f} --add"
    b, t = TB, TN; R = DBR; S = SIM; G = DBV["범위"]; gap = t["Tmain"] - OUT["T_at_trialV"]; DOC = DBV["문서의_압력해석"]
    L = []; w = L.append
    w(f"# DB 6배치와 시뮬레이터 {VER}의 비교 · 증기압식 상수 계산\n")
    w("- 이 문서의 표와 숫자는 `발표자료/DB_맞춤.py`가 만든다. 손으로 고치지 않는다.")
    w(f"- DB 값: 사내망에서 쓴 'CpHf 2차정제 DB 배치 분석(6배치, {DBV['기간']})'의 배치 표를 옮긴 `발표자료/DB값.json`. 10분 간격 시계열을 구간별로 평균한 값이다.")
    w(f"- 계산값: 시뮬레이터 {VER}의 레시피 운전 기록(`발표자료/값.json`, 점검 기록의 배치 끝 값).")
    w(f"- 시험 계산: 시뮬레이터 파일은 그대로 두고, 실행 중에 CpHf 증기압식의 상수 A만 바꿔 넣어 한 배치를 돌린 기록(`발표자료/시험계산.py` → `시험계산_기록.json`, {TRIAL['when']}).")
    w("- 시뮬레이터 기본값은 바꾸지 않았다. 10절의 반영안은 사용자 판단을 기다린다.\n")
    w("## 1. 요약\n")
    w("| 구분 | 내용 |\n|---|---|")
    w(f"| DB와 맞는 것 | 증발량(환류 + 유출)은 초류 {_f(S['Vfore'])} · 본류 {_f(S['Vmain'])} kg/h로 DB 범위({_r(R['Vfore'])} · {_r(R['Vmain'])} kg/h) 안이다. 전환류 {_f(S['t_tr'])} h · 초류 {_f(S['t_fore'])} h · 본류 {_f(S['t_main'])} h도 DB 범위({_r(R['t_tr'])} · {_r(R['t_fore'])} · {_r(R['t_main'])} h) 안이다 |")
    w(f"| DB와 다른 것 | 본류 내부 온도가 {_f(S['Tmain'] - R['Tmain'][1], 0)}~{_f(S['Tmain'] - R['Tmain'][0], 0)} ℃, 탑 온도가 {_f(S['ThMain'] - R['ThMain'][1], 0)}~{_f(S['ThMain'] - R['ThMain'][0], 0)} ℃ 높다. 자켓 온도도 내부 온도를 따라 높다 |")
    w(f"| 원인 | CpHf 증기압식의 절대값(상수 A)이 낮다. 지금 식으로 본류 탑 온도의 포화압을 구하면 {_r(OUT['P0t_main'], 3)} torr인데, 같은 유량이 80A 배관을 지나려면 {_r(OUT['Pson_main'], 2)} torr 이상이어야 한다(음속 한계). 이 한계가 지금 식의 포화압보다 {_r(OUT['sonRatio_main'], 1)}배 높다 |")
    w(f"| DB로 구한 상수 | A = {A_use:.2f}(지금 {A0}). 기울기 B는 그대로 {_f(B0, 0)}. 100 ℃의 증기압이 {_f(OUT['P100_old'], 2)} → {_f(OUT['P100_new'], 2)} torr({_f(OUT['ratio100'], 1)}배)가 된다 |")
    w(f"| 시험 계산 | A만 {A_use:.2f}로 바꾸면 내부 온도가 초류 {_f(S['Tfore'])} → {_f(t['Tfore'])} ℃, 본류 {_f(S['Tmain'])} → {_f(t['Tmain'])} ℃로 DB 범위({_r(R['Tfore'])} · {_r(R['Tmain'])} ℃)에 든다. 증기 배관 출구 압력의 포화 온도는 {_f(t['Tex30'])} ℃로 DB 탑 온도({_r(R['ThMain'])} ℃, 평균 {_f(DBM['ThMain'])} ℃)의 아래쪽에 있다(평균보다 {_f(DBM['ThMain'] - t['Tex30'])} ℃ 낮다) |")
    w(f"| 정하지 못한 것 | 기울기 B(12점으로는 {_f(Bfit, 0)} ± {_f(Bse, 0)}), 압력계 영점 · 리크(압력 기록을 쓸 수 없다), 전열 · 열용량(시계열 회귀가 필요하다), 탑 온도계의 실제 자리 |\n")

    w("## 2. 계기별 비교\n")
    w(f"| 항목 | DB 6배치(구간 평균의 범위) | 계산 {VER} | 시험 계산(A {A_use:.2f}) |\n|---|---|---|---|")
    rows = [("내부 온도 TICH071, 초류 · 본류(℃)", f"{_r(R['Tfore'])} · {_r(R['Tmain'])}", f"{_f(S['Tfore'])} · {_f(S['Tmain'])}", f"{_f(t['Tfore'])} · {_f(t['Tmain'])}"),
            ("탑 온도 TIH075, 초류 · 본류(℃)", f"{_r(R['ThFore'])} · {_r(R['ThMain'])}", f"{_f(S['ThFore'])} · {_f(S['ThMain'])}(컬럼 상부)", f"{_f(t['ThFore'])} · {_f(t['ThMain'])}(컬럼 상부)"),
            ("증기 배관 출구 압력의 포화 온도, 6 h · 30 h(℃)", "—", f"{_f(b['Tex6'])} · {_f(b['Tex30'])}", f"{_f(t['Tex6'])} · {_f(t['Tex30'])}"),
            ("내부 − 탑, 초류 · 본류(℃)", f"{_r(R['dTfore'])} · {_r(R['dTmain'])}", f"{_f(S['Tfore'] - S['ThFore'])} · {_f(S['Tmain'] - S['ThMain'])}", f"{_f(t['Tfore'] - t['ThFore'])} · {_f(t['Tmain'] - t['ThMain'])}"),
            ("자켓 온도 TIH074, 초류 · 본류(℃)", f"{_r(R['TjFore'])} · {_r(R['TjMain'])}", f"{_f(b['TjFore'])} · {_f(b['TjMain'])}", f"{_f(t['TjFore'])} · {_f(t['TjMain'])}"),
            ("자켓 − 내부, 초류 · 본류(℃)", f"{_r(R['dTjFore'])} · {_r(R['dTjMain'])}", f"{_f(b['TjFore'] - b['Tfore'])} · {_f(b['TjMain'] - b['Tmain'])}", f"{_f(t['TjFore'] - t['Tfore'])} · {_f(t['TjMain'] - t['Tmain'])}"),
            ("환류 FICH073, 초류 · 본류(kg/h)", f"{_r(R['Rfore'])} · {_r(R['Rmain'])}", f"{_f(S['Rfore'], 2)} · {_f(S['Rmain'], 2)}", f"{_f(t['Rfore'], 2)} · {_f(t['Rmain'], 2)}"),
            ("유출 FICH072 지시값, 초류 · 본류(kg/h)", f"{_r(R['Dfore'])} · {_r(R['Dmain'])}", f"{_f(S['Dfore'], 2)} · {_f(S['Dmain'], 2)}", f"{_f(t['Dfore'], 2)} · {_f(t['Dmain'], 2)}"),
            ("증발량 = 환류 + 유출(유량계 보정), 초류 · 본류(kg/h)", f"{_r(R['Vfore'], 2)} · {_r(R['Vmain'], 2)}", f"{_f(S['Vfore'], 2)} · {_f(S['Vmain'], 2)}", f"{_f(t['Rfore'] + t['Dfore'], 2)} · {_f(t['Rmain'] + t['Dmain'], 2)}"),
            ("응축액 출구 TICH071D, 본류(℃)", _r(R["T1main"]), _f(S["T1main"]), _f(t["T1main"])),
            ("90 ℃ 도달(h)", _r(R["t_heat"]), _f(b["t90"], 2), _f(t["t90"], 2)),
            ("승온 중 자켓 최고(℃)", _r(G["자켓_승온_최고"], 0), _f(b["tjMax"]), _f(t["tjMax"])),
            ("전환류 · 초류 · 본류(h)", f"{_r(R['t_tr'])} · {_r(R['t_fore'])} · {_r(R['t_main'])}", f"{_f(S['t_tr'])} · {_f(S['t_fore'])} · {_f(S['t_main'])}", f"{_f(t['t_tr'])} · {_f(t['t_fore'])} · {_f(t['t_main'])}"),
            ("투입 · 초류 · 본류 · 남은 양(kg)", f"{_r(R['feed'], 0)} · {_r(R['fore'])} · {_r(R['main'], 0)} · {_r(R['left'], 0)}", f"{_f(S['feed'], 0)} · {_f(S['fore'])} · {_f(S['main'])} · {_f(S['left'])}", f"{_f(t['feed'], 0)} · {_f(t['fore'])} · {_f(t['main'])} · {_f(t['left'])}"),
            ("2차 응축기 → 초류 탱크(kg/h)", f"{R['m2'][0]}~{R['m2'][1]}", f"{b['m2_30']:.4f}", f"{t['m2_30']:.4f}"),
            ("정제기 · 컬럼 상부 · 배관 출구 압력, 30 h(torr)", "기록을 쓸 수 없다", f"{_f(b['Pstill30'], 2)} · {_f(b['Ptop30'], 2)} · {_f(b['Pexit30'], 2)}", f"{_f(t['Pstill30'], 2)} · {_f(t['Ptop30'], 2)} · {_f(t['Pexit30'], 2)}")]
    for r in rows: w("| " + " | ".join(r) + " |")
    w("")
    w(f"- 유출 유량의 계산값 {_f(S['Dmain'], 2)} kg/h는 운전 기준의 설정값(본류 유출 6)이다. DB 지시값의 상한 {_f(R['Dmain'][1])} kg/h와 같은 수준이고, 무게 기준(지시값 × {kmean:.2f})으로는 DB가 {_f(R['Dmain'][0] * kmean)}~{_f(R['Dmain'][1] * kmean)} kg/h다.")
    w(f"- 초류 환류의 계산값 {_f(S['Rfore'], 1)} kg/h는 운전 기준(환류 4)이고, DB는 {_r(R['Rfore'])} kg/h다(PIMS 화면의 설정값은 5).")
    w(f"- 90 ℃ 도달이 DB보다 늦다. 계산은 {_f(b['T0'], 0)} ℃에서 시작해 끓기 전까지 분당 {_f(b['slope'], 2)} ℃로 오르고(DB는 {_r(G['승온_시작온도'], 0)} ℃에서 분당 {_r(G['승온_기울기'])} ℃), 끓기 시작하면 전환류 목표에 맞춰 스팀을 줄인다. 스팀 밸브 특성식과 조절 방식의 가정에서 나온 차이다.")
    w(f"- 시험 계산에서 초류 구간이 {_f(S['t_fore'])} → {_f(t['t_fore'])} h로 짧아진다. 스팀 밸브 최소 개도의 열량은 그대로인데 내부 온도가 낮아져 열손실이 줄고, 그만큼 초류 유출이 {_f(S['Dfore'], 2)} → {_f(t['Dfore'], 2)} kg/h(설정 2)로 늘기 때문이다. 스팀 밸브 특성식의 가정값에서 나온 결과다.")
    w(f"- 2차 응축기 유입량은 {b['m2_30']:.4f} → {t['m2_30']:.4f} kg/h로 DB 범위의 아래쪽에 든다. 1차 응축기 출구 온도(50 ℃)에서의 증기압이 {_f(OUT['ratio100'], 1)}배가 되기 때문이다. 리크 유입량이 가정값이라 크기는 참고만 한다.\n")

    w("## 3. 증기 배관의 음속 한계\n")
    w(f"80A 증기 배관(내경 {_f(OUT['Dpipe'])} mm)을 유량 V가 지나려면 관 안 어디서든 압력이 G·√(RT/M) 이상이어야 한다(G = V ÷ 관 단면적, M = {MW}). 마찰 가정과 무관한 조건이다.\n")
    w("| 배치 | 구간 | 환류 + 유출 V(kg/h) | 탑 온도(℃) | 지금 식의 포화압(torr) | 음속 한계(torr) | 한계 ÷ 포화압 |\n|---|---|---|---|---|---|---|")
    for p in pts: w(f"| 26#{p['b']} | {p['ph']} | {_f(p['V'], 2)} | {p['Tt']} | {_f(p['P0t'], 3)} | {_f(p['Pson'], 3)} | {_f(p['sonRatio'], 2)} |")
    w(f"\n12점 모두 음속 한계가 지금 식의 포화압보다 {_r(OUT['sonRatio'], 1)}배 높다. 탑 온도계가 그 자리의 포화 온도를 읽는다면 A는 적어도 {jo(_f(A_son, 2), '이어야', '여야')} 한다.\n")

    w("## 4. 증발량과 내부 온도의 관계\n")
    w("| 배치 | 구간 | 환류(kg/h) | 유출 지시값(kg/h) | 무게 ÷ 적분 | V(kg/h) | 내부 온도(℃) | 지금 식의 증기압(torr) | V ÷ 증기압 |\n|---|---|---|---|---|---|---|---|---|")
    for p in pts: w(f"| 26#{p['b']} | {p['ph']} | {p['R']} | {p['D']} | {p['k']:.2f} | {_f(p['V'], 2)} | {p['T']} | {_f(p['P0'], 3)} | {_f(p['VP'])} |")
    w(f"\n- V ÷ 증기압은 {_f(OUT['VPmean'])} ± {jo(_f(OUT['VPsd']), '이고', '고')} 변동은 {OUT['VPsd'] / OUT['VPmean'] * 100:.0f} %다. V는 {_r(OUT['Vrng'], 2)} kg/h로 {OUT['Vrng'][1] / OUT['Vrng'][0]:.2f}배 범위다. 증발량이 정제기 압력에 비례한다는 뜻이고, 출구가 초킹인 관의 성질이다. 26#RE31의 유출은 무게 ÷ 적분 값이 없어 다섯 배치의 평균 {kmean:.2f}로 보정했다.")
    w(f"- 이 관계에서 내부 온도가 정해지면 증발량이 정해진다: 95 ℃ {_f(OUT['V_at']['T95'])} · 98 ℃ {_f(OUT['V_at']['T98'])} · 101 ℃ {_f(OUT['V_at']['T101'])} kg/h. 현장이 내부 온도 제어로 운전하면 온도 설정이 증발량을 정한다.")
    w(f"- 12점으로 기울기를 다시 구하면 B = {_f(Bfit, 0)} ± {_f(Bse, 0)}(표준오차)다. 지금 값 {_f(B0, 0)}은 표준오차의 {abs(B0 - Bfit) / Bse:.1f}배 거리에 있다. 내부 온도 범위가 {_r(OUT['Trng'])} ℃로 좁아 기울기는 이 자료로 정해지지 않는다. B는 그대로 둔다.\n")

    w("## 5. 증기압식 상수 A\n")
    w("증기 배관 식(시뮬레이터의 `lineTop`: 출구 초킹 마하 0.95 + 등온 압축성 마찰 + 가속 항)에 DB의 V와 내부 온도를 넣어 컬럼 상부 압력을 구하고, 충전층 압력 손실을 더한 정제기 압력이 내부 온도의 포화압이 되도록 A를 정했다. 충전층 손실의 비례 상수는 시뮬레이터 30 h 기록에서 가져왔다.\n")
    w("| 계산 조건 | A | 지금 값과의 차 |\n|---|---|---|")
    w(f"| 배관 유량 = 환류 + 유출, 상당 길이 {_f(Leq, 2)} m(직관 {_f(Leq - Lfit, 1)} m + 이음쇠) | {A_phys:.3f} ± {A_sd:.3f}(12점의 표준편차) | +{A_phys - A0:.2f} |")
    w(f"| 본류 6점만 | {A_main:.3f} | +{A_main - A0:.2f} |")
    w(f"| 상당 길이를 절반으로 | {A_half:.3f} | +{A_half - A0:.2f} |")
    w(f"| 상당 길이를 1.5배로 | {A_x15:.3f} | +{A_x15 - A0:.2f} |")
    w(f"| 마찰을 0으로(출구 초킹 + 충전층만. 하한) | {A_min:.3f} | +{A_min - A0:.2f} |")
    w(f"| 시뮬레이터에 넣어 본류의 (V, 내부 온도)가 DB 관계 위에 오는 값 | {A_cal:.3f} → **{A_use:.2f}** | +{A_use - A0:.2f} |")
    w("")
    w(f"- 문서와 시험 계산은 마지막 줄의 {jo(f'{A_use:.2f}', '을', '를')} 쓴다. 시뮬레이터는 과냉 환류가 컬럼 안에서 응축시키는 양(환류의 {sub_new * 100:.0f} %)까지 증기 배관 유량에 넣어 계산하므로, 실제로 돌려서 본류 구간의 (V, 내부 온도)가 4절의 관계 위에 오는 값을 골랐다. 시험 계산의 본류 내부 온도 {_f(t['Tmain'], 2)} ℃는 같은 V의 DB 관계 {_f(OUT['T_at_trialV'], 2)} ℃와 {abs(gap):.2f} ℃ 차이다.")
    w(f"- DB가 정하는 것은 '증기압 ÷ 배관 저항'의 묶음이다. 증기 배관의 상당 길이(직관 {_f(Leq - Lfit, 1)} m는 현장 치수, 직진 티 1개는 검토서 값)를 ±50 % 달리 보면 A는 {_s(OUT['dA_half'])} ~ {_s(OUT['dA_x15'])} 움직인다. 마찰을 0으로 두어도 본류 정제기 압력은 {_r(OUT['Pstill0_main'], 2)} torr로, 지금 식의 포화압 {_r(OUT['P0_main'], 2)} torr보다 높다.")
    w(f"- A {A_use:.2f}일 때 본류 6배치의 정제기 압력은 {_r(OUT['Pstill_main'], 2)} torr, 컬럼 상부 {_r(OUT['Ptop_main'], 2)} torr, 배관 출구 {_r(OUT['Pexit_main'], 2)} torr다(시뮬레이터 계산 방식).\n")

    w("## 6. 내부 온도 − 탑 온도와 탑 온도계 자리\n")
    w(f"- 온도 차를 압력비로 바꾸면(기울기 B만 쓰고 A와 무관하다) 본류 {_r(OUT['pr_main'], 2)}(평균 {_f(OUT['pr_main_mean'], 2)}), 초류 {_r(OUT['pr_fore'], 2)}(평균 {_f(OUT['pr_fore_mean'], 2)}) 수준이다. 본류는 배치와 유량이 달라도 거의 같다. 압력 차가 아니라 압력비가 일정한 것은 초킹인 관의 성질이다.")
    w(f"- 시뮬레이터 {VER}의 압력비는 정제기 ÷ 배관 출구 {_f(sim_pr_exit, 2)}, 정제기 ÷ 컬럼 상부 {jo(_f(sim_pr_top, 2), '이다', '다')}. DB의 값은 배관 출구 쪽에 가깝다.")
    w(f"- A {A_use:.2f}로 탑 온도를 압력으로 바꾸면 {_r(OUT['TE_P'], 2)} torr로, 배관 출구 압력의 {_r(OUT['TE_rel'], 2)}배다. 관 식으로는 출구에서 상당 길이 {_r(OUT['TE_Lst'], 2)} m 앞이다. 배관 출구의 포화 온도는 {_r(OUT['TE_Tex'])} ℃, 컬럼 상부는 {_r(OUT['TE_Ttop'])} ℃다.")
    w("- 초류의 압력비가 더 큰 것은 탑 쪽 증기에 가벼운 성분이 많아 같은 압력에서 온도가 더 낮기 때문으로 보인다.")
    w("- TE-H075의 실제 자리는 확인하지 못했다. 위 내용은 DB의 온도 차가 어느 자리의 압력과 맞는지만 말한다.\n")

    w("## 7. 문헌 증기압\n")
    w(f"| 출처 | 온도 · 증기압 | 지금 식(A {A0}) | A {A_use:.2f} |\n|---|---|---|---|")
    for l in LIT: w(f"| {l['src']} — {l['note']} | {l['T']:.0f} ℃ · {l['P']:.2f} torr | {l['P_old']:.3f} torr | {l['P_new']:.3f} torr |")
    w(f"\n- 60 ℃의 문헌값 두 개는 지금 식보다 {LIT[0]['r_old']:.0f}~{LIT[1]['r_old']:.0f}배 높다. 지금 식이 낮다는 방향은 이 계산과 같다. A {A_use:.2f}의 식으로도 60 ℃에서는 문헌값이 {LIT[0]['r_new']:.1f}~{LIT[1]['r_new']:.1f}배 높다.")
    w(f"- 60 ℃의 문헌값과 100 ℃의 증기압 {_f(OUT['P100_new'], 2)} torr(이 계산)를 함께 지나는 기울기는 B ≈ {jo(_f(B_lit, 0), '이다', '다')}(증발열 {_f(OUT['lam_lit'], 0)} J/g, 지금 {_f(OUT['lam0'], 0)} J/g). 4절의 {_f(Bfit, 0)} ± {jo(_f(Bse, 0), '과', '와')} 함께 보면 기울기가 지금 값보다 작을 수 있다. 운전 온도(95~101 ℃)의 증기압은 기울기와 무관하게 정해지지만, 비등 시작 온도와 증발열은 기울기에 달려 있다.")
    w("- 문헌값은 이론 · 문서에 해당하므로 추론으로 다룬다. 기울기는 8절의 시계열 값으로 정한다.\n")

    w("## 8. 사내망에 요청할 값(시계열에서 읽는 것)\n")
    w("| 읽을 값 | 쓰임 |\n|---|---|")
    w("| 비등 개시 온도: 비등이 시작되는 시점의 TICH071(TIH075가 오르기 시작하거나 FICH073이 0에서 올라오는 때), 6배치 | 낮은 압력 쪽의 한 점이 되어 기울기 B가 정해진다(그때의 압력 = 진공 설정 + 액 깊이의 정수두) |")
    w("| 승온 구간의 TICH071 · TIH074(10분 간격 그대로) | 맞춤 안내 6번: dT/dt를 (자켓 − 내부), (내부 − 외기)에 회귀해 U·A ÷ 열용량을 구한다 |")
    w("| 스팀을 끊은 뒤 2시간의 TICH071 | 맞춤 안내 7번: 열손실 ÷ 열용량 |")
    w("| TICH071_MV · FIH071이 추출 태그에 있는지, 있으면 구간 평균 | 스팀 밸브 특성식 |")
    w("| 전환류를 시작할 때 WIH071이 줄어든 양(온도 보정 0.3 kg/℃를 뺀 뒤) | 충전층 홀드업 + 관에 머무는 액 |")
    w("| TE-H075가 증기 배관의 어디에 달려 있는지(P&ID · 현장) | 탑 온도를 읽는 자리 |\n")

    w("## 9. DB 분석 문서 4절과 해석이 다른 곳\n")
    w("DB 분석 문서의 측정값과 목표값은 그대로 쓴다. 다른 것은 온도를 압력으로 바꾼 값(4-1 · 4-2)이다. 그 값은 지금 증기압식으로 역산한 것이라 식이 낮으면 함께 낮아진다.\n")
    w("| DB 분석 문서 | 이 계산 | 근거 |\n|---|---|---|")
    w(f"| 4-1 본류 탑 압력 {_r(rng(DOC['탑_torr']), 3)} torr | 탑 온도계 자리 {_r(OUT['TE_P'], 2)} torr | 같은 유량이 80A 배관을 지나는 최소 압력이 {_r(OUT['Pson_main'], 2)} torr다(3절) |")
    w("| 4-1 '0.01 torr였다면 탑은 약 58 ℃' → 진공도는 0.1 torr | 탑 온도로는 응축기 쪽 진공도를 가릴 수 없다 | 관 출구가 초킹이면 그 뒤쪽 압력은 앞쪽 온도에 영향을 주지 않는다. `P` 0.1 torr는 그대로 둔다(바꿀 근거가 없다) |")
    w(f"| 4-2 본류 정제기 포화압 {_r(DOC['정제기_포화압_torr'], 2)} torr, 액면 → 탑 압력 차 최대 {_r(DOC['압력차_최대_torr'], 2)} torr | 정제기 {_r(OUT['Pstill_main'], 2)} torr, 정제기 − 배관 출구 {_f(OUT['Pstill_main'][0] - OUT['Pexit_main'][0], 2)}~{_f(OUT['Pstill_main'][1] - OUT['Pexit_main'][1], 2)} torr | 마찰을 0으로 두어도 정제기 압력은 {_r(OUT['Pstill0_main'], 2)} torr다(5절) |")
    w(f"| 4-4 본류 열 부하 약 0.65 kW | 같다(시험 계산의 전달 열량 {_f(t['Q30'] / 1000, 2)} kW, 열손실 포함) | 증발열은 기울기 B에서 나오고 B는 그대로다 |\n")

    w("## 10. 시뮬레이터 반영안(판단 대기)\n")
    w("| 항목 | 지금 | 반영안 | 근거 · 남는 가정 |\n|---|---|---|---|")
    w(f"| 증기압식 상수 A | {A0} | {A_use:.2f}(B 그대로) | DB 12점 + 80A 배관 식. 배관 상당 길이는 가정값이다. 점검 I2의 기준과 회귀 기준을 함께 바꾼다 |")
    w(f"| 탑 온도 TIH075를 읽는 자리 | 컬럼 상부(증기 배관 입구) | 증기 배관 출구 쪽(입력칸에 '가정' 표시) | DB의 내부 − 탑 온도 차. 실제 자리는 미확인이다. 출구 압력 그대로 읽으면 {_f(t['Tex30'])} ℃로 DB 평균 {_f(DBM['ThMain'])} ℃보다 {_f(DBM['ThMain'] - t['Tex30'])} ℃ 낮다 |")
    w(f"| 스팀 조절 | 응축량(환류 + 유출 설정)에 맞추는 PI | 내부 온도 제어(TIC)를 고를 수 있게 한다. 설정은 초류 약 {_f(DBM['Tfore'], 0)} ℃ · 본류 약 {_f(DBM['Tmain'], 0)} ℃(DB 평균) | DB: 내부 온도가 {_r(G['내부온도_제어'], 0)} ℃에서 유지된다. 조절기 이득과 배치별 설정값은 기록이 없다 |")
    w(f"| 레시피 기본값 | 환류 4, 유출 2 → 6 → 5 kg/h, 투입 350 · 초류 30 · 후류 30 kg | 그대로(사용자 운전 기준) | DB: 초류 환류 {_r(R['Rfore'])} · 본류 유출 지시값 {_r(R['Dmain'])} kg/h, 투입 {_r(R['feed'], 0)} · 초류 {_r(R['fore'])} · 남은 양 {_r(R['left'], 0)} kg |")
    w("| 점검 항목 | 없음 | DB 분석 문서 4-6의 여덟 가지 판정을 점검기에 더한다 | 판정 기준은 DB 범위 |")
    w("| 스팀 밸브 특성식 · 금속 열용량 | 가정값 · 없음 | 승온 구간의 시계열 회귀 결과를 받은 뒤 | 8절 |\n")
    return "\n".join(L) + "\n"


def guide_block():
    """현장_데이터_맞춤_안내.md의 10절(표시 사이)을 다시 쓴다."""
    assert TB and TN; b, t = TB, TN; R = DBR; S = SIM
    L = []; w = L.append
    w("## 10. DB 6배치 분석 결과 (2026-11-20)\n")
    w(f"사내망에서 2차정제 6배치({DBV['기간']})의 시계열을 구간별로 평균한 표를 받았다. 계산과 표는 `현장값_DB_맞춤_계산.md`(만드는 것 `발표자료/DB_맞춤.py`), 배치 표는 `발표자료/DB값.json`에 있다. 이 절의 숫자는 그 스크립트가 쓴다.\n")
    w("| 4절 단계 | 6배치 요약값으로 한 것 | 결과 |\n|---|---|---|")
    w("| 2) 두 압력계의 영점 차 · 5) 리크 | 못 함 | PICH071은 배치마다 단위와 스케일이 다르고 PIH093은 −1로 붙어 있다 |")
    w(f"| 3) 증기압 곡선 | 압력 기록 대신 4)의 음속 한계와 증기 배관 식으로 절대값만 정함 | A = {A_use:.2f}(지금 {A0}). 기울기 B는 12점으로 {_f(Bfit, 0)} ± {jo(_f(Bse, 0), '이라', '라')} 정해지지 않아 그대로 둔다 |")
    w(f"| 4) 탑 온도로 증기관 확인 | 12점 모두 | 음속 한계가 지금 식으로 구한 탑 압력보다 {_r(OUT['sonRatio'], 1)}배 높다. V ÷ 증기압 = {_f(OUT['VPmean'])} ± {jo(_f(OUT['VPsd']), '으로', '로')} 일정하다(초킹) |")
    w(f"| 6) 전열 ÷ 열용량 | 어림만 | 승온 기울기 {_r(DBV['범위']['승온_기울기'])} ℃/분, 자켓 최고 {_r(DBV['범위']['자켓_승온_최고'], 0)} ℃. 회귀는 시계열로 사내망에서 한다 |")
    w(f"| 10) 컬럼 압력 손실 | 온도 차를 압력비로 | 본류 {_r(OUT['pr_main'], 2)}. 컬럼만의 손실(계산 {_f(sim_pr_top, 2)})이 아니라 증기 배관 출구까지의 비({_f(sim_pr_exit, 2)})에 가깝다. 탑 온도계가 배관 출구 쪽에 있는 것으로 보인다 |")
    w("| 7) · 8) · 9) · 11) · 12) · 13) | 못 함 | 요약 표에 값이 없다(냉각 구간, 스팀 개도 · 유량, 무게 변화, 성분 분석) |\n")
    w(f"- {jo('계산 ' + VER, '과', '와')} DB의 차이: 본류 내부 {_f(S['Tmain'])} ℃(DB {_r(R['Tmain'])}), 탑 {_f(S['ThMain'])} ℃(DB {_r(R['ThMain'])}), 자켓 {_f(b['TjMain'])} ℃(DB {_r(R['TjMain'])}). 증발량과 구간 길이는 DB 범위 안이다.")
    w(f"- 시험 계산(A만 {A_use:.2f}로 바꿈, 시뮬레이터 파일은 그대로): 본류 내부 {_f(t['Tmain'])} ℃ · 컬럼 상부 {_f(t['ThMain'])} ℃ · 증기 배관 출구의 포화 온도 {_f(t['Tex30'])} ℃ · 자켓 {_f(t['TjMain'])} ℃ · 정제기 {_f(t['Pstill30'], 2)} torr · 2차 응축기 유입 {t['m2_30']:.4f} kg/h(DB {R['m2'][0]}~{R['m2'][1]}).")
    w("- 스팀 조절: DB에서 내부 온도가 일정하게 유지된다(내부 온도 제어). 8절의 '스팀 조절 방식' 줄이 이것으로 정해졌다.")
    w("- DB 분석 문서 4-1 · 4-2의 압력(탑 0.11~0.135 torr, 압력 차 0.2~0.25 torr)은 지금 증기압식으로 역산한 값이라 위 결과와 다르다. 측정값과 목표값은 그대로 쓴다(`현장값_DB_맞춤_계산.md` 9절).")
    w("- 시뮬레이터 기본값은 바꾸지 않았다. 반영안은 `현장값_DB_맞춤_계산.md` 10절에 있고 사용자 판단을 기다린다.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    print(f"DB 12점: V {_r(OUT['Vrng'], 2)} kg/h · 내부 {_r(OUT['Trng'])} ℃ · V÷증기압(지금 식) {_f(OUT['VPmean'])} ± {_f(OUT['VPsd'])} · 기울기 B(DB) {Bfit:.0f} ± {Bse:.0f}(지금 {B0:.0f})")
    print(f"음속 한계 ÷ 지금 식의 탑 압력 {_r(OUT['sonRatio'], 2)}배 · A: 배관 식 {A_phys:.3f} ± {A_sd:.3f} · 길이 ½ {A_half:.3f} · 1.5배 {A_x15:.3f} · 마찰 0 {A_min:.3f} · 음속 한계만 {A_son:.3f}")
    print(f"시험 계산으로 확인한 값 {A_cal:.3f}({', '.join(f'{a:.3f}' for a in _cal) or '시험 계산 없음'}) → 문서가 쓰는 값 {A_use:.2f} · 100 ℃ 증기압 {OUT['P100_old']:.3f} → {OUT['P100_new']:.3f} torr({OUT['ratio100']:.2f}배)")
    print(f"압력비 본류 {_r(OUT['pr_main'], 2)} · 초류 평균 {_f(OUT['pr_fore_mean'], 2)} · 시뮬레이터 정제기÷출구 {_f(sim_pr_exit, 2)} · 정제기÷컬럼 상부 {_f(sim_pr_top, 2)} · 탑 온도계 자리 ÷ 출구 {_r(OUT['TE_rel'], 2)}")
    if TB and TN:
        (HERE.parent / "현장값_DB_맞춤_계산.md").write_text(report(), encoding="utf-8", newline="\n"); print("현장값_DB_맞춤_계산.md")
        g = HERE.parent / "현장_데이터_맞춤_안내.md"; a, z = "<!-- DB 6배치: DB_맞춤.py가 쓴다 -->", "<!-- DB 6배치 끝 -->"
        if g.exists() and a in g.read_text(encoding="utf-8"):
            s = g.read_text(encoding="utf-8"); i, j = s.index(a), s.index(z)
            g.write_text(s[:i] + a + "\n" + guide_block() + s[j:], encoding="utf-8", newline="\n"); print("현장_데이터_맞춤_안내.md 10절")
    else:
        print(f"시험 계산에 A = {A_use:.2f} 기록이 없다 — python 시험계산.py {A_use:.2f} --add")
