# -*- coding: utf-8 -*-
"""정제 교과서 만들기 — 설비 구간 8개, 항목마다 산출값 → 용도 → 식의 요지 → 계산값

실행:  python 교과서.py [점검 결과 이름]        예: python 교과서.py v130_최종
- 사용자 요구(2026-11-20): "이걸구해서 뭘어떻게쓰는지에대해 아직좀빈약한거같아. 교과서도 재정립하자. 쓸데없는건지우고 식도 최대한 단순화시켜서설명해주셈"
- 내용은 발표자료와 같은 자료에서 읽는다: 내용.py(공식 · 계산값) · 용도.py(용도 · 식의 요지) · 값.json · 점검 기록 · 시연 기록. 숫자를 손으로 옮겨 적지 않는다.
- 구간 그림은 발표자료의 그림을 그대로 쓰되, 말풍선의 식을 식의 요지로 바꾸고 가정 · 추정 표식은 뺀다(근거 목록은 발표자료에 있다).
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
import 장면, 틀, 이상

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

def tcard(i, f):
    """핵심 계산 한 항목: 산출값 → 용도 → 식의 요지 → 계산값. 시뮬레이터의 계산식은 접어 둔다."""
    u = f["use"]; eqs = [f["eq"]] if isinstance(f["eq"], str) else f["eq"]
    return (f'<article class="tcard" data-f="{f["k"]}"><header><span class="n">{i}</span><h4>{esc(f["name"])}</h4><span class="law">{esc(f["law"])}</span></header><dl>'
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
    tr = "".join(f'<tr data-f="{f["k"]}"><td class="m">{i}</td><td><b>{esc(f["name"])}</b></td><td>{esc(f["gets"])}</td><td>{esc(f["use"]["calc"])} {esc(f["use"]["plant"])}'
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
    crow = "".join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td><td class="m">{esc(c)}</td><td>{esc(d)}</td></tr>' for a, b, c, d in 이상.cmp_rows(D))
    return ('<section class="ch" id="cmp"><div class="sh"><h2>계산값과 현장값</h2><span class="tag">현장값은 PIMS 화면과 배치 트렌드 그래프(육안 판독)</span></div>'
            f'<div class="blk"><div class="tw"><table><tr><th></th><th>현장</th><th>계산</th><th>차이의 원인</th></tr>{crow}</table></div>'
            '<p class="small">증기압식의 상수와 스팀 밸브 특성식은 현재 확보한 정보만으로는 정할 수 없어 변경하지 않았으며, 시계열 데이터를 확보하면 보정한다. 가정 · 추정 값의 근거와 DB 데이터 항목은 발표자료에 있다.</p></div></section>')

def how():
    chain = "".join(f"<li><span>{esc(a)} <em>→</em> {esc(b)}<u>{k}</u></span></li>" for a, b, k in CHAIN)
    cells = [("산출값", "그 식으로 구하는 값이다."),
             ("용도", "구한 값이 계산에서는 어느 식의 입력이 되는지, 운전에서는 무엇을 판단하는 데 쓰이는지 적었다. 입력 하나를 바꿔 본 시험 기록이 있으면 적용 예로 붙였다."),
             ("식의 요지", "식을 가장 단순한 형태로 나타낸 것이다. 시뮬레이터가 실제로 쓰는 계산식은 항목마다 접어 두었다."),
             ("계산값", f"투입 {N(END['m0'], 0)} kg 배치의 본류 구간({N(P30['t_h'], 0)} h) 값이다. 다른 시점의 값은 시점을 함께 적었다.")]
    return ('<section class="ch" id="how"><div class="sh"><h2>읽는 법</h2><span class="tag">항목의 구성 · 전체 그림 · 값이 넘어가는 순서</span></div>'
            '<div class="how4">' + "".join(f'<div><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in cells) + "</div>"
            '<p class="small">적용 예는 레시피 운전 10 h(초류 구간)에 입력 하나를 바꾸고 30분 뒤에 읽은 값이다. 괄호 안의 번호는 발표자료 \'이상 상황\' 화면의 시나리오 번호다. '
            f'\'시연 ①\'만 예외로, 승온 구간에서 교반을 멈추고 {round(REC["t"]["s1b"])}초 뒤에 읽은 값이다(발표자료 \'시연 순서\'의 기록).</p>'
            f'<figure><div class="swipe">그림은 좌우로 스크롤</div><div class="scroll">{장면.fig_overview(NODES)}</div><figcaption>번호는 구간 번호이고, 옆의 목록은 그 위치에서 구하는 값이다(총 {NFOR}개). 번호를 누르면 해당 구간으로 이동한다.</figcaption></figure>'
            f'<div class="blk"><h3>값이 넘어가는 순서 <small>오른쪽 번호는 해당 구간</small></h3><ol class="chain">{chain}</ol></div></section>')

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
"""

def page(standalone):
    nav = ('<nav class="tnav" aria-label="구간"><button class="x" data-to="how">읽는 법</button>' + "".join(f'<button data-to="c{n["n"]}"><i>{n["n"]}</i>{esc(n["name"])}</button>' for n in NODES)
           + '<button class="x" data-to="loop">피드백 루프</button><button class="x" data-to="cmp">계산값과 현장값</button><button class="x" data-to="terms">용어</button></nav>')
    hero = ('<header class="hero"><h1>정제 교과서</h1>'
            '<p>정제는 혼합액을 가열해 증발시키고, 그 증기를 다시 응축해 회수하는 공정이다. 시뮬레이터는 설비를 8개 구간으로 나누어 열, 증기, 액의 이동량을 계산하며, 한 구간에서 구한 값이 다음 구간의 입력이 된다.</p>'
            f'<span class="ver">CpHf 2차 정제 · 투입 {N(END["m0"], 0)} kg · 시뮬레이터 {esc(VER)} 계산값</span></header>')
    body = f'<div class="app">{hero}{nav}<main>{how()}{"".join(chapter(n) for n in NODES)}{loops()}{compare()}{terms()}</main></div>'
    head = '<title>정제 교과서</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n' + 틀.FONTS + "\n<style>" + 틀.CSS + CSS + "</style>\n"
    script = "<script>" + JS + "</script>"
    if standalone:
        return ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n' + head + "</head>\n<body>\n" + body + "\n" + script + "\n</body>\n</html>\n")
    return head + body + "\n" + script + "\n"

out1 = HERE.parent / "정제_교과서.html"; out2 = HERE / "교과서_아티팩트.html"
out1.write_text(page(True), encoding="utf-8", newline="\n"); out2.write_text(page(False), encoding="utf-8", newline="\n")
ncore = sum(1 for n in NODES for f in n["formulas"] if not f["use"]["sub"])
print("교과서", out1.name, out1.stat().st_size, "바이트 · 구간", len(NODES), "· 핵심 계산", ncore, "· 보조 계산", NFOR - ncore)
