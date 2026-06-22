#!/usr/bin/env python3
"""
Market Evening Brief — Daily evening market summary and AI-filtered news digest.

Two modes:
1. --mode market: lightweight trading summary (activity, overnight watch, signals today)
2. --mode news: full news digest with two-stage AI filtering (relevance + materiality gate)

The news variant includes:
- Stage 1: DDG news search → Qwen relevance analysis (is_significant, confidence 0-1, category, summary)
- Stage 2: Qwen materiality gate comparing candidates against 48h history (prevents notification fatigue)
- Fail-closed design: if Qwen fails, drop all articles (silence over noise)
- Configurable: topics list, max_per_topic (3), min_confidence (0.7), briefing_time (18:00)
- News history persistence in ~/.openclaw/state/evening_news_history.json (48h rolling, max 200 entries)
- Category icons: policy 🏛️, markets 📈, technology 💻, geopolitics 🌍

Usage:
    python evening_brief.py [--mode {market|news}] [--config CONFIG] [--force] [--dry-run] [--debug]
    python evening_brief.py --mode news --topics "crypto,AI,Fed" --min-confidence 0.8
    python evening_brief.py --mode news --no-materiality-gate  # skip Stage 2 filter
    python evening_brief.py --mode market --force --debug

Outputs plain text to stdout (no markdown, no emojis — SMS/iMessage compatible).
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Optional dependencies
try:
    import requests
except ImportError:
    requests = None

try:
    import yaml
except ImportError:
    yaml = None

try:
    from kalshi_python_sync import Configuration as KalshiConfiguration, KalshiClient
except ImportError:
    try:
        from kalshi_python import Configuration as KalshiConfiguration, KalshiClient
    except ImportError:
        KalshiConfiguration = None
        KalshiClient = None


def log(msg, debug=False):
    """Log message to stderr if debug enabled."""
    if debug:
        print(f"[DEBUG] {msg}", file=sys.stderr)


def check_cache_age(cache_file, max_age_seconds):
    """Check if cache is fresh. Returns ('fresh', age_secs) or ('stale', age_secs) or ('missing', 0)."""
    try:
        with open(cache_file) as f:
            data = json.load(f)

        cached_at = data.get("cached_at")
        if not cached_at:
            return "missing", 0

        dt = datetime.fromisoformat(cached_at.replace("Z", "+00:00"))
        age_seconds = (datetime.now(timezone.utc) - dt).total_seconds()

        if age_seconds > max_age_seconds:
            return "stale", age_seconds
        return "fresh", age_seconds
    except FileNotFoundError:
        return "missing", 0
    except Exception:
        return "error", 0


# ============================================================================
# MARKET MODE: Activity Summary + Overnight Watch + Today's X Signals
# ============================================================================

def format_activity_section(kalshi, config, debug=False):
    """Fetch and format day's trading activity."""
    section_lines = []

    if not kalshi:
        return "ACTIVITY: unavailable (Kalshi API not configured)"

    try:
        # Get current portfolio
        positions = kalshi.get_portfolio()
        total_cost = sum(
            p.get("quantity", 0) * p.get("average_price", 0) / 100
            for p in positions
        )
        total_unrealized = sum(
            p.get("quantity", 0) * (p.get("last_price", p.get("average_price", 0)) - p.get("average_price", 0)) / 100
            for p in positions
        )

        # Format activity section
        lines = [
            f"ACTIVITY:",
            f"Current positions: {len(positions)} | Cost: ${total_cost:.0f} | Unrealized: {'$+' if total_unrealized >= 0 else '$'}{total_unrealized:.0f}",
        ]

        return "\n".join(lines)

    except Exception as e:
        log(f"Activity fetch error: {e}", debug)
        return f"ACTIVITY: unavailable ({str(e)[:40]})"


def format_overnight_watch_section(kalshi, config, debug=False):
    """Identify positions expiring soon and low-liquidity markets."""
    if not kalshi:
        return "OVERNIGHT WATCH: (none)"

    try:
        positions = kalshi.get_portfolio()
        now = datetime.now(timezone.utc)

        watch_items = []

        for pos in positions:
            ticker = pos.get("ticker", "?")

            # Check expiration (< 7 days)
            try:
                market = kalshi.get_market(ticker)
                exp_ts = market.get("close_datetime")
                if exp_ts:
                    exp_dt = datetime.fromisoformat(exp_ts.replace("Z", "+00:00"))
                    days_to_exp = (exp_dt - now).days

                    if days_to_exp < 7 and days_to_exp >= 0:
                        watch_items.append(f"{ticker} expires in {days_to_exp}d — monitor for resolution")

                    # Check liquidity
                    volume = market.get("volume", 0)
                    if volume < 100:
                        watch_items.append(f"{ticker} low liquidity ({volume} vol) — wide spreads")

            except Exception:
                pass

        if not watch_items:
            return "OVERNIGHT WATCH: (none)"

        lines = ["OVERNIGHT WATCH:"]
        for item in watch_items[:5]:  # Max 5 items
            lines.append(f"• {item}")

        return "\n".join(lines)

    except Exception as e:
        log(f"Watch list error: {e}", debug)
        return "OVERNIGHT WATCH: (unavailable)"


def format_xsignals_today_section(cache_path, config, debug=False):
    """Read Xpulse signals from today only (not last 24h rolling)."""
    freshness, age = check_cache_age(cache_path, 14400)  # 4 hour tolerance

    if freshness == "missing":
        return "X SIGNALS TODAY: (none)"

    if freshness == "stale":
        log(f"Xpulse cache stale: {age}s old", debug)
        return "X SIGNALS TODAY: (none)"

    try:
        with open(cache_path) as f:
            data = json.load(f)

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        signals = []
        for sig in data.get("signals", []):
            ts_str = sig.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if ts > today_start:
                    signals.append(sig)
            except Exception:
                pass

        # Sort by confidence, take top 3
        signals.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        signals = signals[:3]

        if not signals:
            return "X SIGNALS TODAY: (none)"

        lines = ["X SIGNALS TODAY:"]

        for sig in signals:
            signal_text = sig.get("signal", "?")
            confidence = sig.get("confidence", 0)

            lines.append(f"• {signal_text} ({confidence*100:.0f}% conf)")

        return "\n".join(lines)

    except Exception as e:
        log(f"Xpulse parse error: {e}", debug)
        return "X SIGNALS TODAY: (none)"


def format_scorecard_section(config, debug=False):
    """Build a fail-loud month-to-date trading scorecard from the trade ledger."""
    try:
        script_dir = Path(__file__).resolve().parents[2] / "kalshalyst" / "scripts"
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))
        from trade_ledger import get_monthly_scorecard
    except Exception as e:
        log(f"Scorecard import error: {e}", debug)
        return "P&L SCORECARD: I don't know (trade ledger unavailable)"

    try:
        scorecard = get_monthly_scorecard()
    except Exception as e:
        log(f"Scorecard build error: {e}", debug)
        return f"P&L SCORECARD: I don't know ({str(e)[:60]})"

    lines = [f"P&L SCORECARD ({scorecard['month']}):"]
    lines.append(
        f"Wins/Losses: {scorecard['wins']}W / {scorecard['losses']}L | "
        f"Total P&L: ${scorecard['total_pnl']:+.2f}"
    )

    if scorecard["best_trade"]:
        best = scorecard["best_trade"]
        lines.append(
            f"Best: {best.get('ticker', '?')} ${float(best.get('pnl', 0)):+.2f} | {best.get('title', '')[:36]}"
        )
    else:
        lines.append("Best: I don't know yet (no resolved trades this month)")

    if scorecard["worst_trade"]:
        worst = scorecard["worst_trade"]
        lines.append(
            f"Worst: {worst.get('ticker', '?')} ${float(worst.get('pnl', 0)):+.2f} | {worst.get('title', '')[:36]}"
        )
    else:
        lines.append("Worst: I don't know yet (no resolved trades this month)")

    if scorecard["edge_accuracy_pct"] is not None:
        lines.append(f"Edge accuracy: {scorecard['edge_accuracy_pct']:.1f}% this month")
    else:
        lines.append("Edge accuracy: I don't know yet (no resolved win/loss sample)")

    lines.append(
        f"Known sample: {scorecard['resolved_entries']} resolved, {scorecard['confirmed_entries']} confirmed fills"
    )
    return "\n".join(lines)


def build_market_brief(config, kalshi=None, debug=False):
    """Build lightweight market-only evening brief."""
    now = datetime.now()
    header = f"EVENING BRIEFING — {now.strftime('%A, %B %d, %Y')}"

    sections = [header]

    # Activity summary
    if config.get("include", {}).get("activity", True):
        activity = format_activity_section(kalshi, config, debug)
        sections.append(activity)

    if config.get("include", {}).get("scorecard", True):
        sections.append(format_scorecard_section(config, debug))

    # Overnight watch
    if config.get("include", {}).get("overnight_watch", True):
        watch = format_overnight_watch_section(kalshi, config, debug)
        sections.append(watch)

    # X signals from today
    if config.get("include", {}).get("xpulse_signals_today", True):
        cache_path = config.get("cache_paths", {}).get("xpulse")
        if cache_path:
            signals = format_xsignals_today_section(cache_path, config, debug)
            sections.append(signals)

    return "\n\n".join(sections)


# ============================================================================
# NEWS MODE: Two-Stage AI-Filtered News Pipeline
# ============================================================================

def _search_news(topics, max_per_topic=3, debug=False):
    """Search for recent news using ddgs.news() or fallback to duckduckgo_search."""
    all_articles = []

    # Strategy 1: ddgs package (newer, preferred)
    try:
        from ddgs import DDGS
        d = DDGS()
        for topic in topics:
            try:
                results = list(d.news(topic, max_results=max_per_topic))
                for article in results:
                    all_articles.append({
                        "topic": topic,
                        "title": article.get("title", ""),
                        "body": article.get("body", ""),
                        "source": article.get("source", ""),
                        "url": article.get("url", ""),
                        "date": article.get("date", ""),
                    })
                log(f"  {topic}: {len(results)} articles found", debug)
            except Exception as e:
                log(f"  {topic}: search failed ({e})", debug)
        if all_articles:
            return all_articles
    except ImportError:
        log("ddgs not available, trying legacy duckduckgo_search", debug)
    except Exception as e:
        log(f"ddgs error: {e}, trying legacy", debug)

    # Strategy 2: duckduckgo_search (legacy fallback)
    try:
        from duckduckgo_search import DDGS as DDGS_OLD
        with DDGS_OLD() as ddgs:
            for topic in topics:
                try:
                    results = list(ddgs.news(topic, max_results=max_per_topic))
                    for article in results:
                        all_articles.append({
                            "topic": topic,
                            "title": article.get("title", ""),
                            "body": article.get("body", ""),
                            "source": article.get("source", ""),
                            "url": article.get("url", ""),
                            "date": article.get("date", ""),
                        })
                    log(f"  {topic}: {len(results)} articles found", debug)
                except Exception as e:
                    log(f"  {topic}: search failed ({e})", debug)
        return all_articles
    except ImportError:
        log("duckduckgo_search not available", debug)
    except Exception as e:
        log(f"duckduckgo_search error: {e}", debug)

    return []


def _analyze_relevance_local(articles, debug=False):
    """Stage 1: Analyze articles for relevance and significance using local Qwen."""
    if not articles:
        return []

    significant_articles = []

    for article in articles:
        try:
            title = article.get("title", "")
            body = article.get("body", "")
            source = article.get("source", "")
            topic = article.get("topic", "")

            if not title or not body:
                continue

            prompt = (
                f"You are a news relevance analyzer for prediction markets and finance. "
                f"Evaluate this news article for significance.\n\n"
                f"Topic: {topic}\n"
                f"Title: {title}\n"
                f"Body: {body}\n"
                f"Source: {source}\n\n"
                f"Respond in JSON: {{"
                f"\"is_significant\": true/false, "
                f"\"confidence\": 0.0-1.0, "
                f"\"category\": \"policy/markets/technology/geopolitics/other\", "
                f"\"summary\": \"one line summary\""
                f"}}"
            )

            result = subprocess.run(
                ["ollama", "run", "qwen3:latest", "--format", "json", prompt],
                capture_output=True, timeout=30, text=True
            )

            if result.returncode != 0:
                log(f"  Stage 1: Qwen failed for '{title[:50]}...'", debug)
                continue

            parsed = json.loads(result.stdout.strip())
            if parsed.get("is_significant", False):
                article["confidence"] = float(parsed.get("confidence", 0))
                article["category"] = parsed.get("category", "other")
                article["summary"] = parsed.get("summary", title)
                significant_articles.append(article)

        except subprocess.TimeoutExpired:
            log(f"  Stage 1: timeout for '{title[:50]}...'", debug)
            continue
        except Exception as e:
            log(f"  Stage 1 error: {e}", debug)
            continue

    return significant_articles


def _load_news_history(history_path=None, debug=False):
    """Load history of previously sent evening briefing news (48h rolling)."""
    if not history_path:
        history_path = Path.home() / ".openclaw" / "state" / "evening_news_history.json"
    else:
        history_path = Path(history_path)

    try:
        with open(history_path) as f:
            data = json.load(f)
            # Only keep last 48h of history
            cutoff = time.time() - 48 * 3600
            kept = [h for h in data if h.get("timestamp", 0) > cutoff]
            log(f"Loaded {len(kept)} articles from 48h history", debug)
            return kept
    except (OSError, json.JSONDecodeError):
        log("No history found or error reading history", debug)
        return []


def _save_news_history(history, history_path=None, debug=False):
    """Persist sent news history (max 200 entries, 48h rolling)."""
    if not history_path:
        history_path = Path.home() / ".openclaw" / "state" / "evening_news_history.json"
    else:
        history_path = Path(history_path)

    try:
        # Ensure directory exists
        history_path.parent.mkdir(parents=True, exist_ok=True)
        # Keep max 200 entries
        with open(history_path, "w") as f:
            json.dump(history[-200:], f, indent=2)
        log(f"Saved {len(history[-200:])} articles to history", debug)
    except OSError as e:
        log(f"Error saving history: {e}", debug)


def _filter_material_news(articles, history, debug=False):
    """Stage 2: Qwen materiality gate — only pass through news worth an interruption.

    Compares candidate articles against recently sent history.
    Returns only articles that represent genuinely new, material developments.
    """
    if not articles:
        return []

    # Build history context for Qwen
    recent_summaries = []
    for h in history[-20:]:  # Last 20 sent articles
        ts = h.get("timestamp", 0)
        age_h = (time.time() - ts) / 3600
        recent_summaries.append(
            f"- [{age_h:.0f}h ago] {h.get('topic', '?')}: {h.get('title', '')}"
        )

    history_block = "\n".join(recent_summaries) if recent_summaries else "(No previous news sent)"

    # Build candidate articles block
    candidate_block = "\n".join(
        f"- [{a['topic']}] {a['title']}"
        for a in articles
    )

    try:
        prompt = (
            "You are a personal news filter for a prediction market trader. "
            "Your job is to PREVENT notification fatigue. Only let through news that is genuinely NEW and MATERIAL.\n\n"
            "RECENTLY SENT NEWS (what the user already knows):\n"
            f"{history_block}\n\n"
            "CANDIDATE NEW ARTICLES:\n"
            f"{candidate_block}\n\n"
            "RULES:\n"
            "- REJECT if the article covers the same story/development as recent news (even with different wording)\n"
            "- REJECT if it's ongoing background noise (e.g. 'Fed considers rate change' when rates have been discussed for weeks)\n"
            "- REJECT if there's no concrete new event, just commentary or opinion pieces\n"
            "- REJECT routine earnings reports, minor corporate announcements, or incremental updates\n"
            "- ACCEPT only if: (a) a genuinely new development occurred (policy change, major announcement, crisis, data release, market event), "
            "OR (b) a significant escalation/reversal of something previously reported\n"
            "- When in doubt, REJECT. The user prefers silence over noise.\n\n"
            "Respond in JSON: {\"keep\": [list of article titles to keep], \"reasoning\": \"one line explaining why\"}"
        )

        result = subprocess.run(
            ["ollama", "run", "qwen3:latest", "--format", "json", prompt],
            capture_output=True, timeout=90, text=True
        )

        if result.returncode != 0:
            log("Stage 2 filter: Qwen failed, dropping all articles (fail-closed)", debug)
            return []  # Fail closed — silence over noise when filter is broken

        parsed = json.loads(result.stdout.strip())
        keep_titles = set(parsed.get("keep", []))
        reasoning = parsed.get("reasoning", "")

        filtered = [a for a in articles if a["title"] in keep_titles]
        log(f"Stage 2 filter: {len(articles)} candidates → {len(filtered)} kept. Reason: {reasoning}", debug)
        return filtered

    except subprocess.TimeoutExpired:
        log("Stage 2 filter: Qwen timeout, dropping all articles (fail-closed)", debug)
        return []
    except Exception as e:
        log(f"Stage 2 filter error: {e}, dropping all articles (fail-closed)", debug)
        return []


def build_news_brief(config, debug=False, history_path=None):
    """Build full news digest with two-stage AI filtering."""
    now = datetime.now()
    header = f"EVENING NEWS BRIEFING — {now.strftime('%A, %B %d, %Y')}"

    # Get config
    topics = config.get("topics", ["prediction markets", "AI policy", "federal reserve"])
    max_per_topic = config.get("max_per_topic", 3)
    min_confidence = config.get("min_confidence", 0.7)
    use_materiality = config.get("materiality_gate", True)

    log(f"Evening news briefing starting... ({len(topics)} topics)", debug)

    # Search for news
    articles = _search_news(topics, max_per_topic=max_per_topic, debug=debug)

    if not articles:
        log("Evening news briefing: no articles found", debug)
        return f"{header}\n\n(No articles found)"

    log(f"Evening news briefing: {len(articles)} articles found, analyzing relevance...", debug)

    # Stage 1: Relevance filter
    significant = _analyze_relevance_local(articles, debug=debug)
    significant = [a for a in significant if a.get("confidence", 0) >= min_confidence]

    if not significant:
        log("Evening news briefing: no significant articles passed Stage 1 filter", debug)
        return f"{header}\n\n(No significant news found)"

    log(f"Evening news briefing: {len(significant)} significant articles after Stage 1", debug)

    # Limit to top 10 most confident articles for Stage 2 (to avoid timeout)
    significant.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    if len(significant) > 10:
        log(f"Evening news briefing: limiting to top 10 articles for Stage 2 filter", debug)
        significant = significant[:10]

    # Stage 2: Materiality gate
    news_history = _load_news_history(history_path=history_path, debug=debug)

    if use_materiality:
        material = _filter_material_news(significant, news_history, debug=debug)
        if not material:
            log("Evening news briefing: all articles filtered by materiality gate (nothing new)", debug)
            return f"{header}\n\n(No new material developments)"
        significant = material

    # Build briefing message
    significant.sort(key=lambda x: x.get("confidence", 0), reverse=True)

    parts = [header]
    for article in significant[:5]:  # Top 5
        category_icon = {
            "policy": "🏛️",
            "markets": "📈",
            "technology": "💻",
            "geopolitics": "🌍",
        }.get(article.get("category", "other"), "📌")

        confidence = int(article.get("confidence", 0) * 100)
        summary = article.get("summary", article.get("title", ""))
        source = article.get("source", "")

        parts.append(f"\n{category_icon} {summary} ({confidence}% conf, {source})")

    message = "".join(parts)

    # Save to history
    for article in significant[:5]:
        news_history.append({
            "topic": article.get("topic", ""),
            "title": article.get("title", ""),
            "summary": article.get("summary", ""),
            "category": article.get("category", ""),
            "confidence": article.get("confidence", 0),
            "timestamp": time.time(),
        })
    _save_news_history(news_history, history_path=history_path, debug=debug)
    log(f"Evening news briefing: {len(significant[:5])} material articles sent", debug)

    return message


# ============================================================================
# Main Entry Point
# ============================================================================

def load_config(config_path=None):
    """Load config from YAML file or return defaults."""
    if config_path and Path(config_path).exists():
        if yaml:
            with open(config_path) as f:
                data = yaml.safe_load(f)
                return data.get("market_morning_brief", {})

    # Default config
    return {
        "enabled": True,
        "kalshi": {"enabled": False},
        "cache_paths": {
            "xpulse": "state/.x_signal_cache.json",
        },
        "include": {
            "activity": True,
            "scorecard": True,
            "overnight_watch": True,
            "xpulse_signals_today": True,
        },
        "topics": ["prediction markets", "AI policy", "federal reserve"],
        "max_per_topic": 3,
        "min_confidence": 0.7,
        "materiality_gate": True,
    }


def check_time_window(config, debug=False):
    """Check if current time is within configured evening briefing window (±30 min)."""
    briefing_time = config.get("time", "18:00")
    try:
        bt_hour, bt_min = map(int, briefing_time.split(":"))
    except (ValueError, AttributeError):
        bt_hour, bt_min = 18, 0

    now = datetime.now()
    target = now.replace(hour=bt_hour, minute=bt_min, second=0, microsecond=0)
    diff_minutes = (now - target).total_seconds() / 60

    in_window = 0 <= diff_minutes <= 30
    log(f"Time check: {now.strftime('%H:%M:%S')}, target {briefing_time}, diff {diff_minutes:.0f}min, in_window={in_window}", debug)
    return in_window


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Market Evening Brief")
    parser.add_argument("--mode", choices=["market", "news"], default="market", help="Brief mode: market activity or news digest")
    parser.add_argument("--config", help="Path to config.yaml")
    parser.add_argument("--topics", help="Comma-separated topics (news mode only)")
    parser.add_argument("--min-confidence", type=float, help="Min confidence threshold (0-1, news mode only)")
    parser.add_argument("--max-per-topic", type=int, help="Max articles per topic (news mode only)")
    parser.add_argument("--no-materiality-gate", action="store_true", help="Disable Stage 2 materiality filter (news mode only)")
    parser.add_argument("--history-path", help="Path to news history JSON (news mode only)")
    parser.add_argument("--time", help="Briefing time in HH:MM format (default 18:00)")
    parser.add_argument("--force", action="store_true", help="Force send regardless of time window")
    parser.add_argument("--dry-run", action="store_true", help="Print without side effects")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    config = load_config(args.config)

    # Override config from CLI args
    if args.topics:
        config["topics"] = [t.strip() for t in args.topics.split(",")]
    if args.min_confidence:
        config["min_confidence"] = args.min_confidence
    if args.max_per_topic:
        config["max_per_topic"] = args.max_per_topic
    if args.no_materiality_gate:
        config["materiality_gate"] = False
    if args.time:
        config["time"] = args.time

    log(f"Evening brief mode: {args.mode}", args.debug)
    log(f"Config: {json.dumps(config, indent=2)}", args.debug)

    # Build appropriate brief
    if args.mode == "news":
        brief = build_news_brief(config, debug=args.debug, history_path=args.history_path)
    else:
        # Market mode - initialize Kalshi if configured
        kalshi = None
        if config.get("kalshi", {}).get("enabled") and KalshiClient:
            try:
                api_key_id = config["kalshi"].get("api_key_id")
                private_key_file = config["kalshi"].get("private_key_file")

                if api_key_id and private_key_file:
                    base_url = "https://api.elections.kalshi.com/trade-api/v2"
                    sdk_config = KalshiConfiguration(host=base_url)
                    with open(private_key_file) as f:
                        sdk_config.private_key_pem = f.read()
                    sdk_config.api_key_id = api_key_id
                    kalshi = KalshiClient(sdk_config)
                    sdk_config.private_key_pem = None
                    log("Kalshi initialized", args.debug)
            except Exception as e:
                log(f"Kalshi init error: {e}", args.debug)

        brief = build_market_brief(config, kalshi=kalshi, debug=args.debug)

    print(brief)

    if args.debug:
        print("\n[DEBUG] Evening brief generated successfully", file=sys.stderr)


if __name__ == "__main__":
    main()
