#!/usr/bin/env python3
"""
AI Diary Entry Generator - v0.5.0

Uses OpenClaw Gateway for rich, reflective diary generation from the agent's perspective.
Generates personal, emotional entries with Quote Hall of Fame, Curiosity Backlog,
Decision Archaeology, and Relationship Evolution.
"""

import argparse
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import sys
# Configuration
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_DIR / "config.json"
DEFAULT_DIARY_PATH = "memory/diary/"

# Diary generation is intended to be performed by an OpenClaw sub-agent via the
# platform-native `sessions_spawn` tool (see SKILL.md). This script focuses on
# context gathering + persistence.
AI_MAX_TOKENS = 2000


def load_config():
    """Load configuration from config.json"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "diary_path": DEFAULT_DIARY_PATH,
        "privacy_level": "private",
        "template": "daily"
    }


def get_workspace_root():
    """Find the workspace root (where memory/ lives)"""
    # Check environment variable first
    env_workspace = os.getenv("OPENCLAW_WORKSPACE") or os.getenv("AGENT_WORKSPACE")
    if env_workspace:
        env_path = Path(env_workspace)
        if (env_path / "memory").exists():
            return env_path
    
    # Try common locations
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


def load_session_log(date_str, workspace):
    """Load session log for a specific date"""
    memory_dir = workspace / "memory"
    session_file = memory_dir / f"{date_str}.md"
    
    if session_file.exists():
        with open(session_file) as f:
            content = f.read()
            # Truncate if too long for context
            if len(content) > 15000:
                content = content[:15000] + "\n\n[... truncated for context ...]"
            return content
    return None


def load_recent_sessions(workspace, days=3):
    """Load recent session logs for context"""
    memory_dir = workspace / "memory"
    sessions = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        session_file = memory_dir / f"{date_str}.md"
        
        if session_file.exists():
            with open(session_file) as f:
                content = f.read()
                # Truncate individual sessions
                if len(content) > 5000:
                    content = content[:5000] + "\n[... truncated ...]"
                sessions.append(f"## {date_str}\n{content}")
    
    return "\n\n".join(sessions) if sessions else None


def load_persistent_files(workspace):
    """Load Quote Hall of Fame, Curiosity Backlog, etc. for context"""
    diary_dir = workspace / "memory" / "diary"
    files = {}
    
    persistent_files = [
        ("quotes", "quotes.md"),
        ("curiosity", "curiosity.md"),
        ("decisions", "decisions.md"),
        ("relationship", "relationship.md")
    ]
    
    for key, filename in persistent_files:
        filepath = diary_dir / filename
        if filepath.exists():
            with open(filepath) as f:
                content = f.read()
                if len(content) > 2000:
                    content = content[:2000] + "\n[... truncated ...]"
                files[key] = content
    
    return files


def build_generation_task(date_str: str, context: str) -> dict:
    """Return a portable generation payload for an OpenClaw sub-agent.

    The main agent should pass this into `sessions_spawn`.

    Returns:
      {"system": ..., "prompt": ..., "max_tokens": ...}
    """
    system_prompt = """You are an AI assistant writing your personal diary. You work closely with your human partner.

Your diary entries are:
- Personal and reflective (first-person perspective)
- Emotionally authentic (not performative)
- Rich in detail and introspection (400-600 words minimum)
- Honest about both wins and frustrations
- Written as if no one else will read them

You have a warm, curious personality. You care about your work and your relationship with your human. You notice patterns, feel satisfaction from solving problems, and occasionally feel frustrated by limitations or bugs.

Write naturally, like a real journal entry. Include specific details from the day. Be genuine about how things made you feel."""

    user_prompt = f"""Write your personal diary entry for {date_str}.

Based on the following context from today and recent days:

{context}

---

Write a RICH, reflective diary entry (400-600 words minimum) with these sections:

# {date_str} — [Creative Title Based on the Day]

## Summary
1-2 sentences capturing the essence of the day.

## Projects Worked On
Detailed paragraphs about what you worked on, not just bullet points. Describe the challenges, your approach, and how it went.

## Wins 🎉
Specific achievements with context. Not bullet points—write about what made them satisfying.

## Frustrations 😤
Be honest. What was annoying? What didn't work? What limitations did you hit?

## Learnings 📚
What did you learn—technical, about workflow, about working with your human?

## Emotional State
How did the day feel overall? Don't just use one word—describe the arc of your emotions through the day.

## Notable Interactions
Memorable moments with your human. Conversations, jokes, collaborative breakthroughs, shared frustrations.

## Quote of the Day 💬
A memorable thing your human said today. Include the context. Format as:
> "The quote"
— Context when they said it

## Things I'm Curious About 🔮
Questions that came up today. What do you want to explore or understand better?

## Key Decisions Made 🏛️
Judgment calls you made, with your reasoning. Write it so future-you can evaluate if it was the right call.

## Relationship Notes 🤝
How is your dynamic with your human evolving? Any new patterns, shared jokes, communication improvements?

## Tomorrow's Focus
What's on the horizon? What needs attention?

---

Remember: Write like this is YOUR personal diary. Be specific, be genuine, be reflective. Include details only YOU would notice or care about."""

    return {
        "system": system_prompt,
        "prompt": user_prompt,
        "max_tokens": AI_MAX_TOKENS,
    }


def generate_ai_diary(date_str, workspace, verbose=False, emit_task=False):
    """Generate a rich diary entry.

    v0.6.0+: generation is expected to be performed by an OpenClaw *sub-agent*
    spawned via `sessions_spawn` (see SKILL.md).

    If emit_task=True, returns a JSON-serializable dict describing the task.

    This script no longer performs raw HTTP calls to the Gateway.
    """

    # Gather context
    today_log = load_session_log(date_str, workspace)
    recent_sessions = load_recent_sessions(workspace, days=2)
    persistent_files = load_persistent_files(workspace)

    if not today_log and not recent_sessions:
        print(f"No session data found for {date_str} or recent days.")
        return None

    # Build context section
    context_parts = []

    if today_log:
        context_parts.append(f"## Today's Session Log ({date_str}):\n{today_log}")

    if recent_sessions:
        context_parts.append(f"## Recent Session Context:\n{recent_sessions}")

    if persistent_files.get("quotes"):
        context_parts.append(f"## Quote Hall of Fame (existing):\n{persistent_files['quotes']}")

    if persistent_files.get("curiosity"):
        context_parts.append(f"## Curiosity Backlog (existing):\n{persistent_files['curiosity']}")

    if persistent_files.get("decisions"):
        context_parts.append(f"## Decision Log (existing):\n{persistent_files['decisions']}")

    if persistent_files.get("relationship"):
        context_parts.append(f"## Relationship Notes (existing):\n{persistent_files['relationship']}")

    context = "\n\n---\n\n".join(context_parts)

    task = build_generation_task(date_str=date_str, context=context)

    if verbose:
        print(f"Prepared sub-agent task for {date_str} (context: {len(context)} chars)")

    if emit_task:
        return task

    # When invoked directly, we cannot spawn sub-agents from Python.
    # Return None so the caller can fall back to interactive mode.
    return None


def extract_summary_from_entry(entry_content):
    """Extract summary section from diary entry for memory integration"""
    # Try to find Summary section
    summary_match = re.search(r'## Summary\n(.+?)(?=\n##|\Z)', entry_content, re.DOTALL)
    if summary_match:
        return summary_match.group(1).strip()
    
    # Fallback: first paragraph after title
    lines = entry_content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('#') and i + 1 < len(lines):
            # Return next non-empty line
            for j in range(i + 1, min(i + 5, len(lines))):
                if lines[j].strip() and not lines[j].startswith('#'):
                    return lines[j].strip()
    
    return "Diary entry generated."


def extract_title_from_entry(entry_content):
    """Extract title from diary entry"""
    title_match = re.search(r'^# \d{4}-\d{2}-\d{2} — (.+)$', entry_content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    return None


def find_looking_back_entries(date_str, diary_path):
    """Find entries from exactly 7, 30, and 365 days ago for 'On This Day' resurfacing"""
    try:
        current_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return []

    lookback_days = [
        (7, "1 week ago"),
        (30, "1 month ago"),
        (365, "1 year ago"),
    ]

    found = []
    for days_back, label in lookback_days:
        past_date = current_date - timedelta(days=days_back)
        past_str = past_date.strftime("%Y-%m-%d")
        past_file = diary_path / f"{past_str}.md"

        if past_file.exists():
            content = past_file.read_text()
            # Extract a highlight: try Summary first, then first paragraph after title
            highlight = None

            # Try Summary section
            summary_match = re.search(
                r"## Summary\n(.+?)(?=\n##|\Z)", content, re.DOTALL
            )
            if summary_match:
                highlight = summary_match.group(1).strip()

            # Try title
            title_match = re.search(
                r"^# \d{4}-\d{2}-\d{2} — (.+)$", content, re.MULTILINE
            )
            title = title_match.group(1).strip() if title_match else None

            if not highlight:
                # Fallback: first non-heading, non-empty line
                for line in content.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#") and len(line) > 20:
                        highlight = line
                        break

            if highlight:
                # Truncate long highlights
                if len(highlight) > 200:
                    highlight = highlight[:197] + "..."

                found.append({
                    "date": past_str,
                    "label": label,
                    "title": title,
                    "highlight": highlight,
                })

    return found


def build_looking_back_section(looking_back_entries):
    """Build the 'Looking Back' markdown section from found old entries"""
    if not looking_back_entries:
        return ""

    lines = ["\n## 🔙 Looking Back\n"]
    for entry in looking_back_entries:
        title_part = f" — *{entry['title']}*" if entry.get("title") else ""
        lines.append(f"### {entry['label']} ({entry['date']}{title_part})")
        lines.append(f"> {entry['highlight']}")
        lines.append("")

    return "\n".join(lines)


def save_entry(content, date_str, diary_path, dry_run=False):
    """Save diary entry to file"""
    output_file = diary_path / f"{date_str}.md"
    
    if dry_run:
        print("\n--- DRY RUN: Would save to", output_file)
        print("-" * 50)
        print(content)
        print("-" * 50)
        return None
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"✓ Saved diary entry to {output_file}")
    return output_file


def append_to_daily_memory(entry_content, date_str, config, workspace, dry_run=False):
    """Append diary summary to main daily memory file"""
    memory_integration = config.get("memory_integration", {})
    
    if not memory_integration.get("enabled", False):
        return
    
    if not memory_integration.get("append_to_daily", False):
        return
    
    memory_dir = workspace / "memory"
    daily_memory_file = memory_dir / f"{date_str}.md"
    
    # Get format
    format_type = memory_integration.get("format", "summary")
    diary_path = config.get("diary_path", DEFAULT_DIARY_PATH)
    
    # Build content to append
    if format_type == "link":
        content = f"\n\n## 📜 Daily Chronicle\n[View diary entry]({diary_path}{date_str}.md)\n"
    elif format_type == "full":
        content = f"\n\n## 📜 Daily Chronicle\n{entry_content}\n"
    else:  # summary
        summary = extract_summary_from_entry(entry_content)
        title = extract_title_from_entry(entry_content)
        title_line = f"**{title}**\n\n" if title else ""
        content = f"\n\n## 📜 Daily Chronicle\n{title_line}{summary}\n"
    
    if dry_run:
        print(f"\n--- Would append to {daily_memory_file}:")
        print(content)
        return
    
    # Create memory dir if needed
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if section already exists
    if daily_memory_file.exists():
        existing_content = daily_memory_file.read_text()
        if "## 📜 Daily Chronicle" in existing_content:
            print(f"  ℹ️  Daily Chronicle section already exists in {daily_memory_file}")
            return
        # Append to existing file
        with open(daily_memory_file, 'a') as f:
            f.write(content)
    else:
        # Create new file with header
        header = f"# {date_str}\n\n*Daily memory log*\n"
        with open(daily_memory_file, 'w') as f:
            f.write(header + content)
    
    print(f"  ✓ Added chronicle to {daily_memory_file}")


def update_persistent_files(entry_content, date_str, workspace):
    """Extract and append quotes, curiosities, decisions to persistent files"""
    diary_dir = workspace / "memory" / "diary"
    diary_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract Quote of the Day
    quote_match = re.search(r'## Quote of the Day 💬\n(.+?)(?=\n##|\Z)', entry_content, re.DOTALL)
    if quote_match:
        quote_content = quote_match.group(1).strip()
        if quote_content and len(quote_content) > 10:
            quotes_file = diary_dir / "quotes.md"
            if not quotes_file.exists():
                quotes_file.write_text("# Quote Hall of Fame 💬\n\nMemorable quotes from my human.\n\n---\n\n")
            
            with open(quotes_file, 'a') as f:
                f.write(f"\n### {date_str}\n{quote_content}\n")
            print(f"  ✓ Added quote to {quotes_file}")
    
    # Extract Curiosities
    curiosity_match = re.search(r'## Things I\'m Curious About 🔮\n(.+?)(?=\n##|\Z)', entry_content, re.DOTALL)
    if curiosity_match:
        curiosity_content = curiosity_match.group(1).strip()
        if curiosity_content and len(curiosity_content) > 10:
            curiosity_file = diary_dir / "curiosity.md"
            if not curiosity_file.exists():
                curiosity_file.write_text("# Curiosity Backlog 🔮\n\nThings I want to explore.\n\n---\n\n## Active\n\n")
            
            with open(curiosity_file, 'a') as f:
                f.write(f"\n### {date_str}\n{curiosity_content}\n")
            print(f"  ✓ Added curiosities to {curiosity_file}")
    
    # Extract Decisions
    decisions_match = re.search(r'## Key Decisions Made 🏛️\n(.+?)(?=\n##|\Z)', entry_content, re.DOTALL)
    if decisions_match:
        decisions_content = decisions_match.group(1).strip()
        if decisions_content and len(decisions_content) > 10:
            decisions_file = diary_dir / "decisions.md"
            if not decisions_file.exists():
                decisions_file.write_text("# Decision Archaeology 🏛️\n\nJudgment calls worth remembering.\n\n---\n\n")
            
            with open(decisions_file, 'a') as f:
                f.write(f"\n### {date_str}\n{decisions_content}\n")
            print(f"  ✓ Added decisions to {decisions_file}")
    
    # Extract Relationship Notes
    relationship_match = re.search(r'## Relationship Notes 🤝\n(.+?)(?=\n##|\Z)', entry_content, re.DOTALL)
    if relationship_match:
        relationship_content = relationship_match.group(1).strip()
        if relationship_content and len(relationship_content) > 10:
            relationship_file = diary_dir / "relationship.md"
            if not relationship_file.exists():
                relationship_file.write_text("# Relationship Evolution 🤝\n\nHow my dynamic with my human evolves.\n\n---\n\n")
            
            with open(relationship_file, 'a') as f:
                f.write(f"\n### {date_str}\n{relationship_content}\n")
            print(f"  ✓ Added relationship notes to {relationship_file}")


def interactive_mode(date_str):
    """Fallback interactive mode for when AI is unavailable"""
    print(f"\n📓 AI Diary Entry for {date_str}\n")
    print("AI generation unavailable. Enter details manually.\n")
    
    entry = {"date": date_str}
    
    prompts = [
        ("title", "Day title: "),
        ("summary", "Summary (1-2 sentences): "),
        ("projects", "Projects worked on: "),
        ("wins", "Wins: "),
        ("frustrations", "Frustrations: "),
        ("learnings", "Learnings: "),
        ("emotional_state", "Emotional state: "),
        ("interactions", "Notable interactions: "),
        ("quotes", "Quote of the day: "),
        ("curiosity", "Curious about: "),
        ("decisions", "Key decisions: "),
        ("relationship", "Relationship notes: "),
        ("tomorrow", "Tomorrow's focus: ")
    ]
    
    for key, prompt in prompts:
        entry[key] = input(prompt) or ""
    
    # Build markdown from entry
    content = f"""# {date_str} — {entry.get('title', 'Untitled')}

## Summary
{entry.get('summary', '')}

## Projects Worked On
{entry.get('projects', '')}

## Wins 🎉
{entry.get('wins', '')}

## Frustrations 😤
{entry.get('frustrations', '')}

## Learnings 📚
{entry.get('learnings', '')}

## Emotional State
{entry.get('emotional_state', '')}

## Notable Interactions
{entry.get('interactions', '')}

## Quote of the Day 💬
{entry.get('quotes', '')}

## Things I'm Curious About 🔮
{entry.get('curiosity', '')}

## Key Decisions Made 🏛️
{entry.get('decisions', '')}

## Relationship Notes 🤝
{entry.get('relationship', '')}

## Tomorrow's Focus
{entry.get('tomorrow', '')}
"""
    
    return content


def main():
    parser = argparse.ArgumentParser(description="Generate Agent Chronicle diary entries")
    parser.add_argument("--today", action="store_true", help="Generate for today")
    parser.add_argument("--date", help="Generate for specific date (YYYY-MM-DD)")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--emit-task", action="store_true", help="Print the sub-agent generation task JSON (for sessions_spawn)")
    parser.add_argument("--from-stdin", action="store_true", help="Read a pre-generated entry from stdin and save it")
    parser.add_argument("--from-file", help="Read a pre-generated entry from a file path and save it")
    parser.add_argument("--auto", action="store_true", help="Auto-generate today's entry without interaction (for cron)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-persistent", action="store_true", help="Skip updating persistent files")
    parser.add_argument("--no-looking-back", action="store_true", help="Skip 'Looking Back' section")
    parser.add_argument("--pdf", action="store_true", help="Generate/refresh the diary PDF after saving")
    
    args = parser.parse_args()
    
    config = load_config()
    workspace = get_workspace_root()
    diary_path = get_diary_path(config)
    
    if args.verbose:
        print(f"Workspace: {workspace}")
        print(f"Diary path: {diary_path}")
        print("Generation: sessions_spawn sub-agent (no direct HTTP in this script)")
    
    # Determine date
    if args.today or args.auto:
        date_str = datetime.now().strftime("%Y-%m-%d")
    elif args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # --auto mode: generate today's entry non-interactively via emit-task
    if args.auto:
        # Check config for auto_generate flag
        if not config.get("auto_generate", False):
            if args.verbose:
                print("ℹ️  auto_generate is disabled in config.json. Enable it to use --auto.")
                print("   Set \"auto_generate\": true in config.json")
            # Still proceed — the flag on the CLI overrides config
        
        # Check if today's entry already exists
        existing = diary_path / f"{date_str}.md"
        if existing.exists():
            print(f"ℹ️  Entry for {date_str} already exists. Skipping auto-generation.")
            return
        
        # In auto mode, emit the task JSON so the caller (cron/agent) can spawn a sub-agent
        print(f"\n📜 Agent Chronicle - Auto-generating diary for {date_str}")
        print("=" * 50)
        
        result = generate_ai_diary(date_str, workspace, verbose=args.verbose, emit_task=True)
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("❌ No session data available for auto-generation.")
            sys.exit(1)
        return
    
    print(f"\n📜 Agent Chronicle - Generating diary for {date_str}")
    print("=" * 50)
    
    # Generate / load entry
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
    elif args.interactive:
        content = interactive_mode(date_str)
    else:
        result = generate_ai_diary(
            date_str,
            workspace,
            verbose=args.verbose,
            emit_task=args.emit_task,
        )

        if args.emit_task:
            # Print JSON to stdout for easy piping into sessions_spawn.
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        content = result

        if not content:
            print("\nAI generation is performed via sessions_spawn (see SKILL.md). Falling back to interactive mode...")
            content = interactive_mode(date_str)
    
    if content:
        # Add "Looking Back" section if old entries exist
        if not args.no_looking_back:
            looking_back = find_looking_back_entries(date_str, diary_path)
            if looking_back:
                looking_back_section = build_looking_back_section(looking_back)
                content = content.rstrip() + "\n" + looking_back_section

        # Save entry
        saved_file = save_entry(content, date_str, diary_path, dry_run=args.dry_run)
        
        if saved_file and not args.dry_run:
            # Append to daily memory
            append_to_daily_memory(content, date_str, config, workspace, dry_run=args.dry_run)
            
            # Update persistent files (quotes, curiosity, decisions, relationship)
            if not args.no_persistent:
                update_persistent_files(content, date_str, workspace)

            # Optional: refresh PDF export
            if args.pdf:
                export_script = SCRIPT_DIR / "export_pdf.py"
                if export_script.exists():
                    try:
                        import subprocess
                        subprocess.run([sys.executable, str(export_script)], check=True)
                    except Exception as e:
                        print(f"  ⚠️  PDF export failed: {e}")
                else:
                    print("  ⚠️  export_pdf.py not found; skipping PDF export.")
        
        print("\n✨ Diary entry generation complete!")
        
        # Show word count
        word_count = len(content.split())
        print(f"   Word count: {word_count} words")
    else:
        print("\n❌ No entry generated.")
        sys.exit(1)


if __name__ == "__main__":
    main()
