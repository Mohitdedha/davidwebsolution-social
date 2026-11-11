"""
David Web Solution — Social Media Auto-Poster
Runs via GitHub Actions hourly. Posts to Facebook + Instagram.
100% informative card posts (dark_pro template removed permanently).

No-repeat rule: every topic is posted once only. Posted topics are recorded in
data/posted_topics.json (committed back by the workflow). When the written
pool is used up, a fresh topic is generated with Groq and checked against the
full history. If no new topic can be produced, the run skips posting rather
than repeating an old post.
"""
import os
import re
import sys
import json
import time
import datetime
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from image import upload_to_imgbb
from social import post_to_all, post_reel
from informative_post import generate_informative_image, build_caption
from informative_topics import TOPICS
from festival_calendar import get_today_festival
from festival_post import generate_festival_post, build_festival_caption

try:
    from informative_topics import TREND_TOPIC_START
except ImportError:
    TREND_TOPIC_START = 0

POSTS_PER_RUN = int(os.environ.get("POSTS_PER_RUN", "1"))

# ── Posted-topics history (no repeats, ever) ───────────────────────────────
HISTORY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "posted_topics.json")
GROQ_MODEL = "openai/gpt-oss-20b"
SIMILARITY_LIMIT = 0.6   # headlines sharing this share of words count as a repeat
_STOPWORDS = {"a", "an", "the", "your", "you", "youre", "is", "are", "to", "of", "in",
              "on", "for", "and", "or", "that", "this", "why", "how", "it", "its",
              "not", "from", "with", "be", "by", "at"}
_THEMES = [
    "website design and user experience", "SEO and Google rankings",
    "AI search, AI Overviews and GEO", "AI UGC video ads", "ecommerce and online stores",
    "Instagram and social media growth", "Google Ads and paid ads", "email marketing",
    "branding and trust", "lead generation and conversion rate", "WordPress and website care",
    "local SEO and Google Business Profile", "analytics and tracking",
    "content marketing and short-form video", "AI tools and automation for small businesses",
]


def _words(headline):
    text = " ".join(headline) if isinstance(headline, (list, tuple)) else str(headline)
    return [w for w in re.sub(r"[^a-z0-9 ]", "", text.lower()).split() if w]


def _key(topic):
    return " ".join(_words(topic.get("headline", "")))


def _load_history():
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data.get("posted"), list):
            return data
    except FileNotFoundError:
        pass
    except Exception as e:
        # Never fall back to an empty history: that would allow repeats.
        raise RuntimeError(f"posted_topics.json is unreadable: {e}")
    # First run: topics that were already posted before this system existed.
    seeded = [{"key": _key(t), "eyebrow": t["eyebrow"], "date": "before-2026-11-12"}
              for t in TOPICS[:TREND_TOPIC_START]]
    return {"posted": seeded}


def _save_history(history):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=1)


def _is_repeat(topic, history):
    key = _key(topic)
    new = set(key.split()) - _STOPWORDS
    for item in history["posted"]:
        old_key = item.get("key", "")
        if key == old_key:
            return True
        old = set(old_key.split()) - _STOPWORDS
        if new and old and len(new & old) / len(new | old) >= SIMILARITY_LIMIT:
            return True
    return False


def _valid_topic(t):
    try:
        if not (isinstance(t["eyebrow"], str) and 3 <= len(t["eyebrow"]) <= 28):
            return False
        if not (isinstance(t["headline"], list) and len(t["headline"]) == 3
                and all(isinstance(h, str) and 2 <= len(h) <= 20 for h in t["headline"])):
            return False
        if not (isinstance(t["sub"], str) and 10 <= len(t["sub"]) <= 70):
            return False
        if not (isinstance(t["pills"], list) and len(t["pills"]) == 3):
            return False
        for p in t["pills"]:
            if not (len(p) == 2 and 3 <= len(p[0]) <= 34 and 10 <= len(p[1]) <= 85):
                return False
        if not (isinstance(t["cta"], str) and len(t["cta"]) <= 48 and re.search(r'DM "[A-Z]{2,12}"', t["cta"])):
            return False
    except (KeyError, TypeError):
        return False
    blob = json.dumps(t)
    # No statistics, years, hashtags or emojis: these go stale or can't be verified.
    if "%" in blob or "#" in blob or re.search(r"\b20\d\d\b", blob) or re.search(r"\\u[0-9a-f]{4}", re.sub(r"\\u201[489cd]", "", blob)):
        return False
    return True


def _generate_topic(history):
    """Ask Groq for a brand-new topic that is unlike anything already posted."""
    try:
        from groq import Groq
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
    except Exception as e:
        print(f"[GEN] Groq unavailable: {e}")
        return None

    used = [f"- {i.get('eyebrow', '')}: {i.get('key', '')}" for i in history["posted"]][-150:]
    theme = _THEMES[len(history["posted"]) % len(_THEMES)]
    prompt = f"""You write Instagram card posts for David Web Solution, a digital agency
(web design, SEO, AI UGC video ads, ecommerce) serving business owners in the US and UK.

Write ONE new post topic about: {theme}.
It must cover a different idea from every topic already posted:
{chr(10).join(used)}

Return ONLY a JSON object with exactly these keys:
"eyebrow": category label in CAPITALS, max 26 characters
"headline": array of exactly 3 short lines, each max 18 characters, reading as one sentence
"sub": one supporting sentence, max 65 characters
"pills": array of exactly 3 items, each [title (max 32 characters), description (max 80 characters)]
"cta": call to action, max 44 characters, ending with — DM "KEYWORD" (KEYWORD = one word in capitals)

Rules: plain practical advice a business owner can act on. No statistics, no percentages,
no numbers presented as facts, no years, no hashtags, no emojis."""

    for attempt in range(4):
        try:
            resp = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=700,
            )
            raw = resp.choices[0].message.content or ""
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            topic = json.loads(match.group(0)) if match else None
            if not topic or not _valid_topic(topic):
                print(f"[GEN] Attempt {attempt + 1}: invalid format, retrying")
                continue
            topic["eyebrow"] = topic["eyebrow"].upper()
            topic["pills"] = [tuple(p) for p in topic["pills"]]
            if _is_repeat(topic, history):
                print(f"[GEN] Attempt {attempt + 1}: too close to an old post, retrying")
                continue
            return topic
        except Exception as e:
            print(f"[GEN] Attempt {attempt + 1} error: {str(e)[:120]}")
            time.sleep(3)
    return None


def _pick_topic(history):
    # 1) Written pool: newest (trend) topics first, then the rest, in file order.
    order = list(range(TREND_TOPIC_START, len(TOPICS))) + list(range(TREND_TOPIC_START))
    for i in order:
        if not _is_repeat(TOPICS[i], history):
            return TOPICS[i]
    # 2) Pool used up: generate a new one.
    print("[CONTENT] Written topics are all used — generating a new one")
    return _generate_topic(history)


def run():
    print("[START] David Web Solution Social Poster")
    success = 0
    errors = []
    history = _load_history()
    print(f"[HISTORY] {len(history['posted'])} topics already posted")

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
            topic = _pick_topic(history)
            if topic is None:
                print("[SKIP] No new topic available — not posting, to avoid a repeat")
                continue
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
                history["posted"].append({
                    "key": _key(topic),
                    "eyebrow": topic["eyebrow"],
                    "date": datetime.date.today().isoformat(),
                })
                _save_history(history)
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
