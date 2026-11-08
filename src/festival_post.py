"""
Festival post generator — premium design for David Web Solution.
1080x1080 branded festival greetings with per-theme layouts.
"""
import io, os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from festival_calendar import THEME_COLORS

SIZE  = 1080
WHITE = (255, 255, 255)
DARK  = (8,   8,  12)
PHONE = "+91 82854 23939"
HANDLE = "@davidwebsolution"

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

def _load_logo(max_w=200, max_h=60):
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
                if a > 10: op[x, y] = (255,255,255,a)
        out.thumbnail((max_w, max_h), Image.LANCZOS)
        return out
    except: return None

# ── Drawing helpers ───────────────────────────────────────────────────────────
def _radial_glow(img, cx, cy, r_max, color, strength=60):
    glow = Image.new("RGBA", (SIZE, SIZE), (0,0,0,0))
    gd   = ImageDraw.Draw(glow)
    for r in range(r_max, 0, -18):
        a = int(strength * (1 - r/r_max))
        gd.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*color, a))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

def _rangoli_ring(draw, cx, cy, radius, color, dots=24, dot_r=5):
    for i in range(dots):
        angle = math.radians(360/dots * i)
        x = cx + int(radius * math.cos(angle))
        y = cy + int(radius * math.sin(angle))
        draw.ellipse([x-dot_r, y-dot_r, x+dot_r, y+dot_r], fill=color)

def _draw_diya_large(img, cx, cy, size=130):
    """Large decorative diya as center visual element."""
    draw = ImageDraw.Draw(img, "RGBA")
    GOLD   = (245, 184,  0)
    GOLD2  = (255, 215, 60)
    ORANGE = (255, 110, 20)
    RED    = (220,  40, 40)
    CLAY   = (180,  90, 30)

    # Shadow
    for r in range(size+40, size, -6):
        a = int(40*(1-(r-size)/40))
        draw.ellipse([cx-r, cy-r//3, cx+r, cy+r//3+10], fill=(0,0,0,a))

    # Bowl body
    bw, bh = size, size//2
    draw.ellipse([cx-bw, cy, cx+bw, cy+bh+10], fill=CLAY)
    draw.ellipse([cx-bw+6, cy+6, cx+bw-6, cy+bh+4], fill=(200,110,50))

    # Gold rim
    draw.arc([cx-bw, cy, cx+bw, cy+bh+10], 180, 0, fill=GOLD, width=5)

    # Oil surface (inner ellipse lighter)
    draw.ellipse([cx-bw+16, cy+10, cx+bw-16, cy+bh-6], fill=(160,70,20))

    # Spout
    pts = [(cx-bw, cy+bh//3),
           (cx-bw-size//2, cy+bh//2+10),
           (cx+bw+size//2, cy+bh//2+10),
           (cx+bw, cy+bh//3)]
    draw.polygon(pts, fill=CLAY)
    draw.line([(cx-bw, cy+bh//3),(cx-bw-size//2, cy+bh//2+10)], fill=GOLD2, width=3)
    draw.line([(cx+bw, cy+bh//3),(cx+bw+size//2, cy+bh//2+10)], fill=GOLD2, width=3)

    # Wick
    draw.line([(cx, cy-5),(cx, cy-size//2)], fill=(220,220,200), width=4)

    # Flame — layered glows
    flame_cx, flame_cy = cx, cy - size//2
    for r, col, alpha in [
        (size//2+10, ORANGE,  25),
        (size//2,    ORANGE,  40),
        (size//3,    (255,160,0), 60),
        (size//4,    GOLD2,  100),
        (size//5,    (255,240,180), 160),
    ]:
        draw.ellipse([flame_cx-r//3, flame_cy-r,
                      flame_cx+r//3, flame_cy+r//4],
                     fill=(*col, alpha))

    # Bright core
    draw.ellipse([flame_cx-12, flame_cy-20,
                  flame_cx+12, flame_cy+8], fill=(255,255,220,230))

def _draw_snowflake_lg(draw, cx, cy, size=48, color=(180,220,255)):
    for i in range(6):
        angle = math.radians(60*i)
        ex = cx + int(size*math.cos(angle))
        ey = cy + int(size*math.sin(angle))
        draw.line([(cx,cy),(ex,ey)], fill=(*color,210), width=3)
        for d in [0.35, 0.65]:
            bx = cx+int(size*d*math.cos(angle))
            by = cy+int(size*d*math.sin(angle))
            for ba in [angle+math.pi/4, angle-math.pi/4]:
                draw.line([(bx,by),(bx+int(12*math.cos(ba)),by+int(12*math.sin(ba)))],
                          fill=(*color,160), width=2)
    draw.ellipse([cx-6,cy-6,cx+6,cy+6], fill=color)

def _draw_star5(draw, cx, cy, size=40, color=(245,184,0)):
    pts = []
    for i in range(10):
        a = math.radians(-90+36*i)
        r = size if i%2==0 else size//2
        pts.append((cx+int(r*math.cos(a)), cy+int(r*math.sin(a))))
    draw.polygon(pts, fill=color)

def _draw_heart(draw, cx, cy, size=32, color=(220,30,80)):
    pts = []
    for t_int in range(360):
        t = math.radians(t_int)
        x = int(cx + size*16*math.sin(t)**3/16)
        y = int(cy - size*(13*math.cos(t)-5*math.cos(2*t)
                           -2*math.cos(3*t)-math.cos(4*t))/16)
        pts.append((x,y))
    if len(pts) > 2:
        draw.polygon(pts, fill=(*color,220))

def _draw_crescent(draw, cx, cy, size=42, color=(0,160,80)):
    draw.ellipse([cx-size,cy-size,cx+size,cy+size], fill=(*color,220))
    draw.ellipse([cx-size+size//3,cy-size-4,cx+size+size//3,cy+size-4],
                 fill=(*DARK,255))

DARK = (8,8,12)

# ── Shared layout pieces ──────────────────────────────────────────────────────
def _draw_top_header(img, draw, logo, accent):
    """Logo center + thin divider. Returns y after header."""
    y = 56
    if logo:
        lx = SIZE//2 - logo.width//2
        img.paste(logo, (lx, y), logo)
        y += logo.height + 16
    else:
        f = _font(34, True)
        bw = draw.textlength("David Web Solution", font=f)
        draw.text((SIZE//2-bw//2, y), "David Web Solution", font=f, fill=WHITE)
        y += 50
    # Divider with dot ornaments
    draw.rectangle([SIZE//2-200, y, SIZE//2+200, y+2], fill=(*accent,160))
    for dx in [-210,-4,4,210]:
        draw.ellipse([SIZE//2+dx-5,y-3,SIZE//2+dx+5,y+5], fill=accent)
    return y + 22

def _draw_footer_bar(draw, accent):
    """Bottom bar: handle | phone | website"""
    y = SIZE - 68
    draw.rectangle([40, y-6, SIZE-40, y-5], fill=(*accent,80))
    f = _font(26, False)
    items = [HANDLE, PHONE, "davidwebsolution.com"]
    full  = "  •  ".join(items)
    fw    = draw.textlength(full, font=f)
    # If too wide, split into 2 lines
    if fw > SIZE - 80:
        line1 = f"{HANDLE}  •  {PHONE}"
        line2 = "davidwebsolution.com"
        l1w = draw.textlength(line1, font=f)
        l2w = draw.textlength(line2, font=f)
        draw.text((SIZE//2-l1w//2, y), line1, font=f, fill=(*accent,180))
        draw.text((SIZE//2-l2w//2, y+32), line2, font=_font(22,False), fill=(*accent,130))
    else:
        draw.text((SIZE//2-fw//2, y), full, font=f, fill=(*accent,180))

def _border(draw, accent, accent2):
    M = 18
    draw.rectangle([M,M,SIZE-M,SIZE-M], outline=(*accent,200), width=3)
    draw.rectangle([M+12,M+12,SIZE-M-12,SIZE-M-12], outline=(*accent,55), width=1)
    # Corner diamonds
    for cx,cy in [(M+10,M+10),(SIZE-M-10,M+10),(M+10,SIZE-M-10),(SIZE-M-10,SIZE-M-10)]:
        pts = [(cx,cy-10),(cx+10,cy),(cx,cy+10),(cx-10,cy)]
        draw.polygon(pts, fill=accent)
        draw.polygon(pts, outline=accent2, width=1)

# ── DIWALI ────────────────────────────────────────────────────────────────────
def _make_diwali(festival):
    c = THEME_COLORS["diwali"]
    ac, ac2, txt = c["accent"], c["accent2"], c["text"]
    bg = c["bg"]

    img  = Image.new("RGB", (SIZE,SIZE), bg)
    img  = _radial_glow(img, SIZE//2, SIZE//2+100, 600, (140,60,10), 55)
    img  = _radial_glow(img, SIZE//2, 200, 350, ac2, 30)
    draw = ImageDraw.Draw(img, "RGBA")

    # Rangoli rings
    _rangoli_ring(draw, SIZE//2, SIZE//2, 480, (*ac,  60), 36, 4)
    _rangoli_ring(draw, SIZE//2, SIZE//2, 440, (*ac2, 40), 48, 3)
    _rangoli_ring(draw, SIZE//2, SIZE//2, 400, (*ac,  30), 60, 2)

    # Scattered sparkles
    random.seed(1)
    for _ in range(30):
        sx,sy = random.randint(50,SIZE-50), random.randint(50,SIZE-50)
        col   = ac if random.random()>0.4 else ac2
        sz    = random.randint(8,20)
        for ang in [0,45,90,135]:
            rad = math.radians(ang)
            draw.line([(sx+int(sz*math.cos(rad)),sy+int(sz*math.sin(rad))),
                       (sx-int(sz*math.cos(rad)),sy-int(sz*math.sin(rad)))],
                      fill=(*col,180), width=1)

    _border(draw, ac, ac2)

    logo = _load_logo(190,58)
    y = _draw_top_header(img, draw, logo, ac)
    y += 10

    # "Wishing You A"
    f1 = _font(44, False)
    t1 = "Wishing You A"
    w1 = draw.textlength(t1, font=f1)
    draw.text((SIZE//2-w1//2, y), t1, font=f1, fill=(*txt,180))
    y += 58

    # "Happy"
    f2 = _font(96, True)
    t2 = "Happy"
    w2 = draw.textlength(t2, font=f2)
    draw.text((SIZE//2-w2//2, y), t2, font=f2, fill=WHITE)
    y += 106

    # "DIWALI" — big gold
    f3 = _font(148, True)
    t3 = "DIWALI"
    w3 = draw.textlength(t3, font=f3)
    for ox,oy in [(4,4),(-4,-4),(4,-4),(-4,4)]:
        draw.text((SIZE//2-w3//2+ox, y+oy), t3, font=f3, fill=(*ac2,55))
    draw.text((SIZE//2-w3//2, y), t3, font=f3, fill=ac)
    y += 162

    # Underline
    draw.rectangle([SIZE//2-180,y,SIZE//2+180,y+4], fill=(*ac2,220))
    y += 18

    # Sub with star icons
    f4   = _font(34, False)
    sub  = festival.get("sub","Festival of Lights")
    sw   = draw.textlength(sub, font=f4)
    _draw_star5(draw, SIZE//2-sw//2-28, y+17, 13, ac2)
    _draw_star5(draw, SIZE//2+sw//2+28, y+17, 13, ac2)
    draw.text((SIZE//2-sw//2, y), sub, font=f4, fill=(*ac2,230))
    y += 52

    # Message
    f5  = _font(30, False)
    msg = festival.get("msg","")
    mw  = draw.textlength(msg, font=f5)
    if mw > SIZE-120:
        words = msg.split()
        lines,cur = [],""
        for w in words:
            test=(cur+" "+w).strip()
            if draw.textlength(test,font=f5)<=SIZE-120: cur=test
            else:
                if cur: lines.append(cur)
                cur=w
        if cur: lines.append(cur)
    else:
        lines=[msg]
    for ln in lines[:2]:
        lw=draw.textlength(ln,font=f5)
        draw.text((SIZE//2-lw//2,y),ln,font=f5,fill=(*txt,175))
        y+=44
    y += 6

    # Large diya center-bottom area
    _draw_diya_large(img, SIZE//2-200, y+30, 90)
    _draw_diya_large(img, SIZE//2,     y,    110)
    _draw_diya_large(img, SIZE//2+200, y+30, 90)

    _draw_footer_bar(draw, ac)
    return img

# ── CHRISTMAS ─────────────────────────────────────────────────────────────────
def _make_christmas(festival):
    c = THEME_COLORS["christmas"]
    ac, ac2, txt = c["accent"], c["accent2"], c["text"]

    img  = Image.new("RGB",(SIZE,SIZE),c["bg"])
    img  = _radial_glow(img, SIZE//2, SIZE//2, 580, (10,60,10), 50)
    img  = _radial_glow(img, SIZE//2, 100, 300, ac, 25)
    draw = ImageDraw.Draw(img,"RGBA")

    # Snowflake pattern background
    random.seed(2)
    for _ in range(18):
        sx,sy = random.randint(50,SIZE-50),random.randint(50,SIZE-50)
        _draw_snowflake_lg(draw,sx,sy,random.randint(16,36),(180,220,255))

    _border(draw, ac, ac2)
    logo = _load_logo(190,58)
    y = _draw_top_header(img, draw, logo, ac)
    y += 14

    f1 = _font(48, False)
    t1 = "Wishing You A"
    w1 = draw.textlength(t1,font=f1)
    draw.text((SIZE//2-w1//2,y),t1,font=f1,fill=(*txt,180)); y+=64

    f2 = _font(130, True)
    t2 = "Merry"
    w2 = draw.textlength(t2,font=f2)
    draw.text((SIZE//2-w2//2,y),t2,font=f2,fill=WHITE); y+=140

    f3 = _font(130, True)
    t3 = "Christmas"
    w3 = draw.textlength(t3,font=f3)
    for ox,oy in [(4,4),(-4,-4)]:
        draw.text((SIZE//2-w3//2+ox,y+oy),t3,font=f3,fill=(*ac,50))
    draw.text((SIZE//2-w3//2,y),t3,font=f3,fill=ac); y+=144

    draw.rectangle([SIZE//2-200,y,SIZE//2+200,y+4],fill=(*ac2,200)); y+=22

    f4 = _font(34,False)
    sub=festival.get("sub","Merry Christmas")
    sw=draw.textlength(sub,font=f4)
    _draw_star5(draw,SIZE//2-sw//2-28,y+17,13,ac2)
    _draw_star5(draw,SIZE//2+sw//2+28,y+17,13,ac2)
    draw.text((SIZE//2-sw//2,y),sub,font=f4,fill=(*ac2,230)); y+=56

    f5=_font(30,False)
    msg=festival.get("msg","")
    mw=draw.textlength(msg,font=f5)
    lines=[msg] if mw<=SIZE-120 else []
    if not lines:
        words=msg.split(); cur=""
        for w in words:
            test=(cur+" "+w).strip()
            if draw.textlength(test,font=f5)<=SIZE-120: cur=test
            else:
                if cur: lines.append(cur); cur=w
        if cur: lines.append(cur)
    for ln in lines[:2]:
        lw=draw.textlength(ln,font=f5)
        draw.text((SIZE//2-lw//2,y),ln,font=f5,fill=(*txt,175)); y+=44
    y+=10

    # Big snowflake trio
    _draw_snowflake_lg(draw,SIZE//2-180,y+30,52,(200,230,255))
    _draw_snowflake_lg(draw,SIZE//2,    y,   64,(220,240,255))
    _draw_snowflake_lg(draw,SIZE//2+180,y+30,52,(200,230,255))

    _draw_footer_bar(draw, ac)
    return img

# ── NEW YEAR ──────────────────────────────────────────────────────────────────
def _make_newyear(festival):
    c = THEME_COLORS["newyear"]
    ac, ac2, txt = c["accent"], c["accent2"], c["text"]

    img  = Image.new("RGB",(SIZE,SIZE),c["bg"])
    img  = _radial_glow(img,SIZE//2,SIZE//2,600,(60,30,120),55)
    img  = _radial_glow(img,100,100,300,ac,30)
    img  = _radial_glow(img,SIZE-100,SIZE-100,300,ac2,30)
    draw = ImageDraw.Draw(img,"RGBA")

    # Firework bursts
    for cx,cy,col in [(160,180,ac),(900,160,ac2),(80,620,ac),(960,560,ac2),
                      (200,880,ac),(850,840,ac2)]:
        for i in range(12):
            ang=math.radians(360/12*i)
            ex=cx+int(55*math.cos(ang)); ey=cy+int(55*math.sin(ang))
            draw.line([(cx,cy),(ex,ey)],fill=(*col,160),width=2)
            draw.ellipse([ex-4,ey-4,ex+4,ey+4],fill=col)

    random.seed(3)
    for _ in range(26):
        sx,sy=random.randint(50,SIZE-50),random.randint(50,SIZE-50)
        col=ac if random.random()>0.4 else ac2
        sz=random.randint(8,18)
        for ang in [0,45,90,135]:
            rad=math.radians(ang)
            draw.line([(sx+int(sz*math.cos(rad)),sy+int(sz*math.sin(rad))),
                       (sx-int(sz*math.cos(rad)),sy-int(sz*math.sin(rad)))],
                      fill=(*col,180),width=1)

    _border(draw,ac,ac2)
    logo=_load_logo(190,58)
    y=_draw_top_header(img,draw,logo,ac)
    y+=10

    f1=_font(46,False)
    t1="Cheers To A New Year!"
    w1=draw.textlength(t1,font=f1)
    draw.text((SIZE//2-w1//2,y),t1,font=f1,fill=(*txt,185)); y+=62

    # Year number big
    year_txt="2027"
    for fsz in [220,200,180]:
        f_yr=_font(fsz,True)
        yw=draw.textlength(year_txt,font=f_yr)
        if yw<=SIZE-80: break
    for ox,oy in [(5,5),(-5,-5)]:
        draw.text((SIZE//2-yw//2+ox,y+oy),year_txt,font=f_yr,fill=(*ac2,45))
    draw.text((SIZE//2-yw//2,y),year_txt,font=f_yr,fill=ac); y+=fsz+16

    draw.rectangle([SIZE//2-220,y,SIZE//2+220,y+4],fill=(*ac2,200)); y+=22

    f4=_font(34,False)
    sub=festival.get("sub","Happy New Year 2027")
    sw=draw.textlength(sub,font=f4)
    _draw_star5(draw,SIZE//2-sw//2-28,y+17,13,ac2)
    _draw_star5(draw,SIZE//2+sw//2+28,y+17,13,ac2)
    draw.text((SIZE//2-sw//2,y),sub,font=f4,fill=(*ac2,230)); y+=56

    f5=_font(30,False)
    msg=festival.get("msg","")
    mw=draw.textlength(msg,font=f5)
    lines=[msg] if mw<=SIZE-120 else []
    if not lines:
        words=msg.split(); cur=""
        for w in words:
            test=(cur+" "+w).strip()
            if draw.textlength(test,font=f5)<=SIZE-120: cur=test
            else:
                if cur: lines.append(cur); cur=w
        if cur: lines.append(cur)
    for ln in lines[:2]:
        lw=draw.textlength(ln,font=f5)
        draw.text((SIZE//2-lw//2,y),ln,font=f5,fill=(*txt,175)); y+=44

    _draw_footer_bar(draw,ac)
    return img

# ── HOLI ─────────────────────────────────────────────────────────────────────
def _make_holi(festival):
    c = THEME_COLORS["holi"]
    ac, ac2, txt = c["accent"], c["accent2"], c["text"]
    colors_splash=[(255,80,120),(80,200,255),(255,200,0),(100,255,180),(200,100,255),(255,140,0)]

    img=Image.new("RGB",(SIZE,SIZE),(15,5,35))
    draw=ImageDraw.Draw(img,"RGBA")

    # Colour splash circles
    random.seed(4)
    for _ in range(45):
        sx=random.randint(0,SIZE); sy=random.randint(0,SIZE)
        sr=random.randint(30,120)
        col=random.choice(colors_splash)
        draw.ellipse([sx-sr,sy-sr,sx+sr,sy+sr],fill=(*col,random.randint(30,70)))

    img=_radial_glow(img,SIZE//2,SIZE//2,500,(20,5,50),80)
    draw=ImageDraw.Draw(img,"RGBA")
    _border(draw,ac,ac2)
    logo=_load_logo(190,58)
    y=_draw_top_header(img,draw,logo,ac)
    y+=10

    f1=_font(46,False)
    t1="Wishing You A"
    w1=draw.textlength(t1,font=f1)
    draw.text((SIZE//2-w1//2,y),t1,font=f1,fill=(*WHITE,180)); y+=62

    f2=_font(130,True)
    t2="Happy"
    w2=draw.textlength(t2,font=f2)
    draw.text((SIZE//2-w2//2,y),t2,font=f2,fill=WHITE); y+=140

    f3=_font(130,True)
    t3="Holi!"
    w3=draw.textlength(t3,font=f3)
    for ox,col in [(-4,colors_splash[0]),(4,colors_splash[1])]:
        draw.text((SIZE//2-w3//2+ox,y+4),t3,font=f3,fill=(*col,70))
    draw.text((SIZE//2-w3//2,y),t3,font=f3,fill=ac); y+=144

    draw.rectangle([SIZE//2-200,y,SIZE//2+200,y+4],fill=(*ac2,200)); y+=22

    f4=_font(34,False)
    sub=festival.get("sub","Festival of Colours")
    sw=draw.textlength(sub,font=f4)
    _draw_star5(draw,SIZE//2-sw//2-28,y+17,13,ac2)
    _draw_star5(draw,SIZE//2+sw//2+28,y+17,13,ac2)
    draw.text((SIZE//2-sw//2,y),sub,font=f4,fill=(*ac2,230)); y+=56

    f5=_font(30,False)
    msg=festival.get("msg","")
    mw=draw.textlength(msg,font=f5)
    lines=[msg] if mw<=SIZE-120 else []
    if not lines:
        words=msg.split(); cur=""
        for w in words:
            test=(cur+" "+w).strip()
            if draw.textlength(test,font=f5)<=SIZE-120: cur=test
            else:
                if cur: lines.append(cur); cur=w
        if cur: lines.append(cur)
    for ln in lines[:2]:
        lw=draw.textlength(ln,font=f5)
        draw.text((SIZE//2-lw//2,y),ln,font=f5,fill=(*WHITE,175)); y+=44
    y+=10

    # Coloured dot row
    for i,col in enumerate(colors_splash*2):
        dx = SIZE//2-150+i*22
        if dx>SIZE//2+150: break
        draw.ellipse([dx-9,y-9,dx+9,y+9],fill=(*col,220))

    _draw_footer_bar(draw,ac)
    return img

# ── Generic fallback ──────────────────────────────────────────────────────────
def _make_generic(festival):
    theme=festival.get("theme","diwali")
    c=THEME_COLORS.get(theme,THEME_COLORS["diwali"])
    ac,ac2,txt=c["accent"],c["accent2"],c["text"]

    img=Image.new("RGB",(SIZE,SIZE),c["bg"])
    img=_radial_glow(img,SIZE//2,SIZE//2,600,ac2,45)
    draw=ImageDraw.Draw(img,"RGBA")

    random.seed(5)
    for _ in range(24):
        sx,sy=random.randint(50,SIZE-50),random.randint(50,SIZE-50)
        col=ac if random.random()>0.4 else ac2
        sz=random.randint(8,20)
        for ang in [0,45,90,135]:
            rad=math.radians(ang)
            draw.line([(sx+int(sz*math.cos(rad)),sy+int(sz*math.sin(rad))),
                       (sx-int(sz*math.cos(rad)),sy-int(sz*math.sin(rad)))],
                      fill=(*col,180),width=1)

    _border(draw,ac,ac2)
    logo=_load_logo(190,58)
    y=_draw_top_header(img,draw,logo,ac)
    y+=14

    f1=_font(46,False)
    t1="Wishing You A"
    w1=draw.textlength(t1,font=f1)
    draw.text((SIZE//2-w1//2,y),t1,font=f1,fill=(*txt,180)); y+=62

    name=festival.get("name","").upper()
    for fsz in [144,120,100,86]:
        f2=_font(fsz,True)
        nw=draw.textlength(name,font=f2)
        if nw<=SIZE-100: break
    for ox,oy in [(4,4),(-4,-4)]:
        draw.text((SIZE//2-nw//2+ox,y+oy),name,font=f2,fill=(*ac2,55))
    draw.text((SIZE//2-nw//2,y),name,font=f2,fill=ac); y+=fsz+18

    draw.rectangle([SIZE//2-200,y,SIZE//2+200,y+4],fill=(*ac2,200)); y+=22

    f4=_font(34,False)
    sub=festival.get("sub","")
    sw=draw.textlength(sub,font=f4)
    _draw_star5(draw,SIZE//2-sw//2-28,y+17,13,ac2)
    _draw_star5(draw,SIZE//2+sw//2+28,y+17,13,ac2)
    draw.text((SIZE//2-sw//2,y),sub,font=f4,fill=(*ac2,230)); y+=56

    f5=_font(30,False)
    msg=festival.get("msg","")
    mw=draw.textlength(msg,font=f5)
    lines=[msg] if mw<=SIZE-120 else []
    if not lines:
        words=msg.split(); cur=""
        for w in words:
            test=(cur+" "+w).strip()
            if draw.textlength(test,font=f5)<=SIZE-120: cur=test
            else:
                if cur: lines.append(cur); cur=w
        if cur: lines.append(cur)
    for ln in lines[:2]:
        lw=draw.textlength(ln,font=f5)
        draw.text((SIZE//2-lw//2,y),ln,font=f5,fill=(*txt,175)); y+=44

    _draw_footer_bar(draw,ac)
    return img

# ── Public API ────────────────────────────────────────────────────────────────
_THEME_RENDERERS = {
    "diwali":    _make_diwali,
    "christmas": _make_christmas,
    "newyear":   _make_newyear,
    "holi":      _make_holi,
}

def generate_festival_post(festival: dict) -> bytes:
    theme    = festival.get("theme", "diwali")
    renderer = _THEME_RENDERERS.get(theme, _make_generic)
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
