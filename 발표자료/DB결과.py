# -*- coding: utf-8 -*-
"""DB 6배치 분석 결과 — 발표자료 'DB 데이터 활용' 탭의 첫 화면과, 다른 화면이 함께 쓰는 비교표 · 문장.

- DB 값은 DB값.json, 계산값은 값.json · 점검 기록, 상수 계산은 DB_맞춤.py, 시험 계산은 시험계산_기록.json에서 읽는다. 숫자를 손으로 옮겨 적지 않는다.
- 시험 계산은 시뮬레이터 기본값을 바꾸지 않고 실행 중에 증기압식의 상수 A만 바꿔 넣은 계산이다(시험계산.py).
- 글의 판정('범위에 든다', '높다', '짧아진다')은 숫자로 확인한 뒤에 적는다(judge의 assert).
"""
import math
from 그림 import esc, text, tw, tagbub, svg_open, P
from 설비도 import plant
from 내용 import N, PIMS, jo
import DB_맞춤 as F

BATCH = lambda b: "26#" + b
f2 = lambda x: f"{x:.2f}"


def rg(v, d=1):
    lo, hi = v
    return f"{lo:,.{d}f}" if abs(hi - lo) < 0.5 * 10 ** -d else f"{lo:,.{d}f}~{hi:,.{d}f}"


def inside(v, r, tol=0.0):
    return r[0] - tol <= v <= r[1] + tol


def trial(db, VER=None):
    """시험 계산 기록에서 (기준 계산, 상수를 바꾼 계산)의 요약을 꺼낸다."""
    T = db.get("trial"); assert T, "시험계산_기록.json이 없다 — python 시험계산.py 11.87 12.41 을 먼저 돌릴 것"
    key = f'{db["A_use"]:.2f}'; assert key in T["runs"], f"시험 계산에 A = {key} 기록이 없다(있는 것: {list(T['runs'])}) — python 시험계산.py {key} --add"
    base, new = T["runs"][T["base"]]["sum"], T["runs"][key]["sum"]
    assert abs(base["A"] - db["A0"]) < 1e-9, "시험 계산의 기준 상수가 지금 증기압식과 다르다"
    if VER: assert VER in base["ver"] and VER in new["ver"], f'시험 계산의 판({base["ver"]})이 발표자료의 판({VER})과 다르다 — python 시험계산.py를 다시 돌릴 것'
    S = db["SIM"]
    assert abs(base["Tmain"] - S["Tmain"]) < 0.3 and abs(base["ThMain"] - S["ThMain"]) < 0.3 and abs(base["t_all"] - S["t_all"]) < 0.5, "기준 시험 계산이 점검 기록의 배치 끝 값과 다르다"
    return base, new


def judge(db, VER=None):
    """발표 문장에 쓰는 판정. 숫자가 달라져 판정이 바뀌면 여기서 멈춘다."""
    R = db["DBR"]; S = db["SIM"]; M = db["DBM"]; b, n = trial(db, VER)
    j = dict(dT_main=[S["Tmain"] - R["Tmain"][1], S["Tmain"] - R["Tmain"][0]], dT_top=[S["ThMain"] - R["ThMain"][1], S["ThMain"] - R["ThMain"][0]],
             V_in=inside(S["Vfore"], R["Vfore"]) and inside(S["Vmain"], R["Vmain"]),
             t_in=inside(S["t_tr"], R["t_tr"]) and inside(S["t_fore"], R["t_fore"]) and inside(S["t_main"], R["t_main"]),
             D_over=S["Dmain"] - R["Dmain"][1], trial_in=inside(n["Tmain"], R["Tmain"]) and inside(n["Tfore"], R["Tfore"]), trial_gap=n["Tmain"] - db["T_at_trialV"],
             ex_low=M["ThMain"] - n["Tex30"], ex_edge=n["Tex30"] - R["ThMain"][0], m2_in=inside(n["m2_30"], R["m2"]),
             fore_short=S["t_fore"] - n["t_fore"], main_same=abs(n["t_main"] - S["t_main"]), Dfore_up=n["Dfore"] - S["Dfore"], dTj=[n["TjMain"] - R["TjMain"][1], n["TjMain"] - R["TjMain"][0]])
    assert j["dT_main"][0] > 10 and j["dT_top"][0] > 20, "계산 온도가 DB보다 높다는 글의 근거가 달라졌다"
    assert j["V_in"] and j["t_in"], "증발량 · 구간 소요 시간이 DB 범위 안이라는 글의 근거가 달라졌다"
    assert 0 <= j["D_over"] < 0.3, "본류 유출의 계산값이 DB 지시값 상한과 0.3 kg/h 안에서 같다는 글의 근거가 달라졌다"
    assert j["trial_in"], f'시험 계산의 내부 온도({n["Tfore"]:.1f} · {n["Tmain"]:.1f} ℃)가 DB 범위를 벗어났다 — 글을 고칠 것'
    assert abs(j["trial_gap"]) < 0.3, f'시험 계산의 본류 내부 온도가 같은 증발량의 DB 관계와 {j["trial_gap"]:.2f} ℃ 다르다 — 상수를 다시 구할 것'
    assert abs(j["ex_edge"]) < 0.3 and 0 < j["ex_low"] < 3, f'배관 출구 포화 온도가 DB 탑 온도의 하한 수준이라는 글의 근거가 달라졌다({j["ex_edge"]:.2f}, {j["ex_low"]:.2f})'
    assert j["m2_in"], "시험 계산의 2차 응축기 유입량이 DB 범위 안이라는 글의 근거가 달라졌다"
    assert j["fore_short"] > 0.5 and j["main_same"] < 1 and j["Dfore_up"] > 0.2, "시험 계산에서 초류 구간이 짧아진다는 글의 근거가 달라졌다"
    assert 0 < j["dTj"][0] < 5, "시험 계산의 자켓 온도가 DB보다 조금 높다는 글의 근거가 달라졌다"
    return j


def cmp_rows(D):
    """계산값과 DB 6배치의 비교표. 줄 = dict(k, name, db, sim, trial, why). db · sim · trial은 칸 안의 줄 목록이다."""
    db = D["db"]; R = db["DBR"]; S = db["SIM"]; b, n = trial(db); G = D["dbv"]["범위"]
    return [
        dict(k="T", name="내부 온도 TICH071", db=[f'초류 {rg(R["Tfore"])} ℃', f'본류 {rg(R["Tmain"])} ℃'], sim=[f'초류 {N(S["Tfore"])} ℃', f'본류 {N(S["Tmain"])} ℃'],
             trial=[f'초류 {N(n["Tfore"])} ℃', f'본류 {N(n["Tmain"])} ℃'], why="증기압식의 상수 A"),
        dict(k="Th", name="탑 온도 TIH075", db=[f'초류 {rg(R["ThFore"])} ℃', f'본류 {rg(R["ThMain"])} ℃'], sim=[f'초류 {N(S["ThFore"])} ℃', f'본류 {N(S["ThMain"])} ℃', "(컬럼 상부)"],
             trial=[f'본류 {N(n["ThMain"])} ℃(컬럼 상부)', f'본류 {N(n["Tex30"])} ℃(배관 출구)'], why="증기압식의 상수 A, 온도계 설치 위치"),
        dict(k="Tj", name="자켓 온도 TIH074", db=[f'초류 {rg(R["TjFore"])} ℃', f'본류 {rg(R["TjMain"])} ℃'], sim=[f'초류 {N(b["TjFore"])} ℃', f'본류 {N(b["TjMain"])} ℃'],
             trial=[f'초류 {N(n["TjFore"])} ℃', f'본류 {N(n["TjMain"])} ℃'], why="증기압식의 상수 A(자켓 온도는 내부 온도를 따라간다)"),
        dict(k="RD", name="환류 · 유출(kg/h)", db=[f'초류 {rg(R["Rfore"])} · {rg(R["Dfore"])}', f'본류 {rg(R["Rmain"])} · {rg(R["Dmain"])}'],
             sim=[f'초류 {N(S["Rfore"], 2)} · {N(S["Dfore"], 2)}', f'본류 {N(S["Rmain"], 2)} · {N(S["Dmain"], 2)}'], trial=[f'초류 {N(n["Rfore"], 2)} · {N(n["Dfore"], 2)}', f'본류 {N(n["Rmain"], 2)} · {N(n["Dmain"], 2)}'],
             why="운전 기준의 설정값(환류 4, 유출 2 → 6 → 5 kg/h), 스팀 밸브 특성식"),
        dict(k="t", name="구간 소요 시간", db=[f'전환류 {rg(R["t_tr"])} h', f'초류 {rg(R["t_fore"])} h', f'본류 {rg(R["t_main"])} h'],
             sim=[f'전환류 {N(S["t_tr"])} h', f'초류 {N(S["t_fore"])} h', f'본류 {N(S["t_main"])} h'], trial=[f'전환류 {N(n["t_tr"])} h', f'초류 {N(n["t_fore"])} h', f'본류 {N(n["t_main"])} h'],
             why=f'투입량(DB {rg(R["feed"], 0)} kg, 계산 {N(S["feed"], 0)} kg)과 초류량(DB {rg(R["fore"])} kg, 계산 {N(S["fore"], 0)} kg)'),
        dict(k="heat", name="승온", db=[f'90 ℃ 도달 {rg(R["t_heat"])} h', f'자켓 최고 {rg(G["자켓_승온_최고"], 0)} ℃'],
             sim=[f'90 ℃ 도달 {N(b["t90"], 2)} h', f'자켓 최고 {N(b["tjMax"])} ℃'], trial=[f'90 ℃ 도달 {N(n["t90"], 2)} h', f'자켓 최고 {N(n["tjMax"])} ℃'], why="스팀 밸브 특성식(가정), 스팀 제어 방식, 승온 시작 온도"),
        dict(k="T1", name="응축액 출구 온도 TICH071D", db=[f'본류 {rg(R["T1main"])} ℃'], sim=[f'본류 {N(S["T1main"])} ℃'], trial=[f'본류 {N(n["T1main"])} ℃'], why="출구 배관의 열손실(계산에 없음)"),
        dict(k="m2", name="2차 응축기 유입량", db=[f'{R["m2"][0]}~{R["m2"][1]} kg/h'], sim=[f'{b["m2_30"]:.4f} kg/h'], trial=[f'{n["m2_30"]:.4f} kg/h'], why="1차 응축기 출구 온도에서의 증기압(상수 A), 리크 유입량(가정)"),
    ]


def cell(lines):
    """비교표 한 칸: 줄마다 줄바꿈."""
    return "<br>".join(esc(x) for x in lines)


# ---------------------------------------------------------------- 수집 항목마다의 6배치 결과(구간 번호 · 태그 글로 찾는다)
def attach(D, NODES):
    """NODES의 db 항목마다 st(ok 확인 · part 일부 확인 · no 자료 없음)와 got(6배치에서 확인한 내용)을 붙인다."""
    db = D["db"]; V = D["dbv"]; R = db["DBR"]; G = V["범위"]; b, n = trial(db); cv = db["VPsd"] / db["VPmean"] * 100
    kr = [k for k in V["FICH072_무게_적분_비"] if k is not None]
    M = {
        (1, "TICH071_MV"): ("no", "개도와 스팀 유량의 시계열은 이번 분석 문서에 없다."),
        (1, "TICH071 · TIH074"): ("part", f'승온 속도 {rg(G["승온_기울기"])} ℃/분, 자켓 최고 {rg(G["자켓_승온_최고"], 0)} ℃, 90 ℃ 도달 {rg(R["t_heat"])} h(계산 {N(b["t90"], 2)} h). 식의 계수 a · b는 시계열 회귀로 구한다.'),
        (1, "TICH071(스팀 차단"): ("no", "냉각 구간은 이번 분석 문서에 없다."),
        (2, "FICH073 + FICH072"): ("ok", f'증발량 ÷ 증기압이 12점에서 {N(db["VPmean"])} ± {jo(N(db["VPsd"]), "으로", "로")} 일정하다(변동 {cv:.0f} %). 증기 배관 식으로 구한 상수 A는 {jo(f2(db["A_use"]), "이다", "다")}(현재 {db["A0"]}).'),
        (2, "TICH071 · PICH071"): ("no", "PICH071 기록은 배치마다 단위와 스케일이 달라 쓸 수 없다. 기울기 B와 영점 오차는 정하지 못했다."),
        (3, "원료 · 초류"): ("no", "성분 분석 자료는 이번 분석 문서에 없다."),
        (3, "WIH071(전환류"): ("part", f'WIH071은 승온 중 내부 온도 1 ℃당 약 {G["WIH071_증가_대표"]} kg 높게 지시한다(승온 전체로 {rg(G["WIH071_승온중_증가_kg"], 0)} kg). 이 영향을 보정해야 홀드업을 분리할 수 있다.'),
        (3, "TICH071 · TIH075"): ("ok", f'내부 온도 − 탑 온도는 초류 {rg(R["dTfore"])} ℃, 본류 {rg(R["dTmain"])} ℃다. 본류의 온도 차를 증기압의 비로 환산하면 {jo(rg(db["pr_main"], 2), "이다", "다")}.'),
        (4, "TE-H075"): ("part", f'본류의 압력비 {jo(rg(db["pr_main"], 2), "은", "는")} 계산상 정제기 ÷ 배관 출구({N(db["sim_pr_exit"], 2)})에 가깝다. TE-H075는 증기 배관 출구 쪽에 있는 것으로 보이며 현장 확인이 필요하다.'),
        (4, "FICH073 + FICH072"): ("ok", f'12점(증발량 {rg(db["Vrng"], 2)} kg/h)에서 증발량 ÷ 증기압의 변동이 {cv:.0f} %다. 증기 배관 식으로 계산하면 12점 모두 출구 초킹 조건이다.'),
        (5, "TICH071D · TICH364"): ("part", f'TICH071D는 본류에서 {rg(R["T1main"])} ℃로 N-Brine 50 ℃보다 낮다. TICH364는 값이 없다.'),
        (5, "냉매 출구"): ("no", "온도계가 없다."),
        (6, "FICH073 · FICH072"): ("ok", f'초류 중 유출 {rg(R["Dfore"])}(설정 {G["초류_유출_SV"]}) · 환류 {rg(R["Rfore"])} kg/h, 본류 중 유출 {rg(R["Dmain"])} · 환류 {rg(R["Rmain"])} kg/h.'),
        (6, "WIH072 · WIH073"): ("ok", f'초류 · 본류 무게 ÷ FICH072 유량 적분값이 {min(kr):.2f}~{max(kr):.2f}다. FICH072 지시값이 무게 기준보다 높다.'),
        (6, "TICH071_MV · 단계"): ("part", f'TICH071이 {rg(G["내부온도_제어"], 0)} ℃에 도달한 뒤 그 부근에서 유지된다(내부 온도 제어). 개도와 설정값의 기록은 없다.'),
        (7, "PIH093"): ("no", "PIH093 지시값이 −1로 고정되어 있어 쓸 수 없다."),
        (7, "PICH071 · PIH093"): ("no", "두 압력계 기록 모두 쓸 수 없다."),
        (8, "원료 · 초류"): ("no", "성분 분석 자료는 이번 분석 문서에 없다."),
        (8, "WIH071 · WIH072"): ("ok", f'초류 {rg(R["fore"])} kg(투입의 {rg(R["forePct"], 0)} %), 본류 {rg(R["main"], 0)} kg, 본류 종료 후 잔량 {rg(R["left"], 0)} kg(5배치).'),
    }
    used = set()
    for nd in NODES:
        for d in nd["db"]:
            hit = [k for k in M if k[0] == nd["n"] and d["tags"].startswith(k[1])]
            assert len(hit) == 1, (nd["n"], d["tags"], hit)
            d["st"], d["got"] = M[hit[0]]; used.add(hit[0])
    assert used == set(M), set(M) - used
    return NODES


ST = {"ok": ("확인", "b-db"), "part": ("일부 확인", "b-est"), "no": ("확인 불가", "b-hard")}      # 확인 불가 = 기록이 없거나, 있어도 쓸 수 없음
def st_count(NODES):
    c = {k: 0 for k in ST}
    for nd in NODES:
        for d in nd["db"]: c[d["st"]] += 1
    return c


# ---------------------------------------------------------------- 그림 1: 계기 위치별 DB 값과 계산값(본류 구간)
def _tv(x, y, tag, l1, l2=None, anchor="start", cls="tgd", c1="dbv", c2="cvi", below=False):
    w = tw(tag, 10.5) + 12; out = tagbub(x, y, tag, anchor, cls)
    if below:
        an = "middle" if anchor == "middle" else "start"; xx = x if anchor in ("middle", "start") else x - w
        return out + text(xx, y + 23, l1, c1, an) + (text(xx, y + 37, l2, c2, an) if l2 else "")
    xx = x + w + 6 if anchor == "start" else x - w - 6
    return out + text(xx, (y - 2) if l2 else y + 4, l1, c1, anchor) + (text(xx, y + 12, l2, c2, anchor) if l2 else "")


def _cv(val, r, d=1, unit=""):
    lo, hi = r; mark = " ▲" if val > hi + 1e-9 else (" ▼" if val < lo - 1e-9 else "")
    return f"계산 {val:,.{d}f}{unit}{mark}", ("cvo" if mark else "cvi")


def fig_dr(D):
    db = D["db"]; R = db["DBR"]; S = db["SIM"]; b, _ = trial(db); fid = "fig-dr"
    o = [svg_open(fid, 1200, 690, "계기 위치별 DB 6배치 값(본류 구간)과 시뮬레이터 계산값. 온도는 계산값이 높고 환류 유량과 회수량은 DB 범위 안에 있다", y0=36)]
    o.append(plant(fid, level=0.57, main=0.3, fore=0.3, flows=(), tags=True))
    def two(x, y, tag, dbt, val, r, d=1, unit="", **kw):
        l2, c2 = _cv(val, r, d, unit); return _tv(x, y, tag, f"DB {dbt}{unit}", l2, c2=c2, **kw)
    o.append(two(400, 52, "TIH075", rg(R["ThMain"]), S["ThMain"], R["ThMain"], unit=" ℃"))
    o.append(two(14, 440, "TIH074", rg(R["TjMain"]), b["TjMain"], R["TjMain"], unit=" ℃", below=True))
    o.append(_tv(228, 372, "SICAH071", f'DB {D["dbv"]["교반_rpm"][0]} rpm', f'계산 {N(D["snap"]["30"]["CUR"]["N"] * 60, 0)} rpm(입력)', anchor="end"))
    o.append(two(386, 476, "TICH071", rg(R["Tmain"]), S["Tmain"], R["Tmain"], unit=" ℃"))
    o.append(_tv(386, 508, "PICH071", "기록 사용 불가", cls="tgx", c1="ts"))
    o.append(two(386, 540, "WIH071", rg(R["feed"], 0), S["feed"], R["feed"], d=0, unit=" kg", below=True))
    o.append(two(400, 394, "FICH073", rg(R["Rmain"]), S["Rmain"], R["Rmain"], unit=" kg/h"))
    o.append(two(624, 362, "FICH072", rg(R["Dmain"]), S["Dmain"], R["Dmain"], unit=" kg/h"))
    o.append(two(624, 282, "TICH071D", rg(R["T1main"]), S["T1main"], R["T1main"], unit=" ℃"))
    o.append(_tv(540, 228, "TICH364", "DB 값 없음", anchor="end", cls="tgx", c1="ts"))
    o.append(_tv(896, 282, "TIH353", "DB 값 없음", anchor="middle", cls="tgx", c1="ts", below=True))
    o.append(two(610, 540, "WIH073", rg(R["main"], 0), S["main"], R["main"], d=0, unit=" kg", anchor="middle", below=True))
    o.append(tagbub(775, 560, "WIH072", "middle", "tgd"))
    l2, c2 = _cv(S["fore"], R["fore"], 1, " kg"); o.append(text(826, 558, f'DB {rg(R["fore"])} kg', "dbv", "start") + text(826, 572, l2, c2, "start"))
    l2, c2 = _cv(b["m2_30"], R["m2"], 4, " kg/h")
    o.append(text(862, 486, "2차 응축기 → 초류 탱크", "ts") + text(862, 500, f'DB {R["m2"][0]}~{R["m2"][1]} kg/h', "dbv") + text(862, 514, l2, c2))
    o.append(_tv(1040, 240, "PIH093", "기록 사용 불가", anchor="middle", cls="tgx", c1="ts", below=True))
    o.append("</svg>"); return "".join(o)


# ---------------------------------------------------------------- 그림 2: 증발량과 내부 온도(DB 12점 · 계산선 두 가지)
def _curve(A, sub, Rr, Vs, anchor):
    """계산선: 증기 배관 식 + 충전층 압력 손실로 구한 정제기 압력이 내부 온도의 증기압과 같아지는 (내부 온도, 증발량).
    배관 유량은 시뮬레이터 방식(환류 + 유출 + 과냉 환류가 응축시키는 양). 기록의 한 점 anchor = (증발량, 정제기 압력, 내부 온도)를 지나도록 압력을 맞춘다."""
    pm = lambda V, Tk: F.p_still(F.line_top(V + sub * Rr, Tk)["Ptop"], V + sub * Rr, Tk)
    Va, Pa, Ta = anchor; k = Pa / pm(Va, Ta + 273.15); out = []
    for V in Vs:
        T = Ta
        for _ in range(6): T = F.tsat(k * pm(V, T + 273.15), A)
        out.append((T, V))
    return out, k


def fig_vt(D, VER):
    db = D["db"]; S = db["SIM"]; b, n = trial(db); fid = "fig-vt"; W_, H_ = 640, 400
    x0, y0, pw, ph = 62, 30, 548, 296; Tmin, Tmax, Vmin, Vmax = 92.0, 122.0, 4.0, 12.0
    X = lambda T: x0 + (T - Tmin) / (Tmax - Tmin) * pw; Y = lambda V: y0 + ph - (V - Vmin) / (Vmax - Vmin) * ph
    Tdb = F.T_of_V(S["V30"]); gap = S["T30"] - Tdb
    o = [svg_open(fid, W_, H_, f"증발량과 내부 온도의 관계. DB 12점은 상수 A {db['A_use']:.2f}의 계산선 주위에 있고, 현재 식의 계산선은 같은 증발량에서 약 {gap:.0f} ℃ 높다")]
    for v in (4, 6, 8, 10, 12): o.append(f'<path class="plot-g" d="M{x0} {Y(v):.1f}H{x0 + pw}"/>' + text(x0 - 8, Y(v) + 4, f"{v}", "tk", "end"))
    for t in (95, 100, 105, 110, 115, 120): o.append(f'<path class="plot-g" d="M{X(t):.1f} {y0}V{y0 + ph}"/>' + text(X(t), y0 + ph + 17, f"{t}", "tk"))
    o.append(f'<path class="plot-ax" d="M{x0} {y0}V{y0 + ph}H{x0 + pw}"/>')
    o.append(text(x0 + pw, y0 + ph + 38, "내부 온도 TICH071 (℃)", "ts", "end") + text(x0 - 46, y0 - 12, "환류 + 유출 (kg/h)", "ts", "start"))
    Vs = [4.6 + i * 0.2 for i in range(36)]
    old, k0 = _curve(db["A0"], S["sub"], S["Rmain"], Vs, (S["V30"], S["Pstill"], S["T30"])); new, k1 = _curve(db["A_use"], n["sub30"], n["Rmain"], Vs, (n["V30"], n["Pstill30"], n["T30"]))
    assert abs(k0 - 1) < 0.02 and abs(k1 - 1) < 0.06, ("옮긴 식의 압력이 시뮬레이터 기록과 다르다", k0, k1)
    cut = lambda c: [p for p in c if Tmin <= p[0] <= Tmax and p[1] <= Vmax]; old, new = cut(old), cut(new)
    o.append(f'<path class="plot-c" d="{P([(X(t), Y(v)) for t, v in old])}"/>' + f'<path class="plot-c3" d="{P([(X(t), Y(v)) for t, v in new])}"/>')
    for p in db["pts"]:
        o.append(f'<circle class="{"pt-m" if p["ph"] == "본류" else "pt-f"}" cx="{X(p["T"]):.1f}" cy="{Y(p["V"]):.1f}" r="5"><title>{esc(BATCH(p["b"]))} {p["ph"]} · {p["T"]} ℃ · {p["V"]:.2f} kg/h</title></circle>')
    kq = db["kmean"]
    for T, V in ((PIMS["T"], PIMS["R"] + PIMS["D"] * kq), (D["extra"]["plant_T"], D["pims_main"][0] + D["pims_main"][1] * kq)):
        o.append(f'<path class="pt-p" d="M{X(T):.1f} {Y(V) - 6:.1f}l6 6l-6 6l-6 -6z"/>')
    o.append(f'<rect class="pt-s" x="{X(S["T30"]) - 5:.1f}" y="{Y(S["V30"]) - 5:.1f}" width="10" height="10"/>' + f'<rect class="pt-t" x="{X(n["T30"]) - 5:.1f}" y="{Y(n["V30"]) - 5:.1f}" width="10" height="10"/>')
    # 곡선 이름(선 끝), 계산점 이름, 온도 차 표시
    o.append(text(X(new[-1][0]) + 12, Y(new[-1][1]) + 6, f"상수 A {db['A_use']:.2f}의 계산선", "nlv", "start") + text(X(old[-1][0]) - 12, Y(old[-1][1]) + 6, f"현재 식(A {db['A0']})의 계산선", "nl", "end"))
    o.append(text(X(S["T30"]) + 12, Y(S["V30"]) + 24, f"계산 {VER}", "nl", "start") + text(X(S["T30"]) + 12, Y(S["V30"]) + 39, f"{N(S['T30'])} ℃", "tnum", "start"))
    o.append(text(X(n["T30"]) + 12, Y(n["V30"]) + 20, f"시험 계산 {N(n['T30'])} ℃", "nlv", "start"))
    ya = Y(S["V30"]); xa, xb = X(Tdb) + 10, X(S["T30"]) - 10
    o.append(f'<path class="plot-p3" d="M{xa:.1f} {ya:.1f}H{xb:.1f}"/>' + text((xa + xb) / 2, ya - 8, f"같은 증발량에서 {gap:.0f} ℃ 차이", "markt"))
    lx, ly = X(103.6), Y(6.9)
    o.append(f'<circle class="pt-m" cx="{lx}" cy="{ly}" r="5"/>' + text(lx + 12, ly + 4, "DB 본류(6배치)", "ts", "start") + f'<circle class="pt-f" cx="{lx}" cy="{ly + 20}" r="5"/>' + text(lx + 12, ly + 24, "DB 초류(6배치)", "ts", "start")
             + f'<path class="pt-p" d="M{lx} {ly + 34}l6 6l-6 6l-6 -6z"/>' + text(lx + 12, ly + 44, "PIMS 화면 2점", "ts", "start"))
    o.append("</svg>"); return "".join(o)


# ---------------------------------------------------------------- 막대: 배치별 구간 소요 시간
def bars(D, VER):
    V = D["dbv"]; db = D["db"]; S = db["SIM"]; mx = max(V["전체_h"])
    def row(name, sub, pre, fore, main, cls=""):
        tot = pre + fore + main
        return (f'<div class="brow{cls}"><div class="bl"><b>{esc(name)}</b><small>{esc(sub)}</small></div><div class="bb"><div class="sbar" style="width:{tot / mx * 100:.1f}%">'
                f'<i class="sg-heat" style="flex:{pre:.3f}"></i><i class="sg-fore" style="flex:{fore:.3f}"></i><i class="sg-main" style="flex:{main:.3f}"></i></div></div>'
                f'<div class="bv">{N(pre)} · <b>{N(fore)}</b> · <b>{N(main)}</b> h</div></div>')
    rows = [row(BATCH(b), f'투입 {V["투입"][j]} kg · 초류 {V["초류량"][j]} kg', V["전체_h"][j] - V["초류_h"][j] - V["본류_h"][j], V["초류_h"][j], V["본류_h"][j]) for j, b in enumerate(V["배치"])]
    rows.append(row(f"계산 {VER}", f'투입 {N(S["feed"], 0)} kg · 초류 {N(S["fore"], 0)} kg', S["t_all"] - S["t_fore"] - S["t_main"], S["t_fore"], S["t_main"], " sim"))
    leg = '<div class="sleg"><span><i class="sg-heat"></i>승온 · 전환류</span><span><i class="sg-fore"></i>초류</span><span><i class="sg-main"></i>본류</span><span>오른쪽 숫자는 구간별 시간(h)</span></div>'
    return f'<div class="brows">{"".join(rows)}</div>{leg}'


# ---------------------------------------------------------------- 문장
def facts(D):
    db = D["db"]; V = D["dbv"]; R = db["DBR"]; G = V["범위"]; b, n = trial(db); cv = db["VPsd"] / db["VPmean"] * 100; va = db["V_at"]
    kr = [k for k in V["FICH072_무게_적분_비"] if k is not None]; dj = max(abs(v) for v in R["dTjFore"] + R["dTjMain"])
    return [
        ("증기 배관의 초킹", f'12점(증발량 {rg(db["Vrng"], 2)} kg/h)에서 증발량 ÷ 증기압(내부 온도 기준)이 {N(db["VPmean"])} ± {jo(N(db["VPsd"]), "으로", "로")} 일정하다(변동 {cv:.0f} %). 증발량이 정제기 압력에 비례하는 것은 증기 배관 출구가 음속 한계에 걸린 초킹 상태의 특징이며, '
                        f'증기 배관 식으로 계산해도 12점 모두 초킹 조건이다. 따라서 내부 온도가 정해지면 증발량도 정해진다(95 ℃ {N(va["T95"])}, 98 ℃ {N(va["T98"])}, 101 ℃ {N(va["T101"])} kg/h).'),
        ("증기압식의 상수 A", f'현재 식(A = {db["A0"]})으로는 본류 탑 온도 {rg(R["ThMain"])} ℃의 포화압이 {rg(db["P0t_main"], 3)} torr다. 같은 유량이 80A 배관(내경 {N(db["Dpipe"])} mm)을 지나려면 관 내 압력이 {rg(db["Pson_main"], 2)} torr 이상이어야 한다(음속 한계). '
                         f'이 한계가 현재 식의 포화압보다 {rg(db["sonRatio_main"], 1)}배 높으므로, 현재 식은 증기압을 낮게 계산한다. 증기 배관 식에 DB의 유량과 내부 온도를 넣으면 A = {db["A_phys"]:.2f} ± {jo(f2(db["A_sd"]), "이고", "고")}, 시뮬레이터에 넣어 확인한 값은 {jo(f2(db["A_use"]), "이다", "다")}. '
                         f'100 ℃의 증기압은 {N(db["P100_old"], 3)} → {N(db["P100_new"], 3)} torr가 된다.'),
        ("탑 온도계의 위치", f'본류의 내부 온도 − 탑 온도는 {rg(R["dTmain"])} ℃로, 배치와 유량이 달라도 거의 같다. 이 온도 차를 증기압의 비로 환산하면 {jo(rg(db["pr_main"], 2), "이며", "며")}, 계산상 정제기 ÷ 배관 출구의 압력비 {N(db["sim_pr_exit"], 2)}에 가깝고 정제기 ÷ 컬럼 상부의 압력비 {jo(N(db["sim_pr_top"], 2), "과는", "와는")} 다르다. '
                        '탑 온도 TIH075의 측정 소자(TE-H075)는 증기 배관 출구 쪽 압력의 포화 온도를 지시하는 위치에 있는 것으로 보인다.'),
        ("스팀 제어 방식", f'내부 온도 TICH071이 {rg(G["내부온도_제어"], 0)} ℃에 도달한 뒤 그 부근에서 유지된다(내부 온도 제어). 자켓 온도 TIH074는 승온 중 최고 {rg(G["자켓_승온_최고"], 0)} ℃이고, 정제 중에는 내부 온도와의 차가 {N(dj)} ℃ 이내다. 스팀 헤더 온도 133 ℃는 TCV-H071 전단의 값이다.'),
        ("유량계와 무게 지시값", f'초류 · 본류 무게 ÷ FICH072 유량 적분값이 {min(kr):.2f}~{max(kr):.2f}로, FICH072 지시값이 무게 기준보다 높다. WIH071은 승온 중 내부 온도 1 ℃당 약 {G["WIH071_증가_대표"]} kg 높게 지시하고, WIH071 · WIH073은 {G["무게_바닥_kg"]} kg 미만에서 0을 지시한다.'),
        ("1차 응축기의 응축률", f'초류 종료 후 초류 탱크의 무게 증가는 {G["이차응축기_유입"][0]}~{G["이차응축기_유입"][1]} kg/h다. P&ID상 2차 응축기의 응축액은 초류 탱크로 들어가므로 이 값이 2차 응축기로 넘어간 양이며, 증기는 1차 응축기에서 거의 전량 응축된다(계산 {b["m2_30"]:.4f} kg/h).'),
    ]


def opens(D):
    db = D["db"]; V = D["dbv"]; G = V["범위"]; hk = db["heat_kw"]
    return [
        ("증기압식의 기울기 B", f'12점의 증발량과 내부 온도로 구한 기울기는 {N(db["Bfit"], 0)} ± {jo(N(db["Bse"], 0), "이다", "다")}. 내부 온도 범위({rg(db["Trng"])} ℃)가 좁아 현재 값 {jo(N(db["B0"], 0), "을", "를")} 확인하기에는 부족하다. 비등 개시 온도를 시계열에서 읽으면 정할 수 있다.'),
        ("압력계 기록", "PICH071은 배치마다 단위와 스케일이 다르고 PIH093은 −1로 고정되어 있다. 압력은 온도와 유량에서 역산했으며, 압력계 영점과 리크 속도는 구하지 못했다."),
        ("TE-H075 · TIH074의 설치 위치", "탑 온도계가 증기 배관의 어느 지점에 있는지, 자켓 온도계가 자켓 본체와 응축수 출구 중 어디를 측정하는지는 현장 확인이 필요하다."),
        ("전열과 열용량", f'승온 속도 {rg(G["승온_기울기"])} ℃/분은 액의 열용량 기준으로 {N(hk[0], 0)}~{N(hk[1], 0)} kW에 해당한다(배치 26#28, 투입 {V["투입"][V["배치"].index("28")]} kg 기준). 자켓 온도와 내부 온도의 시계열을 회귀하면 U·A와 금속 열용량을 분리해 구할 수 있다.'),
        ("값이 없는 태그", "투입량 · 컷 설정(VAC2_FEED_SET · LCUT_SET · MCUT_SET, TH071_*_WT), 냉매 온도(TICH364 · TIH353), 회수 탱크 압력(PIH072 · PIH073)은 이번 추출에 값이 없어 다시 요청한다."),
        ("성분 분석", "원료 · 초류 · 본류 · 잔류액의 분석 자료가 없어 농축비와 본류 순도는 검증하지 못했다."),
    ]


def lit_text(D):
    db = D["db"]; L = db["LIT"]; rn1 = f"{L[1]['r_new']:.1f}"
    return (f'CpHf(NMe₂)₃의 증기압은 60 ℃에서 약 {L[0]["P"]:.2f} torr(Sharma 외, 2017)와 {L[1]["P"]:.2f} torr(Oike 외, 2024)로 보고되어 있다. 현재 식의 60 ℃ 값은 {L[0]["P_old"]:.3f} torr로 문헌값의 1/{L[0]["r_old"]:.0f}~1/{L[1]["r_old"]:.0f}이고, '
            f'상수 A를 {jo(f2(db["A_use"]), "으로", "로")} 바꾼 식의 값은 {L[0]["P_new"]:.3f} torr로 문헌값의 1/{L[0]["r_new"]:.1f}~1/{jo(rn1, "이다", "다")}. 현재 식의 기준점(84 ℃ · 0.1 torr)은 제조사 SDS의 값이다. '
            f'문헌값과 이번 계산을 모두 만족하려면 기울기 B가 약 {jo(N(db["B_lit"], 0), "이어야", "여야")} 한다. 기울기는 비등 개시 온도로 확인한다.')


def trial_text(D, VER):
    db = D["db"]; R = db["DBR"]; S = db["SIM"]; b, n = trial(db, VER); j = judge(db, VER)
    same = f'{n["Tex30"]:.1f}' == f'{R["ThMain"][0]:.1f}'
    return (f'시뮬레이터 {VER}에 증기압식의 상수 A만 {jo(f2(db["A_use"]), "으로", "로")} 바꿔 넣고 같은 레시피로 한 배치를 돌렸다. 내부 온도는 초류 {N(S["Tfore"])} → {N(n["Tfore"])} ℃, 본류 {N(S["Tmain"])} → {N(n["Tmain"])} ℃로 DB 범위에 든다. '
            f'컬럼 상부 온도는 {N(n["ThMain"])} ℃이고, 증기 배관 출구 압력({N(n["Pexit30"], 2)} torr)의 포화 온도는 {N(n["Tex30"])} ℃로 DB 탑 온도({rg(R["ThMain"])} ℃)의 {"하한과 같다" if same else "하한 수준이다"}. 자켓 온도는 {N(n["TjMain"])} ℃로 DB보다 {j["dTj"][0]:.1f}~{j["dTj"][1]:.1f} ℃ 높다. '
            f'2차 응축기 유입량은 {b["m2_30"]:.4f} → {n["m2_30"]:.4f} kg/h로 DB 범위 안으로 들어온다. 본류 구간은 {N(n["t_main"])} h로 같고, 초류 구간은 {N(S["t_fore"])} → {N(n["t_fore"])} h로 짧아진다. '
            f'내부 온도가 낮아져 열손실이 줄어든 만큼 최소 개도의 초류 유출량이 {N(S["Dfore"], 2)} → {N(n["Dfore"], 2)} kg/h로 늘기 때문이다. 이 차이는 스팀 밸브 특성식의 가정값에 따른 결과다. 시뮬레이터 기본값은 변경하지 않았다.')


def short_text(D, VER):
    """요약 화면 · 교과서에 쓰는 글."""
    db = D["db"]; R = db["DBR"]; S = db["SIM"]; b, n = trial(db, VER); j = judge(db, VER)
    return (f'증발량(환류 + 유출)과 구간 소요 시간은 DB 6배치의 범위 안에 있다. 내부 온도와 탑 온도는 계산값이 DB보다 높다(본류 내부 {N(j["dT_main"][0], 0)}~{N(j["dT_main"][1], 0)} ℃, 탑 {N(j["dT_top"][0], 0)}~{N(j["dT_top"][1], 0)} ℃). '
            f'주된 원인은 증기압식의 상수 A다. DB 12점의 유량과 내부 온도로 구한 값은 {jo(f2(db["A_use"]), "이며", "며")}(현재 {db["A0"]}), 이 값만 바꿔 넣은 시험 계산에서는 본류 내부 온도가 {N(n["Tmain"])} ℃로 DB 범위({rg(R["Tmain"])} ℃)에 든다. 시뮬레이터 기본값은 아직 변경하지 않았다.')


# ---------------------------------------------------------------- 화면
def scene_dr(D, NODES, VER):
    db = D["db"]; V = D["dbv"]; R = db["DBR"]; S = db["SIM"]; b, n = trial(db, VER); j = judge(db, VER); rows = cmp_rows(D)
    crow = "".join(f'<tr><td>{esc(r["name"])}</td><td class="m">{cell(r["db"])}</td><td class="m">{cell(r["sim"])}</td><td class="m">{cell(r["trial"])}</td><td>{esc(r["why"])}</td></tr>' for r in rows)
    fl = "".join(f"<li><b>{esc(a)}</b> {esc(t)}</li>" for a, t in facts(D)); ol = "".join(f"<li><b>{esc(a)}</b> {esc(t)}</li>" for a, t in opens(D))
    c = st_count(NODES)
    return ('<section class="scene" id="dr" data-tab="db" hidden><div class="sh"><h2>DB 6배치 분석 결과</h2>' f'<span class="tag">2차 정제 {len(V["배치"])}배치 · {esc(V["기간"])} · 10분 간격 시계열의 구간 평균</span></div>'
            '<p class="q">DB 6배치와 계산값의 비교, DB로 구한 증기압식 상수</p>'
            f'<p class="say">사내 DB에서 2차 정제 {len(V["배치"])}배치의 계기 기록을 받아 구간별로 평균했다. 증발량(환류 + 유출)과 구간 소요 시간은 계산값이 배치 간 범위 안에 있다. 온도는 계산값이 DB보다 높다(본류 내부 {N(j["dT_main"][0], 0)}~{N(j["dT_main"][1], 0)} ℃, 탑 {N(j["dT_top"][0], 0)}~{N(j["dT_top"][1], 0)} ℃). '
            f'주된 원인은 증기압식의 상수 A이며, DB 12점으로 구한 값은 {jo(f2(db["A_use"]), "이다", "다")}(현재 {db["A0"]}).</p>'
            f'<figure><div class="scroll">{fig_dr(D)}</div><figcaption>본류 구간의 평균값이다. 초록색 글은 DB 6배치의 범위, 그 아래는 {esc(VER)} 계산값이다. 계산값이 DB 범위를 벗어나면 주황색 글자와 ▲(높음) · ▼(낮음)으로 표시했다. '
            '점선 태그는 기록이 없거나 쓸 수 없는 계기다. 투입량(WIH071) · 초류량(WIH072) · 본류량(WIH073)은 배치 전체의 값이다.</figcaption></figure>'
            '<div class="grid2"><div class="blk"><h3>증발량과 내부 온도 <small>DB 12점과 계산선</small></h3>'
            f'<figure class="plain"><div class="scroll">{fig_vt(D, VER)}</div></figure>'
            f'<p class="small">계산선은 정제기 압력(증기 배관 식 + 충전층 압력 손실)이 내부 온도의 증기압과 같아지는 점을 이은 선이다(환류 {N(S["Rmain"], 0)} kg/h 기준). DB의 유출 유량은 무게 기준으로 보정했다(FICH072 지시값 × {db["kmean"]:.2f}).</p></div>'
            f'<div class="blk"><h3>배치별 구간 소요 시간 <small>승온 시작 → 본류 종료</small></h3>{bars(D, VER)}'
            f'<p class="small">초류량은 {rg(R["fore"])} kg(투입의 {rg(R["forePct"], 0)} %)으로 배치마다 다르고, 초류 구간도 {rg(R["t_fore"])} h다. 계산은 운전 기준(초류 {N(S["fore"], 0)} kg)을 따른다.</p></div></div>'
            f'<div class="blk"><h3>계기별 비교 <small>DB는 6배치 구간 평균의 범위 · 시험 계산은 상수 A만 {db["A_use"]:.2f}로 변경</small></h3>'
            f'<div class="tw"><table class="cmp"><tr><th></th><th>DB 6배치</th><th>계산 {esc(VER)}</th><th>시험 계산</th><th>차이의 원인</th></tr>{crow}</table></div>'
            f'<p class="small">{esc(trial_text(D, VER))} 표의 배관 출구 온도는 증기 배관 출구 압력의 포화 온도다.</p></div>'
            '<div class="grid2"><div class="blk"><h3>DB로 확인한 사항 <span class="bdg b-db">DB</span></h3>' f'<ul class="pl">{fl}</ul></div>'
            '<div class="blk"><h3>정하지 못한 사항과 추가 요청 <span class="bdg b-est">가정</span></h3>' f'<ul class="pl">{ol}</ul>'
            f'<p class="small">{esc(lit_text(D))}</p>'
            f'<p class="small">수집 항목 {sum(c.values())}건 가운데 확인 {c["ok"]}건, 일부 확인 {c["part"]}건, 확인 불가 {c["no"]}건이다. 항목별 내용은 <button class="lnk" data-go="db">DB 데이터로 결정되는 항목</button>에 있다.</p></div></div></section>')
