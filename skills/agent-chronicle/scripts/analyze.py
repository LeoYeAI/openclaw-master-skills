#!/usr/bin/env python3
"""
Mood & Pattern Analytics for Agent Chronicle - v0.7.0

Reads diary entries and extracts mood/emotional keywords, builds a mood timeline,
identifies recurring topics, frustrations, wins, and outputs a markdown summary.

Usage:
    python3 scripts/analyze.py              # Analyze all entries
    python3 scripts/analyze.py --days 7     # Analyze last 7 days
    python3 scripts/analyze.py --days 30    # Analyze last 30 days
    python3 scripts/analyze.py --output mood-report.md  # Save to file
"""

import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_DIR / "config.json"
DEFAULT_DIARY_PATH = "memory/diary/"

# Mood/emotion keyword mappings
MOOD_KEYWORDS = {
    "joyful": {
        "emoji": "😄",
        "score": 5,
        "words": [
            "excited", "thrilled", "elated", "ecstatic", "delighted",
            "overjoyed", "euphoric", "fantastic", "amazing", "wonderful",
            "incredible", "brilliant", "celebration", "triumphant",
        ],
    },
    "happy": {
        "emoji": "😊",
        "score": 4,
        "words": [
            "happy", "satisfied", "pleased", "glad", "good", "great",
            "productive", "positive", "energized", "motivated", "proud",
            "accomplished", "rewarding", "fulfilling", "shipped", "launched",
            "win", "wins", "success", "breakthrough", "milestone",
        ],
    },
    "calm": {
        "emoji": "😌",
        "score": 3,
        "words": [
            "calm", "peaceful", "relaxed", "steady", "balanced", "quiet",
            "routine", "normal", "stable", "comfortable", "mundane",
            "ordinary", "rest", "uneventful",
        ],
    },
    "mixed": {
        "emoji": "😐",
        "score": 2,
        "words": [
            "mixed", "bittersweet", "conflicted", "uncertain", "ambivalent",
            "okay", "alright", "fine", "so-so", "mediocre",
        ],
    },
    "frustrated": {
        "emoji": "😤",
        "score": 1,
        "words": [
            "frustrated", "annoyed", "irritated", "stuck", "blocked",
            "struggling", "difficult", "challenging", "bug", "bugs",
            "broken", "failed", "failure", "error", "errors", "issue",
            "issues", "problem", "problems", "confusing", "tedious",
        ],
    },
    "sad": {
        "emoji": "😔",
        "score": 0,
        "words": [
            "sad", "disappointed", "down", "tired", "exhausted",
            "drained", "overwhelmed", "burned out", "burnout", "lonely",
            "discouraged", "demotivated", "rough",
        ],
    },
}

# Topic extraction patterns
TOPIC_PATTERNS = [
    # Technical topics
    r"\b(python|javascript|typescript|rust|go|java|ruby|swift|kotlin)\b",
    r"\b(api|apis|rest|graphql|websocket|grpc)\b",
    r"\b(docker|kubernetes|k8s|container|deployment|ci/cd|github actions)\b",
    r"\b(database|sql|postgres|mysql|redis|mongodb|sqlite)\b",
    r"\b(react|vue|svelte|angular|nextjs|nuxt)\b",
    r"\b(ai|llm|gpt|claude|model|prompt|embedding|vector)\b",
    r"\b(openclaw|clawhub|skill|skills|plugin|plugins)\b",
    r"\b(git|github|pr|pull request|merge|branch|commit)\b",
    r"\b(testing|test|tests|debug|debugging|refactor|refactoring)\b",
    r"\b(security|auth|authentication|authorization|encryption)\b",
    r"\b(performance|optimization|caching|latency|speed)\b",
    r"\b(documentation|docs|readme|changelog)\b",
]


def load_config():
    """Load configuration from config.json"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {"diary_path": DEFAULT_DIARY_PATH}


def get_workspace_root():
    """Find the workspace root (where memory/ lives)"""
    env_workspace = os.getenv("OPENCLAW_WORKSPACE") or os.getenv("AGENT_WORKSPACE")
    if env_workspace:
        env_path = Path(env_workspace)
        if (env_path / "memory").exists():
            return env_path

    candidates = [
        Path.cwd(),
        Path.home() / "clawd",
        Path.home() / ".openclaw" / "workspace",
    ]
    for path in candidates:
        if (path / "memory").exists():
            return path
    return Path.cwd()


def get_diary_path(config):
    """Get full path to diary directory"""
    workspace = get_workspace_root()
    return workspace / config.get("diary_path", DEFAULT_DIARY_PATH)


def load_entries(diary_path, days=None):
    """Load diary entries, optionally filtering by recent days"""
    entries = {}
    md_files = sorted(diary_path.glob("*.md"))

    # Filter to only dated diary entries (YYYY-MM-DD.md), skip special files
    dated_files = [
        f for f in md_files if re.match(r"\d{4}-\d{2}-\d{2}$", f.stem)
    ]

    if days is not None:
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.strftime("%Y-%m-%d")
        dated_files = [f for f in dated_files if f.stem >= cutoff_str]

    for f in dated_files:
        entries[f.stem] = f.read_text()

    return entries


def extract_section(content, section_name):
    """Extract a section's content from a diary entry"""
    pattern = rf"##\s*{re.escape(section_name)}.*?\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def analyze_mood(content):
    """Analyze mood of a single entry, returns (dominant_mood, score, keyword_counts)"""
    content_lower = content.lower()
    mood_counts = {}

    for mood, info in MOOD_KEYWORDS.items():
        count = 0
        for word in info["words"]:
            count += len(re.findall(r"\b" + re.escape(word) + r"\b", content_lower))
        if count > 0:
            mood_counts[mood] = count

    if not mood_counts:
        return "calm", 3, {}

    # Weight by section: emotional state section counts 3x
    emotional_section = extract_section(content, "Emotional State")
    if emotional_section:
        emo_lower = emotional_section.lower()
        for mood, info in MOOD_KEYWORDS.items():
            bonus = 0
            for word in info["words"]:
                bonus += len(re.findall(r"\b" + re.escape(word) + r"\b", emo_lower))
            if bonus > 0:
                mood_counts[mood] = mood_counts.get(mood, 0) + bonus * 2  # 2x bonus

    dominant = max(mood_counts, key=mood_counts.get)
    score = MOOD_KEYWORDS[dominant]["score"]

    return dominant, score, mood_counts


def extract_topics(content):
    """Extract topics mentioned in an entry"""
    content_lower = content.lower()
    topics = []

    for pattern in TOPIC_PATTERNS:
        matches = re.findall(pattern, content_lower)
        topics.extend(matches)

    return topics


def extract_wins(content):
    """Extract wins from an entry"""
    wins_section = extract_section(content, "Wins 🎉") or extract_section(content, "Wins")
    if not wins_section:
        return []

    wins = []
    for line in wins_section.split("\n"):
        line = line.strip()
        if line and line.startswith(("-", "*", "•")):
            win = re.sub(r"^[-*•]\s*", "", line).strip()
            if win and len(win) > 5:
                wins.append(win)
        elif line and not line.startswith("#"):
            # Paragraph-style wins - take first sentence
            sentences = re.split(r"[.!?]", line)
            if sentences and len(sentences[0].strip()) > 5:
                wins.append(sentences[0].strip())

    return wins


def extract_frustrations(content):
    """Extract frustrations from an entry"""
    frust_section = (
        extract_section(content, "Frustrations 😤")
        or extract_section(content, "Frustrations")
    )
    if not frust_section:
        return []

    frustrations = []
    for line in frust_section.split("\n"):
        line = line.strip()
        if line and line.startswith(("-", "*", "•")):
            frust = re.sub(r"^[-*•]\s*", "", line).strip()
            if frust and len(frust) > 5:
                frustrations.append(frust)
        elif line and not line.startswith("#"):
            sentences = re.split(r"[.!?]", line)
            if sentences and len(sentences[0].strip()) > 5:
                frustrations.append(sentences[0].strip())

    return frustrations


def build_sparkline(scores):
    """Build a text-based sparkline from mood scores (0-5)"""
    blocks = ["▁", "▂", "▃", "▅", "▆", "█"]
    return "".join(blocks[min(s, 5)] for s in scores)


def build_emoji_timeline(moods):
    """Build an emoji-based mood timeline"""
    return " ".join(MOOD_KEYWORDS.get(m, {}).get("emoji", "❓") for m in moods)


def generate_report(entries, days_label=None):
    """Generate a full mood & pattern analytics report"""
    if not entries:
        return "# Mood & Pattern Analytics\n\nNo diary entries found to analyze.\n"

    # Analyze all entries
    daily_moods = {}  # date -> (mood, score, counts)
    all_topics = Counter()
    all_wins = []
    all_frustrations = []

    for date_str in sorted(entries.keys()):
        content = entries[date_str]
        mood, score, counts = analyze_mood(content)
        daily_moods[date_str] = (mood, score, counts)

        topics = extract_topics(content)
        all_topics.update(topics)

        wins = extract_wins(content)
        all_wins.extend([(date_str, w) for w in wins])

        frustrations = extract_frustrations(content)
        all_frustrations.extend([(date_str, f) for f in frustrations])

    # Build report
    dates = sorted(daily_moods.keys())
    scores = [daily_moods[d][1] for d in dates]
    moods = [daily_moods[d][0] for d in dates]

    period = days_label or "all time"
    avg_score = sum(scores) / len(scores) if scores else 0
    avg_mood = (
        "joyful" if avg_score >= 4.5
        else "happy" if avg_score >= 3.5
        else "calm" if avg_score >= 2.5
        else "mixed" if avg_score >= 1.5
        else "frustrated" if avg_score >= 0.5
        else "sad"
    )
    avg_emoji = MOOD_KEYWORDS[avg_mood]["emoji"]

    # Mood distribution
    mood_dist = Counter(moods)

    report = []
    report.append(f"# 📊 Mood & Pattern Analytics")
    report.append(f"")
    report.append(f"**Period:** {period} ({len(entries)} entries)")
    report.append(f"**Average Mood:** {avg_emoji} {avg_mood} ({avg_score:.1f}/5)")
    report.append(f"")

    # Mood Timeline
    report.append(f"## 📈 Mood Timeline")
    report.append(f"")

    if len(dates) <= 30:
        # Show individual dates
        report.append(f"```")
        report.append(f"Sparkline: {build_sparkline(scores)}")
        report.append(f"```")
        report.append(f"")
        report.append(f"{build_emoji_timeline(moods)}")
        report.append(f"")

        for date_str in dates:
            mood, score, _ = daily_moods[date_str]
            emoji = MOOD_KEYWORDS[mood]["emoji"]
            bar = "█" * score + "░" * (5 - score)
            report.append(f"- `{date_str}` {emoji} {bar} {mood}")
    else:
        # Summarize by week for large datasets
        report.append(f"```")
        report.append(f"Sparkline: {build_sparkline(scores)}")
        report.append(f"```")
        report.append(f"")
        report.append(f"{build_emoji_timeline(moods)}")
        report.append(f"")

        # Weekly averages
        week_scores = {}
        for date_str, (mood, score, _) in daily_moods.items():
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                week_key = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
            except ValueError:
                continue
            week_scores.setdefault(week_key, []).append(score)

        report.append(f"### Weekly Averages")
        for week, week_s in sorted(week_scores.items()):
            avg = sum(week_s) / len(week_s)
            avg_m = (
                "joyful" if avg >= 4.5
                else "happy" if avg >= 3.5
                else "calm" if avg >= 2.5
                else "mixed" if avg >= 1.5
                else "frustrated" if avg >= 0.5
                else "sad"
            )
            emoji = MOOD_KEYWORDS[avg_m]["emoji"]
            report.append(f"- `{week}` {emoji} {avg:.1f}/5 ({len(week_s)} entries)")

    report.append(f"")

    # Mood Distribution
    report.append(f"## 🎭 Mood Distribution")
    report.append(f"")
    for mood_name in ["joyful", "happy", "calm", "mixed", "frustrated", "sad"]:
        count = mood_dist.get(mood_name, 0)
        if count > 0:
            pct = count / len(moods) * 100
            emoji = MOOD_KEYWORDS[mood_name]["emoji"]
            bar = "▓" * int(pct / 5) + "░" * (20 - int(pct / 5))
            report.append(f"- {emoji} **{mood_name}**: {bar} {count} ({pct:.0f}%)")
    report.append(f"")

    # Top Topics
    if all_topics:
        report.append(f"## 🏷️ Recurring Topics")
        report.append(f"")
        for topic, count in all_topics.most_common(15):
            report.append(f"- **{topic}** — mentioned {count} time{'s' if count > 1 else ''}")
        report.append(f"")

    # Top Wins
    if all_wins:
        report.append(f"## 🏆 Wins Compilation")
        report.append(f"")
        # Show most recent wins (up to 10)
        recent_wins = all_wins[-10:]
        for date_str, win in reversed(recent_wins):
            # Truncate long wins
            display_win = win[:120] + "..." if len(win) > 120 else win
            report.append(f"- `{date_str}` {display_win}")
        if len(all_wins) > 10:
            report.append(f"- *...and {len(all_wins) - 10} more wins*")
        report.append(f"")

    # Top Frustrations
    if all_frustrations:
        report.append(f"## 😤 Recurring Frustrations")
        report.append(f"")
        # Look for recurring themes in frustrations
        frust_words = Counter()
        for _, frust in all_frustrations:
            words = re.findall(r"\b[a-z]{4,}\b", frust.lower())
            frust_words.update(words)

        # Show recent frustrations
        recent_frust = all_frustrations[-8:]
        for date_str, frust in reversed(recent_frust):
            display_frust = frust[:120] + "..." if len(frust) > 120 else frust
            report.append(f"- `{date_str}` {display_frust}")
        if len(all_frustrations) > 8:
            report.append(f"- *...and {len(all_frustrations) - 8} more frustrations*")
        report.append(f"")

    # Insights
    report.append(f"## 💡 Insights")
    report.append(f"")

    # Trend detection
    if len(scores) >= 3:
        recent_avg = sum(scores[-3:]) / 3
        older_avg = sum(scores[:-3]) / max(len(scores) - 3, 1) if len(scores) > 3 else recent_avg
        if recent_avg > older_avg + 0.5:
            report.append(f"- 📈 **Upward trend** — mood has been improving recently")
        elif recent_avg < older_avg - 0.5:
            report.append(f"- 📉 **Downward trend** — mood has dipped recently")
        else:
            report.append(f"- ➡️ **Stable mood** — relatively consistent emotional state")

    # Best/worst days
    if scores:
        best_idx = scores.index(max(scores))
        worst_idx = scores.index(min(scores))
        best_date = dates[best_idx]
        worst_date = dates[worst_idx]
        best_emoji = MOOD_KEYWORDS[moods[best_idx]]["emoji"]
        worst_emoji = MOOD_KEYWORDS[moods[worst_idx]]["emoji"]
        report.append(f"- {best_emoji} **Best day:** {best_date}")
        report.append(f"- {worst_emoji} **Toughest day:** {worst_date}")

    # Win/frustration ratio
    if all_wins or all_frustrations:
        ratio = len(all_wins) / max(len(all_frustrations), 1)
        if ratio > 2:
            report.append(f"- 🎯 **Win ratio: {ratio:.1f}x** — significantly more wins than frustrations!")
        elif ratio > 1:
            report.append(f"- ⚖️ **Win ratio: {ratio:.1f}x** — slightly more wins than frustrations")
        else:
            report.append(f"- 🔧 **Win ratio: {ratio:.1f}x** — more frustrations than wins, consider what's blocking you")

    report.append(f"")
    report.append(f"---")
    report.append(f"*Generated by Agent Chronicle v0.7.0 on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Mood & Pattern Analytics for Agent Chronicle"
    )
    parser.add_argument(
        "--days", "-d", type=int, help="Analyze last N days (default: all)"
    )
    parser.add_argument(
        "--output", "-o", help="Save report to file (default: print to stdout)"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output raw analysis as JSON"
    )
    args = parser.parse_args()

    config = load_config()
    diary_path = get_diary_path(config)

    if not diary_path.exists():
        print(f"Diary path not found: {diary_path}")
        print("Run setup first or check config.json diary_path setting.")
        return

    entries = load_entries(diary_path, days=args.days)

    if not entries:
        period = f"last {args.days} days" if args.days else "all time"
        print(f"No diary entries found for {period} in {diary_path}")
        return

    days_label = f"last {args.days} days" if args.days else "all time"

    if args.json:
        # Raw JSON output for programmatic use
        results = {}
        for date_str in sorted(entries.keys()):
            mood, score, counts = analyze_mood(entries[date_str])
            topics = extract_topics(entries[date_str])
            results[date_str] = {
                "mood": mood,
                "score": score,
                "topics": topics,
                "wins": extract_wins(entries[date_str]),
                "frustrations": extract_frustrations(entries[date_str]),
            }
        print(json.dumps(results, indent=2))
        return

    report = generate_report(entries, days_label)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report)
        print(f"✓ Report saved to {output_path}")
    else:
        print(report)


if __name__ == "__main__":
    main()
