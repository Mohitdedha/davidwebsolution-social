"""
David Web Solution — Social Media Auto-Poster
Runs via GitHub Actions 10x/day. Posts to Facebook + Instagram.
Mix: 40% informative card posts, 60% regular Pillow template posts.
"""
import os
import sys
import time
import random
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from content import generate_post
from image import get_image, upload_to_imgbb
from social import post_to_all
from informative_post import generate_informative_image, build_caption
from informative_topics import TOPICS

POSTS_PER_RUN = int(os.environ.get("POSTS_PER_RUN", "1"))
# 40% chance of informative post each run
INFORMATIVE_RATIO = float(os.environ.get("INFORMATIVE_RATIO", "0.4"))


def run():
    print("[START] David Web Solution Social Poster")
    success = 0
    errors  = []

    for i in range(POSTS_PER_RUN):
        print(f"\n[POST {i+1}/{POSTS_PER_RUN}]")
        try:
            use_informative = random.random() < INFORMATIVE_RATIO
            print(f"[TYPE] {'Informative card' if use_informative else 'Regular template'}")

            if use_informative:
                # ── Informative card post ──────────────────────────────
                topic = random.choice(TOPICS)
                print(f"[CONTENT] Topic: {topic['eyebrow']}")
                img_bytes = generate_informative_image(topic)
                caption = build_caption(topic)
                print(f"[CONTENT] Caption preview: {caption[:100]}...")
            else:
                # ── Regular Pillow template post ───────────────────────
                post = generate_post()
                print(f"[CONTENT] Pillar: {post['pillar']}")
                print(f"[CONTENT] Preview: {post['text'][:120]}...")
                img_bytes = get_image(post["pillar"], post["text"])
                caption = post["text"]

            image_url = None
            if img_bytes:
                slug = "informative" if use_informative else post["pillar"].replace("_", "-")
                image_url = upload_to_imgbb(img_bytes, f"dws-{slug}-{int(time.time())}.jpg")

            # Post to FB + IG
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
