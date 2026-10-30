"""
Facebook Page + Instagram Business + LinkedIn Company poster for David Web Solution.
Uses Facebook Graph API v21.0 and LinkedIn API v2.
"""
import os
import time
import requests

FB_PAGE_ID    = os.environ["DWS_FB_PAGE_ID"]
FB_PAGE_TOKEN = os.environ["DWS_FB_PAGE_TOKEN"]
IG_USER_TOKEN = os.environ.get("DWS_IG_USER_TOKEN", FB_PAGE_TOKEN)

# LinkedIn — optional, skipped if secrets not set
LI_TOKEN   = os.environ.get("DWS_LI_ACCESS_TOKEN", "")
LI_ORG_ID  = os.environ.get("DWS_LI_ORGANIZATION_ID", "")

BASE = "https://graph.facebook.com/v21.0"
LI_BASE = "https://api.linkedin.com/v2"

_ig_account_id_cache = None


def _get_ig_account_id() -> str | None:
    """Auto-fetch Instagram Business Account ID linked to the FB Page."""
    global _ig_account_id_cache

    # 1. Check env var first (set DWS_IG_ACCOUNT_ID to skip auto-discovery)
    env_id = os.environ.get("DWS_IG_ACCOUNT_ID", "").strip()
    if env_id:
        _ig_account_id_cache = env_id
        return env_id

    if _ig_account_id_cache:
        return _ig_account_id_cache

    try:
        # Use Page Token (not User Token) to read page fields — it has page access
        r = requests.get(
            f"{BASE}/{FB_PAGE_ID}",
            params={
                "fields": "instagram_business_account",
                "access_token": FB_PAGE_TOKEN,
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


def post_reel(video_url: str, caption: str) -> str | None:
    """Post a Reel to Instagram. video_url must be publicly accessible MP4."""
    ig_id = _get_ig_account_id()
    if not ig_id:
        print("[REEL] Skipping — IG account not found.")
        return None
    try:
        # Step 1: Create reel container
        r = requests.post(f"{BASE}/{ig_id}/media", data={
            "video_url": video_url,
            "caption": caption,
            "media_type": "REELS",
            "share_to_feed": "true",
            "access_token": IG_USER_TOKEN,
        }, timeout=30)
        if r.status_code != 200:
            print(f"[REEL] Container error {r.status_code}: {r.text[:300]}")
            return None
        container_id = r.json().get("id")
        print(f"[REEL] Container: {container_id}")

        # Step 2: Wait for processing (up to 60s)
        import time as _time
        for attempt in range(8):
            _time.sleep(10)
            sr = requests.get(f"{BASE}/{container_id}", params={
                "fields": "status_code", "access_token": IG_USER_TOKEN,
            }, timeout=15)
            status = sr.json().get("status_code", "")
            print(f"[REEL] Status: {status} (attempt {attempt+1})")
            if status == "FINISHED": break
            if status == "ERROR":
                print("[REEL] Processing failed.")
                return None

        # Step 3: Publish
        r2 = requests.post(f"{BASE}/{ig_id}/media_publish", data={
            "creation_id": container_id,
            "access_token": IG_USER_TOKEN,
        }, timeout=30)
        if r2.status_code == 200:
            media_id = r2.json().get("id")
            print(f"[REEL] Published: {media_id}")
            return media_id
        else:
            print(f"[REEL] Publish error {r2.status_code}: {r2.text[:300]}")
            return None
    except Exception as e:
        print(f"[REEL] Exception: {e}")
        return None


def _get_li_author() -> str | None:
    """Get LinkedIn author URN — company page if set, else personal profile."""
    headers = {"Authorization": f"Bearer {LI_TOKEN}"}
    # Company page takes priority
    if LI_ORG_ID:
        return f"urn:li:organization:{LI_ORG_ID}"
    # Personal profile — fetch numeric ID from token
    try:
        r = requests.get(f"{LI_BASE}/me", headers=headers, timeout=15)
        if r.status_code == 200:
            person_id = r.json().get("id")
            print(f"[LI] Personal profile ID: {person_id}")
            return f"urn:li:person:{person_id}"
        else:
            print(f"[LI] Could not fetch profile ID: {r.status_code} {r.text[:200]}")
            return None
    except Exception as e:
        print(f"[LI] Profile fetch error: {e}")
        return None


def _post_linkedin(text: str, image_url: str | None = None) -> str | None:
    """Post to LinkedIn (personal profile or company page). Returns post URN or None."""
    if not LI_TOKEN:
        print("[LI] Skipping — DWS_LI_ACCESS_TOKEN not set.")
        return None

    headers = {
        "Authorization": f"Bearer {LI_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202401",
    }

    author = _get_li_author()
    if not author:
        print("[LI] Skipping — could not determine LinkedIn author URN.")
        return None

    try:
        # Step 1: Upload image if provided
        media_asset = None
        if image_url:
            reg = requests.post(
                f"{LI_BASE}/assets?action=registerUpload",
                headers=headers,
                json={
                    "registerUploadRequest": {
                        "owner": author,
                        "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                        "serviceRelationships": [{"identifier": "urn:li:userGeneratedContent", "relationshipType": "OWNER"}],
                    }
                },
                timeout=30,
            )
            if reg.status_code == 200:
                reg_data = reg.json()["value"]
                upload_url = reg_data["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
                media_asset = reg_data["asset"]
                img_bytes = requests.get(image_url, timeout=30).content
                requests.put(upload_url, data=img_bytes,
                             headers={"Authorization": f"Bearer {LI_TOKEN}"}, timeout=60)
                print(f"[LI] Image uploaded: {media_asset}")
            else:
                print(f"[LI] Image register failed {reg.status_code}: {reg.text[:200]}")

        # Step 2: Create post
        post_body = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "IMAGE" if media_asset else "NONE",
                    **({"media": [{"status": "READY", "media": media_asset}]} if media_asset else {}),
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        r = requests.post(f"{LI_BASE}/ugcPosts", headers=headers, json=post_body, timeout=30)
        if r.status_code in (200, 201):
            post_id = r.headers.get("x-restli-id") or r.json().get("id", "ok")
            print(f"[LI] Posted: {post_id}")
            return post_id
        else:
            print(f"[LI] Error {r.status_code}: {r.text[:300]}")
            return None

    except Exception as e:
        print(f"[LI] Exception: {e}")
        return None


def post_to_all(text: str, image_url: str | None = None) -> dict:
    """Post to Facebook + Instagram + LinkedIn. Returns results dict."""
    results = {}

    results["facebook"]  = _post_fb(text, image_url)
    time.sleep(2)
    results["instagram"] = _post_ig(text, image_url)
    time.sleep(2)
    results["linkedin"]  = _post_linkedin(text, image_url)

    fb_ok = bool(results["facebook"])
    ig_ok = bool(results["instagram"])
    li_ok = bool(results["linkedin"])
    print(f"[SOCIAL] FB={'OK' if fb_ok else 'FAIL'} | IG={'OK' if ig_ok else 'FAIL'} | LI={'OK' if li_ok else 'FAIL/SKIP'}")
    return results
