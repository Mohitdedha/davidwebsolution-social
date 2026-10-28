"""
Weekly trend updater for David Web Solution automation.
Uses Groq to generate 35 fresh trending hashtags for US/UK/Global
digital marketing audience, then patches informative_post.py.
Run via GitHub Actions every Sunday.
"""
import os, re, sys

try:
    from groq import Groq
except ImportError:
    print("[ERROR] groq not installed")
    sys.exit(1)

PROMPT = """You manage Instagram for a digital agency called David Web Solution.
Target audience: business owners and startups in US, UK, and globally.
Services: web design, SEO, Google Ads, AI UGC video ads, ecommerce.

Give me exactly 35 Instagram hashtags that are currently trending for this niche.
Mix: digital marketing, web design, SEO, small business, US business, UK business,
ecommerce, AI marketing, agency life, entrepreneur.

Rules:
- Each hashtag starts with #
- No spaces inside a hashtag
- No numbering, no explanation
- One hashtag per line
- Only 35 hashtags total

Output ONLY the hashtags, nothing else."""


def fetch_trending_hashtags() -> list[str]:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": PROMPT}],
        temperature=0.7,
        max_tokens=600,
    )
    raw = resp.choices[0].message.content.strip()
    tags = []
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("#") and " " not in line and len(line) > 2:
            tags.append(line)
    return tags[:35]


def patch_informative_post(tags: list[str]) -> bool:
    path = os.path.join(os.path.dirname(__file__), "informative_post.py")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Build new pool string
    lines = []
    chunk = []
    for i, tag in enumerate(tags):
        chunk.append(f'"{tag}"')
        if len(chunk) == 5 or i == len(tags) - 1:
            lines.append("    " + ", ".join(chunk) + ",")
            chunk = []
    new_pool = "_HASHTAG_POOL = [\n" + "\n".join(lines) + "\n]"

    # Replace existing pool
    patched = re.sub(
        r"_HASHTAG_POOL\s*=\s*\[.*?\]",
        new_pool,
        content,
        flags=re.DOTALL,
    )
    if patched == content:
        print("[WARN] Pattern not matched — pool not updated")
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(patched)
    return True


if __name__ == "__main__":
    print("[TRENDS] Fetching trending hashtags via Groq...")
    tags = fetch_trending_hashtags()
    if len(tags) < 10:
        print(f"[ERROR] Only got {len(tags)} tags — aborting")
        sys.exit(1)
    print(f"[TRENDS] Got {len(tags)} tags:")
    for t in tags:
        print(" ", t)

    ok = patch_informative_post(tags)
    if ok:
        print("[TRENDS] informative_post.py patched successfully")
    else:
        sys.exit(1)
