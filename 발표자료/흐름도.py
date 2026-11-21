# -*- coding: utf-8 -*-
"""계산값 흐름도 — 공식 35개의 산출값이 어느 계산으로 넘어가는지를 한 장에 그린다(교과서의 '계산값 흐름도').

- 사용자 요구(2026-11-20): "공식에서 나온 답이 어디에쓰이는지 5번쨰공식 10번쨰공식에 이게 사용된다 뭐 이런식으로말로되어잇는데
  그림으로 flow그려서 구한것들이 어디로가서 어떻게 사용되는지 한눈에 한화면으로볼수있게 만들어줄수는없어?"
- 상자 = 공식 하나(구간 번호-식 번호 · 이름 · 본류 구간의 계산값). 선 = 한 식의 산출값이 다른 식의 입력으로 넘어가는 경로.
- 선의 목록(MAIN · AUX)은 용도.py의 '계산' 글(구한 값이 어느 계산의 입력이 되는가)과 같은 내용이다. 점검_교과서.py가 글에 적힌 '식 N' · '구간 N'과 선이 맞는지 본다.
- 열과 증기 · 액의 양은 왼쪽 → 오른쪽(스팀 → 정제기 → 응축기 → 회수 탱크), 압력은 오른쪽 → 왼쪽(진공펌프 → 증기 배관 → 정제기)으로 넘어가 정제기(2-4)에서 만난다.
- 늘 보이는 선: 열 · 양 · 압력 · 제어의 주 경로와, 바로 옆 식에 들어가는 보조 입력. 멀리 떨어진 보조 입력(AUX)은 상자를 고르면 나타난다.
- 숫자는 다른 화면과 같은 기록(값.json · 점검 기록)에서 읽는다.
"""
import json, math
from 그림 import esc

W, H = 1200, 566
X0, PX, BW = 26, 147, 124            # 첫 칸 왼쪽, 칸 간격, 상자 너비(칸 사이 통로 23)
Y0, PY, BH = 70, 72, 50              # 첫 줄 위, 줄 간격, 상자 높이(줄 사이 22: 통로의 선과 이름표가 들어간다)
CH = PX - BW

# 상자 자리(칸 = 구간, 줄). 주 경로의 상자가 이웃하도록 배치했다
GRID = dict(valve=(0, 0), steamlam=(0, 1), jacket=(0, 2), agit=(0, 3), heatbal=(0, 4), loss=(0, 5),
            antoine=(1, 0), hvap=(1, 1), vboil=(1, 2), bubble=(1, 3), head=(1, 4),
            subcool=(2, 0), mccabe=(2, 1), nst=(2, 2), dp=(2, 3), flood=(2, 4), holdup=(2, 5),
            leq=(3, 1), fric=(3, 2), comp=(3, 3), choke=(3, 4),
            load=(4, 2), frac=(4, 3), ntu=(4, 4), sat=(4, 5),
            seal=(5, 1), recipe=(5, 2), split=(5, 3), pi=(5, 4),
            sat2=(6, 0), tau=(6, 4), pump=(6, 5),
            rayleigh=(7, 2), accum=(7, 3), mass=(7, 4))
# 상자에 적는 짧은 이름(카드의 이름이 길면 줄인다)
SHORT = dict(valve="밸브 유량 특성", steamlam="스팀 공급 열량", heatbal="액 온도 열수지", agit="교반 전열", head="정수두", vboil="진공 비등 평형",
             subcool="과냉 환류 응축", choke="음속 한계(초킹)", ntu="응축기 처리 열량", sat="공기 동반 증기", sat2="2차 포화 한계", rayleigh="본류 저비점 농도")

# 주 경로와 가까운 보조 입력: (주는 식, 받는 식, 넘어가는 값, 종류, 그리는 방법)
#  종류 heat 열 · mass 증기와 액의 양 · pres 압력 · ctrl 제어 · sup 보조 입력
#  방법 v 위아래 이웃 · h 같은 줄 · s 이웃 칸 · loop 같은 칸에서 건너뜀 · lane 줄 사이 통로로 여러 칸을 건넘
MAIN = [
    ("valve", "steamlam", "스팀 유량", "heat", dict(t="v")),
    ("steamlam", "jacket", "공급 열량의 상한", "heat", dict(t="v")),
    ("jacket", "vboil", "전달 열량", "heat", dict(t="h")),
    ("vboil", "dp", "증발량", "mass", dict(t="s", so=9, do=9)),
    ("vboil", "load", "컬럼 상부를 통과한 증기량", "mass", dict(t="lane", lane=("gap", 1), so=-11, cs=15, cd=8, lab="증기량", lx=2.75)),
    ("load", "frac", "응축 부하", "mass", dict(t="v")),
    ("frac", "split", "응축량", "mass", dict(t="h")),
    ("split", "accum", "유출량", "mass", dict(t="h", lab="유출량", lx=6.0)),
    ("split", "mccabe", "환류량", "mass", dict(t="lane", lane=("gap", 0), so=-11, cs=7, cd=7, lab="환류량", lx=4.0)),
    ("mccabe", "accum", "유출액의 조성", "mass", dict(t="lane", lane="top", so=-11, do=-11, cs=16, cd=11, lab="유출액의 조성", lx=4.5)),
    ("tau", "pump", "압력 응답 시간", "pres", dict(t="v")),
    ("pump", "choke", "응축기 측 압력", "pres", dict(t="lane", lane=("gap", 4), cs=11, cd=11, lab="응축기 측 압력", lx=5.0)),
    ("choke", "comp", "배관 출구 압력", "pres", dict(t="v")),
    ("comp", "dp", "컬럼 상부 압력", "pres", dict(t="h")),
    ("dp", "vboil", "충전층 압력 손실을 더한 정제기 압력", "pres", dict(t="s", so=-9, do=-9)),
    ("vboil", "bubble", "정제기 압력", "pres", dict(t="v", ox=-20)),
    ("bubble", "vboil", "끓는점(내부 온도)", "pres", dict(t="v", ox=20)),
    ("split", "pi", "응축량(환류 + 유출) 측정값", "ctrl", dict(t="v")),
    ("pi", "valve", "스팀 밸브 개도", "ctrl", dict(t="lane", lane="bot", lab="스팀 밸브 개도", lx=2.5)),
    ("agit", "jacket", "액 측 전열계수", "sup", dict(t="v")),
    ("jacket", "heatbal", "전달 열량", "sup", dict(t="loop", side="R", lo=8)),
    ("loss", "heatbal", "열손실", "sup", dict(t="v")),
    ("antoine", "hvap", "증기압 곡선의 기울기", "sup", dict(t="v")),
    ("hvap", "vboil", "증발열", "sup", dict(t="v")),
    ("antoine", "bubble", "증기압", "sup", dict(t="loop", side="L", lo=9)),
    ("bubble", "head", "액면의 끓는점", "sup", dict(t="v")),
    ("subcool", "mccabe", "내부 응축량(환류비 보정)", "sup", dict(t="v")),
    ("nst", "mccabe", "이론단수", "sup", dict(t="v")),
    ("flood", "holdup", "범람률", "sup", dict(t="v")),
    ("fric", "comp", "마찰계수", "sup", dict(t="v")),
    ("leq", "comp", "상당 길이", "sup", dict(t="loop", side="R", lo=5)),
    ("ntu", "frac", "처리 가능 열량", "sup", dict(t="v")),
    ("recipe", "split", "환류 · 유출 설정값", "sup", dict(t="v")),
    ("seal", "split", "액봉 충전 후 흐름 시작", "sup", dict(t="loop", side="R", lo=8)),
    ("accum", "mass", "초류 · 본류의 양", "sup", dict(t="v")),
    ("accum", "rayleigh", "농도(결과 해석)", "sup", dict(t="v", dash=True)),
]
# 멀리 떨어진 보조 입력: 상자를 고르면 나타난다
AUX = [
    ("antoine", "ntu", "응축기 압력의 포화 온도"), ("antoine", "sat", "응축액 온도의 증기압"), ("antoine", "sat2", "2차 응축기 온도의 증기압"),
    ("hvap", "load", "증발열"), ("loss", "vboil", "열손실"), ("bubble", "jacket", "내부 온도(자켓과의 온도 차)"), ("bubble", "heatbal", "승온이 끝나는 온도"), ("heatbal", "vboil", "비등 개시 시점"),
    ("vboil", "flood", "증발량"), ("vboil", "comp", "증기 유량"), ("flood", "mccabe", "분리 효율"), ("holdup", "mccabe", "조성 변화의 지연"),
    ("split", "subcool", "환류량"), ("pump", "ntu", "응축기 측 압력"), ("pump", "sat", "응축기 측 압력"), ("frac", "sat2", "응축되지 않은 증기"), ("sat", "sat2", "1차 응축기를 빠져나간 증기"),
    ("sat2", "mass", "진공펌프 측 손실량"), ("seal", "mass", "배관 잔류액"), ("split", "recipe", "누적 유출량"), ("recipe", "accum", "회수 탱크 전환"),
]
KIND = dict(heat="열", mass="증기 · 액의 양", pres="압력", ctrl="제어", sup="보조 입력", aux="보조 입력")


def links():
    return [(s, d, lab, k) for s, d, lab, k, _ in MAIN] + [(s, d, lab, "aux") for s, d, lab in AUX]


def values(D):
    """상자에 적는 계산값(본류 구간 · 배치 끝). 다른 화면과 같은 기록에서 읽는다."""
    P = D["snap"]["30"]["PR"]; C = D["snap"]["30"]["CUR"]; X = D["extra"]; E = D["end"]
    err = E["m0"] - E["m"] - E["fore"] - E["main"] - C["holdC"]
    return dict(valve=[f'스팀 {P["steamKgh"]:.1f} kg/h'], steamlam=[f'상한 {P["Qcap"]:.0f} W'], jacket=[f'전달 {P["Q"]:.0f} W'], heatbal=[f'비등 개시 {E["st2"]:.2f} h'],
                agit=[f'{X["hi"]:.0f} W/m²·K'], loss=[f'{P["Qloss"]:.0f} W'], antoine=[f'{P["Pstill"]:.2f} torr', f'({P["Tmean"]:.0f} ℃에서)'], bubble=[f'{P["Tbub"]:.1f} ℃'],
                head=[f'1 cm당 +{X["dT_1cm"]:.0f} ℃'], vboil=[f'증발 {P["vdot"]:.1f} kg/h', f'정제기 {P["Pstill"]:.2f} torr'], hvap=[f'{P["lam"] / 1000:.0f} kJ/kg'],
                mccabe=[f'저비점 {P["xDw"] * 100:.2f} %'], nst=[f'{C["Nst"]:.0f}단'], dp=[f'손실 {P["dpPackC"]:.2f} torr'], subcool=[f'{P["subR"] * P["Rkg"]:.2f} kg/h'], flood=[f'{P["flood"] * 100:.0f} %'],
                holdup=[f'{P["mHold"]:.2f} kg'], leq=[f'{C["Lpipe"]:.2f} m'], comp=[f'입구 {P["Ptop"]:.2f} torr'], fric=[f'f {X["f_pipe"]:.3f}'], choke=[f'출구 {P["Pexit"]:.2f} torr'],
                load=[f'{P["Qc"]:.0f} W'], ntu=[f'{P["cap1"] / 1000:.0f} kW'], frac=[f'{min(100.0, P["c1"] * 100):.1f} %'], sat=[f'{P["m2kg"] * 1000:.2f} g/h'],
                split=[f'환류 {P["Rkg"]:.1f} kg/h', f'유출 {P["Dkg"]:.1f} kg/h'], seal=[f'{C["holdC"]:.2f} kg'], pi=[f'개도 {P["MVpct"]:.1f} %'], recipe=[f'종료 {E["t"]:.1f} h'],
                sat2=[X["lost_txt"]], tau=[f'{P["tauP"]:.0f} 초'], pump=[f'{P["Ppump"]:.2f} torr'], accum=[f'본류 {E["wM"]:.2f} %'], mass=[f'수지 차 {abs(err):.2f} kg'], rayleigh=[f'농축비 {E["Eeff"]:.2f}'])


# ---------------------------------------------------------------- 그리기
def _xy(k):
    c, r = GRID[k]; return X0 + c * PX, Y0 + r * PY

def _port(k, side, off=0.0):
    x, y = _xy(k)
    return {"R": (x + BW, y + BH / 2 + off), "L": (x, y + BH / 2 + off), "T": (x + BW / 2 + off, y), "B": (x + BW / 2 + off, y + BH)}[side]

def _round(pts, r=6.0):
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        d1, d2 = math.hypot(x1 - x0, y1 - y0), math.hypot(x2 - x1, y2 - y1)
        if d1 < 0.5 or d2 < 0.5: continue
        rr = min(r, d1 / 2, d2 / 2)
        d += f"L{x1 - (x1 - x0) / d1 * rr:.1f} {y1 - (y1 - y0) / d1 * rr:.1f}Q{x1:.1f} {y1:.1f} {x1 + (x2 - x1) / d2 * rr:.1f} {y1 + (y2 - y1) / d2 * rr:.1f}"
    return d + f"L{pts[-1][0]:.1f} {pts[-1][1]:.1f}"

def _lane_y(lane, off=0.0):
    if lane == "top": return Y0 - 9 + off
    if lane == "bot": return Y0 + 5 * PY + BH + 22 + off
    return Y0 + lane[1] * PY + BH + 15 + off

def _path(s, d, o):
    """선의 경로(d 속성)와 이름표 자리."""
    (cs, rs), (cd, rd) = GRID[s], GRID[d]; t = o["t"]; G = 2.0          # G = 화살촉이 상자에 닿기 전에 멈추는 거리
    if t == "v":
        assert cs == cd and abs(rs - rd) == 1, (s, d)
        ox = o.get("ox", 0.0); a = _port(s, "B" if rd > rs else "T", ox); b = _port(d, "T" if rd > rs else "B", ox)
        b = (b[0], b[1] - G if rd > rs else b[1] + G)
        return f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}", None
    if t == "h":
        assert rs == rd, (s, d)
        a = _port(s, "R" if cd > cs else "L"); b = _port(d, "L" if cd > cs else "R"); b = (b[0] - G if cd > cs else b[0] + G, b[1])
        return f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}", ((a[0] + b[0]) / 2, a[1] - 6)
    if t == "s":
        assert abs(cs - cd) == 1, (s, d)
        right = cd > cs; a = _port(s, "R" if right else "L", o.get("so", 0)); b = _port(d, "L" if right else "R", o.get("do", 0)); b = (b[0] - G if right else b[0] + G, b[1])
        m = (a[0] + b[0]) / 2
        return f"M{a[0]:.1f} {a[1]:.1f}C{m:.1f} {a[1]:.1f} {m:.1f} {b[1]:.1f} {b[0]:.1f} {b[1]:.1f}", None
    if t == "loop":
        assert cs == cd and abs(rs - rd) > 1, (s, d)
        side = o["side"]; sg = 1 if side == "R" else -1; a = _port(s, side); b = _port(d, side); x = a[0] + sg * o["lo"]; b = (b[0] + sg * G, b[1])
        return _round([a, (x, a[1]), (x, b[1]), b], 5), None
    if t == "lane":
        right = cd > cs; ly = _lane_y(o["lane"], o.get("lo", 0.0))
        if o["lane"] == "bot":            # 아래 통로: 상자 아래로 내려가 왼쪽 여백을 타고 올라가 받는 상자의 왼쪽으로
            a = _port(s, "B"); b = _port(d, "L"); x = X0 - 13; b = (b[0] - G, b[1])
            return _round([a, (a[0], ly), (x, ly), (x, b[1]), b]), (X0 + o.get("lx", 2.5) * PX, ly - 4)
        a = _port(s, "R" if right else "L", o.get("so", 0)); b = _port(d, "L" if right else "R", o.get("do", 0))
        x1 = a[0] + (o.get("cs", CH / 2) if right else -o.get("cs", CH / 2)); x2 = b[0] - (o.get("cd", CH / 2) if right else -o.get("cd", CH / 2)); b = (b[0] - G if right else b[0] + G, b[1])
        return _round([a, (x1, a[1]), (x1, ly), (x2, ly), (x2, b[1]), b]), (X0 + o.get("lx", (cs + cd) / 2) * PX, ly - 4)
    raise ValueError(t)

def _aux_path(s, d):
    """멀리 떨어진 보조 입력: 상자 가장자리에서 가장자리로 완만한 곡선."""
    (cs, rs), (cd, rd) = GRID[s], GRID[d]
    if cs == cd:
        a = _port(s, "R"); b = _port(d, "R"); x = a[0] + 12 + 3 * abs(rs - rd)
        return f"M{a[0]:.1f} {a[1]:.1f}C{x:.1f} {a[1]:.1f} {x:.1f} {b[1]:.1f} {b[0] + 2:.1f} {b[1]:.1f}"
    right = cd > cs; a = _port(s, "R" if right else "L"); b = _port(d, "L" if right else "R"); b = (b[0] - 2 if right else b[0] + 2, b[1]); m = (a[0] + b[0]) / 2
    return f"M{a[0]:.1f} {a[1]:.1f}C{m:.1f} {a[1]:.1f} {m:.1f} {b[1]:.1f} {b[0]:.1f} {b[1]:.1f}"


def build(D, NODES):
    """(svg, data). data = 상자를 골랐을 때 아래 칸에 적을 내용."""
    F = {f["k"]: (nd, i + 1, f) for nd in NODES for i, f in enumerate(nd["formulas"])}
    assert set(F) == set(GRID), set(F) ^ set(GRID)
    for k, (c, r) in GRID.items(): assert F[k][0]["n"] == c + 1, (k, "칸 = 구간이어야 한다")
    assert len(set(GRID.values())) == len(GRID)
    L = links(); assert len({(s, d) for s, d, _, _ in L}) == len(L), "같은 선이 두 번 있다"
    for s, d, _, _ in L: assert s in GRID and d in GRID and s != d, (s, d)
    V = values(D); fid = lambda k: f"{F[k][0]['n']}-{F[k][1]}"
    o = [f'<svg id="fig-flow" viewBox="0 0 {W} {H}" role="img" aria-label="공식 {len(F)}개의 산출값이 넘어가는 경로. 열과 증기 · 액의 양은 왼쪽에서 오른쪽으로, 압력은 오른쪽에서 왼쪽으로 넘어가 정제기의 진공 비등 평형에서 만난다">'
         '<defs>' + "".join(f'<marker id="fl-a-{k}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" markerUnits="userSpaceOnUse" orient="auto"><path class="fl-m fl-m-{k}" d="M0 0.6L8 4L0 7.4z"/></marker>' for k in ("heat", "mass", "pres", "ctrl", "sup", "aux")) + '</defs>']
    # 칸 바탕과 구간 이름
    for nd in NODES:
        x = X0 + (nd["n"] - 1) * PX
        o.append(f'<rect class="fl-col" x="{x - 4}" y="{Y0 - 4}" width="{BW + 8}" height="{5 * PY + BH + 8}" rx="10"/>')
        o.append(f'<g class="fl-h" data-to="c{nd["n"]}" role="link" tabindex="0"><circle cx="{x + 10}" cy="24" r="10"/><text class="fl-hn" x="{x + 10}" y="28" text-anchor="middle">{nd["n"]}</text><text class="fl-ht" x="{x + 25}" y="28">{esc(nd["name"])}</text></g>')
    # 선(상자보다 먼저 그려 상자 뒤로 지나가게 한다)
    labs = []
    for s, d, lab, kind, opt in MAIN:
        p, lp = _path(s, d, opt)
        o.append(f'<path class="fl-e fl-{kind}{" fl-dash" if opt.get("dash") else ""}" d="{p}" marker-end="url(#fl-a-{kind})" data-s="{s}" data-d="{d}"><title>{esc(fid(s))} → {esc(fid(d))}: {esc(lab)}</title></path>')
        if opt.get("lab") and lp: labs.append(f'<text class="fl-lab fl-lab-{kind}" x="{lp[0]:.1f}" y="{lp[1]:.1f}" text-anchor="middle" data-s="{s}" data-d="{d}">{esc(opt["lab"])}</text>')
    for s, d, lab in AUX:
        o.append(f'<path class="fl-e fl-aux" d="{_aux_path(s, d)}" marker-end="url(#fl-a-aux)" data-s="{s}" data-d="{d}"><title>{esc(fid(s))} → {esc(fid(d))}: {esc(lab)}</title></path>')
    # 상자
    for k, (nd, i, f) in F.items():
        x, y = _xy(k); nm = SHORT.get(k, f["name"]); v = V[k]; y1 = y + (17 if len(v) == 2 else 20)
        o.append(f'<g class="fl-b" data-k="{k}" tabindex="0" role="button" aria-label="{esc(fid(k))} {esc(f["name"])}"><rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="8"/>'
                 f'<text class="fl-id" x="{x + 8}" y="{y1}">{fid(k)}</text><text class="fl-nm" x="{x + 33}" y="{y1}">{esc(nm)}</text>'
                 + "".join(f'<text class="fl-v" x="{x + 8}" y="{y1 + 14 + j * 12.5}">{esc(t)}</text>' for j, t in enumerate(v)) + "</g>")
    o += labs                                    # 이름표는 상자보다 위에 그린다
    # 범례
    ly = H - 16; lx = X0
    for kind, name in (("heat", "열"), ("mass", "증기 · 액의 양"), ("pres", "압력"), ("ctrl", "제어"), ("sup", "보조 입력")):
        o.append(f'<path class="fl-e fl-{kind}" d="M{lx} {ly}h30" marker-end="url(#fl-a-{kind})"/><text class="fl-lg" x="{lx + 38}" y="{ly + 4}">{name}</text>'); lx += 62 + len(name) * 11.5
    o.append(f'<text class="fl-lg" x="{W - 14}" y="{ly + 4}" text-anchor="end">숫자는 본류 구간({D["snap"]["30"]["PR"]["t_h"]:.0f} h)의 계산값 · 상자를 누르면 들어오는 값과 쓰이는 곳을 표시</text>')
    o.append("</svg>")
    data = dict(n={k: dict(id=fid(k), name=f["name"], sec=nd["name"], gets=f["gets"], val=f["val"], calc=f["use"]["calc"], sub=bool(f["use"]["sub"])) for k, (nd, i, f) in F.items()},
                l=[[s, d, lab, kind] for s, d, lab, kind in L], kind=KIND)
    return "".join(o), data


def check_words(NODES):
    """용도의 '계산' 글에 적힌 '식 N' · '구간 N'이 흐름도의 선과 맞는지 본다. 맞지 않는 것의 목록을 돌려준다(없으면 빈 목록).
    맞다는 것 = 글이 가리키는 식(또는 구간의 어느 식)과 이 식이 선으로 이어져 있거나, 두 식이 같은 식으로 값을 넘긴다."""
    import re
    F = {f["k"]: (nd["n"], i + 1, f) for nd in NODES for i, f in enumerate(nd["formulas"])}
    by = {(n, i): k for k, (n, i, f) in F.items()}; L = links(); adj = {k: set() for k in F}; out = {k: set() for k in F}
    for s, d, _, _ in L: adj[s].add(d); adj[d].add(s); out[s].add(d)
    bad = []
    for k, (n, i, f) in F.items():
        t = f["use"]["calc"]
        for m in re.finditer(r"식 (\d+)", t):
            tk = by.get((n, int(m.group(1))))
            if tk is None or tk == k: bad.append((k, m.group(0), "그런 식이 없다")); continue
            if tk not in adj[k] and not (out[k] & out[tk]): bad.append((k, m.group(0), f"{tk}와 선이 없다"))
        for m in re.finditer(r"구간 (\d+)", t):
            sec = int(m.group(1)); ks = {q for q, (nn, _, _) in F.items() if nn == sec}
            if not (adj[k] & ks): bad.append((k, m.group(0), "그 구간의 식과 선이 없다"))
    return bad
