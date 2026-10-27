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
    r = requests.get("https://picsum.photos/seed/woman/1080/1350", timeout=20, allow_redirects=True)
    if r.status_code == 200 and len(r.content) > 10000:
        photo_bytes = r.content
        print(f"[PHOTO] Got {len(r.content)//1024}KB")
    else:
        print(f"[PHOTO] Failed: {r.status_code}")
except Exception as e:
    print(f"[PHOTO] Error: {e}")

original_choice = random.choice
for tpl_name in ["agency_split", "dark_pro"]:
    random.choice = lambda x, t=tpl_name: t
    img = design_post(pillar, TEST_TEXT, photo_bytes=photo_bytes)
    path = os.path.join(out_dir, f"demo_{tpl_name}.png")
    with open(path, "wb") as f:
        f.write(img)
    print(f"[OK] {tpl_name} -> {path}")

random.choice = original_choice
print("\nDone.")
