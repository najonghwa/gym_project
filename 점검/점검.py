# -*- coding: utf-8 -*-
"""정제 탱크 시뮬레이터 자동 점검기

요구 목록(요구목록.md)의 자동 검사 항목을 실제 브라우저(헤드리스 크롬)로 돌려 숫자로 판정한다.
만든 쪽(시뮬레이터 코드)과 따로 떨어진 검사 프로그램이다. 시뮬레이터 안의 검사용 고리(window.__dt)만 읽는다.

실행:  python 점검.py [--only 기본,끓기,전환류,...] [--tag 이름] [--url 주소]
       --url을 주지 않으면 이 폴더 위의 시뮬레이터 파일(index.html 또는 정제_탱크_시뮬레이터.html)을 스스로 띄운 로컬 서버로 연다.
필요:  Python 3, Node.js(Claude Code가 쓰는 것), 크롬 또는 엣지(크로미움). 브라우저 경로는 CHROME_PATH로 바꿀 수 있다.
결과:  점검결과_<이름>.md(표), 점검결과_<이름>.json, shots/ 캡처
"""
import json, os, re, subprocess, sys, time, argparse, pathlib, math

HERE = pathlib.Path(__file__).resolve().parent
def _drive():   # 브라우저를 움직이는 도구: 같은 폴더 도구/drive.mjs(사내망용 사본, MIT) → 개발 PC의 anatomy 스킬
    if os.environ.get("DRIVE"): return os.environ["DRIVE"]
    loc = HERE / "도구" / "drive.mjs"
    return str(loc) if loc.exists() else r"C:/Users/large/.claude/skills/anatomy/scripts/drive.mjs"
DRIVE = _drive()
SHOTS = HERE / "shots"; SHOTS.mkdir(exist_ok=True)
SIM_DIR = HERE.parent
SIM_HTML = next((SIM_DIR / n for n in ("정제_탱크_시뮬레이터.html", "index.html") if (SIM_DIR / n).exists()), SIM_DIR / "index.html")

def _browser_env():   # 크롬이 없으면 엣지(같은 크로미움)
    env = dict(os.environ)
    if env.get("CHROME_PATH"): return env
    la = env.get("LOCALAPPDATA", "")
    for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              os.path.join(la, r"Google\Chrome\Application\chrome.exe") if la else "",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]:
        if c and os.path.exists(c): env["CHROME_PATH"] = c; break
    return env

def serve_local():   # 시뮬레이터 파일을 로컬 서버로(아무 경로나 같은 페이지)
    import http.server, threading
    body = ("<!doctype html><meta charset=utf-8><meta name=viewport content=\"width=device-width\">" + SIM_HTML.read_text(encoding="utf-8")).encode("utf-8")
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.send_header("content-type", "text/html;charset=utf-8"); self.send_header("cache-control", "no-store"); self.send_header("content-length", str(len(body))); self.end_headers(); self.wfile.write(body)
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}/x.html"

BOOT = [["wait", 2000], ["until", "!!window.__dt&&!!window.__dt.M&&!!window.__dt.PR", 120000], ["wait", 4000]]
def jump(h):
    return [["eval", f"window.__dt.startJump('at',{h});1"],
            ["until", f"(()=>{{const D=window.__dt,P=D.PR;return !!(P&&!D.TURBO&&P.t>={h}*3600-120)}})()", 900000]]

# ---------- 페이지 안에서 재는 식(JS) ----------
JS_TEXT = r"""(()=>{
  const vis=(el)=>{for(let e=el;e&&e!==document.body;e=e.parentElement){const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden'||e.hidden)return false;}return true;};
  const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let t=[],n;
  while(n=w.nextNode()){const s=n.nodeValue.trim();if(!s)continue;const p=n.parentElement;if(!p||['SCRIPT','STYLE','NOSCRIPT'].includes(p.tagName))continue;if(!vis(p))continue;const r=p.getBoundingClientRect();if(r.width<1||r.height<1)continue;t.push(s);}
  const txt=t.join(' \n ');
  const words={};for(const m of txt.matchAll(/[A-Za-z][A-Za-z]+/g)){words[m[0]]=(words[m[0]]||0)+1;}
  const bad=['받는 곳 없음','받는 중','되감기 재생 중','회수 회수','미래로','점프','완전혼합 중'];const badHit=bad.filter(b=>txt.includes(b));
  const dup=[];for(const one of t)for(const m of one.matchAll(/(^|\s)([가-힣]{2,})\s+\2(?=\s|$)/g))dup.push(m[2]);
  const ver=(document.querySelector('.ver')||{}).textContent||'';
  const spd=['spdD2','spdD15','spdCur','spdU15','spdU2'].map(i=>{const e=document.getElementById(i);return e?e.textContent.trim():null;});
  const dr=document.getElementById('drawer');let rows=0,kinded=0,estNoTip=0;
  if(dr)dr.querySelectorAll('.row > label[for]').forEach(lb=>{const inp=document.getElementById(lb.htmlFor);if(!inp)return;rows++;if(lb.dataset.kind)kinded++;if(lb.dataset.kind==='est'&&!(lb.dataset.tip||'').trim())estNoTip++;});
  const D=window.__dt;const vBefore=!!D.VLV.V;try{D.setValve('V',false);}catch(e){}const vAfter=!!D.VLV.V;const Cb=(document.getElementById('C')||{}).value;const alarmBtn=/알림\s*\d+\s*개/.test(txt);
  return JSON.stringify({vBefore,vAfter,Cb,alarmBtn,words,badHit,dup,ver,spd,rows,kinded,estNoTip,P:(document.getElementById('P')||{}).value,style:D.STYLE,solver:D.solverKind,mat:(D.CUR&&D.CUR.A&&D.CUR.A.name)||null,len:txt.length});
})()"""

# 점 표본: 두 번 재서 움직인 방향과 색을 본다. 허용 = 증기관 꺾여 내려가는 관(7)·1차 응축기(종류 2)·2차/펌프 쪽 길
JS_DOTS = r"""(async()=>{
  const D=window.__dt,M=D.M,q=M.pipe,ys=M.surfY(0,0),out={pale_down:{},yellow:0,other:{},n:0,drops:0,frames:0};
  const snap=()=>{const m=new Map();for(const v of D.VP)if(v._k!=null)m.set(v,[v._x,v._y,v._k]);return m;};
  for(let rep=0;rep<__REP__;rep++){
    const a=snap();await new Promise(r=>setTimeout(r,120));out.frames++;
    for(const v of D.VP){const p=a.get(v);if(!p||v._k===p[2]||v._k==null)continue;out.n++;if(v._drop){out.drops++;continue;}
      const dy=v._y-p[1],c=v._c||[0,0,0];const pale=c[1]>0.7&&c[2]>0.8;const blue=c[2]>0.5&&c[0]<0.3&&c[1]<0.5;
      const rt=v.route||'';const allowed=(v.s===7)||(v.s>=8&&!/colBack|stuck|sealed/.test(rt));
      const reg=v._y<M.topY?'정제기':v._y<q.colBase?'목관':v._y<q.colTop?'컬럼':'위';
      if(pale&&dy<-1e-5&&!allowed){const k=reg+':'+rt+':s'+v.s+(v.cd>=0?':응축중':'');out.pale_down[k]=(out.pale_down[k]||0)+1;}
      if(!pale&&!blue){const k=reg+':'+c.map(x=>x.toFixed(2)).join(',')+(v.cd>=0?':응축중':'');if(v.cd>=0&&v.cd<0.04)continue;out.other[k]=(out.other[k]||0)+1;if(c[0]>0.4&&c[2]<0.5)out.yellow++;}
    }
  }
  return JSON.stringify(out);
})()"""

JS_ONSET = r"""(async()=>{
  const D=window.__dt;const glow=[];const flowEarly=[];let downTank=0,downKinds=null;const t0=D.PR.t;
  const end=t0+__SPAN__;
  while(D.PR.t<end){const P=D.PR,st=D.vaporStats(),F=D.FILL;glow.push(!!(D.FX.colGlow&&D.FX.colGlow.visible));
    if(st.head<8)for(const k of ['RD','R','P','F','M','C']){const f=F[k];if(f&&f.head>0.02&&!(f.full))flowEarly.push(k+'@'+(P.t/60).toFixed(1)+'min head='+st.head.toFixed(2));}
    {const M=D.M,ys=M.surfY(0,0);const k={};for(const p of D.FXP){if(p.y==null||p.vy==null||!(p.vy<0))continue;if(Math.hypot(p.x,p.z||0)>=M.R||p.y<=ys||p.y>=M.topY)continue;k[p.kind]=(k[p.kind]||0)+1;}const n=Object.entries(k).filter(([kk])=>kk!=='drip'&&kk!=='spl').reduce((a,[,v])=>a+v,0);if(n>downTank){downTank=n;downKinds=k;}else if(!downKinds)downKinds=k;}
    await new Promise(r=>setTimeout(r,250));}
  const L=D.STEPLOG.filter(r=>r[0]>=t0&&r[0]<=end);let vmax=0,pmax=0,pmin=1e9;for(const r of L){vmax=Math.max(vmax,r[1]);pmax=Math.max(pmax,r[2]);pmin=Math.min(pmin,r[2]);}
  const win=[];for(let t=t0;t<end;t+=30){const w=L.filter(r=>r[0]>=t&&r[0]<t+30);if(w.length)win.push(+(w.reduce((a,r)=>a+r[1],0)/w.length).toFixed(2));}
  let first=-1;for(let i=0;i<win.length;i++)if(win[i]>2){first=i;break;}
  let zeroAfter=0;if(first>=0)for(let i=first+1;i<win.length;i++)if(win[i]<0.3)zeroAfter++;
  let sw=0;for(let i=1;i<glow.length;i++)if(glow[i]!==glow[i-1])sw++;
  return JSON.stringify({n:L.length,vmax:+vmax.toFixed(1),pmax:+pmax.toFixed(3),pmin:+pmin.toFixed(3),win,zeroAfter,glowSw:sw,glowOn:glow.filter(x=>x).length,flowEarly:flowEarly.slice(0,10),flowEarlyN:flowEarly.length,downTank,downKinds});
})()"""

JS_DCS = r"""(()=>{
  const D=window.__dt,B=D.dcsBox||[];const ov=(a,b)=>Math.max(0,Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x))*Math.max(0,Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y));
  const pairs=[];for(let i=0;i<B.length;i++)for(let j=i+1;j<B.length;j++){const o=ov(B[i],B[j]);if(o>1)pairs.push(B[i].n+' / '+B[j].n+' '+o.toFixed(0)+'px²');}
  const pipe=B.filter(b=>b.hits&&b.hits.length).map(b=>b.n+': '+b.hits.join('; '));const touch=B.filter(b=>!(b.hits&&b.hits.length)&&b.cost>=60).map(b=>b.n+':'+Math.round(b.cost));
  const far=B.filter(b=>{const cx=Math.max(b.x,Math.min(b.ax,b.x+b.w)),cy=Math.max(b.y,Math.min(b.ay,b.y+b.h));return Math.hypot(cx-b.ax,cy-b.ay)>60;}).map(b=>b.n);
  const dist=B.find(b=>b.n==='FI 유출');const distRight=dist?dist.x>=dist.ax-1:null;
  const gaps=[];document.querySelectorAll('.dcs-tag').forEach(el=>{if(el.offsetParent===null)return;const i=el.children[0],b=el.children[1];if(!i||!b||!b.textContent.trim())return;const g=b.getBoundingClientRect().left-i.getBoundingClientRect().right;gaps.push([el.dataset.n,+g.toFixed(1)]);});
  const bigGap=gaps.filter(g=>g[1]>6);
  const hb=B.find(b=>/TIC-H071D/.test(b.n));
  return JSON.stringify({n:B.length,pairs,pipe,touch,far,distRight,bigGap,hbName:hb?(document.querySelector('.dcs-tag[data-n="'+hb.n+'"]')||{children:[{textContent:'?'}]}).children[0].textContent:null,boxes:B.map(b=>[b.n,Math.round(b.x),Math.round(b.y)])});
})()"""

JS_STATE = r"""(()=>{const D=window.__dt,P=D.PR,s=D.vaporStats();const kinds={};for(const p of D.FXP)kinds[p.kind]=(kinds[p.kind]||0)+1;
  return JSON.stringify({t:+(P.t/3600).toFixed(3),vdot:+P.vdot.toFixed(1),P:+P.Pstill.toFixed(3),flood:+(P.flood||0).toFixed(2),R:+(P.Rkg||0).toFixed(1),D:+(P.Dkg||0).toFixed(1),hC1:+(P.hC1||0).toFixed(3),n2:P.fr?+(((P.fr.n2||0)+(P.fr.lost||0))*100).toFixed(2):null,sec:s.sec,down:s.down,cw:Object.keys(kinds).filter(k=>/^cw/.test(k)).reduce((a,k)=>a+kinds[k],0),kinds});})()"""


# 수동 스팀 70 % 끓기 시작(부모 세션 요청 v114): 끓기 시작 뒤 (계산 끓는점 − 액 온도) 최대, 30초 평균 증발 변동 — 빨리 감기·실시간
SET_MANUAL = "(()=>{const D=window.__dt;D.opSetMode(true);D.OP.rfic.sv=4;return 1})()"
JS_TB_HIST = r"""(()=>{const H=window.__dt.PR.hist.filter(h=>h.t>=0.9*3600&&h.t<=1.4*3600);let on=-1;for(let i=0;i<H.length;i++)if(H[i].T>=H[i].Tb-0.3){on=i;break;}let mx=0,at=null;if(on>=0)for(let i=on;i<H.length;i++){const d=H[i].Tb-H[i].T;if(d>mx){mx=d;at=H[i].t/3600;}}return JSON.stringify({n:H.length,onset:on>=0?+(H[on].t/3600).toFixed(3):null,mx:+mx.toFixed(2),at,T:H.length?[+H[0].T.toFixed(1),+H[H.length-1].T.toFixed(1)]:null})})()"""
JS_TB_LIVE = r"""(async()=>{const D=window.__dt,t0=D.PR.t;D.STEPLOG.length=0;while(D.PR.t<t0+__SPAN__)await new Promise(r=>setTimeout(r,500));const L=D.STEPLOG.slice();let on=-1;for(let i=0;i<L.length;i++)if(L[i][4]>=L[i][5]-0.3){on=i;break;}let mx=0;if(on>=0)for(let i=on;i<L.length;i++)mx=Math.max(mx,L[i][5]-L[i][4]);const win=[];for(let t=t0;t<t0+__SPAN__;t+=30){const w=L.filter(r=>r[0]>=t&&r[0]<t+30);if(w.length)win.push(+(w.reduce((a,r)=>a+r[1],0)/w.length).toFixed(2));}let drop=0,first=-1;for(let i=0;i<win.length;i++)if(win[i]>2){first=i;break;}if(first>=0)for(let i=first+1;i<win.length;i++)if(win[i]<0.5*win[i-1])drop++;return JSON.stringify({n:L.length,onset:on>=0?+(L[on][0]/3600).toFixed(3):null,mx:+mx.toFixed(2),win,drop,T:[+L[0][4].toFixed(1),+L[L.length-1][4].toFixed(1)]})})()"""


# v115: 끓기 시작 순서·점 수(흰 점이 응축해 파란 점이 된다), 지워지는 증기 점, 액막 높이, 2차 응축기 넘친 액
JS_ORDER = r"""(async()=>{const D=window.__dt,q=D.M.pipe;let tV=null,tL=null,dripMax=0,ratioMax=0,filmMax=0,lost0=D.vaporStats().lost,n=0;const t0=D.PR.t;
  while(D.PR.t<t0+__SPAN__){const s=D.vaporStats();let vN=0,dN=0;for(const v of D.VP){if(v._y==null||v.liq||v._drop)continue;if(v._y>D.M.topY&&v._y<q.colBase)vN++;}for(const p of D.FXP)if(p.kind==='drip'&&Math.abs(p.x-q.xN)<q.rCol*1.2)dN++;
    const tm=D.PR.t/60;if(vN>0&&tV==null)tV=tm;if(s.nNeckLiq>0&&tL==null)tL=tm;dripMax=Math.max(dripMax,dN);if(vN>=3)ratioMax=Math.max(ratioMax,s.nNeckLiq/vN);if(!(D.FILL.RD&&D.FILL.RD.full))filmMax=Math.max(filmMax,s.filmH);n++;await new Promise(r=>setTimeout(r,250));}
  return JSON.stringify({n,tV,tL,dripMax,ratio:+ratioMax.toFixed(2),filmMax,lost:D.vaporStats().lost-lost0})})()"""
JS_OV = r"""(()=>{const D=window.__dt,P=D.PR,s=D.vaporStats();return JSON.stringify({ovKg:+(P.ovKg||0).toFixed(1),ov2:s.ov2,Tbot:P.Tbot,T1out:P.T1out,Tcw:D.CUR.Tcw})})()"""


# 재검토(v116): 점 개수 보존, 2차 응축기 거짓 흐름, 막힘 표시, 증기관 색칠, 용기 간격·크기, 배치 시트, 카메라, 밸브 토글 때 관 채움, 환류 관 6 mm 고임
JS_FLUX = r"""(async()=>{const D=window.__dt;const prev=new Map();const c={t01:0,t12:0,t45:0,t78:0};const b0=D.PR.fr?D.PR.fr.back||0:0;const T0=performance.now();
  while(performance.now()-T0<9000){for(const v of D.VP){if(v.liq||v.cd>=0){prev.delete(v);continue;}const p=prev.get(v);if(p!=null&&v.s!==p){if(p===0&&v.s>=1)c.t01++;if(p<=1&&v.s>=2)c.t12++;if(p<=4&&v.s>=5)c.t45++;if(p<=7&&v.s>=8)c.t78++;}prev.set(v,v.s);}await new Promise(r=>requestAnimationFrame(()=>r()));}
  const b1=D.PR.fr?D.PR.fr.back||0:0;return JSON.stringify({...c,back:+((b0+b1)/2).toFixed(3),top:+(c.t12?c.t45/c.t12:0).toFixed(3),cond:+(c.t45?c.t78/c.t45:0).toFixed(3)})})()"""
JS_MISC = r"""(()=>{const D=window.__dt,P=D.PR,F=D.FILL;const fr=P.fr||{};const n2kg=((fr.n2||0)+(fr.lost||0))*P.vdot;
  const frac=(k)=>F[k]&&F[k].Ltot?+(F[k].head/F[k].Ltot).toFixed(3):0;
  const chipsBlk=[...document.querySelectorAll('.chip')].filter(e=>e.offsetParent!==null&&/막힘/.test(e.textContent)).length;
  let hot=0,nm=0;const PI=D.PIPES;for(const o of (PI.V||[])){const m=o.material;if(!m||!m.color||!o.visible)continue;nm++;const h={};m.color.getHSL(h);if(h.s>0.45&&(h.h<0.17||h.h>0.95))hot++;}
  return JSON.stringify({n2kg:+n2kg.toFixed(2),ovKg:+(P.ovKg||0).toFixed(2),T2:frac('T2'),L2:frac('L2'),chipsBlk,vMesh:nm,vHot:hot})})()"""
JS_GEOM = r"""(()=>{const D=window.__dt,M=D.M,q=M.pipe,P=D.PR;const R=M.R;const g1=(q.xMn-q.rRM)-R,g2=(q.xF-q.rRF)-(q.xMn+q.rRM);const Vm=Math.PI*q.rRM*q.rRM*(q.HrM+4/3*(q.hdM||0)),Vf=Math.PI*q.rRF*q.rRF*(q.HrF+4/3*(q.hdF||0)),Vchg=(P.m0||350)/((P.mix&&P.mix.rho)||1000);
  const bs=document.getElementById('batchSheet');const btn=bs?[...bs.querySelectorAll('button')].some(b=>/스타트/.test(b.textContent)):false;
  return JSON.stringify({g1:+g1.toFixed(3),g2:+g2.toFixed(3),ratio:+(g1/g2).toFixed(2),Vm:+Vm.toFixed(3),Vf:+Vf.toFixed(3),Vchg:+Vchg.toFixed(3),x2o:+q.x2o.toFixed(3),xF:+q.xF.toFixed(3),batch:!!bs,fore:!!document.getElementById('rcpForeKg'),main:!!document.getElementById('rcpMainKg'),btn,cam:D.CAM||null})})()"""
JS_RTOGGLE = r"""(async()=>{const D=window.__dt,F=D.FILL;const smp=[];const rec=(tag)=>{const f=F.R;smp.push([tag,f?+(f.head/f.Ltot).toFixed(3):null,f?+(f.tail/f.Ltot).toFixed(3):null,+(D.PR.Rkg||0).toFixed(2)]);};
  const cam0=D.CAM?D.CAM.dist:null;D.setValve('R',false);for(let i=0;i<60;i++){rec('닫음');await new Promise(r=>setTimeout(r,100));}const camC=D.CAM?D.CAM.dist:null;
  D.setValve('R',true);for(let i=0;i<60;i++){rec('엶');await new Promise(r=>setTimeout(r,100));}const cam1=D.CAM?D.CAM.dist:null;
  let jump=0;for(let i=1;i<smp.length;i++){if(smp[i][0]!==smp[i-1][0])continue;if(smp[i-1][2]>=0.9&&smp[i][1]===0&&smp[i][2]===0)continue;const dh=Math.abs((smp[i][1]||0)-(smp[i-1][1]||0)),dt=Math.abs((smp[i][2]||0)-(smp[i-1][2]||0));jump=Math.max(jump,dh,dt);}
  const closedEnd=smp.filter(x=>x[0]==='닫음').slice(-1)[0],openEnd=smp.slice(-1)[0];return JSON.stringify({jump:+jump.toFixed(3),closedEnd,openEnd,cam:[cam0,camC,cam1]})})()"""
JS_POOL = r"""(()=>{const D=window.__dt,P=D.PR;return JSON.stringify({hC1:+(P.hC1||0).toFixed(4),c1h:D.C1H!=null?+D.C1H.toFixed(4):null,Tbot:P.Tbot!=null?+P.Tbot.toFixed(2):null,T1out:P.T1out!=null?+P.T1out.toFixed(2):null,n2:+((((P.fr&&P.fr.n2)||0)+((P.fr&&P.fr.lost)||0))*P.vdot).toFixed(2),ov:+(P.ovKg||0).toFixed(2),R:+(P.Rkg||0).toFixed(1),WR:+(P.WR||0).toFixed(1),t:+(P.t/3600).toFixed(3),DR:document.getElementById('DpipeR').value})})()"""
SET_DR = lambda v: ["eval", "(()=>{const e=document.getElementById('DpipeR');e.value='" + v + "';e.dispatchEvent(new Event('change',{bubbles:true}));return e.value})()"]

def scen(name, actions, width=1440, height=1000, theme=None):
    return {"name": name, "actions": actions, "width": width, "height": height, "theme": theme}

def tag(t, js):  # eval 결과에 이름을 붙인다
    return ["eval", f"(async()=>{{const r=await ({js});return JSON.stringify({{tag:{json.dumps(t)},v:JSON.parse(r)}})}})()"]

def build_scenarios():
    S = []
    S.append(scen("기본", BOOT + [tag("text", JS_TEXT), tag("geom", JS_GEOM), ["shot", str(SHOTS / "기본.png")]]))
    onset = BOOT + [["eval", "window.__dt.opSetMode('free');1"], ["wait", 1500]] + jump(1.1) + [
        tag("onset", JS_ONSET.replace("__SPAN__", "720")), tag("dots_onset", JS_DOTS.replace("__REP__", "12")),
        ["shot", str(SHOTS / "끓기시작_컬럼.png"), "#stage", 2, [250, 60, 260, 480]], tag("state_onset", JS_STATE)]
    S.append(scen("끓기 시작", onset))
    for (w, h) in [(1440, 1000), (1366, 768), (1920, 1080)]:
        a = BOOT + [["eval", "window.__dt.opSetMode('free');1"], ["wait", 1500]] + jump(2.6) + [["wait", 4000], ["eval", "window.__dt.setValve('P',true);1"], ["wait", 5000],
            tag("dcs", JS_DCS), ["wait", 5000], tag("dcs2", JS_DCS), tag("dots_reflux", JS_DOTS.replace("__REP__", "10")), tag("state_reflux", JS_STATE), tag("flux", JS_FLUX), tag("misc", JS_MISC), tag("rtoggle", JS_RTOGGLE),
            ["shot", str(SHOTS / f"전환류_{w}x{h}.png")]]
        S.append(scen(f"전환류 {w}×{h}", a, w, h))
    light = BOOT + [["eval", "window.__dt.opSetMode('free');1"], ["wait", 1500]] + jump(2.3) + [["wait", 5000], tag("dots_light", JS_DOTS.replace("__REP__", "8")), ["shot", str(SHOTS / "밝은화면.png")]]
    S.append(scen("밝은 화면", light, theme="light"))
    hot = BOOT + [["eval", "window.__dt.opSetMode('free');1"], ["wait", 1500],
        ["eval", "(()=>{document.getElementById('Psteam').value='';const j=document.getElementById('Tj');j.value='160';j.dispatchEvent(new Event('change',{bubbles:true}));return 1})()"], ["wait", 3000],
        ["eval", "(()=>{const j=document.getElementById('jOpen');j.value='100';j.dispatchEvent(new Event('input',{bubbles:true}));j.dispatchEvent(new Event('change',{bubbles:true}));return 1})()"], ["wait", 1500]] + jump(1.5) + [
        ["wait", 5000], tag("state_hot", JS_STATE), tag("dots_hot", JS_DOTS.replace("__REP__", "8")), ["shot", str(SHOTS / "스팀과다.png")]]
    S.append(scen("스팀 과다", hot))
    S.append(scen("수동 끓기 순서", BOOT + [["eval", SET_MANUAL], ["wait", 1500]] + jump(1.03) + [tag("order", JS_ORDER.replace("__SPAN__", "540")), ["shot", str(SHOTS / "수동끓기_컬럼.png"), "#stage", 2, [250, 60, 260, 480]]]))
    S.append(scen("1차 응축기 넘침", BOOT + [["eval", "window.__dt.opSetMode('free');1"], ["wait", 1500]] + jump(2.3) + [["wait", 3000], ["eval", "window.__dt.setValve('R',false);window.__dt.setValve('P',false);1"], ["until", "(window.__dt.PR.ovKg||0)>5", 240000], ["wait", 6000], tag("ov", JS_OV), ["shot", str(SHOTS / "넘침_2차응축기.png"), "#stage", 2, [500, 40, 300, 260]]]))
    S.append(scen("환류 관 2 mm 고임", BOOT + [["eval", "window.__dt.opSetMode('free');1"], ["wait", 1500]] + jump(2.3) + [["wait", 3000], tag("pool0", JS_POOL), SET_DR("2"), ["until", "(window.__dt.PR.hC1||0)>0.01", 240000], ["wait", 20000], tag("pool6", JS_POOL), ["shot", str(SHOTS / "환류관2mm_응축기.png"), "#stage", 2, [380, 30, 260, 260]], SET_DR("15.8"), ["wait", 40000], tag("poolBack", JS_POOL)]))
    S.append(scen("수동 끓기 빨리 감기", BOOT + [["eval", SET_MANUAL], ["wait", 1500]] + jump(1.4) + [tag("tb_jump", JS_TB_HIST)]))
    S.append(scen("수동 끓기 실시간 ×120", BOOT + [["eval", SET_MANUAL], ["wait", 1500]] + jump(1.0) + [["eval", "(()=>{const e=document.getElementById('accel');e.value='120';e.dispatchEvent(new Event('change',{bubbles:true}));return e.value})()"], tag("tb_live", JS_TB_LIVE.replace("__SPAN__", "900"))]))
    return S

def run(sc, url):
    f = HERE / ("_act_" + re.sub(r"\W", "_", sc["name"]) + ".json")
    f.write_text(json.dumps(sc["actions"], ensure_ascii=False), encoding="utf-8")
    cmd = ["node", DRIVE, url, "--actions", str(f), "--width", str(sc["width"]), "--height", str(sc["height"])]
    if sc["theme"]: cmd += ["--theme", sc["theme"]]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600, env=_browser_env())
    res, console = {}, []
    for line in (p.stdout + p.stderr).splitlines():
        if line.startswith("eval: "):
            try:
                v = json.loads(line[6:])
                if isinstance(v, str): v = json.loads(v)
                if isinstance(v, dict) and "tag" in v: res[v["tag"]] = v["v"]
            except Exception: pass
        elif line.startswith("console") or "error" in line.lower(): console.append(line[:300])
    return {"res": res, "console": console, "sec": round(time.time() - t0), "code": p.returncode}

# ---------- 판정 ----------
ALLOW = set("""kg h mmHg torr rpm mm kW W bar barg kPa Pa wt mol min s m K CpHf TDMAHf Cp Hf CpH HfCl DMA FIC TIC FI PI TI WI ZI PCV FCV CV TT FT LT PT
H T P F M R D L A B C S V J U N Q x y z D2 RD T2 L2 EQV GPU CPU DCS MSDS HMI VDI CFD PID ID OD JIS SUS STS NPS HTML Antoine Raoult NRTL Wilson Watson
Fenske Underwood Gilliland Ergun Darcy Nusselt Prandtl Reynolds Re Pr Nu Ma Fr Kn Tate Nagata Souders Brown Chapman Enskog Harkins TTL v n ms fps
cP cp CP UA LMTD NTU dP dT ON OFF OK Kp Ti""".split())   # Kp·Ti = PI 조절 기호(식의 문자처럼 씀)
def judge(out):
    R = []
    def add(id_, name, ok, val, crit):
        R.append({"id": id_, "name": name, "ok": ok, "val": val, "crit": crit})
    g = lambda s, t: (out.get(s) or {}).get("res", {}).get(t)
    t = g("기본", "text")
    if t:
        unk = {w: c for w, c in t["words"].items() if w not in ALLOW and not re.fullmatch(r"[A-Z]{1,3}\d*", w)}
        add("A1", "화면 글 한국어(허용 목록 밖 영어 낱말)", len(unk) == 0, ", ".join(f"{k}×{v}" for k, v in sorted(unk.items(), key=lambda x: -x[1])[:15]) or "0개", "0개")
        add("A2", "어색한 문구·금지어", not t["badHit"] and not t["dup"], (t["badHit"] + t["dup"]) or "0건", "0건")
        add("G3", "'점프'·'미래로' 문구", not any(b in ("점프", "미래로") for b in t["badHit"]), "없음" if not any(b in ("점프", "미래로") for b in t["badHit"]) else "있음", "0건")
        add("C25", "판 번호 표시", bool(re.match(r"v\d{3}", t["ver"])), t["ver"], "vNNN · 날짜")
        add("G2", "속도 단추 5개, 가운데 '현재'", len([x for x in t["spd"] if x is not None]) == 5 and (t["spd"][2] or "").startswith("현재"), " | ".join(x or "-" for x in t["spd"]), "5개·가운데 현재")
        add("B3", "입력칸 구분 표시(운전·도면·가정…)", t["rows"] > 0 and t["kinded"] == t["rows"] and t["estNoTip"] == 0, f"{t['kinded']}/{t['rows']}칸, 이유 없는 가정 {t['estNoTip']}", "100 %, 0")
        add("G1", "첫 화면 0.1 torr", t["P"] == "0.1", f"P={t['P']}", "0.1")
        add("C31", "첫 화면 3D(HMI)", t["style"] == "hmi", t["style"], "hmi")
        add("E14", "증기 밸브 없음(닫기 조작 무시)", t.get("vAfter") is True, f"닫기 전 {t.get('vBefore')} → 뒤 {t.get('vAfter')}", "열림 유지")
        add("E15", "교반기 바닥 간격 기본 150 mm", str(t.get("Cb")) == "150", t.get("Cb"), "150")
        add("C3", "'알림 n개' 단추 없음", t.get("alarmBtn") is False, "없음" if not t.get("alarmBtn") else "있음", "없음")
    o = g("끓기 시작", "onset")
    if o:
        add("E22", "끓기 시작: 30초 평균 증발이 다시 0으로 꺼지는 창", o["zeroAfter"] == 0, f"{o['zeroAfter']}개 · 30초 평균 {o['win'][:14]}", "0개")
        add("E23", "끓기 시작: 한 걸음 순간 증발 최대", o["vmax"] <= 300, f"{o['vmax']} kg/h", "≤ 300 kg/h(전 3,800)")
        add("E24", "끓기 시작: 정제기 압력 튐(최대/최소)", o["pmax"] <= 3 * o["pmin"], f"{o['pmin']} ~ {o['pmax']} mmHg", "최대 ≤ 3 × 최소")
        add("D21", "끓기 시작: 범람 테두리 깜박임", o["glowSw"] <= 1, f"켜짐↔꺼짐 {o['glowSw']}번", "≤ 1번")
        add("D1", "증기가 응축기 닿기 전 액 흐름", o["flowEarlyN"] == 0, (o["flowEarly"] or "0건"), "0건")
        add("D5", "정제기 빈 공간에서 아래로 가는 점(목관 낙하 액 방울 제외)", o["downTank"] == 0, f"{o['downTank']}개 · 종류별 {o.get('downKinds')}", "0개")
    st = g("끓기 시작", "state_onset")
    if st:
        add("D3", "끓기 시작: 목관에 증기 점", st["sec"]["neck"]["n"] > 0, f"목관 {st['sec']['neck']['n']}개, 증발 {st['vdot']} kg/h", "> 0")
    for sname, tg in [("끓기 시작", "dots_onset"), ("전환류 1440×1000", "dots_reflux"), ("밝은 화면", "dots_light"), ("스팀 과다", "dots_hot")]:
        d = g(sname, tg)
        if d:
            n_pd = sum(d["pale_down"].values())
            add("D4", f"아래로 가는 하늘색(증기 색) 점 — {sname}", n_pd == 0, (json.dumps(d["pale_down"], ensure_ascii=False) if n_pd else "0개") + f" (본 점 {d['n']}, 방울 {d['drops']})", "0개(증기관 꺾인 관·응축기 안 제외)")
            add("D8", f"노랑·초록 계열 점 — {sname}", d["yellow"] == 0, d["yellow"] if d["yellow"] == 0 else json.dumps(d["other"], ensure_ascii=False)[:200], "0개")
    for (w, h) in [(1440, 1000), (1366, 768), (1920, 1080)]:
        sn = f"전환류 {w}×{h}"; d = g(sn, "dcs"); d2 = g(sn, "dcs2")
        if d:
            add("C1", f"값 상자끼리 겹침 — {w}×{h}", not d["pairs"], d["pairs"] or "0쌍", "0쌍")
            add("C1", f"값 상자가 배관에 걸림 — {w}×{h}", not d["pipe"], d["pipe"] or "0개", "0개")
            add("C1", f"값 상자가 설비 몸통·밸브 테두리 상자와 겹침(참고) — {w}×{h}", None, d.get("touch") or "0개", "참고(설비 외곽 직사각형 기준이라 실제 겹침보다 넓게 잡힘)")
            add("C2", f"값 상자가 기준점에서 60 px 넘게 떨어짐 — {w}×{h}", not d["far"], d["far"] or "0개", "0개")
            add("C34", f"'유출' 상자가 유출 관 오른쪽 — {w}×{h}", d["distRight"] is True, d["distRight"], "오른쪽")
            if w == 1440:
                add("C27", "이름–값 사이 빈칸 > 6 px", not d["bigGap"], d["bigGap"] or "0개", "0개")
                add("A4", "응축액 온도 이름 '하부'", d["hbName"] == "하부", d["hbName"], "하부")
                names = [b[0] for b in d["boxes"]]
                need = ["TI 탱크 내부", "TI-H075 탑 온도", "TIC-H071D 응축액 출구"]
                add("C29", "기본 값 상자: 내부·탑·하부 온도 있음, '끓는점' 없음", all(n in names for n in need) and not any("끓는점" in n for n in names), f"{len(names)}개 · 빠진 것 {[n for n in need if n not in names] or '없음'}", "3개 있음 · 끓는점 0")
                if d2: add("C28", "카메라 고정 5초 동안 상자 위치 변화", d["boxes"] == d2["boxes"], "같음" if d["boxes"] == d2["boxes"] else "달라짐", "0 px")
        s2 = g(sn, "state_reflux")
        if s2 and w == 1440:
            add("D13", "냉각수 흐름 그림", s2["cw"] == 0, s2["cw"], "0개")
            add("E1", "기본 운전 2차 응축기로 가는 몫", s2.get("n2") is not None and s2["n2"] <= 2, f"{s2.get('n2')} %", "≤ 2 %")
    ge = g("기본", "geom")
    if ge:
        add("C9", "세 용기 간격 균형(정제기–본류 틈 ÷ 본류–초류 틈)", 0.6 <= ge["ratio"] <= 1.6, f"{ge['g1']} / {ge['g2']} m = {ge['ratio']}", "0.6 ~ 1.6")
        add("C11", "본류 탱크 > 초류 탱크, 본류 용량 ≥ 투입 부피", ge["Vm"] > ge["Vf"] and ge["Vm"] >= ge["Vchg"], f"본류 {ge['Vm']} · 초류 {ge['Vf']} · 투입 {ge['Vchg']} m³(원통 + 2:1 경판 둘)", "본류 > 초류, 본류 ≥ 투입")
        add("C18", "2차 응축기 → 초류 관(L2)이 초류 관(F) 오른쪽", ge["x2o"] > ge["xF"], f"L2 x {ge['x2o']} · F x {ge['xF']}", "L2 > F")
        add("G6", "배치 시트(투입·초류 컷·본류 컷 + 스타트)", ge["batch"] and ge["fore"] and ge["main"] and ge["btn"], f"시트 {ge['batch']} · 초류 컷 {ge['fore']} · 본류 컷 {ge['main']} · 스타트 {ge['btn']}", "모두 있음")
        cm = ge.get("cam")
        if cm:
            import math as _m
            th = abs(_m.degrees(cm["theta"])); el = 90 - _m.degrees(cm["phi"])
            add("C21", "기본 시점: 옆 각도 ≤ 5°, 위에서 10~17°", th <= 5 and 10 <= el <= 17, f"옆 {th:.1f}° · 위 {el:.1f}°", "≤ 5° · 10~17°")
    fx = g("전환류 1440×1000", "flux")
    if fx:
        exp = 1 - fx["back"]
        add("D2", "점 개수 보존: 컬럼 꼭대기를 넘는 점 ÷ 컬럼에 들어온 점 = 1 − 컬럼 안 응축 비율", abs(fx["top"] - exp) <= 0.15, f"{fx['top']} (기대 {exp:.3f}) · 들어옴 {fx['t12']} · 넘음 {fx['t45']}", "± 0.15")
        add("D2", "점 개수 보존: 응축기에 들어간 점 ÷ 꼭대기를 넘은 점", 0.85 <= fx["cond"] <= 1.1, f"{fx['cond']} · 넘음 {fx['t45']} · 응축기 {fx['t78']}", "0.85 ~ 1.1")
    mi = g("전환류 1440×1000", "misc")
    if mi:
        quiet = mi["n2kg"] < 1 and mi["ovKg"] < 1
        add("D14", "2차 응축기 쪽 계산 흐름 < 1 kg/h일 때 T2·L2 관 흐름 그림 없음", (not quiet) or (mi["T2"] <= 0.01 and mi["L2"] <= 0.01), f"2차로 {mi['n2kg']} kg/h · 넘침 {mi['ovKg']} · T2 {mi['T2']} · L2 {mi['L2']}", "T2·L2 = 0")
        add("B1", "기본 운전에 '막힘' 표시 없음", mi["chipsBlk"] == 0, f"{mi['chipsBlk']}개", "0개")
        add("D20", "증기관 빨강·주황 칠 없음", mi["vHot"] == 0 and mi["vMesh"] > 0, f"증기관 조각 {mi['vMesh']}개 중 {mi['vHot']}개", "0개")
    rt = g("전환류 1440×1000", "rtoggle")
    if rt:
        add("D6", "환류 밸브 닫고 열 때 관 채움이 0.1초에 0.5 넘게 바뀌지 않음(점점 차고 빠짐)", rt["jump"] <= 0.5, f"한 번에 최대 {rt['jump']}", "≤ 0.5")
        add("E2", "환류 밸브를 닫으면 환류 유량이 줄고, 다시 열면 흐름", rt["closedEnd"][3] < rt["openEnd"][3] or rt["openEnd"][1] > 0.5, f"닫음 끝 {rt['closedEnd']} · 엶 끝 {rt['openEnd']}", "닫으면 줄고 열면 참")
        cams = rt.get("cam") or []
        if cams and cams[0] is not None:
            add("C24", "밸브를 눌러도 화면 크기(카메라 거리) 그대로", max(cams) - min(cams) < 1e-6, f"{cams}", "변화 0")
    p0 = g("환류 관 2 mm 고임", "pool0"); p6 = g("환류 관 2 mm 고임", "pool6"); pb = g("환류 관 2 mm 고임", "poolBack")
    if p0 and p6:
        add("E8", "환류 관 2 mm(CpHf 응축액 약 20 kg/h보다 배출 한계가 작게): 1차 응축기에 고임 → 하부 온도 하강 · 2차·넘침 증가", p6["hC1"] > 0.005 and p6["Tbot"] is not None and p6["Tbot"] <= p6["T1out"] and (p6["n2"] + p6["ov"]) >= p0["n2"] + p0["ov"], f"고임 {p0['hC1']} → {p6['hC1']} m · 하부 {p6['Tbot']} ≤ 출구 {p6['T1out']} ℃ · 2차+넘침 {p0['n2'] + p0['ov']:.2f} → {p6['n2'] + p6['ov']:.2f} kg/h", "고임 > 0, 하부 ≤ 출구, 2차 증가")
        if p6.get("c1h") is not None:
            add("D16", "1차 응축기 그린 액면 높이 = 계산 고임 높이", abs(p6["c1h"] - p6["hC1"]) <= max(0.003, 0.1 * p6["hC1"]), f"그림 {p6['c1h']} · 계산 {p6['hC1']} m", "± 10 %")
    if pb and p6:
        add("E8", "환류 관을 15.8 mm로 되돌리면 고임이 빠짐", pb["hC1"] < p6["hC1"], f"{p6['hC1']} → {pb['hC1']} m", "줄어듦")
    od = g("수동 끓기 순서", "order")
    if od:
        add("D1", "끓기 시작: 목관 액 점이 증기 점보다 먼저 생김", od["tV"] is not None and (od["tL"] is None or od["tL"] >= od["tV"]), f"증기 점 {round(od['tV'], 1) if od['tV'] is not None else None}분 → 액 점 {round(od['tL'], 1) if od['tL'] is not None else None}분", "증기 먼저")
        add("D30", "목관에 흰 점과 따로 뿌린 파란 방울", od["dripMax"] == 0, f"최대 {od['dripMax']}개", "0개")
        add("D31", "목관 파란 점 ÷ 흰 점(흰 점 3개 이상일 때 최대)", od["ratio"] <= 3, f"{od['ratio']}배", "≤ 3배")
        add("D3", "액이 되지 못하고 지워진 증기 점(정제기·목관·컬럼)", od["lost"] == 0, f"{od['lost']}개", "0개")
        add("D32", "환류가 위에서 들어오기 전 충전층 액막 높이(충전층 비율)", od["filmMax"] <= 0.5, f"최대 {od['filmMax']}", "≤ 응축 전선(0.5 이하)")
    ov = g("1차 응축기 넘침", "ov")
    if ov:
        add("D33", "1차 응축기 넘침 때 2차 응축기 안을 지나는 액 점", ov["ov2"] > 0, f"넘침 {ov['ovKg']} kg/h · 2차 응축기 안 액 점 {ov['ov2']}개", "> 0")
        add("E27", "고인 응축기 하부 온도는 냉각수 온도 아래로 안 내려감", ov["Tbot"] is not None and ov["Tbot"] >= ov["Tcw"] - 0.05, f"하부 {ov['Tbot']:.2f} ℃ · 응축 출구 {ov['T1out']:.2f} ℃ · 냉각수 {ov['Tcw']} ℃" if ov["Tbot"] is not None else "-", "≥ 냉각수")
    tj = g("수동 끓기 빨리 감기", "tb_jump")
    if tj:
        add("E25", "수동 스팀 70 % 빨리 감기: 끓기 시작 뒤 (계산 끓는점 − 액 온도) 최대", tj["mx"] <= 2, f"{tj['mx']} ℃ (끓기 시작 {tj['onset']} h, 액 {tj['T']})", "≤ 2 ℃")
    tl = g("수동 끓기 실시간 ×120", "tb_live")
    if tl:
        add("E25", "수동 스팀 70 % 실시간 ×120: 끓기 시작 뒤 (계산 끓는점 − 액 온도) 최대", tl["mx"] <= 2, f"{tl['mx']} ℃ (끓기 시작 {tl['onset']} h, 액 {tl['T']})", "≤ 2 ℃")
        add("E26", "수동 스팀 70 % 실시간 ×120: 30초 평균 증발이 직전 창의 절반 아래로 떨어진 창(2 kg/h 넘은 뒤)", tl["drop"] == 0, f"{tl['drop']}개 · {tl['win'][:16]}", "0개")
    for sn, r in out.items():
        bad = [c for c in r["console"] if "error" in c.lower() and "clean" not in c.lower()]
        add("F6", f"콘솔 오류 — {sn}", not bad, bad[:2] or "깨끗", "0건")
    return R

def static_checks():
    R = []
    html = SIM_HTML.read_text(encoding="utf-8")
    ext = re.findall(r"""(?:src|href)\s*=\s*["'](https?://[^"']+)""", html)
    R.append({"id": "F2", "name": "파일 하나로 동작(외부 http 참조)", "ok": not ext, "val": ext[:3] or "0개", "crit": "0개"})
    ver = re.search(r">(v\d{3}) · ", html); ver = ver.group(1) if ver else None
    docp = SIM_DIR / "적용_공식_정리.md"; doc = docp.read_text(encoding="utf-8") if docp.exists() else ""
    if not doc:   # 저장소에 계산 근거 문서가 없으면 건너뜀(공개 저장소라 따로 받는다)
        for i, n in (("F5", "공식 정리에 최신 판 절"), ("A5", "문서 제목 명사형(공식 정리)"), ("A6", "문서 한다체('~요.' 문장)")):
            R.append({"id": i, "name": n + "(적용_공식_정리.md 없음 — 건너뜀)", "ok": None, "val": "-", "crit": "-"})
    else:
        R.append({"id": "F5", "name": "공식 정리에 최신 판 절", "ok": bool(ver and re.search(rf"^## {ver}\b", doc, re.M)), "val": ver, "crit": "## vNNN 절 있음"})
        heads = re.findall(r"^#{1,3} (.+)$", doc, re.M)
        badh = [h for h in heads if re.search(r"(나\?|하려면|한다|했다|인가|일까)\s*$", h)]
        R.append({"id": "A5", "name": "문서 제목 명사형(공식 정리)", "ok": not badh, "val": badh[:3] or "0개", "crit": "0개"})
        yo = [l for l in doc.splitlines() if re.search(r"[가-힣]요\.\s*$", l) and not l.startswith("|")]
        R.append({"id": "A6", "name": "문서 한다체('~요.' 문장)", "ok": not yo, "val": yo[:2] or "0개", "crit": "0개"})
    srv = pathlib.Path(r"C:/Users/large/OneDrive/Desktop/Claude/정제분석/사내망_시뮬레이터_서버")
    if srv.exists():   # 개발 PC에만 있는 확인
        sv = None
        for f in srv.rglob("distill*.html"):
            m = re.search(r">(v\d{3}) · ", f.read_text(encoding="utf-8", errors="ignore"));
            if m: sv = m.group(1); break
        R.append({"id": "F3", "name": "사내망 서버 판 = 빌드 판", "ok": sv == ver, "val": f"서버 {sv} / 빌드 {ver}", "crit": "같음"})
    else: R.append({"id": "F3", "name": "사내망 서버 판 = 빌드 판(이 PC에 서버 폴더 없음 — 건너뜀)", "ok": None, "val": "-", "crit": "-"})
    gitd = SIM_DIR if (SIM_DIR / ".git").exists() else pathlib.Path(r"C:/Users/large/OneDrive/Desktop/Claude/정제분석/깃허브_distill-sim")
    if not (gitd / ".git").exists():
        R.append({"id": "F1", "name": "깃허브 distill-sim 판 = 빌드 판(깃 폴더 없음 — 건너뜀)", "ok": None, "val": "-", "crit": "-"}); return R, ver
    try:
        subprocess.run(["git", "-C", str(gitd), "fetch", "-q", "origin", "distill-sim"], timeout=60)
        txt = subprocess.run(["git", "-C", str(gitd), "show", "origin/distill-sim:index.html"], capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=60).stdout
        m = re.search(r">(v\d{3}) · ", txt); gv = m.group(1) if m else None
    except Exception as e: gv = f"오류 {e}"
    R.append({"id": "F1", "name": "깃허브 distill-sim 판 = 빌드 판", "ok": gv == ver, "val": f"깃 {gv} / 빌드 {ver}", "crit": "같음"})
    return R, ver

def regress_checks(prefix):
    R = []
    d = pathlib.Path(prefix)
    files = sorted(f for f in d.parent.glob(d.name + "_*.txt") if not f.stem.endswith("_all"))
    for f in files:
        txt = f.read_text(encoding="utf-8", errors="ignore")
        fails = len(re.findall(r"\b(FAIL|XX)\b", txt)); oks = len(re.findall(r"\bOK\b", txt)); clean = "console: clean" in txt
        R.append({"id": "F6", "name": "회귀 " + f.stem.split("_", 1)[1], "ok": fails == 0 and clean, "val": f"OK {oks} · FAIL {fails} · 콘솔 {'깨끗' if clean else '오류'}", "crit": "FAIL 0 · 콘솔 깨끗"})
    return R

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--url", default=""); ap.add_argument("--only", default=""); ap.add_argument("--reg", default=""); ap.add_argument("--tag", default=""); ap.add_argument("--rejudge", default="")
    a = ap.parse_args()
    if not a.url and not a.rejudge: a.url = serve_local(); print("로컬 서버:", a.url, "←", SIM_HTML.name, flush=True)
    only = set(x for x in a.only.split(",") if x)
    out = {}
    if a.rejudge: out = json.loads((HERE / f"점검결과_{a.rejudge}.json").read_text(encoding="utf-8"))["raw"]
    for sc in ([] if a.rejudge else build_scenarios()):
        if only and not any(sc["name"].startswith(o) for o in only): continue
        print("▶", sc["name"], flush=True); out[sc["name"]] = run(sc, a.url); print("  ", out[sc["name"]]["sec"], "s", list(out[sc["name"]]["res"].keys()), flush=True)
    R = judge(out)
    S, ver = static_checks(); R += S
    if a.reg: R += regress_checks(a.reg)
    npass = sum(r["ok"] is True for r in R); nfail = sum(r["ok"] is False for r in R); nref = sum(r["ok"] is None for r in R)
    md = [f"# 자동 점검 결과 {ver or ''} {a.tag}".rstrip(), "", f"통과 {npass} · 실패 {nfail} · 판정 {npass + nfail}항목(참고 {nref}줄 따로)  ({time.strftime('%Y-%m-%d %H:%M')})", "", "| 결과 | ID | 항목 | 잰 값 | 기준 |", "|---|---|---|---|---|"]
    for r in R:
        v = r["val"]; v = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
        md.append(f"| {'참고' if r['ok'] is None else '통과' if r['ok'] else '**실패**'} | {r['id']} | {r['name']} | {v.replace('|', '/')[:300]} | {r['crit']} |")
    name = "점검결과" + (("_" + a.tag) if a.tag else "")
    (HERE / (name + ".md")).write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / (name + ".json")).write_text(json.dumps({"ver": ver, "R": R, "raw": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"통과 {npass} · 실패 {nfail}")
    for r in R:
        if r["ok"] is False: print("  실패", r["id"], r["name"], "→", str(r["val"])[:200])

if __name__ == "__main__":
    main()
