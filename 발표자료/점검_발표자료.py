# -*- coding: utf-8 -*-
"""발표자료 점검 — 요구 목록(요구목록_발표자료.md)의 항목을 만든 HTML에서 다시 세어 판정한다.

실행:  python 점검_발표자료.py [점검 결과 이름]        예: python 점검_발표자료.py v130_최종
- 만들기.py와 따로 돈다. 판정 기준은 이 파일에만 있다(만드는 쪽이 제 기준으로 통과시키지 못하게).
- 브라우저(헤드리스 크롬)로 실제 그려진 화면에서 센다: 구조 · 겹침(어두운 · 밝은 화면) · 좁은 화면.
- 내는 것: 점검결과_발표자료.md · 점검결과_발표자료.json
"""
import json, pathlib, re, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "정제_시뮬레이터_발표자료.html"; ART = HERE / "발표자료_아티팩트.html"
DRV = pathlib.Path.home() / ".claude" / "skills" / "anatomy" / "scripts" / "drive.mjs"
tag = sys.argv[1] if len(sys.argv) > 1 else "v130_최종"
OV = (HERE / "점검_겹침.js").read_text(encoding="utf-8").split("\n", 1)[1].strip()
IDS = ["ov", "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "ab", "db", "rs", "pl", "gd", "dm"]
NFIG = 11 + 5 + 12      # 겹침을 보는 그림: 설비 그림 11(전체 1 · 구간 8 · 이상 상황 1 · DB 1) + 시연 화면 5 + 이상 상황 12가지
CASES = ["c1hot", "c1cold", "c2hot", "cwlow", "steam", "rhigh", "rlow", "leak", "pump", "pstop", "cold", "bare"]

STRUCT = r"""(()=>{const q=(s,r)=>[...(r||document).querySelectorAll(s)];const tx=e=>e?e.textContent.trim():'';const out={};
out.title=document.title;out.scriptSrc=q('script[src]').length;out.links=q('link[rel=stylesheet]').map(l=>l.href);out.imgs=q('img,iframe,object,embed').length;
out.scenes=q('.scene').map(s=>s.id);
out.nodes=q('.scene[data-tab=nd]').map(s=>{const cards=q('.fcard',s),cos=q('.co',s);
 return {id:s.id,q:tx(s.querySelector('.q')).length,cap:tx(s.querySelector('figcaption')).length,cards:cards.length,
  cardsFull:cards.filter(c=>['.eqline','.words','.gets','.val','.why'].every(k=>tx(c.querySelector(k)).length>3)).length,
  cardKeys:cards.map(c=>c.getAttribute('data-f')),coKeys:cos.map(c=>c.getAttribute('data-f')),
  coFull:cos.filter(c=>['.co-n','.co-e','.co-g','.co-v'].every(k=>tx(c.querySelector(k)).length>1)).length,
  lds:q('path.ld',s).map(p=>p.getAttribute('data-of')),
  am:q('.am',s).map(a=>a.getAttribute('data-a')+':'+tx(a.querySelector('text')).slice(0,2)),
  al:q('.alist li',s).map(l=>tx(l.querySelector('.lt'))+':'+tx(l.querySelector('.bdg'))),alFull:q('.alist li',s).filter(l=>tx(l.querySelector('.y')).length>5&&tx(l.querySelector('.e')).length>5).length,
  dl:q('.dlist li',s).length,dlFull:q('.dlist li',s).filter(l=>tx(l.querySelector('.tg')).length>2&&l.querySelector('.eqn')&&tx(l.querySelector('.g')).length>5).length,
  tgd:q('rect.tgd',s).length,badgeCo:q('.co .bd',s).length,badgeCard:q('.fcard .bdg',s).length,
  useFull:cards.filter(c=>{const u=q('.why .u',c);return u.length>=2&&tx(u[0].querySelector('i'))==='계산'&&tx(u[1].querySelector('i'))==='운전'&&u.every(x=>tx(x.querySelector('span')).length>12)}).length,
  simp:cards.filter(c=>tx(c.querySelector('.simp .eqn')).length>5).length,ex:q('.why .ex',s).length,folded:cards.filter(c=>{const d=c.querySelector('details.eqs');return d&&!d.open&&d.querySelector('.eqline')&&d.querySelector('.words')}).length,
  order:cards.filter(c=>{const k=[...c.children].map(e=>e.className.split(' ')[0]);return k.indexOf('gets')<k.indexOf('why')&&k.indexOf('why')<k.indexOf('simp')&&k.indexOf('simp')<k.indexOf('val')}).length}});
const ov=document.getElementById('ov');out.ov={pins:q('#fig-ov .pin').length,lds:q('#fig-ov path.ld').length,names:q('#fig-ov text.nl').length,ncards:q('.ncard',ov).length,gloss:q('table tr',ov).length,chain:q('.chain li',ov).length};
const ab=document.getElementById('ab'),AB=window.AB_DATA||{cases:{}};const cs=Object.values(AB.cases);
out.ab={svg:!!document.querySelector('#ab figure svg#fig-ab'),btns:q('.ablist button',ab).length,steps:q('.step',ab).length,cases:cs.length,
 full:cs.filter(c=>c.cause&&c.why&&c.crit&&c.undo&&(c.what.match(/<li>/g)||[]).length>=3&&c.mark&&Object.values(c.vals).some(v=>v.chg)).length,
 pass:cs.filter(c=>/판정: 통과/.test(c.crit)).length,vb:q('#fig-ab [data-vb]').length,marks:q('#fig-ab [data-mark]').length,
 valveKeys:[...new Set(cs.flatMap(c=>Object.keys(c.valves)))],closed:cs.map(c=>Object.entries(c.valves).filter(e=>e[1]==='closed').map(e=>e[0]).join('+'))};
const db=document.getElementById('db');const tb=q('table',db);out.db={rows:tb[0]?q('tr',tb[0]).length-1:0,tables:tb.length,tags:q('#fig-db rect.tgd').length,tagx:q('#fig-db rect.tgx').length};
out.tracks=window.TRACKS||null;
out.gd=q('#gd .track').map(t=>({key:t.getAttribute('data-track'),name:tx(t.querySelector('h3')),tot:tx(t.querySelector('.tot')),flow:tx(t.querySelector('.flow')).length,start:q('[data-start]',t).length,bar:q('.tbar i',t).length,
 steps:q('.tsteps li',t).map(l=>({t:tx(l.querySelector('.hd b')),tm:tx(l.querySelector('.tt')),go:(l.querySelector('[data-go]')||{getAttribute:()=>null}).getAttribute('data-go'),msg:tx(l.querySelector('.sb p')).length,demo:!!l.querySelector('.kd')}))}));
out.dm={tag:tx(document.querySelector('#dm .tag')),prep:q('#dm .blk li').length,steps:q('#dm .dstep').map(d=>({n:+d.getAttribute('data-demo'),t:tx(d.querySelector('h3')),ops:q('ol.ops li',d).length,see:q('.dcols ul li',d).length,
 say:tx(q('.dcols > div',d)[2]).length,img:q('figure svg image',d).filter(i=>/^data:image\/webp;base64,/.test(i.getAttribute('href'))&&i.getAttribute('href').length>20000).length,marks:q('.mkc',d).length,rings:q('.mkr',d).length,t5:!!d.querySelector('.b-t5'),cap:tx(d.querySelector('figcaption')).length}))};
out.rs={bars:q('#rs .sbar').length,segs:q('#rs .sbar i').length,rows:q('#rs table tr').length-1,legs:q('#rs .sleg span').map(tx)};
out.pl={stats:q('#pl .stat').map(e=>tx(e.querySelector('b'))),rows:q('#pl table tr').length-1,lists:q('#pl ul.pl').map(u=>q('li',u).length)};
out.subs=q('.subs button').length;out.pbar=!!document.getElementById('pbar')&&document.getElementById('pbar').hidden;
out.heads=q('h2,h3').map(h=>[...h.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join('').trim());out.tabs=q('.tabs button').map(tx);out.navs=q('.nodes button').length;
return JSON.stringify(out)})()"""
SCROLL = "(()=>{const d=document.documentElement;return JSON.stringify({scroll:1,sw:d.scrollWidth,cw:d.clientWidth})})()"

def drive(actions, width, theme=None):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(actions, f, ensure_ascii=False); path = f.name
    cmd = ["node", str(DRV), OUT.as_uri(), "--actions", path, "--width", str(width), "--height", "1000"] + (["--theme", theme] if theme else [])
    r = subprocess.run(cmd, capture_output=True, timeout=600); txt = (r.stdout or b"").decode("utf-8", "replace") + (r.stderr or b"").decode("utf-8", "replace")
    vals = []
    for m in re.finditer(r'^eval: (".*")\s*$', txt, re.M):
        try: v = json.loads(m.group(1))
        except Exception: continue
        if isinstance(v, str) and v.startswith("{"): vals.append(json.loads(v))
    other = [s.strip() for s in re.findall(r"^(?!eval:|shot ).+$", txt, re.M) if s.strip()]
    return vals, other

def go(i): return [["eval", f"(()=>{{location.hash='{i}';return 1}})()"], ["wait", 500]]

GQ = ("(()=>{const v=[...document.querySelectorAll('.scene')].filter(s=>!s.hidden)[0];const pb=document.getElementById('pbar');const tx=i=>document.getElementById(i).textContent;"
      "return JSON.stringify({gq:1,scene:v&&v.id,hidden:pb.hidden,tr:tx('pb-tr'),n:tx('pb-n'),t:tx('pb-t'),msg:tx('pb-msg'),tm:tx('pb-tm'),ck:tx('pb-ck'),pg:tx('pg'),"
      "off:[...document.querySelectorAll('.dstep')].filter(e=>!e.classList.contains('off')).map(e=>+e.getAttribute('data-demo')),"
      "top:(()=>{const e=document.querySelector('.dstep:not(.off)');return e&&v&&v.id==='dm'?Math.round(e.getBoundingClientRect().top-pb.getBoundingClientRect().bottom):null})()})})()")
def guide_run(key, n):
    """발표 순서를 시작해 끝 단계까지 → 키로 넘기며, 단계마다 보이는 장면과 표시줄을 읽는다. 마지막에 한 번 더 누르고(넘어가지 않아야 한다) ← 로 한 단계 돌아간 뒤 끝낸다."""
    a = [["wait", 2000]] + go("gd") + [["click", f"[data-start={key}]"], ["wait", 500], ["eval", GQ]]
    for _ in range(n - 1): a += [["key", "ArrowRight", "#pb-next"], ["wait", 450], ["eval", GQ]]
    a += [["key", "ArrowRight", "#pb-next"], ["wait", 300], ["eval", GQ], ["key", "ArrowLeft", "#pb-next"], ["wait", 300], ["eval", GQ], ["click", "#pb-end"], ["wait", 300], ["eval", GQ]]
    v, o = drive(a, 1440); return [d for d in v if d.get("gq")], o

def overlap_run(theme):
    a = [["wait", 2500]]
    for i in IDS: a += go(i) + [["eval", OV]]
    a += go("ab")
    for k in CASES: a += [["eval", f"(()=>{{document.querySelector('[data-ab={k}]').click();return 1}})()"], ["wait", 150], ["eval", OV]]
    vals, other = drive(a, 1440, theme); n = 0; bad = []; figs = 0
    for d in vals:
        for fid, r in d.get("figs", {}).items():
            figs += 1
            for k in ("overlap", "out", "spill", "box", "cross", "lbox", "ltext"):
                n += len(r[k]); bad += [f"{fid} {k}: {s}" for s in r[k]]
    return n, bad, figs, other

R = []   # (번호, 항목, 통과, 근거)
def item(i, name, ok, why): R.append(dict(id=i, name=name, ok=bool(ok), why=str(why)))

# ---------------------------------------------------------------- 파일
src = OUT.read_text(encoding="utf-8"); art = ART.read_text(encoding="utf-8")
ext = [u for u in re.findall(r'(?:src|href)="(https?://[^"]+)"', src) if not re.match(r"https://fonts\.(googleapis|gstatic)\.com", u)]
item("P1-1", "파일 하나로 열림(doctype 있음 · 글꼴 말고 바깥 자원 0)", src.lstrip().lower().startswith("<!doctype html>") and not ext, f"바깥 자원 {len(ext)}")
item("P1-2", "크기 16 MB 이하", OUT.stat().st_size < 16e6, f"{OUT.stat().st_size / 1e6:.2f} MB")

# ---------------------------------------------------------------- 구조(브라우저에서 센다)
vals, other = drive([["wait", 2500], ["eval", STRUCT]], 1440); S = vals[0]; ND = S["nodes"]
ncard = sum(n["cards"] for n in ND); nco = sum(len(n["coKeys"]) for n in ND)
item("P2-1", "공식 수가 세 곳에서 같음(전체 구조의 이름 · 구간 그림 말풍선 · 카드)", ncard == nco == S["ov"]["names"] and ncard >= 30, f"이름 {S['ov']['names']} · 말풍선 {nco} · 카드 {ncard}")
item("P2-2", "카드마다 식 · 말로 쓴 식 · 구하는 것 · 지금 값 · 쓰임", sum(n["cardsFull"] for n in ND) == ncard, f"{sum(n['cardsFull'] for n in ND)} / {ncard}")
item("P3-1", "구간 그림의 말풍선 = 아래 카드(공식 열쇠와 순서까지)", all(n["coKeys"] and sorted(n["coKeys"]) == sorted(n["cardKeys"]) for n in ND), f"{sum(1 for n in ND if sorted(n['coKeys']) == sorted(n['cardKeys']))} / {len(ND)} 구간")
item("P3-2", "말풍선마다 이름 · 식 · 구하는 것 · 지금 값", sum(n["coFull"] for n in ND) == nco, f"{sum(n['coFull'] for n in ND)} / {nco}")
item("P3-3", "말풍선마다 화살표 하나(같은 열쇠)", all(sorted(n["lds"]) == sorted(n["coKeys"]) for n in ND), f"화살표 {sum(len(n['lds']) for n in ND)} / 말풍선 {nco}")
item("P4-1", "구간마다 물음 한 줄과 그림 설명 한 줄", all(n["q"] > 8 and n["cap"] > 20 for n in ND), f"{sum(1 for n in ND if n['q'] > 8 and n['cap'] > 20)} / {len(ND)}")
item("P4-2", "말 풀이 8개 이상", S["ov"]["gloss"] >= 8, f"{S['ov']['gloss']}개")
ndl = sum(n["dl"] for n in ND)
item("P5-1", "구간마다 DB 항목 2개 이상(태그 · 식 · 정해지는 것), 합계 = DB 화면 표", all(n["dl"] >= 2 and n["dlFull"] == n["dl"] for n in ND) and ndl == S["db"]["rows"], f"구간 합 {ndl} · DB 화면 표 {S['db']['rows']}줄")
item("P5-2", "구간 그림마다 DB 이름표(PIMS 태그) 1개 이상", all(n["tgd"] >= 1 for n in ND), " · ".join(str(n["tgd"]) for n in ND))
item("P5-3", "DB 화면: 계기 지도의 이름표 14개 이상 · 표 3개", S["db"]["tags"] >= 14 and S["db"]["tables"] == 3, f"이름표 {S['db']['tags']} + 없음 표시 {S['db']['tagx']} · 표 {S['db']['tables']}")
kind = {"가정": "가정", "추정": "추정"}
item("P6-1", "구간 그림의 가정 · 추정 표식 = 아래 목록(글자와 구분까지)", all(n["am"] and sorted(n["am"]) == sorted(n["al"]) for n in ND), f"표식 {sum(len(n['am']) for n in ND)} · 목록 {sum(len(n['al']) for n in ND)}")
item("P6-2", "목록마다 왜 · 영향", sum(n["alFull"] for n in ND) == sum(len(n["al"]) for n in ND), f"{sum(n['alFull'] for n in ND)} / {sum(len(n['al']) for n in ND)}")
item("P6-3", "가정 · 추정 배지가 말풍선과 카드에 똑같이", all(n["badgeCo"] == n["badgeCard"] for n in ND), f"말풍선 {sum(n['badgeCo'] for n in ND)} · 카드 {sum(n['badgeCard'] for n in ND)}")
item("P7-1", "첫 장면 = 전체 구조: 번호 8 · 화살표 8 · 공식 이름 = 공식 수", S["scenes"][0] == "ov" and S["ov"]["pins"] == 8 and S["ov"]["lds"] == 8 and S["ov"]["names"] == ncard, f"번호 {S['ov']['pins']} · 화살표 {S['ov']['lds']} · 이름 {S['ov']['names']}")
item("P7-2", "구간 카드 8 · 계산 순서 12", S["ov"]["ncards"] == 8 and S["ov"]["chain"] == 12, f"카드 {S['ov']['ncards']} · 순서 {S['ov']['chain']}")
item("P8-1", "구간 장면 8 · 구간 줄 단추 8 · 탭은 처음 넷이 그대로(뒤에 요약 · 발표 순서)", len(ND) == 8 and S["navs"] == 8 and S["tabs"] == ["전체 구성", "구간별 공식", "이상 상황", "DB 데이터 활용", "요약", "발표 순서"], f"장면 {len(ND)} · 단추 {S['navs']} · 탭 {' / '.join(S['tabs'])}")
A = S["ab"]
item("P9-1", "이상 상황 탭: 2D 그림과 상황 12가지(단추 12)", A["svg"] and A["cases"] == 12 and A["btns"] == 12 and "이상 상황" in S["tabs"], f"상황 {A['cases']} · 단추 {A['btns']}")
item("P9-2", "상황마다 바꾼 입력 · 보여 준 것 3줄 이상 · 까닭 · 판정 기준 · 되돌림 · 바뀐 값", A["full"] == 12, f"{A['full']} / 12")
_ck = HERE.parent / "점검" / f"점검결과_{tag}.json"
if not _ck.exists(): _ck = HERE / f"점검결과_{tag}.json"
CHK = json.loads(_ck.read_text(encoding="utf-8"))
kpass = sum(1 for r in CHK["R"] if r["id"].startswith("K-") and not r["id"].endswith("-u") and r["ok"] is True)
item("P9-3", "구현 방법 3단계 · 값 상자 15 · 시험 결과가 점검 기록과 같음", A["steps"] == 3 and A["vb"] == 15 and A["pass"] == kpass, f"단계 {A['steps']} · 값 상자 {A['vb']} · 통과 {A['pass']} (기록 {kpass})")

# ---------------------------------------------------------------- 숫자 대조(기록에서 따로 다시 만든다)
VAL = json.loads((HERE / "값.json").read_text(encoding="utf-8")); P30 = VAL["snap"]["30"]["PR"]; END = CHK["raw"]["합침 배치 끝"]["res"]["end"]
plain = re.sub(r"<[^>]+>", "", src).replace("&amp;", "&")
want = [f"정제기 {P30['Pstill']:.2f} torr", f"컬럼 상부 {P30['Ptop']:.2f} torr", f"출구 {P30['Pexit']:.2f} torr", f"액 {P30['Tmean']:.1f} ℃", f"환류 {P30['Rkg']:.1f} kg/h", f"유출 {P30['Dkg']:.1f} kg/h",
        f"마하수 {P30['Mach']:.2f}", f"본류 {END['main']:.1f} kg", f"초류 {END['fore']:.1f} kg", f"투입 {END['m0']:.0f} kg", f"응축기 측 {P30['Pcond']:.2f} torr", f"펌프 측 {P30['Ppump']:.3f} torr",
        f"증기 {P30['vdot'] - P30['backKg']:.1f} kg/h", f"응축 {P30['Rkg'] + P30['Dkg']:.1f} = 환류 {P30['Rkg']:.1f} + 유출 {P30['Dkg']:.1f} kg/h", f"자켓 {P30['TjEff']:.1f} ℃", f"{P30['Thead']:.1f} ℃", f"본류: {P30['flood'] * 100:.0f} %", f"(차 {P30['dpPackC']:.2f})"]
# 증기 = 꼭대기를 넘는 증기(증발 − 컬럼 안 응축). 응축액 = 환류 + 유출. 코드 대조(코드_대조_결과.md) 뒤 기준을 코드에 맞췄다.
for k, key, dec, unit in (("c1hot", "MV", 1, "%"), ("steam", "V", 2, "kg/h"), ("steam", "Pstill", 2, "torr"), ("pstop", "Ppump", 2, "torr"), ("bare", "Qloss", 0, "W"), ("leak", "Tpot", 1, "℃")):
    nm = [n for n in CHK["raw"] if n.startswith("이상 상황") and f"ab_{k}_0" in CHK["raw"][n]["res"]][0]; a, b = CHK["raw"][nm]["res"][f"ab_{k}_0"], CHK["raw"][nm]["res"][f"ab_{k}_1"]
    want.append(f"{a[key]:.{dec}f} → {b[key]:.{dec}f} {unit}")
miss = [w for w in want if w not in plain and w not in src]
item("S1", "그림·글의 숫자가 계산 기록과 같음(기록에서 따로 만든 글 조각이 화면에 있음)", not miss, f"{len(want) - len(miss)} / {len(want)}" + (" · 없음: " + ", ".join(miss) if miss else ""))

# ---------------------------------------------------------------- 발표 순서(P10) — 사용자 2026-11-20
mmss = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
TR = S["tracks"] or {}; GD = {t["key"]: t for t in S["gd"]}; t5 = TR.get("t5", {"steps": [], "slack": 0}); fu = TR.get("full", {"steps": [], "slack": 0})
def tsum(T, kind=None): return sum(x["sec"] for x in T["steps"] if kind is None or x["kind"] == kind)
ok_list = all(k in GD and GD[k]["start"] == 1 and GD[k]["flow"] > 10 and len(GD[k]["steps"]) == len(TR[k]["steps"]) and
              all(a["t"] == b["t"] and a["go"] == b["go"] and a["tm"].startswith(mmss(b["sec"])) and a["msg"] > 30 and a["demo"] == (b["kind"] == "demo") for a, b in zip(GD[k]["steps"], TR[k]["steps"])) for k in ("t5", "full")) and len(S["gd"]) == 2
item("P10-1", "발표 순서 화면: 순서 2종(5분 버전 · 자세한 버전), 단계마다 제목 · 배정 시간 · 띄울 화면 · 요지, 순서마다 흐름 한 줄과 시작 버튼", ok_list and S["scenes"][0] == "ov", f"5분 버전 {len(t5['steps'])}단계 · 자세한 버전 {len(fu['steps'])}단계")
bad_go = [x["go"] for T in (t5, fu) for x in T["steps"] if x["go"] not in S["scenes"]]
tot5 = tsum(t5) + t5["slack"]; demo5 = tsum(t5, "demo"); talk5 = tsum(t5, "talk")
item("P10-2", "5분 버전: 시연을 포함해 5분 이내, 설명은 5분에서 시연 시간을 뺀 것보다 짧음", 0 < tot5 <= 300 and demo5 >= 60 and talk5 <= 300 - demo5 and GD.get("t5", {}).get("tot") == "총 " + mmss(tot5),
     f"총 {mmss(tot5)} = 설명 {mmss(talk5)} + 시연 {mmss(demo5)} + 여유 {mmss(t5['slack'])}")
gos = [x["go"] for x in fu["steps"]]; core = ["ov"] + [f"n{i}" for i in range(1, 9)] + ["ab", "db"]
pos = [gos.index(c) if c in gos else -1 for c in core]
item("P10-3", "자세한 버전: 전체 구성 → 구간 1~8 → 이상 상황 → DB 데이터 순서로 기존 화면을 모두 지나고 시연이 들어 있음, 띄울 화면이 모두 실제 화면", min(pos) >= 0 and pos == sorted(pos) and tsum(fu, "demo") > 0 and not bad_go and GD.get("full", {}).get("tot") == "총 " + mmss(tsum(fu) + fu["slack"]),
     f"총 {mmss(tsum(fu) + fu['slack'])} · 설명 {mmss(tsum(fu, 'talk'))} · 시연 {mmss(tsum(fu, 'demo'))}" + (f" · 없는 화면 {bad_go}" if bad_go else ""))
gbad = []; goth = []
for key, T in (("t5", t5), ("full", fu)):
    g, o = guide_run(key, len(T["steps"])); goth += o; n = len(T["steps"]); cum = 0
    if len(g) != n + 3: gbad.append(f"{key}: 읽은 횟수 {len(g)}"); continue
    for i, (st, x) in enumerate(zip(T["steps"], g[:n])):
        cum += st["sec"]; tot = tsum(T) + T["slack"]
        want_tm = f"배정 {mmss(st['sec'])} · 누적 {mmss(cum)} / {mmss(tot)}"
        if x["hidden"] or x["scene"] != st["go"] or x["t"] != st["t"] or x["msg"] != st["msg"] or x["n"] != f"{i + 1} / {n}" or x["pg"] != f"{i + 1} / {n}" or x["tm"] != want_tm or not x["ck"].startswith("경과 "):
            gbad.append(f"{key} {i + 1}단계: 화면 {x['scene']} · {x['n']} · {x['tm']}")
        if st["kind"] == "demo" and (x["off"] != st["demo"] or x["top"] is None or not (0 <= x["top"] <= 40)): gbad.append(f"{key} {i + 1}단계 시연: 강조 {x['off']} · 표시줄 아래 {x['top']}px")
    if g[n]["n"] != f"{n} / {n}" or g[n]["scene"] != T["steps"][-1]["go"]: gbad.append(f"{key}: 끝에서 더 넘어감")
    if g[n + 1]["n"] != f"{n - 1} / {n}": gbad.append(f"{key}: ← 키로 돌아가지 않음")
    if not g[n + 2]["hidden"] or g[n + 2]["scene"] != "gd": gbad.append(f"{key}: 끝내기 뒤 표시줄이 남음")
item("P10-4", "진행 표시줄: 시작하면 → 키로 단계 순서대로 화면이 바뀌고 단계 · 요지 · 배정/누적 시간 · 경과 시간이 나옴, 시연 단계는 해당 번호만 강조, 끝내면 사라짐", not gbad and S["pbar"], f"5분 버전 {len(t5['steps'])}단계 · 자세한 버전 {len(fu['steps'])}단계 넘김" + (" · " + "; ".join(gbad[:3]) if gbad else ""))
DM = S["dm"]["steps"]; in5 = sorted(next((x["demo"] for x in t5["steps"] if x["kind"] == "demo"), []))
item("P10-5", "시연 순서: 단계 5, 단계마다 조작 · 화면 변화 2줄 이상 · 설명 요지 · 화면 그림, 2~5번 그림에 누르는 자리 번호, '5분 버전 포함' 표시 = 5분 버전의 시연 번호, 준비 5줄",
     [d["n"] for d in DM] == [1, 2, 3, 4, 5] and all(d["ops"] >= 2 and d["see"] >= 2 and d["say"] > 40 and d["img"] == 1 and d["cap"] > 15 for d in DM) and all(d["marks"] >= 1 and d["marks"] == d["rings"] for d in DM[1:]) and sorted(d["n"] for d in DM if d["t5"]) == in5 and S["dm"]["prep"] == 5,
     f"단계 {len(DM)} · 그림 {sum(d['img'] for d in DM)} · 번호 {sum(d['marks'] for d in DM)} · 5분 버전 {in5}")
REC = json.loads((HERE / "시연_기록.json").read_text(encoding="utf-8")); Q = REC["s"]; f1 = lambda x: f"{x:.1f}"
wantd = [f"자켓 온도는 {f1(Q['s1a']['Tj'])} → {f1(Q['s1b']['Tj'])} ℃", f"액 내부의 최대 온도 차는 {f1(Q['s1b']['zmax'])} ℃", f"{f1(REC['t']['st3'])}초 뒤 초류 회수", f"증발 {f1(Q['s2b']['V'])} kg/h · 환류 {f1(Q['s2b']['R'])} kg/h · 유출 {f1(Q['s2b']['D'])} kg/h",
         f"환류 {f1(Q['s4a']['R'])} → {f1(Q['s4b']['R'])} kg/h, 유출 {f1(Q['s4a']['D'])} → {f1(Q['s4b']['D'])} kg/h", f"2차 응축량이 0 → {f1(Q['s4b']['m2'])} kg/h", f"스팀 개도는 {f1(Q['s4a']['MV'])} → {f1(Q['s4c']['MV'])} %",
         f"환류 {f1(Q['s5a']['R'])} → {f1(Q['s5b']['R'])} kg/h, 유출 {f1(Q['s5a']['D'])} → {f1(Q['s5b']['D'])} kg/h", f"U자 액봉의 액은 {Q['s5b']['seal']:.2f} kg"]
missd = [w for w in wantd if w not in plain]
vdeck = re.search(r"v\d+", S["dm"]["tag"]); nbadrec = sum(1 for c in REC["check"] if not c["ok"])
item("P10-6", "시연 기록: 기록한 시뮬레이터 판 = 발표자료의 판, 기록의 자체 확인 실패 0, 기록에서 따로 만든 숫자 글이 화면에 있음", REC["ver"] == (CHK.get("ver") or REC["ver"]) and bool(vdeck) and vdeck.group(0) == REC["ver"] and nbadrec == 0 and len(REC["check"]) >= 15 and not missd,
     f"판 {REC['ver']} · 자체 확인 {len(REC['check'])}항목 실패 {nbadrec} · 숫자 글 {len(wantd) - len(missd)} / {len(wantd)}" + (" · 없음: " + ", ".join(missd) if missd else ""))
nfor_ = sum(n["cards"] for n in ND); nal = [x for n in ND for x in n["al"]]; nest_ = sum(1 for x in nal if x.endswith("가정")); nhard_ = sum(1 for x in nal if x.endswith("추정"))
wants = [f"소요 시간 {END['t']:.1f} h", f"초류 {END['fore']:.1f} kg", f"본류 {END['main']:.1f} kg", f"정제기 잔량 {END['m']:.1f} kg", f"환류 U자 액봉 {END['m0'] - END['m'] - END['fore'] - END['main']:.2f} kg"]
flat = plain.replace(" ", ""); misss = [w for w in wants if w.replace(" ", "") not in flat]
item("P10-7", "요약 화면 2: 배치 결과 막대 2(시간 4칸 · 물질 4칸) · 현장값 비교 4줄 · 지표 4(공식 · 가정 · 추정 수가 본문과 같음) · 구간 표 8줄 · 추정 목록 = 추정 수, 숫자가 기록과 같음",
     S["rs"]["bars"] == 2 and S["rs"]["segs"] == 8 and S["rs"]["rows"] == 4 and S["pl"]["stats"][:3] == [str(nfor_), str(nest_), str(nhard_)] and len(S["pl"]["stats"]) == 4 and S["pl"]["rows"] == 8 and S["pl"]["lists"][0] == nhard_ and S["subs"] == 4 and not misss,
     f"지표 {' · '.join(S['pl']['stats'])} · 추정 목록 {S['pl']['lists'][0]} · 숫자 글 {len(wants) - len(misss)} / {len(wants)}" + (" · 없음: " + ", ".join(misss) if misss else ""))

# ---------------------------------------------------------------- 공식 카드의 용도 · 식의 요지(P11) — 사용자 2026-11-20
nex = sum(n["ex"] for n in ND)
item("P11-1", "공식 카드마다 산출값 → 용도(계산 · 운전 두 줄) → 식의 요지 → 계산값 순, 계산식 · 말로 쓴 식은 접어 둠", sum(n["useFull"] for n in ND) == ncard and sum(n["simp"] for n in ND) == ncard and sum(n["folded"] for n in ND) == ncard and sum(n["order"] for n in ND) == ncard,
     f"용도 두 줄 {sum(n['useFull'] for n in ND)} · 식의 요지 {sum(n['simp'] for n in ND)} · 접은 계산식 {sum(n['folded'] for n in ND)} · 순서 {sum(n['order'] for n in ND)} / {ncard}")
def _ab(k):
    nm = [n for n in CHK["raw"] if n.startswith("이상 상황") and f"ab_{k}_0" in CHK["raw"][n]["res"]][0]; r = CHK["raw"][nm]["res"]; return r[f"ab_{k}_0"], r[f"ab_{k}_1"]
a, b = _ab("bare"); wantu = [f"열손실이 {a['Qloss']:.0f} → {b['Qloss']:.0f} W"]
a, b = _ab("steam"); wantu += [f"증발량이 {a['V']:.1f} → {b['V']:.1f} kg/h", f"범람률이 {a['flood'] * 100:.0f} → {b['flood'] * 100:.0f} %"]
a, b = _ab("leak"); wantu += [f"펌프 측 압력이 {a['Ppump']:.2f} → {b['Ppump']:.2f} torr", f"끓는점이 {a['Tbub']:.1f} → {b['Tbub']:.1f} ℃"]
a, b = _ab("c1cold"); wantu += [f"{a['subR']:.2f} → {b['subR']:.2f} kg"]
a, b = _ab("rlow"); wantu += [f"{a['xD']:.2f} → {b['xD']:.2f} mol%"]
a, b = _ab("cwlow"); wantu += [f"처리 가능 열량이 {b['cap1']:.0f} W"]
a, b = _ab("pstop"); wantu += [f"펌프 측 압력이 {a['Ppump']:.2f} → {b['Ppump']:.2f} torr가 되어 비등이 멈춘다"]
a, b = _ab("c1hot"); wantu += [f"개도를 {a['MV']:.1f} → {b['MV']:.1f} %로 높인다"]
missu = [w for w in wantu if w not in plain]
item("P11-2", "적용 예 12개 이상, 그 숫자가 이상 상황 기록과 같음(기록에서 따로 만든 글 조각이 화면에 있음)", nex >= 12 and not missu, f"적용 예 {nex}개 · 숫자 글 {len(wantu) - len(missu)} / {len(wantu)}" + (" · 없음: " + ", ".join(missu) if missu else ""))

# ---------------------------------------------------------------- 겹침 · 좁은 화면 · 오류
nd_, bad_d, figs_d, oth_d = overlap_run(None); nl_, bad_l, figs_l, oth_l = overlap_run("light")
item("S2", "겹침 · 그림 밖 · 상자 넘침 · 화살표 엇갈림 0(어두운 · 밝은 화면, 설비 그림 11 + 시연 화면 5 + 상황 12)", nd_ == 0 and nl_ == 0 and figs_d == NFIG and figs_l == NFIG, f"어두운 {nd_} · 밝은 {nl_} · 본 그림 {figs_d} + {figs_l}" + (" · " + "; ".join((bad_d + bad_l)[:4]) if nd_ + nl_ else ""))
sc = {}
for w in (390, 768, 1440):
    a = [["wait", 2000]]
    for i in IDS: a += go(i) + [["eval", SCROLL]]
    v, o = drive(a, w); sc[w] = (max(d["sw"] - d["cw"] for d in v if d.get("scroll")), len(v), o)
item("S3", "쪽 가로 스크롤 없음(390 · 768 · 1440 너비, 장면 15)", all(x[0] <= 0 and x[1] == len(IDS) for x in sc.values()), " · ".join(f"{w}: 넘침 {x[0]}" for w, x in sc.items()))
cons = [s for s in other + oth_d + oth_l + goth + sum((x[2] for x in sc.values()), []) if not s.startswith("console: clean")]
item("S4", "콘솔 오류 0", not cons, "; ".join(cons[:3]) or "없음")
bad_h = [h for h in S["heads"] if re.search(r"(다|요|까|죠)[.?!]?$", h) and not h.endswith("순서")]
item("S5", "제목(h2 · h3)이 명사형", not bad_h, f"제목 {len(S['heads'])}개" + (" · " + ", ".join(bad_h) if bad_h else ""))
okart = ("<title>" in art[:8000] and 'name="claude:viewport-fit-sides"' in art[:8000] and not re.search(r"<!doctype|<html[\s>]|<head[\s>]|<body[\s>]", art, re.I)
         and "@media (prefers-color-scheme: dark)" in art and ':root[data-theme="dark"]' in art and "env(safe-area-inset-left" in art)
item("S6", "아티팩트 조각: 제목 · 옆 여백 표시 · 밝은/어두운 색 묶음, doctype/html/head/body 없음", okart, f"{ART.stat().st_size / 1e3:.0f} KB")
item("S7", "이상 상황의 밸브 색은 입력으로 바꾼 밸브만(닫힘 표시는 펌프 정지의 PCV 하나)", A["valveKeys"] == ["PCV"] and sum(1 for c in A["closed"] if c) == 1 and A["marks"] >= 9, f"밸브 {A['valveKeys']} · 닫힘 표시 {sum(1 for c in A['closed'] if c)}곳")

npass = sum(1 for r in R if r["ok"]); nfail = len(R) - npass
lines = [f"# 발표자료 점검 결과 — 통과 {npass} · 실패 {nfail}", "", f"- 대상: `{OUT.name}` ({OUT.stat().st_size / 1e3:.0f} KB) · 점검 기록 `{tag}`", "- 기준과 출처: `요구목록_발표자료.md`", "", "| 번호 | 항목 | 판정 | 근거 |", "|---|---|---|---|"]
for r in R: lines.append(f"| {r['id']} | {r['name']} | {'통과' if r['ok'] else '**실패**'} | {r['why']} |")
S8 = "- S8 식은 코드가 계산하는 그대로: `코드_대조_결과.md`(공식 35개를 시뮬레이터 코드와 따로 대조한 기록). 위 통과 수에는 넣지 않았다."
if (HERE / "코드_대조_결과.md").exists(): lines += ["", S8]      # S8은 이 점검기가 세지 않는다(코드를 읽어 대조한 기록을 가리킨다)
(HERE / "점검결과_발표자료.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
(HERE / "점검결과_발표자료.json").write_text(json.dumps(dict(tag=tag, npass=npass, nfail=nfail, R=R), ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
print(f"통과 {npass} · 실패 {nfail}")
for r in R:
    if not r["ok"]: print("  실패", r["id"], r["name"], "—", r["why"])
