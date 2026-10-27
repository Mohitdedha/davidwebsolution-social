"""
Facebook Page Token Auto-Refresher.
Exchanges short-lived token → long-lived user token → permanent page token.
Then updates GitHub Secret DWS_FB_PAGE_TOKEN automatically.
"""
import os
import sys
import requests
import base64
import json
from datetime import datetime

APP_ID         = os.environ["FB_APP_ID"]
APP_SECRET     = os.environ["FB_APP_SECRET"]
CURRENT_TOKEN  = os.environ["DWS_FB_PAGE_TOKEN"]
FB_PAGE_ID     = os.environ["DWS_FB_PAGE_ID"]
GH_TOKEN       = os.environ["GH_PAT"]          # GitHub Personal Access Token
GH_REPO        = os.environ.get("GITHUB_REPOSITORY", "Mohitdedha/davidwebsolution-social")
SECRET_NAME    = "DWS_FB_PAGE_TOKEN"


def step1_long_lived_user_token(short_token):
    """Exchange any token for a 60-day long-lived user token."""
    print("[TOKEN] Step 1: getting long-lived user token...")
    r = requests.get(
        "https://graph.facebook.com/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": APP_ID,
            "client_secret": APP_SECRET,
            "fb_exchange_token": short_token,
        },
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError(f"Step 1 failed: {data}")
    print(f"[TOKEN] Long-lived user token obtained (expires: {data.get('expires_in','?')}s)")
    return data["access_token"]


def step2_permanent_page_token(user_token):
    """Get permanent Page Access Token from long-lived user token."""
    print(f"[TOKEN] Step 2: getting permanent page token for page {FB_PAGE_ID}...")
    r = requests.get(
        "https://graph.facebook.com/me/accounts",
        params={"access_token": user_token},
        timeout=15,
    )
    r.raise_for_status()
    accounts = r.json().get("data", [])
    for acc in accounts:
        if acc.get("id") == FB_PAGE_ID:
            token = acc.get("access_token", "")
            print(f"[TOKEN] Permanent page token found for: {acc.get('name')}")
            return token
    # If page ID not found, list what we found
    found = [f"{a['id']} ({a.get('name','')})" for a in accounts]
    raise RuntimeError(f"Page {FB_PAGE_ID} not in accounts. Found: {found}")


def step3_verify_token(page_token):
    """Verify token works and check expiry."""
    r = requests.get(
        "https://graph.facebook.com/debug_token",
        params={
            "input_token": page_token,
            "access_token": f"{APP_ID}|{APP_SECRET}",
        },
        timeout=15,
    )
    r.raise_for_status()
    data = r.json().get("data", {})
    expires = data.get("expires_at", 0)
    is_valid = data.get("is_valid", False)
    if expires == 0:
        print("[TOKEN] Token is PERMANENT (never expires)")
    else:
        from datetime import datetime
        print(f"[TOKEN] Token valid={is_valid}, expires={datetime.fromtimestamp(expires)}")
    return is_valid or expires == 0


def step4_update_github_secret(new_token):
    """Update GitHub Secret via API using sodium encryption."""
    print(f"[TOKEN] Step 4: updating GitHub Secret {SECRET_NAME}...")

    # Get repo public key for secret encryption
    key_resp = requests.get(
        f"https://api.github.com/repos/{GH_REPO}/actions/secrets/public-key",
        headers={
            "Authorization": f"Bearer {GH_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        timeout=15,
    )
    key_resp.raise_for_status()
    key_data = key_resp.json()
    key_id   = key_data["key_id"]
    pub_key  = key_data["key"]

    # Encrypt secret using PyNaCl (libsodium)
    try:
        from nacl import encoding, public
        pub = public.PublicKey(pub_key.encode(), encoding.Base64Encoder())
        sealed = public.SealedBox(pub).encrypt(new_token.encode())
        encrypted = base64.b64encode(sealed).decode()
    except ImportError:
        # Fallback: use subprocess with openssl if nacl not available
        import subprocess, tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pub") as kf:
            kf.write(base64.b64decode(pub_key))
            kf.flush()
            result = subprocess.run(
                ["openssl", "pkeyutl", "-encrypt", "-pubin",
                 "-inkey", kf.name, "-pkeyopt", "rsa_padding_mode:oaep"],
                input=new_token.encode(), capture_output=True
            )
        encrypted = base64.b64encode(result.stdout).decode()

    # PUT the encrypted secret
    put_resp = requests.put(
        f"https://api.github.com/repos/{GH_REPO}/actions/secrets/{SECRET_NAME}",
        headers={
            "Authorization": f"Bearer {GH_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        json={
            "encrypted_value": encrypted,
            "key_id": key_id,
        },
        timeout=15,
    )
    if put_resp.status_code in (201, 204):
        print(f"[TOKEN] GitHub Secret {SECRET_NAME} updated successfully!")
    else:
        raise RuntimeError(f"Secret update failed: {put_resp.status_code} {put_resp.text}")


def main():
    print(f"[TOKEN] Starting auto-refresh at {datetime.utcnow().isoformat()}Z")

    try:
        # Step 1: get long-lived user token
        ll_token = step1_long_lived_user_token(CURRENT_TOKEN)

        # Step 2: get permanent page token
        page_token = step2_permanent_page_token(ll_token)

        # Step 3: verify it's valid/permanent
        ok = step3_verify_token(page_token)
        if not ok:
            raise RuntimeError("Token verification failed")

        # Step 4: update GitHub Secret
        step4_update_github_secret(page_token)

        print("[TOKEN] Done — permanent page token is now active.")
        return 0

    except Exception as e:
        print(f"[ERROR] Token refresh failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
