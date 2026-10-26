"""
AI content generator for David Web Solution social media posts.
Target: US/UK audience, WordPress agency niche.
"""
import os
import random
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

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
    "wordpress_tip": """Write a short, punchy social media post (150-200 words) about a practical WordPress tip for small business owners in the US or UK.
Topic ideas: speed optimisation, security, SEO plugins, WooCommerce, page builders, backups, custom post types, staging sites.
Tone: friendly expert. No fluff. Start with a strong hook line.
End with: 1 clear call-to-action (DM us / comment below / link in bio).
Add 5-7 relevant hashtags on a new line.""",

    "seo_tip": """Write a short social media post (150-200 words) sharing one specific SEO tip that helps a UK or US local business rank higher on Google.
Topic ideas: Google Business Profile, Core Web Vitals, schema markup, internal linking, meta descriptions, E-E-A-T, local citations, image alt text.
Tone: direct, no jargon unless explained. Start with a hook.
End with a CTA and 5-7 hashtags.""",

    "ai_video_ugc": """Write a social media post (150-200 words) about AI video or UGC ads for businesses.
Topic ideas: how AI-generated UGC ads outperform traditional ads, tools we use (HeyGen, ElevenLabs, Runway), cost savings, client results, how to brief a UGC creator.
Tone: forward-thinking, exciting. Target US/UK e-commerce or service businesses.
Hook first, then value, then CTA + 5-7 hashtags.""",

    "web_mistake": """Write a social media post (150-200 words) about a common website mistake that costs businesses money or leads.
Topic ideas: slow load time, no SSL, no mobile version, unclear CTA, stock photos, missing contact info, no Google Analytics, bad navigation.
Tone: slightly alarming but helpful. Hook: "Most [business type] websites make this mistake..."
End with CTA + 5-7 hashtags.""",

    "client_result": """Write a social media post (150-200 words) as a web agency sharing a (realistic, hypothetical) client win.
Example: "We rebuilt a UK plumber's website last month. Load time dropped from 8s to 1.2s. Enquiries up 40% in 30 days."
Keep it specific with numbers. Don't name the client. Tone: proud but humble.
End with CTA (want results like this? DM us) + 5-7 hashtags.""",

    "tool_spotlight": """Write a social media post (150-200 words) spotlighting one tool we use in our web/SEO/AI workflow.
Pick one: Elementor Pro, WP Rocket, Rank Math, Ahrefs, Canva Pro, HeyGen, ElevenLabs, Figma, Semrush, GTmetrix, Cloudflare, Gravity Forms.
Share: what it does, why we love it, one tip for using it. Tone: knowledgeable peer.
End with CTA + 5-7 hashtags.""",

    "industry_insight": """Write a social media post (150-200 words) sharing an insight or trend about web development, SEO or digital marketing relevant to US/UK businesses in 2025.
Topic ideas: AI in web design, voice search, Core Web Vitals update, cookie-less tracking, video SEO, mobile-first indexing.
Tone: thought leader. Start with a surprising stat or bold claim.
End with CTA + 5-7 hashtags.""",
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

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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

    text = response.choices[0].message.content.strip()
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
