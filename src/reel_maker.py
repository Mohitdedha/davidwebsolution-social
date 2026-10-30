"""
Reel generator for David Web Solution.
Creates a 1080x1920 vertical MP4 (15s) using Pillow frames + FFmpeg.
Audio: gTTS voiceover + royalty-free tech background music (mixed with FFmpeg).
No moviepy needed — pure FFmpeg + PIL + gTTS.
"""
import io, os, random, subprocess, tempfile, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests as _req

# Royalty-free IT/tech ambient music from Pixabay (CC0 license)
# These are direct MP3 download URLs — no API key needed
_TECH_MUSIC_URLS = [
    "https://cdn.pixabay.com/audio/2024/03/13/audio_c8d84b9892.mp3",  # corporate tech
    "https://cdn.pixabay.com/audio/2023/10/20/audio_b5b8b2b4e0.mp3",  # digital innovation
    "https://cdn.pixabay.com/audio/2024/01/15/audio_a8f94c2b5d.mp3",  # modern business
    "https://cdn.pixabay.com/audio/2023/08/16/audio_d18e4e0b26.mp3",  # tech background
    "https://cdn.pixabay.com/audio/2023/11/07/audio_e9c2f18a3b.mp3",  # startup vibe
]


def _fetch_music(tmpdir: str) -> str | None:
    """Download a random tech background track. Returns local path or None."""
    url = random.choice(_TECH_MUSIC_URLS)
    try:
        r = _req.get(url, timeout=15, stream=True)
        if r.status_code == 200:
            path = os.path.join(tmpdir, "bg_music.mp3")
            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            print(f"[REEL] Background music downloaded")
            return path
    except Exception as e:
        print(f"[REEL] Music fetch failed: {e}")
    return None


def _make_voiceover(topic: dict, tmpdir: str) -> str | None:
    """Generate TTS voiceover using gTTS. Returns local MP3 path or None."""
    try:
        from gtts import gTTS
    except ImportError:
        print("[REEL] gTTS not installed — no voiceover")
        return None

    # Build a natural-sounding script
    lines = []
    eyebrow = topic.get("eyebrow", "").title()
    headline = topic.get("headline", [])
    sub = topic.get("sub", "")
    pills = topic.get("pills", [])
    cta = topic.get("cta", "Contact us today")

    if eyebrow:
        lines.append(eyebrow + ".")
    if headline:
        lines.append(" ".join(headline) + ".")
    if sub:
        lines.append(sub + ".")
    for title, desc in pills[:3]:
        lines.append(f"{title}. {desc}.")
    lines.append(cta + ". David Web Solution.")

    script = " ".join(lines)
    print(f"[REEL] TTS script: {script[:100]}...")

    try:
        tts = gTTS(text=script, lang="en", slow=False)
        vo_path = os.path.join(tmpdir, "voiceover.mp3")
        tts.save(vo_path)
        print("[REEL] Voiceover generated")
        return vo_path
    except Exception as e:
        print(f"[REEL] TTS failed: {e}")
        return None

SIZE_W, SIZE_H = 1080, 1920
FPS     = 30
DURATION = 15   # seconds
FRAMES  = FPS * DURATION

NAVY   = (5,  12, 31)
BLUE   = (26, 86, 219)
YELLOW = (245, 184, 0)
WHITE  = (255, 255, 255)
MUTED  = (139, 163, 201)

# ── Font loader ───────────────────────────────────────────────────────────────
def _font(size, bold=True):
    dirs = ["C:/Windows/Fonts/", "/usr/share/fonts/truetype/dejavu/",
            "/usr/share/fonts/truetype/liberation/"]
    names_b = ["arialbd.ttf","Arial Bold.ttf","DejaVuSans-Bold.ttf","LiberationSans-Bold.ttf"]
    names_r = ["arialmt.ttf","Arial.ttf","DejaVuSans.ttf","LiberationSans-Regular.ttf"]
    for d in dirs:
        for n in (names_b if bold else names_r):
            p = os.path.join(d, n)
            if os.path.exists(p):
                try: return ImageFont.truetype(p, size)
                except: pass
    return ImageFont.load_default()

def _wrap(text, font, max_w, draw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def _load_logo():
    path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if not os.path.exists(path):
        return None
    try:
        logo = Image.open(path).convert("RGBA")
        px = logo.load()
        for y in range(logo.height):
            for x in range(logo.width):
                r, g, b, a = px[x, y]
                if r > 215 and g > 215 and b > 215:
                    px[x, y] = (r, g, b, 0)
        bb = logo.getbbox()
        if bb: logo = logo.crop(bb)
        out = Image.new("RGBA", logo.size, (0,0,0,0))
        opx, lpx = out.load(), logo.load()
        for y in range(logo.height):
            for x in range(logo.width):
                r, g, b, a = lpx[x, y]
                if a > 10: opx[x, y] = (255,255,255,a)
        logo = out
        logo.thumbnail((260, 80), Image.LANCZOS)
        return logo
    except: return None

def _fetch_bg(query: str):
    px_key = os.environ.get("PIXABAY_API_KEY", "")
    if not px_key:
        return None
    try:
        r = _req.get("https://pixabay.com/api/", params={
            "key": px_key, "q": query + " technology office",
            "image_type": "photo", "orientation": "vertical",
            "per_page": 10, "safesearch": "true", "min_width": 800,
        }, timeout=10)
        hits = r.json().get("hits", [])
        if not hits: return None
        url = random.choice(hits[:5]).get("webformatURL")
        resp = _req.get(url, timeout=15)
        bg = Image.open(io.BytesIO(resp.content)).convert("RGB")
        bg = bg.resize((SIZE_W, SIZE_H), Image.LANCZOS)
        bg = ImageEnhance.Brightness(bg).enhance(0.35)
        bg = ImageEnhance.Color(bg).enhance(0.5)
        return bg
    except: return None

# ── Build one frame ───────────────────────────────────────────────────────────
def _build_frame(topic: dict, frame_idx: int, bg_base=None, color=None):
    if color is None:
        color = YELLOW
    progress = frame_idx / max(FRAMES - 1, 1)   # 0.0 → 1.0

    img = bg_base.copy().convert("RGBA") if bg_base else Image.new("RGBA", (SIZE_W, SIZE_H), (*NAVY, 255))

    # Dark overlay (fades in slightly)
    ov_alpha = int(160 + 30 * progress)
    overlay = Image.new("RGBA", (SIZE_W, SIZE_H), (*NAVY, ov_alpha))
    img = Image.alpha_composite(img, overlay)

    # Grid lines
    draw = ImageDraw.Draw(img, "RGBA")
    for i in range(0, SIZE_W, 50):
        draw.line([(i,0),(i,SIZE_H)], fill=(*BLUE, 25), width=1)
    for i in range(0, SIZE_H, 50):
        draw.line([(0,i),(SIZE_W,i)], fill=(*BLUE, 20), width=1)

    # Glow top-right
    glow = Image.new("RGBA", (SIZE_W, SIZE_H), (0,0,0,0))
    gd   = ImageDraw.Draw(glow)
    for r in range(500, 0, -25):
        a = int(40 * (1 - r/500))
        gd.ellipse([SIZE_W-300-r, -r, SIZE_W-300+r, r], fill=(*BLUE, a))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    P = 70
    y = 80

    # Logo
    logo = _load_logo()
    if logo:
        img.paste(logo, (P, y), logo)
        y += logo.height + 20
    else:
        f = _font(36); draw.text((P, y), "David Web Solution", font=f, fill=WHITE); y += 50

    # Handle
    fh = _font(28, False)
    draw.text((P, y), "@davidwebsolution", font=fh, fill=MUTED); y += 48

    # Divider
    draw.rectangle([P, y, SIZE_W-P, y+2], fill=(*color, 180)); y += 28

    # Eyebrow pill — slides in from left
    slide_x = int((1 - min(progress * 3, 1)) * (-300))
    ey_font = _font(28, bold=True)
    eyebrow = topic.get("eyebrow", "").upper()
    ew = draw.textlength(eyebrow, font=ey_font) + 40
    draw.rounded_rectangle([P + slide_x, y, P + ew + slide_x, y+44], radius=22, fill=color)
    draw.text((P + 20 + slide_x, y+8), eyebrow, font=ey_font, fill=(10,10,10)); y += 68

    # Headline — fades in word by word
    h1f = _font(88, bold=True)
    h2f = _font(88, bold=True)
    headline = topic.get("headline", ["","",""])
    total_lines = len(headline[:3])
    for idx, line in enumerate(headline[:3]):
        reveal = min(progress * 4 - idx * 0.4, 1.0)
        alpha  = max(0, int(255 * reveal))
        col    = (*color, alpha) if idx == total_lines - 1 else (*WHITE, alpha)
        draw.text((P, y), line, font=(h2f if idx == total_lines-1 else h1f), fill=col)
        y += 96
    y += 16

    # Sub
    sf = _font(34, False)
    sub_reveal = min(progress * 3 - 0.6, 1.0)
    sub_alpha  = max(0, int(200 * sub_reveal))
    draw.text((P, y), topic.get("sub",""), font=sf, fill=(*MUTED, sub_alpha)); y += 56

    # Pills — slide in one by one
    pill_h, pill_gap = 110, 16
    num_font = _font(30, bold=True)
    txt_font = _font(28, bold=True)
    dsc_font = _font(24, False)
    for idx, (title, desc) in enumerate(topic.get("pills", [])[:3]):
        pill_reveal = min(progress * 4 - 1.2 - idx * 0.3, 1.0)
        if pill_reveal <= 0:
            y += pill_h + pill_gap; continue
        pill_alpha = max(0, int(pill_reveal * 255))
        slide_px   = int((1 - min(pill_reveal, 1)) * 200)
        px0, py0 = P + slide_px, y
        px1, py1 = SIZE_W - P + slide_px, y + pill_h
        draw.rounded_rectangle([px0, py0, px1, py1], radius=16,
                                fill=(*BLUE, min(pill_alpha//4, 60)),
                                outline=(*color, min(pill_alpha, 100)), width=1)
        cx, cy_ = px0 + 42, py0 + pill_h//2
        draw.ellipse([cx-22, cy_-22, cx+22, cy_+22], fill=(*color, pill_alpha))
        nw = draw.textlength(str(idx+1), font=num_font)
        draw.text((cx - nw//2, cy_-18), str(idx+1), font=num_font, fill=(*WHITE, pill_alpha))
        tx = px0 + 82
        tw = SIZE_W - P - tx - 10
        draw.text((tx, py0+14), title, font=txt_font, fill=(*WHITE, pill_alpha))
        for dl in _wrap(desc, dsc_font, tw, draw)[:1]:
            draw.text((tx, py0+52), dl, font=dsc_font, fill=(*MUTED, pill_alpha))
        y += pill_h + pill_gap

    y += 20
    # CTA — pulsing scale effect
    cta_reveal = min(progress * 3 - 2.0, 1.0)
    if cta_reveal > 0:
        cta_text  = topic.get("cta", "DM us today")
        cta_font  = _font(38, bold=True)
        cta_alpha = max(0, int(255 * cta_reveal))
        cta_w     = int(draw.textlength(cta_text, font=cta_font)) + 80
        cx0 = SIZE_W//2 - cta_w//2
        draw.rounded_rectangle([cx0, y, cx0+cta_w, y+76], radius=38,
                                fill=(*YELLOW, cta_alpha))
        tw2 = draw.textlength(cta_text, font=cta_font)
        draw.text((SIZE_W//2 - tw2//2, y+18), cta_text, font=cta_font,
                  fill=(*(10,10,10), cta_alpha))
        y += 96

    # Footer
    ff = _font(26, False)
    footer = "Websites  •  SEO  •  AI UGC Ads  |  US & UK brands"
    fw = draw.textlength(footer, font=ff)
    draw.text((SIZE_W//2 - fw//2, SIZE_H - 80), footer, font=ff, fill=(*MUTED, 180))

    return img.convert("RGB")


# ── Main entry ────────────────────────────────────────────────────────────────
def generate_reel(topic: dict) -> bytes | None:
    """Generate a 15s vertical Reel MP4. Returns bytes or None if FFmpeg missing."""
    if not shutil.which("ffmpeg"):
        print("[REEL] FFmpeg not found — skipping reel generation")
        return None

    color_options = [YELLOW, (99,152,255), (245,184,0), (99,255,200), (255,120,100)]
    color = random.choice(color_options)

    bg_query = topic.get("eyebrow", "digital marketing")
    bg_base  = _fetch_bg(bg_query)

    tmpdir = tempfile.mkdtemp()
    try:
        print(f"[REEL] Generating {FRAMES} frames...")
        for i in range(FRAMES):
            frame = _build_frame(topic, i, bg_base, color)
            frame.save(os.path.join(tmpdir, f"frame_{i:05d}.png"))

        silent_path = os.path.join(tmpdir, "silent.mp4")
        out_path    = os.path.join(tmpdir, "reel.mp4")

        # Step 1: Render silent video
        cmd_video = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", os.path.join(tmpdir, "frame_%05d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "23", "-preset", "fast",
            silent_path,
        ]
        r1 = subprocess.run(cmd_video, capture_output=True, timeout=120)
        if r1.returncode != 0:
            print(f"[REEL] FFmpeg video error: {r1.stderr.decode()[:300]}")
            return None

        # Step 2: Generate audio (voiceover + background music)
        vo_path    = _make_voiceover(topic, tmpdir)
        music_path = _fetch_music(tmpdir)

        if vo_path and music_path:
            # Mix: voiceover (full) + music (18% volume), trim to video length
            cmd_audio = [
                "ffmpeg", "-y",
                "-i", silent_path,
                "-i", vo_path,
                "-i", music_path,
                "-filter_complex",
                f"[1:a]apad=whole_dur={DURATION}[vo];"
                f"[2:a]aloop=loop=-1:size=44100,atrim=0:{DURATION},volume=0.18[bg];"
                "[vo][bg]amix=inputs=2:duration=first[aout]",
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-shortest", out_path,
            ]
            r2 = subprocess.run(cmd_audio, capture_output=True, timeout=120)
            if r2.returncode != 0:
                print(f"[REEL] Audio mix error: {r2.stderr.decode()[:200]} — falling back to VO only")
                # Fallback: voiceover only
                cmd_vo = [
                    "ffmpeg", "-y",
                    "-i", silent_path, "-i", vo_path,
                    "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", out_path,
                ]
                subprocess.run(cmd_vo, capture_output=True, timeout=60)
        elif vo_path:
            # Voiceover only (no music)
            cmd_vo = [
                "ffmpeg", "-y",
                "-i", silent_path, "-i", vo_path,
                "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-shortest", out_path,
            ]
            subprocess.run(cmd_vo, capture_output=True, timeout=60)
        else:
            # No audio available — use silent video as final
            out_path = silent_path

        final = out_path if os.path.exists(out_path) else silent_path
        with open(final, "rb") as f:
            video_bytes = f.read()
        print(f"[REEL] Generated: {len(video_bytes)//1024}KB")
        return video_bytes
    except Exception as e:
        print(f"[REEL] Error: {e}")
        return None
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
