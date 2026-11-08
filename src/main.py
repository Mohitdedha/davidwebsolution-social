"""
David Web Solution — Social Media Auto-Poster
Runs via GitHub Actions hourly. Posts to Facebook + Instagram.
100% informative card posts (dark_pro template removed permanently).
"""
import os
import sys
import time
import random
import datetime
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from image import upload_to_imgbb
from social import post_to_all, post_reel
from informative_post import generate_informative_image, build_caption
from informative_topics import TOPICS
from festival_calendar import get_today_festival
from festival_post import generate_festival_post, build_festival_caption

POSTS_PER_RUN = int(os.environ.get("POSTS_PER_RUN", "1"))

# Cross-run topic rotation: seed by (date_ordinal * 100 + run_number)
_RUN_NUM          = int(os.environ.get("GITHUB_RUN_NUMBER", "0"))
_DATE_ORD         = datetime.date.today().toordinal()
_topic_rng        = random.Random(_DATE_ORD * 100 + _RUN_NUM)
_shuffled_topics  = list(TOPICS)
_topic_rng.shuffle(_shuffled_topics)
_topic_idx        = 0

def _pick_topic():
    global _topic_idx
    topic = _shuffled_topics[_topic_idx % len(_shuffled_topics)]
    _topic_idx += 1
    return topic


def run():
    print("[START] David Web Solution Social Poster")
    success = 0
    errors  = []

    # ── Festival check first ───────────────────────────────────────────────
    festival = get_today_festival()
    if festival:
        print(f"\n[FESTIVAL] {festival['name']} detected — posting festival greeting")
        try:
            img_bytes = generate_festival_post(festival)
            caption   = build_festival_caption(festival)
            image_url = upload_to_imgbb(img_bytes, f"dws-festival-{festival['name'].replace(' ','-')}.jpg")
            results   = post_to_all(caption, image_url)
            if results.get("facebook") or results.get("instagram"):
                success += 1
                print(f"[FESTIVAL] Posted. FB={results['facebook']} IG={results['instagram']}")
        except Exception as e:
            print(f"[FESTIVAL] Error: {e}")
            traceback.print_exc()
        time.sleep(8)

    # ── Informative card posts (100%) ──────────────────────────────────────
    for i in range(POSTS_PER_RUN):
        print(f"\n[POST {i+1}/{POSTS_PER_RUN}]")
        try:
            topic = _pick_topic()
            print(f"[CONTENT] Topic: {topic['eyebrow']}")
            img_bytes = generate_informative_image(topic)
            caption   = build_caption(topic)
            print(f"[CONTENT] Caption: {caption[:100]}...")

            image_url = upload_to_imgbb(img_bytes, f"dws-informative-{int(time.time())}.jpg")

            print("[POST] Publishing...")
            results = post_to_all(caption, image_url)

            if results.get("facebook") or results.get("instagram"):
                success += 1
                print(f"[OK] Posted. FB={results['facebook']} IG={results['instagram']}")
            else:
                errors.append(f"Post {i+1}: both FB and IG failed")

        except Exception as e:
            err = f"Post {i+1} error: {str(e)[:150]}"
            print(f"[ERROR] {err}")
            traceback.print_exc()
            errors.append(err)

        if i < POSTS_PER_RUN - 1:
            time.sleep(10)

    print(f"\n[DONE] Success: {success}/{POSTS_PER_RUN} | Errors: {len(errors)}")
    if errors:
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
