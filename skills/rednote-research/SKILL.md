---
name: rednote-research
description: Research a topic through RedNote/Xiaohongshu discussion signals using either public-web mode (no login) or optional login-enhanced browser review when the user explicitly chooses deeper access. Use when checking RedNote community sentiment, reputation, latest policy/community updates, gossip/drama/news synthesis, local recommendations like restaurants/shops, when recovering evidence from weak public-web snippets/titles/OCR/subtitle fragments, or when analyzing posts, comments, screenshots, image posts, video/gif snippets, subtitles, or audio/transcript clues. Especially useful for prompts like "查小红书口碑", "搜 RedNote 讨论", "看看最近有什么风向/新政策", "总结八卦/争议", "找本地探店推荐", "分析评论区", "分析截图/视频/字幕", "根据截图线索继续搜", "总结某个账号最近发了什么", or "做一个 RedNote 社区情报初筛".
---

# RedNote Community Intelligence

Research a topic with a RedNote/Xiaohongshu-first lens. Default to public-web mode, but support an optional login-enhanced path when the user explicitly wants fuller coverage. Expand queries deliberately, collect signals from multiple source types, separate evidence from vibe, and return a concise report that is honest about uncertainty.

## Access modes

Read `references/access-modes.md` when deciding whether to stay in public-web mode or offer login-enhanced browser review.
Read `references/login-enhanced-workflow.md` when the user explicitly chooses deeper access and you need an execution pattern for authenticated review.
Read `references/minimal-user-input-paths.md` when public-web access is weak and the user prefers not to log in.
Read `references/account-summary-template.md` when the task is to summarize a creator/account or recent posting behavior.

Default behavior:
- start in public-web mode
- do not assume login
- if the user wants fuller account-level, recent-post, or comment-level coverage, offer the login-enhanced path as an explicit choice
- if the user declines login, ask for the smallest useful seed input instead of giving up
- state in the final answer whether findings came from public-web mode or login-enhanced mode

## Core operating rules

- Treat RedNote as a signal-discovery layer, not final proof.
- Prefer a few inspectable sources over many shallow snippets.
- Separate direct evidence, repeated anecdote, platform chatter, and rumor.
- Put dates on fast-moving claims whenever possible.
- Do not imply access to hidden comments, full threads, or app-only media.
- If a page is inaccessible, do not overclaim from the search snippet alone.
- Keep modality explicit: text-page, screenshot, image, video, gif, audio, or transcript.
- Separate extraction from interpretation: OCR/ASR output is evidence, not automatic truth.
- When media access is partial, say exactly what is visible and what remains uninspectable.

## Default workflow

1. Clarify the subject, time scope, geography, output goal, and whether the user wants no-login mode or login-enhanced mode.
2. Start in public-web mode unless the user explicitly chooses login-enhanced mode.
3. Build a compact query set with mixed query families.
4. Search broadly across RedNote, official sources, media, and supporting review sites.
5. If public-web coverage is too thin for the task, explain that and offer login-enhanced browser review as the next step.
6. Extract recurring claims, contradictions, and missing evidence.
7. Score credibility separately from risk or recommendation strength.
8. Deliver a short report with links, caveats, next checks, and a brief note about which access mode was used.

## 1) Clarify the research target

Identify:
- canonical name in Chinese and English
- aliases, abbreviations, nicknames, hashtags, old names
- category: `education`, `policy`, `gossip`, `local`, or `general`
- geography if relevant: city, district, mall, campus, country, online/offline
- time scope: latest 7 days, latest month, current season, or broader background
- user intent: reputation check, update scan, controversy synthesis, shortlist, comment analysis, or post/video analysis

If the prompt is broad, infer likely aliases before searching.

For account-summary tasks, ask for the smallest useful identifier if available: profile URL, user ID/handle, screenshot, copied title list, or 3-5 recent note links. If the user wants fuller coverage and agrees to log in, switch from public-web mode to login-enhanced browser review instead of pretending public-web search is complete. If the user does not want login, read `references/minimal-user-input-paths.md` and ask for the least burdensome seed material that will improve coverage.

## 2) Build queries

Use `scripts/query_builder.py` when deterministic query expansion would help, especially if you need a media-focused query set or a starter claim log schema.
Use `scripts/recovery_query_builder.py` when your starting point is weak public-web evidence: a thin search snippet, partial title, OCR fragment, subtitle line, hashtag, price, or visible date that needs recovery-oriented search pivots.

Prefer a mixed query set instead of one giant keyword dump:
- `overview`: baseline discovery
- `latest`: newest updates and recent turns in sentiment
- `trending`: hot discussion and rumor-tracking discovery
- `comment`: comment-area reactions and repeated talking points
- `review`: reputation, quality, warning signs, user experience
- `recommendation`: worth-it, shortlist, comparison, local picks
- `verification`: official notices, registration records, named responses, implementation details

Typical source patterns:
- `site:xiaohongshu.com <entity> <modifier>`
- `site:www.xiaohongshu.com <entity> <modifier>`
- `<entity> 小红书 <modifier>`
- `<entity> <modifier>`

Category hints:
- `education`: 口碑, 避雷, 退费, 课程质量, 就业, offer, 合同, 维权
- `policy`: 政策, 新规, 通知, 官方回应, 执行, 解读, 影响
- `gossip`: 爆料, 八卦, 翻车, 塌房, 争议, 后续, 聊天记录, 回应
- `local`: 推荐, 探店, 菜品, 排队, 价格, 服务, 环境, 值不值, 避雷
- `general`: 评价, 口碑, 体验, 真实反馈, 怎么样, 值不值

Query-building heuristics:
- Start with 8-16 queries, not 40+.
- Mix discovery queries with 2-4 verification queries.
- Add geography for local or policy tasks.
- Use a narrow time scope for fast-moving topics.
- Search aliases and nicknames when drama or local slang is involved.
- For cross-market topics, run both Chinese and English variants.

## 3) Search public-web sources

Prefer breadth before depth. Search first, then fetch only the strongest pages.

Target source mix:
- RedNote/Xiaohongshu indexed pages and snippets
- official statements, brands, schools, stores, regulators, or platform notices
- reputable media reports for disputes or policy coverage
- maps/review/listing sites for local businesses
- forums and other community sites only as supplementary anecdotal signals

Search heuristics:
- favor recency for policy, gossip, and local recommendations
- keep a short source list with one-line relevance notes
- search exact names, aliases, hashtags, and comparison targets
- cross-check surprising claims with at least one non-RedNote source when possible
- if the task is about a specific account and public-web search returns thin results, say so explicitly instead of overclaiming; then offer the login-enhanced path or ask for a few seed links/screenshots

## 4) Extract claims and discussion patterns

Normalize findings into compact bullets with fields like:
- claim type: complaint / praise / neutral fact / official claim / media report / rumor / recommendation
- theme: pricing, quality, service, fraud risk, policy impact, taste, queue, environment, controversy, support, etc.
- evidence snippet
- source URL
- source class
- visible date
- repetition count if multiple sources echo the same point

Read `references/output-patterns.md` when you need output templates or comment clustering patterns.
Read `references/claim-log-schema.md` when the task is evidence-heavy, rumor-sensitive, or needs claim-by-claim tracking.
Read `references/multimodal-capture.md` when screenshots, images, videos, gifs, subtitles, or audio cues materially affect the answer.
Read `references/public-web-recovery.md` when the first page is partial, blocked, snippet-only, or clearly weaker than the underlying media/discussion.
Use `scripts/claim_log_tools.py` to initialize, normalize, or summarize a structured claim log when you have enough evidence items that manual tracking will become noisy.

### Post / comment / screenshot / image / video / gif / audio analysis

Stay explicit about what is and is not directly observable from public-web access.

Break analysis into layers:
1. **Surface metadata** — visible title, caption, date, platform text, source URL.
2. **Observed media evidence** — visible text, OCR-able text, subtitles, scene details, sequence, speaker labels, or audio/transcript clues.
3. **Content summary** — what is clearly shown, spoken, or claimed.
4. **Reaction summary** — visible comment themes, sentiment split, repeated jokes, skepticism, support.
5. **Credibility check** — firsthand evidence vs repost vs edit-heavy clip vs rumor relay.
6. **Open questions** — what would require login, in-app rendering, browser automation, direct file access, frame extraction, OCR cleanup, or ASR.

If the user provides screenshots, transcripts, fetched page text, or media files, analyze those directly and keep extraction separate from interpretation.

### Claim-first working pattern

When the topic is messy, do not jump straight from search results to a vibe summary.

Use this loop instead:
1. list the 2-6 decision-relevant claims
2. attach evidence items with explicit modality and access level
3. downgrade anything that remains snippet-only or relay-only
4. summarize only after the strongest claim/evidence pairs are visible

Good trigger conditions for a claim log:
- rumor-heavy controversies
- screenshot-led accusations
- policy interpretation disputes
- local recommendation tasks with sharply conflicting chatter
- any answer where you need to explain why one repeated claim is still weak

## 5) Verify before concluding

Read `references/verification-patterns.md` when the task involves rumors, policy changes, business legitimacy, or claims that could materially affect a decision.

Default verification moves:
- find the earliest visible source, not just the loudest repost
- separate claim, response, and confirmed consequence
- check whether the page is firsthand, quoted, scraped, or relayed
- look for official names, dates, location details, and implementation language
- for local businesses, compare RedNote chatter with maps/review data or official menu/hours pages
- for policy topics, prioritize primary notices over interpretation posts
- for gossip, keep anonymous screenshots and clipped media at rumor level unless independently corroborated
- for screenshots, note whether key text is fully visible, cropped, or OCR-uncertain
- for videos, distinguish caption-level evidence from frame-level evidence
- for audio claims, distinguish direct transcript, ASR-derived wording, and second-hand paraphrase

## 6) Score credibility and decision risk

Read `references/scoring-rubric.md` when you need the full rubric.

Use at least two separate judgments:

### Credibility score (0-5)
- 5: official documents, regulator notices, court/government records, direct statements, reputable reporting
- 4: detailed firsthand post or review with dates, screenshots, prices, names, or concrete specifics
- 3: specific but weakly corroborated anecdote or snippet
- 2: vague anecdote, repost, engagement bait, or SEO page
- 1: obvious rumor or unsourced assertion
- 0: cannot inspect or verify

### Risk / caution / recommendation score (0-5)
Interpret the second score according to task type:
- education / reputation / policy / gossip: higher means more caution or downside risk
- local recommendation: higher can mean stronger recommendation confidence only if you label it explicitly; otherwise keep it as caution risk to avoid ambiguity

Weight repeated, independent, recent, and specific evidence more heavily than loud but vague posts.

## 7) Deliver the report

Keep the report concise and decision-oriented.

Choose the smallest fitting format:

### A) Quick snapshot
- Subject:
- Category:
- Time scope:
- Overall signal: positive / mixed / caution / high risk / inconclusive
- Confidence: low / medium / high

### B) Findings
- 3-6 bullets, strongest evidence first

### C) Evidence list
Use compact bullets when tables are awkward:
- `[credibility 4 | score 4 | first-hand | 2025-09] refund complaints repeat across multiple posts — <url>`

### D) Discussion clusters
- cluster name
- representative wording pattern
- approximate repetition count
- confidence note

### E) What remains unverified
- missing items that public-web access cannot confirm

### F) Suggested next checks
- official notice or registration lookup
- a more recent search window
- map/review cross-check for local places
- direct in-app or browser review if the user wants deeper comment or media extraction

## Fast paths

### Quick reputation check
1. Build a mixed `overview` + `review` + `verification` query set.
2. Search 6-12 strong queries.
3. Capture 5-10 sources.
4. Score each source.
5. Return a short summary plus caveats.

### Latest update or policy scan
1. Use `latest` + `trending` + `verification`.
2. Bias toward the last 7-30 days.
3. Separate official update from community interpretation.
4. State whether the trend is confirmed, contested, or still rumor-level.

### Local recommendation scan
1. Use category `local`.
2. Mix review, recommendation, complaint, and verification queries.
3. Cluster themes: taste, price, queue, service, environment, location convenience.
4. Return a shortlist plus tradeoffs, not just one winner.

### Comment or post analysis
1. Collect visible text, screenshots, snippets, or transcript first.
2. Cluster reactions into 3-5 themes.
3. Mark what is directly seen vs inferred.
4. State clearly when deeper extraction would require login, browser automation, or direct media processing.
5. If the user wants deeper comment-level coverage, offer login-enhanced mode as an explicit escalation path.
6. If the user declines login, ask for screenshots or copied comment text instead of pretending the full thread was inspected.

### Account summary or recent-post scan
1. Start with public-web mode and gather any inspectable profile URL, note URLs, snippets, mirrors, or search-engine traces.
2. Read `references/account-summary-template.md` for output structure.
3. If the goal is a broad impression only, summarize from public-web evidence with caveats.
4. If the goal is recent-post completeness, tell the user public-web coverage may be partial and offer login-enhanced browser review.
5. If the user chooses login-enhanced mode, read `references/login-enhanced-workflow.md` and follow the controlled authenticated-review path.
6. If the user does not want login, read `references/minimal-user-input-paths.md` and ask for a few seed links, screenshots, or copied note titles to improve coverage.
7. Distinguish clearly between account-level observations, note-level evidence, and anything missing because of access limits.

### Screenshot / image-led analysis
1. Capture the page context plus image-visible text, prices, dates, names, and watermarks.
2. Note image legibility and likely OCR uncertainty.
3. Separate image-contained claims from caption-contained claims.
4. If the page itself is weak, pivot on the strongest visible fragment with `scripts/recovery_query_builder.py`.
5. Log the strongest inspectable claim(s) before summarizing.

### Video / subtitle / gif-led analysis
1. Capture caption, visible duration, upload date, and any subtitle/on-screen text.
2. Distinguish clip content from commentary about the clip.
3. If you only have snippet-level access, keep conclusions provisional and pivot on distinctive subtitle fragments or overlays with `scripts/recovery_query_builder.py`.
4. Say whether frames or the original file would materially improve confidence.

### Audio / transcript-led analysis
1. Identify whether you have direct audio, subtitles, ASR text, or only quoted paraphrases.
2. Treat transcript quality as part of the evidence rating.
3. Avoid overreading tone, sarcasm, or exact wording without direct audio access.
4. If the only foothold is a quoted line, subtitle fragment, or repost caption, use `scripts/recovery_query_builder.py` to search for the earliest visible source or mirrors.
5. Log the spoken claim separately from reactions to it.

## Reliability caveats

- Search indexing can lag behind live app discussion.
- Viral repetition does not equal verification.
- Snippets can omit qualifiers or updates visible only on the landing page.
- Local quality and policy enforcement can change quickly; recency matters.
- Platform anti-bot controls can make no-login account research much thinner than in-app browsing.
- If evidence stays thin after cross-checking, say `inconclusive` rather than stretching.

## Recommended product posture

Treat this skill as a dual-mode RedNote research tool:
- **public-web mode** for broad research, weak-clue recovery, and no-login investigations
- **login-enhanced mode** for fuller account, recent-post, and comment review when the user explicitly opts in

When neither mode is enough on its own, use a hybrid path:
- public-web evidence + a few user-provided links/screenshots
