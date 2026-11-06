"""
festival_post.py - Generates & posts a festival/event card to DWS Instagram.
Run: python post_festival.py --festival "Dhanteras"
Or auto-mode (cron): python post_festival.py --auto
"""
import os, sys, datetime, argparse, textwrap, requests
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
except ImportError:
    os.system("pip install pillow numpy requests --quiet")
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np

FESTIVALS = {
    "11-06": {"name": "Dhanteras",         "hindi": "Dhan Teras Ki Shubhkamnayen",    "emoji": "diya", "msg": "May Goddess Lakshmi bless your home with wealth and happiness on this auspicious day of Dhanteras."},
    "11-07": {"name": "Diwali",             "hindi": "Deepawali Ki Hardik Shubhkamnayen", "emoji": "sparkles", "msg": "Wishing you a Diwali filled with light, joy, and prosperity. May every dream of yours shine bright!"},
    "11-08": {"name": "Diwali",             "hindi": "Deepawali Ki Hardik Shubhkamnayen", "emoji": "sparkles", "msg": "Wishing you a Diwali filled with light, joy, and prosperity. May every dream of yours shine bright!"},
    "11-09": {"name": "Govardhan Puja",     "hindi": "Govardhan Puja Ki Shubhkamnayen",  "emoji": "leaf",     "msg": "On this sacred day of Govardhan Puja, may Lord Krishna shower his blessings of strength and abundance."},
    "11-10": {"name": "Bhai Dooj",          "hindi": "Bhai Dooj Ki Shubhkamnayen",       "emoji": "handshake","msg": "Celebrating the beautiful bond of siblings on Bhai Dooj. May this relationship grow stronger every year."},
    "12-25": {"name": "Christmas",          "hindi": "Christmas Ki Shubhkamnayen",        "emoji": "tree",     "msg": "Wishing you a Merry Christmas filled with joy, warmth and the magic of the season!"},
    "01-01": {"name": "New Year",           "hindi": "Nav Varsh Ki Shubhkamnayen",        "emoji": "fireworks","msg": "Wishing you a Happy New Year full of success, growth and new opportunities!"},
    "01-26": {"name": "Republic Day",       "hindi": "Gantantra Divas Ki Shubhkamnayen", "emoji": "flag",     "msg": "Happy Republic Day! Celebrating the spirit of unity, democracy and progress. Jai Hind!"},
    "08-15": {"name": "Independence Day",   "hindi": "Swatantrata Divas Ki Shubhkamnayen","emoji": "flag",    "msg": "Happy Independence Day! 78 years of freedom, unity and progress. Jai Hind!"},
    "03-14": {"name": "Holi",               "hindi": "Holi Ki Shubhkamnayen",             "emoji": "colors",  "msg": "May the colors of Holi fill your life with happiness, health and prosperity. Happy Holi!"},
    "10-02": {"name": "Gandhi Jayanti",     "hindi": "Gandhi Jayanti Ki Shubhkamnayen",   "emoji": "dove",    "msg": "Honoring the Father of the Nation and his timeless values of truth, peace and service to humanity."},
    "10-24": {"name": "Dussehra",           "hindi": "Dussehra Ki Shubhkamnayen",         "emoji": "bow",     "msg": "Happy Dussehra! May the victory of good over evil inspire us to overcome every challenge."},
    "09-07": {"name": "Ganesh Chaturthi",   "hindi": "Ganesh Chaturthi Ki Shubhkamnayen", "emoji": "elephant","msg": "Ganpati Bappa Morya! May Lord Ganesha remove all obstacles and bless you with wisdom and prosperity."},
    "10-12": {"name": "Navratri",           "hindi": "Navratri Ki Shubhkamnayen",         "emoji": "flower",  "msg": "Wishing you a blessed Navratri! May Goddess Durga shower her divine blessings upon you."},
    "04-14": {"name": "Dr. Ambedkar Jayanti","hindi": "Dr. Ambedkar Jayanti",             "emoji": "bow",     "msg": "Celebrating the visionary Dr. B.R. Ambedkar. His legacy of equality and justice inspires us all."},
}

HASHTAGS = {
    "Dhanteras":       "#HappyDhanteras #Dhanteras2026 #ShubhDhanteras #DavidWebSolution #DigitalMarketing #WebDesign #FestiveGreetings #Diwali2026",
    "Diwali":          "#HappyDiwali #Diwali2026 #ShubhDiwali #DavidWebSolution #DigitalMarketing #WebDesign #FestiveGreetings #Deepawali",
    "Govardhan Puja":  "#GovardhanPuja #HappyGovardhanPuja #DavidWebSolution #DigitalMarketing #WebDesign #FestiveGreetings",
    "Bhai Dooj":       "#HappyBhaiDooj #BhaiDooj2026 #DavidWebSolution #DigitalMarketing #WebDesign #SiblingLove",
    "Christmas":       "#MerryChristmas #Christmas2026 #DavidWebSolution #DigitalMarketing #WebDesign",
    "New Year":        "#HappyNewYear #NewYear2027 #DavidWebSolution #DigitalMarketing #NewBeginnings",
    "Republic Day":    "#RepublicDay #JaiHind #DavidWebSolution #ProudIndian",
    "Independence Day":"#IndependenceDay #JaiHind #DavidWebSolution #ProudIndian #Azaadi",
    "Holi":            "#HappyHoli #Holi2027 #FestivalOfColors #DavidWebSolution #DigitalMarketing",
}

EMOJI_MAP = {
    "diya": "🪔", "sparkles": "✨", "leaf": "🌿", "handshake": "🤝",
    "tree": "🎄", "fireworks": "🎆", "flag": "🇮🇳", "colors": "🎨",
    "dove": "🕊️", "bow": "🏹", "elephant": "🐘", "flower": "🌺",
}

def make_caption(f):
    emoji = EMOJI_MAP.get(f["emoji"], "🎉")
    tags = HASHTAGS.get(f["name"], f"#{f['name'].replace(' ','')} #DavidWebSolution #DigitalMarketing")
    return (f"{emoji} {f['name']} Greetings from David Web Solution! {emoji}\n\n"
            f"{f['msg']}\n\n"
            f"At David Web Solution, we help Indian businesses grow globally.\n\n"
            f"{f['hindi']}\n\n"
            f"+91 82854 23939 | davidwebsolution.com\n\n"
            f"{tags} #IndianBusiness #SmallBusiness #StartupIndia")

SIZE = 1080
NAVY = (4, 8, 26)
NAVY2 = (8, 15, 40)
GOLD = (201, 147, 10)
GOLD2 = (240, 180, 41)
WHITE = (255, 255, 255)
MUTED = (122, 141, 181)

def gradient_bg(img):
    draw = ImageDraw.Draw(img)
    for y in range(SIZE):
        t = y / SIZE
        c = tuple(int(NAVY[i] + (NAVY2[i]-NAVY[i])*t) for i in range(3))
        draw.line([(0,y),(SIZE,y)], fill=c)

def border_ring(draw):
    pad = 28
    draw.rectangle([pad, pad, SIZE-pad, SIZE-pad], outline=(*GOLD, 80), width=2)
    clen = 36
    for x1,y1,dx,dy in [(pad,pad,1,1),(SIZE-pad,pad,-1,1),(pad,SIZE-pad,1,-1),(SIZE-pad,SIZE-pad,-1,-1)]:
        draw.line([(x1,y1),(x1+dx*clen,y1)], fill=GOLD2, width=3)
        draw.line([(x1,y1),(x1,y1+dy*clen)], fill=GOLD2, width=3)

def load_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def draw_logo(draw, img, logo_path):
    if logo_path and Path(logo_path).exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            data = np.array(logo)
            mask = (data[:,:,0]>220)&(data[:,:,1]>220)&(data[:,:,2]>220)
            data[mask,3] = 0
            logo = Image.fromarray(data)
            bbox = logo.getbbox()
            if bbox: logo = logo.crop(bbox)
            lh = 52
            lw = int(logo.width * lh / logo.height)
            logo = logo.resize((lw,lh), Image.LANCZOS)
            img.paste(logo, (52, 36), logo)
            return
        except Exception as e:
            print(f"Logo error: {e}")
    fn = load_font(14, True)
    draw.text((52,44), "DAVID WEB SOLUTION", font=fn, fill=WHITE)

def make_image(f, logo_path, out_path):
    img = Image.new("RGB", (SIZE,SIZE), NAVY)
    gradient_bg(img)
    draw = ImageDraw.Draw(img)
    border_ring(draw)
    draw_logo(draw, img, logo_path)
    fn_h = load_font(18)
    draw.text((SIZE-52, 50), "@davidwebsolution", font=fn_h, fill=MUTED, anchor="ra")
    draw.line([(52,108),(SIZE-52,108)], fill=(*GOLD,40), width=1)
    cy = SIZE//2 - 60
    fn_lbl = load_font(26, True)
    label = f"- {f['name'].upper()} -"
    bbox = draw.textbbox((0,0), label, font=fn_lbl)
    draw.text(((SIZE-(bbox[2]-bbox[0]))//2, cy-90), label, font=fn_lbl, fill=GOLD2)
    emoji_text = EMOJI_MAP.get(f["emoji"], "🎉")
    fn_e = load_font(80)
    bbox2 = draw.textbbox((0,0), emoji_text, font=fn_e)
    draw.text(((SIZE-(bbox2[2]-bbox2[0]))//2, cy-45), emoji_text, font=fn_e, fill=WHITE)
    fn_hd = load_font(64, True)
    headline = f["name"]
    words = headline.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur+" "+w).strip()
        if len(test) <= 14: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    y_h = cy + 55
    for ln in lines:
        b = draw.textbbox((0,0), ln, font=fn_hd)
        draw.text(((SIZE-(b[2]-b[0]))//2, y_h), ln, font=fn_hd, fill=WHITE)
        y_h += 72
    fn_hi = load_font(28)
    hi = f["hindi"]
    b4 = draw.textbbox((0,0), hi, font=fn_hi)
    draw.text(((SIZE-(b4[2]-b4[0]))//2, y_h+8), hi, font=fn_hi, fill=(*GOLD2,220))
    y_div = y_h + 55
    draw.line([(SIZE//2-60,y_div),(SIZE//2+60,y_div)], fill=GOLD, width=2)
    fn_msg = load_font(26)
    for i, ln in enumerate(textwrap.wrap(f["msg"], 44)[:3]):
        b5 = draw.textbbox((0,0), ln, font=fn_msg)
        draw.text(((SIZE-(b5[2]-b5[0]))//2, y_div+18+i*36), ln, font=fn_msg, fill=(200,210,240))
    fn_ft = load_font(22)
    draw.line([(52,SIZE-108),(SIZE-52,SIZE-108)], fill=(*GOLD,40), width=1)
    draw.text((52,SIZE-80), "davidwebsolution.com  +91 82854 23939", font=fn_ft, fill=MUTED)
    fn_cta = load_font(20, True)
    cta = "Free Quote"
    bc = draw.textbbox((0,0), cta, font=fn_cta)
    bw = bc[2]-bc[0]+28; bh = 34
    bx = SIZE-52-bw; by = SIZE-90
    draw.rounded_rectangle([bx,by,bx+bw,by+bh], radius=17, fill=GOLD2)
    draw.text((bx+14,by+7), cta, font=fn_cta, fill=NAVY)
    img.save(out_path, "JPEG", quality=95)
    print(f"Saved: {out_path}")

def upload_to_imgbb(path, key):
    import base64
    with open(path,"rb") as f: b64 = base64.b64encode(f.read()).decode()
    r = requests.post("https://api.imgbb.com/1/upload", data={"key":key,"image":b64})
    r.raise_for_status()
    return r.json()["data"]["url"]

def post_to_instagram(url, caption, uid, token):
    r1 = requests.post(f"https://graph.facebook.com/v19.0/{uid}/media",
        data={"image_url":url,"caption":caption,"access_token":token})
    r1.raise_for_status()
    r2 = requests.post(f"https://graph.facebook.com/v19.0/{uid}/media_publish",
        data={"creation_id":r1.json()["id"],"access_token":token})
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
        if not f:
            print(f"No festival today ({key}).")
            sys.exit(0)
    else:
        f = next((v for v in FESTIVALS.values() if v["name"].lower()==args.festival.lower()), None)
        if not f:
            print(f"Unknown: {args.festival}")
            sys.exit(1)
    print(f"Festival: {f['name']}")
    logo = os.environ.get("LOGO_PATH","posts/logo.jpg")
    out = f"/tmp/festival_{f['name'].replace(' ','_').lower()}.jpg"
    make_image(f, logo, out)
    if args.dry_run:
        print("Dry run done.")
        return
    uid = os.environ["DWS_IG_ACCOUNT_ID"]
    token = os.environ["DWS_IG_USER_TOKEN"]
    imgbb = os.environ["IMGBB_API_KEY"]
    img_url = upload_to_imgbb(out, imgbb)
    pid = post_to_instagram(img_url, make_caption(f), uid, token)
    print(f"Posted! ID: {pid}")

if __name__ == "__main__":
    main()
