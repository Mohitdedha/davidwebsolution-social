"""
Premium Instagram Post — SEO Topic
"Is Your Business Invisible on Google?"
Google SERP mockup visual, dark editorial style.
1080x1350px
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350

# Deep dark palette — premium editorial
BG          = (  7,   8,  16)
BG2         = ( 11,  12,  24)
CARD_BG     = ( 16,  18,  36)
CARD_BORDER = ( 32,  36,  72)
BLUE        = (  1, 146, 239)
BLUE_DARK   = (  0,  46, 160)
ORANGE      = (234, 110,  12)
WHITE       = (255, 255, 255)
OFF_WHITE   = (230, 235, 255)
MUTED       = (120, 140, 195)
DIMMED      = ( 70,  82, 130)
GREEN       = ( 52, 199, 110)
RED_DIM     = (180,  50,  50)
GOOGLE_BLUE = ( 26, 115, 232)
GOOGLE_GRN  = ( 52, 168,  83)
GOOGLE_YEL  = (251, 188,   4)
GOOGLE_RED  = (234,  67,  53)
DIVIDER     = ( 26,  30,  58)

BRAND_WEB   = "davidwebsolution.com"
BRAND_PHONE = "+91 82854 23939"
BRAND_TAG   = "@davidwebsolution"


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

def _rr(draw, xy, r, fill=None, outline=None, ow=2):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=ow)

def _alpha_rect(img, x0, y0, x1, y1, color, alpha):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(ov).rectangle([x0,y0,x1,y1], fill=(*color,alpha))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

def _gv(img, x0, y0, x1, y1, c1, c2):
    draw = ImageDraw.Draw(img)
    n = y1 - y0
    for i in range(n):
        t = i/max(n-1,1)
        c = tuple(int(c1[j]+t*(c2[j]-c1[j])) for j in range(3))
        draw.line([(x0,y0+i),(x1,y0+i)], fill=c)


def _draw_google_dots(draw, x, y, r=9, gap=6):
    """Draw 4 Google logo colored dots."""
    cols = [GOOGLE_BLUE, GOOGLE_RED, GOOGLE_YEL, GOOGLE_GRN]
    for i, c in enumerate(cols):
        cx = x + i*(r*2+gap)
        draw.ellipse([cx, y, cx+r*2, y+r*2], fill=c)


def _draw_serp_card(img, x, y, w, h):
    """Draw a Google SERP mockup card."""
    draw = ImageDraw.Draw(img)
    PAD = 28

    # Card background
    _rr(draw, [x, y, x+w, y+h], 20, CARD_BG, CARD_BORDER, 1)

    cy = y + PAD

    # Google logo dots + "Google" text
    _draw_google_dots(draw, x+PAD, cy+2, r=7, gap=4)
    gf = _font(22, False)
    draw.text((x+PAD+7*2*4+4*4+12, cy), "Google", font=gf, fill=MUTED)
    cy += 28

    # Search bar
    bar_h = 46
    _rr(draw, [x+PAD, cy, x+w-PAD, cy+bar_h], 23,
        (22,24,50), CARD_BORDER, 1)
    sf = _font(20, False)
    query = "web design agency UK"
    draw.text((x+PAD+20, cy+12), query, font=sf, fill=OFF_WHITE)
    # Search icon (magnifier sketch)
    ix = x+w-PAD-36
    iy = cy+12
    draw.ellipse([ix, iy, ix+18, iy+18], outline=MUTED, width=2)
    draw.line([(ix+16, iy+16),(ix+24, iy+24)], fill=MUTED, width=2)
    cy += bar_h + 20

    # Thin separator
    draw.rectangle([x+PAD, cy, x+w-PAD, cy+1], fill=DIVIDER)
    cy += 14

    # Result count line
    rcf = _font(16, False)
    draw.text((x+PAD, cy), "About 482,000,000 results (0.43 seconds)", font=rcf, fill=DIMMED)
    cy += 26

    # ── RESULT 1: Sponsored / Competitor (dimmed) ─────────────────────────────
    # "Sponsored" badge
    spf = _font(14, False)
    _rr(draw, [x+PAD, cy, x+PAD+84, cy+20], 4, None, DIMMED, 1)
    spw = draw.textbbox((0,0),"Sponsored",font=spf)[2]
    draw.text((x+PAD+(84-spw)//2, cy+3), "Sponsored", font=spf, fill=DIMMED)
    cy += 24

    comp_url_f = _font(16, False)
    comp_ttl_f = _font(20, False)
    draw.text((x+PAD, cy), "competitor-agency.co.uk", font=comp_url_f, fill=DIMMED)
    cy += 22
    draw.text((x+PAD, cy), "Best Web Design Agency UK | Low Price", font=comp_ttl_f, fill=DIMMED)
    cy += 24
    draw.text((x+PAD, cy), "Award-winning web design. Get a free quote today...", font=spf, fill=DIMMED)
    cy += 28

    draw.rectangle([x+PAD, cy, x+w-PAD, cy+1], fill=DIVIDER)
    cy += 14

    # ── RESULT 2: DWS — HIGHLIGHTED (THE #1 ORGANIC) ─────────────────────────
    # Highlight box around this result
    res_h = 110
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(ov).rounded_rectangle(
        [x+PAD-10, cy-8, x+w-PAD+10, cy+res_h],
        radius=12, fill=(*BLUE_DARK, 80), outline=(*BLUE, 180), width=2)
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    draw = ImageDraw.Draw(img)

    # "#1" badge
    bf = _font(16)
    _rr(draw, [x+PAD, cy, x+PAD+40, cy+22], 11, GREEN)
    bw = draw.textbbox((0,0),"#1",font=bf)[2]
    draw.text((x+PAD+(40-bw)//2, cy+3), "#1", font=bf, fill=WHITE)

    url_f   = _font(17, False)
    title_f = _font(22)
    desc_f  = _font(17, False)

    draw.text((x+PAD+50, cy+2), BRAND_WEB, font=url_f, fill=GREEN)
    cy += 28
    draw.text((x+PAD, cy), "David Web Solution | Web Design & SEO Agency", font=title_f, fill=BLUE)
    cy += 28
    draw.text((x+PAD, cy), "Custom websites, SEO & eCommerce for UK & US", font=desc_f, fill=OFF_WHITE)
    cy += 22
    draw.text((x+PAD, cy), "businesses — built to convert visitors into clients.", font=desc_f, fill=MUTED)
    cy += res_h - 90 + 8

    # ── RESULT 3: Another competitor (dimmed) ─────────────────────────────────
    draw.rectangle([x+PAD, cy, x+w-PAD, cy+1], fill=DIVIDER)
    cy += 12

    draw.text((x+PAD, cy), "anotherwebstudio.com", font=comp_url_f, fill=DIMMED)
    cy += 22
    draw.text((x+PAD, cy), "Web Design Services — Professional & Affordable", font=comp_ttl_f, fill=DIMMED)
    cy += 24
    draw.text((x+PAD, cy), "Modern web design services for all businesses...", font=spf, fill=DIMMED)

    return img


def build_post():
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    _gv(img, 0, 0, W, H, BG, BG2)

    PAD = 60

    # ── HEADER ────────────────────────────────────────────────────────────────
    HH = 88
    draw.rectangle([0, 0, W, HH], fill=(8, 9, 20))
    draw.rectangle([0, HH-3, W, HH], fill=ORANGE)
    img  = _paste_logo(img, PAD, (HH-52)//2, white=True)
    draw = ImageDraw.Draw(img)
    tf = _font(20, False)
    tw = draw.textbbox((0,0), BRAND_TAG, font=tf)[2]
    draw.text((W-PAD-tw, (HH-22)//2), BRAND_TAG, font=tf, fill=MUTED)

    # ── LEFT ACCENT BAR (orange, not blue) ───────────────────────────────────
    draw.rectangle([0, 0, 5, H], fill=ORANGE)

    # ── CATEGORY LABEL ────────────────────────────────────────────────────────
    y = HH + 44
    cf = _font(16, False)
    ct = "SEO & GOOGLE RANKING"
    draw.text((PAD, y), ct, font=cf, fill=ORANGE)
    cw = draw.textbbox((0,0), ct, font=cf)[2]
    y += 24
    draw.rectangle([PAD, y, PAD+cw, y+2], fill=WHITE)
    y += 16

    # ── HEADLINE ──────────────────────────────────────────────────────────────
    fh1 = _font(82)
    fh2 = _font(88)

    lines = [
        ("IS YOUR BUSINESS", fh1, WHITE),
        ("INVISIBLE", fh2, ORANGE),
        ("ON GOOGLE?", fh1, BLUE),       # only headline uses blue
    ]
    for txt, fnt, col in lines:
        draw.text((PAD, y), txt, font=fnt, fill=col)
        y += draw.textbbox((0,0), txt, font=fnt)[3] + 2
    y += 10

    # Accent rule: orange + white
    draw.rectangle([PAD, y, PAD+100, y+4], fill=ORANGE)
    draw.rectangle([PAD+108, y, PAD+148, y+4], fill=WHITE)
    y += 18

    # Tagline
    tl_f = _font(25, False)
    tl_t = "93% of clicks go to Page 1 results.\nIf you're not there, you don't exist."
    for tl in tl_t.split("\n"):
        draw.text((PAD, y), tl, font=tl_f, fill=MUTED)
        y += draw.textbbox((0,0), tl, font=tl_f)[3] + 4
    y += 20

    # ── GOOGLE SERP MOCKUP CARD ───────────────────────────────────────────────
    CARD_X = PAD
    CARD_W = W - PAD*2
    CARD_H = 420
    img  = _draw_serp_card(img, CARD_X, y, CARD_W, CARD_H)
    draw = ImageDraw.Draw(img)
    y   += CARD_H + 28

    # ── STATS STRIP ───────────────────────────────────────────────────────────
    ST_H = 96
    draw.rectangle([0, y, W, y+ST_H], fill=CARD_BG)
    draw.rectangle([0, y, W, y+2], fill=DIVIDER)
    draw.rectangle([0, y+ST_H-2, W, y+ST_H], fill=DIVIDER)

    stats = [("93%","Clicks on Page 1"), ("75%","Never Scroll Past It"), ("3x","More Leads for #1")]
    cw2   = W // 3
    sf2   = _font(38)
    lf2   = _font(17, False)
    # Colors: orange, white, blue — balanced, not all-blue
    stat_cols = [ORANGE, WHITE, BLUE]
    for idx, (val, lbl) in enumerate(stats):
        cx = idx*cw2 + cw2//2
        vw = draw.textbbox((0,0), val, font=sf2)[2]
        lw = draw.textbbox((0,0), lbl, font=lf2)[2]
        draw.text((cx-vw//2, y+10), val, font=sf2, fill=stat_cols[idx])
        draw.text((cx-lw//2, y+58), lbl, font=lf2, fill=MUTED)
        if idx < 2:
            draw.rectangle([idx*cw2+cw2-1, y+16, idx*cw2+cw2+1, y+ST_H-16], fill=DIVIDER)
    y += ST_H + 24

    # ── CTA BUTTON ────────────────────────────────────────────────────────────
    cf3   = _font(28)
    cta   = "GET ON PAGE 1  —  FREE SEO AUDIT"
    cta_h = 68
    cta_w = W - PAD*2
    _rr(draw, [PAD, y, PAD+cta_w, y+cta_h], 34, ORANGE)
    tw3 = draw.textbbox((0,0), cta, font=cf3)[2]
    th3 = draw.textbbox((0,0), cta, font=cf3)[3]
    draw.text((PAD+(cta_w-tw3)//2, y+(cta_h-th3)//2-1), cta, font=cf3, fill=WHITE)
    y += cta_h + 20

    # ── SERVICES ROW ──────────────────────────────────────────────────────────
    svcs = ["Website Design", "SEO & Ranking", "AI Video Ads", "eCommerce"]
    sw_f = _font(20)
    cw3  = W // 4
    SVC_H = 52
    draw.rectangle([0, y, W, y+SVC_H], fill=CARD_BG)
    draw.rectangle([0, y, W, y+2], fill=DIVIDER)
    draw.rectangle([0, y+SVC_H-2, W, y+SVC_H], fill=DIVIDER)
    for si, svc in enumerate(svcs):
        sx  = si*cw3
        sc  = BLUE if si%2==0 else ORANGE
        stw = draw.textbbox((0,0), svc, font=sw_f)[2]
        draw.text((sx+(cw3-stw)//2, y+(SVC_H-24)//2), svc, font=sw_f, fill=sc)
        if si < 3:
            draw.rectangle([sx+cw3-1, y+10, sx+cw3+1, y+SVC_H-10], fill=DIVIDER)
    y += SVC_H + 16

    # ── FOOTER ────────────────────────────────────────────────────────────────
    # Fill remaining space to H with dark footer
    FOOT_Y = y
    draw.rectangle([0, FOOT_Y, W, H], fill=(6, 7, 16))
    draw.rectangle([0, FOOT_Y, W, FOOT_Y+2], fill=DIVIDER)

    # Brand name large
    bn_f = _font(26)
    bn_t = "DAVID WEB SOLUTION"
    bnw  = draw.textbbox((0,0), bn_t, font=bn_f)[2]
    bnh  = draw.textbbox((0,0), bn_t, font=bn_f)[3]
    foot_center = FOOT_Y + (H - FOOT_Y)//2
    draw.text(((W-bnw)//2, foot_center - bnh - 10), bn_t, font=bn_f, fill=WHITE)

    wf   = _font(19, False)
    info = f"{BRAND_WEB}   |   {BRAND_PHONE}"
    iw   = draw.textbbox((0,0), info, font=wf)[2]
    draw.text(((W-iw)//2, foot_center + 6), info, font=wf, fill=DIMMED)

    # Bottom glow
    draw.rectangle([0, H-4, W, H], fill=ORANGE)
    return img


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "posts")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "post_premium_seo.png")
    print("[DWS] Building Premium SEO post...")
    img = build_post()
    img.save(out, format="PNG", optimize=True)
    print(f"[DWS] Done: {out}  {img.size[0]}x{img.size[1]}")
