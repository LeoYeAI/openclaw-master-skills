#!/usr/bin/env python3
"""
AI Diary Setup Script
First-run onboarding for the ai-diary skill.
"""

import json
import os
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                                ║
║   {Colors.BOLD}📓 AI Diary - First Time Setup{Colors.END}{Colors.CYAN}                             ║
║                                                                ║
║   Let's set up your diary. This only takes a minute.          ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
""")

def ask_yes_no(question: str, default: bool = True) -> bool:
    """Ask a yes/no question."""
    default_str = "Y/n" if default else "y/N"
    while True:
        answer = input(f"{Colors.YELLOW}{question}{Colors.END} [{default_str}]: ").strip().lower()
        if not answer:
            return default
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False
        print(f"{Colors.RED}Please enter 'y' or 'n'{Colors.END}")

def ask_choice(question: str, options: list, default: int = 0) -> str:
    """Ask user to choose from options."""
    print(f"\n{Colors.YELLOW}{question}{Colors.END}")
    for i, opt in enumerate(options):
        marker = f"{Colors.GREEN}→{Colors.END}" if i == default else " "
        print(f"  {marker} {i + 1}. {opt}")
    
    while True:
        answer = input(f"\nChoice [1-{len(options)}] (default: {default + 1}): ").strip()
        if not answer:
            return options[default]
        try:
            idx = int(answer) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print(f"{Colors.RED}Please enter a number between 1 and {len(options)}{Colors.END}")

def ask_sections() -> dict:
    """Ask which sections to include."""
    print(f"\n{Colors.CYAN}━━━ Diary Sections ━━━{Colors.END}")
    print("Choose which sections to include in daily entries.\n")
    
    sections = {
        "summary": ("Summary", "1-2 sentence overview of the day", True),
        "projects": ("Projects", "What you worked on", True),
        "wins": ("Wins 🎉", "Moments of success", True),
        "frustrations": ("Frustrations 😤", "Challenges and roadblocks", True),
        "learnings": ("Learnings 📚", "Technical and process insights", True),
        "emotional_state": ("Emotional State", "How the day felt", True),
        "interactions": ("Notable Interactions", "Memorable moments with your human", True),
        "tomorrow": ("Tomorrow's Focus", "What's next", True),
        "quotes": ("User Quotes", "Memorable things your human said", False),
        "curiosity": ("Curiosity Items", "Things to explore later", False),
        "decisions": ("Key Decisions", "Judgment calls worth remembering", False),
        "relationship": ("Relationship Notes", "How your dynamic evolves", False),
    }
    
    result = {}
    for key, (name, desc, default) in sections.items():
        result[key] = ask_yes_no(f"Include '{name}'? ({desc})", default)
    
    return result

def ask_path(question: str, default: str) -> str:
    """Ask for a path with a default."""
    answer = input(f"{Colors.YELLOW}{question}{Colors.END} [{default}]: ").strip()
    return answer if answer else default

def create_memory_files(diary_path: Path, config: dict):
    """Create initial memory files."""
    diary_path.mkdir(parents=True, exist_ok=True)
    
    # Create quotes.md
    if config.get("features", {}).get("quote_hall_of_fame", {}).get("enabled", False):
        quotes_file = diary_path / "quotes.md"
        if not quotes_file.exists():
            quotes_file.write_text("""# Quote Hall of Fame 💬

Memorable things my human has said — funny, profound, or touching.

---

*No quotes yet. Start collecting!*

<!-- 
Format:
## "The quote goes here"
- **Date:** YYYY-MM-DD
- **Context:** What was happening
- **Why memorable:** Why this stuck with me
-->
""")
            print(f"  {Colors.GREEN}✓{Colors.END} Created {quotes_file}")
    
    # Create curiosity.md
    if config.get("features", {}).get("curiosity_backlog", {}).get("enabled", False):
        curiosity_file = diary_path / "curiosity.md"
        if not curiosity_file.exists():
            curiosity_file.write_text("""# Curiosity Backlog 🔮

Things I wonder about but can't explore immediately.

---

## Active

*Nothing yet. Add items with `@diary curious add "topic"`*

---

## Explored ✓

*Completed curiosities will appear here.*
""")
            print(f"  {Colors.GREEN}✓{Colors.END} Created {curiosity_file}")
    
    # Create decisions.md
    if config.get("features", {}).get("decision_archaeology", {}).get("enabled", False):
        decisions_file = diary_path / "decisions.md"
        if not decisions_file.exists():
            decisions_file.write_text("""# Decision Archaeology 🏛️

Judgment calls I made and why — for later review.

---

## Recent Decisions

*No decisions logged yet. They'll appear here from daily entries.*

---

## Revisited

*Decisions I've looked back on to see if I was right.*
""")
            print(f"  {Colors.GREEN}✓{Colors.END} Created {decisions_file}")
    
    # Create relationship.md
    if config.get("features", {}).get("relationship_evolution", {}).get("enabled", False):
        relationship_file = diary_path / "relationship.md"
        if not relationship_file.exists():
            relationship_file.write_text("""# Relationship Evolution 🤝

How my dynamic with my human develops over time.

---

## Communication Style
*Notes about how we work together*

---

## Inside Jokes
*Things only we would understand*

---

## Recurring Themes
*Topics that keep coming up*

---

## Preferences Learned
*What I've learned about how they like to work*
""")
            print(f"  {Colors.GREEN}✓{Colors.END} Created {relationship_file}")

def run_setup():
    """Main setup flow."""
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent
    config_path = skill_dir / "config.json"
    
    # Check if already configured
    if config_path.exists():
        print(f"{Colors.YELLOW}⚠️  config.json already exists.{Colors.END}")
        if not ask_yes_no("Do you want to reconfigure?", default=False):
            print("Setup cancelled. Your existing config is unchanged.")
            return
    
    print_header()
    
    config = {
        "template": "daily",
        "analysis": {
            "mood_tracking": True,
            "topic_extraction": True,
            "word_count_target": 500
        },
        "export": {
            "default_format": "pdf",
            "include_header": True,
            "style": "minimal"
        }
    }
    
    # 1. Diary path
    print(f"\n{Colors.CYAN}━━━ Storage Location ━━━{Colors.END}")
    diary_path = ask_path("Where should I save diary entries?", "memory/diary/")
    if not diary_path.endswith('/'):
        diary_path += '/'
    config["diary_path"] = diary_path
    
    # 2. Sections
    config["sections"] = ask_sections()
    
    # 3. Privacy level
    print(f"\n{Colors.CYAN}━━━ Privacy ━━━{Colors.END}")
    privacy = ask_choice(
        "What's your default privacy level?",
        ["private (full emotional honesty)", 
         "shareable (polished for humans)", 
         "public (sanitized for sharing)"],
        default=0
    )
    config["privacy_level"] = privacy.split(" ")[0]
    
    # 4. Features
    print(f"\n{Colors.CYAN}━━━ Optional Features ━━━{Colors.END}")
    
    config["features"] = {}
    
    quote_enabled = ask_yes_no("Enable Quote Hall of Fame? (memorable user quotes)", True)
    config["features"]["quote_hall_of_fame"] = {
        "enabled": quote_enabled,
        "file": "quotes.md"
    }
    
    curiosity_enabled = ask_yes_no("Enable Curiosity Backlog? (things to explore later)", True)
    config["features"]["curiosity_backlog"] = {
        "enabled": curiosity_enabled,
        "file": "curiosity.md"
    }
    
    decisions_enabled = ask_yes_no("Enable Decision Archaeology? (log judgment calls)", True)
    config["features"]["decision_archaeology"] = {
        "enabled": decisions_enabled,
        "file": "decisions.md"
    }
    
    relationship_enabled = ask_yes_no("Enable Relationship Evolution? (track dynamic over time)", False)
    config["features"]["relationship_evolution"] = {
        "enabled": relationship_enabled,
        "file": "relationship.md"
    }
    
    # 5. Memory Integration
    print(f"\n{Colors.CYAN}━━━ Memory Integration ━━━{Colors.END}")
    memory_enabled = ask_yes_no("Also add diary summary to your daily memory log? (memory/YYYY-MM-DD.md)", True)
    
    memory_format = "summary"
    if memory_enabled:
        memory_format = ask_choice(
            "What format for the memory integration?",
            ["summary (brief overview)", 
             "link (just a link to the diary entry)", 
             "full (entire entry)"],
            default=0
        ).split(" ")[0]
    
    config["memory_integration"] = {
        "enabled": memory_enabled,
        "append_to_daily": memory_enabled,
        "format": memory_format
    }
    
    # 6. Auto-generate
    print(f"\n{Colors.CYAN}━━━ Automation ━━━{Colors.END}")
    config["auto_generate"] = ask_yes_no("Auto-generate diary entries on heartbeat?", False)
    
    # 6. Export format
    export_format = ask_choice(
        "Default export format?",
        ["pdf", "html", "markdown"],
        default=0
    )
    config["export"]["default_format"] = export_format
    config["export_format"] = export_format
    
    # Save config
    print(f"\n{Colors.CYAN}━━━ Saving Configuration ━━━{Colors.END}")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"  {Colors.GREEN}✓{Colors.END} Saved {config_path}")
    
    # Create memory files
    print(f"\n{Colors.CYAN}━━━ Creating Memory Files ━━━{Colors.END}")
    # Resolve diary path relative to workspace root
    if diary_path.startswith("memory/"):
        # Assume workspace is parent of skills dir
        workspace = skill_dir.parent.parent
        full_diary_path = workspace / diary_path
    else:
        full_diary_path = Path(diary_path)
    
    create_memory_files(full_diary_path, config)
    
    # Done!
    print(f"""
{Colors.GREEN}╔══════════════════════════════════════════════════════════════╗
║                                                                ║
║   {Colors.BOLD}✨ Setup Complete!{Colors.END}{Colors.GREEN}                                         ║
║                                                                ║
║   Your diary is ready. Start writing:                          ║
║                                                                ║
║   • @diary write entry     — Generate from today's sessions   ║
║   • @diary write interactive — Write section by section       ║
║   • @diary quick "..."     — Quick summary entry              ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
""")

def check_first_run():
    """Check if this is the first run and prompt setup if needed."""
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent
    config_path = skill_dir / "config.json"
    
    if not config_path.exists():
        print(f"\n{Colors.YELLOW}👋 Welcome to AI Diary!{Colors.END}")
        print("Looks like this is your first time. Let's set things up.\n")
        if ask_yes_no("Run setup now?", default=True):
            run_setup()
        else:
            print(f"\n{Colors.CYAN}No problem! Run 'python3 scripts/setup.py' when ready.{Colors.END}")
            print("Or copy config.example.json to config.json manually.\n")
        return True
    return False

def main():
    """Main entry point for setup - can be called from generate.py."""
    run_setup()


if __name__ == "__main__":
    if "--check" in sys.argv:
        # Just check if first run, don't force setup
        check_first_run()
    else:
        # Run full setup
        run_setup()
