"""
Festival post generator — premium design for David Web Solution.
1080x1080. Fixed layout zones to prevent any overlap.

ZONES:
  0–160   : header (logo + divider)
  160–680 : text content
  680–860 : decorative icons
  860–1080: footer bar
"""
import io, os, math, random
from PIL import Image, ImageDraw, ImageFont
from festival_calendar import THEME_COLORS

SIZE    = 1080
WHITE   = (255, 255, 255)
DARK    = (8,   8,  12)
PHONE   = "+91 82854 23939"
HANDLE  = "@davidwebsolution"

# ── Zones (fixed, never overlap) ─────────────────────────────────────────────
Z_HEADER_END  = 160    # logo + divider end
Z_TEXT_END    = 670    # all text must end here
Z_ICON_MID    = 770    # center of icon row
Z_FOOTER_Y    = 900    # footer text y

# ── Fonts ─────────────────────────────────────────────────────────────────────
def _font(size, bold=True):
    dirs  = ["C:/Windows/Fonts/", "/usr/share/fonts/truetype/dejavu/",
             "/usr/share/fonts/truetype/liberation/"]
    b = ["arialbd.ttf","Arial Bold.ttf","DejaVuSans-Bold.ttf","LiberationSans-Bold.ttf"]
    r = ["arialmt.ttf","Arial.ttf","DejaVuSans.ttf","LiberationSans-Regular.ttf"]
    for d in dirs:
        for n in (b if bold else r):
            p = os.path.join(d, n)
            if os.path.exists(p):
                try: return ImageFont.truetype(p, size)
                except: pass
    return ImageFont.load_default()

def _load_logo(max_w=200, max_h=56):
    path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if not os.path.exists(path): return None
    try:
        logo = Image.open(path).convert("RGBA")
        px = logo.load()
        for y in range(logo.height):
            for x in range(logo.width):
                r, g, b, a = px[x, y]
                if r > 215 and g > 215 and b > 215:
                    px[x, y] = (r, g, b, 0)
        bb = logo.getbbox()
        if bb: logo = logo.crop(bb)
        out = Image.new("RGBA", logo.size, (0,0,0,0))
        op, lp = out.load(), logo.load()
        for y in range(logo.height):
            for x in range(logo.width):
                r, g, b, a = lp[x, y]
                if a > 10: op[x, y] = (255, 255, 255, a)
        out.thumbnail((max_w, max_h), Image.LANCZOS)
        return out
    except: return None

# ── Shared draw helpers ───────────────────────────────────────────────────────
def _radial_glow(img, cx, cy, r_max, color, strength=55):
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(glow)
    for r in range(r_max, 0, -20):
        a = int(strength * (1 - r / r_max))
        gd.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*color, a))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

def _border(draw, ac, ac2):
    M = 18
    draw.rectangle([M, M, SIZE-M, SIZE-M], outline=(*ac, 200), width=3)
    draw.rectangle([M+13, M+13, SIZE-M-13, SIZE-M-13], outline=(*ac, 50), width=1)
    for cx, cy in [(M+10,M+10),(SIZE-M-10,M+10),(M+10,SIZE-M-10),(SIZE-M-10,SIZE-M-10)]:
        pts = [(cx,cy-9),(cx+9,cy),(cx,cy+9),(cx-9,cy)]
        draw.polygon(pts, fill=ac)

def _draw_top_header(img, draw, logo, ac):
    """Logo centered, divider. Always ends at Z_HEADER_END."""
    y = 44
    if logo:
        lx = SIZE//2 - logo.width//2
        img.paste(logo, (lx, y), logo)
        y += logo.height + 14
    else:
        f = _font(30, True)
        bw = draw.textlength("David Web Solution", font=f)
        draw.text((SIZE//2-bw//2, y), "David Web Solution", font=f, fill=WHITE)
        y += 44
    draw.rectangle([SIZE//2-200, y, SIZE//2+200, y+2], fill=(*ac, 160))
    for dx in [-210, -4, 4, 210]:
        draw.ellipse([SIZE//2+dx-5, y-3, SIZE//2+dx+5, y+5], fill=ac)

def _draw_footer(draw, ac):
    """3-line footer in the bottom zone."""
    f1 = _font(26, False)
    f2 = _font(22, False)
    line1 = f"{HANDLE}  •  {PHONE}"
    line2 = "davidwebsolution.com"
    l1w = draw.textlength(line1, font=f1)
    l2w = draw.textlength(line2, font=f2)
    draw.rectangle([40, Z_FOOTER_Y-10, SIZE-40, Z_FOOTER_Y-9], fill=(*ac, 70))
    draw.text((SIZE//2-l1w//2, Z_FOOTER_Y+2),  line1, font=f1, fill=(*ac, 185))
    draw.text((SIZE//2-l2w//2, Z_FOOTER_Y+36), line2, font=f2, fill=(*ac, 130))

def _draw_star5(draw, cx, cy, size=14, color=(245,184,0)):
    pts = []
    for i in range(10):
        a = math.radians(-90+36*i)
        r = size if i%2==0 else size//2
        pts.append((cx+int(r*math.cos(a)), cy+int(r*math.sin(a))))
    draw.polygon(pts, fill=color)

def _sparkle(draw, cx, cy, size=18, color=(245,184,0)):
    for ang in [0, 45, 90, 135]:
        rad = math.radians(ang)
        draw.line([(cx+int(size*math.cos(rad)), cy+int(size*math.sin(rad))),
                   (cx-int(size*math.cos(rad)), cy-int(size*math.sin(rad)))],
                  fill=(*color, 190), width=2)
    draw.ellipse([cx-4, cy-4, cx+4, cy+4], fill=color)

def _text_block(draw, y_start, lines_data, max_y):
    """
    Draw a list of (text, font, color, gap_after).
    Returns final y. Skips any line that would exceed max_y.
    """
    y = y_start
    for text, font, color, gap in lines_data:
        if not text: y += gap//2; continue
        h = font.size if hasattr(font, 'size') else 32
        if y + h > max_y: break
        tw = draw.textlength(text, font=font)
        draw.text((SIZE//2 - tw//2, y), text, font=font, fill=color)
        y += h + gap
    return y

def _auto_fontsize(draw, text, max_w, sizes, bold=True):
    for sz in sizes:
        f = _font(sz, bold)
        if draw.textlength(text, font=f) <= max_w:
            return f, sz
    return _font(sizes[-1], bold), sizes[-1]

def _wrap1(draw, text, font, max_w):
    """Split text into lines that fit max_w."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur+" "+w).strip()
        if draw.textlength(test, font=font) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ── Icon rows (drawn in Z_ICON zone, never overlaps text) ────────────────────
def _diya(img, cx, cy, size=70):
    """Simple clean diya — bowl + flame. cy = bowl top."""
    draw = ImageDraw.Draw(img, "RGBA")
    GOLD, CLAY, FLAME = (245,184,0), (170,85,30), (255,120,20)
    # Bowl
    bw, bh = size, size//2
    draw.ellipse([cx-bw, cy, cx+bw, cy+bh], fill=CLAY)
    draw.ellipse([cx-bw+6, cy+6, cx+bw-6, cy+bh-4], fill=(190,100,40))
    draw.arc([cx-bw, cy, cx+bw, cy+bh], 180, 0, fill=GOLD, width=4)
    # Spout tips
    draw.ellipse([cx-bw-8, cy+bh//2-4, cx-bw+8, cy+bh//2+4], fill=GOLD)
    draw.ellipse([cx+bw-8, cy+bh//2-4, cx+bw+8, cy+bh//2+4], fill=GOLD)
    # Wick
    wick_top = cy - size//2
    draw.line([(cx, cy-4), (cx, wick_top)], fill=(220,220,200), width=3)
    # Flame layers (contained above wick_top)
    for r, col, alpha in [(size//2, FLAME, 20), (size//3, FLAME, 45),
                          (size//4, (255,180,0), 90), (size//5, (255,230,80), 160)]:
        draw.ellipse([cx-r//3, wick_top-r, cx+r//3, wick_top+r//5],
                     fill=(*col, alpha))
    draw.ellipse([cx-9, wick_top-16, cx+9, wick_top+5], fill=(255,245,200,220))

def _snowflake(draw, cx, cy, size=44, color=(190,220,255)):
    for i in range(6):
        a = math.radians(60*i)
        ex = cx+int(size*math.cos(a)); ey = cy+int(size*math.sin(a))
        draw.line([(cx,cy),(ex,ey)], fill=(*color,210), width=3)
        for d in [0.38, 0.68]:
            bx=cx+int(size*d*math.cos(a)); by=cy+int(size*d*math.sin(a))
            for ba in [a+math.pi/4, a-math.pi/4]:
                draw.line([(bx,by),(bx+int(10*math.cos(ba)),by+int(10*math.sin(ba)))],
                          fill=(*color,160), width=2)
    draw.ellipse([cx-5,cy-5,cx+5,cy+5], fill=color)

def _firework_burst(draw, cx, cy, rays=10, length=48, color=(245,184,0)):
    for i in range(rays):
        a = math.radians(360/rays*i)
        ex=cx+int(length*math.cos(a)); ey=cy+int(length*math.sin(a))
        draw.line([(cx,cy),(ex,ey)], fill=(*color,165), width=2)
        draw.ellipse([ex-4,ey-4,ex+4,ey+4], fill=color)

def _heart(draw, cx, cy, size=28, color=(220,30,80)):
    pts = []
    for t in range(360):
        rad = math.radians(t)
        x = int(cx + size*16*math.sin(rad)**3/16)
        y = int(cy - size*(13*math.cos(rad)-5*math.cos(2*rad)
                           -2*math.cos(3*rad)-math.cos(4*rad))/16)
        pts.append((x,y))
    if len(pts) > 2: draw.polygon(pts, fill=(*color,210))

# ── BACKGROUND helpers ────────────────────────────────────────────────────────
def _bg_sparkles(draw, seed, ac, ac2, count=24):
    random.seed(seed)
    for _ in range(count):
        sx,sy = random.randint(55,SIZE-55), random.randint(55,SIZE-55)
        col   = ac if random.random() > 0.4 else ac2
        _sparkle(draw, sx, sy, random.randint(8,18), col)

# ══════════════════════════════════════════════════════════════════════════════
# PER-THEME GENERATORS
# ══════════════════════════════════════════════════════════════════════════════
def _make_diwali(festival):
    c   = THEME_COLORS["diwali"]
    ac, ac2, txt = c["accent"], c["accent2"], c["text"]

    img  = Image.new("RGB",(SIZE,SIZE),c["bg"])
    img  = _radial_glow(img,SIZE//2,SIZE//2+80,580,(130,55,8),55)
    img  = _radial_glow(img,SIZE//2,160,300,ac2,28)
    draw = ImageDraw.Draw(img,"RGBA")

    # Subtle rangoli ring
    for i in range(48):
        a = math.radians(360/48*i)
        x = SIZE//2+int(490*math.cos(a)); y = SIZE//2+int(490*math.sin(a))
        draw.ellipse([x-3,y-3,x+3,y+3], fill=(*ac,50))

    _bg_sparkles(draw, 1, ac, ac2, 22)
    _border(draw, ac, ac2)

    logo = _load_logo(); _draw_top_header(img, draw, logo, ac)
    draw = ImageDraw.Draw(img,"RGBA")

    # ── Text block (160 → 670) ────────────────────────────────────────────
    y = Z_HEADER_END + 18

    f_pre = _font(40, False)
    pre = "Wishing You A"
    pw  = draw.textlength(pre, font=f_pre)
    draw.text((SIZE//2-pw//2, y), pre, font=f_pre, fill=(*txt,175)); y += 54

    f_hap = _font(84, True)
    hw = draw.textlength("Happy", font=f_hap)
    draw.text((SIZE//2-hw//2, y), "Happy", font=f_hap, fill=WHITE); y += 96

    f_name, fsz = _auto_fontsize(draw,"DIWALI",SIZE-100,[130,118,106],True)
    nw = draw.textlength("DIWALI", font=f_name)
    for ox,oy in [(3,3),(-3,-3)]:
        draw.text((SIZE//2-nw//2+ox,y+oy),"DIWALI",font=f_name,fill=(*ac2,50))
    draw.text((SIZE//2-nw//2,y),"DIWALI",font=f_name,fill=ac); y += fsz+14

    # Underline
    draw.rectangle([SIZE//2-180,y,SIZE//2+180,y+4],fill=(*ac2,210)); y += 18

    # Sub with stars
    f_sub = _font(32, False)
    sub   = festival.get("sub","Festival of Lights")
    sw    = draw.textlength(sub, font=f_sub)
    sx0   = SIZE//2-sw//2
    _draw_star5(draw, sx0-24, y+16, 12, ac2)
    _draw_star5(draw, sx0+int(sw)+24, y+16, 12, ac2)
    draw.text((sx0, y), sub, font=f_sub, fill=(*ac2,230)); y += 50

    # Message
    f_msg = _font(28, False)
    msg   = festival.get("msg","")
    for ln in _wrap1(draw, msg, f_msg, SIZE-110)[:2]:
        lw = draw.textlength(ln, font=f_msg)
        if y + 36 > Z_TEXT_END: break
        draw.text((SIZE//2-lw//2, y), ln, font=f_msg, fill=(*txt,170)); y += 40

    # ── Icons zone (680–860) ──────────────────────────────────────────────
    icon_y = Z_ICON_MID - 30   # top of diya bowl
    _diya(img, SIZE//2-210, icon_y, 65)
    _diya(img, SIZE//2,     icon_y-20, 80)
    _diya(img, SIZE//2+210, icon_y, 65)

    _draw_footer(draw, ac)
    return img.convert("RGB")


def _make_christmas(festival):
    c   = THEME_COLORS["christmas"]
    ac, ac2, txt = c["accent"], c["accent2"], c["text"]

    img  = Image.new("RGB",(SIZE,SIZE),c["bg"])
    img  = _radial_glow(img,SIZE//2,SIZE//2,580,(8,55,8),55)
    img  = _radial_glow(img,SIZE//2,120,300,ac,25)
    draw = ImageDraw.Draw(img,"RGBA")

    random.seed(2)
    for _ in range(14):
        sx,sy=random.randint(55,SIZE-55),random.randint(55,SIZE-55)
        _snowflake(draw,sx,sy,random.randint(14,32),(160,210,255))

    _bg_sparkles(draw,2,ac,ac2,16)
    _border(draw,ac,ac2)
    logo=_load_logo(); _draw_top_header(img,draw,logo,ac)
    draw=ImageDraw.Draw(img,"RGBA")

    y = Z_HEADER_END+18

    f_pre=_font(40,False)
    pre="Wishing You A"
    pw=draw.textlength(pre,font=f_pre)
    draw.text((SIZE//2-pw//2,y),pre,font=f_pre,fill=(*txt,175)); y+=54

    f_m=_font(110,True)
    mw=draw.textlength("Merry",font=f_m)
    draw.text((SIZE//2-mw//2,y),"Merry",font=f_m,fill=WHITE); y+=122

    f_x,fsz=_auto_fontsize(draw,"Christmas",SIZE-80,[110,96,84],True)
    xw=draw.textlength("Christmas",font=f_x)
    for ox,oy in [(3,3),(-3,-3)]:
        draw.text((SIZE//2-xw//2+ox,y+oy),"Christmas",font=f_x,fill=(*ac,50))
    draw.text((SIZE//2-xw//2,y),"Christmas",font=f_x,fill=ac); y+=fsz+14

    draw.rectangle([SIZE//2-180,y,SIZE//2+180,y+4],fill=(*ac2,210)); y+=18

    f_sub=_font(32,False)
    sub=festival.get("sub","Merry Christmas")
    sw=draw.textlength(sub,font=f_sub)
    _draw_star5(draw,SIZE//2-sw//2-24,y+16,12,ac2)
    _draw_star5(draw,SIZE//2+int(sw)//2+24+int(sw)//2,y+16,12,ac2)
    draw.text((SIZE//2-sw//2,y),sub,font=f_sub,fill=(*ac2,230)); y+=50

    f_msg=_font(28,False)
    msg=festival.get("msg","")
    for ln in _wrap1(draw,msg,f_msg,SIZE-110)[:2]:
        lw=draw.textlength(ln,font=f_msg)
        if y+36>Z_TEXT_END: break
        draw.text((SIZE//2-lw//2,y),ln,font=f_msg,fill=(*txt,170)); y+=40

    # Icons: 3 snowflakes
    _snowflake(draw,SIZE//2-190,Z_ICON_MID,50,(200,230,255))
    _snowflake(draw,SIZE//2,    Z_ICON_MID-18,62,(220,240,255))
    _snowflake(draw,SIZE//2+190,Z_ICON_MID,50,(200,230,255))

    _draw_footer(draw,ac)
    return img.convert("RGB")


def _make_newyear(festival):
    c   = THEME_COLORS["newyear"]
    ac, ac2, txt = c["accent"], c["accent2"], c["text"]

    img  = Image.new("RGB",(SIZE,SIZE),c["bg"])
    img  = _radial_glow(img,SIZE//2,SIZE//2,600,(55,25,110),55)
    img  = _radial_glow(img,100,100,280,ac,28)
    img  = _radial_glow(img,SIZE-100,SIZE-100,280,ac2,28)
    draw = ImageDraw.Draw(img,"RGBA")

    for cx,cy,col in [(170,190,ac),(880,170,ac2),(90,580,ac),(950,540,ac2)]:
        _firework_burst(draw,cx,cy,10,46,col)
    _bg_sparkles(draw,3,ac,ac2,20)
    _border(draw,ac,ac2)
    logo=_load_logo(); _draw_top_header(img,draw,logo,ac)
    draw=ImageDraw.Draw(img,"RGBA")

    y = Z_HEADER_END+14

    f_pre=_font(38,False)
    pre="Cheers To"
    pw=draw.textlength(pre,font=f_pre)
    draw.text((SIZE//2-pw//2,y),pre,font=f_pre,fill=(*txt,175)); y+=50

    f_ny=_font(38,False)
    ny="A New Year!"
    nyw=draw.textlength(ny,font=f_ny)
    draw.text((SIZE//2-nyw//2,y),ny,font=f_ny,fill=(*txt,175)); y+=54

    # Big year
    f_yr,ysz=_auto_fontsize(draw,"2027",SIZE-80,[200,180,160,140],True)
    yw=draw.textlength("2027",font=f_yr)
    for ox,oy in [(4,4),(-4,-4)]:
        draw.text((SIZE//2-yw//2+ox,y+oy),"2027",font=f_yr,fill=(*ac2,45))
    draw.text((SIZE//2-yw//2,y),"2027",font=f_yr,fill=ac); y+=ysz+14

    draw.rectangle([SIZE//2-200,y,SIZE//2+200,y+4],fill=(*ac2,210)); y+=18

    f_sub=_font(32,False)
    sub=festival.get("sub","Happy New Year 2027")
    sw=draw.textlength(sub,font=f_sub)
    _draw_star5(draw,SIZE//2-sw//2-24,y+16,12,ac2)
    _draw_star5(draw,SIZE//2+int(sw//2)+24+int(sw//2),y+16,12,ac2)
    draw.text((SIZE//2-sw//2,y),sub,font=f_sub,fill=(*ac2,230)); y+=50

    f_msg=_font(28,False)
    msg=festival.get("msg","")
    for ln in _wrap1(draw,msg,f_msg,SIZE-110)[:2]:
        lw=draw.textlength(ln,font=f_msg)
        if y+36>Z_TEXT_END: break
        draw.text((SIZE//2-lw//2,y),ln,font=f_msg,fill=(*txt,170)); y+=40

    # Icons: fireworks
    for dx,col in [(-200,ac),(-80,ac2),(80,ac),(200,ac2)]:
        _firework_burst(draw,SIZE//2+dx,Z_ICON_MID,9,38,col)

    _draw_footer(draw,ac)
    return img.convert("RGB")


def _make_holi(festival):
    c   = THEME_COLORS["holi"]
    ac, ac2 = c["accent"], c["accent2"]
    cols = [(255,80,120),(80,200,255),(255,200,0),(100,255,180),(200,100,255),(255,140,0)]

    img=Image.new("RGB",(SIZE,SIZE),(14,5,32))
    draw=ImageDraw.Draw(img,"RGBA")

    random.seed(4)
    for _ in range(40):
        sx,sy=random.randint(0,SIZE),random.randint(0,SIZE)
        sr=random.randint(28,110)
        col=random.choice(cols)
        draw.ellipse([sx-sr,sy-sr,sx+sr,sy+sr],fill=(*col,random.randint(28,65)))

    img=_radial_glow(img,SIZE//2,SIZE//2,520,(18,5,48),78)
    draw=ImageDraw.Draw(img,"RGBA")
    _border(draw,ac,ac2)
    logo=_load_logo(); _draw_top_header(img,draw,logo,ac)
    draw=ImageDraw.Draw(img,"RGBA")

    y = Z_HEADER_END+18

    f_pre=_font(40,False)
    pre="Wishing You A"
    pw=draw.textlength(pre,font=f_pre)
    draw.text((SIZE//2-pw//2,y),pre,font=f_pre,fill=(*WHITE,180)); y+=54

    f_hap=_font(100,True)
    hw=draw.textlength("Happy",font=f_hap)
    draw.text((SIZE//2-hw//2,y),"Happy",font=f_hap,fill=WHITE); y+=114

    f_ho,hsz=_auto_fontsize(draw,"Holi!",SIZE-80,[118,104,90],True)
    hcw=draw.textlength("Holi!",font=f_ho)
    for ox,col in [(-4,cols[0]),(4,cols[1])]:
        draw.text((SIZE//2-hcw//2+ox,y+4),"Holi!",font=f_ho,fill=(*col,65))
    draw.text((SIZE//2-hcw//2,y),"Holi!",font=f_ho,fill=ac); y+=hsz+14

    draw.rectangle([SIZE//2-180,y,SIZE//2+180,y+4],fill=(*ac2,210)); y+=18

    f_sub=_font(32,False)
    sub=festival.get("sub","Festival of Colours")
    sw=draw.textlength(sub,font=f_sub)
    _draw_star5(draw,SIZE//2-sw//2-24,y+16,12,ac2)
    _draw_star5(draw,SIZE//2+int(sw//2)+24+int(sw//2),y+16,12,ac2)
    draw.text((SIZE//2-sw//2,y),sub,font=f_sub,fill=(*ac2,230)); y+=50

    f_msg=_font(28,False)
    msg=festival.get("msg","")
    for ln in _wrap1(draw,msg,f_msg,SIZE-110)[:2]:
        lw=draw.textlength(ln,font=f_msg)
        if y+36>Z_TEXT_END: break
        draw.text((SIZE//2-lw//2,y),ln,font=f_msg,fill=(*WHITE,170)); y+=40
    y+=10

    # Coloured dot row in icon zone
    for i,col in enumerate(cols*3):
        dx = SIZE//2-150+i*22
        if dx > SIZE//2+150: break
        draw.ellipse([dx-10,Z_ICON_MID-10,dx+10,Z_ICON_MID+10],fill=(*col,220))

    _draw_footer(draw,ac)
    return img.convert("RGB")


def _make_generic(festival):
    theme = festival.get("theme","diwali")
    c     = THEME_COLORS.get(theme, THEME_COLORS["diwali"])
    ac, ac2, txt = c["accent"], c["accent2"], c["text"]

    img  = Image.new("RGB",(SIZE,SIZE),c["bg"])
    img  = _radial_glow(img,SIZE//2,SIZE//2,600,ac2,45)
    draw = ImageDraw.Draw(img,"RGBA")
    _bg_sparkles(draw,5,ac,ac2,22)
    _border(draw,ac,ac2)
    logo=_load_logo(); _draw_top_header(img,draw,logo,ac)
    draw=ImageDraw.Draw(img,"RGBA")

    y = Z_HEADER_END+18

    f_pre=_font(40,False)
    pre="Wishing You A"
    pw=draw.textlength(pre,font=f_pre)
    draw.text((SIZE//2-pw//2,y),pre,font=f_pre,fill=(*txt,175)); y+=54

    name=festival.get("name","").upper()
    f_nm,fsz=_auto_fontsize(draw,name,SIZE-80,[120,106,94,82],True)
    nw=draw.textlength(name,font=f_nm)
    for ox,oy in [(3,3),(-3,-3)]:
        draw.text((SIZE//2-nw//2+ox,y+oy),name,font=f_nm,fill=(*ac2,50))
    draw.text((SIZE//2-nw//2,y),name,font=f_nm,fill=ac); y+=fsz+14

    draw.rectangle([SIZE//2-180,y,SIZE//2+180,y+4],fill=(*ac2,210)); y+=18

    f_sub=_font(32,False)
    sub=festival.get("sub","")
    sw=draw.textlength(sub,font=f_sub)
    _draw_star5(draw,SIZE//2-sw//2-24,y+16,12,ac2)
    _draw_star5(draw,SIZE//2+int(sw//2)+24+int(sw//2),y+16,12,ac2)
    draw.text((SIZE//2-sw//2,y),sub,font=f_sub,fill=(*ac2,230)); y+=50

    f_msg=_font(28,False)
    msg=festival.get("msg","")
    for ln in _wrap1(draw,msg,f_msg,SIZE-110)[:2]:
        lw=draw.textlength(ln,font=f_msg)
        if y+36>Z_TEXT_END: break
        draw.text((SIZE//2-lw//2,y),ln,font=f_msg,fill=(*txt,170)); y+=40

    # Generic sparkle icons
    for dx in [-200,-80,80,200]:
        _sparkle(draw,SIZE//2+dx,Z_ICON_MID,28,ac)

    _draw_footer(draw,ac)
    return img.convert("RGB")


def _make_chhath(festival):
    c   = THEME_COLORS.get("chhath", {"bg":(20,8,0),"accent":(255,140,0),"accent2":(255,220,80),"text":(255,240,210)})
    ac, ac2, txt = c["accent"], c["accent2"], c["text"]

    img  = Image.new("RGB",(SIZE,SIZE),c["bg"])
    img  = _radial_glow(img,SIZE//2,SIZE-200,600,(120,50,0),70)
    img  = _radial_glow(img,SIZE//2,SIZE-200,350,ac,45)
    draw = ImageDraw.Draw(img,"RGBA")

    # Horizon water reflection
    for i in range(12):
        y = SIZE-180 + i*8
        alpha = max(10, 60 - i*5)
        draw.rectangle([0, y, SIZE, y+4], fill=(*ac2, alpha))

    # Sun rising from horizon
    sun_cx, sun_cy = SIZE//2, SIZE-160
    for r,col,a in [(110,ac,18),(80,ac,35),(55,ac2,70),(38,ac2,130),(22,(255,255,200),200)]:
        draw.ellipse([sun_cx-r,sun_cy-r,sun_cx+r,sun_cy+r], fill=(*col,a))
    draw.ellipse([sun_cx-18,sun_cy-18,sun_cx+18,sun_cy+18], fill=(255,255,220))

    # Sun rays
    for i in range(16):
        a = math.radians(360/16*i)
        r1,r2 = 26, 55
        draw.line([(sun_cx+int(r1*math.cos(a)),sun_cy+int(r1*math.sin(a))),
                   (sun_cx+int(r2*math.cos(a)),sun_cy+int(r2*math.sin(a)))],
                  fill=(*ac2,120), width=2)

    _bg_sparkles(draw,6,ac,ac2,16)
    _border(draw,ac,ac2)
    logo=_load_logo(); _draw_top_header(img,draw,logo,ac)
    draw=ImageDraw.Draw(img,"RGBA")

    y = Z_HEADER_END+18

    f_pre=_font(40,False)
    pre="Wishing You A"
    pw=draw.textlength(pre,font=f_pre)
    draw.text((SIZE//2-pw//2,y),pre,font=f_pre,fill=(*txt,175)); y+=54

    f_hap=_font(96,True)
    hw=draw.textlength("Happy",font=f_hap)
    draw.text((SIZE//2-hw//2,y),"Happy",font=f_hap,fill=WHITE); y+=110

    f_nm,fsz=_auto_fontsize(draw,"Chhath Puja",SIZE-80,[110,96,84],True)
    nw=draw.textlength("Chhath Puja",font=f_nm)
    for ox,oy in [(3,3),(-3,-3)]:
        draw.text((SIZE//2-nw//2+ox,y+oy),"Chhath Puja",font=f_nm,fill=(*ac2,50))
    draw.text((SIZE//2-nw//2,y),"Chhath Puja",font=f_nm,fill=ac); y+=fsz+14

    draw.rectangle([SIZE//2-180,y,SIZE//2+180,y+4],fill=(*ac2,210)); y+=18

    f_sub=_font(32,False)
    sub=festival.get("sub","Festival of Sun & Nature")
    sw=draw.textlength(sub,font=f_sub)
    _draw_star5(draw,SIZE//2-sw//2-24,y+16,12,ac2)
    _draw_star5(draw,SIZE//2+int(sw//2)+24+int(sw//2),y+16,12,ac2)
    draw.text((SIZE//2-sw//2,y),sub,font=f_sub,fill=(*ac2,230)); y+=50

    f_msg=_font(28,False)
    msg=festival.get("msg","")
    for ln in _wrap1(draw,msg,f_msg,SIZE-110)[:2]:
        lw=draw.textlength(ln,font=f_msg)
        if y+36>Z_TEXT_END: break
        draw.text((SIZE//2-lw//2,y),ln,font=f_msg,fill=(*txt,170)); y+=40

    # Icons: 3 small suns
    for dx,sz in [(-200,32),(0,42),(200,32)]:
        cx=SIZE//2+dx; cy=Z_ICON_MID
        draw.ellipse([cx-sz,cy-sz,cx+sz,cy+sz],fill=(*ac2,200))
        for i in range(8):
            a=math.radians(45*i)
            draw.line([(cx+int((sz+4)*math.cos(a)),cy+int((sz+4)*math.sin(a))),
                       (cx+int((sz+16)*math.cos(a)),cy+int((sz+16)*math.sin(a)))],
                      fill=(*ac,180),width=2)

    _draw_footer(draw,ac)
    return img.convert("RGB")


# ── Public API ────────────────────────────────────────────────────────────────
_RENDERERS = {
    "diwali":    _make_diwali,
    "christmas": _make_christmas,
    "newyear":   _make_newyear,
    "holi":      _make_holi,
}

def generate_festival_post(festival: dict) -> bytes:
    renderer = _RENDERERS.get(festival.get("theme",""), _make_generic)
    img      = renderer(festival)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=95)
    return buf.getvalue()

def build_festival_caption(festival: dict) -> str:
    name  = festival.get("name","Festival")
    msg   = festival.get("msg","")
    theme = festival.get("theme","")
    tags  = {
        "diwali":    "#HappyDiwali #Diwali2026 #FestivalOfLights #Diwali",
        "christmas": "#MerryChristmas #Christmas2026 #Xmas #ChristmasVibes",
        "newyear":   "#HappyNewYear #NewYear2027 #NewYear #Cheers2027",
        "holi":      "#HappyHoli #Holi2027 #FestivalOfColours #Holi",
        "eid":       "#EidMubarak #Eid2027 #EidUlFitr",
        "valentine": "#HappyValentinesDay #ValentinesDay #Love",
        "halloween": "#HappyHalloween #Halloween2027 #Spooky",
    }.get(theme, f"#{name.replace(' ','')}")
    return (
        f"Happy {name} from all of us at David Web Solution! 🎉\n\n"
        f"{msg}\n\n"
        f"We're grateful for every client who trusted us to grow their brand.\n\n"
        f"📞 {PHONE}\n"
        f"🌐 davidwebsolution.com\n\n"
        f"#DavidWebSolution #DigitalMarketing #WebDesign {tags} "
        f"#USBusiness #UKBusiness #SmallBusiness"
    )
