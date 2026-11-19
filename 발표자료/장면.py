# -*- coding: utf-8 -*-
"""장면 그림 — 전체 구조와 구간 여덟 개. 설비 그림 옆에 공식 말풍선을 두고 화살표로 쓰이는 자리를 가리킨다.

배치 규칙
- 말풍선은 왼쪽·오른쪽 줄에 위 → 아래로 놓는다. 위아래 순서는 화살표가 닿는 자리의 위아래 순서와 같다(화살표가 서로 엇갈리지 않는다).
- 화살표는 꺾지 않은 곧은 선이다(관은 직각으로 꺾이므로 관과 헷갈리지 않는다). 말풍선 옆 변에서 닿는 자리와 가장 가까운 높이로 나간다.
- 그림 위 표식: 번호 = 공식, 노랑(가정)·자주(추정) 표식의 글자 = 그림 아래 '가정과 추정' 목록의 글자, 초록 이름표 = DB로 받는 계기(PIMS 태그).
"""
import math
from 그림 import *
from 설비도 import plant, GEO
from 내용 import N

LX, LW, RX, RW = 20, 300, 880, 300
LET = "abcdefgh"

def _f(nd, k):
    for i, f in enumerate(nd["formulas"]):
        if f["k"] == k: return i + 1, f
    raise KeyError(k)

def _hgt(nd, k, w):
    i, f = _f(nd, k)
    return callout("x", 0, 0, w, i, f["name"], f["eq"], f["gets"], f.get("val", ""), f.get("badges", ()), law=f.get("law", ""))[1]

def _one(fid, nd, k, x, y, w, tgt, side, kind="n", via=None, at=None):
    """공식 하나를 말풍선으로. at을 주지 않으면 닿는 자리와 가장 가까운 곳에서 화살표가 나간다."""
    i, f = _f(nd, k); h = _hgt(nd, k, w); ref = (via[0] if via else tgt)
    if at is None:
        if ref is None: at = 0.5
        elif side in ("L", "R"): at = (min(max(ref[1], y + 14), y + h - 14) - y) / h
        else: at = (min(max(ref[0], x + 16), x + w - 16) - x) / w
    return callout(fid, x, y, w, i, f["name"], f["eq"], f["gets"], f.get("val", ""), f.get("badges", ()), tgt, side, kind, via, key=f["k"], at=at, law=f.get("law", ""))[0]

def _col(fid, nd, specs, x, w, side, y0=22, y1=618, gap=12):
    """말풍선 한 줄(위 → 아래). specs = [(열쇠, 닿는 점, 색, 선택)] — 선택: y(위치 고정) · via · side · at
    상자 가운데를 화살표가 닿는 높이에 맞추고, 겹치면 순서를 지킨 채 위아래로 민다."""
    hs = [_hgt(nd, s[0], w) for s in specs]; tops = []
    for s, h in zip(specs, hs):
        o = s[3] if len(s) > 3 else {}
        tops.append(o["y"] if "y" in o else (s[1][1] - h / 2 if s[1] else y0))
    for i in range(len(tops)): tops[i] = max(tops[i], y0 if i == 0 else tops[i - 1] + hs[i - 1] + gap)
    for i in reversed(range(len(tops))): tops[i] = min(tops[i], (y1 - hs[i]) if i == len(tops) - 1 else tops[i + 1] - gap - hs[i])
    out = []
    for s, h, y in zip(specs, hs, tops):
        o = s[3] if len(s) > 3 else {}
        out.append(_one(fid, nd, s[0], x, y, w, s[1], o.get("side", side), s[2], o.get("via"), o.get("at")))
    return "".join(out)

def _am(nd, i, x, y, anchor="start", short=True, dy=19.0):
    """가정·추정 표식(글자는 그림 아래 목록과 같다)."""
    a = nd["assume"][i]
    return amark(x, y, a["kind"], LET[i], a.get("fig", "") if short else "", anchor, dy)

def _arrow(fid, x0, y0, x1, y1, kind="heat", cls="hx"):
    return f'<path class="{cls}" d="M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}" marker-end="url(#{fid}-a-{kind})"/>'

# ====================================================================== 전체 구조
def fig_overview(nodes):
    fid = "fig-ov"; g = GEO; o = [svg_open(fid, 1200, 690, "정제 설비의 전체 구성과 8개 구간에 적용한 공식 이름", y0=36)]
    o.append(plant(fid, level=0.57, main=0.35, fore=0.55))
    # 번호 자리(px, py) · 이름 목록 자리(tx, ty) · 화살표(번호 옆 → 설비의 그 자리)
    pos = {1: (32, 420, 22, 444, [(114, 428), (148, 510)]), 2: (378, 498, 396, 502, [(367, 503), (340, 514)]), 3: (112, 196, 130, 200, [(172, 196), (293, 196)]),
           4: (410, 108, 428, 112, [(410, 97), (410, 77)]), 5: (668, 214, 686, 218, [(657, 214), (641, 214)]), 6: (700, 306, 718, 310, [(689, 305), (614, 301)]),
           7: (996, 248, 1014, 252, [(989, 239), (973, 221)]), 8: (868, 520, 886, 524, [(858, 526), (822, 562)])}
    for nd in nodes:
        px_, py_, tx, ty, ld = pos[nd["n"]]
        o.append(leader(fid, ld, "n", of=f"n{nd['n']}"))
        o.append(pin(px_, py_, nd["n"], "pin link", extra=f' data-go="{nd["id"]}" role="link" tabindex="0" aria-label="{esc(nd["name"])} 구간으로 이동"'))
        if nd["n"] == 1:
            o.append(text(px_ + 17, py_ + 4.5, nd["verb"], "nlv", "start")); yy = ty
        else:
            o.append(text(tx, ty, nd["verb"], "nlv", "start")); yy = ty + 17
        for f in nd["formulas"]:
            o.append(text(tx, yy, f.get("short", f["name"]), "nl", "start")); yy += 14.5
    o.append("</svg>"); return "".join(o)

# ====================================================================== ① 자켓 · 스팀
def fig_n1(nd, D):
    fid = "fig-n1"; P30 = D["snap"]["30"]["PR"]; C = D["snap"]["30"]["CUR"]; X = D["extra"]
    o = [svg_open(fid, 1200, 640, "정제기 자켓 단면: 스팀 밸브에서 자켓 벽을 거쳐 액으로 열이 전달되는 경로와 적용 공식 6개")]
    cx, y0, w, h, hd = 600, 150, 300, 250, 75; yt = y0 + hd; yb = yt + h; r = w / 2; jt = yb - h * 0.575; lv = jt - 8
    sx = 384; yin = jt + 19                                                            # 스팀 관 · 자켓으로 들어가는 높이
    steam = [(sx, 26), (sx, yin), (cx - r - 14, yin)]
    o.append(pipe(steam, "steam") + flow(steam, "steam"))
    o.append(pipe([(cx, yb + hd + 14), (cx, 622), (474, 622)], "thin") + text(466, 626, "응축수(스팀 트랩)", "ts", "end"))
    o.append(insulation(cx, y0, w, h, hd, top=jt, gap=14, t=15, fid=fid))
    o.append(vessel(cx, y0, w, h, hd, level=lv) + jacket(cx, y0, w, h, hd, top=jt, gap=14) + agitator(cx, y0, w, h, hd))
    o.append(valve(sx, 100, False, "open", s=10))
    o.append(text(sx + 14, 42, f"LP 스팀 {N(C['Tj'], 0)} ℃", "ts", "start") + tagdb(sx + 14, 64, "FIH071", "start"))
    o.append(text(sx + 14, 96, "TCV-H071", "tk", "start") + tagdb(sx + 14, 117, "TICH071_MV", "start") + _am(nd, 0, sx + 14, 141))
    for yy, xa in ((425, cx - r - 12), (470, cx - r - 12), (515, cx - r + 5)):          # 자켓 → 액으로 넘어가는 열
        o.append(_arrow(fid, xa, yy, xa + 44, yy))
    for yy, xa in ((500, 779), (530, 758)):                                             # 보온재를 지나 새는 열
        o.append(_arrow(fid, xa, yy, xa + 34, yy, cls="hx hx-loss"))
    o.append(text(cx - 62, 372, f"액 {N(P30['Tmean'])} ℃", "tnum") + text(cx - 62, 389, f"{N(P30['m'], 0)} kg", "ts") + _am(nd, 2, cx - 95, 408))
    o.append(tagdb(cx + 12, 368, "TICH071", "start"))
    o.append(text(410, yin + 26, "자켓 내부", "ts", "end") + text(410, yin + 42, f"{N(P30['TjEff'])} ℃", "tm", "end") + tagdb(410, yin + 62, "TIH074", "end"))
    o.append(text(730, 172, "T-H071 정제기", "t", "start") + _am(nd, 3, 762, 236) + _am(nd, 4, 762, 284))
    o.append(text(cx + 22, 112, f"교반 {N(X['rpm'], 0)} rpm", "ts", "start") + tagdb(cx + 22, 131, "SICAH071", "start"))
    o.append(text(742, 566, f"보온 {N(C['tIns'], 0)} mm", "ts", "start") + _am(nd, 1, cx + 16, 600))
    o.append(_col(fid, nd, [("valve", (sx - 9, 100), "heat"), ("steamlam", (sx - 5, 230), "heat"), ("jacket", (cx - r - 17, 448), "heat")], LX, LW, "R"))
    o.append(_col(fid, nd, [("heatbal", (718, 372), "liq"), ("agit", (688, 466), "n"), ("loss", (819, 515), "heat")], RX, RW, "L"))
    o.append("</svg>"); return "".join(o)

# ====================================================================== ② 정제기 안
def fig_n2(nd, D):
    fid = "fig-n2"; P30 = D["snap"]["30"]["PR"]; C = D["snap"]["30"]["CUR"]; X = D["extra"]
    o = [svg_open(fid, 1200, 640, "정제기 내부: 액면에서 증발한 증기가 상승하고, 깊은 곳은 압력이 높아 끓지 못한다. 적용 공식 5개와 증기압 곡선")]
    cx, y0, w, h, hd = 590, 120, 340, 250, 85; yt = y0 + hd; yb = yt + h; r = w / 2; lv = yb - h * 0.56
    xn = cx + 96; ynz = yt - hd * math.sqrt(1 - (96 / r) ** 2)
    vap = [(xn, ynz + 3), (xn, 34)]
    o.append(pipe(vap, "vap") + flow(vap, "vap") + text(xn + 14, 46, "컬럼으로", "ts", "start"))
    o.append(vessel(cx, y0, w, h, hd, level=lv) + agitator(cx, y0, w, h, hd))
    for dx in (-70, 45, 120):                                                          # 액면에서 올라가는 증기
        o.append(f'<path class="pp pp-vap" stroke-width="2.2" d="M{cx + dx} {lv - 6:.1f}v-30" marker-end="url(#{fid}-a-vap)"/>')
    xr = cx - r + 14
    o.append(f'<path class="thin" d="M{xr} {lv:.1f}V{lv + 165:.1f}"/>' + "".join(f'<path class="thin" d="M{xr - 5} {lv + dep:.1f}h10"/>' for dep in (0, 40, 80, 120, 160)))
    o.append(text(xr + 14, lv + 16, "액면", "ts", "start") + text(xr + 14, lv + 78, "깊을수록", "ts", "start") + text(xr + 14, lv + 93, "압력 증가", "ts", "start"))
    o.append(text(428, 150, "T-H071 정제기", "t", "end") + _am(nd, 1, cx - r + 24, 236))
    o.append(text(cx + 14, 240, f"정제기 {N(P30['Pstill'], 2)} torr", "tnum", "start") + tagdb(cx + 14, 259, "PICH071", "start"))
    o.append(text(cx + 14, 352, f"액 {N(P30['Tmean'])} ℃", "tnum", "start") + tagdb(cx + 14, 371, "TICH071", "start") + _am(nd, 2, cx + 14, 396))
    o.append(text(cx - 8, 562, f"{N(P30['m'], 0)} kg", "tnum", "end") + tagdb(cx, 558, "WIH071", "start"))
    # 증기압 곡선(작은 그림): log10 P = A − B/T
    A_, B_ = C["antB"]["A"], C["antB"]["B"]; bx, by, bw, bh = 850, 356, 330, 262; px0, py0, pw, ph = 898, 410, 258, 154
    Tmin, Tmax, Pmax = 70.0, 130.0, 3.0; X_ = lambda T: px0 + (T - Tmin) / (Tmax - Tmin) * pw; Y_ = lambda Pv: py0 + ph - min(Pv, Pmax) / Pmax * ph
    psat = lambda T: 10 ** (A_ - B_ / (T + 273.15)); q = []
    a0 = nd["assume"][0]
    q.append(text(bx + 14, by + 22, "증기압 곡선(현재 증기압식)", "co-n", "start") + amark(bx + bw - 12, by + 18, a0["kind"], "a", "", "end") + text(bx + bw - 60, by + 22, a0["fig"], "ast", "end"))
    for pv in (1, 2, 3): q.append(f'<path class="plot-g" d="M{px0} {Y_(pv):.1f}H{px0 + pw}"/>' + text(px0 - 6, Y_(pv) + 4, f"{pv}", "tk", "end"))
    for tv in (80, 100, 120): q.append(text(X_(tv), py0 + ph + 16, f"{tv}", "tk"))
    q.append(f'<path class="plot-ax" d="M{px0} {py0}V{py0 + ph}H{px0 + pw}"/>' + text(px0 + pw, py0 + ph + 34, "온도 ℃", "ts", "end") + text(px0 - 6, py0 - 9, "torr", "ts", "end"))
    q.append(f'<path class="plot-c" d="{P([(X_(T), Y_(psat(T))) for T in [Tmin + i * 1.0 for i in range(int(Tmax - Tmin) + 1)]])}"/>')
    q.append(f'<circle class="plot-p" cx="{X_(84):.1f}" cy="{Y_(psat(84)):.1f}" r="4.5"/>' + text(X_(84) + 4, Y_(psat(84)) - 10, "84 ℃ · 0.10(문헌값)", "ts", "middle"))
    Tn = P30["Tmean"]; q.append(f'<circle class="plot-p2" cx="{X_(Tn):.1f}" cy="{Y_(psat(Tn)):.1f}" r="5"/>' + text(X_(Tn) - 10, Y_(psat(Tn)) - 22, "현재 계산", "tm", "end") + text(X_(Tn) - 10, Y_(psat(Tn)) - 7, f"{N(Tn)} ℃", "tm", "end"))
    Tp = X["plant_T"]; q.append(f'<path class="plot-p3" d="M{X_(Tp):.1f} {py0 + 6}V{py0 + ph}"/>' + text(X_(Tp) - 6, py0 + 16, f"현장 내부 온도 {N(Tp)} ℃", "markt", "end"))
    o.append(panel("plot", bx, by, bw, bh, "".join(q)))
    o.append(_col(fid, nd, [("antoine", (500, 300), "liq"), ("bubble", (cx - r + 2, lv + 1), "liq"), ("head", (xr + 2, lv + 100), "liq")], LX, LW, "R"))
    o.append(_col(fid, nd, [("vboil", (xn + 8, 104), "vap"), ("hvap", (cx + 132, lv - 9), "vap")], RX, RW, "L", y1=by - 12))
    o.append("</svg>"); return "".join(o)

# ====================================================================== ③ 충전 컬럼
def fig_n3(nd, D):
    fid = "fig-n3"; P30 = D["snap"]["30"]["PR"]; C = D["snap"]["30"]["CUR"]
    o = [svg_open(fid, 1200, 640, "충전 컬럼: 상승하는 증기와 하강하는 환류액이 충전층에서 접촉한다. 적용 공식 6개")]
    cx, y0, w, h = 600, 70, 130, 500; x0 = cx - w / 2; x1 = cx + w / 2; yp0 = y0 + h * 0.62; yp1 = y0 + h * 0.88; ym = y0 + h * 0.16
    vout = [(cx, y0), (cx, 28), (700, 28)]; vin = [(cx, 632), (cx, y0 + h)]; rf = [(760, 64), (760, 120), (x1, 120)]
    o.append(pipe(vout, "vap") + flow(vout, "vap") + text(708, 32, "응축기로", "ts", "start"))
    o.append(pipe(vin, "vap") + flow(vin, "vap") + text(cx + 14, 628, "정제기에서", "ts", "start"))
    o.append(pipe(rf, "liq") + flow(rf, "liq") + tagdb(772, 60, "FICH073", "start") + text(772, 86, f"환류 {N(P30['Rkg'])} kg/h", "tnum", "start"))
    o.append(column(cx, y0, w, h, pack=(0.62, 0.88), fid=fid))
    for dx in (-34, 34):                                                               # 증기는 위로, 액은 아래로
        o.append(f'<path class="pp pp-vap" stroke-width="2.4" d="M{cx + dx} {yp0 - 14:.1f}V{y0 + 190}" marker-end="url(#{fid}-a-vap)"/>')
    o.append(f'<path class="pp pp-liq" stroke-width="2" d="M{cx} {y0 + 96}V{yp0 - 16:.1f}" marker-end="url(#{fid}-a-liq)"/>')
    o.append(text(x1 + 10, 196, f"컬럼 상부 {N(P30['Ptop'], 2)} torr", "tnum", "start") + text(x1 + 10, 212, f"{N(P30['Thead'])} ℃", "tm", "start") + tagdb(x1 + 10, 231, "TIH075", "start"))
    o.append(text(x1 + 10, ym + 4, "메시", "ts", "start") + text(x1 + 10, 556, f"컬럼 하부 {N(P30['Pstill'], 2)} torr", "tnum", "start"))
    o.append(text(x0 - 8, 532, f"충전층 {N(C['Hpack'], 1)} m", "tnum", "end") + text(x0 - 8, 548, "1인치 폴 링", "ts", "end") + text(x0 - 8, 44, "C-H071", "t", "end"))
    o.append(_am(nd, 0, x1 + 16, 440) + _am(nd, 1, 352, 438) + _am(nd, 2, 352, 350) + _am(nd, 3, 716, 140))
    o.append(_col(fid, nd, [("mccabe", (x0 - 2, 92), "vap"), ("nst", (x0 - 2, 400), "n"), ("dp", (x0 - 2, 492), "vap")], LX, LW, "R"))
    o.append(_col(fid, nd, [("subcool", (766, 120), "liq"), ("flood", (x1 + 2, 410), "vap"), ("holdup", (x1 + 2, 495), "liq")], RX, RW, "L"))
    o.append("</svg>"); return "".join(o)

# ====================================================================== ④ 증기 배관
def fig_n4(nd, D):
    fid = "fig-n4"; P30 = D["snap"]["30"]["PR"]; C = D["snap"]["30"]["CUR"]; X = D["extra"]
    o = [svg_open(fid, 1200, 540, "증기 배관: 컬럼 상부에서 1차 응축기까지. 배관 출구에서 증기가 음속에 도달한다. 적용 공식 4개")]
    xa, xb, ytop, yca, yce = 430, 760, 150, 370, 300                                    # 컬럼 꼭대기(왼쪽) → 위로 → 가로 → 아래로 응축기
    o.append(f'<rect class="eq eqfill" x="{xa - 44}" y="{yca}" width="88" height="150" rx="5"/>' + text(xa, yca + 72, "C-H071", "t") + text(xa, yca + 89, "컬럼 상부", "ts"))
    o.append(cond_v(xb, yce, 96, 210, tubes=5) + text(xb - 60, yce + 120, "E-H071", "t", "end") + text(xb - 60, yce + 137, "1차 응축기", "ts", "end"))
    line = [(xa, yca), (xa, ytop), (xb, ytop), (xb, yce)]
    o.append(f'<path class="pp pp-vap" stroke-width="15" d="{P(line)}"/>' + flow(line, "vap"))
    o.append(text((xa + xb) / 2, ytop - 18, "80A-CCH-H0709", "tk") + _am(nd, 0, 476, ytop - 54) + _am(nd, 1, 640, ytop - 54))
    bx0, bx1 = xa + 30, xb - 30                                                         # 압력 띠: 입구 → 출구
    o.append(f'<path class="thin" d="M{bx0} {ytop + 34}H{bx1}" marker-end="url(#{fid}-a-n)"/>')
    o.append(text(bx0, ytop + 54, f"입구 {N(P30['Ptop'], 2)} torr", "tnum", "start") + text(bx1, ytop + 54, f"출구 {N(P30['Pexit'], 2)} torr", "tnum", "end"))
    o.append(text((bx0 + bx1) / 2, ytop + 74, "압력은 낮아지고 유속은 빨라진다", "ts"))
    o.append(text(bx0, ytop + 94, f"증기 {N(X['vpass'], 1)} kg/h", "tm", "start") + text(bx1, ytop + 94, f"마하수 {N(P30['Mach'], 2)} · 한계 0.95", "tm", "end"))
    o.append(tagbub(xa + 16, ytop + 142, "TIH075 위치 미확정", "start", "tgx") + _am(nd, 2, xa + 16, ytop + 166))
    o.append(text(xb - 56, yce + 20, f"응축기 측 {N(P30['Pcond'], 2)} torr", "ts", "end"))
    # 현장 두 점(PIMS 화면)
    tx, ty = 20, 300; q = [text(tx + 14, ty + 22, "현장 데이터 2점(PIMS 화면)", "co-n", "start")]
    rows = [("", "초류", "본류"), ("환류 + 유출", "5.25 kg/h", "9.75 kg/h"), ("내부 온도", "93.5 ℃", "101.5 ℃"), ("해당 온도의 증기압", "0.215 torr", "0.398 torr")]
    for i, (a, b, c) in enumerate(rows):
        yy = ty + 46 + i * 20
        q.append((text(tx + 14, yy, a, "ts", "start") if a else "") + text(tx + 214, yy, b, "tnum" if i else "ts", "end") + text(tx + 326, yy, c, "tnum" if i else "ts", "end"))
    q.append(text(tx + 14, ty + 132, "증발량 비 1.857 = 증기압 비 1.852", "tm", "start") + text(tx + 14, ty + 152, "→ 증기 배관이 초킹 상태로 추정됨", "ts", "start"))
    q.append(text(tx + 14, ty + 180, "사용 계기", "ts", "start") + tagdb(tx + 70, ty + 176, "FICH073", "start") + tagdb(tx + 138, ty + 176, "FICH072", "start") + tagdb(tx + 206, ty + 176, "TICH071", "start"))
    o.append(panel("pims", tx, ty, 340, 196, "".join(q)))
    o.append(_col(fid, nd, [("leq", (xa - 9, ytop - 6), "n"), ("comp", (xa - 9, ytop + 100), "vap")], 20, 340, "R", y1=ty - 12))
    o.append(_col(fid, nd, [("fric", (700, ytop - 8), "n"), ("choke", (xb + 9, yce - 20), "vap")], 838, 342, "L", y1=520))
    o.append("</svg>"); return "".join(o)

# ====================================================================== ⑤ 1차 응축기
def fig_n5(nd, D):
    fid = "fig-n5"; P30 = D["snap"]["30"]["PR"]; C = D["snap"]["30"]["CUR"]; X = D["extra"]
    o = [svg_open(fid, 1200, 640, "1차 응축기: 증기가 튜브 내부를 내려가면서 냉매에 열을 전달하고 응축된다. 적용 공식 4개")]
    cx, y0, w, h = 600, 110, 170, 420; x0 = cx - w / 2; x1 = cx + w / 2
    vin = [(420, 60), (cx, 60), (cx, y0)]; cout = [(cx, y0 + h), (cx, 626)]; side = [(x1, 502), (790, 502), (790, 472)]
    o.append(f'<path class="pp pp-vap" stroke-width="10" d="{P(vin)}"/>' + flow(vin, "vap") + text(430, 44, f"증기 {N(X['vpass'], 1)} kg/h", "tnum", "start"))
    o.append(pipe(cout, "liq", 4) + flow(cout, "liq") + text(cx + 14, 598, f"응축액 {N(X['Trf'])} ℃", "tnum", "start") + tagdb(cx + 14, 618, "TICH071D", "start"))
    o.append(pipe(side, "vap", 3.2) + arrowhead(790, 470, -90, "vap") + text(x1 + 9, 524, "미응축 증기 · 공기", "ts", "start") + text(790, 456, "2차 응축기로", "ts"))
    o.append(pipe([(425, 440), (x0, 440)], "brine", 3) + pipe([(x0, 200), (425, 200)], "brine", 3) + arrowhead(480, 440, 0, "brine") + arrowhead(455, 200, 180, "brine"))
    o.append(text(x0 - 8, 462, f"N-Brine {N(C['Tcw'], 0)} ℃", "tnum", "end") + tagdb(x0 - 8, 481, "TICH364", "end") + _am(nd, 0, x0 - 8, 508, "end"))
    o.append(text(x0 - 8, 186, f"출구 {N(P30['Tw1out'])} ℃", "tm", "end"))
    o.append(cond_v(cx, y0, w, h, tubes=7))
    for dx in (-48, 0, 48):                                                            # 관 안 증기 → 관 밖 냉매로 가는 열
        o.append(_arrow(fid, cx + dx - 8, y0 + 210, cx + dx - 26, y0 + 210))
    o.append(text(x1 + 12, 150, "E-H071", "t", "start") + text(x1 + 12, 167, "1차 응축기", "ts", "start"))
    o.append(text(x1 + 12, 250, f"포화 {N(P30['Tsat'], 0)} ℃", "tm", "start") + text(x1 + 12, 266, f"({N(P30['Pcond'], 2)} torr)", "ts", "start"))
    o.append(_am(nd, 1, x1 + 9, 546) + _am(nd, 2, cx - 14, 560, "end") + _am(nd, 3, 470, 80, dy=18))
    o.append(_col(fid, nd, [("load", (440, 66), "vap", {"y": 92}), ("ntu", (x0 - 2, 300), "brine")], LX, LW, "R"))
    o.append(_col(fid, nd, [("frac", (x1 + 2, 400), "vap"), ("sat", (794, 502), "vac")], RX, RW, "L"))
    o.append("</svg>"); return "".join(o)

# ====================================================================== ⑥ 환류 · 유출
def fig_n6(nd, D):
    fid = "fig-n6"; P30 = D["snap"]["30"]["PR"]; C = D["snap"]["30"]["CUR"]
    o = [svg_open(fid, 1200, 640, "환류와 유출: 응축액 일부는 U자 배관을 거쳐 컬럼으로 환류되고, 나머지는 회수 탱크로 유출된다. 적용 공식과 운전 기준 4개")]
    ex, ys, xf = 660, 200, 790
    o.append(f'<path class="eq eqfill" d="M{ex - 60} 40v70a18 18 0 0 0 18 18h84a18 18 0 0 0 18 -18v-70"/>' + text(ex, 84, "E-H071", "t") + text(ex, 101, "1차 응축기 하부", "ts"))
    o.append('<rect class="eq eqfill" x="370" y="60" width="70" height="170" rx="5"/>' + text(405, 150, "C-H071", "t") + text(405, 167, "컬럼", "ts"))
    cond = [(ex, 128), (ex, ys)]; refl = [(ex, ys), (580, ys), (580, 340), (500, 340), (500, 130), (440, 130)]; dist = [(ex, ys), (ex, 460)]
    tomain = [(ex, 460), (ex, 540)]; tofore = [(ex, 460), (xf, 460), (xf, 540)]
    o.append(pipe(cond, "liq", 4) + flow(cond, "liq") + pipe(refl, "liq", 3.4) + flow(refl, "liq") + pipe(dist, "liq", 3.4) + flow(dist, "liq"))
    o.append(pipe(tomain, "liq", 3.4) + flow(tomain, "liq") + pipe(tofore, "liq", 3.4))
    o.append(text(ex + 14, 152, "응축액", "ts", "start") + text(ex + 14, 168, f"{N(P30['Rkg'] + P30['Dkg'], 1)} kg/h", "tnum", "start"))
    o.append(valve(540, 340, True, "open", s=10) + text(540, 364, "FCV-H073", "tk") + tagdb(540, 383, "FICH073", "middle") + text(540, 407, f"환류 {N(P30['Rkg'])} kg/h", "tnum"))
    o.append(valve(ex, 290, False, "open", s=10) + text(ex + 16, 286, "FCV-H072", "tk", "start") + tagdb(ex + 16, 305, "FICH072", "start") + text(ex + 16, 329, f"유출 {N(P30['Dkg'])} kg/h", "tnum", "start"))
    o.append(valve(ex, 505, False, "open", s=9) + text(ex - 14, 509, "XV-H077", "tk", "end") + valve(xf, 505, False, "closed", s=9) + text(xf - 14, 509, "XV-H074", "tk", "end"))
    o.append(text(ex, 560, "T-H073 본류", "t") + tagdb(ex, 580, "WIH073", "middle") + text(xf, 560, "T-H072 초류", "t") + tagdb(xf, 580, "WIH072", "middle"))
    o.append(_am(nd, 2, 478, 246, "end") + text(478, 286, "U자 하단은", "ts", "end") + text(478, 302, "컬럼 환류 노즐보다", "ts", "end") + text(478, 318, "300 mm 이상 낮음(P&ID)", "ts", "end"))
    o.append(_am(nd, 1, 452, 92) + _am(nd, 3, ex + 16, 224))
    # 스팀 조절: 잰 응축량 → 조절(PI) → 스팀 밸브
    o.append(pipe([(540, 416), (540, 520), (440, 520)], "sig") + arrowhead(440, 520, 180, "n", 6) + text(548, 462, "응축량 측정값", "ts", "start") + text(548, 478, "(환류 + 유출)", "ts", "start"))
    o.append(panel("pi", 366, 503, 68, 34, text(400, 525, "PI 제어", "tn")) + _am(nd, 0, 366, 470))
    o.append(pipe([(400, 537), (400, 576)], "sig") + arrowhead(400, 577, 90, "n", 6))
    o.append(pipe([(340, 590), (470, 590)], "steam") + valve(400, 590, True, "open", s=10) + arrowhead(470, 590, 0, "heat") + text(400, 614, "TCV-H071", "tk") + text(344, 578, "스팀", "ts", "start") + text(480, 594, "자켓으로", "ts", "start"))
    o.append(_col(fid, nd, [("seal", (497, 342), "liq"), ("pi", (362, 520), "n")], LX, LW, "R"))
    o.append(_col(fid, nd, [("split", (ex + 8, ys - 4), "liq"), ("recipe", (xf + 10, 505), "n")], RX, RW, "L"))
    o.append("</svg>"); return "".join(o)

# ====================================================================== ⑦ 2차 응축기 · 진공펌프
def fig_n7(nd, D):
    fid = "fig-n7"; P30 = D["snap"]["30"]["PR"]; C = D["snap"]["30"]["CUR"]; X = D["extra"]
    o = [svg_open(fid, 1200, 600, "2차 응축기와 진공펌프: 미응축 증기를 응축시키고 유입 공기를 배기한다. 적용 공식 3개")]
    ex, ecy, ew, eh = 430, 300, 260, 84; px_, py_, pr_ = 930, 300, 46
    vin = [(250, 190), (ex + 60, 190), (ex + 60, ecy - eh / 2)]; vac = [(ex + ew - 40, ecy - eh / 2), (ex + ew - 40, 190), (px_, 190), (px_, py_ - pr_)]
    o.append(pipe(vin, "vap", 5) + text(250, 212, "1차 응축기의 미응축 증기 · 공기", "ts", "start"))
    o.append(pipe(vac, "vac", 3) + valve(790, 190, True, "open", s=10) + text(790, 174, "PCV-H093", "tk") + _am(nd, 2, 790, 132, "middle"))
    o.append(pipe([(620, ecy + eh / 2), (620, 408)], "liq", 2.6) + arrowhead(620, 410, 90, "liq") + text(632, 404, "응축액 → 초류 탱크", "ts", "start"))
    o.append(pipe([(470, ecy + eh / 2), (470, 386)], "brine", 3) + pipe([(510, ecy + eh / 2), (510, 386)], "brine", 3) + text(490, 404, f"L-Brine {N(C['Tcw2'], 1)} ℃", "tnum") + tagdb(490, 424, "TIH353", "middle"))
    o.append(cond_h(ex, ecy, ew, eh) + text(570, 228, "E-H072", "t") + text(570, 245, "2차 응축기", "ts"))
    o.append(pump(px_, py_, pr_) + pipe([(px_ + pr_, py_), (px_ + pr_ + 64, py_)], "vac", 3) + arrowhead(px_ + pr_ + 64, py_, 0, "vac") + text(px_ + pr_ + 74, py_ + 4, "배기", "ts", "start"))
    o.append(text(990, 346, "VP-H093 진공펌프", "t", "start") + _am(nd, 0, 990, 368))
    for lx in (330, 420):                                                              # 리크(새어 드는 공기)
        o.append(f'<path class="pp pp-vac" stroke-width="1.6" d="M{lx} 120V178" marker-end="url(#{fid}-a-vac)"/>')
    o.append(_am(nd, 1, 375, 64, "middle") + text(375, 106, "유입 공기(리크)", "ts"))
    o.append(text(922, 226, f"펌프 측 {N(P30['Ppump'], 3)} torr", "tnum", "end") + tagdb(922, 246, "PIH093", "end"))
    o.append(_one(fid, nd, "pump", 782, 452, 398, (908, 344), "T", "vac") + _one(fid, nd, "tau", 372, 452, 390, (750, 197), "T", "vac") + _one(fid, nd, "sat2", 22, 452, 330, (446, 338), "T", "vac"))
    o.append("</svg>"); return "".join(o)

# ====================================================================== ⑧ 회수 탱크 · 순도
def fig_n8(nd, D):
    fid = "fig-n8"; E = D["end"]
    o = [svg_open(fid, 1200, 620, "회수 탱크와 순도: 투입량 350 kg이 초류, 본류, 후류로 나뉜다. 적용 공식 3개와 물질 수지 막대그래프")]
    mx, my0, mw, mh, mhd = 560, 150, 230, 150, 56; fx, fy0, fw, fh, fhd = 790, 250, 110, 110, 28
    inl = [(mx, 56), (mx, my0 + 4)]; br = [(mx, 100), (fx, 100), (fx, fy0 + 4)]
    o.append(pipe(inl, "liq", 3.4) + flow(inl, "liq") + pipe(br, "liq", 3.4))
    o.append(valve(mx, 128, False, "open", s=9) + text(mx - 14, 132, "XV-H077", "tk", "end") + valve(690, 100, True, "closed", s=9) + text(690, 84, "XV-H074", "tk"))
    o.append(text(mx + 12, 66, "유출(1차 응축기에서)", "ts", "start"))
    mfull = my0 + mhd + mh + mhd * 0.6; ffull = fy0 + fhd + fh + fhd * 0.6
    o.append(vessel(mx, my0, mw, mh, mhd, level=mfull - (mh + mhd * 0.6) * 0.72) + text(mx, 292, f"본류 {N(E['main'])} kg", "tnum") + text(mx, 310, f"저비점 성분 {N(E['wM'], 2)} %", "tm") + _am(nd, 0, mx, 332, "middle"))
    o.append(vessel(fx, fy0, fw, fh, fhd, level=ffull - (fh + fhd * 0.6) * 0.42) + text(fx, 370, f"초류 {N(E['fore'])} kg", "tnum") + text(fx, 386, f"{N(E['wF'], 2)} %", "tm"))
    o.append(text(mx, 436, "T-H073 본류 탱크", "t") + tagdb(mx, 455, "WIH073", "middle") + text(fx, 440, "T-H072 초류 탱크", "t") + tagdb(fx, 459, "WIH072", "middle"))
    # 무게 막대: 투입 = 초류 + 본류 + 후류 + 나머지
    bx, by, bw, bh = 360, 508, 710, 32; tot = E["m0"]; x = bx; rest = max(0.0, tot - E["fore"] - E["main"] - E["m"])
    o.append(text(bx, by - 12, f"투입 {N(tot, 0)} kg의 배분", "co-n", "start"))
    for nm, kg, cl in (("초류", E["fore"], "bar-f"), ("본류", E["main"], "bar-m"), ("후류(정제기 잔류)", E["m"], "bar-t"), ("배관 · 충전층 홀드업", rest, "bar-h")):
        ww = bw * kg / tot; o.append(f'<rect class="{cl}" x="{x:.1f}" y="{by}" width="{max(1.5, ww):.1f}" height="{bh}"/>')
        if nm.startswith("배관"): o.append(text(bx + bw, by + bh + 34, f"{nm} {N(kg)}", "ts", "end"))
        else: o.append(text(x + ww / 2, by + bh + 16, f"{nm} {N(kg)}", "tnum"))
        x += ww
    o.append(text(bx, by + bh + 36, f"초류 비율 f = {N(E['fore'] / tot * 100)} % · 본류까지의 누적 회수 비율 f₂ = {N((tot - E['m']) / tot * 100)} %", "ts", "start"))
    xt = bx + bw * (E["fore"] + E["main"]) / tot
    o.append(_am(nd, 1, xt - 3, 468))
    o.append(_col(fid, nd, [("accum", (mx - mw / 2 - 2, 300), "liq"), ("mass", (bx - 4, by + bh / 2), "n")], LX, LW, "R", y1=600))
    o.append(_one(fid, nd, "rayleigh", RX, 262, RW, (960, by - 2), "B", "n"))
    o.append("</svg>"); return "".join(o)

FIGS = {1: fig_n1, 2: fig_n2, 3: fig_n3, 4: fig_n4, 5: fig_n5, 6: fig_n6, 7: fig_n7, 8: fig_n8}
