# Apify Discovery & Token Costs

Research on using Apify for competitor discovery and understanding token/cost implications.

---

## Discovery Actors Available

| Actor | Purpose | Pricing |
|-------|---------|---------|
| [Instagram Hashtag Scraper](https://apify.com/apify/instagram-hashtag-scraper) | Find posts/accounts by hashtag | ~$0.40-0.50/1K results |
| [Instagram Search Scraper](https://apify.com/apify/instagram-search-scraper) | Search accounts by keyword | ~$2.60/1K results |
| [Instagram Related Person Scraper](https://apify.com/scrapio/instagram-related-person-scraper) | Find similar accounts to known handles | $14.99/mo + usage |
| [Instagram Profile Scraper](https://apify.com/apify/instagram-profile-scraper) | Mine specific profiles | ~$0.40-0.50/1K results |

---

## Competitor Discovery Workflows

### 1. Hashtag Discovery
User doesn't know competitors. Find them via niche hashtags.

```
Input: "#contentcreator", "#ugccreator", "#reelsmarketing"
Output: Accounts posting with those hashtags + engagement metrics
```

### 2. Keyword Search
Search for accounts matching terms.

```
Input: "content strategist", "UGC creator"
Output: Matching profiles with follower counts, bios
```

### 3. Similar Accounts (Related Person)
Start with 1-2 known competitors, find their "suggested" accounts.

```
Input: @known_competitor
Output: Instagram's related accounts suggestions
```

### 4. Engagement Network
Mine who known competitors engage with (comments, tags).

```
Input: @competitor posts
Output: Accounts they tag, accounts commenting
```

---

## Token Costs (Claude Context)

**The data Apify returns becomes Claude tokens.**

| Data Volume | Approx. Tokens | Notes |
|-------------|----------------|-------|
| 10 posts/competitor | ~3-5k | Minimal scan |
| 30 posts/competitor | ~10-15k | Standard mine |
| 50+ posts/competitor | ~20-25k | Deep mine |

### Limits
- MAX_MCP_OUTPUT_TOKENS default: 25,000
- Warning threshold: 10,000 tokens
- Each post includes: caption, metrics, timestamps, hashtags, user data

### Controlling Token Usage

1. **Limit posts per competitor** — "top 5 posts" vs "top 20 posts"
2. **Limit competitors per run** — Mine 2-3, not 10
3. **Request specific fields** — Some actors let you filter output fields
4. **Quick scan vs deep mine** — Offer user the choice

---

## Apify Credit Costs

| Tier | Credits | Approx. Posts |
|------|---------|---------------|
| Free | $5 | ~2,000 posts |
| Starter | $49/mo | ~20,000 posts |
| Scale | $499/mo | ~200,000 posts |

Most users stay on free tier. ~2000 posts/month covers:
- 3 competitors × 20 posts × 4 mining sessions = 240 posts
- Plenty of headroom for discovery searches

---

## MCP Integration Notes

### Dynamic Actor Discovery
The MCP server has `discover-actors` tool — can search for new actors by keyword:

```
"Find actors for Instagram hashtag analysis"
→ Returns available actors matching query
```

### Adding Actors
Can dynamically add actors as tools without reconfiguring:

```
add-actor-as-tool apify/instagram-hashtag-scraper
```

### Selective Loading
Reduce context by specifying only needed actors:

```bash
npx @apify/actors-mcp-server --tools apify/instagram-profile-scraper
```

---

## Recommendations for /content Skill

1. **Default to Profile Scraper** — Already configured, most common use
2. **Offer discovery when handles.md is empty** — "Want me to help find competitors?"
3. **Show token estimate before running** — Builds trust, prevents surprise
4. **Quick vs deep scan** — Let user control depth
5. **Cache/reuse mining** — Don't re-mine same handles same day

---

## Sources

- [Apify MCP Documentation](https://docs.apify.com/platform/integrations/mcp)
- [Instagram Hashtag Scraper](https://apify.com/apify/instagram-hashtag-scraper)
- [Instagram Search Scraper](https://apify.com/apify/instagram-search-scraper)
- [Instagram Related Person Scraper](https://apify.com/scrapio/instagram-related-person-scraper)
- [Apify Pricing](https://apify.com/pricing)
- [Claude Code MCP Token Management](https://github.com/anthropics/claude-code/issues/7172)
