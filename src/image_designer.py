"""
Professional branded image designer for David Web Solution.
Generates 1080x1080 posts using Pillow — no external API needed.
4 templates inspired by professional digital marketing agency posts.
"""
import io
import os
import re
import random
from PIL import Image, ImageDraw, ImageFont

SIZE = 1080

BRAND_NAME    = "David Web Solution"
BRAND_WEB     = "davidwebsolution.com"
BRAND_TAG     = "WordPress  |  SEO  |  AI Video  |  Flutter"

CTA_OPTIONS = [
    "DM us to get started",
    "Free consultation -> DM us",
    "Comment GROW below",
    "Book a free call -> DM",
    "Link in bio",
]

PILLAR_COLORS = {
    "wordpress_tip":    (0,   115, 170),
    "seo_tip":          (52,  168,  83),
    "ai_video_ugc":     (124,  58, 237),
    "web_mistake":      (220,  38,  38),
    "client_result":    (8,   145, 178),
    "tool_spotlight":   (217, 119,   6),
    "industry_insight": (30,   64, 175),
}

PILLAR_TEMPLATES = {
    "wordpress_tip":    ["blue_pro",       "clean_light"],
    "seo_tip":          ["gradient_dark",  "blue_pro"],
    "ai_video_ugc":     ["dark_neon",      "gradient_dark"],
    "web_mistake":      ["gradient_dark",  "dark_neon"],
    "client_result":    ["blue_pro",       "clean_light"],
    "tool_spotlight":   ["dark_neon",      "gradient_dark"],
    "industry_insight": ["gradient_dark",  "dark_neon"],
}


# ── Font loading (Ubuntu/Actions + Windows + macOS) ──────────────────────────

def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidates = []
    if bold:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ── Text helpers ─────────────────────────────────────────────────────────────

def _clean(text: str) -> str:
    """Remove non-ASCII characters (emoji etc)."""
    return re.sub(r"[^\x00-\x7F]+", "", text).strip()


def _headline(text: str) -> str:
    first = _clean(text.strip().split("\n")[0])
    return first[:62] + ("..." if len(first) > 62 else "")


def _bullets(text: str) -> list[str]:
    out = []
    for line in text.split("\n")[1:]:
        line = line.strip()
        clean = _clean(re.sub(r"^[•\-*=>#]+\s*", "", line))
        if clean and len(clean) > 8 and not clean.startswith("http"):
            out.append(clean[:58])
        if len(out) >= 4:
            break
    if not out:
        for line in text.split("\n")[1:6]:
            clean = _clean(line.strip())
            if clean and len(clean) > 10:
                out.append(clean[:58])
        out = out[:4]
    return out


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int,
          draw: ImageDraw.ImageDraw) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        test = (cur + " " + word).strip()
        w = draw.textbbox((0, 0), test, font=font)[2]
        if w <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _rr(draw: ImageDraw.ImageDraw, xy, r: int, fill):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    draw.ellipse([x0, y0, x0 + 2*r, y0 + 2*r], fill=fill)
    draw.ellipse([x1 - 2*r, y0, x1, y0 + 2*r], fill=fill)
    draw.ellipse([x0, y1 - 2*r, x0 + 2*r, y1], fill=fill)
    draw.ellipse([x1 - 2*r, y1 - 2*r, x1, y1], fill=fill)


# ── Template 1: Gradient Dark ────────────────────────────────────────────────

def _tpl_gradient_dark(hl: str, bullets: list, cta: str, color: tuple) -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE), (8, 12, 28))
    draw = ImageDraw.Draw(img)

    # Background gradient bands
    for y in range(SIZE):
        t = y / SIZE
        r = int(8  + t * 20)
        g = int(12 + t * 10)
        b = int(28 + t * 40)
        draw.line([(0, y), (SIZE, y)], fill=(r, g, b))

    # Top-right circle accent
    draw.ellipse([700, -120, 1180, 360], fill=(20, 40, 100))
    draw.ellipse([760, -60,  1120, 300], fill=(8, 12, 28))

    # Left pillar stripe
    draw.rectangle([0, 160, 7, 760], fill=color)

    # Brand header
    draw.text((35, 38), BRAND_NAME.upper(), font=_font(26), fill=(255, 255, 255))
    draw.text((35, 72), BRAND_WEB,          font=_font(20, False), fill=(100, 116, 139))

    # Headline
    fh = _font(60)
    hl_lines = _wrap(hl, fh, 820, draw)
    y = 170
    for line in hl_lines[:3]:
        draw.text((35, y), line, font=fh, fill=(255, 255, 255))
        y += draw.textbbox((0, 0), line, font=fh)[3] + 8

    # Divider
    draw.rectangle([35, y + 18, 220, y + 22], fill=color)
    y += 48

    # Bullets
    fb = _font(30, False)
    for b in bullets[:4]:
        draw.text((35, y), "->", font=_font(30), fill=color)
        draw.text((78, y), b,    font=fb,         fill=(203, 213, 225))
        y += 50

    # CTA button
    btn_y = max(y + 36, 870)
    _rr(draw, [35, btn_y, 390, btn_y + 58], 12, color)
    draw.text((55, btn_y + 13), cta, font=_font(26), fill=(255, 255, 255))

    # Footer
    draw.text((35, 1024), BRAND_TAG, font=_font(20, False), fill=(51, 65, 85))

    return img


# ── Template 2: Blue Professional ────────────────────────────────────────────

def _tpl_blue_pro(hl: str, bullets: list, cta: str, color: tuple) -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE), color)
    draw = ImageDraw.Draw(img)

    # Decorative circles on blue section
    r, g, b = color
    lighter = (min(255, r + 40), min(255, g + 40), min(255, b + 40))
    draw.ellipse([-80, -80, 300, 300], fill=lighter)
    draw.ellipse([820, -50, 1140, 270], fill=lighter)

    # White card (lower 62%)
    card_top = 390
    draw.rectangle([0, card_top, SIZE, SIZE], fill=(255, 255, 255))

    # Brand on colored top
    draw.text((48, 42), BRAND_NAME.upper(), font=_font(26),      fill=(255, 255, 255))
    draw.text((48, 76), "AGENCY TIP",       font=_font(20, False), fill=(220, 235, 255))

    # Headline on blue
    fh = _font(62)
    hl_lines = _wrap(hl, fh, 800, draw)
    y = 155
    for line in hl_lines[:3]:
        draw.text((48, y), line, font=fh, fill=(255, 255, 255))
        y += draw.textbbox((0, 0), line, font=fh)[3] + 8

    # Bullets on white
    y = card_top + 40
    fb = _font(30, False)
    for bul in bullets[:4]:
        draw.ellipse([48, y + 10, 64, y + 26], fill=color)
        draw.text((80, y), bul, font=fb, fill=(30, 41, 59))
        y += 52

    # CTA
    btn_y = max(y + 28, 880)
    _rr(draw, [48, btn_y, 420, btn_y + 62], 14, color)
    draw.text((72, btn_y + 14), cta, font=_font(26), fill=(255, 255, 255))

    # Footer
    draw.text((48, 1024), BRAND_WEB, font=_font(22, False), fill=(148, 163, 184))

    return img


# ── Template 3: Dark Neon ────────────────────────────────────────────────────

def _tpl_dark_neon(hl: str, bullets: list, cta: str, color: tuple) -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE), (3, 7, 18))
    draw = ImageDraw.Draw(img)

    # Subtle grid
    for x in range(0, SIZE, 108):
        draw.line([(x, 0), (x, SIZE)], fill=(16, 24, 40), width=1)
    for y in range(0, SIZE, 108):
        draw.line([(0, y), (SIZE, y)], fill=(16, 24, 40), width=1)

    # Top neon bar
    draw.rectangle([0, 0, SIZE, 7], fill=color)

    # Brand
    draw.text((40, 24), BRAND_NAME, font=_font(26),      fill=color)
    draw.text((40, 58), BRAND_WEB,  font=_font(18, False), fill=(55, 65, 81))

    # Headline (2 colors)
    fh = _font(62)
    hl_lines = _wrap(hl, fh, 860, draw)
    y = 130
    for i, line in enumerate(hl_lines[:3]):
        col = (255, 255, 255) if i == 0 else color
        draw.text((40, y), line, font=fh, fill=col)
        y += draw.textbbox((0, 0), line, font=fh)[3] + 8

    y += 28

    # Service boxes 2x2 grid
    fw = _font(24, False)
    for i, bul in enumerate(bullets[:4]):
        bx = 40  + (i % 2) * 512
        by = y   + (i // 2) * 108
        _rr(draw, [bx, by, bx + 488, by + 88], 10, (12, 22, 42))
        draw.rectangle([bx, by, bx + 5, by + 88], fill=color)
        draw.text((bx + 20, by + 26), bul[:36], font=fw, fill=(203, 213, 225))

    y += 248

    # CTA
    btn_y = max(y + 14, 882)
    _rr(draw, [40, btn_y, 430, btn_y + 62], 14, color)
    draw.text((64, btn_y + 14), cta, font=_font(26), fill=(3, 7, 18))

    # Footer
    draw.text((40, 1024), BRAND_TAG, font=_font(20, False), fill=(55, 65, 81))

    return img


# ── Template 4: Clean Light ──────────────────────────────────────────────────

def _tpl_clean_light(hl: str, bullets: list, cta: str, color: tuple) -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE), (248, 250, 252))
    draw = ImageDraw.Draw(img)

    # Top band
    draw.rectangle([0, 0, SIZE, 175], fill=color)

    # Decorative circle top-right
    r, g, b = color
    lighter = (min(255, r + 40), min(255, g + 40), min(255, b + 40))
    draw.ellipse([830, -60, 1130, 240], fill=lighter)

    # Brand on band
    draw.text((44, 34),  BRAND_NAME.upper(), font=_font(26),      fill=(255, 255, 255))
    draw.text((44, 68),  BRAND_TAG,          font=_font(17, False), fill=(220, 235, 255))

    # White card
    draw.rectangle([24, 148, SIZE - 24, SIZE - 24], fill=(255, 255, 255))

    # Headline in card
    fh = _font(54)
    hl_lines = _wrap(hl, fh, 920, draw)
    y = 185
    for line in hl_lines[:3]:
        draw.text((52, y), line, font=fh, fill=(15, 23, 42))
        y += draw.textbbox((0, 0), line, font=fh)[3] + 6

    draw.rectangle([52, y + 14, 52 + 90, y + 18], fill=color)
    y += 44

    # Bullets with colored squares
    fb = _font(30, False)
    for bul in bullets[:4]:
        _rr(draw, [52, y + 6, 74, y + 28], 4, color)
        draw.text((90, y), bul, font=fb, fill=(30, 41, 59))
        y += 54

    # CTA
    btn_y = max(y + 28, 886)
    _rr(draw, [52, btn_y, 440, btn_y + 62], 14, color)
    draw.text((76, btn_y + 14), cta, font=_font(26), fill=(255, 255, 255))

    # Footer line
    draw.rectangle([24, 1010, SIZE - 24, 1011], fill=(226, 232, 240))
    draw.text((52, 1018), BRAND_WEB, font=_font(22, False), fill=(148, 163, 184))

    return img


# ── Public API ────────────────────────────────────────────────────────────────

def design_post(pillar: str, post_text: str) -> bytes:
    """Generate a branded 1080x1080 image. Returns PNG bytes."""
    hl      = _headline(post_text)
    blts    = _bullets(post_text)
    cta     = random.choice(CTA_OPTIONS)
    color   = PILLAR_COLORS.get(pillar, (37, 99, 235))
    tpls    = PILLAR_TEMPLATES.get(pillar, ["gradient_dark", "blue_pro"])
    tpl     = random.choice(tpls)

    dispatch = {
        "gradient_dark": _tpl_gradient_dark,
        "blue_pro":      _tpl_blue_pro,
        "dark_neon":     _tpl_dark_neon,
        "clean_light":   _tpl_clean_light,
    }
    img = dispatch[tpl](hl, blts, cta, color)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    print(f"[DESIGN] Template={tpl} pillar={pillar} size={buf.tell()//1024}KB")
    return buf.getvalue()
