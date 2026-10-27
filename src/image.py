"""
Image provider for David Web Solution posts.
Primary: Pillow-based designed graphic (always works).
Fallback: Pexels -> Unsplash -> Picsum (photo variety).
"""
import os
import random
import requests
import base64

PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
IMGBB_KEY    = os.environ.get("IMGBB_API_KEY", "")

PILLAR_QUERIES = {
    "wordpress_tip":    ["wordpress website design", "web development laptop"],
    "seo_tip":          ["google search seo", "digital marketing analytics"],
    "ai_video_ugc":     ["ai technology futuristic", "video content creation"],
    "web_mistake":      ["website error broken", "computer screen problem"],
    "client_result":    ["business growth success", "website analytics dashboard"],
    "tool_spotlight":   ["web development tools", "coding software"],
    "industry_insight": ["digital marketing trends", "technology business"],
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


def _fetch_picsum() -> bytes | None:
    try:
        seed = random.randint(1, 1000)
        r = requests.get(f"https://picsum.photos/seed/{seed}/1080/1080", timeout=20)
        if r.status_code == 200:
            return r.content
    except Exception as e:
        print(f"[IMAGE] Picsum error: {e}")
    return None


def get_image(pillar: str, post_text: str) -> bytes | None:
    # 1. Fetch a real photo to composite into the design
    query = random.choice(PILLAR_QUERIES.get(pillar, ["web development agency"]))
    photo_bytes = _fetch_pexels(query) or _fetch_unsplash(query)
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

    # 3. Last resort: raw photo or picsum
    return photo_bytes or _fetch_picsum()


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
