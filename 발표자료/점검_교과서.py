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
out.how={cells:q('#how .how4 > div').length,fig:q('#how figure svg').length,pins:q('#fig-ov .pin').length,chain:q('#how .chain li').length};
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
want_secs = ["how"] + [f"c{i}" for i in range(1, 9)] + ["loop", "cmp", "terms"]
item("T2-1", "구성: 읽는 법 → 구간 8개 → 피드백 루프 → 계산값과 현장값 → 용어, 구간 줄의 버튼이 같은 순서", S["secs"] == want_secs and S["nav"] == want_secs and S["h1"] == "정제 교과서", f"절 {len(S['secs'])} · 구간 줄 {len(S['nav'])}")
item("T2-2", "구간마다 요지 한 줄 · 설명 · 넘기는 값 · 그림 하나 · 그림 설명", all(c["q"] > 8 and c["say"] > 20 and c["hand"] >= 1 and c["fig"] == 1 and c["cap"] > 20 for c in CH) and len(CH) == 8, f"{sum(1 for c in CH if c['q'] > 8 and c['fig'] == 1)} / 8")
item("T2-3", "읽는 법: 항목 구성 설명 4칸 · 전체 그림(번호 8) · 값이 넘어가는 순서 12", S["how"]["cells"] == 4 and S["how"]["fig"] == 1 and S["how"]["pins"] == 8 and S["how"]["chain"] == 12, f"칸 {S['how']['cells']} · 번호 {S['how']['pins']} · 순서 {S['how']['chain']}")
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

def overlap_run(theme):
    vals, other = drive([["wait", 2500], ["eval", OV]], 1440, theme); n = 0; bad = []; figs = 0
    for d in vals:
        for fid, r in d.get("figs", {}).items():
            figs += 1
            for k in ("overlap", "out", "spill", "box", "cross", "lbox", "ltext"):
                n += len(r[k]); bad += [f"{fid} {k}: {s}" for s in r[k]]
    return n, bad, figs, other
nd_, bad_d, figs_d, oth_d = overlap_run(None); nl_, bad_l, figs_l, oth_l = overlap_run("light")
item("S2", "그림의 글 겹침 · 그림 밖 · 말풍선 넘침 · 화살표 엇갈림 0(어두운 · 밝은 화면, 그림 9)", nd_ == 0 and nl_ == 0 and figs_d == 9 and figs_l == 9, f"어두운 {nd_} · 밝은 {nl_} · 본 그림 {figs_d} + {figs_l}" + (" · " + "; ".join((bad_d + bad_l)[:4]) if nd_ + nl_ else ""))
sc = {}
for w in (390, 768, 1440):
    v, o = drive([["wait", 2000], ["eval", SCROLL]], w); sc[w] = (max(d["sw"] - d["cw"] for d in v if d.get("scroll")), o)
item("S3", "쪽 가로 스크롤 없음(390 · 768 · 1440 너비)", all(x[0] <= 0 for x in sc.values()), " · ".join(f"{w}: 넘침 {x[0]}" for w, x in sc.items()))
nav_a = [["wait", 2000]]
for sid in ("c3", "loop", "c8", "how"): nav_a += [["click", f".tnav [data-to={sid}]"], ["wait", 400], ["eval", NAVQ % (sid, sid)]]
nv, nvo = drive(nav_a, 1440); nv = [d for d in nv if d.get("nav")]
item("T6-1", "구간 줄의 버튼을 누르면 그 절이 구간 줄 바로 아래로 옴(구간 줄은 위에 붙어 있음)", len(nv) == 4 and all(0 <= d["top"] - d["navb"] <= 40 or d["nav"] == "how" for d in nv) and all(d["navb"] <= 120 for d in nv[:3]),
     " · ".join(f"{d['nav']}: 구간 줄 아래 {d['top'] - d['navb']}px" for d in nv))
cons = [s for s in other + oth_d + oth_l + nvo + sum((x[1] for x in sc.values()), []) if not s.startswith("console: clean")]
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
