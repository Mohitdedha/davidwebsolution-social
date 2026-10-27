"""
Facebook Page + Instagram Business poster for David Web Solution.
Uses Facebook Graph API v21.0.
IG account ID is auto-discovered from the FB Page — no separate secret needed.
"""
import os
import time
import requests

FB_PAGE_ID    = os.environ["DWS_FB_PAGE_ID"]
FB_PAGE_TOKEN = os.environ["DWS_FB_PAGE_TOKEN"]
# Instagram requires a User Access Token (Page Tokens lack instagram_content_publish).
# Falls back to FB_PAGE_TOKEN if not set (which will fail — set DWS_IG_USER_TOKEN).
IG_USER_TOKEN = os.environ.get("DWS_IG_USER_TOKEN", FB_PAGE_TOKEN)

BASE = "https://graph.facebook.com/v21.0"

_ig_account_id_cache = None


def _get_ig_account_id() -> str | None:
    """Auto-fetch Instagram Business Account ID linked to the FB Page."""
    global _ig_account_id_cache

    # 1. Check env var first (optional override)
    env_id = os.environ.get("DWS_IG_ACCOUNT_ID", "").strip()
    if env_id:
        _ig_account_id_cache = env_id
        return env_id

    if _ig_account_id_cache:
        return _ig_account_id_cache

    try:
        r = requests.get(
            f"{BASE}/{FB_PAGE_ID}",
            params={
                "fields": "instagram_business_account",
                "access_token": IG_USER_TOKEN,
            },
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        ig = data.get("instagram_business_account", {})
        ig_id = ig.get("id", "")
        if ig_id:
            print(f"[IG] Auto-discovered IG account ID: {ig_id}")
            _ig_account_id_cache = ig_id
            return ig_id
        else:
            print("[IG] No Instagram Business account linked to this FB Page.")
            print(f"[IG] Response: {data}")
            return None
    except Exception as e:
        print(f"[IG] Could not fetch IG account ID: {e}")
        return None


def _post_fb(text: str, image_url: str | None = None) -> str | None:
    """Post to Facebook Page. Returns post ID or None on failure."""
    try:
        if image_url:
            r = requests.post(
                f"{BASE}/{FB_PAGE_ID}/photos",
                data={
                    "url": image_url,
                    "caption": text,
                    "access_token": FB_PAGE_TOKEN,
                },
                timeout=30,
            )
        else:
            r = requests.post(
                f"{BASE}/{FB_PAGE_ID}/feed",
                data={
                    "message": text,
                    "access_token": FB_PAGE_TOKEN,
                },
                timeout=30,
            )

        if r.status_code == 200:
            post_id = r.json().get("post_id") or r.json().get("id")
            print(f"[FB] Posted: {post_id}")
            return post_id
        else:
            print(f"[FB] Error {r.status_code}: {r.text[:300]}")
            return None
    except Exception as e:
        print(f"[FB] Exception: {e}")
        return None


def _post_ig(text: str, image_url: str | None = None) -> str | None:
    """Post to Instagram Business account. Returns media ID or None."""
    if not image_url:
        print("[IG] Skipping — no image URL.")
        return None

    ig_id = _get_ig_account_id()
    if not ig_id:
        print("[IG] Skipping — Instagram account not linked or not found.")
        return None

    try:
        # Step 1: Create media container
        r = requests.post(
            f"{BASE}/{ig_id}/media",
            data={
                "image_url": image_url,
                "caption": text,
                "access_token": IG_USER_TOKEN,
            },
            timeout=30,
        )
        if r.status_code != 200:
            print(f"[IG] Container error {r.status_code}: {r.text[:300]}")
            # Common errors:
            # (#10) = missing instagram_content_publish permission
            # (#100) = invalid image URL
            # (#36000) = image not accessible
            if "10" in r.text and "permission" in r.text.lower():
                print("[IG] FIX NEEDED: Add 'instagram_content_publish' permission to your Facebook App.")
            return None

        container_id = r.json().get("id")
        print(f"[IG] Container created: {container_id}")

        # Step 2: Wait for media to process (retry up to 3x)
        for attempt in range(3):
            time.sleep(8)
            status_r = requests.get(
                f"{BASE}/{container_id}",
                params={
                    "fields": "status_code",
                    "access_token": IG_USER_TOKEN,
                },
                timeout=15,
            )
            status = status_r.json().get("status_code", "")
            print(f"[IG] Container status: {status} (attempt {attempt + 1})")
            if status == "FINISHED":
                break
            if status == "ERROR":
                print("[IG] Media container processing failed.")
                return None

        # Step 3: Publish
        r2 = requests.post(
            f"{BASE}/{ig_id}/media_publish",
            data={
                "creation_id": container_id,
                "access_token": IG_USER_TOKEN,
            },
            timeout=30,
        )
        if r2.status_code == 200:
            media_id = r2.json().get("id")
            print(f"[IG] Published: {media_id}")
            return media_id
        else:
            print(f"[IG] Publish error {r2.status_code}: {r2.text[:300]}")
            return None

    except Exception as e:
        print(f"[IG] Exception: {e}")
        return None


def post_to_all(text: str, image_url: str | None = None) -> dict:
    """Post to Facebook + Instagram. Returns results dict."""
    results = {}

    results["facebook"] = _post_fb(text, image_url)
    time.sleep(2)
    results["instagram"] = _post_ig(text, image_url)

    fb_ok = bool(results["facebook"])
    ig_ok = bool(results["instagram"])
    print(f"[SOCIAL] FB={'OK' if fb_ok else 'FAIL'} | IG={'OK' if ig_ok else 'FAIL'}")
    return results
