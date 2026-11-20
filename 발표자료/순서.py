# -*- coding: utf-8 -*-
"""발표 순서 — 5분 버전과 자세한 버전의 단계 · 시연 순서 · 요약 화면 둘.

- 사용자 요구(2026-11-20): "발표자료 수정해줘 어떤순서와 흐름으로 설명하면될지 · 자세한버전과 간단히 5분내로 설명해야하는버전으로 (시연까지포함하면 더짧아야할듯)"
- 단계마다 제목 · 배정 시간 · 띄울 화면 · 요지를 둔다. 시간은 이 파일의 표에만 있다(바꾸면 합계 · 시간 막대 · 진행 표시줄이 따라 바뀐다).
- 시연 순서의 숫자 · 걸린 시간 · 그림은 시연_기록.json(시연_캡처.py가 시뮬레이터의 버튼을 직접 눌러 남긴 기록)에서 읽는다. 손으로 옮겨 적지 않는다.
- 요약 화면의 숫자는 다른 화면과 같은 기록(값.json · 점검결과_*.json)에서 읽는다.
- 문체: 한다체, 제목은 명사형, 현업 표준 용어. 대괄호 모양으로 보이는 말(btn)은 시뮬레이터 화면에 적힌 버튼 이름 그대로다.
"""
import base64, math, pathlib, re
from 그림 import esc
from 내용 import N
import 이상

HERE = pathlib.Path(__file__).resolve().parent
mmss = lambda s: f"{int(s) // 60}:{int(s) % 60:02d}"
def minsec(s):
    """165 → '2분 45초'"""
    m, r = divmod(int(s), 60); return " ".join(([f"{m}분"] if m else []) + ([f"{r}초"] if r or not m else []))
btn = lambda t: f'<span class="btnc">{esc(t)}</span>'
BD = {"est": ("b-est", "가정"), "hard": ("b-hard", "추정")}
bdg = lambda k: f'<span class="bdg {BD[k][0]}">{BD[k][1]}</span>'
CIRC = "①②③④⑤"

# 구간 화면에서 대표로 제시할 공식(구간마다 하나) — 값은 그 공식 카드의 '계산값' 그대로
NODE_KEY = {1: "jacket", 2: "vboil", 3: "nst", 4: "choke", 5: "ntu", 6: "split", 7: "pump", 8: "mass"}
NODE_SEC = {1: 90, 2: 90, 3: 90, 4: 60, 5: 60, 6: 60, 7: 60, 8: 90}
PIMS_MAIN = (3.82, 5.93)      # PIMS 화면의 본류 구간 환류 · 유출 지시값(kg/h). 이상.cmp_rows의 현장 칸과 같은 값인지 아래에서 확인한다
DEMO_NAME = {1: "교반에 따른 액 내 온도 분포", 2: "정상 운전 흐름", 3: "도면 보기", 4: "이상 상황: 1차 N-Brine 온도 상승", 5: "밸브 조작: 환류 밸브 닫기"}


def tracks(D, NODES, REC, npass):
    """두 순서의 단계 목록. go = 띄울 화면, at = 그 화면에서 맞출 자리, demo = 시연 순서의 번호, sec = 배정 시간(초)."""
    E = D["end"]; nfor = sum(len(n["formulas"]) for n in NODES)
    nest = sum(1 for n in NODES for a in n["assume"] if a["kind"] == "est"); nhard = sum(1 for n in NODES for a in n["assume"] if a["kind"] == "hard")
    F = {f["k"]: f for n in NODES for f in n["formulas"]}
    row = [r for r in 이상.cmp_rows(D) if r[0].startswith("환류")][0]
    assert f"본류 {PIMS_MAIN[0]} · {PIMS_MAIN[1]}" in row[1], row[1]
    assert abs(E["Rmain"] - PIMS_MAIN[0]) < 0.3 and abs(E["Dmain"] - PIMS_MAIN[1]) < 0.3, "본류 환류 · 유출이 현장값과 0.3 kg/h 넘게 다르다 — '거의 같다'는 글을 고칠 것"
    assert E["Tmain"] > 101.5 + 5 and E["ThMain"] > 87.6 + 5, "온도 계산값이 현장값보다 높다는 글의 근거가 달라졌다"
    assert "에너지 수지" in F["vboil"]["law"] and "압력 평형" in F["vboil"]["law"], F["vboil"]["law"]
    verbs = " → ".join(n["verb"] for n in NODES)
    t5 = [
        dict(t="개요", sec=30, go="ov", kind="talk", scr="전체 구성",
             msg=f"CpHf 2차 정제 설비(투입 {N(E['m0'], 0)} kg)의 열 · 증기 · 액 이동을 계산해 3D 화면과 도면으로 표시하는 시뮬레이터다. 정상 운전과 이상 상황에서 흐름이 어떻게 달라지는지 확인하는 데 쓴다."),
        dict(t="계산 구조", sec=45, go="ov", at="#fig-ov", kind="talk", scr="전체 구성의 그림",
             msg=f"설비를 {len(NODES)}개 구간으로 나누어 공식 {nfor}개로 계산한다. 구간은 {verbs} 순이며, 각 공식의 산출값이 다음 구간의 입력이 된다."),
        dict(t="시연", sec=120, go="dm", kind="demo", demo=[1, 2, 4], scr="시연 순서 ① ② ④",
             msg="시뮬레이터 화면으로 전환한다. 교반에 따른 온도 분포, 정상 운전 흐름, 이상 상황(1차 N-Brine 온도 상승) 순으로 조작하고, 수치는 설비 옆에 표시되는 계산값으로 확인한다."),
        dict(t="계산 결과와 현장값 비교", sec=45, go="rs", kind="talk", scr="계산 결과와 현장값 비교",
             msg=f"투입 {N(E['m0'], 0)} kg 배치의 계산 결과는 종료 {N(E['t'])} h, 초류 {N(E['fore'])} kg, 본류 {N(E['main'])} kg이다. 현장값과 비교하면 본류 구간의 환류 · 유출 유량은 거의 같고, 온도는 계산값이 높다."),
        dict(t="한계와 개선 계획", sec=45, go="pl", kind="talk", scr="한계와 개선 계획",
             msg=f"입력값 가운데 가정 {nest}건은 계기 시계열 데이터로 정할 수 있고, 추정 {nhard}건은 물성 · 분석 자료가 더 필요하다. 식의 형태는 그대로 두고 상수를 현장 데이터에 맞춰 보정하는 작업이 남아 있다."),
    ]
    full = [
        dict(t="전체 구성", sec=120, go="ov", kind="talk", scr="전체 구성",
             msg=f"정제 설비를 {len(NODES)}개 구간으로 나누고, 구간마다 적용한 공식(총 {nfor}개)을 한 장에 표시했다. 각 공식의 산출값이 다음 구간의 입력이 된다. 압력과 끓는점이 서로 영향을 주므로, 에너지 수지와 압력 평형을 함께 만족하는 증발량을 구한다."),
        dict(t="시연 1 · 정상 운전", sec=120, go="dm", kind="demo", demo=[1, 2, 3], scr="시연 순서 ① ② ③",
             msg="공식을 설명하기 전에 화면의 동작을 먼저 보인다. 교반에 따른 온도 분포, 정상 운전 흐름, 도면 보기 순으로 조작하고, 끝나면 [일시정지]를 눌러 둔다."),
    ]
    for n in NODES:
        f = F[NODE_KEY[n["n"]]]
        full.append(dict(t=f"구간 {n['n']} · {n['name']}", sec=NODE_SEC[n["n"]], go=n["id"], kind="talk", scr=f"구간별 공식 {n['n']}", msg=n["say"], val=f"{f['name']}: {f['val']}"))
    full += [
        dict(t="이상 상황 구현 방법", sec=60, go="ab", ab="c1hot", kind="talk", scr="이상 상황",
             msg=f"원인에 해당하는 입력값 하나만 바꾸고, 정상 운전과 같은 공식으로 다시 계산한다. 시나리오 12종을 적용해, 계산된 변화의 방향과 크기를 별도로 구한 기준과 비교했다(검증 {npass} / 12 통과)."),
        dict(t="시연 2 · 이상 상황", sec=120, go="dm", kind="demo", demo=[4, 5], scr="시연 순서 ④ ⑤",
             msg="방금 설명한 시나리오를 시뮬레이터에 적용한다. [재생]을 누르고 1차 N-Brine 온도 상승을 적용했다가 되돌린 다음, 환류 밸브를 닫았다가 연다."),
        dict(t="DB 데이터 활용", sec=120, go="db", kind="talk", scr="DB 데이터 활용",
             msg=f"가정 {nest}건은 계기 시계열 데이터를 공식에 대입해 정할 수 있다. 수집 데이터, 적용 식, 결정 항목을 표로 정리했으며, 계산값과 현장값의 차이와 그 원인은 비교표에 있다."),
        dict(t="한계와 개선 계획", sec=60, go="pl", kind="talk", scr="한계와 개선 계획",
             msg=f"현재 수치의 근거 수준을 정리하며 마친다. 가정 {nest}건과 추정 {nhard}건, 계산에 포함되지 않은 현상을 밝히고 데이터 확보 후의 보정 방향을 제시한다."),
    ]
    return dict(t5=dict(name="5분 버전", slack=15, steps=t5, flow="대상과 목적 → 계산 구조 → 동작 확인(시연) → 결과와 현장값 → 한계와 계획"),
                full=dict(name="자세한 버전", slack=0, steps=full, flow="전체 구조 → 동작 확인(시연 1) → 구간별 공식 1~8 → 이상 상황의 구현 방법과 시연 2 → 데이터 활용 → 한계와 계획"))


def _split(T):
    st = T["steps"]; talk = sum(s["sec"] for s in st if s["kind"] == "talk"); demo = sum(s["sec"] for s in st if s["kind"] == "demo")
    return talk, demo, talk + demo + T["slack"]


def _track_html(key, T):
    st = T["steps"]; talk, demo, tot = _split(T)
    parts = f"설명 {mmss(talk)} · 시연 {mmss(demo)}" + (f" · 화면 전환 여유 {mmss(T['slack'])}" if T["slack"] else "")
    bar = "".join(f'<i class="tk-{s["kind"]}" style="flex:{s["sec"]}" title="{esc(s["t"])} {mmss(s["sec"])}">{i + 1}</i>' for i, s in enumerate(st)) + (f'<i class="tk-slack" style="flex:{T["slack"]}" title="여유 {mmss(T["slack"])}"></i>' if T["slack"] else "")
    li = []; cum = 0
    for i, s in enumerate(st):
        cum += s["sec"]
        li.append(f'<li class="is-{s["kind"]}"><span class="no">{i + 1}</span><span class="tt">{mmss(s["sec"])}<small>~{mmss(cum)}</small></span><div class="sb"><div class="hd"><b>{esc(s["t"])}</b>'
                  + ('<span class="kd">시연</span>' if s["kind"] == "demo" else "") + f'<button class="lnk" data-go="{s["go"]}">{esc(s["scr"])}</button></div><p>{esc(s["msg"])}</p>'
                  + (f'<p class="vl"><span>대표 계산값</span>{esc(s["val"])}</p>' if s.get("val") else "") + "</div></li>")
    return (f'<article class="track" data-track="{key}"><div class="trh"><h3>{esc(T["name"])}</h3><span class="tot">총 {mmss(tot)}</span><span class="pt">{parts}</span>'
            f'<button class="start" data-start="{key}">이 순서로 시작</button></div><p class="flow"><span>흐름</span>{esc(T["flow"])}</p><div class="tbar" role="img" aria-label="{esc(T["name"])}의 단계별 시간 배분">{bar}</div>'
            f'<ol class="tsteps">{"".join(li)}</ol></article>'), tot


def scene_gd(TR):
    a, ta = _track_html("t5", TR["t5"]); b, tb = _track_html("full", TR["full"]); talk, demo, tot = _split(TR["t5"]); slack = TR["t5"]["slack"]
    assert tot <= 300 and slack > 0
    return ('<section class="scene" id="gd" data-tab="gd" hidden><div class="sh"><h2>발표 순서</h2>' f'<span class="tag">5분 버전 {mmss(ta)} · 자세한 버전 {mmss(tb)}</span></div>'
            f'<p class="say">발표 시간에 맞춰 두 가지 순서를 마련했다. 5분 버전의 {minsec(tot)}에는 시연 {minsec(demo)}이 포함되므로, 설명은 {minsec(talk)}에 마치고 {minsec(slack)}는 화면 전환에 쓴다. '
            f'순서를 고르고 시작 버튼을 누르면 화면 위에 진행 표시줄이 나타나고, ← → 키나 {btn("이전")} · {btn("다음")} 버튼을 누르면 그 순서대로 화면이 넘어간다. 표시줄에는 단계 제목과 요지, 배정 시간, 경과 시간이 나오며, 경과 시간을 누르면 0:00부터 다시 잰다.</p>'
            '<div class="tkey"><span><i class="tk-talk"></i>설명</span><span><i class="tk-demo"></i>시연(시뮬레이터 화면)</span><span><i class="tk-slack"></i>화면 전환 여유</span><span>시간은 단계 배정 시간과 누적 시간(~)이다</span></div>'
            f'<div class="tracks">{a}{b}</div>'
            '<div class="blk"><h3>구간별 화면의 설명 순서 <small>자세한 버전의 구간 1~8 공통</small></h3><ol class="pl gl">'
            '<li>제목 아래의 요지와 그림으로 흐름의 방향을 먼저 보인다. 선의 색은 스팀 · 열, 증기, 액, 냉매, 진공을 나타낸다.</li>'
            '<li>그림의 번호 순서대로 공식의 이름, 산출값, 계산값을 설명한다. 식의 전개는 아래 카드에 있으므로 질문이 있을 때 참조한다.</li>'
            '<li>그림에 기호(a, b, c …)로 표시한 가정 · 추정 값이 어떤 근거로 정해졌는지 밝힌다.</li>'
            '<li>어떤 계기 데이터를 확보하면 그 값을 정할 수 있는지 제시하고 다음 구간으로 넘어간다.</li></ol></div></section>')


# ---------------------------------------------------------------- 시연 순서
def _shot(n, REC, label, marks=(), caps=()):
    """기록한 화면 그림 + 누르는 자리 번호. marks = (기록 묶음, 버튼 이름, 번호, 놓는 쪽). caps = (x, 글) 그림 위 띠에 적는 설명."""
    w, h = REC["img1"] if n == 1 else REC["img"]; k = w / REC["view"][0]; top = 30 if caps else 0
    b64 = base64.b64encode((HERE / f"시연_화면_{n}.webp").read_bytes()).decode("ascii")
    o = [f'<svg id="shot{n}" class="shot" viewBox="0 0 {w} {h + top}" role="img" aria-label="{esc(label)}"><image href="data:image/webp;base64,{b64}" y="{top}" width="{w}" height="{h}"/>']
    for x, t in caps: o.append(f'<text class="capt" x="{x}" y="20">{esc(t)}</text>')
    for rk, key, num, side in marks:
        x, y, ww, hh = (v * k for v in REC["rects"][rk][key])
        cx, cy = {"top": (x + ww / 2, y - 15), "bottom": (x + ww / 2, y + hh + 15), "left": (x - 15, y + hh / 2), "right": (x + ww + 15, y + hh / 2)}[side]
        o.append(f'<rect class="mkr" x="{x - 3:.1f}" y="{y - 3:.1f}" width="{ww + 6:.1f}" height="{hh + 6:.1f}" rx="6"/><circle class="mkc" cx="{cx:.1f}" cy="{cy:.1f}" r="11"/><text class="mkt" x="{cx:.1f}" y="{cy + 4.3:.1f}">{num}</text>')
    o.append("</svg>"); return "".join(o)


def scene_dm(D, NODES, REC, TR):
    S = REC["s"]; T = REC["t"]; f1 = lambda x: f"{x:.1f}"; sec = lambda k: f"{round(T[k])}초"; within = lambda k: f"{math.ceil(T[k])}초"
    assert REC["kind"] == "LUMP", "시연 기록이 가벼운 계산이 아니다 — '시작 전 준비'의 글을 고칠 것"
    Tsat = D["ab"]["c1hot"][0]["Tsat"]
    assert abs(S["s4c"]["Tsat"] - Tsat) < 1.0, "시연 기록의 포화 온도가 이상 상황 기록과 다르다"
    proc1 = (S["s1b"]["t_h"] - S["s1a"]["t_h"]) * 60                      # 교반을 세워 둔 공정 시간(분)
    note = lambda s: s["note"].split("·", 1)[1].strip()                     # '붉은 정도 = …' 뒤의 문구(화면 '밸브' 줄 오른쪽 끝에 나오는 그대로)
    mix = re.search(r"혼합 시간 (\d+)초", S["s1a"]["note"]).group(1); assert "로그 눈금 0.1~10 ℃" in S["s1a"]["note"], S["s1a"]["note"]
    fr = S["s5b"]["fillR"]
    in5 = set(TR["t5"]["steps"][2]["demo"])
    steps = [
        dict(n=1, sec=30, where="승온 구간",
             ops=[f"{btn('재생')}을 눌러 배치를 진행한다.",
                  f"왼쪽 {btn('운전')} 탭을 열고 맨 아래 '{esc(REC['rpmHead'])}'의 {btn('교반 회전수')}를 80에서 0으로 바꾼다.",
                  f"약 10초 뒤 80으로 되돌리고 {btn('운전')} 탭을 닫는다."],
             see=[f"80 rpm: 액 안에 흐름선이 보이고 색이 고르다. '밸브' 줄 오른쪽 끝의 문구는 '{esc(note(S['s1a']))}', 액 내부의 최대 온도 차는 {S['s1a']['zmax']:.2f} ℃다.",
                  f"0 rpm으로 바꾸고 {sec('s1b')} 뒤(공정 시간 {proc1:.0f}분): 벽 쪽과 위쪽만 붉어지고 중앙 하부는 평균보다 낮은 온도로 남는다. 문구는 '{esc(note(S['s1b']))}', 액 내부의 최대 온도 차는 {f1(S['s1b']['zmax'])} ℃다.",
                  f"같은 시간에 자켓 온도는 {f1(S['s1a']['Tj'])} → {f1(S['s1b']['Tj'])} ℃로 오른다. 80 rpm으로 되돌리면 {within('s1c')} 안에 벽 쪽 온도 차가 {f1(S['s1c']['dW'])} ℃로 돌아온다."],
             say="자켓 벽에서 받은 열은 교반으로 액 전체에 퍼진다. 교반이 멈추면 벽면의 열은 자연대류로만 전달되므로, 같은 스팀 개도에서도 자켓 온도가 오르고 액은 벽 쪽만 뜨거워진다. "
                 f"붉은색은 평균과의 온도 차를 로그 눈금(0.1~10 ℃)으로 강조한 표시이며, 실제 온도 차는 '밸브' 줄 오른쪽 끝의 문구로 확인한다. 혼합 시간 {mix}초는 Grenville–Nienow 상관식으로 구했고, 앵커형 임펠러의 동력수 0.35는 가정값이다.",
             ref="구간 1 자켓 · 스팀(교반 전열 상관식)",
             fig=_shot(1, REC, "교반 80 rpm과 0 rpm일 때의 정제기 화면 비교", caps=((6, "교반 80 rpm"), (REC["img1"][0] // 2 + 6, f"교반 0 rpm · {sec('s1b')} 뒤"))),
             cap=f"왼쪽은 80 rpm, 오른쪽은 0 rpm으로 바꾸고 {sec('s1b')} 뒤의 정제기다. 스팀 개도는 두 화면 모두 {S['s1a']['MV']:.0f} %다."),
        dict(n=2, sec=30, where="승온 → 초류 회수",
             ops=[f"'시간' 줄 오른쪽의 {btn('매우 빠르게')}를 5번 누른다. 그 옆의 표시가 '{esc(S['s2a']['spd'])}'이 된다.",
                  f"화면 위쪽의 상태 문구가 '초류 회수 중'으로 바뀌면 {btn('현재')}를 눌러 속도를 '{esc(S['s2b']['spd'])}'로 되돌린다."],
             see=[f"{f1(T['st2'])}초 뒤 전환류 안정화, {f1(T['st3'])}초 뒤 초류 회수로 넘어간다. 공정 시간으로는 {f1(S['s2c']['t_h'])} h다.",
                  "증기(흰 점)가 정제기 액면에서 컬럼을 지나 1차 응축기로 올라가고, 응축액이 환류 관과 유출 관으로 나뉘어 흐른다.",
                  f"설비 옆 표시값: 증발 {f1(S['s2b']['V'])} kg/h · 환류 {f1(S['s2b']['R'])} kg/h · 유출 {f1(S['s2b']['D'])} kg/h · 압력 {S['s2b']['Pstill']:.2f} mmHg · 탱크 {f1(S['s2b']['T'])} ℃ · 탑 {f1(S['s2b']['Thead'])} ℃ · 스팀 개도 {f1(S['s2b']['MV'])} %"],
             say="레시피는 승온, 전환류 안정화, 초류, 본류 순으로 진행되며, 단계별 조건이 충족되면 다음 단계로 자동 전환된다. PI 제어가 스팀 개도를 조절해 응축량을 환류 · 유출 설정값의 합에 맞춘다.",
             ref="구간 2 정제기 내부 · 구간 3 충전 컬럼 · 구간 6 환류 · 유출",
             fig=_shot(2, REC, "초류 회수 중의 시뮬레이터 화면과 속도 버튼의 위치", marks=(("r2", "fast", 1, "top"), ("r2", "cur", 2, "top"), ("r2", "phase", 3, "bottom"))),
             cap=f"초류 회수 중의 화면이다. 1은 {btn('매우 빠르게')}, 2는 {btn('현재')}, 3은 상태 문구의 위치다."),
        dict(n=3, sec=30, where="초류 회수 중",
             ops=[f"화면 위쪽의 {btn('도면으로 보기')}를 누른다.", f"확인한 뒤 같은 자리의 {btn('3D로 보기')}를 눌러 돌아온다."],
             see=["같은 계산 상태가 P&amp;ID 형태의 도면으로 표시된다. 설비 번호(T-H071, C-H071, E-H071 등)와 계기 태그, 값이 함께 나온다.",
                  "증기와 응축액의 흐름은 배관 위를 움직이는 점으로 나타난다. 휠로 확대하고 끌어서 이동한다."],
             say="3D 화면과 도면은 같은 계산값을 다르게 그린 것이다. 도면에는 계기 태그가 표시되므로 현장 계기와 하나씩 대조할 수 있다.",
             ref="DB 데이터 활용(계기 태그)",
             fig=_shot(3, REC, "도면으로 본 시뮬레이터 화면", marks=(("r3", "btn", 1, "bottom"),)),
             cap="도면으로 본 같은 시점의 화면이다. 1을 다시 누르면 3D 화면으로 돌아간다."),
        dict(n=4, sec=50, where="초류 회수 중",
             ops=[f"화면 아래 '밸브' 줄의 {btn('이상 상황 ▸')} → {btn('상황 고르기')} → {btn('1차 N-Brine 온도 상승')} → {btn('닫기')} 순으로 누른다.",
                  f"변화를 확인한 뒤 {btn('상황 1개 적용 중')} → {btn('모두 되돌리기')} → {btn('닫기')}로 되돌린다."],
             see=[f"{within('s4b')} 안에 환류 {f1(S['s4a']['R'])} → {f1(S['s4b']['R'])} kg/h, 유출 {f1(S['s4a']['D'])} → {f1(S['s4b']['D'])} kg/h로 떨어지고, {sec('s4c')} 뒤에는 둘 다 {f1(S['s4c']['R'] + S['s4c']['D'])} kg/h다.",
                  f"증기가 1차 응축기를 지나 2차 응축기로 넘어간다. 2차 응축량이 0 → {f1(S['s4b']['m2'])} kg/h가 되고, 그 응축액은 초류 탱크로 내려간다.",
                  f"1차 응축기 표시: N-Brine {f1(S['s4a']['Tcw'])} → {f1(S['s4c']['Tcw'])} ℃, 하부 {f1(S['s4a']['Tbot'])} → {f1(S['s4c']['Tbot'])} ℃. {sec('s4c')} 뒤 스팀 개도는 {f1(S['s4a']['MV'])} → {f1(S['s4c']['MV'])} %로 오른다.",
                  f"되돌리면 {within('s4d')} 안에 환류 {f1(S['s4d']['R'])} kg/h, 유출 {f1(S['s4d']['D'])} kg/h로 회복된다."],
             say=f"입력 하나(N-Brine 공급 온도 {S['s4a']['Tcw']:.0f} → {S['s4c']['Tcw']:.0f} ℃)만 바꾸고 같은 공식으로 다시 계산한 결과다. 냉매 온도가 응축기 압력에 해당하는 포화 온도({Tsat:.0f} ℃)보다 높아 1차 응축기의 처리 가능 열량이 0이 된다. "
                 "응축량이 설정값에 못 미치므로 스팀 제어가 개도를 높인다.",
             ref="구간 5 1차 응축기(ε–NTU 법) · 구간 7 2차 응축기 · 이상 상황 화면의 시나리오 1",
             fig=_shot(4, REC, "1차 N-Brine 온도 상승을 적용한 뒤의 시뮬레이터 화면", marks=(("r4", "adv", 1, "bottom"), ("r4", "ab", 2, "bottom"))),
             cap=f"시나리오를 적용하고 {sec('s4c')} 뒤의 화면이다. 1은 {btn('이상 상황 ▸')}, 2는 {btn('상황 고르기')}(적용 중에는 {btn('상황 1개 적용 중')})의 위치다."),
        dict(n=5, sec=40, where="초류 회수 중",
             ops=[f"화면 아래 '밸브' 줄의 {btn('환류')} 스위치를 끈다.", "변화를 확인한 뒤 다시 켠다."],
             see=[f"환류 {f1(S['s5a']['R'])} → {f1(S['s5b']['R'])} kg/h, 유출 {f1(S['s5a']['D'])} → {f1(S['s5b']['D'])} kg/h: 응축액 전량이 유출로 나간다.",
                  f"환류 관(길이 {fr['L']:.2f} m)은 컬럼 쪽 끝 구간만 비고, 관의 시작부터 U자 액봉 끝까지 {fr['head']:.2f} m에는 액이 남는다. U자 액봉의 액은 {S['s5b']['seal']:.2f} kg이다.",
                  f"컬럼 안으로 내려오던 환류액이 사라지고 증기만 올라간다. 다시 켜면 {within('s5c')} 안에 환류 {f1(S['s5c']['R'])} kg/h로 회복된다."],
             say="밸브를 닫으면 응축액의 배분이 다시 계산된다. 환류 관의 U자 액봉은 컬럼 노즐과 같은 높이여서 밸브를 닫아도 그 안의 액이 빠지지 않는다. "
                 "관이 비는 속도는 계산값이 아니라 표시 규칙이며, 비는 순서와 액이 남는 구간만 배관 구조에 맞추었다.",
             ref="구간 6 환류 · 유출(분배 · U자 액봉)",
             fig=_shot(5, REC, "환류 밸브를 닫은 뒤의 시뮬레이터 화면", marks=(("r5", "valve", 1, "top"),)),
             cap=f"환류 밸브를 닫고 {sec('s5b')} 뒤의 화면이다. 1은 {btn('환류')} 스위치의 위치다."),
    ]
    assert [s["n"] for s in steps] == [1, 2, 3, 4, 5]
    for key in ("t5", "full"):                                              # 순서에 배정한 시연 시간이 시연 단계의 합보다 짧지 않은지
        for s in TR[key]["steps"]:
            if s["kind"] == "demo": assert sum(x["sec"] for x in steps if x["n"] in s["demo"]) <= s["sec"], (key, s["t"])
    cards = []
    for s in steps:
        cards.append(f'<article class="dstep" data-demo="{s["n"]}"><div class="dh"><span class="num">{s["n"]}</span><h3>{esc(DEMO_NAME[s["n"]])}</h3><span class="tt">약 {s["sec"]}초</span>'
                     + ('<span class="bdg b-t5">5분 버전 포함</span>' if s["n"] in in5 else "") + f'<span class="where">{esc(s["where"])}</span></div>'
                     '<div class="dcols"><div><h4>조작</h4><ol class="ops">' + "".join(f"<li>{x}</li>" for x in s["ops"]) + "</ol></div>"
                     '<div><h4>화면 변화 <small>기록값</small></h4><ul class="pl">' + "".join(f"<li>{x}</li>" for x in s["see"]) + "</ul></div>"
                     f'<div><h4>설명 요지</h4><p>{esc(s["say"])}</p><p class="small">관련 화면: {esc(s["ref"])}</p></div></div>'
                     f'<figure><div class="scroll">{s["fig"]}</div><figcaption>{s["cap"]}</figcaption></figure></article>')
    t5 = " ".join(CIRC[i - 1] for i in sorted(in5)); d5 = sum(s["sec"] for s in steps if s["n"] in in5)
    fd = [s for s in TR["full"]["steps"] if s["kind"] == "demo"]
    return ('<section class="scene" id="dm" data-tab="gd" hidden><div class="sh"><h2>시연 순서</h2>' f'<span class="tag">시뮬레이터 {esc(REC["build"])} · 기록 {esc(REC["when"])}</span></div>'
            f'<p class="say">시뮬레이터에서 누를 버튼과 그때 화면에 나타나는 변화를 정리했다. 수치와 그림은 이 순서대로 조작하면서 기록한 것이다. '
            f'5분 버전은 {t5}만 진행하고(조작 {d5}초, 배정 {mmss(TR["t5"]["steps"][2]["sec"])}), 자세한 버전은 시연 1에서 {" ".join(CIRC[i - 1] for i in fd[0]["demo"])}, 시연 2에서 {" ".join(CIRC[i - 1] for i in fd[1]["demo"])}를 진행한다. '
            '시간이 부족하면 ①을 생략한다. 시뮬레이터를 열 수 없을 때는 아래 그림으로 대신 설명한다.</p>'
            '<div class="blk"><h3>시작 전 준비</h3><ul class="pl">'
            '<li>시뮬레이터를 발표자료와 다른 탭에 미리 열어 둔다. 화면이 열리면 CpHf 350 kg 배치의 승온이 바로 시작된다.</li>'
            f'<li>{btn("처음부터")}를 누른 뒤 {btn("일시정지")}를 눌러 둔다. {btn("처음부터")}는 속도와 교반 회전수를 되돌리지 않으므로, 속도 표시가 \'{esc(S["s0"]["spd"])}\'인지(다르면 {btn("현재")}를 누른다), 교반 회전수가 80 rpm인지 확인한다.</li>'
            f'<li>브라우저 창의 높이가 낮으면 화면 아래 \'밸브\' 줄이 접힌 채로 시작한다(기록: {REC["win"][0]} × {REC["win"][1]} 창에서는 펼쳐져 있고 {REC["low"]["wh"][0]} × {REC["low"]["wh"][1]} 창에서는 접혀 있다). 접혀 있으면 {btn(REC["low"]["btn"])}를 눌러 스위치가 보이게 해 둔다.</li>'
            f'<li>화면 아래 \'밸브\' 줄의 {btn("열 퍼짐 강조")}가 켜져 있는지 확인한다. ①의 붉은색 강조는 성능 모드가 \'가벼운 계산\'일 때 나타나며, 아래 기록값도 \'가벼운 계산\'에서 얻었다.</li>'
            f'<li>시연은 {btn("재생")}을 누르면서 시작한다. 자세한 버전에서는 시연 1을 마치고 {btn("일시정지")}를 눌러 두었다가 시연 2에서 다시 {btn("재생")}을 누른다.</li></ul></div>'
            f'<div class="dsteps">{"".join(cards)}</div></section>')


# ---------------------------------------------------------------- 요약 화면
def _bar(segs, unit, dec):
    """비례 막대 + 범례. segs = (이름, 값, 색 묶음). 1보다 작은 값은 두 자리까지 적는다."""
    b = "".join(f'<i class="sg-{c}" style="flex:{v:.4f}"></i>' for _, v, c in segs)
    lg = "".join(f'<span><i class="sg-{c}"></i>{esc(nm)} <b>{v:.{dec if v >= 1 else 2}f} {unit}</b></span>' for nm, v, c in segs)
    return f'<div class="sbar">{b}</div><div class="sleg">{lg}</div>'


def scene_rs(D, NODES, VER):
    E = D["end"]; st = {s[0]: s[1] for s in E["stages"]}; F = {f["k"]: f for n in NODES for f in n["formulas"]}
    tseg = [("승온", st[2] - st[1], "heat"), ("전환류 안정화", st[3] - st[2], "vap"), ("초류 회수", st[4] - st[3], "fore"), ("본류 회수", E["t"] - st[4], "main")]
    seal = E["m0"] - E["m"] - E["fore"] - E["main"]
    mseg = [("초류", E["fore"], "fore"), ("본류", E["main"], "main"), ("정제기 잔량", E["m"], "rest"), ("환류 U자 액봉", seal, "seal")]
    assert abs(sum(v for _, v, _ in tseg) - E["t"]) < 1e-6 and abs(sum(v for _, v, _ in mseg) - E["m0"]) < 1e-6
    rows = [r for r in 이상.cmp_rows(D) if r[0].split()[0] in ("내부", "탑", "환류", "구간")]; assert len(rows) == 4, [r[0] for r in rows]
    crow = "".join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td><td class="m">{esc(c)}</td><td>{esc(d)}</td></tr>' for a, b, c, d in rows)
    acc = F["accum"]
    return ('<section class="scene" id="rs" data-tab="sm" hidden><div class="sh"><h2>계산 결과와 현장값 비교</h2>' f'<span class="tag">투입 {N(E["m0"], 0)} kg 배치 · {esc(VER)}</span></div>'
            '<p class="q">배치 계산 결과 및 PIMS 현장값과의 차이</p>'
            '<div class="grid2"><div class="blk"><h3>배치 계산 결과 <small>레시피 운전 · 시작부터 종료까지</small></h3>'
            f'<p class="lb">소요 시간 <b>{N(E["t"])} h</b></p>{_bar(tseg, "h", 1)}'
            f'<p class="lb">물질수지 <b>{N(E["m0"], 0)} kg</b></p>{_bar(mseg, "kg", 1)}'
            f'<p class="small">{esc(acc["val"])} {bdg("hard")} {esc(acc["why"])}</p></div>'
            '<div class="blk"><h3>현장값과의 비교 <small>현장값은 PIMS 화면과 배치 트렌드 그래프(육안 판독)</small></h3>'
            f'<div class="tw"><table><tr><th></th><th>현장</th><th>계산</th><th>차이의 원인</th></tr>{crow}</table></div>'
            '<p class="small">본류 구간의 환류 · 유출 유량은 현장값과 거의 같다. 내부 온도와 탑 온도는 계산값이 높다. 증기압식의 상수와 스팀 밸브 특성식은 현재 확보한 정보만으로는 정할 수 없어 변경하지 않았으며, 시계열 데이터를 확보하면 보정한다.</p>'
            '<p class="small"><button class="lnk" data-go="db">DB 데이터 활용 화면</button>에 전체 비교표와 스팀 유량 지시값을 검토한 내용이 있다.</p></div></div></section>')


def scene_pl(D, NODES, npass):
    nfor = sum(len(n["formulas"]) for n in NODES); ndb = sum(len(n["db"]) for n in NODES)
    nest = sum(1 for n in NODES for a in n["assume"] if a["kind"] == "est"); nhard = sum(1 for n in NODES for a in n["assume"] if a["kind"] == "hard")
    tiles = [(str(nfor), "적용 공식", f"{len(NODES)}개 구간"), (str(nest), "가정", "도면 · 운전 데이터로 정할 수 있는 값"), (str(nhard), "추정", "데이터를 확보해도 정하기 어려운 값"),
             (f"{npass} / 12", "이상 상황 검증", "변화 방향과 크기를 별도 기준과 비교")]
    th = "".join(f'<div class="stat"><b>{esc(a)}</b><span>{esc(b)}</span><small>{esc(c)}</small></div>' for a, b, c in tiles)
    cnt = "".join(f'<tr><td><button class="lnk" data-go="{n["id"]}">{n["n"]} {esc(n["name"])}</button></td><td class="m">{sum(1 for a in n["assume"] if a["kind"] == "est")}</td>'
                  f'<td class="m">{sum(1 for a in n["assume"] if a["kind"] == "hard")}</td><td class="m">{len(n["db"])}</td></tr>' for n in NODES)
    hard = "".join(f'<li><b>{n["n"]} {esc(n["name"])}</b> {esc(a["what"])}</li>' for n in NODES for a in n["assume"] if a["kind"] == "hard")
    nm = "".join(f"<li>{esc(x)}</li>" for x in 이상.NOT_MODELED)
    return ('<section class="scene" id="pl" data-tab="sm" hidden><div class="sh"><h2>한계와 개선 계획</h2>' f'<span class="tag">가정 {nest}건 · 추정 {nhard}건 · DB 수집 항목 {ndb}건</span></div>'
            '<p class="q">현재 입력값의 근거 수준과 데이터 확보 후의 보정 방향</p>' f'<div class="stats">{th}</div>'
            '<div class="cols"><div class="blk"><h3>데이터로 결정할 수 있는 항목 ' + bdg("est") + '</h3>'
            f'<p class="p">가정 {nest}건은 계기 시계열 데이터를 공식에 대입해 정한다. 식의 형태는 그대로 두고 상수만 현장 데이터에 맞춰 보정한다. DB 수집 항목 {ndb}건마다 수집 데이터와 적용 식을 정리했다.</p>'
            f'<div class="tw"><table><tr><th>구간</th><th>가정</th><th>추정</th><th>DB 항목</th></tr>{cnt}</table></div>'
            '<p class="small"><button class="lnk" data-go="db">DB 데이터 활용 화면</button>에 수집 데이터 · 적용 식 · 결정 항목의 표가 있다.</p></div>'
            '<div class="blk"><h3>데이터로도 정하기 어려운 항목 ' + bdg("hard") + f'</h3><ul class="pl">{hard}</ul>'
            '<p class="small">본류 순도는 원료 · 초류 · 본류 · 잔류액의 성분 분석 데이터로 농축비 E를 정한 뒤에야 예측할 수 있다.</p></div>'
            f'<div class="blk"><h3>계산에 포함되지 않은 현상</h3><ul class="pl">{nm}</ul>'
            '<p class="small">이 현상들은 화면에도 표시하지 않는다. 이상 상황의 결과는 계산에 포함된 범위 안에서 해석한다.</p></div></div></section>')


def build(D, NODES, REC, VER):
    npass = sum(1 for r in D["chk"] if r["id"].startswith("K-") and not r["id"].endswith("-u") and r["ok"] is True)
    TR = tracks(D, NODES, REC, npass)
    scenes = [scene_rs(D, NODES, VER), scene_pl(D, NODES, npass), scene_gd(TR), scene_dm(D, NODES, REC, TR)]
    data = {k: dict(name=T["name"], slack=T["slack"], steps=[{a: b for a, b in s.items() if a in ("t", "sec", "go", "at", "ab", "demo", "kind", "msg", "val")} for s in T["steps"]]) for k, T in TR.items()}
    return scenes, data
