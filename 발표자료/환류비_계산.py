# -*- coding: utf-8 -*-
"""환류비별 계산 — 시뮬레이터에서 본류 구간의 환류 · 유출 설정만 바꿔 가며 한 배치씩 끝까지 돌린다.

실행:  python 환류비_계산.py [--part main|fore] [--sim 시뮬레이터 파일] [--only 1.5]        (백그라운드 권장: 경우마다 4~15분)
- --part main(기본): 본류 환류 · 유출 설정만 바꾼다(합 10 kg/h로 같게 두어 증발량이 같다). 본류 끝의 유출 감소(정제기에 70 kg 남으면 6 → 5 kg/h)는 넣지 않는다
  (환류비를 구간 내내 같게 두려고 rcpLateD = 본류 유출). 내는 것 환류비_기록.json
- --part fore: 초류 환류 · 유출 설정만 바꾼다(합 7 kg/h. 초류 구간은 스팀 밸브가 하한 개도에 있어 증발량이 약 7 kg/h로 정해진다). 본류는 기본 조건(환류 4, 유출 6 → 5). 내는 것 환류비_기록_초류.json
- 두 경우 모두 저비점 불순물의 상대휘발도(입력칸 'A 휘발도 보정')를 두 값으로 돌린다. 나머지는 CpHf 정제 조건 그대로다(투입 350 kg, 초류 30 kg, 후류 30 kg).
- 읽는 것: 배치 끝 기록(점검_합침.py의 JS_END와 같은 식) · 스팀 사용량.
- 내는 것: 환류비_기록.json — 경우 하나가 끝날 때마다 저장하므로 중간에 끊겨도 이어서 돌릴 수 있다.
- 시뮬레이터의 계산식은 건드리지 않는다. 화면의 입력칸에 값을 넣고 레시피 운전을 돌리는 것뿐이다.
"""
import datetime, io, json, math, os, pathlib, re, subprocess, sys, threading, http.server, time

HERE = pathlib.Path(__file__).resolve().parent
KDIR = HERE.parent / "점검"
sys.path.insert(0, str(KDIR))
arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SIM = pathlib.Path(arg("--sim")) if arg("--sim") else next((HERE.parent / n for n in ("정제_탱크_시뮬레이터.html", "index.html") if (HERE.parent / n).exists()), None)
DRIVE = str(KDIR / "도구" / "drive.mjs") if (KDIR / "도구" / "drive.mjs").exists() else str(pathlib.Path.home() / ".claude" / "skills" / "anatomy" / "scripts" / "drive.mjs")
PART = arg("--part", "main"); assert PART in ("main", "fore")
OUT = HERE / (arg("--out") or ("환류비_기록.json" if PART == "main" else "환류비_기록_초류.json"))      # --out: 여러 창에서 나눠 돌릴 때 따로 받아 두는 파일(끝나면 환류비_합치기.py로 합친다)
VTOT = 10.0 if PART == "main" else 7.0                             # 그 구간의 환류 + 유출 설정(kg/h). 본류 기본 조건은 4 + 6, 초류는 하한 개도에서의 증발량에 맞춘 값
RS = [0.0, 2.0, 4.0, 5.0, 6.0] if PART == "main" else [0.0, 2.0, 4.0, 5.0, 5.8, 6.2]      # 환류 설정(kg/h). 유출 = VTOT − 환류. 본류는 환류비 0 ~ 1.5(DB의 본류 환류비 범위를 덮는다)
ALPHAS = [1.5, 20.0]                                               # 저비점 불순물의 상대휘발도: 1.5 = 지금 입력 기본값(가정), 20 = 사내 검토서의 TDMAHf 증기압에 해당하는 값

def browser_env():
    env = dict(os.environ)
    if env.get("CHROME_PATH"): return env
    la = env.get("LOCALAPPDATA", "")
    for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              os.path.join(la, r"Google\Chrome\Application\chrome.exe") if la else "",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]:
        if c and os.path.exists(c): env["CHROME_PATH"] = c; break
    return env

def serve():
    body = ("<!doctype html><meta charset=utf-8><meta name=viewport content=\"width=device-width\">" + SIM.read_text(encoding="utf-8")).encode("utf-8")
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.send_header("content-type", "text/html;charset=utf-8"); self.send_header("cache-control", "no-store"); self.send_header("content-length", str(len(body))); self.end_headers(); self.wfile.write(body)
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}/x.html"

import 점검_합침 as MG
JS_X = r"""(()=>{const D=window.__dt,P=D.PR,p=D.CUR,H=P.hist||[],st=P.rcpStages||[];const t4=(st.find(x=>x.st===4)||{}).t;
const w=t4!=null?H.filter(r=>r.t>=t4+2*3600&&r.t<=P.t-600):[];const avg=(k)=>w.length?w.reduce((a,r)=>a+(r[k]||0),0)/w.length:null;
return JSON.stringify({steamKg:P.steamKg,Tm:avg('T'),Th:avg('Th'),Rf:avg('Rf'),Pd:avg('Pd'),mv:avg('mv'),xDw:P.xDw,wA:P.wA,aA:parseFloat(document.getElementById('aA').value),
R:parseFloat(document.getElementById('rcpMainR').value),Dm:parseFloat(document.getElementById('rcpMainD').value),Dl:parseFloat(document.getElementById('rcpLateD').value),Rf0:parseFloat(document.getElementById('rcpForeR').value),Df0:parseFloat(document.getElementById('rcpForeD').value),alphaB:p.A&&p.A.alphaB,Nst:p.Nst,ver:((document.querySelector('.ver')||{}).textContent||'').trim()})})()"""

def actions(R, D, a):
    boot = [["wait", 2000], ["until", "!!window.__dt&&!!window.__dt.M&&!!window.__dt.PR", 120000], ["wait", 4000]]
    tag = lambda t, js: ["eval", f"(async()=>{{const r=await ({js});return JSON.stringify({{tag:{json.dumps(t)},v:JSON.parse(r)}})}})()"]
    ids = f"set('rcpMainR',{R});set('rcpMainD',{D});set('rcpLateD',{D});" if PART == "main" else f"set('rcpForeR',{R});set('rcpForeD',{D});"
    setv = ("(()=>{const set=(id,v)=>{const e=document.getElementById(id);e.value=String(v);e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));};"
            f"set('aA',{a});{ids}document.getElementById('btnRestart').click();return JSON.stringify({{ok:1}})}})()")
    h = 420
    return (boot + [tag("set", setv), ["wait", 3500], ["eval", "window.__dt.opSetMode('recipe');1"], ["wait", 1500],
                    ["eval", f"window.__dt.startJump('at',{h});1"], ["until", f"(()=>{{const D=window.__dt,P=D.PR;return !!(P&&!D.TURBO&&(P.t>={h}*3600-120||P.stopped))}})()", 3000000], ["wait", 2500],
                    tag("end", MG.JS_END), tag("x", JS_X)])

def run(R, D, a, url):
    f = HERE / "_workspace"; f.mkdir(exist_ok=True); af = f / f"_환류비_{PART}_{a}_{R}.json"      # 구간 이름을 넣는다: 본류 · 초류를 같이 돌릴 때 같은 이름의 동작 파일을 서로 덮어써 다른 구간의 설정으로 돈 적이 있다(입력 확인 assert가 잡음)
    af.write_text(json.dumps(actions(R, D, a), ensure_ascii=False), encoding="utf-8")
    t0 = time.time()
    p = subprocess.run(["node", DRIVE, url, "--actions", str(af), "--width", "1440", "--height", "1000"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=7200, env=browser_env())
    res = {}
    for line in (p.stdout + p.stderr).splitlines():
        if not line.startswith("eval: "): continue
        try:
            v = json.loads(line[6:])
            if isinstance(v, str): v = json.loads(v)
            if isinstance(v, dict) and "tag" in v: res[v["tag"]] = v["v"]
        except Exception: pass
    if "end" not in res or "x" not in res: raise SystemExit(f"R={R} α={a}: 기록이 빠졌다\n" + (p.stdout + p.stderr)[-1500:])
    e, x = res["end"], res["x"]
    assert e["stopped"], f"R={R} α={a}: 배치가 끝까지 가지 않았다"
    if PART == "main": assert abs(x["aA"] - a) < 1e-9 and abs(x["R"] - R) < 1e-9 and abs(x["Dm"] - D) < 1e-9 and abs(x["Dl"] - D) < 1e-9, ("입력이 들어가지 않았다", x)
    else: assert abs(x["aA"] - a) < 1e-9 and abs(x["Rf0"] - R) < 1e-9 and abs(x["Df0"] - D) < 1e-9 and abs(x["R"] - 4) < 1e-9 and abs(x["Dm"] - 6) < 1e-9, ("입력이 들어가지 않았다", x)
    assert x["alphaB"] is None or abs(x["alphaB"] - a) < 1e-9, x
    st = {s[0]: s[1] for s in e["stages"]}
    wM = e["mainA"] / e["main"] * 100; wF = e["foreA"] / e["fore"] * 100; xs = e["xS"]; wS = xs * e["MWA"] / (xs * e["MWA"] + (1 - xs) * e["MWB"]) * 100
    return dict(part=PART, R=R, D=D, RD=R / D, RDact=(e["Rfore"] / e["Dfore"] if PART == "fore" else x["Rf"] / x["Pd"]), alpha=a, ver=x["ver"], sec=round(time.time() - t0), t_all=e["t"], t_fore=st[4] - st[3], t_main=e["t"] - st[4], t_pre=st[3], feed=e["m0"], fore=e["fore"], main=e["main"], left=e["m"],
                w0=e["wA0"], wF=wF, wM=wM, wS=wS, Rf=x["Rf"], Pd=x["Pd"], Tm=x["Tm"], Th=x["Th"], mv=x["mv"], steamKg=x["steamKg"], Nst=x["Nst"], Dfore=e["Dfore"], Rfore=e["Rfore"], why=e["why"])

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    url = serve(); only = [float(a) for a in arg("--only", "").split(",") if a]
    if arg("--rs"): RS = [float(a) for a in arg("--rs").split(",")]            # --rs: 환류 설정 가운데 일부만(나눠 돌릴 때)
    rec = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else dict(runs=[])
    rec.update(vtot=VTOT, part=PART, note=("본류 환류 + 유출 = 10 kg/h로 두고 환류만 바꿈. rcpLateD = 본류 유출(끝의 유출 감소 없음). 나머지는 CpHf 정제 조건" if PART == "main" else "초류 환류 + 유출 = 7 kg/h로 두고 환류만 바꿈. 본류는 기본 조건. 나머지는 CpHf 정제 조건"))
    done = {(r["alpha"], r["R"]) for r in rec["runs"]}
    for a in ALPHAS:
        if only and a not in only: continue
        for R in RS:
            if (a, R) in done: continue
            r = run(R, VTOT - R, a, url); rec["runs"].append(r); rec["when"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M"); rec["ver"] = r["ver"]
            assert len({q["ver"] for q in rec["runs"]}) == 1, "기록마다 시뮬레이터 판이 다르다 — 환류비_기록.json을 지우고 다시 돌릴 것"
            OUT.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
            print(f"[{PART}] α={a} 환류 {R} · 유출 {VTOT - R:.1f} (환류비 설정 {r['RD']:.2f} · 실제 {r['RDact']:.2f}, {r['sec']} s): 초류 {r['t_fore']:.1f} h(유출 {r['Dfore']:.2f}) · 본류 {r['t_main']:.1f} h · 전체 {r['t_all']:.1f} h · 본류 저비점 {r['wM']:.4f} %(원료 {r['w0']}) · 초류 {r['wF']:.3f} % · 잔류 {r['wS']:.4f} % · 스팀 {r['steamKg']:.0f} kg · 내부 {r['Tm']:.1f} ℃", flush=True)
    print(OUT.name, len(rec["runs"]), "건")
