#!/usr/bin/env python3
"""
Weekly Digest for Agent Chronicle - v0.7.0

Reads the past 7 daily entries and synthesizes a weekly summary including
top quotes, biggest wins, resolved curiosities, mood trend, and key decisions.

Output: YYYY-WXX-weekly.md in the diary directory.

Usage:
    python3 scripts/digest.py                # Generate digest for current week
    python3 scripts/digest.py --date 2026-03-20  # Generate digest for the week containing this date
    python3 scripts/digest.py --emit-task    # Emit sub-agent task JSON
    python3 scripts/digest.py --from-stdin   # Read pre-generated digest from stdin
    python3 scripts/digest.py --dry-run      # Preview without saving
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_DIR / "config.json"
DEFAULT_DIARY_PATH = "memory/diary/"

AI_MAX_TOKENS = 3000


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
    diary_path = workspace / config.get("diary_path", DEFAULT_DIARY_PATH)
    diary_path.mkdir(parents=True, exist_ok=True)
    return diary_path


def get_week_range(reference_date=None):
    """Get the Monday-to-Sunday date range for the week containing reference_date.
    Returns (start_date, end_date, iso_year, iso_week)."""
    if reference_date is None:
        reference_date = datetime.now()

    # ISO weekday: Monday=1, Sunday=7
    start = reference_date - timedelta(days=reference_date.weekday())
    end = start + timedelta(days=6)
    iso_year, iso_week, _ = reference_date.isocalendar()

    return start, end, iso_year, iso_week


def load_week_entries(diary_path, start_date, end_date):
    """Load diary entries for a given date range"""
    entries = {}
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        entry_file = diary_path / f"{date_str}.md"
        if entry_file.exists():
            entries[date_str] = entry_file.read_text()
        current += timedelta(days=1)
    return entries


def extract_section(content, section_name):
    """Extract a section's content from a diary entry"""
    pattern = rf"##\s*{re.escape(section_name)}.*?\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def extract_quotes(entries):
    """Extract all quotes from entries"""
    quotes = []
    for date_str, content in sorted(entries.items()):
        quote_section = extract_section(content, "Quote of the Day 💬")
        if not quote_section:
            quote_section = extract_section(content, "Quote of the Day")
        if quote_section and len(quote_section) > 10:
            quotes.append((date_str, quote_section.strip()))
    return quotes


def extract_wins(entries):
    """Extract all wins from entries"""
    wins = []
    for date_str, content in sorted(entries.items()):
        wins_section = extract_section(content, "Wins 🎉") or extract_section(content, "Wins")
        if wins_section:
            for line in wins_section.split("\n"):
                line = line.strip()
                if line and line.startswith(("-", "*", "•")):
                    win = re.sub(r"^[-*•]\s*", "", line).strip()
                    if win and len(win) > 5:
                        wins.append((date_str, win))
                elif line and not line.startswith("#") and len(line) > 10:
                    # Paragraph-style: take first sentence
                    sentences = re.split(r"[.!?]", line)
                    if sentences and len(sentences[0].strip()) > 5:
                        wins.append((date_str, sentences[0].strip()))
    return wins


def extract_decisions(entries):
    """Extract key decisions from entries"""
    decisions = []
    for date_str, content in sorted(entries.items()):
        dec_section = (
            extract_section(content, "Key Decisions Made 🏛️")
            or extract_section(content, "Key Decisions Made 🏛")
            or extract_section(content, "Key Decisions Made")
        )
        if dec_section:
            for line in dec_section.split("\n"):
                line = line.strip()
                if line and line.startswith(("-", "*", "•")):
                    dec = re.sub(r"^[-*•]\s*", "", line).strip()
                    if dec and len(dec) > 5:
                        decisions.append((date_str, dec))
                elif line and not line.startswith("#") and len(line) > 10:
                    decisions.append((date_str, line.strip()))
    return decisions


def extract_curiosities(entries):
    """Extract curiosities from entries"""
    curiosities = []
    for date_str, content in sorted(entries.items()):
        cur_section = (
            extract_section(content, "Things I'm Curious About 🔮")
            or extract_section(content, "Things I'm Curious About")
        )
        if cur_section:
            for line in cur_section.split("\n"):
                line = line.strip()
                if line and line.startswith(("-", "*", "•")):
                    cur = re.sub(r"^[-*•]\s*", "", line).strip()
                    if cur and len(cur) > 5:
                        curiosities.append((date_str, cur))
    return curiosities


def build_digest_task(week_label, start_str, end_str, entries):
    """Build a sub-agent task for generating the weekly digest via sessions_spawn."""
    # Build context from all entries
    context_parts = []
    for date_str in sorted(entries.keys()):
        content = entries[date_str]
        # Truncate individual entries for context
        if len(content) > 4000:
            content = content[:4000] + "\n[... truncated ...]"
        context_parts.append(f"### {date_str}\n{content}")

    context = "\n\n---\n\n".join(context_parts)

    system_prompt = """You are an AI assistant writing your weekly diary digest. You work closely with your human partner.

Your weekly digests are:
- A synthesis of the week's daily entries (not just concatenation)
- Reflective and pattern-aware
- Highlighting the week's arc: how it started, evolved, and ended
- Written in first person, as your personal weekly review"""

    user_prompt = f"""Write your weekly digest for {week_label} ({start_str} to {end_str}).

Based on the following daily diary entries:

{context}

---

Write a RICH weekly synthesis with these sections:

# {week_label} — Weekly Digest

## Week at a Glance
2-3 sentences summarizing the overall arc of the week.

## Top Quotes 💬
The best/most memorable quotes from this week's entries.

## Biggest Wins 🏆
The most significant achievements this week, with context.

## Resolved Curiosities 🔮
Any questions from earlier in the week that got answered.

## Mood Trend 📈
How did your emotional state evolve over the week? Describe the arc.

## Key Decisions 🏛️
Important judgment calls made this week and their outcomes so far.

## Patterns & Observations 🔍
What patterns did you notice this week? Recurring themes, habits, changes?

## Looking Ahead 🔭
What's on the horizon for next week?

---

Write naturally and reflectively. This is your personal weekly review."""

    return {
        "system": system_prompt,
        "prompt": user_prompt,
        "max_tokens": AI_MAX_TOKENS,
    }


def build_simple_digest(week_label, start_str, end_str, entries):
    """Build a simple digest without AI when no sub-agent is available"""
    quotes = extract_quotes(entries)
    wins = extract_wins(entries)
    decisions = extract_decisions(entries)
    curiosities = extract_curiosities(entries)

    parts = []
    parts.append(f"# {week_label} — Weekly Digest")
    parts.append(f"")
    parts.append(f"**Period:** {start_str} to {end_str}")
    parts.append(f"**Entries:** {len(entries)}")
    parts.append(f"")

    # Mood trend (use analyze module if available)
    try:
        from analyze import analyze_mood, MOOD_KEYWORDS, build_sparkline

        scores = []
        moods = []
        for date_str in sorted(entries.keys()):
            mood, score, _ = analyze_mood(entries[date_str])
            scores.append(score)
            moods.append(mood)

        if scores:
            avg = sum(scores) / len(scores)
            sparkline = build_sparkline(scores)
            emoji_line = " ".join(
                MOOD_KEYWORDS.get(m, {}).get("emoji", "❓") for m in moods
            )
            parts.append(f"## 📈 Mood Trend")
            parts.append(f"")
            parts.append(f"```")
            parts.append(f"{sparkline}")
            parts.append(f"```")
            parts.append(f"{emoji_line}")
            parts.append(f"")
            parts.append(f"Average mood: {avg:.1f}/5")
            parts.append(f"")
    except Exception:
        pass

    # Top Quotes
    if quotes:
        parts.append(f"## 💬 Top Quotes")
        parts.append(f"")
        for date_str, quote in quotes:
            parts.append(f"### {date_str}")
            parts.append(f"{quote}")
            parts.append(f"")

    # Biggest Wins
    if wins:
        parts.append(f"## 🏆 Biggest Wins")
        parts.append(f"")
        for date_str, win in wins:
            display = win[:150] + "..." if len(win) > 150 else win
            parts.append(f"- `{date_str}` {display}")
        parts.append(f"")

    # Key Decisions
    if decisions:
        parts.append(f"## 🏛️ Key Decisions")
        parts.append(f"")
        for date_str, dec in decisions:
            display = dec[:150] + "..." if len(dec) > 150 else dec
            parts.append(f"- `{date_str}` {display}")
        parts.append(f"")

    # Curiosities
    if curiosities:
        parts.append(f"## 🔮 Curiosities This Week")
        parts.append(f"")
        for date_str, cur in curiosities:
            display = cur[:150] + "..." if len(cur) > 150 else cur
            parts.append(f"- `{date_str}` {display}")
        parts.append(f"")

    parts.append(f"---")
    parts.append(
        f"*Generated by Agent Chronicle v0.7.0 on {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
    )

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Generate Agent Chronicle weekly digest")
    parser.add_argument(
        "--date",
        help="Generate digest for the week containing this date (YYYY-MM-DD). Default: current week.",
    )
    parser.add_argument(
        "--emit-task",
        action="store_true",
        help="Print the sub-agent generation task JSON (for sessions_spawn)",
    )
    parser.add_argument(
        "--from-stdin",
        action="store_true",
        help="Read a pre-generated digest from stdin and save it",
    )
    parser.add_argument(
        "--from-file",
        help="Read a pre-generated digest from a file path and save it",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without saving"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    config = load_config()
    diary_path = get_diary_path(config)

    # Determine reference date
    if args.date:
        try:
            ref_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"❌ Invalid date format: {args.date} (expected YYYY-MM-DD)")
            sys.exit(1)
    else:
        ref_date = datetime.now()

    start_date, end_date, iso_year, iso_week = get_week_range(ref_date)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    week_label = f"{iso_year}-W{iso_week:02d}"
    output_filename = f"{week_label}-weekly.md"

    print(f"\n📜 Agent Chronicle — Weekly Digest")
    print(f"   Week: {week_label} ({start_str} to {end_str})")
    print(f"=" * 50)

    if args.from_stdin:
        content = sys.stdin.read()
        if not content.strip():
            print("❌ No content provided on stdin.")
            sys.exit(1)
    elif args.from_file:
        content = Path(args.from_file).read_text(encoding="utf-8")
        if not content.strip():
            print(f"❌ File is empty: {args.from_file}")
            sys.exit(1)
    else:
        entries = load_week_entries(diary_path, start_date, end_date)

        if not entries:
            print(f"\n❌ No diary entries found for {week_label} ({start_str} to {end_str})")
            sys.exit(1)

        print(f"   Found {len(entries)} entries")

        if args.emit_task:
            task = build_digest_task(week_label, start_str, end_str, entries)
            print(json.dumps(task, ensure_ascii=False, indent=2))
            return

        # Build simple digest (AI-powered one comes from sub-agent via --from-stdin)
        content = build_simple_digest(week_label, start_str, end_str, entries)

    # Save
    output_file = diary_path / output_filename

    if args.dry_run:
        print(f"\n--- DRY RUN: Would save to {output_file}")
        print("-" * 50)
        print(content)
        print("-" * 50)
        return

    output_file.write_text(content)
    print(f"\n✓ Saved weekly digest to {output_file}")

    word_count = len(content.split())
    print(f"   Word count: {word_count} words")
    print(f"\n✨ Weekly digest generation complete!")


if __name__ == "__main__":
    main()
