"""
Professional branded image designer for David Web Solution.
Generates 1080x1080 posts matching agency social media reference templates.
Supports optional photo compositing for reference-quality designs.
"""
import io, os, re, random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

SIZE = 1080
_LOGO_CACHE = None

# ── Logo ──────────────────────────────────────────────────────────────────────

def _load_logo(max_w=260, max_h=80):
    global _LOGO_CACHE
    if _LOGO_CACHE is not None:
        return _LOGO_CACHE
    path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if not os.path.exists(path):
        return None
    try:
        logo = Image.open(path).convert("RGBA")
        px = logo.load()
        w, h = logo.size
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if r > 215 and g > 215 and b > 215:
                    px[x, y] = (r, g, b, 0)
        bb = logo.getbbox()
        if bb:
            logo = logo.crop(bb)
        logo.thumbnail((max_w, max_h), Image.LANCZOS)
        _LOGO_CACHE = logo
        return logo
    except Exception:
        return None


def _paste_logo(img, x, y, white=False):
    logo = _load_logo()
    if not logo:
        return img
    if white:
        # Make logo white by filling non-transparent pixels
        wlogo = Image.new("RGBA", logo.size, (0, 0, 0, 0))
        px = logo.load()
        wpx = wlogo.load()
        for yy in range(logo.size[1]):
            for xx in range(logo.size[0]):
                r, g, b, a = px[xx, yy]
                if a > 10:
                    wpx[xx, yy] = (255, 255, 255, a)
        logo = wlogo
    base = img.convert("RGBA")
    base.paste(logo, (x, y), logo)
    return base.convert("RGB")


def _load_photo(photo_bytes):
    if not photo_bytes:
        return None
    try:
        img = Image.open(io.BytesIO(photo_bytes)).convert("RGB")
        w, h = img.size
        s = min(w, h)
        left = (w - s) // 2
        top = (h - s) // 2
        return img.crop((left, top, left + s, top + s))
    except Exception:
        return None


def _fit_photo(photo, w, h):
    pw, ph = photo.size
    scale = max(w / pw, h / ph)
    nw, nh = int(pw * scale), int(ph * scale)
    photo = photo.resize((nw, nh), Image.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return photo.crop((left, top, left + w, top + h))


def _enhance_photo(photo, contrast=1.1, color=1.05, brightness=0.95):
    photo = ImageEnhance.Contrast(photo).enhance(contrast)
    photo = ImageEnhance.Color(photo).enhance(color)
    photo = ImageEnhance.Brightness(photo).enhance(brightness)
    return photo


# ── Constants ─────────────────────────────────────────────────────────────────

BRAND_WEB = "davidwebsolution.com"
BRAND_TAG = "@davidwebsolution"
BRAND_PHONE = "+91 82854 23939"

CTA_OPTIONS = [
    "DM us to get started",
    "Free consultation → DM",
    "Comment GROW below",
    "Book a free call → DM",
    "Get a FREE quote",
]

PILLAR_COLORS = {
    "wordpress_tip":    (0,   115, 170),   # blue
    "seo_tip":          (16,  160,  83),   # green
    "ai_video_ugc":     (139,  92, 246),   # purple
    "web_mistake":      (220,  50,  50),   # red
    "client_result":    (234, 110,  12),   # orange
    "tool_spotlight":   (234, 110,  12),   # orange
    "industry_insight": (37,   99, 235),   # blue
}

PILLAR_INTRO = {
    "wordpress_tip":    "PRO TIP",
    "seo_tip":          "SEO TIP",
    "ai_video_ugc":     "AI & VIDEO",
    "web_mistake":      "AVOID THIS",
    "client_result":    "CLIENT WIN",
    "tool_spotlight":   "TOOL PICK",
    "industry_insight": "INSIGHTS",
}

PILLAR_TEMPLATES = {
    "wordpress_tip":    ["dark_pro", "agency_split"],
    "seo_tip":          ["dark_pro", "agency_split"],
    "ai_video_ugc":     ["dark_pro", "agency_split"],
    "web_mistake":      ["dark_pro", "agency_split"],
    "client_result":    ["dark_pro", "agency_split"],
    "tool_spotlight":   ["dark_pro", "agency_split"],
    "industry_insight": ["dark_pro", "agency_split"],
}

# ── Fonts ─────────────────────────────────────────────────────────────────────

def _font(size, bold=True):
    paths = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
         "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf",
         "C:/Windows/Fonts/segoeui.ttf"]
        if bold else
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf",
         "C:/Windows/Fonts/segoeui.ttf"]
    )
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clean(t):
    # Remove non-ASCII (emojis etc.) but keep readable text
    return re.sub(r"[^\x00-\x7F]+", "", t).strip()

def _headline(text):
    # Find the first line that has meaningful ASCII text (skip emoji-only lines)
    for line in text.strip().split("\n"):
        c = _clean(line)
        # Strip leading punctuation/bullets that might remain
        c = re.sub(r"^[\s\-•*#>|]+", "", c).strip()
        if len(c) > 8:
            return c[:55] + ("..." if len(c) > 55 else "")
    return "David Web Solution"

def _bullets(text):
    lines = text.strip().split("\n")

    # PASS 1: prefer lines that explicitly start with a bullet/number marker
    out = []
    for line in lines[1:]:
        raw = line.strip()
        if re.match(r"^[•\-*]\s+|^\d+[.)]\s+", raw):
            c = _clean(re.sub(r"^[•\-*=>#0-9.)]+\s*", "", raw))
            c = c.strip()
            if len(c) > 6 and not c.startswith("http") and not c.startswith("#"):
                out.append(c[:52])
        if len(out) >= 4:
            break

    # PASS 2: if no bullet lines found, grab short punchy sentences (not the long intro)
    if not out:
        for line in lines[1:]:
            c = _clean(re.sub(r"^[•\-*=>#0-9.)]+\s*", "", line.strip()))
            c = c.strip()
            # skip hashtag lines, urls, and long run-on sentences (>90 chars)
            if len(c) > 8 and len(c) < 90 and not c.startswith("http") and not c.startswith("#"):
                out.append(c[:52])
            if len(out) >= 4:
                break

    return out or ["WordPress Experts", "SEO Specialists", "AI Video & UGC Ads", "Flutter Apps"]

def _wrap(text, font, max_w, draw, max_lines=3):
    lines, cur = [], ""
    for word in text.split():
        test = (cur + " " + word).strip()
        try:
            w = draw.textbbox((0, 0), test, font=font)[2]
        except Exception:
            w = len(test) * 20
        if w <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines[:max_lines]

def _rr(draw, xy, r, fill, outline=None, outline_w=0):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    for ex, ey in [(x0, y0), (x1 - 2*r, y0), (x0, y1 - 2*r), (x1 - 2*r, y1 - 2*r)]:
        draw.ellipse([ex, ey, ex + 2*r, ey + 2*r], fill=fill)
    if outline and outline_w:
        draw.rounded_rectangle(xy, radius=r, outline=outline, width=outline_w)

def _grad(img, x0, y0, x1, y1, c1, c2, horiz=False):
    draw = ImageDraw.Draw(img)
    n = (x1 - x0) if horiz else (y1 - y0)
    for i in range(n):
        t = i / max(n - 1, 1)
        c = tuple(int(c1[j] + t * (c2[j] - c1[j])) for j in range(3))
        if horiz:
            draw.line([(x0 + i, y0), (x0 + i, y1)], fill=c)
        else:
            draw.line([(x0, y0 + i), (x1, y0 + i)], fill=c)

def _dim(c, amt=60):
    return tuple(max(0, v - amt) for v in c)

def _light(c, amt=60):
    return tuple(min(255, v + amt) for v in c)

def _btn(draw, x, y, w, h, fill, text, font, text_color=(255, 255, 255), r=None):
    if r is None:
        r = h // 2
    _rr(draw, [x, y, x + w, y + h], r, fill)
    tb = draw.textbbox((0, 0), text, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    draw.text((x + (w - tw) // 2, y + (h - th) // 2 - 1), text,
              font=font, fill=text_color)

def _color_overlay(img, x0, y0, x1, y1, color, alpha=160):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    dr.rectangle([x0, y0, x1, y1], fill=(*color, alpha))
    base = img.convert("RGBA")
    return Image.alpha_composite(base, ov).convert("RGB")

def _grad_overlay(img, x0, y0, x1, y1, color, start_alpha=0, end_alpha=200):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    h = y1 - y0
    for i in range(h):
        t = i / max(h - 1, 1)
        a = int(start_alpha + t * (end_alpha - start_alpha))
        dr.line([(x0, y0 + i), (x1, y0 + i)], fill=(*color, a))
    base = img.convert("RGBA")
    return Image.alpha_composite(base, ov).convert("RGB")


# ═══════════════════════════════════════════════════════════════════════════════
# Template 1 — AGENCY SPLIT
# Inspired by reference images 3 & 4:
# White/light BG | Left: color accent strip + bold text | Right: person photo
# Clean professional agency look
# ═══════════════════════════════════════════════════════════════════════════════

def _tpl_agency_split(hl, bullets, cta, color, photo=None, intro_label="WE PROVIDE"):
    WHITE = (255, 255, 255)
    DARK  = (18, 20, 35)
    GRAY  = (240, 242, 248)

    PAD   = 48          # outer horizontal padding
    GAP   = 32          # gap between text panel and photo

    img = Image.new("RGB", (SIZE, SIZE), WHITE)
    draw = ImageDraw.Draw(img)

    # ── Left accent strip (full height)
    STRIP_W = 10
    draw.rectangle([0, 0, STRIP_W, SIZE], fill=color)

    # ── Top color header band (full width)
    BAND_H = 120
    _grad(img, 0, 0, SIZE, BAND_H, _dim(color, 20), color)
    draw = ImageDraw.Draw(img)

    # Decorative circles in band (top right)
    for rad, opa in [(220, 15), (155, 25), (90, 40)]:
        col = tuple(int(c * opa / 100 + 255 * (1 - opa / 100)) for c in color)
        draw.ellipse([SIZE - rad, -rad // 2, SIZE + rad, rad + BAND_H // 2],
                     outline=col, width=2)

    # Logo on band — white, vertically centered with clear margin
    logo_y = (BAND_H - 52) // 2   # centers a ~52px-tall logo; never clips top or bottom
    img = _paste_logo(img, PAD, logo_y, white=True)
    draw = ImageDraw.Draw(img)

    # Social icons — top right on band, same vertical center as logo
    for i, ic in enumerate(["f", "ig", "in"]):
        ix = SIZE - PAD - 36 - i * 52
        iy = (BAND_H - 36) // 2
        draw.ellipse([ix, iy, ix + 36, iy + 36], outline=(255, 255, 255), width=2)
        tw = draw.textbbox((0, 0), ic, font=_font(15, False))[2]
        draw.text((ix + (36 - tw) // 2, iy + 9), ic, font=_font(15, False), fill=(255, 255, 255))

    # ── Layout constants
    CONTENT_Y = BAND_H + 36       # top of content area
    BOTTOM_BAR_H = 96
    BAR_Y = SIZE - BOTTOM_BAR_H  # y where bottom bar starts

    PHOTO_W = 420
    PHOTO_X0 = SIZE - PAD - PHOTO_W
    PHOTO_Y0 = CONTENT_Y
    PHOTO_Y1 = BAR_Y - 24
    PHOTO_H  = PHOTO_Y1 - PHOTO_Y0

    TEXT_X = STRIP_W + PAD
    TEXT_W = PHOTO_X0 - TEXT_X - GAP

    # ── Right photo panel
    if photo:
        ph = _enhance_photo(_fit_photo(photo, PHOTO_W, PHOTO_H))
        mask = Image.new("L", (PHOTO_W, PHOTO_H), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [(0, 0), (PHOTO_W - 1, PHOTO_H - 1)], radius=20, fill=255)
        img.paste(ph, (PHOTO_X0, PHOTO_Y0), mask)
        draw = ImageDraw.Draw(img)
        draw.rectangle([PHOTO_X0 - 8, PHOTO_Y0 - 8, PHOTO_X0 + 32, PHOTO_Y0 + 8], fill=color)
        draw.rectangle([PHOTO_X0 - 8, PHOTO_Y0 - 8, PHOTO_X0 + 8, PHOTO_Y0 + 32], fill=color)
    else:
        # Branded gradient panel — looks intentional, not a placeholder
        panel = Image.new("RGB", (PHOTO_W, PHOTO_H), color)
        _grad(panel, 0, 0, PHOTO_W, PHOTO_H, color, _dim(color, 70))
        pd = ImageDraw.Draw(panel)
        # Decorative circles
        for rad, opa in [(200, 20), (140, 35), (75, 55)]:
            pd.ellipse([PHOTO_W // 2 - rad, PHOTO_H // 2 - rad,
                        PHOTO_W // 2 + rad, PHOTO_H // 2 + rad],
                       outline=tuple(min(255, c + opa) for c in color), width=2)
        # Center: large intro label
        fc = _font(46)
        tw = pd.textbbox((0, 0), intro_label, font=fc)[2]
        pd.text(((PHOTO_W - tw) // 2, PHOTO_H // 2 - 60), intro_label, font=fc, fill=WHITE)
        # Underline
        pd.rectangle([(PHOTO_W - 80) // 2, PHOTO_H // 2 + 0,
                       (PHOTO_W + 80) // 2, PHOTO_H // 2 + 5], fill=WHITE)
        # Website
        fw = _font(18, False)
        tw2 = pd.textbbox((0, 0), BRAND_WEB, font=fw)[2]
        pd.text(((PHOTO_W - tw2) // 2, PHOTO_H // 2 + 22), BRAND_WEB, font=fw,
                fill=tuple(min(255, c + 90) for c in color))
        # Corner dots
        for cx, cy in [(30, 30), (PHOTO_W - 30, 30), (30, PHOTO_H - 30), (PHOTO_W - 30, PHOTO_H - 30)]:
            pd.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=WHITE)
        mask = Image.new("L", (PHOTO_W, PHOTO_H), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [(0, 0), (PHOTO_W - 1, PHOTO_H - 1)], radius=20, fill=255)
        img.paste(panel, (PHOTO_X0, PHOTO_Y0), mask)
        draw = ImageDraw.Draw(img)

    # ── Left text content
    y = CONTENT_Y

    # Intro label
    draw.text((TEXT_X, y), intro_label, font=_font(22), fill=color)
    y += 36

    # Colored accent bar
    draw.rectangle([TEXT_X, y, TEXT_X + 56, y + 5], fill=color)
    y += 20

    # Headline — first half dark, second half color
    fh1 = _font(74)
    fh2 = _font(92)
    words = hl.split()
    mid = max(1, len(words) // 2)
    for part, fnt, col in [(" ".join(words[:mid]), fh1, DARK),
                            (" ".join(words[mid:]), fh2, color)]:
        for wl in _wrap(part, fnt, TEXT_W, draw, max_lines=2):
            draw.text((TEXT_X, y), wl, font=fnt, fill=col)
            y += draw.textbbox((0, 0), wl, font=fnt)[3] + 4

    y += 10

    # Tagline
    draw.text((TEXT_X, y), "We Help To Grow Your Business", font=_font(20, False),
              fill=(100, 112, 145))
    y += 36

    # Divider
    draw.rectangle([TEXT_X, y, TEXT_X + TEXT_W, y + 2], fill=(218, 222, 238))
    y += 20

    # Services label
    draw.text((TEXT_X, y), "What We Do", font=_font(24), fill=DARK)
    y += 40

    # Numbered bullets
    fb = _font(22, False)
    fn = _font(30)
    for i, bul in enumerate(bullets[:4]):
        num = f"0{i + 1}"
        draw.text((TEXT_X, y), num, font=fn, fill=color)
        nw = draw.textbbox((0, 0), num, font=fn)[2]
        draw.text((TEXT_X + nw + 12, y + 4), bul, font=fb, fill=(28, 38, 62))
        y += 46
        if i < 3:
            draw.rectangle([TEXT_X, y, TEXT_X + TEXT_W - 8, y + 1], fill=(228, 232, 246))
            y += 10

    # ── Bottom bar
    draw.rectangle([0, BAR_Y, SIZE, SIZE], fill=DARK)
    draw.rectangle([0, BAR_Y, SIZE, BAR_Y + 4], fill=color)

    BTN_Y = BAR_Y + (BOTTOM_BAR_H - 48) // 2
    btn_font = _font(19)
    btn_w = draw.textbbox((0, 0), cta, font=btn_font)[2] + 64
    btn_w = max(220, min(btn_w, 320))
    _btn(draw, PAD, BTN_Y, btn_w, 48, color, cta, btn_font, WHITE)

    INFO_X = PAD + btn_w + 36   # wider gap between button and phone text
    footer_text = f"{BRAND_PHONE}  |  {BRAND_WEB}"
    draw.text((INFO_X, BAR_Y + (BOTTOM_BAR_H - 26) // 2),
              footer_text, font=_font(19, False), fill=(190, 200, 230))

    return img


# ═══════════════════════════════════════════════════════════════════════════════
# Template 2 — DARK PRO
# Inspired by reference images 1, 2 & 5:
# Dark gradient BG | Left: bold headline + list | Right: person photo prominent
# Gold/color accents, high contrast professional look
# ═══════════════════════════════════════════════════════════════════════════════

def _tpl_dark_pro(hl, bullets, cta, color, photo=None, intro_label="WE ARE"):
    DARK  = (10, 12, 28)
    DARK2 = (16, 18, 40)
    WHITE = (255, 255, 255)

    PAD  = 48           # outer padding
    GAP  = 28           # gap between text and photo
    LINE_GAP = 10       # extra space between text lines

    img = Image.new("RGB", (SIZE, SIZE), DARK)
    _grad(img, 0, 0, SIZE // 2, SIZE, DARK2, DARK)
    draw = ImageDraw.Draw(img)

    # Decorative background circles (top-right)
    for rad in [420, 320, 220]:
        alpha = 12 if rad == 420 else (20 if rad == 320 else 35)
        col = tuple(int(c * alpha / 100 + DARK[i] * (1 - alpha / 100))
                    for i, c in enumerate(color))
        draw.ellipse([SIZE - rad - 60, -rad // 3, SIZE + rad - 60, rad * 4 // 3],
                     outline=col, width=2)

    # ── Top bar
    draw.rectangle([0, 0, SIZE, 6], fill=color)

    # ── Layout constants
    BOTTOM_BAR_H = 96
    BAR_Y = SIZE - BOTTOM_BAR_H

    PHOTO_X0 = SIZE // 2 + 20
    PHOTO_Y0 = PAD + 56          # below logo row
    PHOTO_X1 = SIZE - PAD
    PHOTO_Y1 = BAR_Y - 20
    PHOTO_W  = PHOTO_X1 - PHOTO_X0
    PHOTO_H  = PHOTO_Y1 - PHOTO_Y0

    # ── Photo right panel
    if photo:
        ph = _enhance_photo(_fit_photo(photo, PHOTO_W, PHOTO_H),
                            contrast=1.1, brightness=0.97)
        mask = Image.new("L", (PHOTO_W, PHOTO_H), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [(0, 0), (PHOTO_W - 1, PHOTO_H - 1)], radius=22, fill=255)
        img.paste(ph, (PHOTO_X0, PHOTO_Y0), mask)
        draw = ImageDraw.Draw(img)
        # Corner accent bottom-right
        draw.rectangle([PHOTO_X1 - 48, PHOTO_Y1, PHOTO_X1, PHOTO_Y1 + 6], fill=color)
        draw.rectangle([PHOTO_X1, PHOTO_Y1 - 48, PHOTO_X1 + 6, PHOTO_Y1 + 6], fill=color)
        # Dot accent top-left
        draw.ellipse([PHOTO_X0 - 14, PHOTO_Y0 - 14, PHOTO_X0 + 14, PHOTO_Y0 + 14],
                     fill=color)
    else:
        panel = Image.new("RGB", (PHOTO_W, PHOTO_H), _dim(color, 60))
        _grad(panel, 0, 0, PHOTO_W, PHOTO_H, _dim(color, 80), _dim(color, 30))
        pd = ImageDraw.Draw(panel)
        for rad, opa in [(200, 18), (135, 30), (70, 50)]:
            pd.ellipse([PHOTO_W // 2 - rad, PHOTO_H // 2 - rad,
                        PHOTO_W // 2 + rad, PHOTO_H // 2 + rad],
                       outline=tuple(min(255, c + opa) for c in color), width=2)
        fc = _font(46)
        tw = pd.textbbox((0, 0), intro_label, font=fc)[2]
        pd.text(((PHOTO_W - tw) // 2, PHOTO_H // 2 - 60), intro_label, font=fc, fill=WHITE)
        pd.rectangle([(PHOTO_W - 80) // 2, PHOTO_H // 2 + 0,
                       (PHOTO_W + 80) // 2, PHOTO_H // 2 + 5], fill=color)
        fw = _font(18, False)
        tw2 = pd.textbbox((0, 0), BRAND_WEB, font=fw)[2]
        pd.text(((PHOTO_W - tw2) // 2, PHOTO_H // 2 + 22), BRAND_WEB, font=fw,
                fill=_light(color, 80))
        for cx, cy in [(30, 30), (PHOTO_W - 30, 30), (30, PHOTO_H - 30), (PHOTO_W - 30, PHOTO_H - 30)]:
            pd.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=color)
        mask = Image.new("L", (PHOTO_W, PHOTO_H), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [(0, 0), (PHOTO_W - 1, PHOTO_H - 1)], radius=22, fill=255)
        img.paste(panel, (PHOTO_X0, PHOTO_Y0), mask)
        draw = ImageDraw.Draw(img)

    # ── Left text area
    TEXT_W = PHOTO_X0 - PAD - GAP

    # Logo top-left (white)
    img = _paste_logo(img, PAD, (PAD + 56 - 60) // 2 + 8, white=True)
    draw = ImageDraw.Draw(img)

    # Social icons top-right
    for i, ic in enumerate(["f", "ig", "in"]):
        ix = SIZE - PAD - 34 - i * 50
        iy = (PAD + 56 - 34) // 2 + 8
        draw.ellipse([ix, iy, ix + 34, iy + 34], outline=(80, 92, 132), width=2)
        tw = draw.textbbox((0, 0), ic, font=_font(14, False))[2]
        draw.text((ix + (34 - tw) // 2, iy + 8), ic,
                  font=_font(14, False), fill=(130, 148, 188))

    # Intro label pill
    y = PHOTO_Y0 + 4
    intro_w = draw.textbbox((0, 0), intro_label, font=_font(24))[2] + 44
    _rr(draw, [PAD, y, PAD + intro_w, y + 42], 21, color)
    draw.text((PAD + 22, y + 8), intro_label, font=_font(24), fill=WHITE)
    y += 62

    # Big headline — first half big white, second half medium color
    fh_big = _font(96)
    fh_med = _font(70)
    words = hl.split()
    mid = max(1, len(words) // 2)
    for part, fnt, col in [(" ".join(words[:mid]), fh_big, WHITE),
                            (" ".join(words[mid:]), fh_med, color)]:
        for line in _wrap(part, fnt, TEXT_W, draw, max_lines=2):
            draw.text((PAD, y), line, font=fnt, fill=col)
            y += draw.textbbox((0, 0), line, font=fnt)[3] + LINE_GAP

    # Accent sub-text
    y += 6
    draw.text((PAD, y), "for your business", font=_font(26, False),
              fill=_light(color, 55))
    y += 46

    # Thick underline
    draw.rectangle([PAD, y, PAD + 180, y + 6], fill=color)
    y += 28

    # Services header
    draw.text((PAD, y), "Our Services", font=_font(26), fill=(200, 210, 240))
    y += 44

    # Bullet list
    fb = _font(23, False)
    for bul in bullets[:4]:
        draw.rectangle([PAD, y + 8, PAD + 8, y + 22], fill=color)
        draw.text((PAD + 22, y), bul, font=fb, fill=(168, 184, 222))
        y += 44
        if y > BAR_Y - 50:
            break

    # ── Bottom info bar
    draw.rectangle([0, BAR_Y, SIZE, SIZE], fill=(14, 16, 34))
    draw.rectangle([0, BAR_Y, SIZE, BAR_Y + 4], fill=color)

    BTN_Y = BAR_Y + (BOTTOM_BAR_H - 48) // 2
    btn_font = _font(19)
    btn_w = draw.textbbox((0, 0), cta, font=btn_font)[2] + 64
    btn_w = max(220, min(btn_w, 320))
    _btn(draw, PAD, BTN_Y, btn_w, 48, color, cta, btn_font, WHITE)

    INFO_X = PAD + btn_w + 36   # wider gap between button and phone text
    footer_text = f"{BRAND_PHONE}  |  {BRAND_WEB}"
    draw.text((INFO_X, BAR_Y + (BOTTOM_BAR_H - 26) // 2),
              footer_text, font=_font(19, False), fill=(190, 200, 240))

    return img


# ── Public API ────────────────────────────────────────────────────────────────

def design_post(pillar: str, post_text: str, photo_bytes: bytes = None) -> bytes:
    """Generate a branded 1080x1080 image. Returns PNG bytes."""
    hl    = _headline(post_text)
    blts  = _bullets(post_text)
    cta   = random.choice(CTA_OPTIONS)
    color = PILLAR_COLORS.get(pillar, (234, 110, 12))
    tpls  = PILLAR_TEMPLATES.get(pillar, ["agency_split", "dark_pro"])
    tpl   = random.choice(tpls)
    intro = PILLAR_INTRO.get(pillar, "WE OFFER")

    photo = _load_photo(photo_bytes) if photo_bytes else None

    if tpl == "agency_split":
        img = _tpl_agency_split(hl, blts, cta, color, photo, intro_label=intro)
    else:
        img = _tpl_dark_pro(hl, blts, cta, color, photo, intro_label=intro)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    print(f"[DESIGN] tpl={tpl} pillar={pillar} photo={'yes' if photo else 'no'} {buf.tell()//1024}KB")
    return buf.getvalue()
