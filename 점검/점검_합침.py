# -*- coding: utf-8 -*-
"""사내망 v117~v124 합침 확인(v125~) — 점검.py가 불러 쓴다.

사내망 변경내역(정제시뮬레이터_사내망_변경내역_v116-v124.md) 6절의 줄마다 '합친 판에 들어갔는가'를 숫자로 본다.
만든 쪽 코드와 따로 떨어진 확인이어야 하므로 기대값은 변경내역에서 옮겨 적었고(PRESET 등), 식은 여기서 다시 계산한다.
항목 번호 M1~M21은 요구목록.md (M)절, N1~N7은 (N)절(추가 점검 문서와 운전 개념, 2026-11-18)과 같다.
"""
import json, math, re

# ---------- 변경내역에서 옮겨 적은 기대값 ----------
# CpHf 정제 조건(사내망 v120~v123): P&ID PCH-PID-H107 Rev.7 · 장치 조립도 GA-071~073 · PIMS 2차정제 화면
PRESET = {"T": 700, "bottom": "ell", "Hs": 800, "wallMat": "sus", "tw": 8, "tIns": 100, "Tj": 133, "Hpack": 0.3,
          "Dpipe": 83.1, "Lpipe": 4.1, "nElb": 2, "nTee": 0, "nTeeR": 1, "nVg": 0, "nVgl": 0, "DpipeC": 43, "DpipeR": 17.5, "DpipeP": 17.5,
          "UAmode": "area", "A1": 21.71, "A2": 2.0, "capF": 69, "capM": 398, "holdC": 0.45, "Tcw": 50, "Tcw2": -22.6,
          "type": "anchor", "D": 390, "C": 90}
# 추가 점검 문서(설비pnid.pdf, 2026-11-18): 자켓 높이는 사내망 오독(855)을 바로잡은 635, 컬럼은 조립도 H-VP-ME-C-H081-001(태그 칸 C-H071) 값
PRESET_GA = {"Hj": 635, "Dcol": 155.2, "packFill": 26, "pack": "pall25"}
# 운전 개념(사용자 2026-11-18): 환류 4 kg/h 고정, 유출 초류 2 · 본류 6 → 정제기에 약 70 kg 남으면 5, 투입 350 · 초류 30 · 후류 30 kg
PRESET_OP = {"H": 350, "rcpForeKg": 30, "swM": 30, "rcpForeR": 4, "rcpForeD": 2, "rcpMainR": 4, "rcpMainD": 6, "rcpLateKg": 70, "rcpLateD": 5, "rcpTailKg": 30, "rcpMainKg": 0}
TAGS = ["TICH071 탱크 내부", "WIH071 정제기 무게", "TIH074 자켓", "TICH071 스팀 밸브 개도", "TIH075 탑 온도", "PICH071 탱크 압력", "TICH071D 응축액 출구",
        "FICH073 환류", "FICH072 유출", "WIH072 초류 무게", "WIH073 본류 무게"]   # SICAH071 교반은 값 상자에서 빼 둔 설정값(DCS_SKIP)
OLD = ["FIC-072", "FIC-073", "FCV-072", "FCV-073", "유출 FT-H073", "고점 FT-H073", "FT-H073 0", "TIC-H071D 응축액", "(TIC-H071D)", "TI-H075 탑"]   # 옛 번호와 옛 이름표 쓰임. P&ID 표기(FT/FIQC-H073 = 환류 유량계, TE/TIC-H071D, TE/TI-H075)는 설비 설명에 남는다
PID_WORDS = ["80A-CCH-H0709", "80A-CCH-H0701", "15A-CCH-H0704", "15A-CCH-H0710", "15A-CCH-H0703", "15A-CCH-H0706", "50A-CCH-H0702", "P&ID T-H071", "P&ID C-H071", "P&ID E-H071", "P&ID E-H072",
             "P&ID T-H072", "P&ID T-H073", "VP-H093", "PCV-H093", "TCV-H072", "XV-H074", "XV-H077", "MIN. 300 mm"]
KIND_EXPECT = {"Dpipe": "dwg", "DpipeR": "dwg", "DpipeP": "dwg", "DpipeC": "dwg", "T": "dwg", "Hs": "dwg", "Hj": "dwg", "tw": "dwg", "tIns": "dwg", "A1": "dwg", "A2": "dwg", "capF": "dwg", "capM": "dwg",
               "holdC": "dwg", "type": "dwg", "Tcw": "meas", "Tcw2": "meas", "pack": "dwg", "D": "est", "C": "est", "Lpipe": "est", "nElb": "est", "nTeeR": "est", "hqMode": "view",
               "rcpLateKg": "op", "rcpLateD": "op", "rcpTailKg": "op"}

# ---------- 페이지 안에서 재는 식 ----------
JS_M1 = r"""(()=>{const D=window.__dt,P=D.PR,p=D.CUR,$=(i)=>document.getElementById(i);
const ids=__IDS__,inp={};for(const i of ids){const e=$(i);inp[i]=e?e.value:null;}
const kinds={};for(const i of __KIDS__){const lb=document.querySelector('label[for="'+i+'"]');kinds[i]=lb?[lb.dataset.kind||null,(lb.dataset.tip||'').length,!!lb.querySelector('.hq')]:null;}
const tags=(D.dcsBox||[]).map(b=>b.n),act=[...document.querySelectorAll('.dcs-tag.act')].map(e=>e.dataset.n);
const tabs=[...document.querySelectorAll('.trend .tt[data-t]')].map(b=>[b.dataset.t,getComputedStyle(b).display==='none'||b.hidden]);
const lg=[...document.querySelectorAll('.trend .graph')].map(g=>[g.querySelector('h2').textContent.trim(),[...g.querySelectorAll('.lg span')].map(s=>s.textContent.trim())]);
const dock=[...document.querySelectorAll('#valves button[data-v]')].map(b=>b.dataset.v+':'+b.textContent.trim());
const S=D.SUBS,rev=S.tdmahf_rev||null,F=D.fn,one=(s)=>[s,s,s],U=p.Ucalc||null,q=D.M.pipe;
return JSON.stringify({inp,kinds,tags,act,app:document.querySelector('.app').className,tabs,lg,dock,
rev:rev?{A:rev.antoine.A,B:rev.antoine.B,C:rev.antoine.C,Tb:rev.Tb,hvap:rev.hvap,Tc:rev.Tc}:null,revTb:rev?F.bubbleT([0,1,0],one(rev),0.1):null,revP85:rev?F.bubbleP([0,1,0],one(rev),85):null,cpP85:F.bubbleP([0,1,0],one(S.cphf),85),rhoCp:S.cphf.rho,
subOpts:[...$('subA').options].map(o=>o.value),types:[...$('type').options].map(o=>o.value),
Lfit:p.Lfit,Dp:p.Dpipe,cnt:{nElb:p.nElb,nTee:p.nTee,nTeeR:p.nTeeR,nVg:p.nVg,nVgl:p.nVgl},Tcw:p.Tcw,Tcw2:p.Tcw2,UA1:p.UA1,UA2:p.UA2,Uc:p.Uc,tcw2n:document.querySelectorAll('#Tcw2').length,
U:U?{hAg:U.hAg,Re:U.Re,Pr:U.Pr}:null,kL:p.kL,Tt:p.T,type:p.type,
look:D.LOOK,dpr:window.devicePixelRatio,hq:$('hqMode')?[...$('hqMode').options].map(o=>o.value):null,hqVal:$('hqMode')?$('hqMode').value:null,
pipe:{yU:q.yU,yRf:q.yRf,xU1:q.xU1,xRf:q.xRf,xSpl:q.xSpl,ySpl:q.ySpl},
Rpipe:(D.PIPES.R||[]).filter(o=>o.geometry&&o.geometry.type==='CylinderGeometry'&&!o.userData.ov).map(o=>[+o.position.x.toFixed(3),+o.position.y.toFixed(3),+o.geometry.parameters.height.toFixed(3)]),
vR:D.VALVE_PARTS.R?[D.VALVE_PARTS.R.tag.position.x,D.VALVE_PARTS.R.tag.position.y]:null,c1:D.C1TUBES,
bs:{tail:!!$('bsTail'),tailV:$('bsTail')?$('bsTail').value:null,foreV:$('bsFore')?$('bsFore').value:null,chargeV:$('bsCharge')?$('bsCharge').value:null},hMin:F.hMin(p),C:p.C,Dimp:p.D,m0:P.m0})})()"""

JS_M2 = r"""(async()=>{const D=window.__dt,P=D.PR,p=D.CUR,$=(i)=>document.getElementById(i),zz=(ms)=>new Promise(r=>setTimeout(r,ms));
const H=P.hist,last=H[H.length-1]||{};
const pre={om:P.omV,y:P.y?[P.y[0],P.y[1]]:null,TbA:p.A.Tb,TbB:p.B.Tb,Tbub:P.Tbub,histKeys:Object.keys(last),Rf:last.Rf,Pd:last.Pd,Tje:last.Tje,tLast:last.t,Rkg:P.Rkg,Dkg:P.Dkg,TjEff:P.TjEff,nh:H.length,t:P.t};
$('btn3d').click();await zz(2500);
const Q=D.PID2,root=Q.root,svg=Q.svg,vd=document.querySelector('.valvedock'),rv=vd.getBoundingClientRect(),rp=root.getBoundingClientRect();
const at=document.elementFromPoint(rv.left+rv.width/2,rv.top+rv.height/2),inDock=!!(at&&at.closest&&at.closest('.valvedock'));
const now={T:P.Tmean,m:P.m,Pst:P.Pstill,Th:P.Thead,R:P.Rkg||0,Dk:P.Dkg||0,V:P.vdot,fore:P.ves.fore.A+P.ves.fore.B,main:P.ves.main.A+P.ves.main.B,Pp:P.Ppump!=null?P.Ppump:P.Pcond,Tcw:p.Tcw,Tcw2:p.Tcw2,jOpen:p.jOpen,Tj:P.TjEff};
await zz(400);const vals={};for(const k in Q.vals)vals[k]=Q.vals[k].textContent;const lbl={};for(const k in (Q.lbl||{}))lbl[k]=Q.lbl[k].textContent;
const flowsOn=[...new Set(Q.flows.filter(f=>f.el.classList.contains('on')).map(f=>f.k))],vkeys=Object.keys(Q.valves),hint=$('viewhint').textContent;
const vb0=svg.getAttribute('viewBox'),r=svg.getBoundingClientRect();root.dispatchEvent(new WheelEvent('wheel',{deltaY:-100,clientX:r.left+r.width/2,clientY:r.top+r.height/2,bubbles:true,cancelable:true}));await zz(250);const vb1=svg.getAttribute('viewBox');
root.dispatchEvent(new MouseEvent('dblclick',{bubbles:true}));await zz(250);const vb2=svg.getAttribute('viewBox');
const f0=!!D.VLV.M,gM=Q.valves.M[0];gM.dispatchEvent(new MouseEvent('click',{bubbles:true}));await zz(500);const f1=!!D.VLV.M,cls1=gM.getAttribute('class');gM.dispatchEvent(new MouseEvent('click',{bubbles:true}));await zz(500);const f2=!!D.VLV.M;
return JSON.stringify({pre,style:D.STYLE,pidHidden:root.hidden,isoHidden:$('isoView').hidden,canvasVis:getComputedStyle(D.canvas).visibility,inDock,pidBottom:rp.bottom,dockTop:rv.top,vals,lbl,now,flowsOn,vkeys,tog:[f0,f1,f2],cls1,vb:[vb0,vb1,vb2],hint,els:svg.querySelectorAll('*').length,btn:$('btn3d').textContent.trim()})})()"""

JS_LQ = r"""(()=>{const D=window.__dt,e=document.getElementById('hqMode');return JSON.stringify({look:D.LOOK,dpr:window.devicePixelRatio,hqVal:e?e.value:null})})()"""

JS_END = r"""(()=>{const D=window.__dt,P=D.PR,p=D.CUR,R=P.rcp||{},H=P.hist,st=P.rcpStages||[];const tOf=(n)=>{const s=st.find(x=>x.st===n);return s?s.t:null;};const t3=tOf(3),t4=tOf(4);
const avg=(a,b,k)=>{const w=H.filter(r=>r.t>=a&&r.t<=b&&r[k]!=null);return w.length?w.reduce((x,r)=>x+r[k],0)/w.length:null;};
const lateOp=(P.ops||[]).find(o=>o.text.indexOf('유출')>=0&&o.text.indexOf('아래)')>=0),tL=lateOp?lateOp.t:null,tE=P.t;
return JSON.stringify({stopped:!!P.stopped,why:P.why||'',t:P.t/3600,m:P.m,m0:P.m0,h:P.h,fore:P.ves.fore.A+P.ves.fore.B,main:P.ves.main.A+P.ves.main.B,rho:P.mix.rho,C:p.C,Dimp:p.D,T:p.T,type:p.type,head:p.head,st:R.st,
late:!!R.late,lateAt:R.lateAt,dT:R.dT,rT:R.rT,hMin:D.fn.hMin(p),stages:st.map(x=>[x.st,+(x.t/3600).toFixed(2)]),tLate:tL!=null?tL/3600:null,
Rfore:t3!=null&&t4!=null?avg(t3+3600,t4,'Rf'):null,Dfore:t3!=null&&t4!=null?avg(t3+3600,t4,'Pd'):null,Rmain:t4!=null&&tL!=null?avg(t4+4*3600,tL,'Rf'):null,Dmain:t4!=null&&tL!=null?avg(t4+4*3600,tL,'Pd'):null,Dlate:tL!=null?avg(tL+2*3600,tE-600,'Pd'):null,Rlate:tL!=null?avg(tL+2*3600,tE-600,'Rf'):null,
mvFore:t3!=null&&t4!=null?avg(t3+3600,t4,'mv'):null,mvMain:t4!=null&&tL!=null?avg(t4+4*3600,tL,'mv'):null,Tfore:t3!=null&&t4!=null?avg(t3+3600,t4,'T'):null,Tmain:t4!=null&&tL!=null?avg(t4+4*3600,tL,'T'):null,ThFore:t3!=null&&t4!=null?avg(t3+3600,t4,'Th'):null,ThMain:t4!=null&&tL!=null?avg(t4+4*3600,tL,'Th'):null,T1main:t4!=null&&tL!=null?avg(t4+4*3600,tL,'T1'):null,TjeFore:t3!=null&&t4!=null?avg(t3+3600,t4,'Tje'):null,TjeMain:t4!=null&&tL!=null?avg(t4+4*3600,tL,'Tje'):null,
ops:(P.ops||[]).filter(o=>o.text.indexOf('레시피')>=0).map(o=>(o.t/3600).toFixed(2)+'h '+o.text),warn:P.rcpWarn||'',
foreA:P.ves.fore.A,mainA:P.ves.main.A,xS:P.x&&P.x.length>1?P.x[0]/Math.max(1e-12,P.x[0]+P.x[1]):null,MWA:p.A&&p.A.MW,MWB:p.B&&p.B.MW,wA0:parseFloat((document.getElementById('wA')||{}).value),wC0:parseFloat((document.getElementById('wC')||{}).value),aA:parseFloat((document.getElementById('aA')||{}).value),Nst:p.Nst})})()"""

JS_P2OV = r"""(()=>{const P=window.__dt.PID2,svg=P&&P.svg;if(!svg)return JSON.stringify({err:'도면 없음'});
const segs=[];for(const p of svg.querySelectorAll('path')){const cls=p.getAttribute('class')||'';if(!/p2-(pipe|eq-line|brine)/.test(cls))continue;
  const d=p.getAttribute('d')||'';const pts=[];d.replace(/([ML])\s*(-?[\d.]+)[ ,]+(-?[\d.]+)/g,(m,c,x,y)=>{pts.push([c,+x,+y]);return m});
  for(let i=1;i<pts.length;i++)if(pts[i][0]==='L')segs.push({cls,a:[pts[i-1][1],pts[i-1][2]],b:[pts[i][1],pts[i][2]]});}
const hit=(r,s)=>{const x0=r.x+r.pad,x1=r.x+r.w-r.pad,y0=r.y+r.pad,y1=r.y+r.h-r.pad;const [ax,ay]=s.a,[bx,by]=s.b;
  if(Math.abs(ax-bx)<1e-6)return ax>x0&&ax<x1&&Math.max(Math.min(ay,by),y0)<Math.min(Math.max(ay,by),y1);
  if(Math.abs(ay-by)<1e-6)return ay>y0&&ay<y1&&Math.max(Math.min(ax,bx),x0)<Math.min(Math.max(ax,bx),x1);
  const n=40;for(let i=0;i<=n;i++){const x=ax+(bx-ax)*i/n,y=ay+(by-ay)*i/n;if(x>x0&&x<x1&&y>y0&&y<y1)return true}return false};
const items=[];
for(const t of svg.querySelectorAll('text')){if(t.closest('.p2-val'))continue;const b=t.getBBox();if(!b.width)continue;items.push({k:'글 '+t.textContent.trim().slice(0,28),x:b.x,y:b.y,w:b.width,h:b.height,pad:Math.min(6,b.height*0.18)})}
for(const g of svg.querySelectorAll('g.p2-val')){const r=g.querySelector('rect');if(!r)continue;const s0=svg.getCTM().inverse().multiply(g.getCTM());const b=r.getBBox();items.push({k:'상자 '+(g.textContent||'').trim().slice(0,24),x:s0.a*b.x+s0.e,y:s0.d*b.y+s0.f,w:b.width*s0.a,h:b.height*s0.d,pad:4})}
const cross=[];for(const it of items){const hs=segs.filter(s=>hit(it,s));if(hs.length)cross.push(it.k+' ← '+[...new Set(hs.map(s=>s.cls.replace('p2-','')))].join(','))}
const overlap=[];for(let i=0;i<items.length;i++)for(let j=i+1;j<items.length;j++){const a=items[i],b=items[j];const w=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x),h=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);if(w>6&&h>6)overlap.push(a.k+' × '+b.k)}
return JSON.stringify({segs:segs.length,items:items.length,cross,overlap})})()"""

JS_OP = r"""(()=>{const q=(e)=>{if(!e)return null;const r=e.getBoundingClientRect();return [Math.round(r.left),Math.round(r.top),Math.round(r.right),Math.round(r.bottom)]};
const op=document.getElementById('opPanel'),w=document.querySelector('.op-warn');
return JSON.stringify({op:q(op),closed:op?op.classList.contains('closed'):null,sel:q(document.getElementById('lblMode')),dock:q(document.querySelector('.valvedock')),warnH:w?Math.round(w.getBoundingClientRect().height):0,warn:w?w.textContent.trim():''})})()"""

def jumpS(h):   # 배치가 먼저 끝나면(가열 정지) 거기서 멈춘다
    return [["eval", f"window.__dt.startJump('at',{h});1"],
            ["until", f"(()=>{{const D=window.__dt,P=D.PR;return !!(P&&!D.TURBO&&(P.t>={h}*3600-120||P.stopped))}})()", 1500000], ["wait", 1500]]

def scenarios(scen, tag, BOOT, jump, SHOTS):
    js1 = JS_M1.replace("__IDS__", json.dumps(list(PRESET) + list(PRESET_GA) + list(PRESET_OP))).replace("__KIDS__", json.dumps(list(KIND_EXPECT)))
    rec = BOOT + [["eval", "window.__dt.opSetMode('recipe');1"], ["wait", 1500]]
    S = [scen("합침 첫 화면", BOOT + [tag("m1", js1), ["shot", str(SHOTS / "합침_첫화면.png")]]),
         scen("합침 2D 도면", rec + jump(3) + [["wait", 3000], ["shot", str(SHOTS / "합침_3D_3h.png")], ["shot", str(SHOTS / "합침_3D_환류U_응축기.png"), "#stage", 2, [470, 30, 330, 290]],
                                             tag("m2", JS_M2), ["wait", 1500], tag("p2ov", JS_P2OV), ["shot", str(SHOTS / "합침_2D_3h.png")]]),
         scen("합침 화질 가볍게", BOOT + [tag("lq", JS_LQ)], q="lq=1"),
         scen("합침 운전 패널", rec + jump(4) + [["wait", 2000], ["eval", "(()=>{const f=document.querySelector('.op-fold');if(f)f.click();return f?1:0})()"], ["wait", 2500], tag("op", JS_OP), ["shot", str(SHOTS / "합침_운전패널_4h.png")]]),
         scen("합침 배치 끝", rec + jumpS(90) + [tag("end", JS_END)])]
    return S

# ---------- 따로 계산 ----------
def neufeld(Tst):   # 충돌 적분 Ω_v (Neufeld·Janzen·Aziz 1972)
    return 1.16145 * Tst ** -0.14874 + 0.52487 * math.exp(-0.77320 * Tst) + 2.16178 * math.exp(-2.43787 * Tst)
def vol_ell(R, h):   # 2:1 타원 경판(깊이 R/2) + 원통에 든 액 부피
    hh = R / 2; y = min(h, hh)
    return math.pi * R * R * (y - (hh ** 3 - (hh - y) ** 3) / (3 * hh * hh)) + math.pi * R * R * max(0, h - hh)
def num(s):
    m = re.search(r"-?\d+(?:\.\d+)?", s or ""); return float(m.group(0)) if m else None

def judge(g, add):
    d = g("합침 첫 화면", "m1")
    if d:
        bad = [f"{k}={d['inp'].get(k)}(기대 {v})" for k, v in PRESET.items() if (str(d["inp"].get(k)) != str(v) if isinstance(v, str) else d["inp"].get(k) in (None, "") or abs(float(d["inp"][k]) - v) > 1e-9)]
        add("M11", f"CpHf 정제 조건 = P&ID·장치 조립도·PIMS 값(입력 {len(PRESET)}칸, 뒤에 바뀐 값은 N1~N4)", not bad, f"{len(PRESET) - len(bad)}/{len(PRESET)}칸 일치" + (" · 다름 " + ", ".join(bad[:6]) if bad else ""), "모두 일치")
        def diff(exp): return [f"{k}={d['inp'].get(k)}(기대 {v})" for k, v in exp.items() if (str(d["inp"].get(k)) != str(v) if isinstance(v, str) else d["inp"].get(k) in (None, "") or abs(float(d["inp"][k]) - v) > 1e-9)]
        b1 = diff({"Hj": 635}); add("N1", "자켓 높이 635 mm(GA-071: 경판 175 + S.T.L → 덮개판 460. 855는 오독)", not b1, "635" if not b1 else ", ".join(b1), "635")
        b2 = diff({k: v for k, v in PRESET_GA.items() if k != "Hj"}); add("N2", "컬럼 조립도 값: 1인치 폴 링 · 내경 155.2 mm · 충전율 26 %", not b2, "pall25 · 155.2 · 26" if not b2 else ", ".join(b2), "모두 일치")
        b3 = diff(PRESET_OP); bs = d.get("bs") or {}
        add("N4", "기본값: 투입 350 kg · 초류 30 kg · 후류 30 kg, 환류 4 · 유출 2 → 6 → 5 kg/h(정제기 70 kg부터)", not b3 and abs(d["m0"] - 350) < 0.5, f"{len(PRESET_OP) - len(b3)}/{len(PRESET_OP)}칸 일치 · 투입 {d['m0']:.1f} kg" + (" · 다름 " + ", ".join(b3) if b3 else ""), "모두 일치")
        add("N5", "배치 시트에 후류 줄(투입 · 초류 컷 · 본류 컷 · 후류)", bool(bs.get("tail")) and str(bs.get("tailV")) == "30" and str(bs.get("foreV")) == "30" and str(bs.get("chargeV")) == "350", f"후류 칸 {'있음' if bs.get('tail') else '없음'} · 투입 {bs.get('chargeV')} · 초류 {bs.get('foreV')} · 후류 {bs.get('tailV')}", "350 · 30 · 30")
        miss = [t for t in TAGS if t not in d["tags"]]
        add("M2", "값 상자 이름 = PIMS 태그(TICH071·WIH071·TIH074·TIH075·PICH071·TICH071D·FICH073·FICH072·WIH072·WIH073)", not miss and "FICH073 환류" in d["act"], ("모두 있음" if not miss else "없음: " + ", ".join(miss)) + f" · 누르면 조절 표시 {d['act']}", "11개 모두 · 환류 상자에 조절 표시")
        dk = " ".join(d["dock"])
        add("M3", "밸브 줄 냉매 이름 = 1차 N-Brine · 2차 L-Brine", "C1:1차 N-Brine" in dk and "C2:2차 L-Brine" in dk, dk[:160], "N-Brine · L-Brine")
        add("M4", "2차 응축기 냉매 온도 입력칸은 하나, CpHf 조건 1차 50 ℃ · 2차 -22.6 ℃가 계산값에", d["tcw2n"] == 1 and abs(d["Tcw"] - 50) < 1e-9 and abs(d["Tcw2"] + 22.6) < 1e-9, f"입력칸 {d['tcw2n']}개 · 계산 Tcw {d['Tcw']} · Tcw2 {d['Tcw2']}", "1개 · 50 · -22.6")
        c = d["cnt"]; Lf = d["Dp"] * (30 * c["nElb"] + 60 * c["nTee"] + 20 * c["nTeeR"] + 8 * c["nVg"] + 340 * c["nVgl"])
        add("M5", "증기관 부속 상당 길이 = 내경 × (엘보 30 + 티 분기 60 + 티 직진 20 + 게이트 8 + 글로브 340)", abs(d["Lfit"] / Lf - 1) < 1e-6 and c["nTeeR"] == 1, f"시뮬 {d['Lfit']:.4f} m · 따로 {Lf:.4f} m(직진 티 {c['nTeeR']}개)", "같음(직진 티 1개 포함)")
        r = d["rev"]
        if r:
            tb = r["B"] / (r["A"] - math.log10(0.1)) - r["C"]; ratio = 10 ** (r["A"] - r["B"] / (85 + r["C"])) / 10 ** (11.87 - 4597 / (85 + 273.15))
            ok = abs(r["A"] - 11.89) < 1e-9 and abs(r["B"] - 4141) < 1e-9 and abs(d["revTb"] - tb) < 0.05 and abs(d["revP85"] / d["cpP85"] / ratio - 1) < 0.01 and "tdmahf_rev" in d["subOpts"] and "tdmahf" in d["subOpts"]
            add("M6", "비교용 물질 'TDMAHf 검토서 증기압'(A 11.89 · B 4141), 기본 TDMAHf는 그대로", ok, f"0.1 torr 끓는점 {d['revTb']:.2f} ℃(따로 {tb:.2f}) · 85 ℃ 증기압 ÷ CpHf = {d['revP85'] / d['cpP85']:.1f}배(따로 {ratio:.1f})", "식 직접 계산과 같음")
        else: add("M6", "비교용 물질 'TDMAHf 검토서 증기압'", False, "물질 표에 없음", "있음")
        add("M12", "CpHf 밀도 1530 kg/m³(장치 설계 데이터 Sp.Gr 1.532)", abs(d["rhoCp"] - 1530) < 1e-9, f"{d['rhoCp']}", "1530")
        lk = d["look"]; pr = min(d["dpr"], 2)
        add("M8", "화질 기본 = 고화질: 계단 펴기 켜짐 · 화면 배율 = min(기기 배율, 2) (그래픽 카드 유무와 무관)", lk["aa"] and not lk["lq"] and abs(lk["pr"] - pr) < 1e-6 and d["hq"] == ["high", "low"] and d["hqVal"] == "high",
            f"계단 펴기 {lk['aa']} · 배율 {lk['pr']}(기기 {d['dpr']}) · 소프트웨어 렌더링 {lk['sw']} · 입력칸 {d['hq']} = {d['hqVal']}", "켜짐 · 기기 배율 · 입력칸 high/low")
        hid = [t for t, h in d["tabs"] if h]; vis = [t for t, h in d["tabs"] if not h]
        add("M9", "첫 화면 = 그림 중심: 입력 서랍·계기판 닫힘, 트렌드 탭 하나", "nodrawer" in d["app"] and "nodock" in d["app"] and vis == ["g"] and sorted(hid) == ["e", "r", "s"], f"{d['app']} · 보이는 탭 {vis} · 숨긴 탭 {hid}", "nodrawer·nodock · 탭 g만")
        lg = dict((a, b) for a, b in d["lg"]); t = " ".join(lg.get("온도", [])); f = " ".join(lg.get("유량", []))
        add("M10", "트렌드 범례: 온도 = TICH071·TIH075·TICH071D·TIH074, 유량 = FICH073 환류·FICH072 유출", all(x in t for x in ("TICH071 ", "TIH075", "TICH071D", "TIH074")) and "끓는점" not in t and "충전물" not in t and "FICH073" in f and "FICH072" in f and "조성" not in " ".join(lg),
            f"온도 [{t}] · 유량 [{f}]", "PIMS 4계기 · 환류·유출")
        add("N6", "온도 트렌드에 스팀 개도 TICH071_MV(오른쪽 축) — 현장 그래프와 같은 구성", "TICH071_MV" in t, f"범례 [{t}]", "TICH071_MV 있음")
        kb = [f"{k}={v[0] if v else None}(기대 {KIND_EXPECT[k]})" for k, v in d["kinds"].items() if not v or v[0] != KIND_EXPECT[k]]; notip = [k for k, v in d["kinds"].items() if v and v[1] < 10]; nohelp = [k for k in ("nTeeR", "Tcw2", "hqMode") if not (d["kinds"].get(k) and d["kinds"][k][2])]
        add("M14", "입력칸 구분: 도면에서 온 값 '도면', 도면에 없어 넣은 값 '가정'(충전물·교반기 치수·직관 길이·엘보·직진 티), 이유 글과 '?' 설명", not kb and not notip and not nohelp, f"{len(d['kinds']) - len(kb)}/{len(d['kinds'])}칸" + (" · 다름 " + ", ".join(kb) if kb else "") + (" · 이유 없음 " + ",".join(notip) if notip else "") + (" · '?' 없음 " + ",".join(nohelp) if nohelp else ""), "모두 일치 · 이유 있음")
        u = d["U"]
        if u:
            K = u["hAg"] / (u["Re"] ** (2 / 3) * u["Pr"] ** (1 / 3) * d["kL"] / d["Tt"])
            add("M15", "교반기 2-세미 앵커: 선택지에 있고 자켓 쪽 Nu = 0.36·Re^⅔·Pr^⅓(Uhl & Gray)", d["type"] == "anchor" and "anchor" in d["types"] and abs(K - 0.36) < 0.004, f"형식 {d['type']} · 계수 {K:.4f}(Re {u['Re']:.0f} · Pr {u['Pr']:.1f} · h {u['hAg']:.0f} W/m²K)", "0.36 ± 1 %")
        c1 = d["c1"]
        add("M16", "E-H071 그림 = 세로 BEM: 곧은 관 17개 · 관판 2장 · U자 굽힘 0", c1["tubes"] == 17 and c1["sheets"] == 2 and c1["bends"] == 0, f"곧은 관 {c1['tubes']} · 관판 {c1['sheets']} · 굽힘 {c1['bends']}", "17 · 2 · 0")
        q = d["pipe"]; seg = d["Rpipe"]; low = [s for s in seg if abs(s[1] - q["yU"]) < 0.01]; vr = d["vR"]
        okU = abs((q["yRf"] - q["yU"]) - 0.3) < 1e-6 and len(seg) >= 5 and len(low) >= 1 and vr is not None and abs(vr[0] - (q["xU1"] + q["xRf"]) / 2) < 0.12 and abs(vr[1] - q["yU"]) < 0.2 and abs(float(d["inp"]["holdC"]) - 0.45) < 1e-9
        add("M17", "환류 U자 액봉: 바닥 = 환류 노즐 − 300 mm, 관 조각 5개, FCV-H073은 바닥, 실 루프 0.45 kg", okU, f"노즐 − 바닥 {(q['yRf'] - q['yU']) * 1000:.0f} mm · 관 조각 {len(seg)}개(바닥 {len(low)}개) · 밸브 자리 {[round(v, 2) for v in vr] if vr else None} · 바닥 가운데 {round((q['xU1'] + q['xRf']) / 2, 2)}, {round(q['yU'], 2)}", "300 mm · 5개 · 밸브가 바닥")
    o = g("합침 운전 패널", "op")
    if o:
        okp = bool(o.get("op") and o.get("sel") and o.get("dock")) and not o["closed"] and o["warnH"] > 0 and o["sel"][3] <= o["dock"][1] and o["op"][3] <= o["dock"][1]
        add("C1", "운전 패널을 폈을 때(초류 경고 글이 뜬 채) 그 아래 이름표 선택 상자가 밸브 줄을 가리지 않음", okp,
            f"패널 아래 끝 {o['op'][3] if o.get('op') else '–'} · 선택 상자 아래 끝 {o['sel'][3] if o.get('sel') else '–'} · 밸브 줄 위 {o['dock'][1] if o.get('dock') else '–'} px(경고 글 높이 {o['warnH']} px)", "둘 다 밸브 줄 위 · 경고 글 있음")
        add("N7", "스팀 하한 경고 글이 원인을 스팀 밸브 가정값으로 밝힘(운전 설정 탓으로 적지 않음)", "가정" in o["warn"] and "목표가 너무 작음" not in o["warn"], o["warn"][:160], "'가정' 있음 · '목표가 너무 작음' 없음")
    e = g("합침 2D 도면", "m2")
    if e:
        p0 = e["pre"]
        if p0.get("y") and p0.get("om"):
            Tst = (p0["Tbub"] + 273.15) / (1.15 * (p0["y"][0] * (p0["TbA"] + 273.15) + p0["y"][1] * (p0["TbB"] + 273.15))); om = neufeld(Tst)
            add("M7", "증기 점도의 충돌 적분 Ω = Neufeld 식(T* = T/(1.15·T_b)), 1.2 고정이 아님", abs(p0["om"] / om - 1) < 0.01 and abs(p0["om"] - 1.2) > 0.05, f"시뮬 {p0['om']:.4f} · 따로 {om:.4f} (T* {Tst:.3f})", "차 < 1 %")
        hk = p0["histKeys"]
        add("M10", "유량 트렌드 기록: 환류(Rf)·유출(Pd) = 그때의 FICH073·FICH072, TIH074 선 = 실효 자켓 온도", all(k in hk for k in ("Rf", "Pd", "Tje")) and p0["nh"] > 20 and abs((p0["Rf"] or 0) - p0["Rkg"]) < max(0.3, 0.1 * p0["Rkg"]) and abs((p0["Tje"] or 0) - p0["TjEff"]) < 3,
            f"기록 {p0['nh']}점 · 마지막 환류 {p0['Rf']:.2f}(지금 {p0['Rkg']:.2f}) · 유출 {p0['Pd']:.2f}(지금 {p0['Dkg']:.2f}) kg/h · 자켓 {p0['Tje']:.1f}(지금 {p0['TjEff']:.1f}) ℃" if all(k in hk for k in ("Rf", "Pd", "Tje")) else f"기록 칸 {hk}", "기록 있음 · 지금 값과 같음")
        add("M18", "'도면으로 보기' = 2D 도면(예전 아이소 그림 숨김, 3D 캔버스 숨김)", e["style"] == "iso" and not e["pidHidden"] and e["isoHidden"] and e["canvasVis"] == "hidden" and e["els"] > 150 and e["btn"] == "3D로 보기", f"모양 {e['style']} · 2D 숨김 {e['pidHidden']} · 아이소 숨김 {e['isoHidden']} · 캔버스 {e['canvasVis']} · 도면 요소 {e['els']}개 · 단추 '{e['btn']}'", "2D 보임 · 아이소 숨김")
        n = e["now"]; v = e["vals"]; pairs = [("TICH071", n["T"], 0.6), ("WIH071", n["m"], 0.3), ("PICH071", n["Pst"], 0.03), ("TIH075", n["Th"], 0.6), ("FICH073", n["R"], 0.3), ("FICH072", n["Dk"], 0.3), ("vdot", n["V"], 0.5), ("WIH072", n["fore"], 0.3), ("WIH073", n["main"], 0.3), ("Ppump", n["Pp"], 0.02), ("jOpen", n["jOpen"] * 100, 1.0), ("TIH074", n["Tj"], 1.0)]
        off = [f"{k} {v.get(k)} ≠ {x:.2f}" for k, x, tol in pairs if x is not None and (num(v.get(k)) is None or abs(num(v.get(k)) - x) > tol)]; need = ["TICH071", "WIH071", "PICH071", "TIH074", "jOpen", "TIH075", "vdot", "TICH071D", "FICH073", "FICH072", "WIH073", "WIH072", "Ppump"]; missk = [k for k in need if k not in v]
        add("M18", "2D 도면 값 13개 = 그때 계산값(PIMS 태그 이름 + 펌프 쪽 압력)", not off and not missk, (f"{len(need) - len(missk)}/13개" + (" · 없음 " + ",".join(missk) if missk else "") + (" · 다름 " + "; ".join(off[:4]) if off else " · 모두 같음")), "13개 · 같음")
        lb = e["lbl"]
        add("M18", "2D 도면에 냉매 입구 온도(N-Brine · L-Brine)", "50.0" in (lb.get("Tcw") or "") and "-22.6" in (lb.get("Tcw2") or ""), f"{lb.get('Tcw')} / {lb.get('Tcw2')}", "50.0 ℃ · -22.6 ℃")
        add("M18", "2D 도면: 끓는 동안 증기·환류·유출 흐름 점선", all(k in e["flowsOn"] for k in ("V", "C", "R")) , f"켜진 흐름 {e['flowsOn']}", "V·C·R 켜짐")
        ov = g("합침 2D 도면", "p2ov")
        if ov and not ov.get("err"):
            bad = ov["cross"] + ov["overlap"]
            add("M18", "2D 도면: 글·값 상자가 관 선에 걸리거나 서로 겹치지 않음(도면 좌표로 잼)", not bad and ov["items"] >= 30 and ov["segs"] >= 25,
                f"글·상자 {ov['items']}개 · 선 조각 {ov['segs']}개 · 걸림 {len(ov['cross'])}곳 · 겹침 {len(ov['overlap'])}곳" + (" · " + "; ".join(bad[:4]) if bad else ""), "0곳 · 0곳")
        elif ov: add("M18", "2D 도면: 글·값 상자가 관 선에 걸리거나 서로 겹치지 않음(도면 좌표로 잼)", False, ov.get("err"), "0곳 · 0곳")
        t0, t1, t2 = e["tog"]
        add("M18", "2D 도면: 밸브를 누르면 열고 닫힌다(본류 XV-H077)", t1 == (not t0) and t2 == t0 and ("open" in (e["cls1"] or "")) == t1, f"{t0} → {t1} → {t2} · 밸브 그림 '{e['cls1']}' · 밸브 {len(e['vkeys'])}개 {e['vkeys']}", "누를 때마다 바뀜")
        add("M19", "2D 도면이 시간 막대·밸브 줄을 가리지 않는다", bool(e["inDock"]) and e["pidBottom"] <= e["dockTop"] + 1, f"밸브 줄 가운데를 누르면 닿는 것 = {'밸브 줄' if e['inDock'] else '도면'} · 도면 아래 끝 {e['pidBottom']:.0f} ≤ 밸브 줄 위 {e['dockTop']:.0f} px", "밸브 줄 · 도면이 그 위")
        w = [float(x.split()[2]) for x in e["vb"]]
        add("M20", "2D 도면: 휠로 확대, 두 번 누르면 전체", w[1] < 0.9 * w[0] and abs(w[2] - w[0]) < 1 and "확대" in e["hint"], f"보는 폭 {w[0]:.0f} → {w[1]:.0f} → {w[2]:.0f} · 안내 '{e['hint'][:40]}…'", "줄었다가 처음 값")
    l = g("합침 화질 가볍게", "lq")
    if l:
        lk = l["look"]
        add("M8", "화질 '화면 가볍게'(?lq=1): 계단 펴기 꺼짐 · 화면 배율 1", lk["lq"] and not lk["aa"] and abs(lk["pr"] - 1) < 1e-6 and l["hqVal"] == "low", f"계단 펴기 {lk['aa']} · 배율 {lk['pr']} · 입력칸 {l['hqVal']}", "꺼짐 · 1 · low")
    z = g("합침 배치 끝", "end")
    if z:
        hmin = z["C"] + 0.035 * z["Dimp"] if z["type"] == "anchor" else z["C"] + z["Dimp"] / 2 + 0.03 * z["T"]; mi = z["rho"] * vol_ell(z["T"] / 2, hmin)
        add("M21", "가열 정지 액위(앵커 = 가로 막대 윗면): 식 값과 그 액위의 남은 양이 후류 30 kg보다 아래", abs(z["hMin"] - hmin) < 1e-6 and mi < 30 and z["m"] / z["m0"] < 0.12,
            f"액위 {z['hMin'] * 1000:.1f} mm(따로 {hmin * 1000:.1f}) = {mi:.1f} kg · 배치는 {z['m']:.1f} kg(투입의 {z['m'] / z['m0'] * 100:.0f} %)까지 감", "식 같음 · 30 kg 아래 · 투입의 12 % 아래까지")
        f2 = lambda x: "–" if x is None else f"{x:.2f}"
        okF = z["Rfore"] is not None and abs(z["Rfore"] - 4) < 0.2 and z["Rmain"] is not None and abs(z["Rmain"] - 4) < 0.2 and z["Rlate"] is not None and abs(z["Rlate"] - 4) < 0.2
        okD = z["Dmain"] is not None and abs(z["Dmain"] - 6) < 0.4 and z["Dlate"] is not None and abs(z["Dlate"] - 5) < 0.4 and z["late"] and z["lateAt"] is not None and abs(z["lateAt"] - 70) < 1.5
        add("N3", "운전 개념: 환류 4 kg/h 고정(초류·본류), 본류 유출 6 → 정제기 70 kg부터 5 kg/h", okF and okD,
            f"환류 초류 {f2(z['Rfore'])} · 본류 {f2(z['Rmain'])} · 끝 무렵 {f2(z['Rlate'])} kg/h · 유출 본류 {f2(z['Dmain'])} → {f2(z['Dlate'])} kg/h(정제기 {f2(z['lateAt'])} kg에서 바꿈, {f2(z['tLate'])} h)", "환류 4 ± 0.2 · 유출 6 ± 0.4 → 5 ± 0.4 · 70 ± 1.5 kg")
        add("N3", "운전 개념: 초류 유출 2 kg/h(참고 — 스팀 밸브 가정값의 하한 열량이 초류에 필요한 열과 거의 같아, 전환류에서 데워진 액이 식는 동안 설정보다 많다)", None,
            f"초류 유출 평균 {f2(z['Dfore'])} kg/h(설정 2) · 스팀 개도 평균 초류 {f2(z['mvFore'])} % · 본류 {f2(z['mvMain'])} %", "참고(스팀 밸브 식을 현장 스팀 유량·개도로 맞춘 뒤 판정)")
        add("N4", "배치 끝 = 후류: 정제기에 30 kg 남으면 끝, 초류 30 kg, 본류 = 투입 − 초류 − 후류", z["stopped"] and "후류" in z["why"] and abs(z["m"] - 30) < 1.5 and abs(z["fore"] - 30) < 1.0 and abs(z["main"] - (z["m0"] - z["fore"] - z["m"])) < 3,
            f"{z['t']:.1f} h에 끝 · 정제기 {z['m']:.1f} · 초류 {z['fore']:.1f} · 본류 {z['main']:.1f} kg(투입 − 초류 − 후류 = {z['m0'] - z['fore'] - z['m']:.1f}) · 단계 {z['stages']} · 사유 '{z['why'][:30]}'", "30 ± 1.5 kg · 초류 30 ± 1 · 본류 수지 ± 3 kg")
        add("N7", "현장 그래프(2026-03-09 배치)와 견줌(참고): 본류 내부 · 탑 · 응축액 출구 온도, 단계 길이", None,
            f"시뮬 본류 내부 {f2(z['Tmain'])} · 탑 {f2(z['ThMain'])} · 응축액 {f2(z['T1main'])} · 자켓 {f2(z.get('TjeMain'))} ℃ / 현장 약 100 · 86~87 · 46 · 100(화면) ℃ · 시뮬 승온~끝 {z['t']:.0f} h / 현장 약 82 h", "참고(증기압식·탑 온도계 자리·스팀 밸브는 DB로 맞춘다)")

def static(html_path):
    R = []; h = html_path.read_text(encoding="utf-8")
    left = {k: h.count(k) for k in OLD if h.count(k)}
    R.append({"id": "M1", "name": "환류 = FICH073·FCV-H073, 유출 = FICH072·FCV-H072 — 옛 번호(FIC-072·073, FCV-072·073)와 옛 이름표(유출 FT-H073, TIC-H071D 응축액 출구, TI-H075 탑 온도) 0개", "ok": not left and h.count("FICH073") >= 10 and h.count("FICH072") >= 5 and h.count("FCV-H073") >= 5,
              "val": (f"옛 표기 남음 {left}" if left else "옛 표기 0개") + f" · FICH073 {h.count('FICH073')}곳 · FICH072 {h.count('FICH072')}곳 · FCV-H073 {h.count('FCV-H073')}곳 · FCV-H072 {h.count('FCV-H072')}곳", "crit": "옛 표기 0개"})
    miss = [w for w in PID_WORDS if w not in h]
    R.append({"id": "M13", "name": "설비 설명 = P&ID 라인 번호·형식·연결(PCH-PID-H107)", "ok": not miss, "val": f"{len(PID_WORDS) - len(miss)}/{len(PID_WORDS)}개" + (" · 없음 " + ", ".join(miss) if miss else ""), "crit": "모두 있음"})
    a1 = 'anc ? 2 : S.p.type === "pbt" ? 4 : 3' in h; a2 = 'p.type === "anchor" ? 3 : 2' in h and "S.type === 3 ? 2 : 3" in h
    R.append({"id": "M15", "name": "격자 계산(작업자·GPU)의 앵커 날개 = 수직 날개 2개", "ok": a1 and a2, "val": f"작업자 {'있음' if a1 else '없음'} · GPU {'있음' if a2 else '없음'}", "crit": "둘 다 있음"})
    body = re.sub("<script[ >].*?</script>", "", h, flags=re.S); cw = len(re.findall("냉각수", re.sub("/[*].*?[*]/", "", body, flags=re.S)))   # 스크립트(계산 코드·도면 자료)와 스타일 주석을 뺀 화면 글
    R.append({"id": "M3", "name": "화면 글에 '냉각수' 없음(1차 = N-Brine, 2차 = L-Brine)", "ok": cw == 0 and "N-Brine" in body and "L-Brine" in body, "val": f"'냉각수' {cw}곳 · N-Brine {body.count('N-Brine')}곳 · L-Brine {body.count('L-Brine')}곳", "crit": "0곳"})
    return R
