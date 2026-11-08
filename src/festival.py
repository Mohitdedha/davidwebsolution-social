"""
Festival detection for David Web Solution auto-poster.
Returns today's festival (if any) so main.py can post a special card.
"""
from datetime import date, timedelta

# Fixed-date festivals (day, month)
_FIXED = {
    (1,  1):  ("NEW_YEAR",    "NEW YEAR",          "✨", "Happy New",    "Year!",      "Wishing you bigger clients, better rankings\n& faster growth — David Web Solution."),
    (26, 1):  ("REPUBLIC",    "REPUBLIC DAY",       "🇮🇳","Happy Republic","Day!",       "Proud to serve India's businesses.\nJai Hind — David Web Solution."),
    (25, 12): ("CHRISTMAS",   "MERRY CHRISTMAS",    "🎄","Merry",        "Christmas!", "Wishing you joy, growth & great rankings\nthis festive season — David Web Solution."),
    (15, 8):  ("INDEPENDENCE","INDEPENDENCE DAY",   "🇮🇳","Happy",        "Independence Day!", "75+ years of freedom. Building India's digital future.\n— David Web Solution."),
}

# Variable-date festivals hardcoded for 2026 & 2027
# Format: (year, month, day) -> festival data
_VARIABLE = {
    # Diwali
    (2026, 10, 20): ("DIWALI",   "FESTIVAL OF LIGHTS", "🪔", "Happy",  "Diwali!",   "May this Diwali bring prosperity & success\nto your business — David Web Solution."),
    (2027, 11,  8): ("DIWALI",   "FESTIVAL OF LIGHTS", "🪔", "Happy",  "Diwali!",   "May this Diwali bring prosperity & success\nto your business — David Web Solution."),
    # Holi
    (2026,  3, 20): ("HOLI",     "HAPPY HOLI",         "🎨", "Happy",  "Holi!",     "May your life be as colourful as your brand.\nWith love — David Web Solution."),
    (2027,  3, 10): ("HOLI",     "HAPPY HOLI",         "🎨", "Happy",  "Holi!",     "May your life be as colourful as your brand.\nWith love — David Web Solution."),
    # Eid al-Fitr
    (2026,  3, 20): ("EID",      "EID MUBARAK",        "🌙", "Eid",    "Mubarak!",  "Wishing you blessings, peace & prosperity.\nFrom David Web Solution family."),
    (2027,  3, 10): ("EID",      "EID MUBARAK",        "🌙", "Eid",    "Mubarak!",  "Wishing you blessings, peace & prosperity.\nFrom David Web Solution family."),
    # Dussehra
    (2026, 10,  2): ("DUSSEHRA", "HAPPY DUSSEHRA",     "🏹", "Happy",  "Dussehra!", "Victory of good over evil. Build your digital\npresence right — David Web Solution."),
    (2027, 10, 20): ("DUSSEHRA", "HAPPY DUSSEHRA",     "🏹", "Happy",  "Dussehra!", "Victory of good over evil. Build your digital\npresence right — David Web Solution."),
    # Navratri start
    (2026,  9, 24): ("NAVRATRI", "HAPPY NAVRATRI",     "🪔", "Happy",  "Navratri!", "Nine nights of celebration & new beginnings.\nGrow your brand — David Web Solution."),
    # Chhath Puja
    (2026, 11,  8): ("CHHATH",   "HAPPY CHHATH PUJA",  "🌅", "Happy",  "Chhath Puja!", "Celebrating the festival of the Sun God.\nBlessings & prosperity — David Web Solution."),
    (2027, 10, 28): ("CHHATH",   "HAPPY CHHATH PUJA",  "🌅", "Happy",  "Chhath Puja!", "Celebrating the festival of the Sun God.\nBlessings & prosperity — David Web Solution."),
}

# Background colors per festival key (bg1, bg2, accent RGB)
FESTIVAL_COLORS = {
    "DIWALI":       ((26, 10,  0), (45, 19,  0), (245, 197,  24)),
    "CHRISTMAS":    ((10, 31, 10), ( 0, 21,  5), (220,  50,  50)),
    "NEW_YEAR":     (( 5,  9, 26), (10, 18, 48), (100, 148, 255)),
    "REPUBLIC":     ((10,  5,  5), (30, 10, 10), (255, 153,  51)),
    "INDEPENDENCE": ((10,  5,  5), (30, 10, 10), (255, 153,  51)),
    "HOLI":         ((61,  0,102), (26,  0, 64), (255, 136, 255)),
    "EID":          (( 3, 18,  8), ( 0, 26, 10), ( 74, 222, 128)),
    "DUSSEHRA":     ((30, 10,  0), (50, 15,  0), (255, 165,   0)),
    "NAVRATRI":     ((40,  0, 40), (20,  0, 20), (255, 100, 200)),
    "CHHATH":       ((20,  8,  0), (40, 15,  0), (255, 165,   0)),
}


def get_today_festival(today: date = None):
    """
    Returns festival dict for today, or None if no festival.
    Dict keys: key, label, emoji, line1, line2, tagline, bg1, bg2, accent
    """
    if today is None:
        today = date.today()

    # Check variable dates first
    key3 = (today.year, today.month, today.day)
    if key3 in _VARIABLE:
        data = _VARIABLE[key3]
    # Check fixed dates
    elif (today.day, today.month) in _FIXED:
        data = _FIXED[(today.day, today.month)]
    else:
        return None

    fkey, label, emoji, line1, line2, tagline = data
    bg1, bg2, accent = FESTIVAL_COLORS.get(fkey, ((5, 9, 26), (10, 18, 48), (100, 148, 255)))

    return {
        "key":     fkey,
        "label":   label,
        "emoji":   emoji,
        "line1":   line1,
        "line2":   line2,
        "tagline": tagline,
        "bg1":     bg1,
        "bg2":     bg2,
        "accent":  accent,
    }


def build_festival_caption(fest: dict) -> str:
    tagline = fest["tagline"].replace("\n", " ")
    cta_map = {
        "DIWALI":        "Happy Diwali from David Web Solution! 🪔",
        "CHRISTMAS":     "Merry Christmas from David Web Solution! 🎄",
        "NEW_YEAR":      "Happy New Year from David Web Solution! ✨",
        "REPUBLIC":      "Happy Republic Day! Jai Hind 🇮🇳",
        "INDEPENDENCE":  "Happy Independence Day! Jai Hind 🇮🇳",
        "HOLI":          "Happy Holi from David Web Solution! 🎨",
        "EID":           "Eid Mubarak from David Web Solution! 🌙",
        "DUSSEHRA":      "Happy Dussehra from David Web Solution! 🏹",
        "NAVRATRI":      "Happy Navratri from David Web Solution! 🪔",
        "CHHATH":        "Happy Chhath Puja from David Web Solution! 🌅",
    }
    main_line = cta_map.get(fest["key"], f"{fest['line1']} {fest['line2']} from David Web Solution!")
    return (
        f"{main_line}\n\n"
        f"{tagline}\n\n"
        f"davidwebsolution.com | +91 82854 23939\n\n"
        f"#DavidWebSolution #DigitalMarketing #WebDesign #{fest['key'].title()}"
    )
