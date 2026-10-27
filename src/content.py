"""
AI content generator for David Web Solution social media posts.
Target: US/UK audience, WordPress agency niche.
"""
import os
import random
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

# Current world trends injected into prompts to keep content fresh
WORLD_TRENDS = [
    "AI automation tools replacing manual agency work in 2025",
    "Google's AI Overviews changing SEO strategy for small businesses",
    "Short-form video dominating B2B marketing (LinkedIn Reels, IG Reels)",
    "Local SEO surge as more consumers search 'near me' on mobile",
    "No-code/low-code WordPress tools empowering non-tech business owners",
    "AI UGC ads outperforming traditional video ads by 3x on Meta",
    "Core Web Vitals 2025 update impacting Google search rankings",
    "WhatsApp Business API becoming key lead gen tool for agencies",
    "Voice search SEO growing with smart home device adoption",
    "Shopify vs WooCommerce debate heating up for UK/US e-commerce",
]

# Content pillars with weights (higher = posted more often)
CONTENT_PILLARS = [
    ("wordpress_tip",      25),
    ("seo_tip",            20),
    ("ai_video_ugc",       15),
    ("web_mistake",        15),
    ("client_result",      10),
    ("tool_spotlight",     10),
    ("industry_insight",    5),
]

PILLAR_PROMPTS = {
    "wordpress_tip": """Write a punchy, value-packed social media post (120-160 words) sharing ONE specific WordPress tip for small business owners in the US or UK.

Rules:
- Start with a bold hook (problem or surprising fact)
- Give 3-5 concrete, actionable bullet points
- Each bullet = one specific fix, not vague advice
- End with ONE clear CTA (DM us / comment SPEED below / link in bio)
- NO hashtags. NO emojis. Plain text only.
- Write like you are talking to a business owner, not a developer

Topic ideas: speed optimisation, security, caching plugins, image compression, staging sites, WooCommerce tips.""",

    "seo_tip": """Write a punchy social media post (120-160 words) sharing ONE specific SEO tip for UK or US local businesses.

Rules:
- Hook first: surprising stat or common mistake
- 3-5 specific bullet points with real actions (not "optimise your site")
- End with ONE CTA (DM us FREE / comment SEO)
- NO hashtags. NO emojis. Plain text only.
- Be specific: mention exact tools, numbers, timelines

Topic ideas: Google Business Profile, Core Web Vitals, local citations, review strategy, page speed.""",

    "ai_video_ugc": """Write a social media post (120-160 words) about how AI video or UGC ads can help US/UK businesses get more customers.

Rules:
- Hook: bold claim or result (e.g. "AI ads are 3x cheaper than traditional video")
- 3-4 bullet points with real value (tools, costs, results)
- ONE CTA at the end
- NO hashtags. NO emojis. Plain text only.""",

    "web_mistake": """Write a social media post (120-160 words) about one costly website mistake that business owners make.

Rules:
- Hook: "Most [type] business websites are losing leads because of this..."
- List 4-5 specific mistakes with real consequences (lost revenue, Google penalty, etc.)
- End: "We fix all of this — DM AUDIT for a free check"
- NO hashtags. NO emojis. Plain text only.
- Be specific: mention numbers, real tools, real impact.""",

    "client_result": """Write a social media post (120-160 words) sharing a realistic client result story.

Rules:
- One specific scenario: plumber, restaurant, dentist, solicitor, e-commerce store in UK or US
- Real numbers: before/after load time, enquiry increase %, revenue gained
- 3-4 bullet points of what was done
- End: "Want results like this? DM us RESULT"
- NO hashtags. NO emojis. Plain text only. Do not name the client.""",

    "tool_spotlight": """Write a social media post (120-160 words) spotlighting one specific tool from our agency workflow.

Rules:
- Pick one tool: WP Rocket, Rank Math, Ahrefs, HeyGen, ElevenLabs, Figma, Semrush, GTmetrix, Cloudflare
- Explain: what it does in one line, why we use it, one pro tip
- End with CTA
- NO hashtags. NO emojis. Plain text only.""",

    "industry_insight": """Write a social media post (120-160 words) about one important trend in web, SEO or digital marketing for 2025.

Rules:
- Open with a surprising stat or bold claim
- 3-4 bullet points explaining what it means for business owners
- Tell them what to do about it
- End with CTA
- NO hashtags. NO emojis. Plain text only.""",
}

IMAGE_PROMPTS = {
    "wordpress_tip":    "Clean minimal flat design, WordPress logo, blue and white, professional agency style",
    "seo_tip":          "Google search bar rising arrow graph, green and white, clean modern design",
    "ai_video_ugc":     "Futuristic AI robot creating video content, purple gradient, modern tech aesthetic",
    "web_mistake":      "Red warning icon on laptop screen, website error concept, flat design",
    "client_result":    "Dashboard showing upward stats growth chart, blue green gradient, success concept",
    "tool_spotlight":   "Tech tool logo spotlight, dark background with neon accents, modern minimal",
    "industry_insight": "Digital trends futuristic concept, globe with data streams, blue purple gradient",
}


def pick_pillar() -> str:
    pillars, weights = zip(*CONTENT_PILLARS)
    return random.choices(pillars, weights=weights, k=1)[0]


def generate_post(pillar: str | None = None) -> dict:
    if not pillar:
        pillar = pick_pillar()

    prompt = PILLAR_PROMPTS[pillar]
    trend  = random.choice(WORLD_TRENDS)
    prompt = f"[Current world trend to reference naturally if relevant: {trend}]\n\n{prompt}"

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": (
                "You are a social media manager for David Web Solution, a web development agency "
                "based in Delhi, India serving US and UK clients. Services: WordPress websites, "
                "SEO, AI video/UGC ads, Flutter apps, Shopify stores, AI automation. "
                "Write engaging posts that attract business owners in the US and UK who need a website or digital presence."
            )},
            {"role": "user", "content": prompt},
        ],
        temperature=0.85,
        max_tokens=400,
    )

    import re
    text = response.choices[0].message.content.strip()
    # Strip markdown bold/italic markers
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    # Remove all hashtag lines and inline hashtags
    text = re.sub(r'#\w+', '', text)
    # Remove lines that are now empty or just whitespace/punctuation
    lines = [l.rstrip() for l in text.splitlines()]
    lines = [l for l in lines if l.strip() and not all(c in ' |,-.' for c in l.strip())]
    text = '\n'.join(lines).strip()
    image_prompt = IMAGE_PROMPTS.get(pillar, "Professional web agency social media graphic, blue white modern design")

    return {
        "pillar": pillar,
        "text": text,
        "image_prompt": image_prompt,
    }


if __name__ == "__main__":
    post = generate_post()
    print(f"Pillar: {post['pillar']}\n")
    print(post["text"])
