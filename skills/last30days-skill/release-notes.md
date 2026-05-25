The AI world reinvents itself every month. This skill keeps you current.

`/last30days` researches your topic across **Reddit, X, YouTube, and the web** from the last 30 days, finds what the community is actually upvoting, sharing, and saying on camera, and writes you a prompt that works today, not six months ago.

## Three Headline Features

**1. Open-class skill with watchlists.** Add any topic to a watchlist -- your competitors, specific people, emerging technologies -- and /last30days re-researches it on demand or via cron. Designed for always-on environments like [Open Claw](https://github.com/openclaw/openclaw). SQLite-backed with FTS5 full-text search.

**2. YouTube transcripts as a 4th source.** When yt-dlp is installed, /last30days automatically searches YouTube, grabs view counts, and extracts auto-generated transcripts from the top videos. A 20-minute review contains 10x the signal of a single post -- now the skill reads it. Inspired by [@steipete](https://x.com/steipete)'s yt-dlp + [summarize](https://github.com/steipete/summarize) toolchain.

**3. Works in OpenAI Codex CLI.** Same skill, same engine, same four sources. Install to `~/.agents/skills/last30days` and invoke with `$last30days`.

Plus: **Bundled X search** -- vendored Bird GraphQL client (MIT). No external CLI, no npm install, no API keys needed. Just Node.js 22+ and your browser cookies.

## Real Results (verified Feb 15)

| Topic | Reddit | X | YouTube | Web |
|-------|--------|---|---------|-----|
| Nano Banana Pro | -- | 32 posts, 164 likes | 5 videos, 98K views, 5 transcripts | 10 pages |
| Seedance 2.0 access | 3 threads, 114 upvotes | 31 posts, 191 likes | 20 videos, 685K views, 4 transcripts | 10 pages |
| OpenClaw use cases | 35 threads, 1,130 upvotes | 23 posts | 20 videos, 1.57M views, 5 transcripts | 10 pages |
| YouTube thumbnails | 7 threads, 654 upvotes | 32 posts, 110 likes | 18 videos, 6.15M views, 5 transcripts | 30 pages |
| AI generated ads | 12 threads | 29 posts, 101 likes | 3 videos, 83K views, 3 transcripts | 30 pages |

## What's New

### Added
- Open-class skill with watchlist, briefing, and history modes
- YouTube search + transcript extraction via yt-dlp
- OpenAI Codex CLI compatibility
- Bundled Twitter/X search (vendored Bird GraphQL, MIT)
- Native web search backends (Parallel AI, Brave, OpenRouter/Perplexity Sonar Pro)
- `--diagnose` flag for source status checking
- `--store` flag for SQLite accumulation
- Conversational first-run experience (NUX)

### Changed
- Two-phase search architecture (entity-aware drill-down)
- Reddit JSON enrichment for real engagement metrics
- Smarter query construction with auto-retry on 0 results
- Engagement-weighted scoring (relevance 45%, recency 25%, engagement 30%)
- `--days=N` configurable lookback (thanks @jonthebeef)

### Fixed
- YouTube/Reddit timeout resilience
- Reddit 429 rate limit fail-fast
- Eager import crash in Codex environments
- X search returning 0 results on popular topics
- Windows Unicode crash (thanks @JosephOIbrahim)

## New Contributors

- @JosephOIbrahim -- Windows Unicode fix ([#17](https://github.com/mvanhorn/last30days-skill/pull/17))
- @levineam -- Model fallback for unverified orgs ([#16](https://github.com/mvanhorn/last30days-skill/pull/16))
- @jonthebeef -- `--days=N` configurable lookback ([#18](https://github.com/mvanhorn/last30days-skill/pull/18))

## Credits

- [@steipete](https://github.com/steipete) -- Bird CLI (vendored X search) and yt-dlp/summarize inspiration for YouTube transcripts
- [@galligan](https://github.com/galligan) -- Marketplace plugin inspiration
- [@hutchins](https://x.com/hutchins) -- Pushed for YouTube feature

## Install

```bash
# Claude Code
git clone https://github.com/mvanhorn/last30days-skill.git ~/.claude/skills/last30days

# Codex CLI
git clone https://github.com/mvanhorn/last30days-skill.git ~/.agents/skills/last30days
```

30 days of research. 30 seconds of work. Four sources. Zero stale prompts.
