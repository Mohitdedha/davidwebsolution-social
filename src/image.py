"""
Image provider for David Web Solution posts.
Primary: Pillow-based designed graphic (always works).
Photo sources: Pexels -> Unsplash API -> Unsplash Source (free, no key)
"""
import os
import random
import requests
import base64

PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
IMGBB_KEY    = os.environ.get("IMGBB_API_KEY", "")

# Queries tuned to return professional, people-inclusive photos
PILLAR_QUERIES = {
    "wordpress_tip":    ["wordpress developer woman laptop", "web designer working"],
    "seo_tip":          ["digital marketing woman analytics", "seo strategy business"],
    "ai_video_ugc":     ["content creator woman studio", "video marketing professional"],
    "web_mistake":      ["web developer woman coding", "designer laptop computer"],
    "client_result":    ["business woman success meeting", "team celebration growth"],
    "tool_spotlight":   ["developer woman tools laptop", "coding professional woman"],
    "industry_insight": ["digital marketing professional woman", "tech business team"],
}

# Unsplash Source keywords (free CDN, no API key needed)
UNSPLASH_SOURCE_QUERIES = {
    "wordpress_tip":    "developer,woman,laptop,web",
    "seo_tip":          "marketing,woman,analytics,digital",
    "ai_video_ugc":     "content,creator,woman,video",
    "web_mistake":      "designer,woman,computer,coding",
    "client_result":    "business,woman,success,team",
    "tool_spotlight":   "developer,woman,technology,laptop",
    "industry_insight": "professional,woman,digital,technology",
}


def _design(pillar: str, post_text: str) -> bytes | None:
    """Generate a designed branded graphic via Pillow."""
    try:
        from image_designer import design_post
        return design_post(pillar, post_text)
    except Exception as e:
        print(f"[IMAGE] Designer error: {e}")
        return None


def _fetch_pexels(query: str) -> bytes | None:
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 10, "orientation": "square"},
            headers={"Authorization": PEXELS_KEY},
            timeout=15,
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = random.choice(photos)["src"]["large"]
                return requests.get(url, timeout=20).content
    except Exception as e:
        print(f"[IMAGE] Pexels error: {e}")
    return None


def _fetch_unsplash(query: str) -> bytes | None:
    if not UNSPLASH_KEY:
        return None
    try:
        r = requests.get(
            "https://api.unsplash.com/photos/random",
            params={"query": query, "orientation": "squarish"},
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
            timeout=15,
        )
        if r.status_code == 200:
            url = r.json()["urls"]["regular"]
            return requests.get(url, timeout=20).content
    except Exception as e:
        print(f"[IMAGE] Unsplash error: {e}")
    return None


def _fetch_unsplash_source(pillar: str) -> bytes | None:
    """Fetch from Unsplash CDN — free, no API key, returns relevant professional photo."""
    try:
        kw = UNSPLASH_SOURCE_QUERIES.get(pillar, "professional,woman,business,technology")
        seed = random.randint(1, 500)
        # Unsplash source with seed for variety
        r = requests.get(
            f"https://source.unsplash.com/1080x1080/?{kw}&sig={seed}",
            timeout=25,
            allow_redirects=True,
        )
        if r.status_code == 200 and len(r.content) > 10000:
            return r.content
    except Exception as e:
        print(f"[IMAGE] Unsplash source error: {e}")
    return None


def get_image(pillar: str, post_text: str) -> bytes | None:
    # 1. Fetch a real photo to composite into the design
    query = random.choice(PILLAR_QUERIES.get(pillar, ["web development agency"]))
    photo_bytes = _fetch_pexels(query) or _fetch_unsplash(query) or _fetch_unsplash_source(pillar)
    if photo_bytes:
        print(f"[IMAGE] Photo fetched for: {query}")
    else:
        print(f"[IMAGE] No photo found for query: {query}, using geometric design")

    # 2. Generate branded design (with or without real photo)
    try:
        from image_designer import design_post
        img = design_post(pillar, post_text, photo_bytes=photo_bytes)
        if img:
            print(f"[IMAGE] Branded design ready for pillar={pillar}")
            return img
    except Exception as e:
        print(f"[IMAGE] Designer error: {e}")

    # 3. Last resort: return raw photo bytes if available
    return photo_bytes


def upload_to_imgbb(img_bytes: bytes, filename: str) -> str | None:
    if not IMGBB_KEY or not img_bytes:
        return None
    try:
        b64 = base64.b64encode(img_bytes).decode()
        r = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_KEY, "image": b64, "name": filename},
            timeout=30,
        )
        if r.status_code == 200:
            url = r.json()["data"]["url"]
            print(f"[IMAGE] Uploaded to ImgBB: {url}")
            return url
    except Exception as e:
        print(f"[IMAGE] ImgBB upload error: {e}")
    return None
