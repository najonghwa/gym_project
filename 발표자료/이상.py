# -*- coding: utf-8 -*-
"""이상 상황 화면과 DB 데이터 화면.

- 이상 상황 12종의 수치는 점검 기록(레시피 운전 10 h 시점의 적용 전 · 적용 30분 후 · 해제 30분 후)에서 읽는다.
- 그림은 전체 설비 2D 위에 값 표시를 얹은 한 장이다. 시나리오를 선택하면 값 · 흐름 · 변경 위치 표시가 바뀐다.
"""
import math
from 그림 import *
from 설비도 import plant, GEO
from 내용 import N

# 값 표시: (키, 이름, x, y, 너비, 단위, 소수 자리, 기록 항목) — 설비 · 배관 · 태그를 가리지 않는 위치
VB = [
    ("Qloss", "정제기 열손실", 14, 404, 118, "W", 0, "Qloss"), ("Q", "스팀 공급 열량", 14, 450, 118, "W", 0, "Q"), ("MV", "스팀 밸브 개도(MV)", 14, 596, 118, "%", 1, "MV"),
    ("Tpot", "내부 온도 TICH071", 386, 478, 142, "℃", 1, "Tpot"), ("Pstill", "정제기 압력 PICH071", 386, 524, 142, "torr", 2, "Pstill"), ("V", "증발량", 386, 570, 142, "kg/h", 2, "V"),
    ("Ttop", "탑 온도 TIH075", 122, 190, 142, "℃", 1, "Ttop"), ("back", "컬럼 내부 응축량", 122, 236, 142, "kg/h", 2, "back"),
    ("R", "환류 FICH073", 398, 386, 150, "kg/h", 2, "R"), ("D", "유출 FICH072", 694, 328, 150, "kg/h", 2, "D"),
    ("Tw1", "N-Brine 출구 온도", 422, 92, 142, "℃", 1, "Tw1"), ("c1", "1차 응축률", 660, 206, 142, "%", 0, "c1"), ("Tbot", "응축액 출구 TICH071D", 660, 252, 150, "℃", 1, "Tbot"),
    ("n2", "2차 응축량", 990, 300, 142, "kg/h", 2, "n2"), ("Pcond", "펌프 측 압력 PIH093", 990, 346, 142, "torr", 2, "Ppump"),
]
MARKS = {  # 입력을 변경한 위치: (x, y, 반지름, 글 위치 dx, dy, 정렬)
    "nb": (553, 232, 22, -28, -26, "end"), "lb": (896, 236, 22, 30, 26, "start"), "tcv": (92, 560, 22, 0, -30, "middle"),
    "fcv73": (436, 352, 22, 0, -30, "middle"), "leak": (965, 150, 16, 25, 14, "start"), "pcv": (1030, 120, 22, 0, -32, "middle"),
    "pump": (1105, 152, 32, 38, 4, "start"), "amb": (345, 630, 22, 31, 22, "start"), "ins": (346, 560, 24, 30, 62, "start"),
}
# 시나리오별: '계산 결과'의 몇 번째 항목이 어느 값 표시에 해당하는지
STEPS = dict(
    c1hot=dict(c1=1, Tw1=1, n2=2, R=3, D=3, MV=4, Q=4, Tpot=4), c1cold=dict(Tbot=1, Tw1=1, D=3, V=3, MV=4, Q=4), c2hot=dict(c1=1, n2=1, Pcond=2, V=2), cwlow=dict(c1=1, n2=2, Tw1=2, R=3, D=3, MV=3),
    steam=dict(V=1, Pstill=1, Tpot=1, R=2, D=2), rhigh=dict(R=1, D=1, MV=2), rlow=dict(R=1, D=1), leak=dict(Pcond=1, V=2, Tpot=3), pump=dict(Pcond=1, V=2, D=3),
    pstop=dict(Pcond=1, V=2, R=2, D=2, MV=3, Pstill=4), cold=dict(Qloss=1, back=2, D=2), bare=dict(Qloss=1, back=2, D=3, Tpot=3))
# 시나리오별: 표시 위치 · 그 위치에 쓰는 글(변경한 입력)
CASE_MARK = dict(c1hot=("nb", "냉매 온도 상승"), c1cold=("nb", "냉매 온도 저하"), cwlow=("nb", "냉매 유량 감소"), c2hot=("lb", "냉매 온도 상승"), steam=("tcv", "밸브 개도 과다"),
                 rhigh=("fcv73", "환류 설정 상향"), rlow=("fcv73", "환류 설정 하향"), leak=("leak", "공기 유입(리크)"), pump=("pcv", "개도 3 %로 축소"), pstop=("pump", "펌프 정지"),
                 cold=("amb", "외기 온도 저하"), bare=("ins", "보온 두께 감소"))
# 시나리오별 판정 기준(점검_공식.py의 판정식을 풀어 쓴 것. 식을 바꾸면 함께 고친다)
CRIT_TXT = dict(
    c1hot="1차 응축률 5 % 미만 · 환류량이 평소의 30 % 미만 · 2차 응축량이 컬럼 상부 통과 증기의 70 % 초과 · 펌프 측 압력 변화 ±20 % 이내 · 해제 후 정상 복귀",
    c1cold="응축액 출구 온도 15 ℃ 미만 · 환류 1 kg당 내부 응축량 1.5배 초과 · 증발량 변화 ±20 % 이내",
    c2hot="1차 응축기가 전량 응축하는 동안에는 영향이 거의 없음(진공펌프 손실 0.01 kg/h 미만, 증발량 변화 ±15 % · 펌프 측 압력 변화 ±20 % 이내)",
    cwlow="처리 가능 열량이 ε·C·(T포화 − T냉매)와 ±3 % 이내로 일치 · 응축률이 처리 가능 열량 ÷ 부하와 ±0.03 이내로 일치 · 2차 응축기로 증기 유입 · 냉매 출구 온도 상승폭 10 ℃ 초과",
    steam="증발량 1.5배 초과 · 정제기 압력 1.5배 초과 · 내부 온도 상승폭 5 ℃ 초과 · 유출량 2배 초과 · 해제 후 개도 하강(30분에 5 %p 초과)",
    rhigh="환류량 1.3배 초과 · 유출량 60 % 미만 · 스팀 밸브 개도는 유지 또는 증가",
    rlow="환류량 40 % 미만 · 유출량 1.2배 초과 · 저비점 성분 농축도 감소",
    leak="펌프 측 압력 5배 초과, 상승폭은 리크 속도에 비례(±35 %) · 30분간 정제기 감소량이 평소 유출량의 20 % 미만 · 액 온도가 새 끓는점에 도달한 뒤에만 재비등(±0.3 ℃) · 해제 후 재비등",
    pump="펌프 측 압력 3배 초과(상승폭 = 1 ÷ 개도, ±35 %) · 컬럼 상부 압력이 그보다 높은 동안(증기 배관 초킹) 증발량 변화 ±15 % 이내",
    pstop="펌프 측 압력 = 초기 압력 + 리크 속도 × 시간(±20 %) · 비등 정지 · 해제 후 재비등",
    cold="열손실 변화가 내외부 온도 차의 비와 일치(±10 %) · 컬럼 내부 응축량 1.1배 초과",
    bare="열손실 변화가 열관류율 1/(t/k + 1/10)의 비 × 내외부 온도 차의 비와 일치(±10 %) · 컬럼 내부 응축량 1.5배 초과")

def fig_ab():
    fid = "fig-ab"; o = [svg_open(fid, 1200, 690, "이상 상황을 적용했을 때 설비 각 지점의 값이 어떻게 변하는지 보여 주는 설비 그림", y0=36)]
    o.append(plant(fid, level=0.53, main=0.0, fore=0.28, valves=dict(XV77="closed", XV74="open"), dyn=True, tags=True))
    for k, lab, x, y, w, unit, dec, key in VB:
        o.append(f'<g data-vb="{k}" data-panel="vb-{k}" data-grp="vb-{k}"><rect class="vb" x="{x}" y="{y}" width="{w}" height="38" rx="7"/>' + text(x + 8, y + 14, lab, "vbl", "start") + text(x + 8, y + 31, "–", "vbv", "start") + "</g>"
                 f'<g data-step="{k}" data-grp="vb-{k}" hidden><circle class="stepc" cx="{x + w - 2}" cy="{y + 2}" r="8.5"/>' + text(x + w - 2, y + 5.8, "1", "stept") + "</g>")
    for mk, (x, y, r, dx, dy, an) in MARKS.items():
        o.append(f'<g data-mark="{mk}" hidden><circle class="mark" cx="{x}" cy="{y}" r="{r}"/>' + text(x + dx, y + dy, "변경", "markt", an) + "</g>")
    o.append("</svg>"); return "".join(o)

def _vals(a, b):
    out = {}
    for k, lab, x, y, w, unit, dec, key in VB:
        va, vb = a.get(key), b.get(key)
        if key == "c1": va, vb = (None if va is None else va * 100), (None if vb is None else vb * 100)
        if va is None or vb is None: out[k] = dict(t="–", chg=False); continue
        chg = abs(vb - va) >= 2 * 10 ** -dec * 0.999 and abs(vb - va) > 0.005 * max(abs(va), abs(vb))   # 표시 자릿수 기준 2 이상, 값의 0.5 % 넘게 변할 때
        out[k] = dict(t=(f"{va:.{dec}f} → {vb:.{dec}f} {unit}" if chg else f"{vb:.{dec}f} {unit}"), chg=bool(chg))
    return out

def _case(k, name, a, b, c, ok):
    f1 = lambda x: f"{x:.1f}"; f2 = lambda x: f"{x:.2f}"; li = lambda *xs: "".join(f"<li>{x}</li>" for x in xs)
    rel = lambda *xs: '<p class="small">관련 공식: ' + " · ".join(xs) + "</p>"
    if k == "c1hot":
        cause = f"N-Brine 공급 온도 {a['Tcw']:g} → {b['Tcw']:g} ℃"
        what = li(f"1차 응축률이 {a['c1'] * 100:.0f} → {b['c1'] * 100:.0f} %로 떨어진다. 응축기 압력({a['Pcond']:.2f} torr)의 포화 온도는 {a['Tsat']:.0f} ℃인데 냉매 온도가 그보다 높기 때문이다.",
                  f"증기 {f1(b['n2'])} kg/h 전량이 2차 응축기로 넘어가 그곳에서 응축된다.", f"환류 {f1(a['R'])} → {f1(b['R'])} kg/h, 유출 {f1(a['D'])} → {f1(b['D'])} kg/h. 컬럼으로 돌아가는 환류가 끊긴다.",
                  f"응축량이 0이 되어 설정값에 못 미치므로 스팀 제어가 밸브 개도를 높인다({a['MV']:g} → {b['MV']:g} %). 내부 온도가 {f1(a['Tpot'])} → {f1(b['Tpot'])} ℃로 상승한다.")
        why = "<p>응축기는 냉매가 증기보다 차가워야 열을 제거할 수 있다. 냉매 온도가 포화 온도보다 높으면 처리 가능 열량이 0이 된다.</p>" + rel("⑤ 응축기 처리 가능 열량 Q<sub>최대</sub> = ε·C·(T<sub>포화</sub> − T<sub>냉매</sub>)", "⑥ 스팀 제어(PI)")
    elif k == "c1cold":
        cause = f"N-Brine 공급 온도 {a['Tcw']:g} → {b['Tcw']:g} ℃"
        what = li(f"응축액 출구 온도가 {f1(a['Tbot'])} → {f1(b['Tbot'])} ℃로 낮아진다.", f"온도가 낮아진 환류액이 컬럼 상부에서 증기를 더 많이 응축시킨다(환류 1 kg당 응축량 {a['subR']:.2f} → {b['subR']:.2f} kg).",
                  f"그만큼 유출량이 {f2(a['D'])} → {f2(b['D'])} kg/h로 줄어든다. 증발량은 변하지 않는다({f2(a['V'])} → {f2(b['V'])} kg/h).",
                  f"유출량이 줄자 스팀 제어가 밸브 개도를 소폭 높인다({a['MV']:g} → {b['MV']:g} %).", "응축액이 고화되어 배관이 막히는 현상은 계산에 포함되지 않는다(어는점 자료 없음).")
        why = "<p>과냉된 환류액은 컬럼에서 가열되면서 그 열량만큼 증기를 응축시킨다. 환류액 온도가 낮을수록 내부 응축량이 많아진다.</p>" + rel("③ 과냉 환류에 의한 내부 응축 ΔL = L·c<sub>p</sub>·ΔT / λ")
    elif k == "c2hot":
        cause = f"L-Brine 공급 온도 {a['Tcw2']:g} → {b['Tcw2']:g} ℃"
        what = li("변화가 거의 없다. 1차 응축기가 증기를 전량 응축하고 있어 2차 응축기로 넘어오는 것은 공기뿐이다.", f"진공펌프로 손실되는 증기 {b['lost']:.5f} kg/h, 증발량 {f2(a['V'])} → {f2(b['V'])} kg/h, 펌프 측 압력 {a['Pcond']:.3f} → {b['Pcond']:.3f} torr.",
                  "1차와 2차 응축기의 냉매 온도가 함께 상승할 때에만 압력이 오른다.")
        why = "<p>2차 응축기는 1차 응축기에서 응축되지 않은 증기를 회수하는 설비다. 넘어오는 증기가 없으면 2차 냉매 온도는 결과에 영향을 주지 않는다.</p>" + rel("⑦ 2차 응축기 포화 한계", "⑤ 응축률")
    elif k == "cwlow":
        cause = f"N-Brine 유량 {a['mcw']:g} → {b['mcw']:g} kg/h"
        what = li(f"1차 응축기의 처리 가능 열량이 {b['cap1']:.0f} W로 줄어 증기의 {b['c1'] * 100:.0f} %만 응축된다.", f"나머지 {f1(b['n2'])} kg/h는 2차 응축기로 넘어간다. 냉매는 포화 온도({b['Tw1']:.0f} ℃)까지 가열되어 배출된다.",
                  f"환류 {f1(a['R'])} → {f1(b['R'])} kg/h, 유출 {f1(a['D'])} → {f1(b['D'])} kg/h. 스팀 밸브 개도는 {a['MV']:g} → {b['MV']:g} %.")
        why = "<p>냉매가 제거하는 열량은 유량 × 비열 × 온도 상승분이다. 유량이 줄면 냉매가 포화 온도까지 가열되어도 제거 열량이 부족하다.</p>" + rel("⑤ 응축기 처리 가능 열량(ε = 1 − e<sup>−UA/C</sup>, C = 유량 × 비열)", "⑤ 응축률")
    elif k == "steam":
        cause = f"스팀 밸브 개도 {a['MV']:g} → {b['MV']:g} % 고정"
        what = li(f"증발량 {f1(a['V'])} → {f1(b['V'])} kg/h, 정제기 압력 {f2(a['Pstill'])} → {f2(b['Pstill'])} torr, 내부 온도 {f1(a['Tpot'])} → {f1(b['Tpot'])} ℃(분해 기준 온도 120 ℃ 초과).",
                  f"환류는 {f1(b['R'])} kg/h로 일정하므로 늘어난 증기가 모두 유출로 나가 유출량이 {f1(a['D'])} → {f1(b['D'])} kg/h가 된다. 사실상 분리되지 않고 그대로 유출된다.",
                  f"컬럼 범람률 {a['flood'] * 100:.0f} → {b['flood'] * 100:.0f} %.", f"스팀을 원래대로 되돌린 지 30분이 지나도 내부 온도 {f1(c['Tpot'])} ℃, 증발량 {f1(c['V'])} kg/h다. 액 온도가 내려가야 증발량이 줄어든다.")
        why = "<p>공급 열량이 늘면 증발량이 늘고, 그 증기를 내보내려면 압력이 높아져야 하며, 압력이 높아지면 끓는점도 높아진다. 증기 배관이 초킹 상태이므로 증발량은 액 온도로 결정된다.</p>" + rel("① 스팀 밸브 유량 특성", "② 진공 비등 평형", "④ 음속 한계(초킹)")
    elif k == "rhigh":
        cause = "환류 설정값 2.5배(4 → 10 kg/h)"
        what = li(f"응축액이 모두 환류로 돌아가 환류는 {f1(a['R'])} → {f1(b['R'])} kg/h(응축량 범위 내), 유출은 {f1(a['D'])} → {f1(b['D'])} kg/h가 된다.", f"스팀 제어가 부족한 응축량을 보충하려고 밸브 개도를 높인다({a['MV']:g} → {b['MV']:g} %).",
                  "같은 양을 회수하는 데 스팀과 시간이 더 든다.")
        why = "<p>환류량은 응축량을 초과할 수 없다. 환류 설정값이 응축량보다 크면 유출량은 0이 된다.</p>" + rel("⑥ 환류 · 유출 분배 D = W<sub>응축</sub> − R", "⑥ 스팀 제어(PI)")
    elif k == "rlow":
        cause = "환류 설정값 0.2배(4 → 0.8 kg/h)"
        what = li(f"환류가 {f1(a['R'])} → {f1(b['R'])} kg/h로 줄고 유출이 {f1(a['D'])} → {f1(b['D'])} kg/h로 늘어난다.", f"유출액의 저비점 성분 농도가 {a['xD']:.2f} → {b['xD']:.2f} mol%로 낮아진다. 컬럼의 분리 효과가 줄어든 것이다.", "회수 속도는 빨라지지만 초류로 제거되는 불순물은 줄어든다.")
        why = "<p>환류량이 적으면 충전층에서 증기와 접촉하는 액이 줄어, 저비점 성분이 컬럼 상부에 덜 농축된다.</p>" + rel("③ 컬럼 상부 조성(환류비 R 감소)", "⑥ 환류 · 유출 분배")
    elif k == "leak":
        lost = a["m"] - b["m"]; usual = a["D"] * (b["t_h"] - a["t_h"])
        cause = f"리크 {a['leak']:g} → {b['leak']:g} mmHg/min"
        what = li(f"펌프 측 압력이 {f2(a['Pcond'])} → {f2(b['Pcond'])} torr로 상승한다.", f"30분 동안 정제기에서 줄어든 양은 {lost:.2f} kg이다(정상 운전 시 {usual:.1f} kg). 비등이 거의 멈춘다.",
                  f"액이 새 끓는점 {f1(b['Tbub'])} ℃까지 {b['Tpot'] - a['Tpot']:.1f} ℃ 가열된 뒤 다시 끓기 시작한다(30분 후 증발량 {f1(b['V'])} kg/h).", f"리크를 원래대로 되돌리면 액이 가열된 만큼 증발량이 늘어난다({f1(c['V'])} kg/h).")
        why = "<p>공기가 유입되면 압력은 펌프의 배기량과 균형을 이루는 수준까지 상승한다. 계의 압력이 오르면 끓는점이 높아지고, 액 온도가 그 온도에 도달할 때까지 증발이 멈춘다.</p>" + rel("⑦ 진공 압력 = 설정 + 리크·τ", "② 끓는점")
    elif k == "pump":
        cause = "PCV-H093 개도 3 %(배기 능력 3 %)"
        what = li(f"펌프 측 압력이 {f2(a['Pcond'])} → {f2(b['Pcond'])} torr로 상승한다(설정 대비 상승폭이 33배 = 1 ÷ 0.03).", f"증발량은 {f2(a['V'])} → {f2(b['V'])} kg/h로 거의 변하지 않는다.",
                  f"유출량은 {f2(a['D'])} → {f2(b['D'])} kg/h로 줄어든다. 응축기 측 포화 온도가 {a['Tsat']:.0f} → {b['Tsat']:.0f} ℃로 올라, 환류액이 컬럼에서 응축시키는 증기가 계산상 늘어나기 때문이다(환류 1 kg당 {a['subR']:.2f} → {b['subR']:.2f} kg. ③ 충전 컬럼의 가정 d).",
                  f"컬럼 상부 압력({f2(b['Ptop'])} torr)이 여전히 더 높으므로 증기 배관 출구는 계속 초킹 상태다.")
        why = "<p>배관 출구가 초킹 상태인 동안에는 하류 압력이 다소 올라도 유량이 변하지 않는다. 하류 압력이 컬럼 상부 압력에 근접해야 영향이 나타난다.</p>" + rel("④ 음속 한계(초킹)", "⑦ 진공 압력")
    elif k == "pstop":
        cause = "PCV-H093 닫힘(진공펌프 정지)"
        lag = (f"정제기 압력({f2(b['Pstill'])} torr)이 펌프 측({f2(b['Ppump'])} torr)보다 낮게 표시된다. 진공 조건에서 계산이 진동하지 않도록, 정제기 압력이 계산 단계마다 목표값의 30 %씩만 따라가도록 완충해 두었기 때문이다. 증기 흐름이 없으면 실제로는 두 압력이 같다.",) if b["Pstill"] < b["Ppump"] - 0.02 else ()
        what = li(f"펌프 측 압력이 리크 속도로 상승해 30분 후 {f2(b['Ppump'])} torr가 된다(리크 {b['leak']:g} mmHg/min × 30분 = {b['leak'] * 30:g} torr 상승).", f"끓는점이 {f1(b['Tbub'])} ℃로 높아져 액 온도({f1(b['Tpot'])} ℃)를 넘는다. 비등이 멈추고 환류와 유출이 0이 된다.",
                  f"스팀 제어가 밸브 개도를 높여({a['MV']:g} → {b['MV']:g} %) 액을 가열한다. 진공이 회복되면 {f1(c['V'])} kg/h로 다시 증발한다.", *lag)
        why = "<p>펌프가 정지하면 유입된 공기가 계속 축적된다. 압력은 리크 속도 × 시간만큼 상승한다.</p>" + rel("⑦ 압력 응답 속도", "② 끓는점")
    elif k == "cold":
        cause = f"외기 온도 {a['Tamb']:g} → {b['Tamb']:g} ℃"
        what = li(f"정제기 열손실 {a['Qloss']:.0f} → {b['Qloss']:.0f} W(내외부 온도 차가 커진 비율만큼 증가).", f"컬럼 벽면에서 응축되어 되돌아가는 액량 {f2(a['back'])} → {f2(b['back'])} kg/h, 유출량 {f2(a['D'])} → {f2(b['D'])} kg/h.", f"보온 두께가 {a['tIns']:g} mm여서 영향이 작다.")
        why = "<p>열손실은 내외부 온도 차에 비례한다.</p>" + rel("① 열손실 Q<sub>손실</sub> = A·(T − T<sub>외기</sub>) / (t/k + 1/h<sub>공기</sub>)")
    else:  # bare
        cause = f"보온 두께 {a['tIns']:g} → {b['tIns']:g} mm"
        what = li(f"정제기 열손실 {a['Qloss']:.0f} → {b['Qloss']:.0f} W({b['Qloss'] / a['Qloss']:.0f}배).", f"컬럼 벽면 열손실 {a['Qcool']:.0f} → {b['Qcool']:.0f} W. 컬럼 내부에서 응축되어 되돌아가는 액량이 {f2(a['back'])} → {f2(b['back'])} kg/h로 늘어난다.",
                  f"유출량 {f2(a['D'])} → {f2(b['D'])} kg/h, 내부 온도 {f1(a['Tpot'])} → {f1(b['Tpot'])} ℃.")
        why = "<p>보온재가 얇아지면 같은 온도 차에서도 열손실이 커진다. 컬럼 벽면에서 냉각된 증기는 응축되어 정제기로 되돌아간다.</p>" + rel("① 열손실", "컬럼 벽면 응축량 = 벽면 열손실 ÷ 증발열")
    flows = dict(vap=b["V"] > 0.05, cond=(b["R"] + b["D"]) > 0.05, reflux=b["R"] > 0.05, dist=b["D"] > 0.05, fore=b["D"] > 0.05, main=False, v2=b["n2"] > 0.05, l2=b["n2"] > 0.05, vac=(k != "pstop"), steam=True)
    valves = dict(PCV="closed" if k == "pstop" else "open")          # 밸브 색은 입력으로 변경한 밸브만 바꾼다(유량이 0이 된 배관은 흐리게 표시한다)
    undo = f"해제 30분 후: 증발량 {c['V']:.2f} kg/h · 내부 온도 {c['Tpot']:.1f} ℃ · 환류 {c['R']:.1f} · 유출 {c['D']:.1f} kg/h"
    return dict(name=name, cause="변경 입력: " + cause, what=what, why=why, crit=("<b>판정: " + ("통과" if ok else "실패") + "</b> · 기준: " + esc(CRIT_TXT[k])), undo=undo,
                vals=_vals(a, b), flows=flows, valves=valves, mark=CASE_MARK[k][0], marklab=CASE_MARK[k][1], steps=STEPS[k])

def scene_ab(D, NODES, ABNAME):
    chk = D["chk"]; byid = {r["id"]: r for r in chk if r["id"].startswith("K-") and not r["id"].endswith("-u")}
    order = ["c1hot", "c1cold", "c2hot", "cwlow", "steam", "rhigh", "rlow", "leak", "pump", "pstop", "cold", "bare"]
    NM = {k: ABNAME[k].replace("진공 펌프", "진공펌프").replace("단열 손상", "보온재 손상").replace("스팀 개도 과다", "스팀 밸브 개도 과다") for k in order}   # 시나리오 이름의 용어를 본문과 맞춘다
    cases = {}
    for k in order:
        a, b, c = D["ab"][k]; r = byid["K-" + k]
        cases[k] = _case(k, NM[k], a, b, c, r["ok"] is True)
    npass = sum(1 for k in order if byid["K-" + k]["ok"] is True)
    btns = "".join(f'<button data-ab="{k}" aria-pressed="false"><i>{i + 1}</i>{esc(NM[k])}</button>' for i, k in enumerate(order))
    a0 = D["ab"]["c1hot"][0]
    rows = "".join(f'<tr><td>{i + 1}</td><td>{esc(NM[k])}</td><td>{esc(cases[k]["cause"].replace("변경 입력: ", ""))}</td><td>{"통과" if byid["K-" + k]["ok"] is True else "실패"}</td></tr>' for i, k in enumerate(order))
    html_ = (f'<section class="scene" id="ab" data-tab="ab" hidden><div class="sh"><h2>이상 상황 시뮬레이션 12종</h2><span class="tag">레시피 운전 10 h(초류 구간)에 적용 · 30분 후 비교 · 검증 {npass} / {len(order)} 통과</span></div>'
             '<p class="say">시뮬레이터의 \'이상 상황\' 메뉴에 등록된 12가지 시나리오다. 검증 단계에서 시나리오를 하나씩 적용하고, 변화 방향과 크기를 별도로 계산한 기준과 비교해 물리적으로 타당한지 확인했다.</p>'
             '<div class="steps"><div class="step"><span class="no">1 · 입력 한 가지만 변경</span><b>원인에 해당하는 입력값 하나만 바꾼다</b><span>냉매 온도, 스팀 밸브 개도, 리크처럼 원인이 되는 값만 바꾼다. 결과(온도, 유량)는 직접 수정하지 않는다.</span></div>'
             '<div class="step"><span class="no">2 · 동일한 공식으로 재계산</span><b>구간별 공식으로 그대로 다시 계산한다</b><span>열수지, 비등 평형, 증기 배관, 응축기, 환류 · 유출 분배를 정상 운전과 같은 방식으로 계산한다. 이상 상황 전용 식은 두지 않았다.</span></div>'
             '<div class="step"><span class="no">3 · 결과는 계산으로만 나온다</span><b>유량 · 온도 · 압력이 연쇄적으로 변한다</b><span>어느 값이 먼저 변하고 어느 값이 유지되는지는 계산 결과로 나타난다. 계산에 포함되지 않은 현상은 그림에 표시하지 않는다.</span></div></div>'
             f'<div class="abwrap"><div class="ablist">{btns}</div><div class="abx"><div class="abhead"><h3 id="ab-name"></h3><span class="cause" id="ab-cause"></span></div>'
             f'<figure><div class="scroll">{fig_ab()}</div><figcaption>값 상자는 \'정상 → 적용 30분 후\' 순서다. 빨간 테두리는 변한 값, 빨간 점선 원은 입력을 변경한 위치, 흐린 배관은 흐름이 끊긴 곳이다. 값 상자 모서리의 번호는 아래 \'계산 결과\'의 항목 번호와 같다. 밸브는 초록이 열림, 빨강이 닫힘이다. 정상 상태: 초류 회수 중, 증발량 {a0["V"]:.1f} kg/h, 내부 온도 {a0["Tpot"]:.1f} ℃.</figcaption></figure>'
             '<div class="grid2"><div class="blk"><h3>계산 결과 <small>번호는 그림의 값 상자와 동일</small></h3><ol class="pl" id="ab-what"></ol><p class="small" id="ab-undo"></p></div>'
             '<div class="blk"><h3>원인 해석</h3><div id="ab-why"></div><p class="small" id="ab-crit"></p></div></div></div></div>'
             f'<div class="grid2"><div class="blk"><h3>시나리오 목록</h3><div class="tw"><table><tr><th></th><th>시나리오</th><th>변경 입력</th><th>검증</th></tr>{rows}</table></div></div>'
             '<div class="blk"><h3>검증 방법</h3><ul class="pl"><li>레시피 운전을 10 h(초류 회수 중)까지 진행한 뒤 값을 기록한다.</li><li>시나리오 하나를 적용하고 30분 후의 값을 기록한다. 이어서 해제하고 30분 후의 값을 다시 기록한다.</li>'
             '<li>판정 기준은 시뮬레이터 출력이 아니라 별도로 계산한 변화 방향과 크기다. 예: 열손실은 내외부 온도 차에 비례, 리크로 오르는 압력은 리크 속도에 비례, 응축 능력은 ε·C·ΔT.</li><li>시나리오마다 새 배치에서 시작해 이전 시나리오의 영향이 섞이지 않도록 했다.</li></ul>'
             '<h3>계산에 포함되지 않은 현상</h3><ul class="pl"><li>과냉으로 응축액이 고화되어 배관이 막히는 현상(어는점 자료 없음)</li><li>고비점 잔류물이 비말에 실려 제품으로 넘어가는 양</li><li>냉매 유량 제어(TICH071D → 냉매 밸브)와 정제기 압력 제어(PICH071 → PCV-H093)의 보상 동작</li><li>정제기 금속의 열용량, 교반 정지 시의 돌비</li></ul></div></div></section>')
    return html_, dict(first="c1hot", cases=cases)

# ---------------------------------------------------------------- DB 데이터 화면
def _tg(x, y, tag, desc="", anchor="start", cls="tgd"):
    """계기 태그 + 측정 항목(태그 오른쪽, end 정렬이면 왼쪽, middle이면 아래)."""
    w = tw(tag, 10.5) + 12; out = tagbub(x, y, tag, anchor, cls)
    if desc:
        if anchor == "start": out += text(x + w + 6, y + 4, desc, "ts", "start")
        elif anchor == "end": out += text(x - w - 6, y + 4, desc, "ts", "end")
        else: out += text(x, y + 22, desc, "ts", "middle")
    return out

def fig_db():
    fid = "fig-db"; g = GEO; o = [svg_open(fid, 1200, 690, "설비에서 수집할 수 있는 계기(PIMS 태그)의 위치와 측정 항목", y0=36)]
    o.append(plant(fid, level=0.57, main=0.3, fore=0.3, flows=(), tags=True))
    T = [(14, 452, "TIH074", "자켓 온도", "start", "tgd"), (14, 476, "TICH071_MV", "밸브 개도", "start", "tgd"), (228, 372, "SICAH071", "교반 속도", "end", "tgd"),
         (386, 484, "TICH071", "내부 온도", "start", "tgd"), (386, 508, "PICH071", "정제기 압력", "start", "tgd"), (386, 532, "WIH071", "정제기 무게", "start", "tgd"),
         (400, 52, "TIH075", "탑 온도(설치 위치 확인 필요)", "start", "tgd"), (400, 394, "FICH073", "환류 유량", "start", "tgd"), (624, 372, "FICH072", "유출 유량", "start", "tgd"),
         (624, 282, "TICH071D", "응축액 출구 온도", "start", "tgd"), (540, 228, "TICH364", "", "end", "tgd"), (896, 282, "TIH353", "", "middle", "tgd"),
         (610, 540, "WIH073", "본류 무게", "middle", "tgd"), (775, 566, "WIH072", "초류 무게", "middle", "tgd"),
         (14, 606, "FIH071", "스팀 유량", "start", "tgd"), (1040, 240, "PIH093", "펌프 측 압력", "middle", "tgd"),
         (540, 122, "N-Brine 출구 온도(미측정)", "", "end", "tgx"), (896, 306, "냉매 유량(미측정)", "", "middle", "tgx")]
    for x, y, tag, desc, an, cls in T: o.append(_tg(x, y, tag, desc, an, cls))
    o.append("</svg>"); return "".join(o)

def scene_db(D, NODES):
    from 내용 import PIMS
    E = D["end"]; P6 = D["snap"]["6"]["PR"]; C = D["snap"]["30"]["CUR"]; lamS = D["snap"]["30"]["fn"]["lamSteam"] / 1000.0; lam = D["snap"]["30"]["PR"]["lam"] / 1000.0
    qS = PIMS["FI"] * lamS / 3600; qP = (PIMS["R"] + PIMS["D"]) * lam / 3600
    P30 = D["snap"]["30"]["PR"]; mix = D["snap"]["30"]["mix"]
    A30 = P30["Q"] / (C["U"] * (P30["TjEff"] - P30["Tmean"]))                    # 자켓 전열 면적(본류 30 h 계산값에서 역산)
    Tv = C["T"]; Ac = math.pi * Tv * Tv / 4; Vh = math.pi * Tv ** 3 / 24
    hh = lambda m: (m / mix["rho"] - Vh) / Ac                                    # 2:1 경판 위 직동부 액 높이
    UAp = C["U"] * (A30 + math.pi * Tv * (hh(PIMS["W"]) - hh(P30["m"])))          # PIMS 화면 시점(정제기 371.9 kg)의 U·A
    dTneed = qS * 1000 / UAp
    rows = "".join(f'<tr><td>{n["n"]} {esc(n["name"])}</td><td class="m">{esc(d["tags"])}</td><td>{eq_html(d["eq"])}</td><td>{esc(d["gets"])}</td></tr>' for n in NODES for d in n["db"])
    hard = "".join(f'<tr><td>{n["n"]} {esc(n["name"])}</td><td>{esc(a["what"])}</td><td>{esc(a["why"])}</td><td>{esc(a["effect"])}</td></tr>' for n in NODES for a in n["assume"] if a["kind"] == "hard")
    est = sum(1 for n in NODES for a in n["assume"] if a["kind"] == "est"); nh = sum(1 for n in NODES for a in n["assume"] if a["kind"] == "hard")
    cmp_ = [("내부 온도 TICH071", "초류 93.5 ℃(화면) · 99~100 ℃(그래프), 본류 100~101.5 ℃", f"초류 {N(E['Tfore'])} ℃, 본류 {N(E['Tmain'])} ℃", "증기압식의 상수 A"),
            ("탑 온도 TIH075", "초류 76.8 · 82~84 ℃, 본류 84 → 87.6 ℃", f"초류 {N(E['ThFore'])} ℃, 본류 {N(E['ThMain'])} ℃", "온도계 설치 위치, 증기압식"),
            ("환류 · 유출", "초류 3.79 · 1.46, 본류 3.82 · 5.93 kg/h(화면)", f"초류 {N(E['Rfore'], 2)} · {N(E['Dfore'], 2)}, 본류 {N(E['Rmain'], 2)} · {N(E['Dmain'], 2)} kg/h", "스팀 밸브 특성식, 제어 방식"),
            ("스팀 밸브 개도 TICH071_MV", f"초류 {PIMS['MV']} %(화면) · 승온 50, 정제 25 내외(그래프)", f"승온 70 %(예시), 초류 {N(E['mvFore'])} %, 본류 {N(E['mvMain'])} %", "스팀 밸브 특성식"),
            ("스팀 유량 FIH071", f"초류 {PIMS['FI']} kg/h(밸브 전단 · 개도 {PIMS['MV']} %, 화면)", f"초류 {N(P6['steamKgh'])} kg/h(개도 {N(P6['MVpct'])} %) · 특성식의 {PIMS['MV']:.0f} % 값은 {N(C['mSteamMax'] * C['valveR'] ** (PIMS['MV'] / 100 - 1))} kg/h", "스팀 밸브 특성식, 스팀 열량 중 액에 전달되는 비율"),
            ("구간 소요 시간", "초류 9.0 h · 본류 72.7 h(그래프의 배치), 중앙값 24.5 h · 61.6 h", f"초류 {N(E['fore_h'])} h · 본류 {N(E['main_h'])} h", "유출량의 설정값 유지 여부")]
    crow = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td class=\"m\">{esc(c)}</td><td>{esc(d)}</td></tr>" for a, b, c, d in cmp_)
    return ('<section class="scene" id="db" data-tab="db" hidden><div class="sh"><h2>DB 데이터로 결정되는 항목</h2><span class="tag">PIMS 시계열 · 분석 데이터</span></div>'
            f'<p class="say">현재 입력값 가운데 {est}건은 가정, {nh}건은 추정이다. 가정 항목은 아래 계기의 시계열 데이터를 확보하면 공식에 대입해 정할 수 있다. 식은 그대로 두고 식의 상수만 현장값으로 바꾸는 작업이다.</p>'
            f'<figure><div class="scroll">{fig_db()}</div><figcaption>초록색 태그는 PIMS 화면에서 확인한 계기(옆의 글은 측정 항목), 점선 태그는 현재 측정하지 않는 항목이다.</figcaption></figure>'
            f'<div class="blk"><h3>수집 데이터 → 적용 식 → 결정 항목 <span class="bdg b-db">DB</span></h3><div class="tw"><table><tr><th>구간</th><th>수집 데이터</th><th>적용 식</th><th>결정 항목</th></tr>{rows}</table></div></div>'
            f'<div class="grid2"><div class="blk"><h3>계산값과 현장값 비교 <small>현장값은 PIMS 화면과 배치 트렌드 그래프(육안 판독)</small></h3><div class="tw"><table><tr><th></th><th>현장</th><th>계산</th><th>차이의 원인</th></tr>{crow}</table></div>'
            f'<p class="small">FIH071은 스팀 컨트롤 밸브 전단에 있다. 같은 배관이면 밸브 앞뒤의 질량 유량은 같으므로, 개도 {PIMS["MV"]} %로 조인 결과가 이미 지시값 {PIMS["FI"]} kg/h에 들어 있다. 그런데 이 양이 자켓에서 전량 응축하면 {qS:.1f} kW이고, 같은 화면의 환류 + 유출 {PIMS["R"] + PIMS["D"]:.2f} kg/h를 증발시키는 데 필요한 열량은 {qP:.2f} kW다({qS / qP:.0f}배 차이). 자켓 온도 TIH074({PIMS["Tj"]} ℃)도 내부 온도({PIMS["T"]} ℃)와 1 ℃ 이내인데, {qS:.1f} kW를 전달하려면 자켓이 액보다 약 {dTneed:.0f} ℃ 높아야 한다(U·A {UAp:.0f} W/K, U는 추정값). 따라서 지시값 전부가 자켓에서 응축된다고 보기는 어렵다. 유량계 측정 범위(저유량 오차), 유량계와 밸브 사이 분기, 스팀 트랩 상태, TIH074 설치 위치를 확인하고, 승온 구간의 온도 상승률과 스팀 유량을 함께 확보하면 판별할 수 있다.</p>'
            '<p class="small">현재 확보한 정보만으로는 정할 수 없어 증기압식과 스팀 밸브 특성식은 변경하지 않았다. 시계열 데이터를 확보하면 위 표의 순서대로 보정한다.</p></div>'
            f'<div class="blk"><h3>데이터로도 정하기 어려운 항목 <span class="bdg b-hard">추정</span></h3><div class="tw"><table><tr><th>구간</th><th>항목</th><th>근거</th><th>영향</th></tr>{hard}</table></div></div></div></section>')
