import cairo, math, json, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))

W, H, FPS = 1280, 720, 24
S = W / 1920  # design at 1920 scale
FONT = "Noto Sans CJK KR"

def hx(h, a=1.0):
    h = h.lstrip("#"); return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)
BG1, BG2 = hx("#081226"), hx("#122a52")
FG, MUT, DIM = hx("#f2f6fc"), hx("#93a6c6"), hx("#2a3c60")
CYAN, BLUE, ORNG, YEL, VIO = hx("#3fe0d8"), hx("#4fb3ff"), hx("#ff8a4c"), hx("#ffd166"), hx("#8a6bff")

def clamp(x, a=0, b=1): return max(a, min(b, x))
def oq(x): x = clamp(x); return 1-(1-x)**5
def iob(x): x = clamp(x); return 4*x**3 if x < .5 else 1-(-2*x+2)**3/2
def ob(x, s=1.5):
    x = clamp(x); x -= 1; return x*x*((s+1)*x+s)+1
def rng(t, a, b): return (t-a)/(b-a)
def lerp(a, b, p): return a+(b-a)*p
def mix(c1, c2, p): return tuple(lerp(a, b, p) for a, b in zip(c1, c2))
def setc(c, col, a=1.0): c.set_source_rgba(col[0], col[1], col[2], col[3]*a)

def text(c, s, x, y, size, col, a=1.0, bold=True, anchor="l", spacing=0):
    if a <= 0.001: return
    c.select_font_face(FONT, 0, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    w = c.text_extents(s).x_advance + spacing*max(0, len(s)-1)
    if anchor == "c": x -= w/2
    elif anchor == "r": x -= w
    setc(c, col, a)
    if not spacing:
        c.move_to(x, y); c.show_text(s); c.new_path()
    else:
        for ch in s:
            c.move_to(x, y); c.show_text(ch); c.new_path(); x += c.text_extents(ch).x_advance+spacing

def tw(c, s, size, bold=True):
    c.select_font_face(FONT, 0, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size); return c.text_extents(s).x_advance

def rrect(c, x, y, w, h, r):
    r = min(r, w/2, h/2); c.new_sub_path()
    c.arc(x+w-r, y+r, r, -math.pi/2, 0); c.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    c.arc(x+r, y+h-r, r, math.pi/2, math.pi); c.arc(x+r, y+r, r, math.pi, 1.5*math.pi); c.close_path()

def card(c, x, y, w, h, a=1.0, r=24, border=None):
    rrect(c, x, y, w, h, r); setc(c, hx("#16284a"), 0.95*a); c.fill_preserve()
    if border: setc(c, border, 0.8*a); c.set_line_width(2.5)
    else: c.set_source_rgba(1, 1, 1, 0.08*a); c.set_line_width(1.5)
    c.stroke()

def pill(c, s, x, y, size, fg, bg, a=1.0, anchor="l", pad=16):
    w = tw(c, s, size)+pad*2; h = size*1.75
    if anchor == "c": x -= w/2
    elif anchor == "r": x -= w
    rrect(c, x, y-h/2, w, h, h/2); setc(c, bg, a); c.fill()
    text(c, s, x+pad, y+size*0.36, size, fg, a)

def cloud(c, cx, cy, s, col, a=1.0):
    setc(c, col, a)
    for (dx, dy, r) in [(-0.45, 0.1, 0.32), (-0.1, -0.15, 0.42), (0.35, 0.02, 0.36)]:
        c.new_path(); c.arc(cx+dx*s, cy+dy*s, r*s, 0, 6.283); c.fill()
    rrect(c, cx-0.78*s, cy+0.02*s, 1.5*s, 0.4*s, 0.2*s); c.fill()

def sun(c, cx, cy, s, a=1.0):
    setc(c, YEL, a); c.set_line_width(s*0.1); c.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(8):
        ang = i*math.pi/4
        c.move_to(cx+math.cos(ang)*s*0.62, cy+math.sin(ang)*s*0.62)
        c.line_to(cx+math.cos(ang)*s*0.85, cy+math.sin(ang)*s*0.85); c.stroke()
    c.new_path(); c.arc(cx, cy, s*0.45, 0, 6.283); c.fill()

def drops(c, cx, cy, s, a=1.0, n=3):
    c.set_line_width(s*0.08); c.set_line_cap(cairo.LINE_CAP_ROUND); setc(c, CYAN, a)
    for i in range(n):
        x = cx+(i-(n-1)/2)*s*0.42; y = cy+s*0.5
        c.move_to(x, y); c.line_to(x-s*0.07, y+s*0.22); c.stroke()

def icon(c, kind, cx, cy, s, a=1.0):
    if kind == "sun": sun(c, cx, cy, s*0.8, a)
    elif kind == "cloudsun":
        sun(c, cx+s*0.35, cy-s*0.3, s*0.55, a); cloud(c, cx-s*0.1, cy+s*0.1, s*0.75, hx("#dfe7f5"), a)
    elif kind == "cloud":
        cloud(c, cx+s*0.25, cy-s*0.22, s*0.55, hx("#8193b3"), a); cloud(c, cx-s*0.05, cy+s*0.08, s*0.8, hx("#c9d4e8"), a)
    elif kind == "rain":
        cloud(c, cx, cy-s*0.12, s*0.82, hx("#a9b8d3"), a); drops(c, cx, cy+s*0.02, s, a)

BGPAT = None
def background(c):
    global BGPAT
    if BGPAT is None:
        BGPAT = cairo.LinearGradient(0, 0, 600, 1080)
        BGPAT.add_color_stop_rgba(0, *BG1); BGPAT.add_color_stop_rgba(1, *BG2)
    c.set_source(BGPAT); c.paint()

def header(c, t, kicker, title, sub):
    p = oq(rng(t, 0.05, 0.7)); off = (1-p)*30
    rrect(c, 96, 90+off*0.5, 8, 142, 4); setc(c, CYAN, p); c.fill()
    text(c, kicker, 128, 112+off*0.5, 20, CYAN, p, spacing=3)
    text(c, title, 126, 176+off, 54, FG, p)
    text(c, sub, 128, 222+off, 25, MUT, oq(rng(t, 0.3, 0.9)), bold=False)

# ---------- data (2026-09-28, 기상청 예보 보도 종합) ----------
D = json.load(open(os.environ.get("WX_DATA", os.path.join(HERE, "data.json"))))
geo = json.load(open(os.path.join(HERE, "provinces.json")))
PROV = {}
MX0, MY0, K = 250, 262, 134
def proj(lon, lat): return MX0+(lon-124.55)*K*math.cos(math.radians(36)), MY0+(38.65-lat)*K
for f in geo["features"]:
    g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    PROV[f["properties"]["name"]] = [[proj(*pt) for pt in poly[0]] for poly in polys]
LVL = {0: hx("#1c2e50"), 1: hx("#2a5f86"), 2: hx("#33b3c4"), 3: hx("#3fe0d8")}

def s_intro(c, t):
    p = oq(rng(t, 0.1, 0.7))
    pill(c, D["datepill"], 960, 360-(1-p)*20, 26, BG1, YEL, p, anchor="c", pad=24)
    title = "오늘의 전국 날씨"; x = 960-tw(c, title, 124)/2
    for i, ch in enumerate(title):
        q = ob(rng(t, 0.3+i*0.05, 0.8+i*0.05)); a = clamp(rng(t, 0.3+i*0.05, 0.55+i*0.05))
        text(c, ch, x, 520+(1-q)*60, 124, FG, a); x += tw(c, ch, 124)
    lw = 560*oq(rng(t, 0.9, 1.6)); rrect(c, 960-lw/2, 580, lw, 5, 2.5); setc(c, CYAN); c.fill()
    chips = D["chips"]; widths = [tw(c, s, 30)+56 for s, _ in chips]; x = 960-(sum(widths)+40*(len(chips)-1))/2
    for i, ((s, col), w) in enumerate(zip(chips, widths)):
        q = ob(rng(t, 1.3+i*0.15, 1.8+i*0.15)); a = clamp(q); col = hx(col)
        rrect(c, x, 650+(1-q)*24, w, 64, 32); setc(c, col, 0.14*a); c.fill()
        rrect(c, x, 650+(1-q)*24, w, 64, 32); setc(c, col, 0.7*a); c.set_line_width(2); c.stroke()
        text(c, s, x+28, 693+(1-q)*24, 30, FG, a); x += w+40

def s_map(c, t):
    header(c, t, D.get("map_kicker", "RAIN  ·  SKY"), D["map_title"], D["map_sub"])
    for i, name in enumerate(D["prov_order"]):
        ap = oq(rng(t, 0.3+i*0.04, 0.8+i*0.04)); fp = iob(rng(t, 1.2+i*0.05, 2.0+i*0.05))
        if ap <= 0: continue
        col = mix(LVL[0], LVL[D["prov_lvl"].get(name, 0)], fp)
        for poly in PROV[name]:
            c.move_to(*poly[0])
            for pt in poly[1:]: c.line_to(*pt)
            c.close_path()
        setc(c, col, ap); c.fill_preserve(); setc(c, hx("#0a1428"), ap); c.set_line_width(1.4); c.stroke()
    for s, lon, lat, lvl, st in D["callouts"]:
        q = ob(rng(t, st, st+0.5))
        if q <= 0: continue
        x, y = proj(lon, lat)
        c.new_path(); c.arc(x, y, 7*clamp(q), 0, 6.283); setc(c, FG); c.fill()
        left = lon < 126.9
        pill(c, s, x-16 if left else x+16, y-4, 22, BG1 if lvl >= 2 else FG, LVL[lvl] if lvl else DIM, clamp(q), anchor="r" if left else "l")
    lx, ly = 150, 860; la = oq(rng(t, 0.6, 1.1))
    for i, (lvl, lab) in enumerate(D.get("legend", [[3, "많은 비"], [2, "비"], [1, "약한 비·빗방울"], [0, "비 없음"]])):
        rrect(c, lx, ly+i*40-14, 26, 26, 6); setc(c, LVL[lvl], la); c.fill()
        text(c, lab, lx+40, ly+i*40+8, 20, MUT, la, bold=False)
    px, py, pw = 960, 300, 820
    for i, (name, amt, note) in enumerate(D["rain_rows"]):
        q = oq(rng(t, 1.0+i*0.15, 1.8+i*0.15)); y = py+i*112
        if q <= 0: continue
        card(c, px+(1-q)*50, y, pw, 92, q, r=18)
        text(c, name, px+30+(1-q)*50, y+45, 30, FG, q)
        text(c, note, px+30+(1-q)*50, y+76, 20, MUT, q, bold=False)
        text(c, amt, px+pw-28, y+58, 32, CYAN, q, anchor="r")
    wq = oq(rng(t, 3.2, 3.8))
    rrect(c, px, py+5*112, pw, 64, 16); setc(c, YEL, 0.14*wq); c.fill()
    text(c, D["map_note"], px+24, py+5*112+42, 23, YEL, wq)

def s_temp(c, t):
    header(c, t, "TEMPERATURE", "주요 도시 아침 최저 · 낮 최고", D["temp_sub"])
    cities = D["cities"]; n = len(cities); cw, gap = 176, 16; x0 = (1920-(n*cw+(n-1)*gap))/2; y0 = 300
    for i, (name, lo, hi, ic) in enumerate(cities):
        st = 0.4+i*0.09; q = ob(rng(t, st, st+0.6), 1.2); a = clamp(rng(t, st, st+0.3))
        if a <= 0: continue
        x = x0+i*(cw+gap); y = y0+(1-q)*90
        card(c, x, y, cw, 580, a)
        text(c, name, x+cw/2, y+60, 32, FG, a, anchor="c")
        icon(c, ic, x+cw/2, y+150, 54, a)
        cp = oq(rng(t, st+0.4, st+1.4))
        text(c, f"{round(lerp(10, hi, cp))}°", x+cw/2, y+305, 70, ORNG, a, anchor="c")
        text(c, "낮 최고", x+cw/2, y+337, 18, MUT, a, bold=False, anchor="c")
        text(c, f"{round(lerp(10, lo, cp))}°", x+cw/2, y+420, 48, BLUE, a, anchor="c")
        text(c, "아침 최저", x+cw/2, y+450, 18, MUT, a, bold=False, anchor="c")
        dq = clamp(rng(t, st+1.3, st+1.7)); d = hi-lo
        pill(c, f"일교차 {d}℃", x+cw/2, y+530, 19, BG1 if d >= 9 else FG, YEL if d >= 9 else DIM, dq, anchor="c", pad=12)
    bq = oq(rng(t, 3.4, 4.0))
    text(c, D["temp_note"], 960, 975, 26, MUT, bq, bold=False, anchor="c")

def s_trend(c, t):
    header(c, t, "OUTLOOK", D["trend_title"], D["trend_sub"])
    days = D["trend"]; n = len(days)
    x0, x1, yb, yt = 260, 1700, 900, 380
    vmin = 5*math.floor((min(d[1] for d in days)-2)/5); vmax = 5*math.ceil((max(d[4] for d in days)+1)/5)
    def Y(v): return lerp(yb, yt, (v-vmin)/(vmax-vmin))
    a0 = oq(rng(t, 0.3, 0.8))
    for v in range(vmin+5 if vmin % 5 == 0 else vmin, vmax+1, 5):
        setc(c, FG, 0.07*a0); c.rectangle(x0-40, Y(v), x1-x0+80, 1.2); c.fill()
        text(c, f"{v}℃", x0-60, Y(v)+7, 18, MUT, a0, bold=False, anchor="r")
    xs = [lerp(x0, x1, i/(n-1)) for i in range(n)]
    p = iob(rng(t, 0.8, 3.0))
    for i, (lab, lo0, lo1, hi0, hi1, ic, note) in enumerate(days):
        q = clamp(rng(t, 0.8+i*0.45, 1.3+i*0.45))
        if q <= 0: continue
        x = xs[i]
        rrect(c, x-34, Y(hi1), 68, Y(lo0)-Y(hi1), 14); setc(c, DIM, 0.55*q); c.fill()
        g = cairo.LinearGradient(0, Y(hi1), 0, Y(lo0))
        g.add_color_stop_rgba(0, *ORNG[:3], 0.9*q); g.add_color_stop_rgba(1, *BLUE[:3], 0.9*q)
        hh = (Y(lo0)-Y(hi1))*oq(q)
        rrect(c, x-34, Y(lo0)-hh, 68, hh, 14); c.set_source(g); c.fill()
        text(c, f"{hi0}~{hi1}°", x, Y(hi1)-18, 24, ORNG, q, anchor="c")
        text(c, f"{lo0}~{lo1}°", x, Y(lo0)+36, 24, BLUE, q, anchor="c")
        text(c, lab, x, 990, 28, FG, q, anchor="c")
        icon(c, ic, x, 286, 38, q)
        if note: pill(c, note, x, 326, 18, BG1, CYAN, q, anchor="c", pad=12)
    # low-temp trend line
    pts = [(xs[i], Y(d[1])) for i, d in enumerate(days)]
    if p > 0:
        c.set_line_width(4); setc(c, BLUE, 0.9); c.move_to(*pts[0])
        tot = p*(n-1)
        for i in range(1, n):
            seg = clamp(tot-(i-1))
            if seg <= 0: break
            c.line_to(lerp(pts[i-1][0], pts[i][0], seg), lerp(pts[i-1][1], pts[i][1], seg))
        c.stroke()

def s_outro(c, t):
    q = oq(rng(t, 0.1, 0.7))
    text(c, D["outro1"], 960, 490+(1-q)*30, 72, FG, q, anchor="c")
    lw = 480*oq(rng(t, 0.4, 1.1)); rrect(c, 960-lw/2, 540, lw, 5, 2.5); setc(c, CYAN); c.fill()
    q2 = oq(rng(t, 0.7, 1.3))
    text(c, D["outro2"], 960, 620, 34, MUT, q2, bold=False, anchor="c")
    text(c, D["source"], 960, 700, 22, MUT, q2*0.8, bold=False, anchor="c")

SCENES = [(s_intro, 3.8), (s_map, 6.2), (s_temp, 6.8), (s_trend, 6.4), (s_outro, 3.2)]
TOTAL = sum(d for _, d in SCENES); XF = 0.35

def frame(c, T, starts):
    background(c)
    idx = max(i for i, s in enumerate(starts) if s <= T+1e-9)
    for j in (idx-1, idx):
        if j < 0: continue
        fn, d = SCENES[j]; t = T-starts[j]
        if t < 0 or t > d: continue
        ain = oq(t/XF) if j > 0 else 1.0
        aout = 1-oq((t-(d-XF))/XF) if t > d-XF else 1.0
        a = min(ain, aout)
        if a <= 0: continue
        c.push_group(); fn(c, t); c.pop_group_to_source(); c.paint_with_alpha(a)
    if T > 3.5:
        ba = oq(rng(T, 3.5, 4.2))
        pill(c, D["badge"], 1824, 70, 18, FG, hx("#16294a"), ba, anchor="r", pad=18)

def main():
    starts = []; acc = 0
    for s in SCENES: starts.append(acc); acc += s[1]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(surf)
    fo = cairo.FontOptions(); fo.set_antialias(cairo.ANTIALIAS_GRAY); fo.set_hint_style(cairo.HINT_STYLE_NONE); c.set_font_options(fo)
    c.scale(S, S)
    if sys.argv[1] == "still":
        for T in map(float, sys.argv[2:]):
            frame(c, T, starts); surf.write_to_png(os.environ.get("WX_OUT", ".")+f"/still_{T}.png")
        return
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryslow", "-tune", "animation", "-crf", "31", "-g", "240", "-bf", "8",
                           "-pix_fmt", "yuv420p", "-movflags", "+faststart", sys.argv[1]], stdin=subprocess.PIPE)
    for f in range(int(TOTAL*FPS)):
        frame(c, f/FPS, starts); surf.flush(); ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close(); ff.wait()

main()
