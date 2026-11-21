# -*- coding: utf-8 -*-
"""사내망 v117~v124 합침 확인(v125~) — 점검.py가 불러 쓴다.

사내망 변경내역(정제시뮬레이터_사내망_변경내역_v116-v124.md) 6절의 줄마다 '합친 판에 들어갔는가'를 숫자로 본다.
만든 쪽 코드와 따로 떨어진 확인이어야 하므로 기대값은 변경내역에서 옮겨 적었고(PRESET 등), 식은 여기서 다시 계산한다.
항목 번호 M1~M21은 요구목록.md (M)절, N1~N7은 (N)절(추가 점검 문서와 운전 개념, 2026-11-18), P1~P9는 (P)절(화면 지적 · 후류 정의 · PIMS 태그, 2026-11-19)과 같다.
v131(2026-11-21): V1~V9는 (V)절(진공 흐름 보기 · 2차 응축기 부하 · 스팀 밸브 옆 개도 게이지). 값만이 아니라 화면 그림의 화소 · 가려짐까지 본다.
"""
import json, math, re

# ---------- 변경내역에서 옮겨 적은 기대값 ----------
# CpHf 정제 조건(사내망 v120~v123): P&ID PCH-PID-H107 Rev.7 · 장치 조립도 GA-071~073 · PIMS 2차정제 화면
# v126(사용자 2026-11-19 현장 배관): 증기관 직관 4.1 → 4.7 m(위 3 + 오른쪽 1.2 + 아래 0.5), U자 액봉 0.45 → 0.55 kg(0.6 + 0.3 + 0.6 m × 15A × 1530 kg/m³)
PRESET = {"T": 700, "bottom": "ell", "Hs": 800, "wallMat": "sus", "tw": 8, "tIns": 100, "Tj": 133, "Hpack": 0.3,
          "Dpipe": 83.1, "Lpipe": 4.7, "nElb": 2, "nTee": 0, "nTeeR": 1, "nVg": 0, "nVgl": 0, "DpipeC": 43, "DpipeR": 17.5, "DpipeP": 17.5,
          "UAmode": "area", "A1": 21.71, "A2": 2.0, "capF": 69, "capM": 398, "holdC": 0.55, "Tcw": 50, "Tcw2": -22.6,
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
               "holdC": "dwg", "type": "dwg", "Tcw": "meas", "Tcw2": "meas", "pack": "dwg", "D": "est", "C": "est", "Lpipe": "dwg", "nElb": "dwg", "nTeeR": "est", "hqMode": "view",
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

# v126(2026-11-19): 예열 중 도면 증기 점 · 충전물 예열 색 · 둥근 점 · 진공 라인 색과 범례(P1·P2·P4·P5)
JS_GEO = r"""(()=>{const D=window.__dt,q=D.M.pipe,M=D.M;return JSON.stringify({hh:M.hh,Hs:M.Hs,topY:M.topY,yNz:q.yNz,colBase:q.colBase,colTop:q.colTop,yRf:q.yRf,ySpl:q.ySpl,yC1:q.yC1,yC0:q.yC0,yPipe:q.yPipe,xCol:q.xCol,xC:q.xC,xSpl:q.xSpl,xU1:q.xU1,xRf:q.xRf,yU:q.yU,yDish:q.yDish,packY0:q.packY0,packY1:q.packY1,Hpack:D.CUR.Hpack,rCol:q.rCol,xMn:q.xMn,yValve:q.yValve,tankTop:q.yTopM+q.hdM})})()"""
JS_V6A = r"""(async()=>{const D=window.__dt,P=D.PR,q=D.M.pipe,p=D.CUR,zz=(ms)=>new Promise(r=>setTimeout(r,ms)),b=document.getElementById('btn3d');
await zz(400);const sec=((D.FX&&D.FX.sec)||[]).map(b=>b.visible?[b.material.color.r,b.material.color.g,b.material.color.b].map(x=>+x.toFixed(3)):null);
let pts=0,ptsMap=0,film=0;window.__world.traverse(o=>{if(o.isPoints&&o.material&&o.material.size>=2){pts++;if(o.material.map)ptsMap++;}const g=o.geometry;if(o.isMesh&&o.visible&&g&&g.type==='CylinderGeometry'&&g.parameters.openEnded&&Math.abs(g.parameters.radiusTop-q.rCol*0.86)<1e-6)film++;});
if(/도면/.test(b.textContent))b.click();await zz(2500);
const Q=D.PID2,on=(k)=>Q.flows.filter(f=>f.k===k).map(f=>({on:!!f.on,d:(f.el.getAttribute('d')||'').length>0}));
const front=D.vaporStats().front,yF=q.colBase+front*(q.colTop-q.colBase);
const K=P.Tsec.length,NR=Q.ringRows,hotRows=[...new Set(Q.rings.filter(r=>r.el.classList.contains('hot')).map(r=>r.row))].sort((a,b)=>a-b);
const secHot=P.Tsec.map(T=>T>p.Tamb+2),expRows=[];for(let i=0;i<NR;i++)if(secHot[Math.min(K-1,Math.floor(i*K/NR))])expRows.push(i);
const blue=Q.rings.filter(r=>{const c=r.el.style.fill;if(!c)return false;const m=(c.match(/\d+/g)||[]).map(Number);return m.length>=3&&m[2]>m[0]+30&&m[2]>m[1];}).length;
const cs=getComputedStyle(Q.flows[0].el),s=Q.flows.find(f=>f.k==='S');
const legend=[...Q.svg.querySelectorAll('text')].map(t=>t.textContent).filter(t=>/비응축 가스|^응축액$|^스팀$|^증기$/.test(t));
const keys=[...Q.svg.querySelectorAll('circle.p2-key')].map(c=>c.getAttribute('class'));
const vtop=!!(Q.flows.find(f=>f.k==='V')||{}).on;
if(/3D/.test(b.textContent))b.click();await zz(1500);
return JSON.stringify({t:P.t/3600,boil:P.vdot>1&&!P.stopped,vpTop:!!P.vpTop,pts,ptsMap,film,VS:on('VS'),VN:on('VN'),VC:on('VC'),vcY:Q.vcY,yF,front,hotRows,expRows,blue,dash:cs.strokeDasharray,cap:cs.strokeLinecap,sCls:s?s.el.getAttribute('class'):null,legend,keys,vtop,sec,Tsec:P.Tsec.map(x=>+x.toFixed(1))});})()"""

# v126: 환류 분배기 노즐 두 곳 · 밸브 부품 색 · 스팀 밸브 목 반지름(P3·P6·P7)
JS_V6B = r"""(()=>{const D=window.__dt,F=D.FILL,segs=F.RD?F.RD.segs:[],vis=segs.map(s=>!!(s.ov&&s.ov.visible)),flow=!!(D.ISOFLOW&&D.ISOFLOW.on&&D.ISOFLOW.on.RD);
const out={};for(const k of Object.keys(D.VALVE_PARTS)){const parts=(D.VALVE_PARTS[k].parts||[]).filter(o=>o.isMesh);const mats=new Set(parts.map(o=>o.material.uuid));
 const fr=parts.filter(o=>o.geometry.type==='CylinderGeometry'&&o.geometry.parameters.radiusTop<o.geometry.parameters.radiusBottom*0.9).map(o=>o.geometry.parameters.radiusTop);
 const head=parts.filter(o=>(o.geometry.type==='SphereGeometry'&&o.geometry.parameters.thetaLength<3)||(o.geometry.type==='CylinderGeometry'&&Math.abs(o.geometry.parameters.radiusTop-o.geometry.parameters.radiusBottom)<1e-9)).length;
 out[k]={n:parts.length,mats:mats.size,fr:fr.length?+Math.min(...fr).toFixed(5):null,head};}
const pj=(D.PIPES.J||[]).filter(o=>o.geometry&&o.geometry.type==='CylinderGeometry').map(o=>o.geometry.parameters.radiusTop);
const q=D.M.pipe;let lo=Infinity,hi=-Infinity;for(const o of (D.VALVE_PARTS.M?D.VALVE_PARTS.M.parts:[])){const bb=new THREE.Box3().setFromObject(o);lo=Math.min(lo,bb.min.y);hi=Math.max(hi,bb.max.y);}
const A=D.AGIT||{},L=D.LVOL||{};let aOrd=null,hOrd=null;window.__world.traverse(o=>{if(!o.isMesh)return;if(A.mat&&o.material===A.mat)aOrd=aOrd==null?o.renderOrder:Math.min(aOrd,o.renderOrder);if(A.hull&&o.material===A.hull)hOrd=hOrd==null?o.renderOrder:Math.min(hOrd,o.renderOrder);});
const ag={n:A.n||0,tr:!!(A.mat&&A.mat.transparent),dw:!!(A.mat&&A.mat.depthWrite),col:A.mat?[A.mat.color.r,A.mat.color.g,A.mat.color.b]:null,ord:aOrd,hull:hOrd,vol:L.mesh?{ord:L.mesh.renderOrder,vis:!!L.mesh.visible,Tm:L.u.Tm.value,tLo:L.u.tLo.value,tHi:L.u.tHi.value,op:L.u.uOp.value}:null,style:D.STYLE};
return JSON.stringify({ag,vis,flow,n:segs.length,valves:out,pipeJ:pj.length?+Math.max(...pj).toFixed(5):null,t:D.PR.t/3600,mv:{lo,hi,tankTop:q.yTopM+q.hdM,tee:q.yValve}})})()"""

# v127(2026-11-20): 도면의 환류 분배 구멍 4개와 구멍마다 떨어지는 액 점(Q1)
JS_V7 = r"""(async()=>{const D=window.__dt,zz=(ms)=>new Promise(r=>setTimeout(r,ms)),b=document.getElementById('btn3d');
if(/도면/.test(b.textContent))b.click();await zz(2500);
const Q=D.PID2,G=Q.geo,q=G.q,X=G.X,Y=G.Y;
const holes=[...Q.svg.querySelectorAll('.p2-hole')].map(c=>[+c.getAttribute('cx'),+c.getAttribute('cy'),+c.getAttribute('r')]);
const rd=Q.flows.filter(f=>f.k==='RD').map(f=>{const m=(f.el.getAttribute('d')||'').match(/M([\d.]+) ([\d.]+)L([\d.]+) ([\d.]+)/);return {on:!!f.on,cls:f.el.getAttribute('class'),seg:m?m.slice(1).map(Number):null};});
const col=[Number(X(q.xCol-q.rCol)),Number(X(q.xCol+q.rCol))],yD=Number(Y(q.yDish)),yP=Number(Y(q.packY1)),on3=!!(D.ISOFLOW&&D.ISOFLOW.on&&D.ISOFLOW.on.RD);
const fl=(k)=>Q.flows.filter(f=>f.k===k).map(f=>({on:!!f.on,d:f.el.getAttribute('d')||''})),P=D.PR;
const more={x0:Number(X(0)),VS:fl('VS'),LC:fl('LC'),LN:fl('LN'),LS:fl('LS'),CE:fl('CE'),back:(P.fr&&P.fr.back)||0,onRD:on3,boil:P.vdot>1&&!P.stopped,yB:Number(Y(q.colBase)),sealOn:!!Q.sealOn,sealM:P.sealM||0,holdC:D.CUR.holdC,
 ld:D.c1Load(),cap1:P.cap1,Qv1:P.Qv1,c1:P.c1,ldTxt:Q.vals.C1load?Q.vals.C1load.textContent:null,liqC:Q.liqC,Tm:P.Tmean};
if(/3D/.test(b.textContent))b.click();await zz(1500);
return JSON.stringify({holes,rd,col,yD,yP,on3,more,t:D.PR.t/3600});})()"""

# v128(2026-11-20): 환류 U자 액봉 — 환류 밸브를 닫아도 U자 세 토막은 찬 채, 다시 열면 흐름 표시가 돌아온다(S3)
JS_US = r"""(()=>{const D=window.__dt,f=D.FILL.R,u=D.uSealSpan(f),P=D.PR,rd=D.FILL.RD,pk=(k)=>{const x=D.FILL[k];return x?{head:x.head,tail:x.tail,L:x.Ltot,sV:x.sV==null?null:x.sV,held:!!x.held,out:!!x.out,dr:x.dr?{t:x.dr.t,hk:x.dr.hk}:null,vis:x.segs.filter(s=>s.ov.visible).length,n:x.segs.length,glass:!!(D.PIPES[k]&&D.PIPES[k][0]&&D.PIPES[k][0].material.transparent)}:null};
return JSON.stringify({seal:P.sealM||0,holdC:D.CUR.holdC,mHeldC:P.mHeldC||0,head:f.head,tail:f.tail,L:f.Ltot,us:u,want:!!f.want,held:!!f.held,out:!!f.out,Rkg:P.Rkg||0,Dkg:P.Dkg||0,R:!!D.VLV.R,t:P.t/3600,pR:pk('R'),pM:pk('M'),pP:pk('P'),rd:rd?{head:rd.head,tail:rd.tail,vis:rd.segs.filter(s=>s.ov.visible).length}:null,VLV:Object.assign({},D.VLV)})})()"""
JS_2DFADE = r"""(async()=>{const D=window.__dt,zz=(ms)=>new Promise(r=>setTimeout(r,ms)),b=document.getElementById('btn3d');if(/도면/.test(b.textContent))b.click();await zz(2500);
const Q=D.PID2,fr=Q.flows.find(f=>f.k==='R'),on0=!!fr.on;D.setValve('R',false);await zz(350);const o1=parseFloat(fr.el.style.strokeDashoffset),a1=parseFloat(getComputedStyle(fr.el).opacity),on1=!!fr.on;await zz(300);const o2=parseFloat(fr.el.style.strokeDashoffset),a2=parseFloat(getComputedStyle(fr.el).opacity);
await zz(1200);const a3=parseFloat(getComputedStyle(fr.el).opacity),o3=parseFloat(fr.el.style.strokeDashoffset);await zz(300);const o4=parseFloat(fr.el.style.strokeDashoffset);D.setValve('R',true);if(/3D/.test(b.textContent))b.click();await zz(1200);
return JSON.stringify({on0,on1,o1,o2,o3,o4,a1,a2,a3})})()"""

# v129(2026-11-20): 정제기 열 퍼짐 — 구획 계산(평균과의 온도 차) · '열 퍼짐 강조' 스위치(T1~T4). 가벼운 계산(LUMP)에서만 돈다
JS_ZH = r"""(()=>{const D=window.__dt,Z=D.ZH,I=Z.info||{},P=D.PR,th=Z.th,NR=Z.NR,NZ=Z.NZ;let sv=0,st=0;if(th){for(let k=0;k<NZ;k++)for(let i=0;i<NR;i++){const v=((i+1)*(i+1)-i*i);sv+=v;st+=v*th[k*NR+i];}}
const b=document.getElementById('heatEm'),n=document.getElementById('heatNote'),s=window.__stir?window.__stir():null,u=D.LVOL&&D.LVOL.u,Tj=P.TjEff!=null?P.TjEff:D.CUR.Tj,fin=(x)=>Number.isFinite(x)?x:null;
return JSON.stringify({on:!!Z.on,kind:D.solverKind,t:P.t/3600,rpm:D.CUR.N*60,Tm:P.Tmean,Tj,th95:fin(I.th95),max:fin(I.max),wall:fin(I.wall),center:fin(I.center),top:fin(I.top),bot:fin(I.bot),mean:sv?st/sv:null,dW:Z.dW||0,S:0.31*Math.max(0,Tj-P.Tmean),turn:fin(I.turn),Qin:fin(I.Qin),
 emph:!!Z.emph,pressed:b?b.getAttribute('aria-pressed'):null,note:n&&!n.hidden?n.textContent:null,zEm:u?u.zEm.value:null,zOn:u?u.zOn.value:null,hot:s?s.hot:null,nStir:s?s.n:null})})()"""
JS_RPM = lambda v: "(()=>{const e=document.getElementById('rpm');e.value='%d';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));return 1})()" % v

# ---------- v131: 진공 흐름 · 2차 부하 · 스팀 게이지 ----------
# 계산 상태(PR)와 화면(값 상자 글 · 화살촉 · 뜻 글 · 게이지)을 함께 읽는다. 자리는 #stage 왼쪽 위 기준(화면 그림의 화소와 맞춘다)
JS_VAC = r"""(()=>{const D=window.__dt,P=D.PR,st=D.vacState(),bt=document.getElementById('vacFlow'),nt=document.getElementById('vacNote'),sg=document.getElementById('stage').getBoundingClientRect(),cv=D.canvas,cr=cv.getBoundingClientRect(),cam=D.camera,V=cam.position.constructor,v=new V(),g=D.PIPES.V[0].parent;
const inS=(r)=>r.width>0&&r.height>0&&r.left>=sg.left-1&&r.right<=sg.right+1&&r.top>=sg.top-1&&r.bottom<=sg.bottom+1;
const tags={},tvis={};document.querySelectorAll('.dcs-tag').forEach(e=>{if(e.hidden||!e.dataset.n)return;tags[e.dataset.n]=e.children[1].textContent;const r=e.getBoundingClientRect(),t=document.elementFromPoint(r.left+r.width/2,r.top+Math.min(8,r.height/2));tvis[e.dataset.n]=inS(r)&&!!t&&e.contains(t)});
const arr=D.VAC.arr.map(a=>{v.set(a.g.position.x,a.g.position.y,0);g.localToWorld(v);v.project(cam);const x=(v.x+1)/2*cr.width+cr.left,y=(1-v.y)/2*cr.height+cr.top;v.set(a.g.position.x+a.g.scale.x*0.55,a.g.position.y,0);g.localToWorld(v);v.project(cam);const rx=Math.abs((v.x+1)/2*cr.width+cr.left-x),e=document.elementFromPoint(x,y);
 return {id:a.id,sec:a.sec,on:a.g.visible,k:+(a.g.scale.x/a.s0).toFixed(4),hollow:a.ring.visible,rot:+a.g.rotation.z.toFixed(4),x:+(x-sg.left).toFixed(1),y:+(y-sg.top).toFixed(1),r:+rx.toFixed(1),top:e===cv}});
const Q=D.PID2,iso=D.STYLE==='iso',gon=Q&&Q.vac?Q.vac.g.getAttribute('display')!=='none':false,p2=Q&&Q.vac?{disp:Q.vac.g.getAttribute('display'),
 arr:Q.vac.arr.map(a=>{const on=gon&&a.el.getAttribute('display')!=='none',r=on?a.el.getBoundingClientRect():{left:0,top:0,width:0,height:0,right:0,bottom:0};return {id:a.id,sec:a.sec,on,k:a.k!=null?+a.k.toFixed(4):null,base:a.base,hollow:/ o$/.test(a.el.getAttribute('class')),deg:a.deg,x:+(r.left+r.width/2-sg.left).toFixed(1),y:+(r.top+r.height/2-sg.top).toFixed(1),r:+(Math.max(r.width,r.height)/2).toFixed(1),inS:on?inS(r):false}}),
 vals:Object.fromEntries(['Ptop','Pexit','Pcond','PICH071','Ppump','C1load','C2load','jOpen'].map(k=>[k,Q.vals[k]?Q.vals[k].textContent:null])),
 box:Object.fromEntries(['Ptop','Pexit','Pcond','C2load'].map(k=>{const e=Q.vals[k]&&Q.vals[k].closest('.p2-val');if(!e||(k!=='C2load'&&!gon))return [k,false];return [k,inS(e.getBoundingClientRect())]}))}:null;
const nr=nt&&!nt.hidden?nt.getBoundingClientRect():null,ovl=(a,b)=>Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1,ncs=nt?getComputedStyle(nt):null,
 cover=nr?[...document.querySelectorAll('#hud > *, #opPanel, #batchSheet, #lblModeBox, .dcs-tag')].filter(e=>!e.hidden&&e.offsetParent!==null&&ovl(e.getBoundingClientRect(),nr)).map(e=>e.id||e.dataset.n||e.className):[];
const tank=[...document.querySelectorAll('.dcs-tag')].filter(e=>!e.hidden&&/초류|본류|회수/.test(e.dataset.n||'')&&/압력|PI /.test(e.dataset.n||'')).map(e=>e.dataset.n);
const te=document.getElementById('vacNoteT'),TL=te&&!te.hidden&&nt&&!nt.hidden?te.textContent:null;
return JSON.stringify({t:+(P.t/3600).toFixed(3),iso,on:D.VAC.on,cam:D.camera.position.toArray().map(x=>+x.toFixed(4)),pressed:bt?bt.getAttribute('aria-pressed'):null,note:nt&&!nt.hidden?nt.innerText.replace(/\s+/g,' ').trim():null,noteVis:!!nr&&inS(nr)&&ncs.visibility==='visible'&&+ncs.opacity>0.9&&cover.length===0,noteCover:cover,pump:st.pump,lag:st.lag,tank,tline:TL,stTank:st.tank===undefined?null:st.tank,glOn:!!D.CUR.glOn,gl:P.gl&&P.gl.F&&P.gl.M?{F:P.gl.F.P,M:P.gl.M.P}:null,
raw:{Pstill:P.Pstill,Ptop:P.Ptop,Pexit:P.Pexit,Pcond:P.Pcond,Ppump:P.Ppump,Pseal:P.Pseal||0,vdot:P.vdot,vpass:P.vpass,c1:P.c1,c2:P.c2,Qv1:P.Qv1,Qc2:P.Qc2,cap1:P.cap1,cap2:P.cap2,m2:P.m2kg,lost:P.lostkg||0,nAir:P.nAir,stopped:!!P.stopped,VS:!!D.VLV.S,VV:!!D.VLV.V,Mach:P.Mach},
c1L:D.c1Load(),c2L:D.c2Load(),arr,tags,tvis,p2})})()"""
# 스팀 게이지: 3D 값 상자 안의 막대 · 상태 글 · [자동으로], 도면 게이지, 운전 상태
JS_GA = r"""(()=>{const D=window.__dt,el=document.querySelector('.dcs-tag.gauge'),r=el&&el.querySelector('.dg-r'),a=el&&el.querySelector('.dg-a'),t=el&&el.querySelector('.dg-t'),bb=el&&!el.hidden?el.getBoundingClientRect():null,rb=r&&bb?r.getBoundingClientRect():null,P=D.PID2,G=P&&P.gauge,cr=D.canvas.getBoundingClientRect();
let vx=null;try{const q=D.M.pipe,g=D.PIPES.V[0].parent,v=new D.camera.position.constructor(-(q.Rj||D.M.R)-0.22*D.M.p.T,q.yJin,0);g.localToWorld(v);v.project(D.camera);vx=[(v.x+1)/2*cr.width+cr.left,(1-v.y)/2*cr.height+cr.top]}catch(e){}
const at=rb?document.elementFromPoint(rb.left+rb.width*0.5,rb.top+rb.height/2):null,gr=G?G.g.getBoundingClientRect():null,hr=G?G.g.querySelector('.p2-ghit').getBoundingClientRect():null;
return JSON.stringify({iso:D.STYLE==='iso',el:!!el,txt:el?el.children[1].textContent:null,rv:r?+r.value:null,dis:r?r.disabled:null,mode:t?t.textContent:null,chip:a?!a.hidden:null,held:el?el.classList.contains('held'):null,box:bb?[bb.left,bb.top,bb.width,bb.height]:null,valve:vx,reach:!!at&&at===r,
j:+document.getElementById('jOpen').value,mv:D.CUR.jOpen*100,hold:!!D.OP.hold.J,recipe:!!D.OP.recipe,vdot:D.PR.vdot,lock:D.steamLock(),
g2:G?{cx:+G.th.getAttribute('cx'),w:+G.fill.getAttribute('width'),auto:G.auto.getAttribute('display')!=='none',x0:G.x0,x1:G.x1,num:P.vals.jOpen.textContent,mode:G.mode.textContent,held:G.g.classList.contains('held'),view:P.view?P.view.join(','):null,box:gr?[gr.width,gr.height]:null,hit:hr?[hr.width,hr.height]:null}:null,
pop:(()=>{const g=document.getElementById('vGauge');return !!(g&&!g.hidden)})(),log:(D.PR.ops||[]).slice(-4).map(o=>o.text)})})()"""
JS_GTOUCH = r"""(()=>{const h=document.querySelector('.p2-ghit'),r=h.getBoundingClientRect(),y=r.top+r.height/2,ev=(t,f)=>h.dispatchEvent(new PointerEvent(t,{pointerType:'touch',pointerId:7,isPrimary:true,button:0,buttons:t==='pointerup'?0:1,clientX:r.left+r.width*f,clientY:y,bubbles:true,cancelable:true}));ev('pointerdown',0.3);ev('pointermove',0.5);ev('pointermove',0.8);ev('pointerup',0.8);return JSON.stringify({ok:1})})()"""
# 3D 값 상자가 설비 몸통(정면 윤곽 사각형) · 화살촉을 가리는지, 게이지가 스팀 밸브에서 얼마나 떨어졌는지(JS_DCS에 없는 것)
JS_VEQ = r"""(()=>{const D=window.__dt,M=D.M,q=M.pipe,cam=D.camera,cv=D.canvas,W=cv.clientWidth,H=cv.clientHeight,Rj=q.Rj||M.R,V=cam.position.constructor,v=new V(),g=D.PIPES.V[0].parent;
const pj=(x,y,z)=>{v.set(x,y,z);g.localToWorld(v);v.project(cam);return [(v.x+1)/2*W,(1-v.y)/2*H]};
const bb=(x0,x1,y0,y1)=>{const a=pj(x0,y0,0),b=pj(x1,y1,0);return [Math.min(a[0],b[0]),Math.min(a[1],b[1]),Math.max(a[0],b[0]),Math.max(a[1],b[1])]};
const eq={정제기:bb(-Rj,Rj,M.hh,M.Hs),컬럼:bb(q.xCol-q.rCol,q.xCol+q.rCol,q.colBase,q.colTop),'1차 응축기':bb(q.xC-q.rC,q.xC+q.rC,q.yC1,q.yC0),'2차 응축기':bb(q.x20,q.x21,q.y2c-q.r2,q.y2c+q.r2),'본류 탱크':bb(q.xMn-q.rRM,q.xMn+q.rRM,q.yRvM,q.yTopM),'초류 탱크':bb(q.xF-q.rRF,q.xF+q.rRF,q.yRvF,q.yTopF)};
const B=(D.dcsBox||[]).filter(b=>{const e=[...document.querySelectorAll('.dcs-tag')].find(x=>x.dataset.n===b.n);return e&&!e.hidden});
const equip=[];for(const b of B)for(const k in eq){const r=eq[k],w=Math.min(b.x+b.w,r[2])-Math.max(b.x,r[0]),h=Math.min(b.y+b.h,r[3])-Math.max(b.y,r[1]);if(w>2&&h>2)equip.push(b.n+' ↔ '+k+' '+Math.round(w*h)+'px²')}
const arrows=[];for(const a of D.VAC.arr){if(!a.g.visible)continue;const c=pj(a.g.position.x,a.g.position.y,0),e=pj(a.g.position.x+a.g.scale.x*0.62,a.g.position.y,0),r=Math.abs(e[0]-c[0]);for(const b of B)if(c[0]+r>b.x&&c[0]-r<b.x+b.w&&c[1]+r>b.y&&c[1]-r<b.y+b.h)arrows.push(a.id+' ↔ '+b.n)}
const gz=B.find(b=>/스팀 밸브 개도/.test(b.n)),jv=pj(-Rj-0.22*M.p.T,q.yJin,0),gd=gz?Math.hypot(Math.max(gz.x,Math.min(jv[0],gz.x+gz.w))-jv[0],Math.max(gz.y,Math.min(jv[1],gz.y+gz.h))-jv[1]):null;
const nt=document.getElementById('vacNote'),cr=cv.getBoundingClientRect(),nr=nt&&!nt.hidden?nt.getBoundingClientRect():null,note=[];if(nr)for(const b of B){const w=Math.min(b.x+b.w,nr.right-cr.left)-Math.max(b.x,nr.left-cr.left),h=Math.min(b.y+b.h,nr.bottom-cr.top)-Math.max(b.y,nr.top-cr.top);if(w>1&&h>1)note.push(b.n)}
return JSON.stringify({equip,arrows,note,gd:gd==null?null:+gd.toFixed(1),n:B.length,nArr:D.VAC.arr.filter(a=>a.g.visible).length})})()"""
# 도면: 화살촉이 글 · 값 상자에 걸리는지(JS_P2OV는 관 선과 글 · 상자만 본다)
JS_P2ARR = r"""(()=>{const P=window.__dt.PID2,svg=P.svg,out=[],rs=[],gon=P.vac.g.getAttribute('display')!=='none';
for(const t of svg.querySelectorAll('text')){if(t.closest('.p2-val'))continue;const r=t.getBoundingClientRect();if(r.width)rs.push(['글 '+t.textContent.trim().slice(0,20),r])}
for(const g of svg.querySelectorAll('g.p2-val')){if(!gon&&g.closest('.p2-vacg'))continue;const r=g.querySelector('rect').getBoundingClientRect();if(r.width)rs.push(['상자 '+(g.textContent||'').trim().slice(0,20),r])}
if(gon)for(const a of P.vac.arr){if(a.el.getAttribute('display')==='none')continue;const r=a.el.getBoundingClientRect();for(const [k,q] of rs){const w=Math.min(r.right,q.right)-Math.max(r.left,q.left),h=Math.min(r.bottom,q.bottom)-Math.max(r.top,q.top);if(w>1&&h>1)out.push(a.id+' × '+k)}}
return JSON.stringify({hit:out,n:gon?P.vac.arr.filter(a=>a.el.getAttribute('display')!=='none').length:0})})()"""
V_GL = lambda on: ["eval", "(()=>{const c=document.getElementById('glOn');if(c.checked!==" + ("true" if on else "false") + "){c.checked=" + ("true" if on else "false") + ";c.dispatchEvent(new Event('input',{bubbles:true}));c.dispatchEvent(new Event('change',{bubbles:true}))}return c.checked})()"]   # 유출관 높이로 막힘 계산 켬 · 끔
V_ON = ["eval", "(()=>{const b=document.getElementById('vacFlow');if(b.getAttribute('aria-pressed')!=='true')b.click();return b.getAttribute('aria-pressed')})()"]
V_OFF = ["eval", "(()=>{const b=document.getElementById('vacFlow');if(b.getAttribute('aria-pressed')==='true')b.click();return b.getAttribute('aria-pressed')})()"]
V_2D = ["eval", "(()=>{const b=document.getElementById('btn3d');if(/도면/.test(b.textContent))b.click();return b.textContent})()"]
V_3D = ["eval", "(()=>{const b=document.getElementById('btn3d');if(/3D/.test(b.textContent))b.click();return b.textContent})()"]

def png_rows(path):
    """표준 라이브러리만 쓰는 PNG 읽기(8비트 RGB · RGBA, 인터레이스 없음) — 화면 그림에 화살촉 색이 실제로 찍혔는지 볼 때 쓴다"""
    import struct, zlib
    b = open(path, "rb").read()
    if b[:8] != b"\x89PNG\r\n\x1a\n": raise ValueError("PNG 아님")
    i = 8; w = h = bpp = None; idat = []
    while i < len(b):
        n, typ = struct.unpack(">I4s", b[i:i + 8]); d = b[i + 8:i + 8 + n]; i += 12 + n
        if typ == b"IHDR":
            w, h, bit, col, _, _, inter = struct.unpack(">IIBBBBB", d)
            if bit != 8 or inter != 0 or col not in (2, 6): raise ValueError(f"PNG 형식 {bit}/{col}/{inter}")
            bpp = 3 if col == 2 else 4
        elif typ == b"IDAT": idat.append(d)
        elif typ == b"IEND": break
    raw = zlib.decompress(b"".join(idat)); st = w * bpp; rows = []; prev = bytearray(st); p = 0
    for _ in range(h):
        f = raw[p]; cur = bytearray(raw[p + 1:p + 1 + st]); p += 1 + st
        if f == 1:
            for x in range(bpp, st): cur[x] = (cur[x] + cur[x - bpp]) & 255
        elif f == 2:
            for x in range(st): cur[x] = (cur[x] + prev[x]) & 255
        elif f == 3:
            for x in range(st): cur[x] = (cur[x] + (((cur[x - bpp] if x >= bpp else 0) + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(st):
                a = cur[x - bpp] if x >= bpp else 0; bb = prev[x]; c = prev[x - bpp] if x >= bpp else 0; pa = abs(bb - c); pb = abs(a - c); pc = abs(a + bb - 2 * c)
                cur[x] = (cur[x] + (a if pa <= pb and pa <= pc else bb if pb <= pc else c)) & 255
        rows.append(cur); prev = cur
    return w, h, bpp, rows

def violet_px(img, x, y, r, iso):
    """(x, y) 둘레의 화살촉 색(보라) 화소 수. 그림은 #stage를 4 px 여백과 함께 찍은 것이라 자리에 4를 더한다.
    3D 화살촉은 화면에 (217, 202, 252)로 찍히고(증기 흰 점 · 균압 라인의 옅은 보라 점과 다른 색), 도면 화살촉은 #b79cff — 빈 화살촉의 가는 선은 바탕과 섞인 색까지 센다"""
    w, h, bpp, rows = img; n = 0; x += 4; y += 4; r = max(6, r + 2)
    for yy in range(max(0, int(y - r)), min(h, int(y + r) + 1)):
        row = rows[yy]
        for xx in range(max(0, int(x - r)), min(w, int(x + r) + 1)):
            o = xx * bpp; R, G, B = row[o], row[o + 1], row[o + 2]
            if (R >= 85 and G >= 75 and B >= 125 and R >= G and B - G >= 45) if iso else (R >= 195 and G >= 180 and B >= 235 and B - G >= 30 and R - G >= 5): n += 1
    return n

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
         scen("합침 배치 끝", rec + jumpS(90) + [tag("end", JS_END)]),
         scen("v126 후류 규칙", rec + [["eval", "(()=>{const e=document.getElementById('rcpTailKg');e.value='40';return e.value})()"]] + jumpS(90) + [tag("end40", JS_END)]),
         scen("v128 U자 액봉", BOOT + [["eval", "window.__dt.opSetMode('free');1"], ["wait", 1500]] + jump(2.3) + [["wait", 4000], tag("us0", JS_US), ["eval", "window.__dt.setValve('R',false);1"], ["wait", 350], tag("usA", JS_US), ["wait", 6000], tag("us1", JS_US),
                                    ["shot", str(SHOTS / "v128_U자_환류닫음.png"), "#stage", 3, [480, 110, 190, 130]], ["eval", "window.__dt.setValve('R',true);1"], ["wait", 5000], tag("us2", JS_US),
                                    ["eval", "window.__dt.setValve('P',true);window.__dt.setValve('M',true);window.__dt.setValve('F',false);1"], ["wait", 9000], tag("mv0", JS_US), ["eval", "window.__dt.setValve('M',false);1"], ["wait", 350], tag("mvA", JS_US), ["wait", 6000], tag("mv1", JS_US),
                                    ["shot", str(SHOTS / "v130_본류밸브_닫음.png"), "#stage", 3, [560, 300, 200, 130]], ["eval", "window.__dt.setValve('M',true);1"], ["wait", 6000], ["eval", "window.__dt.setValve('P',false);1"], ["wait", 7000], tag("pv1", JS_US),
                                    ["eval", "window.__dt.setValve('P',true);1"], ["wait", 3000], tag("fade", JS_2DFADE)]),
         scen("v129 열 퍼짐", rec + jump(1.3) + [["wait", 3000], tag("z0", JS_ZH), ["shot", str(SHOTS / "v129_강조_교반중.png"), "#stage", 3, [380, 300, 170, 230]], ["eval", "document.getElementById('heatEm').click();1"], ["wait", 1500], tag("z1", JS_ZH),
                                   ["eval", "document.getElementById('heatEm').click();1"], ["wait", 6000], tag("z2", JS_ZH), ["eval", JS_RPM(0)], ["wait", 25000], tag("z3", JS_ZH), ["shot", str(SHOTS / "v129_교반_정지.png"), "#stage", 3, [380, 300, 170, 230]],
                                   ["eval", JS_RPM(80)], ["wait", 3000], tag("z4", JS_ZH)]),
         scen("v126 화면", rec + [tag("geo", JS_GEO)] + jump(1.25) + [tag("v6a", JS_V6A), ["wait", 1500], ["shot", str(SHOTS / "v126_예열_3D.png")]] + jump(6) + [["wait", 3000], tag("v6b", JS_V6B), tag("v7", JS_V7)])]
    st4 = lambda name: ["shot", str(SHOTS / name), "#stage"]   # v131: 스테이지만(자리 = 화소) — 화살촉이 실제로 찍혔는지 그림에서 센다
    S += [scen("v131 진공 흐름", rec + jump(0.3) + [["wait", 3000], tag("p0", JS_VAC), V_ON, ["wait", 3500], tag("p1", JS_VAC), st4("v131_진공흐름_예열_3D.png")] + jump(6) + [["wait", 5000], tag("n3", JS_VAC), st4("v131_진공흐름_정상_3D.png"), tag("n3eq", JS_VEQ),
                                    V_2D, ["wait", 3500], tag("n2", JS_VAC), st4("v131_진공흐름_정상_2D.png"), tag("n2ov", JS_P2OV), tag("n2arr", JS_P2ARR), V_OFF, ["wait", 1500], st4("v131_진공흐름_정상_2D_끔.png"), V_3D, ["wait", 3000], st4("v131_진공흐름_정상_3D_끔.png"), tag("off", JS_VAC),
                                    V_ON, ["eval", "window.__dt.ab('pstop');1"]] + jump(6.6) + [["wait", 5000], tag("s3", JS_VAC), st4("v131_진공흐름_펌프정지_3D.png"), V_2D, ["wait", 3500], tag("s2", JS_VAC), st4("v131_진공흐름_펌프정지_2D.png")]),
          scen("v131 진공 흐름 리크", rec + [V_ON] + jump(6) + [["eval", "window.__dt.ab('leak');1"]] + jump(7.3) + [["wait", 5000], tag("l3", JS_VAC), st4("v131_진공흐름_리크_3D.png"), V_2D, ["wait", 3500], tag("l2", JS_VAC), st4("v131_진공흐름_리크_2D.png")]),
          scen("v131 2차 부하", rec + jump(6) + [["wait", 4000], tag("c0", JS_VAC), V_ON, ["eval", "window.__dt.ab('c1hot');1"]] + jump(6.5) + [["wait", 5000], tag("c1", JS_VAC), st4("v131_2차부하_1차냉매95도_3D.png"), V_2D, ["wait", 3500], tag("c2", JS_VAC), st4("v131_2차부하_1차냉매95도_2D.png"),
                                  V_GL(True), ["wait", 5000], tag("t2", JS_VAC), V_3D, ["wait", 3000], tag("t3", JS_VAC), st4("v131_진공흐름_막힘계산_3D.png"), V_GL(False), ["wait", 4000], tag("t0", JS_VAC)]),
          scen("v131 스팀 게이지", rec + jump(6) + [["wait", 5000], tag("g0", JS_GA), st4("v131_스팀게이지_3D_자동.png"), ["click", ".dcs-tag.gauge .dg-r", 0.5, 0.5], ["wait", 1500], tag("g1", JS_GA), ["wait", 5000], tag("g2", JS_GA), st4("v131_스팀게이지_3D_수동.png"),
                                     ["drag", ".dcs-tag.gauge .dg-r", 0.5, 0.5, 0.22, 0.5, 12], ["wait", 1500], tag("g3", JS_GA), ["click", ".dcs-tag.gauge .dg-a"], ["wait", 1200], tag("g4", JS_GA), ["wait", 6000], tag("g5", JS_GA),
                                     V_2D, ["wait", 3500], tag("h0", JS_GA), ["click", ".p2-ghit", 0.6, 0.5], ["wait", 1500], tag("h1", JS_GA), ["drag", ".p2-ghit", 0.6, 0.5, 0.3, 0.5, 12], ["wait", 1500], tag("h2", JS_GA), st4("v131_스팀게이지_2D_수동.png"),
                                     ["eval", JS_GTOUCH], ["wait", 1200], tag("h3", JS_GA), ["click", ".p2-gauto"], ["wait", 1200], tag("h4", JS_GA), ["wait", 5000], tag("h5", JS_GA)])]
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
        okU = abs((q["yRf"] - q["yU"]) - 0.3) < 1e-6 and len(seg) >= 5 and len(low) >= 1 and vr is not None and abs(vr[0] - (q["xSpl"] + q["xU1"]) / 2) < 0.12 and abs(vr[1] - q["ySpl"]) < 0.25 and abs(float(d["inp"]["holdC"]) - 0.55) < 1e-9
        add("M17", "환류 U자 액봉: 그림 깊이 = 환류 노즐 − 300 mm(그림 비율 · P&ID MIN. 300, 현장 600 mm는 실 루프 0.55 kg로 계산에), 관 조각 5개, FCV-H073은 티 다음 구간(현장 계기 자리, v126)", okU,
            f"노즐 − 바닥 {(q['yRf'] - q['yU']) * 1000:.0f} mm · 관 조각 {len(seg)}개(바닥 {len(low)}개) · 밸브 자리 {[round(v, 2) for v in vr] if vr else None}(티 다음 구간 가운데 {round((q['xSpl'] + q['xU1']) / 2, 2)}, 높이 {round(q['ySpl'], 2)}) · 실 루프 {d['inp']['holdC']} kg", "300 mm · 5개 · 밸브는 티 다음 구간 · 0.55 kg")
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
        left = z["m0"] - z["fore"] - z["main"]; byTail = "후류" in z["why"]; byStop = "액위 하한" in z["why"]
        add("P8", "배치 끝 = 후류(기본 조건): 투입 − 초류 − 본류 = 후류 30 kg(사용자 11-19 '300 · 초류 30 · 후류 30이면 본류 240'), 초류 30 kg", z["stopped"] and (byTail or byStop) and abs(left - 30) < 0.5 and abs(z["fore"] - 30) < 1.0,
            f"{z['t']:.1f} h에 끝 · 초류 {z['fore']:.1f} · 본류 {z['main']:.1f} kg → 투입 − 초류 − 본류 = {left:.1f} kg(끝난 뒤 정제기 {z['m']:.1f} kg) · 사유 '{z['why'][:70]}'",
            "30 ± 0.5 kg · 초류 30 ± 1 · 사유 후류(가열 정지 액위가 먼저 오면 그때도 30 ± 0.5)")
        add("N7", "현장 그래프(2026-03-09 배치)와 견줌(참고): 본류 내부 · 탑 · 응축액 출구 온도, 단계 길이", None,
            f"시뮬 본류 내부 {f2(z['Tmain'])} · 탑 {f2(z['ThMain'])} · 응축액 {f2(z['T1main'])} · 자켓 {f2(z.get('TjeMain'))} ℃ / 현장 약 100 · 86~87 · 46 · 100(화면) ℃ · 시뮬 승온~끝 {z['t']:.0f} h / 현장 약 82 h", "참고(증기압식·탑 온도계 자리·스팀 밸브는 DB로 맞춘다)")

    z4 = g("v126 후류 규칙", "end40")
    if z4:
        left = z4["m0"] - z4["fore"] - z4["main"]
        add("P8", "후류 규칙: 후류를 40 kg으로 바꾸면 본류가 투입 − 초류 − 40에 이를 때 '후류 도달'로 끝", z4["stopped"] and "후류" in z4["why"] and abs(left - 40) < 0.5,
            f"{z4['t']:.1f} h에 끝 · 초류 {z4['fore']:.1f} · 본류 {z4['main']:.1f} kg → 투입 − 초류 − 본류 = {left:.1f} kg(정제기 {z4['m']:.1f}) · 사유 '{z4['why'][:50]}'", "40 ± 0.5 kg · 사유 '후류'")
    v = g("v126 화면", "v6a")
    if v:
        okVS = all(x["on"] and x["d"] for x in v["VS"]) and len(v["VS"]) == 5;   # v128: 액면 전체 5줄
        okVS = okVS; okVN = all(x["on"] for x in v["VN"]) and len(v["VN"]) >= 1; okVC = all(x["on"] and x["d"] for x in v["VC"]) and len(v["VC"]) == 2
        pre = v["boil"] and not v["vpTop"]
        add("P1", "도면: 끓는 동안 정제기 안(액면 → 목관) · 목관 · 컬럼 안(바닥 → 예열 전선) 증기 점(예열 중에도)", pre and okVS and okVN and okVC and v["vcY"] is not None and abs(v["vcY"] - v["yF"]) < 0.003 and not v["vtop"],
            f"{v['t']:.2f} h(끓음 {v['boil']} · 꼭대기 넘음 {v['vpTop']}) · 정제기 안 {sum(x['on'] for x in v['VS'])}/5 · 목관 {sum(x['on'] for x in v['VN'])} · 컬럼 안 {sum(x['on'] for x in v['VC'])}/2 · 점 끝 {v['vcY']:.3f} m = 예열 전선 {v['yF']:.3f} m · 꼭대기 위 증기관 {'켜짐' if v['vtop'] else '꺼짐'}",
            "예열 중 · 셋 다 켜짐 · 점 끝 = 전선 ± 3 mm · 증기관은 아직 꺼짐")
        add("P2", "3D 컬럼: 액막 원통 없음 · 충전물 = 구간 예열 정도 색(데워진 구간만, 파랑 없음) · 도면 충전물도 같은 색", v["film"] == 0 and v["hotRows"] == v["expRows"] and v["blue"] == 0 and len(v["hotRows"]) > 0,
            f"보이는 액막 원통 {v['film']}개 · 데워진 줄 {v['hotRows']}(구간 온도로 기대 {v['expRows']}) · 파란 고리 {v['blue']}개 · 구간 온도 {v['Tsec']} ℃", "0개 · 같음 · 0개")
        add("P4", "도면 진공 라인 점 = 비응축 가스(리크 공기) 색 · 범례 4줄(증기 · 응축액 · 스팀 · 비응축 가스)", "air" in (v["sCls"] or "") and len(v["legend"]) == 4 and len(v["keys"]) == 4,
            f"진공 라인 '{v['sCls']}' · 범례 {v['legend']}", "air · 4줄")
        add("P5", "둥근 점: 3D 점 재질(2 px 이상) 모두 원 무늬 · 도면 점 = 길이 0 점선 + 둥근 끝", v["pts"] > 0 and v["ptsMap"] == v["pts"] and v["cap"] == "round" and v["dash"].replace("px", "").replace(" ", "").startswith("0,"),
            f"3D 점 {v['ptsMap']}/{v['pts']}개 원 무늬 · 도면 점선 '{v['dash']}' · 끝 '{v['cap']}'", "모두 · 0, 간격 · round")
    v = g("v126 화면", "v6b")
    if v:
        add("P3", "환류 분배 구멍 4개 모두에서 줄기(환류가 흐를 때, 3D). v127: 현장 작은 구멍 약 4개(사용자 11-20)", v["flow"] and v["n"] == 4 and all(v["vis"]), f"환류 흐름 {v['flow']} · 줄기 {sum(v['vis'])}/{v['n']}개 보임", "4/4")
        vs = v["valves"]; bad = [k for k, x in vs.items() if x["mats"] != 1]; noHead = [k for k, x in vs.items() if x["head"] < 1]
        add("P6", "밸브 머리(조절 밸브 덮개 · 액추에이터)까지 상태 색 한 가지(열림 초록 · 닫힘 빨강)", vs and not bad and not noHead,
            f"밸브 {len(vs)}개 · 부품 색이 둘 이상 {bad or '없음'} · 머리 없음 {noHead or '없음'} · 부품 수 " + ", ".join(f"{k} {x['n']}" for k, x in vs.items()), "모두 한 색 · 머리 있음")
        j = vs.get("J") or {}
        add("P7", "스팀 밸브 가운데로 관이 비치지 않음: 밸브 목 반지름 ≥ 관 반지름 × 1.1", j.get("fr") is not None and v["pipeJ"] and j["fr"] >= 1.1 * v["pipeJ"],
            f"목 {j.get('fr')} m · 스팀 관 {v['pipeJ']} m(비 {j['fr'] / v['pipeJ']:.2f})" if j.get("fr") and v["pipeJ"] else f"목 {j.get('fr')} · 관 {v['pipeJ']}", "≥ 1.1")
    v = g("v126 화면", "v7")
    if v:
        H, F = v["holes"], v["rd"]; xs = sorted(h[0] for h in H)
        inCol = all(v["col"][0] < h[0] < v["col"][1] and abs(h[1] - v["yD"]) < 0.6 for h in H)
        under = all(f["seg"] and any(abs(f["seg"][0] - x) < 0.6 for x in xs) and abs(f["seg"][2] - f["seg"][0]) < 0.6 and v["yD"] < f["seg"][1] < f["seg"][3] <= v["yP"] + 1 for f in F)
        add("Q1", "도면: 분배 헤더의 작은 구멍 4개(컬럼 안, 헤더 높이) · 구멍마다 떨어지는 액 점 4줄(헤더 아래 → 충전층 위, 환류가 흐를 때 켜짐 — 3D와 같은 판정)", len(H) == 4 and inCol and len(F) == 4 and under and v["on3"] and all(f["on"] for f in F),
            f"구멍 {len(H)}개(x {', '.join(f'{x:.0f}' for x in xs)} · 컬럼 {v['col'][0]:.0f}~{v['col'][1]:.0f}) · 액 점 {sum(f['on'] for f in F)}/{len(F)}줄 켜짐 · 구멍 아래 {'예' if under else '아니오'} · 3D 판정 {v['on3']}", "4개 · 4/4줄 · 예")
    v = g("v126 화면", "v6a")
    if v and v.get("sec") is not None:
        on = [c for c in v["sec"] if c]; blue = [c for c in on if c[2] > c[0] + 0.02]
        add("R1", "컬럼 옆 온도 띠에 파랑 없음(예열 중) — 충전물과 같은 예열 정도 색(회색 → 노랑 → 주황). 사용자 11-20 '아직 컬럼이 파란색으로 나오는 게 있는데'", len(on) > 0 and not blue,
            f"보이는 띠 {len(on)}/{len(v['sec'])}개 · 파란 띠 {len(blue)}개 · 색 " + ", ".join("#%02x%02x%02x" % tuple(round(x * 255) for x in c) for c in on), "보이는 띠 있음 · 파랑 0개")
    v = g("v126 화면", "v6b")
    if v and v.get("ag"):
        a = v["ag"]; vol = a.get("vol") or {}
        lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        lum = lambda c: 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2])
        stops = [(.114, .247, .722), (.122, .643, .788), (.373, .827, .541), (.949, .835, .267), (.941, .416, .165)]   # 액 온도 입체의 색 눈금(셰이더와 같은 값)
        def ramp(t):
            t = min(1, max(0, t)) * 4; i = min(3, int(t)); k = t - i; return tuple(stops[i][j] + (stops[i + 1][j] - stops[i][j]) * k for j in range(3))
        ok = a["n"] >= 5 and a["tr"] and a["dw"] and vol.get("ord") is not None and a["ord"] is not None and a["ord"] > vol["ord"]; cr = None
        if a.get("col") and vol.get("tHi") is not None:
            liq = ramp((vol["Tm"] - vol["tLo"]) / max(1, vol["tHi"] - vol["tLo"])); l1, l2 = lum(liq), lum(a["col"]); cr = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
        add("R2", "교반기 축 · 날개가 액 온도 입체에 가려지지 않음(입체 뒤에 그림) · 뜨거운 액 색과 명도 대비 3 이상(재질 색 기준). 사용자 11-20 '교반기가 흐릿한 색이라 거의 안 보이네'", bool(ok and cr is not None and cr >= 3),
            f"부품 {a['n']}개 · 그리는 순서 {a['ord']}(액 온도 입체 {vol.get('ord')}) · 외곽선 {a.get('hull')} · 재질 색 #" + ("%02x%02x%02x" % tuple(round(x * 255) for x in a["col"]) if a.get("col") else "-") + (f" · 액 {vol['Tm']:.1f} ℃ 색과 대비 {cr:.1f}" if cr is not None else " · 액 온도 입체 없음"), "5개 넘게 · 3.5 > 3 · 대비 ≥ 3")
    v = g("v126 화면", "v7")
    if v and v.get("more"):
        m = v["more"]; num0 = lambda d: float(d[1:].split(" ")[0]) if d.startswith("M") else None
        xs = [num0(x["d"]) for x in m["VS"] if x["d"]]; left = [x for x in xs if x < m["x0"] - 50]; right = [x for x in xs if x > m["x0"] + 50]
        add("S1", "도면: 정제기 증기 점이 액면 전체에서 올라감(왼쪽 · 오른쪽 모두). 사용자 11-20 '너무 오른쪽에서만 기체가 올라가고'", len(xs) == 5 and len(left) >= 2 and len(right) >= 2 and all(x["on"] for x in m["VS"]),
            f"증기 줄 {len(xs)}개 · 축 왼쪽 {len(left)} · 오른쪽 {len(right)} · 켜짐 {sum(x['on'] for x in m['VS'])}", "5줄 · 왼쪽 2 넘게 · 오른쪽 2 넘게 · 모두 켜짐")
        want = bool(m["boil"] and (m["onRD"] or m["back"] > 0.02)); okL = all(len(m[k]) >= 1 and all(bool(x["on"]) == want and x["d"] for x in m[k]) for k in ("LC", "LN", "LS")) and len(m["LC"]) == 2
        add("S2", "도면: 컬럼 안 · 목관 · 정제기 위 공간으로 내려오는 액 점(환류 + 컬럼에서 응축한 몫) — 3D 목관 줄기와 같은 판정. 사용자 11-20 '컬럼에서 그냥 식어서 내려오는 건 표현 안 된 거 같네'", want and okL and all(x["on"] for x in m["CE"]),
            f"판정(끓음 {m['boil']} · 환류가 헤더에 닿음 {m['onRD']} · 컬럼 응축 몫 {m['back'] * 100:.1f} %) = {want} · 컬럼 안 {sum(x['on'] for x in m['LC'])}/{len(m['LC'])}줄 · 목관 {sum(x['on'] for x in m['LN'])} · 정제기 위 {sum(x['on'] for x in m['LS'])} · 응축기 관 안 {sum(x['on'] for x in m['CE'])}", "모두 켜짐")
        ld = m.get("ld"); okLd = ld is not None and m["cap1"] > 0 and abs(ld - 100 * m["Qv1"] / m["cap1"]) < 1e-6 and (m.get("ldTxt") or "").endswith("%")
        d1 = g("합침 첫 화면", "m1"); has3 = bool(d1 and "E-H071 응축 부하(계산)" in d1["tags"])
        add("S5", "1차 응축기 부하율(응축 능력 대비 %) 값 상자: 3D · 도면. 사용자 11-20 '케파 대비 %도 나올 수 있나? 몇 퍼센트 이상이면 2차로'", bool(okLd and has3),
            (f"부하 {ld:.2f} % = 응축 열 {m['Qv1'] / 1000:.2f} kW ÷ 응축 능력 {m['cap1'] / 1000:.1f} kW · 도면 '{m.get('ldTxt')}' · 3D 값 상자 {'있음' if has3 else '없음'} · 지금 2차로 가는 몫 {(1 - m['c1']) * 100:.3f} %" if ld is not None else "값 없음"), "값 = 응축 열 ÷ 능력 · 두 화면에 있음")
        add("S6", "도면: 정제기 액 색 = 온도 색(3D와 같은 눈금) · U자 액봉에 찬 액 표시", bool(m.get("liqC")) and m["sealOn"] == (m["holdC"] > 0 and m["sealM"] >= m["holdC"] * 0.999) and m["sealOn"],
            f"액 색 {m.get('liqC')}({m['Tm']:.1f} ℃) · U자 표시 {m['sealOn']}(실 루프 {m['sealM']:.2f} / {m['holdC']:.2f} kg)", "색 있음 · U자 표시 켜짐")
    z = [g("v129 열 퍼짐", "z%d" % i) for i in range(5)]
    if all(z):
        z0, z1, z2, z3, z4 = z
        if not z0["on"]:
            add("T1", "정제기 열 퍼짐 구획 계산(가벼운 계산에서만 — 이 PC는 격자 계산이라 건너뜀)", None, f"계산 방식 {z0['kind']}", "-")
        else:
            add("T1", "열 퍼짐 구획 계산: 교반 중(80 rpm) 승온에서는 평균과의 차이가 0.5 ℃ 밑(고르게 섞임) · 부피 평균 0 · 혼합 시간 식 값 5~60 s", z0["max"] is not None and z0["max"] < 0.5 and abs(z0["mean"]) < 1e-3 and z0["th95"] is not None and 5 < z0["th95"] < 60,
                f"{z0['t']:.2f} h · {z0['rpm']:.0f} rpm · 최대 편차 {z0['max']:.3f} ℃(벽 쪽 {z0['wall']:+.3f} · 가운데 {z0['center']:+.3f}) · 부피 평균 {z0['mean']:.1e} · 혼합 시간 {z0['th95']:.1f} s · 벽 막 온도 차 {z0['dW']:.1f} ℃", "< 0.5 ℃ · 평균 0 · 5~60 s")
            tb = (z3["top"] or 0) - (z3["bot"] or 0); ratio = tb / z3["S"] if z3["S"] > 0 else None
            add("T2", "교반을 멈추면(0 rpm) 위쪽이 뜨겁고 가운데는 평균보다 차다 — 크기가 옛 격자 계산의 비율(0.31 × (자켓 − 액))과 같은 자릿수. 사용자 11-20 '교반 안 돌리고 하면 벽만 빨개지고 대류가 잘 안 되는 거'",
                z3["rpm"] < 1 and tb > 3 and (z3["center"] or 0) < 0 and ratio is not None and 0.3 <= ratio <= 3 and z3["dW"] > 15,
                f"멈춘 뒤 공정 {(z3['t'] - z2['t']) * 60:.0f}분 · 위 {z3['top']:+.1f} · 아래 {z3['bot']:+.1f} · 가운데 {z3['center']:+.1f} ℃ · 위 − 아래 {tb:.1f} ℃ = 옛 비율 값 {z3['S']:.1f} ℃의 {ratio:.2f}배 · 벽 막 온도 차 {z3['dW']:.1f} ℃ · 자연대류 한 바퀴 {(z3['turn'] or 0) / 60:.0f}분" if ratio is not None else "값 없음", "위 − 아래 > 3 ℃ · 가운데 < 0 · 0.3~3배")
            add("T3", "교반을 다시 켜면 혼합 시간의 몇 배(공정 시간) 안에 차이가 풀린다. 사용자 11-20 '교반 돌면서 점차적으로 다른 곳으로 색이 퍼지게'", z4["rpm"] > 70 and z4["max"] is not None and z4["max"] < 0.1 * z3["max"],
                f"켠 뒤 공정 {(z4['t'] - z3['t']) * 3600:.0f} s(혼합 시간 {z4['th95']:.0f} s) · 최대 편차 {z3['max']:.2f} → {z4['max']:.3f} ℃", "10 % 밑으로")
            okOn0 = z0["pressed"] == "true" and z0["zEm"] == 1 and bool(z0["note"]) and "로그 눈금" in (z0["note"] or "") and (z0["hot"] or 0) >= 3
            okOff = z1["pressed"] == "false" and z1["zEm"] == 0 and z1["note"] is None and (z1["hot"] or 0) == 0
            okOn = z2["pressed"] == "true" and z2["zEm"] == 1 and (z2["hot"] or 0) >= 3
            add("T4", "'열 퍼짐 강조' 스위치: 기본 켜짐(v130, 사용자 '기본 켜짐으로') — 평균보다 뜨거운 곳을 붉게 덧칠 + 벽을 지난 흐름 줄기가 붉어짐 + 무엇을 뜻하는지 글이 밸브 줄에 나옴. 끄면 실제 온도 색만, 다시 켜면 돌아옴", okOn0 and okOff and okOn,
                f"처음 {z0['pressed']} · 덧칠 {z0['zEm']} · 붉은 줄기 {z0['hot']}/{z0['nStir']}개 · 글 '{(z0['note'] or '')[:60]}' · 끈 뒤 덧칠 {z1['zEm']} · 붉은 줄기 {z1['hot']}개 · 다시 켠 뒤 붉은 줄기 {z2['hot']}개", "기본 켜짐 · 덧칠 · 줄기 3개 넘게 · 글 · 끄면 0")
    u0, u1, u2, uA = g("v128 U자 액봉", "us0"), g("v128 U자 액봉", "us1"), g("v128 U자 액봉", "us2"), g("v128 U자 액봉", "usA")
    if u0 and u1 and u2:
        us = u1.get("us") or {}; okHold = bool(us) and abs(u1["head"] - us["s1"]) < 1e-3 and u1["tail"] < 1e-6 and u1["held"] and not u1["want"] and not u1["R"]
        add("S3", "환류 U자 액봉: 환류 밸브를 닫아도 U자와 그 앞 구간(넘침 높이와 같은 높이)은 찬 채로, 컬럼 쪽 끝 토막만 빈다. 실 루프 무게 유지, 다시 열면 흐름 표시가 돌아옴. 사용자 11-20 '정제 밸브를 닫으면 U관에 액이 차 있나? 이런 것도 구현되어 있나?'",
            okHold and abs(u1["seal"] - u1["holdC"]) < 1e-6 and u1["mHeldC"] >= u1["seal"] - 1e-6 and u2["want"] and not u2["held"] and abs(u2["head"] - u2["L"]) < 1e-3 and u2["tail"] < 1e-6,
            f"닫기 전 환류 {u0['Rkg']:.1f} kg/h · 닫은 뒤 찬 구간 {u1['tail']:.3f}~{u1['head']:.3f} m(U자 끝 {us.get('s1', 0):.3f} m, 관 전체 {u1['L']:.3f} m) · 실 루프 {u1['seal']:.2f} kg · 다시 연 뒤 {u2['tail']:.3f}~{u2['head']:.3f} m · 갇힘 표시 {u2['held']}", "U자 끝까지 참 · 0.55 kg 유지 · 다시 흐름")
    if u0 and u1 and uA and uA.get("pR"):
        a, b1 = uA["pR"], u1["pR"]; rdA, rd1 = uA.get("rd") or {}, u1.get("rd") or {}
        okNow = a["glass"] and a["vis"] >= 4 and (uA["out"] or (a["dr"] and a["dr"]["t"] < a["head"] - 1e-6)) and (rdA.get("vis") or 0) >= 1
        okEnd = b1["glass"] and b1["vis"] >= 4 and not u1["out"] and (rd1.get("vis") or 0) == 0
        add("U1", "환류 밸브를 닫아도 관 속 액이 갑자기 사라지지 않음(3D): 바탕 관은 유리로 남고, 닫은 직후에는 컬럼 쪽 끝 토막이 아직 흘러 나가며 분배 구멍 줄기가 이어지고, 몇 초 뒤 끝 토막 · 줄기만 빈다. 사용자 11-20 '리플럭스 밸브 잠그면 밸브랑 컬럼 사이 배관 흐르던 액은 갑자기 사라지는'",
            bool(okNow and okEnd),
            f"닫고 0.35 s: 유리 {a['glass']} · 보이는 토막 {a['vis']}/{a['n']} · 흘러 나가는 중 {uA['out']} · 분배 줄기 {rdA.get('vis')}개 → 6 s 뒤: 유리 {b1['glass']} · 보이는 토막 {b1['vis']}/{b1['n']} · 분배 줄기 {rd1.get('vis')}개", "직후에는 이어짐 · 뒤에는 U자와 앞 구간만")
    m0, m1, p1 = g("v128 U자 액봉", "mv0"), g("v128 U자 액봉", "mv1"), g("v128 U자 액봉", "pv1")
    if m0 and m1 and m0.get("pM"):
        a, b1, pp = m0["pM"], m1["pM"], m1["pP"]
        add("U2", "본류 밸브(XV-H077)를 닫으면 밸브 위의 액은 남고 아래는 탱크로 빠진다. 받는 탱크 밸브가 모두 닫히면 유출 관의 액은 갈 곳이 없어 그대로 남는다(3D)",
            m0["Dkg"] > 1 and abs(a["head"] - a["L"]) < 1e-3 and a["sV"] is not None and abs(b1["head"] - b1["sV"]) < 1e-3 and b1["tail"] < 1e-6 and b1["held"] and b1["glass"] and abs(pp["head"] - pp["L"]) < 1e-3 and pp["held"],
            f"닫기 전 유출 {m0['Dkg']:.1f} kg/h · 본류 가지 {a['head']:.3f}/{a['L']:.3f} m → 닫은 뒤 0~{b1['head']:.3f} m(밸브 자리 {b1['sV']:.3f} m) · 유출 관 {pp['head']:.3f}/{pp['L']:.3f} m 남음", "밸브 위만 남음 · 유출 관은 전부 남음")
    if p1 and p1.get("pP"):
        pp, mm = p1["pP"], p1["pM"]
        add("U3", "유출 밸브(FCV-H072)를 닫으면 밸브 위의 액은 남고 아래는 열린 본류 탱크로 흘러 내려가 빈다(3D)", pp["sV"] is not None and abs(pp["head"] - pp["sV"]) < 1e-3 and pp["tail"] < 1e-6 and pp["held"] and mm["head"] < 1e-6 and not p1["VLV"]["P"] and p1["VLV"]["M"],
            f"유출 관 0~{pp['head']:.3f} m(밸브 자리 {pp['sV']:.3f} m, 관 전체 {pp['L']:.3f} m) · 본류 가지 {mm['head']:.3f} m", "밸브 위만 남음 · 아래 0")
    fd = g("v128 U자 액봉", "fade")
    if fd:
        add("U4", "도면: 흐름이 멈춘 점은 바로 꺼지지 않고 1초 동안 흘러가며 옅어진다", fd["on0"] and not fd["on1"] and abs(fd["o2"] - fd["o1"]) > 1 and 0.02 < fd["a2"] < 0.98 and fd["a3"] < 0.05 and abs(fd["o4"] - fd["o3"]) < 1e-9,
            f"멈춘 뒤 0.35 s 불투명도 {fd['a1']:.2f} → 0.65 s {fd['a2']:.2f} → 1.85 s {fd['a3']:.2f} · 그동안 점 이동 {abs(fd['o2'] - fd['o1']):.0f} · 다 옅어진 뒤 이동 {abs(fd['o4'] - fd['o3']):.0f}", "옅어지는 동안 이동 · 끝나면 멈춤")
    en = g("합침 배치 끝", "end")
    if en:
        res = en["m0"] - en["fore"] - en["main"] - en["m"]
        add("S4", "배치 끝: 환류 U자 액봉에 든 액(0.55 kg)은 관에 남고 정제기로 흘러내리지 않음(물질 수지: 투입 = 초류 + 본류 + 정제기 + U자)", abs(res - 0.55) < 0.05 and "U자 액봉" in en["why"],
            f"투입 {en['m0']:.1f} − 초류 {en['fore']:.2f} − 본류 {en['main']:.2f} − 정제기 {en['m']:.2f} = {res:.2f} kg · 끝 글에 'U자 액봉' {'있음' if 'U자 액봉' in en['why'] else '없음'}", "0.55 ± 0.05 kg · 글 있음")
    e = g("v126 화면", "geo")
    if e and e.get("packY0") is not None:
        neck = e["colBase"] - e["yNz"]; col = e["colTop"] - e["colBase"]; keep = abs(e["colTop"] - 2.492) < 1e-3 and abs(e["yDish"] - 2.352) < 1e-3 and abs(e["tankTop"] - 0.876) < 1e-3 and abs(e["yValve"] - 1.226) < 1e-3
        hd = e["packY1"] - e["packY0"]
        add("R4", "그림의 충전층 구간을 길게(구간 6칸이 구분되게) — 실제 높이는 계산에만. 사용자 11-20 '128도 컬럼이 너무 작은데? 패킹 있는 구간 말야 · 단을 나누기에 너무 짧음 · 이미지만 수정, 실제 사이즈는 계산으로'",
            hd >= 0.6 and hd >= 2 * e["Hpack"] and abs(e["Hpack"] - 0.3) < 1e-9 and abs(e["yDish"] - e["packY1"] - 0.112) < 1e-3,
            f"그림 충전층 {hd:.3f} m(구간 하나 {hd / 6 * 1000:.0f} mm) · 계산에 쓰는 충전 높이 {e['Hpack']:.2f} m · 분배 헤더는 충전층 위 {(e['yDish'] - e['packY1']) * 1000:.0f} mm", "그림 ≥ 0.6 m · 계산 0.30 m 그대로")
        add("R3", "컬럼을 크게 · 목관을 짧게(그림 배치): 컬럼 몸통 ÷ 목관 ≥ 2, 목관은 0.3 m 넘게(요구 C8 · 모터 위 간격), 충전층은 컬럼 바닥에, 컬럼 꼭대기 · 분배 헤더 · 회수 탱크는 v127 자리(유출 티만 0.14 m 위 — P11). 사용자 11-20 '컬럼이 너무 작게 표현 · 사이 배관이 너무 긴데'",
            col / neck >= 2 and 0.3 < neck < 0.5 and abs(e["packY0"] - e["colBase"] - 0.042) < 1e-3 and keep,
            f"컬럼 몸통 {col:.3f} m · 목관 {neck:.3f} m(비 {col / neck:.2f}, v127은 0.594 · 0.779 = 0.76) · 충전층 {e['packY0']:.3f}~{e['packY1']:.3f} · 꼭대기 {e['colTop']:.3f} · 헤더 {e['yDish']:.3f} · 본류 탱크 꼭대기 {e['tankTop']:.3f} · 유출 티 {e['yValve']:.3f}", "비 ≥ 2 · 목관 0.3~0.5 m · 제자리")
    if e:
        add("P12", "정제기 몸통 직관부 = P&ID 800 mm(위 접선 = 아래 경판 + 800, 0.40 m³와 맞음)", abs(e["Hs"] - e["hh"] - 0.8) < 1e-6 and abs(e["topY"] - e["Hs"] - 0.175) < 1e-6,
            f"아래 경판 {e['hh']:.3f} · 위 접선 {e['Hs']:.3f} · 꼭지점 {e['topY']:.3f} m(직관부 {e['Hs'] - e['hh']:.3f})", "직관부 0.800")
    v = g("v126 화면", "v6b")
    if v and v.get("mv"):
        m = v["mv"]; a = m["lo"] - m["tankTop"]; b = m["tee"] - m["hi"]
        add("P11", "본류 탱크 위 밸브(XV-H077)가 탱크 경판 · 티에 붙지 않음(사용자 11-19 '너무 붙어 있는데?' · 11-20 '밸브가 너무 탱크 상부랑 붙어 있는데' — v128: 기준 20 mm → 80 mm)", a > 0.08 and b > 0.08,
            f"밸브 아래 끝 ~ 탱크 꼭대기 {a * 1000:.0f} mm · 밸브 위 끝 ~ 티 {b * 1000:.0f} mm", "아래 · 위 모두 80 mm 넘게")
    d = g("합침 첫 화면", "m1")
    if d:
        ip = d["inp"]; okI = abs(float(ip["Lpipe"]) - 4.7) < 1e-9 and abs(float(ip["nElb"]) - 2) < 1e-9 and abs(float(ip["holdC"]) - 0.55) < 1e-9
        add("P10", "현장 배관 치수는 계산에(사용자 11-19 '그림은 보기 좋게, 계산 시 수치만'): 증기관 직관 4.7 m(위 3 + 오른쪽 1.2 + 아래 0.5) · 엘보 2 · U자 액봉 0.55 kg(0.6 + 0.3 + 0.6 m × 15A × 1530 kg/m³)", okI,
            f"Lpipe {ip['Lpipe']} m · 엘보 {ip['nElb']} · holdC {ip['holdC']} kg", "4.7 · 2 · 0.55")
        need = ["PIH093 펌프 쪽 압력", "FIH071 스팀 유량"]; miss = [t for t in need if t not in d["tags"]]
        add("P9", "PIMS 태그: 펌프 쪽 압력 PIH093 · 스팀 유량 FIH071(11-19 PIMS 화면) 값 상자", not miss, "모두 있음" if not miss else "없음: " + ", ".join(miss), "둘 다 있음")
    judge131(g, add)

def judge131(g, add):
    """v131: 진공 흐름(V1~V4 · V9) · 2차 부하(V5) · 스팀 게이지(V6 · V7) · 자리(V8). 기준은 계산 상태(PR)에서 여기서 다시 구한 값이고, 화살촉은 화면 그림의 화소로도 본다."""
    import pathlib
    shots = pathlib.Path(__file__).resolve().parent / "shots"
    f2 = lambda v: f"{v:.2f}"; VT = {"PI 컬럼 상부(계산)": "top", "PI 증기 배관 출구(계산)": "exit", "PI 응축기(계산)": "cond"}
    def chain(d):   # 따로 구한 구간 압력: 응축기 = 펌프 쪽 + 밀폐 압력, 위쪽 값은 아래쪽보다 낮지 않게
        r = d["raw"]; pc = r["Ppump"] + (r["Pseal"] if r["VV"] else 0); ps = max(r["Pstill"], pc); pt = max(pc, min(r["Ptop"], ps)); pe = max(pc, min(r["Pexit"], pt)); return dict(still=ps, top=pt, exit=pe, cond=pc, pump=r["Ppump"])
    def want(d):    # 따로 구한 화살촉: 구간 → (보임, 크기 배율, 빈 화살촉)
        r = d["raw"]; c = chain(d); live = not r["stopped"]; vd = max(0, r["vdot"] or 0) if live else 0; vp = max(0, r["vpass"] or 0) if live and r["VV"] else 0; thr = max(1e-4, 0.002 * c["still"])
        dd = dict(AB=c["still"] - c["top"], BC=c["top"] - c["exit"], CD=c["exit"] - c["cond"]); gas = dict(AB=vd > 0.05, BC=vp > 0.05, CD=vp > 0.05); mx = max([dd[k] for k in dd if gas[k] and dd[k] > thr] or [0]); out = {}
        for k in dd: hol = not dd[k] > thr; out[k] = (gas[k], 0.6 if hol else 0.6 + 0.6 * dd[k] / mx, hol)
        c1 = min(1, max(0, r["c1"])) if r["c1"] is not None else 1; air = (r["nAir"] or 0) * 0.028964 * 3600; pump = d["pump"]; lost = max(0, r["lost"] or 0) if live else 0
        out["T2"] = (vp * (1 - c1) > 1e-4 or bool(pump and air > 0), 0.6, True); out["S"] = (bool(pump and (air > 0 or lost > 1e-6)), 0.6, True)
        return out, dd, dict(vd=vd, vp=vp, v2=vp * (1 - c1), air=air, thr=thr)
    def arrows_bad(d, iso):   # 화살촉(3D 또는 도면)의 보임 · 크기 · 빈 여부가 따로 구한 것과 다른 것
        w, _, fl = want(d); bad = []
        for a in (d["p2"]["arr"] if iso else d["arr"]):
            on, k, hol = w[a["sec"]]; kk = k * (a.get("base") or 1) if iso else k
            if on and not hol and abs(k - 0.6) < 0.02: continue   # 압력 차가 문턱 바로 위(채움 ↔ 빈 경계)는 판정하지 않는다
            if bool(a["on"]) != bool(on) or (on and (abs((a["k"] or 0) - kk) > 0.03 or bool(a["hollow"]) != hol)): bad.append(f'{a["id"]}: 보임 {a["on"]}(기대 {on}) · 크기 {a["k"]}(기대 {kk:.3f}) · 빈 {a["hollow"]}(기대 {hol})')
        return bad
    def num(s):
        m = re.search(r"-?\d+(?:\.\d+)?", s or ""); return float(m.group(0)) if m else None
    def vals_bad(d, tol=0.016):   # 화면 숫자(3D 값 상자 글 또는 도면 값 글) = 따로 구한 구간 압력(소수 둘째 자리 반올림 + 값 글을 고치는 간격만큼의 여유)
        c = chain(d); src = {"top": d["p2"]["vals"]["Ptop"], "exit": d["p2"]["vals"]["Pexit"], "cond": d["p2"]["vals"]["Pcond"]} if d["iso"] else {v: d["tags"].get(k) for k, v in VT.items()}; bad = []
        for k, s in src.items():
            x = num(s)
            if x is None or "mmHg" not in s or abs(x - c[k]) > tol: bad.append(f"{k} '{s}' ≠ {c[k]:.3f}")
        return bad
    def seen(d, on_png, off_png, iso):   # 화면 그림에서 보이는 화살촉마다 [이름, 켠 그림의 보라 화소, 끈 그림의 보라 화소]
        try: a = png_rows(str(shots / on_png)); b = png_rows(str(shots / off_png)) if off_png else None
        except Exception as e: return None, f"그림을 못 읽음({e})"
        out = [[x["id"], violet_px(a, x["x"], x["y"], x["r"], iso), violet_px(b, x["x"], x["y"], x["r"], iso) if b else 0] for x in (d["p2"]["arr"] if iso else d["arr"]) if x["on"]]
        return out, ""
    TK = "회수 탱크 · 균압 라인: 응축기와 같은 압력으로 둔다(따로 계산하지 않음)"   # 뜻 글의 회수 탱크 줄(기본 계산)
    sn = "v131 진공 흐름"; p0, p1, n3, n2, s3, s2, off, ov, n2arr, n3eq = (g(sn, k) for k in ("p0", "p1", "n3", "n2", "s3", "s2", "off", "n2ov", "n2arr", "n3eq"))
    if p0 and p1 and n3 and n2 and off:
        vt0 = [k for k in VT if k in p0["tags"]]; c = chain(n3); t3 = {k: n3["tags"].get(k) for k in VT}; b3 = vals_bad(n3); b2 = vals_bad(n2); v2 = n2["p2"]["vals"]
        okOff0 = p0["pressed"] == "false" and not p0["on"] and not vt0 and p0["note"] is None and not any(a["on"] for a in p0["arr"]) and (p0["p2"] is None or p0["p2"]["disp"] == "none")
        okOn3 = n3["pressed"] == "true" and not b3 and all(n3["tvis"].get(k) for k in VT) and bool(n3["note"]) and "압력 차" in n3["note"] and "방향" in n3["note"] and n3["noteVis"]
        okOn2 = n2["iso"] and n2["p2"]["disp"] != "none" and not b2 and all(n2["p2"]["box"].get(k) for k in ("Ptop", "Pexit", "Pcond")) and n2["noteVis"]
        okOff1 = off["pressed"] == "false" and not any(k in off["tags"] for k in VT) and off["note"] is None and not any(a["on"] for a in off["arr"]) and max(abs(a - b) for a, b in zip(off["cam"], n3["cam"])) < 1e-3
        add("V1", "[진공 흐름] 스위치: 기본 꺼짐(값 상자 · 화살촉 · 뜻 글 없음). 켜면 구간 압력 값 상자 3개(컬럼 상부 · 증기 배관 출구 · 응축기, 계산값)가 3D와 도면에 보이고 뜻 글이 그림 왼쪽 위에 나온다. 끄면 되돌아가고 그림 크기(카메라)는 그대로. 사용자 11-20 '진공흐름 버튼누르면 … 각 구간마다 어떤지'",
            bool(okOff0 and okOn3 and okOn2 and okOff1),
            f"처음 {p0['pressed']} · 상자 {len(vt0)}개 → 켠 뒤 3D {t3}(따로 구한 값 상부 {c['top']:.3f} · 출구 {c['exit']:.3f} · 응축기 {c['cond']:.3f}, 가려지지 않음 {all(n3['tvis'].get(k) for k in VT)}) · 도면 {v2['Ptop']} · {v2['Pexit']} · {v2['Pcond']}(화면 안 {n2['p2']['box']}) · 뜻 글 보임 3D {n3['noteVis']} · 도면 {n2['noteVis']} · 끈 뒤 상자 {sum(1 for k in VT if k in off['tags'])}개 · 어긋남 {(b3 + b2) or '없음'}",
            "꺼짐 0개 → 켜면 3개(3D = 도면 = 계산값, 보임) · 뜻 글 → 끄면 0개")
        _, dd, fl = want(n3); order = c["still"] > c["top"] > c["exit"] > c["cond"] >= c["pump"] - 1e-9; a3 = arrows_bad(n3, False); a2 = arrows_bad(n2, True)
        kk = {a["id"]: a["k"] for a in n3["arr"] if a["on"]}; rot = {a["id"]: a["rot"] for a in n3["arr"]}; deg = {a["id"]: a["deg"] for a in n2["p2"]["arr"]}
        dirOK = abs(rot["neck"] - math.pi / 2) < 1e-3 and abs(rot["up"] - math.pi / 2) < 1e-3 and abs(rot["run"]) < 1e-3 and abs(rot["in"] + math.pi / 2) < 1e-3 and abs(rot["t2"]) < 1e-3 and abs(rot["s"]) < 1e-3 and [deg[k] for k in ("neck", "up", "run", "in", "t2", "s")] == [-90, -90, 0, 90, 0, 0]
        add("V2", "진공 흐름의 방향 · 세기(정상 운전 6 h): 구간 압력이 정제기 > 컬럼 상부 > 증기 배관 출구 > 응축기 순이고, 화살촉은 그 순서(위 → 오른쪽 → 아래 → 펌프 쪽)를 가리킨다. 크기 = 0.6 + 0.6 × (구간 압력 차 ÷ 가장 큰 구간 압력 차) — 3D와 도면이 같다(표시 규칙)",
            bool(order and not a3 and not a2 and dirOK and kk and kk.get("up", 0) == max(kk.values()) and max(dd, key=dd.get) == "BC"),
            f"압력 {c['still']:.3f} > {c['top']:.3f} > {c['exit']:.3f} > {c['cond']:.3f} ≥ {c['pump']:.3f} mmHg · 압력 차 충전층 {dd['AB']:.3f} · 배관 {dd['BC']:.3f} · 출구 {dd['CD']:.3f} · 증기 {fl['vp']:.1f} kg/h · 3D 크기 {kk} · 어긋남 3D {a3 or '없음'} · 도면 {a2 or '없음'}", "순서대로 · 가장 큰 화살촉 = 증기 배관 · 어긋남 없음")
        s3d, e3 = seen(n3, "v131_진공흐름_정상_3D.png", "v131_진공흐름_정상_3D_끔.png", False); s2d, e2 = seen(n2, "v131_진공흐름_정상_2D.png", "v131_진공흐름_정상_2D_끔.png", True)
        okPx = bool(s3d) and bool(s2d) and len(s3d) == 6 and len(s2d) == 6 and all(x[1] >= 15 and x[2] <= 2 for x in s3d + s2d) and all(a["top"] for a in n3["arr"] if a["on"]) and all(a["inS"] for a in n2["p2"]["arr"] if a["on"])
        add("V2", "화살촉이 화면에 실제로 보인다(정상 운전 6 h): 화면 그림에서 화살촉 자리마다 화살촉 색(보라) 화소를 센다 — 켠 그림에는 있고 끈 그림의 같은 자리에는 없다. 3D는 다른 화면 요소에 가려지지 않고, 도면은 그림 안에 있다",
            okPx, f"[이름, 켠 그림, 끈 그림] 3D {s3d if s3d is not None else e3} · 도면 {s2d if s2d is not None else e2}", "화살촉 6개 모두 켠 그림 15화소 이상 · 끈 그림 2화소 이하")
        hol = {a["id"]: (a["on"], a["hollow"], a["k"]) for a in n3["arr"] if a["sec"] in ("T2", "S")}; hol2 = {a["id"]: (a["on"], a["hollow"], a["k"]) for a in n2["p2"]["arr"] if a["sec"] in ("T2", "S")}
        add("V3", "계산에 없는 것은 지어내지 않는다: 응축기 → 2차 응축기 → 진공펌프 구간은 계산에서 같은 압력(관 압력 손실 없음)이라 크기를 매기지 않고 빈 화살촉(가장 작은 크기)으로 방향만 내고, 회수 탱크 · 균압 라인은 값 상자도 화살촉도 없고, 뜻 글에 '응축기와 같은 압력으로 둔다(따로 계산하지 않음)'고 적는다(3D · 도면 같은 글)",
            bool(len(hol) == 2 and all(v == (True, True, 0.6) for v in hol.values()) and all(v == (True, True, 0.6) for v in hol2.values()) and abs(c["cond"] - c["pump"]) < 1e-9 and not n3["tank"] and not p1["tank"] and len(n3["arr"]) == 6 and len(n2["p2"]["arr"]) == 6 and n3.get("tline") == TK and n2.get("tline") == TK and n3.get("stTank") is False),
            f"응축기 {c['cond']:.3f} = 펌프 쪽 {c['pump']:.3f} mmHg · 1차 → 2차 · 2차 → 펌프 화살촉 3D {hol} · 도면 {hol2} · 리크 공기 {fl['air'] * 1000:.2f} g/h · 회수 탱크 압력 상자 {len(n3['tank'])}개 · 화살촉 자리 {len(n3['arr'])}곳(균압 라인 0) · 뜻 글 3D '{n3.get('tline')}' · 도면 '{n2.get('tline')}'", "빈 화살촉 2개(크기 0.6) · 회수 탱크 상자 0개 · 뜻 글에 한 줄")
        if ov and n2arr and n3eq:
            add("V8", "진공 흐름을 켠 도면: 새 값 상자(컬럼 상부 · 증기관 출구 · 응축기 압력, E-H072 부하) · 게이지 상자가 관 선과 다른 글에 걸리지 않고, 화살촉이 글 · 값 상자에 걸리지 않음", not ov["cross"] and not ov["overlap"] and not n2arr["hit"] and n2arr["n"] == 6,
                f"관에 걸림 {ov['cross'] or '없음'} · 서로 겹침 {ov['overlap'] or '없음'} · 본 글 · 상자 {ov['items']}개 · 화살촉 {n2arr['n']}개 중 걸린 것 {n2arr['hit'] or '없음'}", "0개")
            add("V8", "진공 흐름을 켠 3D(1440×1000, 레시피 6 h): 값 상자가 설비 몸통(정면 윤곽 사각형) · 화살촉 · 뜻 글을 가리지 않음", not n3eq["equip"] and not n3eq["arrows"] and not n3eq["note"] and n3eq["nArr"] == 6,
                f"설비 가림 {n3eq['equip'] or '없음'} · 화살촉 가림 {n3eq['arrows'] or '없음'} · 뜻 글 가림 {n3eq['note'] or '없음'} · 값 상자 {n3eq['n']}개 · 화살촉 {n3eq['nArr']}개", "0개")
    if p1 and s3 and s2:
        c = chain(p1); eq = max(c.values()) - min(c.values()); fil = [a["id"] for a in p1["arr"] if a["on"] and not a["hollow"]]; hol = [a["id"] for a in p1["arr"] if a["on"] and a["hollow"]]; b1 = arrows_bad(p1, False) + vals_bad(p1)
        cs = chain(s3); eqs = max(cs.values()) - min(cs.values()); ons = [a["id"] for a in s3["arr"] if a["on"]]; on2 = [a["id"] for a in s2["p2"]["arr"] if a["on"]]; bs = arrows_bad(s3, False) + arrows_bad(s2, True) + vals_bad(s3, 0.03) + vals_bad(s2, 0.03)
        lagOK = s3["lag"] is None or "따라오지 않은" in (s3["note"] or "")
        add("V4", "흐름이 없으면 화살촉도 없다: 끓기 전(0.3 h)에는 구간 압력이 모두 같고 채운 화살촉 0개(펌프가 빼는 리크 공기 방향만 빈 화살촉 2개). 진공 펌프를 세우고(PCV 0 %) 6.6 h까지 건너뛴 뒤(약 30분)에는 증발이 멈추고 펌프로 가는 기체도 없어 화살촉 0개(3D · 도면), 구간 압력은 펌프 쪽 값과 같다. 정제기 압력 상자(저장값)가 낮게 남아 있으면 뜻 글에 밝힌다",
            bool(eq < 0.01 * c["pump"] and not fil and sorted(hol) == ["s", "t2"] and not b1 and not s3["pump"] and (s3["raw"]["vdot"] or 0) < 0.05 and not ons and not on2 and not bs and eqs < 1e-9 and cs["pump"] > 5 * c["pump"] and lagOK),
            f"끓기 전: 압력 {c['still']:.3f}~{c['pump']:.3f} mmHg · 채운 화살촉 {fil or '없음'} · 빈 화살촉 {hol} → 펌프 정지 {((s3['t'] - off['t']) * 60 if off else float('nan')):.0f}분 뒤: 펌프 쪽 {cs['pump']:.2f} mmHg · 증발 {s3['raw']['vdot']:.2f} kg/h · 화살촉 3D {ons or '없음'} · 도면 {on2 or '없음'} · 값 상자 {[s3['tags'].get(k) for k in VT]} · 정제기 압력 상자 {s3['tags'].get('PICH071 탱크 압력')}(저장값 {s3['raw']['Pstill']:.2f}) · 뜻 글 '{(s3['note'] or '')[-42:]}' · 어긋남 {(b1 + bs) or '없음'}",
            "끓기 전 채운 화살촉 0 · 빈 화살촉 2 → 펌프 정지 뒤 0개 · 낮게 남은 값은 밝힘")
    l3, l2 = g("v131 진공 흐름 리크", "l3"), g("v131 진공 흐름 리크", "l2")
    if l3 and l2 and n3:
        c = chain(l3); c0 = chain(n3); w, dd, fl = want(l3); bad = arrows_bad(l3, False) + arrows_bad(l2, True) + vals_bad(l3) + vals_bad(l2); a = {x["id"]: (x["on"], x["hollow"]) for x in l3["arr"]}
        add("V9", "이상 상황에서 숫자 · 화살촉이 계산값대로 바뀐다(진공 리크 증가 5 mmHg/min, 78분 뒤): 펌프 쪽 압력이 올라 증기 배관 출구가 초킹되지 않으면 출구 압력 = 응축기 압력이 되고 그 구간 화살촉은 빈 것(방향만), 충전층 · 배관 구간은 채운 화살촉. 3D = 도면 = 계산값",
            bool(not bad and c["cond"] > 5 * c0["cond"] and fl["vp"] > 1 and abs(c["exit"] - c["cond"]) <= fl["thr"] and a["in"] == (True, True) and a["neck"] == (True, False) and a["run"] == (True, False) and dd["BC"] < chain(n3)["top"] - chain(n3)["exit"]),
            f"응축기 {c0['cond']:.2f} → {c['cond']:.2f} mmHg · 정제기 {c['still']:.2f} · 상부 {c['top']:.2f} · 출구 {c['exit']:.2f} · 증기 {fl['vp']:.1f} kg/h · 마하 {l3['raw']['Mach']:.2f} · 화살촉(보임, 빈 것) {a} · 3D 값 {[l3['tags'].get(k) for k in VT]} · 도면 값 {[l2['p2']['vals'][k] for k in ('Ptop', 'Pexit', 'Pcond')]} · 어긋남 {bad or '없음'}",
            "출구 = 응축기 → 빈 화살촉 · 나머지 채운 화살촉 · 어긋남 없음")
    sn = "v131 2차 부하"; c0, c1, c2 = g(sn, "c0"), g(sn, "c1"), g(sn, "c2")
    if c0 and c1 and c2:
        def ld2(d):
            r = d["raw"]; return None if not (r["cap2"] and r["cap2"] > 0) or r["stopped"] else 100 * r["Qv1"] * (1 - min(1, max(0, r["c1"]))) / r["cap2"]
        fmt = lambda v: "–" if v is None else (f"{v:.1f}" if v < 10 else f"{v:.0f}"); a, b1, b2 = ld2(c0), ld2(c1), ld2(c2); N2 = "E-H072 응축 부하(계산)"; t0, t1 = c0["tags"].get(N2), c1["tags"].get(N2); r1 = c1["raw"]; d2 = c2["p2"]["vals"]["C2load"]
        okV = a is not None and b1 is not None and abs((c0["c2L"] or 0) - a) < 1e-9 and abs((c1["c2L"] or 0) - b1) < 1e-9 and t0 == fmt(a) + "%" and num(t1) is not None and abs(num(t1) - b1) < 0.06 and num(d2) is not None and abs(num(d2) - b2) < 0.06 and d2.endswith(" %")
        okSee = bool(c0["tvis"].get(N2) and c1["tvis"].get(N2) and c2["p2"]["box"].get("C2load"))
        okHot = b1 is not None and r1["c1"] < 0.01 and b1 > 50 * max(a or 0, 1e-9) and abs(b1 - 100 * r1["Qv1"] / r1["cap2"]) < 0.02 * b1 and (r1["m2"] or 0) > 1 and str(c1["tags"].get("E-H071 응축 부하(계산)") or "–").startswith("–")
        add("V5", "2차 응축기 부하 값 상자(3D '2차 부하' · 도면 'E-H072 부하'): 부하율 = 1차에서 응축되지 못하고 넘어온 증기의 응축 열 ÷ 2차 응축 능력 = Qv1·(1 − c1) ÷ cap2(1차와 같은 뜻 · 같은 형식). 1차 N-Brine 온도 상승(95 ℃)이면 증기가 모두 2차로 넘어가 부하율이 오르고 1차는 능력 0이라 '–'. 사용자 11-20 '2차콘덴서쪽도 2차 부하로 적어놓자'",
            bool(okV and okSee and okHot),
            f"정상: 넘어온 열 {c0['raw']['Qv1'] * (1 - c0['raw']['c1']):.3f} W ÷ 능력 {c0['raw']['cap2'] / 1000:.1f} kW = {(a or 0):.5f} % → 상자 '{t0}' · 1차 N-Brine 95 ℃: 1차 응축 비율 {r1['c1']:.3f} · 2차로 {(r1['m2'] or 0):.2f} kg/h · {r1['Qv1']:.0f} W ÷ {(r1['cap2'] or 0) / 1000:.1f} kW = {(b1 or 0):.3f} % → 상자 '{t1}' · 도면 '{d2}' · 1차 상자 '{c1['tags'].get('E-H071 응축 부하(계산)')}' · 화면에 보임 {okSee}", "상자 = 따로 구한 값 · 보임 · 냉매 온도 상승 때 50배 넘게 오름")
    t2, t3, t0 = g("v131 2차 부하", "t2"), g("v131 2차 부하", "t3"), g("v131 2차 부하", "t0")
    if t2 and t3 and t0:
        def tl_ok(d):   # '초류 탱크 x.xx · 본류 탱크 x.xx mmHg(…)'의 두 숫자 = 계산한 탱크 압력
            m = re.match(r"초류 탱크 (-?\d+(?:\.\d+)?) · 본류 탱크 (-?\d+(?:\.\d+)?) mmHg", d.get("tline") or ""); gl = d.get("gl")
            return bool(m and gl and abs(float(m.group(1)) - gl["F"]) < 0.016 and abs(float(m.group(2)) - gl["M"]) < 0.016 and "응축기와 같은 압력" not in d["tline"])
        add("V3", "'유출관 높이로 막힘 계산'을 켜면 회수 탱크 압력을 따로 계산하므로 뜻 글의 회수 탱크 줄이 '응축기와 같은 압력으로 둔다' 대신 계산값(초류 탱크 · 본류 탱크 mmHg)으로 바뀐다(3D · 도면). 끄면 되돌아온다",
            bool(t3.get("glOn") and t2.get("glOn") and isinstance(t3.get("stTank"), dict) and tl_ok(t3) and tl_ok(t2) and (not t3["iso"]) and t2["iso"] and not t0.get("glOn") and t0.get("tline") == TK),
            f"켬: 3D '{t3.get('tline')}'(계산값 초류 {(t3.get('gl') or {}).get('F', float('nan')):.3f} · 본류 {(t3.get('gl') or {}).get('M', float('nan')):.3f}) · 도면 '{t2.get('tline')}' → 끔: '{t0.get('tline')}'", "켜면 계산값 · 끄면 원래 글")
    sn = "v131 스팀 게이지"; G = {k: g(sn, k) for k in ("g0", "g1", "g2", "g3", "g4", "g5", "h0", "h1", "h2", "h3", "h4", "h5")}
    if all(G.values()):
        g0, g1, g2, g3, g4, g5, h0, h1, h2, h3, h4, h5 = (G[k] for k in ("g0", "g1", "g2", "g3", "g4", "g5", "h0", "h1", "h2", "h3", "h4", "h5"))
        bx = g0["box"]; vx = g0["valve"]; dist = math.hypot(max(bx[0], min(vx[0], bx[0] + bx[2])) - vx[0], max(bx[1], min(vx[1], bx[1] + bx[3])) - vx[1]) if bx and vx else 999
        same = bool(bx and g1["box"] and g4["box"]) and all(abs(a - b) < 0.6 for a, b in zip(bx, g1["box"])) and all(abs(a - b) < 0.6 for a, b in zip(bx, g4["box"]))
        ok0 = g0["el"] and g0["recipe"] and not g0["hold"] and g0["chip"] is False and g0["mode"] == "자동(PI) 조절 중" and abs(g0["rv"] - round(g0["mv"])) <= 1 and dist <= 30 and g0["reach"] and not g0["pop"]
        ok1 = g1["hold"] and g1["chip"] and g1["held"] and g1["mode"] == "수동 고정" and 45 <= g1["rv"] <= 55 and abs(g1["mv"] - g1["rv"]) < 0.6 and abs(g2["mv"] - g1["mv"]) < 0.6 and g2["vdot"] > g0["vdot"] + 0.3 and not g1["pop"] and same
        ok3 = g3["hold"] and 14 <= g3["rv"] <= 26 and abs(g3["mv"] - g3["rv"]) < 0.6
        ok4 = (not g4["hold"]) and g4["chip"] is False and not g4["held"] and g4["mode"] == "자동(PI) 조절 중" and "스팀 자동(PI) 복귀" in " ".join(g4["log"]) and abs(g5["mv"] - g3["mv"]) > 0.3
        add("V6", "스팀 밸브 옆 개도 게이지(3D): '스팀 개도' 값 상자 안의 막대가 지금 개도(자동이면 스팀 PI가 정한 값)와 '자동(PI) 조절 중'을 보인다. 막대를 누르거나 끌면 개도가 바로 바뀌고, 레시피 운전 중이면 그 개도로 고정되어 '수동 고정'과 [자동으로]가 나타난다. [자동으로]를 누르면 스팀 PI로 돌아간다(운전 패널의 '스팀 자동(PI)으로'와 같음). 상자 크기 · 자리는 그대로. 사용자 11-20 '스팀밸브옆에서 그냥 바로 게이지가있어서 내가 바로바로 게이지조절'",
            bool(ok0 and ok1 and ok3 and ok4),
            f"자동: 막대 {g0['rv']} · 개도 {g0['mv']:.1f} % · '{g0['mode']}' · 밸브까지 {dist:.0f} px · 막대가 맨 위 {g0['reach']} → 가운데를 누름: {g1['mv']:.0f} %('{g1['mode']}' · [자동으로] {g1['chip']}) · 5초 뒤 {g2['mv']:.0f} % · 증발 {g0['vdot']:.2f} → {g2['vdot']:.2f} kg/h · 상자 그대로 {same} → 끌어서 {g3['mv']:.0f} % → [자동으로]: 고정 {g4['hold']} · '{g4['mode']}' · 6초 뒤 {g5['mv']:.1f} %", "누름 · 끌기 = 그 개도로 고정 · [자동으로] = PI 복귀 · 밸브에서 30 px 안")
        gg = h0["g2"] or {}; pos = (gg["cx"] - gg["x0"]) / (gg["x1"] - gg["x0"]) * 100 if gg else -1
        ok20 = h0["iso"] and bool(gg) and not gg["auto"] and gg["mode"] == "자동(PI) 조절 중" and abs(pos - h0["mv"]) < 1.5 and (gg["hit"] or [0, 0])[0] > 20
        ok21 = h1["hold"] and h1["g2"]["auto"] and h1["g2"]["mode"] == "수동 고정" and 55 <= h1["mv"] <= 70 and h1["g2"]["num"] == f"{h1['mv']:.1f} %" and 20 <= h2["mv"] <= 34 and h2["g2"]["view"] == h0["g2"]["view"]
        ok22 = 78 <= h3["mv"] <= 92 and h3["hold"] and (not h4["hold"]) and not h4["g2"]["auto"] and h4["g2"]["mode"] == "자동(PI) 조절 중" and abs(h5["mv"] - h3["mv"]) > 0.2
        add("V7", "스팀 밸브 옆 개도 게이지(도면): 'TCV-H071 개도' 값 상자 안의 막대 — 누름 · 끌기 · 터치 포인터로 개도가 바뀌고, 끄는 동안 도면은 움직이지 않는다. 상태 글(자동 · 수동 고정)과 [자동으로]는 3D와 같다",
            bool(ok20 and ok21 and ok22),
            f"도면 막대 자리 {pos:.1f} %(개도 {h0['mv']:.1f} % · '{gg.get('mode')}' · 누르는 자리 {[round(x) for x in (gg.get('hit') or [0, 0])]} px) → 누름 {h1['mv']:.0f} %('{h1['g2']['num']}' · '{h1['g2']['mode']}') → 끌기 {h2['mv']:.0f} % · 도면 보는 범위 그대로 {h2['g2']['view'] == h0['g2']['view']} → 터치 {h3['mv']:.0f} % → [자동으로]: 고정 {h4['hold']} · 5초 뒤 {h5['mv']:.1f} %", "누름 · 끌기 · 터치로 바뀜 · 도면 안 움직임 · 자동 복귀")

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
    a = "안쪽 관의 작은 구멍 약 4개로 충전층 위에 떨어진다(현장, 사용자 2026-11-20" in h; old = "컬럼 가운데 한 점에 떨어진다(분배기 없음)" in h
    R.append({"id": "Q2", "name": "설비 설명(컬럼): 환류는 작은 구멍 약 4개로 떨어진다(현장, 사용자 11-20) — 조립도 판독 '가운데 한 점(분배기 없음)'은 남지 않음", "ok": a and not old,
              "val": f"현장 문장 {'있음' if a else '없음'} · 옛 문장 {'남음' if old else '없음'}", "crit": "있음 · 없음"})
    R.append({"id": "M3", "name": "화면 글에 '냉각수' 없음(1차 = N-Brine, 2차 = L-Brine)", "ok": cw == 0 and "N-Brine" in body and "L-Brine" in body, "val": f"'냉각수' {cw}곳 · N-Brine {body.count('N-Brine')}곳 · L-Brine {body.count('L-Brine')}곳", "crit": "0곳"})
    return R
