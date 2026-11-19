# -*- coding: utf-8 -*-
"""전체 설비 그림(P&ID 배치를 따른 2D) — 전체 구조 · 이상 상황 · DB 화면이 같이 쓴다."""
import math
from 그림 import *

# 자리(1200 × 690). 이름은 P&ID 장치 번호.
GEO = dict(
    vx=250, vy0=392, vw=190, vh=160, vhd=46,          # T-H071 정제기: 위 경판 꼭대기 392 · 몸통 438~598 · 바닥 644
    cx=318, cy0=120, cw=46, ch=210,                    # C-H071 컬럼 120~330
    e1x=610, e1y0=110, e1w=58, e1h=150,                # E-H071 1차 응축기 110~260
    ysp=300, xU1=480, yU=352, xRf=392, yRf=160,        # 분기 · 환류 U자
    yTee=410,
    mx=610, my0=478, mw=150, mh=92, mhd=37,            # T-H073 본류 탱크(바닥 644)
    fx=775, fy0=530, fw=88, fh=70, fhd=22,             # T-H072 초류 탱크(바닥 644)
    e2x=850, e2cy=202, e2w=130, e2h=42,                # E-H072 2차 응축기
    px=1105, py=152, pr=22,                            # VP-H093 진공펌프
)

def plant(fid, level=0.57, main=0.0, fore=0.0, flows=("steam", "vap", "reflux", "dist"), tags=True, valves=None, dyn=False):
    """설비와 관. level·main·fore = 액 높이(0~1). flows = 흐름 표시를 켤 관. valves = {이름: open/closed}. dyn = 이상 상황 화면용(data-* 붙임)."""
    g = GEO; o = []; V = dict(TCV="open", FCV73="open", FCV72="open", XV77="open", XV74="closed", PCV="open"); V.update(valves or {})
    vx, vy0, vw, vh, vhd = g["vx"], g["vy0"], g["vw"], g["vh"], g["vhd"]; vyt = vy0 + vhd; vyb = vyt + vh; r = vw / 2
    jt = vyb - vh * 0.575                                           # 자켓 윗끝: 몸통 800 가운데 아래 460
    df = (lambda k: f' data-flow="{k}"') if dyn else (lambda k: "")
    # --- 관(설비보다 먼저 그려 설비가 위에 온다)
    cx, cy0, cw, ch = g["cx"], g["cy0"], g["cw"], g["ch"]
    yneck = vyt - vhd * math.sqrt(max(0.0, 1 - ((cx - vx) / r) ** 2))
    e1x, e1y0, e1w, e1h = g["e1x"], g["e1y0"], g["e1w"], g["e1h"]; e1yb = e1y0 + e1h
    vap1 = [(cx, cy0 + ch), (cx, yneck + 2)]; vap2 = [(cx, cy0), (cx, 72), (e1x, 72), (e1x, e1y0)]
    o.append(f'<g{df("vap")}>' + pipe(vap1, "vap") + pipe(vap2, "vap") + (flow(list(reversed(vap1)), "vap") + flow(vap2, "vap") if "vap" in flows else "") + "</g>")
    ysp = g["ysp"]; cond = [(e1x, e1yb), (e1x, ysp)]
    refl = [(e1x, ysp), (g["xU1"], ysp), (g["xU1"], g["yU"]), (g["xRf"], g["yU"]), (g["xRf"], g["yRf"]), (cx + cw / 2, g["yRf"])]
    o.append(f'<g{df("cond")}>' + pipe(cond, "liq") + "</g>")
    o.append(f'<g{df("reflux")}>' + pipe(refl, "liq") + (flow(refl, "liq") if "reflux" in flows else "") + "</g>")
    mx, my0 = g["mx"], g["my0"]; fx, fy0 = g["fx"], g["fy0"]; yT = g["yTee"]
    dist = [(e1x, ysp), (e1x, yT)]; tomain = [(e1x, yT), (mx, my0 + 2)]; tofore = [(e1x, yT), (fx, yT), (fx, fy0 + 2)]
    o.append(f'<g{df("dist")}>' + pipe(dist, "liq") + (flow(dist, "liq") if "dist" in flows else "") + "</g>")
    o.append(f'<g{df("main")}>' + pipe(tomain, "liq") + (flow(tomain, "liq") if "dist" in flows and V["XV77"] == "open" else "") + "</g>")
    o.append(f'<g{df("fore")}>' + pipe(tofore, "liq") + (flow(tofore, "liq") if "dist" in flows and V["XV74"] == "open" else "") + "</g>")
    e2x, e2cy, e2w, e2h = g["e2x"], g["e2cy"], g["e2w"], g["e2h"]
    v2 = [(e1x + e1w / 2, 140), (e2x + 40, 140), (e2x + 40, e2cy - e2h / 2)]
    o.append(f'<g{df("v2")}>' + pipe(v2, "vap", 3.4) + "</g>")
    l2 = [(e2x + 105, e2cy + e2h / 2), (e2x + 105, 470), (fx + 15, 470), (fx + 15, fy0 + 3)]
    o.append(f'<g{df("l2")}>' + pipe(l2, "liq", 1.8) + "</g>")
    px, py, pr = g["px"], g["py"], g["pr"]
    vac = [(e2x + 115, e2cy - e2h / 2), (e2x + 115, 120), (px, 120), (px, py - pr)]
    o.append(f'<g{df("vac")}>' + pipe(vac, "vac") + "</g>")
    steam = [(36, 560), (vx - r - 9, 560)]
    o.append(f'<g{df("steam")}>' + pipe(steam, "steam") + (flow(steam, "steam") if "steam" in flows else "") + "</g>")
    o.append(pipe([(vx, vyb + vhd + 9), (vx, 668), (60, 668)], "thin"))                      # 스팀 응축수(LC)
    o.append(pipe([(e1x - e1w / 2, 140), (e1x - e1w / 2 - 34, 140)], "brine") + pipe([(e1x - e1w / 2, 232), (e1x - e1w / 2 - 34, 232)], "brine"))   # N-Brine 나감 · 들어옴
    o.append(pipe([(e2x + 30, e2cy + e2h / 2), (e2x + 30, e2cy + e2h / 2 + 22)], "brine") + pipe([(e2x + 62, e2cy + e2h / 2), (e2x + 62, e2cy + e2h / 2 + 22)], "brine"))
    # --- 설비
    o.append(insulation(vx, vy0, vw, vh, vhd, top=jt, gap=9, t=9, fid=fid))
    o.append(vessel(vx, vy0, vw, vh, vhd, level=vyb - vh * level))
    o.append(jacket(vx, vy0, vw, vh, vhd, top=jt, gap=9))
    o.append(agitator(vx, vy0, vw, vh, vhd))
    o.append(column(cx, cy0, cw, ch, pack=(0.62, 0.88), fid=fid))
    o.append(cond_v(e1x, e1y0, e1w, e1h, tubes=4))
    o.append(vessel(mx, my0, g["mw"], g["mh"], g["mhd"], level=(my0 + g["mhd"] + g["mh"] + g["mhd"] * 0.6) - (g["mh"] + g["mhd"] * 0.6) * main if main > 0 else None))
    o.append(vessel(fx, fy0, g["fw"], g["fh"], g["fhd"], level=(fy0 + g["fhd"] + g["fh"] + g["fhd"] * 0.6) - (g["fh"] + g["fhd"] * 0.6) * fore if fore > 0 else None))
    o.append(cond_h(e2x, e2cy, e2w, e2h)); o.append(pump(px, py, pr))
    # --- 밸브
    o.append(valve(92, 560, True, V["TCV"], vid="TCV") + valve((e1x + g["xU1"]) / 2, ysp, True, V["FCV73"], vid="FCV73") + valve(e1x, 346, False, V["FCV72"], vid="FCV72")
             + valve(mx, 446, False, V["XV77"], vid="XV77") + valve((e1x + fx) / 2, yT, True, V["XV74"], vid="XV74") + valve(px - 75, 120, True, V["PCV"], vid="PCV"))
    if tags:
        o.append(text(vx - 22, vy0 - 44, "T-H071 정제기", "t", "end"))
        o.append(text(cx - cw / 2 - 10, cy0 + 16, "C-H071", "t", "end") + text(cx - cw / 2 - 10, cy0 + 32, "충전 컬럼", "ts", "end"))
        o.append(text(e1x + e1w / 2 + 10, e1y0 + 64, "E-H071", "t", "start") + text(e1x + e1w / 2 + 10, e1y0 + 80, "1차 응축기", "ts", "start"))
        o.append(text(e2x + e2w / 2 + 8, e2cy - e2h / 2 - 28, "E-H072", "t", "middle") + text(e2x + e2w / 2 + 8, e2cy - e2h / 2 - 12, "2차 응축기", "ts", "middle"))
        o.append(text(px, py + pr + 18, "VP-H093", "t") + text(px, py + pr + 34, "진공펌프", "ts"))
        o.append(text(mx, 664, "T-H073 본류 탱크", "t") + text(fx, 664, "T-H072 초류 탱크", "t"))
        o.append(text(36, 548, "LP 스팀", "ts", "start") + text(92, 582, "TCV-H071", "tk") + text(e1x - e1w / 2 - 17, 252, "N-Brine", "ts", "middle") + text(e2x + 46, e2cy + e2h / 2 + 38, "L-Brine", "ts"))
        o.append(text((e1x + g["xU1"]) / 2, ysp + 21, "FCV-H073", "tk") + text(e1x + 14, 350, "FCV-H072", "tk", "start") + text(mx - 13, 450, "XV-H077", "tk", "end") + text((e1x + fx) / 2, yT - 12, "XV-H074", "tk") + text(px - 75, 106, "PCV-H093", "tk"))
    return "".join(o)

# 그림 위 표식 자리(전체 구조 화면의 번호와 공식 이름 목록)
PINS = {
    1: dict(pin=(60, 438), tx=78, ty=442, anchor="start"),
    2: dict(pin=(378, 500), tx=396, ty=504, anchor="start"),
    3: dict(pin=(104, 196), tx=122, ty=200, anchor="start"),
    4: dict(pin=(396, 30), tx=414, ty=34, anchor="start"),
    5: dict(pin=(668, 214), tx=686, ty=218, anchor="start"),
    6: dict(pin=(410, 196), tx=428, ty=200, anchor="start"),
    7: dict(pin=(996, 248), tx=1014, ty=252, anchor="start"),
    8: dict(pin=(868, 520), tx=886, ty=524, anchor="start"),
}
