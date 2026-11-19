# -*- coding: utf-8 -*-
"""발표자료 그림 도구 — 설비 2D 그림(SVG 조각)과 공식 말풍선.

- 좌표는 그림마다의 viewBox 단위다(px처럼 쓴다, y는 아래로 커진다).
- 색은 전부 CSS 클래스로 준다(밝은·어두운 화면에서 같이 읽히게). 클래스는 만들기.py의 스타일에 있다.
- 식은 작은 표기로 쓴다: 아래 첨자 _{...}, 위 첨자 ^{...}. 나머지는 그대로(· − × ÷ √ Σ ≤ λ ρ ε Δ).
"""
import html, math, re

esc = html.escape
NOITAL = {"log", "ln", "exp", "min", "max", "atanh", "e", "kg"}

# ---------- 글 너비 어림(글상자 크기·줄바꿈에 쓴다) ----------
def tw(s, size=13.0):
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o >= 0x2E80: w += 0.96            # 한글
        elif ch == " ": w += 0.28
        elif ch in ".,·:;'|!()[]{}ilj": w += 0.33
        elif ch in "mwMW%": w += 0.88
        elif ch in "−–-+=×÷≤≥≈<>→": w += 0.62
        elif ch.isupper(): w += 0.68
        elif ch.isdigit(): w += 0.58
        else: w += 0.55
    return w * size

def twm(s, size=11.5):
    """고정폭 글꼴(값 줄)의 너비 어림: 영문·숫자 0.6, 한글 1.0."""
    return sum(1.0 if ord(ch) >= 0x2E80 else 0.6 for ch in s) * size

def wrap(s, width, size=12.0, mono=False):
    """낱말 단위 줄바꿈(너비 어림 기준). ' · '에서 먼저 끊는다."""
    f = twm if mono else tw; out, cur = [], ""
    for word in s.split(" "):
        t = (cur + " " + word).strip()
        if cur and f(t, size) > width: out.append(cur); cur = word
        else: cur = t
    if cur: out.append(cur)
    return [x[2:] if x.startswith("· ") and i else x for i, x in enumerate(out)]

# ---------- 식 표기 ----------
_TOK = re.compile(r"_\{([^{}]*)\}|\^\{([^{}]*)\}")
_LET = re.compile(r"[A-Za-zα-ωΑ-Ωλρεμγτη]+")

def eq_chunks(eq):
    """'Q = U·A·(T_{자켓} − T_{액})' → [(글, 층)]  층 0 본문 · -1 아래 첨자 · +1 위 첨자"""
    out, i = [], 0
    for m in _TOK.finditer(eq):
        if m.start() > i: out.append((eq[i:m.start()], 0))
        out.append((m.group(1), -1) if m.group(1) is not None else (m.group(2), 1))
        i = m.end()
    if i < len(eq): out.append((eq[i:], 0))
    return out

def _pieces(text):
    """글을 (조각, 기울임) 목록으로: 라틴·그리스 글자 묶음은 기울임(함수 이름 빼고)."""
    out, i = [], 0
    for m in _LET.finditer(text):
        if m.start() > i: out.append((text[i:m.start()], False))
        out.append((m.group(0), m.group(0) not in NOITAL))
        i = m.end()
    if i < len(text): out.append((text[i:], False))
    return out

def eq_width(eq, size=14.0):
    return sum(tw(t, size * (1 if lv == 0 else 0.72)) for t, lv in eq_chunks(eq))

def eq_html(eq):
    out = []
    for t, lv in eq_chunks(eq):
        inner = "".join(f"<i>{esc(p)}</i>" if it else esc(p) for p, it in _pieces(t))
        out.append(inner if lv == 0 else f"<sub>{inner}</sub>" if lv < 0 else f"<sup>{inner}</sup>")
    return '<span class="eqn">' + "".join(out) + "</span>"

def eq_svg(eq, x, y, size=14.0, cls="co-e", anchor="start"):
    cur, parts = 0.0, []
    for t, lv in eq_chunks(eq):
        target = 0.0 if lv == 0 else (0.30 * size if lv < 0 else -0.40 * size)
        fs = size if lv == 0 else round(size * 0.72, 1)
        first = True
        for p, it in _pieces(t):
            a = f' dy="{target - cur:.1f}"' if first and abs(target - cur) > 1e-6 else ""
            if first: cur = target
            first = False
            st = ' font-style="italic"' if it else ""
            parts.append(f'<tspan font-size="{fs}"{a}{st}>{esc(p)}</tspan>')
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">' + "".join(parts) + "</text>"

# ---------- 기본 도형 ----------
def P(pts):
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts)

def pipe(pts, kind="liq", w=None, extra=""):
    """관: kind = vap(증기) · liq(액) · steam(스팀) · brine(냉매) · vac(진공) · thin"""
    sw = f' stroke-width="{w}"' if w else ""
    return f'<path class="pp pp-{kind}" d="{P(pts)}"{sw}{extra}/>'

def flow(pts, kind="liq"):
    """관 위에 겹치는 흐름 표시(점선이 흐른다). 계산에서 그 관에 흐름이 있을 때만 그린다."""
    return f'<path class="fl fl-{kind}" d="{P(pts)}"/>'

def text(x, y, s, cls="t", anchor="middle", extra=""):
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}"{extra}>{esc(s)}</text>'

def arrowhead(x, y, ang, kind="n", s=7.0):
    """관 위 방향 표시(작은 세모). ang = 도(0 오른쪽, 90 아래)."""
    a = math.radians(ang); c, sn = math.cos(a), math.sin(a)
    pts = [(x + s * c, y + s * sn), (x - s * 0.7 * c + s * 0.62 * sn, y - s * 0.7 * sn - s * 0.62 * c), (x - s * 0.7 * c - s * 0.62 * sn, y - s * 0.7 * sn + s * 0.62 * c)]
    return f'<path class="ah ah-{kind}" d="{P(pts)}Z"/>'

def defs(fid):
    """그림마다 쓰는 화살촉·무늬(id는 그림 안에서만 쓴다)."""
    mk = "".join(f'<marker id="{fid}-a-{k}" viewBox="0 0 10 10" refX="8.5" refY="5" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" orient="auto-start-reverse"><path class="ah ah-{k}" d="M0 0L10 5L0 10z"/></marker>' for k in ("n", "heat", "vap", "liq", "brine", "vac", "db"))
    pat = (f'<pattern id="{fid}-pack" width="12" height="12" patternUnits="userSpaceOnUse"><circle class="pk" cx="3" cy="3" r="2.4"/><circle class="pk" cx="9" cy="9" r="2.4"/></pattern>'
           f'<pattern id="{fid}-ins" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line class="insl" x1="0" y1="0" x2="0" y2="7"/></pattern>')
    return "<defs>" + mk + pat + "</defs>"

def leader(fid, pts, kind="n", dash=False, of=""):
    """말풍선에서 설비로 가는 화살표. of = 이 화살표가 딸린 말풍선의 열쇠(겹침 검사에 쓴다)."""
    d = ' stroke-dasharray="5 4"' if dash else ""; a = f' data-of="{esc(of)}"' if of else ""
    return f'<path class="ld ld-{kind}" d="{P(pts)}" marker-end="url(#{fid}-a-{kind})"{d}{a}/>'

# ---------- 설비 ----------
def vessel_d(cx, y0, w, h, hd=None):
    """2:1 타원 경판 용기 외곽선. y0 = 위 경판 꼭대기, h = 몸통(직선부) 높이."""
    r = w / 2; hd = w / 4 if hd is None else hd; yt = y0 + hd; yb = yt + h
    return f"M{cx - r:.1f} {yt:.1f}A{r:.1f} {hd:.1f} 0 0 1 {cx + r:.1f} {yt:.1f}V{yb:.1f}A{r:.1f} {hd:.1f} 0 0 1 {cx - r:.1f} {yb:.1f}Z"

def vessel(cx, y0, w, h, hd=None, level=None, cls="eq"):
    """용기 + 액(level = 액면의 y, None이면 빈 용기)."""
    r = w / 2; hd = w / 4 if hd is None else hd; yt = y0 + hd; yb = yt + h; out = []
    if level is not None:
        yl = max(yt, min(yb + hd - 1, level))
        if yl <= yb: out.append(f'<path class="liqfill" d="M{cx - r:.1f} {yl:.1f}V{yb:.1f}A{r:.1f} {hd:.1f} 0 0 0 {cx + r:.1f} {yb:.1f}V{yl:.1f}Z"/>')
        else:
            q = (yl - yb) / hd; hw = r * math.sqrt(max(0.0, 1 - q * q))
            out.append(f'<path class="liqfill" d="M{cx - hw:.1f} {yl:.1f}A{r:.1f} {hd:.1f} 0 0 0 {cx + hw:.1f} {yl:.1f}Z"/>')
        out.append(f'<path class="liqtop" d="M{cx - r + 1:.1f} {yl:.1f}H{cx + r - 1:.1f}"/>' if yl <= yb else "")
    out.append(f'<path class="{cls}" d="{vessel_d(cx, y0, w, h, hd)}"/>')
    return "".join(out)

def jacket(cx, y0, w, h, hd=None, top=None, gap=9.0, cls="jk"):
    """자켓: 몸통 아래쪽과 아래 경판을 감싼 겉벽. top = 자켓 윗끝의 y."""
    r = w / 2; hd = w / 4 if hd is None else hd; yt = y0 + hd; yb = yt + h; yj = yt + h * 0.35 if top is None else top; g = gap
    return (f'<path class="{cls}" d="M{cx - r:.1f} {yj:.1f}H{cx - r - g:.1f}V{yb:.1f}A{r + g:.1f} {hd + g:.1f} 0 0 0 {cx + r + g:.1f} {yb:.1f}V{yj:.1f}H{cx + r:.1f}"/>')

def insulation(cx, y0, w, h, hd=None, top=None, gap=9.0, t=11.0, fid="f"):
    """보온재: 자켓 바깥의 빗금 띠."""
    r = w / 2; hd = w / 4 if hd is None else hd; yt = y0 + hd; yb = yt + h; yj = yt + h * 0.35 if top is None else top; a = gap + 2; b = gap + 2 + t
    d = (f"M{cx - r - a:.1f} {yj:.1f}V{yb:.1f}A{r + a:.1f} {hd + a:.1f} 0 0 0 {cx + r + a:.1f} {yb:.1f}V{yj:.1f}H{cx + r + b:.1f}V{yb:.1f}"
         f"A{r + b:.1f} {hd + b:.1f} 0 0 1 {cx - r - b:.1f} {yb:.1f}V{yj:.1f}Z")
    return f'<path class="ins" d="{d}" fill="url(#{fid}-ins)"/>'

def agitator(cx, y0, w, h, hd=None, aw=None, clear=None, motor=True):
    """2-세미 앵커 교반기: 축 + 바닥 가로 막대 + 수직 날개 둘."""
    r = w / 2; hd = w / 4 if hd is None else hd; yt = y0 + hd; yb = yt + h
    aw = w * 0.56 if aw is None else aw; ybar = yb + hd - (hd * 0.42 if clear is None else clear); ytopb = ybar - h * 0.30; out = []
    if motor: out.append(f'<rect class="eq eqfill" x="{cx - 13:.1f}" y="{y0 - 34:.1f}" width="26" height="30" rx="3"/>')
    out.append(f'<path class="shaft" d="M{cx:.1f} {y0 - 4:.1f}V{ybar:.1f}"/>')
    out.append(f'<path class="anchor" d="M{cx - aw / 2:.1f} {ytopb:.1f}V{ybar:.1f}H{cx + aw / 2:.1f}V{ytopb:.1f}"/>')
    return "".join(out)

def column(cx, y0, w, h, pack=(0.55, 0.9), fid="f", mesh=True):
    """충전 컬럼: pack = 충전층이 차지하는 구간(위에서부터의 비율)."""
    x = cx - w / 2; yp0 = y0 + h * pack[0]; yp1 = y0 + h * pack[1]; out = [f'<rect class="eq eqfill" x="{x:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="5"/>']
    out.append(f'<rect class="packfill" x="{x + 2:.1f}" y="{yp0:.1f}" width="{w - 4:.1f}" height="{yp1 - yp0:.1f}" fill="url(#{fid}-pack)"/>')
    out.append(f'<path class="thin" d="M{x + 2:.1f} {yp0:.1f}H{x + w - 2:.1f}M{x + 2:.1f} {yp1:.1f}H{x + w - 2:.1f}"/>')
    if mesh: out.append(f'<path class="thin" stroke-dasharray="3 3" d="M{x + 2:.1f} {y0 + h * 0.16:.1f}H{x + w - 2:.1f}"/>')
    return "".join(out)

def cond_v(cx, y0, w, h, tubes=5):
    """세로 응축기(BEM): 곧은 관 다발 + 위·아래 관판."""
    x = cx - w / 2; ch = h * 0.13; out = [f'<rect class="eq eqfill" x="{x:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{w * 0.28:.1f}"/>']
    out.append(f'<path class="sheet" d="M{x:.1f} {y0 + ch:.1f}H{x + w:.1f}M{x:.1f} {y0 + h - ch:.1f}H{x + w:.1f}"/>')
    for i in range(tubes):
        tx = x + w * (i + 1) / (tubes + 1); out.append(f'<path class="tube" d="M{tx:.1f} {y0 + ch:.1f}V{y0 + h - ch:.1f}"/>')
    return "".join(out)

def cond_h(x, cy, w, h):
    """가로 응축기(BEU): U자 관."""
    r = h / 2; y = cy - r
    return (f'<rect class="eq eqfill" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:.1f}"/>'
            f'<path class="tube" d="M{x + w * 0.12:.1f} {cy - h * 0.2:.1f}H{x + w * 0.8:.1f}A{h * 0.2:.1f} {h * 0.2:.1f} 0 0 1 {x + w * 0.8:.1f} {cy + h * 0.2:.1f}H{x + w * 0.12:.1f}"/>')

def pump(cx, cy, r=20.0):
    return (f'<circle class="eq eqfill" cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"/>'
            f'<path class="thin" d="M{cx - r * 0.45:.1f} {cy - r * 0.5:.1f}L{cx + r * 0.55:.1f} {cy:.1f}L{cx - r * 0.45:.1f} {cy + r * 0.5:.1f}"/>')

def valve(x, y, horiz=True, state="open", s=8.0, vid=""):
    """밸브(나비넥타이). state = open(초록) · closed(빨강) · ctl(조절, 초록 테두리)."""
    rot = "" if horiz else " rotate(90)"; a = f' data-v="{vid}"' if vid else ""
    return f'<path class="vv vv-{state}"{a} transform="translate({x:.1f} {y:.1f}){rot}" d="M{-s} {-s * 0.72:.1f}L{s} {s * 0.72:.1f}V{-s * 0.72:.1f}L{-s} {s * 0.72:.1f}Z"/>'

def tagbub(x, y, s, anchor="middle", cls="tg"):
    """계기 이름표(PIMS 태그)."""
    w = tw(s, 10.5) + 12; x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
    return f'<g><rect class="{cls}" x="{x0:.1f}" y="{y - 9:.1f}" width="{w:.1f}" height="17" rx="8.5"/>' + text(x0 + w / 2, y + 3.6, s, cls + "t") + "</g>"

def tagdb(x, y, s, anchor="start"):
    """DB로 받는 계기 이름표(초록)."""
    return tagbub(x, y, s, anchor, "tgd")

def amark(x, y, kind, letter, short="", anchor="start", dy=19.0):
    """그림 위 가정·추정 표식: 배지(가정 a) + 짧은 글(아래 줄). 글자는 그림 아래 목록과 같다."""
    lab = {"est": "가정", "hard": "추정"}[kind] + " " + letter; w = tw(lab, 10.5) + 12
    x0 = x if anchor == "start" else (x - w if anchor == "end" else x - w / 2)
    out = f'<g class="am" data-a="{letter}"><rect class="bd bd-{kind}" x="{x0:.1f}" y="{y - 8.5:.1f}" width="{w:.1f}" height="16" rx="8"/>' + text(x0 + w / 2, y + 3.4, lab, f"bdt bdt-{kind}")
    if short: out += text(x, y + dy, short, "ast", anchor)
    return out + "</g>"

def panel(key, x, y, w, h, inner):
    """그림 속 글상자(표·작은 그래프). 겹침 검사에서 한 덩어리로 본다."""
    return f'<g data-panel="{esc(key)}" data-grp="{esc(key)}"><rect class="co-b" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="9"/>' + inner + "</g>"

def pin(x, y, n, cls="pin", r=11.0, extra=""):
    """번호 표식."""
    return f'<g class="{cls}"{extra}><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>' + text(x, y + 4.4, str(n), "pint") + "</g>"

def badge(x, y, kind, anchor="start"):
    """구분 배지: 가정 · 추정 · DB · 도면."""
    lab = {"est": "가정", "hard": "추정", "db": "DB", "dwg": "도면"}[kind]; w = tw(lab, 10.5) + 12
    x0 = x if anchor == "start" else (x - w if anchor == "end" else x - w / 2)
    return f'<g><rect class="bd bd-{kind}" x="{x0:.1f}" y="{y - 8.5:.1f}" width="{w:.1f}" height="16" rx="8"/>' + text(x0 + w / 2, y + 3.4, lab, f"bdt bdt-{kind}") + "</g>", w

def note(x, y, lines, cls="nt", anchor="start", lh=15.0):
    """그림 속 짧은 설명 글(여러 줄)."""
    return "".join(text(x, y + i * lh, s, cls, anchor) for i, s in enumerate(lines))

# ---------- 공식 말풍선 ----------
def callout(fid, x, y, w, n, name, eqs, gets, val="", badges=(), tgt=None, side="R", kind="n", via=None, key="", at=0.5, law=""):
    """공식 말풍선: 번호 · 이름 · 식(한 줄 또는 여러 줄) · 구하는 것 · 지금 값.
    tgt = 화살표가 닿는 점, side = 화살표가 나가는 변(L · R · T · B), via = 꺾이는 점 목록. 돌려주는 값: (svg, 높이)"""
    eqs = [eqs] if isinstance(eqs, str) else list(eqs)
    pad = 11.0; inner = w - 2 * pad
    size = 14.0
    for e in eqs:
        while eq_width(e, size) > inner and size > 11.0: size -= 0.5
    g_lines = wrap("→ " + gets, inner, 12.0) if gets else []
    v_lines = wrap(val, inner, 11.5, mono=True) if val else []
    lw = 15.0 if law else 0.0      # 통용 명칭 줄
    h = pad + 17 + lw + len(eqs) * (size + 7) + (len(g_lines) * 15.5 + 3 if g_lines else 0) + (len(v_lines) * 15 + 4 if v_lines else 0) + pad - 4
    out = [f'<g class="co" data-f="{esc(key or str(n))}">', f'<rect class="co-b co-b-{kind}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="9"/>']
    out.append(f'<circle class="co-nc co-nc-{kind}" cx="{x + pad + 8:.1f}" cy="{y + pad + 7:.1f}" r="9.5"/>' + text(x + pad + 8, y + pad + 11, str(n), "co-nt"))
    out.append(text(x + pad + 23, y + pad + 12, name, "co-n", "start"))
    bx = x + w - pad
    for b in reversed(list(badges)):
        s, bw = badge(bx, y + pad + 8, b, "end"); out.append(s); bx -= bw + 4
    if law: out.append(text(x + pad + 23, y + pad + 27, law, "co-l", "start"))
    yy = y + pad + 17 + lw
    for e in eqs:
        yy += size + 4; out.append(eq_svg(e, x + pad, yy, size)); yy += 3
    if g_lines:
        yy += 3
        for s in g_lines: yy += 15.5; out.append(text(x + pad, yy - 3, s, "co-g", "start"))
    if v_lines:
        yy += 4
        for s in v_lines: yy += 15; out.append(text(x + pad, yy - 3, s, "co-v", "start"))
    out.append("</g>")
    if tgt is not None:
        sx, sy = {"R": (x + w, y + h * at), "L": (x, y + h * at), "T": (x + w * at, y), "B": (x + w * at, y + h)}[side]
        out.append(leader(fid, [(sx, sy)] + list(via or []) + [tgt], kind, of=key or str(n)))
    return "".join(out), h

def svg_open(fid, W, H, label, y0=0):
    """y0 = 위에서 잘라 낼 높이(전체 설비 그림은 위쪽이 비어 있다)."""
    return f'<svg id="{fid}" viewBox="0 {y0} {W} {H - y0}" role="img" aria-label="{esc(label)}">' + defs(fid)
