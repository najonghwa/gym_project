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
          "UAmode": "design", "Q1des": 2050, "Q2des": 700, "Tdes": 86, "f2": 0.1, "A1": 21.71, "A2": 2.0, "capF": 69, "capM": 398, "holdC": 0.55, "Tcw": 50, "Tcw2": -22.6,
          "type": "anchor", "D": 390, "C": 90}
# 추가 점검 문서(설비pnid.pdf, 2026-11-18): 자켓 높이는 사내망 오독(855)을 바로잡은 635, 컬럼은 조립도 H-VP-ME-C-H081-001(태그 칸 C-H071) 값
PRESET_GA = {"Hj": 635, "Dcol": 155.2, "packFill": 26, "pack": "pall25"}
# 운전 개념(사용자 2026-11-18): 환류 4 kg/h 고정, 유출 초류 2 · 본류 6 → 정제기에 약 70 kg 남으면 5, 투입 350 · 초류 30 · 후류 30 kg
PRESET_OP = {"H": 350, "rcpForeKg": 30, "swM": 30, "rcpForeR": 4, "rcpForeD": 2, "rcpMainR": 4, "rcpMainD": 6, "rcpLateKg": 70, "rcpLateD": 5, "rcpTailKg": 30, "rcpMainKg": 0, "splitMode": "D"}   # v142 분배: 유출 FICH072 고정 · 나머지 환류(사용자 2026-11-25)
TAGS = ["TICH071 탱크 내부", "WIH071 정제기 무게", "TIH074 자켓", "TICH071 스팀 밸브 개도", "TIH075 탑 온도", "PICH071 탱크 압력", "TICH071D 응축액 출구",
        "FICH073 환류", "FICH072 유출", "WIH072 초류 무게", "WIH073 본류 무게"]   # SICAH071 교반은 값 상자에서 빼 둔 설정값(DCS_SKIP)
OLD = ["FIC-072", "FIC-073", "FCV-072", "FCV-073", "유출 FT-H073", "고점 FT-H073", "FT-H073 0", "TIC-H071D 응축액", "(TIC-H071D)", "TI-H075 탑"]   # 옛 번호와 옛 이름표 쓰임. P&ID 표기(FT/FIQC-H073 = 환류 유량계, TE/TIC-H071D, TE/TI-H075)는 설비 설명에 남는다
PID_WORDS = ["80A-CCH-H0709", "80A-CCH-H0701", "15A-CCH-H0704", "15A-CCH-H0710", "15A-CCH-H0703", "15A-CCH-H0706", "50A-CCH-H0702", "P&ID T-H071", "P&ID C-H071", "P&ID E-H071", "P&ID E-H072",
             "P&ID T-H072", "P&ID T-H073", "VP-H093", "PCV-H093", "TCV-H072", "XV-H074", "XV-H077", "MIN. 300 mm"]
KIND_EXPECT = {"Q1des": "dwg", "Q2des": "dwg", "Tdes": "est", "f2": "meas", "Dpipe": "dwg", "DpipeR": "dwg", "DpipeP": "dwg", "DpipeC": "dwg", "T": "dwg", "Hs": "dwg", "Hj": "dwg", "tw": "dwg", "tIns": "dwg", "A1": "dwg", "A2": "dwg", "capF": "dwg", "capM": "dwg",
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
pop:(()=>{const g=document.getElementById('vGauge');return !!(g&&!g.hidden)})(),log:(D.PR.ops||[]).slice(-4).map(o=>o.text),rule:(document.getElementById('rcpSteam')||{}).value||null})})()"""   # v138s: 스팀 개도 정하는 법
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
         scen("v129 열 퍼짐", rec + jump(0.3) + [["wait", 3000], tag("z0", JS_ZH),   # v141f: 승온 중(스팀 개도 70 %)인 0.3 h. 전 1.3 h는 v139부터 승온이 끝난 뒤(개도 26 %)라 벽 막 온도 차가 3 ℃뿐이다
                                    ["shot", str(SHOTS / "v129_강조_교반중.png"), "#stage", 3, [380, 300, 170, 230]], ["eval", "document.getElementById('heatEm').click();1"], ["wait", 1500], tag("z1", JS_ZH),
                                   ["eval", "document.getElementById('heatEm').click();1"], ["wait", 6000], tag("z2", JS_ZH), ["eval", JS_RPM(0)], ["wait", 25000], tag("z3", JS_ZH), ["shot", str(SHOTS / "v129_교반_정지.png"), "#stage", 3, [380, 300, 170, 230]],
                                   ["eval", JS_RPM(80)], ["wait", 3000], tag("z4", JS_ZH)]),
         scen("v126 화면", rec + [tag("geo", JS_GEO)] + jump(0.74) + [["until", "(()=>{const D=window.__dt,P=D.PR,s=D.vaporStats();return (P.vdot>1&&!P.vpTop&&s.front>=0.3)||!!P.vpTop||P.t>3600*1.3})()", 120000], tag("v6a", JS_V6A),   # v141f: 예열 중(끓기 시작 ~ 꼭대기 넘기 전)이 0.64 ~ 0.96 h로 당겨졌다(전 jump(1.25))
                           ["wait", 1500], ["shot", str(SHOTS / "v126_예열_3D.png")]] + jump(6) + [["wait", 3000], tag("v6b", JS_V6B), tag("v7", JS_V7)])]
    st4 = lambda name: ["shot", str(SHOTS / name), "#stage"]   # v131: 스테이지만(자리 = 화소) — 화살촉이 실제로 찍혔는지 그림에서 센다
    S += [scen("v131 진공 흐름", rec + jump(0.3) + [["wait", 3000], tag("p0", JS_VAC), V_ON, ["wait", 3500], tag("p1", JS_VAC), st4("v131_진공흐름_예열_3D.png")] + jump(6) + [["wait", 5000], tag("n3", JS_VAC), st4("v131_진공흐름_정상_3D.png"), tag("n3eq", JS_VEQ),
                                    V_2D, ["wait", 3500], tag("n2", JS_VAC), st4("v131_진공흐름_정상_2D.png"), tag("n2ov", JS_P2OV), tag("n2arr", JS_P2ARR), V_OFF, ["wait", 1500], st4("v131_진공흐름_정상_2D_끔.png"), V_3D, ["wait", 3000], st4("v131_진공흐름_정상_3D_끔.png"), tag("off", JS_VAC),
                                    V_ON, ["eval", "window.__dt.ab('pstop');1"]] + jump(6.6) + [["wait", 5000], tag("s3", JS_VAC), st4("v131_진공흐름_펌프정지_3D.png"), V_2D, ["wait", 3500], tag("s2", JS_VAC), st4("v131_진공흐름_펌프정지_2D.png")]),
          scen("v131 진공 흐름 리크", rec + [V_ON] + jump(6) + [["eval", "window.__dt.ab('leak');1"]] + jump(10) +   # v141f: 전 jump(7.3) — 스팀 개도가 고정이라 리크 뒤 끓음이 1시간 반쯤 멈춘다
                                          [["wait", 5000], tag("l3", JS_VAC), st4("v131_진공흐름_리크_3D.png"), V_2D, ["wait", 3500], tag("l2", JS_VAC), st4("v131_진공흐름_리크_2D.png")]),
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
        add("N4", "기본값: 투입 350 kg · 초류 30 kg · 후류 30 kg, 환류 4 · 유출 2 → 6 → 5 kg/h(정제기 70 kg부터) · 분배 방식 유출 고정(FICH072, v142)", not b3 and abs(d["m0"] - 350) < 0.5, f"{len(PRESET_OP) - len(b3)}/{len(PRESET_OP)}칸 일치 · 투입 {d['m0']:.1f} kg" + (" · 다름 " + ", ".join(b3) if b3 else ""), "모두 일치")
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
            tb = r["B"] / (r["A"] - math.log10(0.1)) - r["C"]; ratio = 10 ** (r["A"] - r["B"] / (85 + r["C"])) / 10 ** (12.41 - 4597 / (85 + 273.15))   # v141f: CpHf 상수 A 12.41(사용자 결정 2026-11-24, 전 11.87)
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
        okp = bool(o.get("op") and o.get("sel") and o.get("dock")) and not o["closed"] and (o["warnH"] > 0 or not o["warn"]) and o["sel"][3] <= o["dock"][1] and o["op"][3] <= o["dock"][1]
        add("C1", "운전 패널을 폈을 때(초류 경고 글이 뜬 채) 그 아래 이름표 선택 상자가 밸브 줄을 가리지 않음", okp,
            f"패널 아래 끝 {o['op'][3] if o.get('op') else '–'} · 선택 상자 아래 끝 {o['sel'][3] if o.get('sel') else '–'} · 밸브 줄 위 {o['dock'][1] if o.get('dock') else '–'} px(경고 글 높이 {o['warnH']} px)", "둘 다 밸브 줄 위(경고 글이 있으면 그 높이까지 — 레시피 개도면 스팀 하한 경고가 없다)")   # v138s-C1
        add("N7", "스팀 하한 경고 글이 원인을 스팀 밸브 가정값으로 밝힘(운전 설정 탓으로 적지 않음) — 레시피 개도(CpHf 첫 화면)는 PI가 없어 경고 자체가 없다", (not o["warn"]) or ("가정" in o["warn"] and "목표가 너무 작음" not in o["warn"]), o["warn"][:160] or "경고 없음", "경고가 있으면 '가정' 있음 · '목표가 너무 작음' 없음")   # v138s-C1
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
        okD = all(z.get(k) is not None for k in ("Dfore", "Dmain", "Dlate")) and abs(z["Dfore"] - 2) < 0.2 and abs(z["Dmain"] - 6) < 0.2 and abs(z["Dlate"] - 5) < 0.2 and z["late"] and z["lateAt"] is not None and abs(z["lateAt"] - 70) < 1.5
        okR = all(z.get(k) is not None and z[k] > 0.3 for k in ("Rfore", "Rmain", "Rlate"))   # v142: 환류는 나머지(응축액 − 유출) — 흐르고 있으면 된다
        add("N3", "운전 개념(v142 분배 — 사용자 결정 2026-11-25): 유출 FICH072 고정 초류 2 · 본류 6 → 정제기 70 kg부터 5 kg/h, 환류는 나머지(스팀이 레시피 개도라 증발이 개도로 정해진다)", okD and okR,
            f"유출 초류 {f2(z['Dfore'])} · 본류 {f2(z['Dmain'])} → {f2(z['Dlate'])} kg/h(정제기 {f2(z['lateAt'])} kg에서 바꿈, {f2(z['tLate'])} h) · 환류(나머지) 초류 {f2(z['Rfore'])} · 본류 {f2(z['Rmain'])} · 끝 무렵 {f2(z['Rlate'])} kg/h", "유출 2 · 6 → 5 ± 0.2 · 70 ± 1.5 kg · 환류 > 0.3")
        add("N3", "운전 개념: 참고 — 환류(나머지)와 스팀 개도 · 내부 온도(초류 · 본류 구간 평균)", None,
            f"환류 초류 {f2(z['Rfore'])} · 본류 {f2(z['Rmain'])} kg/h(운전 개념의 환류 4는 설정 칸에만 남음) · 스팀 개도 초류 {f2(z['mvFore'])} · 본류 {f2(z['mvMain'])} % · 내부 초류 {f2(z.get('Tfore'))} · 본류 {f2(z.get('Tmain'))} ℃", "참고")
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
    judge_real(g, add)   # 현실성(X), 2026-11-22
    judge_ds(g, add)   # 새 디자인(v132~), 2026-11-22

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
        add("V9", "이상 상황에서 숫자 · 화살촉이 계산값대로 바뀐다(진공 리크 증가 5 mmHg/min, 4시간 뒤 — 스팀 개도가 고정이라 끓음이 한동안 멈췄다가 액이 새 끓는점까지 데워져 다시 끓은 때): 펌프 쪽 압력이 올라 증기 배관 출구가 초킹되지 않으면 출구 압력 = 응축기 압력이 되고 그 구간 화살촉은 빈 것(방향만), 충전층 · 배관 구간은 채운 화살촉. 3D = 도면 = 계산값",
            bool(not bad and c["cond"] > 5 * c0["cond"] and fl["vp"] > 1 and abs(c["exit"] - c["cond"]) <= fl["thr"] and a["in"] == (True, True) and a["neck"] == (True, False) and a["run"] == (True, False) and dd["BC"] < chain(n3)["top"] - chain(n3)["exit"]),
            f"응축기 {c0['cond']:.2f} → {c['cond']:.2f} mmHg · 정제기 {c['still']:.2f} · 상부 {c['top']:.2f} · 출구 {c['exit']:.2f} · 증기 {fl['vp']:.1f} kg/h · 마하 {l3['raw']['Mach']:.2f} · 화살촉(보임, 빈 것) {a} · 3D 값 {[l3['tags'].get(k) for k in VT]} · 도면 값 {[l2['p2']['vals'][k] for k in ('Ptop', 'Pexit', 'Pcond')]} · 어긋남 {bad or '없음'}",
            "출구 = 응축기 → 빈 화살촉 · 나머지 채운 화살촉 · 어긋남 없음")
    sn = "v131 2차 부하"; c0, c1, c2 = g(sn, "c0"), g(sn, "c1"), g(sn, "c2")
    if c0 and c1 and c2:
        def ld2(d):
            r = d["raw"]; return None if not (r["cap2"] and r["cap2"] > 0) or r["stopped"] else 100 * r["Qv1"] * (1 - min(1, max(0, r["c1"]))) / r["cap2"]
        fmt = lambda v: "–" if v is None else (f"{v:.1f}" if v < 10 else f"{v:.0f}"); a, b1, b2 = ld2(c0), ld2(c1), ld2(c2); N2 = "E-H072 응축 부하(계산)"; t0, t1 = c0["tags"].get(N2), c1["tags"].get(N2); r1 = c1["raw"]; d2 = c2["p2"]["vals"]["C2load"]
        okV = a is not None and b1 is not None and abs((c0["c2L"] or 0) - a) < 1e-9 and abs((c1["c2L"] or 0) - b1) < 1e-9 and t0 == fmt(a) + "%" and num(t1) is not None and abs(num(t1) - b1) < (0.5 if b1 >= 10 else 0.06) and num(d2) is not None and abs(num(d2) - b2) < (0.5 if b2 >= 10 else 0.06) and d2.endswith(" %")
        okSee = bool(c0["tvis"].get(N2) and c1["tvis"].get(N2) and c2["p2"]["box"].get("C2load"))
        okHot = b1 is not None and r1["c1"] < 0.01 and b1 > 50 * max(a or 0, 1e-9) and abs(b1 - 100 * r1["Qv1"] / r1["cap2"]) < 0.02 * b1 and (r1["m2"] or 0) > 1 and str(c1["tags"].get("E-H071 응축 부하(계산)") or "–") in ("응축 불가",)
        add("V5", "2차 응축기 부하 값 상자(3D '2차 부하' · 도면 'E-H072 부하'): 부하율 = 1차에서 응축되지 못하고 넘어온 증기의 응축 열 ÷ 2차 응축 능력 = Qv1·(1 − c1) ÷ cap2(1차와 같은 뜻 · 같은 형식). 1차 N-Brine 온도 상승(95 ℃)이면 증기가 모두 2차로 넘어가 부하율이 오르고 1차는 능력 0이라 '응축 불가'(v138 — 전에는 값 없음 '–'로 보여 구분이 안 됐다). 사용자 11-20 '2차콘덴서쪽도 2차 부하로 적어놓자'",
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
        AUTO = "레시피 개도" if g0.get("rule") == "mv" else "자동(PI) 조절 중"; LOGA = "스팀 레시피 개도로 복귀" if g0.get("rule") == "mv" else "스팀 자동(PI) 복귀"   # v138s: 레시피 개도면 '자동' = 레시피 개도
        bx = g0["box"]; vx = g0["valve"]; dist = math.hypot(max(bx[0], min(vx[0], bx[0] + bx[2])) - vx[0], max(bx[1], min(vx[1], bx[1] + bx[3])) - vx[1]) if bx and vx else 999
        same = bool(bx and g1["box"] and g4["box"]) and all(abs(a - b) < 0.6 for a, b in zip(bx, g1["box"])) and all(abs(a - b) < 0.6 for a, b in zip(bx, g4["box"]))
        ok0 = g0["el"] and g0["recipe"] and not g0["hold"] and g0["chip"] is False and g0["mode"] == AUTO and abs(g0["rv"] - round(g0["mv"])) <= 1 and dist <= 30 and g0["reach"] and not g0["pop"]
        ok1 = g1["hold"] and g1["chip"] and g1["held"] and g1["mode"] == "수동 고정" and 45 <= g1["rv"] <= 55 and abs(g1["mv"] - g1["rv"]) < 0.6 and abs(g2["mv"] - g1["mv"]) < 0.6 and g2["vdot"] > g0["vdot"] + 0.3 and not g1["pop"] and same
        ok3 = g3["hold"] and 14 <= g3["rv"] <= 26 and abs(g3["mv"] - g3["rv"]) < 0.6
        ok4 = (not g4["hold"]) and g4["chip"] is False and not g4["held"] and g4["mode"] == AUTO and LOGA in " ".join(g4["log"]) and abs(g5["mv"] - g3["mv"]) > 0.3
        add("V6", "스팀 밸브 옆 개도 게이지(3D): '스팀 개도' 값 상자 안의 막대가 지금 개도(자동이면 레시피 개도 — '스팀 개도 정하는 법'이 응축량 맞춤이면 스팀 PI가 정한 값)와 '레시피 개도'(응축량 맞춤이면 '자동(PI) 조절 중')를 보인다. 막대를 누르거나 끌면 개도가 바로 바뀌고, 레시피 운전 중이면 그 개도로 고정되어 '수동 고정'과 [자동으로]가 나타난다. [자동으로]를 누르면 레시피 개도(응축량 맞춤이면 스팀 PI)로 돌아간다(운전 패널의 '스팀 레시피 개도로' · '스팀 자동(PI)으로'와 같음). 상자 크기 · 자리는 그대로. 사용자 11-20 '스팀밸브옆에서 그냥 바로 게이지가있어서 내가 바로바로 게이지조절'",
            bool(ok0 and ok1 and ok3 and ok4),
            f"자동: 막대 {g0['rv']} · 개도 {g0['mv']:.1f} % · '{g0['mode']}' · 밸브까지 {dist:.0f} px · 막대가 맨 위 {g0['reach']} → 가운데를 누름: {g1['mv']:.0f} %('{g1['mode']}' · [자동으로] {g1['chip']}) · 5초 뒤 {g2['mv']:.0f} % · 증발 {g0['vdot']:.2f} → {g2['vdot']:.2f} kg/h · 상자 그대로 {same} → 끌어서 {g3['mv']:.0f} % → [자동으로]: 고정 {g4['hold']} · '{g4['mode']}' · 6초 뒤 {g5['mv']:.1f} %", "누름 · 끌기 = 그 개도로 고정 · [자동으로] = 레시피 개도(또는 PI) 복귀 · 밸브에서 30 px 안")
        gg = h0["g2"] or {}; pos = (gg["cx"] - gg["x0"]) / (gg["x1"] - gg["x0"]) * 100 if gg else -1
        ok20 = h0["iso"] and bool(gg) and not gg["auto"] and gg["mode"] == AUTO and abs(pos - h0["mv"]) < 1.5 and (gg["hit"] or [0, 0])[0] > 20
        ok21 = h1["hold"] and h1["g2"]["auto"] and h1["g2"]["mode"] == "수동 고정" and 55 <= h1["mv"] <= 70 and h1["g2"]["num"] == f"{h1['mv']:.1f} %" and 20 <= h2["mv"] <= 34 and h2["g2"]["view"] == h0["g2"]["view"]
        ok22 = 78 <= h3["mv"] <= 92 and h3["hold"] and (not h4["hold"]) and not h4["g2"]["auto"] and h4["g2"]["mode"] == AUTO and abs(h5["mv"] - h3["mv"]) > 0.2
        add("V7", "스팀 밸브 옆 개도 게이지(도면): 'TCV-H071 개도' 값 상자 안의 막대 — 누름 · 끌기 · 터치 포인터로 개도가 바뀌고, 끄는 동안 도면은 움직이지 않는다. 상태 글(자동 · 수동 고정)과 [자동으로]는 3D와 같다",
            bool(ok20 and ok21 and ok22),
            f"도면 막대 자리 {pos:.1f} %(개도 {h0['mv']:.1f} % · '{gg.get('mode')}' · 누르는 자리 {[round(x) for x in (gg.get('hit') or [0, 0])]} px) → 누름 {h1['mv']:.0f} %('{h1['g2']['num']}' · '{h1['g2']['mode']}') → 끌기 {h2['mv']:.0f} % · 도면 보는 범위 그대로 {h2['g2']['view'] == h0['g2']['view']} → 터치 {h3['mv']:.0f} % → [자동으로]: 고정 {h4['hold']} · 5초 뒤 {h5['mv']:.1f} %", "누름 · 끌기 · 터치로 바뀜 · 도면 안 움직임 · 자동 복귀")

# >>> 현실성(X) 판정 시작
# ---------- 현실성(2026-11-22): 화면이 실제 설비 · 계산대로 움직이는가 — 요구목록 (X)절(번호 = 현실성_목록.md 항목 번호) ----------
# 기준은 지금 화면이 아니라 실제 설비 · 계산에서 정했다(현실성_목록.md '통과 기준'). v131이 못 지키면 실패로 남긴다.
# 3D 줄은 지금 화면(가벼움)을 본다 — 새 디자인용 줄은 따로 더한다. 계산 · 운전 논리를 고쳐야 하는 것은 이름 끝에 '(사용자 판단 대기)'를 붙이고 X8 말고는 참고 줄(판정 없음)로 둔다.
def _xpng(name):
    import pathlib
    try: return png_rows(str(pathlib.Path(__file__).resolve().parent / "shots" / name))
    except Exception: return None
def _xpx(img, x, y):
    w, h, bpp, rows = img; xi = min(w - 1, max(0, int(round(x)))); yi = min(h - 1, max(0, int(round(y)))); o = xi * bpp; r = rows[yi]
    return r[o], r[o + 1], r[o + 2]
def _xblue(c):   # 액 색(파랑) 화소: 도면 액 점 #4aa8ff · U자 표시와 같은 계열(어두운 · 밝은 바탕에 반투명으로 섞여도). 증기 점(#f3e3c2 · #c7922f) · 회색 관은 아님
    return c[2] >= 120 and c[2] - c[0] >= 60 and c[2] - c[1] >= 20
def _xcover(img, pts, rad=1):   # 고른 점 가운데 둘레(3×3)에 액 색 화소가 있는 점의 몫
    if not img or not pts: return None
    n = sum(1 for x, y in pts if any(_xblue(_xpx(img, x + dx, y + dy)) for dx in range(-rad, rad + 1) for dy in range(-rad, rad + 1)))
    return n / len(pts)
def _xrgb(s):   # 'rgb(74, 168, 255)' 또는 '4aa8ff' → (r, g, b)
    if not s: return None
    m = re.findall(r"\d+(?:\.\d+)?", s) if "rgb" in s else None
    if m: return tuple(int(float(v)) for v in m[:3])
    s = s.strip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)) if re.fullmatch(r"[0-9a-fA-F]{6}", s) else None
def _xisblue(s):
    c = _xrgb(s); return bool(c) and _xblue(c)
def _xisred(s):   # 밸브 닫힘 색(빨강 계열)
    c = _xrgb(s); return bool(c) and c[0] >= 150 and c[0] - c[1] >= 70 and c[0] - c[2] >= 70
def _xhue(c):
    import colorsys
    return colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
def _xinterp(v, xs, ys):
    pr = sorted(zip(xs, ys))
    if not pr: return None
    if v <= pr[0][0]: return pr[0][1]
    if v >= pr[-1][0]: return pr[-1][1]
    for (x0, y0), (x1, y1) in zip(pr, pr[1:]):
        if x0 <= v <= x1: return y0 + (y1 - y0) * (v - x0) / ((x1 - x0) or 1e-9)
    return pr[-1][1]
def _xlad(lad):   # 사다리 → 설비 높이 · 그림 속 x · 줄(자리가 있는 것만)
    ys, xs, rs = [], [], []
    for y, p in lad:
        if p is None: continue
        ys.append(y); xs.append(p[0]); rs.append(p[1])
    return ys, xs, rs
def _xves_frac(q, y):   # 그린 받는 탱크(2:1 타원 경판 + 몸통)에서 높이 y까지의 부피 비
    R, hd = q["R"], q["hd"]; yb0 = q["y0"] + hd; yb1 = q["y1"] - hd; A = math.pi * R * R; Vh = A * hd * 2 / 3; Vb = A * (yb1 - yb0); tot = 2 * Vh + Vb
    cap = lambda m: A * m * m * (3 * hd - m) / (3 * hd * hd)
    if y <= q["y0"]: return 0.0
    if y <= yb0: return cap(y - q["y0"]) / tot
    if y <= yb1: return (Vh + A * (y - yb0)) / tot
    if y >= q["y1"]: return 1.0
    return (tot - cap(q["y1"] - y)) / tot
def _xdiff(a, b, x, y, half=1):
    s = 0
    for dx in range(-half, half + 1):
        ca = _xpx(a, x + dx, y); cb = _xpx(b, x + dx, y); s += max(abs(ca[i] - cb[i]) for i in range(3))
    return s / (2 * half + 1)
def _xtop(base, imgs, x, r0, r1, thr=12):   # 빈 탱크 그림과 달라진 맨 윗줄(찍은 두 그림 모두에서) = 그린 액면
    for r in range(int(math.floor(r0)), int(math.ceil(r1)) + 1):
        if all(_xdiff(im, base, x, r) > thr for im in imgs): return r
    return None
def _xmed(v):
    v = sorted(v); return v[len(v) // 2] if v else None
def _xrim(imgs, x, e):   # 정제기 액면 테두리: 세로 11줄 가운데 값 · 두 그림의 작은 값(지나가는 흰 증기 점을 지움) → 액면 위 기체 칸(e−30 ~ e−18줄) 색에서 20 넘게 달라지는 줄이 4줄 넘게 이어지는 첫 줄(탱크 윤곽 · 자켓 테두리 같은 1 ~ 3 px 선은 액면으로 치지 않음)
    P = {}
    for r in range(int(e) - 32, int(e) + 32):
        vals = [[_xmed([_xpx(im, x + dx, r)[c] for dx in range(-5, 6)]) for c in range(3)] for im in imgs]
        P[r] = [min(v[c] for v in vals) for c in range(3)]
    bg = [_xmed([P[r][c] for r in range(int(e) - 30, int(e) - 17)]) for c in range(3)]
    dev = lambda r: max(abs(P[r][c] - bg[c]) for c in range(3)) > 20
    for r in range(int(e) - 16, int(e) + 26):
        if all(dev(r + k) for k in range(6)): return r   # v142: 4 → 6줄 — 자켓 아래 테두리 반사(흰 줄 4줄)가 액면 바로 위에 올 때(50 h 115 kg) 그 줄을 액면으로 골랐다. 액 몸통은 20줄 넘게 이어진다
    return None
def _xfirst(lg, cond, key=0):
    for r in lg:
        try:
            if cond(r): return r[key]
        except Exception: pass
    return None
def _xnum(s):
    m = re.search(r"-?\d+(?:\.\d+)?", s or ""); return float(m.group(0)) if m else None

def _xhs(pix):   # 색이 있는 화소(채도 · 밝기 0.25 넘음)의 색상 · 채도 가운데 값과 화소 수
    hs = [h for h in (_xhue(c) for c in pix) if h[1] >= 0.25 and h[2] >= 0.25]
    return (_xmed([h[0] for h in hs]), _xmed([h[1] for h in hs]), len(hs)) if hs else (None, None, 0)
def _xsegpix(imgs, s):   # 관 토막(화면 p0 → p1, 반지름 rpx)의 가운데 띠 화소
    (x0, y0), (x1, y1) = s["p0"], s["p1"]; L = math.hypot(x1 - x0, y1 - y0) or 1; nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    return [_xpx(im, x0 + (x1 - x0) * i / 12 + nx * j * s["rpx"], y0 + (y1 - y0) * i / 12 + ny * j * s["rpx"]) for im in imgs for i in range(13) for j in (-0.4, -0.2, 0, 0.2, 0.4)]
def _xdeg(h): return None if h is None else round(h * 360)

def _xlevels3d(lad, base, imgsA, imgsB, key):   # 받는 탱크 하나: (계산 부피 비, 화면 부피 비, 액면 줄, 기대 줄)
    q = lad[key]; ys, xs, rs = _xlad(q["lad"]); x = _xmed(xs); r0 = min(rs) - 3; r1 = max(rs) + 3
    top = _xtop(base, [imgsA, imgsB], x, r0, r1)
    if top is None: return q["frac"], (0.0 if q["frac"] < 0.003 else None), None
    y = _xinterp(top, rs, ys); return q["frac"], _xves_frac(q, y), top

L3 = "3D(가벼움 · 지금 화면)"

def _xj_valve(g, add):   # (A) 밸브 조작
    # ---------------- (A) 밸브 조작 ----------------
    sn = "현실성 밸브 조작"; A = {k: g(sn, k) for k in ("a_f0", "a_fc", "a_reopen", "a_x10", "a_x10_2d", "a_x11", "a_x11_2d", "a_x59_0", "a_x59_2d", "a_x59_1", "a_pool0", "a_pool", "a_ov2d", "a_ovseg")}
    # v135 사본(조율 쪽 지시 11-23): X26 · X10 · X11을 v134 규칙(사용자 지적 5 '밸브를 닫으면 관이 갑자기 가득')으로 — 닫힌 밸브 앞에 남는 액은 닫는 순간 모인 액 + 그 관으로 오는
    #  계산 유량만큼 밸브에서 위로 차는 액(관 채움 FILL.plug · f.pls)뿐이고, 흐르던 가는 액은 빠진다. 전 판정(v130 규칙)은 '닫힌 밸브 앞 관 전체가 남음'을 앞머리 값(FILL.head)으로 쟀다 —
    #  v134는 고인 액 끝을 앞머리 값에 적어 두어 3D 줄은 통과했지만 화면에는 고인 액만 있었다. 그래서 그린 액 길이(흐르는 · 빠지는 구간 ∪ 고인 구간, 점검.py H.drawn)와 고인 액(FILL.plug)으로 잰다.
    ro = A["a_reopen"]
    if ro and ro.get("lg"):
        lg = ro["lg"]; Lt = ro["Lt"]; i0 = next((i for i, r in enumerate(lg) if r[2] == 1), None)
        if i0 is not None and i0 > 0 and lg[i0][3][0] and len(lg[i0][3][0]) > 4:
            mx = {"P": 0, "F": 0}; rt0 = lg[i0][0]; gap = 0; first = {}
            for i in range(i0, len(lg)):
                if lg[i][0] - rt0 > 6: break
                gap = max(gap, lg[i][0] - lg[i - 1][0])
                for j, k in ((0, "P"), (1, "F")):
                    a, b = lg[i - 1][3][j], lg[i][3][j]
                    if a and b and a[4] is not None and b[4] is not None: mx[k] = max(mx[k], abs(b[4] - a[4]) / Lt[k])
                    if b and b[6] == 1 and k not in first: first[k] = (round(lg[i][0] - rt0, 2), round((b[4] or 0) / Lt[k], 3))
            pb = (lg[i0 - 1][3][0][4] or 0) / Lt["P"]; fb = (lg[i0 - 1][3][1][4] or 0) / Lt["F"]
            add("X26", f"닫았던 초류 밸브(XV-H074)를 다시 열 때 — {L3}: 한 기록(0.1 s) 사이 그린 액 길이(흐르는 구간 ∪ 고인 구간)의 변화가 관 길이의 0.5를 넘지 않는다 — 관이 한 걸음에 가득 차거나 한 번에 사라지지 않고, 새 흐름 앞머리는 관 시작부터 나아간다(v135 사본: v134 규칙 — 닫혀 있는 동안 남는 액은 밸브 앞에 모인 액뿐. 전 판정은 v130 규칙의 앞머리 값)",
                max(mx.values()) <= 0.5, f"연 직전 그린 액 유출 관 {pb:.3f} · 초류 가지 {fb:.3f}(관 길이 비) · 한 기록 사이 최대 변화 유출 관 {mx['P']:.2f} · 초류 가지 {mx['F']:.2f} · 흐르기 시작한 때(연 뒤 s, 그린 액) {first} · 기록 간격 최대 {gap:.2f} s", "≤ 0.5(관 길이 비)")
        else:
            add("X26", f"닫았던 초류 밸브(XV-H074)를 다시 열 때 — {L3}: (v135 사본 기록 없음 — 그린 액 길이가 없는 옛 기록)", None, "-", "-")
    x10, x10b = A["a_x10"], A["a_x10_2d"]
    if x10:
        f = x10["fill"]; p, fb, fl = f["P"], f["F"], f["FL"]
        if len(fb) > 11:
            sv = fb[7]; pl = fb[9] or 0; ends = [q[1] for q in (fb[10] or [])]; atv = sv is not None and any(abs(e - sv) <= 0.01 for e in ends)
            ok = x10["VLV"]["F"] == 0 and pl > 0 and atv and fb[11] <= pl + 0.01 and (p[11] or 0) <= (p[9] or 0) + 0.01 and (fl[11] or 0) <= 0.005
            add("X10", f"받는 밸브(XV-H074)를 닫은 뒤 닫힌 밸브 앞 관의 액 — {L3}: 닫고 6초 뒤 초류 가지에는 밸브 앞에 모인 액(밸브 자리 ± 1 cm에서 끝남)만 남고, 막힌 유출 관도 관 끝에 모인 액뿐, 밸브 뒤 입구 관은 빈다(v135 사본: v134 규칙 — 전 판정 '유출 관 전체가 남음'은 사용자 지적 5의 '밸브를 닫으면 관이 갑자기 가득'이라 바꿈)", ok,
                f"초류 가지 고인 액 {pl:.3f} m · 고인 구간 끝 {ends} (밸브 자리 {sv}) · 그린 액 {fb[11]:.3f} m · 유출 관 그린 액 {p[11]} m(고인 액 {p[9]}) · 입구 관 그린 액 {fl[11]} m", "고인 액 > 0 · 끝 = 밸브 자리 ± 0.01 m · 그린 액 ≤ 고인 액 + 0.01 m · 유출 관 그린 액 ≤ 고인 액 + 0.01 m · 입구 관 ≤ 0.005 m")
    if x10b and not x10b.get("hidden"):
        img = _xpng("x_a_x10_2d.png"); vF = (x10b.get("valves") or {}).get("F"); ptsP = x10b["pts"]["P"]; ptsF = [q for q in x10b["pts"]["F"] if vF and q[0] <= vF[0] - 6]
        dF = lambda q: math.hypot(q[0] - vF[0], q[1] - vF[1]); near = [q for q in ptsF if dF(q) <= 30]; far = [q for q in ptsF if dF(q) > 120]
        cN, cX, cP, cA = _xcover(img, near), _xcover(img, far), _xcover(img, ptsP), _xcover(img, ptsF); nN = round((cN or 0) * len(near))
        add("X10", "받는 밸브(XV-H074)를 닫은 뒤 닫힌 밸브 앞 관의 액 — 도면: 3D처럼 초류 가지 밸브 바로 앞(30 화소 안)에 멈춘 액 색이 있고(액 색 점 3개 ≈ 4 화소 이상 — 고인 액은 수 cm라 몇 화소), 초류 가지 전체와 유출 관 선은 칠하지 않는다(v135 사본: v134 규칙 — 전 판정은 '유출 관 선 · 초류 가지 전체 ≥ 0.6'. 120 화소 밖 점은 가지가 짧아 있을 때만 봄)",
            cN is not None and cA is not None and cP is not None and nN >= 3 and cA <= 0.6 and (cX is None or cX <= 0.15) and cP <= 0.2, f"액 색 점: 초류 가지 밸브 앞 30 화소 안 {nN}점 / {len(near)}점 · 밸브 앞 가지 전체 몫 {cA if cA is None else round(cA, 2)}({len(ptsF)}점) · 120 화소 밖 {cX if cX is None else round(cX, 2)}({len(far)}점) · 유출 관 선 {cP if cP is None else round(cP, 2)}({len(ptsP)}점) · 흐름 점 상태 P {x10b['st'].get('P')} · F {x10b['st'].get('F')}", "≥ 3점 · ≤ 0.6 · ≤ 0.15(점이 있으면) · ≤ 0.2")
    x11, x11b = A["a_x11"], A["a_x11_2d"]
    if x11:
        f = x11["fill"]; p, fb, fl = f["P"], f["F"], f["FL"]
        if len(p) > 11:
            sv = p[7]; pl = p[9] or 0; ends = [q[1] for q in (p[10] or [])]; atv = sv is not None and any(abs(e - sv) <= 0.01 for e in ends)
            ok = x11["VLV"]["P"] == 0 and pl > 0 and atv and p[11] <= pl + 0.01 and (fb[11] or 0) <= 0.005 and (fl[11] or 0) <= 0.005
            add("X11", f"유출 밸브(FCV-H072)를 닫은 뒤 — {L3}: 닫고 6초 뒤 유출 관에는 밸브 위에 모인 액(밸브 자리 ± 1 cm에서 끝남)만 남고, 아래 초류 가지 · 입구 관은 열린 받는 탱크로 빠져 빈다(v135 사본: v134 규칙 — 전 판정은 앞머리 값이 밸브 자리)", ok,
                f"유출 관 고인 액 {pl:.3f} m · 고인 구간 끝 {ends} (밸브 자리 {sv}) · 그린 액 {p[11]:.3f} m · 초류 가지 그린 액 {fb[11]} · 입구 관 {fl[11]} m", "고인 액 > 0 · 끝 = 밸브 자리 ± 0.01 m · 그린 액 ≤ 고인 액 + 0.01 m · 초류 가지 · 입구 관 ≤ 0.005 m")
    if x11b and not x11b.get("hidden"):
        img = _xpng("x_a_x11_2d.png"); vP = (x11b.get("valves") or {}).get("P"); up = [q for q in x11b["pts"]["P"] if vP and q[1] <= vP[1] - 6]
        dP = lambda q: math.hypot(q[0] - vP[0], q[1] - vP[1]); near = [q for q in up if dP(q) <= 30]; far = [q for q in up if dP(q) > 120]
        cN, cX, cU = _xcover(img, near), _xcover(img, far), _xcover(img, up); nN = round((cN or 0) * len(near))
        add("X11", "유출 밸브(FCV-H072)를 닫은 뒤 — 도면: 밸브 바로 위(30 화소 안)에 멈춘 액 색이 있고(액 색 점 3개 ≈ 4 화소 이상 — 고인 액은 수 cm라 몇 화소), 밸브 위 유출 관 전체는 칠하지 않는다(v135 사본: v134 규칙 — 전 판정은 '밸브 위 유출 관 전체 ≥ 0.6'. 120 화소 밖 점은 캡처 안에 있을 때만 봄)",
            cN is not None and cU is not None and nN >= 3 and cU <= 0.6 and (cX is None or cX <= 0.15), f"액 색 점: 밸브 위 30 화소 안 {nN}점 / {len(near)}점 · 밸브 위 전체 몫 {cU if cU is None else round(cU, 2)}({len(up)}점) · 120 화소 밖 {cX if cX is None else round(cX, 2)}({len(far)}점) · 흐름 점 상태 P {x11b['st'].get('P')}", "≥ 3점 · ≤ 0.6 · ≤ 0.15(점이 있으면)")
    s0, s1 = A["a_x59_0"], A["a_x59_1"]
    if s0 and s1:
        h0, h1 = s0["R"][0], s1["R"][0]; ue = (s0.get("us") or [None, None])[1]
        add("X59", f"환류 밸브를 닫아 U자에 액이 남은 상태에서 도면으로 바꿨다가 3D로 돌아왔을 때 — {L3}: 환류 관의 남은 액 표시가 바꾸기 전과 같다(실 루프 0.55 kg은 계산에 그대로 있다)",
            s0["VR"] == 0 and h0 > 0.05 and abs(h1 - h0) <= 0.01 and s1["R"][5] >= s0["R"][5],
            f"바꾸기 전 환류 관 채움 {h0:.3f} m(U자 끝 {ue}) · 보이는 덧관 {s0['R'][5]}개 → 도면 3초(U자 표시 '{(A['a_x59_2d'] or {}).get('seal2d')}') → 3D 4초 뒤 {h1:.3f} m · 덧관 {s1['R'][5]}개 · 실 루프 {s0['sealM']} → {s1['sealM']} kg", "차 ≤ 0.01 m · 덧관 수 그대로")
    fc = A["a_fc"]
    if fc:
        add("X58", "유출이 막혔을 때의 환류 유량: 레시피 운전에서 초류 밸브를 닫으면 환류가 FICH073 설정을 넘어 응축액 전부로 간다(현장 FICH073 자동이면 설정 유지 · 남는 응축액은 응축기 쪽에 고임) — 참고(사용자 판단 대기)", None,
            f"닫기 전 환류 {(A['a_f0'] or {}).get('R')} · 유출 {(A['a_f0'] or {}).get('Dk')} → 닫고 8초 뒤 환류 {fc['R']} · 유출 {fc['Dk']} · 응축 {fc['cond']} kg/h(FICH073 설정 {fc['sv']} · 레시피 {fc['recipe']})", "현장 제어 방식 확인 뒤 판정")
    po = A["a_pool"]
    if po and po.get("lg"):
        lg = po["lg"]; ic = next((i for i, r in enumerate(lg) if r[19] == 0 and r[20] == 0), None)
        if ic is not None:
            lg = lg[ic:]; rt0 = lg[0][0]
            liqT2 = lambda f: bool(f) and f[5] > 0 and f[6] == 0   # 증기 관(T2)이 액 모양(fillLook 액)으로 보이는 덧관
            liqL2 = lambda f: bool(f) and f[5] > 0                 # 액 관(L2)에 덧관이 보임
            c1b = lg[0][5] or 0   # 닫을 때 그린 액막(고임 0이어도 바닥에 얇게 그리는 표시 규칙) — 그 위로 1 mm 오르면 '액면이 차기 시작'
            t_spl = _xfirst(lg, lambda r: r[2] > 0.02); t_cp = _xfirst(lg, lambda r: r[3] > 0.02); t_c1 = _xfirst(lg, lambda r: (r[5] or 0) > c1b + 0.001); t_ovs = _xfirst(lg, lambda r: r[6] > 0.05); t_ovv = _xfirst(lg, lambda r: liqT2(r[9]) and liqL2(r[10]))
            rel = lambda t: None if t is None else round(t - rt0, 1)
            seq = [t_spl, t_cp, t_c1, t_ovv]
            add("X13", f"환류 · 유출을 모두 닫았을 때 차오르는 순서 — {L3}: 분배기(계산 채움) → 응축액 관(계산 채움) → 1차 응축기 그린 액면 → 넘어가는 액(미응축 증기 관 T2 · 2차 응축기 → 초류 관 L2가 액 모양) 순서. 뒤바뀐 곳 0",
                all(t is not None for t in seq) and all(a <= b for a, b in zip(seq, seq[1:])), f"닫고 분배기 +{rel(t_spl)} s → 응축액 관 +{rel(t_cp)} s → 그린 응축기 액면(바닥 액막 {c1b} m 위로 1 mm) +{rel(t_c1)} s → 계산 넘침 +{rel(t_ovs)} s → T2 · L2 액 모양 +{rel(t_ovv)} s", "순서대로 · 모두 나타남")
            rise = [r for r in lg if r[4] >= 0.03 and (t_ovs is None or r[0] < t_ovs)]; after = [r for r in lg if t_ovs is not None and r[0] >= t_ovs + 3]
            e1 = max((abs((r[5] or 0) - r[4]) / r[4] for r in rise), default=None); e2 = max((abs((r[5] or 0) - r[4]) / r[4] for r in after), default=None)
            add("X1", f"1차 응축기 고임 — {L3}: 그린 액면 높이 = 계산 액위(차오르는 동안 3 cm 넘으면 ± 10 % — 매끈하게 따라가는 표시 규칙의 지연 몫, 넘치기 시작하고 3초 뒤부터 ± 2 %)",
                e1 is not None and e2 is not None and e1 <= 0.10 and e2 <= 0.02, f"차오르는 동안 최대 차 {e1 if e1 is None else f'{100 * e1:.1f} %'}({len(rise)}기록) · 넘친 뒤 {e2 if e2 is None else f'{100 * e2:.1f} %'}({len(after)}기록) · 멈춘 액위 {lg[-1][4]} m / 그림 {lg[-1][5]} m", "≤ 10 % · ≤ 2 %")
            add("X2", f"고임이 옆 노즐을 넘을 때 — {L3}: 계산 넘침이 시작되고 화면 1초 안에 미응축 증기 관(T2)과 2차 응축기 → 초류 관(L2)이 액이 찬 모양(액 덧관)으로 바뀐다(색은 '넘어가는 액의 색' 줄이 따로 본다)",
                t_ovs is not None and t_ovv is not None and t_ovv - t_ovs <= 1.0, f"계산 넘침 > 0.05 kg/h +{rel(t_ovs)} s → T2 · L2 액 모양 +{rel(t_ovv)} s(차 {None if t_ovs is None or t_ovv is None else round(t_ovv - t_ovs, 2)} s) · T2 색 {lg[-1][9][8] if lg[-1][9] else None} · L2 색 {lg[-1][10][8] if lg[-1][10] else None}", "≤ 1.0 s")
            win = [r for r in lg if t_ovs is not None and r[0] >= t_ovs + 2]
            if len(win) >= 2 and win[-1][1] - win[0][1] > 60:
                dt = (win[-1][1] - win[0][1]) / 3600; rate = (win[-1][7] - win[0][7]) / dt; ovm = sum(r[6] for r in win) / len(win); cdm = sum(r[8] for r in win) / len(win)
                add("X2", "넘치는 동안의 양(X1 · X2 · X13): 초류 탱크 무게 증가율 = 넘침 유량 ± 5 %, 넘침 = 응축 ± 5 %(1차 응축기에 더 고이지 않고 응축한 만큼 넘어간다)",
                    ovm > 0.5 and abs(rate - ovm) <= 0.05 * ovm and abs(ovm - cdm) <= 0.05 * cdm, f"공정 {dt * 60:.1f}분 동안 초류 증가 {rate:.2f} kg/h · 넘침 평균 {ovm:.2f} · 응축 평균 {cdm:.2f} kg/h", "± 5 % · ± 5 %")
            t9 = rt0 + 9; pw = [r for r in lg if r[0] >= t9 and (t_ovs is None or r[0] < t_ovs) and r[11] > 0]
            if pw:
                ratio = sum(r[12] / r[11] for r in pw) / len(pw); share = sum(r[14] for r in pw) / len(pw); mxr = max(r[12] / r[11] for r in pw)
                add("X14", f"응축액이 고이는 동안 증기 점이 가는 길 — {L3}: 1차 응축기 뒤 구간(미응축 증기 관 · 2차 응축기 · 진공 라인)의 증기 점 ÷ 전체 증기 점 ≤ 계산 몫(2차 응축 + 펌프 손실) + 5 %p(실제: 응축 능력이 남아 있으면 1차에서 다 응축)",
                    ratio <= share + 0.05, f"닫고 9초 ~ 넘치기 전({len(pw)}기록): 응축기 뒤 증기 점 비 평균 {ratio:.3f}(최대 {mxr:.3f}) · 계산 몫 평균 {share:.4f} · 2차 응축 {lg[-1][16]} kg/h · 펌프 손실 {lg[-1][17]} kg/h", "≤ 계산 몫 + 0.05")
    ov2 = A["a_ov2d"]
    if ov2 and not ov2.get("hidden"):
        img = _xpng("x_a_ov_2d.png"); onT2 = [s for s in ov2["T2"]["st"] if s[0] == 1]; blue = bool(onT2) and all(_xisblue(s[2]) for s in onT2); cov = _xcover(img, ov2["T2"]["pts"])
        add("X2", "고임이 옆 노즐을 넘는 동안 — 도면: 미응축 증기 관(T2)으로 넘어가는 것은 액이라 T2의 흐름 점이 액 색(파랑)이다(계산: 2차로 가는 증기 몫 ≈ 0)",
            (ov2["ov"] or 0) > 1 and blue and cov is not None and cov >= 0.08, f"넘침 {ov2['ov']} kg/h · 2차로 가는 증기 몫 {ov2['fr2']} · T2 흐름 점 {ov2['T2']['st']} · T2 선의 액 색 점 몫 {cov if cov is None else round(cov, 2)} · L2 흐름 점 {ov2['L2']['st']}", "켜짐 · 액 색 · 액 색 점 ≥ 0.08")
        sg = A["a_ovseg"]; imgs = [i for i in (_xpng("x_a_ov_seg_a.png"), _xpng("x_a_ov_seg_b.png")) if i]
        if sg and imgs and "T2" in sg["seg"] and "L2" in sg["seg"]:
            hT, sT, nT = _xhs(_xsegpix(imgs, sg["seg"]["T2"])); hL, sL, nL = _xhs(_xsegpix(imgs, sg["seg"]["L2"])); lgp = (A["a_pool"] or {}).get("lg") or [[None] * 21]
            add("X2", f"넘어가는 액의 색 — {L3}: 넘치는 동안 미응축 증기 관(T2)에 찬 액이 바로 이어지는 2차 응축기 → 초류 관(L2)의 액과 같은 색으로 보인다(같은 액, 화면 화소 색상 차 ≤ 22°)",
                hT is not None and hL is not None and abs(hT - hL) <= 0.06, f"T2 화소 색상 {_xdeg(hT)}° · 채도 {sT if sT is None else round(sT, 2)}({nT}화소) · L2 {_xdeg(hL)}° · {sL if sL is None else round(sL, 2)}({nL}화소) · 덧관 재질 색 T2 {(lgp[-1][9] or [None] * 9)[8]} · L2 {(lgp[-1][10] or [None] * 9)[8]}", "색상 차 ≤ 22°")
        c1 = ov2["c1"]
        if c1.get("hpx") is not None and c1.get("hC1"):
            exp = c1["hC1"] * c1["k"]
            add("X1", "1차 응축기 고임 — 도면: 고임 사각형 높이 = 계산 액위(± 2 %, 1 px 아래 차는 같게 본다)", abs(c1["hpx"] - exp) <= max(1.0, 0.02 * exp), f"사각형 {c1['hpx']} px · 계산 {c1['hC1']} m × {c1['k']:.1f} px/m = {exp:.1f} px", "± 2 %")

def _xj_tank(g, add):   # (B) 받는 탱크 가득 참
    # ---------------- (B) 받는 탱크 가득 참 ----------------
    sn = "현실성 받는 탱크 가득 참"; B = {k: g(sn, k) for k in ("b_lad0", "b_lad_near", "b_near_2d", "b_lad_lah", "b_lah10", "b_lah_2d", "b_spill", "b_lad_spill", "b_spill_2d", "b_spill2", "b_log")}
    bl = B["b_log"]
    if bl and bl.get("lg"):
        lg = bl["lg"]; il = next((i for i, r in enumerate(lg) if r[6] is not None), None)
        if il is not None:
            tl = lg[il][1]; fl0 = lg[il][2]
            closed = next((r for r in lg[il:] if r[1] <= tl + 60 and r[3] == 0 and r[4] == "false" and _xisred(r[5])), None)
            ring = next((r for r in lg[il:] if r[8] == 1 and r[0] - lg[il][0] <= 2), None); l10 = B["b_lah10"]; inc = (l10["fore"] - fl0) if l10 else None
            red = None; bl0, ll = _xpng("x_b0_fore.png"), _xpng("x_b_lah_fore_a.png"); ld = B["b_lad_lah"]
            if bl0 and ll and ld:
                q = ld["fore"]; rx, ry = q["ring"]; tx = q["top"][0]; rp = abs(q["spx"] - tx) / 1.02; cnt = lambda im: sum(1 for y in range(int(ry - 26), int(ry + 9)) for x in range(int(tx - 1.3 * rp), int(tx + 1.3 * rp)) if (lambda c: c[0] > 200 and c[1] < 150 and c[2] < 150)(_xpx(im, x, y)))
                red = cnt(ll) - cnt(bl0)
            v2 = (B["b_lah_2d"] or {}).get("valveF") or []
            ok = bool(closed) and inc is not None and inc <= 0.05 and l10["VLV"]["F"] == 0 and bool(ring) and red is not None and red >= 30 and any("shut" in c for c in v2)
            add("X8", f"받는 탱크 LT HH(97 %)에서 받는 밸브가 닫힘 — {L3} · 도면: 97 % 도달 뒤 공정 60초 안에 초류 밸브가 닫힘(밸브 빨강 · 밸브 줄 단추 · 도면 밸브)이고 닫힌 채 공정 10분 동안 초류 증가 ≤ 0.05 kg, LT HH 고리가 화면에 보인다(실제: LT HH Interlock이 닫고 운전원이 열 때까지 그대로 — v145부터 레시피도 다시 열지 않는다)",
                ok, f"LT HH {tl / 3600:.2f} h 초류 {fl0:.3f} kg → 60초 안 닫힘 {'있음' if closed else '없음'}(밸브 상태 {lg[min(len(lg) - 1, il + 20)][3]} · 단추 {lg[min(len(lg) - 1, il + 20)][4]} · 색 {lg[min(len(lg) - 1, il + 20)][5]}) · 10분 뒤 초류 +{inc if inc is None else round(inc, 3)} kg(밸브 {l10['VLV']['F'] if l10 else None}, 단계 {l10['st'] if l10 else None}) · 고리 보임 {'있음' if ring else '없음'} · 고리 자리 빨간 화소 +{red} · 도면 밸브 {v2}",
                "60초 안 닫힘 · ≤ 0.05 kg · 고리 보임 · 도면 닫힘")
        isp = next((i for i, r in enumerate(lg) if r[7] > 0.05), None)
        sp, sp2, lsp = B["b_spill"], B["b_spill2"], B["b_lad_spill"]
        if isp is not None and sp and sp2 and lsp:
            fxr = next((r for r in lg[isp:] if r[9] == 1 and r[10] == 1), None); dtv = None if not fxr else round(fxr[0] - lg[isp][0], 2)
            base, a, b = _xpng("x_b0_fore.png"), _xpng("x_b_spill_fore_a.png"), _xpng("x_b_spill_fore_b.png"); frac_rows = None; hue = hueT = (None, None, 0)
            if base and a and b:
                q = lsp["fore"]; x = q["spx"]; r0, r1 = int(q["top"][1]), int(q["bot"][1] + 10); rows = list(range(r0, r1 + 1))
                ch = [r for r in rows if any(_xdiff(a, base, x + dx, r, 0) > 25 and _xdiff(b, base, x + dx, r, 0) > 25 for dx in (-2, 0, 2))]
                frac_rows = len(ch) / max(1, len(rows))
                hue = _xhs([_xpx(a, x + dx, r) for r in ch for dx in (-1, 0, 1) if _xdiff(a, base, x + dx, r, 0) > 25])   # 넘침 줄기 화소
                ys_, xs_, rs_ = _xlad(q["lad"]); xl = _xmed(xs_)
                hueT = _xhs([_xpx(a, xl + dx, r) for r in range(int(min(rs_)) + 6, int(max(rs_)) - 5) for dx in (-1, 0, 1) if _xdiff(a, base, xl + dx, r, 0) > 25])   # 같은 그림의 탱크 안 액 화소
            dt = (sp2["t"] - sp["t"]) / 3600; rate = (sp2["spill"][0] - sp["spill"][0]) / dt if dt > 0 else None; inflow = ((sp["Dk"] or 0) + (sp2["Dk"] or 0)) / 2
            add("X9", f"받는 탱크가 가득 찬 뒤에도 들어오면 넘침 — {L3}: 넘친 양 > 0.05 kg이면 화면 2초 안에 넘침 줄기 · 바닥 웅덩이가 보이고(그림 화소: 탱크 옆 줄기 자리의 30 % 넘는 줄이 빈 탱크 그림과 다름), 넘친 양 증가율 = 들어오는 유량 ± 5 %",
                dtv is not None and dtv <= 2 and frac_rows is not None and frac_rows >= 0.3 and rate is not None and inflow > 0 and abs(rate - inflow) <= 0.05 * inflow,
                f"넘침 시작 {lg[isp][1] / 3600:.2f} h → 줄기 · 웅덩이 보임 +{dtv} s · 줄기 자리 달라진 줄 몫 {frac_rows if frac_rows is None else round(frac_rows, 2)} · 넘친 양 증가 {rate if rate is None else round(rate, 2)} kg/h · 들어오는 유량(유출) {inflow:.2f} kg/h", "≤ 2 s · ≥ 0.3 · ± 5 %")
            add("X9", f"넘침 줄기 · 웅덩이의 색 — {L3}: 넘친 것은 탱크 안 액과 같은 액이므로 같은 색으로 보인다(같은 그림에서 넘침 줄기 화소와 탱크 안 액 화소의 색상 차 ≤ 22°)",
                hue[0] is not None and hueT[0] is not None and abs(hue[0] - hueT[0]) <= 0.06, f"넘침 줄기 색상 {_xdeg(hue[0])}° · 채도 {hue[1] if hue[1] is None else round(hue[1], 2)}({hue[2]}화소) · 탱크 안 액 {_xdeg(hueT[0])}° · {hueT[1] if hueT[1] is None else round(hueT[1], 2)}({hueT[2]}화소)", "색상 차 ≤ 22°")
        t2l, t2s = B["b_lah_2d"], B["b_spill_2d"]
        if t2l and t2s and not t2l.get("hidden") and not t2s.get("hidden"):
            il2, is2, in2 = _xpng("x_b_lah_2d.png"), _xpng("x_b_spill_2d.png"), _xpng("x_b_near_2d.png"); redL = blueS = None; t2n = B.get("b_near_2d") or {}
            same = bool(in2) and t2n.get("rect") == t2l.get("rect") == t2s.get("rect")   # LT HH 전 도면 그림과 같은 자리를 찍었으면, 그때 없던 색만 센다(범례 · 밸브 기호 같은 늘 있는 색은 빠짐)
            isred = lambda c: c[0] > 190 and c[1] < 130 and c[2] < 130
            if il2:
                (x0, y0), (x1, y1) = t2l["tank"]; vp = t2l.get("vpos") or []; offv = lambda x, y: all(math.hypot(x - v[1], y - v[2]) > v[3] for v in vp)   # 밸브 기호(닫히면 빨강)는 빼고 센다
                redL = sum(1 for y in range(int(y0 - 30), int(y0 + 0.2 * (y1 - y0))) for x in range(int(x0 - 40), int(x1 + 40)) if offv(x, y) and isred(_xpx(il2, x, y)) and not (same and isred(_xpx(in2, x, y))))
            if is2:
                (x0, y0), (x1, y1) = t2s["tank"]; blueS = sum(1 for y in range(int(y0), int(y1 + 28)) for x in range(int(x1 + 3), int(x1 + 38)) if _xblue(_xpx(is2, x, y)) and not (same and _xblue(_xpx(in2, x, y))))
            okL = bool(t2l["hits"]) or (redL is not None and redL >= 30); okS = bool(t2s["hits"]) or (blueS is not None and blueS >= 40)
            add("X9", "받는 탱크 LT HH · 넘침 — 도면: LT HH가 되면 표시(요소 또는 탱크 둘레 빨간 표시)가 보이고, 넘치면 넘침 표시(요소 또는 탱크 옆 액 색)가 보인다(도면 그림 화소 · 요소)",
                okL and okS, f"LT HH 때 표시 요소 {t2l['hits'] or '0개'} · 새로 생긴 빨간 화소 {redL} · 밸브 {t2l['valveF']} / 넘침 때(넘친 양 {t2s['spill']} kg) 표시 요소 {t2s['hits'] or '0개'} · 탱크 옆에 새로 생긴 액 색 화소 {blueS}" + ("" if same else " · LT HH 전 기준 그림 없음(늘 있는 색도 셈)"), "LT HH 표시 · 넘침 표시 모두 있음")

def _xj_level(g, add):   # 액면(받는 탱크 · 정제기)
    # ---------------- 액면(받는 탱크 · 정제기) ----------------
    sn = "현실성 받는 탱크 가득 참"; B = {k: g(sn, k) for k in ("b_lad_near", "b_lad_spill")}
    rows7 = []; ok7 = True
    E = {k: g("현실성 액면 · 배치 끝", k) for k in ["e_lad0", "e_end_log", "e_end_3d", "e_end_ga", "e_end_2d", "e_end_ga2"] + [f"{p}{h}" for h in (6, 30, 50) for p in ("e_lad", "e_rate", "e_seg", "e_p2_")]}
    base = {k: _xpng(f"x_e0_{k}.png") for k in ("fore", "main")}
    for h in (6, 30, 50):
        ld = E[f"e_lad{h}"]
        if not ld: continue
        for k in ("fore", "main"):
            a, b = _xpng(f"x_e{h}_{k}_a.png"), _xpng(f"x_e{h}_{k}_b.png")
            if not (a and b and base[k]): rows7.append(f"{h} h {k} 그림 없음"); ok7 = False; continue
            fc, fm, top = _xlevels3d(ld, base[k], a, b, k)
            if fm is None or abs(fm - fc) > 0.03: ok7 = False
            rows7.append(f"{h} h {'초류' if k == 'fore' else '본류'} {ld[k]['m']:.1f} kg 계산 {100 * fc:.1f} % · 화면 {'-' if fm is None else f'{100 * fm:.1f} %'}")
    for tg, nm in (("b_lad_near", "LT HH 직전"), ("b_lad_spill", "넘침")):
        ld = B.get(tg); bb0 = _xpng("x_b0_fore.png"); stem = {"b_lad_near": "x_b_near_fore", "b_lad_spill": "x_b_spill_fore"}[tg]; a, b = _xpng(stem + "_a.png"), _xpng(stem + "_b.png")
        if ld and bb0 and a and b:
            fc, fm, top = _xlevels3d(ld, bb0, a, b, "fore")
            if fm is None or abs(fm - fc) > 0.03: ok7 = False
            rows7.append(f"{nm} 초류 {ld['fore']['m']:.1f} kg 계산 {100 * fc:.1f} % · 화면 {'-' if fm is None else f'{100 * fm:.1f} %'}")
    if rows7:
        add("X7", f"받는 탱크 액면 = 계산 부피(X7 · X37) — {L3}: 화면 그림에서 빈 탱크 그림과 달라진 맨 윗줄(액면)을 높이로 바꾸고 그린 탱크 형상(2:1 타원 경판 + 몸통)으로 구한 부피 비 = 무게 ÷ 밀도 ÷ 용량 ± 3 %p", ok7, " · ".join(rows7), "± 3 %p")
    rows36 = []; ok36 = True
    for h in (6, 30, 50):
        ld = E[f"e_lad{h}"]; a, b = _xpng(f"x_e{h}_still_a.png"), _xpng(f"x_e{h}_still_b.png")
        if not (ld and a and b): continue
        q = ld["still"]; ys, xs, rs = _xlad(q["lad"]); x = _xmed(xs); e = q["exp"][1]; rim = _xrim([a, b], x, e)
        if rim is None or abs(rim - e) > 3: ok36 = False
        vexp = q["m"] / q["rho"]; R, hh, hm = q["R"], q["hh"], q["h"]; A_ = math.pi * R * R; vh = A_ * hm * hm * (3 * hh - hm) / (3 * hh * hh) if hm <= hh else A_ * hh * 2 / 3 + A_ * (hm - hh)
        if abs(vh - vexp) > 0.005 * vexp: ok36 = False
        rows36.append(f"{h} h {q['m']:.1f} kg: 벽 쪽 액면 기대 줄 {e:.1f} · 화면 {rim} · 형상 부피 차 {100 * (vh - vexp) / vexp:+.2f} %")
    if rows36:
        add("X36", f"정제기 액면 = 무게 · 형상 — {L3}: 화면 그림의 액면 테두리 줄 = 계산 벽 쪽 액면(와류 포함)의 줄 ± 3 px, 평균 액 높이의 형상 부피 = 무게 ÷ 밀도 ± 0.5 %", ok36, " · ".join(rows36), "± 3 px · ± 0.5 %")
    r2 = []; ok2a = ok2b = True; n2 = 0
    for h in (6, 30, 50):
        p = E[f"e_p2_{h}"]
        if not p or p.get("hidden"): continue
        n2 += 1; yof = lambda sy: p["mY"][0] + (p["mY"][1] - p["mY"][0]) * sy / 1000
        for k in ("fore", "main"):
            q = p[k]; fm = 0.0 if not q["box"] else _xves_frac(q, yof(q["box"][1]))
            if abs(fm - q["frac"]) > 0.03: ok2a = False
            r2.append(f"{h} h {'초류' if k == 'fore' else '본류'} 계산 {100 * q['frac']:.1f} % · 도면 {100 * fm:.1f} %")
        s = p["still"]; d = None if not s["box"] else s["box"][1] - s["yh"]
        if d is None or abs(d) > 3: ok2b = False
        r2.append(f"{h} h 정제기 액면 줄 차 {None if d is None else round(d, 1)} px")
    if n2:
        add("X7", "받는 탱크 액면 = 계산 부피(X7 · X37) — 도면: 액 도형의 윗변을 높이로 바꾼 부피 비 = 계산 ± 3 %p", ok2a, " · ".join(x for x in r2 if "정제기" not in x), "± 3 %p")
        add("X36", "정제기 액면 — 도면: 액 도형의 윗변 = 계산 평균 액 높이의 자리 ± 3 px", ok2b, " · ".join(x for x in r2 if "정제기" in x), "± 3 px")
    r40 = []; ok40 = True
    for h in (6, 30, 50):
        rt = E[f"e_rate{h}"]
        if not rt or len(rt["s"]) < 4: continue
        s = rt["s"]; col = 1 if rt["VLV"]["F"] and not rt["VLV"]["M"] else 2; dt = (s[-1][0] - s[0][0]) / 3600
        if dt <= 0: continue
        rate = (s[-1][col] - s[0][col]) / dt; dm = sum(x[3] for x in s) / len(s)
        if dm <= 0 or abs(rate - dm) > 0.05 * dm: ok40 = False
        r40.append(f"{h} h {'초류' if col == 1 else '본류'} 무게 증가 {rate:.3f} · 유출 표시 평균 {dm:.3f} kg/h(공정 {dt * 60:.1f}분)")
    if r40:
        add("X40", "받는 탱크 무게 증가 = 유출 적산: 무게 증가 ÷ 시간 = 유출 표시(FICH072) 평균 ± 5 %", ok40, " · ".join(r40), "± 5 %")
    rat = []
    for h in (6, 30, 50):
        rt = E[f"e_rate{h}"]
        if rt and rt["s"]:
            v = [x[5] / x[4] for x in rt["s"] if x[4] > 1]
            if v: rat.append((f"{h} h", sum(x[4] for x in rt["s"]) / len(rt["s"]), sum(v) / len(v)))
    g1 = g("현실성 스팀 과다 · 펌프 쪽 넘침", "g_1")
    if g1 and (g1["vdot"] or 0) > 1: rat.append(("스팀 과다", g1["vdot"], g1["nv"] / g1["vdot"]))
    if len(rat) >= 2:
        md = _xmed([r[2] for r in rat])
        add("X32", f"증기 점 수 ∝ 증발량 — {L3}: 화면의 증기 점 수 ÷ 증발이 시점마다 같다(가운데 값 ± 20 %, 점 하나 = 같은 양 — 표시 규칙)", all(abs(r[2] - md) <= 0.2 * md for r in rat),
            " · ".join(f"{r[0]} 증발 {r[1]:.1f} kg/h → {r[2]:.1f}개/(kg/h)" for r in rat) + f" · 가운데 값 {md:.1f}", "± 20 %")
    r34 = []; ok34 = True
    for h in (6, 30):
        sg = E[f"e_seg{h}"]; a, b = _xpng(f"x_e{h}_seg_a.png"), _xpng(f"x_e{h}_seg_b.png")
        if not (sg and a and b and "R" in sg["seg"] and "P" in sg["seg"]): continue
        wd = {}
        for k in ("R", "P"):
            s = sg["seg"][k]; (x0, y0), (x1, y1) = s["p0"], s["p1"]; L = math.hypot(x1 - x0, y1 - y0) or 1; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux; ws = []
            for im in (a, b):
                for i in range(9):
                    t = 0.1 + 0.8 * i / 8; cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t; span = s["rpx"] + 5
                    ws.append(0.5 * sum(1 for j in range(int(-2 * span), int(2 * span) + 1) if (lambda c: c[2] > 150 and c[2] - c[0] > 70 and c[1] > 90)(_xpx(im, cx + nx * j * 0.5, cy + ny * j * 0.5))))
            wd[k] = _xmed(ws)
        qR, qP = sg["R"] or 0, sg["Dk"] or 0
        if (qR - qP) * (wd["R"] - wd["P"]) < 0 and abs(wd["R"] - wd["P"]) >= 0.5: ok34 = False
        r34.append(f"{h} h 환류 {qR} kg/h 굵기 {wd['R']} px · 유출 {qP} kg/h 굵기 {wd['P']} px")
    if r34:
        add("X34", f"환류 · 유출 줄기의 많고 적음 — {L3}: 화면의 관 속 액 굵기(파란 화소 너비) 순서 = 유량 순서(뒤바뀜 0, 0.5 px 밑은 같게 봄 — 굵기 식은 표시 규칙)", ok34, " · ".join(r34), "뒤바뀜 0")

def _xj_end(g, add):   # 배치 끝
    # ---------------- 배치 끝 ----------------
    E = {k: g("현실성 액면 · 배치 끝", k) for k in ("e_end_log", "e_end_3d", "e_end_ga", "e_end_2d", "e_end_ga2")}
    el = E["e_end_log"]
    if el and el.get("lg"):
        lg = el["lg"]; isp = next((i for i, r in enumerate(lg) if r[2] == 1), None)
        if isp is not None:
            rts = lg[isp][0]; iv = next((i for i in range(isp, len(lg)) if lg[i][9] < 1), isp); rtv = lg[iv][0]
            late = [r for r in lg if r[0] >= rtv + 10]; z1 = _xfirst(lg[iv:], lambda r: r[3] == 0 and r[4] == 0)
            add("X28", f"가열을 끊으면 증기 표현이 사라짐(배치 끝 가열 정지) — {L3}: 증발이 1 kg/h 아래가 된 뒤 화면 10초 안에 증기 점 0 · 액면 기포 0",
                bool(late) and all(r[3] == 0 and r[4] == 0 for r in late), f"정지 → 증발 1 kg/h 밑 +{rtv - rts:.1f} s → 점 · 기포 0 +{None if z1 is None else round(z1 - rtv, 1)} s · 10초 뒤 최대 점 {max((r[3] for r in late), default=None)} · 기포 {max((r[4] for r in late), default=None)}", "10초 안에 0")
            late = [r for r in lg if r[0] >= rts + 10]; bad = set(); ue = None
            for r in late:
                ue = r[6] if r[6] is not None else ue
                for k, v in r[5].items():
                    if k == "R":
                        if ue is None or abs(v[0] - ue) > 0.01: bad.add("R")
                    elif v[0] - v[1] > 0.002: bad.add(k)
            add("X31", f"배치 끝: 흐름이 멈추고 관이 빔 — {L3}: 정지 뒤 화면 10초 안에 U자 밖 관(증기관 · 응축액 관 · 분배 줄기 · 유출 관 · 받는 가지 · T2 · L2) 채움 0, 환류 관은 U자 끝까지 남음",
                bool(late) and not bad, f"10초 뒤 남은 관 {sorted(bad) or '없음'} · 환류 관 {late[-1][5].get('R') if late else None} m(U자 끝 {ue})", "U자 밖 0 · U자 남음")
    e3, ga, e2, ga2 = E["e_end_3d"], E["e_end_ga"], E["e_end_2d"], E["e_end_ga2"]
    if e3 and ga and e2 and ga2:
        n3 = _xnum(ga.get("txt")); g2 = ga2.get("g2") or {}; n2_ = _xnum(g2.get("num"))
        ok = e3["stopped"] and _xisred(e3["vcol"]["J"]) and n3 is not None and n3 <= 0.05 and "조절 중" not in (ga.get("mode") or "") and n2_ is not None and n2_ <= 0.05 and "조절 중" not in (g2.get("mode") or "")
        add("X19", f"정제기 액위 하한에서 가열 정지 — {L3} · 도면: 정지 뒤 스팀 밸브(TCV-H071) 표시가 닫힘 — 3D 밸브 빨강, 개도 게이지 0 %이고 '자동(PI) 조절 중'이 아님(도면 게이지도 같음)",
            bool(ok), f"정지 {e3['stopped']} · 3D 스팀 밸브 색 {e3['vcol']['J']} · 3D 게이지 '{ga.get('txt')}' · '{ga.get('mode')}'(개도 {ga.get('mv')} %) · 도면 게이지 '{g2.get('num')}' · '{g2.get('mode')}' · 도면 밸브 {e2.get('valveJ')}", "빨강 · 0 % · 조절 중 아님")

def _xj_onset(g, add):   # (C · D) 끓기 시작
    # ---------------- (C · D) 끓기 시작 ----------------
    cl = g("현실성 끓기 시작 3D", "c_log")
    if cl and cl.get("lg"):
        lg = cl["lg"]; hold = cl.get("holdC") or 0.55; F = lambda c: _xfirst(lg, c)
        # 재는 방법 고침(11-22, 시각 경합 — v133 · v132 가벼움에서 드러남). 기준(순서)은 그대로.
        #  ① 응축기 증기 점 = 0.1 s 기록에 응축기 안 점이 보인 첫 기록과, 증기 점 앞머리(VF.head — 끓는 동안 가장 멀리 간 곳을 지킴, 경로 구간 8 = 1차 응축기 안)가 8에 닿은 첫 기록 중 이른 쪽.
        #     응축기에 든 점은 계산의 칸별 응축 깊이(가장 얕으면 3 %)에서 곧 응축해 짧게만 보이고, 끓기 시작 직후에는 점이 드물어 기록 사이에 빠진다.
        #     응축액 관은 앞머리가 8에 닿은 뒤 응축 시작(PR.vpCond)에 차므로, 보인 점만 보면 그림에서는 점이 먼저 닿았어도 기록상 거꾸로 나왔다. 앞머리 열이 없는 지난 기록은 보인 점만 본다.
        #  ② X22 순서는 한 기록(화면 0.1 s) 안의 앞뒤를 같은 때로 본다: 꼭대기 넘음 · 증기관 채움은 점 앞머리가 증기관에 든 뒤 흐름 판정에서 켜져 한 프레임 늦을 수 있고,
        #     채움 2 %가 다음 기록으로 넘어가기도 한다(v133: 점이 든 기록의 채움 0.007 → 다음 기록 0.104). 한 기록 차로 같은 때로 본 곳은 잰 값에 적는다.
        hd = lambda r: len(r) > 19 and r[19] is not None and r[19] >= 8
        def I(c):
            for i, r in enumerate(lg):
                try:
                    if c(r): return i
                except Exception: pass
            return None
        cs = dict(boil=lambda r: r[1] > 1, bub=lambda r: r[2] > 0, tank=lambda r: r[3] > 0, neck=lambda r: r[4] > 0, colLow=lambda r: r[5] > 0, colUp=lambda r: r[6] > 0, top=lambda r: r[10] == 1,
                  V=lambda r: r[12] > 0.02, pipe=lambda r: r[7] > 0, cond=lambda r: r[8] > 0 or hd(r), neckL=lambda r: r[9] > 0, C=lambda r: r[13] > 0.02, R=lambda r: r[14] > 0.02, RD=lambda r: r[15] > 0,
                  seal=lambda r: r[16] >= hold * 0.999, txR=lambda r: (_xnum(r[18]) or 0) > 0.05, rfx=lambda r: len(r) > 20 and (r[20] or 0) > 0)   # rfx136
        ix = {k: I(c) for k, c in cs.items()}; ev = {k: (None if i is None else lg[i][0]) for k, i in ix.items()}
        hasH = any(len(r) > 19 for r in lg); cvis, chd = F(lambda r: r[8] > 0), (F(hd) if hasH else "기록 없음")
        nm = dict(boil="끓음", bub="기포", tank="정제기 위", neck="목관", colLow="컬럼 아래", colUp="컬럼 위", top="꼭대기 넘음", V="증기관 채움", pipe="증기 배관 점", cond="응축기 점")
        ch = ["boil", "bub", "tank", "neck", "colLow", "colUp", "top", "V", "pipe", "cond"]; prs = list(zip(ch, ch[1:]))
        okc = all(ix[k] is not None for k in ch) and all(ix[a] <= ix[b] + 1 for a, b in prs)
        one = [f"{nm[a]} · {nm[b]}" for a, b in prs if ix[a] is not None and ix[b] is not None and ix[a] == ix[b] + 1]
        add("X22", f"끓기 시작: 기포 → 증기가 올라가는 순서 — {L3}: 첫 시각이 끓음 ≤ 기포 ≤ 정제기 위 증기 점 ≤ 목관 ≤ 컬럼 아래 ≤ 컬럼 위 ≤ 꼭대기 넘음 ≤ 증기관 채움 ≤ 증기 배관 점 ≤ 응축기 점. 뒤바뀐 곳 0. 한 기록(화면 0.1 s) 안의 앞뒤는 같은 때로 본다(꼭대기 넘음 · 증기관 채움은 점이 증기관에 든 뒤 켜져 한 기록 갈릴 수 있음). 응축기 점은 점 앞머리가 응축기에 닿은 때도 셈", okc,
            " → ".join(f"{nm[k]} {ev[k]}" for k in ch) + " (공정 분)" + f" · 한 기록 차로 같은 때로 본 곳 {one or '없음'}", "순서대로(한 기록 차는 같은 때)")
        pairs = [("neck", "neckL", "목관 증기 점 → 목관 액 점"), ("cond", "C", "응축기 증기 점 → 응축액 관"), ("C", "R", "응축액 관 → 환류 관"), ("C", "txR", "응축액 관 → 환류 값"), ("seal", "RD", "U자 가득 → 분배 줄기")]
        pre = lambda a, b: min([x for x in (ev[a], ev.get("rfx") if (a, b) == ("C", "R") else None) if x is not None], default=None)   # v136 사본: 환류 관(U자 고인 액)은 응축액 관 또는 빈 환류관 관 벽 응축(계산 PR.rfx.condTot > 0) 뒤
        bad = [n for a, b, n in pairs if ev[b] is not None and (pre(a, b) is None or ev[b] < pre(a, b))]
        add("X24", f"액이 증기보다 먼저 나오지 않음 — {L3}: 목관 액 점은 목관 증기 점 뒤, 응축액 관은 응축기 증기 점 뒤, 환류 관은 응축액 관 또는 빈 환류관 관 벽 응축(계산 쪽 v135c, 첫 {ev.get('rfx')}분) 뒤, 환류 값은 응축액 관 뒤, 분배 줄기는 U자가 찬 뒤. 먼저 나온 곳 0건. 응축기 증기 점은 보인 점의 첫 기록과 점 앞머리(VF.head)가 응축기에 닿은 첫 기록 중 이른 쪽(응축기 안 점은 짧게만 보여 0.1 s 기록 사이에 빠질 수 있음)", not bad,
            " · ".join(f"{n} {ev[a]} → {ev[b]}" for a, b, n in pairs) + f" · 응축기 증기 점: 보인 점 {cvis} · 앞머리 {chd} · 먼저 나온 곳 {bad or '0건'}", "0건")
        pre = [r for r in lg if r[16] < hold * 0.999 and r[1] > 1]; vio = [r for r in pre if r[15] > 0 or (_xnum(r[18]) or 0) > 0.05]
        ts = ev["seal"]; post = None if ts is None else next((r[0] for r in lg if r[0] >= ts and r[15] > 0 and (_xnum(r[18]) or 0) > 0.05), None)
        add("X6", f"환류 U자 액봉이 찬 뒤에야 환류가 흐름 — {L3}: 실 루프가 0.55 kg에 닿기 전 분배 구멍 줄기 0 · 환류 값 0.0, 닿은 뒤 공정 30초 안에 줄기와 환류 값",
            not vio and post is not None and post - ts <= 0.5, f"차는 동안 {len(pre)}기록 중 줄기 · 값이 나온 기록 {len(vio)}개 · U자 가득 {ts}분 → 줄기 · 값 {post}분", "차기 전 0 · 찬 뒤 0.5분 안")
    dl = g("현실성 끓기 시작 도면", "d_log")
    if dl and dl.get("lg"):
        lg = dl["lg"]; hold = dl.get("holdC") or 0.55; on = lambda r, k: (r[7] or {}).get(k, 0) > 0; F = lambda c: _xfirst(lg, c)
        ev = {k: F(lambda r, k=k: on(r, k)) for k in ("VS", "VN", "VC", "V", "CE", "C", "R", "RD", "LS", "LN", "LC")}; ev["boil"] = F(lambda r: r[1] > 1)
        ch = ["boil", "VS", "VN", "VC", "V", "CE"]; okc = all(ev[k] is not None for k in ch) and all(ev[a] <= ev[b] for a, b in zip(ch, ch[1:]))
        add("X22", "끓기 시작 순서 — 도면: 흐름 점이 켜지는 첫 시각이 끓음 ≤ 정제기 안 증기 ≤ 목관 ≤ 컬럼 ≤ 증기관 ≤ 응축기 안. 뒤바뀐 곳 0", okc, " → ".join(f"{k} {ev[k]}" for k in ch) + " (공정 분)", "순서대로")
        pairs = [("VS", "LS"), ("VN", "LN"), ("VC", "LC"), ("V", "C"), ("C", "R"), ("R", "RD")]; bad = [f"{a}→{b}" for a, b in pairs if ev[b] is not None and (ev[a] is None or ev[b] < ev[a])]
        add("X24", "액이 증기보다 먼저 나오지 않음 — 도면: 같은 구간의 내려오는 액 점은 증기 점과 같거나 뒤, 응축액 관은 증기관 뒤, 환류 관은 응축액 관 뒤, 분배 구멍은 환류 관 뒤", not bad,
            " · ".join(f"{a} {ev[a]} → {b} {ev[b]}" for a, b in pairs) + f" · 먼저 나온 곳 {bad or '0건'}", "0건")
        zero = [r for r in lg if r[2] < hold * 0.999 and (_xnum(r[4]) or 0) <= 0.05 and r[1] > 1 and r[5] == 1]; vio = [r for r in zero if on(r, "R")]
        add("X6", "환류 U자 액봉이 찬 뒤에야 환류가 흐름 — 도면: U자가 차는 동안(도면 환류 값 0.0) 환류 관의 흐름 점은 꺼져 있다",
            bool(zero) and not vio, f"U자가 차는 동안 {len(zero)}기록({(zero[-1][0] - zero[0][0]) if zero else 0:.1f}분) 가운데 환류 관 점이 켜진 기록 {len(vio)}개" + (f"({vio[0][0]} ~ {vio[-1][0]}분)" if vio else ""), "0개")

def _xj_c1hot(g, add):   # (F) 1차 N-Brine 온도 상승
    # ---------------- (F) 1차 N-Brine 온도 상승 ----------------
    sn = "현실성 1차 냉매 95도"; f1, f2, f2d = g(sn, "f_1"), g(sn, "f_2"), g(sn, "f_2d")
    if f1 and f2 and f2d and not f2d.get("hidden"):
        c = f2["C"]; flow3 = bool(c) and c[3] == 1 and c[5] > 0; on2 = [k for k in ("C", "CE") if any(s[0] == 1 for s in f2d["st"].get(k, []))]
        add("X45", f"1차 냉매 온도 상승(N-Brine 95 ℃)으로 1차 응축이 0일 때 — {L3} · 도면: 응축액 관(1차 응축기 → 분배기)의 흐름 표현이 없다(3D 관 속 액 흐름 · 도면 응축액 관 · 응축기 안 액 점 꺼짐)",
            (f2["c1"] or 0) <= 0.01 and not flow3 and not on2, f"1차 응축 비율 {f2['c1']} · 환류 {f2['R']} · 유출 {f2['Dk']} kg/h · 3D 응축액 관 흐름 {'있음' if flow3 else '없음'}({c}) · 도면 켜진 점 {on2 or '없음'} · 3D '하부' 값 '{f2.get('tagBot')}'", "흐름 표현 0")
        vt = (f2["vdot"] or 0) * max(0.0, 1 - (f2["back"] or 0) - (f2["seal"] or 0)); m2 = (f2["m2"] or 0) + (f2["lostkg"] or 0); dt = (f2["t"] - f1["t"]) / 3600; rate = (f2["fore"] - f1["fore"]) / dt if dt > 0 else None; m2m = ((f1["m2"] or 0) + (f2["m2"] or 0)) / 2
        add("X45", "1차 응축 0일 때의 양(계산 일관): 2차 응축 + 펌프 손실 = 컬럼 꼭대기를 넘는 증기 ± 10 %, 초류 무게 증가 = 2차 응축 ± 5 %",
            vt > 0.5 and abs(m2 - vt) <= 0.1 * vt and rate is not None and m2m > 0 and abs(rate - m2m) <= 0.05 * m2m, f"꼭대기 증기 {vt:.2f} · 2차 응축 + 손실 {m2:.2f} kg/h · 초류 증가 {rate if rate is None else round(rate, 2)} · 2차 응축 평균 {m2m:.2f} kg/h", "± 10 % · ± 5 %")
        add("X4", "2차 응축기 고임 · 넘침: 계산에 2차 응축기 · L2 관의 고임과 배출 한계가 없어 2차 응축액이 생긴 걸음에 초류 무게로 간다(그림의 2차 응축기 바닥 방울은 표시 규칙) — 참고(사용자 판단 대기)", None,
            f"1차 냉매 95 ℃: 2차 응축 {f2['m2']} kg/h → 초류 증가 {rate if rate is None else round(rate, 2)} kg/h(고임 0) · L2 관 {f2['L2']}", "계산을 넣을지 사용자 판단 뒤")

def _xj_steam(g, add):   # (G) 스팀 과다 · 펌프 쪽 넘침
    # ---------------- (G) 스팀 과다 · 펌프 쪽 넘침 ----------------
    sn = "현실성 스팀 과다 · 펌프 쪽 넘침"; g1, g3, g32 = g(sn, "g_1"), g(sn, "g_3"), g(sn, "g_3_2d")
    if g1:
        _ov = lambda x: bool(x) and ((x["hot"] or 0) > 0 or (x["Tlim"] is not None and (x["TmaxL"] or 0) > x["Tlim"]))
        _gs = [(nm, x) for nm, x in (("g_1", g1), ("g_2", g(sn, "g_2")), ("g_3", g3)) if x]; _hit = next(((nm, x) for nm, x in _gs if _ov(x)), None)   # v141f: 한계를 넘은 첫 표본(새 밸브 특성에서는 20분 뒤가 아니라 약 50분 뒤에 넘는다)
        _tr = " → ".join(f"{x['T']} ℃" for _, x in _gs); g1 = _hit[1] if _hit else g1
        alarm = [t for t in g1["tags"] if re.search(r"bad|alarm|warn|hot", t[2] or "") and re.search(r"TICH071|탱크 내부|TIH", t[0] or "")]
        over = (g1["hot"] or 0) > 0 or (g1["Tlim"] is not None and (g1["TmaxL"] or 0) > g1["Tlim"])
        add("X53", f"열안정성 한계 초과(스팀 개도 과다) — {L3}: 넘은 액 비율이 0보다 크면 화면에 한계 초과 표현(글 · 붉은 빛 · 값 상자 경고 색 가운데 하나)이 보인다",
            over and bool(g1["txtHot"] or g1["glow"] or alarm), f"내부 온도 흐름 {_tr}({_hit[0] if _hit else '넘은 표본 없음'}에서 판정) · 내부 {g1['T']} ℃ · 최고 액온 {g1['TmaxL']} ℃ · 한계 {g1['Tlim']} ℃ · 넘은 액 비율 {g1['hot']} · 보이는 글 {g1['txtHot'] or '0건'} · 붉은 빛 {g1['glow']} · 경고 색 값 상자 {alarm or '0개'}", "한계를 넘으면 표현 있음")
    if g3 and g32 and not g32.get("hidden"):
        s = g3["S"]; liq3 = bool(s) and s[5] > 0 and s[6] == 0; onS = [x for x in g32["S"]["st"] if x[0] == 1]; liq2 = bool(onS) and any(_xisblue(x[2]) for x in onS); cov = _xcover(_xpng("x_g_3_2d.png"), g32["S"]["pts"])
        lostv = bool(g3["txtLost"]) or any(re.search(r"잃은|손실 액|펌프 쪽.{0,8}액", (t[0] or "") + (t[1] or "")) for t in g3["tags"]) or bool(g32["txt"])
        add("X3", f"넘친 액을 초류 쪽 관이 다 받지 못해 진공펌프 쪽으로 갈 때 — {L3} · 도면: 펌프 쪽 액 > 0.5 kg/h이면 진공 라인에 액 표현(3D 관 속 액 색 · 도면 액 색 점)이 보이고, 잃은 양이 화면 값으로 나온다",
            (g3["pumpLiq"] or 0) > 0.5 and liq3 and liq2 and lostv, f"펌프 쪽 액 {g3['pumpLiq']} kg/h · 잃은 양 누적 {g3['lost']} kg · 넘침(초류 쪽) {g3['ov']} kg/h · 3D 진공 라인 {s} · 도면 진공 라인 점 {g32['S']['st']}(액 색 점 몫 {cov if cov is None else round(cov, 2)}) · 잃은 양 글 · 값 {g3['txtLost'] or g32['txt'] or '없음'}",
            "액 표현 3D · 도면 · 잃은 양 값")

def _xj_flood(g, add):   # (H) 범람
    # ---------------- (H) 범람 ----------------
    sn = "현실성 범람"; h25, h40, h2d = g(sn, "h_25"), g(sn, "h_40"), g(sn, "h_25_2d")
    if h25:
        hx, bed, top = h25["hx"] or 0, h25["bed"] or 1, h25["top"] or 1; exp = hx / bed if hx <= bed else 1 + min(1, (hx - bed) / top)
        add("X15", f"컬럼 범람: 충전층에 액이 차오름 — {L3}: 범람비 1을 넘으면 그린 범람 액 높이 = 쌓인 액 ÷ 충전층 자리 ± 10 %(충전층 높이 기준, 실제 속도로 5초 둔 뒤)",
            (h25["flood"] or 0) > 1 and h25["vis"] and abs((h25["lv"] or 0) - exp) <= 0.10, f"컬럼 내경 {h25['Dcol']} m · 범람비 {h25['flood']} · 쌓인 액 {hx:.3f} ÷ 자리 {bed:.3f} kg = {exp:.3f} · 그린 높이 {h25['lv']}(보임 {h25['vis']}) · 테두리 {h25['glow']}", "± 0.10")
    if h2d and not h2d.get("hidden"):
        cov = _xcover(_xpng("x_h_25_2d.png"), h2d["pts"])
        add("X15", "컬럼 범람: 충전층에 액이 차오름 — 도면: 3D처럼 쌓인 액 높이만큼 컬럼 충전층이 액 색으로 찬다(테두리 색만으로는 안 됨, 도면 그림 화소)",
            (h2d["flood"] or 0) > 1 and h2d["lv"] >= 0.05 and cov is not None and cov >= 0.6, f"범람비 {h2d['flood']} · 계산 높이 {h2d['lv']} · 충전층 자리 점 가운데 액 색 {cov if cov is None else round(cov, 2)} · 컬럼 테두리 '{h2d['colCls']}'", "≥ 0.6")
    if h25 and h40:
        dm = (h40["mFlood"] or 0) - (h25["mFlood"] or 0); dt = (h40["t"] - h25["t"]) / 3600
        add("X15", "컬럼 범람의 쌓이는 양: 범람비(꼭대기 기준)가 1을 넘어도 쌓이는 양은 L_max 기준이라 멈춘다 — 두 판정 기준이 달라 계산 확인이 필요 — 참고(사용자 판단 대기)", None,
            f"2.5 h → {h40['t'] / 3600:.1f} h: 범람비 {h25['flood']} → {h40['flood']} · 쌓인 액 {h25['mFlood']} → {h40['mFlood']} kg({dm / dt if dt > 0 else 0:+.3f} kg/h) · 환류 {h40['R']} · L_max {h40['Lmax']} kg/h", "계산 기준 확인 뒤 판정")

def _xj_charge(g, add):   # (I) 과충전
    # ---------------- (I) 과충전 ----------------
    i0, i1 = g("현실성 과충전", "i_0"), g("현실성 과충전", "i_1")
    if i0 and i1:
        add("X21", "정제기에 용량보다 많이 투입(700 kg): 계산에 과충전 판정이 없어 경고 없이 탱크 그림이 커진다(실제: 넣을 수 없거나 넘침) — 참고(사용자 판단 대기)", None,
            f"투입 {i0['m0']} → {i1['m0']} kg({i1['V0']} L) · 그린 위 접선 {i0['Hs']} → {i1['Hs']} m · 그린 탱크 안 부피 {i0['Vshell']} → {i1['Vshell']} L · 경고 글 {i1['warn'] or '0건'} · 칩 {i1['chips'] or '0개'} · 안내 '{i1['note'][:60]}'", "입력 검사(계산)를 넣을지 사용자 판단 뒤")

def judge_real(g, add):
    """현실성(X) 판정 줄 — 장면마다 따로 판정한다. 한 장면의 판정 계산에서 오류가 나면 그 장면만 '판정 계산 오류' 줄로 남기고 나머지는 그대로 판정한다(기록을 잃지 않게)."""
    import traceback
    for nm, fn in (("(A) 밸브 조작", _xj_valve), ("(B) 받는 탱크 가득 참", _xj_tank), ("액면(받는 탱크 · 정제기)", _xj_level), ("배치 끝", _xj_end), ("(C · D) 끓기 시작", _xj_onset), ("(F) 1차 N-Brine 온도 상승", _xj_c1hot), ("(G) 스팀 과다 · 펌프 쪽 넘침", _xj_steam), ("(H) 범람", _xj_flood), ("(I) 과충전", _xj_charge)):
        try: fn(g, add)
        except Exception as e: add("X0", f"현실성 판정 계산 오류 — {nm}", False, f"{type(e).__name__}: {e} · {traceback.format_exc(limit=3)[-400:]}", "오류 0")
# <<< 현실성(X) 판정 끝

# >>> 새 디자인 판정 시작
# ---------- 새 디자인(v132~) 판정 줄: 번호 = 현실성 항목 번호(기본 표현 줄은 XD), 이름은 '새 디자인:'으로 시작 ----------
# 기준은 v132 작업 기록(진행.md)의 제안 N1 ~ N16과 그쪽 판정(judge2 · 3 · 4.py)을 그대로 옮겼다. 재는 방법을 고친 곳은 줄 이름 · 잰 값에 밝혔다. N17(가벼움 = v131 화소)은 넣지 않는다.
G_DS = lambda q: min(1.5, 0.9 * (q / 25) ** 0.6) if q > 0.05 else 0.0   # 김 진하기 규칙(새 디자인 표시 규칙): 0.9 × (계산 유량 ÷ 25 kg/h)^0.6, 1.5에서 자름
RO_DS = lambda q: max(0.0011, 0.002585 * math.sqrt(max(0, q)))          # 물줄기 반지름 규칙(m, 사용자가 정한 것 8): max(1.1 mm, 2.585 mm × √유량)
VK_DS = ["head", "neck", "col", "V", "bon", "tub", "T2", "C2", "S", "J", "jk"]
VN_DS = {"head": "정제기 위", "neck": "목관", "col": "컬럼", "V": "증기관", "bon": "응축기 뚜껑", "tub": "응축기 관", "T2": "배기관", "C2": "2차 응축기", "S": "진공 라인", "J": "스팀 관", "jk": "자켓"}
def _dsvis(p, k): return bool(p and ((p.get("vap") or {}).get(k) or {}).get("vis"))
def _dsvisset(p): return sorted(k for k in VK_DS if _dsvis(p, k))
def _dsext(e): return 0 if not e or not e.get("a") else max(0, e["a"][1] - e["a"][0]) + max(0, e["b"][1] - e["b"][0])
def _dsnm(ks): return " · ".join(VN_DS.get(k, k) for k in ks) or "없음"
DS3 = "새 디자인:"

def _xd_boil(g, add):   # N1 · N2 · N8
    b = g("새디자인 끓기 시작", "ds_boil")
    if not b: return
    f = b["first"]; seq = ["boil", "v.head", "v.neck", "v.col", "v.V", "v.bon", "v.tub"]; ts = [f.get(k) for k in seq]; m = lambda k: "–" if f.get(k) is None else f"{f[k] / 60:.2f}"
    ok = all(x is not None for x in ts) and all(ts[i] <= ts[i + 1] + 1e-6 for i in range(len(ts) - 1)) and f["v.V"] >= f.get("vpTop", 1e9) - 1e-6 and f["v.tub"] >= f.get("vpCond", 1e9) - 1e-6 and f["v.head"] - f["boil"] <= 60
    add("X22", f"{DS3} 끓기 시작 — 김이 정제기 위 → 목관 → 컬럼 → 증기관 → 응축기 뚜껑 → 관 순서로 나타나고, 증기관은 꼭대기를 넘은 뒤 · 관은 응축 시작 뒤(N1)", ok,
        " → ".join(f"{n} {m(k)}" for n, k in zip(["끓음", "정제기 위", "목관", "컬럼", "증기관", "뚜껑", "관"], seq)) + f" (공정 분) · 꼭대기 넘음 {m('vpTop')} · 응축 시작 {m('vpCond')}",
        "첫 보인 시각 끓음 ≤ 정제기 위 ≤ 목관 ≤ 컬럼 ≤ 증기관 ≤ 뚜껑 ≤ 관, 증기관 ≥ 꼭대기 넘음, 관 ≥ 응축 시작, 끓음 → 정제기 위 60 s(공정) 안")
    vs = b.get("vs") or []; dif = [abs(v[4] - v[1] / v[2]) for v in vs if v[4] is not None and v[3] and v[2]]
    add("X22", f"{DS3} 증기관 김 앞머리 = 지금 장면의 증기 앞머리(VF.headLenV ÷ VF.lenV)(N2)", bool(dif) and max(dif) <= 0.03, f"0.5 s마다 {len(dif)}표본 · 차 최대 {round(max(dif), 4) if dif else '–'}", "차 ≤ 0.03(관 길이 비)")
    pairs = [("l.C", "v.tub"), ("l.C", "vpCond"), ("c1film", "v.tub"), ("pool", "v.tub"), ("c1str", "c1film"), ("pool", "c1str"), ("l.C", "c1str"), ("l.R", "l.C"), ("RD", "l.R"), ("filmR", "RD"), ("filmC", "v.col"), ("neck", "v.col"), ("l.P", "l.C"), ("l.F", "l.P"), ("l.FL", "l.F"), ("foreStream", "l.FL"), ("vpDrops", "v.col")]
    nm = {"l.C": "응축액 관", "v.tub": "응축기 관 김", "vpCond": "응축 시작", "c1film": "응축기 관 액막", "pool": "응축기 바닥 고임", "c1str": "관 끝 줄기", "l.R": "환류 관", "RD": "분배 줄기", "filmR": "충전층 적심", "filmC": "컬럼 맺힌 액막", "v.col": "컬럼 김", "neck": "목관 줄기", "l.P": "유출 관", "l.F": "초류 가지", "l.FL": "초류 입구 관", "foreStream": "초류 줄기", "vpDrops": "떨어지는 방울"}
    pc = lambda a, c: min([x for x in (f.get(c), f.get("rfx") if (a, c) == ("l.R", "l.C") else None) if x is not None], default=None)   # rfx136 v136 사본: 환류 관(U자 고인 액)은 응축액 관 또는 빈 환류관 관 벽 응축(PR.rfx.condTot > 0) 뒤
    bad = [f"{nm[a]}({m(a)}) < {nm[c]}({m(c)})" for a, c in pairs if f.get(a) is not None and (pc(a, c) is None or f[a] < pc(a, c) - 0.05)]; seen = [a for a, c in pairs if f.get(a) is not None]
    add("X24", f"{DS3} 액이 증기보다 먼저 나오지 않음 — 응축기 관 액막 · 응축액 관 · 환류 관 · 분배 줄기 · 충전층 적심 · 유출 관 → 초류 가지 → 입구 관 → 초류 줄기가 각각 앞(김 또는 윗관) 뒤에 나온다(N8 · X6)",
        len(seen) >= 12 and not bad, f"확인한 짝 {len(seen)}/{len(pairs)} · 어긋남 {bad or '없음'} · 빈 환류관 관 벽 응축 첫 {m('rfx')} · " + " · ".join(f"{nm[k]} {m(k)}" for k in ["v.tub", "c1film", "l.C", "l.R", "RD", "filmR", "l.P", "l.F", "l.FL", "foreStream"] if f.get(k) is not None) + " (공정 분)",
        "짝마다 액의 첫 보인 시각 ≥ 앞의 첫 보인 시각(0.05 s 여유), 확인한 짝 12개 넘게")

DS_GATE = ("V", "bon", "tub", "T2", "C2")   # 앞머리 규칙이 있는 구간(dsflow.js): 증기관 = 꼭대기 넘음 뒤, 뚜껑 = 증기관이 다 찬 뒤, 관 = 뚜껑이 다 찬 뒤, 배기관 · 2차 = 응축 시작 뒤에 켜짐(N1 차례)
def _xd_n3(g, add):   # N3: 김 진하기 규칙 · 흐름 0이면 0(모든 새 디자인 장면의 1초 표본)
    # 재는 범위(11-22 고침): 처음 옮긴 판정은 앞머리가 닿기 전 표본(계산 유량 > 0.05 · 목표 0)까지 진하기 비에 넣어 비 0이 나왔다(1회차 22표본 — 끓기 시작 · 펌프 정지 뒤 다시 끓을 때의 증기관 · 뚜껑 · 관).
    # 그 표본에서 김을 켜면 같은 제안의 N1(증기관은 꼭대기를 넘은 뒤, 뚜껑 · 관은 앞 구간 뒤)을 어긴다. v132 쪽 V4도 정제기 위만 쟀다. 그래서 진하기 비는 켜진 표본으로 보고,
    # 앞머리 전 표본은 따로 세어 '앞머리 규칙이 있는 구간에서 켜지기 바로 앞에만(바로 앞 표본이 켜짐이 아니고 이어서 켜짐)' 있는지 본다. 기준값 1 ± 0.005는 그대로.
    src = [("새디자인 끓기 시작", "ds_boil"), ("새디자인 6 h 밸브", "ds_hold"), ("새디자인 1차 냉매 95도", "ds_cv"), ("새디자인 진공 펌프 정지", "ds_pv"), ("새디자인 배치 끝", "ds_ev")]
    rat = []; jk = []; bad0 = []; tot = 0; used = []; pre = []; badpre = []
    for sn, t in src:
        d = g(sn, t)
        if not d or not d.get("n3"): continue
        sn0 = sn.replace("새디자인 ", ""); used.append(sn0); n3 = d["n3"]
        for j, k in enumerate(VK_DS):
            st = []   # 표본마다 0 = 유량 ≤ 0.05 · 1 = 켜짐 · 2 = 유량 > 0.05인데 목표 0 · None = 값 없음
            for tt, arr in n3:
                e = arr[j] if j < len(arr) else None
                if not e: st.append(None); continue
                q, tg = e; tot += 1
                if q <= 0.05:
                    st.append(0)
                    if tg > 0: bad0.append(f"{VN_DS[k]} {tt / 60:.1f}분 유량 {q} · 목표 {tg}")
                elif k == "jk": st.append(None); jk.append(tg / (0.35 * G_DS(q)))
                elif tg > 0: st.append(1); rat.append(tg / G_DS(q))
                else: st.append(2)
            i = 0
            while i < len(st):
                if st[i] != 2: i += 1; continue
                i0 = i
                while i < len(st) and st[i] == 2: i += 1
                r = (sn0, k, round(n3[i0][0] / 60, 1), i - i0)
                (pre if k in DS_GATE and (i0 == 0 or st[i0 - 1] != 1) and i < len(st) and st[i] == 1 else badpre).append(r)
    if not used: return
    pres = " · ".join(f"{a} {VN_DS[k]} {n}" for a, k, _, n in pre)
    add("X32", f"{DS3} 김 진하기 ∝ 증발량 — 목표 진하기 = 0.9 × (계산 유량 ÷ 25 kg/h)^0.6, 증기 김(정제기 위 ~ 진공 라인)과 스팀 관(N3). 증기관 · 뚜껑 · 관 · 배기관 · 2차는 앞머리가 닿은 뒤의 표본으로 잰다(N1 차례 — 앞머리 전 표본은 켜지기 바로 앞에만). 자켓 안 김 띠는 v142에서 뺐다(Y17 — 액 속 김처럼 보임)",
        bool(rat) and min(rat) >= 0.995 and max(rat) <= 1.005 and not badpre,
        f"장면 {used} · 목표 ÷ 규칙값 {round(min(rat), 4) if rat else '–'} ~ {round(max(rat), 4) if rat else '–'}({len(rat)}표본, 켜진 구간) · 앞머리 전 표본 {sum(r[3] for r in pre)}개({pres or '없음'} — 모두 켜지기 바로 앞) · 그 밖에 유량 > 0.05인데 목표 0인 표본 {sum(r[3] for r in badpre)}개"
        + (f"({' · '.join(f'{a} {VN_DS[k]} {m}분부터 {n}' for a, k, m, n in badpre[:4])})" if badpre else "") + f" · 자켓 ÷ (0.35 × 규칙값) {round(min(jk), 4) if jk else '–'} ~ {round(max(jk), 4) if jk else '–'}",
        "1 ± 0.005(켜진 구간) · 앞머리 전 표본은 앞머리 규칙이 있는 구간에서 켜지기 바로 앞에만")
    add("X33", f"{DS3} 흐름이 0이면 김 0 — 계산 유량 ≤ 0.05 kg/h인 구간의 목표 진하기 0(N3)", tot > 0 and not bad0, f"장면 {used} · 표본 × 구간 {tot} · 어긋남 {len(bad0)}개{(' — ' + ' / '.join(bad0[:3])) if bad0 else ''}", "어긋남 0")

def _xd_valve(g, add):   # N9 · N10 · N11 · N12 · N4
    sn = "새디자인 6 h 밸브"; p = g(sn, "ds_h6")
    if p and p.get("liq"):
        l = p["liq"]; kS = p.get("kS", 1); Rq = (p.get("calc") or {}).get("R") or 0; chk = []
        if (l.get("RD") or {}).get("on"): chk.append(("분배 줄기(구멍 하나)", l["RD"]["r"], RO_DS(Rq / 4) * kS * 1000, Rq / 4))
        nk = l.get("neck") or {}
        if nk.get("on"): chk.append(("목관 줄기(하나)", nk["r"], RO_DS(nk["q"] / nk["n"]) * kS * 1000, nk["q"] / nk["n"]))
        fs = l.get("foreStream") or {}
        if fs.get("on"): chk.append(("초류 탱크 줄기", fs["r"], RO_DS(fs["q"]) * kS * 1000, fs["q"]))
        errs = [abs(a / b - 1) for _, a, b, _ in chk if b > 0]; per = [(nm, round(a ** 2 / q, 3)) for nm, a, b, q in chk if q >= 0.2]
        spread = (max(x[1] for x in per) / min(x[1] for x in per) - 1) if len(per) >= 2 else None
        add("X34", f"{DS3} 물줄기 굵기 = 유량(단면적 ∝ 유량, 어디서나 같은 식 — 사용자가 정한 것 8)(N9)", len(chk) >= 2 and max(errs) <= 0.01 and spread is not None and spread <= 0.02,
            f"화면 배율 {kS} · " + " · ".join(f"{nm} {a:.2f} mm(식 {b:.2f}, {q:.2f} kg/h)" for nm, a, b, q in chk) + f" · 반지름² ÷ 유량 {per} · 차 {None if spread is None else round(spread * 100, 2)} %" + (" · 목관은 방울 영역(줄기 없음)" if nk.get("drip") else ""),
            "줄기마다 반지름 = 식 ± 1 %, 반지름² ÷ 유량이 줄기끼리 ± 2 %")
    fd = g(sn, "ds_f")
    if fd and fd.get("s"):
        s = fd["s"]; tc = next((r[0] for r in s if r[8] == 0), None); to = next((r[0] for r in s if tc is not None and r[0] > tc and r[8] == 1), None); drops = []
        for j, k in ((1, "유출 관"), (2, "초류 가지"), (3, "초류 입구 관")):
            for i in range(1, len(s)):
                if s[i][0] - s[i - 1][0] <= 0.15 and (s[i - 1][j] or 0) - (s[i][j] or 0) > 0.5: drops.append((k, s[i][0], s[i - 1][j], s[i][j]))
        emp = next((r for r in s if tc is not None and r[0] > tc and (to is None or r[0] < to) and (r[4] or 0) < 0.02 and (r[5] or 0) < 0.02), None)
        held = [emp[6], emp[7]] if emp else None; dC = [d for d in drops if tc is not None and d[1] >= tc and (to is None or d[1] < to - 0.2)]; dO = [d for d in drops if to is not None and d[1] >= to - 0.2]
        add("X27", f"{DS3} 초류 밸브를 닫으면 밸브 뒤 관이 꼬리부터 비고 밸브 앞 액은 남는다(N10)", bool(emp) and emp[0] - tc <= 6 and held and held[1] is not None and held[1] > (held[0] or 0) and not dC,
            f"닫음 → 밸브 뒤 빔 {None if not emp else round(emp[0] - tc, 2)} s · 밸브 앞 남은 구간 {held} · 닫힌 동안 한순간 줄어듦 {[(d[0], d[2], d[3]) for d in dC] or '없음'}", "6 s 안에 빔 · 밸브 앞 남음 · 0.1 s 사이 관 절반 넘게 줄어든 일 0")
        pv = [r[1] for r in s if to is not None and to - 0.3 <= r[0] <= to + 0.6]
        add("X26", f"{DS3} 닫았던 초류 밸브를 다시 열 때 남아 있던 액이 그대로 이어 흐른다(N10)", to is not None and not dO,
            f"다시 연 앞뒤 유출 관 보이는 길이 비 {pv[:10]} · 한순간 줄어듦 {[(d[0], d[2], d[3]) for d in dO] or '없음'}", "다시 연 뒤 0.1 s 사이 유출 · 초류 관의 보이는 길이가 관 절반 넘게 줄어든 일 0")
    r0, r1 = g(sn, "ds_r0"), g(sn, "ds_r1")
    if r0 and r1:
        a, b = r0.get("b"), r1.get("b"); ok = bool(a and b and a[1] > a[0] and abs(a[0] - b[0]) < 0.01 and abs(a[1] - b[1]) < 0.01)
        s0, s1 = r0.get("sealp"), r1.get("sealp")
        if s0 and s1:   # v141: U자 액봉 = 수평 액면(dsfSealStep) — 관 길 방향 '남는 구간'이 없어 액봉 질량 · 양쪽 액면 · 닫힌 밸브 앞 층 높이로 잰다
            mF = (s0.get("geo") or {}).get("mFull") or 0; same = lambda k: s0.get(k) is not None and s1.get(k) is not None and abs(s0[k] - s1[k]) < 0.002
            ok2 = bool(s0.get("vis") and s1.get("vis") and mF > 0 and s0["m"] >= 0.99 * mF and abs(s0["m"] - s1["m"]) < 0.005 and same("Yin") and same("Yout") and same("yup"))
            add("X59", f"{DS3} 환류 밸브를 닫아 U자에 액이 남은 상태에서 도면을 다녀와도 남은 액 표시가 그대로(N11 · X12) — v141: 액봉 질량 · 양쪽 액면 · 닫힌 밸브 앞 층 높이", ok2,
                f"닫고 8 s 액봉 {s0.get('m')} kg(다 찬 값 {mF}) · 액면 응축기 쪽 {s0.get('Yin')} · 컬럼 쪽 {s0.get('Yout')} · 밸브 앞 층 {s0.get('yup')} → 도면 3 s 다녀온 뒤 {s1.get('m')} · {s1.get('Yin')} · {s1.get('Yout')} · {s1.get('yup')} · 밸브 {r0.get('VR')}", "액봉이 보이고 다 찬 채로 남음 · 다녀온 뒤 질량 ± 0.005 kg · 높이 ± 2 mm(그림 길이 0.002)")
        else: add("X59", f"{DS3} 환류 밸브를 닫아 U자에 액이 남은 상태에서 도면을 다녀와도 남은 액 표시가 그대로(N11 · X12)", ok, f"닫고 8 s 남는 구간 {a} · 도면 3 s 다녀온 뒤 {b} · 실 루프 {r0.get('seal')} → {r1.get('seal')} kg · 밸브 {r0.get('VR')}", "남는 구간 있음 · 다녀온 뒤 = 바꾸기 전 ± 0.01(관 길이 비)")
    hd = g(sn, "ds_hold")
    if hd and hd.get("s"):
        s = hd["s"]; i0 = next((i for i, r in enumerate(s) if r[11] == 0 and r[12] == 0), None)
        if i0 is not None:
            t0 = s[i0][0]; lg = s[i0:]
            win = [r for r in lg if t0 + 20 <= r[0] <= t0 + 60]; vis2 = sum(r[8] + r[9] + r[10] for r in win)
            add("X14", f"{DS3} 응축액이 고이는 동안 김이 2차 응축기 · 진공펌프로 가지 않는다 — 환류 · 유출 밸브를 닫고 20 ~ 60 s(N4)", len(win) > 50 and vis2 == 0, f"표본 {len(win)} · 배기관 · 2차 · 진공 라인 김이 보인 표본 {vis2}", "보인 표본 0")
            pf = []; st = []
            for i, r in enumerate(lg):
                q0 = lg[i - 10] if i >= 10 else None
                if r[4] is None or r[5] is None or not q0 or q0[5] is None or r[2] < 0.03 or r[5] < q0[5] - 0.01: continue
                pf.append((r[4], r[5]))
                if abs(r[5] - q0[5]) < 0.005: st.append((r[4], r[5]))
            err = [abs(a / c - 1) for a, c in pf if c > 0]; ers = [abs(a / c - 1) for a, c in st if c > 0]
            add("X1", f"{DS3} 응축액이 고이면 1차 응축기 아래 뚜껑에 액면이 차오름 = 계산 액위(N12)", bool(pf) and max(err) <= 0.10 and (not st or max(ers) <= 0.02),
                f"차오르는 표본 {len(pf)} · 차 최대 {max(err) * 100 if err else 0:.1f} % · 멈춘 표본 {len(st)} · 차 최대 {max(ers) * 100 if ers else 0:.1f} %", "계산 액위 3 cm 넘을 때 그린 비 ÷ 계산 비 = 1 ± 0.10, 멈춘 뒤 ± 0.02")
            tov = next((r[0] for r in lg if (r[3] or 0) > 1), None); tT2 = next((r[0] for r in lg if tov is not None and r[0] >= tov - 0.05 and (r[6] or 0) > 0.01), None); tL2 = next((r[0] for r in lg if tov is not None and r[0] >= tov - 0.05 and (r[7] or 0) > 0.01), None)
            add("X2", f"{DS3} 고임이 옆 노즐을 넘으면 배기관 · 2차 응축기 → 초류 관(L2)에 액(N12)", bool(tov is not None and tT2 is not None and tT2 - tov <= 1.0 and tL2 is not None and tL2 - tov <= 1.0),
                f"넘침 > 1 kg/h +{None if tov is None else round(tov - t0, 1)} s · 배기관 액 +{None if tT2 is None or tov is None else round(tT2 - tov, 2)} s · L2 액 +{None if tL2 is None or tov is None else round(tL2 - tov, 2)} s", "넘침 뒤 화면 1 s 안에 배기관 · L2 액")
    qs = [g(sn, f"ds_q{i}") for i in range(1, 6)]; qs = [q for q in qs if q]
    if qs:
        ok = all(abs((q.get("ds") or 0) - min(1, max(0, q.get("spl") or 0))) < 0.002 for q in qs); lv = []
        for q in qs:   # v141: 분배기 = T자 관 — 고임은 티 세로 관 액면으로 그린다. 높이 = max(닫는 순간의 층 높이, 가로 관 바닥 + 계산 분배기 액 비 × (티 위 끝 − 가로 관 바닥)), 응축액 관 몫은 그 위
            s = q.get("seal") or {}; ge = s.get("geo") or {}
            if ge.get("yTee") is None or s.get("yT") is None: continue
            sp = min(1, max(0, q.get("spl") or 0)); cp = min(1, max(0, q.get("cp") or 0)); yc = (ge["invIn"] + sp * (ge["yTee"] - ge["invIn"]) if sp < 1 else ge["yTee"] + cp * (ge["yCt"] - ge["yTee"])) if sp > 0.002 else -1e9
            ex = max(ge["invIn"], s["yup"] if s.get("yup") is not None else -1e9, yc); lv.append((round(s["yT"], 4), round(ex, 4)))
        if lv: ok = ok and all(abs(a - b) < 0.002 for a, b in lv)
        add("X5", f"{DS3} 환류 · 유출을 닫으면 분배기에 액이 고임 = 계산 분배기 액 비(N12 · X13)", ok, " / ".join(f"계산 {round(q.get('spl') or 0, 4)} · 그림 {q.get('ds')}" for q in qs) + (f" · 티 세로 관 액면(그림, 계산에서 정한 높이) {lv}" if lv else ""), "15 s마다 그린 비 = 계산 비 ± 0.002" + (" · 티 액면 = 정한 높이 ± 0.002" if lv else ""))

def _xd_c1hot(g, add):   # N5
    sn = "새디자인 1차 냉매 95도"; p2, cv = g(sn, "ds_c2"), g(sn, "ds_cv")
    if not (p2 and cv): return
    c = p2.get("calc") or {}; t2 = (p2.get("vap") or {}).get("T2") or {}; q2 = (c.get("vpass") or 0) * (1 - (c.get("c1") if c.get("c1") is not None else 1)); dr = abs((t2.get("d") or 0) / max(1e-6, G_DS(q2)) - 1)
    f = cv.get("first") or {}; dt = None if f.get("nocond") is None or f.get("Cempty") is None else round(f["Cempty"] - f["nocond"], 2); ce = _dsext((p2.get("liq") or {}).get("C"))
    ok = _dsvis(p2, "T2") and _dsvis(p2, "C2") and not _dsvis(p2, "S") and ce < 0.02 and dr < 0.05 and dt is not None and dt <= 6
    add("X45", f"{DS3} 1차 N-Brine 온도 상승 40 s — 김이 1차를 지나 배기관 · 2차 응축기로(진하기 = 규칙값), 진공 라인 김 없음, 1차 응축이 0이 되면 응축액 관이 빈다(N5)", bool(ok),
        f"1차 응축 비율 {c.get('c1')} · 2차로 {round(q2, 3)} kg/h · 보이는 김 {_dsnm(_dsvisset(p2))} · 배기관 진하기 {t2.get('d')}(규칙값 {round(G_DS(q2), 4)}) · 응축 0 → 응축액 관 빔 {dt} s · 40 s 응축액 관 {ce}", "배기관 · 2차 보임(± 5 %) · 진공 라인 없음 · 6 s 안에 빔 · 응축액 관 액 0")

def _xd_pstop(g, add):   # N6 · 4단계 A7
    sn = "새디자인 진공 펌프 정지"; pv, p2 = g(sn, "ds_pv"), g(sn, "ds_p2")
    if not pv: return
    f = pv.get("first") or {}; last = {k: v for k, v in (pv.get("last") or {}).items() if k not in ("J", "jk")}; nb = f.get("noboil"); rt = None if nb is None or not last else round(max(last.values()) - nb, 2)
    mk = pv.get("marks") or {}; v30 = [k for k, e in ((mk.get("30분") or {}).get("vap") or {}).items() if e.get("vis") and k not in ("J", "jk")]; vb = [k for k in ("head", "neck", "col", "V") if (((mk.get("되돌림 20분") or {}).get("vap") or {}).get(k) or {}).get("vis")]
    add("X29", f"{DS3} 진공 펌프 정지 — 끓음이 멈추면 김이 사라지고 되돌리면 다시 나타난다(N6 · X42)", rt is not None and rt <= 10 and not v30 and len(vb) == 4,
        f"끓음 멈춤 → 증기 김이 다 사라질 때까지 화면 {rt} s · 30분에 보이는 증기 김 {_dsnm(v30)} · 되돌린 뒤 {_dsnm(vb)}", "10 s 안에 0 · 30분에 0 · 되돌리면 정제기 위 · 목관 · 컬럼 · 증기관 다시 보임")
    # 4단계 A7(11-22 고침): 제안은 '40 s 한 점에서 증발 < 1 kg/h면 목표 0'이었다. 40 s는 끓음이 멈추는 때와 겹쳐(1회차: 펌프 정지 뒤 38.5 s에 증발 < 1) 같은 빌드 규칙에서도
    # 시각에 따라 통과(v132 4단계 — 넘는 증기 0.047 kg/h) · 실패(1회차 — 0.066 kg/h)가 갈린다. 그래서 되돌리기 전까지 끓지 않는 1 s 표본 전부로 본다. 기준 '증발 < 1이면 증기 김 목표 0'은 그대로.
    # 끓지 않음 = 정제기 위 계산 유량 0(dsflow.js: 끓을 때 — 증발 > 1 kg/h — 만 증발을 넣음)
    # v145 X29(사용자 11-27 "실제처럼해줘"): 끓음이 멈춘 뒤에도 관에 남은 증기는 응축기로 빠진다(계산 넘는 증기 vpass). 그 동안 증기관 · 뚜껑 · 관 김은 그 띠 계산 유량대로 옅게 —
    #  0.05 kg/h 넘으면 김 진하기 규칙(N3과 같은 식), 넘는 증기가 0.05 아래면 0. 정제기 위 · 목관 · 컬럼은 증발이 0이라 0. 전(4단계 A7): 끓지 않으면 모든 김 목표 0 — 계산이 넘는 증기를 두는 동안 어긋났다
    t30 = ((mk.get("30분") or {}).get("calc") or {}).get("t"); nbs = []; bad = []; shown = []
    for tt, arr in pv.get("n3") or []:
        if t30 is None or tt > t30 or not arr or not arr[0] or arr[0][0] != 0: continue
        nbs.append(tt)
        for k, e in zip(VK_DS[:9], arr[:9]):
            if not e: continue
            q, tg = e
            if q <= 0.05 or k in ("head", "neck", "col"):
                if tg > 0: bad.append((k, round(tt / 60, 1), q, tg))
            elif tg > 0:
                if abs(tg / G_DS(q) - 1) > 0.005: bad.append((k, round(tt / 60, 1), q, tg))
                else: shown.append((k, q))
    c2 = (p2 or {}).get("calc") or {}
    add("X29", f"{DS3} 진공 펌프 정지 — 끓지 않는 동안(증발 < 1 kg/h) 정제기 위 · 목관 · 컬럼 김은 0, 증기관 · 뚜껑 · 관 김은 관에 남아 응축기로 빠지는 증기(계산 넘는 증기)대로 — 0.05 kg/h 넘는 동안만 김 진하기 규칙만큼 옅게(현장 실제, 사용자 11-27 '실제처럼해줘'. 전: 끓지 않으면 모두 0)", bool(nbs) and not bad,
        f"끓지 않는 1 s 표본 {len(nbs)}개 · 규칙과 다른 김 {len(bad)}개" + (f"({bad[:3]})" if bad else "") + f" · 남은 증기로 옅게 보인 띠 {len(shown)}번" + (f"({_dsnm(sorted(set(k for k, _ in shown)))} · 최대 {max(q for _, q in shown):.3f} kg/h)" if shown else "")
        + f" · 40 s 한 점: 증발 {c2.get('vdot')} · 넘는 증기 {c2.get('vpass')} kg/h", "정제기 위 · 목관 · 컬럼 0 · 그 밖은 그 띠 계산 유량의 김 진하기 규칙(0.05 kg/h 이하면 0)")

def _xd_end(g, add):   # N7
    sn = "새디자인 배치 끝"; ev, e1 = g(sn, "ds_ev"), g(sn, "ds_e1")
    if ev:
        m = (ev.get("marks") or {}).get("12 s") or {}; vis = [k for k, e in (m.get("vap") or {}).items() if e.get("vis")]
        add("X28", f"{DS3} 배치 끝(가열 정지) — 김 · 스팀 김이 모두 사라진다(N7)", bool(m) and not vis, f"가열 정지 뒤 화면 12 s에 보이는 김 {_dsnm(vis)}", "보이는 김 0")
    if e1:
        add("X19", f"{DS3} 가열 정지(액위 하한 인터록)면 스팀 밸브가 닫힘 색(N7)", e1.get("stopped") is True and e1.get("dsJ") is False and (e1.get("steam") or 0) < 0.05,
            f"정지 {e1.get('stopped')} · 새 디자인 스팀 밸브 열림 {e1.get('dsJ')} · 스팀 유량 {round(e1.get('steam') or 0, 4)} kg/h · '{e1.get('why')}'", "열림 거짓 · 스팀 유량 < 0.05")

def _xd_ab(g, add):   # N13(이상 상황 열 가지 — 1차 냉매 온도 상승 · 펌프 정지는 N5 · N6 장면)
    def P(sn, k, i): return g(sn, f"ds_{k}_p{i}")
    sn = "새디자인 이상 상황 냉매 · 배기"
    for k, nm, xid in (("c1cold", "1차 N-Brine 과냉", "X46"), ("c2hot", "2차 L-Brine 온도 상승", "X47"), ("pump", "진공 배기 능력 저하", "X44")):
        p0, p2 = P(sn, k, 0), P(sn, k, 2)
        if not (p0 and p2): continue
        add(xid, f"{DS3} {nm} — 흐름이 계산상 그대로면 김도 그대로(N13)", _dsvisset(p0) == _dsvisset(p2) and not any(_dsvis(p2, x) for x in ("T2", "C2", "S")),
            f"전 {_dsnm(_dsvisset(p0))} → 40 s {_dsnm(_dsvisset(p2))} · 1차 응축 비율 {(p2.get('calc') or {}).get('c1')} · 펌프 쪽 {(p2.get('calc') or {}).get('Ppump')} mmHg", "보이는 김 구간 같음 · 2차 쪽 김 없음")
    p2 = P(sn, "cwlow", 2)
    if p2:
        c = p2.get("calc") or {}; q2 = (c.get("vpass") or 0) * (1 - (c.get("c1") if c.get("c1") is not None else 1)); t2 = (p2.get("vap") or {}).get("T2") or {}
        ok = (q2 > 0.05 and _dsvis(p2, "T2") and abs((t2.get("d") or 0) / G_DS(q2) - 1) < 0.05) or (q2 <= 0.05 and not _dsvis(p2, "T2"))
        add("X46", f"{DS3} 냉매 유량 부족 — 1차가 못 잡은 몫만큼 배기관 김(N13)", bool(ok), f"1차 응축 비율 {c.get('c1')} · 2차로 {round(q2, 3)} kg/h · 배기관 {t2}", "2차로 > 0.05 kg/h면 배기관 진하기 = 규칙값 ± 5 %(아니면 없음)")
    sn = "새디자인 이상 상황 스팀 과다"; p0, p2 = P(sn, "steam", 0), P(sn, "steam", 2)
    if p0 and p2:
        c0, c2 = p0.get("calc") or {}, p2.get("calc") or {}; d0, d2 = p0["vap"]["head"]["d"], p2["vap"]["head"]["d"]
        add("X48", f"{DS3} 스팀 개도 과다 — 증발이 늘면 김이 진해진다(N13)", c2["vdot"] > c0["vdot"] * 1.2 and d2 > d0 and abs(d2 / G_DS(c2["vdot"]) - 1) < 0.05, f"증발 {c0['vdot']} → {c2['vdot']} kg/h · 진하기 {d0} → {d2}(규칙값 {round(G_DS(c2['vdot']), 4)})", "40 s에 증발 1.2배 넘게 · 정제기 위 진하기 = 규칙값 ± 5 %")
    sn = "새디자인 이상 상황 환류"
    for k, nm in (("rhigh", "과다"), ("rlow", "부족")):
        p0, p2 = P(sn, k, 0), P(sn, k, 2)
        if not (p0 and p2): continue
        R0, R2 = p0["calc"]["R"], p2["calc"]["R"]; rd0, rd2 = p0["liq"].get("RD") or {}, p2["liq"].get("RD") or {}; kS = p2.get("kS", 1)
        ok = rd2.get("on") and abs(rd2["r"] / (RO_DS(R2 / 4) * kS * 1000) - 1) < 0.01 and ((R2 > R0 and rd2["r"] > (rd0.get("r") or 0)) or (R2 < R0 and rd2["r"] < (rd0.get("r") or 1e9)))
        add("X49", f"{DS3} 환류 {nm} — 분배 줄기 굵기가 환류를 따른다(N13)", bool(ok), f"환류 {R0} → {R2} kg/h · 반지름 {rd0.get('r')} → {rd2.get('r')} mm(식 {round(RO_DS(R2 / 4) * kS * 1000, 2)})", "40 s에 반지름 = 식 √(환류 ÷ 4) ± 1 %, 환류를 따라 굵어지거나 가늘어짐")
    sn = "새디자인 이상 상황 진공 리크"; p1, p2 = P(sn, "leak", 1), P(sn, "leak", 2)
    if p1 and p2:
        out = []; ok = True
        for nm_, p in (("20 s", p1), ("40 s", p2)):
            c = p.get("calc") or {}; air = 1 - (c.get("fNC") if c.get("fNC") is not None else 1); a = (p.get("liq") or {}).get("air") or {}
            boil = c.get("vdot", 0) > 1 and not c.get("stopped"); o1 = (bool(a.get("on")) == (boil and air > 0.03)); o2 = boil or not any(_dsvis(p, x) for x in ("head", "neck", "col", "V", "bon", "tub")); ok = ok and o1 and o2
            out.append(f"{nm_}: 증발 {c.get('vdot')} · 비응축 몫 {air:.3f} · 공기막 {a.get('on')} · 김 {_dsnm(_dsvisset(p))}")
        add("X43", f"{DS3} 진공 리크 증가 — 비응축 가스 막(끓을 때 비응축 몫 3 % 넘으면) · 끓음이 멈추면 증기 김 0(N13 · X54)", ok, " / ".join(out), "공기막 = 끓음 · 비응축 몫 > 3 %, 증발 < 1이면 증기 김 0")
    for k, nm, sn in (("cold", "외기 한파", "새디자인 이상 상황 외기 한파"), ("bare", "단열 손상", "새디자인 이상 상황 단열 손상")):
        p0, p2 = P(sn, k, 0), P(sn, k, 2)
        if not (p0 and p2): continue
        b0, b2 = p0["calc"]["back"], p2["calc"]["back"]; fm0, fm2 = p0["liq"]["film"], p2["liq"]["film"]; c0, c2 = fm0.get("cvC"), fm2.get("cvC")
        # v135 사본(조율 쪽 지시 11-23): v134 규칙 — 맺혀 내려오는 액막의 덮는 비 = 같은 유량을 나르는 줄기 4줄의 지름 합 ÷ 액막 둘레(분배 · 목관 줄기와 같은 줄기 식, 사용자 지시 '액막도 같은 유량 기준').
        #  줄기 반지름 d(q) = max(1.1 mm, 2.585 mm × √(q ÷ 4)) — 4줄 바닥값 아래(q ≤ 0.72 kg/h)는 같은 덮는 비. 그래서 덮는 비의 비 = d(q2) ÷ d(q0)(화면 배율 · 둘레는 같은 카메라라 지워짐) ± 15 %. 전 판정(v132 규칙: 0.05 + 응축 ÷ 45)은 바꿈
        d = lambda q: max(1.1, 2.585 * math.sqrt(max(0.0, q) / 4)); q0x, q2x = (max(0.0, (p["calc"].get("L") or 0) - (p["calc"].get("R") or 0)) for p in (p0, p2))   # v141: 그림이 쓰는 양 = 컬럼 아래 액 − 환류(Lkg − Rkg)
        want = d(q2x) / d(q0x) if b0 > 0.05 and q0x > 0.05 else None
        ok = bool(b2 > b0 and c0 and c2 and want and c2 >= c0 * (1 - 0.02) and abs(c2 / c0 - want) <= 0.15 * want)
        add("X50", f"{DS3} {nm} — 컬럼 안 응축이 늘면 맺혀 내려오는 액막이 줄지 않고, 덮는 비가 줄기 식을 따른다(N13 · v135 사본: v134 같은 줄기 식 규칙)", ok, f"컬럼 안 응축 {b0} → {b2} kg/h · 컬럼 아래 액 − 환류 {round(q0x, 3)} → {round(q2x, 3)} kg/h · 덮는 비 {c0} → {c2}(비 {None if not (c0 and c2) else round(c2 / c0, 3)} · 줄기 식 비 {None if want is None else round(want, 3)}) · 셰이더 값 {fm0.get('c')} → {fm2.get('c')}", "응축이 늘고 덮는 비가 줄지 않음, 덮는 비의 비 = d(q2) ÷ d(q0) ± 15 %(q = 컬럼 아래 액 − 환류)")

def _xd_flood(g, add):   # N14
    sn = "새디자인 범람"; ps = [(t, g(sn, t)) for t in ("ds_fl0", "ds_fl1", "ds_fl2")]; ps = [(t, p) for t, p in ps if p]
    if not ps: return
    # 기준은 N14 그대로: 쌓인 액(계산 PR.mHeld − PR.mHold0)이 충전층 자리(PR.mFloodBed)의 2 %를 넘으면 그림 > 0, 테두리 = 범람비 ≥ 0.9(빨강 여부는 탐침에 색이 없어 안 봄 — 그쪽 A9도 켜짐만).
    # 그린 값(s4.flood.liq)은 쌓인 액 기둥의 높이(장면 단위)라 계산 비(쌓인 액 ÷ 자리)와 바로 견주지 않는다
    out = []; ok = True; seen = False
    for t, p in ps:
        c = p.get("calc") or {}; fl = ((p.get("s4") or {}).get("flood")) or {}; r = c.get("flood") or 0; liq = fl.get("liq") or 0; hx = max(0, (c.get("mHeld") or 0) - (c.get("mHold0") or 0)); bed = c.get("bed") or 0
        big = bed > 0 and hx > 0.02 * bed; seen = seen or big; ok = ok and (liq > 0 if big else True) and (bool(fl.get("glow")) == (r >= 0.9))
        out.append(f"{c.get('t', 0) / 3600:.1f} h 범람비 {r} · 쌓인 액 ÷ 자리 {round(hx / bed, 3) if bed else '–'} · 그린 쌓인 액 기둥 높이 {liq}(장면 단위) · 테두리 {fl.get('glow')}")
    add("X15", f"{DS3} 컬럼 범람 — 쌓인 액이 충전층 자리의 2 %를 넘으면 쌓인 액 그림, 테두리는 범람비 0.9부터(N14). 장면은 현실성 범람 장면과 같은 조작(컬럼 내경 100 mm · 스팀 헤더 160 ℃ · 개도 100 % · 유출 닫음) — 제안 장면(70 mm → 3 h)은 쌓인 액이 자리의 2 % 아래라 그림을 볼 수 없어서(그쪽 4단계 A9b)",
        ok if seen else None, " / ".join(out), "쌓인 액 > 자리의 2 %이면 그림 > 0 · 테두리 = 범람비 ≥ 0.9")

def _xd_lah(g, add):   # N15
    d = g("새디자인 받는 탱크 고액위", "ds_lah")
    if not d or not d.get("s"): return
    s = d["s"]; bad = [r for r in s if r[3] != r[4]]; saw = any(r[3] for r in s); sp = next((r for r in s if r[5]), None)
    add("X8", f"{DS3} 받는 탱크 LT HH 고리 = 계산 LT HH(PR.lah)(N15). v145부터 레시피도 인터록이 닫은 밸브를 다시 열지 않는다(이 장면은 운전원이 밸브 단추로 다시 열어 넘침을 본다)", saw and not bad,
        f"표본 {len(s)} · LT HH 본 표본 {sum(r[3] for r in s)} · 고리와 계산이 다른 표본 {len(bad)} · 넘침 줄기 {('켜짐 ' + str(round(sp[0] - s[0][0], 1)) + ' s') if sp else '없음'} · 마지막 넘친 양 {s[-1][7]} kg · 초류 밸브 {s[-1][8]}", "고리 = PR.lah(모든 표본) · LT HH를 본 표본 있음")
    # N15의 뒷부분(넘친 양이 늘면 넘침 줄기 · 웅덩이 반지름 증가 — 그쪽 4단계 A10은 적기만 했다). 표본 = [화면 s, 공정 s, 초류 kg, 계산 LT HH, 고리, 줄기, 웅덩이 반지름, 넘친 양 kg, 초류 밸브]
    # 넘친 양 0.05 kg과 켜지는 데 화면 2 s 여유는 가벼움 화면 X9 기준과 같은 값
    i0 = next((i for i, r in enumerate(s) if r[7] > 0.05), None)
    if i0 is None:
        add("X9", f"{DS3} 받는 탱크가 넘치면 넘침 줄기 · 웅덩이 — 넘친 양이 늘면 줄기가 보이고 웅덩이 반지름이 커진다(N15)", None, f"넘친 양이 0.05 kg을 넘지 않아 못 봄(마지막 {s[-1][7]} kg)", "–"); return
    t0 = s[i0][0]; on1 = next((r for r in s[i0:] if r[5]), None); dt = None if on1 is None else round(on1[0] - t0, 2)
    inc = [s[i] for i in range(max(1, i0), len(s)) if s[i][7] > s[i - 1][7] + 1e-6 and s[i][7] > 0.05 and s[i][0] - t0 > 2]
    off = [r for r in inc if not r[5]]; low = [r for r in s if r[5] and r[7] <= 0.05]
    sub = [r for i, r in enumerate(s[i0:]) if i == 0 or r[7] > s[i0 + i - 1][7] + 1e-6]; dec = [(a[6], b[6]) for a, b in zip(sub, sub[1:]) if b[6] < a[6] - 1e-6]
    ok = dt is not None and dt <= 2 and not off and not low and not dec and s[-1][6] > s[i0][6]
    add("X9", f"{DS3} 받는 탱크가 넘치면 넘침 줄기 · 웅덩이 — 넘친 양이 늘면 줄기가 보이고 웅덩이 반지름이 커진다(N15)", bool(ok),
        f"넘친 양 {s[i0][7]} → {s[-1][7]} kg(화면 {round(s[-1][0] - t0, 1)} s) · 0.05 kg 넘은 뒤 줄기 켜짐 {dt} s · 그 뒤 넘친 양이 는 표본 {len(inc)}개 중 줄기 꺼짐 {len(off)} · 0.05 kg 이하에서 줄기 켜짐 {len(low)} · 웅덩이 반지름 {s[i0][6]} → {s[-1][6]}(넘친 양이 늘 때 줄어든 표본 {len(dec)})",
        "0.05 kg 넘은 뒤 화면 2 s 안에 줄기 · 그 뒤 늘어난 표본마다 줄기 · 0.05 kg 이하면 줄기 없음 · 웅덩이 반지름이 줄지 않고 커짐")

def _xd_default(g, add):   # N16 · 와류(4단계 A17)
    st = g("새디자인 기본 표현", "ds_st")
    if st:
        add("XD", f"{DS3} 기본 표현 — 주소에 표현 없이 열면 새 디자인(이 PC의 그래픽) · 트렌드 접힘 · 안내 글에 '만드는 중' 없음(N16)", st.get("on") is True and st.get("pick") is None and st.get("trend") is True and "만드는 중" not in str(st.get("hint")),
            f"켜짐 {st.get('on')} · 시작 {st.get('want')} · 고른 값 {st.get('pick')} · 트렌드 접힘 {st.get('trend')} · 소프트웨어 렌더링 {(st.get('look') or {}).get('sw')} · 그래픽 '{st.get('gpu')}'", "켜짐 · 고른 값 없음 · 트렌드 접힘")
    a, b = g("새디자인 기본 표현 소프트웨어 렌더링", "ds_st"), g("새디자인 기본 표현 화면 가볍게", "ds_st")
    if a or b:
        a, b = a or {}, b or {}
        add("XD", f"{DS3} 기본 표현 — 소프트웨어 렌더링 · 화질 '화면 가볍게'(?lq=1)면 가벼움으로 시작(N16)", a.get("on") is False and (a.get("look") or {}).get("sw") is True and b.get("on") is False,
            f"소프트웨어 렌더링: 시작 {a.get('want')}(켜짐 {a.get('on')} · 소프트웨어 {(a.get('look') or {}).get('sw')}) · 화면 가볍게: 시작 {b.get('want')}(켜짐 {b.get('on')} · lq {(b.get('look') or {}).get('lq')})", "둘 다 가벼움(켜짐 거짓)")
    s0, s1 = g("새디자인 기본 표현 느린 화면", "ds_s0"), g("새디자인 기본 표현 느린 화면", "ds_s1")
    if s0 and s1:
        add("XD", f"{DS3} 기본 표현 — 사용자가 고르지 않았는데 새 디자인이 느리면(초당 20장 아래 5 s 넘게) 가벼움으로 바꾸고 알림 한 줄(N16)", s0.get("on") is True and s1.get("on") is False and bool(s1.get("auto")) and bool(s1.get("note")),
            f"전 {s0.get('on')} → 뒤 {s1.get('on')} · 자동 {s1.get('auto')} · 알림 '{s1.get('note')}'", "느리게 만든 뒤 가벼움 · 알림 있음")
    p = g("새디자인 기본 표현", "ds_def")
    if p:
        vx = p.get("vortex") or {}
        add("X36", f"{DS3} 정제기 액면 = 교반 와류 모양(계산 액면 식 M.surfY), 넓이 평균 = 계산 평균 액면 PR.h(4단계 A17)", bool(vx) and (vx.get("wall") or 0) > 0 and (vx.get("center") or 0) < 0 and abs(vx.get("meanCheck", 1)) <= 0.003,
            f"벽 쪽 {vx.get('wall')} m · 가운데 {vx.get('center')} m · 넓이 평균 − 평균 액면 {vx.get('meanCheck')} m", "벽 쪽 > 0 · 가운데 < 0 · 평균 차 ≤ 3 mm")

def _segh(a):   # 원의 활꼴 넓이 비 → 높이 비(지름에 대한) — 점검기 쪽에서 따로 푼다
    a = max(0.0, min(1.0, a))
    if a <= 0: return 0.0
    if a >= 1: return 1.0
    lo, hi = 0.0, 2 * math.pi
    for _ in range(40):
        th = (lo + hi) / 2
        if (th - math.sin(th)) / (2 * math.pi) < a: lo = th
        else: hi = th
    return (1 - math.cos((lo + hi) / 4)) / 2
def _xd_useal(g, add):   # v141: 환류 관 U자 액봉(수평 액면) — 요구목록 (Y)절
    sn = "새디자인 U자 액봉"; u = g(sn, "ds_u")
    if not u or not u.get("s") or not u.get("geo"): return
    S = u["s"]; ge = u["geo"]; mF = ge["mFull"]; mS = u.get("mSeal") or 0.2 * mF; Ri = ge["Ri"]; yB0, yB1, inv = ge["yB0"], ge["yB1"], ge["inv"]
    ic = next((i for i, r in enumerate(S) if r[23] == 0), len(S)); F = S[:ic]   # 환류 밸브를 닫기 전까지
    first = lambda f: next((r[0] for r in F if f(r)), None); fm = lambda v: "–" if v is None else f"{v:.1f}"
    tC, tp0, tp1, thq, tarr, tm, tfull, tov = first(lambda r: (r[21] or 0) >= 0.999), first(lambda r: r[17] > 0), first(lambda r: r[17] >= 1), first(lambda r: r[11] > 0), first(lambda r: r[15] == 1), first(lambda r: r[5] > 0.002), first(lambda r: r[16] == 1), first(lambda r: r[14] == 1)
    seq = [tC, tp0, tp1, thq, tarr, tm, tfull, tov]
    add("Y4", f"{DS3} U자 액봉 — 차례: 응축액 관 끝 → 티 아래 세로 관(데드 레그)이 차기 시작 → 다 참 → 환류 쪽 줄기 → 줄기가 고일 자리에 닿음 → 고임 → 다 참 → 넘침", all(x is not None for x in seq) and all(seq[i] <= seq[i + 1] + 0.11 for i in range(len(seq) - 1)),
        " → ".join(f"{n} {fm(v)}" for n, v in zip(["응축액 관 끝", "데드 레그 시작", "다 참", "줄기 시작", "닿음", "고임", "액봉 다 참", "넘침"], seq)) + " (화면 s)", "첫 시각이 이 차례(0.1 s 표본 한 칸 여유) · 모두 일어남")
    aft = [r for r in F if tarr is not None and r[0] >= tarr + 0.25]; dec = [(a[0], a[5], b[5]) for a, b in zip(F, F[1:]) if b[5] < a[5] - 1e-4]
    ks = [(mF - r[5]) / (mF - r[4]) for r in aft if r[4] is not None and mF - r[4] > 0.02]; over = [r for r in F if r[5] > min(mF, r[4] or 0) + 1e-3]
    tcf = first(lambda r: (r[4] or 0) >= mF - 1e-4); lag = None if tcf is None or tfull is None else round(tfull - tcf, 2)
    add("Y1", f"{DS3} U자 액봉 — 그림 채움이 계산 액봉 질량을 따라간다: 줄기가 닿기 전에는 고이지 않고, 닿은 뒤에는 (다 찬 값 − 그림) ÷ (다 찬 값 − 계산)이 그대로(남은 용량 비례 — 가벼움 표현과 같은 규칙), 줄지 않고 계산을 앞지르지 않으며, 계산이 다 차는 때 함께 다 찬다",
        bool(ks) and max(ks) / min(ks) - 1 <= 0.03 and not dec and not over and (tm is None or tarr is None or tm >= tarr - 0.11) and lag is not None and abs(lag) <= 0.35,
        f"닿은 뒤 표본 {len(ks)} · 비 {round(min(ks), 3) if ks else '–'} ~ {round(max(ks), 3) if ks else '–'} · 줄어든 표본 {len(dec)} · 계산을 앞지른 표본 {len(over)} · 닿음 {fm(tarr)} s · 첫 고임 {fm(tm)} s · 계산 다 참 → 그림 다 참 {lag} s", "비가 ± 3 % 안에서 그대로 · 줄어듦 0 · 앞지름 0 · 고임은 닿은 뒤 · 다 차는 때 차 ≤ 0.35 s")
    e1 = []; e2 = []; e3 = []; e0 = []
    for r in F:
        m, Yin, Yout, d, dP, rho = r[5], r[6], r[7], r[8], r[20], (r[25] or 1500)
        if m <= 1e-4: continue
        if m < mS - 1e-6: e0.append(max(abs(Yout - (yB0 + 2 * Ri * _segh(m / mS))), abs(Yin - Yout)))
        elif m < mF - 1e-6:
            lf = (m - mS) / (mF - mS); e1.append(abs(Yout - (yB1 + lf * (inv - yB1)))); e2.append(abs((Yin - Yout) - d * min(1, lf / 0.1)))
            if tarr is not None and r[0] >= tarr + 3 and dP is not None and lf > 0.15:
                dx = min(2.4 * Ri, dP * 133.322 / (rho * 9.81) / (ge["Dr"] / 1000) * 2 * Ri)
                if dx > 1e-5: e3.append(abs(d / dx - 1))
    add("Y2", f"{DS3} U자 액봉 — 액면 높이 = 식: 바닥 관은 활꼴 넓이 비 → 높이(양쪽 같음), 다리는 채움 비 × (넘침 높이 − 바닥 관 위 끝), 응축기 쪽 − 컬럼 쪽 = ΔP ÷ (ρ g)(계산 압력 차, 관 안지름에 대한 비)", bool(e1) and bool(e0) and max(e0) <= 0.001 and max(e1) <= 0.001 and max(e2) <= 0.0006 and bool(e3) and max(e3) <= 0.15,
        f"바닥 관 표본 {len(e0)} · 차 최대 {round(max(e0), 5) if e0 else '–'} · 다리 표본 {len(e1)} · 컬럼 쪽 액면 차 최대 {round(max(e1), 5) if e1 else '–'} · 액면 차의 차 최대 {round(max(e2), 5) if e2 else '–'} · ΔP 머리 ÷ 따로 계산한 값 − 1 최대 {round(max(e3), 3) if e3 else '–'}({len(e3)}표본)", "높이 ± 0.001(그림 길이) · 액면 차 ± 0.0006 · ΔP 머리 ± 15 %(따라가기 0.5 s 몫)")
    pre = [r for r in F if r[16] == 0 and r[10] < ge["xo"] - 1e-4]; ovbad = [r for r in F if r[14] == 1 and not ((r[3] or 0) > 0.05 and r[16] == 1)]
    tend = first(lambda r: r[14] == 1 and r[10] <= ge["xe"] + 0.03); trd = first(lambda r: r[22] == 1)
    add("Y3", f"{DS3} U자 액봉 — 넘침: 다 차기 전에는 컬럼 쪽 가로 관에 액이 없고, 넘침 층은 계산 환류가 흐를 때만, 앞머리는 2 s 안에 컬럼에 닿고 분배 줄기는 그 뒤", not pre and not ovbad and tov is not None and tend is not None and tend - tov <= 2 and (trd is None or trd >= tend - 0.31),
        f"다 차기 전 컬럼 쪽 가로 관에 액이 있던 표본 {len(pre)} · 환류 없이 넘침 층이 있던 표본 {len(ovbad)} · 넘침 시작 {fm(tov)} → 컬럼 도착 {fm(tend)} s · 분배 줄기 {fm(trd)} s", "표본 0 · 0 · 2 s 안 · 분배 줄기 ≥ 도착")
    fl = [r for r in F if (r[21] or 0) >= 0.999 and len(r) > 26 and r[26] is not None]; rate = (fl[-1][26] - fl[0][26]) / (fl[-1][0] - fl[0][0]) if len(fl) >= 10 and fl[-1][0] > fl[0][0] else None
    add("Y7", f"{DS3} 관 속 액 — 흐르는 동안 무늬가 움직인다(응축액 관의 무늬 위치 값이 늘어남. v136 ~ v139는 이 값이 늘 0이라 액이 멈춰 보였다)", rate is not None and rate > 0.05,
        f"응축액 관이 찬 표본 {len(fl)} · 무늬 위치 값 {fl[0][26] if fl else None} → {fl[-1][26] if fl else None} · 초당 {None if rate is None else round(rate, 3)}", "초당 0.05 넘게 늘어남")
    px = g(sn, "ds_u_pix"); img = _xpng("x_ds_useal.png")
    if px and img:
        w, h, bpp, rows = img; liq = lambda x, yy: (lambda p: p[2] - p[0] > 18 and p[2] > 95)(rows[yy][x * bpp:x * bpp + 3])   # 액 = 파랑이 빨강보다 뚜렷이 큼(빈 유리 · 흰 반사 줄은 아님)
        def tops(xs, y0, y1):
            out = []
            for x in xs:
                x = int(round(x))
                if not (0 <= x < w): continue
                t = next((yy for yy in range(max(0, int(y0)), min(h, int(y1))) if liq(x, yy) and liq(x, min(h - 1, yy + 2))), None)
                if t is not None: out.append(t)
            return out
        res = {}
        for key, cols in (("up", lambda l, r: [l + (r - l) * f for f in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)]), ("dn", lambda l, r: [l + (r - l) * f for f in (0.07, 0.10, 0.13, 0.87, 0.90, 0.93)])):
            l, r = px[key]["l"], px[key]["r"]; ye = (l[1] + r[1]) / 2; tp = tops(cols(l[0], r[0]), ye - 60, ye + 60)
            if len(tp) >= 5:   # 흰 무늬가 액면에 걸린 줄 하나는 뺀다
                md = sorted(tp)[len(tp) // 2]; far = max(tp, key=lambda v: abs(v - md))
                if abs(far - md) > 2: tp = [v for v in tp if v != far] if tp.count(far) == 1 else tp
            res[key] = (ye, tp)
        okp = all(len(tp) >= 4 and max(tp) - min(tp) <= 2 and abs(sum(tp) / len(tp) - ye) <= 4 for ye, tp in res.values())
        if okp:
            mu = lambda k: sum(res[k][1]) / len(res[k][1]); dpx = mu("up") - mu("dn"); dex = (px["Yin"] - px["Yout"]) * px["px"]; okp = abs(dpx - dex) <= 3
        else: dpx = dex = None
        add("Y5", f"{DS3} U자 액봉 — 화면 그림(멈춘 화면 화소): 양쪽 다리의 액면이 수평이고 계산한 높이에 있으며, 응축기 쪽이 ΔP 머리만큼 높다", bool(okp),
            f"그림 채움 {px.get('m')} kg · 컬럼 쪽 다리 액면 줄 {res['up'][1]}(계산 자리 {round(res['up'][0], 1)}) · 응축기 쪽 다리(줄기 밖 양 끝) {res['dn'][1]}(계산 자리 {round(res['dn'][0], 1)}) · 두 다리 액면 차 {None if dpx is None else round(dpx, 1)} px(계산 {None if dex is None else round(dex, 1)} px) · 멈춤 {px.get('paused')}",
            "다리마다 액면 줄의 흩어짐 ≤ 2 px · 계산 자리 ± 4 px · 두 다리 차 = 계산 ± 3 px")
    pf, pc, po = g(sn, "ds_u_full"), g(sn, "ds_u_close"), g(sn, "ds_u_open")
    if pf and pc and po:
        sf, sc, so = ((p.get("liq") or {}).get("seal") or {} for p in (pf, pc, po)); Rc = (pc.get("calc") or {}).get("R") or 0
        okc = Rc <= 0.05 and (sc.get("m") or 0) >= 0.999 * mF and abs((sc.get("Yout") or 0) - inv) <= 0.001 and (sc.get("ho") or 0) <= 0.002 and (sc.get("xh") or 0) >= ge["xo"] - 1e-3 and sc.get("yup") is not None and abs(sc["yup"] - (sf.get("Yin") or 0)) <= 0.002
        oko = bool(so.get("ovOn")) and (so.get("xh") or 9) <= ge["xe"] + 0.03 and so.get("yup") is None
        add("Y6", f"{DS3} U자 액봉 — 환류 밸브를 닫으면 넘침 층이 빠지고(컬럼 쪽 가로 관 빔) U자는 넘침 높이까지 남으며 밸브 앞 층은 닫는 순간의 높이로 멈춘다. 다시 열면 넘침이 이어진다", bool(okc and oko),
            f"닫기 전 응축기 쪽 액면 {sf.get('Yin')} · 닫고 8 s: 환류 {Rc} kg/h · 액봉 {sc.get('m')} kg · 컬럼 쪽 액면 {sc.get('Yout')}(넘침 높이 {inv}) · 넘침 층 {sc.get('ho')} · 밸브 앞 층 {sc.get('yup')} → 다시 열고 6 s: 넘침 {so.get('ovOn')} · 앞머리 {so.get('xh')}(컬럼 끝 {ge['xe']})",
            "닫음: 환류 ≤ 0.05 · 액봉 다 찬 채 · 컬럼 쪽 액면 = 넘침 높이 ± 0.001 · 층 ≤ 0.002 · 밸브 앞 층 = 닫기 전 액면 ± 0.002 / 다시 엶: 넘침 · 컬럼 도착")

def _xd_usoff(g, add):   # v141 Y13: 스팀을 끈 뒤 U자 액봉 — 넘침 층 · 줄기는 화면의 응축액 흐름 표시와 함께 꺼지고 액봉은 남는다
    sn = "새디자인 U자 액봉 스팀 끔"; s0, sa, sb = g(sn, "ds_so_0"), g(sn, "ds_so_a"), g(sn, "ds_so_b")
    if not (s0 and sa and sb): return
    q0, qa, qb = (x.get("seal") or {} for x in (s0, sa, sb)); ge = qa.get("geo") or q0.get("geo") or {}; mF = ge.get("mFull") or 0; Ri = ge.get("Ri") or 0; Dr = (ge.get("Dr") or 25) / 1000
    head = lambda q: None if q.get("dP") is None or not Ri else min(2.4 * Ri, q["dP"] * 133.322 / ((q.get("rho") or 1500) * 9.81) / Dr * 2 * Ri)   # ΔP ÷ (ρ g)를 그림 길이로(관 안지름에 대한 비 그대로)
    ha = head(qa); da = None if qa.get("Yin") is None else qa["Yin"] - qa["Yout"]
    okA = bool(sa.get("mv") == 0 and (sa.get("V") or 0) < (s0.get("V") or 0) and sa.get("cw") == 1 and qa.get("ovOn") and qa.get("inflow") and mF > 0 and qa.get("m", 0) >= mF - 1e-3
               and ha is not None and da is not None and abs(da - ha) <= max(0.15 * ha, 0.0005) and (qa.get("d") or 0) < (q0.get("d") or 0))
    add("Y13", f"{DS3} U자 액봉 — 스팀을 끈 뒤에도 증발이 남아 있는 동안은 넘침 층 · 줄기가 이어지고 응축기 쪽 − 컬럼 쪽 액면 = ΔP ÷ (ρ g)(증기가 줄어 머리도 줄어듦)", okA,
        f"6 h 증발 {s0.get('V')} kg/h · ΔP 머리 {q0.get('d')} → 스팀 0 % 뒤 {sa.get('t')} h: 증발 {sa.get('V')} · 환류 {sa.get('R')} · 유출 {sa.get('Dk')} kg/h · 응축액 관 흐름 표시 {sa.get('cw')} · 넘침 {qa.get('ovOn')} · 줄기 {qa.get('inflow')} · 액봉 {qa.get('m')} kg · 액면 차 {None if da is None else round(da, 4)}(식 {None if ha is None else round(ha, 4)})",
        "스팀 개도 0 % · 증발이 줄었고 흐름 표시가 켜져 있음 · 넘침 · 줄기 있음 · 액봉 다 참 · 액면 차 = 식 ± 15 % · 머리가 6 h보다 작음")
    offb = sb.get("cw") == 0   # 화면이 끓지 않는 것으로 그리는 때(증발 1 kg/h 아래 → 응축액 관 흐름 표시 꺼짐)
    okB = bool(offb and not qb.get("ovOn") and not qb.get("inflow") and (qb.get("ho") or 0) <= 0.05 * Ri and mF > 0 and qb.get("m", 0) >= mF - 1e-3 and qb.get("vis")
               and abs((qb.get("Yout") or 0) - (qb.get("inv") or 0)) <= 0.05 * Ri and (qb.get("pl") or 0) <= 0.02 and not (sb.get("C") and sb["C"][1] > sb["C"][0] + 1e-6))
    add("Y13", f"{DS3} U자 액봉 — 화면에서 응축액 흐름이 꺼지면(증발 1 kg/h 아래) 넘침 층 · 줄기 · 데드 레그도 비고 액봉은 넘침 높이까지 찬 채 남는다", okB if offb else None,
        f"{sb.get('t')} h: 증발 {sb.get('V')} · 계산 환류 {sb.get('R')} kg/h · 응축기 김 닿음 {sb.get('vc')} · 응축액 관 흐름 표시 {sb.get('cw')} · 응축액 관 그린 구간 {sb.get('C')} · 넘침 {qb.get('ovOn')} · 층 두께 {qb.get('ho')} · 줄기 {qb.get('inflow')} · 데드 레그 {qb.get('pl')} · 액봉 {qb.get('m')} kg(다 찬 값 {mF}) · 컬럼 쪽 액면 {qb.get('Yout')}(넘침 높이 {qb.get('inv')})",
        "흐름 표시가 꺼진 때: 넘침 0 · 층 ≤ 0.05 × 관 반지름 · 줄기 0 · 데드 레그 ≤ 0.02 · 응축액 관 빔 · 액봉 다 참 · 컬럼 쪽 액면 = 넘침 높이" if offb else "(이 시각에 흐름 표시가 아직 켜져 있어 판정하지 않음 — 장면 시각을 늦춘다)")
def _xd_tee(g, add):   # v142 Y15: 응축기 하부 분배기(티) — 줄기 굵기가 액면에서 이어지고, 고인 액 · 환류 액봉도 줄기와 같은 빠르기로 흐르며(사용자 11-25 둘째 지적), 무늬는 아래로 · 가로 갈래 겹침 지움
    sn = "새디자인 6 h 밸브"; a, b = g(sn, "ds_tee0"), g(sn, "ds_tee1")
    if not a or a.get("none"): return
    r = lambda x, n=4: None if x is None else round(x, n); near = lambda x, y, t: x is not None and y is not None and y > 0 and abs(x - y) <= t * y
    down = a.get("y0") is not None and a.get("y1") is not None and a["y0"] > a["y1"]; flow = a.get("vp") == 1 and (a.get("dk") or 0) > 0.05
    okS = flow and near(a.get("spd"), a.get("pspd"), 0.05) and (not a.get("ov") or near(a.get("rspd"), a.get("rsp"), 0.05))
    okJ = a.get("ys") is not None and a.get("yT") is not None and abs(a["ys"] - a["yT"]) <= 1e-4 and near(a.get("flL"), 2 * (a.get("riT") or 0), 0.01)
    ok = bool(down and okS and okJ and a.get("own") and (a.get("pc") or 0) > 0.5 and a.get("isT") == 1 and a.get("rt") is not None and abs(a["rt"] - a["riT"]) <= 0.002 * a["riT"] and a.get("vis"))
    add("Y15", f"{DS3} 응축기 하부 분배기(티): 응축액 관 줄기 굵기가 액면 위 관 지름 1배 구간에서 관 굵기로 이어지고, 티 아래 고인 액(유출 줄기 빠르기) · 환류 액봉(환류 줄기 빠르기)이 흐르며 무늬는 아래로(위 → 아래로 그림), 잠긴 줄기 · 가로 갈래 겹침 지움", ok,
        f"그린 방향 위 {r(a.get('y0'))} → 아래 {r(a.get('y1'))} · 유출 {r(a.get('dk'), 2)} kg/h · 티 무늬 {r(a.get('spd'))}(유출 줄기 {r(a.get('pspd'))}) · 환류 액봉 무늬 {r(a.get('rspd'))}(환류 줄기 {r(a.get('rsp'))}, 넘침 {a.get('ov')}) · 굵기 이음 액면 {r(a.get('ys'))}(티 액면 {r(a.get('yT'))}) · 길이 {r(a.get('flL'))}(관 지름 {r(2 * (a.get('riT') or 0))}) · 잠긴 줄기 {r(a.get('pc'), 2)} · 지우는 원기둥 {a.get('rt')}(티 관 {a.get('riT')})",
        "위 → 아래 · 무늬 = 줄기 빠르기 ± 5 % · 이음 액면 = 티 액면 · 길이 = 관 지름 · 잠긴 줄기 > 0.5 · 원기둥 = 티 관")
    if b and not b.get("none"):
        add("Y15", f"{DS3} 응축기 하부 분배기(티): 유출 밸브를 닫으면 티 아래 고인 액 무늬가 멈춘다", b.get("vp") == 0 and (b.get("spd") or 0) == 0, f"유출 밸브 {b.get('vp')} · 무늬 빠르기 {b.get('spd')}", "닫힘 · 0")
def _xd_walk(g, add):   # v142 Y16: 액(김)이 지나가는 길 둘러보기(사용자 11-25) — 김 띠 무늬에 각진 조각 없음 · 초류를 받는 동안 본류 쪽 막힌 다리가 참
    sn = "새디자인 6 h 밸브"; v = g(sn, "ds_vap"); d = g(sn, "ds_dl")
    if v and not v.get("none"):
        res = []
        for nm in ("x_ds_vap_a.png", "x_ds_vap_b.png"):
            img = _xpng(nm)
            if not img: res.append(None); continue
            w, h, bpp, rows = img; L = [[(r[x * bpp] * 299 + r[x * bpp + 1] * 587 + r[x * bpp + 2] * 114) // 1000 for x in range(w)] for r in rows]
            n6 = mx = s = s2 = 0
            for yy in range(h):
                row = L[yy]; nx = L[yy + 1] if yy + 1 < h else None
                for x in range(w):
                    a = row[x]; s += a; s2 += a * a
                    if x + 1 < w:
                        dd = abs(row[x + 1] - a); mx = max(mx, dd); n6 += dd >= 6
                    if nx is not None:
                        dd = abs(nx[x] - a); mx = max(mx, dd); n6 += dd >= 6
            N = w * h; sd = max(0.0, s2 / N - (s / N) ** 2) ** 0.5
            res.append((n6, mx, round(sd, 1), w, h))
        ok = len(res) == 2 and all(r is not None and r[0] <= 20 and r[2] >= 3 and r[3] >= 40 and r[4] >= 40 for r in res) and v.get("vis") and (v.get("d") or 0) > 0.05
        add("Y16", f"{DS3} 둘러보기 — 김 띠 무늬에 각진 조각이 없다(목관 김만 남긴 확대 화면 2장의 이웃 화소 밝기 차. 잡음 격자 꼭짓점 값이 이웃 칸에서 어긋나면 곧은 모서리 조각이 생겼다)", bool(ok),
            " · ".join((f"그림 {i + 1}: {r[3]}×{r[4]} px, 밝기 차 6 이상 {r[0]}쌍, 최대 {r[1]}, 밝기 표준편차 {r[2]}" if r else f"그림 {i + 1} 없음") for i, r in enumerate(res)) + f" · 김 진하기 {v.get('d')} · 무늬 자리 {v.get('phK')} · 끈 재질 {v.get('hid')}",
            "그림마다 밝기 차 6 이상 ≤ 20쌍 · 표준편차 ≥ 3(무늬가 보임)")
    if d and not d.get("none"):
        flow = d.get("M") == 0 and d.get("F") == 1 and d.get("P") == 1 and (d.get("Dk") or 0) > 0.05; bs = d.get("bs") or []; vm = d.get("vMr")
        leg = vm is not None and any(len(x) > 2 and x[2] in (1, -1) and x[0] <= 0.001 and abs(x[1] - vm) <= 0.002 for x in bs)   # 1 = 채우는 중 · -1 = 닫힌 밸브 앞에 고인 액(남겨 둔 끝 규칙이 같은 구간을 넘겨받는다)
        add("Y16", f"{DS3} 둘러보기 — 초류를 받는 동안 본류 쪽 막힌 다리(갈림 티 → 닫힌 본류 밸브)가 액으로 찬다(표시 규칙 0.8 s, 계산에 이 부피는 없다)", bool(flow and (d.get("dl") or 0) >= 0.999 and leg),
            f"본류 밸브 {d.get('M')} · 초류 밸브 {d.get('F')} · 유출 {d.get('Dk')} kg/h · 채움 {d.get('dl')} · 그린 구간 {bs} · 밸브 자리 {vm}", "닫힘 · 열림 · 유출 > 0.05 · 채움 1 · 관 시작 ~ 밸브 구간")

def _xd_warm(g, add):   # v142 Y17: 승온 중(끓기 전) 정제기 액 속에 김이 없고, 액 속 기체는 끓을 때만 기포로(사용자 11-25)
    pre = [x for x in (g("새디자인 승온", "ds_warm0"), g("새디자인 승온", "ds_warm1")) if x]; b = g("새디자인 6 h 밸브", "ds_warm6")
    if pre:
        cond = all((x.get("steam") or 0) > 1 and x.get("J") == 1 and (x.get("vdot") or 0) <= 1 and (x.get("Tm") or 0) < (x.get("Tb") or 0) for x in pre)
        ok = cond and all(x.get("jk") == 0 and x.get("head") == 0 and x.get("neck") == 0 and (x.get("bub") or 0) == 0 and not x.get("inL") for x in pre)
        add("Y17", f"{DS3} 승온 중(스팀 켜짐 · 끓기 전) 정제기 액 속에 김이 없다 — 자켓 안 김 띠를 그리지 않고(스팀은 투명한 기체), 정제기 위 · 목관 김과 기포 0, 액과 겹친 김 띠 없음", bool(ok),
            " · ".join(f"{x.get('t')} h: 내부 {x.get('Tm')} ℃(끓는점 {x.get('Tb')}) · 증발 {x.get('vdot')} · 스팀 {x.get('steam')} kg/h · 자켓 김 띠 {x.get('jk')} · 정제기 위 {x.get('head')} · 목관 {x.get('neck')} · 기포 {x.get('bub')} · 액과 겹친 김 {x.get('inL')}" for x in pre),
            "스팀 > 1 kg/h · 증발 ≤ 1 · 내부 < 끓는점에서 자켓 김 띠 없음 · 김 0 · 기포 0 · 액과 겹친 김 없음")
    if b:
        add("Y17", f"{DS3} 끓는 동안 액 속 기체는 기포로 그린다(그 깊이 끓는점 이상인 자리 · 액면 증발 — 지금 장면 규칙 13), 자켓 안 김 띠는 없다", bool((b.get("vdot") or 0) > 1 and (b.get("bub") or 0) > 0 and b.get("jk") == 0),
            f"{b.get('t')} h: 증발 {b.get('vdot')} kg/h · 기포 {b.get('bub')} · 터지는 기포 {b.get('dome')} · 자켓 김 띠 {b.get('jk')}", "증발 > 1 · 기포 > 0 · 자켓 김 띠 없음")

def _xd_v142pm(g, add):   # v142 Y18 · Y19 · Y20(사용자 11-25 오후): U자 액봉은 환류 몫으로 · 밸브 몸통과 색 · 정제기 위 김 깔때기
    sp = g("새디자인 U자 액봉 유출 열림", "ds_sp")
    if sp and sp.get("s"):
        S = sp["s"]; mS = sp.get("seal") or 0.55; fil = [r for r in S if r[2] is not None and r[2] < 0.99 * mS and (r[3] or 0) > 0.5 and r[4] == 1]
        flow = [r for r in fil if (r[1] or 0) > 0.05]; full = any(r[2] is not None and r[2] >= 0.999 * mS for r in S)
        ok = len(fil) >= 3 and len(flow) == len(fil) and full
        add("Y18", f"{DS3} 유출 밸브를 연 채 응축이 시작되면 U자 액봉이 차는 동안에도 유출이 흐른다 — U자는 환류 쪽(FCV-H073 뒤)이라 환류 몫으로만 찬다(전: U자가 다 찰 때까지 유출 0)", bool(ok),
            f"U자가 차는 표본 {len(fil)}개 가운데 유출 > 0.05 kg/h {len(flow)}개 · 그때 유출 {min((r[1] for r in fil), default=None)} ~ {max((r[1] for r in fil), default=None)} kg/h · 환류 {min((r[5] for r in fil), default=None)} ~ {max((r[5] for r in fil), default=None)} · U자 다 참 {full}(액봉 {mS} kg)",
            "차는 표본 ≥ 3 · 모두 유출 > 0.05 · 결국 다 참")
    vl = g("새디자인 6 h 밸브", "ds_vlv")
    if vl and vl.get("v") is not None:
        V = vl["v"]; badS = [x[0] for x in V if x[2] is not None and x[1] != x[2]]; badC = [x[0] for x in V if x[4]]; badB = [x[0] for x in V if x[5] is None or x[5] < 0.5]
        ok = bool(V) and not badS and not badC and not badB and vl.get("drainOpen") == 0 and (vl.get("drainShut") or 0) > 0 and (vl.get("eo") or 0) >= 1.5 and (vl.get("es") or 0) >= 1.5
        add("Y19", f"{DS3} 밸브는 닫힘 빨강 · 열림 초록으로 몸통 전체를 칠하고, 관보다 굵은 몸통이 관 속 액을 가린다. 이름 없는 수동 밸브(탱크 배수)는 닫힘. 색은 자체 발광이 내 빛 받는 면 · 그늘진 면이 같은 색", ok,
            f"밸브 {len(V)}개 · 상태와 다른 그림 {badS or 0} · 색이 상태와 다른 밸브 {badC or 0} · 몸통 ÷ 원뿔 반지름 {sorted(set(x[5] for x in V))}(관 1.0 ÷ 2.05 = 0.49 넘으면 관을 가림, 모자란 밸브 {badB or 0}) · 배수 밸브 초록 {vl.get('drainOpen')} · 빨강 {vl.get('drainShut')} · 자체 발광 ÷ 바탕색 밝기 초록 {vl.get('eo')} · 빨강 {vl.get('es')}",
            "상태 일치 · 색 일치 · 몸통 ≥ 0.5 · 배수 밸브 모두 빨강 · 자체 발광 ÷ 바탕색 ≥ 1.5")
    fu = g("새디자인 6 h 밸브", "ds_fun")
    if fu and not fu.get("none"):
        P = fu.get("parts") or []
        def _asp(p, e):   # v144: 높이 e에서 흐름 방향 무늬 길이(보이는 빠르기 ÷ 무늬 박자) ÷ 둘레 무늬 크기(띠 반지름 ÷ rad) — 1이면 둥근 덩어리, 클수록 곧은 빛살
            if not all(p.get(x) for x in ("r0", "r1", "i0", "kv", "rad", "K")): return None
            r = p["r0"] + (p["r1"] - p["r0"]) * e ** p["K"]; v = (1 / p["i0"]) * (p["r0"] / r) ** (2 / 3)
            return round((v / p["kv"]) / (r / p["rad"]), 2)
        AS = [[_asp(p, e) for e in (0, 0.5, 1)] for p in P]
        ok = bool(P) and all((p.get("K") or 0) >= 2 and p.get("aX") and p.get("fun") == 1 and (p.get("vr") or 0) >= 2 and p.get("net") == 1 for p in P) and all(a9[1] is not None and 0.4 <= a9[1] <= 3 and a9[2] <= 10 for a9 in AS) and any(p.get("vis") for p in P)
        add("Y20", f"{DS3} 정제기 위 김은 액면에서 곧게 오르다 노즐 가까이에서 휘어 모이는 깔때기이고, 단면이 좁아지는 만큼 무늬가 빨라진다(실제 속도 ∝ 1/r², 보이는 빠르기는 김 규칙 세제곱근 ∝ r^(−2/3)). 둘레 무늬 결은 높이 방향과 비슷하게(곧은 빛살 줄 없음)", bool(ok),
            " · ".join(f"띠 {i + 1}: 모이는 정도 η^{p.get('K')} · 노즐 쪽 무늬 빠르기 ÷ 액면 {p.get('vr')}배(무늬 자리 끝 {p.get('top')} — 높이 1) · 무늬 자리 속성 {p.get('aX')} · 깔때기 무늬 {p.get('fun')} · 김 사슬 {p.get('net')} · 둘레 결 rad {p.get('rad')} · 무늬 길이 ÷ 둘레 결 액면 {AS[i][0]} · 가운데 {AS[i][1]} · 노즐 {AS[i][2]} · 보임 {p.get('vis')}" for i, p in enumerate(P)) + f" · 진하기 {fu.get('d')}",
            "K ≥ 2 · 노즐 쪽 무늬 빠르기 ÷ 액면 ≥ 2 · 깔때기 무늬 · 김 사슬 · 무늬 길이 ÷ 둘레 결 가운데 0.4 ~ 3 · 노즐 ≤ 10(v143: 노즐 18 · 30 — 곧은 빛살) · 보임")

def _xd_net(g, add):   # v143 Y21: 노드별 흐름 잇기(사용자 11-25 밤)
    a = g("새디자인 6 h 밸브", "ds_net")
    if not a or not a.get("ch"): return
    C = a["ch"]; G = a.get("G"); rows = []; ok = G is not None
    for k in ("C", "P", "F", "FL"):
        c = C.get(k)
        if not c or not (c.get("spd") or 0) > 0 or c.get("ph") is None or abs(c["ph"] - G) > 1e-4: ok = False
    end = lambda c: c["x0"] + c["len"] * c["vi"]
    for up, dn in (("C", "P"), ("P", "F"), ("F", "FL")):
        cu, cd = C.get(up), C.get(dn)
        if not (cu and cd): ok = False; continue
        e = abs(end(cu) - cd["x0"]); rows.append(f"{up} → {dn} 무늬 자리 차 {e:.5f}"); ok = ok and e <= 1e-3
    rv = a.get("rv")
    if rv and C.get("FL"):
        e = abs(end(C["FL"]) - rv["x0"]); rt = (rv["rS"] or 0) * (rv["k0"] or 0); rp = rv.get("rP") or 0
        okr = e <= 1e-3 and rp > 0 and abs(rt - rp) <= 0.1 * rp and (rv.get("acc") or 0) > 0 and G is not None and abs((rv.get("ph") or 0) - G) <= 1e-4
        rows.append(f"FL → 초류 탱크 줄기 무늬 자리 차 {e:.5f} · 줄기 위 끝 반지름 {rt * 1000:.2f} mm(관 속 액 {rp * 1000:.2f} mm) · 가속 {rv.get('acc')}"); ok = ok and okr
    else: ok = False; rows.append("초류 탱크 줄기 없음")
    t = a.get("tee")
    if t: rows.append(f"티 기둥 위상 {t.get('ph')}(× (1 − {t.get('bv')}) = 공용 {G}) · 잠긴 줄기 위상 {t.get('phc')}"); ok = ok and t.get("ph") is not None and abs(t["ph"] * (1 - (t.get("bv") or 0)) - G) <= 1e-3 and t.get("phc") is not None and abs(t["phc"] - G) <= 1e-4
    add("Y21", f"{DS3} 노드별 흐름 잇기 — 흐르는 관(응축액 C · 유출 P · 초류 F · 초류 탱크 입구 FL) · 티 기둥 · 초류 탱크 줄기가 공용 위상을 같이 쓰고, 노드마다 무늬 자리가 이어진다. 탱크 줄기 위 끝 굵기 = 들어오는 관 속 액 굵기, 아래로 빨라진다", bool(ok),
        f"공용 위상 {G} · " + " · ".join(rows) + " · 빠르기 " + " · ".join(f"{k} {C[k]['spd']}" for k in C), "위상 = 공용 · 무늬 자리 차 ≤ 0.001 · 위 끝 반지름 ± 10 % · 가속 > 0")

def _xd_white(g, add):   # v144 Y22: 관 속 액 흰빛(사용자 11-26 "물이 흰색이너무 쎄게표현되어서 이렇게 전체가 하얗게표현될때도잇던데 좀 과하지않나")
    w = g("새디자인 이상 상황 스팀 과다", "ds_wh"); WH_MAX = 0.05
    if not w or w.get("none"): return
    res = []
    for nm in ("x_ds_wh_a.png", "x_ds_wh_b.png", "x_ds_wh_c.png"):
        img = _xpng(nm)
        if not img: res.append(None); continue
        wd, h, bpp, rows = img; cs = [(rows[y9][x * bpp], rows[y9][x * bpp + 1], rows[y9][x * bpp + 2]) for y9 in (0, h - 1) for x in (0, wd - 1)]
        bg = tuple(sorted(c[i] for c in cs)[len(cs) // 2] for i in range(3))   # 배경(네 모서리 가운데값)
        liq = wht = 0
        for y9 in range(h):
            r9 = rows[y9]
            for x in range(wd):
                R, G, B = r9[x * bpp], r9[x * bpp + 1], r9[x * bpp + 2]
                if abs(R - bg[0]) + abs(G - bg[1]) + abs(B - bg[2]) <= 40: continue
                liq += 1; mn = min(R, G, B)
                if mn >= 190 and max(R, G, B) - mn <= 45: wht += 1
        res.append((wht, liq))
    fr = [round(r9[0] / r9[1], 3) if r9 and r9[1] else None for r9 in res]
    ok = all(r9 is not None and r9[1] >= 2000 for r9 in res) and all(f is not None and f <= WH_MAX for f in fr) and (w.get("vC") or 0) > 0.4
    add("Y22", f"{DS3} 관 속 액 흰빛 — 응축액이 많을 때(스팀 과다) 응축기 아래 떨어지는 줄기 · 분배기 티 · 환류 관의 액이 통째로 하얗게 보이지 않는다(관 속 액 재질만 남긴 화면 3장의 거의 흰 화소 몫 — 흰 무늬는 작은 반짝임 · 빛 반사만, 밝은 덩어리는 옅은 파랑)", bool(ok),
        " · ".join((f"그림 {i + 1}: 액 화소 {r9[1]} · 거의 흰 {r9[0]}({fr[i]})" if r9 else f"그림 {i + 1} 없음") for i, r9 in enumerate(res)) + f" · 응축액 관 무늬 빠르기 {w.get('vC')} · 무늬 자리 배율 {w.get('viC')} · 환류 {w.get('R')} · 유출 {w.get('D')} · 증발 {w.get('vdot')} kg/h · 끈 재질 {w.get('hid')}",
        f"그림마다 거의 흰(가장 어두운 색 ≥ 190 · 색 차 ≤ 45) ≤ {WH_MAX} · 액 화소 ≥ 2000 · 빠르기 > 0.4")

def _xd_vnet(g, add):   # v144 Y23: 김 띠 잇기(v143에서 남긴 것 — 사용자 11-25 밤 노드별 흐름 잇기)
    a = g("새디자인 6 h 밸브", "ds_vnet")
    if not a or a.get("none"): return
    B = a.get("b") or {}; G = a.get("G"); rows = []; ok = G is not None and "head" in B
    chain = [k for k in ("head", "neck", "col", "V", "bon", "tub", "T2", "C2", "S") if k in B]
    def end(k):
        b = B[k]; p = b["p"][0]
        if k == "head": return p["x0"] + b["len"] * (p["top"] or 1) * p["i0"]
        return p["x0"] + b["len"] * (p["i0"] + p["i1"]) / 2
    kv0 = B["head"]["p"][0].get("kv") if "head" in B else None
    for k in chain + (["rfx"] if "rfx" in B else []):
        for p in B[k]["p"]:
            if p.get("net") != 1 or p.get("g") is None or G is None or abs(p["g"] - G) > 1e-4 or p.get("kv") != kv0: ok = False
    for up, dn in zip(chain, chain[1:]):
        e = abs(end(up) - B[dn]["p"][0]["x0"]); rows.append(f"{up} → {dn} {e:.5f}"); ok = ok and e <= 1e-3
    sA = sorted({B[k]["p"][0]["seed"] for k in chain}); sB = sorted({B[k]["p"][1]["seed"] for k in ("head", "col", "V", "bon") if k in B and len(B[k]["p"]) > 1})
    ok = ok and len(sA) == 1 and len(sB) == 1
    sp = lambda k, j="i0": (1 / B[k]["p"][0][j]) if B.get(k) and B[k]["p"][0].get(j) else 0
    okv = sp("neck") > sp("col") > 0 and 0 < sp("bon", "i1") < sp("bon", "i0"); ok = ok and okv
    add("Y23", f"{DS3} 김 띠 잇기 — 정제기 위 → 목관 → 컬럼 → 증기관 → 응축기 뚜껑 → 관 → 2차 쪽 김 띠가 공용 위상 · 같은 무늬 박자를 쓰고 이음매마다 무늬 자리가 이어진다(사슬마다 씨앗 하나). 보이는 빠르기는 김 규칙(실제 속도의 세제곱근) — 좁은 목관은 컬럼보다 빠르고, 넓어지는 응축기 뚜껑에서 느려진다", bool(ok),
        f"공용 위상 {G} · 무늬 결 {kv0} · 이음매 무늬 자리 차 " + " · ".join(rows) + f" · 씨앗 A {sA} · B {sB} · 빠르기 목관 {sp('neck'):.3f} · 컬럼 {sp('col'):.3f} · 증기관 {sp('V'):.3f} · 뚜껑 {sp('bon'):.3f} → {sp('bon', 'i1'):.3f} · 관 {sp('tub'):.3f} m/s(화면)",
        "위상 = 공용 · 무늬 결 같음 · 이음매 차 ≤ 0.001 · 씨앗 사슬마다 하나 · 목관 > 컬럼 · 뚜껑 끝 < 입구")

def _xd_drip(g, add):   # v144 Y24: 목관 끝 → 정제기 액(사용자 11-26 "너무 우수수수 떨어지는느낌 … 컬럼하부배관에선 천천히나오다가 정제기로갈땐 퍼버버벅 … 자연스럽게 이을수있을까")
    d = g("새디자인 6 h 밸브", "ds_drip")
    if not d: return   # 그 장면을 안 돌린 묶음
    if not d.get("on"): add("Y24", f"{DS3} 목관 끝 → 정제기 액 — 6 h에 목관 줄기가 꺼져 있음", False, f"{d}", "켜짐"); return
    v0 = d.get("v0") or 0; n = d.get("n") or 0; rim = d.get("rim") or 0
    ok = (d.get("sites") or 0) >= 3 and d.get("pend") == d.get("sites") and 0 < n <= 40 and v0 > 0 and (d.get("vmin") or 0) >= 0.95 * v0 and (d.get("vmax") or 9) <= 2.5 * v0 * 1.05 and rim > 0 and abs((d.get("rmin") or 0) - rim) <= 0.05 * rim and abs((d.get("rmax") or 0) - rim) <= 0.05 * rim
    add("Y24", f"{DS3} 목관 끝 → 정제기 액 — 목관 벽 액막이 노즐 끝 둘레 방울 자리마다 맺혀 자라다 떨어지고, 떨어지는 방울은 목관 액막 무늬 빠르기에서 출발해 액면에서 2.5배까지 고르게 빨라진다(받는 탱크 줄기와 같은 표시 규칙 — 전: 노즐 단면 아무 데서나 초당 수백 개가 실제 중력으로 쏟아져 공중 130개 · 액면 초속 2.9 m)", bool(ok),
        f"컬럼 아래 액 {d.get('Lkg')} kg/h · 방울 자리 {d.get('sites')} · 맺힌 방울 {d.get('pend')} · 공중 방울 {n}개 · 빠르기 {d.get('vmin')} ~ {d.get('vmax')} m/s(목관 액막 무늬 {v0}) · 노즐 가운데에서 {d.get('rmin')} ~ {d.get('rmax')} m(자리 {rim}) · 떨어지는 높이 {d.get('h')} m",
        "자리 ≥ 3 · 맺힌 방울 = 자리 · 공중 1 ~ 40개 · 출발 ≥ 0.95 × 액막 · 끝 ≤ 2.5 × 1.05 × 액막 · 자리 반지름 ± 5 %")

def _xd_bubd(g, add):   # v144 Y25: 보기용 기포(사용자 11-26 '액 속 기포도')
    b = g("새디자인 6 h 밸브", "ds_bubd")
    if not b: return
    ok = (b.get("vdot") or 0) > 1 and b.get("on") == 1 and "보기용" in (b.get("label") or "") and "계산 아님" in (b.get("tip") or "") and (b.get("deep") or 0) + (b.get("mid") or 0) >= 10 and (b.get("disp") or 0) >= 10 and (b.get("domes") or 0) >= 3
    add("Y25", f"{DS3} 정제기 끓는 모습 — 끓는 동안 자켓 벽 · 바닥에서 기포가 올라오고 액면이 보글거린다(표시 탭 '기포(보기용)', 기본 켜짐 · 계산 아님이라고 밝힘 — 진공에서는 액 무게 때문에 액면 1 mm 아래로는 끓지 않는다)", bool(ok),
        f"증발 {b.get('vdot')} kg/h · 정제기 {b.get('P')} torr · 핵비등 깊이 {b.get('zN')} m · 기포 {b.get('n')}개(액면 10 cm 아래 {b.get('deep')} · 2 ~ 10 cm {b.get('mid')} · 보기용 {b.get('disp')}) · 액면 터지는 기포 {b.get('domes')} · 표시 칸 '{b.get('label')}' 켜짐 {b.get('on')} · 설명 '{b.get('tip')}'",
        "끓는 중 · 켜짐 · 이름 '보기용' · 설명 '계산 아님' · 액면 2 cm 아래 기포 ≥ 10 · 보기용 ≥ 10 · 터지는 기포 ≥ 3")

def judge_ds(g, add):
    """새 디자인 판정 줄 — 장면마다 따로 판정하고, 판정 계산에서 오류가 나면 그 장면만 'X0' 줄로 남긴다."""
    import traceback
    for nm, fn in (("끓기 시작", _xd_boil), ("김 진하기 규칙", _xd_n3), ("6 h 밸브", _xd_valve), ("U자 액봉", _xd_useal), ("U자 액봉 스팀 끔", _xd_usoff), ("티 고인 액", _xd_tee), ("둘러보기", _xd_walk), ("승온", _xd_warm), ("v142 오후", _xd_v142pm), ("흐름 잇기", _xd_net), ("흰빛", _xd_white), ("김 잇기", _xd_vnet), ("목관 끝 방울", _xd_drip), ("보기용 기포", _xd_bubd), ("1차 냉매 95도", _xd_c1hot), ("진공 펌프 정지", _xd_pstop), ("배치 끝", _xd_end), ("이상 상황", _xd_ab), ("범람", _xd_flood), ("받는 탱크 LT HH", _xd_lah), ("기본 표현", _xd_default)):
        try: fn(g, add)
        except Exception as e: add("X0", f"새 디자인 판정 계산 오류 — {nm}", False, f"{type(e).__name__}: {e} · {traceback.format_exc(limit=3)[-400:]}", "오류 0")
# <<< 새 디자인 판정 끝

def static(html_path):
    R = []; h = html_path.read_text(encoding="utf-8")
    left = {k: h.count(k) for k in OLD if h.count(k)}
    R.append({"id": "M1", "name": "환류 = FICH073·FCV-H073, 유출 = FICH072·FCV-H072 — 옛 번호(FIC-072·073, FCV-072·073)와 옛 이름표(유출 FT-H073, TIC-H071D 응축액 출구, TI-H075 탑 온도) 0개", "ok": not left and h.count("FICH073") >= 10 and h.count("FICH072") >= 5 and h.count("FCV-H073") >= 5,
              "val": (f"옛 표기 남음 {left}" if left else "옛 표기 0개") + f" · FICH073 {h.count('FICH073')}곳 · FICH072 {h.count('FICH072')}곳 · FCV-H073 {h.count('FCV-H073')}곳 · FCV-H072 {h.count('FCV-H072')}곳", "crit": "옛 표기 0개"})
    # v145 Y27: LT HH Interlock 표기(사용자 11-27) — 주석(/* */ · //)을 뺀 빌드 글에 '고액위' 0개, 'LT HH Interlock' 5곳 이상
    hs = re.sub(r"/\*.*?\*/", "", h, flags=re.S); hs = re.sub(r"(?m)(^|[^:'\"])//[^\n]*$", r"\1", hs)
    o27, n27 = hs.count("고액위"), hs.count("LT HH Interlock")
    R.append({"id": "Y27", "name": "LT HH Interlock 표기(사용자 11-27 '고액위 인토록이런건 단어가 너무 이상하다 LT HH Interlock 이라고하면되지') — 화면 글(코드 주석을 뺀 빌드)에 '고액위' 0개 · 'LT HH Interlock'이 운전 패널 · 알림 칩 · 운전 안내 · 기록 · 입력 설명에", "ok": o27 == 0 and n27 >= 5, "val": f"'고액위' {o27}곳 · 'LT HH Interlock' {n27}곳", "crit": "'고액위' 0 · 'LT HH Interlock' ≥ 5"})
    # v146 Y28: 입력 기본 초기 액 온도 35 ℃(사용자 11-27 "35 ℃로 바꾸기") — 입력칸 기본값과 빈칸일 때 쓰는 값
    m28 = re.search(r'<input id="T0"[^>]*value="([0-9.]+)"', h); fb28 = 'num("T0", -50, 300, 35)' in h
    R.append({"id": "Y28", "name": "입력 기본 초기 액 온도 35 ℃(사용자 11-27 '35 ℃로 바꾸기' — 현장 DB 승온 시작 30 ~ 40 ℃의 가운데): 입력칸 기본값 · 빈칸일 때 쓰는 값", "ok": bool(m28) and m28.group(1) == "35" and fb28, "val": f"입력칸 {m28.group(1) if m28 else '없음'} ℃ · 빈칸일 때 {'35' if fb28 else '35 아님'} ℃", "crit": "35 · 35"})
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
