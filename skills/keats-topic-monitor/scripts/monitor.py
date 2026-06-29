#!/usr/bin/env python3
"""
Proactive Research Monitor

Checks topics due for monitoring, scores findings, and sends alerts.
Run via cron for automated monitoring.
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    load_config, load_state, save_state, get_settings,
    get_channel_config, save_finding, queue_alert, ALERTS_QUEUE
)
from importance_scorer import score_result


def hash_url(url: str) -> str:
    """Create hash of URL for deduplication."""
    return hashlib.md5(url.encode()).hexdigest()


def is_duplicate(url: str, state: Dict, dedup_hours: int = 72) -> bool:
    """Check if URL was recently alerted."""
    url_hash = hash_url(url)
    dedup_map = state.get("deduplication", {}).get("url_hash_map", {})
    
    if url_hash not in dedup_map:
        return False
    
    # Check if within deduplication window
    last_seen_str = dedup_map[url_hash]
    last_seen = datetime.fromisoformat(last_seen_str)
    age = datetime.now() - last_seen
    
    return age < timedelta(hours=dedup_hours)


def mark_as_seen(url: str, state: Dict):
    """Mark URL as seen in deduplication map."""
    url_hash = hash_url(url)
    if "deduplication" not in state:
        state["deduplication"] = {"url_hash_map": {}}
    
    state["deduplication"]["url_hash_map"][url_hash] = datetime.now().isoformat()


def search_topic(topic: Dict, dry_run: bool = False, verbose: bool = False) -> List[Dict]:
    """
    Search for topic using web-search-plus (Serper/Tavily/Exa).
    
    Uses the web-search-plus skill for multi-provider search with better
    results than the built-in Brave search.
    """
    query = topic.get("query", "")
    
    if not query:
        print("⚠️ No query specified for topic", file=sys.stderr)
        return []
    
    # Use web-search-plus skill (preferred over built-in Brave)
    web_search_plus = Path(os.environ.get("WEB_SEARCH_PLUS_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "web-search-plus", "scripts", "search.py")))
    
    if web_search_plus.exists():
        import subprocess
        import re
        try:
            # Sanitize query: strip control chars, limit length
            safe_query = re.sub(r'[\x00-\x1f\x7f]', '', query)[:500]
            
            if verbose:
                print(f"   🔍 Searching via web-search-plus: {safe_query}")
            
            # Call web-search-plus (outputs JSON by default)
            # Using list args (not shell=True) prevents shell injection
            result = subprocess.run(
                [
                    "python3", str(web_search_plus),
                    "--query", safe_query,
                    "--max-results", "5"
                ],
                capture_output=True,
                text=True,
                timeout=45,  # Increased timeout for API calls
                env={k: v for k, v in os.environ.items() if k in (
                    "PATH", "HOME", "LANG", "TERM",
                    "SERPER_API_KEY", "TAVILY_API_KEY", "EXA_API_KEY",
                    "YOU_API_KEY", "SEARXNG_INSTANCE_URL", "WSP_CACHE_DIR"
                )}  # Only pass search-relevant env vars
            )
            
            if result.returncode == 0:
                # Parse JSON output
                try:
                    # web-search-plus might output additional info before JSON
                    stdout = result.stdout.strip()
                    # Find JSON in output (might have status messages before)
                    json_start = stdout.find('{')
                    if json_start >= 0:
                        json_str = stdout[json_start:]
                        data = json.loads(json_str)
                        results = data.get("results", [])
                        
                        if verbose:
                            provider = data.get("provider", "unknown")
                            print(f"   ✅ Got {len(results)} results from {provider}")
                        
                        return results
                except json.JSONDecodeError as e:
                    if verbose:
                        print(f"   ⚠️ Failed to parse search results: {e}", file=sys.stderr)
                        print(f"   Raw output: {result.stdout[:200]}", file=sys.stderr)
            else:
                if verbose:
                    print(f"   ⚠️ web-search-plus returned code {result.returncode}", file=sys.stderr)
                    if result.stderr:
                        print(f"   Stderr: {result.stderr[:200]}", file=sys.stderr)
                        
        except subprocess.TimeoutExpired:
            print(f"⚠️ web-search-plus timed out for query: {query}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ web-search-plus failed: {e}", file=sys.stderr)
    else:
        print(f"⚠️ web-search-plus not found at {web_search_plus}", file=sys.stderr)
    
    # Fallback: Return mock results for dry-run testing only
    if dry_run:
        if verbose:
            print(f"   ℹ️ Using mock results for dry-run")
        return [
            {
                "title": f"[Mock] Result for: {query}",
                "url": f"https://example.com/mock-{hashlib.md5(query.encode()).hexdigest()[:8]}",
                "snippet": f"This is a mock/test result for query: {query}. Run without --dry-run to use real search.",
                "published_date": datetime.now().isoformat()
            }
        ]
    
    return []


def should_check_topic(topic: Dict, state: Dict, force: bool = False) -> bool:
    """Determine if topic should be checked now."""
    if force:
        return True
    
    topic_id = topic.get("id")
    frequency = topic.get("frequency", "daily")
    
    # Get last check time
    topic_state = state.get("topics", {}).get(topic_id, {})
    last_check_str = topic_state.get("last_check")
    
    if not last_check_str:
        return True  # Never checked
    
    last_check = datetime.fromisoformat(last_check_str)
    now = datetime.now()
    
    # Check frequency
    if frequency == "hourly":
        return (now - last_check) >= timedelta(hours=1)
    elif frequency == "daily":
        return (now - last_check) >= timedelta(days=1)
    elif frequency == "weekly":
        return (now - last_check) >= timedelta(weeks=1)
    
    return False


def check_rate_limits(topic: Dict, state: Dict, settings: Dict) -> bool:
    """Check if we've hit rate limits."""
    topic_id = topic.get("id")
    max_per_day = settings.get("max_alerts_per_day", 5)
    max_per_topic_per_day = settings.get("max_alerts_per_topic_per_day", 2)
    
    topic_state = state.get("topics", {}).get(topic_id, {})
    alerts_today = topic_state.get("alerts_today", 0)
    
    # Check topic limit
    if alerts_today >= max_per_topic_per_day:
        return False
    
    # Check global limit (count across all topics)
    total_alerts_today = sum(
        s.get("alerts_today", 0) 
        for s in state.get("topics", {}).values()
    )
    
    if total_alerts_today >= max_per_day:
        return False
    
    return True


def send_alert(topic: Dict, result: Dict, priority: str, score: float, reason: str, dry_run: bool = False):
    """
    Send alert via configured channels.
    
    For Telegram: Queues alert for delivery by OpenClaw agent, then outputs
    structured JSON that the agent can parse and send via message tool.
    """
    channels = topic.get("channels", [])
    
    # Build formatted message
    emoji_map = {"high": "🔥", "medium": "📌", "low": "📝"}
    emoji = emoji_map.get(priority, "📌")
    
    topic_name = topic.get("name", "Research Alert")
    topic_emoji = topic.get("emoji", "🔍")
    context = topic.get("context", "")
    
    # Build nice formatted message
    lines = []
    lines.append(f"{emoji} **{topic_name}** {topic_emoji}")
    lines.append("")
    lines.append(f"**{result.get('title', 'Untitled')}**")
    lines.append("")
    
    snippet = result.get('snippet', '')
    if snippet:
        # Truncate long snippets
        if len(snippet) > 300:
            snippet = snippet[:297] + "..."
        lines.append(snippet)
        lines.append("")
    
    if context:
        lines.append(f"💡 _Context: {context}_")
        lines.append("")
    
    lines.append(f"🔗 {result.get('url', '')}")
    lines.append("")
    lines.append(f"📊 _Score: {score:.2f} | {reason}_")
    
    message = "\n".join(lines)
    
    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN - Would send alert:")
        print(f"Channels: {', '.join(channels)}")
        print(f"Priority: {priority.upper()}")
        print(f"\n{message}")
        print(f"{'='*60}\n")
        return None
    
    # Queue alert for each channel
    alert_ids = []
    for channel in channels:
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "priority": priority,
            "channel": channel,
            "topic_id": topic.get("id"),
            "topic_name": topic_name,
            "title": result.get("title", ""),
            "snippet": result.get("snippet", ""),
            "url": result.get("url", ""),
            "score": score,
            "reason": reason,
            "message": message,  # Pre-formatted message
            "context": context
        }
        
        alert_id = queue_alert(alert_data)
        alert_ids.append(alert_id)
        
        # Output structured alert for agent consumption
        print(f"📢 ALERT_QUEUED: {json.dumps({'id': alert_id, 'channel': channel, 'priority': priority, 'topic': topic_name})}")
    
    return alert_ids


def format_alert_for_telegram(alert: Dict) -> str:
    """Format an alert for Telegram delivery."""
    if alert.get("message"):
        return alert["message"]
    
    # Fallback formatting if no pre-formatted message
    emoji_map = {"high": "🔥", "medium": "📌", "low": "📝"}
    emoji = emoji_map.get(alert.get("priority", "medium"), "📌")
    
    lines = [
        f"{emoji} **{alert.get('topic_name', 'Alert')}**",
        "",
        f"**{alert.get('title', 'Untitled')}**",
        "",
    ]
    
    if alert.get("snippet"):
        lines.append(alert["snippet"][:300])
        lines.append("")
    
    if alert.get("url"):
        lines.append(f"🔗 {alert['url']}")
        lines.append("")
    
    lines.append(f"📊 _Score: {alert.get('score', 0):.2f}_")
    
    return "\n".join(lines)


def send_telegram(message: str, priority: str):
    """
    Send via Telegram using OpenClaw message tool.
    
    This function is called when processing the alerts queue.
    The actual sending is done by the OpenClaw agent using the message tool.
    """
    # This is now a helper that outputs the alert for agent processing
    # The actual message tool call happens via the agent
    print(f"📱 [TELEGRAM/{priority.upper()}] Alert ready for delivery ({len(message)} chars)")
    
    # Output in a format the agent can parse
    alert_output = {
        "action": "send_telegram",
        "priority": priority,
        "message": message,
        "target": os.environ.get("TOPIC_MONITOR_TELEGRAM_ID", ""),
        "channel": "telegram"
    }
    print(f"TELEGRAM_ALERT: {json.dumps(alert_output)}")


def send_discord(message: str, priority: str):
    """Output Discord alert as JSON for the agent to send via message tool."""
    alert_output = {
        "message": message,
        "priority": priority,
        "channel": "discord"
    }
    print(f"DISCORD_ALERT: {json.dumps(alert_output)}")
    return True


def send_email(message: str, priority: str, subject: str):
    """Send via email (placeholder - would need SMTP config)."""
    print(f"📧 [EMAIL] {priority.upper()}: {subject}")
    # TODO: Implement actual email sending via SMTP or SendGrid
    return False


def monitor_topic(topic: Dict, state: Dict, settings: Dict, dry_run: bool = False, verbose: bool = False):
    """Monitor a single topic."""
    topic_id = topic.get("id")
    topic_name = topic.get("name")
    
    if verbose:
        print(f"\n🔍 Checking topic: {topic_name} ({topic_id})")
    
    # Search using web-search-plus
    results = search_topic(topic, dry_run=dry_run, verbose=verbose)
    
    if verbose:
        print(f"   Found {len(results)} results")
    
    # Score and filter
    dedup_hours = settings.get("deduplication_window_hours", 72)
    high_priority = []
    medium_priority = []
    
    for result in results:
        url = result.get("url", "")
        
        # Check deduplication
        if is_duplicate(url, state, dedup_hours):
            if verbose:
                print(f"   ⏭️  Skipping duplicate: {url}")
            continue
        
        # Score
        priority, score, reason = score_result(result, topic, settings)
        
        if verbose:
            print(f"   {priority.upper():6} ({score:.2f}) - {result.get('title', '')[:50]}...")
        
        # Categorize
        if priority == "high":
            high_priority.append((result, score, reason))
        elif priority == "medium":
            medium_priority.append((result, score, reason))
        
        # Mark as seen
        mark_as_seen(url, state)
    
    # Send high priority alerts
    for result, score, reason in high_priority:
        if check_rate_limits(topic, state, settings):
            send_alert(topic, result, "high", score, reason, dry_run=dry_run)
            
            # Increment alert counter
            if not dry_run:
                if "topics" not in state:
                    state["topics"] = {}
                if topic_id not in state["topics"]:
                    state["topics"][topic_id] = {}
                
                state["topics"][topic_id]["alerts_today"] = \
                    state["topics"][topic_id].get("alerts_today", 0) + 1
        else:
            if verbose:
                print(f"   ⚠️ Rate limit reached, skipping alert")
    
    # Save medium priority to findings
    date_str = datetime.now().strftime("%Y-%m-%d")
    for result, score, reason in medium_priority:
        if not dry_run:
            save_finding(topic_id, date_str, {
                "result": result,
                "score": score,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
        
        if verbose:
            print(f"   💾 Saved to digest: {result.get('title', '')[:50]}...")
    
    # Update topic state
    if not dry_run:
        if "topics" not in state:
            state["topics"] = {}
        if topic_id not in state["topics"]:
            state["topics"][topic_id] = {}
        
        state["topics"][topic_id]["last_check"] = datetime.now().isoformat()
        state["topics"][topic_id]["last_results_count"] = len(results)
        state["topics"][topic_id]["findings_count"] = \
            state["topics"][topic_id].get("findings_count", 0) + len(medium_priority)


def main():
    parser = argparse.ArgumentParser(description="Monitor research topics")
    parser.add_argument("--dry-run", action="store_true", help="Don't send alerts or save state")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--topic", help="Check specific topic by ID")
    parser.add_argument("--force", action="store_true", help="Force check even if not due")
    parser.add_argument("--frequency", choices=["hourly", "daily", "weekly"], 
                       help="Only check topics with this frequency")
    
    args = parser.parse_args()
    
    # Load config and state
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    
    state = load_state()
    settings = get_settings()
    topics = config.get("topics", [])
    
    if not topics:
        print("⚠️ No topics configured", file=sys.stderr)
        sys.exit(0)
    
    # Filter topics
    topics_to_check = []
    
    for topic in topics:
        # Filter by specific topic
        if args.topic and topic.get("id") != args.topic:
            continue
        
        # Filter by frequency
        if args.frequency and topic.get("frequency") != args.frequency:
            continue
        
        # Check if due
        if should_check_topic(topic, state, force=args.force):
            topics_to_check.append(topic)
    
    if not topics_to_check:
        if args.verbose:
            print("✅ No topics due for checking")
        sys.exit(0)
    
    print(f"🔍 Monitoring {len(topics_to_check)} topic(s)...")
    
    # Monitor each topic
    for topic in topics_to_check:
        try:
            monitor_topic(topic, state, settings, dry_run=args.dry_run, verbose=args.verbose)
        except Exception as e:
            print(f"❌ Error monitoring {topic.get('name')}: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    # Save state
    if not args.dry_run:
        save_state(state)
        print("✅ State saved")
    
    print("✅ Monitoring complete")


if __name__ == "__main__":
    main()
