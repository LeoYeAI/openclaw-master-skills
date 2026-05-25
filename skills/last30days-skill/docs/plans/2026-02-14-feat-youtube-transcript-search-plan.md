---
title: "feat: Add YouTube transcript search as 4th source"
type: feat
date: 2026-02-14
---

# feat: Add YouTube Transcript Search

## Overview

Add YouTube as a 4th research source alongside Reddit, X, and Web. Search for recent videos on the user's topic, fetch transcripts from the top results, and feed the transcript text into the synthesis — giving the Judge Agent access to what people are *saying* in video form, not just what they're posting on social media.

**Why this matters:** For many topics (tutorials, product reviews, drama breakdowns), the best content lives on YouTube, not Reddit or X. A 20-minute video review contains 10x the signal of a tweet. The skill currently misses all of it.

## Proposed Solution

Use **yt-dlp** (already installed via Homebrew) for both YouTube search and transcript extraction. No new API keys, no new dependencies. Follows the same "zero friction" philosophy as vendored Bird search.

### Two-step process per research run:

1. **Search**: `yt-dlp "ytsearch{N}:{topic}" --dateafter {30d_ago} --flat-playlist --print` → top videos by view count
2. **Transcripts**: For top 5 videos, extract auto-generated subtitles via `yt-dlp --write-auto-subs --skip-download`, clean VTT to plaintext in Python

### Why NOT use `summarize` CLI:

- Adds 146MB brew dependency (arm64-only binary)
- Calls OpenAI API per video ($0.01-0.03 each) — adds cost on top of existing API usage
- yt-dlp already extracts raw transcripts for free (covers ~95% of videos with auto-captions)
- Raw transcripts are better for synthesis anyway — the LLM doing synthesis (Claude) should interpret the content itself, not get a pre-summarized version

`summarize` is a great standalone tool, but for integration into a research pipeline where an LLM already synthesizes everything, raw transcripts are the right input.

## Technical Approach

### Architecture

New file: `scripts/lib/youtube_yt.py` (mirrors `bird_x.py` pattern)

```
yt-dlp search → metadata (title, views, channel, date)
     ↓
  sort by views, take top N
     ↓
yt-dlp subtitle extraction → raw VTT files
     ↓
  VTT cleanup → plaintext transcripts
     ↓
  truncate to ~500 words per video
     ↓
  normalize → YouTubeItem objects
     ↓
  score, dedupe, render (same pipeline as Reddit/X)
```

### Implementation Phases

#### Phase 1: Search + Metadata (the fast part)

**New file: `scripts/lib/youtube_yt.py`**

Core search function:
```python
def search_youtube(topic: str, from_date: str, to_date: str, depth: str = "default") -> Dict[str, Any]:
    """Search YouTube via yt-dlp. No API key needed.

    Returns:
        Dict with 'items' list of video metadata dicts.
    """
    count = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    date_filter = from_date.replace("-", "")  # YYYYMMDD format

    # yt-dlp search with metadata extraction
    cmd = [
        "yt-dlp",
        f"ytsearch{count}:{topic}",
        "--dateafter", date_filter,
        "--flat-playlist",
        "--print", "%(view_count)s\t%(id)s\t%(title)s\t%(channel)s\t%(upload_date)s\t%(like_count)s\t%(comment_count)s",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    # Parse tab-separated output, sort by views, return top N
    ...
```

Depth config (matches existing pattern):
```python
DEPTH_CONFIG = {
    "quick": 10,     # search 10, transcript top 3
    "default": 20,   # search 20, transcript top 5
    "deep": 40,      # search 40, transcript top 8
}

TRANSCRIPT_LIMITS = {
    "quick": 3,
    "default": 5,
    "deep": 8,
}
```

**Key detail**: `yt-dlp --flat-playlist` returns exit code 0 with empty stdout when `--dateafter` filters out everything. Check for empty output, not error codes.

#### Phase 2: Transcript Extraction (the slow part)

For top N videos (by view count), fetch transcripts:

```python
def fetch_transcript(video_id: str, temp_dir: str) -> Optional[str]:
    """Fetch auto-generated transcript for a YouTube video.

    Returns:
        Plaintext transcript string, or None if no captions available.
    """
    cmd = [
        "yt-dlp",
        "--write-auto-subs",
        "--sub-lang", "en",
        "--sub-format", "vtt",
        "--skip-download",
        "-o", f"{temp_dir}/%(id)s",
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    vtt_path = Path(temp_dir) / f"{video_id}.en.vtt"
    if not vtt_path.exists():
        return None

    return _clean_vtt(vtt_path.read_text())
```

VTT cleanup (~10 lines of Python):
```python
def _clean_vtt(vtt_text: str) -> str:
    """Convert VTT subtitle format to clean plaintext."""
    text = re.sub(r'^WEBVTT.*?\n\n', '', vtt_text, flags=re.DOTALL)
    text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*\n', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    lines = text.strip().split('\n')
    seen = set()
    unique = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped not in seen:
            seen.add(stripped)
            unique.append(stripped)
    return re.sub(r'\s+', ' ', ' '.join(unique)).strip()
```

**Parallelization**: Run transcript fetches in parallel using ThreadPoolExecutor (same pattern as Phase 2 supplemental searches for Reddit/X):

```python
def fetch_transcripts_parallel(video_ids: List[str], max_workers: int = 5) -> Dict[str, Optional[str]]:
    """Fetch transcripts for multiple videos in parallel."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(fetch_transcript, vid, temp_dir): vid
                for vid in video_ids
            }
            results = {}
            for future in as_completed(futures):
                vid = futures[future]
                results[vid] = future.result()
    return results
```

#### Phase 3: Integration into Pipeline

**Update `scripts/lib/schema.py`** — add YouTubeItem:
```python
@dataclass
class YouTubeItem:
    id: str                    # video_id
    title: str
    url: str
    channel_name: str
    date: Optional[str]
    date_confidence: str       # always "high" for YouTube
    engagement: Engagement     # views, likes, comments
    transcript_snippet: str    # first ~500 words of transcript
    relevance: float
    why_relevant: str
    subs: Optional[SubScores] = None
    score: int = 0
```

Update `Report` to add:
```python
youtube: List[YouTubeItem] = field(default_factory=list)
youtube_error: Optional[str] = None
```

**Update `scripts/lib/score.py`** — YouTube-specific engagement weights:
```python
def compute_youtube_engagement_raw(views, likes, comments):
    """YouTube engagement: views dominate, likes secondary, comments tertiary."""
    return (
        0.50 * math.log1p(views or 0) +
        0.35 * math.log1p(likes or 0) +
        0.15 * math.log1p(comments or 0)
    )
```

**Update `scripts/last30days.py`** — add YouTube to ThreadPoolExecutor:
```python
with ThreadPoolExecutor(max_workers=3) as executor:  # was 2
    if run_reddit:
        reddit_future = executor.submit(_search_reddit, ...)
    if run_x:
        x_future = executor.submit(_search_x, ...)
    if run_youtube:
        youtube_future = executor.submit(_search_youtube, ...)
```

**Update `scripts/lib/render.py`** — YouTube section in compact output:
```
### YouTube Videos

**{id}** (score:{score}) {channel_name} ({date}) [{views} views, {likes} likes]
  {title}
  https://www.youtube.com/watch?v={id}
  {transcript_snippet[:200]}...
  *{why_relevant}*
```

**Update `scripts/lib/env.py`** — YouTube availability detection:
```python
def is_ytdlp_available() -> bool:
    return shutil.which("yt-dlp") is not None
```

No API key needed. YouTube search is available whenever yt-dlp is in PATH.

#### Phase 4: SKILL.md Updates

Stats box adds YouTube line:
```
├─ 🎥 YouTube: {N} videos │ {N} views │ {N} transcripts
```

Citation priority updated:
```
1. @handles from X
2. YouTube creators — "per [Channel Name] on YouTube"
3. r/subreddits from Reddit
4. Web sources
```

Synthesis instructions updated to weight YouTube transcripts highly — a 20-minute video transcript with 500K views is a stronger signal than a tweet with 50 likes.

## Acceptance Criteria

- [x] `yt-dlp` search returns videos matching topic within date range
- [x] Transcripts extracted for top N videos (auto-generated captions)
- [x] Videos without captions gracefully skipped (no error)
- [x] YouTube results appear in compact output with engagement metrics
- [x] YouTube items scored and ranked alongside Reddit/X items
- [x] YouTube auto-activates when yt-dlp is available (no --sources flag needed)
- [x] SKILL.md stats box includes YouTube line
- [x] Transcript snippets (first ~500 words) included in output for LLM synthesis
- [ ] Total YouTube search + transcript extraction completes within 30 seconds
- [x] Works when yt-dlp is not installed (graceful degradation, no crash)
- [ ] Mock mode works for testing without network

## Dependencies & Risks

**Dependencies:**
- `yt-dlp` (Homebrew) — already installed, widely available via brew/pip/standalone
- No API keys needed
- No new Python packages (just subprocess + regex)

**Risks:**
| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| yt-dlp search is slow (>10s) | Medium | Set 30s timeout, run in parallel with Reddit/X |
| YouTube blocks yt-dlp | Low | yt-dlp is actively maintained with anti-bot updates. Degrade gracefully. |
| Videos lack auto-captions | Medium (~5%) | Skip those videos, note in output. Transcript is enrichment, not required. |
| Transcript extraction adds latency | High | Only fetch top 3-5, run in parallel, use tempdir |
| yt-dlp not installed for some users | Medium | Auto-detect, skip YouTube with info message, don't error |
| Linux `--dateafter` date format differs | Low | Use Python to format date, not shell `date -v` |

## Files to Create/Modify

### New Files
- `scripts/lib/youtube_yt.py` — search, transcript extraction, parsing
- `tests/test_youtube_yt.py` — unit tests
- `fixtures/youtube_sample.json` — mock data for tests

### Modified Files
- `scripts/lib/schema.py` — add YouTubeItem, update Report
- `scripts/lib/normalize.py` — add normalize_youtube_items()
- `scripts/lib/score.py` — add YouTube engagement scoring
- `scripts/lib/dedupe.py` — add YouTube dedup (title + channel Jaccard)
- `scripts/lib/render.py` — add YouTube section to compact + full report
- `scripts/lib/env.py` — add yt-dlp availability check, update source detection
- `scripts/last30days.py` — add _search_youtube(), update run_research(), update arg parser
- `SKILL.md` — update stats box, citation rules, synthesis instructions
- `README.md` — document YouTube source, yt-dlp requirement

## Alternative Approaches Considered

**1. YouTube Data API v3** — Rejected. Requires API key + Google Cloud project. Adds friction, counter to "zero config" philosophy. 10K quota/day limit. yt-dlp has no limits.

**2. steipete/summarize for transcripts** — Rejected for MVP. Adds 146MB dependency, requires brew tap, calls OpenAI API per video (adds cost). Raw transcripts via yt-dlp are better input for our synthesis LLM anyway. Could revisit as optional enhancement for captionless videos.

**3. youtube-transcript-api Python package** — Considered. Lightweight, Python-native transcript fetcher. But adds a pip dependency to a project that currently has zero Python deps. yt-dlp is already a brew dependency we can auto-detect.

**4. Skip transcripts, just use metadata** — Rejected. Titles + view counts alone don't give the synthesis LLM enough to work with. Transcripts are what make YouTube a *research* source vs just a link list.

## Cost Impact

**Zero additional API cost.** yt-dlp scrapes YouTube directly. No API keys, no token usage. The only cost is the existing OpenAI/xAI calls for Reddit/X search, which are unchanged.

**Time impact:** Adds ~10-20 seconds to research (search + parallel transcript extraction), running in parallel with Reddit/X so effective wall-clock increase is minimal.
