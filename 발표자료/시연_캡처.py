# -*- coding: utf-8 -*-
"""시연 순서를 시뮬레이터에서 그대로 눌러 보고, 그때의 값 · 단추 자리 · 화면을 기록한다.

실행:  python 시연_캡처.py [--url http://localhost:8770/x.html]
- 발표자료의 '시연 순서'에 적는 숫자와 화면 그림은 모두 이 기록에서 나온다(손으로 옮겨 적지 않는다).
- 누르는 것은 화면의 단추 그대로다(속도 · 도면으로 보기 · 이상 상황 · 환류 밸브). 교반 회전수만 입력 칸에 값을 넣는다.
- 내는 것: 시연_기록.json(판 · 단계별 값 · 걸린 시간 · 단추 자리) · 시연_화면_1~5.webp
  (1은 정제기 가까이 본 두 장[80 rpm · 0 rpm]을 나란히 붙인 것, 2~5는 1440 × 632 화면을 1200 폭으로 줄인 것)
- 창 높이가 낮으면 밸브 줄이 접힌 채 시작하므로, 낮은 창(1366 × 700)을 한 번 더 열어 그 단추 이름과 펴지는지를 함께 기록한다.
- 시뮬레이터 판이 바뀌면 다시 돌린다. 점검_발표자료.py가 기록의 판과 발표자료의 판이 같은지 본다.
"""
import base64, datetime, io, json, pathlib, re, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
def _drive():
    loc = HERE.parent / "점검" / "도구" / "drive.mjs"
    return str(loc) if loc.exists() else str(pathlib.Path.home() / ".claude" / "skills" / "anatomy" / "scripts" / "drive.mjs")
URL = sys.argv[sys.argv.index("--url") + 1] if "--url" in sys.argv else "http://localhost:8770/x.html"
W, H, CROP_H, OUT_W = 1440, 900, 632, 1200
LOW = [1366, 700]               # 낮은 창(노트북 화면에서 흔한 크기)
TANK = [366, 318, 262, 166]      # 정제기 가까이 보기(화면 px). 이름표 '탱크 …'의 자리로 맞는지 아래에서 확인한다
TMP = pathlib.Path(tempfile.mkdtemp(prefix="demo_"))

# 화면에서 읽는 값(계산 상태 PR · 입력 CUR · 밸브 · 관 채움) — 이름은 시뮬레이터의 것 그대로
SNAP = r"""window.__S=function(tag){var d=window.__dt,P=d.PR,C=d.CUR,Z=d.ZH||{},F=(d.FILL||{}).R||{};var c1=null;try{c1=d.c1Load&&d.c1Load()}catch(e){}
var n=function(x,k){return x==null||!isFinite(x)?null:+(+x).toFixed(k==null?3:k)};var hn=document.getElementById('heatNote'),ph=document.getElementById('phase'),sp=document.getElementById('spdEq');
return JSON.stringify({tag:tag,real:n(performance.now()/1000,1),t_h:n(P.t/3600,3),st:P.rcp?P.rcp.st:null,T:n(P.Tmean,1),Tj:n(P.TjEff,1),Thead:n(P.Thead,1),V:n(P.vdot,2),R:n(P.Rkg,2),D:n(P.Dkg,2),
 Pstill:n(P.Pstill,3),Ppump:n(P.Ppump,3),Tbot:n(P.Tbot!=null?P.Tbot:P.T1out,1),Tsat:n(P.Tsat,1),c1f:n(P.c1,3),MV:n((C.jOpen||0)*100,1),m2:n(P.m2kg,2),c1:c1==null?null:n(c1,4),fore:n(P.ves.fore.A+P.ves.fore.B,2),main:n(P.ves.main.A+P.ves.main.B,2),m:n(P.m,1),
 rpm:n(C.N*60,0),Tcw:n(C.Tcw,1),dW:n(Z.dW,1),zmax:n(Z.max,3),tauD:n(Z.tauD,1),VR:!!d.VLV.R,VP:!!d.VLV.P,fillR:{head:n(F.head),tail:n(F.tail),L:n(F.Ltot),held:!!F.held},seal:n(P.sealM,2),
 kind:d.solverKind,note:hn?hn.textContent:'',phase:ph?ph.textContent.replace(/\s+/g,' ').trim():'',spd:sp?sp.textContent:'',btn3d:document.getElementById('btn3d').textContent.trim(),
 pause:document.getElementById('btnPause').textContent.trim(),ab:document.getElementById('abBtn').textContent.replace(/\s+/g,' ').trim()})};
window.__R=function(sel){var e=typeof sel==='string'?document.querySelector(sel):sel;if(!e)return null;var r=e.getBoundingClientRect();return [Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)]};
window.__RS=function(tag,map){var o={};Object.keys(map).forEach(function(k){o[k]=window.__R(map[k])});return JSON.stringify({rects:tag,r:o})};
window.__BT=function(txt){var b=[].filter.call(document.querySelectorAll('button'),function(e){return (e.innerText||'').replace(/\s+/g,' ').trim().indexOf(txt)===0&&e.getBoundingClientRect().width>3})[0];if(!b)throw new Error('단추 없음: '+txt);b.click();return 1};
window.__RPM=function(v){var e=document.getElementById('rpm');e.scrollIntoView({block:'center'});e.value=String(v);e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));return 1};
window.__TK=function(){var e=[].filter.call(document.querySelectorAll('.dcs-tag'),function(x){return (x.textContent||'').trim().indexOf('탱크')===0})[0];return JSON.stringify({tk:window.__R(e)})};
JSON.stringify({ver:(document.querySelector('.ver')||{}).textContent||'',kind:window.__dt.solverKind,lblRpm:document.getElementById('rpm').parentElement.innerText.replace(/\s+/g,' ').trim(),
 rpmTab:(document.getElementById('rpm').closest('.panel')||{getAttribute:function(){return null}}).getAttribute('data-tab'),rpmHead:(function(){var e=document.getElementById('rpm'),p=e.closest('.panel'),h=null;if(p)[].forEach.call(p.querySelectorAll('h3'),function(x){if(x.compareDocumentPosition(e)&4)h=x.textContent.trim()});return h})(),
 railRun:(document.querySelector('.rb[data-tab=run]')||{}).innerText||'',vmin:document.getElementById('valveMin').textContent.trim(),
 vsw:(function(){var r=document.querySelector('button[data-v=R]').getBoundingClientRect();return r.width>3&&r.height>3})()})"""
VMIN = "(function(k){var v=document.getElementById('valveMin'),r=document.querySelector('button[data-v=R]').getBoundingClientRect();return JSON.stringify({low:k,btn:v.textContent.trim(),sw:r.width>3&&r.height>3})})"
snap = lambda tag: ["eval", f"window.__S('{tag}')"]
rects = lambda tag, m: ["eval", f"window.__RS('{tag}',{json.dumps(m, ensure_ascii=False)})"]
shot = lambda n: ["shot", str(TMP / f"shot{n}.png"), "body", 1, [0, 0, W, CROP_H]]
tank = lambda n: ["shot", str(TMP / f"tank{n}.png"), "body", 2.4, TANK]
mark = lambda name: ["eval", f"(window.__M=window.__M||{{}}),window.__M['{name}']=performance.now(),1"]
since = lambda name, a: ["eval", f"JSON.stringify({{since:'{name}',at:'{a}',s:+((performance.now()-window.__M['{a}'])/1000).toFixed(1)}})"]

A = [["until", "!!(window.__dt && window.__dt.PR)", 90000], ["wait", 9000], ["eval", SNAP], snap("s0"),
     # ① 교반과 열 퍼짐 — 교반 회전수 80 → 0 → 80(칸은 운전 탭에 있다. 여기서는 칸에 값을 넣는다)
     ["eval", "window.__TK()"], snap("s1a"), tank("a"), mark("rpm0"), ["eval", "window.__RPM(0)"], ["wait", 12000], snap("s1b"), since("s1b", "rpm0"), tank("b"),
     mark("rpm80"), ["eval", "window.__RPM(80)"], ["wait", 3700], snap("s1c"), since("s1c", "rpm80"),
     # ② 정상 운전 흐름 — [매우 빠르게] 5번 → 초류 회수가 시작되면 [현재]
     ["click", "#spdU2"], ["click", "#spdU2"], ["click", "#spdU2"], ["click", "#spdU2"], ["click", "#spdU2"], mark("fast"), snap("s2a"),
     ["until", "window.__dt.PR.rcp&&window.__dt.PR.rcp.st>=2", 120000], since("st2", "fast"), ["until", "window.__dt.PR.rcp.st>=3", 240000], since("st3", "fast"),
     snap("s2c"), ["click", "#spdCur"], ["wait", 7000], snap("s2b"), rects("r2", {"fast": "#spdU2", "cur": "#spdCur", "phase": "#phase", "spd": "#spdEq"}), shot(2),
     # ③ 도면으로 보기
     ["click", "#btn3d"], ["wait", 3000], snap("s3"), rects("r3", {"btn": "#btn3d"}), shot(3), ["click", "#btn3d"], ["wait", 2500], snap("s3b"),
     # ④ 이상 상황 — 1차 N-Brine 온도 상승을 걸었다가 되돌린다
     snap("s4a"), ["click", "#vAdv"], ["wait", 400], ["click", "#abBtn"], ["wait", 500],
     mark("ab"), ["eval", "window.__BT('1차 N-Brine 온도 상승')"], ["wait", 300], ["eval", "window.__BT('닫기')"], ["wait", 2400], snap("s4b"), since("s4b", "ab"), ["wait", 9000], snap("s4c"), since("s4c", "ab"),
     rects("r4", {"adv": "#vAdv", "ab": "#abBtn"}), shot(4),
     ["click", "#abBtn"], ["wait", 500], mark("undo"), ["eval", "window.__BT('모두 되돌리기')"], ["wait", 300], ["eval", "window.__BT('닫기')"], ["wait", 2400], snap("s4d"), since("s4d", "undo"), ["wait", 7000], snap("s4e"),
     ["click", "#vAdv"], ["wait", 500],
     # ⑤ 밸브 조작 — 환류 밸브를 닫았다가 연다
     snap("s5a"), mark("vclose"), ["click", "button[data-v=R]"], ["wait", 5700], snap("s5b"), since("s5b", "vclose"), rects("r5", {"valve": "button[data-v=R]"}), shot(5),
     mark("vopen"), ["click", "button[data-v=R]"], ["wait", 6500], snap("s5c"), since("s5c", "vopen")]

af = TMP / "actions.json"; af.write_text(json.dumps(A, ensure_ascii=False), encoding="utf-8")
r = subprocess.run(["node", _drive(), URL, "--actions", str(af), "--width", str(W), "--height", str(H), "--scale", "1"], capture_output=True, timeout=900)
txt = (r.stdout or b"").decode("utf-8", "replace") + (r.stderr or b"").decode("utf-8", "replace")
S, RC, TM, head = {}, {}, {}, None
for m in re.finditer(r'^eval: (".*")\s*$', txt, re.M):
    try: v = json.loads(json.loads(m.group(1)))
    except Exception: continue
    if not isinstance(v, dict): continue
    if "tag" in v: S[v["tag"]] = v
    elif "rects" in v: RC[v["rects"]] = v["r"]
    elif "since" in v: TM[v["since"]] = v["s"]
    elif "ver" in v: head = v
    elif "tk" in v: RC["tk"] = v["tk"]
other = [s.strip() for s in re.findall(r"^(?!eval:|shot ).+$", txt, re.M) if s.strip()]
# 낮은 창: 밸브 줄이 접혀 있는지, 단추를 누르면 펴지는지
bf = TMP / "low.json"; bf.write_text(json.dumps([["until", "!!(window.__dt && window.__dt.PR)", 90000], ["wait", 4000], ["eval", VMIN + "('a')"], ["click", "#valveMin"], ["wait", 600], ["eval", VMIN + "('b')"]], ensure_ascii=False), encoding="utf-8")
r2 = subprocess.run(["node", _drive(), URL, "--actions", str(bf), "--width", str(LOW[0]), "--height", str(LOW[1]), "--scale", "1"], capture_output=True, timeout=300)
txt2 = (r2.stdout or b"").decode("utf-8", "replace") + (r2.stderr or b"").decode("utf-8", "replace"); LW = {}
for m in re.finditer(r'^eval: (".*")\s*$', txt2, re.M):
    try: v = json.loads(json.loads(m.group(1)))
    except Exception: continue
    if isinstance(v, dict) and "low" in v: LW[v["low"]] = v
want = ["s0", "s1a", "s1b", "s1c", "s2a", "s2c", "s2b", "s3", "s3b", "s4a", "s4b", "s4c", "s4d", "s4e", "s5a", "s5b", "s5c"]
miss = [k for k in want if k not in S]
if miss or head is None or r.returncode != 0:
    print(txt[-3000:]); raise SystemExit(f"기록 실패: 빠진 시점 {miss} · 끝 코드 {r.returncode}")
assert other == ["console: clean"], other

# 기록이 시연 순서의 주장과 맞는지 여기서 먼저 본다(맞지 않으면 기록을 남기지 않는다)
ck = []
def need(name, ok, why): ck.append(dict(name=name, ok=bool(ok), why=str(why)))
need("밸브 줄: 1440 × 900에서는 펴져 있고, 낮은 창에서는 접힌 채 시작해 단추를 누르면 펴진다", head["vsw"] and head["vmin"] == "접기" and "a" in LW and "b" in LW and not LW["a"]["sw"] and LW["b"]["sw"] and LW["b"]["btn"] == "접기" and len(LW["a"]["btn"]) >= 2,
     f'큰 창 {head["vmin"]} · 낮은 창 {LW.get("a")} → {LW.get("b")}')
need("가벼운 계산(열 퍼짐 구획 계산이 도는 방식)", S["s1a"]["kind"] == "LUMP", S["s1a"]["kind"])
need("교반 회전수 칸은 운전 탭의 '압력 · 교반' 아래", head["rpmTab"] == "run" and head["rpmHead"] == "압력 · 교반" and head["lblRpm"].startswith("교반 회전수") and head["railRun"].strip() == "운전", f'{head["rpmTab"]} · {head["rpmHead"]} · {head["lblRpm"]}')
tk = RC.get("tk") or [0, 0, 0, 0]
need("정제기 가까이 보기 자리(이름표 '탱크'가 그림 안 왼쪽 위)", TANK[0] + 15 < tk[0] < TANK[0] + 70 and TANK[1] + 30 < tk[1] < TANK[1] + 90, f"이름표 {tk} · 자르는 자리 {TANK}")
need("① 액 안 온도 차(평균과의 최대 차)가 교반을 세우면 커진다", S["s1a"]["zmax"] < 0.2 and S["s1b"]["zmax"] > 3, f'{S["s1a"]["zmax"]} → {S["s1b"]["zmax"]} ℃')
need("① 교반을 세우면 벽 쪽 온도 차가 커진다", S["s1b"]["rpm"] == 0 and S["s1b"]["dW"] > S["s1a"]["dW"] + 5 and "교반 정지" in S["s1b"]["note"], f'{S["s1a"]["dW"]} → {S["s1b"]["dW"]} ℃ · {S["s1b"]["note"]}')
need("① 다시 돌리면 돌아온다", S["s1c"]["rpm"] == 80 and abs(S["s1c"]["dW"] - S["s1a"]["dW"]) < 1 and "혼합 시간" in S["s1c"]["note"], f'{S["s1c"]["dW"]} ℃ · {S["s1c"]["note"]}')
need("② [매우 빠르게] 5번 = 실제 1초에 16분", S["s2a"]["spd"] == "실제 1초 = 16분", S["s2a"]["spd"])
need("② 초류 회수까지 30초 안", TM["st3"] < 30 and S["s2b"]["st"] == 3 and "초류 회수 중" in S["s2b"]["phase"], f'{TM["st3"]}초 · {S["s2b"]["phase"][:40]}')
need("② [현재] = 실제 1초에 30초 · 환류와 유출이 흐른다", S["s2b"]["spd"] == "실제 1초 = 30초" and S["s2b"]["R"] > 1 and S["s2b"]["D"] > 1, f'환류 {S["s2b"]["R"]} · 유출 {S["s2b"]["D"]}')
need("③ 도면으로 보기 ↔ 3D로 보기", S["s3"]["btn3d"] == "3D로 보기" and S["s3b"]["btn3d"] == "도면으로 보기", f'{S["s3"]["btn3d"]} / {S["s3b"]["btn3d"]}')
tneed = ["st2", "st3", "s1b", "s1c", "s4b", "s4c", "s4d", "s5b", "s5c"]
need("걸린 시간 기록", all(k in TM for k in tneed) and TM["s4b"] <= 3.0 and TM["s4d"] <= 3.0 and TM["s1c"] <= 4.0 and TM["s5c"] <= 7.0, {k: TM.get(k) for k in tneed})
need("④ 3초 안에 환류 · 유출이 끊기고 증기가 2차 응축기로", S["s4b"]["R"] < 0.5 and S["s4b"]["D"] < 0.5 and S["s4b"]["m2"] > 0.8 * S["s4a"]["V"] and S["s4b"]["Tcw"] == 95, f'환류 {S["s4a"]["R"]} → {S["s4b"]["R"]} · 유출 {S["s4a"]["D"]} → {S["s4b"]["D"]} · 2차 {S["s4b"]["m2"]} kg/h')
need("④ 냉매가 포화 온도보다 뜨거워 1차 응축률 0 · 하부 온도가 포화 온도까지 오른다", S["s4c"]["c1f"] == 0 and S["s4c"]["Tcw"] > S["s4c"]["Tsat"] and abs(S["s4c"]["Tbot"] - S["s4c"]["Tsat"]) < 1.5 and S["s4a"]["c1f"] > 0.99, f'응축률 {S["s4a"]["c1f"]} → {S["s4c"]["c1f"]} · 포화 {S["s4c"]["Tsat"]} ℃ · 하부 {S["s4a"]["Tbot"]} → {S["s4c"]["Tbot"]} ℃')
need("④ 유출이 0인 동안에도 초류 탱크가 는다(2차 응축액이 초류 탱크로)", S["s4c"]["D"] < 0.05 and S["s4c"]["fore"] > S["s4b"]["fore"] + 0.3, f'초류 {S["s4b"]["fore"]} → {S["s4c"]["fore"]} kg · 유출 {S["s4c"]["D"]}')
need("④ 스팀 개도가 오른다", S["s4c"]["MV"] > S["s4a"]["MV"] + 1, f'{S["s4a"]["MV"]} → {S["s4c"]["MV"]} %')
need("④ 되돌리면 3초 안에 환류 · 유출이 돌아온다", S["s4d"]["R"] > 3 and S["s4d"]["D"] > 1 and S["s4d"]["Tcw"] == 50 and S["s4e"]["m2"] < 0.1, f'환류 {S["s4d"]["R"]} · 유출 {S["s4d"]["D"]} · 2차 {S["s4e"]["m2"]}')
fr = S["s5b"]["fillR"]
need("⑤ 환류 밸브를 닫으면 환류 0 · 응축액 전량 유출 · U자 액봉은 남는다", (not S["s5b"]["VR"]) and S["s5b"]["R"] < 0.05 and S["s5b"]["D"] > S["s5a"]["R"] + S["s5a"]["D"] - 0.8 and fr["held"] and 0 < fr["head"] < fr["L"],
     f'환류 {S["s5a"]["R"]} → {S["s5b"]["R"]} · 유출 {S["s5a"]["D"]} → {S["s5b"]["D"]} · 관 속 액 {fr["head"]} / {fr["L"]} m')
need("⑤ 다시 열면 환류가 돌아온다", S["s5c"]["VR"] and S["s5c"]["R"] > 3 and not S["s5c"]["fillR"]["held"], f'환류 {S["s5c"]["R"]} kg/h')
bad = [c for c in ck if not c["ok"]]
for c in ck: print("  통과" if c["ok"] else "  실패", c["name"], "—", c["why"])
if bad: raise SystemExit(f"시연 기록이 순서의 설명과 다르다: 실패 {len(bad)}")

from PIL import Image
sizes = {}
ta, tb = (Image.open(TMP / f"tank{k}.png").convert("RGB") for k in "ab"); tw, th = OUT_W // 2, round(TANK[3] * (OUT_W // 2) / TANK[2])
pair = Image.new("RGB", (OUT_W, th)); pair.paste(ta.resize((tw, th), Image.LANCZOS), (0, 0)); pair.paste(tb.resize((tw, th), Image.LANCZOS), (tw, 0))
pair.save(HERE / "시연_화면_1.webp", "WEBP", quality=82, method=6); sizes[1] = (HERE / "시연_화면_1.webp").stat().st_size
for n in range(2, 6):
    im = Image.open(TMP / f"shot{n}.png").convert("RGB"); assert im.size == (W, CROP_H), im.size
    im = im.resize((OUT_W, round(CROP_H * OUT_W / W)), Image.LANCZOS); out = HERE / f"시연_화면_{n}.webp"; im.save(out, "WEBP", quality=80, method=6); sizes[n] = out.stat().st_size
rec = dict(ver=head["ver"].split("·")[0].strip(), build=head["ver"], when=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), url=URL, view=[W, CROP_H], img=[OUT_W, round(CROP_H * OUT_W / W)], img1=[OUT_W, th],
           kind=S["s1a"]["kind"], lblRpm=head["lblRpm"], rpmHead=head["rpmHead"], win=[W, H], low=dict(wh=LOW, btn=LW["a"]["btn"], btn2=LW["b"]["btn"]), t=TM, s=S, rects=RC, check=ck)
(HERE / "시연_기록.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
print("시연 기록", rec["build"], "· 통과", len(ck), "· 실패 0 · 그림", " ".join(f"{n}: {s // 1000} KB" for n, s in sizes.items()))
