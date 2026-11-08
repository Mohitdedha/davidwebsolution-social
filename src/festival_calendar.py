"""
Festival calendar for David Web Solution auto-poster.
Posts a branded festival greeting on (or day before) each festival.
Covers Indian + Western festivals relevant to US/UK audience.
"""
from datetime import date, timedelta

# Each entry: "YYYY-MM-DD" -> festival config dict
# For recurring annual festivals (fixed date), add both years as needed.
FESTIVALS = {
    # ── Indian festivals ────────────────────────────────────────────────────
    "2026-11-01": {
        "name": "Diwali",
        "sub": "Festival of Lights",
        "msg": "May this Diwali bring joy, prosperity & success",
        "theme": "diwali",
    },
    "2027-10-21": {
        "name": "Diwali",
        "sub": "Festival of Lights",
        "msg": "May this Diwali bring joy, prosperity & success",
        "theme": "diwali",
    },
    "2027-03-29": {
        "name": "Holi",
        "sub": "Festival of Colours",
        "msg": "Wishing you a colourful and joyful Holi",
        "theme": "holi",
    },
    "2027-01-14": {
        "name": "Makar Sankranti",
        "sub": "Harvest Festival",
        "msg": "May this harvest season bring abundance to your business",
        "theme": "sankranti",
    },
    "2027-08-15": {
        "name": "Independence Day",
        "sub": "Happy Independence Day India",
        "msg": "Proud to serve Indian businesses globally",
        "theme": "india_independence",
    },
    "2027-01-26": {
        "name": "Republic Day",
        "sub": "Happy Republic Day",
        "msg": "Celebrating the spirit of a great nation",
        "theme": "india_independence",
    },
    # ── Western / global ────────────────────────────────────────────────────
    "2026-12-25": {
        "name": "Christmas",
        "sub": "Merry Christmas",
        "msg": "Wishing you peace, joy and a prosperous New Year",
        "theme": "christmas",
    },
    "2027-12-25": {
        "name": "Christmas",
        "sub": "Merry Christmas",
        "msg": "Wishing you peace, joy and a prosperous New Year",
        "theme": "christmas",
    },
    "2026-12-31": {
        "name": "New Year's Eve",
        "sub": "Goodbye 2026!",
        "msg": "Thank you for an amazing year — here's to 2027",
        "theme": "newyear",
    },
    "2027-01-01": {
        "name": "New Year",
        "sub": "Happy New Year 2027",
        "msg": "New year, new goals, new growth — let's build together",
        "theme": "newyear",
    },
    "2027-02-14": {
        "name": "Valentine's Day",
        "sub": "Happy Valentine's Day",
        "msg": "We love helping businesses grow — that's our Valentine",
        "theme": "valentine",
    },
    "2027-10-31": {
        "name": "Halloween",
        "sub": "Happy Halloween",
        "msg": "Don't be scared of your website — we'll fix it",
        "theme": "halloween",
    },
    "2027-07-04": {
        "name": "Independence Day",
        "sub": "Happy 4th of July",
        "msg": "Celebrating freedom — including freedom from bad websites",
        "theme": "usa_independence",
    },
    "2027-11-25": {
        "name": "Thanksgiving",
        "sub": "Happy Thanksgiving",
        "msg": "Grateful for every client who trusted us to grow their business",
        "theme": "thanksgiving",
    },
    "2027-04-20": {
        "name": "Easter",
        "sub": "Happy Easter",
        "msg": "New beginnings for your brand — let's grow together",
        "theme": "easter",
    },
    # ── Islamic (approximate — lunar calendar shifts yearly) ────────────────
    "2027-03-20": {
        "name": "Eid ul-Fitr",
        "sub": "Eid Mubarak",
        "msg": "Eid Mubarak — may your business flourish this year",
        "theme": "eid",
    },
    "2027-05-28": {
        "name": "Eid ul-Adha",
        "sub": "Eid Mubarak",
        "msg": "Wishing you blessings, peace and prosperity",
        "theme": "eid",
    },
}

# Theme → color palette
THEME_COLORS = {
    "diwali":           {"bg": (18,5,40),    "accent": (245,184,0),  "accent2": (255,110,20), "text": (255,245,210)},
    "holi":             {"bg": (20,5,45),    "accent": (255,80,120), "accent2": (80,200,255), "text": (255,255,255)},
    "sankranti":        {"bg": (15,30,10),   "accent": (220,180,0),  "accent2": (255,140,20), "text": (255,250,220)},
    "india_independence":{"bg":(5,30,10),    "accent": (19,136,8),   "accent2": (255,153,51), "text": (255,255,255)},
    "christmas":        {"bg": (5,25,10),    "accent": (220,30,30),  "accent2": (245,184,0),  "text": (255,255,255)},
    "newyear":          {"bg": (5,5,30),     "accent": (180,140,255),"accent2": (245,184,0),  "text": (255,255,255)},
    "valentine":        {"bg": (35,5,20),    "accent": (220,30,80),  "accent2": (255,160,180),"text": (255,235,240)},
    "halloween":        {"bg": (15,8,0),     "accent": (255,100,0),  "accent2": (140,0,200),  "text": (255,220,180)},
    "usa_independence": {"bg": (5,10,40),    "accent": (220,30,30),  "accent2": (245,184,0),  "text": (255,255,255)},
    "thanksgiving":     {"bg": (25,12,0),    "accent": (200,100,20), "accent2": (220,160,0),  "text": (255,235,200)},
    "easter":           {"bg": (10,20,35),   "accent": (160,220,100),"accent2": (255,180,220),"text": (255,255,255)},
    "eid":              {"bg": (5,20,10),    "accent": (0,160,80),   "accent2": (200,160,0),  "text": (220,255,230)},
    "chhath":           {"bg": (20,8,0),     "accent": (255,140,0),  "accent2": (255,220,80), "text": (255,240,210)},
}

def get_today_festival(today: date | None = None) -> dict | None:
    """Return festival config if today (or tomorrow) is a festival, else None."""
    if today is None:
        today = date.today()
    for delta in [0, 1]:          # post on the day OR the day before
        key = (today + timedelta(days=delta)).strftime("%Y-%m-%d")
        if key in FESTIVALS:
            fest = FESTIVALS[key].copy()
            fest["days_away"] = delta
            return fest
    return None
