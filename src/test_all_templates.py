"""Generate preview of both templates WITH a real Unsplash photo."""
import os, sys, random, requests
sys.path.insert(0, os.path.dirname(__file__))

from image_designer import design_post

TEST_TEXT = """5 WordPress Mistakes Costing You Clients

Your website is losing you money right now.

- No SSL certificate — Google flags your site as unsafe
- Images not compressed — loads 6 seconds, visitors leave in 3
- No mobile optimisation — 60% of traffic is mobile
- Outdated plugins — security risk plus slow load time
- No clear call-to-action — visitors leave without contacting you

We fixed these for a UK business last month — leads doubled in 30 days.

DM us AUDIT and we will check your site for FREE.

#WordPress #WebDesign #SmallBusiness #UKBusiness #WebDevelopment"""

pillar = "wordpress_tip"
out_dir = os.path.dirname(__file__)

# Fetch real photo from Unsplash Source (free, no API key)
print("[PHOTO] Fetching sample photo from Picsum (local test only)...")
photo_bytes = None
try:
    # Use a fixed seed that gives a professional/person photo for testing
    # ID 1005 confirmed 200 OK — professional woman photo
    r = requests.get("https://picsum.photos/id/1005/1080/1350", timeout=20, allow_redirects=True)
    if r.status_code == 200 and len(r.content) > 10000:
        photo_bytes = r.content
        print(f"[PHOTO] Got {len(r.content)//1024}KB")
    else:
        print(f"[PHOTO] Failed: {r.status_code}")
except Exception as e:
    print(f"[PHOTO] Error: {e}")

original_choice = random.choice

from image_designer import PILLAR_TEMPLATES, PILLAR_COLORS, PILLAR_INTRO, CTA_OPTIONS
from image_designer import _headline, _bullets, _load_photo, _tpl_agency_split, _tpl_dark_pro

import io
hl    = _headline(TEST_TEXT)
blts  = _bullets(TEST_TEXT)
color = PILLAR_COLORS[pillar]
intro = PILLAR_INTRO[pillar]
photo = _load_photo(photo_bytes) if photo_bytes else None
cta   = "DM us to get started"   # fixed CTA for test

for tpl_name, tpl_fn in [("agency_split", _tpl_agency_split), ("dark_pro", _tpl_dark_pro)]:
    img_obj = tpl_fn(hl, blts, cta, color, photo, intro_label=intro)
    buf = io.BytesIO()
    img_obj.save(buf, format="PNG")
    path = os.path.join(out_dir, f"demo_{tpl_name}.png")
    with open(path, "wb") as f:
        f.write(buf.getvalue())
    print(f"[OK] {tpl_name} -> {path}")
print("\nDone.")
