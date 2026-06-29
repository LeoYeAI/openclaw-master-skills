# RedNote Public-Web Recovery Patterns

Use this file when the first RedNote/Xiaohongshu result is partial, blocked, weakly indexed, or reduced to a search snippet.

## 1) Goal

Recover inspectable evidence from the public web without pretending you accessed the full in-app thread.

Priority order:
1. preserve the original snippet/title/caption clues
2. pivot on distinctive fragments
3. recover original or mirrored pages
4. separate originals, relays, and commentary
5. log what remains inaccessible

## 2) What to preserve immediately

Before chasing more links, capture:
- search query used
- visible result title
- visible snippet text
- URL/domain
- visible date if shown
- any prices, names, hashtags, store names, usernames, dates, or subtitle phrases
- whether the result seems to be a post, profile, note, menu image, video page, or discussion about a post

These details often disappear after the next search pivot.

## 3) Recovery pivots

Use the strongest available fragment, not generic keywords.

Best pivots:
- exact title phrase in quotes
- distinctive subtitle line in quotes
- hashtag + location
- store name + dish name + price
- notice title + date
- complaint wording + refund / contract / order / queue / course
- username + unique phrase

Weak pivots:
- generic words like `避雷`, `评价`, `值得吗`
- emotional summaries with no entity/date
- broad one-word category labels

## 4) Recovery workflow

### A. Exact-fragment recovery
1. search the visible title or subtitle fragment in quotes
2. search the same fragment with and without the entity name
3. search the fragment on `site:xiaohongshu.com` and the wider web
4. compare whether results are originals, mirrors, or quote-relays

### B. Entity-detail recovery
Use when you only have partial page access.
1. combine entity name with the strongest inspectable detail: price, product, date, district, hashtag, event name
2. search those combinations in both Chinese and English where relevant
3. search likely aliases, abbreviations, nicknames, or old names

### C. Cross-source recovery
Use when RedNote pages are thin.
1. search the same phrase on news, maps, forum, blog, or official domains
2. recover named actors, dates, and consequences
3. use those recovered facts to search back into RedNote discussion

### D. Media-led recovery
Use when the snippet points to image/video/audio evidence.
1. pivot on on-screen text, watermark, subtitle fragment, menu price, or visible date
2. separate caption-based claims from media-contained claims
3. search for reposts or mirrors quoting the same text
4. keep the claim provisional if you still cannot inspect the media itself

## 5) Source labeling after recovery

When recovery succeeds, tag the page clearly:
- **original**: likely firsthand or original host page
- **mirror/repost**: copied or republished material
- **commentary**: people discussing the original claim
- **verification**: official or documentary follow-up

Do not let a commentary page silently inherit the credibility of the original artifact.

## 6) Good recovery notes to carry into the final answer

Examples:
- "Search snippet suggested a refund dispute; exact phrase recovery found two reposts and one detailed firsthand post."
- "The indexed RedNote page was thin, but a quoted subtitle fragment recovered mirrored discussion and an official response page."
- "I recovered menu-price discussion from public reposts, but not the original image file, so the pricing claim stays medium-confidence."

## 7) When to stop

Stop escalating when:
- repeated searches return only recycled commentary
- no distinct named source emerges
- the remaining uncertainty depends on in-app comments, full media access, or login-only rendering

At that point, say what the public web does show and what artifact would most improve confidence.
