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


# ═══════════════════════════════════════════════════════════════════════════════
# Template 3 — BOLD REVEAL (portrait 1080x1350)
# Dark hero + orange accents + 2x2 service cards grid + orange CTA band
# ═══════════════════════════════════════════════════════════════════════════════

def _tpl_bold_reveal(hl, bullets, cta, color, photo=None, intro_label="WE OFFER"):
    W, H   = SIZE, HEIGHT
    DARK   = (12,  14,  30)
    DARKER = ( 6,   8,  18)
    WHITE  = (255, 255, 255)
    MUTED  = (160, 178, 220)
    LIGHT  = (240, 243, 255)
    PAD    = 52

    img  = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(img)

    # Header band
    HH = 90
    draw.rectangle([0, 0, W, HH], fill=DARKER)
    draw.rectangle([0, 0, 5, HH], fill=color)
    img  = _paste_logo(img, PAD, (HH-52)//2, white=True)
    draw = ImageDraw.Draw(img)
    tf   = _font(20, False)
    tw   = draw.textbbox((0,0), BRAND_TAG, font=tf)[2]
    draw.text((W-PAD-tw, (HH-22)//2), BRAND_TAG, font=tf, fill=MUTED)

    # Hero strip: gradient bg
    HERO_Y, HERO_H = HH, 330
    for i in range(HERO_H):
        t = i/max(HERO_H-1,1)
        c = tuple(int((16,18,42)[j]+t*((8,12,38)[j]-(16,18,42)[j])) for j in range(3))
        draw.line([(0,HERO_Y+i),(W,HERO_Y+i)], fill=c)
    # Diagonal accent stripes top-right
    for i in range(0,220,14):
        draw.line([(W-i,HERO_Y),(W,HERO_Y+i)], fill=(*color,50), width=2)

    y = HERO_Y + 30
    # Service label pill
    pf   = _font(17)
    pt   = intro_label
    pw_  = draw.textbbox((0,0), pt, font=pf)[2] + 32
    _rr(draw, [PAD, y, PAD+pw_, y+34], 17, color)
    draw.text((PAD+16, y+7), pt, font=pf, fill=WHITE)
    y += 52

    # 3-line headline (font 74 — slightly smaller so it fits cleanly)
    fh = _font(74)
    words = hl.split()
    lines_hl = [words[i:i+2] for i in range(0,min(6,len(words)),2)] or [[hl]]
    colors_hl = [WHITE, color, WHITE]
    for idx, wds in enumerate(lines_hl[:3]):
        txt = " ".join(wds)
        draw.text((PAD, y), txt, font=fh, fill=colors_hl[idx % 3])
        y += draw.textbbox((0,0), txt, font=fh)[3] + 3
    y += 10

    # Subtext
    fs = _font(22, False)
    sub = "We Help To Grow Your Business"
    for sl in _wrap(sub, fs, W-PAD*2, draw, 2):
        draw.text((PAD, y), sl, font=fs, fill=MUTED)
        y += 30

    # Divider
    DIV_Y = HERO_Y + HERO_H
    draw.rectangle([0, DIV_Y, W, DIV_Y+6], fill=color)
    draw.rectangle([0, DIV_Y+6, W, DIV_Y+8], fill=DARKER)

    # Services grid 2x2 — height exactly fits 2 rows + header
    CARD_W = (W-PAD*2-20)//2
    CARD_H = 168
    CARD_GAP = 18
    GRID_HDR = 58   # "Our Services" header
    GRID_H   = GRID_HDR + 2*(CARD_H+CARD_GAP) + 10
    GRID_Y   = DIV_Y + 8
    draw.rectangle([0, GRID_Y, W, GRID_Y+GRID_H], fill=DARK)
    gy = GRID_Y + 22
    fsh = _font(27)
    draw.text((PAD, gy), "Our Services", font=fsh, fill=WHITE)
    uw_ = draw.textbbox((0,0),"Our Services",font=fsh)[2]
    draw.rectangle([PAD, gy+33, PAD+uw_, gy+37], fill=color)
    gy += GRID_HDR

    for idx, bul in enumerate(bullets[:4]):
        col_i = idx%2; row_i = idx//2
        cx = PAD + col_i*(CARD_W+20)
        cy = gy + row_i*(CARD_H+CARD_GAP)
        _rr(draw, [cx, cy, cx+CARD_W, cy+CARD_H], 16, (18,20,46))
        _rr(draw, [cx, cy, cx+CARD_W, cy+CARD_H], 16, None, color, 2)
        fn  = _font(38)
        num = f"0{idx+1}"
        draw.text((cx+18, cy+14), num, font=fn, fill=color)
        fn2 = _font(20, False)
        nlines = _wrap(bul, fn2, CARD_W-38, draw, 2)
        ny = cy+62
        for nl in nlines:
            draw.text((cx+18, ny), nl, font=fn2, fill=WHITE); ny+=27
        draw.rectangle([cx+18, cy+CARD_H-12, cx+52, cy+CARD_H-8], fill=color)

    # CTA band — fills remaining space
    CTA_Y = GRID_Y + GRID_H + 6
    CTA_H = H - CTA_Y
    draw.rectangle([0, CTA_Y, W, H], fill=color)
    bf   = _font(26)
    bw_  = draw.textbbox((0,0), cta, font=bf)[2]+64
    bh_  = 62
    bx_  = (W-bw_)//2
    by_  = CTA_Y+(CTA_H-bh_)//2-14
    _rr(draw, [bx_, by_, bx_+bw_, by_+bh_], 31, WHITE)
    tw_  = draw.textbbox((0,0), cta, font=bf)[2]
    th_  = draw.textbbox((0,0), cta, font=bf)[3]
    draw.text((bx_+(bw_-tw_)//2, by_+(bh_-th_)//2-2), cta, font=bf, fill=DARK)
    wf = _font(20, False)
    ww = draw.textbbox((0,0), BRAND_WEB, font=wf)[2]
    draw.text(((W-ww)//2, by_+bh_+12), BRAND_WEB, font=wf, fill=(255,220,180))

    return img


# ═══════════════════════════════════════════════════════════════════════════════
# Template 4 — GROW WITH US (portrait 1080x1350)
# Brand blue gradient + 3 benefit cards + stats strip + dark CTA
# ═══════════════════════════════════════════════════════════════════════════════

def _tpl_grow_with_us(hl, bullets, cta, color, photo=None, intro_label="WE OFFER"):
    W, H    = SIZE, HEIGHT
    BDARK   = (  0,  36, 130)
    BBRIGHT = (  1, 146, 239)
    DARK    = ( 12,  16,  42)
    NAVY    = (  6,  10,  28)
    WHITE   = (255, 255, 255)
    MUTED   = (160, 185, 235)
    LBLUE   = (220, 235, 255)
    PAD     = 52

    img  = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Header
    HH = 90
    draw.rectangle([0, 0, W, HH], fill=(8,12,34))
    draw.rectangle([0, 0, 5, HH], fill=BBRIGHT)
    img  = _paste_logo(img, PAD, (HH-52)//2, white=True)
    draw = ImageDraw.Draw(img)
    tf   = _font(20, False)
    tw   = draw.textbbox((0,0), BRAND_TAG, font=tf)[2]
    draw.text((W-PAD-tw, (HH-22)//2), BRAND_TAG, font=tf, fill=MUTED)

    # Hero gradient
    HERO_Y, HERO_H = HH, 310
    for i in range(HERO_H):
        t = i/max(HERO_H-1,1)
        c = tuple(int(BDARK[j]+t*((8,12,38)[j]-BDARK[j])) for j in range(3))
        draw.line([(0,HERO_Y+i),(W,HERO_Y+i)], fill=c)
    draw.ellipse([W-220,HERO_Y-80,W+80,HERO_Y+220], outline=(*BBRIGHT,40), width=3)
    draw.ellipse([W-160,HERO_Y-20,W+20,HERO_Y+160], outline=(*BBRIGHT,25), width=2)

    y = HERO_Y + 40
    lf   = _font(18)
    lt   = intro_label
    lw_  = draw.textbbox((0,0),lt,font=lf)[2]+32
    _rr(draw,[PAD,y,PAD+lw_,y+34],17,BBRIGHT)
    draw.text((PAD+16,y+7), lt, font=lf, fill=WHITE)
    y += 54

    fh1 = _font(78)
    words = hl.split()
    draw.text((PAD,y), " ".join(words[:2]) if len(words)>1 else hl, font=fh1, fill=WHITE)
    y += draw.textbbox((0,0), " ".join(words[:2]) if len(words)>1 else hl, font=fh1)[3]+4
    if len(words)>2:
        draw.text((PAD,y), " ".join(words[2:4]), font=fh1, fill=BBRIGHT)
        y += draw.textbbox((0,0)," ".join(words[2:4]),font=fh1)[3]+16
    else: y += 12
    fs = _font(23, False)
    sub = "With strategies that actually work — no fluff, just results."
    for sl in _wrap(sub, fs, W-PAD*2, draw, 2):
        draw.text((PAD,y), sl, font=fs, fill=MUTED); y+=33

    # Divider
    DIV_Y = HERO_Y + HERO_H
    for i in range(W):
        t=i/max(W-1,1)
        c=tuple(int(BDARK[j]+t*(BBRIGHT[j]-BDARK[j])) for j in range(3))
        draw.line([(i,DIV_Y),(i,DIV_Y+6)], fill=c)

    # Benefit cards
    BEN_Y = DIV_Y + 6
    draw.rectangle([0,BEN_Y,W,BEN_Y+420], fill=DARK)
    by = BEN_Y + 28
    descs = [
        "Rank higher on Google, get found by buyers who are ready to pay.",
        "Fast, mobile-first design built to turn clicks into paying clients.",
        "Scroll-stopping content for ecom brands and startups that convert.",
    ]
    for i, (bul, desc) in enumerate(zip(bullets[:3], descs)):
        _rr(draw,[PAD,by,W-PAD,by+112],16,(16,20,52))
        draw.rounded_rectangle([PAD,by,PAD+6,by+112],radius=4,fill=BBRIGHT)
        fn  = _font(38)
        num = f"0{i+1}"
        draw.text((PAD+22,by+16), num, font=fn, fill=BBRIGHT)
        nw_ = draw.textbbox((0,0),num,font=fn)[2]
        ft  = _font(26)
        tx_ = PAD+22+nw_+16
        for tl in _wrap(bul, ft, W-PAD-tx_-24, draw, 1):
            draw.text((tx_,by+18), tl, font=ft, fill=WHITE)
        fd  = _font(20, False)
        dy_ = by+56
        for dl in _wrap(desc, fd, W-PAD-tx_-24, draw, 2):
            draw.text((tx_,dy_), dl, font=fd, fill=MUTED); dy_+=28
        by += 122

    # Stats strip
    TR_Y = BEN_Y + 420
    TR_H = 130
    draw.rectangle([0,TR_Y,W,TR_Y+TR_H], fill=BDARK)
    stats = [("100+","Projects Done"),("8+","Years Exp"),("98%","Satisfaction")]
    cw_   = W//3
    for idx,(val,lbl) in enumerate(stats):
        cx = idx*cw_+cw_//2
        fv = _font(44); fl = _font(19, False)
        vw = draw.textbbox((0,0),val,font=fv)[2]
        lw = draw.textbbox((0,0),lbl,font=fl)[2]
        draw.text((cx-vw//2,TR_Y+14), val, font=fv, fill=BBRIGHT)
        draw.text((cx-lw//2,TR_Y+66), lbl, font=fl, fill=LBLUE)
        if idx<2:
            draw.rectangle([idx*cw_+cw_-1,TR_Y+20,idx*cw_+cw_+1,TR_Y+TR_H-20],fill=(80,110,180))

    # CTA
    CTA_Y = TR_Y + TR_H
    CTA_H = H - CTA_Y
    for i in range(CTA_H):
        t=i/max(CTA_H-1,1)
        c=tuple(int((8,12,38)[j]+t*(NAVY[j]-(8,12,38)[j])) for j in range(3))
        draw.line([(0,CTA_Y+i),(W,CTA_Y+i)], fill=c)
    draw = ImageDraw.Draw(img)
    bf   = _font(28)
    bw_  = draw.textbbox((0,0),cta,font=bf)[2]+72
    bh_  = 66
    bx_  = (W-bw_)//2
    by_  = CTA_Y+36
    _rr(draw,[bx_,by_,bx_+bw_,by_+bh_],33,BBRIGHT)
    tw_  = draw.textbbox((0,0),cta,font=bf)[2]
    th_  = draw.textbbox((0,0),cta,font=bf)[3]
    draw.text((bx_+(bw_-tw_)//2,by_+(bh_-th_)//2-2), cta, font=bf, fill=WHITE)
    wf  = _font(20, False)
    info= f"{BRAND_WEB}  |  {BRAND_PHONE}"
    iw  = draw.textbbox((0,0),info,font=wf)[2]
    draw.text(((W-iw)//2, by_+bh_+18), info, font=wf, fill=MUTED)

    return img


# ═══════════════════════════════════════════════════════════════════════════════
# Template 5 — WHAT WE BUILD (portrait 1080x1350)
# Blue gradient header + 4 detailed service cards + CTA
# ═══════════════════════════════════════════════════════════════════════════════

def _tpl_what_we_build(hl, bullets, cta, color, photo=None, intro_label="WE OFFER"):
    W, H    = SIZE, HEIGHT
    BDARK   = (  0,  36, 130)
    BBRIGHT = (  1, 146, 239)
    NAVY    = (  6,  10,  28)
    DARK    = ( 10,  14,  38)
    WHITE   = (255, 255, 255)
    MUTED   = (160, 185, 235)
    LBLUE   = (220, 235, 255)
    PAD     = 52

    img  = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Header
    HH = 90
    draw.rectangle([0, 0, W, HH], fill=(8,12,34))
    draw.rectangle([0, HH-5, W, HH], fill=BBRIGHT)
    img  = _paste_logo(img, PAD, (HH-52)//2, white=True)
    draw = ImageDraw.Draw(img)
    tf   = _font(20, False)
    tw   = draw.textbbox((0,0), BRAND_TAG, font=tf)[2]
    draw.text((W-PAD-tw, (HH-22)//2), BRAND_TAG, font=tf, fill=MUTED)

    # Title section
    TS_Y, TS_H = HH, 130
    for i in range(TS_H):
        t=i/max(TS_H-1,1)
        c=tuple(int(BDARK[j]+t*((10,14,40)[j]-BDARK[j])) for j in range(3))
        draw.line([(0,TS_Y+i),(W,TS_Y+i)], fill=c)
    draw = ImageDraw.Draw(img)
    ft1  = _font(21, False)
    ft2  = _font(62)
    sub_t= "FULL-SERVICE DIGITAL AGENCY"
    stw  = draw.textbbox((0,0),sub_t,font=ft1)[2]
    draw.text(((W-stw)//2,TS_Y+12), sub_t, font=ft1, fill=BBRIGHT)
    main_t = hl[:20] if len(hl)>20 else hl
    mtw    = draw.textbbox((0,0),main_t,font=ft2)[2]
    draw.text(((W-mtw)//2,TS_Y+42), main_t, font=ft2, fill=WHITE)

    # 4 service cards
    CS = TS_Y+TS_H+8
    CH = 200; CG = 12
    svcs = [
        ("Website Design & Dev","Fast, modern sites that convert. WordPress, custom HTML, landing pages."),
        ("SEO & Google Ranking","Get on Page 1. Technical SEO, local SEO, keyword strategy & link building."),
        ("UGC & AI Video Ads","Scroll-stopping video content for social ads and ecom product pages."),
        ("eCommerce Solutions","Shopify, WooCommerce stores built to sell. CRO-optimized product pages."),
    ]
    for idx, (title, desc) in enumerate(svcs):
        cy = CS + idx*(CH+CG)
        cb = (14,18,50) if idx%2==0 else (10,14,38)
        _rr(draw,[PAD//2,cy,W-PAD//2,cy+CH],20,cb)
        sc = BBRIGHT if idx%2==0 else BDARK
        draw.rounded_rectangle([PAD//2,cy,PAD//2+8,cy+CH],radius=4,fill=sc)
        fn  = _font(52)
        num = f"0{idx+1}"
        draw.text((PAD//2+22,cy+14), num, font=fn, fill=sc)
        nw_ = draw.textbbox((0,0),num,font=fn)[2]
        fct = _font(30)
        tx_ = PAD//2+22+nw_+20
        for tl in _wrap(title, fct, W-PAD//2-tx_-30, draw, 1):
            draw.text((tx_,cy+22), tl, font=fct, fill=WHITE)
        fcd = _font(22, False)
        dy2 = cy+70
        for dl in _wrap(desc, fcd, W-PAD//2-tx_-30, draw, 2):
            draw.text((tx_,dy2), dl, font=fcd, fill=MUTED); dy2+=32
        lm_f = _font(19, False)
        lm_t = "Learn More  >"
        lmw  = draw.textbbox((0,0),lm_t,font=lm_f)[2]
        draw.text((W-PAD-lmw, cy+CH-30), lm_t, font=lm_f, fill=BBRIGHT)

    # CTA
    CE = CS+4*(CH+CG)
    for i in range(H-CE):
        t=i/max(H-CE-1,1)
        c=tuple(int(BDARK[j]+t*(NAVY[j]-BDARK[j])) for j in range(3))
        draw.line([(0,CE+i),(W,CE+i)], fill=c)
    draw = ImageDraw.Draw(img)
    tl_f = _font(26, False)
    tl_t = "Ready to grow your business online?"
    tlw  = draw.textbbox((0,0),tl_t,font=tl_f)[2]
    draw.text(((W-tlw)//2, CE+22), tl_t, font=tl_f, fill=LBLUE)
    bf   = _font(28)
    bw_  = draw.textbbox((0,0),cta,font=bf)[2]+68
    bh_  = 64
    bx_  = (W-bw_)//2
    by_  = CE+72
    _rr(draw,[bx_,by_,bx_+bw_,by_+bh_],32,BBRIGHT)
    tw_  = draw.textbbox((0,0),cta,font=bf)[2]
    th_  = draw.textbbox((0,0),cta,font=bf)[3]
    draw.text((bx_+(bw_-tw_)//2,by_+(bh_-th_)//2-2), cta, font=bf, fill=WHITE)
    wf   = _font(20, False)
    info = f"{BRAND_WEB}  |  {BRAND_PHONE}"
    iw   = draw.textbbox((0,0),info,font=wf)[2]
    draw.text(((W-iw)//2, by_+bh_+16), info, font=wf, fill=MUTED)

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
