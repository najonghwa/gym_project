# -*- coding: utf-8 -*-
"""발표자료 페이지 틀 — 스타일과 동작(탭 · 장면 넘기기 · 그림과 카드 잇기 · 이상 상황 고르기 · 발표 순서의 진행 표시줄)."""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&family=STIX+Two+Text:ital,wght@0,500;1,500&display=swap">')

CSS = r"""
/* 배치: 위에 탭 줄, 장면마다 큰 설비 그림 하나(그림 안에 공식 말풍선과 화살표)와 그 아래 세 칸(공식 · 가정과 추정 · DB).
   색은 흐름의 뜻에만 쓴다: 열 = 주황, 증기 = 회청, 액 = 파랑, 냉매 = 청록, 진공 = 보라. 배지: 가정 = 노랑, 추정 = 자주, DB = 초록 */
:root {
  --bg:#f1f3f6; --panel:#ffffff; --ink:#17202b; --sub:#556272; --line:#d2d9e2; --soft:#e8ecf1;
  --heat:#c2410c; --heat-soft:#fde6d8; --vap:#6b7f97; --vap-soft:#e3e9f0; --liq:#1b64c4; --liq-soft:#cfe2fb; --brine:#0a857f; --vac:#7257c4;
  --acc:#0f6e66; --acc-soft:#d6efec;
  --est:#8a5d00; --est-soft:#fbedc2; --hard:#a8246a; --hard-soft:#fbdfec; --db:#19744a; --db-soft:#d9f1e4; --dwg:#3d5068; --dwg-soft:#e1e8f0;
  --ok:#19744a; --ok-soft:#d9f1e4; --ng:#b93a0b; --ng-soft:#fde3d6;
  --f-body:"IBM Plex Sans KR","Apple SD Gothic Neo","Malgun Gothic",sans-serif; --f-mono:"IBM Plex Mono",ui-monospace,Consolas,monospace;
  --f-math:"STIX Two Text","Cambria Math","Times New Roman","IBM Plex Sans KR","Malgun Gothic",serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg:#0e1319; --panel:#171f29; --ink:#e8eef5; --sub:#9aa8b9; --line:#2a3542; --soft:#1e2733;
  --heat:#ff9160; --heat-soft:#40210f; --vap:#a7b8cc; --vap-soft:#232e3b; --liq:#66a9ff; --liq-soft:#17355c; --brine:#48cfc6; --vac:#b19df3;
  --acc:#45c9ba; --acc-soft:#11322f;
  --est:#f1c453; --est-soft:#3a2e0f; --hard:#f48bbd; --hard-soft:#3d1a2c; --db:#5bd39c; --db-soft:#133224; --dwg:#b3c2d4; --dwg-soft:#243140;
  --ok:#5bd39c; --ok-soft:#133224; --ng:#ff9160; --ng-soft:#40210f; color-scheme:dark } }
:root[data-theme="dark"] {
  --bg:#0e1319; --panel:#171f29; --ink:#e8eef5; --sub:#9aa8b9; --line:#2a3542; --soft:#1e2733;
  --heat:#ff9160; --heat-soft:#40210f; --vap:#a7b8cc; --vap-soft:#232e3b; --liq:#66a9ff; --liq-soft:#17355c; --brine:#48cfc6; --vac:#b19df3;
  --acc:#45c9ba; --acc-soft:#11322f;
  --est:#f1c453; --est-soft:#3a2e0f; --hard:#f48bbd; --hard-soft:#3d1a2c; --db:#5bd39c; --db-soft:#133224; --dwg:#b3c2d4; --dwg-soft:#243140;
  --ok:#5bd39c; --ok-soft:#133224; --ng:#ff9160; --ng-soft:#40210f; color-scheme:dark }
* { box-sizing:border-box }
body { background:var(--bg); color:var(--ink); font:15px/1.65 var(--f-body); margin:0 }
button { font:inherit; color:inherit }
.app { max-width:1320px; margin:0 auto; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:14px 56px; display:grid; gap:14px }
/* 머리 줄 */
.top { display:flex; flex-wrap:wrap; align-items:center; gap:10px 18px; padding:6px 0 10px; border-bottom:1px solid var(--line) }
.brand { display:flex; flex-direction:column; min-width:0; margin-right:auto }
.brand b { font-size:17px; letter-spacing:-.01em } .brand span { font-size:12.5px; color:var(--sub) }
.tabs { display:flex; flex-wrap:wrap; gap:4px }
.tabs button { border:1px solid transparent; background:transparent; padding:6px 13px; border-radius:8px; cursor:pointer; font-weight:600; color:var(--sub) }
.tabs button:hover { background:var(--soft) } .tabs button[aria-selected="true"] { background:var(--ink); color:var(--panel) }
.pager { display:flex; align-items:center; gap:6px; font:500 12.5px var(--f-mono); color:var(--sub) }
.pager button { border:1px solid var(--line); background:var(--panel); width:32px; height:30px; border-radius:8px; cursor:pointer }
.pager button:hover { border-color:var(--ink) } button:focus-visible, a:focus-visible { outline:2px solid var(--acc); outline-offset:2px }
/* 구간 줄 */
.nodes { display:flex; flex-wrap:wrap; gap:6px }
.nodes button { display:flex; align-items:center; gap:7px; border:1px solid var(--line); background:var(--panel); padding:4px 11px 4px 5px; border-radius:999px; cursor:pointer; font-size:13px; color:var(--sub) }
.nodes button i { font:700 12px var(--f-mono); font-style:normal; width:22px; height:22px; border-radius:50%; background:var(--soft); color:var(--ink); display:grid; place-items:center }
.nodes button[aria-current="true"] { border-color:var(--ink); color:var(--ink); font-weight:600 } .nodes button[aria-current="true"] i { background:var(--ink); color:var(--panel) }
/* 장면 */
.scene { display:grid; gap:14px; min-width:0 }
.sh { display:flex; flex-wrap:wrap; align-items:baseline; gap:6px 12px }
.sh .num { font:700 15px var(--f-mono); width:30px; height:30px; border-radius:50%; background:var(--ink); color:var(--panel); display:grid; place-items:center; align-self:center }
.sh h2 { font-size:23px; line-height:1.25; margin:0; letter-spacing:-.01em; text-wrap:balance }
.sh .verb { font-size:13px; font-weight:600; color:var(--acc); border:1px solid var(--acc); border-radius:999px; padding:0 9px }
.sh .tag { font:500 12px var(--f-mono); color:var(--sub) }
.q { margin:0; font-size:16.5px; font-weight:600 } .say { margin:0; color:var(--sub); max-width:86ch }
figure { margin:0; background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:10px 12px 8px; min-width:0 }
figure .scroll { overflow-x:auto } figure svg { min-width:860px }
.swipe { display:none; font-size:12px; color:var(--sub); padding:0 4px 6px } @media (max-width:900px) { .swipe { display:block } }
figcaption { font-size:13px; color:var(--sub); padding:6px 4px 2px; border-top:1px dashed var(--line); margin-top:6px }
.key { display:flex; flex-wrap:wrap; gap:6px 16px; font-size:12.5px; color:var(--sub); padding:2px 4px 0 }
.key span { display:inline-flex; align-items:center; gap:6px } .key i { display:inline-block; width:22px; height:0; border-top:3px solid var(--sub) }
.key .tgk { display:inline-block; font:600 10.5px var(--f-mono); color:var(--db); background:var(--db-soft); border:1px solid var(--db); border-radius:999px; padding:0 7px; line-height:1.5 }
.key .nk { display:inline-grid; place-items:center; width:19px; height:19px; border-radius:50%; background:var(--ink); color:var(--panel); font:700 11px var(--f-mono) }
.key .k-heat { border-color:var(--heat) } .key .k-vap { border-color:var(--vap); border-top-width:5px } .key .k-liq { border-color:var(--liq) } .key .k-brine { border-color:var(--brine) } .key .k-vac { border-color:var(--vac); border-top-style:dashed }
.cols { display:grid; grid-template-columns:minmax(0, 1.25fr) minmax(0, 1fr) minmax(0, 1fr); gap:14px; align-items:start }
@media (max-width:1040px) { .cols { grid-template-columns:1fr } }
.blk { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px 16px; min-width:0 }
.blk h3 { font-size:15px; margin:0 0 8px; display:flex; align-items:center; gap:8px }
.blk h3 small { font-weight:500; color:var(--sub); font-size:12.5px }
/* 공식 카드 */
.fcard { border-top:1px solid var(--line); padding:9px 0 8px; display:grid; gap:3px }
.fcard:first-of-type { border-top:0; padding-top:2px }
.fcard.on { background:var(--acc-soft); margin:0 -8px; padding-left:8px; padding-right:8px; border-radius:8px; border-top-color:transparent }
.fh { display:flex; flex-wrap:wrap; align-items:center; gap:6px 8px }
.fh .n { font:700 11.5px var(--f-mono); width:21px; height:21px; border-radius:50%; background:var(--ink); color:var(--panel); display:grid; place-items:center }
.fh b { font-size:14.5px } .fh .law { font-size:12.5px; font-weight:600; color:var(--acc) } .cls { font-size:11.5px; color:var(--sub); border:1px solid var(--line); border-radius:999px; padding:0 7px }
.eqn { font-family:var(--f-math); font-size:16px; letter-spacing:.01em } .eqn i { font-style:italic } .eqn sub, .eqn sup { font-size:.72em; line-height:0 }
.eqline { padding:1px 0 } .words { font-size:13.5px } .gets { font-size:13.5px } .gets b, .val b { font-weight:600; color:var(--sub); font-size:12px; margin-right:6px; font-family:var(--f-body) }
.val { font:500 12.5px var(--f-mono); color:var(--acc) } .why { font-size:12.5px; color:var(--sub) }
.bdg { display:inline-block; font-size:11.5px; font-weight:700; padding:0 8px; border-radius:999px; border:1px solid; white-space:nowrap }
.b-est { color:var(--est); background:var(--est-soft); border-color:var(--est) } .b-hard { color:var(--hard); background:var(--hard-soft); border-color:var(--hard) }
.b-db { color:var(--db); background:var(--db-soft); border-color:var(--db) } .b-dwg { color:var(--dwg); background:var(--dwg-soft); border-color:var(--dwg) }
.alist { list-style:none; margin:0; padding:0; display:grid; gap:9px } .alist li { display:grid; gap:2px; font-size:13.5px }
.alist .w { font-weight:600 } .alist .lt { display:inline-grid; place-items:center; width:19px; height:19px; border-radius:50%; border:1px solid var(--sub); font:600 11px var(--f-mono); margin-right:4px; vertical-align:1px } .alist .y, .alist .e { color:var(--sub); font-size:12.5px }
.dlist { list-style:none; margin:0; padding:0; display:grid; gap:10px } .dlist li { display:grid; gap:2px; font-size:13.5px }
.dlist .tg { font:600 12px var(--f-mono); color:var(--db) } .dlist .g { color:var(--sub); font-size:12.5px }
.tw { overflow-x:auto } table { border-collapse:collapse; width:100%; font-size:13.5px }
th, td { border-bottom:1px solid var(--line); padding:6px 8px; text-align:left; vertical-align:top } th { color:var(--sub); font-weight:600; font-size:12.5px; white-space:nowrap }
td.m, .m { font-family:var(--f-mono); font-variant-numeric:tabular-nums }
.grid2 { display:grid; grid-template-columns:minmax(0, 1fr) minmax(0, 1fr); gap:14px } @media (max-width:900px) { .grid2 { grid-template-columns:1fr } }
.ncards { display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:10px }
.ncard { text-align:left; background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:11px 13px; cursor:pointer; display:grid; gap:4px }
.ncard:hover { border-color:var(--ink) } .ncard .h { display:flex; align-items:center; gap:8px; font-weight:700 }
.ncard .h i { font:700 12px var(--f-mono); font-style:normal; width:22px; height:22px; border-radius:50%; background:var(--ink); color:var(--panel); display:grid; place-items:center }
.ncard .h span { font-size:12px; font-weight:600; color:var(--acc) } .ncard .fl { font-size:13px; color:var(--sub) } .ncard .cnt { font-size:12px; color:var(--sub) }
.chain { display:grid; grid-template-columns:repeat(auto-fill, minmax(250px, 1fr)); gap:6px 14px; counter-reset:c; margin:0; padding:0; list-style:none; font-size:13.5px }
.chain li { counter-increment:c; display:flex; gap:8px; align-items:baseline } .chain li::before { content:counter(c); font:600 11.5px var(--f-mono); color:var(--sub); min-width:18px }
.chain em { font-style:normal; color:var(--sub) } .chain u { text-decoration:none; font:600 11px var(--f-mono); color:var(--panel); background:var(--ink); border-radius:50%; width:17px; height:17px; display:inline-grid; place-items:center; margin-left:4px }
/* 이상 상황 */
.abwrap { display:grid; grid-template-columns:230px minmax(0, 1fr); gap:14px; align-items:start } @media (max-width:980px) { .abwrap { grid-template-columns:1fr } }
.ablist { display:grid; gap:5px } @media (max-width:980px) { .ablist { grid-template-columns:repeat(auto-fill, minmax(170px, 1fr)) } }
.ablist button { text-align:left; border:1px solid var(--line); background:var(--panel); border-radius:9px; padding:6px 10px; cursor:pointer; font-size:13.5px; display:flex; gap:8px; align-items:center }
.ablist button i { font:600 11px var(--f-mono); font-style:normal; color:var(--sub); min-width:16px } .ablist button[aria-pressed="true"] { border-color:var(--ng); background:var(--ng-soft); font-weight:600 }
.abx { display:grid; gap:12px; min-width:0 } .abhead { display:flex; flex-wrap:wrap; gap:6px 12px; align-items:baseline } .abhead h3 { margin:0; font-size:18px }
.abhead .cause { font:500 12.5px var(--f-mono); color:var(--ng); border:1px solid var(--ng); border-radius:999px; padding:0 9px }
.steps { display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:10px } @media (max-width:820px) { .steps { grid-template-columns:1fr } }
.step { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:12px 14px; display:grid; gap:4px } .step b { font-size:14.5px } .step span { font-size:13px; color:var(--sub) }
.step .no { font:700 12px var(--f-mono); color:var(--acc) }
ul.pl { margin:4px 0 0; padding-left:19px } ul.pl li { margin:3px 0; font-size:13.5px }
ol.pl { margin:4px 0 0; padding-left:24px } ol.pl li { margin:4px 0; font-size:13.5px; padding-left:2px } ol.pl li::marker { font:700 12.5px var(--f-mono); color:var(--ng) }
.small { font-size:12.5px; color:var(--sub) }
/* 그림 */
svg { width:100%; height:auto; display:block }
.eq { fill:none; stroke:var(--ink); stroke-width:1.7; stroke-linejoin:round } .eqfill { fill:var(--panel) }
.liqfill { fill:var(--liq-soft); stroke:none } .liqtop { fill:none; stroke:var(--liq); stroke-width:1.5 }
.jk { fill:none; stroke:var(--heat); stroke-width:2.2 } .ins { stroke:none; opacity:.7 } .insl { stroke:var(--sub); stroke-width:1 }
.shaft, .anchor { fill:none; stroke:var(--ink); stroke-width:2.8; stroke-linecap:round; stroke-linejoin:round }
.pk { fill:none; stroke:var(--sub); stroke-width:1 } .packfill { stroke:none } .thin { fill:none; stroke:var(--sub); stroke-width:1.1 }
.sheet { fill:none; stroke:var(--ink); stroke-width:2.6 } .tube { fill:none; stroke:var(--sub); stroke-width:1.2 }
.pp { fill:none; stroke-linejoin:round; stroke-linecap:round }
.pp-vap { stroke:var(--vap); stroke-width:5.5 } .pp-liq { stroke:var(--liq); stroke-width:2.6 } .pp-steam { stroke:var(--heat); stroke-width:2.6 }
.pp-brine { stroke:var(--brine); stroke-width:2 } .pp-vac { stroke:var(--vac); stroke-width:2.2; stroke-dasharray:7 4 } .pp-thin { stroke:var(--sub); stroke-width:1.2 } .pp-sig { stroke:var(--sub); stroke-width:1.2; stroke-dasharray:2 4 }
.fl { fill:none; stroke-width:1.5; stroke-dasharray:2 10; stroke-linecap:round; animation:fl 1.2s linear infinite }
.fl-vap { stroke:var(--panel); stroke-width:2 } .fl-liq, .fl-steam { stroke:var(--panel) }
@keyframes fl { to { stroke-dashoffset:-12 } } @media (prefers-reduced-motion: reduce) { .fl { animation:none } }
.ah { stroke:none } .ah-n { fill:var(--sub) } .ah-heat { fill:var(--heat) } .ah-vap { fill:var(--vap) } .ah-liq { fill:var(--liq) } .ah-brine { fill:var(--brine) } .ah-vac { fill:var(--vac) } .ah-db { fill:var(--db) }
.ld { fill:none; stroke-width:1.4 } .ld-n { stroke:var(--sub) } .ld-heat { stroke:var(--heat) } .ld-vap { stroke:var(--vap) } .ld-liq { stroke:var(--liq) } .ld-brine { stroke:var(--brine) } .ld-vac { stroke:var(--vac) } .ld-db { stroke:var(--db) }
.hx { fill:none; stroke:var(--heat); stroke-width:2 } .hx-loss { stroke-dasharray:4 3; opacity:.8 }
.vv { stroke-width:1.5; stroke-linejoin:round } .vv-open { fill:var(--ok-soft); stroke:var(--ok) } .vv-closed { fill:var(--ng-soft); stroke:var(--ng) }
.t { fill:var(--ink); font:700 13px var(--f-body) } .ts { fill:var(--sub); font:500 11.5px var(--f-body) } .tn { fill:var(--ink); font:500 12px var(--f-body) } .tm { fill:var(--acc); font:500 11.5px var(--f-mono) }
.tnum { fill:var(--ink); font:600 12px var(--f-mono) } .tk { fill:var(--sub); font:600 11px var(--f-mono) }
.nl { fill:var(--ink); font:500 12px var(--f-body) } .nlh { fill:var(--ink); font:700 13px var(--f-body) } .nlv { fill:var(--acc); font:600 12px var(--f-body) }
.co-b { fill:var(--panel); stroke:var(--line); stroke-width:1.3 } .co-b-heat { stroke:var(--heat) } .co-b-vap { stroke:var(--vap) } .co-b-liq { stroke:var(--liq) } .co-b-brine { stroke:var(--brine) } .co-b-vac { stroke:var(--vac) } .co-b-n { stroke:var(--sub) }
.co.on .co-b { stroke-width:2.6 } .co { cursor:default }
.co-nc { fill:var(--ink) } .co-nt { fill:var(--panel); font:700 11.5px var(--f-mono); text-anchor:middle }
.co-n { fill:var(--ink); font:700 13.5px var(--f-body) } .co-e { fill:var(--ink); font-family:var(--f-math); font-weight:500 }
.co-l { fill:var(--acc); font:600 11px var(--f-body) } .co-g { fill:var(--sub); font:500 12px var(--f-body) } .co-v { fill:var(--acc); font:500 11.5px var(--f-mono) }
.bd { stroke-width:1 } .bd-est { fill:var(--est-soft); stroke:var(--est) } .bd-hard { fill:var(--hard-soft); stroke:var(--hard) } .bd-db { fill:var(--db-soft); stroke:var(--db) } .bd-dwg { fill:var(--dwg-soft); stroke:var(--dwg) }
.bdt { font:700 10.5px var(--f-body) } .bdt-est { fill:var(--est) } .bdt-hard { fill:var(--hard) } .bdt-db { fill:var(--db) } .bdt-dwg { fill:var(--dwg) }
.pin circle { fill:var(--ink) } .pint { fill:var(--panel); font:700 12.5px var(--f-mono) } .pin.link { cursor:pointer } .pin.link:hover circle { fill:var(--acc) }
.tg { fill:var(--soft); stroke:var(--line); stroke-width:1 } .tgt { fill:var(--ink); font:600 10.5px var(--f-mono) }
.tgx { fill:var(--panel); stroke:var(--hard); stroke-width:1; stroke-dasharray:3 2 } .tgxt { fill:var(--hard); font:600 10.5px var(--f-mono) }
.tgd { fill:var(--db-soft); stroke:var(--db); stroke-width:1 } .tgdt { fill:var(--db); font:600 10.5px var(--f-mono) }
.ast { fill:var(--ink); font:500 11px var(--f-body) }
.mark { fill:none; stroke:var(--ng); stroke-width:2.4; stroke-dasharray:5 3 } .markt { fill:var(--ng); font:700 12px var(--f-body) }
.vb { fill:var(--panel); stroke:var(--line); stroke-width:1 } .vb.chg { stroke:var(--ng); stroke-width:1.8 } .vbl { fill:var(--sub); font:500 10.5px var(--f-body) } .vbv { fill:var(--ink); font:600 12px var(--f-mono) } .vbv.chg { fill:var(--ng) } .stepc { fill:var(--ng) } .stept { fill:var(--panel); font:700 10.5px var(--f-mono) }
.dim { opacity:.22 } .plot-ax { fill:none; stroke:var(--sub); stroke-width:1 } .plot-g { fill:none; stroke:var(--line); stroke-width:1 } .plot-c { fill:none; stroke:var(--ink); stroke-width:2 } .plot-c2 { fill:none; stroke:var(--hard); stroke-width:1.6; stroke-dasharray:5 3 }
.plot-p { fill:var(--panel); stroke:var(--ink); stroke-width:1.8 } .plot-p2 { fill:var(--acc); stroke:none } .plot-p3 { fill:none; stroke:var(--ng); stroke-width:1.6; stroke-dasharray:4 3 }
.bar-f { fill:var(--est-soft); stroke:var(--est) } .bar-m { fill:var(--liq-soft); stroke:var(--liq) } .bar-t { fill:var(--soft); stroke:var(--sub) } .bar-h { fill:var(--panel); stroke:var(--line) }
"""

# 발표 순서 · 요약 · 시연 화면의 스타일(만들기.py만 쓴다. 흐름학습.py가 같이 쓰는 CSS에는 넣지 않는다)
# --mk · --mk-ink: 시뮬레이터 화면 그림 위의 번호 색. 그림이 늘 어두우므로 밝은 · 어두운 화면에서 같은 색을 쓴다
CSS_GUIDE = r"""
:root { --mk:#ffd23f; --mk-ink:#17202b }
/* 공식 카드: 산출값 → 용도 → 식의 요지 → 계산값. 계산식은 접어 둔다 */
.fgrid { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:10px 14px; align-items:start } @media (max-width:900px) { .fgrid { grid-template-columns:1fr } }
.fgrid .fcard, .fgrid .fcard:first-of-type { border:1px solid var(--line); border-radius:10px; padding:10px 12px; gap:6px; min-width:0 }
.fgrid .fcard.on { margin:0; padding:10px 12px; border-color:var(--acc) }
.fcard > div:not(.fh) > b, .fcard summary { font-weight:600; color:var(--sub); font-size:12px; margin-right:6px; font-family:var(--f-body) }
.fcard .why { display:grid; gap:3px; font-size:13.5px; color:var(--ink); border-left:3px solid var(--acc); padding-left:9px }
.why .u { display:grid; grid-template-columns:44px minmax(0, 1fr); gap:6px } .why .u i { font-style:normal; font-size:11.5px; font-weight:700; color:var(--acc); padding-top:2px }
.why .ex, .why .ex i { color:var(--sub) }
.simp { font-size:13.5px } .simp .eqn { font-size:15.5px; margin-right:8px } .simp .eqn sup, .simp .eqn sub { white-space:nowrap } .simp .rd { display:block; color:var(--sub); font-size:12.5px }
.fcard .note { font-size:12.5px; color:var(--sub) }
details.eqs { font-size:13px } details.eqs summary { cursor:pointer; display:inline-block; list-style:none; border:1px solid var(--line); border-radius:999px; padding:0 9px; margin:0 } details.eqs summary::-webkit-details-marker { display:none }
details.eqs summary::before { content:"+ " } details.eqs[open] summary::before { content:"− " } details.eqs[open] summary { margin-bottom:4px } details.eqs summary:hover { border-color:var(--ink); color:var(--ink) }
/* 발표 순서 · 요약 · 시연 */
body::before { content:""; position:fixed; inset:0 0 auto; height:env(safe-area-inset-top, 0px); background:var(--bg); z-index:10 }
.tabs button.gdtab { border-color:var(--acc); color:var(--acc) } .tabs button.gdtab[aria-selected="true"] { background:var(--acc); color:var(--panel) }
.subs { display:flex; flex-wrap:wrap; gap:6px }
.subs button { border:1px solid var(--line); background:var(--panel); padding:4px 13px; border-radius:999px; cursor:pointer; font-size:13px; color:var(--sub) }
.subs button[aria-current="true"] { border-color:var(--ink); color:var(--ink); font-weight:600 }
.lnk { border:0; border-bottom:1px solid var(--acc); background:transparent; padding:0 1px; cursor:pointer; color:var(--acc); font-size:12.5px; font-weight:600; line-height:1.35 }
.lnk:hover { color:var(--ink); border-color:var(--ink) }
.btnc { display:inline-block; border:1px solid var(--line); background:var(--soft); border-radius:6px; padding:0 6px; font-size:.93em; font-weight:600; line-height:1.45; white-space:nowrap }
.b-t5 { color:var(--acc); background:var(--acc-soft); border-color:var(--acc) }
/* 진행 표시줄 */
.pbar { position:sticky; top:env(safe-area-inset-top, 0px); z-index:6; background:var(--panel); border:1.5px solid var(--acc); border-radius:12px; padding:8px 12px 10px; display:flex; flex-wrap:wrap; align-items:center; gap:6px 16px; overflow:hidden }
.pb-l { display:flex; align-items:center; gap:8px } .pb-tr { font-size:12.5px; font-weight:700; color:var(--panel); background:var(--acc); border-radius:999px; padding:1px 10px; white-space:nowrap }
.pb-n { font:600 13px var(--f-mono); color:var(--sub); white-space:nowrap }
.pb-m { flex:1 1 420px; min-width:0; display:grid; gap:1px } .pb-m b { font-size:15.5px } .pb-m span { font-size:13.5px; color:var(--ink) } .pb-m .pb-val { font:500 12.5px var(--f-mono); color:var(--acc) }
.pb-r { display:flex; flex-wrap:wrap; align-items:center; gap:6px 8px; margin-left:auto } .pb-tm { font:500 12px var(--f-mono); color:var(--sub); white-space:nowrap }
.pb-r button { border:1px solid var(--line); background:var(--panel); border-radius:8px; padding:3px 11px; cursor:pointer; font-size:13px; font-weight:600 }
.pb-r button:hover { border-color:var(--ink) } .pb-r button:disabled { opacity:.4; cursor:default; border-color:var(--line) }
.pb-r .pb-ck { font:600 13px var(--f-mono); color:var(--ok); border-color:var(--ok); background:var(--ok-soft) } .pb-r .pb-ck.late { color:var(--ng); border-color:var(--ng); background:var(--ng-soft) }
.pbar.demo { border-style:dashed } .pb-bar { position:absolute; left:0; right:0; bottom:0; height:3px; background:var(--soft); display:block } .pb-bar i { display:block; height:100%; background:var(--acc); width:0 }
/* 발표 순서 */
.tkey { display:flex; flex-wrap:wrap; gap:6px 16px; font-size:12.5px; color:var(--sub) } .tkey span { display:inline-flex; align-items:center; gap:6px } .tkey i { display:inline-block; width:22px; height:12px; border-radius:3px }
.tk-talk { background:var(--vap-soft); border:1px solid var(--vap) } .tk-demo { background:var(--acc-soft); border:1px solid var(--acc) } .tk-slack { background:transparent; border:1px dashed var(--sub) }
.tracks { display:grid; grid-template-columns:minmax(0, 1fr) minmax(0, 1.2fr); gap:14px; align-items:start } @media (max-width:1040px) { .tracks { grid-template-columns:1fr } }
.track { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px 16px; display:grid; gap:10px; min-width:0 }
.trh { display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 12px } .trh h3 { margin:0; font-size:18px } .trh .tot { font:600 13.5px var(--f-mono); color:var(--acc) } .trh .pt { font-size:12.5px; color:var(--sub) }
.start { margin-left:auto; border:1px solid var(--acc); background:var(--acc); color:var(--panel); border-radius:8px; padding:5px 14px; font-weight:700; cursor:pointer; font-size:13.5px } .start:hover { background:var(--ink); border-color:var(--ink) }
.flow { margin:0; font-size:13.5px; font-weight:600 } .flow span { font-size:11.5px; font-weight:700; color:var(--sub); border:1px solid var(--line); border-radius:999px; padding:0 8px; margin-right:8px }
ol.gl li::marker { color:var(--acc) }
.tbar { display:flex; gap:2px; height:24px } .tbar i { display:grid; place-items:center; min-width:13px; border-radius:4px; font:600 11px var(--f-mono); font-style:normal; color:var(--ink); overflow:hidden }
.tsteps { list-style:none; margin:0; padding:0 } .tsteps li { display:grid; grid-template-columns:24px 50px minmax(0, 1fr); gap:10px; padding:9px 0; border-top:1px solid var(--line); align-items:start }
.tsteps li:first-child { border-top:0; padding-top:2px } .tsteps .no { font:700 11.5px var(--f-mono); width:22px; height:22px; border-radius:50%; background:var(--ink); color:var(--panel); display:grid; place-items:center }
.tsteps li.is-demo .no { background:var(--acc) } .tsteps .tt { font:600 13.5px var(--f-mono); display:grid; line-height:1.3 } .tsteps .tt small { font-weight:500; font-size:11px; color:var(--sub) }
.tsteps .sb { display:grid; gap:3px; min-width:0 } .tsteps .hd { display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 10px } .tsteps .hd b { font-size:14.5px }
.tsteps .kd { font-size:11.5px; font-weight:700; color:var(--acc); border:1px solid var(--acc); border-radius:999px; padding:0 7px } .tsteps p { margin:0; font-size:13.5px } .tsteps .vl { font:500 12.5px var(--f-mono); color:var(--acc) }
.tsteps .vl span { font:600 11.5px var(--f-body); color:var(--sub); margin-right:6px }
/* 시연 순서 */
.dsteps { display:grid; gap:14px } .dstep { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px 16px; display:grid; gap:10px; min-width:0 } .dstep.off { opacity:.36 }
.dh { display:flex; flex-wrap:wrap; align-items:center; gap:6px 10px } .dh .num { font:700 14px var(--f-mono); width:28px; height:28px; border-radius:50%; background:var(--acc); color:var(--panel); display:grid; place-items:center }
.dh h3 { margin:0; font-size:17px } .dh .tt { font:600 12.5px var(--f-mono); color:var(--sub) } .dh .where { font-size:12.5px; color:var(--sub); border:1px solid var(--line); border-radius:999px; padding:0 9px }
.dcols { display:grid; grid-template-columns:minmax(0, 1fr) minmax(0, 1.25fr) minmax(0, 1.1fr); gap:6px 18px } @media (max-width:980px) { .dcols { grid-template-columns:1fr } }
.dcols h4 { margin:0 0 3px; font-size:13px; color:var(--sub) } .dcols h4 small { font-weight:500; font-size:11.5px } .dcols p { margin:0 0 4px; font-size:13.5px }
ol.ops { margin:0; padding-left:21px } ol.ops li { margin:3px 0; font-size:13.5px } ol.ops li::marker { font:700 12.5px var(--f-mono); color:var(--acc) }
.dstep figure { border-color:var(--line); padding:8px } svg.shot { border-radius:6px }
.capt { fill:var(--ink); font:700 13.5px var(--f-body) }
.mkr { fill:none; stroke:var(--mk); stroke-width:2 } .mkc { fill:var(--mk) } .mkt { fill:var(--mk-ink); font:700 12.5px var(--f-mono); text-anchor:middle }
/* 요약 */
.stats { display:grid; grid-template-columns:repeat(auto-fit, minmax(190px, 1fr)); gap:10px }
.stat { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:12px 14px; display:grid; gap:1px } .stat b { font:700 30px/1.15 var(--f-mono); letter-spacing:-.02em } .stat span { font-weight:700; font-size:14.5px } .stat small { font-size:12.5px; color:var(--sub) }
.lb { margin:8px 0 5px; font-size:13px; color:var(--sub) } .lb b { color:var(--ink); font:700 15px var(--f-mono); margin-left:4px } .blk .p { margin:0 0 8px; font-size:13.5px }
.sbar { display:flex; gap:2px; height:22px } .sbar i { display:block; min-width:3px; border-radius:3px }
.sleg { display:flex; flex-wrap:wrap; gap:3px 14px; font-size:12.5px; color:var(--sub); margin:5px 0 6px } .sleg span { display:inline-flex; align-items:center; gap:5px } .sleg i { display:inline-block; width:11px; height:11px; border-radius:3px } .sleg b { color:var(--ink); font:600 12.5px var(--f-mono) }
.sg-heat { background:var(--heat-soft); border:1px solid var(--heat) } .sg-vap { background:var(--vap-soft); border:1px solid var(--vap) } .sg-fore { background:var(--est-soft); border:1px solid var(--est) }
.sg-main { background:var(--liq-soft); border:1px solid var(--liq) } .sg-rest { background:var(--soft); border:1px solid var(--sub) } .sg-seal { background:var(--acc-soft); border:1px solid var(--acc) }
"""

JS = r"""
(function(){
  var scenes=[].slice.call(document.querySelectorAll('.scene')), tabs=[].slice.call(document.querySelectorAll('.tabs button')), nb=[].slice.call(document.querySelectorAll('.nodes button, .subs button'));
  var ids=scenes.map(function(s){return s.id}), cur=0;
  var TR=window.TRACKS||null, G=null, pbar=document.getElementById('pbar'), tick=null;   /* 발표 순서(G = 진행 중인 순서와 단계) */
  function show(id, push){
    var i=ids.indexOf(id); if(i<0) i=0; cur=i;
    scenes.forEach(function(s,k){ s.hidden = k!==i });
    var tab=scenes[i].getAttribute('data-tab');
    tabs.forEach(function(b){ b.setAttribute('aria-selected', b.getAttribute('data-tab')===tab ? 'true' : 'false') });
    var nodes=document.querySelector('.nodes'); if(nodes) nodes.hidden = tab!=='nd';
    [].forEach.call(document.querySelectorAll('.subs'), function(n){ n.hidden = n.getAttribute('data-for')!==tab });
    nb.forEach(function(b){ b.setAttribute('aria-current', b.getAttribute('data-go')===ids[i] ? 'true' : 'false') });
    var pg=document.getElementById('pg'); if(pg) pg.textContent = G ? (G.i+1)+' / '+TR[G.k].steps.length : (i+1)+' / '+ids.length;
    if(push!==false){ try{ if(location.hash!=='#'+ids[i]) history.replaceState(null,'','#'+ids[i]) }catch(e){ try{ location.hash=ids[i] }catch(e2){} } }
    try{ window.scrollTo(0,0) }catch(e){}
  }
  function go(d){ if(G){ gGo(G.i+d); return } show(ids[Math.max(0, Math.min(ids.length-1, cur+d))]) }
  /* 발표 순서: 고른 순서의 단계대로 장면을 넘기고, 위에 진행 표시줄(단계 · 요지 · 배정 시간 · 경과 시간)을 둔다 */
  function mmss(s){ s=Math.max(0, Math.round(s)); return Math.floor(s/60)+':'+('0'+(s%60)).slice(-2) }
  function gid(i){ return document.getElementById(i) }
  function gTotal(T){ var a=T.slack||0; T.steps.forEach(function(s){ a+=s.sec }); return a }
  function gCum(){ var T=TR[G.k], c=0; for(var k=0;k<=G.i;k++) c+=T.steps[k].sec; return c }
  function gClock(){ if(!G) return; var el=(Date.now()-G.t0)/1000, c=gid('pb-ck'); c.textContent='경과 '+mmss(el); c.classList.toggle('late', el>gCum()) }
  function gRender(){
    var T=TR[G.k], s=T.steps[G.i], cum=gCum(), tot=gTotal(T);
    gid('pb-tr').textContent=T.name; gid('pb-n').textContent=(G.i+1)+' / '+T.steps.length; gid('pb-t').textContent=s.t; gid('pb-msg').textContent=s.msg;
    var v=gid('pb-val'); v.textContent=s.val ? '대표 계산값 · '+s.val : ''; v.hidden=!s.val;
    gid('pb-tm').textContent='배정 '+mmss(s.sec)+' · 누적 '+mmss(cum)+' / '+mmss(tot);
    gid('pb-fill').style.width=(cum/tot*100).toFixed(1)+'%';
    gid('pb-prev').disabled = G.i===0; gid('pb-next').disabled = G.i===T.steps.length-1;
    pbar.classList.toggle('demo', s.kind==='demo'); pbar.hidden=false;
    var pg=gid('pg'); if(pg) pg.textContent=(G.i+1)+' / '+T.steps.length; gClock();
  }
  function demoMark(list){ [].forEach.call(document.querySelectorAll('.dstep'), function(e){ e.classList.toggle('off', !!list && list.indexOf(+e.getAttribute('data-demo'))<0) }) }
  function gGo(i){
    var T=TR[G.k]; G.i=Math.max(0, Math.min(T.steps.length-1, i)); var s=T.steps[G.i];
    show(s.go); if(s.ab) pickAb(s.ab); demoMark(s.demo||null); gRender();
    var e = s.at ? document.querySelector(s.at) : (s.demo ? document.querySelector('.dstep[data-demo="'+s.demo[0]+'"]') : null);
    if(e){ e=e.closest('figure')||e; try{ window.scrollTo(0, Math.max(0, e.getBoundingClientRect().top + (window.pageYOffset||0) - pbar.offsetHeight - 10)) }catch(x){} }   /* 표시줄 바로 아래에 맞춘다 */
  }
  function gStart(k){ if(!TR||!TR[k]||!pbar) return; G={k:k, i:0, t0:Date.now()}; if(tick) clearInterval(tick); tick=setInterval(gClock, 1000); gGo(0) }
  function gEnd(){ G=null; if(tick){ clearInterval(tick); tick=null } if(pbar) pbar.hidden=true; demoMark(null); show('gd') }
  if(pbar){
    gid('pb-prev').addEventListener('click', function(){ if(G) gGo(G.i-1) }); gid('pb-next').addEventListener('click', function(){ if(G) gGo(G.i+1) });
    gid('pb-end').addEventListener('click', gEnd); gid('pb-ck').addEventListener('click', function(){ if(G){ G.t0=Date.now(); gClock() } });
  }
  document.addEventListener('click', function(ev){
    var st=ev.target.closest('[data-start]'); if(st){ gStart(st.getAttribute('data-start')); return }
    var t=ev.target.closest('[data-go]'); if(t){ show(t.getAttribute('data-go')); return }
    var tb=ev.target.closest('.tabs button'); if(tb){ var want=tb.getAttribute('data-tab'); var s=scenes.filter(function(x){return x.getAttribute('data-tab')===want})[0]; if(s) show(s.id); return }
  });
  var p=document.getElementById('prev'), n=document.getElementById('next'); if(p) p.addEventListener('click', function(){go(-1)}); if(n) n.addEventListener('click', function(){go(1)});
  document.addEventListener('keydown', function(ev){
    if(ev.target && /INPUT|TEXTAREA|SELECT/.test(ev.target.tagName)) return;
    if(ev.key==='ArrowRight'||ev.key==='PageDown'){ go(1); ev.preventDefault() } else if(ev.key==='ArrowLeft'||ev.key==='PageUp'){ go(-1); ev.preventDefault() }
  });
  window.addEventListener('hashchange', function(){ show((location.hash||'').slice(1), false) });
  /* 그림의 말풍선과 아래 카드를 잇는다 */
  function link(on, sc, f){ [].forEach.call(sc.querySelectorAll('[data-f="'+f+'"]'), function(e){ e.classList.toggle('on', on) }) }
  scenes.forEach(function(sc){
    [].forEach.call(sc.querySelectorAll('[data-f]'), function(e){
      e.addEventListener('mouseenter', function(){ link(true, sc, e.getAttribute('data-f')) });
      e.addEventListener('mouseleave', function(){ link(false, sc, e.getAttribute('data-f')) });
    });
  });
  /* 이상 상황 고르기 */
  var AB=window.AB_DATA||null, abBtns=[].slice.call(document.querySelectorAll('.ablist button'));
  function pickAb(k){
    if(!AB||!AB.cases[k]) return; var c=AB.cases[k];
    abBtns.forEach(function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-ab')===k ? 'true' : 'false') });
    var svg=document.getElementById('fig-ab'); if(!svg) return;
    Object.keys(c.vals).forEach(function(id){
      var g=svg.querySelector('[data-vb="'+id+'"]'); if(!g) return; var v=c.vals[id];
      var tv=g.querySelector('.vbv'); if(tv){ tv.textContent=v.t; tv.classList.toggle('chg', !!v.chg) } var r=g.querySelector('.vb'); if(r) r.classList.toggle('chg', !!v.chg);
    });
    [].forEach.call(svg.querySelectorAll('[data-step]'), function(e){ var n=(c.steps||{})[e.getAttribute('data-step')];
      if(n){ e.removeAttribute('hidden'); e.querySelector('text').textContent=n } else { e.setAttribute('hidden','') } });
    [].forEach.call(svg.querySelectorAll('[data-flow]'), function(e){ var on=c.flows[e.getAttribute('data-flow')]; e.classList.toggle('dim', on===false) });
    [].forEach.call(svg.querySelectorAll('[data-mark]'), function(e){ var on=e.getAttribute('data-mark')===c.mark;
      if(on){ e.removeAttribute('hidden'); var t=e.querySelector('text'); if(t&&c.marklab) t.textContent=c.marklab } else { e.setAttribute('hidden','') } });
    [].forEach.call(svg.querySelectorAll('[data-v]'), function(e){ var st=c.valves[e.getAttribute('data-v')]; if(st){ e.setAttribute('class','vv vv-'+st) } });
    var set=function(id, html){ var e=document.getElementById(id); if(e) e.innerHTML=html };
    set('ab-name', c.name); set('ab-cause', c.cause); set('ab-what', c.what); set('ab-why', c.why); set('ab-crit', c.crit); set('ab-undo', c.undo);
  }
  abBtns.forEach(function(b){ b.addEventListener('click', function(){ pickAb(b.getAttribute('data-ab')) }) });
  if(AB) pickAb(AB.first);
  show((location.hash||'').slice(1) || ids[0], false);
})();
"""
