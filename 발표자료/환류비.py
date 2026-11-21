# -*- coding: utf-8 -*-
"""환류비별 계산 결과 — 발표자료 '요약' 탭의 화면과 교과서의 절.

- 사용자 요구(2026-11-20): "이식으로했을때 환류비를 어느정도로하는게 좋은지 각 환류비별로 그래프같은것도 보여줄수있나"
- 숫자는 환류비_계산.py가 시뮬레이터를 직접 돌려 남긴 기록에서 읽는다(환류비_기록.json = 본류 구간의 환류비, 환류비_기록_초류.json = 초류 구간의 환류비).
- 그래프는 넷: 초류 환류비 → 본류의 저비점 불순물 · 초류 소요 시간, 본류 환류비 → 본류의 저비점 불순물 · 본류 소요 시간.
  불순물 그래프의 세로축은 로그 눈금이다(상대휘발도 1.5와 20의 값이 100배 넘게 차이 나서 보통 눈금으로는 20 쪽의 변화가 보이지 않는다).
- 저비점 불순물의 상대휘발도는 추정값이라 두 값으로 계산했다: 1.5(지금 입력 기본값) · 20(사내 검토서의 TDMAHf 증기압에 해당하는 값).
- 고비점 불순물은 계산에서 증발하지 않는 것으로 두므로, 환류가 고비점 혼입을 줄이는 효과는 이 결과에 없다. 글에 그렇게 밝힌다.
- 글의 판정('줄지 않는다', '늘어난다', '이 값부터는 더 줄지 않는다')은 숫자로 확인한 뒤에 적는다(judge의 assert).
"""
import json, math, pathlib
from 그림 import esc, text, svg_open, P
from 내용 import N, jo

HERE = pathlib.Path(__file__).resolve().parent
A_LO, A_HI = 1.5, 20.0
W_KNEE = 0.001          # 상대휘발도 20에서 '충분히 줄었다'고 보는 기준(wt%): 원료 0.3 %의 1/300. 표시 기준이며 제품 규격이 아니다
W_FLOOR = 0.0001        # 이보다 작은 값은 '0.0001 미만'으로 적고, 그래프에서는 맨 아래 눈금에 그린다


def Wt(v):
    """불순물 농도 표기(wt%): 0.01 이상은 소수 셋째 자리, 그 아래는 다섯째 자리(유효 숫자 두세 자리). 0.0001보다 작으면 '0.0001 미만'."""
    if v < W_FLOOR: return "0.0001 미만"
    return f"{v:.3f}" if v >= 0.01 else f"{v:.5f}"


def load():
    out = {}
    for part, fn in (("main", "환류비_기록.json"), ("fore", "환류비_기록_초류.json")):
        f = HERE / fn; assert f.exists(), f"{fn}이 없다 — python 환류비_계산.py --part {part} 를 먼저 돌릴 것"
        rec = json.loads(f.read_text(encoding="utf-8")); runs = rec["runs"]
        for r in runs:
            if "RDact" not in r: r["RDact"] = r["Rf"] / r["Pd"] if r.get("Pd") else 0.0
            r["x"] = r["RDact"]
            tot = r["feed"] * r["w0"]                                    # 투입한 저비점 불순물(kg × %)
            r["sF"] = r["fore"] * r["wF"] / tot * 100; r["sM"] = r["main"] * r["wM"] / tot * 100      # 초류 탱크 · 본류 탱크에 모인 비율(%)
        out[part] = dict(ver=rec["ver"], when=rec["when"], vtot=rec["vtot"], by={a: sorted([r for r in runs if abs(r["alpha"] - a) < 1e-9], key=lambda r: r["R"]) for a in (A_LO, A_HI)})
    return out


def db_rd(D):
    """DB 6배치의 환류비(환류 ÷ 유출, 유출은 무게 기준으로 보정)."""
    R = D["db"]["DBR"]; return dict(fore=R["RDfore"], main=R["RDmain"])


def judge(D, VER):
    S = load(); m, f = S["main"], S["fore"]; rd = db_rd(D)
    assert VER in m["ver"] and VER in f["ver"], f'환류비 기록의 판({m["ver"]})이 문서의 판({VER})과 다르다 — python 환류비_계산.py를 다시 돌릴 것'
    for part in (m, f):
        assert len(part["by"][A_LO]) >= 5 and len(part["by"][A_HI]) >= 5, "환류비 기록이 모자란다(상대휘발도마다 5점 이상)"
        assert [r["R"] for r in part["by"][A_LO]] == [r["R"] for r in part["by"][A_HI]], "두 상대휘발도의 환류 설정이 같아야 한다"
    ml, mh, fl, fh = m["by"][A_LO], m["by"][A_HI], f["by"][A_LO], f["by"][A_HI]
    base = next(r for r in ml if abs(r["R"] - 4) < 1e-9)                 # 기본 조건(본류 환류 4 · 유출 6, 초류 환류 4 · 유출 2)과 같은 설정으로 돈 경우
    j = dict(S=S, w0=ml[0]["w0"], base=base, base_m=base["x"], base_f=base["Rfore"] / base["Dfore"],
             main_w=[ml[0]["wM"], ml[-1]["wM"]], main_wh=[mh[0]["wM"], mh[-1]["wM"]], main_t=[ml[0]["t_main"], ml[-1]["t_main"]], main_x=[ml[0]["x"], ml[-1]["x"]], main_s=[ml[0]["wS"], ml[-1]["wS"]],
             fore_w=[fl[0]["wM"], fl[-1]["wM"]], fore_wh=[fh[0]["wM"], fh[-1]["wM"]], fore_t=[fl[0]["t_fore"], fl[-1]["t_fore"]], fore_x=[fl[0]["x"], fl[-1]["x"]],
             steam=[ml[0]["steamKg"], ml[-1]["steamKg"]], sF_lo=[min(r["sF"] for r in fl), max(r["sF"] for r in fl)], sF_hi=[min(r["sF"] for r in fh), max(r["sF"] for r in fh)])
    j["main_slope"] = (ml[-1]["t_main"] - ml[0]["t_main"]) / (ml[-1]["x"] - ml[0]["x"])          # 본류 환류비 1마다 늘어나는 본류 시간(h)
    j["wspan_lo"] = [min(r["wM"] for r in ml + fl), max(r["wM"] for r in ml + fl)]; j["wspan_hi"] = [min(r["wM"] for r in mh + fh), max(r["wM"] for r in mh + fh)]
    j["wmain_hi"] = [min(r["wM"] for r in mh), max(r["wM"] for r in mh)]
    # 상대휘발도 20에서 본류의 저비점 불순물이 기준(W_KNEE) 아래로 내려가는 첫 초류 환류비와 그 앞의 점
    k = next((i for i, r in enumerate(fh) if r["wM"] <= W_KNEE), None); assert k is not None and k >= 1, "상대휘발도 20에서 기준 아래로 내려가는 점이 없다 — 글을 다시 쓸 것"
    j["knee"], j["pre"] = fh[k], fh[k - 1]; j["knee_lo"] = fl[k]; j["last_hi"], j["last_lo"] = fh[-1], fl[-1]
    j["knee_in_db"] = rd["fore"][0] <= fh[k]["x"] <= rd["fore"][1]
    # 글의 근거
    assert all(b["t_main"] > a["t_main"] for a, b in zip(ml, ml[1:])) and all(b["t_fore"] > a["t_fore"] for a, b in zip(fl, fl[1:])), "환류비를 올리면 그 구간의 시간이 늘어난다는 글의 근거가 달라졌다"
    assert j["main_w"][1] >= j["main_w"][0] - 0.002 and j["main_wh"][1] >= j["main_wh"][0] - 0.0005, "본류 환류비를 올려도 본류의 저비점 불순물이 줄지 않는다는 글의 근거가 달라졌다"
    assert j["main_s"][1] < j["main_s"][0], "본류 환류비를 올리면 정제기 잔류의 저비점 불순물이 준다는 글의 근거가 달라졌다"
    assert j["fore_w"][1] < j["fore_w"][0] and (j["fore_w"][0] - j["fore_w"][1]) < 0.05, "상대휘발도 1.5에서는 초류 환류비를 올려도 조금만 준다는 글의 근거가 달라졌다"
    assert all(b["wM"] <= a["wM"] + 1e-9 for a, b in zip(fh, fh[1:])) and fh[0]["wM"] > 10 * W_KNEE, "상대휘발도 20에서 초류 환류비를 올리면 크게 준다는 글의 근거가 달라졌다"
    assert j["wspan_hi"][1] < j["wspan_lo"][0] / 3, "상대휘발도 20이면 본류의 저비점 불순물이 훨씬 낮다는 글의 근거가 달라졌다"
    assert j["knee_in_db"], "DB 6배치의 초류 환류비가 기준 아래로 내려가는 환류비를 포함한다는 글의 근거가 달라졌다 — 글을 다시 쓸 것"
    assert j["sF_lo"][1] < 25 and j["sF_hi"][0] > 50, "초류에 모이는 비율(상대휘발도 1.5는 4분의 1 미만, 20은 절반 이상)이 달라졌다"
    assert min(r["sM"] for r in fl + ml) > 75, "상대휘발도 1.5에서는 대부분이 본류로 넘어간다는 글의 근거가 달라졌다"
    return j


# ---------------------------------------------------------------- 그래프
def chart(fid, label, ser, ykey, xmax, xtick, ylab, xlab, ymax=None, ytick=None, logy=None, band=None, base=None, hline=None, d=2):
    """작은 꺾은선 그래프. ser = [(이름, 기록 목록, 선 종류, 점 종류, 이름을 둘 자리 dy)]. logy = (아래 끝, 위 끝)이면 세로축이 로그 눈금.
    band = DB의 환류비 범위, base = 기본 조건의 환류비, hline = (값, 이름)."""
    W_, H_ = 560, 252; x0, y0, pw, ph = 62, 28, 480, 172
    X = lambda v: x0 + min(v, xmax) / xmax * pw
    if logy:
        lo, hi = math.log10(logy[0]), math.log10(logy[1])
        Y = lambda v: y0 + ph - (math.log10(min(max(v, logy[0]), logy[1])) - lo) / (hi - lo) * ph
        yt = [(10.0 ** e, f"{10.0 ** e:.{max(0, -e)}f}") for e in range(round(lo), round(hi) + 1)]
    else:
        Y = lambda v: y0 + ph - min(v, ymax) / ymax * ph
        yt = []; k = 0
        while k * ytick <= ymax + 1e-9: v = k * ytick; yt.append((v, f"{v:.{d}f}" if d else f"{v:.0f}")); k += 1
    o = [svg_open(fid, W_, H_, label)]
    if band: o.append(f'<rect class="plot-band" x="{X(band[0]):.1f}" y="{y0}" width="{X(band[1]) - X(band[0]):.1f}" height="{ph}"/>' + text((X(band[0]) + X(band[1])) / 2, y0 + 12, f"DB {band[0]:.1f}~{band[1]:.1f}", "dbv"))
    for v, s in yt: o.append(f'<path class="plot-g" d="M{x0} {Y(v):.1f}H{x0 + pw}"/>' + text(x0 - 7, Y(v) + 4, s, "tk", "end"))
    k = 0
    while k * xtick <= xmax + 1e-9: v = k * xtick; o.append(text(X(v), y0 + ph + 16, f"{v:g}", "tk")); k += 1
    o.append(f'<path class="plot-ax" d="M{x0} {y0}V{y0 + ph}H{x0 + pw}"/>' + text(x0 + pw, y0 + ph + 36, xlab, "ts", "end") + text(x0 - 50, y0 - 12, ylab, "ts", "start"))
    if hline: o.append(f'<path class="plot-p3" d="M{x0} {Y(hline[0]):.1f}H{x0 + pw}"/>' + text(x0 + pw - 4, Y(hline[0]) - 5, hline[1], "markt", "end"))
    if base is not None: o.append(f'<path class="thin" d="M{X(base):.1f} {y0 + ph}V{y0 + ph + 6}"/>' + text(X(base), y0 + ph + 32, f"기본 조건 {base:.1f}", "nlv"))
    for name, rows, lc, pc, dy in ser:
        pts = [(X(r["x"]), Y(r[ykey])) for r in rows]
        tip = (lambda r: Wt(r[ykey]) + " %") if logy else (lambda r: f"{r[ykey]:.{d + 1}f}")
        o.append(f'<path class="{lc}" d="{P(pts)}"/>' + "".join(f'<circle class="{pc}" cx="{x:.1f}" cy="{y:.1f}" r="4"><title>환류비 {r["x"]:.2f} · {tip(r)}</title></circle>' for (x, y), r in zip(pts, rows)))
        if name: o.append(text(pts[-1][0] - 4, pts[-1][1] + dy, name, "ts" if lc != "plot-c" else "nl", "end"))
    o.append("</svg>"); return "".join(o)


def charts(D, VER):
    j = judge(D, VER); S = j["S"]; m, f = S["main"], S["fore"]; rd = db_rd(D)
    log = (W_FLOOR, 1.0); assert max(r["wM"] for part in (m, f) for a in (A_LO, A_HI) for r in part["by"][a]) < log[1]      # 0.0001 % 미만은 맨 아래 눈금에 그린다(글에 밝힘)
    two = lambda part: [(f"상대휘발도 {A_LO:g}", part["by"][A_LO], "plot-c", "pt-s2", 17), (f"상대휘발도 {A_HI:g}", part["by"][A_HI], "plot-c2", "pt-h", -10)]
    one = lambda part: [("", part["by"][A_LO], "plot-c", "pt-s2", 0)]
    fx = math.ceil(max(r["x"] for r in f["by"][A_LO])); mx = math.ceil(max(r["x"] for r in m["by"][A_LO]))
    tf = math.ceil(max(r["t_fore"] for r in f["by"][A_LO]) / 10) * 10; tm = math.ceil(max(r["t_main"] for r in m["by"][A_LO]) / 20) * 20
    feed = (j["w0"], f'원료 {j["w0"]:.2f} %'); yl = "본류의 저비점 불순물(wt%, 로그 눈금)"
    c = dict(
        fw=chart("fig-rr1", "초류 구간의 환류비와 본류의 저비점 불순물. 상대휘발도 20에서는 환류비를 올릴수록 크게 줄고, 1.5에서는 원료와 거의 같다", two(f), "wM", fx, 1 if fx <= 8 else 2, yl, "초류 구간의 환류비(환류 ÷ 유출)", logy=log, band=rd["fore"], base=j["base_f"], hline=feed),
        ft=chart("fig-rr2", "초류 구간의 환류비와 초류 소요 시간. 환류비를 올리면 초류 구간이 길어진다", one(f), "t_fore", fx, 1 if fx <= 8 else 2, "초류 소요 시간(h)", "초류 구간의 환류비(환류 ÷ 유출)", ymax=tf, ytick=10, band=rd["fore"], base=j["base_f"], d=0),
        mw=chart("fig-rr3", "본류 구간의 환류비와 본류의 저비점 불순물. 두 상대휘발도 모두 환류비를 올려도 줄지 않는다", two(m), "wM", mx, 0.5, yl, "본류 구간의 환류비(환류 ÷ 유출)", logy=log, band=rd["main"], base=j["base_m"], hline=feed),
        mt=chart("fig-rr4", "본류 구간의 환류비와 본류 소요 시간. 환류비에 비례해 길어진다", one(m), "t_main", mx, 0.5, "본류 소요 시간(h)", "본류 구간의 환류비(환류 ÷ 유출)", ymax=tm, ytick=20, band=rd["main"], base=j["base_m"], d=0))
    return c, j


def table(part, S):
    lo, hi = S[part]["by"][A_LO], S[part]["by"][A_HI]; cw = lambda v: "&lt; 0.0001" if v < W_FLOOR else Wt(v)      # 표의 칸은 숫자 글꼴이라 '미만'을 부등호로 적는다
    tr = "".join(f'<tr><td class="m">{a["R"]:g} · {a["D"]:.1f}</td><td class="m">{a["x"]:.2f}</td><td class="m">{a["t_fore"]:.1f}</td><td class="m">{a["t_main"]:.1f}</td><td class="m">{a["t_all"]:.1f}</td>'
                 f'<td class="m">{cw(a["wM"])}</td><td class="m">{cw(b["wM"])}</td><td class="m">{a["steamKg"]:.0f}</td></tr>' for a, b in zip(lo, hi))
    cap = "초류 구간의 환류비를 바꾼 계산" if part == "fore" else "본류 구간의 환류비를 바꾼 계산"
    return (f'<p class="small tcap">{cap}</p><div class="tw"><table class="cmp"><tr><th rowspan="2">환류 · 유출<br>설정(kg/h)</th><th rowspan="2">환류비<br>(계산 결과)</th><th colspan="3">소요 시간(h)</th>'
            f'<th colspan="2">본류의 저비점 불순물(%)</th><th rowspan="2">스팀<br>(kg)</th></tr><tr><th>초류</th><th>본류</th><th>전체</th><th>상대휘발도 {A_LO:g}</th><th>상대휘발도 {A_HI:g}</th></tr>{tr}</table></div>')


def texts(D, VER):
    j = judge(D, VER); rd = db_rd(D); S = j["S"]; fh = S["fore"]["by"][A_HI]; kn, pre, la = j["knee"], j["pre"], j["last_hi"]
    rdf = f"{rd['fore'][0]:.1f}~{rd['fore'][1]:.1f}"; rdm = f"{rd['main'][0]:.1f}~{rd['main'][1]:.1f}"
    xk = f"{kn['x']:.1f}"; xp = f"{pre['x']:.1f}"; xl = f"{la['x']:.1f}"; x1 = f"{j['main_x'][1]:.1f}"; xf1 = f"{j['fore_x'][1]:.1f}"
    more = "그 이상으로 올려도 더 줄어들 양이 거의 없고" if la["wM"] < kn["wM"] else "그 이상으로 올려도 더 줄지 않고"
    mh_ = f'{Wt(j["main_wh"][0])} %로 변화 없음' if Wt(j["main_wh"][0]) == Wt(j["main_wh"][1]) else f'{Wt(j["main_wh"][0])} → {Wt(j["main_wh"][1])} %'
    return dict(
        say=('시뮬레이터에서 환류 · 유출 설정만 바꿔 가며 한 배치씩 끝까지 계산했다. 본류의 저비점 불순물을 줄이는 것은 초류 구간의 환류비이고, 본류 구간의 환류비는 소요 시간만 늘린다. '
             '초류 구간의 환류비로 줄어드는 폭은 저비점 불순물의 상대휘발도(추정값)에 따라 크게 달라진다.'),
        fore=(f'상대휘발도 {A_HI:g}에서 본류의 저비점 불순물은 초류 환류비 {fh[0]["x"]:.0f}일 때 {Wt(fh[0]["wM"])} %, {xp}일 때 {Wt(pre["wM"])} %, {xk}일 때 {Wt(kn["wM"])} %다(원료 {j["w0"]:.2f} %). '
              f'상대휘발도 {A_LO:g}에서는 초류 환류비를 {j["fore_x"][0]:.0f}에서 {jo(xf1, "으로", "로")} 올려도 {Wt(j["fore_w"][0])} → {Wt(j["fore_w"][1])} %로 원료와 거의 같다. '
              f'초류 구간은 {N(j["fore_t"][0])} → {N(j["fore_t"][1])} h로 길어진다. DB 6배치의 초류 환류비는 {jo(rdf, "이다", "다")}.'),
        main=(f'본류 구간의 환류비를 {j["main_x"][0]:.0f}에서 {jo(x1, "으로", "로")} 올려도 본류의 저비점 불순물은 줄지 않는다(상대휘발도 {A_LO:g}: {Wt(j["main_w"][0])} → {Wt(j["main_w"][1])} %, {A_HI:g}: {mh_}). '
              f'본류 구간은 {N(j["main_t"][0])} → {N(j["main_t"][1])} h로, 환류비가 1 오를 때마다 약 {N(j["main_slope"], 0)} h씩 길어진다. DB 6배치의 본류 환류비는 {jo(rdm, "이다", "다")}.'),
        v_fore=(f'초류 구간: 상대휘발도 {A_HI:g} 기준으로 환류비 {xk}에서 본류의 저비점 불순물이 {Wt(kn["wM"])} %까지 내려간다. {more} 초류 구간만 길어진다(환류비 {xk} → {xl}에서 {N(kn["t_fore"])} → {N(la["t_fore"])} h). '
                f'DB 6배치의 초류 환류비 {jo(rdf, "은", "는")} 이 값을 포함한다.'),
        v_main=(f'본류 구간: 환류비를 올려도 본류의 저비점 불순물은 줄지 않는다. 환류가 늘면 정제기에 남던 저비점 불순물이 본류로 넘어오기 때문이다(잔류액의 저비점 불순물 {Wt(j["main_s"][0])} → {Wt(j["main_s"][1])} %). '
                f'소요 시간은 환류비가 1 오를 때마다 약 {N(j["main_slope"], 0)} h씩, 스팀 사용량은 {N(j["steam"][0], 0)} → {N(j["steam"][1], 0)} kg으로 늘어난다.'),
        v_why=(f'초류 30 kg에 모이는 저비점 불순물은 상대휘발도 {A_LO:g}에서 투입량의 {N(j["sF_lo"][0], 0)}~{N(j["sF_lo"][1], 0)} %, {A_HI:g}에서 {N(j["sF_hi"][0], 0)}~{N(j["sF_hi"][1], 0)} %다. '
               f'상대휘발도가 {A_LO:g}이면 초류를 30 kg 받아서는 환류비와 관계없이 저비점 불순물 대부분이 본류로 넘어간다.'),
        limit=('본류 구간의 환류는 고비점 불순물의 혼입을 줄이는 역할을 한다. 이 계산은 고비점 불순물이 증발하지 않고, 비말 동반으로 넘어가는 양도 없는 것으로 두므로 그 효과가 결과에 반영되지 않는다. '
               '따라서 이 결과만으로 본류 환류비를 낮추기로 정할 수는 없으며, 컷별 성분 분석으로 불순물별 거동을 확인한 뒤에 판단한다.'),
        alpha=(f'상대휘발도 {A_LO:g}는 현재 입력 기본값이고, {A_HI:g}은 사내 검토서의 TDMAHf 증기압에 해당하는 값이다. 두 값 모두 추정값이며 컷별 성분 분석으로 정한다.'),
        how=(f'본류 계산은 환류 + 유출을 {S["main"]["vtot"]:g} kg/h로 고정하고 환류만 바꿨으며, 본류 끝의 유출 감소(6 → 5 kg/h)는 반영하지 않았다. 초류 계산은 환류 + 유출을 {S["fore"]["vtot"]:g} kg/h로 두었다. '
             '초류 구간에서는 스팀 밸브가 하한 개도에 있어 증발량이 설정과 조금 다르므로, 가로축에는 계산 결과의 환류비를 썼다. 나머지 조건은 기본 조건(투입 350 kg, 초류 30 kg, 후류 30 kg)과 같다.'),
        legend='초록색 띠는 DB 6배치의 환류비 범위(유출은 무게 기준으로 보정), 가로축 아래의 기본 조건은 현재 레시피로 계산한 환류비다. 불순물 그래프의 세로축은 로그 눈금이며, 0.0001 % 미만은 맨 아래 눈금에 그렸다.')


def scene_rr(D, VER):
    """발표자료 '요약' 탭의 화면."""
    c, j = charts(D, VER); t = texts(D, VER); S = j["S"]
    fig = lambda svg: f'<figure class="plain"><div class="scroll">{svg}</div></figure>'
    return ('<section class="scene" id="rr" data-tab="sm" hidden><div class="sh"><h2>환류비별 계산 결과</h2>' f'<span class="tag">환류 · 유출 설정만 바꾼 배치 계산 {sum(len(v) for p in S.values() for v in p["by"].values())}회 · {esc(VER)}</span></div>'
            '<p class="q">환류비에 따른 본류의 저비점 불순물과 소요 시간</p>' f'<p class="say">{esc(t["say"])}</p>'
            '<div class="grid2"><div class="blk"><h3>초류 구간의 환류비 <small>본류는 기본 조건</small></h3>' f'{fig(c["fw"])}{fig(c["ft"])}<p class="small">{esc(t["fore"])}</p></div>'
            '<div class="blk"><h3>본류 구간의 환류비 <small>초류는 기본 조건</small></h3>' f'{fig(c["mw"])}{fig(c["mt"])}<p class="small">{esc(t["main"])}</p></div></div>'
            '<div class="grid2"><div class="blk"><h3>환류비 판단 <span class="bdg b-hard">추정</span></h3>' f'<ul class="pl"><li>{esc(t["v_fore"])}</li><li>{esc(t["v_main"])}</li><li>{esc(t["v_why"])}</li><li>{esc(t["limit"])}</li></ul>'
            f'<p class="small">{esc(t["alpha"])}</p><p class="small">{esc(t["legend"])} {esc(t["how"])}</p></div>'
            '<div class="blk"><h3>계산 결과 표 <small>시뮬레이터를 직접 돌린 기록</small></h3>' f'{table("fore", S)}{table("main", S)}</div></div></section>')


def section(D, VER):
    """교과서의 절."""
    c, j = charts(D, VER); t = texts(D, VER)
    fig = lambda svg: f'<figure class="plain"><div class="scroll">{svg}</div></figure>'
    return ('<section class="ch" id="rr"><div class="sh"><h2>환류비별 계산 결과</h2>' f'<span class="tag">환류 · 유출 설정만 바꾼 배치 계산 · {esc(VER)}</span></div>'
            f'<p class="say">{esc(t["say"])}</p>'
            '<div class="grid2"><div class="blk"><h3>초류 구간의 환류비 <small>본류는 기본 조건</small></h3>' f'{fig(c["fw"])}{fig(c["ft"])}<p>{esc(t["fore"])}</p></div>'
            '<div class="blk"><h3>본류 구간의 환류비 <small>초류는 기본 조건</small></h3>' f'{fig(c["mw"])}{fig(c["mt"])}<p>{esc(t["main"])}</p></div></div>'
            f'<div class="blk"><h3>환류비 판단</h3><ul class="pl"><li>{esc(t["v_fore"])}</li><li>{esc(t["v_main"])}</li><li>{esc(t["v_why"])}</li><li>{esc(t["limit"])}</li></ul>'
            f'<p class="small">{esc(t["alpha"])} {esc(t["legend"])} {esc(t["how"])} 경우별 숫자는 발표자료의 요약 화면에 있다.</p></div></section>')
