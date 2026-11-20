# -*- coding: utf-8 -*-
"""정제 시뮬레이터 발표자료 만들기

실행:  python 만들기.py [점검 결과 이름]        예: python 만들기.py v127_최종
- 읽는 것: 값.json(시뮬레이터 v126에서 뽑은 계산 값, 다섯 시점) · ../점검/점검결과_<이름>.json(이상 상황 12가지 기록, 배치 끝 기록)
- 내는 것: ../정제_시뮬레이터_발표자료.html(파일 하나로 열림) · 발표자료_아티팩트.html(앞머리 없는 조각)
- 숫자는 손으로 옮겨 적지 않는다. 그림과 글의 값은 모두 위 두 기록에서 읽는다.
"""
import io, json, math, pathlib, sys, html

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "점검"))
import 그림 as G, 내용, 장면, 틀
from 그림 import esc, eq_html
from 내용 import N

tag = sys.argv[1] if len(sys.argv) > 1 else "v127_최종"
_ck = HERE.parent / "점검" / f"점검결과_{tag}.json"
if not _ck.exists(): _ck = HERE / f"점검결과_{tag}.json"      # 깃 저장소(distill-sim)에서는 발표자료/ 안의 사본을 읽는다(점검/점검결과*는 저장소에 올리지 않는다)
CHK = json.loads(_ck.read_text(encoding="utf-8"))
VAL = json.loads((HERE / "값.json").read_text(encoding="utf-8"))
RAW = CHK["raw"]; VER = CHK.get("ver") or "v127"

# ---------------------------------------------------------------- 값 모으기
S30 = VAL["snap"]["30"]; P30 = S30["PR"]; C = S30["CUR"]
A_, B_ = C["antB"]["A"], C["antB"]["B"]
tsat = lambda P: B_ / (A_ - math.log10(P)) - 273.15
END = dict(RAW["합침 배치 끝"]["res"]["end"])
st = {s[0]: s[1] for s in END["stages"]}
xs = END["xS"]; wS = xs * END["MWA"] / (xs * END["MWA"] + (1 - xs) * END["MWB"]) * 100
END.update(st2=st[2], fore_h=st[4] - st[3], main_h=END["t"] - st[4], w0=END["wA0"], wF=END["foreA"] / END["fore"] * 100, wM=END["mainA"] / END["main"] * 100, wS=wS)
END["Eeff"] = 1 + math.log(wS / END["w0"]) / math.log(END["m"] / END["m0"])
import 점검_공식 as F
AB = {k: [RAW["이상 상황 " + nm]["res"][f"ab_{k}_{i}"] for i in (0, 1, 2)] for k, nm, _ in F.AB_CASES}
ABNAME = {k: nm for k, nm, _ in F.AB_CASES}
torr_cm = S30["mix"]["rho"] * 9.80665 * 0.01 / 133.322
# 시뮬레이터 안쪽 함수는 바깥에서 부를 수 없어, 교반 전열과 관 마찰은 같은 식으로 여기서 따로 계산한다(입력은 뽑은 값)
mix = S30["mix"]; Re_ag = mix["rho"] * C["N"] * C["D"] ** 2 / mix["mu"]; Pr_ag = mix["cp"] * mix["mu"] / C["kL"]
hAg = 0.36 * Re_ag ** (2 / 3) * Pr_ag ** (1 / 3) * C["kL"] / C["T"]                       # 앵커: Nu = 0.36·Re^(2/3)·Pr^(1/3)
nu_ = mix["mu"] / mix["rho"]; hNc = 0.13 * (9.81 * 1e-3 * 10 / nu_ ** 2 * Pr_ag) ** (1 / 3) * C["kL"]   # 자연대류 몫(세제곱 합)
hi_ = (hAg ** 3 + hNc ** 3) ** (1 / 3); U_ = 1 / (1 / hi_ + C["Rwall"] + 1 / 8000 + 0.0002)
def churchill(Re, rr):
    a = (2.457 * math.log(1 / ((7 / Re) ** 0.9 + 0.27 * rr))) ** 16; b = (37530 / Re) ** 16
    return 8 * ((8 / Re) ** 12 + (a + b) ** -1.5) ** (1 / 12)
EXTRA = dict(Re=Re_ag, hAg=hAg, U=U_, rpm=C["N"] * 60, torr_cm=torr_cm, dT_1cm=tsat(P30["Pstill"] + torr_cm) - tsat(P30["Pstill"]),
             hvap_mol=8.314462 * B_ * math.log(10) / 1000, Trf=END["T1main"], mHold=P30["mHold"], Leq=C["Lpipe"], Lstr=C["Lpipe"] - C["Lfit"], asound=P30["aSon"], Re_pipe=P30["RePipe"],
             f_pipe=churchill(P30["RePipe"], 4.6e-5 / C["Dpipe"]), lost_gh=(P30["lostkg"] or 0) * 1000, m2_gh=(P30["m2kg"] or 0) * 1000, hi=hi_, vpass=P30["vdot"] - P30["backKg"], dPack=(P30["Pstill"] ** 2 - P30["Ptop"] ** 2) / (2 * P30["Pstill"]),
             Vpack_L=math.pi * C["Dcol"] ** 2 / 4 * C["Hpack"] * 1000, subTop=min(0.5, mix["cp"] * (P30["Thead"] - END["T1main"]) / P30["lam"]),
             lost_txt=("0.01 g/h 미만" if (P30["lostkg"] or 0) * 1000 < 0.01 else f'{(P30["lostkg"] or 0) * 1000:.2f} g/h'), tau_min=P30["tauP"] / 60, pstopP=AB["pstop"][1]["Ppump"], plant_T=101.5)
assert abs(EXTRA["vpass"] - P30["Qc"] / P30["lam"] * 3600) < 0.02, "꼭대기를 넘는 증기: 증발 − 컬럼 안 응축 = 응축 부하 ÷ 증발열이어야 한다"
assert abs(C["hold"] * EXTRA["Vpack_L"] / 1000 * mix["rho"] - P30["mHold"]) < 0.01, "충전층 홀드업 = 6 % × 충전층 부피 × 밀도"
D = dict(snap=VAL["snap"], end=END, extra=EXTRA, ab=AB, chk=CHK["R"])
NODES = 내용.build(D)

# ---------------------------------------------------------------- 조각
BD = {"est": ("b-est", "가정"), "hard": ("b-hard", "추정"), "db": ("b-db", "DB"), "dwg": ("b-dwg", "도면")}
def bdg(k): c, t = BD[k]; return f'<span class="bdg {c}">{t}</span>'

def fcard(i, f):
    eqs = [f["eq"]] if isinstance(f["eq"], str) else f["eq"]
    return (f'<div class="fcard" data-f="{f["k"]}"><div class="fh"><span class="n">{i}</span><b>{esc(f["name"])}</b><span class="law">{esc(f.get("law", ""))}</span><span class="cls">{esc(f["cls"])}</span>' + "".join(bdg(b) for b in f.get("badges", ())) + "</div>"
            + "".join(f'<div class="eqline">{eq_html(e)}</div>' for e in eqs)
            + f'<div class="words">{esc(f["words"])}</div><div class="gets"><b>산출값</b>{esc(f["gets"])}</div>'
            + (f'<div class="val"><b>계산값</b>{esc(f["val"])}</div>' if f.get("val") else "") + f'<div class="why">{esc(f["why"])}</div></div>')

def node_scene(nd):
    fig = 장면.FIGS[nd["n"]](nd, D)
    cards = "".join(fcard(i + 1, f) for i, f in enumerate(nd["formulas"]))
    al = "".join(f'<li><span class="w"><span class="lt">{"abcdefgh"[i]}</span>{bdg(a["kind"])} {esc(a["what"])}</span><span class="y">근거: {esc(a["why"])}</span><span class="e">영향: {esc(a["effect"])}</span></li>' for i, a in enumerate(nd["assume"]))
    dl = "".join(f'<li><span class="tg">{esc(d["tags"])}</span><span>{eq_html(d["eq"])}</span><span class="g">{esc(d["gets"])}</span></li>' for d in nd["db"])
    return (f'<section class="scene" id="{nd["id"]}" data-tab="nd" hidden><div class="sh"><span class="num">{nd["n"]}</span><h2>{esc(nd["name"])}</h2><span class="verb">{esc(nd["verb"])}</span><span class="tag">{esc(nd["tag"])}</span></div>'
            f'<p class="q">{esc(nd["q"])}</p><figure><div class="scroll">{fig}</div>{KEY2}<figcaption>{esc(nd["say"])}</figcaption></figure>'
            f'<div class="cols"><div class="blk"><h3>적용 공식과 용도 <small>번호는 그림과 동일</small></h3>{cards}</div>'
            f'<div class="blk"><h3>가정 · 추정 사항 <small>기호는 그림의 표식과 동일</small></h3><ul class="alist">{al}</ul></div>'
            f'<div class="blk"><h3>DB 데이터 확보 시 개선 사항 {bdg("db")}</h3><ul class="dlist">{dl}</ul></div></div></section>')

KEY = ('<div class="key"><span><i class="k-heat"></i>스팀 · 열</span><span><i class="k-vap"></i>증기</span><span><i class="k-liq"></i>액</span><span><i class="k-brine"></i>냉매</span><span><i class="k-vac"></i>진공 · 공기</span>'
       f'<span>{bdg("est")} 도면·운전 데이터로 정할 수 있는 값</span><span>{bdg("hard")} 데이터를 확보해도 정하기 어려운 값</span></div>')

KEY2 = ('<div class="key"><span><span class="nk">1</span>공식 번호</span>' f'<span>{bdg("est")}{bdg("hard")} 가정 · 추정(기호는 아래 목록 참조)</span>'
        '<span><span class="tgk">TICH071</span>DB 수집 계기(PIMS 태그)</span><span><i class="k-heat"></i>스팀 · 열</span><span><i class="k-vap"></i>증기</span><span><i class="k-liq"></i>액</span><span><i class="k-brine"></i>냉매</span><span><i class="k-vac"></i>진공 · 공기</span></div>')

def overview():
    nfor = sum(len(n["formulas"]) for n in NODES); nas = sum(len(n["assume"]) for n in NODES)
    nest = sum(1 for n in NODES for a in n["assume"] if a["kind"] == "est"); nhard = nas - nest
    cards = "".join(f'<button class="ncard" data-go="{n["id"]}"><span class="h"><i>{n["n"]}</i>{esc(n["name"])}<span>{esc(n["verb"])}</span></span><span class="fl">{esc(n["q"])}</span>'
                    f'<span class="cnt">공식 {len(n["formulas"])} · 가정·추정 {len(n["assume"])} · DB 항목 {len(n["db"])}</span></button>' for n in NODES)
    chain = "".join(f"<li><span>{esc(a)} <em>→</em> {esc(b)}<u>{k}</u></span></li>" for a, b, k in 내용.CHAIN)
    gl = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in 내용.GLOSS)
    ftab = "".join(f'<tr><td>{n["n"]} {esc(n["name"])}</td><td>{esc(f["name"])}</td><td>{esc(f["law"])}</td><td>{esc(f["cls"])}</td></tr>' for n in NODES for f in n["formulas"])
    return (f'<section class="scene" id="ov" data-tab="ov"><div class="sh"><h2>공정 구성과 공식 적용 위치</h2><span class="tag">CpHf 2차 정제 · 투입 {N(END["m0"], 0)} kg · {esc(VER)}</span></div>'
            '<p class="say">정제는 혼합액을 가열해 증발시키고, 그 증기를 다시 응축해 회수하는 공정이다. 시뮬레이터는 설비를 8개 구간으로 나누어 열, 증기, 액의 이동량을 공식으로 계산한다. 각 공식이 하나의 값을 산출하고, 그 값이 다음 구간 공식의 입력이 된다.</p>'
            f'<figure><div class="scroll">{장면.fig_overview(NODES)}</div>{KEY}<figcaption>번호는 구간이고, 옆의 목록은 해당 위치에 적용한 공식이다(총 {nfor}개). 번호나 아래 카드를 누르면 구간별 상세 화면으로 이동한다.</figcaption></figure>'
            f'<div class="ncards">{cards}</div>'
            f'<div class="blk"><h3>적용 공식 일람 <small>공식 · 통용 명칭 · 구분</small></h3><div class="tw"><table><tr><th>구간</th><th>공식</th><th>통용 명칭</th><th>구분</th></tr>{ftab}</table></div></div>'
            f'<div class="grid2"><div class="blk"><h3>계산 흐름 <small>오른쪽 번호는 해당 구간</small></h3><ol class="chain">{chain}</ol>'
            '<p class="small">압력과 끓는점은 서로 영향을 주고받는다. 증발량이 늘면 압력이 오르고, 압력이 오르면 끓는점이 높아져 증발량이 줄어든다. 시뮬레이터는 계산 단계마다 두 조건을 함께 만족하는 증발량을 구한다.</p></div>'
            f'<div class="blk"><h3>용어 설명</h3><div class="tw"><table>{gl}</table></div>'
            f'<p class="small">구간 그림에 표시한 가정 · 추정 항목은 총 {nas}건이다. 그중 {bdg("est")}(도면이나 운전 데이터로 정할 수 있는 값)이 {nest}건, {bdg("hard")}(데이터를 확보해도 정하기 어려운 값)이 {nhard}건이다. 식은 이론식(교과서의 식 · 정의)과 경험식(실험 상관식)으로 구분하고, 그 밖의 항목은 제어식 · 운전 기준 · 입력값 · 해석식(계산 결과를 해석하는 식)으로 표시했다.</p></div></div></section>')

def page(parts, standalone):
    nodes_bar = '<div class="nodes" hidden>' + "".join(f'<button data-go="{n["id"]}"><i>{n["n"]}</i>{esc(n["name"])}</button>' for n in NODES) + "</div>"
    top = ('<header class="top"><div class="brand"><b>정제 시뮬레이터 적용 공식 해설</b><span>' + esc(VER) + ' · CpHf 2차 정제 · 수치는 시뮬레이터 계산값</span></div>'
           '<nav class="tabs" role="tablist"><button role="tab" data-tab="ov">전체 구성</button><button role="tab" data-tab="nd">구간별 공식</button><button role="tab" data-tab="ab">이상 상황</button><button role="tab" data-tab="db">DB 데이터 활용</button></nav>'
           '<div class="pager"><button id="prev" aria-label="이전 장면">←</button><span id="pg">1</span><button id="next" aria-label="다음 장면">→</button></div></header>')
    main = "".join(parts).replace('<figure><div class="scroll">', '<figure><div class="swipe">그림은 좌우로 스크롤</div><div class="scroll">')
    body = f'<div class="app">{top}{nodes_bar}<main>{main}</main></div>'
    head = '<title>정제 시뮬레이터 발표자료</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n' + 틀.FONTS + "\n<style>" + 틀.CSS + "</style>\n"
    script = "<script>" + SCRIPT_DATA + 틀.JS + "</script>"
    if standalone:
        return ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n' + head + "</head>\n<body>\n" + body + "\n" + script + "\n</body>\n</html>\n")
    return head + body + "\n" + script + "\n"

SCRIPT_DATA = ""
PARTS = [overview()] + [node_scene(n) for n in NODES]
try:
    import 이상 as AB_MOD                      # 이상 상황 · DB 화면(따로 둔 파일)
    ab_html, ab_data = AB_MOD.scene_ab(D, NODES, ABNAME); PARTS.append(ab_html); PARTS.append(AB_MOD.scene_db(D, NODES))
    SCRIPT_DATA = "window.AB_DATA=" + json.dumps(ab_data, ensure_ascii=False) + ";\n"
except ModuleNotFoundError:
    pass
out1 = HERE.parent / "정제_시뮬레이터_발표자료.html"; out2 = HERE / "발표자료_아티팩트.html"
out1.write_text(page(PARTS, True), encoding="utf-8", newline="\n"); out2.write_text(page(PARTS, False), encoding="utf-8", newline="\n")
print("발표자료", out1.name, out1.stat().st_size, "바이트 · 장면", len(PARTS), "· 공식", sum(len(n["formulas"]) for n in NODES), "· 가정과 추정", sum(len(n["assume"]) for n in NODES), "· DB", sum(len(n["db"]) for n in NODES))
