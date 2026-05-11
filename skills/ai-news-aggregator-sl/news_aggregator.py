#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "feedparser",
#   "requests",
#   "openai",
#   "anthropic",
#   "tavily-python",
# ]
# ///
"""
AI News Aggregator — OpenClaw Skill Script
==========================================
Sources : TechCrunch, The Verge, NYT Tech (RSS) + Tavily search + Twitter/X + YouTube
AI      : DeepSeek (default) · OpenAI · Anthropic Claude — user's choice
Output  : Discord channel via webhook (formatted markdown)

Credentials: read from environment variables only (no .env file loaded).
OpenClaw passes env vars declared in SKILL.md requires.env automatically.

AI provider selection (pick one):
  Provider   Env var needed          Default model
  ─────────  ──────────────────────  ─────────────────────────
  deepseek   DEEPSEEK_API_KEY        deepseek-chat
  openai     OPENAI_API_KEY          gpt-4o-mini
  claude     ANTHROPIC_API_KEY       claude-3-5-haiku-20241022

  Set AI_PROVIDER=<provider> env var, or pass --provider flag at runtime.
  Override model with AI_MODEL=<model> env var or --model flag.

External endpoints contacted:
  - https://api.deepseek.com/chat/completions     (provider=deepseek)
  - https://api.openai.com/v1/chat/completions    (provider=openai)
  - https://api.anthropic.com/v1/messages         (provider=claude)
  - https://discord.com/api/webhooks/...           (always, required)
  - https://techcrunch.com/.../feed/              (default AI topic only)
  - https://www.theverge.com/rss/...              (default AI topic only)
  - https://www.nytimes.com/svc/collections/...   (default AI topic only)
  - https://api.tavily.com/search                 (only if TAVILY_API_KEY set)
  - https://api.twitterapi.io/...                 (only if TWITTERAPI_IO_KEY set)
  - https://www.googleapis.com/youtube/v3/...     (only if YOUTUBE_API_KEY set)

CLI flags:
    --topic TEXT      Topic to search (default: AI via RSS)
    --days  N         How many days back (default: 1)
    --report TYPE     news | trending | all (default: all)
    --provider TEXT   AI provider: deepseek | openai | claude (default: deepseek)
    --model TEXT      Override AI model (e.g. gpt-4o, claude-3-5-sonnet-20241022)
    --dry-run         Print to stdout instead of posting to Discord
    --test-discord    Send a test message to Discord and exit
"""

import os
import sys
import re
import time
import argparse
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from openai import OpenAI

# ── AI provider config ────────────────────────────────────────
# Reads AI_PROVIDER from env; can be overridden at runtime via --provider flag.
# Only clear OPENAI_BASE_URL to prevent accidental endpoint redirection.
# OPENAI_API_KEY is preserved so provider=openai works correctly.
os.environ.pop("OPENAI_BASE_URL", None)

AI_PROVIDER_DEFAULT = os.getenv("AI_PROVIDER", "openai").lower()

DEEPSEEK_API_KEY   = os.getenv("DEEPSEEK_API_KEY", "")
OPENAI_API_KEY     = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY", "")

TAVILY_API_KEY               = os.getenv("TAVILY_API_KEY", "")
TWITTER_API_KEY              = os.getenv("TWITTERAPI_IO_KEY", "")
YOUTUBE_API_KEY              = os.getenv("YOUTUBE_API_KEY", "")
DISCORD_WEBHOOK_URL          = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
DISCORD_WEBHOOK_URL_TRENDING = os.getenv("DISCORD_WEBHOOK_URL_TRENDING", "").strip() or DISCORD_WEBHOOK_URL

TWITTER_MAX_TWEETS = int(os.getenv("TWITTER_MAX_TWEETS", "15"))
YT_MIN_VIEWS       = int(os.getenv("YT_MIN_VIEWS", "10000"))

DEFAULT_TOPIC = "AI"
DEFAULT_DAYS  = 1

# Default RSS feeds for AI topic
RSS_FEEDS = {
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge":  "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "NYT Tech":   "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/spotlight/artificial-intelligence/rss.xml",
}

# Curated AI YouTube channels (handle -> display name)
AI_YOUTUBE_CHANNELS = {
    "mreflow":              "Matt Wolfe",
    "WesRoth":              "Wes Roth",
    "TwoMinutePapers":      "Two Minute Papers",
    "aiexplained-official": "AI Explained",
    "AndrejKarpathy":       "Andrej Karpathy",
    "lexfridman":           "Lex Fridman",
    "YannicKilcher":        "Yannic Kilcher",
    "3blue1brown":          "3Blue1Brown",
    "Fireship":             "Fireship",
    "TheAIAdvantage":       "The AI Advantage",
    "samwitteveenai":       "Sam Witteveen",
    "Google_DeepMind":      "DeepMind",
    "OpenAI":               "OpenAI",
    "AnthropicAI":          "Anthropic",
    "sentdex":              "Sentdex",
}

# ── Helpers ───────────────────────────────────────────────────

def cutoff_from_days(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)

def is_default_topic(topic: str) -> bool:
    return topic.strip().lower() in ("ai", "artificial intelligence", "")

def _fmt_views(n: int) -> str:
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

def _parse_duration_seconds(duration: str) -> int:
    h  = int(m.group(1)) if (m := re.search(r'(\d+)H', duration)) else 0
    mn = int(m.group(1)) if (m := re.search(r'(\d+)M', duration)) else 0
    s  = int(m.group(1)) if (m := re.search(r'(\d+)S', duration)) else 0
    return h * 3600 + mn * 60 + s

# ── AI provider: call_ai() ────────────────────────────────────

PROVIDER_DEFAULTS = {
    "deepseek": "deepseek-chat",
    "openai":   "gpt-4o-mini",
    "claude":   "claude-3-5-haiku-20241022",
}

def call_ai(prompt: str, provider: str, model_override: str = "") -> str:
    """Send prompt to the chosen AI provider and return the response text."""
    provider = provider.lower()
    model = model_override or os.getenv("AI_MODEL", "") or PROVIDER_DEFAULTS.get(provider, "")

    if provider == "claude":
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()

    elif provider == "openai":
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.6,
        )
        return resp.choices[0].message.content.strip()

    else:  # deepseek (default)
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.6,
        )
        return resp.choices[0].message.content.strip()

def build_english_editorial(items: list, topic: str, days: int,
                             provider: str = "deepseek", model: str = "") -> str:
    if not items:
        return ""
    today  = datetime.now().strftime("%Y-%m-%d")
    period = "today" if days == 1 else f"the last {days} days"
    item_lines = [
        f"{i}. Title: {it.get('title','')}\n   Source: {it.get('source','')}\n   URL: {it.get('url','')}"
        for i, it in enumerate(items, 1)
    ]
    prompt = (
        f"You are a news editor. The date is {today}.\n\n"
        f"Here are the top stories about \"{topic}\" from {period} ({len(items)} items):\n\n"
        + "\n".join(item_lines)
        + "\n\nComplete two tasks — output plain text only (no JSON, no extra commentary):\n\n"
        "## Task 1: Overview\n"
        "Write a 150-200 word editorial paragraph summarising the most important developments.\n"
        "- Natural journalistic prose, no bullet points or lists\n"
        "- Embed the most important story titles as Markdown hyperlinks: [keyword](url)\n"
        "- Highlight connections between stories and the overall trend\n\n"
        "## Task 2: Worth Reading\n"
        "Pick the 3 most worth-reading items. One sentence each explaining why:\n"
        "🔖 [Title](url) — reason\n\n"
        "Output only these two sections."
    )
    try:
        print(f"  [AI] Using provider={provider} model={model or PROVIDER_DEFAULTS.get(provider, '')}")
        editorial = call_ai(prompt, provider, model)
    except Exception as exc:
        print(f"  [AI:{provider}] Editorial failed: {exc}")
        editorial = "\n".join(
            f"• [{it.get('title','')}]({it.get('url','')})" for it in items[:10]
        )
    label = "Today" if days == 1 else f"Last {days} Days"
    return f"**📰 {today} — {topic} News ({label})**\n\n{editorial}"

# ── RSS (AI default topic) ────────────────────────────────────

def fetch_rss(source_name: str, feed_url: str, cutoff: datetime) -> list:
    print(f"  Fetching RSS: {source_name}")
    try:
        feed = feedparser.parse(feed_url)
    except Exception as exc:
        print(f"  [RSS] Failed: {exc}")
        return []
    items = []
    for entry in feed.entries:
        pub = None
        for attr in ("published_parsed", "updated_parsed"):
            t = getattr(entry, attr, None)
            if t:
                pub = datetime(*t[:6], tzinfo=timezone.utc)
                break
        if not pub or pub < cutoff:
            continue
        items.append({
            "title":  entry.get("title", ""),
            "date":   pub.strftime("%Y-%m-%d %H:%M"),
            "source": source_name,
            "url":    entry.get("link", ""),
        })
    print(f"    -> {len(items)} items")
    return items

def fetch_all_rss(cutoff: datetime) -> list:
    items = []
    for name, url in RSS_FEEDS.items():
        items.extend(fetch_rss(name, url, cutoff))
    return items

# ── Tavily news search (custom topics) ───────────────────────

def fetch_tavily(topic: str, days: int, max_results: int = 15) -> list:
    if not TAVILY_API_KEY:
        print("  [Tavily] TAVILY_API_KEY not set — skipping.")
        return []
    print(f"  Fetching Tavily: '{topic}' (last {days}d)")
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key":        TAVILY_API_KEY,
                "query":          f"{topic} news",
                "topic":          "news",
                "days":           days,
                "max_results":    max_results,
                "include_answer": False,
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"  [Tavily] Failed: {exc}")
        return []
    items = []
    for result in data.get("results", []):
        items.append({
            "title":  result.get("title", ""),
            "date":   result.get("published_date", datetime.now().strftime("%Y-%m-%d")),
            "source": result.get("source", result.get("url", "")[:50]),
            "url":    result.get("url", ""),
        })
    print(f"    -> {len(items)} results from Tavily")
    return items

# ── Twitter / X search ────────────────────────────────────────

def fetch_twitter(topic: str, cutoff: datetime) -> list:
    if not TWITTER_API_KEY:
        print("  [Twitter] TWITTERAPI_IO_KEY not set — skipping.")
        return []
    print(f"  Fetching Twitter: '{topic}'")
    try:
        resp = requests.get(
            "https://api.twitterapi.io/twitter/tweet/advanced_search",
            headers={"X-API-Key": TWITTER_API_KEY},
            params={"query": topic, "queryType": "Top"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"  [Twitter] Failed: {exc}")
        return []
    items = []
    for tweet in data.get("tweets", [])[:TWITTER_MAX_TWEETS]:
        raw = tweet.get("createdAt") or tweet.get("created_at", "")
        try:
            created = datetime.strptime(
                raw.replace("+0000", "UTC"), "%a %b %d %H:%M:%S UTC %Y"
            ).replace(tzinfo=timezone.utc)
        except Exception:
            try:
                created = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except Exception:
                continue
        if created < cutoff:
            continue
        user = (
            tweet.get("author", {}).get("userName", "")
            or tweet.get("user", {}).get("screen_name", "")
        )
        tid = tweet.get("id", "")
        items.append({
            "title":  tweet.get("text", ""),
            "date":   created.strftime("%Y-%m-%d %H:%M"),
            "source": f"Twitter/@{user}",
            "url":    f"https://twitter.com/{user}/status/{tid}" if tid else "",
        })
    print(f"    -> {len(items)} tweets")
    return items

# ── YouTube ───────────────────────────────────────────────────

def _enrich_videos(video_ids: list, video_meta: dict, min_views: int = 0) -> list:
    if not video_ids:
        print("    -> 0 videos")
        return []
    stats_map = {}
    for i in range(0, len(video_ids), 50):
        try:
            resp = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "statistics,contentDetails",
                    "id":   ",".join(video_ids[i:i+50]),
                    "key":  YOUTUBE_API_KEY,
                },
                timeout=10,
            )
            for v in resp.json().get("items", []):
                stats_map[v["id"]] = {
                    "stats":    v.get("statistics", {}),
                    "duration": v.get("contentDetails", {}).get("duration", ""),
                }
        except Exception:
            pass
    items = []
    for vid_id in video_ids:
        meta     = video_meta[vid_id]
        info     = stats_map.get(vid_id, {})
        duration = info.get("duration", "")
        views    = int(info.get("stats", {}).get("viewCount", 0))
        # Skip Shorts (60 seconds or under)
        if duration and _parse_duration_seconds(duration) <= 61:
            continue
        if views < min_views:
            continue
        items.append({
            "title":  meta["title"],
            "date":   meta["pub"].strftime("%Y-%m-%d %H:%M"),
            "source": meta["channel"],
            "url":    f"https://www.youtube.com/watch?v={vid_id}",
            "views":  views,
        })
    items.sort(key=lambda x: x.get("views", 0), reverse=True)
    print(f"    -> {len(items)} video(s)")
    return items

def _resolve_channel_ids(handles: list) -> dict:
    resolved = {}
    for handle in handles:
        try:
            resp = requests.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part":      "contentDetails,snippet",
                    "forHandle": handle,
                    "key":       YOUTUBE_API_KEY,
                },
                timeout=10,
            )
            its = resp.json().get("items", [])
            if its:
                resolved[handle] = (
                    its[0]["id"],
                    its[0]["contentDetails"]["relatedPlaylists"]["uploads"],
                )
        except Exception as exc:
            print(f"    [YouTube] Could not resolve @{handle}: {exc}")
        time.sleep(0.1)
    return resolved

def fetch_youtube_from_channels(cutoff: datetime, videos_per_channel: int = 3) -> list:
    if not YOUTUBE_API_KEY:
        print("  [YouTube] YOUTUBE_API_KEY not set — skipping.")
        return []
    print(f"  Fetching YouTube: {len(AI_YOUTUBE_CHANNELS)} curated AI channels")
    handle_map    = _resolve_channel_ids(list(AI_YOUTUBE_CHANNELS.keys()))
    all_ids, meta = [], {}
    for handle, (_, playlist_id) in handle_map.items():
        display = AI_YOUTUBE_CHANNELS.get(handle, handle)
        try:
            resp = requests.get(
                "https://www.googleapis.com/youtube/v3/playlistItems",
                params={
                    "part":       "snippet",
                    "playlistId": playlist_id,
                    "maxResults": videos_per_channel,
                    "key":        YOUTUBE_API_KEY,
                },
                timeout=10,
            )
            for item in resp.json().get("items", []):
                s      = item.get("snippet", {})
                vid_id = s.get("resourceId", {}).get("videoId", "")
                pub_s  = s.get("publishedAt", "")
                if not vid_id or not pub_s:
                    continue
                try:
                    pub = datetime.fromisoformat(pub_s.replace("Z", "+00:00"))
                except Exception:
                    continue
                if pub < cutoff:
                    continue
                all_ids.append(vid_id)
                meta[vid_id] = {"title": s.get("title", ""), "channel": display, "pub": pub}
        except Exception as exc:
            print(f"    [YouTube] Failed for {display}: {exc}")
        time.sleep(0.1)
    return _enrich_videos(all_ids, meta, min_views=YT_MIN_VIEWS)

def fetch_youtube_by_topic(topic: str, cutoff: datetime, max_results: int = 12) -> list:
    if not YOUTUBE_API_KEY:
        print("  [YouTube] YOUTUBE_API_KEY not set — skipping.")
        return []
    print(f"  Searching YouTube: '{topic}'")
    published_after = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part":           "snippet",
                "q":              topic,
                "type":           "video",
                "videoDuration":  "medium",
                "order":          "viewCount",
                "publishedAfter": published_after,
                "maxResults":     max_results,
                "key":            YOUTUBE_API_KEY,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"  [YouTube] Search failed: {exc}")
        return []
    all_ids, meta = [], {}
    for item in data.get("items", []):
        vid_id = item.get("id", {}).get("videoId", "")
        s      = item.get("snippet", {})
        title  = s.get("title", "")
        # Skip Shorts by title tag
        if any(tag in title.lower() for tag in ("#short", "#shorts", "shorts")):
            continue
        pub_s = s.get("publishedAt", "")
        try:
            pub = datetime.fromisoformat(pub_s.replace("Z", "+00:00"))
        except Exception:
            continue
        all_ids.append(vid_id)
        meta[vid_id] = {"title": title, "channel": s.get("channelTitle", ""), "pub": pub}
    return _enrich_videos(all_ids, meta, min_views=0)

# ── Discord output ────────────────────────────────────────────

DISCORD_MAX_CHARS = 1900

def _chunk_markdown(md: str, max_len: int = DISCORD_MAX_CHARS) -> list:
    lines = md.split("\n")
    chunks, current = [], ""
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            if current:
                chunks.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks or [md[:max_len]]

def post_to_discord(webhook_url: str, content: str, title: str = "") -> bool:
    if not webhook_url:
        print("  [Discord] No webhook URL set — printing to stdout.")
        print("=" * 60)
        print(content)
        print("=" * 60)
        return True
    chunks = _chunk_markdown(content)
    print(f"  [Discord] Sending {len(chunks)} chunk(s)...")
    for i, chunk in enumerate(chunks):
        if title and len(chunks) > 1:
            header = f"**{title}** *(part {i+1}/{len(chunks)})*\n"
        elif title and i == 0:
            header = f"**{title}**\n"
        else:
            header = ""
        try:
            resp = requests.post(webhook_url, json={"content": header + chunk}, timeout=15)
            print(f"  [Discord] Chunk {i+1} → HTTP {resp.status_code}")
            if resp.status_code == 429:
                wait = resp.json().get("retry_after", 2)
                print(f"  [Discord] Rate limited — waiting {wait}s...")
                time.sleep(float(wait) + 0.5)
                resp = requests.post(webhook_url, json={"content": header + chunk}, timeout=15)
            if not resp.ok:
                print(f"  [Discord] Error: {resp.text[:300]}")
                return False
            time.sleep(0.6)
        except Exception as exc:
            print(f"  [Discord] Exception: {exc}")
            return False
    return True

def build_youtube_section(yt_items: list, topic: str, days: int) -> str:
    if not yt_items:
        return ""
    today = datetime.now().strftime("%Y-%m-%d")
    label = "Today" if days == 1 else f"Last {days} Days"
    lines = [f"**▶️ {today} — {topic} YouTube ({label})**\n"]
    for v in yt_items[:12]:
        views_str = f" ({_fmt_views(v.get('views', 0))} views)" if v.get("views", 0) > 0 else ""
        lines.append(
            f"▶ **{v.get('source', '')}** — [{v.get('title', '')}]({v.get('url', '')}){views_str}"
        )
    return "\n".join(lines).strip()

# ── Config validation ─────────────────────────────────────────

def validate_config(provider: str):
    key_map = {
        "deepseek": ("DEEPSEEK_API_KEY", DEEPSEEK_API_KEY),
        "openai":   ("OPENAI_API_KEY",   OPENAI_API_KEY),
        "claude":   ("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY),
    }
    if provider not in key_map:
        print(f"\n❌ Unknown provider '{provider}'. Choose: deepseek | openai | claude")
        sys.exit(1)
    var_name, key_val = key_map[provider]
    if not key_val:
        print(f"\n❌ {var_name} not set. Register it with: openclaw config set env.{var_name} '<key>'")
        sys.exit(1)
    if not DISCORD_WEBHOOK_URL:
        print("  ⚠️  DISCORD_WEBHOOK_URL not set — output will print to stdout only.")

# ── Report runners ────────────────────────────────────────────

def run_news_report(topic: str, days: int, provider: str, model: str, dry_run: bool = False):
    cutoff = cutoff_from_days(days)
    print(f"\n📰 === News: '{topic}' | last {days}d ===")
    if is_default_topic(topic):
        items = fetch_all_rss(cutoff)
    else:
        if not TAVILY_API_KEY:
            print("  ❌ TAVILY_API_KEY not set — cannot search custom topics.")
            return
        items = fetch_tavily(topic, days)
    if not items:
        print(f"  No news found for '{topic}' in last {days}d.")
        return
    print(f"\n  Building editorial for {len(items)} items...")
    digest = build_english_editorial(items, topic, days, provider=provider, model=model)
    if dry_run:
        print("\n--- DRY RUN ---\n" + digest)
    else:
        print("\n  Posting to Discord...")
        ok = post_to_discord(DISCORD_WEBHOOK_URL, digest)
        print("  ✅ Posted." if ok else "  ❌ Failed.")

def run_trending_report(topic: str, days: int, provider: str, model: str, dry_run: bool = False):
    cutoff = cutoff_from_days(days)
    print(f"\n🔥 === Trending: '{topic}' | last {days}d ===")
    twitter_items = fetch_twitter(topic, cutoff)
    yt_items = (
        fetch_youtube_from_channels(cutoff)
        if is_default_topic(topic)
        else fetch_youtube_by_topic(topic, cutoff)
    )
    twitter_digest = ""
    if twitter_items:
        print(f"\n  Building Twitter editorial for {len(twitter_items)} tweets...")
        twitter_digest = build_english_editorial(
            twitter_items, f"{topic} on Twitter", days, provider=provider, model=model
        )
    yt_section = build_youtube_section(yt_items, topic, days) if yt_items else ""
    if not twitter_digest and not yt_section:
        print("  No trending content found.")
        return
    full = "\n\n".join(filter(None, [twitter_digest, yt_section]))
    if dry_run:
        print("\n--- DRY RUN ---\n" + full)
    else:
        print("\n  Posting to Discord...")
        ok = post_to_discord(DISCORD_WEBHOOK_URL_TRENDING, full)
        print("  ✅ Posted." if ok else "  ❌ Failed.")

def test_discord_webhook():
    print("\n🔔 Testing Discord webhook...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    ok = post_to_discord(
        DISCORD_WEBHOOK_URL,
        f"✅ **AI News Aggregator** — webhook working! ({timestamp})",
    )
    print("  ✅ Check your Discord channel." if ok else "  ❌ Webhook test failed.")
    sys.exit(0 if ok else 1)

# ── Entry point ───────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI News Aggregator")
    parser.add_argument("--topic",        type=str, default=DEFAULT_TOPIC,
                        help="Topic to search. Default: AI (RSS feeds). Custom topics use Tavily.")
    parser.add_argument("--days",         type=int, default=DEFAULT_DAYS,
                        help="How many days back to search (default: 1)")
    parser.add_argument("--report",       choices=["all", "news", "trending"], default="all",
                        help="Which report to run (default: all)")
    parser.add_argument("--provider",     type=str, default=AI_PROVIDER_DEFAULT,
                        help="AI provider: deepseek | openai | claude (default: deepseek or AI_PROVIDER env)")
    parser.add_argument("--model",        type=str, default="",
                        help="Override AI model (e.g. gpt-4o, claude-3-5-sonnet-20241022, deepseek-reasoner)")
    parser.add_argument("--dry-run",      action="store_true",
                        help="Print output to stdout instead of posting to Discord")
    parser.add_argument("--test-discord", action="store_true",
                        help="Send a test message to Discord and exit")
    args = parser.parse_args()

    provider = args.provider.lower()
    model    = args.model.strip()

    validate_config(provider)

    if args.test_discord:
        test_discord_webhook()

    topic = args.topic.strip()
    days  = max(1, args.days)

    start = time.time()
    print(f"\n🦞 AI News Aggregator — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   Topic: {topic} | Last {days} day(s) | Provider: {provider} | Dry-run: {args.dry_run}")

    if args.report in ("all", "news"):
        run_news_report(topic, days, provider=provider, model=model, dry_run=args.dry_run)
    if args.report in ("all", "trending"):
        run_trending_report(topic, days, provider=provider, model=model, dry_run=args.dry_run)

    print(f"\n✅ Done in {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
