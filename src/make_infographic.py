"""
Infographic Post — "5 Signs Your Website Is Costing You Customers"
Clean numbered list infographic, brand colors, icons from geometry.
1080x1350px
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350

BG          = (248, 250, 255)
HDR_BG      = (  6,   8,  28)
BLUE        = (  0,  36, 130)
BLUE_BRIGHT = (  1, 146, 239)
ORANGE      = (234, 110,  12)
PURPLE      = ( 70,  50, 170)
WHITE       = (255, 255, 255)
TEXT_DARK   = ( 12,  14,  30)
TEXT_MED    = ( 80,  90, 130)
DIVIDER     = (210, 218, 240)
GREEN       = ( 32, 180, 100)

BRAND_WEB   = "davidwebsolution.com"
BRAND_PHONE = "+91 82854 23939"
BRAND_TAG   = "@davidwebsolution"

TITLE_1  = "5 Signs Your Website"
TITLE_2  = "Is Costing You"
TITLE_3  = "Customers"
SUBTITLE = "Fix these and your leads will double."

SIGNS = [
    (ORANGE,      "⚡", "Loads in 3+ Seconds",       "53% of visitors leave before it even opens. Speed = money."),
    (BLUE_BRIGHT, "📱", "Not Mobile-Friendly",        "Over 70% of traffic is mobile. A broken layout kills trust instantly."),
    (PURPLE,      "🔍", "Not on Google Page 1",       "If you're on page 2+, you're invisible. 95% never scroll past page 1."),
    (GREEN,       "📞", "No Clear Call-to-Action",    "Visitors don't know what to do next. No CTA = no enquiry."),
    (BLUE,        "🔒", "Looks Outdated or Unsecure", "Old design = untrustworthy. No SSL? Google flags you as dangerous."),
]

BOTTOM_CTA = "We Fix All 5.  DM Us FREE AUDIT"


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


def build_infographic():
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    PAD = 52

    # ── HEADER ────────────────────────────────────────────────────────────────
    HH = 88
    draw.rectangle([0, 0, W, HH], fill=HDR_BG)
    draw.rectangle([0, HH-4, W, HH], fill=BLUE_BRIGHT)
    img  = _paste_logo(img, PAD, (HH-52)//2, white=True)
    draw = ImageDraw.Draw(img)
    tf   = _font(20, False)
    tw   = draw.textbbox((0,0), BRAND_TAG, font=tf)[2]
    draw.text((W-PAD-tw, (HH-22)//2), BRAND_TAG, font=tf, fill=(140,160,210))

    # ── TITLE SECTION ─────────────────────────────────────────────────────────
    # Big colored band behind title
    TITLE_Y = HH
    TITLE_H = 280
    # Gradient: blue dark → blue bright
    for i in range(TITLE_H):
        t = i / (TITLE_H-1)
        c = tuple(int(BLUE[j] + t*(( 0,50,160)[j]-BLUE[j])) for j in range(3))
        draw.line([(0, TITLE_Y+i),(W, TITLE_Y+i)], fill=c)

    # Decorative diagonal lines (Swiss)
    for di in range(0, W+200, 60):
        draw.line([(di, TITLE_Y),(di-120, TITLE_Y+TITLE_H)],
                  fill=(*WHITE, 12), width=1)

    # "WEBSITE AUDIT" label
    lf = _font(17, False)
    lt = "WEBSITE AUDIT  //  DAVID WEB SOLUTION"
    lw = draw.textbbox((0,0), lt, font=lf)[2]
    draw.text(((W-lw)//2, TITLE_Y+22), lt, font=lf, fill=(*BLUE_BRIGHT, 200))

    # Headline
    fh1 = _font(76)
    fh2 = _font(84)
    t1h = draw.textbbox((0,0), TITLE_1, font=fh1)[3]
    t2h = draw.textbbox((0,0), TITLE_2, font=fh1)[3]
    t3h = draw.textbbox((0,0), TITLE_3, font=fh2)[3]
    total_h = t1h + t2h + t3h + 8
    ty = TITLE_Y + (TITLE_H - total_h - 30) // 2 + 16

    t1w = draw.textbbox((0,0), TITLE_1, font=fh1)[2]
    draw.text(((W-t1w)//2, ty), TITLE_1, font=fh1, fill=WHITE)
    ty += t1h + 2

    t2w = draw.textbbox((0,0), TITLE_2, font=fh1)[2]
    draw.text(((W-t2w)//2, ty), TITLE_2, font=fh1, fill=WHITE)
    ty += t2h + 2

    t3w = draw.textbbox((0,0), TITLE_3, font=fh2)[2]
    draw.text(((W-t3w)//2, ty), TITLE_3, font=fh2, fill=ORANGE)
    ty += t3h + 8

    # Subtitle
    sf = _font(24, False)
    sw = draw.textbbox((0,0), SUBTITLE, font=sf)[2]
    draw.text(((W-sw)//2, ty), SUBTITLE, font=sf, fill=(200,220,255))

    # ── 5 SIGN CARDS ──────────────────────────────────────────────────────────
    CARDS_Y = TITLE_Y + TITLE_H + 16
    CARDS_END = H - 130
    CARD_H  = (CARDS_END - CARDS_Y) // 5
    CARD_GAP = 8

    num_f   = _font(48)
    sign_f  = _font(30)
    desc_f  = _font(21, False)
    stat_f  = _font(22)

    for idx, (color, _icon, sign, desc) in enumerate(SIGNS):
        cy = CARDS_Y + idx * (CARD_H + CARD_GAP)

        # Card background (alternating white / very light blue)
        card_bg = WHITE if idx % 2 == 0 else (242, 245, 255)
        draw.rectangle([0, cy, W, cy+CARD_H], fill=card_bg)

        # Left color strip (thick, colored per sign)
        draw.rectangle([0, cy+8, 10, cy+CARD_H-8], fill=color)

        # Number circle
        CIRC_R = 36
        ncx = PAD + CIRC_R
        ncy = cy + CARD_H//2
        draw.ellipse([ncx-CIRC_R, ncy-CIRC_R, ncx+CIRC_R, ncy+CIRC_R], fill=color)
        num_txt = str(idx+1)
        nf2 = _font(34)
        ntw = draw.textbbox((0,0), num_txt, font=nf2)[2]
        nth = draw.textbbox((0,0), num_txt, font=nf2)[3]
        draw.text((ncx-ntw//2, ncy-nth//2-2), num_txt, font=nf2, fill=WHITE)

        # Sign title
        tx = PAD + CIRC_R*2 + 22
        draw.text((tx, cy+16), sign, font=sign_f, fill=TEXT_DARK)

        # Description (2 lines max, smaller font)
        # Pre-split to 2 lines
        words = desc.split()
        line1, line2, cur = "", "", ""
        for w in words:
            test = (cur + " " + w).strip()
            if draw.textbbox((0,0), test, font=desc_f)[2] <= W-tx-PAD-10:
                cur = test
            else:
                if not line1: line1 = cur; cur = w
                else: line2 = (line2+" "+cur+" "+w).strip(); cur = ""
        if cur:
            if not line1: line1 = cur
            else: line2 = (line2+" "+cur).strip()

        dy = cy + 58
        draw.text((tx, dy), line1, font=desc_f, fill=TEXT_MED)
        if line2:
            dy += draw.textbbox((0,0), line1, font=desc_f)[3] + 2
            draw.text((tx, dy), line2, font=desc_f, fill=TEXT_MED)

        # Right: colored "SIGN #N" badge
        badge_txt = f"#{idx+1}"
        bf = _font(36)
        bw = draw.textbbox((0,0), badge_txt, font=bf)[2]
        draw.text((W-PAD-bw, cy + (CARD_H-40)//2), badge_txt, font=bf, fill=(*color, 60 if True else 60))
        draw.text((W-PAD-bw+0, cy + (CARD_H-40)//2), badge_txt, font=bf,
                  fill=tuple(min(255, v+80) for v in color))

        # Thin bottom divider
        draw.rectangle([0, cy+CARD_H, W, cy+CARD_H+CARD_GAP], fill=DIVIDER)

    # ── BOTTOM CTA ────────────────────────────────────────────────────────────
    CTA_Y = CARDS_END + CARD_GAP
    CTA_H = H - CTA_Y - 4
    draw.rectangle([0, CTA_Y, W, CTA_Y+CTA_H], fill=HDR_BG)
    draw.rectangle([0, CTA_Y, W, CTA_Y+3], fill=ORANGE)

    cf3  = _font(32)
    ctaw = draw.textbbox((0,0), BOTTOM_CTA, font=cf3)[2] + 80
    ctah = 66
    ctx  = (W - ctaw) // 2
    cty  = CTA_Y + (CTA_H - ctah) // 2 - 4
    draw.rounded_rectangle([ctx, cty, ctx+ctaw, cty+ctah], radius=33, fill=ORANGE)
    tw4  = draw.textbbox((0,0), BOTTOM_CTA, font=cf3)[2]
    th4  = draw.textbbox((0,0), BOTTOM_CTA, font=cf3)[3]
    draw.text((ctx+(ctaw-tw4)//2, cty+(ctah-th4)//2-1), BOTTOM_CTA, font=cf3, fill=WHITE)

    wf2  = _font(19, False)
    info = f"{BRAND_WEB}   |   {BRAND_PHONE}"
    iw2  = draw.textbbox((0,0), info, font=wf2)[2]
    draw.text(((W-iw2)//2, cty+ctah+10), info, font=wf2, fill=(130,155,200))

    draw.rectangle([0, H-4, W, H], fill=BLUE_BRIGHT)
    return img


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "posts")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "post_infographic.png")
    print("[DWS] Building Infographic...")
    img = build_infographic()
    img.save(out, format="PNG", optimize=True)
    print(f"[DWS] Done: {out}  {img.size[0]}x{img.size[1]}")
