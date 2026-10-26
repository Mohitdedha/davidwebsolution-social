"""
Image fetcher for David Web Solution posts.
Uses Pexels → Unsplash → Picsum (no key needed, always works) → None.
"""
import os
import re
import requests
import random

PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
IMGBB_KEY    = os.environ.get("IMGBB_API_KEY", "")

PILLAR_QUERIES = {
    "wordpress_tip":    ["wordpress website design", "web development laptop", "website builder"],
    "seo_tip":          ["google search seo", "digital marketing analytics", "website ranking"],
    "ai_video_ugc":     ["ai technology futuristic", "video content creation", "social media advertising"],
    "web_mistake":      ["website error broken", "computer screen problem", "web design mistake"],
    "client_result":    ["business growth success", "website analytics dashboard", "digital success"],
    "tool_spotlight":   ["web development tools", "coding software", "digital tools laptop"],
    "industry_insight": ["digital marketing trends", "technology business", "web design future"],
}

FALLBACK_COLORS = {
    "wordpress_tip":    "0073aa",
    "seo_tip":          "34a853",
    "ai_video_ugc":     "7c3aed",
    "web_mistake":      "dc2626",
    "client_result":    "0891b2",
    "tool_spotlight":   "d97706",
    "industry_insight": "1e40af",
}


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
                img = requests.get(url, timeout=20)
                return img.content
    except Exception as e:
        print(f"[IMAGE] Pexels error: {e}")
    return None


def _fetch_unsplash(query: str) -> bytes | None:
    if not UNSPLASH_KEY:
        return None
    try:
        r = requests.get(
            "https://api.unsplash.com/photos/random",
            params={"query": query, "orientation": "squarish", "content_filter": "high"},
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
            timeout=15,
        )
        if r.status_code == 200:
            url = r.json()["urls"]["regular"]
            img = requests.get(url, timeout=20)
            return img.content
    except Exception as e:
        print(f"[IMAGE] Unsplash error: {e}")
    return None


def _placeholder_url(pillar: str, text: str) -> str:
    color = FALLBACK_COLORS.get(pillar, "0073aa")
    safe = re.sub(r'[^a-zA-Z0-9 ]', '', text[:40]).replace(' ', '+')
    return f"https://placehold.co/1080x1080/{color}/ffffff/png?text={safe}"


def _fetch_picsum() -> bytes | None:
    """Fetch a random square image from picsum.photos — no key needed."""
    try:
        seed = random.randint(1, 1000)
        r = requests.get(f"https://picsum.photos/seed/{seed}/1080/1080", timeout=20)
        if r.status_code == 200:
            return r.content
    except Exception as e:
        print(f"[IMAGE] Picsum error: {e}")
    return None


def get_image(pillar: str, post_text: str) -> bytes | None:
    """Return image bytes for the post, or None if unavailable."""
    queries = PILLAR_QUERIES.get(pillar, ["web development agency"])
    query = random.choice(queries)

    img = _fetch_pexels(query)
    if img:
        print(f"[IMAGE] Fetched from Pexels: {query}")
        return img

    img = _fetch_unsplash(query)
    if img:
        print(f"[IMAGE] Fetched from Unsplash: {query}")
        return img

    img = _fetch_picsum()
    if img:
        print(f"[IMAGE] Fetched from Picsum (no-key fallback)")
        return img

    print(f"[IMAGE] No image available for pillar: {pillar}")
    return None  # social.py will skip image if None


def upload_to_imgbb(img_bytes: bytes, filename: str) -> str | None:
    """Upload image bytes to ImgBB and return public URL."""
    if not IMGBB_KEY or not img_bytes:
        return None
    try:
        import base64
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
