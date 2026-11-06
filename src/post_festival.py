"""
post_festival.py - Festival card generator for DWS Instagram
Requires: pillow numpy requests
Fonts: install fonts-noto-color-emoji fonts-noto on Ubuntu
"""
import os, sys, datetime, argparse, textwrap, requests, base64, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

FESTIVALS = {
    "11-06": {"name": "Dhanteras",         "sub": "Dhan Teras Ki Shubhkamnayen",    "symbol": "DIYA",        "msg": "May Goddess Lakshmi bless your home with wealth, health and happiness on this auspicious Dhanteras."},
    "11-07": {"name": "Diwali",             "sub": "Deepawali Ki Hardik Shubhkamnayen","symbol": "DIYAS",      "msg": "Wishing you a Diwali filled with light, joy and prosperity. May every dream of yours shine bright!"},
    "11-08": {"name": "Diwali",             "sub": "Deepawali Ki Hardik Shubhkamnayen","symbol": "DIYAS",      "msg": "Wishing you a Diwali filled with light, joy and prosperity. May every dream of yours shine bright!"},
    "11-09": {"name": "Govardhan Puja",     "sub": "Govardhan Puja Ki Shubhkamnayen","symbol": "PUJA",        "msg": "On this sacred day, may Lord Krishna shower blessings of strength, success and abundance upon you."},
    "11-10": {"name": "Bhai Dooj",          "sub": "Bhai Dooj Ki Shubhkamnayen",    "symbol": "BOND",        "msg": "Celebrating the beautiful bond of siblings. May this relationship grow stronger every year."},
    "12-25": {"name": "Christmas",          "sub": "Christmas Ki Shubhkamnayen",    "symbol": "STAR",        "msg": "Wishing you a Merry Christmas filled with joy, warmth and the magic of the festive season!"},
    "01-01": {"name": "New Year",           "sub": "Nav Varsh Ki Shubhkamnayen",    "symbol": "NEW",         "msg": "Wishing you a Happy New Year full of success, growth and exciting new opportunities!"},
    "01-26": {"name": "Republic Day",       "sub": "Gantantra Divas Ki Shubhkamnayen","symbol": "INDIA",     "msg": "Happy Republic Day! Celebrating the spirit of unity, democracy and progress. Jai Hind!"},
    "08-15": {"name": "Independence Day",   "sub": "Swatantrata Divas Ki Shubhkamnayen","symbol": "INDIA",   "msg": "Happy Independence Day! Celebrating 78 years of freedom, unity and progress. Jai Hind!"},
    "03-14": {"name": "Holi",               "sub": "Holi Ki Shubhkamnayen",         "symbol": "COLORS",      "msg": "May the colors of Holi fill your life with happiness, health and prosperity. Happy Holi!"},
    "10-02": {"name": "Gandhi Jayanti",     "sub": "Gandhi Jayanti Ki Shubhkamnayen","symbol": "PEACE",      "msg": "Honoring the Father of the Nation and his timeless values of truth, peace and service to humanity."},
    "10-24": {"name": "Dussehra",           "sub": "Dussehra Ki Shubhkamnayen",     "symbol": "VICTORY",     "msg": "Happy Dussehra! May the victory of good over evil inspire us to overcome every challenge!"},
    "09-07": {"name": "Ganesh Chaturthi",   "sub": "Ganesh Chaturthi Ki Shubhkamnayen","symbol": "BAPPA",    "msg": "Ganpati Bappa Morya! May Lord Ganesha remove all obstacles and bless you with wisdom and prosperity."},
    "10-12": {"name": "Navratri",           "sub": "Navratri Ki Shubhkamnayen",     "symbol": "SHAKTI",      "msg": "Wishing you a blessed Navratri! May Goddess Durga shower her divine blessings upon you."},
    "04-14": {"name": "Dr. Ambedkar Jayanti","sub": "Dr. Ambedkar Jayanti",         "symbol": "RESPECT",     "msg": "Celebrating Dr. B.R. Ambedkar on his birth anniversary. His legacy of equality inspires us all."},
}

HASHTAGS = {
    "Dhanteras":       "#HappyDhanteras #Dhanteras2026 #ShubhDhanteras #DavidWebSolution #DigitalMarketing #WebDesign #FestiveGreetings #Diwali2026",
    "Diwali":          "#HappyDiwali #Diwali2026 #ShubhDiwali #DavidWebSolution #DigitalMarketing #WebDesign #FestiveGreetings #Deepawali",
    "Govardhan Puja":  "#GovardhanPuja #DavidWebSolution #DigitalMarketing #WebDesign #FestiveGreetings",
    "Bhai Dooj":       "#HappyBhaiDooj #BhaiDooj2026 #DavidWebSolution #DigitalMarketing #SiblingLove",
    "Christmas":       "#MerryChristmas #Christmas2026 #DavidWebSolution #DigitalMarketing #WebDesign",
    "New Year":        "#HappyNewYear #NewYear2027 #DavidWebSolution #DigitalMarketing",
    "Republic Day":    "#RepublicDay #JaiHind #DavidWebSolution #ProudIndian",
    "Independence Day":"#IndependenceDay #JaiHind #DavidWebSolution #ProudIndian",
    "Holi":            "#HappyHoli #Holi2027 #FestivalOfColors #DavidWebSolution",
}

def make_caption(f):
    tags = HASHTAGS.get(f["name"], "#" + f["name"].replace(" ","") + " #DavidWebSolution #DigitalMarketing")
    return (f"~ {f['name']} Greetings from David Web Solution ~\n\n"
            f"{f['msg']}\n\n"
            f"At David Web Solution, we help Indian businesses grow globally "
            f"with stunning websites, powerful SEO & AI-driven digital marketing.\n\n"
            f"{f['sub']}\n\n"
            f"Call: +91 82854 23939 | Web: davidwebsolution.com\n\n"
            f"{tags} #IndianBusiness #SmallBusiness #StartupIndia")

SIZE = 1080
NAVY  = (4,   8,  26)
NAVY2 = (8,  15,  40)
GOLD  = (201,147,  10)
GOLD2 = (240,180,  41)
WHITE = (255,255, 255)
MUTED = (140,160, 200)

def load_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansBold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def draw_centered(draw, text, y, font, color, shadow=False):
    if shadow:
        bbox = draw.textbbox((0,0), text, font=font)
        w = bbox[2]-bbox[0]
        x = (SIZE-w)//2
        draw.text((x+2, y+2), text, font=font, fill=(0,0,0,80))
    bbox = draw.textbbox((0,0), text, font=font)
    w = bbox[2]-bbox[0]
    x = (SIZE-w)//2
    draw.text((x, y), text, font=font, fill=color)
    return bbox[3]-bbox[1]

def make_image(f, logo_path, out_path):
    img = Image.new("RGBA", (SIZE, SIZE), (*NAVY, 255))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(SIZE):
        t = y / SIZE
        c = tuple(int(NAVY[i] + (NAVY2[i]-NAVY[i])*t) for i in range(3))
        draw.line([(0,y),(SIZE,y)], fill=c)



    # Border frame
    pad = 30
    draw.rectangle([pad, pad, SIZE-pad, SIZE-pad], outline=(*GOLD2, 90), width=2)
    draw.rectangle([pad+7, pad+7, SIZE-pad-7, SIZE-pad-7], outline=(*GOLD, 35), width=1)

    # Corner L-shapes
    clen = 40
    for x1,y1,dx,dy in [(pad,pad,1,1),(SIZE-pad,pad,-1,1),(pad,SIZE-pad,1,-1),(SIZE-pad,SIZE-pad,-1,-1)]:
        draw.line([(x1,y1),(x1+dx*clen,y1)], fill=GOLD2, width=3)
        draw.line([(x1,y1),(x1,y1+dy*clen)], fill=GOLD2, width=3)

    # ── HEADER ──
    # DWS Logo
    logo_placed = False
    if logo_path and Path(logo_path).exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            data = np.array(logo)
            # Remove white background
            mask = (data[:,:,0]>215) & (data[:,:,1]>215) & (data[:,:,2]>215)
            data[mask,3] = 0
            logo = Image.fromarray(data)
            bbox = logo.getbbox()
            if bbox:
                logo = logo.crop(bbox)
            # Scale to 56px height
            lh = 75
            lw = int(logo.width * lh / logo.height)
            logo = logo.resize((lw, lh), Image.LANCZOS)
            img.paste(logo, (52, 32), logo)
            logo_placed = True
        except Exception as e:
            print(f"Logo error: {e}")
    
    if not logo_placed:
        fn_lg = load_font(13, True)
        # Draw diamond symbol
        draw.polygon([(70,55),(82,43),(94,55),(82,67)], fill=GOLD2)
        draw.polygon([(70,55),(82,43),(94,55),(82,67)], outline=GOLD, width=1)
        draw.text((100, 44), "DAVID WEB SOLUTION", font=fn_lg, fill=WHITE)

    # Handle
    fn_hd = load_font(19)
    h_text = "@davidwebsolution"
    hb = draw.textbbox((0,0), h_text, font=fn_hd)
    draw.text((SIZE-52-(hb[2]-hb[0]), 44), h_text, font=fn_hd, fill=MUTED)

    # Header divider
    draw.line([(52, 102), (SIZE-52, 102)], fill=(*GOLD, 50), width=1)

    # ── DECORATIVE SYMBOL (center top) ──
    fn_sym = load_font(32, True)
    sym_text = "* " + f["name"].upper() + " *"
    cy_start = 250
    h = draw_centered(draw, sym_text, cy_start, fn_sym, GOLD2, shadow=False)

    # Decorative diya SVG-like shape (drawn with Pillow)
    # Flame - teardrop polygon (not oval)
    cx, cy2 = SIZE//2, cy_start + 150
    pts = [(cx,cy2-80),(cx+35,cy2-30),(cx+22,cy2+10),(cx-22,cy2+10),(cx-35,cy2-30)]
    draw.polygon(pts, fill=(*GOLD2, 240))
    pts2 = [(cx,cy2-65),(cx+18,cy2-20),(cx+11,cy2+6),(cx-11,cy2+6),(cx-18,cy2-20)]
    draw.polygon(pts2, fill=(255,240,160))
    # Bowl
    draw.ellipse([cx-80, cy2+5, cx+80, cy2+80], fill=(180,110,15))
    draw.arc([cx-80, cy2+5, cx+80, cy2+80], 0, 180, fill=(*GOLD, 180), width=2)
    # Sparkles
    for sx, sy in [(cx-70, cy2-30),(cx+65, cy2-20),(cx+40, cy2-55),(cx-45, cy2-50)]:
        draw.ellipse([sx-3,sy-3,sx+3,sy+3], fill=(*GOLD2, 160))

    # ── HEADLINE ──
    fn_title = load_font(80, True)
    fn_title_sm = load_font(60, True)
    y_title = cy2 + 100

    words = f["name"].split()
    if len(f["name"]) <= 10:
        h = draw_centered(draw, f["name"], y_title, fn_title, WHITE, shadow=True)
        y_title += h + 10
    else:
        line1 = " ".join(words[:len(words)//2])
        line2 = " ".join(words[len(words)//2:])
        h1 = draw_centered(draw, line1, y_title, fn_title_sm, WHITE, shadow=True)
        y_title += h1 + 8
        h2 = draw_centered(draw, line2, y_title, fn_title_sm, WHITE, shadow=True)
        y_title += h2 + 8

    # Sub-line (romanized Hindi)
    fn_sub = load_font(28)
    h = draw_centered(draw, f["sub"], y_title + 8, fn_sub, (*GOLD2, 220))
    y_div = y_title + 8 + h + 20

    # Gold divider
    draw.line([(SIZE//2-80, y_div), (SIZE//2+80, y_div)], fill=GOLD, width=2)

    # Message text
    fn_msg = load_font(27)
    wrapped = textwrap.wrap(f["msg"], width=46)
    y_msg = y_div + 20
    for ln in wrapped[:3]:
        h = draw_centered(draw, ln, y_msg, fn_msg, (210, 220, 245))
        y_msg += h + 8

    # Hashtags
    fn_hash = load_font(20)
    htag = HASHTAGS.get(f["name"], "#DavidWebSolution")
    draw_centered(draw, htag[:65], y_msg + 25, fn_hash, (*GOLD, 85))
    # ── FOOTER ──
    fn_ft = load_font(22)
    fn_cta = load_font(20, True)
    
    draw.line([(52, SIZE-110),(SIZE-52,SIZE-110)], fill=(*GOLD,50), width=1)
    draw.text((52, SIZE-82), "davidwebsolution.com  |  +91 82854 23939", font=fn_ft, fill=MUTED)

    # CTA button
    cta = "FREE QUOTE"
    cb = draw.textbbox((0,0), cta, font=fn_cta)
    bw = cb[2]-cb[0]+32; bh = 36
    bx = SIZE-52-bw; by = SIZE-90
    draw.rounded_rectangle([bx,by,bx+bw,by+bh], radius=18, fill=GOLD2)
    draw.text((bx+16, by+8), cta, font=fn_cta, fill=NAVY)

    img.convert("RGB").save(out_path, "JPEG", quality=95)
    print(f"Saved: {out_path}")
    return out_path

def upload_to_imgbb(path, key):
    with open(path,"rb") as fh: b64 = base64.b64encode(fh.read()).decode()
    r = requests.post("https://api.imgbb.com/1/upload", data={"key":key,"image":b64})
    r.raise_for_status()
    return r.json()["data"]["url"]

def post_to_instagram(url, caption, uid, token):
    r1 = requests.post(
        f"https://graph.facebook.com/v19.0/{uid}/media",
        data={"image_url":url,"caption":caption,"access_token":token})
    r1.raise_for_status()
    container_id = r1.json()["id"]

    for attempt in range(15):
        time.sleep(4)
        status_r = requests.get(
            f"https://graph.facebook.com/v19.0/{container_id}",
            params={"fields": "status_code", "access_token": token})
        status_r.raise_for_status()
        status_code = status_r.json().get("status_code", "")
        print(f"Container status ({attempt+1}): {status_code}")
        if status_code == "FINISHED":
            break
        if status_code == "ERROR":
            raise Exception(f"Container failed: {status_r.json()}")

    r2 = requests.post(
        f"https://graph.facebook.com/v19.0/{uid}/media_publish",
        data={"creation_id":container_id,"access_token":token})
    r2.raise_for_status()
    return r2.json()["id"]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--festival")
    p.add_argument("--auto", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    if args.auto or not args.festival:
        key = datetime.date.today().strftime("%m-%d")
        f = FESTIVALS.get(key)
        if not f: print(f"No festival today ({key})."); sys.exit(0)
    else:
        f = next((v for v in FESTIVALS.values() if v["name"].lower()==args.festival.lower()), None)
        if not f: print(f"Unknown: {args.festival}"); sys.exit(1)
    print(f"Festival: {f['name']}")
    logo = os.environ.get("LOGO_PATH","posts/logo.jpg")
    out  = f"/tmp/festival_{f['name'].replace(' ','_').lower()}.jpg"
    make_image(f, logo, out)
    if args.dry_run: print("Dry run done."); return
    uid   = os.environ["DWS_IG_ACCOUNT_ID"]
    token = os.environ["DWS_IG_USER_TOKEN"]
    imgbb = os.environ["IMGBB_API_KEY"]
    img_url = upload_to_imgbb(out, imgbb)
    print(f"Image URL: {img_url}")
    pid = post_to_instagram(img_url, make_caption(f), uid, token)
    print(f"Posted! ID: {pid}")

if __name__ == "__main__":
    main()
