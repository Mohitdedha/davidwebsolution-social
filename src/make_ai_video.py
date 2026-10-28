"""
AI & Video Post — Clean split layout matching reference screenshot.
Light background, dark text, geometric robot on right card.
1080x1350px
"""
import os, random
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350

# Light theme
BG          = (248, 250, 255)   # near white
CARD_BG     = (235, 240, 255)   # light blue-gray for right card
HDR_BG      = (  6,   8,  28)   # dark navy header
FTR_BG      = (  6,   8,  28)   # dark navy footer
TEXT_DARK   = ( 12,  14,  30)   # almost black
TEXT_MED    = ( 80,  90, 130)   # medium gray
TEXT_LIGHT  = (140, 155, 200)
BLUE        = (  0,  82, 204)   # primary blue
BLUE_BRIGHT = (  1, 146, 239)
ORANGE      = (234, 110,  12)
PURPLE      = ( 82,  54, 180)
WHITE       = (255, 255, 255)
DIVIDER     = (210, 218, 240)
ROBOT_BG    = (220, 228, 250)

BRAND_WEB   = "davidwebsolution.com"
BRAND_PHONE = "+91 82854 23939"
BRAND_TAG   = "@davidwebsolution"

CATEGORY   = "AI & VIDEO"
HEADLINE   = ["Want your", "ads to", "really pop\non Meta?"]
TAGLINE    = "We Help To Grow Your Business"
SECTION    = "What We Do"
BULLETS = [
    ("Recent data shows AI-generated UGC ads", "outperform traditional video by 3x."),
    ("At David Web Solution, we blend AI tools", "with proven brand strategy."),
    ("Cost Savings: Cut production time from", "weeks to just 48 hours."),
    ("Proven Results: UK ecom client saw", "2-4x ROAS in under 30 days."),
]
CTA = "Book a free call  →  DM"


def _font(size, bold=True):
    candidates = (
        ["C:/Windows/Fonts/arialbd.ttf","C:/Windows/Fonts/calibrib.ttf",
         "C:/Windows/Fonts/seguisb.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
        if bold else
        ["C:/Windows/Fonts/arial.ttf","C:/Windows/Fonts/calibri.ttf",
         "C:/Windows/Fonts/segoeui.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    )
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()


_LOGO_CACHE = None
def _load_logo():
    global _LOGO_CACHE
    if _LOGO_CACHE: return _LOGO_CACHE
    path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if not os.path.exists(path): return None
    logo = Image.open(path).convert("RGBA")
    px = logo.load()
    for y in range(logo.height):
        for x in range(logo.width):
            r, g, b, a = px[x, y]
            if r > 215 and g > 215 and b > 215:
                px[x, y] = (r, g, b, 0)
    bb = logo.getbbox()
    if bb: logo = logo.crop(bb)
    logo.thumbnail((190, 56), Image.LANCZOS)
    _LOGO_CACHE = logo
    return logo

def _paste_logo(img, x, y, white=True):
    logo = _load_logo()
    if not logo: return img
    if white:
        wl = Image.new("RGBA", logo.size, (0,0,0,0))
        src = logo.load(); dst = wl.load()
        for yy in range(logo.height):
            for xx in range(logo.width):
                r, g, b, a = src[xx, yy]
                if a > 10: dst[xx, yy] = (255, 255, 255, a)
        logo = wl
    base = img.convert("RGBA")
    base.paste(logo, (x, y), logo)
    return base.convert("RGB")


def _draw_robot(img, rx, ry, rw, rh):
    """Geometric robot illustration on light card."""
    draw = ImageDraw.Draw(img)
    cx = rx + rw // 2

    # Card bg already drawn
    # Outer glow rings
    cy_c = ry + rh // 2 - 20
    for rad, alpha in [(170, 30), (130, 50), (95, 70)]:
        ov = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(ov).ellipse(
            [cx-rad, cy_c-rad, cx+rad, cy_c+rad],
            outline=(*BLUE_BRIGHT, alpha), width=2)
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    draw = ImageDraw.Draw(img)

    # HEAD
    HW, HH2 = 148, 118
    hx = cx - HW//2
    hy = cy_c - 200
    # Head shape
    draw.rounded_rectangle([hx, hy, hx+HW, hy+HH2], radius=20,
                            fill=(  6,  8, 28), outline=BLUE_BRIGHT, width=3)
    # Antenna
    draw.line([(cx, hy),(cx, hy-32)], fill=BLUE_BRIGHT, width=4)
    draw.ellipse([cx-10, hy-44, cx+10, hy-24], fill=ORANGE)
    draw.ellipse([cx-5, hy-39, cx+5, hy-29], fill=WHITE)

    # Eyes
    EY = hy + 28
    for ex in [cx-36, cx+16]:
        draw.rounded_rectangle([ex, EY, ex+30, EY+26], radius=8, fill=(20,24,60))
        draw.rounded_rectangle([ex+4, EY+4, ex+26, EY+22], radius=6, fill=BLUE_BRIGHT)
        draw.ellipse([ex+9, EY+8, ex+21, EY+20], fill=WHITE)
        draw.ellipse([ex+12, EY+11, ex+18, EY+17], fill=(6,8,28))

    # Mouth bar
    MY = hy + 76
    for mi in range(8):
        sx = hx + 18 + mi*14
        c  = BLUE_BRIGHT if mi % 2 == 0 else (20, 24, 60)
        draw.rounded_rectangle([sx, MY, sx+10, MY+9], radius=3, fill=c)

    # Ear nodes
    draw.ellipse([hx-14, hy+38, hx+2, hy+54], fill=(20,24,60), outline=BLUE_BRIGHT, width=2)
    draw.ellipse([hx+HW-2, hy+38, hx+HW+14, hy+54], fill=(20,24,60), outline=BLUE_BRIGHT, width=2)

    # BODY
    BW, BH = 188, 150
    bx = cx - BW//2
    by = hy + HH2 + 10
    draw.rounded_rectangle([bx, by, bx+BW, by+BH], radius=18,
                            fill=(6,8,28), outline=BLUE_BRIGHT, width=2)
    # Chest panel
    draw.rounded_rectangle([bx+24, by+16, bx+BW-24, by+BH-16],
                            radius=10, fill=(16,20,56))
    # Power orb
    draw.ellipse([cx-16, by+28, cx+16, by+60], fill=(20,24,60), outline=ORANGE, width=3)
    draw.ellipse([cx-8, by+36, cx+8, by+52], fill=ORANGE)
    draw.line([(cx, by+28),(cx, by+37)], fill=WHITE, width=3)
    # Status bars
    for bi in range(3):
        bw3 = 36 + bi*14
        bby2 = by + BH - 36 + bi*9
        draw.rounded_rectangle([cx-bw3//2, bby2, cx+bw3//2, bby2+5],
                                radius=3, fill=(BLUE_BRIGHT if bi==2 else (30,50,120)))

    # Arms
    draw.rounded_rectangle([bx-42, by+18, bx+2, by+92], radius=12,
                            fill=(6,8,28), outline=BLUE_BRIGHT, width=1)
    draw.ellipse([bx-48, by+84, bx-16, by+110], fill=(16,20,56), outline=BLUE_BRIGHT, width=2)
    draw.rounded_rectangle([bx+BW-2, by+18, bx+BW+42, by+92], radius=12,
                            fill=(6,8,28), outline=BLUE_BRIGHT, width=1)
    draw.ellipse([bx+BW+16, by+84, bx+BW+48, by+110], fill=(16,20,56), outline=BLUE_BRIGHT, width=2)

    # Floating dots
    random.seed(7)
    for _ in range(16):
        px2 = rx + random.randint(8, rw-8)
        py2 = ry + random.randint(8, rh-8)
        pr2 = random.randint(2, 5)
        c   = random.choice([BLUE_BRIGHT, ORANGE, (100,130,220)])
        draw.ellipse([px2-pr2, py2-pr2, px2+pr2, py2+pr2], fill=c)

    # AI POWERED badge
    af  = _font(22)
    abt = "AI POWERED"
    aw  = draw.textbbox((0,0), abt, font=af)[2]
    badge_y = ry + rh - 54
    draw.rounded_rectangle([cx-aw//2-18, badge_y, cx+aw//2+18, badge_y+36],
                            radius=18, fill=ORANGE)
    draw.text((cx - aw//2, badge_y+6), abt, font=af, fill=WHITE)

    return img


def build_post():
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── HEADER ────────────────────────────────────────────────────────────────
    HH = 88
    draw.rectangle([0, 0, W, HH], fill=HDR_BG)
    img  = _paste_logo(img, 40, (HH-52)//2, white=True)
    draw = ImageDraw.Draw(img)

    # Social icons
    icon_f = _font(17)
    for ii, (lbl, col) in enumerate([("in", BLUE_BRIGHT),("ig", ORANGE),("f", WHITE)]):
        ix = W - 48 - ii*50
        iy = (HH-30)//2
        draw.ellipse([ix, iy, ix+30, iy+30], outline=col, width=2)
        tw = draw.textbbox((0,0), lbl, font=icon_f)[2]
        draw.text((ix+(30-tw)//2, iy+5), lbl, font=icon_f, fill=col)

    # ── BODY LAYOUT ───────────────────────────────────────────────────────────
    PAD   = 44
    BODY_Y = HH + 4
    # Right robot card
    CARD_X = 520
    CARD_Y = BODY_Y + 16
    CARD_W = W - CARD_X - 20
    CARD_H = 600

    draw.rounded_rectangle([CARD_X, CARD_Y, CARD_X+CARD_W, CARD_Y+CARD_H],
                            radius=28, fill=ROBOT_BG)
    img  = _draw_robot(img, CARD_X, CARD_Y, CARD_W, CARD_H)
    draw = ImageDraw.Draw(img)

    # ── LEFT TEXT ─────────────────────────────────────────────────────────────
    MAX_W = CARD_X - PAD - 16
    y = BODY_Y + 40

    # Category
    cf = _font(18, False)
    draw.text((PAD, y), CATEGORY, font=cf, fill=BLUE)
    cw = draw.textbbox((0,0), CATEGORY, font=cf)[2]
    y += draw.textbbox((0,0), CATEGORY, font=cf)[3] + 6
    draw.rectangle([PAD, y, PAD+cw, y+3], fill=ORANGE)
    y += 14

    # Headline
    fh_reg = _font(60)
    fh_big = _font(64)
    lines_info = [
        (HEADLINE[0], fh_reg, TEXT_DARK),
        (HEADLINE[1], fh_reg, TEXT_DARK),
        (HEADLINE[2].split("\n")[0], fh_big, PURPLE),
        (HEADLINE[2].split("\n")[1], fh_big, PURPLE),
    ]
    for txt, fnt, col in lines_info:
        draw.text((PAD, y), txt, font=fnt, fill=col)
        y += draw.textbbox((0,0), txt, font=fnt)[3] + 2
    y += 10

    # Tagline
    tl_f = _font(22, False)
    draw.text((PAD, y), TAGLINE, font=tl_f, fill=TEXT_MED)
    y += draw.textbbox((0,0), TAGLINE, font=tl_f)[3] + 8
    draw.rectangle([PAD, y, CARD_X-16, y+1], fill=DIVIDER)
    y += 14

    # Section heading
    sh_f = _font(28)
    draw.text((PAD, y), SECTION, font=sh_f, fill=TEXT_DARK)
    y += draw.textbbox((0,0), SECTION, font=sh_f)[3] + 8

    # Bullets
    num_f  = _font(26)
    bull_f = _font(20, False)
    for bi, (line1, line2) in enumerate(BULLETS):
        num = f"0{bi+1}"
        nc  = BLUE if bi % 2 == 0 else ORANGE
        draw.text((PAD, y+2), num, font=num_f, fill=nc)
        nw  = draw.textbbox((0,0), num, font=num_f)[2]
        tx  = PAD + nw + 12
        tw2 = MAX_W - nw - 12
        draw.text((tx, y+2),  line1, font=bull_f, fill=TEXT_DARK)
        lh1 = draw.textbbox((0,0), line1, font=bull_f)[3]
        draw.text((tx, y+2+lh1+2), line2, font=bull_f, fill=TEXT_MED)
        lh2 = draw.textbbox((0,0), line2, font=bull_f)[3]
        y  += max(lh1+lh2+10, 44) + 8

    y += 6

    # ── CTA BUTTON ────────────────────────────────────────────────────────────
    cf2   = _font(26)
    cta_h = 62
    BTN_W = CARD_X - PAD - 16
    draw.rounded_rectangle([PAD, y, PAD+BTN_W, y+cta_h], radius=31, fill=HDR_BG)
    tw3 = draw.textbbox((0,0), CTA, font=cf2)[2]
    th3 = draw.textbbox((0,0), CTA, font=cf2)[3]
    draw.text((PAD+(BTN_W-tw3)//2, y+(cta_h-th3)//2-1), CTA, font=cf2, fill=WHITE)
    y += cta_h + 12

    # Contact under button
    wf = _font(19, False)
    draw.text((PAD, y), BRAND_PHONE, font=wf, fill=TEXT_MED)
    draw.text((PAD + 220, y), BRAND_WEB, font=wf, fill=BLUE)

    # ── SERVICES STRIP ────────────────────────────────────────────────────────
    ST_Y = CARD_Y + CARD_H + 18
    ST_H = H - ST_Y - 74
    draw.rectangle([0, ST_Y, W, ST_Y+ST_H], fill=BG)
    draw.rectangle([0, ST_Y, W, ST_Y+2], fill=DIVIDER)
    svcs = ["Website Design", "SEO & Rankings", "AI Video Ads", "eCommerce"]
    cw2  = W // 4
    sf2  = _font(22)
    for si, svc in enumerate(svcs):
        sx  = si * cw2
        col = BLUE if si % 2 == 0 else PURPLE
        sw2 = draw.textbbox((0,0), svc, font=sf2)[2]
        draw.text((sx+(cw2-sw2)//2, ST_Y+(ST_H-28)//2), svc, font=sf2, fill=col)
        if si < 3:
            draw.rectangle([sx+cw2-1, ST_Y+10, sx+cw2+1, ST_Y+ST_H-10], fill=DIVIDER)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    FY = H - 68
    draw.rectangle([0, FY, W, H], fill=HDR_BG)
    draw.rectangle([0, FY, W, FY+2], fill=BLUE_BRIGHT)
    draw.rectangle([0, H-4, W, H], fill=ORANGE)
    inf  = _font(19, False)
    info = f"{BRAND_WEB}   |   {BRAND_PHONE}   |   {BRAND_TAG}"
    iw   = draw.textbbox((0,0), info, font=inf)[2]
    draw.text(((W-iw)//2, FY+20), info, font=inf, fill=TEXT_LIGHT)

    return img


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "posts")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "post_ai_video.png")
    print("[DWS] Building AI Video post v2...")
    img = build_post()
    img.save(out, format="PNG", optimize=True)
    print(f"[DWS] Done: {out}  {img.size[0]}x{img.size[1]}")
