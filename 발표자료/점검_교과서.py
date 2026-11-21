# -*- coding: utf-8 -*-
"""정제 교과서 점검 — 요구 목록(요구목록_교과서.md)의 항목을 만든 HTML에서 다시 세어 판정한다.

실행:  python 점검_교과서.py [점검 결과 이름]        예: python 점검_교과서.py v130_최종
- 교과서.py와 따로 돈다. 판정 기준은 이 파일에만 있다.
- 브라우저(헤드리스 크롬)로 실제 그려진 화면에서 센다: 구조 · 그림 겹침(어두운 · 밝은 화면) · 좁은 화면 · 구간 이동.
- 내는 것: 점검결과_교과서.md · 점검결과_교과서.json
"""
import json, pathlib, re, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "정제_교과서.html"; ART = HERE / "교과서_아티팩트.html"; DECK = HERE.parent / "정제_시뮬레이터_발표자료.html"
def _drive():
    loc = HERE.parent / "점검" / "도구" / "drive.mjs"
    return str(loc) if loc.exists() else str(pathlib.Path.home() / ".claude" / "skills" / "anatomy" / "scripts" / "drive.mjs")
tag = sys.argv[1] if len(sys.argv) > 1 else "v130_최종"
OV = (HERE / "점검_겹침.js").read_text(encoding="utf-8").split("\n", 1)[1].strip()

STRUCT = r"""(()=>{const q=(s,r)=>[...(r||document).querySelectorAll(s)];const tx=e=>e?e.textContent.trim():'';const out={};
out.title=document.title;out.h1=tx(document.querySelector('h1'));out.secs=q('section.ch').map(s=>s.id);out.nav=q('.tnav button').map(b=>b.getAttribute('data-to'));
out.ch=q('section.ch').filter(s=>/^c\d$/.test(s.id)).map(s=>{const cards=q('.tcard',s),rows=q('.subt tr[data-f]',s);
 return {id:s.id,q:tx(s.querySelector('.q')).length,say:tx(s.querySelector('.say')).length,hand:q('.hand .hd',s).length,fig:q('figure svg',s).length,cap:tx(s.querySelector('figcaption')).length,
  keys:cards.map(c=>c.getAttribute('data-f')),subkeys:rows.map(r=>r.getAttribute('data-f')),co:q('.co',s).map(c=>c.getAttribute('data-f')),
  full:cards.filter(c=>tx(c.querySelector('dd.gets')).length>3&&q('dd.use p',c).length>=2&&q('dd.use p',c).every(p=>tx(p.querySelector('span')).length>12)&&tx(c.querySelector('dd.simp .eqn')).length>5&&tx(c.querySelector('dd.val')).length>3&&c.querySelector('details .eqline')&&tx(c.querySelector('details .words')).length>5).length,
  ex:q('dd.use .ex',s).length,subfull:rows.filter(r=>q('td',r).length===6&&q('td',r).every(t=>tx(t).length>0)).length,
  vals:Object.fromEntries(cards.map(c=>[c.getAttribute('data-f'),tx(c.querySelector('dd.val'))]).concat(rows.map(r=>[r.getAttribute('data-f'),tx(q('td',r)[5])]))),
  coeq:Object.fromEntries(q('.co',s).map(c=>[c.getAttribute('data-f'),q('.co-e',c).map(tx).join(' ')])),
  simp:Object.fromEntries(cards.map(c=>[c.getAttribute('data-f'),tx(c.querySelector('dd.simp .eqn'))]).concat(rows.map(r=>[r.getAttribute('data-f'),tx(q('td',r)[4])]))),
  amShown:q('.am',s).filter(a=>getComputedStyle(a).display!=='none').length,tgd:q('rect.tgd',s).length}});
out.how={cells:q('#how .how4 > div').length,fig:q('#how figure svg').length,pins:q('#fig-ov .pin').length,chain:q('#how .chain li').length,toflow:q('#how [data-to=flow]').length};
const fl=document.getElementById('fig-flow');out.flow=fl?{boxes:q('.fl-b',fl).map(b=>({k:b.getAttribute('data-k'),id:tx(b.querySelector('.fl-id')),v:q('.fl-v',b).map(tx).join(' ')})),edges:q('.fl-e[data-s]',fl).map(e=>[e.getAttribute('data-s'),e.getAttribute('data-d'),getComputedStyle(e).display!=='none']),
 labs:q('.fl-lab',fl).map(tx),heads:q('.fl-h',fl).map(h=>h.getAttribute('data-to')),data:window.FLOW||null,panel:tx(document.getElementById('flow-p')).length}:null;
out.cards=q('.tcard[data-f], tr[data-f]').map(c=>{const sec=c.closest('section.ch').id.slice(1);const n=c.matches('tr')?tx(q('td',c)[0]):tx(c.querySelector('.n'));return {k:c.getAttribute('data-f'),id:sec+'-'+n,calc:c.matches('tr')?tx(q('td',c)[3]):tx(c.querySelector('dd.use p span'))}});
const rr=document.getElementById('rr');out.rr=rr?{figs:q('figure svg',rr).map(s=>s.id),bands:q('.plot-band',rr).length,pts:q('figure svg circle',rr).length,tx:tx(rr).replace(/\s+/g,' ')}:null;
out.cmpx={cols:q('#cmp table.cmp th').length,cells:q('#cmp table.cmp td').map(tx),tx:tx(document.getElementById('cmp')).replace(/\s+/g,' ')};
out.loop=q('#loop .loop').length;out.cmp=q('#cmp table tr').length-1;out.terms=q('#terms table tr').length;
out.heads=q('h1,h2,h3,h4').map(h=>[...h.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join('').trim());
return JSON.stringify(out)})()"""
SCROLL = "(()=>{const d=document.documentElement;return JSON.stringify({scroll:1,sw:d.scrollWidth,cw:d.clientWidth})})()"
NAVQ = "(()=>{const e=document.getElementById('%s');const n=document.querySelector('.tnav');return JSON.stringify({nav:'%s',top:Math.round(e.getBoundingClientRect().top),navb:Math.round(n.getBoundingClientRect().bottom),hash:location.hash})})()"

def drive(actions, width, theme=None, target=None):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(actions, f, ensure_ascii=False); path = f.name
    cmd = ["node", _drive(), (target or OUT).as_uri(), "--actions", path, "--width", str(width), "--height", "1000"] + (["--theme", theme] if theme else [])
    r = subprocess.run(cmd, capture_output=True, timeout=600); txt = (r.stdout or b"").decode("utf-8", "replace") + (r.stderr or b"").decode("utf-8", "replace")
    vals = []
    for m in re.finditer(r'^eval: (".*")\s*$', txt, re.M):
        try: v = json.loads(m.group(1))
        except Exception: continue
        if isinstance(v, str) and v.startswith("{"): vals.append(json.loads(v))
    other = [s.strip() for s in re.findall(r"^(?!eval:|shot ).+$", txt, re.M) if s.strip()]
    return vals, other

R = []
def item(i, name, ok, why): R.append(dict(id=i, name=name, ok=bool(ok), why=str(why)))

src = OUT.read_text(encoding="utf-8"); art = ART.read_text(encoding="utf-8")
plain = re.sub(r"<[^>]+>", "", re.sub(r"<(script|style).*?</\1>", "", src, flags=re.S)).replace("&amp;", "&")
ext = [u for u in re.findall(r'(?:src|href)="(https?://[^"]+)"', src) if not re.match(r"https://fonts\.(googleapis|gstatic)\.com", u)]
item("T1-1", "파일 하나로 열림(doctype 있음 · 글꼴 말고 바깥 자원 0) · 크기 16 MB 이하", src.lstrip().lower().startswith("<!doctype html>") and not ext and OUT.stat().st_size < 16e6, f"바깥 자원 {len(ext)} · {OUT.stat().st_size / 1e3:.0f} KB")

vals, other = drive([["wait", 2500], ["eval", STRUCT]], 1440); S = vals[0]; CH = S["ch"]
# 발표자료의 공식 열쇠 · 계산값 · 계산식(같은 자료에서 만든 것이어야 한다)
dv, _ = drive([["wait", 2500], ["eval", r"""(()=>{const q=(s,r)=>[...(r||document).querySelectorAll(s)];const tx=e=>e?e.textContent.trim():'';
 return JSON.stringify({deck:1,cards:q('.fcard').map(c=>({k:c.getAttribute('data-f'),val:tx(c.querySelector('.val')).replace(/^계산값/,''),simp:tx(c.querySelector('.simp .eqn')),eq:q('.eqline',c).map(tx).join(' ')}))})})()"""]], 1440, target=DECK)
DK = {c["k"]: c for c in dv[0]["cards"]}
keys = [k for c in CH for k in c["keys"] + c["subkeys"]]; ncore = sum(len(c["keys"]) for c in CH); nsub = sum(len(c["subkeys"]) for c in CH)
want_secs = ["how", "flow"] + [f"c{i}" for i in range(1, 9)] + ["loop", "rr", "cmp", "terms"]
item("T2-1", "구성: 읽는 법 → 계산값 흐름도 → 구간 8개 → 피드백 루프 → 환류비별 계산 결과 → 계산값과 현장값 → 용어, 구간 줄의 버튼이 같은 순서", S["secs"] == want_secs and S["nav"] == want_secs and S["h1"] == "정제 교과서", f"절 {len(S['secs'])} · 구간 줄 {len(S['nav'])}")
item("T2-2", "구간마다 요지 한 줄 · 설명 · 넘기는 값 · 그림 하나 · 그림 설명", all(c["q"] > 8 and c["say"] > 20 and c["hand"] >= 1 and c["fig"] == 1 and c["cap"] > 20 for c in CH) and len(CH) == 8, f"{sum(1 for c in CH if c['q'] > 8 and c['fig'] == 1)} / 8")
item("T2-3", "읽는 법: 항목 구성 설명 4칸 · 전체 그림(번호 8) · 계산값 흐름도로 가는 줄(글 목록 대신 그림)", S["how"]["cells"] == 4 and S["how"]["fig"] == 1 and S["how"]["pins"] == 8 and S["how"]["chain"] == 0 and S["how"]["toflow"] == 1, f"칸 {S['how']['cells']} · 번호 {S['how']['pins']} · 흐름도로 가는 줄 {S['how']['toflow']}")
item("T3-1", "항목 = 발표자료의 공식 35개(핵심 계산 카드 + 보조 계산 표, 빠짐 · 겹침 없음)", sorted(keys) == sorted(DK) and len(keys) == len(set(keys)) == 35, f"핵심 {ncore} + 보조 {nsub} = {len(keys)} · 발표자료 {len(DK)}")
item("T3-2", "핵심 계산 카드마다 산출값 · 용도 2줄 이상(계산 · 운전) · 식의 요지 · 계산값 · 접어 둔 계산식", sum(c["full"] for c in CH) == ncore and ncore >= 20, f"{sum(c['full'] for c in CH)} / {ncore} · 적용 예 {sum(c['ex'] for c in CH)}개")
item("T3-3", "보조 계산 표의 줄마다 여섯 칸(번호 · 이름 · 산출값 · 용도 · 식의 요지 · 계산값)이 참", sum(c["subfull"] for c in CH) == nsub, f"{sum(c['subfull'] for c in CH)} / {nsub}")
nsp = lambda s: re.sub(r"\s+", "", s)
badv = [k for c in CH for k, v in c["vals"].items() if nsp(v) != nsp(DK[k]["val"])]
bads = [k for c in CH for k, v in c["simp"].items() if nsp(v) != nsp(DK[k]["simp"])]
item("T4-1", "계산값과 식의 요지가 발표자료의 같은 공식과 글자까지 같음(같은 기록에서 만든 값)", not badv and not bads, f"계산값 {len(keys) - len(badv)} / {len(keys)} · 식의 요지 {len(keys) - len(bads)} / {len(keys)}" + (f" · 다름: {badv + bads}" if badv or bads else ""))
# 그림: 말풍선의 식이 식의 요지인지(줄을 나눠 적으므로 띄어쓰기를 빼고 견준다) · 가정 표식은 숨김
coeq = {k: v for c in CH for k, v in c["coeq"].items()}; allsimp = {k: v for c in CH for k, v in c["simp"].items()}
badc = [k for k in keys if nsp(coeq.get(k, "")) != nsp(allsimp[k])]
long_ = [k for k in keys if len(nsp(DK[k]["eq"])) > len(nsp(allsimp[k])) + 12]
item("T4-2", "구간 그림: 말풍선 35개의 식 = 식의 요지(시뮬레이터 계산식이 아님) · 가정 표식은 숨김 · 현장 계기 태그는 남김", not badc and sum(len(c["co"]) for c in CH) == 35 and all(c["amShown"] == 0 and c["tgd"] >= 1 for c in CH),
     f"말풍선 {sum(len(c['co']) for c in CH)} · 식의 요지와 같음 {35 - len(badc)} · 보이는 가정 표식 {sum(c['amShown'] for c in CH)} · 계산식보다 12자 넘게 짧아진 식 {len(long_)}개")
# 숫자: 기록에서 따로 만든 글 조각
_ck = HERE.parent / "점검" / f"점검결과_{tag}.json"
if not _ck.exists(): _ck = HERE / f"점검결과_{tag}.json"
CHK = json.loads(_ck.read_text(encoding="utf-8")); VAL = json.loads((HERE / "값.json").read_text(encoding="utf-8")); P30 = VAL["snap"]["30"]["PR"]; END = CHK["raw"]["합침 배치 끝"]["res"]["end"]
def ab(k):
    nm = [n for n in CHK["raw"] if n.startswith("이상 상황") and f"ab_{k}_0" in CHK["raw"][n]["res"]][0]; r = CHK["raw"][nm]["res"]; return r[f"ab_{k}_0"], r[f"ab_{k}_1"]
a, b = ab("bare"); want = [f"열손실이 {a['Qloss']:.0f} → {b['Qloss']:.0f} W"]
a, b = ab("steam"); want += [f"증발량이 {a['V']:.1f} → {b['V']:.1f} kg/h", f"범람률이 {a['flood'] * 100:.0f} → {b['flood'] * 100:.0f} %"]
a, b = ab("leak"); want += [f"펌프 측 압력이 {a['Ppump']:.2f} → {b['Ppump']:.2f} torr", f"끓는점이 {a['Tbub']:.1f} → {b['Tbub']:.1f} ℃"]
a, b = ab("c1cold"); want += [f"{a['subR']:.2f} → {b['subR']:.2f} kg"]
a, b = ab("rlow"); want += [f"{a['xD']:.2f} → {b['xD']:.2f} mol%"]
a, b = ab("cwlow"); want += [f"처리 가능 열량이 {b['cap1']:.0f} W"]
a, b = ab("pstop"); want += [f"펌프 측 압력이 {a['Ppump']:.2f} → {b['Ppump']:.2f} torr가 되어 비등이 멈춘다"]
want += [f"증발량 {P30['vdot']:.1f} kg/h와 정제기 압력 {P30['Pstill']:.2f} torr", f"환류 {P30['Rkg']:.1f} kg/h와 유출 {P30['Dkg']:.1f} kg/h를 유지하는 개도가 {P30['MVpct']:.1f} %", f"투입 {END['m0']:.0f} kg"]
miss = [w for w in want if w not in plain]
item("T4-3", "글의 숫자가 계산 기록과 같음(이상 상황 기록 · 본류 30 h 값에서 따로 만든 글 조각이 화면에 있음)", not miss, f"{len(want) - len(miss)} / {len(want)}" + (" · 없음: " + ", ".join(miss) if miss else ""))
# 예전 교과서에서 지운 것
gone = ["헥산", "톨루엔", "배우는 과목", "슬라이더", "주전자", "소주", "UNIFAC", "이것만 기억", "확인 문제", "쉽게 말하면", "격자", "화공양론"]
left = [w for w in gone if w in plain]
_old = HERE.parent / "정제_교과서_이전판.html"       # 예전 판은 개발 PC의 정제탱크/에만 둔다(깃 저장소에는 올리지 않는다)
item("T5-1", "예전 교과서의 내용(헥산–톨루엔 예 · 비유 · 배우는 과목 · 확인 문제 · 계산 방법)이 남아 있지 않음", not left,
     f"남은 낱말 {left if left else 0} · 크기 {OUT.stat().st_size / 1e3:.0f} KB" + (f"(예전 판 {_old.stat().st_size / 1e3:.0f} KB는 {_old.name}로 보관)" if _old.exists() else "(예전 판 보관본은 이 폴더에 없음)"))

NFIG = 14
def overlap_run(theme):
    vals, other = drive([["wait", 2500], ["eval", OV]], 1440, theme); n = 0; bad = []; figs = 0
    for d in vals:
        for fid, r in d.get("figs", {}).items():
            figs += 1
            for k in ("overlap", "out", "spill", "box", "cross", "lbox", "ltext"):
                n += len(r[k]); bad += [f"{fid} {k}: {s}" for s in r[k]]
    return n, bad, figs, other
nd_, bad_d, figs_d, oth_d = overlap_run(None); nl_, bad_l, figs_l, oth_l = overlap_run("light")
item("S2", "그림의 글 겹침 · 그림 밖 · 말풍선 넘침 · 화살표 엇갈림 0(어두운 · 밝은 화면, 그림 14: 전체 1 · 흐름도 1 · 구간 8 · 환류비 4)", nd_ == 0 and nl_ == 0 and figs_d == NFIG and figs_l == NFIG, f"어두운 {nd_} · 밝은 {nl_} · 본 그림 {figs_d} + {figs_l}" + (" · " + "; ".join((bad_d + bad_l)[:4]) if nd_ + nl_ else ""))
sc = {}
for w in (390, 768, 1440):
    v, o = drive([["wait", 2000], ["eval", SCROLL]], w); sc[w] = (max(d["sw"] - d["cw"] for d in v if d.get("scroll")), o)
item("S3", "쪽 가로 스크롤 없음(390 · 768 · 1440 너비)", all(x[0] <= 0 for x in sc.values()), " · ".join(f"{w}: 넘침 {x[0]}" for w, x in sc.items()))
nav_a = [["wait", 2000]]
for sid in ("c3", "loop", "c8", "how"): nav_a += [["click", f".tnav [data-to={sid}]"], ["wait", 400], ["eval", NAVQ % (sid, sid)]]
nv, nvo = drive(nav_a, 1440); nv = [d for d in nv if d.get("nav")]
item("T6-1", "구간 줄의 버튼을 누르면 그 절이 구간 줄 바로 아래로 옴(구간 줄은 위에 붙어 있음)", len(nv) == 4 and all(0 <= d["top"] - d["navb"] <= 40 or d["nav"] == "how" for d in nv) and all(d["navb"] <= 120 for d in nv[:3]),
     " · ".join(f"{d['nav']}: 구간 줄 아래 {d['top'] - d['navb']}px" for d in nv))
# ---------------------------------------------------------------- 계산값 흐름도(T7)
FL = S["flow"] or {}; FD = FL.get("data") or {"n": {}, "l": []}; CARD = {c["k"]: c for c in S["cards"]}
bk = [b["k"] for b in FL.get("boxes", [])]; badid = [b["k"] for b in FL.get("boxes", []) if CARD.get(b["k"], {}).get("id") != b["id"]]
ends = {l[0] for l in FD["l"]} | {l[1] for l in FD["l"]}; lone = [k for k in bk if k not in ends]
item("T7-1", "계산값 흐름도: 상자 35 = 공식 35(번호가 구간의 핵심 계산 · 보조 계산 번호와 같음) · 선 = 자료의 경로 수 · 모든 식이 선으로 이어짐 · 구간 이름 8",
     sorted(bk) == sorted(keys) and len(bk) == 35 and not badid and len(FL.get("edges", [])) == len(FD["l"]) and not lone and FL.get("heads") == [f"c{i}" for i in range(1, 9)],
     f"상자 {len(bk)} · 선 {len(FL.get('edges', []))}(늘 보이는 것 {sum(1 for e in FL.get('edges', []) if e[2])}) · 번호 다름 {badid or '없음'} · 외딴 식 {lone or '없음'}")
# 용도의 '계산' 글에 적힌 '식 N' · '구간 N'이 흐름도의 선과 맞는지(흐름도.check_words와 같은 규칙을 화면의 글과 자료로 다시 본다)
byid = {c["id"]: c["k"] for c in S["cards"]}; adj = {k: set() for k in bk}; outs = {k: set() for k in bk}
for a, b, _, _ in FD["l"]: adj[a].add(b); adj[b].add(a); outs[a].add(b)
badw = []
for c in S["cards"]:
    k = c["k"]; sec = c["id"].split("-")[0]
    for m in re.finditer(r"식 (\d+)", c["calc"]):
        tk = byid.get(f"{sec}-{m.group(1)}")
        if tk is None or tk == k or (tk not in adj[k] and not (outs[k] & outs[tk])): badw.append(f"{c['id']} {m.group(0)}")
    for m in re.finditer(r"구간 (\d+)", c["calc"]):
        ks = {q for i, q in byid.items() if i.split("-")[0] == m.group(1)}
        if not (adj[k] & ks): badw.append(f"{c['id']} {m.group(0)}")
item("T7-2", "항목마다 적은 '계산' 용도의 글(식 N · 구간 N)과 흐름도의 선이 같은 내용", not badw and len(S["cards"]) == 35, f"글 {len(S['cards'])}개 · 다름 {badw or '없음'}")
# 상자의 숫자 = 기록(본류 30 h)
P3 = VAL["snap"]["30"]["PR"]; fv = {b["k"]: b["v"] for b in FL.get("boxes", [])}
wantf = {"vboil": [f"증발 {P3['vdot']:.1f} kg/h", f"정제기 {P3['Pstill']:.2f} torr"], "jacket": [f"전달 {P3['Q']:.0f} W"], "bubble": [f"{P3['Tbub']:.1f} ℃"], "comp": [f"입구 {P3['Ptop']:.2f} torr"], "choke": [f"출구 {P3['Pexit']:.2f} torr"],
         "split": [f"환류 {P3['Rkg']:.1f} kg/h", f"유출 {P3['Dkg']:.1f} kg/h"], "pump": [f"{P3['Ppump']:.2f} torr"], "load": [f"{P3['Qc']:.0f} W"], "loss": [f"{P3['Qloss']:.0f} W"], "pi": [f"개도 {P3['MVpct']:.1f} %"]}
missf = [k for k, ws in wantf.items() if not all(w in fv.get(k, "") for w in ws)]
item("T7-3", "흐름도 상자의 계산값이 기록(본류 30 h)과 같음(10개 상자를 기록에서 따로 만들어 대조)", not missf, f"{len(wantf) - len(missf)} / {len(wantf)}" + (f" · 다름: {missf}" if missf else ""))
# 눌러 보기: 상자를 고르면 들어오는 값 · 쓰이는 곳이 자료와 같은 수로 표시되고, 설명 보기가 그 항목으로 간다. 그림이 한 화면에 들어온다
FQ = ("(()=>{const s=document.getElementById('fig-flow'),p=document.getElementById('flow-p');const r=s.getBoundingClientRect(),nb=document.querySelector('.tnav').getBoundingClientRect().bottom;"
      "return JSON.stringify({fq:1,sel:s.classList.contains('sel'),on:[...s.querySelectorAll('.fl-b.on')].map(b=>b.getAttribute('data-k')),nin:s.querySelectorAll('.fl-b.in').length,nout:s.querySelectorAll('.fl-b.out').length,"
      "hit:s.querySelectorAll('.fl-e.hit').length,shown:[...s.querySelectorAll('.fl-e.hit')].filter(e=>getComputedStyle(e).display!=='none').length,lis:[...p.querySelectorAll('.fio > div')].map(d=>d.querySelectorAll('li:not(.none)').length),"
      "top:Math.round(r.top),bottom:Math.round(r.bottom),navb:Math.round(nb),vh:innerHeight,card:(()=>{const c=document.querySelector('.tcard.flash, tr.flash');if(!c)return null;const q=c.getBoundingClientRect();return q.top>=0&&q.bottom<=innerHeight+2})()})})()")
fa = [["wait", 2000], ["click", ".tnav [data-to=flow]"], ["wait", 500], ["eval", FQ], ["click", ".fl-b[data-k=vboil]"], ["wait", 300], ["eval", FQ], ["click", ".fl-b[data-k=mass]"], ["wait", 300], ["eval", FQ],
      ["click", "#flow-p [data-card]"], ["wait", 500], ["eval", FQ], ["click", ".tnav [data-to=flow]"], ["wait", 400], ["click", ".fl-b[data-k=mass]"], ["wait", 300], ["eval", FQ]]
fq, fqo = drive(fa, 1440); fq = [d for d in fq if d.get("fq")]
nin = lambda k: sum(1 for l in FD["l"] if l[1] == k); nout = lambda k: sum(1 for l in FD["l"] if l[0] == k)
ok74 = (len(fq) == 5 and not fq[0]["sel"] and fq[1]["on"] == ["vboil"] and fq[1]["lis"] == [nin("vboil"), nout("vboil")] and fq[1]["hit"] == fq[1]["shown"] == nin("vboil") + nout("vboil")
        and fq[2]["on"] == ["mass"] and fq[2]["lis"] == [nin("mass"), nout("mass")] and nout("mass") == 0 and fq[3]["card"] is True and not fq[4]["sel"])
item("T7-4", "흐름도의 상자를 누르면 들어오는 값 · 쓰이는 곳이 자료와 같은 수로 표시되고(숨겨 둔 보조 입력의 선도 나타남), '이 계산의 설명 보기'가 그 항목으로 가며, 다시 누르면 풀림",
     ok74, " · ".join(f"{d['on'] or '없음'} 들어옴·쓰임 {d['lis']} 선 {d['shown']}" for d in fq[1:3]) if len(fq) >= 3 else "기록 없음")
item("T7-5", "흐름도가 한 화면에 들어옴(1440 × 1000 창에서 구간 줄 아래부터 그림 끝까지가 창 안)", len(fq) >= 1 and fq[0]["bottom"] <= fq[0]["vh"] and fq[0]["top"] >= fq[0]["navb"],
     f"그림 위 {fq[0]['top']} · 아래 {fq[0]['bottom']} · 창 높이 {fq[0]['vh']}" if fq else "기록 없음")
# ---------------------------------------------------------------- 환류비별 계산 결과(T8) · DB 6배치 비교(T9)
RRS = S["rr"] or {}
item("T8-1", "환류비별 계산 결과: 그래프 4(초류 · 본류 환류비별 저비점 불순물과 소요 시간) · DB 환류비 띠 4 · '환류비 판단'과 한계(상대휘발도는 추정 · 고비점 불순물은 계산에 없음 · 컷별 성분 분석 뒤 판단)가 글에 있음",
     RRS.get("figs") == ["fig-rr1", "fig-rr2", "fig-rr3", "fig-rr4"] and RRS.get("bands") == 4 and all(w in RRS.get("tx", "") for w in ("추정", "고비점 불순물", "컷별 성분 분석", "환류비 판단")), f"그래프 {len(RRS.get('figs', []))} · 띠 {RRS.get('bands')} · 점 {RRS.get('pts')}")
DBV = json.loads((HERE / "DB값.json").read_text(encoding="utf-8")); TRL = json.loads((HERE / "시험계산_기록.json").read_text(encoding="utf-8")); DBF = json.loads((HERE / "DB_맞춤_결과.json").read_text(encoding="utf-8"))
tn_ = TRL["runs"].get(f"{DBF['A_use']:.2f}", {}).get("sum"); cx = " ".join(S["cmpx"]["cells"]); rngs = lambda v, d=1: f"{min(v):.{d}f}~{max(v):.{d}f}"
want9 = [rngs(DBV["본류"]["T"]), rngs(DBV["본류"]["Ttop"]), rngs(DBV["초류_h"]), rngs(DBV["본류_h"]), f"{END['Tmain']:.1f}", f"{END['ThMain']:.1f}"] + ([f"{tn_['Tmain']:.1f}", f"{tn_['Tex30']:.1f}"] if tn_ else ["시험 계산 없음"])
miss9 = [w for w in want9 if w not in cx]
item("T9-1", "계산값과 현장값: DB 6배치 · 계산 · 시험 계산 · 차이의 원인 5칸 8줄, 숫자가 DB값.json · 점검 기록 · 시험 계산 기록과 같고 '기본값은 아직 변경하지 않았다'는 글이 있음",
     S["cmp"] == 8 and S["cmpx"]["cols"] == 5 and not miss9 and "기본값은 아직 변경하지 않았다" in S["cmpx"]["tx"], f"{S['cmp']}줄 · 숫자 {len(want9) - len(miss9)} / {len(want9)}" + (f" · 없음: {miss9}" if miss9 else ""))
# ---------------------------------------------------------------- 흐름도의 DB 6배치 기록 줄(T10) · 고른 상자의 설명(T11)
# 판정 기준은 여기에만 둔다: 화면의 상자 · 선 · 설명 칸을 세어 자료(window.FLOW)와 견주고, 글의 숫자는 기록(DB값.json · 시험 계산 기록 · 점검 기록)에서 따로 만들어 찾는다.
DBD = FD.get("db") or {"src": [], "best": {}, "st": {}, "lead": ""}; SRCD = {x["k"]: x for x in DBD["src"]}; ndb = sum(len(x["t"]) for x in DBD["src"])
FQ2 = ("(()=>{const s=document.getElementById('fig-flow'),p=document.getElementById('flow-p');const q=(c,r)=>[...(r||document).querySelectorAll(c)];const vis=e=>getComputedStyle(e).display!=='none';"
       "const fl=q('.fio li:not(.none)',p);"
       "return JSON.stringify({q2:1,sel:s.classList.contains('sel'),on:q('.fl-b.on',s).map(b=>b.getAttribute('data-k')),dbon:q('.fl-dbb.on',s).map(b=>b.getAttribute('data-db')),"
       "dbb:q('.fl-dbb',s).map(b=>b.getAttribute('data-db')),de:q('.fl-de',s).length,dshown:q('.fl-de',s).filter(vis).length,bd:q('.fl-b',s).filter(b=>b.querySelector('.fl-bd')).map(b=>b.getAttribute('data-k')),"
       "dbt:q('.fl-b.dbt',s).map(b=>b.getAttribute('data-k')),pli:q('.fdbt li',p).length,plip:q('.fdbt li',p).filter(l=>l.querySelector('p')&&l.querySelector('p').textContent.trim().length>20&&l.querySelector('.dst')).length,"
       "dts:q('.fdl dt',p).map(e=>e.textContent.trim()),dds:q('.fdl dd',p).map(e=>e.textContent.trim().length),fdb:q('.fdl .fdb p',p).length,lin:fl.length,lip:fl.filter(l=>l.querySelector('p')&&l.querySelector('p').textContent.trim().length>8).length,"
       "sum:q('.fdbs',p).length,rows:q('.fdbl > li',p).length,btn:q('[data-flow]').length,btnk:[...new Set(q('[data-flow]').map(b=>b.getAttribute('data-flow')))].length,"
       "top:Math.round(s.getBoundingClientRect().top),vh:innerHeight})})()")
fb = [["wait", 2000], ["click", ".tnav [data-to=flow]"], ["wait", 500], ["eval", FQ2], ["click", ".fl-dbb[data-db=vt]"], ["wait", 300], ["eval", FQ2], ["click", ".fl-dball"], ["wait", 300], ["eval", FQ2],
      ["click", ".fl-dball"], ["wait", 300], ["eval", FQ2], ["click", ".fl-b[data-k=vboil]"], ["wait", 300], ["eval", FQ2], ["click", ".fl-b[data-k=agit]"], ["wait", 300], ["eval", FQ2],
      ["scroll", ".tcard[data-f=choke] [data-flow]"], ["wait", 300], ["click", ".tcard[data-f=choke] [data-flow]"], ["wait", 600], ["eval", FQ2],
      ["scroll", "#cmp [data-dbgo]"], ["wait", 300], ["click", "#cmp [data-dbgo]"], ["wait", 600], ["eval", FQ2]]
f2, fbo = drive(fb, 1440); f2 = [d for d in f2 if d.get("q2")]
g = lambda i: f2[i] if len(f2) > i else {}
ok101 = (len(f2) == 8 and len(g(0)["dbb"]) == 7 and sorted(g(0)["dbb"]) == sorted(SRCD) and g(0)["de"] == ndb and ndb >= 20 and g(0)["dshown"] == 0 and sorted(g(0)["bd"]) == sorted(DBD["best"]) and g(0)["sum"] == 1 and g(0)["rows"] == 7)
item("T10-1", "흐름도의 DB 6배치 기록 줄: 기록 묶음 상자 7 · 기록 → 식의 선 = 자료의 쓰임 수(고르기 전에는 숨김) · 대조 표시가 붙은 식 = 자료에서 DB와 대조한 식 · 아래 칸에 'DB 6배치 기록이 쓰인 곳' 요약(기록 묶음 7줄)",
     ok101, f"기록 묶음 {len(g(0).get('dbb', []))} · 선 {g(0).get('de')}(자료 {ndb}, 보이는 것 {g(0).get('dshown')}) · 표시가 붙은 식 {len(g(0).get('bd', []))}(자료 {len(DBD['best'])}) · 요약 {g(0).get('rows')}줄" if f2 else "기록 없음")
nvt = len(SRCD.get("vt", {}).get("t", []))
ok102 = (len(f2) == 8 and g(1)["dbon"] == ["vt"] and g(1)["dshown"] == nvt and sorted(g(1)["dbt"]) == sorted(t[0] for t in SRCD["vt"]["t"]) and g(1)["pli"] == g(1)["plip"] == nvt and "쓴 방법" in g(1)["dts"]
         and len(g(2)["dbon"]) == 7 and g(2)["dshown"] == ndb and sorted(g(2)["dbt"]) == sorted(DBD["best"]) and not g(3)["sel"] and g(3)["dshown"] == 0
         and len(g(7)["dbon"]) == 7 and 0 <= g(7)["top"] <= g(7)["vh"])
item("T10-2", "기록 상자를 누르면 그 기록이 쓰인 식이 자료와 같은 수로 표시되고(선 · 테두리 · 설명 칸의 줄마다 대조 결과와 글), '쓰인 곳 모두 보기'는 모든 선과 대조한 식 전부를 표시하며 다시 누르면 풀림. 계산값과 현장값의 'DB 6배치 기록'을 누르면 흐름도가 전체 보기로 열림",
     ok102, f"증발량 · 내부 온도: 선 {g(1).get('dshown')} · 식 {len(g(1).get('dbt', []))} · 줄 {g(1).get('plip')} / {nvt} · 모두 보기: 선 {g(2).get('dshown')} / {ndb} · 식 {len(g(2).get('dbt', []))} / {len(DBD['best'])}" if len(f2) >= 3 else "기록 없음")
DBV2 = json.loads((HERE / "DB값.json").read_text(encoding="utf-8")); TRL2 = json.loads((HERE / "시험계산_기록.json").read_text(encoding="utf-8")); DBF2 = json.loads((HERE / "DB_맞춤_결과.json").read_text(encoding="utf-8"))
tn2 = TRL2["runs"][f"{DBF2['A_use']:.2f}"]["sum"]; tb2 = TRL2["runs"][TRL2["base"]]["sum"]; r2 = lambda v, d=1: f"{min(v):.{d}f}~{max(v):.{d}f}"
dbtx = DBD.get("lead", "") + " " + " ".join(x["what"] + " " + x["how"] + " " + " ".join(t[2] for t in x["t"]) for x in DBD["src"])
want10 = [f"{DBF2['A0']} → {DBF2['A_use']:.2f}", f"{END['Tmain']:.1f} → {tn2['Tmain']:.1f}", f"{END['Tfore']:.1f} → {tn2['Tfore']:.1f}", r2(DBV2["본류"]["T"]), r2(DBV2["초류"]["T"]), r2(DBV2["본류"]["Ttop"]), f"{tn2['Tex30']:.1f} ℃",
          f"{tb2['m2_30']:.4f}", f"{tn2['m2_30']:.4f}", f"{tb2['t90']:.2f} h", r2(DBV2["본류_h"]), r2(DBV2["초류_h"]), f"{DBF2['P100_old']:.3f} → {DBF2['P100_new']:.3f}", f"{END['TjeMain']:.1f} → {tn2['TjMain']:.1f}", r2(DBV2["본류"]["Tbot"]),
          f"{min(k for k in DBV2['FICH072_무게_적분_비'] if k is not None):.2f}~{max(k for k in DBV2['FICH072_무게_적분_비'] if k is not None):.2f}"]
miss10 = [w for w in want10 if w not in dbtx]
item("T10-3", "DB 글의 숫자가 기록과 같음(DB값.json · 시험 계산 기록 · 점검 기록에서 따로 만든 글 조각이 자료에 있음) · '시뮬레이터 기본값은 아직 변경하지 않았다'는 글이 있음",
     not miss10 and "시뮬레이터 기본값은 아직 변경하지 않았" in DBD.get("lead", ""), f"{len(want10) - len(miss10)} / {len(want10)}" + (f" · 없음: {miss10}" if miss10 else ""))
whys = [k for k in bk if len((FD["n"].get(k) or {}).get("why", "")) < 25]; howk = set((FD.get("how") or {}).keys()); wantk = {f"{l[0]}>{l[1]}" for l in FD["l"]}
dts5 = ["필요한 이유", "산출값", "계산값", "계산에서", "운전에서", "DB 6배치"]
ok111 = (not whys and howk == wantk and all(len(v) > 8 for v in (FD.get("how") or {}).values()) and len(f2) == 8
         and g(4)["on"] == ["vboil"] and g(4)["dts"] == dts5 and all(n > 8 for n in g(4)["dds"]) and g(4)["lin"] == g(4)["lip"] == nin("vboil") + nout("vboil") and g(4)["fdb"] == sum(1 for x in DBD["src"] for t in x["t"] if t[0] == "vboil") >= 1
         and g(4)["dshown"] == g(4)["fdb"] and g(5)["on"] == ["agit"] and g(5)["dts"] == dts5 and g(5)["fdb"] == 1 and g(5)["dshown"] == 0)
item("T11-1", "식 상자를 누르면 필요한 이유 · 산출값 · 계산값 · 계산에서 · 운전에서 · DB 6배치 여섯 줄이 나오고, 들어오는 값 · 쓰이는 곳의 줄마다 받는 식에서 쓰는 방법이 적혀 있음(필요한 이유 35 · 쓰는 방법 = 선의 수). DB와 대조한 식은 그 기록의 선도 나타남",
     ok111, f"필요한 이유 {len(bk) - len(whys)} / {len(bk)} · 쓰는 방법 {len(howk & wantk)} / {len(wantk)} · 진공 비등 평형: 줄 {g(4).get('lip')} / {nin('vboil') + nout('vboil')} · DB {g(4).get('fdb')}건" if len(f2) >= 6 else "기록 없음")
item("T11-2", "구간의 항목(핵심 계산 카드 · 보조 계산 줄) 35개마다 '값의 흐름 보기'가 있고, 누르면 흐름도가 화면에 오며 그 식이 골라짐",
     len(f2) == 8 and g(0)["btn"] == 35 and g(0)["btnk"] == 35 and g(6)["on"] == ["choke"] and 0 <= g(6)["top"] <= g(6)["vh"], f"단추 {g(0).get('btn')} · 음속 한계: 고른 식 {g(6).get('on')} · 그림 위 {g(6).get('top')}" if len(f2) >= 7 else "기록 없음")
cons = [s for s in other + oth_d + oth_l + nvo + fqo + fbo + sum((x[1] for x in sc.values()), []) if not s.startswith("console: clean")]
item("S4", "콘솔 오류 0", not cons, "; ".join(cons[:3]) or "없음")
bad_h = [h for h in S["heads"] if re.search(r"(다|요|까|죠)[.?!]?$", h)]
item("S5", "제목(h1 ~ h4)이 명사형", not bad_h, f"제목 {len(S['heads'])}개" + (" · " + ", ".join(bad_h) if bad_h else ""))
okart = ("<title>" in art[:8000] and 'name="claude:viewport-fit-sides"' in art[:8000] and not re.search(r"<!doctype|<html[\s>]|<head[\s>]|<body[\s>]", art, re.I)
         and "@media (prefers-color-scheme: dark)" in art and ':root[data-theme="dark"]' in art and "env(safe-area-inset-left" in art)
item("S6", "아티팩트 조각: 제목 · 옆 여백 표시 · 밝은/어두운 색 묶음, doctype/html/head/body 없음", okart, f"{ART.stat().st_size / 1e3:.0f} KB")

npass = sum(1 for r in R if r["ok"]); nfail = len(R) - npass
lines = [f"# 정제 교과서 점검 결과 — 통과 {npass} · 실패 {nfail}", "", f"- 대상: `{OUT.name}` ({OUT.stat().st_size / 1e3:.0f} KB) · 점검 기록 `{tag}`", "- 기준과 출처: `요구목록_교과서.md`", "", "| 번호 | 항목 | 판정 | 근거 |", "|---|---|---|---|"]
for r in R: lines.append(f"| {r['id']} | {r['name']} | {'통과' if r['ok'] else '**실패**'} | {r['why']} |")
(HERE / "점검결과_교과서.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
(HERE / "점검결과_교과서.json").write_text(json.dumps(dict(tag=tag, npass=npass, nfail=nfail, R=R), ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
print(f"통과 {npass} · 실패 {nfail}")
for r in R:
    if not r["ok"]: print("  실패", r["id"], r["name"], "—", r["why"])
