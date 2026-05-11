# Changelog

## v3.15.0 — 2026-03-15

### Added
- **GetXAPI backend** for Twitter/X — new third-party API option with Bearer auth
  - Auto-select priority: getxapi > twitterapiio > official
  - New env var: `GETX_API_KEY`
  - Multi-format date parsing (Twitter, ISO 8601, simple datetime)
  - Page 2 retry logic for pagination
  - API key format validation
- Cross-topic deduplication — each article now appears in only ONE topic
  (highest priority wins: llm > ai_agent > crypto > github > trending)
- New test: `test_cross_topic_deduplication`

### Fixed
- **RSS cache thread safety** — added `threading.RLock()` and `global` declarations
  - Fixes `UnboundLocalError` on Python 3.13+ (#7)
  - Fixes potential deadlock from nested lock acquisition
- Title similarity threshold lowered (0.85 → 0.75) to catch more near-duplicates
- Previous digest penalty window extended (7 → 14 days)

### Changed
- Environment variables documentation reorganized with clear sections
  (Twitter, Web Search, GitHub, Other)
- Removed subjective pricing/recommendation comments from env var docs
- `run-pipeline.py` docstring updated: 5 steps → 6 steps

### Docs
- Added Dependencies section to README (core + optional)
- README_CN synced with English README
- Moved Dependencies section after Environment Variables

## v3.14.0 — 2026-03-02

### Changed
- `BLOG_PICKS_COUNT` restored as configurable placeholder (default 3, weekly 3-5)
- SKILL.md aligned with v3.13.0 features: 6-source pipeline, 151 sources, enrich/trending docs
- Cron examples updated with ENRICH and BLOG_PICKS_COUNT placeholders

## v3.13.0 — 2026-03-01

### Added
- `enrich-articles.py` — full-text enrichment for high-scoring articles
  - Cloudflare Markdown for Agents (Accept: text/markdown) preferred
  - HTML readability extraction fallback
  - Skip list for paywalled/social/video domains
  - Blog domain whitelist with lower score threshold (>=3)
  - Parallel fetching (5 workers, 10s timeout)
- Pipeline `--enrich` flag to enable enrichment after merge (default off)
- `<ENRICH>` placeholder in digest-prompt for cron control
- Blog Picks section in digest (3-5 indie blog articles with summaries)
- 13 HN top tech blogs added to RSS sources (49->62 feeds, 151 total)
- Featured In section in README

### Changed
- Digest template: 3-5 items daily, 10-15 weekly per section
- Digest template: min quality_score >= 5 for topic sections
- Digest template: GitHub Releases + Trending at bottom, no score prefix
- Digest template: all English (output language controlled by placeholder)
- Trending: top 5 + any with daily_stars_est > 50
- No dedup between GitHub Releases and Trending sections

### Fixed
- `skip_set` -> `skip_steps` variable name bug in run-pipeline.py
- Blog Picks section made mandatory even without enrichment

### Removed
- Community Buzz section from digest template

## v3.12.0

- **GitHub Trending**: Fetch daily trending repos via GitHub Search API (4 topics, sorted by stars)
- **Trending display**: Shows ⭐ total stars, +N/day growth estimate, language, description
- **Quality scoring**: Trending repos scored by daily star growth (base 5 + growth/10, max 15)
- **Pipeline integration**: `run-pipeline.py` runs trending as a 6th parallel step
- **Merge integration**: Trending repos deduplicated and grouped by topic alongside other sources
- **Tavily backend**: Dual web search backend (Tavily/Brave) with auto-detection
- **Templates updated**: Discord/digest templates show trending count in stats footer

## v3.11.0

- **Tavily Search backend**: Alternative to Brave Search via `TAVILY_API_KEY` + `WEB_SEARCH_BACKEND` env
- **Quality scores in output**: 🔥 score prefix on every article, strict descending order per topic
- **Domain limit fix**: Exempt x.com/github.com/reddit.com from per-topic domain limits (#1)
- **Brave multi-key**: `BRAVE_API_KEYS` for comma-separated key rotation
- **Config naming**: User overlay files renamed to `tech-news-digest-sources.json` / `tech-news-digest-topics.json`
- **Tests**: 41 unit + integration tests with real fixture data, GitHub Actions CI (Python 3.9 + 3.12)
- **Docs**: Full env var alignment, Network Access/Shell Safety updates, README badges, CN sync

## v3.10.3

- **Docs**: Align API Keys & Environment with all 10 actual env vars
- **Docs**: Update Network Access (add Reddit) and Shell Safety (send-email.py + generate-pdf.py)
- **Refactor**: Rename user overlay configs to `tech-news-digest-sources.json` / `tech-news-digest-topics.json` to avoid naming conflicts

## v3.10.2

- **Fix domain limits**: Exempt multi-author platforms (x.com, github.com, reddit.com) from per-topic domain limits — previously 77 tweets were cut to 12 (#1)
- **Brave multi-key**: Prefer `BRAVE_API_KEYS` (comma-separated) over `BRAVE_API_KEY` for key rotation in `fetch-web.py`

## v3.10.1

- **Fix email MIME**: New `send-email.py` — proper multipart MIME construction for HTML body + PDF attachment (replaces broken `mail -a -A` approach)
- **Docs alignment**: README + SKILL.md updated to v3.10 (source counts, PDF, all scripts documented)

## v3.10.0

- **PDF generation**: New `generate-pdf.py` script — converts markdown digest to styled A4 PDF with Chinese typography (Noto Sans CJK SC), emoji icons, page headers/footers, blue accent theme. Requires `weasyprint`.
- **PDF template**: `references/templates/pdf.md` with usage docs and examples

## v3.9.1

- Remove unused markdown and telegram templates
- Add `sanitize-html.py` for safe markdown→HTML email conversion (XSS-safe, inline CSS)

## v3.9.0

- **URL-based dedup**: merge-sources now deduplicates by normalized URL (domain+path) before title similarity, catching cross-source duplicates
- **Brave rate limit caching**: `detect_brave_rate_limit()` results cached for 24h; supports `BRAVE_PLAN=free|pro` env override
- **source-health**: Now tracks Reddit (`--reddit`) and Web (`--web`) sources; flexible key detection
- **run-pipeline**: `--skip` (comma-separated step names) and `--reuse-dir` (reuse intermediate outputs) for partial reruns

## v3.8.1

- **merge-sources**: Fix `getattr` → direct `args.reddit`; domain limit stats now accurate; SequenceMatcher early-exit for >30% length diff
- **merge-sources**: RSS priority sources get +2 extra score bonus (prevent drowning by low-engagement tweets)
- **run-pipeline**: Add `--twitter-backend` parameter (transparent passthrough); clean up tmp dir after success
- **fetch-rss**: Warn when feedparser not installed (basic regex parser fallback)
- **config_loader**: Validate required fields (id, type, enabled) on source load, skip invalid with warning

## v3.8.0

- **twitterapiio pagination**: Fetches up to 2 pages (40 tweets) for high-volume users; logs truncation warning
- **Unified tweet limit**: `MAX_TWEETS_PER_USER` 10→20 for official backend (matches twitterapiio)
- **Shared result helpers**: `_make_result()` / `_make_error()` on base class, reduces duplication
- **Smarter rate limiting**: `RateLimiter` class with `threading.Lock` for twitterapiio (5 QPS); replaces per-thread sleep
- **Retry improvements**: `RETRY_COUNT` 1→2 (3 attempts); twitterapiio 429 wait 60s→5s
- **Tweet text limit**: 200→280 chars (matches Twitter's actual limit)
- **Empty result format**: Now matches normal output structure for consistent downstream parsing
- **Removed redundant isReply filter** in twitterapiio (API already excludes replies)

## v3.7.1

- **twitterapi.io bugfix**: Fix response envelope parsing (`data.tweets` not top-level `tweets`)
- **twitterapi.io concurrency**: 3-worker parallel fetch with progress logs showing tweet counts and top likes
- **test-pipeline.sh revamp**: `--only`, `--skip`, `--topics`, `--ids`, `--twitter-backend` filtering; per-step timing; detailed `--help`

## v3.7.0

- **twitterapi.io backend**: Alternative Twitter data source via `TWITTERAPI_IO_KEY` — no username→ID resolution needed, simpler API, same normalized output format
- **Backend auto-detection**: `TWITTER_API_BACKEND=auto` (default) uses twitterapi.io if key is set, else falls back to official X API v2
- **`--backend` CLI arg**: Override env var per invocation (`official`, `twitterapiio`, `auto`)
- **Backend abstraction**: `fetch-twitter.py` refactored with `TwitterBackend` base class and two implementations (`OfficialBackend`, `TwitterApiIoBackend`)

## v3.6.3

- Add GitHub source: zeroclaw-labs/zeroclaw (137→138 total, 27→28 GitHub)

## v3.6.2

- Add 3 GitHub sources: cloudflare/moltworker, sipeed/picoclaw, HKUDS/nanobot (134→137 total, 24→27 GitHub)

## v3.6.1

- Prompt review & optimization pass (no functional changes)

## v3.6.0

- Simplify digest-prompt: 232→122 lines (-47%), remove fallback scripts block, merge redundant rules
- Add optional `<EMAIL_FROM>` placeholder for sender display name
- Add "Environment vs Code" separation rule to CONTRIBUTING.md

## v3.5.1

- Email delivery: prefer `mail` (msmtp) over `gog`, remove redundant fallback options
- Require email content to match Discord (no abbreviation or skipped sections)
- Add CONTRIBUTING.md with development conventions

## v3.5.0

- **Unified source count**: 134 sources (49 RSS + 48 Twitter + 24 GitHub + 13 Reddit)
- Updated README source counts and sub-totals

## v3.4.9

- Declare `openssl` as optional binary in SKILL.md (used for GitHub App JWT signing)

## v3.4.8

- **New `summarize-merged.py` helper**: Outputs structured human-readable summary of merged data, sorted by quality score with metrics/sources
- **Prevent ad-hoc JSON parsing**: `digest-prompt.md` now instructs agents to use `summarize-merged.py` instead of writing inline Python (which often failed with `AttributeError` on nested structures)

## v3.4.7

- **Inline GitHub App JWT signing**: Remove `GH_APP_TOKEN_SCRIPT` env var entirely. Token generation now built into `fetch-github.py` using `openssl` CLI for RS256 signing — no external scripts executed, no arbitrary code execution risk.
- Only 3 env vars needed: `GH_APP_ID`, `GH_APP_INSTALL_ID`, `GH_APP_KEY_FILE`
- Remove unused imports, fix bare excepts across all scripts

## v3.4.6

- Add `reddit` to config/schema.json source type enum (was missing, caused validation mismatch)
- Rename all archive paths `tech-digest/` → `tech-news-digest/` for consistency
- Fix Discord template: default delivery is channel (via DISCORD_CHANNEL_ID), not DM
- GH_APP_TOKEN_SCRIPT: add trust warning in code and env var description
- Path placeholders: SKILL.md uses `<workspace>/` consistently with digest-prompt.md

## v3.4.5

- Fix source count inconsistencies across docs (131/132 → 133: 49 RSS + 49 Twitter + 22 GitHub + 13 Reddit)
- Rename legacy `tech-digest` references to `tech-news-digest` in comments, descriptions, and cache file paths

## v3.4.4

- Remove hardcoded Discord channel ID from SKILL.md (use `<your-discord-channel-id>` placeholder)
- Cron prompt examples: Chinese → English, default LANGUAGE = English
- Remove outdated "Migration from v1.x" section

## v3.4.3

- **Audit compliance**: Address all ClawHub Code Insights findings:
  - Declare `gh` as optional binary in SKILL.md metadata
  - Document credential access cascade and file access scope in security section
  - Add "Dependency Installation" section clarifying skill never runs `pip install`
  - Explicitly state scripts do not read `~/.config/`, `~/.ssh/`, or arbitrary credential files

## v3.4.2

- **Remove hardcoded GitHub App credentials**: App ID, install ID, key file path, and token script path now read exclusively from env vars (`GH_APP_ID`, `GH_APP_INSTALL_ID`, `GH_APP_KEY_FILE`, `GH_APP_TOKEN_SCRIPT`). No defaults — if not set, this auth method is silently skipped.
- **Declare new env vars in SKILL.md**: All 4 GitHub App env vars declared in metadata
- **Fix security docs**: Updated Shell Execution section to accurately describe `subprocess.run()` usage in `run-pipeline.py` and `fetch-github.py`

## v3.4.1

- **KOL Display Names**: KOL Updates section now shows "Sam Altman (@sama)" instead of bare "@sama" across all templates (Discord, Email, Telegram)
- **`display_name` in Merged JSON**: `merge-sources.py` propagates Twitter source `name` to article-level `display_name` field, eliminating need to re-read raw Twitter data
- **New Twitter Sources**: Added @OpenClawAI (official) and @steipete (Peter Steinberger), total 49 Twitter KOLs / 133 sources
- **Enforce Unified Pipeline**: `digest-prompt.md` now says "You MUST use" `run-pipeline.py`, individual steps demoted to `<details>` fallback with `--force` flags

## v3.4.0

- **Unified Pipeline**: New `run-pipeline.py` runs all 5 fetch steps (RSS, Twitter, GitHub, Reddit, Web) in parallel, then merges — total ~30s vs ~3-4min sequential. Digest prompt updated to use this by default.
- **Reddit Parallel Fetch**: `fetch-reddit.py` now uses `ThreadPoolExecutor(max_workers=4)` instead of sequential requests with `sleep(1)`
- **Reddit 403 Fix**: Added explicit `ssl.create_default_context()` and `Accept-Language` header to fix Reddit blocking Python's default `urllib` TLS fingerprint
- **Brave API Auto-Concurrency**: `fetch-web.py` probes `x-ratelimit-limit` header at startup — paid plans auto-switch to parallel queries, free plans stay sequential
- **GitHub Auto-Auth**: `fetch-github.py` resolves tokens in priority order: `$GITHUB_TOKEN` → GitHub App auto-generate → `gh` CLI → unauthenticated. No manual token setup needed if GitHub App credentials exist.
- **Timeout Increase**: All fetch scripts 15s → 30s per HTTP request; pipeline per-step subprocess 120s → 180s
- **Pipeline Metadata**: `run-pipeline.py` saves `*.meta.json` with per-step timing, counts, and status

## v3.3.2

- **Declare tools and file access**: Added `tools` (python3 required, gog optional) and `files` (read/write paths) to SKILL.md metadata, addressing VirusTotal "undeclared tools/binaries" and "modify workspace files" audit findings
- **Added `metadata.openclaw.requires`**: Declares `python3` binary dependency

## v3.3.1

- **Remove anthropic-rss mirror**: Removed third-party community RSS mirror (`anthropic-rss`) to eliminate supply chain risk flagged by VirusTotal Code Insights. Anthropic coverage remains via Twitter KOL, GitHub releases, and Reddit sources.
- **Remove Third-Party RSS Sources section** from SKILL.md security docs (no longer applicable)

## v3.3.0

- **RSS Domain Validation**: New `expected_domains` field in sources.json rejects articles from unexpected origins (applied to anthropic-rss mirror)
- **Email Shell Safety**: HTML body written to temp file before CLI delivery; subjects restricted to static format strings
- **Discord Embed Suppression**: Footer links wrapped in `<>` to prevent preview embeds

## v3.2.1

- **Mandatory Reddit Execution**: Agent explicitly required to run `fetch-reddit.py` script — cannot skip or generate fake output

## v3.2.0

- **Unified English Templates**: All prompt instructions, section titles, stats footer, and example content standardized to English. Output language controlled by `<LANGUAGE>` placeholder at runtime.

## v3.1.0

- **Executive Summary**: 2-4 sentence overview of top stories at the beginning of each digest
- **Community Buzz Section**: Merged Twitter/X Trending and Reddit Hot Discussions into unified 🔥 社区热议
- **Reddit in Topic Sections**: Reddit posts now selected by quality_score alongside other sources
- **Digest Footer Branding**: Shows skill version and OpenClaw link
- **Prompt Fix**: Agent explicitly instructed to read Reddit data from merged JSON

## v3.0.0

- **Reddit Data Source**: New `fetch-reddit.py` script — 5th data layer using Reddit's public JSON API (no auth required). 13 subreddits: r/MachineLearning, r/LocalLLaMA, r/CryptoCurrency, r/artificial, r/ethereum, r/ChatGPT, r/singularity, r/OpenAI, r/Bitcoin, r/programming, r/Anthropic, r/defi, r/ExperiencedDevs
- **Reddit Score Bonus**: Posts with score > 500 get +5, > 200 get +3, > 100 get +1 in quality scoring
- **10 New Non-Reddit Sources**: Ben's Bites, The Decoder, a16z Crypto, Bankless (RSS); @ClementDelangue, @GregBrockman, @zuck (Twitter); MCP Servers, DeepSeek-V3, Meta Llama (GitHub)
- **Tweet Engagement Metrics**: KOL entries display `👁|💬|🔁|❤️` stats in inline code blocks across all templates
- **Date Timezone Fix**: Report date explicitly provided via `<DATE>` placeholder, preventing UTC/local mismatch
- **Mandatory Links**: KOL Updates and Twitter/X Trending sections require source URLs for every entry
- **Graceful Twitter Degradation**: Missing `X_BEARER_TOKEN` outputs empty JSON instead of failing
- **URL Sanitization**: `resolve_link()` rejects non-HTTP(S) schemes
- **Security Documentation**: Added Security Considerations section to SKILL.md
- **Total Sources**: 132 (50 RSS + 47 Twitter + 22 GitHub + 13 Reddit + 4 web search topics)

## v2.8.1

- **Metrics Data Fix**: Agent now required to read actual `metrics` values from Twitter JSON data instead of defaulting to 0
- **Email Template Enhancement**: Added KOL metrics and Twitter/X Trending section to email template

## v2.8.0

- **Tweet Metrics Display**: KOL entries show `👁|💬|🔁|❤️` engagement stats wrapped in inline code to prevent emoji enlargement on Discord
- **Standardized Metrics Format**: Fixed 4-metric order, show 0 for missing values, one tweet per bullet with own URL
- **10 New Sources (119 total)**: Ben's Bites, The Decoder, a16z Crypto, Bankless (RSS); @ClementDelangue, @GregBrockman, @zuck (Twitter); MCP Servers, DeepSeek-V3, Meta Llama (GitHub)

## v2.7.0

- **Tweet Engagement Metrics**: KOL Updates now display 👁 views, 💬 replies, 🔁 retweets, ❤️ likes from Twitter public_metrics across all templates (Discord, Email, Telegram)

## v2.6.1

- **Graceful Twitter Degradation**: Missing `X_BEARER_TOKEN` now outputs empty JSON and exits 0 instead of failing with exit code 1, allowing the pipeline to continue without Twitter data

## v2.6.0

- **Date Timezone Fix**: Added `<DATE>` placeholder to digest prompt — report date now explicitly provided by caller, preventing UTC/local timezone mismatch
- **Mandatory Links in KOL/Trending**: KOL Updates and Twitter/X Trending sections now require source URLs for every entry (no link-free entries allowed)
- **URL Sanitization**: `resolve_link()` in fetch-rss.py rejects non-HTTP(S) schemes (javascript:, data:, etc.)
- **Third-Party Source Annotation**: Community-maintained RSS mirrors (e.g. anthropic-rss) are annotated with notes in sources.json
- **Security Documentation**: Added Security Considerations section to SKILL.md covering shell execution model, input sanitization, and network access

## v2.5.0

- **Twitter Reply Filter Fix**: Use `referenced_tweets` field instead of text prefix to distinguish replies from mentions
- **Scoring Consistency**: digest-prompt.md now matches code (`PENALTY_OLD_REPORT = -5`)
- **Template Version Cleanup**: Removed hardcoded version numbers from email/markdown/telegram templates
- **Article Count Fix**: `merge-sources.py` uses deduplicated count instead of inflated topic-grouped sum
- **Pipeline Resume Support**: All fetch scripts support `--force` flag; skip if cached output < 1 hour old
- **Source Health Monitoring**: New `scripts/source-health.py` tracks per-source success/failure history
- **End-to-End Test**: New `scripts/test-pipeline.sh` smoke test for the full pipeline
- **Archive Auto-Cleanup**: digest-prompt.md documents 90-day archive retention policy
- **Twitter Rate Limiting**: Moved sleep into `fetch_user_tweets` for actual per-request rate limiting
- **Web Article Scoring**: Web articles now use `calculate_base_score` instead of hardcoded 1.0
- **Dead Code Removal**: Removed unused `load_sources_with_overlay` / `load_topics_with_overlay` wrappers

## v2.4.0

- **Batch Twitter Lookup**: Single API call for all username→ID resolution + 7-day local cache (~88→~45 API calls)
- **Smart Dedup**: Token-based bucketing replaces O(n²) SequenceMatcher — only compares articles sharing 2+ key tokens
- **Conditional Fetch (RSS)**: ETag/Last-Modified caching, 304 responses skip parsing
- **Conditional Fetch (GitHub)**: Same caching pattern + prominent warning when GITHUB_TOKEN is unset
- **`--no-cache` flag**: All fetch scripts support bypassing cache

## v2.3.0

- **GitHub Releases**: 19 tracked repositories as a fourth data source
- **Data Source Stats Footer**: Pipeline statistics in all templates
- **Twitter Queries**: Added to all 4 topics for better coverage
- **Simplified Cron Prompts**: Reference digest-prompt.md with parameters only

## v2.1.0

- **Unified Source Model**: Single `sources.json` for RSS, Twitter, and web sources
- **Enhanced Topics**: Richer topic definitions with search queries and filters
- **Pipeline Scripts**: Modular fetch → merge → template workflow
- **Quality Scoring**: Multi-source detection, deduplication, priority weighting
- **Multiple Templates**: Discord, email, and markdown output formats
- **Configuration Validation**: JSON schema validation and consistency checks
- **User Customization**: Workspace config overrides for personalization
