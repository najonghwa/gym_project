# -*- coding: utf-8 -*-
"""시험 계산 — 시뮬레이터 파일은 그대로 두고, 실행 중에 CpHf 증기압식의 상수 A만 바꿔 넣어 같은 레시피로 한 배치를 돌린다.

실행:  python 시험계산.py 11.87 12.41        (상수 A를 하나 이상. 첫 값이 기준)
       python 시험계산.py 12.43 --add        (앞서 돌린 기록에 상수 하나를 더한다)
- 하는 일: 브라우저에서 시뮬레이터를 열고 → 물질 표(window.__dt.SUBS)의 CpHf 상수 A를 바꾸고 → [CpHf 정제 조건]을 다시 눌러 처음부터 시작 →
           레시피 운전으로 6 h · 30 h에서 계산 상태를 읽고 → 배치 끝까지 돌려 구간 평균을 읽는다.
- 내는 것: 시험계산_기록.json(상수별 기록). DB_맞춤.py와 발표자료가 이 기록을 읽는다.
- 시뮬레이터의 기본값은 바꾸지 않는다. 상수를 정식으로 바꾸는 일은 판을 올릴 때 따로 한다.
- 읽는 식(구간 평균 · 계산 상태)은 점검기가 쓰는 것과 같다: 점검_합침.py의 JS_END, 값_뽑기_동작.json의 계산 상태 읽기.
"""
import datetime, io, json, math, os, pathlib, re, subprocess, sys, threading, http.server, time

HERE = pathlib.Path(__file__).resolve().parent
KDIR = HERE.parent / "점검"
sys.path.insert(0, str(KDIR))
SIM = next((HERE.parent / n for n in ("정제_탱크_시뮬레이터.html", "index.html") if (HERE.parent / n).exists()), None)
DRIVE = str(KDIR / "도구" / "drive.mjs") if (KDIR / "도구" / "drive.mjs").exists() else str(pathlib.Path.home() / ".claude" / "skills" / "anatomy" / "scripts" / "drive.mjs")

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
SNAP = json.loads((HERE / "값_뽑기_동작.json").read_text(encoding="utf-8"))[12][1]      # 계산 상태 읽기(값.json을 만들 때 쓴 것과 같은 식)
JS_HIST = r"""(()=>{const P=window.__dt.PR,H=P.hist||[];const first=(f)=>{const r=H.find(f);return r?r.t/3600:null};
const t90=first(r=>r.T>=90),t40=first(r=>r.T>=40),tb=first(r=>r.T>=r.Tb-0.3&&r.t>120),top70=first(r=>r.Th!=null&&r.Th>=70);
const pre=H.filter(r=>t90!=null&&r.t<=t90*3600);let tjMax=null,tjAt=null;for(const r of pre)if(tjMax==null||r.Tje>tjMax){tjMax=r.Tje;tjAt=r.t/3600;}
const sl=(a,b)=>{const ra=H.find(r=>r.T>=a),rb=H.find(r=>r.T>=b);return ra&&rb&&rb.t>ra.t?(rb.T-ra.T)/((rb.t-ra.t)/60):null};
const r10=H.find(r=>r.t>=600)||{},Tb0=H.find(r=>r.T>=r.Tb-0.3&&r.t>120)||{};
return JSON.stringify({n:H.length,T0:H.length?H[0].T:null,t40,t90,tBoil:tb,Tboil:Tb0.T!=null?Tb0.T:null,top70,tjMax,tjAt,tj10:r10.Tje!=null?r10.Tje:null,slope:sl(Math.max(40,(H[0]||{}).T+2||40),80),mv0:(H.find(r=>r.t>=300)||{}).mv})})()"""

def actions(A):
    boot = [["wait", 2000], ["until", "!!window.__dt&&!!window.__dt.M&&!!window.__dt.PR", 120000], ["wait", 4000]]
    tag = lambda t, js: ["eval", f"(async()=>{{const r=await ({js});return JSON.stringify({{tag:{json.dumps(t)},v:JSON.parse(r)}})}})()"]
    jump = lambda h: [["eval", f"window.__dt.startJump('at',{h});1"],
                      ["until", f"(()=>{{const D=window.__dt,P=D.PR;return !!(P&&!D.TURBO&&(P.t>={h}*3600-120||P.stopped))}})()", 1500000], ["wait", 2500]]
    setA = ("(()=>{const S=window.__dt.SUBS.cphf,a0=S.antoine.A;S.antoine.A=%r;document.getElementById('btnCpHf').click();"
            "return JSON.stringify({a0,a1:S.antoine.A,B:S.antoine.B,ver:((document.querySelector('.ver')||{}).textContent||'').trim()})})()" % float(A))
    chk = "(()=>{const p=window.__dt.CUR;return JSON.stringify({A:p.B.antoine.A,Alight:p.A.antoine.A,aA:parseFloat(document.getElementById('aA').value),P:p.P,H:parseFloat(document.getElementById('H').value)})})()"
    return (boot + [tag("set", setA), ["wait", 4000], ["eval", "window.__dt.opSetMode('recipe');1"], ["wait", 1500], tag("chk", chk)]
            + jump(6) + [tag("s6", SNAP)] + jump(30) + [tag("s30", SNAP)] + jump(90) + [tag("end", MG.JS_END), tag("hist", JS_HIST)])

def run(A, url):
    f = HERE / "_workspace"; f.mkdir(exist_ok=True); af = f / f"_시험계산_{A}.json"
    af.write_text(json.dumps(actions(A), ensure_ascii=False), encoding="utf-8")
    t0 = time.time()
    p = subprocess.run(["node", DRIVE, url, "--actions", str(af), "--width", "1440", "--height", "1000"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5400, env=browser_env())
    res = {}
    for line in (p.stdout + p.stderr).splitlines():
        if not line.startswith("eval: "): continue
        try:
            v = json.loads(line[6:])
            if isinstance(v, str): v = json.loads(v)
            if isinstance(v, dict) and "tag" in v: res[v["tag"]] = v["v"]
        except Exception: pass
    need = ["set", "chk", "s6", "s30", "end", "hist"]
    miss = [k for k in need if k not in res]
    if miss: raise SystemExit(f"A={A}: 기록이 빠졌다 {miss}\n" + (p.stdout + p.stderr)[-1500:])
    assert abs(res["chk"]["A"] - float(A)) < 1e-9, ("상수가 들어가지 않았다", res["chk"])
    assert abs(res["chk"]["Alight"] - (float(A) + math.log10(res["chk"]["aA"]))) < 1e-9, "가벼운 성분의 증기압은 CpHf × 휘발도 보정이어야 한다"
    for k in ("s6", "s30"): res[k].pop("cards", None)
    e = res["end"]; assert e["stopped"], "배치가 끝까지 가지 않았다"
    st = {s[0]: s[1] for s in e["stages"]}; B = res["set"]["B"]
    tex = lambda P: B / (float(A) - math.log10(P)) - 273.15
    s30 = res["s30"]["PR"]; s6 = res["s6"]["PR"]
    res["sum"] = dict(A=float(A), ver=res["set"]["ver"], sec=round(time.time() - t0), Tfore=e["Tfore"], Tmain=e["Tmain"], ThFore=e["ThFore"], ThMain=e["ThMain"], TjFore=e["TjeFore"], TjMain=e["TjeMain"],
                      Rfore=e["Rfore"], Dfore=e["Dfore"], Rmain=e["Rmain"], Dmain=e["Dmain"], T1main=e["T1main"], mvFore=e["mvFore"], mvMain=e["mvMain"],
                      t_boil=st.get(2), t_tr=st[3] - st[2], t_fore=st[4] - st[3], t_main=e["t"] - st[4], t_all=e["t"], feed=e["m0"], fore=e["fore"], main=e["main"], left=e["m"],
                      Pstill30=s30["Pstill"], Ptop30=s30["Ptop"], Pexit30=s30["Pexit"], Pcond30=s30["Pcond"], T30=s30["Tmean"], Th30=s30["Thead"], Tj30=s30["TjEff"], V30=s30["Rkg"] + s30["Dkg"], Wpipe30=s30["vdot"] - s30["backKg"],
                      sub30=s30["subR"], m2_30=s30["m2kg"], Tsat30=s30["Tsat"], Tex30=tex(s30["Pexit"]), Ttop30=tex(s30["Ptop"]), Q30=s30["Q"], T1out30=s30["T1out"], c1_30=s30["c1"],
                      Pstill6=s6["Pstill"], Pexit6=s6["Pexit"], T6=s6["Tmean"], Th6=s6["Thead"], V6=s6["Rkg"] + s6["Dkg"], Tex6=tex(s6["Pexit"]), st6=s6["st"], st30=s30["st"], m2_6=s6["m2kg"],
                      **{k: res["hist"][k] for k in ("T0", "t90", "tBoil", "Tboil", "top70", "tjMax", "tj10", "slope")})
    return res

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    As = [a for a in sys.argv[1:] if re.fullmatch(r"\d+(\.\d+)?", a)]
    if not As: raise SystemExit("상수 A를 하나 이상 준다. 예: python 시험계산.py 11.87 12.43")
    url = sys.argv[sys.argv.index("--url") + 1] if "--url" in sys.argv else serve()
    out = dict(when=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), base=As[0], runs={})
    rec = HERE / "시험계산_기록.json"
    if "--add" in sys.argv and rec.exists():      # 앞서 돌린 기록에 상수를 더한다(기준은 그대로)
        out = json.loads(rec.read_text(encoding="utf-8")); out["when"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M"); As = [a for a in As if a not in out["runs"]]
    for A in As:
        r = run(A, url); out["runs"][A] = r; s = r["sum"]
        print(f"A={A} ({s['ver']}, {s['sec']} s): 초류 내부 {s['Tfore']:.1f} · 탑 {s['ThFore']:.1f} · 본류 내부 {s['Tmain']:.1f} · 탑 {s['ThMain']:.1f} · 자켓 {s['TjMain']:.1f} ℃ · "
              f"30 h 정제기 {s['Pstill30']:.3f} · 출구 {s['Pexit30']:.3f} torr(출구 포화 {s['Tex30']:.1f} ℃) · 초류 {s['t_fore']:.1f} h · 본류 {s['t_main']:.1f} h · 2차 응축기 {s['m2_30']} kg/h", flush=True)
    out["ver"] = out["runs"][out["base"]]["sum"]["ver"]
    assert len({r["sum"]["ver"] for r in out["runs"].values()}) == 1, "기록마다 시뮬레이터 판이 다르다 — --add 없이 다시 돌릴 것"
    (HERE / "시험계산_기록.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print("시험계산_기록.json")
