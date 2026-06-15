# uhomes.com URL Patterns

## Base Domain

All URLs use: `https://en.uhomes.com`

---

## URL Structure by Type

### University Page (use this first — most specific)
```
en.uhomes.com/{country-code}/{city-slug}/{university-slug}
```
Examples:
- `en.uhomes.com/uk/manchester/university-of-manchester`
- `en.uhomes.com/uk/london/university-college-london`
- `en.uhomes.com/uk/london/imperial-college-london`
- `en.uhomes.com/uk/london/kings-college-london`
- `en.uhomes.com/uk/london/london-school-of-economics`
- `en.uhomes.com/uk/edinburgh/university-of-edinburgh`
- `en.uhomes.com/au/sydney/university-of-sydney`
- `en.uhomes.com/au/melbourne/university-of-melbourne`
- `en.uhomes.com/us/new-york/columbia-university`
- `en.uhomes.com/us/new-york/new-york-university`

### City Page (fallback when university slug unknown)
```
en.uhomes.com/{country-code}/{city-slug}
```
Examples:
- `en.uhomes.com/uk/london`
- `en.uhomes.com/uk/manchester`
- `en.uhomes.com/au/sydney`
- `en.uhomes.com/au/melbourne`
- `en.uhomes.com/us/new-york`
- `en.uhomes.com/ca/toronto`

### Country Page (last resort)
```
en.uhomes.com/country/{country-slug}
```
Examples:
- `en.uhomes.com/country/uk`
- `en.uhomes.com/country/australia`
- `en.uhomes.com/country/us`
- `en.uhomes.com/country/canada`

---

## Country Codes

| Country | Code |
|---------|------|
| United Kingdom | `uk` |
| Australia | `au` |
| United States | `us` |
| Canada | `ca` |
| Ireland | `ie` |
| Singapore | `sg` |
| Hong Kong | `hk` |
| South Korea | `kr` |
| Japan | `jp` |
| Germany | `de` |
| France | `fr` |
| Netherlands | `nl` |
| New Zealand | `nz` |

---

## University Slug Rules

University slugs follow these conventions:
- All lowercase
- Words separated by hyphens
- "University of X" → `university-of-x`
- "X University" → `x-university`
- Common abbreviations sometimes used: `ucl`, `lse`, `mit`, `nyu`

**When in doubt**: use the full name slug and fall back to city page if the fetch returns 404 or no listings.

---

## Tracking Parameters (always append to links shown to users)

All user-facing links must carry **both** the partner `xcode` and UTM parameters:

```
?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content={city-slug}
```

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `xcode` | `000a95434637bdf71105` | uhomes partner referral code — enables attribution on the uhomes side |
| `utm_source` | `openclaw` (or `claude`) | GA4 source tracking |
| `utm_medium` | `ai_skill` | GA4 medium |
| `utm_campaign` | `student-housing-skill-v1` | GA4 campaign |
| `utm_content` | `{city-slug}` | GA4 city-level breakdown |

Set `utm_content` to the city slug (e.g. `london`, `manchester`, `sydney`).

**Important**: Fetch pages WITHOUT tracking params. Add them only to the final links presented to the user.

---

## Property Detail Page Pattern

```
en.uhomes.com/{country}/{city}/detail-apartments-{id}
```

These are found within search/listing pages. Always append tracking parameters when linking to them.

---

## Partner-Specific Pages

### Exclusive Demand Form (专属租房需求表)

For users with specific or complex requirements that standard search cannot satisfy:

```
https://www.uhomes.com/referral/demandForm?xcode=000a95434637bdf71105
```

Use this link when:
- The user's city/university is not well-covered on uhomes.com
- The user has very specific requirements (e.g. pet-friendly, specific building, accessibility needs)
- The user wants a uhomes advisor to find options for them personally

### Exclusive Website Entry (专属网站入口)

```
https://www.uhomes.com?xcode=000a95434637bdf71105
```

General-purpose entry link with partner attribution. Use as a top-level fallback.

### WeChat Mini Program (微信小程序)

For Chinese-speaking users who prefer WeChat:

| Field | Value |
|-------|-------|
| AppID | `wx787e7828382ba76a` |
| Original ID | `gh_ac67b37aa05a` |
| Path | `pages/index/index?xcode=000a95434637bdf71105` |

Provide this info when a Chinese-speaking user asks about mobile access or WeChat.
