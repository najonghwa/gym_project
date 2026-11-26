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
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import 점검_공식 as X   # v117: 공식 검산·이상 상황 반응 시험
import 점검_합침 as Y   # v125: 사내망 v117~v124 합침 확인
import 점검_스팀 as SV   # v138s: 스팀 개도 레시피 · 밸브 → 자켓 · 승온(현장 DB 판정 범위) — 장면 이름이 '스팀'으로 시작(--only 스팀)

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
  const D=window.__dt;const vBefore=!!D.VLV.V;try{D.setValve('V',false);}catch(e){}const vAfter=!!D.VLV.V;const Cb=(document.getElementById('C')||{}).value,agType=(document.getElementById('type')||{}).value;const alarmBtn=/알림\s*\d+\s*개/.test(txt);
  return JSON.stringify({vBefore,vAfter,Cb,agType,alarmBtn,words,badHit,dup,ver,spd,rows,kinded,estNoTip,P:(document.getElementById('P')||{}).value,style:D.STYLE,solver:D.solverKind,mat:(D.CUR&&D.CUR.A&&D.CUR.A.name)||null,len:txt.length});
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
  const dist=B.find(b=>b.n==='FICH072 유출');const distRight=dist?dist.x>=dist.ax-1:null;
  const gaps=[];document.querySelectorAll('.dcs-tag').forEach(el=>{if(el.offsetParent===null)return;const i=el.children[0],b=el.children[1];if(!i||!b||!b.textContent.trim())return;const g=b.getBoundingClientRect().left-i.getBoundingClientRect().right;gaps.push([el.dataset.n,+g.toFixed(1)]);});
  const bigGap=gaps.filter(g=>g[1]>6);
  const hb=B.find(b=>/TICH071D/.test(b.n));
  return JSON.stringify({n:B.length,pairs,pipe,touch,far,distRight,bigGap,hbName:hb?(document.querySelector('.dcs-tag[data-n="'+hb.n+'"]')||{children:[{textContent:'?'}]}).children[0].textContent:null,boxes:B.map(b=>[b.n,Math.round(b.x),Math.round(b.y)])});
})()"""

JS_STATE = r"""(()=>{const D=window.__dt,P=D.PR,s=D.vaporStats();const kinds={};for(const p of D.FXP)kinds[p.kind]=(kinds[p.kind]||0)+1;
  return JSON.stringify({t:+(P.t/3600).toFixed(3),vdot:+P.vdot.toFixed(1),P:+P.Pstill.toFixed(3),flood:+(P.flood||0).toFixed(2),R:+(P.Rkg||0).toFixed(1),D:+(P.Dkg||0).toFixed(1),hC1:+(P.hC1||0).toFixed(3),n2:P.fr?+(((P.fr.n2||0)+(P.fr.lost||0))*100).toFixed(2):null,sec:s.sec,down:s.down,cw:Object.keys(kinds).filter(k=>/^cw/.test(k)).reduce((a,k)=>a+kinds[k],0),kinds});})()"""


# 수동 스팀 70 % 끓기 시작(부모 세션 요청 v114): 끓기 시작 뒤 (계산 끓는점 − 액 온도) 최대, 30초 평균 증발 변동 — 빨리 감기·실시간
SET_MANUAL = "(()=>{const D=window.__dt;D.opSetMode(true);D.OP.rfic.sv=4;return 1})()"
JS_TB_HIST = r"""(()=>{const H=window.__dt.PR.hist.filter(h=>h.t>=0.9*3600&&h.t<=1.4*3600);let on=-1;for(let i=0;i<H.length;i++)if(H[i].T>=H[i].Tb-0.3){on=i;break;}let mx=0,at=null;if(on>=0)for(let i=on;i<H.length;i++){const d=H[i].Tb-H[i].T;if(d>mx){mx=d;at=H[i].t/3600;}}return JSON.stringify({n:H.length,onset:on>=0?+(H[on].t/3600).toFixed(3):null,mx:+mx.toFixed(2),at,T:H.length?[+H[0].T.toFixed(1),+H[H.length-1].T.toFixed(1)]:null})})()"""
JS_TB_LIVE = r"""(async()=>{const D=window.__dt,t0=D.PR.t;D.STEPLOG.length=0;while(D.PR.t<t0+__SPAN__)await new Promise(r=>setTimeout(r,500));const L=D.STEPLOG.slice();let on=-1;for(let i=0;i<L.length;i++)if(L[i][4]>=L[i][5]-0.3){on=i;break;}let mx=0;if(on>=0)for(let i=on;i<L.length;i++)mx=Math.max(mx,L[i][5]-L[i][4]);const win=[];for(let t=t0;t<t0+__SPAN__;t+=30){const w=L.filter(r=>r[0]>=t&&r[0]<t+30);if(w.length)win.push(+(w.reduce((a,r)=>a+r[1],0)/w.length).toFixed(2));}let drop=0,first=-1;for(let i=0;i<win.length;i++)if(win[i]>2){first=i;break;}if(first>=0)for(let i=first+1;i<win.length;i++)if(win[i]<0.5*win[i-1])drop++;return JSON.stringify({n:L.length,onset:on>=0?+(L[on][0]/3600).toFixed(3):null,mx:+mx.toFixed(2),win,drop,T:[+L[0][4].toFixed(1),+L[L.length-1][4].toFixed(1)]})})()"""


# v115: 끓기 시작 순서·점 수(흰 점이 응축해 파란 점이 된다), 지워지는 증기 점, 액막 높이, 2차 응축기 넘친 액
# v128: 파란 점도 흰 점과 같은 구간(정제기 꼭대기 ~ 컬럼 바닥, 목관 둘레)에서 센다. 전에는 vaporStats의 nNeckLiq(목관 아래 정제기 위 공간으로 떨어지는 점까지)를 써서, 그림에서 목관을 줄이자(v128) 흰 점 구간만 짧아져 비가 2.38 → 3.75로 커졌다
JS_ORDER = r"""(async()=>{const D=window.__dt,q=D.M.pipe;let tV=null,tL=null,dripMax=0,ratioMax=0,filmMax=0,filmOver=-1,filmFront=null,lost0=D.vaporStats().lost,n=0;const t0=D.PR.t;
  while(D.PR.t<t0+__SPAN__){const s=D.vaporStats();let vN=0,dN=0,lN=0;for(const v of D.VP){if(v._y==null)continue;const inNeck=v._y>D.M.topY&&v._y<q.colBase&&Math.abs((v._x==null?q.xN:v._x)-q.xN)<q.rCol*1.5;if(v.liq||v._drop){if(inNeck)lN++;continue;}if(v._y>D.M.topY&&v._y<q.colBase)vN++;}for(const p of D.FXP)if(p.kind==='drip'&&Math.abs(p.x-q.xN)<q.rCol*1.2)dN++;
    const tm=D.PR.t/60;if(vN>0&&tV==null)tV=tm;if(s.nNeckLiq>0&&tL==null)tL=tm;dripMax=Math.max(dripMax,dN);if(vN>=3)ratioMax=Math.max(ratioMax,lN/vN);if(!(D.FILL.RD&&D.FILL.RD.full)){const fp=Math.max(0.02,Math.min(1,(q.colBase+s.front*(q.colTop-q.colBase)-q.packY0)/(q.packY1-q.packY0)));if(s.filmH>filmMax){filmMax=s.filmH;filmFront=+fp.toFixed(3);}filmOver=Math.max(filmOver,s.filmH-fp);}n++;await new Promise(r=>setTimeout(r,250));}
  return JSON.stringify({n,tV,tL,dripMax,ratio:+ratioMax.toFixed(2),filmMax,filmOver:+filmOver.toFixed(3),filmFront,lost:D.vaporStats().lost-lost0})})()"""
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

def scen(name, actions, width=1440, height=1000, theme=None, q=""):
    return {"name": name, "actions": actions, "width": width, "height": height, "theme": theme, "q": q}

def tag(t, js):  # eval 결과에 이름을 붙인다
    return ["eval", f"(async()=>{{const r=await ({js});return JSON.stringify({{tag:{json.dumps(t)},v:JSON.parse(r)}})}})()"]

# >>> 현실성(X) 장면 시작
# ---------- 현실성(2026-11-22): 화면이 실제 설비 · 계산대로 움직이는가 — 요구목록 (X)절, 번호 = 현실성_목록.md 항목 번호 ----------
# 장면은 화면 조작으로만 상태를 만든다: 밸브 줄 단추 누르기 · 입력칸 · 이상 상황 창(ab) · 스팀 개도 게이지(steamSet) · 빨리 감기(startJump). 계산 상태(PR)는 읽기만 한다.
# 재는 것: 0.1초마다 적은 기록(관 채움 · 그린 높이 · 점의 길), 화면 그림을 잘라 찍은 것(받는 탱크 · 정제기 액면, 도면의 관 · 컬럼 색 화소), 보이는 물체의 상태.
# 판정은 점검_합침.judge_real이 한다. 그림 자르기: 측정 식이 그 자리에 보이지 않는 상자(#__xc_*)를 두고 그 상자를 찍는다(그림에는 아무것도 더하지 않는다).
XVB = lambda k: ["click", '#valves button[data-v="' + k + '"]']   # 밸브 줄 단추를 마우스로 누른다
def XSET(i, v): return ["eval", "(()=>{const e=document.getElementById(" + json.dumps(i) + ");if(!e)return 'no';e.value=" + json.dumps(str(v)) + ";e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));return e.value})()"]
def XDL(sec): return ["eval", "window.__xdl=performance.now()+" + str(int(sec * 1000)) + ";1"]   # 기다림의 끝(기다리던 일이 안 생겨도 장면이 끊기지 않게)
def XJUMP(h, settle=3000):   # 빨리 감기(배치가 먼저 끝나면 거기서 멈춘다)
    return [["eval", f"window.__dt.startJump('at',{h});1"], ["until", f"(()=>{{const D=window.__dt,P=D.PR;return !!(P&&!D.TURBO&&(P.t>={h}*3600-120||P.stopped))}})()", 1500000], ["wait", settle]]
def XJREL(dh, settle=4000):   # 지금부터 dh 시간 빨리 감기
    return [["eval", "window.__xjt=window.__dt.PR.t/3600+" + str(dh) + ";window.__dt.startJump('at',window.__xjt);1"], ["until", "(()=>{const D=window.__dt,P=D.PR;return !!(P&&!D.TURBO&&(P.t>=window.__xjt*3600-120||P.stopped))})()", 900000], ["wait", settle]]
def XSHOT(name, sel): return ["shot", str(SHOTS / name), sel]

# 재는 도우미(읽기만): 3D 점 → 화면 자리, 관 채움, 잘라 찍을 상자, 보이는 글, 도면 좌표(mm) → 화면 자리, 점의 길
XH = r"""(()=>{const D=window.__dt,H=window.__xh={};
H.r=(v,n)=>v==null||!isFinite(v)?null:+(+v).toFixed(n==null?3:n);
H.pr=(x,y,z)=>{const cam=D.camera,rc=D.canvas.getBoundingClientRect(),G=D.PIPES.V[0].parent;G.updateMatrixWorld(true);const v=new cam.position.constructor(x,y,z||0);v.applyMatrix4(G.matrixWorld);v.project(cam);return [(v.x*0.5+0.5)*rc.width+rc.left,(-v.y*0.5+0.5)*rc.height+rc.top]};
H.drawn=(f)=>{const iv=[],fl0=!f.want&&f.dr?Math.max(f.tail,f.dr.t||0):f.tail,fh=f.want&&f.fv!=null?Math.min(f.head,f.fv):f.head;if(fh>fl0+1e-6)iv.push([fl0,fh]);for(const p of f.pls||[])if(p[1]>p[0]+1e-6)iv.push([p[0],p[1]]);iv.sort((a,b)=>a[0]-b[0]);let L=0,c=null;for(const x of iv){if(!c||x[0]>c[1]){if(c)L+=c[1]-c[0];c=[x[0],x[1]]}else c[1]=Math.max(c[1],x[1])}if(c)L+=c[1]-c[0];return L};   /* v135 사본: 그린 액 길이(흐르는 · 빠지는 구간 ∪ 고인 구간) — v134부터 고인 액은 f.pls로 따로 */
H.fill=(k)=>{const f=D.FILL[k];if(!f)return null;const s0=f.segs.find(s=>s.ov.visible)||f.segs[0];return [H.r(f.head,4),H.r(f.tail,4),H.r(f.Ltot,4),f.want?1:0,f.held?1:0,f.segs.filter(s=>s.ov.visible).length,f.vapNow===undefined?-1:f.vapNow?1:0,f.sV==null?null:H.r(f.sV,4),s0&&s0.om&&s0.om.color?s0.om.color.getHexString():null,f.plug?H.r(f.plug.L,4):null,(f.pls||[]).map(p=>[H.r(p[0],4),H.r(p[1],4)]),H.r(H.drawn(f),4)]};   /* v135 사본: 뒤에 [9] 밸브 앞 고인 액 길이 · [10] 고인 구간들 · [11] 그린 액 길이 */
H.crop=(id,x,y,w,h)=>{x=Math.round(x);y=Math.round(y);w=Math.max(8,Math.round(w));h=Math.max(8,Math.round(h));let e=document.getElementById(id);if(!e){e=document.createElement('div');e.id=id;document.body.appendChild(e)}e.style.cssText='position:fixed;left:'+x+'px;top:'+y+'px;width:'+w+'px;height:'+h+'px;pointer-events:none;opacity:0';return [x,y,w,h]};
for(const id of ['__xc_fore','__xc_main','__xc_still','__xc_p2','__xc_seg'])H.crop(id,0,0,8,8);
H.vis=(e)=>{for(let x=e;x&&x!==document.body;x=x.parentElement){const cs=getComputedStyle(x);if(cs.display==='none'||cs.visibility==='hidden'||x.hidden||+cs.opacity===0)return false}const r=e.getBoundingClientRect();return r.width>1&&r.height>1&&r.bottom>0&&r.top<innerHeight&&r.right>0&&r.left<innerWidth};
H.tagv=(n)=>{const e=document.querySelector('.dcs-tag[data-n="'+n+'"]');return e&&H.vis(e)&&e.children[1]?e.children[1].textContent.trim():null};
H.texts=(rx)=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);const out=[];let n;while(n=w.nextNode()){const s=n.nodeValue.trim();if(!s)continue;const p=n.parentElement;if(!p||['SCRIPT','STYLE'].includes(p.tagName))continue;if(rx.test(s)&&H.vis(p))out.push(s.slice(0,140))}return out};
H.pts=(els,step)=>{const pts=[];for(const el of els){if(!el||!el.getTotalLength)continue;let L=0;try{L=el.getTotalLength()}catch(e){continue}const m=el.getScreenCTM();if(!m||!(L>0))continue;for(let s=0;s<=L+1e-6;s+=step){const p=el.getPointAtLength(Math.min(s,L));pts.push([m.a*p.x+m.c*p.y+m.e,m.b*p.x+m.d*p.y+m.f])}}return pts};
H.box=(pts,pad)=>{let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(const p of pts){x0=Math.min(x0,p[0]);y0=Math.min(y0,p[1]);x1=Math.max(x1,p[0]);y1=Math.max(y1,p[1])}if(!pts.length)return [0,0,8,8];return [x0-pad,y0-pad,x1-x0+2*pad,y1-y0+2*pad]};
H.rel=(rc,pts)=>pts.map(p=>[+(p[0]-rc[0]+4).toFixed(1),+(p[1]-rc[1]+4).toFixed(1)]);
H.p2=()=>{const Q=D.PID2,M=D.M,q=M.pipe;if(!Q||!Q.svg||Q.root.hidden)return null;const g=Q.svg.firstChild,m=g&&g.getScreenCTM?g.getScreenCTM():null;if(!m)return null;const xMin=-(M.R||M.p.T/2)-0.75,yMax=q.yPipe+0.2;return {f:(x,y)=>{const X=(x-xMin)*1000,Y=(yMax-y)*1000;return [m.a*X+m.c*Y+m.e,m.b*X+m.d*Y+m.f]},iy:(sy)=>yMax-((sy-m.f)/m.d)/1000,k:1000*m.d}};
H.vrt=()=>{let n=0,aft=0,thru=0;for(const v of D.VP){if(v.liq||v.cd>=0)continue;n++;const r=v.route;if(r==='vent'||r==='passvent'||r==='c2fore'||r==='pass2fore'){if(v.s>=9)aft++;else if(v.s===8)thru++}}return [n,aft,thru]};
H.bub=()=>{let n=0;for(const p of D.FXP)if(p.kind==='bub'||p.kind==='bubS')n++;return n};
H.vcol=(k)=>{const p=D.VALVE_PARTS&&D.VALVE_PARTS[k];if(!p||!p.parts||!p.parts.length)return null;const m=p.parts[0].material;return m&&m.color?m.color.getHexString():null};
H.btn=(k)=>{const b=document.querySelector('#valves button[data-v="'+k+'"]');return b?b.getAttribute('aria-pressed'):null};
return 1})()"""

# 밸브 · 관 상태 한 장
XSTATE = r"""(()=>{const D=window.__dt,P=D.PR,H=window.__xh,F=D.FILL;const o={};for(const k of ['C','R','RD','P','F','FL','M','T2','L2','S'])o[k]=H.fill(k);const u=D.uSealSpan(F.R);
 return JSON.stringify({rt:+(performance.now()/1000).toFixed(2),t:+P.t.toFixed(1),st:P.rcp?P.rcp.st:null,stopped:!!P.stopped,VLV:Object.fromEntries(['R','P','F','M','J','C1','V'].map(k=>[k,D.VLV[k]?1:0])),
  vcol:{F:H.vcol('F'),P:H.vcol('P'),R:H.vcol('R'),J:H.vcol('J')},btn:{F:H.btn('F'),P:H.btn('P'),R:H.btn('R'),J:H.btn('J')},
  R:H.r(P.Rkg,2),Dk:H.r(P.Dkg,2),cond:H.r(P.condKg,2),sv:D.OP&&D.OP.rfic?D.OP.rfic.sv:null,manual:!!(D.OP&&D.OP.manual),recipe:!!(D.OP&&D.OP.recipe),
  fore:H.r(P.ves.fore.A+P.ves.fore.B,4),main:H.r(P.ves.main.A+P.ves.main.B,4),spill:[H.r(P.spill.fore,4),H.r(P.spill.main,4)],lah:[P.lah.fore,P.lah.main],
  fx:{ring:!!(D.FX.lah&&D.FX.lah.fore&&D.FX.lah.fore.visible),spill:!!(D.FX.spill&&D.FX.spill.fore&&D.FX.spill.fore.visible),pud:!!(D.FX.pud&&D.FX.pud.fore&&D.FX.pud.fore.visible)},
  sealM:H.r(P.sealM,4),holdC:D.CUR.holdC,us:u?[H.r(u.s0,4),H.r(u.s1,4)]:null,fill:o,style:D.STYLE,tagR:H.tagv('FICH073 환류'),tagD:H.tagv('FICH072 유출')})})()"""

# 0.1초마다 적는 기록: 다시 열 때 관 채움(X26)
XPOLL_FILL = r"""(()=>{const D=window.__dt;window.__lg=[];let last=-1;if(window.__pi)clearInterval(window.__pi);window.__pi=setInterval(()=>{const P=D.PR;if(!P||P.t===last)return;last=P.t;const F=D.FILL,H=window.__xh,o=[];for(const k of ['P','F','FL']){const f=F[k];o.push(f?[+f.head.toFixed(4),+f.tail.toFixed(4),f.held?1:0,f.segs.filter(s=>s.ov.visible).length,H&&H.drawn?+H.drawn(f).toFixed(4):null,f.plug?+f.plug.L.toFixed(4):null,f.want?1:0]:null)}   /* v135 사본: [4] 그린 액 길이 · [5] 밸브 앞 고인 액 · [6] 흐름 */window.__lg.push([+(performance.now()/1000).toFixed(2),+P.t.toFixed(1),D.VLV.F?1:0,o])},100);return 1})()"""
# 0.1초마다: 환류 · 유출을 닫아 고이고 넘칠 때(X1 · X2 · X13 · X14)
XPOLL_POOL = r"""(()=>{const D=window.__dt,H=window.__xh;window.__lg=[];let last=-1;if(window.__pi)clearInterval(window.__pi);window.__pi=setInterval(()=>{const P=D.PR;if(!P||P.t===last)return;last=P.t;const fr=P.fr||{},vr=H.vrt();
 window.__lg.push([+(performance.now()/1000).toFixed(2),+P.t.toFixed(1),+(P.splFrac||0).toFixed(3),+(P.cPipeFrac||0).toFixed(3),+(P.hC1||0).toFixed(4),D.C1H==null?null:+D.C1H.toFixed(4),+(P.ovKg||0).toFixed(3),+(P.ves.fore.A+P.ves.fore.B).toFixed(4),+(P.condKg||0).toFixed(3),H.fill('T2'),H.fill('L2'),vr[0],vr[1],vr[2],+((fr.n2||0)+(fr.lost||0)).toFixed(5),+(P.vdot||0).toFixed(3),+(P.m2kg||0).toFixed(4),+(P.lostkg||0).toFixed(5),+(P.mC1||0).toFixed(3),D.VLV.R?1:0,D.VLV.P?1:0])},100);return 1})()"""
# 0.1초마다: 받는 탱크 고액위 · 넘침(X8 · X9)
XPOLL_LAH = r"""(()=>{const D=window.__dt,H=window.__xh;window.__lg=[];let last=-1;if(window.__pi)clearInterval(window.__pi);window.__pi=setInterval(()=>{const P=D.PR;if(!P||P.t===last)return;last=P.t;const FX=D.FX;
 window.__lg.push([+(performance.now()/1000).toFixed(2),+P.t.toFixed(1),+(P.ves.fore.A+P.ves.fore.B).toFixed(4),D.VLV.F?1:0,H.btn('F'),H.vcol('F'),P.lah.fore,+(P.spill.fore||0).toFixed(4),FX.lah&&FX.lah.fore&&FX.lah.fore.visible?1:0,FX.spill&&FX.spill.fore&&FX.spill.fore.visible?1:0,FX.pud&&FX.pud.fore&&FX.pud.fore.visible?1:0,+(P.Dkg||0).toFixed(3),P.rcp?P.rcp.st:null])},100);return 1})()"""
# 0.1초마다: 끓기 시작(3D) — 기포 · 구간별 증기 점 · 목관 액 점 · 관 채움 · U자 · 환류 값 상자(X6 · X22 · X24) · 끝 열 = 증기 점 앞머리 VF.head(11-22 더함: 응축기 안 점이 기록 사이에 빠지는 시각 경합)
XPOLL_ON3 = r"""(()=>{const D=window.__dt,H=window.__xh;window.__lg=[];let last=-1;if(window.__pi)clearInterval(window.__pi);window.__pi=setInterval(()=>{const P=D.PR;if(!P||P.t===last)return;last=P.t;let s=null;try{s=D.vaporStats()}catch(e){}const F=D.FILL,fr=(k)=>F[k]?+(F[k].head/F[k].Ltot).toFixed(3):0;
 window.__lg.push([+(P.t/60).toFixed(3),+P.vdot.toFixed(3),H.bub(),s?s.sec.tank.n:0,s?s.sec.neck.n:0,s?s.sec.colLow.n:0,s?s.sec.colUp.n:0,s?s.sec.pipe.n:0,s?s.sec.cond.n:0,s?s.nNeckLiq:0,P.vpTop?1:0,P.vpCond?1:0,fr('V'),fr('C'),fr('R'),F.RD?F.RD.segs.filter(x=>x.ov.visible).length:0,+(P.sealM||0).toFixed(4),+(P.Rkg||0).toFixed(2),H.tagv('FICH073 환류'),s?s.head:null,P.rfx?+(P.rfx.condTot||0).toFixed(5):0/*rfxc136*/])},100);return 1})()"""
# 0.1초마다: 끓기 시작(도면) — 켜진 흐름 점 · 도면 환류 값(X6 · X22 · X24)
XPOLL_ON2 = r"""(()=>{const D=window.__dt;window.__lg=[];let last=-1;if(window.__pi)clearInterval(window.__pi);window.__pi=setInterval(()=>{const P=D.PR,Q=D.PID2;if(!P||P.t===last)return;last=P.t;const on={};if(Q&&Q.flows&&!Q.root.hidden){for(const f of Q.flows){if(f.el.classList.contains('on'))on[f.k]=(on[f.k]||0)+1}}
 window.__lg.push([+(P.t/60).toFixed(3),+P.vdot.toFixed(3),+(P.sealM||0).toFixed(4),+(P.Rkg||0).toFixed(2),Q&&Q.vals&&Q.vals.FICH073?Q.vals.FICH073.textContent:null,P.vpTop?1:0,P.vpCond?1:0,on])},100);return 1})()"""
# 0.1초마다: 배치 끝(X19 · X28 · X31)
XPOLL_END = r"""(()=>{const D=window.__dt,H=window.__xh;window.__lg=[];let last=-1;if(window.__pi)clearInterval(window.__pi);window.__pi=setInterval(()=>{const P=D.PR;if(!P||P.t===last)return;last=P.t;const F=D.FILL,o={};for(const k of ['V','C','R','RD','P','F','FL','M','T2','L2']){const f=F[k];if(f)o[k]=[+f.head.toFixed(4),+f.tail.toFixed(4)]}const u=D.uSealSpan(F.R);
 window.__lg.push([+(performance.now()/1000).toFixed(2),+P.t.toFixed(1),P.stopped?1:0,H.vrt()[0],H.bub(),o,u?+u.s1.toFixed(4):null,D.VLV.J?1:0,+(D.CUR.jOpen*100).toFixed(2),+(P.vdot||0).toFixed(3)])},100);return 1})()"""
XGET = r"""(()=>{if(window.__pi)clearInterval(window.__pi);window.__pi=null;const L=window.__lg||[];window.__lg=[];const D=window.__dt,F=D.FILL;const Lt={},sv={};for(const k in F){Lt[k]=+F[k].Ltot.toFixed(4);sv[k]=F[k].sV==null?null:+F[k].sV.toFixed(4)}return JSON.stringify({lg:L,Lt,sv,holdC:D.CUR.holdC})})()"""

# 받는 탱크 · 정제기: 잘라 찍을 상자(처음 잰 자리를 그대로 쓴다)와 높이 사다리(설비 높이 y ↔ 그림 속 자리), 계산 부피 비(무게 ÷ 밀도 ÷ 용량 — 여기서 다시 구함)
XLAD3 = r"""(()=>{const D=window.__dt,H=window.__xh,q=D.M.pipe,M=D.M,P=D.PR,C=D.CUR;
 const vesR=(key,y)=>{const f=key==='fore',R=f?q.rRF:q.rRM,hd=f?q.hdF:q.hdM,y0=f?q.yRvF:q.yRvM,y1=f?q.yTopF:q.yTopM,u=y<y0?(y0-y)/hd:y>y1?(y-y1)/hd:0;return R*Math.sqrt(Math.max(0,1-u*u))};
 if(!H.rects)H.rects={};const out={};
 for(const key of ['fore','main']){const f=key==='fore',x=f?q.xF:q.xMn,R=f?q.rRF:q.rRM,hd=f?q.hdF:q.hdM,y0=(f?q.yRvF:q.yRvM)-hd,y1=(f?q.yTopF:q.yTopM)+hd,dx=0.5*R;
  if(!H.rects[key]){const a=H.pr(x-1.25*R,y1,0),b=H.pr(x+1.25*R,y0,0),c=H.pr(x,y1+0.03,-R),d=H.pr(x,y0-0.04,R);H.rects[key]=H.crop('__xc_'+key,Math.min(a[0],b[0]),Math.min(a[1],c[1])-8,Math.abs(b[0]-a[0]),Math.max(b[1],d[1])-Math.min(a[1],c[1])+16)}else H.crop('__xc_'+key,...H.rects[key]);
  const rc=H.rects[key],lad=[];for(let i=0;i<=120;i++){const y=y0+(y1-y0)*i/120,r=vesR(key,y);if(r<=dx){lad.push([+y.toFixed(5),null]);continue}const z=-Math.sqrt(r*r-dx*dx),p=H.pr(x-dx,y,z);lad.push([+y.toFixed(5),[+(p[0]-rc[0]+4).toFixed(2),+(p[1]-rc[1]+4).toFixed(2)]])}
  const v=P.ves[key],m=v.A+v.B,rho=m>0?1/((v.A/m)/P.pA.rho+(v.B/m)/P.pB.rho):800,cap=(f?C.capF:C.capM)/1000,frac=Math.min(1,m/rho/cap);
  const sx=H.pr(x+1.02*R,(y0+y1)/2,0)[0],top=H.pr(x,y1,0),bot=H.pr(x,y0,0);
  out[key]={rect:rc,R,hd,y0,y1,m:+m.toFixed(4),rho:+rho.toFixed(1),frac:+frac.toFixed(5),lad,spx:+(sx-rc[0]+4).toFixed(1),top:H.rel(rc,[top])[0],bot:H.rel(rc,[bot])[0],ring:H.rel(rc,[H.pr(x,(y0+hd)+0.97*((y1-hd)-(y0+hd)),R)])[0]}}
 {const R=M.R,hh=M.hh,dx=0.5*R;if(!H.rects.still){const a=H.pr(-1.15*R,M.topY,0),b=H.pr(1.15*R,0,0),c=H.pr(0,M.topY,-R),d=H.pr(0,0,R);H.rects.still=H.crop('__xc_still',Math.min(a[0],b[0]),Math.min(a[1],c[1])-8,Math.abs(b[0]-a[0]),Math.max(b[1],d[1])-Math.min(a[1],c[1])+16)}else H.crop('__xc_still',...H.rects.still);
  const rc=H.rects.still,lad=[],zb=-Math.sqrt(R*R-dx*dx);for(let i=0;i<=140;i++){const y=M.topY*i/140,r=y>=hh?R:R*Math.sqrt(Math.max(0,1-((hh-y)/hh)**2));if(r<=dx){lad.push([+y.toFixed(5),null]);continue}const z=-Math.sqrt(r*r-dx*dx),p=H.pr(-dx,y,z);lad.push([+y.toFixed(5),[+(p[0]-rc[0]+4).toFixed(2),+(p[1]-rc[1]+4).toFixed(2)]])}
  const sw=M.surfY(-dx,zb),pe=H.pr(-dx,sw,zb);out.still={rect:rc,R,hh,topY:M.topY,h:+P.h.toFixed(5),m:+P.m.toFixed(3),rho:+P.mix.rho.toFixed(1),sw:+sw.toFixed(5),exp:H.rel(rc,[pe])[0],lad}}
 out.t=+P.t.toFixed(1);out.st=P.rcp?P.rcp.st:null;return JSON.stringify(out)})()"""

# 도면: 액 도형(정제기 · 받는 탱크 · 1차 응축기 고임)의 화면 상자와 계산값의 화면 자리
XP2LEV = r"""(()=>{const D=window.__dt,H=window.__xh,Q=D.PID2,P=D.PR,M=D.M,q=M.pipe,C=D.CUR;const T=H.p2();if(!T)return JSON.stringify({hidden:true});
 const bb=(e)=>{if(!e)return null;const r=e.getBoundingClientRect();return r.width||r.height?[+r.left.toFixed(1),+r.top.toFixed(1),+r.width.toFixed(1),+r.height.toFixed(1)]:null};
 const v=(key)=>{const x=P.ves[key],m=x.A+x.B,rho=m>0?1/((x.A/m)/P.pA.rho+(x.B/m)/P.pB.rho):800,f=key==='fore',cap=(f?C.capF:C.capM)/1000,hd=f?q.hdF:q.hdM,y0=(f?q.yRvF:q.yRvM)-hd,y1=(f?q.yTopF:q.yTopM)+hd;
  return {m:+m.toFixed(4),frac:+Math.min(1,m/rho/cap).toFixed(5),R:f?q.rRF:q.rRM,hd,y0,y1,box:bb(Q.dyn[key])}};
 return JSON.stringify({k:+T.k.toFixed(4),mY:[T.iy(0),T.iy(1000)],f0:T.f(0,0),f1:T.f(0,1),still:{h:+P.h.toFixed(5),yh:+T.f(0,P.h)[1].toFixed(2),yb:+T.f(0,0)[1].toFixed(2),box:bb(Q.dyn.tankLiq)},fore:v('fore'),main:v('main'),c1:{h:H.r(P.hC1,4),box:bb(Q.dyn.c1Liq)},t:+P.t.toFixed(1)})})()"""

# 받는 탱크 무게 증가 · 유출 표시 · 증기 점 수(20초, 0.5초마다)
XRATE = r"""(async()=>{const D=window.__dt,H=window.__xh;const s=[];const t0=performance.now();
 while(performance.now()-t0<20000){const p=D.PR,vr=H.vrt();s.push([+(p.t).toFixed(1),+(p.ves.fore.A+p.ves.fore.B).toFixed(5),+(p.ves.main.A+p.ves.main.B).toFixed(5),+(p.Dkg||0).toFixed(3),+(p.vdot||0).toFixed(3),vr[0],H.tagv('FICH072 유출'),H.tagv('WIH072 초류 무게'),H.tagv('WIH073 본류 무게')]);await new Promise(r=>setTimeout(r,500))}
 return JSON.stringify({s,st:D.PR.rcp?D.PR.rcp.st:null,VLV:{F:D.VLV.F?1:0,M:D.VLV.M?1:0,P:D.VLV.P?1:0}})})()"""

# 환류 관 · 유출 관에서 가장 긴 토막의 화면 자리(줄기 굵기 재기, X34)
XSEG = r"""(()=>{const D=window.__dt,H=window.__xh,F=D.FILL,P=D.PR;const out={},pts=[];
 for(const k of ['R','P']){const f=F[k];if(!f||!f.segs.length)continue;const s=f.segs.reduce((a,b)=>b.L>a.L?b:a),a=s.a,d=s.d,at=(t)=>H.pr(a.x+d.x*s.L*t,a.y+d.y*s.L*t,a.z+d.z*s.L*t);
  const p0=at(0.2),p1=at(0.8),m=[a.x+d.x*s.L/2,a.y+d.y*s.L/2,a.z+d.z*s.L/2],pm=H.pr(m[0],m[1],m[2]),pu=H.pr(m[0],m[1]+s.r,m[2]),px=H.pr(m[0]+s.r,m[1],m[2]);
  out[k]={p0,p1,rpx:+Math.max(Math.hypot(pu[0]-pm[0],pu[1]-pm[1]),Math.hypot(px[0]-pm[0],px[1]-pm[1])).toFixed(2),w:s.w==null?null:+s.w.toFixed(3),head:H.r(f.head,3),L:H.r(f.Ltot,3),want:f.want?1:0};pts.push(p0,p1)}
 const rc=H.crop('__xc_seg',...H.box(pts,16));for(const k in out){out[k].p0=H.rel(rc,[out[k].p0])[0];out[k].p1=H.rel(rc,[out[k].p1])[0]}
 return JSON.stringify({rect:rc,seg:out,R:H.r(P.Rkg,2),Dk:H.r(P.Dkg,2),VLV:{F:D.VLV.F?1:0,M:D.VLV.M?1:0}})})()"""

# 도면: 닫힌 밸브 앞 관(유출 관 P · 초류 가지 F)의 선을 따라 고른 점(그림 화소로 남은 액 색을 본다)과 흐름 점 상태
XP2RES = r"""(()=>{const D=window.__dt,H=window.__xh,Q=D.PID2;if(!Q||!Q.svg||Q.root.hidden)return JSON.stringify({hidden:true});
 const fl=(k)=>Q.flows.filter(f=>f.k===k);const smp={P:H.pts(fl('P').map(f=>f.el),6),F:H.pts(fl('F').map(f=>f.el),6)};const rc=H.crop('__xc_p2',...H.box(smp.P.concat(smp.F),12));
 const st={};for(const k of ['P','F','FL','M','R']){st[k]=fl(k).map(f=>[f.el.classList.contains('on')?1:0,+(+getComputedStyle(f.el).opacity).toFixed(2),getComputedStyle(f.el).stroke])}
 const vb=(k)=>{const g=(Q.valves[k]||[])[0];if(!g)return null;const r=g.getBoundingClientRect();return [+(r.left+r.width/2-rc[0]+4).toFixed(1),+(r.top+r.height/2-rc[1]+4).toFixed(1),g.getAttribute('class')]};
 return JSON.stringify({rect:rc,pts:{P:H.rel(rc,smp.P),F:H.rel(rc,smp.F)},st,valves:{P:vb('P'),F:vb('F'),M:vb('M')},VLV:{P:D.VLV.P?1:0,F:D.VLV.F?1:0,M:D.VLV.M?1:0},fill:{P:H.fill('P'),F:H.fill('F'),FL:H.fill('FL')}})})()"""

# 도면: 넘치는 동안 미응축 증기 관(T2) · 2차 응축기 → 초류 관(L2)의 흐름 점 색과 선을 따라 고른 점, 1차 응축기 고임 사각형 높이
XP2OV = r"""(()=>{const D=window.__dt,H=window.__xh,Q=D.PID2,P=D.PR;const T=H.p2();if(!T)return JSON.stringify({hidden:true});
 const fl=(k)=>Q.flows.filter(f=>f.k===k);const st=(k)=>fl(k).map(f=>[f.el.classList.contains('on')?1:0,+(+getComputedStyle(f.el).opacity).toFixed(2),getComputedStyle(f.el).stroke,f.kind]);
 const pT2=H.pts(fl('T2').map(f=>f.el),5),pL2=H.pts(fl('L2').map(f=>f.el),5);const rc=H.crop('__xc_p2',...H.box(pT2.concat(pL2),10));const c=Q.dyn.c1Liq?Q.dyn.c1Liq.getBoundingClientRect():null;
 return JSON.stringify({rect:rc,T2:{st:st('T2'),pts:H.rel(rc,pT2)},L2:{st:st('L2'),pts:H.rel(rc,pL2)},ov:H.r(P.ovKg,2),fr2:P.fr?H.r((P.fr.n2||0)+(P.fr.lost||0),4):null,c1:{hC1:H.r(P.hC1,4),hpx:c?+c.height.toFixed(2):null,k:+T.k.toFixed(4)}})})()"""

# 환류 관(U자) 채움
XRSNAP = r"""(()=>{const D=window.__dt,H=window.__xh,P=D.PR,f=D.FILL.R;const u=D.uSealSpan(f);return JSON.stringify({style:D.STYLE,R:H.fill('R'),us:u?[H.r(u.s0,4),H.r(u.s1,4)]:null,sealM:H.r(P.sealM,4),holdC:D.CUR.holdC,VR:D.VLV.R?1:0,segs:f.segs.map(s=>s.ov.visible?1:0),seal2d:D.PID2&&D.PID2.dyn&&D.PID2.dyn.useal?D.PID2.dyn.useal.getAttribute('class'):null})})()"""

# 도면: 초류 탱크 둘레(고액위 · 넘침 표시)
XP2TANK = r"""(()=>{const D=window.__dt,H=window.__xh,Q=D.PID2,P=D.PR,q=D.M.pipe;const T=H.p2();if(!T)return JSON.stringify({hidden:true});
 const x=q.xF,R=q.rRF,hd=q.hdF,y0=q.yRvF-hd,y1=q.yTopF+hd,a=T.f(x-R,y1),b=T.f(x+R,y0);const rc=H.crop('__xc_p2',Math.min(a[0],b[0])-45,Math.min(a[1],b[1])-35,Math.abs(b[0]-a[0])+90,Math.abs(b[1]-a[1])+70);
 const tok=/^(p2-)?(lah|spill|ovf|overflow|pud|hilevel|hiLevel|alarm)/;const hits=[];for(const e of Q.svg.querySelectorAll('*')){if(e===Q.dyn.col)continue;const cl=(e.getAttribute('class')||'').split(/\s+/);const tx=e.tagName==='text'?e.textContent:'';if((cl.some(c=>tok.test(c))||/고액위|넘침|LAH/.test(tx))&&+getComputedStyle(e).opacity>0.05&&getComputedStyle(e).display!=='none')hits.push((e.getAttribute('class')||e.tagName)+':'+tx.slice(0,20))}
 const vf=(Q.valves.F||[]).map(g=>g.getAttribute('class'));const vpos=[];for(const k in Q.valves)for(const g of Q.valves[k]){const r=g.getBoundingClientRect();vpos.push([k,+(r.left+r.width/2-rc[0]+4).toFixed(1),+(r.top+r.height/2-rc[1]+4).toFixed(1),+(Math.max(r.width,r.height)/2+4).toFixed(1)])}
 return JSON.stringify({rect:rc,tank:H.rel(rc,[[Math.min(a[0],b[0]),Math.min(a[1],b[1])],[Math.max(a[0],b[0]),Math.max(a[1],b[1])]]),hits,valveF:vf,vpos,VF:D.VLV.F?1:0,spill:H.r(P.spill.fore,4),lah:P.lah.fore,fore:H.r(P.ves.fore.A+P.ves.fore.B,4),box:(()=>{const e=Q.dyn.fore;if(!e)return null;const r=e.getBoundingClientRect();return H.rel(rc,[[r.left,r.top],[r.right,r.bottom]])})()})})()"""

# 1차 냉매 온도 상승 · 스팀 과다 · 펌프 쪽 넘침 · 범람 · 과충전 상태
XSTF = r"""(()=>{const D=window.__dt,H=window.__xh,P=D.PR,fr=P.fr||{};return JSON.stringify({t:+P.t.toFixed(1),c1:P.c1==null?null:+P.c1.toFixed(4),m2:H.r(P.m2kg,3),lostkg:H.r(P.lostkg,4),vdot:H.r(P.vdot,3),back:H.r(fr.back,4),seal:H.r(fr.seal,4),n2:H.r(fr.n2,4),R:H.r(P.Rkg,2),Dk:H.r(P.Dkg,2),fore:H.r(P.ves.fore.A+P.ves.fore.B,4),
 C:H.fill('C'),T2:H.fill('T2'),L2:H.fill('L2'),tagBot:H.tagv('TICH071D 응축액 출구'),tagC2:H.tagv('E-H072 응축 부하(계산)')})})()"""
XP2FLOWS = r"""(()=>{const D=window.__dt,Q=D.PID2;if(!Q||!Q.svg||Q.root.hidden)return JSON.stringify({hidden:true});const st={};for(const f of Q.flows){(st[f.k]=st[f.k]||[]).push([f.el.classList.contains('on')?1:0,+(+getComputedStyle(f.el).opacity).toFixed(2),getComputedStyle(f.el).stroke,f.kind])}
 return JSON.stringify({st,vals:Object.fromEntries(Object.entries(Q.vals||{}).map(([k,v])=>[k,v.textContent])),valveJ:(Q.valves.J||[]).map(g=>g.getAttribute('class'))})})()"""
XSTG = r"""(()=>{const D=window.__dt,H=window.__xh,P=D.PR,C=D.CUR;const tags=[...document.querySelectorAll('.dcs-tag')].filter(e=>H.vis(e)).map(e=>[e.dataset.n,e.children[1]?e.children[1].textContent.trim():'',e.className]);
 return JSON.stringify({t:+P.t.toFixed(1),T:H.r(P.Tmean,2),TmaxL:H.r(P.TmaxL,2),hot:H.r(P.hotFrac,3),Tlim:C.Tlim,vdot:H.r(P.vdot,3),nv:H.vrt()[0],glow:!!(D.FX.hotGlow&&D.FX.hotGlow.visible),txtHot:H.texts(/열안정|분해|한계.{0,8}초과/),
  pumpLiq:H.r(P.pumpLiqKg,3),lost:H.r(P.lost,4),ov:H.r(P.ovKg,2),Dk:H.r(P.Dkg,2),R:H.r(P.Rkg,2),fore:H.r(P.ves.fore.A+P.ves.fore.B,4),S:H.fill('S'),T2:H.fill('T2'),L2:H.fill('L2'),txtLost:H.texts(/펌프 쪽.{0,12}액|잃은|진공펌프.{0,12}액|액이 넘어/),tags,chips:[...document.querySelectorAll('.chip')].filter(e=>H.vis(e)).map(e=>e.textContent.trim().slice(0,80))})})()"""
XP2S = r"""(()=>{const D=window.__dt,H=window.__xh,Q=D.PID2;if(!Q||!Q.svg||Q.root.hidden)return JSON.stringify({hidden:true});const fl=(k)=>Q.flows.filter(f=>f.k===k);const pS=H.pts(fl('S').map(f=>f.el),5);const rc=H.crop('__xc_p2',...H.box(pS,10));
 const st=(k)=>fl(k).map(f=>[f.el.classList.contains('on')?1:0,+(+getComputedStyle(f.el).opacity).toFixed(2),getComputedStyle(f.el).stroke,f.kind]);
 const txt=[...Q.svg.querySelectorAll('text')].map(e=>e.textContent).filter(s=>/잃은|손실 액|펌프 쪽.{0,8}액|진공펌프.{0,8}액/.test(s)).slice(0,10);
 return JSON.stringify({rect:rc,S:{st:st('S'),pts:H.rel(rc,pS)},T2:st('T2'),L2:st('L2'),vals:Object.fromEntries(Object.entries(Q.vals||{}).map(([k,v])=>[k,v.textContent])),txt})})()"""
XSTH = r"""(()=>{const D=window.__dt,H=window.__xh,P=D.PR,FX=D.FX;const hx=Math.max(0,(P.mHeld||0)-(P.mHold0||0));return JSON.stringify({t:+P.t.toFixed(1),flood:H.r(P.flood,3),mFlood:H.r(P.mFlood,4),hx:H.r(hx,4),bed:H.r(P.mFloodBed,4),top:H.r(P.mFloodTop,4),colFull:!!P.colFull,R:H.r(P.Rkg,2),Lmax:P.Lmax==null||!isFinite(P.Lmax)?null:H.r(P.Lmax,1),vdot:H.r(P.vdot,2),
 lv:H.r(FX.floodLv,4),vis:!!(FX.floodLiq&&FX.floodLiq.visible),glow:!!(FX.colGlow&&FX.colGlow.visible),Dcol:D.CUR.Dcol,jOpen:H.r(D.CUR.jOpen,3),VP:D.VLV.P?1:0,hold:Object.keys(D.OP.hold||{}).filter(k=>D.OP.hold[k]),Ps:H.r(P.Pstill,3)})})()"""
# 도면: 컬럼 충전층(범람 액이 차오를 자리)을 따라 고른 점
XP2COL = r"""(()=>{const D=window.__dt,H=window.__xh,Q=D.PID2,P=D.PR,q=D.M.pipe;const T=H.p2();if(!T)return JSON.stringify({hidden:true});const hx=Math.max(0,(P.mHeld||0)-(P.mHold0||0)),bed=P.mFloodBed||1,lv=Math.min(1,hx/bed),yTop=q.packY0+lv*(q.packY1-q.packY0);
 const pts=[];for(const fx of [-0.5,0,0.5]){const a=T.f(q.xCol+fx*q.rCol,q.packY0+0.005),b=T.f(q.xCol+fx*q.rCol,yTop);const n=Math.max(2,Math.ceil(Math.abs(b[1]-a[1])/3));for(let i=0;i<=n;i++)pts.push([a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n])}
 const all=pts.concat([T.f(q.xCol-q.rCol,q.packY1),T.f(q.xCol+q.rCol,q.packY0)]);const rc=H.crop('__xc_p2',...H.box(all,12));
 return JSON.stringify({rect:rc,pts:H.rel(rc,pts),lv:+lv.toFixed(4),flood:H.r(P.flood,3),colCls:Q.dyn.col?Q.dyn.col.getAttribute('class'):null,colInCls:Q.dyn.colIn?Q.dyn.colIn.getAttribute('class'):null})})()"""
XCHG = r"""(()=>{const D=window.__dt,H=window.__xh,M=D.M,P=D.PR,C=D.CUR;const R=M.R,hh=M.hh,A=Math.PI*R*R,Vs=A*hh*2/3+A*(M.Hs-hh)+A*M.ht*2/3;
 return JSON.stringify({H:(document.getElementById('H')||{}).value,HsIn:(document.getElementById('Hs')||{}).value,m0:H.r(P.m0,1),V0:H.r(P.V0*1000,1),h0:H.r(C.H0,4),Hs:H.r(M.Hs,4),topY:H.r(M.topY,4),Vshell:H.r(Vs*1000,1),
  note:((document.getElementById('fillnote')||{}).textContent||'').slice(0,160),warn:H.texts(/용량.{0,6}(초과|넘)|넘칩|과충전|넣을 수 없|투입.{0,6}초과/).slice(0,6),chips:[...document.querySelectorAll('.chip')].filter(e=>H.vis(e)).map(e=>e.textContent.trim().slice(0,80))})})()"""

def real_scenarios():
    """현실성(X) 장면 9개 — 모두 이름이 '현실성'으로 시작한다(--only 현실성)."""
    S = []; rec = BOOT + [["eval", "window.__dt.opSetMode('recipe');1"], ["wait", 1500], ["eval", XH]]
    W, H = 1920, 1080
    # (A) 밸브 조작: 레시피 ③ 초류(6 h)에서 밸브 줄 단추로 닫고 연다 — X26 다시 열기 · X10 · X11 닫힌 밸브 앞(3D · 도면) · X59 도면 다녀오기 · X13 · X1 · X2 · X14 고임과 넘침 · X58 참고
    a = rec + XJUMP(6, 5000) + [tag("a_f0", XSTATE), XVB("F"), ["wait", 8000], tag("a_fc", XSTATE), ["eval", XPOLL_FILL], ["wait", 600], XVB("F"), ["wait", 6000], tag("a_reopen", XGET), ["wait", 2000]]
    a += [XVB("F"), ["wait", 6500], tag("a_x10", XSTATE), Y.V_2D, ["wait", 3000], tag("a_x10_2d", XP2RES), XSHOT("x_a_x10_2d.png", "#__xc_p2"), Y.V_3D, ["wait", 2500], XVB("F"), ["wait", 7000]]
    a += [XVB("P"), ["wait", 6500], tag("a_x11", XSTATE), Y.V_2D, ["wait", 3000], tag("a_x11_2d", XP2RES), XSHOT("x_a_x11_2d.png", "#__xc_p2"), Y.V_3D, ["wait", 2500], XVB("P"), ["wait", 7000]]
    a += [XVB("R"), ["wait", 30000], tag("a_x59_0", XRSNAP), Y.V_2D, ["wait", 3000], tag("a_x59_2d", XRSNAP), Y.V_3D, ["wait", 4000], tag("a_x59_1", XRSNAP), XVB("R"), ["wait", 9000]]
    a += [tag("a_pool0", XSTATE), ["eval", XPOLL_POOL], ["wait", 1000], XVB("R"), XVB("P"), XDL(240), ["until", "(window.__dt.PR.ovKg||0)>1||performance.now()>window.__xdl", 270000], ["wait", 14000],
          tag("a_ovseg", XSEG.replace("['R','P']", "['T2','L2']")), XSHOT("x_a_ov_seg_a.png", "#__xc_seg"), ["wait", 400], XSHOT("x_a_ov_seg_b.png", "#__xc_seg"),   # 넘어가는 액의 3D 색(T2 · L2 화소)
          tag("a_pool", XGET), Y.V_2D, ["wait", 3000], tag("a_ov2d", XP2OV), XSHOT("x_a_ov_2d.png", "#__xc_p2"), Y.V_3D, ["wait", 2000], XVB("R"), XVB("P"), ["wait", 3000]]
    S.append(scen("현실성 밸브 조작", a, W, H))
    # (B) 받는 탱크 가득 참: 초류 컷 입력 150 kg(초류 탱크 69 L ≈ 105 kg보다 큼) — X8 고액위 인터록 · X9 넘침(3D · 색 · 도면) · X7 고액위 가까이의 액면
    b = rec + [XSET("rcpForeKg", 150), ["wait", 1200], tag("b_lad0", XLAD3), XSHOT("x_b0_fore.png", "#__xc_fore")] + XJUMP(6, 3000) + [
        ["eval", "(()=>{const D=window.__dt,P=D.PR,v=P.ves.fore,m=v.A+v.B,rho=m>0?1/((v.A/m)/P.pA.rho+(v.B/m)/P.pB.rho):1500,left=0.955*D.CUR.capF/1000*rho-m;window.__xjt=P.t/3600+Math.max(0,0.9*left/Math.max(1,P.Dkg||0));D.startJump('at',window.__xjt);return window.__xjt})()"],   # 유출 유량으로 어림한 시각의 90 %까지 한 번에 빨리 감기
        ["until", "(()=>{const D=window.__dt,P=D.PR;return !!(P&&!D.TURBO&&(P.t>=window.__xjt*3600-120||P.stopped||P.lah.fore!=null))})()", 1500000], ["wait", 2000], XDL(900),
        ["until", "(()=>{const D=window.__dt,P=D.PR;if(D.TURBO)return false;const v=P.ves.fore,m=v.A+v.B,rho=m>0?1/((v.A/m)/P.pA.rho+(v.B/m)/P.pB.rho):1500,left=0.955*D.CUR.capF/1000*rho-m;if(left<=0||P.lah.fore!=null||P.stopped||performance.now()>window.__xdl)return true;D.startJump('at',P.t/3600+Math.min(2,Math.max(0.05,0.5*left/Math.max(1,P.Dkg||0))));return false})()", 960000],   # 고액위(97 %) 바로 앞(95.5 %)까지 남은 양에 맞춰 줄여 가며 빨리 감기
        ["wait", 4000], tag("b_lad_near", XLAD3), XSHOT("x_b_near_fore_a.png", "#__xc_fore"), ["wait", 700], XSHOT("x_b_near_fore_b.png", "#__xc_fore"),
        Y.V_2D, ["wait", 3000], tag("b_near_2d", XP2TANK), XSHOT("x_b_near_2d.png", "#__xc_p2"), Y.V_3D, ["wait", 2000],   # 도면 기준 그림(고액위 전) — 범례 등 늘 있는 색을 빼고 새로 생긴 표시만 센다
        ["eval", XPOLL_LAH], XDL(300), ["until", "window.__dt.PR.lah.fore!=null||window.__dt.PR.stopped||performance.now()>window.__xdl", 320000], ["wait", 1500],
        tag("b_lad_lah", XLAD3), XSHOT("x_b_lah_fore_a.png", "#__xc_fore"), ["wait", 20000], tag("b_lah10", XSTATE),
        Y.V_2D, ["wait", 3000], tag("b_lah_2d", XP2TANK), XSHOT("x_b_lah_2d.png", "#__xc_p2"), Y.V_3D, ["wait", 2000],
        ["eval", "(()=>{const D=window.__dt;if(!D.VLV.F){const b=document.querySelector('#valves button[data-v=\"F\"]');if(b)b.click();return 'reopen'}return 'open'})()"],   # 인터록이 닫았으면 사용자가 다시 연다(넘침을 보려고)
        XDL(700), ["until", "(()=>{const D=window.__dt,P=D.PR;if(D.TURBO)return false;if((P.spill.fore||0)>0.05||P.stopped||performance.now()>window.__xdl)return true;const v=P.ves.fore,m=v.A+v.B,rho=m>0?1/((v.A/m)/P.pA.rho+(v.B/m)/P.pB.rho):1500,cap=D.CUR.capF/1000*rho;if(m<cap-1.2&&D.VLV.F&&D.VLV.P)D.startJump('at',P.t/3600+0.2);return false})()", 730000],
        ["wait", 2500], tag("b_spill", XSTATE), tag("b_lad_spill", XLAD3), XSHOT("x_b_spill_fore_a.png", "#__xc_fore"), ["wait", 700], XSHOT("x_b_spill_fore_b.png", "#__xc_fore"),
        Y.V_2D, ["wait", 3000], tag("b_spill_2d", XP2TANK), XSHOT("x_b_spill_2d.png", "#__xc_p2"), Y.V_3D, ["wait", 14000], tag("b_spill2", XSTATE), tag("b_log", XGET)]
    S.append(scen("현실성 받는 탱크 가득 참", b, W, H))
    # (C) 끓기 시작 3D · (D) 도면: 레시피, 1.0 h부터 실제 속도로 환류가 자리 잡을 때까지 — X6 · X22 · X24
    done = "(()=>{const D=window.__dt,P=D.PR,F=D.FILL;return !!(F.RD&&F.RD.full&&(P.Rkg||0)>3)||performance.now()>window.__xdl})()"
    S.append(scen("현실성 끓기 시작 3D", rec + XJUMP(1.0, 2500) + [["eval", XPOLL_ON3], XDL(420), ["until", done, 450000], ["wait", 4000], tag("c_log", XGET)], 1440, 900))
    S.append(scen("현실성 끓기 시작 도면", rec + XJUMP(1.0, 2500) + [Y.V_2D, ["wait", 3000], ["eval", XPOLL_ON2], XDL(420), ["until", done, 450000], ["wait", 4000], tag("d_log", XGET)], 1440, 900))
    # (E) 레시피 기본 배치: 0 · 6 · 30 · 50 h 액면(3D 그림 화소 · 도면 도형) · 무게 증가율 · 증기 점 수 · 줄기 굵기, 배치 끝 — X7 · X36 · X40 · X32 · X34 · X19 · X28 · X31
    e = rec + [["wait", 1500], tag("e_lad0", XLAD3), XSHOT("x_e0_fore.png", "#__xc_fore"), XSHOT("x_e0_main.png", "#__xc_main")]
    for hh in (6, 30, 50):
        e += XJUMP(hh, 6000) + [tag(f"e_lad{hh}", XLAD3), XSHOT(f"x_e{hh}_fore_a.png", "#__xc_fore"), XSHOT(f"x_e{hh}_main_a.png", "#__xc_main"), XSHOT(f"x_e{hh}_still_a.png", "#__xc_still"), ["wait", 700],
                                XSHOT(f"x_e{hh}_fore_b.png", "#__xc_fore"), XSHOT(f"x_e{hh}_main_b.png", "#__xc_main"), XSHOT(f"x_e{hh}_still_b.png", "#__xc_still"),
                                tag(f"e_seg{hh}", XSEG), XSHOT(f"x_e{hh}_seg_a.png", "#__xc_seg"), ["wait", 500], XSHOT(f"x_e{hh}_seg_b.png", "#__xc_seg"),
                                tag(f"e_rate{hh}", XRATE), Y.V_2D, ["wait", 3500], tag(f"e_p2_{hh}", XP2LEV), Y.V_3D, ["wait", 2500]]
    e += XJUMP(61.0, 3000) + [XDL(900), ["until", "(()=>{const D=window.__dt,P=D.PR,m=P.ves.main.A+P.ves.main.B;if(D.TURBO)return false;if(P.stopped||m>=288.0||performance.now()>window.__xdl)return true;D.startJump('at',P.t/3600+0.15);return false})()", 960000], ["wait", 3000],
          ["eval", XPOLL_END], XDL(420), ["until", "window.__dt.PR.stopped||performance.now()>window.__xdl", 450000], ["wait", 12000],
          tag("e_end_log", XGET), tag("e_end_3d", XSTATE), tag("e_end_ga", Y.JS_GA), Y.V_2D, ["wait", 3000], tag("e_end_2d", XP2FLOWS), tag("e_end_ga2", Y.JS_GA), Y.V_3D, ["wait", 1500]]
    S.append(scen("현실성 액면 · 배치 끝", e, W, H))
    # (F) 1차 N-Brine 온도 상승(이상 상황 창): 1차 응축 0 — X45 · X4 참고
    f = rec + XJUMP(6, 4000) + [tag("f_0", XSTF), ["eval", "window.__dt.ab('c1hot');1"]] + XJREL(0.33, 5000) + [tag("f_1", XSTF), ["wait", 10000], tag("f_2", XSTF), Y.V_2D, ["wait", 3000], tag("f_2d", XP2FLOWS), Y.V_3D, ["wait", 1500]]
    S.append(scen("현실성 1차 냉매 95도", f, W, H))
    # (G) 유출 관 내경 입력 2 mm(넘침 관 능력 약 13 kg/h) + 이상 상황 '스팀 개도 과다' — X53 한계 초과 · X32 점 수, 이어서 환류 · 유출을 닫아 펌프 쪽 넘침 — X3
    gg = rec + [XSET("DpipeP", 2), ["wait", 1500]] + XJUMP(6, 3000) + [tag("g_0", XSTG), ["eval", "window.__dt.ab('steam');1"]] + XJREL(0.33, 5000) + [tag("g_1", XSTG)] + XJREL(0.27, 4000) + [
         tag("g_2", XSTG), XVB("R"), XVB("P"), XDL(400), ["until", "(window.__dt.PR.pumpLiqKg||0)>0.5||performance.now()>window.__xdl", 420000], ["wait", 12000], tag("g_3", XSTG),
         Y.V_2D, ["wait", 3000], tag("g_3_2d", XP2S), XSHOT("x_g_3_2d.png", "#__xc_p2"), Y.V_3D, ["wait", 1500]]
    S.append(scen("현실성 스팀 과다 · 펌프 쪽 넘침", gg, W, H))
    # (H) 컬럼 범람: CpHf 기본 설비는 계산상 범람하지 않으므로 컬럼 내경 입력 100 mm · 스팀 헤더 160 ℃ · 게이지 100 % · 유출 밸브 닫음(사용자 잡음) — X15
    hh_ = rec + [XSET("Dcol", 100), XSET("Psteam", ""), XSET("Tj", 160), ["wait", 2500]] + XJUMP(1.6, 3000) + [["eval", "window.__dt.steamSet(100,true);1"], XVB("P"), ["wait", 400], XVB("P"), ["wait", 600], tag("h_hold", XSTH)] + XJUMP(2.5, 5000) + [
          tag("h_25", XSTH), Y.V_2D, ["wait", 3000], tag("h_25_2d", XP2COL), XSHOT("x_h_25_2d.png", "#__xc_p2"), Y.V_3D, ["wait", 2500]] + XJUMP(4.0, 5000) + [tag("h_40", XSTH)]
    S.append(scen("현실성 범람", hh_, W, H))
    # (I) 정제기 용량보다 많이 투입(700 kg, 정제기 안 부피 약 398 L ≈ 608 kg) — X21 참고
    S.append(scen("현실성 과충전", rec + [tag("i_0", XCHG), XSET("H", 700), ["wait", 6000], ["until", "!!window.__dt.PR&&!!window.__dt.M", 60000], ["wait", 3000], tag("i_1", XCHG)], W, H))
    return S
# <<< 현실성(X) 장면 끝

# >>> 새 디자인 장면 시작
# ---------- 새 디자인(v132~) 장면: 이름이 '새디자인'으로 시작(--only 새디자인), 옵션과 상관없이 look=design으로 연다(기본 표현 장면은 주소에 look을 붙이지 않음) ----------
# 옮긴 곳: v132 작업 기록(진행.md '공식 검사 프로그램에 옮길 장면 · 판정 줄(제안)' N1 ~ N16)과 그쪽 시험 도구(t20_vapor · t30_liquid · t40_stage4). 판정은 점검_합침.judge_ds.
# 새 디자인 값은 __dt.dsfProbe()로 읽는다(김 vap[구간] = 진하기 d · 목표 tgt · 앞머리 f · 계산 유량 q · 보임 vis / 액 liq[관] = 흐르는 구간 a · 남는 구간 b · want · q · fill, RD · neck · 줄기 · pool · c1 · air / parts / s4 / vortex).
XDS_H = r"""(()=>{const D=window.__dt,X=window.__xd={};
X.r=(v,n)=>v==null||!isFinite(v)?null:+(+v).toFixed(n==null?3:n);
X.calc=()=>{const P=D.PR;return {t:+P.t.toFixed(1),vdot:X.r(P.vdot,3),vpass:X.r(P.vpass,3),c1:P.c1==null?null:X.r(P.c1,4),m2:X.r(P.m2kg,3),lost:X.r(P.lostkg,4),R:X.r(P.Rkg,3),D:X.r(P.Dkg,3),L:X.r(P.Lkg,3),back:X.r(P.backKg,3),cond:X.r(P.condKg,3),fNC:P.fNC==null?null:X.r(P.fNC,4),flood:X.r(P.flood,3),steam:X.r(P.steamKgh,4),Ppump:X.r(P.Ppump,4),stopped:!!P.stopped,lah:P.lah,spill:P.spill,ov:X.r(P.ovKg,3),hC1:X.r(P.hC1,4),spl:X.r(P.splFrac,4),foreKg:X.r(P.ves.fore.A+P.ves.fore.B,3),mHeld:X.r(P.mHeld,4),mHold0:X.r(P.mHold0,4),bed:X.r(P.mFloodBed,4),seal:X.r(P.sealM,4)}};
X.ext=(e)=>!e||!e.a?0:Math.max(0,e.a[1]-e.a[0])+Math.max(0,e.b[1]-e.b[0]);
X.flowA=(e)=>!e||!e.a?0:Math.max(0,e.a[1]-e.a[0]);
X.VK=['head','neck','col','V','bon','tub','T2','C2','S','J','jk'];
X.n3=(v)=>X.VK.map(k=>v[k]?[v[k].q,v[k].tgt]:null);
return D.dsfProbe?1:0})()"""
XDS_PROBE = r"""(()=>{const D=window.__dt,X=window.__xd;const p=D.dsfProbe?D.dsfProbe():null;return JSON.stringify(Object.assign({},p||{},{calc:X.calc(),ds:D.DS?{on:D.DS.on,want:D.DS.want,pick:D.DS.pick,auto:D.DS.auto||null}:null,VLV:Object.fromEntries(['R','P','F','M','J'].map(k=>[k,D.VLV[k]?1:0]))}))})()"""
# 끓기 시작(N1 · N2 · N3 · N8): 0.1 s마다 김 · 액이 처음 보인 공정 시각, 0.5 s마다 증기관 앞머리(지금 장면 VF와 견줌), 1 s마다 김 (계산 유량, 목표 진하기)
XDS_REC_BOIL = r"""(()=>{const D=window.__dt,X=window.__xd;if(window.__xr&&window.__xr.iv)clearInterval(window.__xr.iv);const R=window.__xr={first:{},vs:[],n3:[],k:0};
const LK=['C','R','P','M','F','FL','L2','T2'];
R.iv=setInterval(()=>{const P=D.PR;if(!P||!D.dsfProbe)return;const pr=D.dsfProbe(),v=pr.vap||{},l=pr.liq||{},t=P.t,fs=(k,c)=>{if(c&&R.first[k]==null)R.first[k]=t};
 fs('boil',(P.vdot||0)>1&&!P.stopped);fs('rfx',!!(P.rfx&&(P.rfx.condTot||0)>0));fs('vpTop',P.vpTop);fs('vpCond',P.vpCond);fs('cond',(P.condKg||0)>0.3);fs('Rkg',(P.Rkg||0)>0.3);fs('Dkg',(P.Dkg||0)>0.3);
 for(const k of X.VK)if(v[k])fs('v.'+k,v[k].vis);
 for(const k of LK){const e=l[k];if(e)fs('l.'+k,(e.a[1]>e.a[0])||(e.b[1]>e.b[0]))}
 fs('RD',l.RD&&l.RD.on);fs('filmR',l.film&&l.film.r>0.01);fs('filmC',l.film&&l.film.c>0.01);fs('neck',l.neck&&l.neck.on);fs('mainStream',l.mainStream&&l.mainStream.on);fs('foreStream',l.foreStream&&l.foreStream.on);
 fs('c1film',l.c1&&l.c1.film>0.01);fs('c1str',l.c1&&l.c1.streams);fs('pool',l.pool&&l.pool.y>l.pool.yb+0.002);const pa=pr.parts||{};fs('drops',pa.drops>0);fs('vpDrops',pa.vpDrops>0);fs('bubbles',pa.bubbles>0);fs('domes',pa.domes>0);
 if(R.k%10===0)R.n3.push([+t.toFixed(1),X.n3(v)]);
 if(R.k%5===0){let s=null;try{s=D.vaporStats()}catch(e){}if(s)R.vs.push([+t.toFixed(1),s.headLenV,s.lenV,s.vpTop?1:0,v.V?v.V.f:null])}
 R.k++;},100);return 1})()"""
XDS_GET_BOIL = r"""(()=>{const R=window.__xr;clearInterval(R.iv);return JSON.stringify({first:R.first,vs:R.vs,n3:R.n3,VK:window.__xd.VK})})()"""
# 초류 밸브 닫았다 열기(N10): 0.1 s마다 [화면 s, 보이는 길이 비 P · F · FL, 흐르는 구간 F · FL, F 남는 구간, 초류 밸브]
XDS_REC_F = r"""(()=>{const D=window.__dt,X=window.__xd;if(window.__xf&&window.__xf.iv)clearInterval(window.__xf.iv);const R=window.__xf={s:[]};
R.iv=setInterval(()=>{if(!D.dsfProbe)return;const l=D.dsfProbe().liq||{};R.s.push([+(performance.now()/1000).toFixed(2),X.r(X.ext(l.P),3),X.r(X.ext(l.F),3),X.r(X.ext(l.FL),3),X.r(X.flowA(l.F),3),X.r(X.flowA(l.FL),3),l.F&&l.F.b?l.F.b[0]:null,l.F&&l.F.b?l.F.b[1]:null,D.VLV.F?1:0])},100);return 1})()"""
XDS_GET_F = r"""(()=>{const R=window.__xf;clearInterval(R.iv);return JSON.stringify({s:R.s})})()"""
XDS_RLIQ = r"""(()=>{const D=window.__dt,l=(D.dsfProbe().liq||{}).R||{};return JSON.stringify({a:l.a||null,b:l.b||null,seal:+(D.PR.sealM||0).toFixed(4),VR:D.VLV.R?1:0,style:D.STYLE,ds:D.DS?D.DS.on:null,sealp:(D.dsfProbe().liq||{}).seal||null})})()"""   # v141: 액봉 탐침(X59)
# 환류 · 유출 닫음 95 s(N4 · N12): 0.1 s마다 [화면 s, 공정 s, 계산 액위, 넘침, 그린 고임 비, 계산 고임 비, 배기관 · L2 액 길이, 배기관 · 2차 · 진공 라인 김 보임, 밸브 R · P], 1 s마다 김 (유량, 목표)
XDS_REC_H = r"""(()=>{const D=window.__dt,X=window.__xd;if(window.__xh2&&window.__xh2.iv)clearInterval(window.__xh2.iv);const R=window.__xh2={s:[],n3:[],k:0};
R.iv=setInterval(()=>{const P=D.PR;if(!P||!D.dsfProbe)return;const pr=D.dsfProbe(),v=pr.vap||{},l=pr.liq||{},po=l.pool||{};
 R.s.push([+(performance.now()/1000).toFixed(2),+P.t.toFixed(1),X.r(P.hC1,4),X.r(P.ovKg,3),po.frac==null?null:X.r(po.frac,4),po.calcFrac==null?null:X.r(po.calcFrac,4),X.r(X.ext(l.T2),3),X.r(X.ext(l.L2),3),v.T2&&v.T2.vis?1:0,v.C2&&v.C2.vis?1:0,v.S&&v.S.vis?1:0,D.VLV.R?1:0,D.VLV.P?1:0]);
 if(R.k%10===0)R.n3.push([+P.t.toFixed(1),X.n3(v)]);R.k++;},100);return 1})()"""
XDS_GET_H = r"""(()=>{const R=window.__xh2;clearInterval(R.iv);return JSON.stringify({s:R.s,n3:R.n3})})()"""
XDS_SPL = r"""(()=>{const D=window.__dt;return JSON.stringify({spl:D.PR.splFrac,cp:D.PR.cPipeFrac,hC1:D.PR.hC1,ds:D.dsfProbe().s4.spl,seal:(D.dsfProbe().liq||{}).seal||null})})()"""   # v141: 티 세로 관 액면(X5)
# U자 액봉(v141, Y1 ~ Y6): 0.1 s마다 [화면 s, 공정 s, 넘는 증기, 환류, 계산 액봉 질량, 그림 질량, 응축기 쪽 · 컬럼 쪽 액면, ΔP 머리, 넘침 층 두께 · 앞머리 x, 줄기 앞머리 · 닿을 자리, 들어옴 · 넘침 · 닿음 · 다 참, 데드 레그 채움 · 줄기, 티 액면, ΔP torr, 응축액 관 끝, 분배 줄기, 환류 밸브, 닫힌 밸브 앞 층]
XDS_REC_U = r"""(()=>{const D=window.__dt,X=window.__xd;if(window.__xu&&window.__xu.iv)clearInterval(window.__xu.iv);const R=window.__xu={s:[],geo:null,mSeal:null};const t0=performance.now();
R.iv=setInterval(()=>{const P=D.PR,p=D.dsfProbe(),l=p.liq||{},s=l.seal;if(!s)return;if(!R.geo&&s.geo){R.geo=s.geo;R.mSeal=s.mSeal}const c=l.C||{},rd=l.RD||{};
R.s.push([+((performance.now()-t0)/1000).toFixed(2),X.r(P.t,1),X.r(P.vpass,3),X.r(P.Rkg,3),X.r(P.sealM,4),s.m,s.Yin,s.Yout,s.d,s.ho,s.xh,s.hq,s.sSurf,s.inflow?1:0,s.ovOn?1:0,s.arr?1:0,s.full?1:0,s.pl,s.ps,s.yT,s.dP,c.a?c.a[1]:null,rd.on?1:0,D.VLV.R?1:0,s.yup,s.rho,D.DSF.L&&D.DSF.L.C?X.r(D.DSF.L.C.parts[0].mt.uniforms.uPh.value,4):null])},100);return 1})()"""
XDS_GET_U = r"""(()=>{const R=window.__xu;clearInterval(R.iv);const D=window.__dt;return JSON.stringify({s:R.s,geo:R.geo,mSeal:R.mSeal,holdC:D.CUR.holdC})})()"""
# 스팀을 끈 뒤(v141 Y13): 계산값(증발 · 응축기 통과 · 환류 · 유출 · 스팀 개도) · 화면 흐름 표시(응축기 김 닿음 PR.vpCond · 응축액 관 흐름 FILL.C.want) · 액봉 탐침 · 응축액 관 그린 구간
XDS_SO = r"""(()=>{const D=window.__dt,X=window.__xd,P=D.PR,l=D.dsfProbe().liq||{},c=l.C||{};return JSON.stringify({t:X.r(P.t/3600,2),mv:X.r(D.CUR.jOpen*100,1),V:X.r(P.vdot,3),vp:X.r(P.vpass,3),R:X.r(P.Rkg,3),Dk:X.r(P.Dkg,3),stop:P.stopped?1:0,vc:P.vpCond?1:0,cw:D.FILL.C&&D.FILL.C.want?1:0,C:c.a||null,seal:l.seal||null,held:D.steamHeld?(D.steamHeld()?1:0):null})})()"""
# 티(분배기)의 고인 액(v142 Y15): 티 세로 관을 그린 방향(uv.x 0 · 1 자리의 높이) · 무늬 빠르기 · 응축액 관 줄기 빠르기 · 잠긴 줄기 세기 · 가로 갈래를 지우는 원기둥 반지름
XDS_TEE = r"""(()=>{const D=window.__dt,X=D.DSF,U=X.sU,P=D.PR;if(!U||!U.teeMs)return JSON.stringify({none:1});const ge=U.teeMs.geometry,ps=ge.attributes.position,uv=ge.attributes.uv;let y0=null,y1=null;for(let i=0;i<uv.count;i++){const a=uv.getX(i);if(a<1e-6&&y0==null)y0=ps.getY(i);if(a>1-1e-6&&y1==null)y1=ps.getY(i);}const tu=U.teeMs.material.uniforms,cp=X.L.C.parts[X.L.C.parts.length-1].mt.uniforms;return JSON.stringify({y0,y1,spd:tu.uSpeed.value*(1-tu.uBv.value),cspd:cp.uSpeed.value,pc:tu.uPc.value,isT:tu.uIsT?tu.uIsT.value:null,pspd:X.Ls.P&&X.Ls.P.sp!=null?X.Ls.P.sp:null,rspd:U.un.uSpeed.value*(1-U.un.uBv.value),rsp:X.Ls.R&&X.Ls.R.sp!=null?X.Ls.R.sp:null,ov:((X.pr.liq||{}).seal||{}).ovOn,ys:X.L.C.parts[0].mt.uniforms.uYs?X.L.C.parts[0].mt.uniforms.uYs.value:null,flL:X.L.C.parts[0].mt.uniforms.uFlL?X.L.C.parts[0].mt.uniforms.uFlL.value:null,yT:((X.pr.liq||{}).seal||{}).yT,rt:U.un.uRt?U.un.uRt.value:null,riT:U.RiT,own:tu.uPh!==U.un.uPh,dk:P.Dkg||0,vp:D.VLV.P?1:0,vis:U.teeMs.visible})})()"""
# v142 Y16 둘러보기: 초류를 받는 동안 본류 쪽 막힌 다리(갈림 티 → 닫힌 본류 밸브) — 채움 값 · 그린 구간(관 길이 비) · 밸브 자리
XDS_DL = r"""(()=>{const D=window.__dt,X=D.DSF,S=X.Ls&&X.Ls.M,P=D.PR,L=X.L&&X.L.M,l=(D.dsfProbe().liq||{}).M||{};if(!S||!L||!X.vS||X.vS.M==null)return JSON.stringify({none:1});return JSON.stringify({dl:S.dl!=null?+S.dl.toFixed(4):0,vMr:+(X.vS.M/L.len).toFixed(4),bs:l.bs||null,b:l.b||null,M:D.VLV.M?1:0,F:D.VLV.F!==false?1:0,P:D.VLV.P!==false?1:0,Dk:P.Dkg!=null?+P.Dkg.toFixed(3):null})})()"""
# v142 Y16 둘러보기: 목관 김 띠 확대(가운데 ± 0.09 m) — 목관 김과 겹치는 자리의 김이 아닌 재질(유리 · 액막 · 떨어지는 액)은 끈다(장면 끝에서만)
XDS_VAP_CAM = r"""(()=>{const D=window.__dt,c=D.camera,o=D.orbit,E=D.DSF.V.neck;if(!E)return 'none';const ms=E.parts[0].ms,xc=ms.position.x,yc=ms.position.y,x0=xc-0.09,x1=xc+0.09,sp=(x1-x0)/0.72,cy=yc-0.09*sp;o.target.set(xc,cy,0);c.position.set(xc,cy+0.03*sp,sp*1.35);c.lookAt(xc,cy,0);if(o.update)o.update();D.DS.root.updateMatrixWorld(true);const gb=ms.geometry;if(!gb.boundingBox)gb.computeBoundingBox();const nb=gb.boundingBox.clone().applyMatrix4(ms.matrixWorld).expandByScalar(0.02);let n=0;D.DS.root.traverse(m=>{if(!m.isMesh||!m.material)return;const g=m.geometry;if(!g.boundingBox)g.computeBoundingBox();const b=g.boundingBox.clone().applyMatrix4(m.matrixWorld);if(!b.intersectsBox(nb))return;const u=m.material.uniforms||{};if(!u.uDens){m.material.visible=false;n++;}});window.__xvh=n;return n})()"""
# 잘라 찍을 범위: 목관 김 원통 가운데(반지름 ± 0.5 · 길이 ± 0.35, 위 · 아래 패널 자리는 뺌)
XDS_VAP_PIX = r"""(()=>{const D=window.__dt,H=window.__xh,E=D.DSF.V.neck;if(!E||!H)return JSON.stringify({none:1});const ms=E.parts[0].ms,u=E.parts[0].mt.uniforms,cam=D.camera,rc=D.canvas.getBoundingClientRect(),G=D.DS.root;G.updateMatrixWorld(true);cam.updateMatrixWorld(true);const r=ms.geometry.parameters.radiusTop,L=E.len,xc=ms.position.x,yc=ms.position.y;const pr=(x,y)=>{const v=cam.position.clone().set(x,y,0);v.applyMatrix4(G.matrixWorld);v.project(cam);return [(v.x*0.5+0.5)*rc.width+rc.left,(-v.y*0.5+0.5)*rc.height+rc.top]};const a=pr(xc-0.5*r,yc+0.35*L),b=pr(xc+0.5*r,yc-0.35*L),X0=Math.max(Math.min(a[0],b[0]),rc.left+0.1*rc.width),X1=Math.min(Math.max(a[0],b[0]),rc.right-0.1*rc.width),Y0=Math.max(Math.min(a[1],b[1]),rc.top+0.08*rc.height),Y1=Math.min(Math.max(a[1],b[1]),rc.top+0.78*rc.height);const cr=H.crop('__xc_seg',X0,Y0,X1-X0,Y1-Y0);return JSON.stringify({crop:cr,vis:!!ms.visible,d:+u.uDens.value.toFixed(3),phK:+(u.uPh.value*u.uK.value).toFixed(2),split:!!ms.userData.sideSplit,hid:window.__xvh||0})})()"""
# v142 Y17: 정제기 액 속 김 · 기포 — 계산(내부 · 끓는점 · 증발 · 스팀) · 자켓 김 띠가 있는지 · 김 띠 켜짐 · 기포 수 · 정제기 액(반지름 R · 액면 아래)과 겹친 김 띠
XDS_WARM = r"""(()=>{const D=window.__dt,P=D.PR,X=D.DSF,V=X.V,pt=(X.pr&&X.pr.parts)||{},r=(v,n)=>v==null||!isFinite(v)?null:+(+v).toFixed(n==null?3:n);const S=D.DS.ves.still,lv=S?S.level:null,R=D.M?D.M.R:null,inL=[];for(const k in V){const E=V[k];if(!(E.d>0.003))continue;for(const p of E.parts){const ms=p.ms;if(!ms.visible)continue;const g=ms.geometry;if(!g.boundingBox)g.computeBoundingBox();const b=g.boundingBox.clone().applyMatrix4(ms.matrixWorld);if(R!=null&&lv!=null&&b.min.y<lv-0.01&&b.max.x>-R&&b.min.x<R&&b.max.z>-R&&b.min.z<R&&inL.indexOf(k)<0)inL.push(k)}}return JSON.stringify({t:r(P.t/3600,3),Tm:r(P.Tmean,2),Tb:r(P.Tbub,2),vdot:r(P.vdot,3),steam:r(P.steamKgh,2),J:D.VLV.J?1:0,jk:V.jk?1:0,head:V.head&&V.head.parts[0].ms.visible?1:0,neck:V.neck&&V.neck.parts[0].ms.visible?1:0,bub:pt.bubbles!=null?pt.bubbles:null,dome:pt.domes!=null?pt.domes:null,inL})})()"""
# v142 Y18: 유출 밸브를 연 채 응축이 시작될 때 — 0.5 s마다 [공정 h, 유출 kg/h, U자 액봉 kg, 응축기 통과 kg/h, 유출 밸브, 환류 kg/h]
XDS_REC_SP = r"""(()=>{const D=window.__dt,P=D.PR;window.__xsp={s:[],seal:D.CUR?D.CUR.holdC:null};const r=(v,n)=>v==null||!isFinite(v)?null:+(+v).toFixed(n);window.__xsp.iv=setInterval(()=>{window.__xsp.s.push([r(P.t/3600,4),r(P.Dkg,3),r(P.sealM,4),r(P.vpass,3),D.VLV.P!==false?1:0,r(P.Rkg,3)])},500);return 1})()"""
XDS_GET_SP = r"""(()=>{const R=window.__xsp;clearInterval(R.iv);return JSON.stringify({s:R.s,seal:R.seal})})()"""
# v142 Y19: 밸브 — 이름 있는 밸브마다 상태 · 몸통 원기둥(반지름 ÷ 원뿔 반지름) · 색 재질이 상태와 맞는지, 이름 없는 수동 밸브(배수)의 색, 색 재질의 자체 발광 ÷ 바탕색 밝기
XDS_VLV = r"""(()=>{const D=window.__dt,S=D.DS,M=S.M||{},vo=M.vOpen,vs=M.vShut,L=(c)=>c?0.2126*c.r+0.7152*c.g+0.0722*c.b:0,ky=new Set(),out=[],so=(k)=>k==="J"?(!!D.VLV.J&&!!D.CUR&&D.CUR.jOpen>0&&!(D.PR&&D.PR.stopped)):k==="S"?(!!D.VLV.S&&(!D.PCV||!D.PCV.man||D.PCV.open>0)):!!D.VLV[k];for(const v of S.valves||[]){let cone=0,body=0,bad=0,n=0;v.g.traverse(o=>{if(!o.isMesh)return;ky.add(o);const g=o.geometry,pa=g.parameters||{};if(o.material!==vo&&o.material!==vs)return;n++;if(o.material!==(v.open?vo:vs))bad++;if(g.type==="ConeGeometry")cone=Math.max(cone,pa.radius||0);if(g.type==="CylinderGeometry"&&(pa.height||0)>(pa.radiusTop||0)*2)body=Math.max(body,pa.radiusTop||0)});out.push([v.key,v.open?1:0,(so(v.key)?1:0),n,bad,cone>0?+(body/cone).toFixed(3):null])}let dO=0,dS=0;S.root.traverse(o=>{if(!o.isMesh||ky.has(o))return;if(o.material===vo)dO++;else if(o.material===vs)dS++});return JSON.stringify({v:out,drainOpen:dO,drainShut:dS,eo:vo?+(L(vo.emissive)/Math.max(1e-6,L(vo.color))).toFixed(2):null,es:vs?+(L(vs.emissive)/Math.max(1e-6,L(vs.color))).toFixed(2):null})})()"""
# v142 Y20: 정제기 위 김 — 깔때기(모이는 정도 K · 무늬 자리 끝 = 높이 1일 때 노즐에서의 무늬 자리) · 재질(uFun · 둘레 무늬 결 rad) · 보임
XDS_FUN = r"""(()=>{const D=window.__dt,E=D.DSF.V.head;if(!E)return JSON.stringify({none:1});return JSON.stringify({parts:E.parts.map(p=>{const g=p.ms.geometry,f=g.userData&&g.userData.funnel,u=p.mt.uniforms;return {K:f?f.K:null,top:f?+f.top.toFixed(4):null,vr:f&&f.r1>0?+Math.pow(f.r0/f.r1,2/3).toFixed(2):null,aX:!!g.attributes.aX,fun:u.uFun?u.uFun.value:null,rad:u.uRad.value,vis:p.ms.visible?1:0}}),d:+E.d.toFixed(3)})})()"""
# v143 Y21: 흐름 잇기 — 흐르는 관(C · P · F · FL · M)의 위상 · 무늬 자리 배율 · 시작 X · 빠르기 · 길이, 초류 탱크 줄기(위 끝 굵기 배율 · 시작 X · 위상 · 가속 · 줄기 반지름), 들어오는 관 끝 관 속 액 반지름, 티 기둥
XDS_NET = r"""(()=>{const D=window.__dt,X=D.DSF,L=X.L,r=(v)=>v==null||!isFinite(v)?null:+(+v).toFixed(5),u=(k)=>L&&L[k]&&L[k].parts.length?L[k].parts[0].mt.uniforms:null,ch={};for(const k of ["C","P","F","FL","M"]){const U=u(k);if(!U||!U.uVi)continue;ch[k]={ph:r(U.uPh.value),vi:r(U.uVi.value),x0:r(U.uX0.value),spd:r(U.uSpeed.value),len:r(L[k].len)}}const lp=L&&L.FL?L.FL.parts[L.FL.parts.length-1]:null,rP=lp?lp.Ri*Math.sqrt(Math.max(0,Math.min(1,lp.mt.uniforms.uFill.value))):null,fs=X.rv&&X.rv.fore,fu=fs?fs.mt.uniforms:null;const rv=fs&&fs.ms.visible&&fu.uVi?{k0:r(fu.uK0.value),x0:r(fu.uX0.value),ph:r(fu.uPh.value),vi:r(fu.uVi.value),acc:r(fu.uAcc.value),rS:r(fs.ms.scale.x),rP:r(rP)}:null;const T=X.sU&&X.sU.teeMs?X.sU.teeMs.material.uniforms:null;return JSON.stringify({G:r(X.G),ch,rv,tee:T&&T.uVi?{vi:r(T.uVi.value),x0:r(T.uX0.value),ph:r(T.uPh.value),bv:r(T.uBv.value),phc:r(T.uPhC.value),vip:r(T.uViP.value)}:null,net:X.net||null})})()"""
XDS_U_CAM = r"""(()=>{const D=window.__dt,c=D.camera,o=D.orbit,q=D.DSF.q;const x0=q.xRf-0.16,x1=q.xU1+0.16,sp=(x1-x0)/0.72,cx=(x0+x1)/2,cy=(q.yU+q.ySpl)/2-0.09*sp;o.target.set(cx,cy,0);c.position.set(cx,cy+0.03*sp,sp*1.35);c.lookAt(cx,cy,0);if(o.update)o.update();return 1})()"""
# 멈춘 화면에서 양쪽 다리의 액면 자리(화소)와 잘라 찍을 범위 — 그림(x_ds_useal.png)의 화소로 액면이 수평인지, 계산한 높이에 있는지 본다
XDS_U_PIX = r"""(()=>{const D=window.__dt,H=window.__xh,s=D.dsfProbe().liq.seal,g=s.geo,cam=D.camera,rc=D.canvas.getBoundingClientRect(),G=D.DS.root;G.updateMatrixWorld(true);
const pr=(x,y)=>{const v=cam.position.clone().set(x,y,0);v.applyMatrix4(G.matrixWorld);v.project(cam);return [(v.x*0.5+0.5)*rc.width+rc.left,(-v.y*0.5+0.5)*rc.height+rc.top]};
const a=pr(g.xRf-2.2*g.Ri,g.invIn-0.06),b=pr(g.xU1+2.2*g.Ri,g.yB1+0.05);const cr=H.crop('__xc_seg',Math.min(a[0],b[0]),Math.min(a[1],b[1]),Math.abs(b[0]-a[0]),Math.abs(b[1]-a[1]));const rel=(p)=>H.rel(cr,[p])[0];
return JSON.stringify({m:s.m,Yin:s.Yin,Yout:s.Yout,up:{l:rel(pr(g.xRf-g.Ri,s.Yout)),r:rel(pr(g.xRf+g.Ri,s.Yout))},dn:{l:rel(pr(g.xU1-g.Ri,s.Yin)),r:rel(pr(g.xU1+g.Ri,s.Yin))},px:Math.abs(pr(0,1)[1]-pr(0,0)[1]),crop:cr,paused:/계속|다시|재생/.test(document.getElementById('btnPause').textContent)})})()"""
# 상태가 바뀔 때(N5 · N6 · N7): 끓음 멈춤 · 응축 0 · 김이 처음 보인 · 사라진 화면 시각, 응축액 관이 빈 시각, 1 s마다 김 (유량, 목표)
XDS_REC_V = r"""(()=>{const D=window.__dt,X=window.__xd;if(window.__xv&&window.__xv.iv)clearInterval(window.__xv.iv);const R=window.__xv={first:{},last:{},marks:{},n3:[],k:0};
R.iv=setInterval(()=>{const P=D.PR;if(!P||!D.dsfProbe)return;const pr=D.dsfProbe(),v=pr.vap||{},l=pr.liq||{},now=+(performance.now()/1000).toFixed(2);
 if(((P.vdot||0)<1||P.stopped)&&R.first.noboil==null)R.first.noboil=now;if((P.condKg||0)<0.3&&R.first.nocond==null)R.first.nocond=now;
 for(const k of X.VK){const e=v[k];if(!e)continue;if(e.vis&&R.first[k]==null)R.first[k]=now;if(R.first.noboil!=null&&!e.vis&&R.last[k]==null&&R.first[k]!=null)R.last[k]=now}
 if(R.first.nocond!=null&&R.first.Cempty==null&&X.ext(l.C)<0.02)R.first.Cempty=now;
 if(R.k%10===0)R.n3.push([+P.t.toFixed(1),X.n3(v)]);R.k++;},100);return 1})()"""
XDS_MARK = lambda nm: ["eval", "(()=>{const D=window.__dt;window.__xv.marks[" + json.dumps(nm) + "]={now:+(performance.now()/1000).toFixed(2),vap:D.dsfProbe().vap,calc:window.__xd.calc()};return 1})()"]
XDS_GET_V = r"""(()=>{const R=window.__xv;clearInterval(R.iv);return JSON.stringify({first:R.first,last:R.last,marks:R.marks,n3:R.n3})})()"""
XDS_END = r"""(()=>{const D=window.__dt;const j=(D.DS&&D.DS.valves||[]).find(v=>v.key==='J');return JSON.stringify({stopped:!!D.PR.stopped,why:String(D.PR.why||'').slice(0,60),VLVJ:!!D.VLV.J,jOpen:D.CUR.jOpen,dsJ:j?!!j.open:null,steam:D.PR.steamKgh,ds:D.DS?D.DS.on:null})})()"""
# 받는 탱크 고액위(N15): 0.1 s마다 [화면 s, 공정 s, 초류 kg, 계산 고액위, 그린 고리, 그린 넘침 줄기, 웅덩이, 넘친 양, 초류 밸브]
XDS_REC_L = r"""(()=>{const D=window.__dt,X=window.__xd;if(window.__xl&&window.__xl.iv)clearInterval(window.__xl.iv);const R=window.__xl={s:[]};
R.iv=setInterval(()=>{const P=D.PR;if(!P||!D.dsfProbe)return;const f=((D.dsfProbe().s4||{}).fore)||{};R.s.push([+(performance.now()/1000).toFixed(2),+P.t.toFixed(1),X.r(P.ves.fore.A+P.ves.fore.B,3),P.lah.fore!=null?1:0,f.lah?1:0,f.spill?1:0,X.r(f.pud,4),X.r(P.spill.fore,4),D.VLV.F?1:0])},100);return 1})()"""
XDS_GET_L = r"""(()=>{const R=window.__xl;clearInterval(R.iv);return JSON.stringify({s:R.s})})()"""
# 기본 표현(N16): 표현 상태 · 트렌드 접힘 · 안내 글 · 그래픽 이름
XDS_ST = r"""(()=>{const D=window.__dt,S=D.DS||{};const d=document.getElementById('jumpDone');return JSON.stringify({on:S.on,want:S.want,pick:S.pick,auto:S.auto||null,look:D.LOOK,trend:(document.getElementById('trend')||{classList:{contains:()=>null}}).classList.contains('closed'),sel:(document.getElementById('lookMode')||{}).value||null,hint:(document.getElementById('viewhint')||{}).textContent||'',note:d&&!d.hidden?d.textContent:null,gpu:String(D.GPU_NAME).slice(0,60),probe:!!D.dsfProbe})})()"""

def ds_scenarios():
    """새 디자인 장면 19개(옵션과 상관없이 새 디자인으로 연다)."""
    S = []; rec = BOOT + [["eval", "window.__dt.opSetMode('recipe');1"], ["wait", 1500], ["eval", XDS_H]]
    W, H = 1440, 900   # 그쪽 시험과 같은 창
    def D(name, acts, look="design", w=W, h=H, q="", args=""):
        s = scen(name, acts, w, h, q=q); s["look"] = look
        if args: s["args"] = args
        S.append(s)
    P = lambda t: tag(t, XDS_PROBE)
    # (1) 끓기 시작 1.0 h → 240분(N1 · N2 · N3 · N8)
    D("새디자인 끓기 시작", rec + XJUMP(1.0, 2500) + [["eval", XDS_REC_BOIL], XDL(560), ["until", "window.__dt.PR.t>=240*60||performance.now()>window.__xdl", 600000], tag("ds_boil", XDS_GET_BOIL)])
    # (1b) 승온(v142 Y17): 스팀이 켜진 끓기 전 0.3 h — 정제기 액 속에 김 · 기포가 없다(자켓 안 김 띠를 그리지 않음)
    D("새디자인 승온", rec + XJUMP(0.3, 2500) + [["wait", 3000], tag("ds_warm0", XDS_WARM), ["wait", 4000], tag("ds_warm1", XDS_WARM)])
    # (2) 6 h: 줄기 굵기(N9) → 초류 밸브 닫았다 열기(N10) → 환류 밸브 닫고 도면 다녀오기(N11) → 환류 · 유출 닫음 95 s(N4 · N12)
    v = rec + XJUMP(6, 4000) + [["wait", 4000], P("ds_h6"), tag("ds_tee0", XDS_TEE), tag("ds_dl", XDS_DL), tag("ds_warm6", XDS_WARM), tag("ds_vlv", XDS_VLV), tag("ds_fun", XDS_FUN), tag("ds_net", XDS_NET)]   # v142 Y15 · Y16(본류 쪽 막힌 다리) · Y17(끓는 중 기포) · Y19(밸브) · Y20(정제기 위 김)
    v += [["eval", XDS_REC_F], ["wait", 600], XVB("F"), ["wait", 8000], XVB("F"), ["wait", 2400], ["wait", 2000], tag("ds_f", XDS_GET_F), ["wait", 6000]]
    v += [XVB("R"), ["wait", 8300], tag("ds_r0", XDS_RLIQ), ["click", "#btn3d"], ["wait", 3000], ["click", "#btn3d"], ["wait", 3000], tag("ds_r1", XDS_RLIQ), XVB("R"), ["wait", 9000]]
    v += [["eval", XDS_REC_H], ["wait", 600], XVB("R"), ["wait", 300], XVB("P")]
    for i in range(1, 6): v += [["wait", 15000], tag(f"ds_q{i}", XDS_SPL)] + ([tag("ds_tee1", XDS_TEE)] if i == 1 else [])   # v142 Y15: 유출 밸브를 닫은 뒤
    v += [["wait", 20000], tag("ds_hold", XDS_GET_H), XVB("R"), ["wait", 300], XVB("P"), ["wait", 3000]]
    v += [["eval", XH], ["eval", XDS_VAP_CAM], ["wait", 900], tag("ds_vap", XDS_VAP_PIX), XSHOT("x_ds_vap_a.png", "#__xc_seg"), ["wait", 350], XSHOT("x_ds_vap_b.png", "#__xc_seg")]   # v142 Y16: 목관 김만 남긴 확대 화면 2장(장면 끝 — 재질을 끈다)
    D("새디자인 6 h 밸브", v)
    # (2b) U자 액봉(v141 — Y1 ~ Y6): 끓기 시작 0.94 h부터 0.1 s마다 액봉 탐침 → 다리가 반쯤 찼을 때 멈추고 화면 그림(액면 화소) → 다 차서 넘친 뒤 5 s → 환류 밸브 닫음 8 s → 다시 엶 6 s
    u = rec + [["eval", XH]] + XJUMP(0.94, 1500) + [["eval", XDS_U_CAM], ["eval", XDS_REC_U], XDL(60),
        ["until", "(()=>{const s=(window.__dt.dsfProbe().liq||{}).seal;return !!(s&&s.m>=0.30)||performance.now()>window.__xdl})()", 70000], ["click", "#btnPause"], ["wait", 800], tag("ds_u_pix", XDS_U_PIX), XSHOT("x_ds_useal.png", "#__xc_seg"), ["click", "#btnPause"], XDL(60),
        ["until", "(()=>{const s=(window.__dt.dsfProbe().liq||{}).seal;return !!(s&&s.ovOn&&s.geo&&s.xh<=s.geo.xe+0.03)||performance.now()>window.__xdl})()", 70000], ["wait", 5000], P("ds_u_full"),
        XVB("R"), ["wait", 8000], P("ds_u_close"), XVB("R"), ["wait", 6000], P("ds_u_open"), tag("ds_u", XDS_GET_U)]
    D("새디자인 U자 액봉", u)
    # (2b-2) U자 액봉 — 유출 밸브를 연 채 응축이 시작될 때(v142 Y18): 수동 운전 0.9 h에 유출 · 초류 밸브를 열고 0.5 s마다 45 s(공정 약 0.37 h — U자가 차는 동안 · 다 찬 뒤)
    D("새디자인 U자 액봉 유출 열림", rec + [["eval", "window.__dt.opSetMode('manual');1"], ["wait", 800]] + XJUMP(0.9, 1500) + [["eval", "(()=>{const D=window.__dt;D.setValve('P',true);D.setValve('F',true);return 1})()"], ["eval", XDS_REC_SP], ["wait", 45000], tag("ds_sp", XDS_GET_SP)])
    # (2c) U자 액봉 — 스팀을 끈 뒤(v141 Y13): 6 h에서 스팀 개도를 0 %로 고정 → 10 h(증발이 남아 흐름이 이어짐) → 31 h(증발 1 kg/h 아래 = 화면이 끓지 않는 것으로 그리는 때)
    so = rec + XJUMP(6, 4000) + [["wait", 2000], tag("ds_so_0", XDS_SO), ["eval", "(()=>{const D=window.__dt;D.steamSet(0,true);return 1})()"], ["wait", 1200]]
    so += XJUMP(10, 4000) + [["wait", 1500], tag("ds_so_a", XDS_SO)] + XJUMP(31, 4000) + [["wait", 6000], tag("ds_so_b", XDS_SO)]
    D("새디자인 U자 액봉 스팀 끔", so)
    # (3) 1차 N-Brine 온도 상승(N5): 40 s
    D("새디자인 1차 냉매 95도", rec + XJUMP(6, 4000) + [P("ds_c0"), ["eval", XDS_REC_V], ["eval", "String(window.__dt.ab('c1hot'))"], ["wait", 40000], P("ds_c2"), tag("ds_cv", XDS_GET_V)])
    # (4) 진공 펌프 정지(N6): 15 s(약 7분) · 40 s · 60 s(약 30분) → 되돌리고 40 s
    D("새디자인 진공 펌프 정지", rec + XJUMP(6, 4000) + [["eval", XDS_REC_V], ["eval", "String(window.__dt.ab('pstop'))"], ["wait", 15000], XDS_MARK("7분"), ["wait", 25000], P("ds_p2"), ["wait", 20000], XDS_MARK("30분"),
                                                      ["eval", "String(window.__dt.ab('pstop'))"], ["wait", 40000], XDS_MARK("되돌림 20분"), tag("ds_pv", XDS_GET_V)])
    # (5) 배치 끝(N7): 끝까지 빨리 감기 → 가열 정지 → 3 s · 12 s
    D("새디자인 배치 끝", rec + XJUMP(6, 3000) + [["eval", "String(window.__dt.startJump('end'))"], ["until", "(()=>{const D=window.__dt,P=D.PR;return !!(P&&P.stopped&&!D.TURBO)})()", 1500000], ["eval", XDS_REC_V], ["wait", 3000], tag("ds_e1", XDS_END), ["wait", 9000], XDS_MARK("12 s"), tag("ds_ev", XDS_GET_V)])
    # (6 ~ 11) 이상 상황(N13): 6 h에서 걸고 20 s · 40 s(공정 약 10분 · 20분). 흐름이 그대로인 셋 · 냉매 부족과 환류 둘은 한 장면에서 되돌리고 30 s 뒤 다음 것
    def ab(keys, name):
        a = rec + XJUMP(6, 4000)
        for j, k in enumerate(keys):
            a += [P(f"ds_{k}_p0"), ["eval", f"String(window.__dt.ab('{k}'))"], ["wait", 20000], P(f"ds_{k}_p1"), ["wait", 20000], P(f"ds_{k}_p2")]
            if j < len(keys) - 1: a += [["eval", f"String(window.__dt.ab('{k}'))"], ["wait", 30000]]
        D(name, a)
    ab(["c1cold", "c2hot", "pump", "cwlow"], "새디자인 이상 상황 냉매 · 배기")
    ab(["rhigh", "rlow"], "새디자인 이상 상황 환류")
    ab(["steam"], "새디자인 이상 상황 스팀 과다")
    ab(["leak"], "새디자인 이상 상황 진공 리크")
    ab(["cold"], "새디자인 이상 상황 외기 한파")
    ab(["bare"], "새디자인 이상 상황 단열 손상")
    # (12) 컬럼 범람(N14): 컬럼 내경 100 mm · 스팀 헤더 160 ℃ · 게이지 100 % · 유출 밸브 닫음(현실성 범람 장면과 같은 조작 — 그쪽 제안 장면 '70 mm → 3 h'는 범람비 1.03 ~ 1.05이지만 쌓인 액이 자리의 2 % 아래라 쌓인 액 그림을 볼 수 없었다, 그쪽 4단계 A9b)
    D("새디자인 범람", rec + [XSET("Dcol", 100), XSET("Psteam", ""), XSET("Tj", 160), ["wait", 2500]] + XJUMP(1.6, 3000) + [P("ds_fl0"), ["eval", "window.__dt.steamSet(100,true);1"], XVB("P"), ["wait", 400], XVB("P"), ["wait", 600]]
      + XJUMP(2.5, 5000) + [P("ds_fl1")] + XJUMP(4.0, 5000) + [P("ds_fl2")])
    # (13) 받는 탱크 고액위(N15): 초류 컷 150 kg → 고액위 바로 앞까지 빨리 감기 → 실제 속도로 고액위 · 20 s → (인터록이 닫았으면 다시 엶) → 넘칠 때까지
    D("새디자인 받는 탱크 고액위", rec + [XSET("rcpForeKg", 150), ["wait", 1200]] + XJUMP(6, 3000) + [
        ["eval", "(()=>{const D=window.__dt,P=D.PR,v=P.ves.fore,m=v.A+v.B,rho=m>0?1/((v.A/m)/P.pA.rho+(v.B/m)/P.pB.rho):1500,left=0.955*D.CUR.capF/1000*rho-m;window.__xjt=P.t/3600+Math.max(0,0.9*left/Math.max(1,P.Dkg||0));D.startJump('at',window.__xjt);return window.__xjt})()"],
        ["until", "(()=>{const D=window.__dt,P=D.PR;return !!(P&&!D.TURBO&&(P.t>=window.__xjt*3600-120||P.stopped||P.lah.fore!=null))})()", 1500000], ["wait", 2000], XDL(900),
        ["until", "(()=>{const D=window.__dt,P=D.PR;if(D.TURBO)return false;const v=P.ves.fore,m=v.A+v.B,rho=m>0?1/((v.A/m)/P.pA.rho+(v.B/m)/P.pB.rho):1500,left=0.955*D.CUR.capF/1000*rho-m;if(left<=0||P.lah.fore!=null||P.stopped||performance.now()>window.__xdl)return true;D.startJump('at',P.t/3600+Math.min(2,Math.max(0.05,0.5*left/Math.max(1,P.Dkg||0))));return false})()", 960000],
        ["wait", 3000], ["eval", XDS_REC_L], XDL(300), ["until", "window.__dt.PR.lah.fore!=null||window.__dt.PR.stopped||performance.now()>window.__xdl", 320000], ["wait", 20000], P("ds_l1"),
        ["eval", "(()=>{const D=window.__dt;if(!D.VLV.F){const b=document.querySelector('#valves button[data-v=\"F\"]');if(b)b.click();return 'reopen'}return 'open'})()"],
        XDL(700), ["until", "(()=>{const D=window.__dt,P=D.PR;if(D.TURBO)return false;if((P.spill.fore||0)>0.05||P.stopped||performance.now()>window.__xdl)return true;const v=P.ves.fore,m=v.A+v.B,rho=m>0?1/((v.A/m)/P.pA.rho+(v.B/m)/P.pB.rho):1500,cap=D.CUR.capF/1000*rho;if(m<cap-1.2&&D.VLV.F&&D.VLV.P)D.startJump('at',P.t/3600+0.2);return false})()", 730000],
        ["wait", 4000], P("ds_l2"), tag("ds_lah", XDS_GET_L)])
    # (14 ~ 17) 기본 표현(N16): 주소에 look 없이 연다 — 이 PC의 GPU · 소프트웨어 렌더링 · 화질 '화면 가볍게'(?lq=1) · 느린 화면(초당 20장 아래 5 s 넘게)
    boot = BOOT + [["eval", XDS_H], ["wait", 3000]]
    D("새디자인 기본 표현", boot + [tag("ds_st", XDS_ST), P("ds_def")], look="")
    D("새디자인 기본 표현 소프트웨어 렌더링", boot + [tag("ds_st", XDS_ST)], look="", args="--use-angle=swiftshader --use-gl=angle --disable-gpu-compositing")
    D("새디자인 기본 표현 화면 가볍게", boot + [tag("ds_st", XDS_ST)], look="", q="lq=1")
    D("새디자인 기본 표현 느린 화면", BOOT + [["eval", "window.__dt.opSetMode('recipe');1"], ["wait", 1500], ["eval", XDS_H]] + XJUMP(6, 4000) + [tag("ds_s0", XDS_ST),
        ["eval", "(()=>{window.__xslow=setInterval(()=>{const t=performance.now();while(performance.now()-t<90){}},0);return 1})()"], ["wait", 9000], ["eval", "(()=>{clearInterval(window.__xslow);return 1})()"], ["wait", 1500], tag("ds_s1", XDS_ST)], look="")
    return S
# <<< 새 디자인 장면 끝

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
            ["shot", str(SHOTS / f"전환류_{w}x{h}.png")],
            tag("veq0", Y.JS_VEQ), Y.V_ON, ["wait", 6500], tag("dcsV", JS_DCS), tag("veq", Y.JS_VEQ), ["shot", str(SHOTS / f"전환류_{w}x{h}_진공흐름.png")], Y.V_OFF, ["wait", 1500]]   # v131
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
    S.append(scen("환류 관 2 mm 고임", BOOT + [["eval", "window.__dt.opSetMode('free');1"], ["wait", 1500]] + jump(2.3) + [["wait", 3000], tag("pool0", JS_POOL), SET_DR("2"), ["until", "(window.__dt.PR.hC1||0)>0.01", 240000], ["wait", 20000], tag("pool6", JS_POOL), ["shot", str(SHOTS / "환류관2mm_응축기.png"), "#stage", 2, [380, 30, 260, 260]], SET_DR("17.5"), ["wait", 40000], tag("poolBack", JS_POOL)]))
    S.append(scen("수동 끓기 빨리 감기", BOOT + [["eval", SET_MANUAL], ["wait", 1500]] + jump(1.4) + [tag("tb_jump", JS_TB_HIST)]))
    S.append(scen("수동 끓기 실시간 ×120", BOOT + [["eval", SET_MANUAL], ["wait", 1500]] + jump(1.0) + [["eval", "(()=>{const e=document.getElementById('accel');e.value='120';e.dispatchEvent(new Event('change',{bubbles:true}));return e.value})()"], tag("tb_live", JS_TB_LIVE.replace("__SPAN__", "900"))]))
    S += X.scenarios(scen, tag, BOOT, jump, SHOTS)
    S += Y.scenarios(scen, tag, BOOT, jump, SHOTS)
    S += real_scenarios()   # 현실성(X), 2026-11-22
    S += ds_scenarios()   # 새 디자인(v132~), 2026-11-22
    S += SV.scenarios(scen, tag)   # v138s: 스팀 개도
    return S

# >>> 표현 옵션(--look · --sim) 시작
# v132~: 표현 고르기(--look lite|design, 기본 lite). 장면에 "look"이 있으면 그것("" = 주소에 안 붙임 — 기본 표현 시험), 없으면 --look 값을 주소에 붙인다. v131처럼 look을 모르는 판은 무시한다.
# --sim: 열 빌드 파일(시험 빌드 등). 정적 검사(F2 · F5 · F1 · F3 · M1 …)도 그 파일로 한다. 장면에 "args"가 있으면 크롬 추가 인자(DRIVE_ARGS — 소프트웨어 렌더링 시험)
LOOK_ARG = "lite"
def _xlook_url(url, sc):
    lk = sc.get("look", LOOK_ARG)
    return url + ("&" if "?" in url else "?") + "look=" + lk if lk else url
def _xmeta(a):   # 결과 파일에 남기는 표현 · 빌드(다시 판정하면 지난 기록의 값을 그대로)
    if a.rejudge:
        try: o = json.loads((HERE / f"점검결과_{a.rejudge}.json").read_text(encoding="utf-8"))
        except Exception: o = {}
        return {"look": o.get("look"), "sim": o.get("sim")}
    return {"look": LOOK_ARG, "sim": str(SIM_HTML)}
def _xlook_head(a):
    m = _xmeta(a); lk = m["look"]; nm = {"lite": "가벼움(look=lite)", "design": "새 디자인(look=design)"}
    ds = " — 이름이 '새디자인'으로 시작하는 장면은 옵션과 상관없이 새 디자인(기본 표현 장면은 주소에 look 없이)"
    if a.rejudge: return f"표현: {nm.get(lk, '기록 없음(--look 전의 기록 — v131까지는 가벼움뿐)')}{ds if lk else ''} · 다시 판정한 기록 '{a.rejudge}'" + (f"(장면을 연 빌드 {m['sim']})" if m.get("sim") else "") + f" · 정적 검사 빌드 {SIM_HTML}"
    return f"표현: {nm[lk]}{ds} · 연 빌드 {m['sim']}"
# <<< 표현 옵션(--look · --sim) 끝

def run(sc, url):
    url = _xlook_url(url, sc); os.environ["DRIVE_ARGS"] = sc.get("args") or ""   # v132~: 표현 · 크롬 추가 인자
    f = HERE / ("_act_" + re.sub(r"\W", "_", sc["name"]) + ".json")
    f.write_text(json.dumps(sc["actions"], ensure_ascii=False), encoding="utf-8")
    if sc.get("q"): url = url + ("&" if "?" in url else "?") + sc["q"]
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
cP cp CP UA LMTD NTU dP dT ON OFF OK Kp Ti
TICH TIH WIH PICH SICAH FICH TCV XVH XV Brine PIMS LP LC NBRS LBRS BEM BEU GA MV""".split())   # Kp·Ti = PI 조절 기호(식의 문자처럼 씀)
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
        add("E15", "교반기 = 2-세미 앵커, 바닥 간격 90 mm(CpHf 조건 · GA-071 그림 비례)", str(t.get("Cb")) == "90" and t.get("agType") == "anchor", f"{t.get('agType')} · {t.get('Cb')} mm", "anchor · 90")
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
            dv, ve, v0 = g(sn, "dcsV"), g(sn, "veq"), g(sn, "veq0")
            if dv and ve and v0:   # v131
                add("V8", f"진공 흐름을 켠 3D: 값 상자(구간 압력 3개 포함)끼리 겹침 · 배관 걸림 · 기준점에서 60 px 넘게 떨어짐 · 설비 몸통 · 화살촉 · 뜻 글 가림 — {w}×{h}",
                    not dv["pairs"] and not dv["pipe"] and not dv["far"] and dv["n"] == d["n"] + 3 and not ve["equip"] and not ve["arrows"] and not ve["note"],
                    f"상자 {d['n']} → {dv['n']}개 · 겹침 {dv['pairs'] or '0쌍'} · 관 걸림 {dv['pipe'] or '0개'} · 먼 것 {dv['far'] or '0개'} · 설비 가림 {ve['equip'] or '0개'} · 화살촉 가림 {ve['arrows'] or '0개'} · 뜻 글 가림 {ve['note'] or '0개'} · 화살촉 {ve['nArr']}개", "3개 늘고 모두 0")
                add("V8", f"스팀 게이지 값 상자가 스팀 밸브 바로 옆(30 px 안)이고, 값 상자가 설비 몸통(정면 윤곽 사각형)을 가리지 않음(진공 흐름 끔 · 켬) — {w}×{h}",
                    v0["gd"] is not None and v0["gd"] <= 30 and ve["gd"] is not None and ve["gd"] <= 30 and not v0["equip"],
                    f"게이지–밸브 끔 {v0['gd']} px · 켬 {ve['gd']} px · 끈 상태 설비 가림 {v0['equip'] or '0개'}", "30 px 안 · 0개")
            if w == 1440:
                add("C27", "이름–값 사이 빈칸 > 6 px", not d["bigGap"], d["bigGap"] or "0개", "0개")
                add("A4", "응축액 온도 이름 '하부'", d["hbName"] == "하부", d["hbName"], "하부")
                names = [b[0] for b in d["boxes"]]
                need = ["TICH071 탱크 내부", "TIH075 탑 온도", "TICH071D 응축액 출구"]
                add("C29", "기본 값 상자: 내부·탑·하부 온도 있음, '끓는점' 없음", all(n in names for n in need) and not any("끓는점" in n for n in names), f"{len(names)}개 · 빠진 것 {[n for n in need if n not in names] or '없음'}", "3개 있음 · 끓는점 0")
                if d2: add("C28", "카메라 고정 5초 동안 상자 위치 변화", d["boxes"] == d2["boxes"], "같음" if d["boxes"] == d2["boxes"] else "달라짐", "0 px")
        s2 = g(sn, "state_reflux")
        if s2 and w == 1440:
            add("D13", "냉각수 흐름 그림", s2["cw"] == 0, s2["cw"], "0개")
            f0 = g("현실성 1차 냉매 95도", "f_0")   # v141: 레시피 운전 6 h(정상 운전) 기록. 자유 운전 장면은 승온 개도가 그대로 남아 1차 응축기 능력을 넘는 조건이라 '기본 운전'이 아니다
            if f0 and f0.get("n2") is not None and (f0.get("vdot") or 0) > 0:
                n2r = ((f0.get("n2") or 0) + (f0.get("lostkg") or 0) / f0["vdot"]) * 100
                add("E1", "기본 운전(레시피 6 h) 2차 응축기로 가는 몫", n2r <= 2, f"{n2r:.2f} %(증발 {f0['vdot']} kg/h) · 참고: 자유 운전 2.7 h(스팀 개도 고정 · 증발 {s2.get('vdot')} kg/h)에서는 {s2.get('n2')} %", "≤ 2 %")
            else: add("E1", "기본 운전 2차 응축기로 가는 몫", s2.get("n2") is not None and s2["n2"] <= 2, f"{s2.get('n2')} %", "≤ 2 %")
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
        add("E8", "환류 관을 17.5 mm로 되돌리면 고임이 빠짐", pb["hC1"] < p6["hC1"], f"{p6['hC1']} → {pb['hC1']} m", "줄어듦")
    od = g("수동 끓기 순서", "order")
    if od:
        add("D1", "끓기 시작: 목관 액 점이 증기 점보다 먼저 생김", od["tV"] is not None and (od["tL"] is None or od["tL"] >= od["tV"]), f"증기 점 {round(od['tV'], 1) if od['tV'] is not None else None}분 → 액 점 {round(od['tL'], 1) if od['tL'] is not None else None}분", "증기 먼저")
        add("D30", "목관에 흰 점과 따로 뿌린 파란 방울", od["dripMax"] == 0, f"최대 {od['dripMax']}개", "0개")
        add("D31", "목관 파란 점 ÷ 흰 점(흰 점 3개 이상일 때 최대, 둘 다 정제기 꼭대기 ~ 컬럼 바닥 구간에서 셈 — v128)", od["ratio"] <= 3, f"{od['ratio']}배", "≤ 3배")
        add("D3", "액이 되지 못하고 지워진 증기 점(정제기·목관·컬럼)", od["lost"] == 0, f"{od['lost']}개", "0개")
        if od.get("filmOver") is not None:   # v141: 표본마다 액막 높이 − 응축 전선(충전층 비율). 전: '0.5 이하'(환류가 일찍 오던 때의 어림 한계 — 실 루프 0.55 kg이 차는 동안 예열 전선이 충전층 끝까지 가면 넘는다)
            add("D32", "환류가 위에서 들어오기 전 충전층 액막 높이 ≤ 응축 전선(충전층 비율, 표본마다)", od["filmOver"] <= 0.02, f"액막 최대 {od['filmMax']}(그때 응축 전선 {od.get('filmFront')}) · 전선을 넘은 양 최대 {od['filmOver']}", "액막 − 응축 전선 ≤ 0.02")
        else: add("D32", "환류가 위에서 들어오기 전 충전층 액막 높이(충전층 비율)", od["filmMax"] <= 0.5, f"최대 {od['filmMax']}", "≤ 응축 전선(0.5 이하)")
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
    X.judge(g, add)
    Y.judge(g, add)
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
    ap.add_argument("--look", default="lite", choices=["lite", "design"]); ap.add_argument("--sim", default="")   # v132~: 표현(기본 가벼움) · 열 빌드 파일
    a = ap.parse_args()
    global SIM_HTML, LOOK_ARG
    LOOK_ARG = a.look
    if a.sim: SIM_HTML = pathlib.Path(a.sim).resolve()
    if not a.url and not a.rejudge: a.url = serve_local(); print("로컬 서버:", a.url, "←", SIM_HTML.name, flush=True)
    only = set(x for x in a.only.split(",") if x)
    out = {}
    if a.rejudge: out = json.loads((HERE / f"점검결과_{a.rejudge}.json").read_text(encoding="utf-8"))["raw"]
    for sc in ([] if a.rejudge else build_scenarios()):
        if only and not any(sc["name"].startswith(o) for o in only): continue
        print("▶", sc["name"], flush=True); out[sc["name"]] = run(sc, a.url); print("  ", out[sc["name"]]["sec"], "s", list(out[sc["name"]]["res"].keys()), flush=True)
    R = judge(out)
    SV.judge(lambda s, t: (out.get(s) or {}).get("res", {}).get(t), lambda i, n, ok, v, c: R.append({"id": i, "name": n, "ok": ok, "val": v, "crit": c}))   # v138s
    S, ver = static_checks(); R += S
    R += Y.static(SIM_HTML)
    if a.reg: R += regress_checks(a.reg)
    npass = sum(r["ok"] is True for r in R); nfail = sum(r["ok"] is False for r in R); nref = sum(r["ok"] is None for r in R)
    md = [f"# 자동 점검 결과 {ver or ''} {a.tag}".rstrip(), "", f"통과 {npass} · 실패 {nfail} · 판정 {npass + nfail}항목(참고 {nref}줄 따로)  ({time.strftime('%Y-%m-%d %H:%M')})", "", "| 결과 | ID | 항목 | 잰 값 | 기준 |", "|---|---|---|---|---|"]
    md[2:2] = [_xlook_head(a), ""]   # v132~: 결과 파일 머리에 표현
    for r in R:
        v = r["val"]; v = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
        md.append(f"| {'참고' if r['ok'] is None else '통과' if r['ok'] else '**실패**'} | {r['id']} | {r['name']} | {v.replace('|', '/')[:300]} | {r['crit']} |")
    name = "점검결과" + (("_" + a.tag) if a.tag else "")
    (HERE / (name + ".md")).write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / (name + ".json")).write_text(json.dumps({"ver": ver, **_xmeta(a), "R": R, "raw": out}, ensure_ascii=False, indent=1), encoding="utf-8")   # v132~: 표현 · 빌드도 남김
    print(f"통과 {npass} · 실패 {nfail}")
    for r in R:
        if r["ok"] is False: print("  실패", r["id"], r["name"], "→", str(r["val"])[:200])

if __name__ == "__main__":
    main()
