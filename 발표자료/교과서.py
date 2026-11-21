# -*- coding: utf-8 -*-
"""정제 교과서 만들기 — 설비 구간 8개, 항목마다 산출값 → 용도 → 식의 요지 → 계산값

실행:  python 교과서.py [점검 결과 이름]        예: python 교과서.py v130_최종
- 사용자 요구(2026-11-20): "이걸구해서 뭘어떻게쓰는지에대해 아직좀빈약한거같아. 교과서도 재정립하자. 쓸데없는건지우고 식도 최대한 단순화시켜서설명해주셈"
- 내용은 발표자료와 같은 자료에서 읽는다: 내용.py(공식 · 계산값) · 용도.py(용도 · 식의 요지) · 값.json · 점검 기록 · 시연 기록. 숫자를 손으로 옮겨 적지 않는다.
- 구간 그림은 발표자료의 그림을 그대로 쓰되, 말풍선의 식을 식의 요지로 바꾸고 가정 · 추정 표식은 뺀다(근거 목록은 발표자료에 있다).
- 계산값 흐름도(2026-11-20 사용자 요구: 구한 값이 어디로 가서 어떻게 쓰이는지 그림 한 장으로): 흐름도.py가 상자 · 선 · 고른 상자의 설명 자료를 만든다.
- 내는 것: ../정제_교과서.html(파일 하나로 열림) · 교과서_아티팩트.html(앞머리 없는 조각)
- 예전 교과서(2026-11-11: 기초 다지기 · 이름 풀이 54개 · 13장 · 헥산–톨루엔 예와 슬라이더)는 ../정제_교과서_이전판.html로 남겨 두었다.
"""
import copy, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "점검"))
_src = (HERE / "만들기.py").read_text(encoding="utf-8")
_head = _src.split("# ---------------------------------------------------------------- 조각")[0]      # 값 모으기 부분만 쓴다(발표자료는 만들지 않음)
NS = {"__file__": str(HERE / "만들기.py")}
exec(compile(_head, "만들기.py", "exec"), NS)

from 그림 import esc, eq_html, eq_width
from 내용 import N, CHAIN, GLOSS
import json
import 장면, 틀, 이상, DB결과, 흐름도, 환류비

D, NODES, END, VER, REC, TAG = NS["D"], NS["NODES"], NS["END"], NS["VER"], NS["REC"], NS["tag"]
P30 = D["snap"]["30"]["PR"]
NFOR = sum(len(n["formulas"]) for n in NODES)


# ---------------------------------------------------------------- 그림: 말풍선의 식을 식의 요지로
def eq_lines(eq, maxw=268.0, size=11.5):
    """식의 요지를 말풍선 너비에 맞게 여러 줄로 나눈다. 연산자 앞에서만 끊고, 첨자 묶음({ }) 안에서는 끊지 않는다."""
    if eq_width(eq, size) <= maxw: return [eq]
    cuts, depth = [], 0
    for i, ch in enumerate(eq):
        if ch == "{": depth += 1
        elif ch == "}": depth -= 1
        elif depth == 0 and ch == " " and eq[i + 1:i + 3] in ("= ", "× ", "÷ ", "+ ", "− ", "∝ "): cuts.append(i)
        elif depth == 0 and ch == " " and i > 0 and eq[i - 1] == ",": cuts.append(i)
    toks, a = [], 0
    for c in cuts: toks.append(eq[a:c]); a = c
    toks.append(eq[a:])
    lines, cur = [], ""
    for t in toks:
        if cur and eq_width((cur + t).strip(), size) > maxw: lines.append(cur.strip()); cur = t
        else: cur += t
    if cur.strip(): lines.append(cur.strip())
    return lines

def fig_simple(nd):
    nd2 = copy.deepcopy(nd)
    for f in nd2["formulas"]: f["eq"] = eq_lines(f["use"]["simple"])
    return 장면.FIGS[nd["n"]](nd2, D)


# ---------------------------------------------------------------- 조각
def use_html(u):
    return (f'<p><i>계산</i><span>{esc(u["calc"])}</span></p><p><i>운전</i><span>{esc(u["plant"])}</span></p>'
            + (f'<p class="ex"><i>적용 예</i><span>{esc(u["ex"])}</span></p>' if u.get("ex") else ""))

def flow_btn(k):
    """그 식을 계산값 흐름도에서 고른 상태로 여는 단추(필요한 이유 · 들어오는 값 · 쓰이는 곳 · DB 대조 결과가 흐름도 아래 칸에 나온다)."""
    return f'<button class="lnk tofl" data-to="flow" data-flow="{k}">값의 흐름 보기</button>'

def tcard(i, f):
    """핵심 계산 한 항목: 산출값 → 용도 → 식의 요지 → 계산값. 시뮬레이터의 계산식은 접어 둔다."""
    u = f["use"]; eqs = [f["eq"]] if isinstance(f["eq"], str) else f["eq"]
    return (f'<article class="tcard" data-f="{f["k"]}"><header><span class="n">{i}</span><h4>{esc(f["name"])}</h4><span class="law">{esc(f["law"])}</span>{flow_btn(f["k"])}</header><dl>'
            f'<dt>산출값</dt><dd class="gets">{esc(f["gets"])}</dd>'
            f'<dt>용도</dt><dd class="use">{use_html(u)}</dd>'
            f'<dt>식의 요지</dt><dd class="simp">{eq_html(u["simple"])}' + (f'<span class="rd">{esc(u["read"])}</span>' if u.get("read") else "") + "</dd>"
            f'<dt>계산값</dt><dd class="val">{esc(f["val"])}</dd></dl>'
            + (f'<p class="note"><b>비고</b>{esc(u["note"])}</p>' if u.get("note") else "")
            + '<details><summary>시뮬레이터의 계산식</summary>' + "".join(f'<div class="eqline">{eq_html(e)}</div>' for e in eqs)
            + f'<p class="words">{esc(f["words"])}</p></details></article>')

def sub_table(nd):
    rows = [(i + 1, f) for i, f in enumerate(nd["formulas"]) if f["use"]["sub"]]
    if not rows: return ""
    tr = "".join(f'<tr data-f="{f["k"]}"><td class="m">{i}</td><td><b>{esc(f["name"])}</b><br>{flow_btn(f["k"])}</td><td>{esc(f["gets"])}</td><td>{esc(f["use"]["calc"])} {esc(f["use"]["plant"])}'
                 + (f' <span class="exs">적용 예: {esc(f["use"]["ex"])}</span>' if f["use"].get("ex") else "") + f'</td><td>{eq_html(f["use"]["simple"])}</td><td class="m">{esc(f["val"])}</td></tr>' for i, f in rows)
    return ('<h3>보조 계산 <small>핵심 계산의 입력을 만들거나 결과를 설명하는 식</small></h3><div class="tw"><table class="subt"><tr><th></th><th>이름</th><th>산출값</th><th>용도</th><th>식의 요지</th><th>계산값</th></tr>'
            + tr + "</table></div>")

def chapter(nd):
    core = "".join(tcard(i + 1, f) for i, f in enumerate(nd["formulas"]) if not f["use"]["sub"])
    hand = "".join(f'<span class="hd"><b>{esc(a)}</b><em>→</em><b>{esc(b)}</b></span>' for a, b, k in CHAIN if k == nd["n"])
    return (f'<section class="ch" id="c{nd["n"]}"><div class="sh"><span class="num">{nd["n"]}</span><h2>{esc(nd["name"])}</h2><span class="verb">{esc(nd["verb"])}</span><span class="tag">{esc(nd["tag"])}</span></div>'
            f'<p class="q">{esc(nd["q"])}</p><p class="say">{esc(nd["say"])}</p>'
            f'<div class="hand"><span class="lb">이 구간에서 넘기는 값</span>{hand}</div>'
            f'<figure><div class="swipe">그림은 좌우로 스크롤</div><div class="scroll">{fig_simple(nd)}</div><figcaption>번호는 아래 핵심 계산 · 보조 계산의 항목 번호다. 말풍선에는 식의 요지와 계산값을 적었다. 초록색 태그는 그 값과 대조하는 현장 계기다.</figcaption></figure>'
            f'<h3>핵심 계산</h3><div class="tgrid">{core}</div>{sub_table(nd)}</section>')

def loops():
    ch = lambda items: "".join(f'<b>{esc(x)}</b>' + ('<em>→</em>' if i < len(items) - 1 else "") for i, x in enumerate(items))
    return ('<section class="ch" id="loop"><div class="sh"><h2>피드백 루프 2개</h2><span class="tag">뒤 구간의 계산값이 앞 구간의 입력으로 되돌아가는 경로</span></div>'
            '<div class="grid2"><div class="blk"><h3>압력과 끓는점</h3>'
            f'<div class="loop">{ch(["증발량", "컬럼 · 증기 배관의 압력 손실", "정제기 압력", "끓는점", "증발량"])}</div>'
            '<p>증발량이 늘면 증기 이송에 필요한 압력이 오르고, 압력이 오르면 끓는점이 높아져 증발량이 줄어든다. 시뮬레이터는 계산 단계마다 에너지 수지와 압력 평형을 함께 만족하는 증발량을 구한다. '
            f'본류의 증발량 {N(P30["vdot"])} kg/h와 정제기 압력 {N(P30["Pstill"], 2)} torr가 이렇게 구한 값이다.</p></div>'
            '<div class="blk"><h3>스팀 제어</h3>'
            f'<div class="loop">{ch(["스팀 개도", "전달 열량", "증발량", "응축량(환류 + 유출)", "설정값과의 편차", "스팀 개도"])}</div>'
            '<p>응축량이 설정값보다 작으면 스팀 밸브 개도를 높이고, 크면 낮춘다. '
            f'본류에서는 환류 {N(P30["Rkg"])} kg/h와 유출 {N(P30["Dkg"])} kg/h를 유지하는 개도가 {N(P30["MVpct"])} %다.</p></div></div></section>')

def compare():
    db = D["db"]; V = D["dbv"]
    crow = "".join(f'<tr><td>{esc(r["name"])}</td><td class="m">{DB결과.cell(r["db"])}</td><td class="m">{DB결과.cell(r["sim"])}</td><td class="m">{DB결과.cell(r["trial"])}</td><td>{esc(r["why"])}</td></tr>' for r in DB결과.cmp_rows(D))
    return ('<section class="ch" id="cmp"><div class="sh"><h2>계산값과 현장값</h2>' f'<span class="tag">현장값은 DB {len(V["배치"])}배치({esc(V["기간"])})의 구간 평균</span></div>'
            f'<div class="blk"><div class="tw"><table class="cmp"><tr><th></th><th>DB 6배치</th><th>계산 {esc(VER)}</th><th>시험 계산</th><th>차이의 원인</th></tr>{crow}</table></div>'
            f'<p class="small">{esc(DB결과.short_text(D, VER))}</p>'
            f'<p class="small">시험 계산은 시뮬레이터에 증기압식의 상수 A만 {db["A_use"]:.2f}로 바꿔 넣고 같은 레시피로 한 배치를 돌린 결과다. 표의 배관 출구 온도는 증기 배관 출구 압력의 포화 온도다. 상수를 구한 근거와 DB로 정하지 못한 항목은 발표자료의 \'DB 6배치 분석 결과\' 화면에 있다.</p>'
            '<p class="small">DB 기록이 어느 식을 확인하거나 바로잡는 데 쓰였는지는 <button class="lnk" data-to="flow" data-dbgo="*">계산값 흐름도의 DB 6배치 기록</button>에 식마다 표시했다.</p></div></section>')

def how():
    cells = [("산출값", "그 식으로 구하는 값이다."),
             ("용도", "구한 값이 계산에서는 어느 식의 입력이 되는지, 운전에서는 무엇을 판단하는 데 쓰이는지 적었다. 입력 하나를 바꿔 본 시험 기록이 있으면 적용 예로 붙였다."),
             ("식의 요지", "식을 가장 단순한 형태로 나타낸 것이다. 시뮬레이터가 실제로 쓰는 계산식은 항목마다 접어 두었다."),
             ("계산값", f"투입 {N(END['m0'], 0)} kg 배치의 본류 구간({N(P30['t_h'], 0)} h) 값이다. 다른 시점의 값은 시점을 함께 적었다.")]
    return ('<section class="ch" id="how"><div class="sh"><h2>읽는 법</h2><span class="tag">항목의 구성 · 전체 그림</span></div>'
            '<div class="how4">' + "".join(f'<div><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in cells) + "</div>"
            '<p class="small">적용 예는 레시피 운전 10 h(초류 구간)에 입력 하나를 바꾸고 30분 뒤에 읽은 값이다. 괄호 안의 번호는 발표자료 \'이상 상황\' 화면의 시나리오 번호다. '
            f'\'시연 ①\'만 예외로, 승온 구간에서 교반을 멈추고 {round(REC["t"]["s1b"])}초 뒤에 읽은 값이다(발표자료 \'시연 순서\'의 기록).</p>'
            f'<figure><div class="swipe">그림은 좌우로 스크롤</div><div class="scroll">{장면.fig_overview(NODES)}</div><figcaption>번호는 구간 번호이고, 옆의 목록은 그 위치에서 구하는 값이다(총 {NFOR}개). 번호를 누르면 해당 구간으로 이동한다.</figcaption></figure>'
            '<p class="small">구한 값이 어느 계산으로 넘어가는지는 <button class="lnk" data-to="flow">계산값 흐름도</button>에 한 장으로 그렸다.</p></section>')

FLOW_SVG, FLOW_DATA = 흐름도.build(D, NODES)
_bad = 흐름도.check_words(NODES); assert not _bad, ("용도의 '계산' 글과 흐름도의 선이 다르다", _bad)

def flow():
    nl = len(FLOW_DATA["l"]); nmain = sum(1 for l in FLOW_DATA["l"] if l[3] != "aux"); ndb = sum(len(x["t"]) for x in FLOW_DATA["db"]["src"])
    return ('<section class="ch" id="flow"><div class="sh"><h2>계산값 흐름도</h2>' f'<span class="tag">공식 {NFOR}개 · 값이 넘어가는 경로 {nl}개 · DB 기록이 쓰인 곳 {ndb}개</span></div>'
            '<p class="say">공식마다 구한 값이 어느 계산의 입력이 되는지를 한 장에 그렸다. 열과 증기 · 액의 양은 왼쪽에서 오른쪽으로(스팀 → 정제기 → 응축기 → 회수 탱크), '
            '압력은 오른쪽에서 왼쪽으로(진공펌프 → 증기 배관 → 정제기) 넘어가 정제기의 진공 비등 평형(2-4)에서 만난다. '
            '아래 줄의 DB 6배치 기록은 현장 기록이 어느 식을 확인하거나 바로잡는 데 쓰였는지를 나타낸다. 식 상자나 기록 상자를 누르면 그림과 아래 칸에 내용을 표시한다.</p>'
            f'<figure><div class="swipe">그림은 좌우로 스크롤</div><div class="scroll">{FLOW_SVG}</div></figure>'
            '<div class="blk flp" id="flow-p" aria-live="polite"><p class="small">식 상자를 누르면 그 계산이 필요한 이유, 들어오는 값, 구한 값이 쓰이는 곳, DB 6배치와 대조한 결과를 표시한다. '
            '값을 주는 식은 파란색, 그 값을 받아 쓰는 식은 주황색 테두리로 표시하고, 서로 값을 주고받는 식(피드백 루프)은 검정 점선 테두리로 표시한다. '
            '상자의 번호는 구간 번호-식 번호로, 각 구간의 핵심 계산 · 보조 계산의 번호와 같다. 위쪽의 구간 이름을 누르면 그 구간으로 이동한다. '
            f'항상 표시되는 선은 {nmain}개(주 경로와, 바로 옆 식에 들어가는 보조 입력)이고, 멀리 떨어진 보조 입력 {nl - nmain}개는 상자를 누르면 점선으로 나타난다. '
            '기록 상자를 누르면 그 기록이 쓰인 식을 선과 테두리로 표시한다. 선의 색은 대조 결과를 나타낸다(초록색: 보정값 산출 · 보정 영향 · 확인, 황색: 일부 확인 · 차이 확인, 회색 점선: 확인 불가).</p></div></section>')

def terms():
    gl = "".join(f"<tr><td><b>{esc(a)}</b></td><td>{esc(b)}</td></tr>" for a, b in GLOSS)
    return ('<section class="ch" id="terms"><div class="sh"><h2>용어</h2></div>' f'<div class="blk"><div class="tw"><table>{gl}</table></div></div>'
            f'<p class="small">수치의 출처: 시뮬레이터 {esc(VER)}의 계산 기록(값.json의 다섯 시점 · 점검 기록 {esc(TAG)} · 시연 기록 {esc(REC["when"])}). 식에 숫자를 대입하는 과정은 \'정제 계산 흐름 학습\'에 있다.</p></section>')


CSS = r"""
/* 교과서: 위에 구간 줄, 구간마다 요지 → 그림 → 핵심 계산(산출값 → 용도 → 식의 요지 → 계산값) → 보조 계산 표 */
body::before { content:""; position:fixed; inset:0 0 auto; height:env(safe-area-inset-top, 0px); background:var(--bg); z-index:10 }
.hero { display:grid; gap:6px; padding:6px 0 2px } .hero h1 { margin:0; font-size:28px; letter-spacing:-.01em } .hero p { margin:0; color:var(--sub); max-width:86ch } .hero .ver { font:500 12.5px var(--f-mono); color:var(--sub) }
.tnav { position:sticky; top:env(safe-area-inset-top, 0px); z-index:6; display:flex; flex-wrap:nowrap; overflow-x:auto; gap:5px; background:var(--bg); padding:8px 0; border-bottom:1px solid var(--line); scrollbar-width:thin }
.tnav button { flex:0 0 auto; white-space:nowrap; display:flex; align-items:center; gap:6px; border:1px solid var(--line); background:var(--panel); padding:3px 11px 3px 5px; border-radius:999px; cursor:pointer; font-size:13px; color:var(--sub) }
.tnav button i { font:700 11.5px var(--f-mono); font-style:normal; min-width:21px; height:21px; border-radius:50%; background:var(--soft); color:var(--ink); display:grid; place-items:center }
.tnav button.x { padding-left:11px } .tnav button:hover { border-color:var(--ink); color:var(--ink) }
.ch { display:grid; gap:12px; min-width:0; scroll-margin-top:64px; padding-top:10px } .ch + .ch { border-top:1px solid var(--line); padding-top:22px; margin-top:8px }
.ch h3 { font-size:15.5px; margin:6px 0 0; display:flex; align-items:baseline; gap:8px } .ch h3 small { font-weight:500; color:var(--sub); font-size:12.5px } .blk h3 { margin:0 0 8px } .blk p { margin:8px 0 0; font-size:13.5px }
.how4 { display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:10px } @media (max-width:900px) { .how4 { grid-template-columns:repeat(2, minmax(0, 1fr)) } } @media (max-width:520px) { .how4 { grid-template-columns:1fr } }
.how4 div { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:11px 13px; display:grid; gap:3px; align-content:start } .how4 b { font-size:14.5px; color:var(--acc) } .how4 span { font-size:13.5px }
.hand { display:flex; flex-wrap:wrap; align-items:center; gap:6px 14px; font-size:13px } .hand .lb { font-size:12px; font-weight:700; color:var(--sub); border:1px solid var(--line); border-radius:999px; padding:0 9px }
.hand .hd { display:inline-flex; align-items:center; gap:6px } .hand b { font-weight:600 } .hand em, .loop em { font-style:normal; color:var(--acc); font-weight:700 }
.loop { display:flex; flex-wrap:wrap; align-items:center; gap:5px 7px; font-size:13.5px } .loop b { border:1px solid var(--line); background:var(--soft); border-radius:8px; padding:1px 9px; font-weight:600 }
.tgrid { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:12px; align-items:start } @media (max-width:980px) { .tgrid { grid-template-columns:1fr } }
.tcard { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:13px 15px; display:grid; gap:8px; min-width:0 }
.tcard header { display:flex; flex-wrap:wrap; align-items:center; gap:5px 9px } .tcard .n { font:700 12px var(--f-mono); width:23px; height:23px; border-radius:50%; background:var(--ink); color:var(--panel); display:grid; place-items:center }
.tcard h4 { margin:0; font-size:16px } .tcard .law { font-size:12.5px; font-weight:600; color:var(--sub) }
.tcard dl { margin:0; display:grid; grid-template-columns:62px minmax(0, 1fr); gap:7px 10px; align-items:baseline } .tcard dt { font-size:12px; font-weight:700; color:var(--sub) } .tcard dd { margin:0; font-size:14px; min-width:0 }
.tcard .gets { font-weight:600 } .tcard .use { display:grid; gap:4px; border-left:3px solid var(--acc); padding-left:9px } .tcard .use p { margin:0; display:grid; grid-template-columns:44px minmax(0, 1fr); gap:6px }
.tcard .use i { font-style:normal; font-size:11.5px; font-weight:700; color:var(--acc); padding-top:2px } .tcard .use .ex, .tcard .use .ex i { color:var(--sub) }
.tcard .simp .eqn { font-size:17px; display:block } .eqn sup, .eqn sub { white-space:nowrap } .tcard .simp .rd { display:block; color:var(--sub); font-size:13px; margin-top:2px } .tcard .val { font:500 13px var(--f-mono); color:var(--acc) }
.tcard .note { margin:0; font-size:12.5px; color:var(--sub) } .tcard .note b { font-size:12px; margin-right:6px }
.tcard details { font-size:13px; color:var(--sub) } .tcard summary { cursor:pointer; display:inline-block; list-style:none; border:1px solid var(--line); border-radius:999px; padding:0 9px; font-size:12px; font-weight:600 }
.tcard summary::-webkit-details-marker { display:none } .tcard summary::before { content:"+ " } .tcard details[open] summary::before { content:"− " } .tcard details[open] summary { margin-bottom:5px }
.tcard details .eqn { color:var(--ink) } .tcard .words { margin:3px 0 0 }
.subt td { font-size:13px } .subt .eqn { font-size:14px } .subt .exs { display:block; color:var(--sub); font-size:12.5px } .subt td:nth-child(2) { white-space:nowrap } .subt { min-width:880px }
.ch .am { display:none }
.lnk { border:0; border-bottom:1px solid var(--acc); background:transparent; padding:0 1px; cursor:pointer; color:var(--acc); font-size:12.5px; font-weight:600; line-height:1.35 } .lnk:hover { color:var(--ink); border-color:var(--ink) }
/* 계산값 흐름도 */
figure #fig-flow { min-width:1080px }
.fl-col { fill:var(--soft); opacity:.55 } .fl-h { cursor:pointer } .fl-h circle { fill:var(--ink) } .fl-hn { fill:var(--panel); font:700 11.5px var(--f-mono) } .fl-ht { fill:var(--ink); font:700 12.5px var(--f-body) } .fl-h:hover .fl-ht { fill:var(--acc) } .fl-h:focus { outline:none } .fl-h:focus-visible .fl-ht { fill:var(--acc); text-decoration:underline }
.fl-b { cursor:pointer } .fl-b rect { fill:var(--panel); stroke:var(--line); stroke-width:1.2 } .fl-b:hover rect { stroke:var(--ink) } .fl-b:focus { outline:none } .fl-b:focus-visible rect { stroke:var(--acc); stroke-width:2.4 }
.fl-id { fill:var(--acc); font:700 10.5px var(--f-mono) } .fl-nm { fill:var(--ink); font:700 11.5px var(--f-body) } .fl-v { fill:var(--sub); font:500 10.5px var(--f-mono) }
.fl-e { fill:none; stroke-width:2 } .fl-heat { stroke:var(--heat) } .fl-mass { stroke:var(--liq) } .fl-pres { stroke:var(--vac) } .fl-ctrl { stroke:var(--ink); stroke-dasharray:6 3 } .fl-sup { stroke:var(--sub); stroke-width:1.2 } .fl-dash { stroke-dasharray:3 3 }
.fl-aux { stroke:var(--sub); stroke-width:1.5; stroke-dasharray:2 3; display:none }
.fl-m { stroke:none } .fl-m-heat { fill:var(--heat) } .fl-m-mass { fill:var(--liq) } .fl-m-pres { fill:var(--vac) } .fl-m-ctrl { fill:var(--ink) } .fl-m-sup, .fl-m-aux { fill:var(--sub) }
.fl-lab { font:700 10.5px var(--f-body); paint-order:stroke; stroke:var(--panel); stroke-width:4px; stroke-linejoin:round } .fl-lab-heat { fill:var(--heat) } .fl-lab-mass { fill:var(--liq) } .fl-lab-pres { fill:var(--vac) } .fl-lab-ctrl { fill:var(--ink) }
.fl-lg { fill:var(--sub); font:500 11.5px var(--f-body) }
#fig-flow.sel .fl-b { opacity:.3 } #fig-flow.sel .fl-b.on, #fig-flow.sel .fl-b.in, #fig-flow.sel .fl-b.out { opacity:1 }
#fig-flow.sel .fl-b.on rect { fill:var(--acc-soft); stroke:var(--ink); stroke-width:2.4 } #fig-flow.sel .fl-b.in rect { stroke:var(--liq); stroke-width:2.2 } #fig-flow.sel .fl-b.out rect { stroke:var(--ng); stroke-width:2.2 }
#fig-flow.sel .fl-b.in.out rect { stroke:var(--ink); stroke-width:2.2; stroke-dasharray:6 3 }
#fig-flow.sel .fl-e[data-s] { opacity:.1 } #fig-flow.sel .fl-e.hit { opacity:1; stroke-width:2.6; display:inline } #fig-flow.sel .fl-lab { opacity:.12 } #fig-flow.sel .fl-lab.hit { opacity:1 }
.flp { display:grid; gap:9px } .flp p { margin:0 } .flp .flh { display:flex; flex-wrap:wrap; align-items:center; gap:6px 10px } .flp .fid, .fchip span { font:700 12px var(--f-mono); color:var(--acc) } .flp .flh b { font-size:16px } .flp .sec { font-size:12.5px; color:var(--sub); margin-right:auto }
.fdl { margin:0; display:grid; grid-template-columns:72px minmax(0, 1fr); gap:5px 10px; font-size:13.5px } .fdl dt { font-size:12px; font-weight:700; color:var(--sub); padding-top:1px } .fdl dd { margin:0; min-width:0 } .fdl .m { color:var(--acc); font-size:13px }
.fio { display:grid; grid-template-columns:minmax(0, 1fr) minmax(0, 1fr); gap:14px } @media (max-width:760px) { .fio { grid-template-columns:1fr } }
.fio h4 { margin:0 0 5px; font-size:13.5px } .fio h4 small { color:var(--sub); font-weight:500 } .fio > div:first-child h4 { color:var(--liq) } .fio > div:last-child h4 { color:var(--ng) }
.fio ul { list-style:none; margin:0; padding:0; display:grid; gap:5px } .fio li { display:flex; flex-wrap:wrap; align-items:center; gap:4px 8px; font-size:13px } .fio li em { font-style:normal; font-size:11.5px; color:var(--sub); border:1px solid var(--line); border-radius:999px; padding:0 7px } .fio li.none { color:var(--sub) }
.fchip { display:inline-flex; align-items:center; gap:6px; border:1px solid var(--line); background:var(--panel); border-radius:999px; padding:1px 10px 1px 8px; font-size:13px; cursor:pointer; color:var(--ink) } .fchip:hover { border-color:var(--ink) }
.tcard.flash, tr.flash { outline:2px solid var(--acc); outline-offset:2px }
/* 흐름도: DB 6배치 기록 줄 · 식 상자의 대조 표시 · 고른 상자의 설명 칸 */
.tcard .tofl { margin-left:auto; font-size:12px } .subt .tofl { font-size:11.5px }
.fl-dband { fill:var(--db-soft); opacity:.6 }
.fl-de { fill:none; stroke:var(--db); stroke-width:1.9; display:none } .fl-de.hit { display:inline } .fl-m-db { fill:var(--db) }
.fl-dbb, .fl-dball { cursor:pointer } .fl-dbb rect { fill:var(--panel); stroke:var(--db); stroke-width:1.3 } .fl-dbb:hover rect { stroke-width:2.2 } .fl-dbb:focus, .fl-dball:focus { outline:none } .fl-dbb:focus-visible rect { stroke-width:2.6 }
.fl-dbb.on rect { fill:var(--db-soft); stroke-width:2.4 }
.fl-dn { fill:var(--ink); font:700 11.5px var(--f-body) } .fl-dt { fill:var(--db); font:600 9px var(--f-mono) } .fl-dv { fill:var(--sub); font:500 10px var(--f-body) } .fl-dtt { fill:var(--db); font:700 13px var(--f-body) }
.fl-dball rect { fill:var(--db) } .fl-dball text { fill:var(--panel); font:700 10.5px var(--f-body) } .fl-dball:hover rect, .fl-dball.on rect { fill:var(--ink) } .fl-dball:focus-visible rect { stroke:var(--ink); stroke-width:2 }
.fl-bd-cal { fill:var(--db) } .fl-bd-eff { fill:var(--panel); stroke:var(--db); stroke-width:1.8 } .fl-bd-ok { fill:var(--db) } .fl-bd-part circle { fill:var(--panel); stroke:var(--est); stroke-width:1.6 } .fl-bd-part path { fill:var(--est) } .fl-bd-no { fill:var(--panel); stroke:var(--sub); stroke-width:1.4 }
.fl-lgb { font-weight:700; fill:var(--ink) }
#fig-flow.sel .fl-dbb { opacity:.35 } #fig-flow.sel .fl-dbb.on, #fig-flow.sel .fl-dbb.hit { opacity:1 } #fig-flow.sel .fl-dbb.hit rect { stroke-width:2.4 }
#fig-flow.sel .fl-b.dbt { opacity:1 } #fig-flow.sel .fl-b.dbt rect { stroke:var(--db); stroke-width:2.2 }
#fig-flow.sel .fl-b.dbt.s-part rect, #fig-flow.sel .fl-b.dbt.s-gap rect { stroke:var(--est) } #fig-flow.sel .fl-b.dbt.s-no rect { stroke:var(--sub); stroke-dasharray:5 3 }
.fl-de-part, .fl-de-gap { stroke:var(--est) } .fl-de-no { stroke:var(--sub); stroke-dasharray:4 3 } .fl-m-dbp { fill:var(--est) } .fl-m-dbn { fill:var(--sub) }
.dst { display:inline-block; font-size:11.5px; font-weight:700; line-height:1.5; border-radius:999px; padding:0 8px; border:1px solid var(--line); white-space:nowrap }
.dst-cal { background:var(--db); border-color:var(--db); color:var(--panel) } .dst-eff { background:var(--db-soft); border-color:var(--db); color:var(--db) } .dst-ok { border-color:var(--db); color:var(--db) }
.dst-part, .dst-gap { background:var(--est-soft); border-color:var(--est); color:var(--est) } .dst-no { color:var(--sub) }
.fchip.dchip { border-color:var(--db) } .fchip.dchip span, .flp .dbid { color:var(--db) }
.fdl .fdb { display:grid; gap:7px } .fdl .fdb p { margin:0; display:flex; flex-wrap:wrap; align-items:center; gap:4px 8px } .fdl .fdb .tx { flex:1 1 100% } .fdl .fdb .none { color:var(--sub) }
.fio ul { gap:9px } .fio li, .fdbt li, .fdbl li { display:grid; gap:3px; align-items:start } .r1, .r2 { display:flex; flex-wrap:wrap; align-items:center; gap:4px 8px }
.fio li p, .fdbt li p, .fdbl li p { margin:0; font-size:13px; color:var(--sub) } .fio li b { font-size:13px; font-weight:600 }
.fdbt h4, .fdbs h4 { margin:0 0 2px; font-size:14px; color:var(--db) } .fdbt h4 small { color:var(--sub); font-weight:500 } .fdbt ul, .fdbl { list-style:none; margin:0; padding:0; display:grid; gap:10px }
.fdbs { display:grid; gap:8px; border-top:1px solid var(--line); padding-top:11px } .fdbs p { font-size:13.5px } .fdbs .cnt { color:var(--sub); font-size:13px; display:flex; flex-wrap:wrap; align-items:center; gap:4px 6px }
.fdbl .tg { font:600 11.5px var(--f-mono); color:var(--db) } .fdbl .pair { display:inline-flex; align-items:center; gap:4px } .fdbl li, .fdbt li { border-left:3px solid var(--db); padding-left:10px }
figure.plain { border:0; padding:0; background:transparent } figure.plain svg { min-width:480px } table.cmp td.m { white-space:nowrap }
"""

JS = r"""
(function(){
  /* 구간 줄 · 전체 그림의 번호를 누르면 그 구간으로 간다 */
  function to(id){ var e=document.getElementById(id); if(!e) return; try{ e.scrollIntoView({behavior:'auto', block:'start'}) }catch(x){ e.scrollIntoView() } try{ history.replaceState(null,'','#'+id) }catch(x){} }
  document.addEventListener('click', function(ev){
    var b=ev.target.closest('[data-to]'); if(b){ to(b.getAttribute('data-to')); return }
    var g=ev.target.closest('[data-go]'); if(g){ var id=g.getAttribute('data-go'); to(/^n\d$/.test(id) ? 'c'+id.slice(1) : id) }
  });
  var h=(location.hash||'').slice(1); if(h) setTimeout(function(){ to(h) }, 60);
})();
(function(){
  /* 계산값 흐름도: 식 상자를 누르면 필요한 이유 · 들어오는 값 · 쓰이는 곳 · DB 대조 결과를, 기록 상자를 누르면 그 기록이 쓰인 식을 그림과 아래 칸에 표시한다 */
  var svg=document.getElementById('fig-flow'), P=document.getElementById('flow-p'), F=window.FLOW; if(!svg||!P||!F) return;
  var DB=F.db, cur=null, curDb=null;
  var boxes=[].slice.call(svg.querySelectorAll('.fl-b')), edges=[].slice.call(svg.querySelectorAll('.fl-e[data-s]')), labs=[].slice.call(svg.querySelectorAll('.fl-lab'));
  var dboxes=[].slice.call(svg.querySelectorAll('.fl-dbb')), dlines=[].slice.call(svg.querySelectorAll('.fl-de')), dall=svg.querySelector('.fl-dball');
  var SRC={}, BYF={};
  DB.src.forEach(function(s){ SRC[s.k]=s; s.t.forEach(function(t){ (BYF[t[0]]=BYF[t[0]]||[]).push([s.k, t[1], t[2]]) }) });
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c] }) }
  function chip(k){ var n=F.n[k]; return '<button class="fchip" data-pick="'+k+'"><span>'+n.id+'</span>'+esc(n.name)+'</button>' }
  function dchip(k){ return '<button class="fchip dchip" data-dbpick="'+k+'"><span>DB</span>'+esc(SRC[k].name)+'</button>' }
  function stc(st){ return '<span class="dst dst-'+st+'" title="'+esc(DB.note[st])+'">'+esc(DB.st[st])+'</span>' }
  function summary(){
    var parts=[]; Object.keys(DB.st).forEach(function(st){ if(DB.cnt[st]) parts.push('<span>'+stc(st)+' '+DB.cnt[st]+'개</span>') });
    var rows=DB.src.map(function(s){
      return '<li><div class="r1">'+dchip(s.k)+'<span class="tg">'+esc(s.tags)+'</span></div><p>'+esc(s.how)+'</p><div class="r2">'
        +s.t.map(function(t){ return '<span class="pair">'+chip(t[0])+stc(t[1])+'</span>' }).join('')+'</div></li>' }).join('');
    return '<div class="fdbs"><h4>DB 6배치 기록이 쓰인 곳</h4><p>'+esc(DB.lead)+'</p><p class="cnt"><span>식 '+Object.keys(F.n).length+'개의 대조 결과</span>'+parts.join('')
      +'<span>대조하지 않은 식 '+DB.none+'개</span></p><ul class="fdbl">'+rows+'</ul></div>';
  }
  var home=P.innerHTML+summary(); P.innerHTML=home;
  function panelF(k, ins, outs){
    var n=F.n[k], ki=Object.keys(ins), ko=Object.keys(outs), d=BYF[k]||[];
    var li=function(l, other){ var h=F.how[l[0]+'>'+l[1]]||''; return '<li><div class="r1">'+chip(other)+'<b>'+esc(l[2])+'</b><em>'+esc(F.kind[l[3]])+'</em></div>'+(h ? '<p>'+esc(h)+'</p>' : '')+'</li>' };
    var dbh=d.length ? d.map(function(e){ return '<p>'+stc(e[1])+dchip(e[0])+'<span class="tx">'+esc(e[2])+'</span></p>' }).join('')
      : '<p class="none">DB 6배치 기록 가운데 이 식과 직접 대조한 것은 없다.</p>';
    return '<div class="flh"><span class="fid">'+n.id+'</span><b>'+esc(n.name)+'</b><span class="sec">'+esc(n.sec)+(n.sub ? ' · 보조 계산' : '')+(n.law ? ' · '+esc(n.law) : '')+'</span>'
      +'<button class="lnk" data-card="'+k+'">이 계산의 설명 보기</button><button class="lnk" data-pick="">선택 해제</button></div>'
      +'<dl class="fdl"><dt>필요한 이유</dt><dd>'+esc(n.why)+'</dd><dt>산출값</dt><dd>'+esc(n.gets)+'</dd><dt>계산값</dt><dd class="m">'+esc(n.val)+'</dd>'
      +'<dt>계산에서</dt><dd>'+esc(n.calc)+'</dd><dt>운전에서</dt><dd>'+esc(n.plant)+'</dd><dt>DB 6배치</dt><dd class="fdb">'+dbh+'</dd></dl>'
      +'<div class="fio"><div><h4>들어오는 값 <small>'+ki.length+'개</small></h4><ul>'+(ki.map(function(q){ return li(ins[q], q) }).join('') || '<li class="none">다른 식에서 받는 값이 없다. 입력값과 물성으로 계산한다.</li>')+'</ul></div>'
      +'<div><h4>구한 값이 쓰이는 곳 <small>'+ko.length+'개</small></h4><ul>'+(ko.map(function(q){ return li(outs[q], q) }).join('') || '<li class="none">다른 식의 입력으로 쓰이지 않는다. 결과를 확인하거나 해석하는 값이다.</li>')+'</ul></div></div>';
  }
  function panelD(k){
    var s=SRC[k];
    return '<div class="flh"><span class="fid dbid">DB</span><b>'+esc(s.name)+'</b><span class="sec">'+esc(s.tags)+' · DB '+DB.nb+'배치('+esc(DB.period)+')</span>'
      +'<button class="lnk" data-dbpick="*">기록 전체 보기</button><button class="lnk" data-pick="">선택 해제</button></div>'
      +'<dl class="fdl"><dt>기록</dt><dd>'+esc(s.what)+'</dd><dt>쓴 방법</dt><dd>'+esc(s.how)+'</dd></dl>'
      +'<div class="fdbt"><h4>'+(k==='none' ? '대조하지 못한 식' : '이 기록이 쓰인 식')+' <small>'+s.t.length+'개</small></h4><ul>'
      +s.t.map(function(t){ return '<li><div class="r1">'+chip(t[0])+stc(t[1])+'</div><p>'+esc(t[2])+'</p></li>' }).join('')+'</ul></div>';
  }
  function render(){
    var ins={}, outs={}, tg={}, sc={};
    svg.classList.toggle('sel', !!(cur||curDb)); svg.classList.toggle('dbm', !!curDb);
    if(cur){ F.l.forEach(function(l){ if(l[1]===cur) ins[l[0]]=l; if(l[0]===cur) outs[l[1]]=l }); (BYF[cur]||[]).forEach(function(e){ sc[e[0]]=1 }) }
    if(curDb) DB.src.forEach(function(s){ if(curDb==='*' || curDb===s.k) s.t.forEach(function(t){ tg[t[0]]=curDb==='*' ? DB.best[t[0]] : t[1] }) });
    boxes.forEach(function(b){ var q=b.getAttribute('data-k'); b.classList.toggle('on', q===cur); b.classList.toggle('in', !!ins[q]); b.classList.toggle('out', !!outs[q]); b.classList.toggle('dbt', !!tg[q]); Object.keys(DB.st).forEach(function(st){ b.classList.toggle('s-'+st, tg[q]===st) }); b.setAttribute('aria-pressed', q===cur ? 'true' : 'false') });
    edges.forEach(function(e){ e.classList.toggle('hit', !!cur && (e.getAttribute('data-s')===cur || e.getAttribute('data-d')===cur)) });
    labs.forEach(function(t){ t.classList.toggle('hit', !!cur && (t.getAttribute('data-s')===cur || t.getAttribute('data-d')===cur)) });
    dlines.forEach(function(e){ e.classList.toggle('hit', curDb==='*' || (!!curDb && e.getAttribute('data-db')===curDb) || (!!cur && e.getAttribute('data-f')===cur)) });
    dboxes.forEach(function(b){ var q=b.getAttribute('data-db'), on=curDb==='*' || curDb===q; b.classList.toggle('on', on); b.classList.toggle('hit', !!sc[q]); b.setAttribute('aria-pressed', on ? 'true' : 'false') });
    if(dall){ dall.classList.toggle('on', curDb==='*'); dall.setAttribute('aria-pressed', curDb==='*' ? 'true' : 'false') }
    P.innerHTML = cur ? panelF(cur, ins, outs) : curDb==='*' ? '<p class="small"><button class="lnk" data-pick="">선택 해제</button></p>'+summary() : curDb ? panelD(curDb) : home;
  }
  function show(k){ cur=k||null; curDb=null; render() }
  function showDb(k){ curDb=k||null; cur=null; render() }
  function pickAt(t){
    var b=t.closest('.fl-b'); if(b){ var k=b.getAttribute('data-k'); show(k===cur ? null : k); return true }
    var d=t.closest('.fl-dbb'); if(d){ var q=d.getAttribute('data-db'); showDb(q===curDb ? null : q); return true }
    if(t.closest('.fl-dball')){ showDb(curDb==='*' ? null : '*'); return true }
    return false;
  }
  svg.addEventListener('click', function(ev){ if(pickAt(ev.target)) return; if(!ev.target.closest('.fl-h')) show(null) });
  svg.addEventListener('keydown', function(ev){
    if(ev.key!=='Enter' && ev.key!==' ') return;
    if(pickAt(ev.target)){ ev.preventDefault(); return }
    var hd=ev.target.closest('.fl-h'); if(hd){ ev.preventDefault(); hd.dispatchEvent(new MouseEvent('click', {bubbles:true})) }
  });
  P.addEventListener('click', function(ev){
    var p=ev.target.closest('[data-pick]'); if(p){ show(p.getAttribute('data-pick')); return }
    var q=ev.target.closest('[data-dbpick]'); if(q){ showDb(q.getAttribute('data-dbpick')); return }
    var c=ev.target.closest('[data-card]'); if(!c) return;
    var k=c.getAttribute('data-card'), e=document.querySelector('.tcard[data-f="'+k+'"], tr[data-f="'+k+'"]'); if(!e) return;
    try{ e.scrollIntoView({block:'center'}) }catch(x){ e.scrollIntoView() }
    e.classList.add('flash'); setTimeout(function(){ e.classList.remove('flash') }, 1800);
  });
  /* 구간의 항목에서 '값의 흐름 보기', 계산값과 현장값에서 'DB 6배치 기록'을 누르면 흐름도로 가서 그 상자를 고른다(이동은 위의 data-to가 한다) */
  document.addEventListener('click', function(ev){
    var f=ev.target.closest('[data-flow]'); if(f){ show(f.getAttribute('data-flow')); return }
    var g=ev.target.closest('[data-dbgo]'); if(g) showDb(g.getAttribute('data-dbgo'));
  });
  window.__flow=show; window.__flowDb=showDb;
})();
"""

def page(standalone):
    nav = ('<nav class="tnav" aria-label="구간"><button class="x" data-to="how">읽는 법</button><button class="x" data-to="flow">계산값 흐름도</button>' + "".join(f'<button data-to="c{n["n"]}"><i>{n["n"]}</i>{esc(n["name"])}</button>' for n in NODES)
           + '<button class="x" data-to="loop">피드백 루프</button><button class="x" data-to="rr">환류비별 계산 결과</button><button class="x" data-to="cmp">계산값과 현장값</button><button class="x" data-to="terms">용어</button></nav>')
    hero = ('<header class="hero"><h1>정제 교과서</h1>'
            '<p>정제는 혼합액을 가열해 증발시키고, 그 증기를 다시 응축해 회수하는 공정이다. 시뮬레이터는 설비를 8개 구간으로 나누어 열, 증기, 액의 이동량을 계산하며, 한 구간에서 구한 값이 다음 구간의 입력이 된다.</p>'
            f'<span class="ver">CpHf 2차 정제 · 투입 {N(END["m0"], 0)} kg · 시뮬레이터 {esc(VER)} 계산값</span></header>')
    body = f'<div class="app">{hero}{nav}<main>{how()}{flow()}{"".join(chapter(n) for n in NODES)}{loops()}{환류비.section(D, VER)}{compare()}{terms()}</main></div>'
    head = '<title>정제 교과서</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n' + 틀.FONTS + "\n<style>" + 틀.CSS + CSS + "</style>\n"
    script = "<script>window.FLOW=" + json.dumps(FLOW_DATA, ensure_ascii=False).replace("</", "<\\/") + ";\n" + JS + "</script>"
    if standalone:
        return ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n' + head + "</head>\n<body>\n" + body + "\n" + script + "\n</body>\n</html>\n")
    return head + body + "\n" + script + "\n"

out1 = HERE.parent / "정제_교과서.html"; out2 = HERE / "교과서_아티팩트.html"
out1.write_text(page(True), encoding="utf-8", newline="\n"); out2.write_text(page(False), encoding="utf-8", newline="\n")
ncore = sum(1 for n in NODES for f in n["formulas"] if not f["use"]["sub"])
print("교과서", out1.name, out1.stat().st_size, "바이트 · 구간", len(NODES), "· 핵심 계산", ncore, "· 보조 계산", NFOR - ncore)
