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
        # Top-biased: face/subject usually in upper portion of photo
        top = max(0, (h - s) // 4)
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
    result = lines[:max_lines]
    # If text was cut, add ellipsis to last line
    if len(lines) > max_lines and result:
        last = result[-1]
        while last and draw.textbbox((0, 0), last + "...", font=font)[2] > max_w:
            last = last.rsplit(" ", 1)[0]
        result[-1] = last + "..."
    return result

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

def _tpl_agency_split(hl, bullets, cta, color, photo=None, intro_label="PRO TIP"):
    """Clean split: photo right (full height), text left, dark footer."""
    WHITE  = (255, 255, 255)
    DARK   = (14, 16, 30)
    LIGHT  = (245, 247, 252)

    PAD    = 44
    FOOTER = 88
    HEADER = 88

    img  = Image.new("RGB", (SIZE, SIZE), LIGHT)
    draw = ImageDraw.Draw(img)

    # ── Header band
    draw.rectangle([0, 0, SIZE, HEADER], fill=DARK)
    draw.rectangle([0, HEADER - 4, SIZE, HEADER], fill=color)
    img = _paste_logo(img, PAD, (HEADER - 50) // 2, white=True)
    draw = ImageDraw.Draw(img)
    # Tag line top right
    tag = BRAND_TAG
    tw = draw.textbbox((0, 0), tag, font=_font(18, False))[2]
    draw.text((SIZE - PAD - tw, (HEADER - 22) // 2), tag,
              font=_font(18, False), fill=(160, 175, 210))

    # ── Right photo panel — full content height
    PH_X0 = SIZE // 2 + 10
    PH_Y0 = HEADER
    PH_X1 = SIZE
    PH_Y1 = SIZE - FOOTER
    PH_W  = PH_X1 - PH_X0
    PH_H  = PH_Y1 - PH_Y0

    if photo:
        ph = _enhance_photo(_fit_photo(photo, PH_W, PH_H))
        img.paste(ph, (PH_X0, PH_Y0))
        draw = ImageDraw.Draw(img)
        # Gradient overlay on left edge of photo so text doesn't clash
        _grad_overlay(img, PH_X0, PH_Y0, PH_X0 + 60, PH_Y1, LIGHT,
                      start_alpha=120, end_alpha=0)
        draw = ImageDraw.Draw(img)
        # Color accent bar on photo left edge
        draw.rectangle([PH_X0, PH_Y0, PH_X0 + 5, PH_Y1], fill=color)
    else:
        # Solid color panel — intentional branded look
        _grad(img, PH_X0, PH_Y0, PH_X1, PH_Y1, _dim(color, 85), _dim(color, 50))
        draw = ImageDraw.Draw(img)
        draw.rectangle([PH_X0, PH_Y0, PH_X0 + 5, PH_Y1], fill=color)
        # Website watermark
        fw = _font(20, False)
        tw = draw.textbbox((0, 0), BRAND_WEB, font=fw)[2]
        draw.text(((PH_X0 + PH_X1 - tw) // 2, (PH_Y0 + PH_Y1) // 2),
                  BRAND_WEB, font=fw, fill=(255, 255, 255, 160))

    # ── Left text panel
    TX  = PAD
    TW  = PH_X0 - PAD - 24          # text max width, stop before photo
    y   = HEADER + 32

    # Pill label
    lw = draw.textbbox((0, 0), intro_label, font=_font(20))[2] + 32
    _rr(draw, [TX, y, TX + lw, y + 36], 18, color)
    draw.text((TX + 16, y + 7), intro_label, font=_font(20), fill=WHITE)
    y += 52

    # Headline — single color, bold, 2-3 lines max
    fh = _font(46)
    for line in _wrap(hl, fh, TW, draw, max_lines=3):
        draw.text((TX, y), line, font=fh, fill=DARK)
        y += draw.textbbox((0, 0), line, font=fh)[3] + 6
    y += 12

    # Divider
    draw.rectangle([TX, y, TX + 60, y + 4], fill=color)
    y += 20

    # Bullets — clean tick style
    fb  = _font(21, False)
    dot = "▸"
    for bul in bullets[:4]:
        # Wrap long bullets
        blines = _wrap(bul, fb, TW - 28, draw, max_lines=2)
        for bi, bl in enumerate(blines):
            if bi == 0:
                dw = draw.textbbox((0, 0), dot + " ", font=fb)[2]
                draw.text((TX, y), dot, font=fb, fill=color)
                draw.text((TX + dw, y), bl, font=fb, fill=(40, 50, 75))
            else:
                draw.text((TX + 28, y), bl, font=fb, fill=(40, 50, 75))
            y += 34
        y += 4
        if y > SIZE - FOOTER - 50:
            break

    # ── Footer
    draw.rectangle([0, SIZE - FOOTER, SIZE, SIZE], fill=DARK)
    draw.rectangle([0, SIZE - FOOTER, SIZE, SIZE - FOOTER + 4], fill=color)

    bf   = _font(19)
    bw   = draw.textbbox((0, 0), cta, font=bf)[2] + 56
    bw   = max(200, min(bw, 300))
    by   = SIZE - FOOTER + (FOOTER - 44) // 2
    _btn(draw, PAD, by, bw, 44, color, cta, bf, WHITE)

    info = f"{BRAND_PHONE}  |  {BRAND_WEB}"
    iw   = draw.textbbox((0, 0), info, font=_font(18, False))[2]
    draw.text((SIZE - PAD - iw, SIZE - FOOTER + (FOOTER - 22) // 2),
              info, font=_font(18, False), fill=(160, 175, 210))

    return img


# ═══════════════════════════════════════════════════════════════════════════════
# Template 2 — DARK PRO
# Inspired by reference images 1, 2 & 5:
# Dark gradient BG | Left: bold headline + list | Right: person photo prominent
# Gold/color accents, high contrast professional look
# ═══════════════════════════════════════════════════════════════════════════════

def _tpl_dark_pro(hl, bullets, cta, color, photo=None, intro_label="PRO TIP"):
    """Dark bg, photo right full-height, bold white headline left."""
    DARK  = (12, 14, 30)
    WHITE = (255, 255, 255)

    PAD    = 44
    FOOTER = 88
    HEADER = 88

    img = Image.new("RGB", (SIZE, SIZE), DARK)
    draw = ImageDraw.Draw(img)

    # Subtle diagonal gradient background
    _grad(img, 0, 0, SIZE, SIZE, (18, 20, 42), DARK)
    draw = ImageDraw.Draw(img)

    # ── Header
    draw.rectangle([0, 0, SIZE, HEADER], fill=(8, 10, 24))
    draw.rectangle([0, HEADER - 4, SIZE, HEADER], fill=color)
    img = _paste_logo(img, PAD, (HEADER - 50) // 2, white=True)
    draw = ImageDraw.Draw(img)
    tag = BRAND_TAG
    tw = draw.textbbox((0, 0), tag, font=_font(18, False))[2]
    draw.text((SIZE - PAD - tw, (HEADER - 22) // 2), tag,
              font=_font(18, False), fill=(100, 120, 170))

    # ── Photo right — full content height, no padding
    PH_X0 = SIZE // 2 + 20
    PH_Y0 = HEADER
    PH_X1 = SIZE
    PH_Y1 = SIZE - FOOTER
    PH_W  = PH_X1 - PH_X0
    PH_H  = PH_Y1 - PH_Y0

    if photo:
        ph = _enhance_photo(_fit_photo(photo, PH_W, PH_H), contrast=1.1, brightness=0.95)
        img.paste(ph, (PH_X0, PH_Y0))
        draw = ImageDraw.Draw(img)
        # Dark gradient fade on left edge of photo so text is readable
        _grad_overlay(img, PH_X0, PH_Y0, PH_X0 + 80, PH_Y1, DARK,
                      start_alpha=180, end_alpha=0)
        draw = ImageDraw.Draw(img)
        draw.rectangle([PH_X0, PH_Y0, PH_X0 + 5, PH_Y1], fill=color)
    else:
        # Color panel fallback
        _grad(img, PH_X0, PH_Y0, PH_X1, PH_Y1, _dim(color, 60), _dim(color, 25))
        draw = ImageDraw.Draw(img)
        draw.rectangle([PH_X0, PH_Y0, PH_X0 + 5, PH_Y1], fill=color)
        fw2 = _font(20, False)
        tw2 = draw.textbbox((0, 0), BRAND_WEB, font=fw2)[2]
        draw.text(((PH_X0 + PH_X1 - tw2) // 2, (PH_Y0 + PH_Y1) // 2),
                  BRAND_WEB, font=fw2, fill=(200, 215, 245))

    # ── Left text
    TX = PAD
    TW = PH_X0 - PAD - 20
    y  = HEADER + 36

    lw = draw.textbbox((0, 0), intro_label, font=_font(20))[2] + 32
    _rr(draw, [TX, y, TX + lw, y + 36], 18, color)
    draw.text((TX + 16, y + 7), intro_label, font=_font(20), fill=WHITE)
    y += 52

    fh = _font(46)
    for line in _wrap(hl, fh, TW, draw, max_lines=3):
        draw.text((TX, y), line, font=fh, fill=WHITE)
        y += draw.textbbox((0, 0), line, font=fh)[3] + 6
    y += 14

    draw.rectangle([TX, y, TX + 60, y + 4], fill=color)
    y += 22

    fb  = _font(21, False)
    dot = "▸"
    for bul in bullets[:4]:
        blines = _wrap(bul, fb, TW - 28, draw, max_lines=2)
        for bi, bl in enumerate(blines):
            dw = draw.textbbox((0, 0), dot + " ", font=fb)[2]
            if bi == 0:
                draw.text((TX, y), dot, font=fb, fill=color)
                draw.text((TX + dw, y), bl, font=fb, fill=(180, 195, 230))
            else:
                draw.text((TX + dw, y), bl, font=fb, fill=(180, 195, 230))
            y += 34
        y += 4
        if y > SIZE - FOOTER - 50:
            break

    # ── Footer
    draw.rectangle([0, SIZE - FOOTER, SIZE, SIZE], fill=(8, 10, 24))
    draw.rectangle([0, SIZE - FOOTER, SIZE, SIZE - FOOTER + 4], fill=color)

    bf  = _font(19)
    bw  = draw.textbbox((0, 0), cta, font=bf)[2] + 56
    bw  = max(200, min(bw, 300))
    by  = SIZE - FOOTER + (FOOTER - 44) // 2
    _btn(draw, PAD, by, bw, 44, color, cta, bf, WHITE)

    info = f"{BRAND_PHONE}  |  {BRAND_WEB}"
    iw   = draw.textbbox((0, 0), info, font=_font(18, False))[2]
    draw.text((SIZE - PAD - iw, SIZE - FOOTER + (FOOTER - 22) // 2),
              info, font=_font(18, False), fill=(100, 120, 170))

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
