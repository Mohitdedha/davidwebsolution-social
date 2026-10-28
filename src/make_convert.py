"""
"What makes a website convert" — reference-style post.
Photo background + navy overlay, browser mockup, 3 info rows, yellow CTA.
1080x1350px
"""
import os, io, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

W, H = 1080, 1350

NAVY        = (  4,  10,  38)
NAVY_MID    = (  8,  20,  65)
ROYAL_BLUE  = ( 20,  80, 200)
BRIGHT_BLUE = ( 30, 120, 255)
WHITE       = (255, 255, 255)
OFF_WHITE   = (230, 238, 255)
MUTED       = (160, 185, 235)
YELLOW      = (255, 210,   0)
YELLOW_DARK = (200, 160,   0)
CARD_BG     = ( 18,  40, 110)   # translucent card fill
ROW_BG      = ( 14,  34,  95)
DIVIDER     = ( 30,  55, 140)
GREEN_DOT   = ( 52, 199, 110)
RED_DOT     = (255,  80,  80)
AMBER_DOT   = (255, 185,  30)


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
    logo.thumbnail((200, 60), Image.LANCZOS)
    _LOGO_CACHE = logo
    return logo

def _paste_logo(img, x, y):
    logo = _load_logo()
    if not logo: return img
    wl = Image.new("RGBA", logo.size, (0,0,0,0))
    src = logo.load(); dst = wl.load()
    for yy in range(logo.height):
        for xx in range(logo.width):
            r, g, b, a = src[xx, yy]
            if a > 10: dst[xx, yy] = (255, 255, 255, a)
    base = img.convert("RGBA")
    base.paste(wl, (x, y), wl)
    return base.convert("RGB")


def _fetch_photo():
    for pid in [442, 160, 683, 119, 0]:
        try:
            url = f"https://picsum.photos/id/{pid}/1080/1350"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=18) as r:
                data = r.read()
            img = Image.open(io.BytesIO(data)).convert("RGB")
            print(f"[PHOTO] Picsum {pid} {img.size}")
            return img
        except Exception as e:
            print(f"[PHOTO] {pid}: {e}")
    return None


def _overlay(img, x0, y0, x1, y1, color, alpha):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(ov).rectangle([x0,y0,x1,y1], fill=(*color, alpha))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def _rr_alpha(img, xy, r, fill_color, alpha, outline=None, ow=2):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    dr = ImageDraw.Draw(ov)
    dr.rounded_rectangle(xy, radius=r, fill=(*fill_color, alpha),
                         outline=(*outline, 200) if outline else None, width=ow)
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def _draw_browser(img, x, y, w, h):
    """Draw a clean browser window illustration."""
    draw = ImageDraw.Draw(img)

    # Main window frame
    img = _rr_alpha(img, [x, y, x+w, y+h], 16, NAVY_MID, 220, ROYAL_BLUE, 2)
    draw = ImageDraw.Draw(img)

    # Title bar
    BAR_H = 44
    img = _rr_alpha(img, [x, y, x+w, y+BAR_H], 16, ROYAL_BLUE, 180)
    draw = ImageDraw.Draw(img)
    # Flatten bottom corners of title bar
    draw.rectangle([x, y+BAR_H-16, x+w, y+BAR_H], fill=(*ROYAL_BLUE, 180))

    # Traffic light dots
    for di, dc in enumerate([RED_DOT, AMBER_DOT, GREEN_DOT]):
        dx = x + 18 + di*22
        dy = y + BAR_H//2 - 7
        draw.ellipse([dx, dy, dx+14, dy+14], fill=dc)

    # Address bar
    addr_x = x + 80
    addr_w = w - 100
    img = _rr_alpha(img, [addr_x, y+8, addr_x+addr_w, y+BAR_H-8], 10, NAVY, 160)
    draw = ImageDraw.Draw(img)
    af = _font(15, False)
    draw.text((addr_x+14, y+15), "davidwebsolution.com", font=af, fill=MUTED)

    # Content area
    CONTENT_Y = y + BAR_H + 10
    CONTENT_H = h - BAR_H - 10

    # Fake hero banner (header block)
    hero_h = int(CONTENT_H * 0.30)
    img = _rr_alpha(img, [x+14, CONTENT_Y, x+w-14, CONTENT_Y+hero_h],
                    8, BRIGHT_BLUE, 140)
    draw = ImageDraw.Draw(img)
    hf = _font(20)
    hw = draw.textbbox((0,0),"Your Website Headline Here",font=hf)[2]
    draw.text((x+14+(w-28-hw)//2, CONTENT_Y+14), "Your Website Headline Here",
              font=hf, fill=WHITE)
    # Fake CTA in hero
    img = _rr_alpha(img, [x+w//2-60, CONTENT_Y+hero_h-32, x+w//2+60, CONTENT_Y+hero_h-8],
                    10, YELLOW, 230)
    draw = ImageDraw.Draw(img)
    bf2 = _font(13)
    draw.text((x+w//2-30, CONTENT_Y+hero_h-26), "Get Started", font=bf2, fill=NAVY)

    # Two column content
    col_y = CONTENT_Y + hero_h + 12
    col_h = int(CONTENT_H * 0.30)
    col_w = (w - 42) // 2
    for ci in range(2):
        cx2 = x + 14 + ci*(col_w+14)
        img = _rr_alpha(img, [cx2, col_y, cx2+col_w, col_y+col_h],
                        6, ROYAL_BLUE, 100)
        draw = ImageDraw.Draw(img)
        # Small icon dot
        draw.ellipse([cx2+10, col_y+8, cx2+24, col_y+22], fill=(*BRIGHT_BLUE,200))
        # Fake text lines
        for li in range(3):
            lw2 = col_w - 20 - (li*20)
            ly2 = col_y + 30 + li*14
            img = _rr_alpha(img, [cx2+10, ly2, cx2+10+lw2, ly2+8], 4, MUTED, 80)
            draw = ImageDraw.Draw(img)

    # Review stars row
    star_y = col_y + col_h + 10
    sf3 = _font(18)
    stars = "★★★★★"
    sw3 = draw.textbbox((0,0), stars, font=sf3)[2]
    draw.text((x + (w-sw3)//2, star_y), stars, font=sf3, fill=YELLOW)
    rf = _font(12, False)
    rev = "98% client satisfaction"
    rw2 = draw.textbbox((0,0), rev, font=rf)[2]
    draw.text((x+(w-rw2)//2, star_y+22), rev, font=rf, fill=MUTED)

    return img


def build_post():
    PAD = 58

    # ── BACKGROUND PHOTO ──────────────────────────────────────────────────────
    photo = _fetch_photo()
    if photo:
        pw, ph = photo.size
        scale  = max(W/pw, H/ph)
        nw, nh = int(pw*scale), int(ph*scale)
        photo  = photo.resize((nw,nh), Image.LANCZOS)
        left   = (nw-W)//2
        top    = (nh-H)//4
        photo  = photo.crop((left,top,left+W,top+H))
        photo  = ImageEnhance.Brightness(photo).enhance(0.55)
        photo  = ImageEnhance.Contrast(photo).enhance(1.1)
        photo  = ImageEnhance.Color(photo).enhance(0.5)
        img    = photo
    else:
        img = Image.new("RGB",(W,H), NAVY)

    # Strong navy overlay for readability
    img = _overlay(img, 0, 0, W, H, NAVY, 175)

    # Subtle gradient: heavier at top & bottom
    for i in range(300):
        t = 1 - i/300
        a = int(140 * t)
        ov = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(ov).line([(0,i),(W,i)], fill=(*NAVY,a))
        img = Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")
    for i in range(250):
        t = i/250
        a = int(160 * t)
        ov = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(ov).line([(0,H-i),(W,H-i)], fill=(*NAVY,a))
        img = Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")

    draw = ImageDraw.Draw(img)

    # ── LOGO (top left) ───────────────────────────────────────────────────────
    img  = _paste_logo(img, PAD, 28)
    draw = ImageDraw.Draw(img)

    # ── HEADLINE ──────────────────────────────────────────────────────────────
    # Font 74px so "What makes a website" fits within W-PAD*2 = 964px
    fh  = _font(74)
    hl1 = "What makes a website"
    hl2 = "convert"
    y   = 118

    draw.text((PAD, y), hl1, font=fh, fill=WHITE)
    y += draw.textbbox((0,0), hl1, font=fh)[3] + 6
    draw.text((PAD, y), hl2, font=fh, fill=BRIGHT_BLUE)
    y += draw.textbbox((0,0), hl2, font=fh)[3] + 52

    # ── BROWSER ILLUSTRATION ──────────────────────────────────────────────────
    BR_W = W - PAD*2
    BR_H = 400
    img  = _draw_browser(img, PAD, y, BR_W, BR_H)
    draw = ImageDraw.Draw(img)
    y   += BR_H + 52

    # ── 3 INFO ROWS ───────────────────────────────────────────────────────────
    rows = [
        ("1", "A clear headline"),
        ("2", "One main button"),
        ("3", "Proof: reviews and results"),
    ]
    ROW_H   = 88
    ROW_GAP = 12
    num_f   = _font(30)
    row_f   = _font(30, False)

    for num, text in rows:
        img  = _rr_alpha(img, [PAD, y, W-PAD, y+ROW_H], 16, CARD_BG, 200,
                         ROYAL_BLUE, 1)
        draw = ImageDraw.Draw(img)

        BADGE_R = 27
        bx = PAD + 27
        by = y + ROW_H//2
        draw.ellipse([bx-BADGE_R, by-BADGE_R, bx+BADGE_R, by+BADGE_R],
                     fill=BRIGHT_BLUE)
        nw2 = draw.textbbox((0,0), num, font=num_f)[2]
        nh2 = draw.textbbox((0,0), num, font=num_f)[3]
        draw.text((bx-nw2//2, by-nh2//2-1), num, font=num_f, fill=WHITE)

        th  = draw.textbbox((0,0), text, font=row_f)[3]
        draw.text((bx+BADGE_R+18, y+(ROW_H-th)//2), text, font=row_f, fill=WHITE)

        y += ROW_H + ROW_GAP

    y += 40

    # ── YELLOW CTA BUTTON ─────────────────────────────────────────────────────
    cf    = _font(34)
    cta   = "DM 'AUDIT' for a free review"
    CTA_H = 84
    CTA_W = W - PAD*2
    draw.rounded_rectangle([PAD, y, PAD+CTA_W, y+CTA_H], radius=42, fill=YELLOW)
    draw.rounded_rectangle([PAD+2, y+CTA_H-4, PAD+CTA_W-2, y+CTA_H+2],
                            radius=4, fill=YELLOW_DARK)
    tw4 = draw.textbbox((0,0), cta, font=cf)[2]
    th4 = draw.textbbox((0,0), cta, font=cf)[3]
    draw.text((PAD+(CTA_W-tw4)//2, y+(CTA_H-th4)//2-1), cta, font=cf, fill=NAVY)
    y += CTA_H + 36

    # ── FOOTER — anchored with bottom breathing room ───────────────────────────
    foot  = "Websites  •  SEO  •  AI UGC Ads  |  US & UK brands"
    ff    = _font(21, False)
    fw    = draw.textbbox((0,0), foot, font=ff)[2]
    fh2   = draw.textbbox((0,0), foot, font=ff)[3]
    # If footer would overflow, clamp to H-56
    y = min(y, H - fh2 - 48)
    mid_y = y + fh2//2 + 2
    draw.line([(PAD, mid_y), (PAD+(CTA_W-fw)//2-16, mid_y)], fill=DIVIDER, width=1)
    draw.line([(PAD+(CTA_W+fw)//2+16, mid_y), (PAD+CTA_W, mid_y)], fill=DIVIDER, width=1)
    draw.text((PAD+(CTA_W-fw)//2, y), foot, font=ff, fill=MUTED)

    return img


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "posts")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "post_convert.png")
    print("[DWS] Building 'What makes a website convert'...")
    img = build_post()
    img.save(out, format="PNG", optimize=True)
    print(f"[DWS] Done: {out}  {img.size[0]}x{img.size[1]}")
