"""
Swiss Typography Post — "BE SEEN. BE REMEMBERED. BE THE BRAND."
No photography. Pure geometry + type on a strict grid.
1080x1350px, 80px safe margins.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 80

# Brand palette
NAVY        = (  6,   8,  22)
DARK        = ( 10,  13,  34)
BLUE_DARK   = (  0,  36, 130)
BLUE_BRIGHT = (  1, 146, 239)
ORANGE      = (234, 110,  12)
WHITE       = (255, 255, 255)
OFF_WHITE   = (240, 244, 255)
MUTED       = (140, 165, 220)
GRID_LINE   = ( 22,  28,  62)

BRAND_WEB   = "davidwebsolution.com"
BRAND_PHONE = "+91 82854 23939"
BRAND_TAG   = "@davidwebsolution"

HEADLINE = ["BE SEEN.", "BE REMEMBERED.", "BE THE BRAND."]
TAGLINE  = "Your digital presence — designed to dominate."
PILLARS  = ["Web Design", "SEO & Rankings", "AI Video Ads", "eCommerce"]
CTA      = "START YOUR PROJECT  →"


def _font(size, bold=True):
    candidates = (
        ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf",
         "C:/Windows/Fonts/seguisb.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
        if bold else
        ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf",
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
    logo.thumbnail((200, 60), Image.LANCZOS)
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


def build_swiss():
    img  = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # ── Background: vertical gradient (NAVY -> DARK) ───────────────────────────
    for i in range(H):
        t = i / (H-1)
        c = tuple(int(NAVY[j] + t*(DARK[j]-NAVY[j])) for j in range(3))
        draw.line([(0,i),(W,i)], fill=c)

    # ── Grid lines (subtle Swiss discipline) ──────────────────────────────────
    # 3 vertical grid lines (column guides)
    col3 = W // 3
    for col in range(1, 3):
        draw.line([(col*col3, 0),(col*col3, H)], fill=GRID_LINE, width=1)
    # Horizontal baseline rules
    for row_y in [MARGIN, H//3, 2*H//3, H-MARGIN]:
        draw.line([(MARGIN, row_y),(W-MARGIN, row_y)], fill=GRID_LINE, width=1)

    # ── Left accent bar (full height, 8px) ─────────────────────────────────────
    draw.rectangle([0, 0, 8, H], fill=BLUE_BRIGHT)

    # ── Orange diagonal slash (large, decorative geometry) ────────────────────
    # A thick diagonal rule from top-right quadrant to mid-right — Swiss flair
    slash_pts = [(W-MARGIN-40, MARGIN+40), (W-MARGIN, MARGIN+40),
                 (W-MARGIN, MARGIN+52), (W-MARGIN-40, MARGIN+52)]
    draw.polygon([(W-240, MARGIN), (W-MARGIN, MARGIN+200),
                  (W-MARGIN, MARGIN+220), (W-260, MARGIN)], fill=ORANGE)

    # ── Header: logo + @handle ─────────────────────────────────────────────────
    HH = 88
    draw.rectangle([0, 0, W, HH], fill=DARK)
    draw.rectangle([0, HH-3, W, HH], fill=BLUE_BRIGHT)
    img  = _paste_logo(img, MARGIN, (HH-50)//2, white=True)
    draw = ImageDraw.Draw(img)
    tf = _font(20, False)
    tw = draw.textbbox((0,0), BRAND_TAG, font=tf)[2]
    draw.text((W-MARGIN-tw, (HH-22)//2), BRAND_TAG, font=tf, fill=MUTED)

    # ── Category label ─────────────────────────────────────────────────────────
    y = HH + 68
    lf = _font(16, False)
    lt = "DAVID WEB SOLUTION  //  FULL-SERVICE DIGITAL AGENCY"
    draw.text((MARGIN, y), lt, font=lf, fill=BLUE_BRIGHT)
    y += 28
    # Thin rule under label
    draw.rectangle([MARGIN, y, W-MARGIN, y+2], fill=BLUE_BRIGHT)
    y += 22

    # ── Massive headline: Swiss style, flush left, different weights/colors ─────
    # Line 1: WHITE, enormous
    fh1 = _font(116)
    draw.text((MARGIN, y), HEADLINE[0], font=fh1, fill=WHITE)
    y += draw.textbbox((0,0), HEADLINE[0], font=fh1)[3] - 8

    # Line 2: ORANGE
    fh2 = _font(90)
    draw.text((MARGIN, y), HEADLINE[1], font=fh2, fill=ORANGE)
    y += draw.textbbox((0,0), HEADLINE[1], font=fh2)[3] - 4

    # Line 3: BLUE_BRIGHT (outlined style: draw text twice for weight effect)
    fh3 = _font(116)
    draw.text((MARGIN+3, y+3), HEADLINE[2], font=fh3, fill=BLUE_DARK)
    draw.text((MARGIN, y), HEADLINE[2], font=fh3, fill=BLUE_BRIGHT)
    y += draw.textbbox((0,0), HEADLINE[2], font=fh3)[3] + 28

    # ── Thick separator rule (Swiss trademark) ─────────────────────────────────
    draw.rectangle([MARGIN, y, MARGIN+200, y+6], fill=WHITE)
    draw.rectangle([MARGIN+208, y, MARGIN+260, y+6], fill=ORANGE)
    y += 28

    # ── Tagline ────────────────────────────────────────────────────────────────
    tl_f = _font(30, False)
    draw.text((MARGIN, y), TAGLINE, font=tl_f, fill=OFF_WHITE)
    y += draw.textbbox((0,0), TAGLINE, font=tl_f)[3] + 36

    # ── 4 Service pills in a 2x2 grid ─────────────────────────────────────────
    pf    = _font(22)
    pill_h= 50
    gap   = 16
    col_w = (W - MARGIN*2 - gap) // 2
    for idx, svc in enumerate(PILLARS):
        cx = MARGIN + (idx % 2) * (col_w + gap)
        cy = y      + (idx // 2) * (pill_h + gap)
        bg = BLUE_DARK if idx % 2 == 0 else (14, 18, 52)
        lc = BLUE_BRIGHT if idx % 2 == 0 else ORANGE
        draw.rounded_rectangle([cx, cy, cx+col_w, cy+pill_h], radius=8, fill=bg)
        draw.rounded_rectangle([cx, cy, cx+8, cy+pill_h], radius=4, fill=lc)
        tw_ = draw.textbbox((0,0), svc, font=pf)[2]
        th_ = draw.textbbox((0,0), svc, font=pf)[3]
        draw.text((cx+24, cy+(pill_h-th_)//2), svc, font=pf, fill=WHITE)
    y += 2*(pill_h+gap) + 36

    # ── CTA block ──────────────────────────────────────────────────────────────
    # Full-width orange bar
    cf    = _font(28)
    cta_h = 70
    # Draw full-width orange button
    draw.rounded_rectangle([MARGIN, y, W-MARGIN, y+cta_h], radius=8, fill=ORANGE)
    # Shadow layer
    for i in range(6):
        draw.rounded_rectangle([MARGIN+i, y+cta_h, W-MARGIN-i, y+cta_h+6-i],
                                radius=4, fill=tuple(max(0,v-15) for v in ORANGE))
    cw_ = draw.textbbox((0,0), CTA, font=cf)[2]
    ch_ = draw.textbbox((0,0), CTA, font=cf)[3]
    draw.text(((W-cw_)//2, y+(cta_h-ch_)//2-1), CTA, font=cf, fill=WHITE)
    y += cta_h + 20

    # Website + phone
    wf   = _font(20, False)
    info = f"{BRAND_WEB}  |  {BRAND_PHONE}"
    iw   = draw.textbbox((0,0), info, font=wf)[2]
    draw.text(((W-iw)//2, y), info, font=wf, fill=MUTED)

    # ── Bottom glow line ───────────────────────────────────────────────────────
    draw.rectangle([0, H-5, W, H], fill=BLUE_BRIGHT)

    return img


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "posts")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "post_swiss_typography.png")
    print("[DWS] Building Swiss Typography Post...")
    img = build_swiss()
    img.save(out, format="PNG", optimize=True)
    print(f"[DWS] Done: {out}  {img.size[0]}x{img.size[1]}")
