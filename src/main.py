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
from social import post_to_all, post_reel
from informative_post import generate_informative_image, build_caption
from informative_topics import TOPICS
from reel_maker import generate_reel

POSTS_PER_RUN    = int(os.environ.get("POSTS_PER_RUN", "1"))
INFORMATIVE_RATIO = float(os.environ.get("INFORMATIVE_RATIO", "0.4"))
REEL_RATIO        = float(os.environ.get("REEL_RATIO", "0.3"))  # 30% chance of reel

# Track recently used topics this run to avoid repeats
_used_topics: list[str] = []

def _pick_topic():
    """Pick a topic not used recently in this run."""
    available = [t for t in TOPICS if t["eyebrow"] not in _used_topics]
    if not available:
        available = TOPICS  # reset if all used
    topic = random.choice(available)
    _used_topics.append(topic["eyebrow"])
    if len(_used_topics) > max(len(TOPICS) // 2, 10):
        _used_topics.pop(0)
    return topic


def run():
    print("[START] David Web Solution Social Poster")
    success = 0
    errors  = []

    for i in range(POSTS_PER_RUN):
        print(f"\n[POST {i+1}/{POSTS_PER_RUN}]")
        try:
            use_informative = random.random() < INFORMATIVE_RATIO
            print(f"[TYPE] {'Informative card' if use_informative else 'Regular template'}")

            use_reel = random.random() < REEL_RATIO
            if use_informative and use_reel:
                # ── Informative Reel ───────────────────────────────────
                topic = _pick_topic()
                print(f"[CONTENT] Reel topic: {topic['eyebrow']}")
                caption = build_caption(topic)
                video_bytes = generate_reel(topic)
                if video_bytes:
                    slug = f"dws-reel-{int(time.time())}.mp4"
                    video_url = upload_to_imgbb(video_bytes, slug)
                    if video_url:
                        reel_id = post_reel(video_url, caption)
                        if reel_id:
                            success += 1
                            print(f"[OK] Reel posted: {reel_id}")
                        else:
                            print("[WARN] Reel post failed — fallback to image")
                            img_bytes = generate_informative_image(topic)
                            image_url = upload_to_imgbb(img_bytes, f"dws-informative-{int(time.time())}.jpg")
                            results = post_to_all(caption, image_url)
                            if results.get("facebook") or results.get("instagram"):
                                success += 1
                    else:
                        print("[WARN] Video upload failed")
                else:
                    # FFmpeg not available — fallback to image
                    img_bytes = generate_informative_image(topic)
                    image_url = upload_to_imgbb(img_bytes, f"dws-informative-{int(time.time())}.jpg")
                    results = post_to_all(caption, image_url)
                    if results.get("facebook") or results.get("instagram"):
                        success += 1
                continue

            if use_informative:
                # ── Informative card post ──────────────────────────────
                topic = _pick_topic()
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
