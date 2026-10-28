"""
Informative post generator for David Web Solution.
Dark navy card, 3 frosted pills, yellow CTA — 1080x1080 square.
"""
import io, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SIZE = 1080
NAVY  = (5, 12, 31)
CARD  = (8, 18, 48)
BLUE  = (26, 86, 219)
YELLOW = (245, 184, 0)
WHITE  = (255, 255, 255)
MUTED  = (139, 163, 201)
DIM    = (74, 96, 144)
PILL_BG = (26, 86, 219, 50)   # semi-transparent
PILL_BORDER = (99, 152, 255, 70)

# Hashtag pool — 5 trending per post
_HASHTAG_POOL = [
    # Global / evergreen
    "#DigitalMarketing", "#WebDesign", "#SEO", "#MarketingTips", "#OnlineMarketing",
    "#BusinessGrowth", "#SocialMediaMarketing", "#ContentMarketing", "#Entrepreneur",
    "#WebDevelopment", "#GoogleAds", "#InstagramMarketing", "#Branding", "#LeadGeneration",
    "#MarketingStrategy", "#StartupLife", "#DigitalAgency", "#AIMarketing",
    # US focused
    "#USBusiness", "#AmericanBusiness", "#SmallBusinessUSA", "#USMarketing", "#USEntrepreneur",
    # UK focused
    "#UKBusiness", "#UKMarketing", "#UKEntrepreneur", "#SmallBusinessUK", "#LondonBusiness",
    # Global ecom / agency
    "#EcommerceMarketing", "#GlobalBusiness", "#AgencyLife", "#GrowthHacking", "#ScaleUp",
]

def _hashtags():
    return " ".join(random.sample(_HASHTAG_POOL, 5))

def _load_font(size, bold=False):
    dirs = [
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/truetype/liberation/",
        "/System/Library/Fonts/",
        "C:/Windows/Fonts/",
    ]
    candidates_bold = ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf", "Arial.ttf", "arialmt.ttf"]
    candidates_reg  = ["DejaVuSans.ttf", "LiberationSans-Regular.ttf", "Arial.ttf", "arialmt.ttf"]
    candidates = candidates_bold if bold else candidates_reg
    for d in dirs:
        for c in candidates:
            p = os.path.join(d, c)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    return ImageFont.load_default()

def _load_logo(max_w=220, max_h=70):
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
        # Make white
        out = Image.new("RGBA", logo.size, (0, 0, 0, 0))
        opx = out.load(); lpx = logo.load()
        for y in range(logo.size[1]):
            for x in range(logo.size[0]):
                r, g, b, a = lpx[x, y]
                if a > 10:
                    opx[x, y] = (255, 255, 255, a)
        logo = out
        logo.thumbnail((max_w, max_h), Image.LANCZOS)
        return logo
    except Exception:
        return None

def _wrap(text, font, max_w, draw):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def _rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def generate_informative_image(topic: dict) -> bytes:
    img = Image.new("RGB", (SIZE, SIZE), NAVY)
    draw = ImageDraw.Draw(img, "RGBA")

    # Background grid — more visible
    for i in range(0, SIZE, 36):
        draw.line([(i, 0), (i, SIZE)], fill=(26, 86, 219, 30), width=1)
        draw.line([(0, i), (SIZE, i)], fill=(26, 86, 219, 25), width=1)

    # Diagonal accent lines for depth
    for i in range(-SIZE, SIZE * 2, 120):
        draw.line([(i, 0), (i + SIZE // 2, SIZE)], fill=(40, 100, 255, 12), width=1)

    # Strong top-right glow
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(400, 0, -20):
        alpha = int(35 * (1 - r / 400))
        gd.ellipse([SIZE - 420 - r, -r, SIZE - 420 + r, r], fill=(26, 86, 219, alpha))
    # Bottom-left accent glow
    for r in range(300, 0, -20):
        alpha = int(20 * (1 - r / 300))
        gd.ellipse([-r, SIZE - r, r, SIZE + r], fill=(245, 184, 0, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    P = 52  # padding
    W = SIZE - 2 * P  # content width
    y = P

    # ── Header: logo + handle ──────────────────────────────────────────
    logo = _load_logo()
    handle_font = _load_font(28)
    if logo:
        img.paste(logo, (P, y), logo)
        logo_h = logo.size[1]
    else:
        # Fallback text logo
        lf = _load_font(32, bold=True)
        draw.text((P, y), "David Web Solution", font=lf, fill=WHITE)
        logo_h = 40
    handle_text = "@davidwebsolution"
    handle_w = draw.textlength(handle_text, font=handle_font)
    draw.text((SIZE - P - handle_w, y + (logo_h - 28) // 2), handle_text, font=handle_font, fill=MUTED)
    y += logo_h + 36

    # ── Eyebrow ────────────────────────────────────────────────────────
    ey_font = _load_font(24, bold=True)
    eyebrow = topic.get("eyebrow", "").upper()
    draw.text((P, y), eyebrow, font=ey_font, fill=YELLOW)
    y += 34

    # ── Headline (3 lines) ─────────────────────────────────────────────
    h1_font = _load_font(72, bold=True)
    h2_font = _load_font(72, bold=True)
    headline = topic.get("headline", ["", "", ""])
    line_gap = 78
    for idx, line in enumerate(headline[:3]):
        color = YELLOW if idx == len(headline) - 1 else WHITE
        draw.text((P, y), line, font=h1_font, fill=color)
        y += line_gap
    y += 8

    # ── Sub ────────────────────────────────────────────────────────────
    sub_font = _load_font(30)
    draw.text((P, y), topic.get("sub", ""), font=sub_font, fill=MUTED)
    y += 48

    # ── Pills ──────────────────────────────────────────────────────────
    pill_h = 108
    pill_gap = 14
    num_font = _load_font(28, bold=True)
    pt_font = _load_font(28, bold=True)
    pd_font = _load_font(24)

    for idx, (title, desc) in enumerate(topic.get("pills", [])[:3]):
        px0, py0 = P, y
        px1, py1 = SIZE - P, y + pill_h
        # Pill background
        _rounded_rect(draw, (px0, py0, px1, py1), radius=14,
                      fill=(26, 86, 219, 48), outline=(99, 152, 255, 60), width=1)
        # Number circle
        cx, cy = px0 + 22 + 20, py0 + pill_h // 2
        draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=BLUE)
        num_w = draw.textlength(str(idx + 1), font=num_font)
        draw.text((cx - num_w // 2, cy - 16), str(idx + 1), font=num_font, fill=WHITE)
        # Text
        tx = px0 + 76
        tw = SIZE - P - tx - 10
        draw.text((tx, py0 + 14), title, font=pt_font, fill=WHITE)
        desc_lines = _wrap(desc, pd_font, tw, draw)
        dy = py0 + 50
        for dl in desc_lines[:2]:
            draw.text((tx, dy), dl, font=pd_font, fill=MUTED)
            dy += 28
        y += pill_h + pill_gap

    y += 16

    # ── CTA button ─────────────────────────────────────────────────────
    cta_font = _load_font(32, bold=True)
    cta_text = topic.get("cta", "DM us today")
    cta_h = 80
    _rounded_rect(draw, (P, y, SIZE - P, y + cta_h), radius=14, fill=YELLOW)
    cta_w = draw.textlength(cta_text, font=cta_font)
    draw.text((SIZE // 2 - cta_w // 2, y + (cta_h - 34) // 2), cta_text, font=cta_font, fill=(10, 10, 10))
    y += cta_h + 18

    # ── Footer ─────────────────────────────────────────────────────────
    footer_font = _load_font(24)
    footer = "Websites  •  SEO  •  AI UGC Ads  |  US & UK brands"
    fw = draw.textlength(footer, font=footer_font)
    draw.text((SIZE // 2 - fw // 2, y), footer, font=footer_font, fill=DIM)
    # Footer lines
    lw = (SIZE // 2 - fw // 2 - P - 10)
    draw.line([(P, y + 12), (P + max(lw, 20), y + 12)], fill=DIM, width=1)
    draw.line([(SIZE - P - max(lw, 20), y + 12), (SIZE - P, y + 12)], fill=DIM, width=1)

    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=90)
    return buf.getvalue()


def build_caption(topic: dict) -> str:
    eyebrow = topic.get("eyebrow", "").title()
    sub = topic.get("sub", "")
    pills = topic.get("pills", [])
    cta = topic.get("cta", "DM us today")
    lines = [
        f"{sub}\n",
    ]
    for i, (title, desc) in enumerate(pills[:3], 1):
        lines.append(f"{i}. {title} — {desc}")
    lines.append(f"\n{cta}")
    lines.append(_hashtags())
    return "\n".join(lines)
