// 그림 안 글·말풍선·화살표의 겹침을 도면 좌표로 센다(점검_발표자료.py가 브라우저에서 돌린다).
(()=>{const out={};
const ccw=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
const hit=(s,t)=>{const d1=ccw(s[0],s[1],t[0]),d2=ccw(s[0],s[1],t[1]),d3=ccw(t[0],t[1],s[0]),d4=ccw(t[0],t[1],s[1]);return d1*d2<0&&d3*d4<0};
const segRect=(s,r,m)=>{const x0=r.x+m,y0=r.y+m,x1=r.x+r.w-m,y1=r.y+r.h-m;if(x1<=x0||y1<=y0)return false;const ins=p=>p[0]>x0&&p[0]<x1&&p[1]>y0&&p[1]<y1;if(ins(s[0])||ins(s[1]))return true;
  return [[[x0,y0],[x1,y0]],[[x1,y0],[x1,y1]],[[x1,y1],[x0,y1]],[[x0,y1],[x0,y0]]].some(g=>hit(s,g))};
for(const svg of document.querySelectorAll('figure svg')){if(svg.closest('[hidden]'))continue;const vb=svg.viewBox.baseVal;const items=[];
for(const t of svg.querySelectorAll('text')){if(t.closest('[hidden]'))continue;const b=t.getBBox();if(!b.width)continue;const g=t.closest('.co');const grp=t.closest('[data-grp]');
  items.push({k:t.textContent.trim().slice(0,22),x:b.x,y:b.y,w:b.width,h:b.height,co:g?g.getAttribute('data-f'):null,grp:grp?grp.getAttribute('data-grp'):null,cls:t.getAttribute('class')})}
const ov=[],outb=[];for(let i=0;i<items.length;i++){const a=items[i];if(a.x<vb.x+2||a.y<vb.y+2||a.x+a.w>vb.x+vb.width-2||a.y+a.h>vb.y+vb.height-2)outb.push(a.k);
 for(let j=i+1;j<items.length;j++){const b=items[j];if(a.co&&a.co===b.co)continue;const w=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x),h=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);if(w>2&&h>4.5)ov.push(a.k+' × '+b.k)}}
// 말풍선 안 글이 상자 밖으로 나가는지
const spill=[];for(const g of svg.querySelectorAll('.co')){const r=g.querySelector('rect').getBBox();for(const t of g.querySelectorAll('text')){const b=t.getBBox();if(b.x<r.x+3||b.x+b.width>r.x+r.width-3||b.y<r.y+1||b.y+b.height>r.y+r.height-1)spill.push(g.getAttribute('data-f')+':'+t.textContent.trim().slice(0,18)+' '+Math.round(b.x+b.width-(r.x+r.width)))}}
// 글상자(판·값 상자) 안 글이 상자 밖으로 나가는지
for(const g of svg.querySelectorAll('[data-panel]')){const r=g.querySelector('rect').getBBox();for(const t of g.querySelectorAll('text')){const b=t.getBBox();if(!b.width)continue;if(b.x<r.x+3||b.x+b.width>r.x+r.width-3||b.y<r.y+1||b.y+b.height>r.y+r.height-1)spill.push('판 '+g.getAttribute('data-panel')+':'+t.textContent.trim().slice(0,18)+' '+Math.round(b.x+b.width-(r.x+r.width)))}}
// 말풍선끼리, 말풍선과 글
const boxes=[...svg.querySelectorAll('.co')].map(g=>{const r=g.querySelector('rect').getBBox();return {k:g.getAttribute('data-f'),x:r.x,y:r.y,w:r.width,h:r.height}});const bo=[];
for(let i=0;i<boxes.length;i++){for(let j=i+1;j<boxes.length;j++){const a=boxes[i],b=boxes[j];const w=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x),h=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);if(w>0&&h>0)bo.push(a.k+' × '+b.k)}
 for(const t of items){if(t.co)continue;const a=boxes[i];const w=Math.min(a.x+a.w,t.x+t.w)-Math.max(a.x,t.x),h=Math.min(a.y+a.h,t.y+t.h)-Math.max(a.y,t.y);if(w>1&&h>1)bo.push(a.k+' × 글 '+t.k)}}
// 판(글상자)과 말풍선·바깥 글
const panels=[...svg.querySelectorAll('[data-panel]')].map(g=>{const r=g.querySelector('rect').getBBox();return {k:g.getAttribute('data-panel'),x:r.x,y:r.y,w:r.width,h:r.height}});
for(const p of panels){for(const a of boxes){const w=Math.min(a.x+a.w,p.x+p.w)-Math.max(a.x,p.x),h=Math.min(a.y+a.h,p.y+p.h)-Math.max(a.y,p.y);if(w>0&&h>0)bo.push('판 '+p.k+' × '+a.k)}
 for(const t of items){if(t.grp===p.k)continue;const w=Math.min(p.x+p.w,t.x+t.w)-Math.max(p.x,t.x),h=Math.min(p.y+p.h,t.y+t.h)-Math.max(p.y,t.y);if(w>1&&h>1)bo.push('판 '+p.k+' × 글 '+t.k)}}
// 화살표: 서로 엇갈림 · 남의 말풍선을 지남 · 글을 지남 · 판을 지남
const lds=[...svg.querySelectorAll('path.ld')].filter(p=>!p.closest('[hidden]')).map(p=>{const pts=p.getAttribute('d').slice(1).split('L').map(s=>s.trim().split(/\s+/).map(Number));const sg=[];for(let i=0;i+1<pts.length;i++)sg.push([pts[i],pts[i+1]]);return {of:p.getAttribute('data-of')||'?',sg}});
const cross=[],lbox=[],ltext=[];
for(let i=0;i<lds.length;i++){const a=lds[i];
 for(let j=i+1;j<lds.length;j++){const b=lds[j];if(a.sg.some(s=>b.sg.some(t=>hit(s,t))))cross.push(a.of+' × '+b.of)}
 for(const bx of boxes){if(bx.k===a.of)continue;if(a.sg.some(s=>segRect(s,bx,0)))lbox.push(a.of+' → 말풍선 '+bx.k)}
 for(const p of panels){if(a.sg.some(s=>segRect(s,p,0)))lbox.push(a.of+' → 판 '+p.k)}
 for(const t of items){if(t.co)continue;if(t.grp&&panels.some(p=>p.k===t.grp))continue;if(a.sg.some(s=>segRect(s,t,1.5)))ltext.push(a.of+' → 글 '+t.k)}}
out[svg.id]={texts:items.length,leaders:lds.length,overlap:ov,out:outb,spill,box:bo,cross,lbox,ltext}}
return JSON.stringify({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,figs:out})})()
