"""
Professional branded image designer for David Web Solution.
Generates 1080x1350 portrait posts (5 premium templates).
Supports optional photo compositing for reference-quality designs.
"""
import io, os, re, random, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

SIZE   = 1080
HEIGHT = 1350
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

def _rr(draw, xy, r, fill=None, outline=None, outline_w=0, ow=None):
    # ow is alias for outline_w (used in new templates)
    ow = ow if ow is not None else outline_w
    if fill is not None:
        x0, y0, x1, y1 = xy
        draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
        draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
        for ex, ey in [(x0, y0), (x1 - 2*r, y0), (x0, y1 - 2*r), (x1 - 2*r, y1 - 2*r)]:
            draw.ellipse([ex, ey, ex + 2*r, ey + 2*r], fill=fill)
    if outline and ow:
        draw.rounded_rectangle(xy, radius=r, outline=outline, width=ow)

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
# Matches test_agency_v2.png reference:
# Orange header band | Left: "WE PROVIDE" + 2-color headline + numbered bullets
# Right: photo panel | Dark footer: CTA button + phone/website
# ═══════════════════════════════════════════════════════════════════════════════

def _social_circles(draw, x, y, r, color):
    """Draw 3 small social-icon circles (like reference header right side)."""
    gap = r * 2 + 8
    for i in range(3):
        cx = x + i * gap
        draw.ellipse([cx, y, cx + r*2, y + r*2], outline=color, width=2)

def _split_headline(hl):
    """Split headline into (dark_part, color_part) — first ~half dark, rest orange."""
    words = hl.split()
    if len(words) <= 1:
        return hl, ""
    mid = max(1, len(words) // 2)
    return " ".join(words[:mid]), " ".join(words[mid:])

def _tpl_agency_split(hl, bullets, cta, color, photo=None, intro_label="PRO TIP"):
    """Orange header + white split layout. Numbered bullets. Photo right panel."""
    WHITE  = (255, 255, 255)
    DARK   = (22, 22, 38)
    GRAY   = (100, 108, 130)

    PAD     = 44
    BAND_H  = 118
    FOOT_H  = 88
    CONTENT_Y = BAND_H
    CONTENT_H = SIZE - BAND_H - FOOT_H  # 874px

    # Left panel width (~52% of width)
    LEFT_W = 545
    RIGHT_X = LEFT_W

    img  = Image.new("RGB", (SIZE, SIZE), WHITE)
    draw = ImageDraw.Draw(img)

    # ── Orange header band
    draw.rectangle([0, 0, SIZE, BAND_H], fill=color)
    img = _paste_logo(img, PAD, (BAND_H - 52) // 2, white=True)
    draw = ImageDraw.Draw(img)
    # 3 social icon circles top-right
    circ_r = 18
    circ_y = (BAND_H - circ_r * 2) // 2
    _social_circles(draw, SIZE - PAD - 3 * (circ_r*2 + 8), circ_y, circ_r, WHITE)

    # ── Right photo panel
    PH_PAD = 24
    PH_X0  = RIGHT_X + PH_PAD
    PH_Y0  = CONTENT_Y + PH_PAD
    PH_X1  = SIZE - PH_PAD
    PH_Y1  = SIZE - FOOT_H - PH_PAD
    PH_W   = PH_X1 - PH_X0
    PH_H   = PH_Y1 - PH_Y0

    if photo:
        ph = _enhance_photo(_fit_photo(photo, PH_W, PH_H))
        # Paste with slight shadow (draw darker rect first)
        draw.rectangle([PH_X0 + 4, PH_Y0 + 4, PH_X1 + 4, PH_Y1 + 4],
                       fill=(200, 200, 210))
        img.paste(ph, (PH_X0, PH_Y0))
        draw = ImageDraw.Draw(img)
    else:
        # Placeholder: light gray rect with color top border
        draw.rectangle([PH_X0, PH_Y0, PH_X1, PH_Y1], fill=(240, 242, 250))
        draw.rectangle([PH_X0, PH_Y0, PH_X1, PH_Y0 + 5], fill=color)

    # Thin vertical separator line between panels
    draw.rectangle([RIGHT_X - 1, CONTENT_Y, RIGHT_X, SIZE - FOOT_H], fill=(225, 228, 240))

    # ── Left text panel
    TX = PAD
    TW = LEFT_W - PAD - 20
    y  = CONTENT_Y + 36

    # "WE PROVIDE" label
    fl = _font(18, False)
    draw.text((TX, y), "WE PROVIDE", font=fl, fill=GRAY)
    y += 26
    # Orange accent bar
    draw.rectangle([TX, y, TX + 50, y + 4], fill=color)
    y += 20

    # Large 2-color headline: first part dark, second part orange
    dark_part, color_part = _split_headline(hl)
    fh = _font(56)
    # Each word on its own line for large impact
    headline_words = hl.split()
    for word in headline_words[:3]:
        is_last_group = headline_words.index(word) >= len(headline_words) // 2
        fill = color if is_last_group else DARK
        draw.text((TX, y), word, font=fh, fill=fill)
        y += draw.textbbox((0, 0), word, font=fh)[3] + 4
    y += 8

    # Tagline
    ft = _font(18, False)
    # Use a short version of first bullet as tagline
    tagline_text = "We Help To Grow Your Business"
    draw.text((TX, y), tagline_text, font=ft, fill=GRAY)
    y += 30

    # Horizontal divider
    draw.rectangle([TX, y, LEFT_W - 24, y + 1], fill=(210, 214, 228))
    y += 18

    # "What We Do" section header
    fw = _font(22)
    draw.text((TX, y), "What We Do", font=fw, fill=DARK)
    y += 36

    # Numbered bullets 01/02/03/04
    fb  = _font(20, False)
    fbn = _font(20)
    nums = ["01", "02", "03", "04"]
    for i, bul in enumerate(bullets[:4]):
        # Number in orange
        num_text = nums[i]
        nw = draw.textbbox((0, 0), num_text, font=fbn)[2]
        draw.text((TX, y), num_text, font=fbn, fill=color)
        # Bullet text
        blines = _wrap(bul, fb, TW - nw - 14, draw, max_lines=1)
        if blines:
            draw.text((TX + nw + 10, y + 2), blines[0], font=fb, fill=(50, 55, 80))
        y += 30
        # Thin divider between items (not after last)
        if i < min(3, len(bullets) - 1):
            draw.rectangle([TX, y, LEFT_W - 24, y + 1], fill=(218, 222, 235))
            y += 8
        if y > SIZE - FOOT_H - 30:
            break

    # ── Dark footer
    draw.rectangle([0, SIZE - FOOT_H, SIZE, SIZE], fill=DARK)

    bf  = _font(19)
    bw  = draw.textbbox((0, 0), cta, font=bf)[2] + 56
    bw  = max(180, bw)
    by  = SIZE - FOOT_H + (FOOT_H - 44) // 2
    _btn(draw, PAD, by, bw, 44, color, cta, bf, WHITE)

    info = f"{BRAND_PHONE}  {BRAND_WEB}"
    iw   = draw.textbbox((0, 0), info, font=_font(18, False))[2]
    draw.text((SIZE - PAD - iw, SIZE - FOOT_H + (FOOT_H - 22) // 2),
              info, font=_font(18, False), fill=(180, 190, 215))

    return img


# ═══════════════════════════════════════════════════════════════════════════════
# Template 2 — DARK PRO
# Matches test_dark_pro_v2.png reference:
# Dark navy BG | Logo top-left | "WE ARE" pill | Large 2-color headline
# Left: services list | Right: orange rounded-rect photo panel
# ═══════════════════════════════════════════════════════════════════════════════

def _tpl_dark_pro(hl, bullets, cta, color, photo=None, intro_label="PRO TIP"):
    """Dark bg. Photo in orange-bordered rounded rect right. Bold headline left."""
    DARK  = (10, 12, 28)
    DARK2 = (16, 18, 40)
    WHITE = (255, 255, 255)
    MUTED = (160, 175, 215)

    PAD    = 44
    FOOT_H = 78

    img = Image.new("RGB", (SIZE, SIZE), DARK)
    draw = ImageDraw.Draw(img)

    # Subtle background gradient
    _grad(img, 0, 0, SIZE, SIZE // 2, DARK2, DARK)
    draw = ImageDraw.Draw(img)

    # ── Logo top-left (no separate band — logo floats on dark bg)
    img = _paste_logo(img, PAD, 32, white=True)
    draw = ImageDraw.Draw(img)

    # 3 social circles top-right
    circ_r = 17
    circ_y = 32 + circ_r // 2
    _social_circles(draw, SIZE - PAD - 3 * (circ_r*2 + 8), circ_y, circ_r, (180, 195, 240))

    # ── Right: orange rounded-rect photo panel
    PH_PAD = 38
    PH_X0  = SIZE // 2 + 20
    PH_Y0  = 115
    PH_X1  = SIZE - PH_PAD
    PH_Y1  = SIZE - FOOT_H - 30
    PH_W   = PH_X1 - PH_X0
    PH_H   = PH_Y1 - PH_Y0
    PANEL_R = 28

    if photo:
        # Clip photo to rounded rect and paste
        ph = _enhance_photo(_fit_photo(photo, PH_W, PH_H), contrast=1.1, brightness=0.93)
        # Draw orange border (slightly larger)
        draw.rounded_rectangle([PH_X0 - 5, PH_Y0 - 5, PH_X1 + 5, PH_Y1 + 5],
                                radius=PANEL_R + 3, fill=color)
        # Paste photo (clipped via mask)
        mask = Image.new("L", (PH_W, PH_H), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle([0, 0, PH_W - 1, PH_H - 1], radius=PANEL_R, fill=255)
        img.paste(ph, (PH_X0, PH_Y0), mask)
        draw = ImageDraw.Draw(img)
    else:
        # Orange filled rounded rect placeholder
        draw.rounded_rectangle([PH_X0, PH_Y0, PH_X1, PH_Y1],
                                radius=PANEL_R, fill=color)
        # Subtle brand text
        fw = _font(18, False)
        tw_b = draw.textbbox((0, 0), BRAND_WEB, font=fw)[2]
        draw.text(((PH_X0 + PH_X1 - tw_b) // 2, (PH_Y0 + PH_Y1) // 2),
                  BRAND_WEB, font=fw, fill=(255, 255, 255, 180))

    # ── Left text panel
    TX = PAD
    TW = PH_X0 - PAD - 28
    y  = 118

    # "WE ARE" pill label
    lw = draw.textbbox((0, 0), "WE ARE", font=_font(18))[2] + 28
    _rr(draw, [TX, y, TX + lw, y + 32], 16, color)
    draw.text((TX + 14, y + 6), "WE ARE", font=_font(18), fill=WHITE)
    y += 50

    # Large 2-color headline: per-word, alternating dark→white, last words orange
    fh = _font(62)
    headline_words = hl.split()
    total = len(headline_words)
    for i, word in enumerate(headline_words[:3]):
        fill = color if i >= total // 2 else WHITE
        draw.text((TX, y), word, font=fh, fill=fill)
        y += draw.textbbox((0, 0), word, font=fh)[3] + 2
    y += 6

    # Tagline
    ft = _font(18, False)
    draw.text((TX, y), "for your business", font=ft, fill=MUTED)
    y += 34

    # Divider
    draw.rectangle([TX, y, TX + 55, y + 3], fill=color)
    y += 18

    # "Our Services" header
    fs = _font(22)
    draw.text((TX, y), "Our Services", font=fs, fill=WHITE)
    y += 38

    # Service bullets with orange square marker
    fb = _font(20, False)
    sq = "■"  # small square bullet
    for bul in bullets[:4]:
        sw = draw.textbbox((0, 0), sq + "  ", font=fb)[2]
        draw.text((TX, y + 2), sq, font=fb, fill=color)
        blines = _wrap(bul, fb, TW - sw - 4, draw, max_lines=1)
        if blines:
            draw.text((TX + sw, y), blines[0], font=fb, fill=MUTED)
        y += 32
        if y > SIZE - FOOT_H - 20:
            break

    # ── Footer
    draw.rectangle([0, SIZE - FOOT_H, SIZE, SIZE], fill=(6, 8, 20))

    bf  = _font(19)
    bw  = draw.textbbox((0, 0), cta, font=bf)[2] + 56
    bw  = max(180, bw)
    by  = SIZE - FOOT_H + (FOOT_H - 44) // 2
    _btn(draw, PAD, by, bw, 44, color, cta, bf, WHITE)

    info = f"{BRAND_PHONE}  {BRAND_WEB}"
    iw   = draw.textbbox((0, 0), info, font=_font(17, False))[2]
    draw.text((SIZE - PAD - iw, SIZE - FOOT_H + (FOOT_H - 20) // 2),
              info, font=_font(17, False), fill=MUTED)

    return img


# ───────────────────────────────────────────────────────────────────────────────
# Shared helpers for premium templates
# ───────────────────────────────────────────────────────────────────────────────

def _ov(img, x0, y0, x1, y1, col, a):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(ov).rectangle([x0,y0,x1,y1], fill=(*col,a))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

def _gv(img, x0, y0, x1, y1, c1, c2):
    draw = ImageDraw.Draw(img)
    n = y1-y0
    for i in range(n):
        t = i/max(n-1,1)
        c = tuple(int(c1[j]+t*(c2[j]-c1[j])) for j in range(3))
        draw.line([(x0,y0+i),(x1,y0+i)], fill=c)

def _gh(img, x0, y0, x1, y1, c1, c2):
    draw = ImageDraw.Draw(img)
    n = x1-x0
    for i in range(n):
        t = i/max(n-1,1)
        c = tuple(int(c1[j]+t*(c2[j]-c1[j])) for j in range(3))
        draw.line([(x0+i,y0),(x0+i,y1)], fill=c)

def _hdr(img, color, logo_white=True):
    """Draw premium top header bar with logo."""
    W, H = img.size
    HH   = 88
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,W,HH], fill=(6,8,22))
    draw.rectangle([0,HH-3,W,HH], fill=color)   # color bottom rule
    draw.rectangle([0,0,6,HH], fill=color)       # left accent bar
    img  = _paste_logo(img, 66, (HH-52)//2, white=logo_white)
    draw = ImageDraw.Draw(img)
    tf   = _font(19, False)
    tw   = draw.textbbox((0,0), BRAND_TAG, font=tf)[2]
    draw.text((W-62-tw, (HH-20)//2), BRAND_TAG, font=tf, fill=(140,165,220))
    return img, draw, HH

def _footer(img, draw, cta, color):
    """Draw premium CTA footer."""
    W, H = img.size
    FH   = 120
    FY   = H - FH
    _gv(img, 0, FY, W, H, (6,8,22), (10,12,32))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, FY, W, FY+3], fill=color)
    # CTA button centered
    bf  = _font(25)
    bw_ = draw.textbbox((0,0),cta,font=bf)[2]+70
    bh_ = 58
    bx_ = (W-bw_)//2
    by_ = FY + (FH-bh_)//2 - 6
    _rr(draw, [bx_,by_,bx_+bw_,by_+bh_], 29, color)
    tw_ = draw.textbbox((0,0),cta,font=bf)[2]
    th_ = draw.textbbox((0,0),cta,font=bf)[3]
    draw.text((bx_+(bw_-tw_)//2, by_+(bh_-th_)//2-1), cta, font=bf, fill=(255,255,255))
    # website + phone
    wf   = _font(18,False)
    info = f"{BRAND_WEB}   |   {BRAND_PHONE}"
    iw   = draw.textbbox((0,0),info,font=wf)[2]
    draw.text(((W-iw)//2, by_+bh_+10), info, font=wf, fill=(120,145,200))
    return FY

# ═══════════════════════════════════════════════════════════════════════════════
# Template 3 — BOLD REVEAL v2
# Premium layout: diagonal photo strip + large headline + service tag row + stats
# ═══════════════════════════════════════════════════════════════════════════════

def _tpl_bold_reveal(hl, bullets, cta, color, photo=None, intro_label="WE OFFER"):
    """
    Premium layout:
    ┌────────────────────────────────┐
    │ HEADER (logo + tag)            │ 88px
    ├────────────────────────────────┤
    │ HERO: full-width photo/gradient│ 480px
    │   large BIG NUMBER + headline  │
    │   pill label, tagline          │
    ├────────────────────────────────┤
    │ FEATURE ROW (3 chips)          │ 72px
    ├────────────────────────────────┤
    │ SERVICES LIST (4 rows)         │ 470px
    ├────────────────────────────────┤
    │ FOOTER (CTA + web/phone)       │ 120px
    └────────────────────────────────┘
    """
    W, H = SIZE, HEIGHT
    NAVY = ( 6,  8, 22)
    DARK = (12, 15, 38)
    MID  = (18, 22, 56)
    WHITE= (255,255,255)
    MUTED= (145,168,225)
    PAD  = 62

    img = Image.new("RGB", (W, H), NAVY)
    _gv(img, 0, 0, W, H, DARK, NAVY)   # subtle base gradient

    # ── Header ────────────────────────────────────────────────────────────────
    img, draw, HH = _hdr(img, color)

    # ── Hero zone ─────────────────────────────────────────────────────────────
    HZ_Y, HZ_H = HH, 480
    _gv(img, 0, HZ_Y, W, HZ_Y+HZ_H, (0,36,130), (6,8,22))
    draw = ImageDraw.Draw(img)

    # Photo composite (right side) if available
    if photo:
        PH_W, PH_H = 420, HZ_H
        ph = _enhance_photo(_fit_photo(photo, PH_W, PH_H), brightness=0.7, contrast=1.2)
        img.paste(ph, (W-PH_W, HZ_Y))
        draw = ImageDraw.Draw(img)
        # Gradient mask: dark from left → transparent right
        _gh(img, W-PH_W, HZ_Y, W-PH_W+200, HZ_Y+HZ_H, DARK, (0,0,0))
        img = _ov(img, W-PH_W, HZ_Y, W, HZ_Y+HZ_H, (0,36,130), 120)
        draw = ImageDraw.Draw(img)

    # Large decorative circle (top-right, brand accent)
    draw.ellipse([W-260, HZ_Y-60, W+60, HZ_Y+220],
                 outline=(*color, 35), width=3)
    draw.ellipse([W-200, HZ_Y-10, W+10, HZ_Y+170],
                 outline=(*color, 20), width=1)

    y = HZ_Y + 38

    # Pill label
    pf  = _font(16)
    pw_ = draw.textbbox((0,0),intro_label,font=pf)[2]+28
    _rr(draw, [PAD, y, PAD+pw_, y+32], 16, color)
    draw.text((PAD+14,y+7), intro_label, font=pf, fill=WHITE)
    y += 50

    # Mega headline — 2 lines, word-wrapped, mixed color
    fh   = _font(90)
    fh2  = _font(90)
    words = hl.upper().split()
    # Line 1: first 2 words — white
    l1 = " ".join(words[:2])
    draw.text((PAD, y), l1, font=fh, fill=WHITE)
    y += draw.textbbox((0,0),l1,font=fh)[3] + 2
    # Line 2: remaining — brand color
    l2 = " ".join(words[2:4]) if len(words)>2 else ""
    if l2:
        draw.text((PAD, y), l2, font=fh2, fill=color)
        y += draw.textbbox((0,0),l2,font=fh2)[3] + 2
    y += 12

    # Accent rule (2-tone)
    draw.rectangle([PAD, y, PAD+80, y+5], fill=color)
    draw.rectangle([PAD+86, y, PAD+116, y+5], fill=(1,146,239))
    y += 20

    # Tagline
    fs = _font(24, False)
    for sl in _wrap("Full-Service Digital Agency — Real Results, No Fluff", fs, W-PAD*2-20, draw, 2):
        draw.text((PAD, y), sl, font=fs, fill=MUTED)
        y += 32

    # ── Feature chip row ──────────────────────────────────────────────────────
    FR_Y = HZ_Y + HZ_H
    draw.rectangle([0, FR_Y, W, FR_Y+70], fill=color)
    chips = bullets[:3]
    chip_x = PAD
    cf = _font(17)
    for chip in chips:
        cw_ = draw.textbbox((0,0),chip[:22],font=cf)[2]+30
        _rr(draw, [chip_x, FR_Y+16, chip_x+cw_, FR_Y+54], 19, (0,0,0))
        draw.text((chip_x+15, FR_Y+24), chip[:22], font=cf, fill=WHITE)
        chip_x += cw_ + 14
        if chip_x > W-PAD: break

    # ── Service list ──────────────────────────────────────────────────────────
    SL_Y = FR_Y + 70
    SL_H = H - SL_Y - 120
    draw.rectangle([0, SL_Y, W, SL_Y+SL_H], fill=DARK)

    svcs = [
        ("01", bullets[0] if len(bullets)>0 else "Website Design & Dev"),
        ("02", bullets[1] if len(bullets)>1 else "SEO & Google Ranking"),
        ("03", bullets[2] if len(bullets)>2 else "UGC & AI Video Ads"),
        ("04", bullets[3] if len(bullets)>3 else "eCommerce Solutions"),
    ]
    row_h = SL_H // 4
    for idx, (num, svc) in enumerate(svcs):
        ry = SL_Y + idx * row_h
        # Alternating subtle bg
        if idx % 2 == 1:
            draw.rectangle([0, ry, W, ry+row_h], fill=MID)
        # Left color bar
        bar_c = color if idx % 2 == 0 else (1,146,239)
        draw.rectangle([0, ry+8, 6, ry+row_h-8], fill=bar_c)
        # Number
        fn  = _font(34)
        draw.text((PAD, ry+(row_h-36)//2), num, font=fn, fill=bar_c)
        nw_ = draw.textbbox((0,0),num,font=fn)[2]
        # Service text
        ft  = _font(26)
        fd  = _font(19,False)
        draw.text((PAD+nw_+20, ry+(row_h-30)//2-2), svc[:38], font=ft, fill=WHITE)
        # Arrow hint
        draw.text((W-PAD-20, ry+(row_h-22)//2), ">", font=fd, fill=bar_c)
        # Thin divider
        if idx < 3:
            draw.rectangle([PAD, ry+row_h-1, W-PAD, ry+row_h], fill=(30,35,70))

    # ── Footer ────────────────────────────────────────────────────────────────
    _footer(img, draw, cta, color)
    return img


# ═══════════════════════════════════════════════════════════════════════════════
# Template 4 — GROW WITH US v2 (portrait 1080x1350)
# Full-bleed diagonal split bg + cinematic photo + stats hero + impact cards
# ═══════════════════════════════════════════════════════════════════════════════

def _tpl_grow_with_us(hl, bullets, cta, color, photo=None, intro_label="WE OFFER"):
    W, H    = SIZE, HEIGHT
    BDARK   = (  0,  36, 130)
    BBRIGHT = (  1, 146, 239)
    DARK    = ( 10,  13,  34)
    NAVY    = (  6,   8,  22)
    WHITE   = (255, 255, 255)
    MUTED   = (145, 170, 225)
    LBLUE   = (210, 228, 255)
    PAD     = 62

    img  = Image.new("RGB", (W, H), NAVY)
    _gv(img, 0, 0, W, H, DARK, NAVY)

    # Header
    img, draw, HH = _hdr(img, BBRIGHT)

    # ── Hero: large diagonal color block + headline ────────────────────────────
    HZ_Y, HZ_H = HH, 400
    # Background: dark navy to brand dark blue
    _gv(img, 0, HZ_Y, W, HZ_Y+HZ_H, BDARK, (8,10,28))
    draw = ImageDraw.Draw(img)

    # Photo composite (right side)
    if photo:
        PH_W, PH_H = 380, HZ_H
        ph = _enhance_photo(_fit_photo(photo, PH_W, PH_H), brightness=0.65, contrast=1.25)
        img.paste(ph, (W-PH_W, HZ_Y))
        draw = ImageDraw.Draw(img)
        _gh(img, W-PH_W-80, HZ_Y, W-PH_W+120, HZ_Y+HZ_H, (8,10,28), (0,0,0))
        img = _ov(img, W-PH_W, HZ_Y, W, HZ_Y+HZ_H, BDARK, 140)
        draw = ImageDraw.Draw(img)

    # Large decorative arc (top right)
    draw.arc([W-350, HZ_Y-80, W+50, HZ_Y+320], 150, 320, fill=(*BBRIGHT,50), width=3)
    draw.arc([W-280, HZ_Y-20, W+20, HZ_Y+260], 150, 320, fill=(*BBRIGHT,30), width=2)

    y = HZ_Y + 36
    # Pill
    pf  = _font(16)
    pw_ = draw.textbbox((0,0),intro_label,font=pf)[2]+28
    _rr(draw, [PAD, y, PAD+pw_, y+32], 16, BBRIGHT)
    draw.text((PAD+14,y+7), intro_label, font=pf, fill=WHITE)
    y += 50

    # Headline: 3 lines
    fh = _font(84)
    words = hl.upper().split()
    pairs = [(words[i:i+2]) for i in range(0,min(6,len(words)),2)]
    hcols = [WHITE, BBRIGHT, color]
    for idx, wds in enumerate(pairs[:3]):
        txt = " ".join(wds)
        draw.text((PAD, y), txt, font=fh, fill=hcols[idx%3])
        y += draw.textbbox((0,0),txt,font=fh)[3] + 2
    y += 14

    # Tagline
    fs = _font(23, False)
    for sl in _wrap("No fluff. Just results that grow your business.", fs, W-PAD*2, draw, 2):
        draw.text((PAD, y), sl, font=fs, fill=MUTED); y += 32

    # ── Stats band ─────────────────────────────────────────────────────────────
    ST_Y = HZ_Y + HZ_H
    ST_H = 108
    _gh(img, 0, ST_Y, W, ST_Y+ST_H, BBRIGHT, BDARK)
    draw = ImageDraw.Draw(img)
    stats = [("100+","Projects"),("8+","Years Exp"),("98%","Satisfaction")]
    cw2   = W // 3
    for idx,(val,lbl) in enumerate(stats):
        cx = idx*cw2 + cw2//2
        fv = _font(42); fl = _font(18, False)
        vw = draw.textbbox((0,0),val,font=fv)[2]
        lw = draw.textbbox((0,0),lbl,font=fl)[2]
        draw.text((cx-vw//2, ST_Y+10), val, font=fv, fill=WHITE)
        draw.text((cx-lw//2, ST_Y+60), lbl, font=fl, fill=(220,235,255))
        if idx < 2:
            draw.rectangle([idx*cw2+cw2-1,ST_Y+16,idx*cw2+cw2+1,ST_Y+ST_H-16], fill=(255,255,255,80))

    # ── 3 benefit cards ────────────────────────────────────────────────────────
    BC_Y = ST_Y + ST_H + 8
    BC_H = H - BC_Y - 120    # leaves 120px for footer
    card_h = (BC_H - 24) // 3
    descs = [
        "Rank higher on Google. Get found by buyers who are ready to pay.",
        "Fast, mobile-first sites built to turn every visitor into a client.",
        "AI video ads & UGC content that stop scrollers and drive sales.",
    ]
    draw.rectangle([0, BC_Y, W, H-120], fill=DARK)
    for i in range(3):
        cy = BC_Y + i*(card_h+12)
        # Subtle alternating bg
        bg = (14,18,48) if i%2==0 else (10,13,36)
        draw.rectangle([PAD-20, cy, W-PAD+20, cy+card_h], fill=bg)
        # Left stripe: alternating colors
        sc  = BBRIGHT if i%2==0 else color
        draw.rectangle([PAD-20, cy, PAD-14, cy+card_h], fill=sc)
        # Number large
        fn  = _font(48)
        num = f"0{i+1}"
        draw.text((PAD, cy+card_h//2-28), num, font=fn, fill=sc)
        nw_ = draw.textbbox((0,0),num,font=fn)[2]
        # Title
        ft  = _font(27)
        bul = bullets[i] if i < len(bullets) else descs[i][:30]
        for tl in _wrap(bul, ft, W-PAD-nw_-PAD-30, draw, 1):
            draw.text((PAD+nw_+20, cy+10), tl, font=ft, fill=WHITE)
        # Desc
        fd  = _font(20, False)
        dy_ = cy+46
        for dl in _wrap(descs[i], fd, W-PAD-nw_-PAD-30, draw, 2):
            draw.text((PAD+nw_+20, dy_), dl, font=fd, fill=MUTED); dy_+=26
        # Divider
        if i < 2:
            draw.rectangle([PAD, cy+card_h-1, W-PAD, cy+card_h], fill=(28,34,72))

    # ── Footer ─────────────────────────────────────────────────────────────────
    _footer(img, draw, cta, BBRIGHT)
    return img


# ═══════════════════════════════════════════════════════════════════════════════
# Template 5 — WHAT WE BUILD v2 (portrait 1080x1350)
# Magazine-style: bold top color block + editorial service list + premium footer
# ═══════════════════════════════════════════════════════════════════════════════

def _tpl_what_we_build(hl, bullets, cta, color, photo=None, intro_label="WE OFFER"):
    W, H    = SIZE, HEIGHT
    BDARK   = (  0,  36, 130)
    BBRIGHT = (  1, 146, 239)
    NAVY    = (  6,   8,  22)
    DARK    = ( 10,  13,  34)
    WHITE   = (255, 255, 255)
    MUTED   = (145, 168, 220)
    LBLUE   = (210, 228, 255)
    PAD     = 72

    img  = Image.new("RGB", (W, H), NAVY)
    _gv(img, 0, 0, W, H, DARK, NAVY)
    draw = ImageDraw.Draw(img)

    # ── Header ─────────────────────────────────────────────────────────────────
    img, draw, HH = _hdr(img, color)

    # ── Bold top section: color block with large headline ──────────────────────
    TOP_Y = HH
    TOP_H = 320
    # Solid brand dark blue
    draw.rectangle([0, TOP_Y, W, TOP_Y+TOP_H], fill=BDARK)
    # Diagonal accent: large triangle bottom-right
    pts = [(W, TOP_Y+TOP_H-120), (W, TOP_Y+TOP_H), (W-240, TOP_Y+TOP_H)]
    draw.polygon(pts, fill=color)
    # Small decorative dots grid (top-right area)
    for row in range(4):
        for col in range(5):
            dx, dy = W-60-col*28, TOP_Y+20+row*28
            draw.ellipse([dx,dy,dx+8,dy+8], fill=(*WHITE,40))

    y = TOP_Y + 38
    # "AGENCY" small label
    al  = _font(16, False)
    at  = "FULL-SERVICE DIGITAL AGENCY"
    draw.text((PAD, y), at, font=al, fill=(*BBRIGHT, 200))
    y += 30
    # Orange accent bar under label
    draw.rectangle([PAD, y, PAD+60, y+3], fill=color)
    y += 18

    # Headline: 2-3 lines, very large, white
    fh  = _font(96)
    words = hl.upper().split()
    pairs = [words[i:i+2] for i in range(0,min(6,len(words)),2)]
    cols_hl = [WHITE, BBRIGHT, color]
    for idx, wds in enumerate(pairs[:3]):
        txt = " ".join(wds)
        draw.text((PAD, y), txt, font=fh, fill=cols_hl[idx%3])
        y += draw.textbbox((0,0),txt,font=fh)[3] + 2

    # ── Divider strip ───────────────────────────────────────────────────────────
    DIV_Y = TOP_Y + TOP_H
    _gh(img, 0, DIV_Y, W, DIV_Y+8, color, BBRIGHT)
    draw = ImageDraw.Draw(img)

    # ── 4 editorial service rows ────────────────────────────────────────────────
    SVC_START = DIV_Y + 8
    SVC_END   = H - 120
    ROW_H     = (SVC_END - SVC_START) // 4
    svcs = [
        ("Website Design & Dev",  "WordPress, custom HTML, landing pages — built to convert."),
        ("SEO & Google Ranking",   "Page 1 results. Technical SEO, local SEO, link building."),
        ("UGC & AI Video Ads",     "Scroll-stopping content for ecom brands and startups."),
        ("eCommerce Solutions",    "Shopify & WooCommerce stores — CRO-optimized to sell."),
    ]
    draw.rectangle([0, SVC_START, W, SVC_END], fill=DARK)

    for idx, (title, desc) in enumerate(svcs):
        ry = SVC_START + idx*ROW_H
        # Alternating row bg
        bg = (14,18,48) if idx%2==0 else (10,13,36)
        draw.rectangle([0, ry, W, ry+ROW_H], fill=bg)

        # Number badge (large, right side)
        fn  = _font(72)
        num = f"0{idx+1}"
        nw_ = draw.textbbox((0,0),num,font=fn)[2]
        # Draw number faint on right
        draw.text((W-PAD-nw_, ry+(ROW_H-80)//2), num, font=fn,
                  fill=(*(color if idx%2==0 else BBRIGHT), 45 if True else 45))
        # Actually draw with low-opacity trick: draw darker version
        nc  = tuple(min(255,v+30) for v in (DARK if idx%2==0 else (14,18,48)))
        draw.text((W-PAD-nw_+2, ry+(ROW_H-80)//2+2), num, font=fn, fill=nc)
        draw.text((W-PAD-nw_, ry+(ROW_H-80)//2), num, font=fn,
                  fill=(color if idx%2==0 else BBRIGHT))

        # Left color bar
        bar = color if idx%2==0 else BBRIGHT
        draw.rectangle([0, ry+12, 7, ry+ROW_H-12], fill=bar)

        # Title
        ft  = _font(30)
        draw.text((PAD, ry+18), title, font=ft, fill=WHITE)
        # Description
        fd  = _font(21, False)
        dy2 = ry + 58
        for dl in _wrap(desc, fd, W-PAD-nw_-PAD-20, draw, 2):
            draw.text((PAD, dy2), dl, font=fd, fill=MUTED); dy2 += 28
        # Thin divider
        if idx < 3:
            draw.rectangle([PAD, ry+ROW_H-1, W-PAD, ry+ROW_H], fill=(24,30,62))

    # ── Footer ─────────────────────────────────────────────────────────────────
    _footer(img, draw, cta, color)
    return img


# ── Public API ────────────────────────────────────────────────────────────────

def design_post(pillar: str, post_text: str, photo_bytes: bytes = None) -> bytes:
    """Generate a branded 1080x1350 portrait image. Returns PNG bytes."""
    hl    = _headline(post_text)
    blts  = _bullets(post_text)
    cta   = random.choice(CTA_OPTIONS)
    color = PILLAR_COLORS.get(pillar, (234, 110, 12))
    intro = PILLAR_INTRO.get(pillar, "WE OFFER")

    photo = _load_photo(photo_bytes) if photo_bytes else None

    # 3 native 1080x1350 portrait templates in rotation
    all_tpls = ["bold_reveal", "grow_with_us", "what_we_build"]
    tpl = random.choice(all_tpls)

    if tpl == "bold_reveal":
        img = _tpl_bold_reveal(hl, blts, cta, color, photo, intro_label=intro)
    elif tpl == "grow_with_us":
        img = _tpl_grow_with_us(hl, blts, cta, color, photo, intro_label=intro)
    else:
        img = _tpl_what_we_build(hl, blts, cta, color, photo, intro_label=intro)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    print(f"[DESIGN] tpl={tpl} pillar={pillar} size={img.size[0]}x{img.size[1]} {buf.tell()//1024}KB")
    return buf.getvalue()
