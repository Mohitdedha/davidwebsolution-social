"""
Facebook Page + Instagram Business poster for David Web Solution.
Uses Facebook Graph API v20.
"""
import os
import time
import requests

FB_PAGE_ID      = os.environ["DWS_FB_PAGE_ID"]
FB_PAGE_TOKEN   = os.environ["DWS_FB_PAGE_TOKEN"]
IG_ACCOUNT_ID   = os.environ.get("DWS_IG_ACCOUNT_ID", "")  # optional

BASE = "https://graph.facebook.com/v20.0"


def _post_fb(text: str, image_url: str | None = None) -> str | None:
    """Post to Facebook Page. Returns post ID or None on failure."""
    if image_url:
        # Photo post
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
        # Text post
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
        print(f"[FB] Error {r.status_code}: {r.text[:200]}")
        return None


def _post_ig(text: str, image_url: str | None = None) -> str | None:
    """Post to Instagram Business account. Returns media ID or None."""
    if not IG_ACCOUNT_ID or not image_url:
        print("[IG] Skipping — no IG account ID or no image.")
        return None

    # Step 1: Create media container
    r = requests.post(
        f"{BASE}/{IG_ACCOUNT_ID}/media",
        data={
            "image_url": image_url,
            "caption": text,
            "access_token": FB_PAGE_TOKEN,
        },
        timeout=30,
    )
    if r.status_code != 200:
        print(f"[IG] Container error {r.status_code}: {r.text[:200]}")
        return None

    container_id = r.json().get("id")
    print(f"[IG] Container created: {container_id}")
    time.sleep(5)  # wait for media to process

    # Step 2: Publish
    r2 = requests.post(
        f"{BASE}/{IG_ACCOUNT_ID}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": FB_PAGE_TOKEN,
        },
        timeout=30,
    )
    if r2.status_code == 200:
        media_id = r2.json().get("id")
        print(f"[IG] Published: {media_id}")
        return media_id
    else:
        print(f"[IG] Publish error {r2.status_code}: {r2.text[:200]}")
        return None


def post_to_all(text: str, image_url: str | None = None) -> dict:
    """Post to Facebook + Instagram. Returns results dict."""
    results = {}
    results["facebook"] = _post_fb(text, image_url)
    time.sleep(2)
    results["instagram"] = _post_ig(text, image_url)
    return results
