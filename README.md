# David Web Solution — Social Media Auto-Poster

Auto-posts 4x/day to Facebook + Instagram using Groq AI.

## Secrets Required (GitHub → Settings → Secrets)

| Secret | Value |
|--------|-------|
| `GROQ_API_KEY` | Same as India BBC News project |
| `DWS_FB_PAGE_ID` | David Web Solution Facebook Page ID |
| `DWS_FB_PAGE_TOKEN` | Long-lived Page Access Token |
| `DWS_IG_ACCOUNT_ID` | Instagram Business Account ID (linked to FB page) |
| `UNSPLASH_ACCESS_KEY` | Free from unsplash.com/developers |
| `IMGBB_API_KEY` | Free from api.imgbb.com |

## Content Pillars
- WordPress tips (25%)
- SEO tips (20%)
- AI video / UGC ads (15%)
- Web mistakes (15%)
- Client results (10%)
- Tool spotlights (10%)
- Industry insights (5%)

## Getting Page Token
1. Go to developers.facebook.com/tools/explorer
2. Select IndiaBBCNews app → Generate Access Token → Allow David Web Solution page
3. Click "David Web Solution" under Page Access Tokens
4. Copy token → run through Token Debugger → get long-lived token
