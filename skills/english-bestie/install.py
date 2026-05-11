#!/usr/bin/env python3
"""
english-bestie — installer for OpenClaw

For ClawHub users: run this AFTER `clawhub install english-bestie`
  to register your Telegram bot and pre-fill the student's Telegram config.

For manual installation (without ClawHub): this script copies all skill
  files into the right workspace and sets up Telegram config.

Usage: python3 install.py
"""

import json
import os
import shutil
import sys
from pathlib import Path

# ── colors ──────────────────────────────────────────────────────────────────
G   = "\033[92m"   # green
Y   = "\033[93m"   # yellow
R   = "\033[91m"   # red
B   = "\033[1m"    # bold
C   = "\033[96m"   # cyan
DIM = "\033[2m"    # dim
X   = "\033[0m"    # reset


def ask(label, default=None, required=True):
    prompt = f"  {B}{label}{X}"
    if default:
        prompt += f" {DIM}[{default}]{X}"
    prompt += f" {C}→{X} "
    while True:
        try:
            ans = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            sys.exit(0)
        if ans:
            return ans
        if default is not None:
            return default
        if not required:
            return ""
        print(f"    {R}✗ required{X}")


def section(title):
    print(f"\n  {B}{title}{X}")
    print(f"  {DIM}{'─' * 36}{X}")


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{C}{B}  🤙 english-bestie setup{X}")
    print(f"  {DIM}Registers your Telegram bot and configures student info{X}")
    print(f"  {DIM}Works after: clawhub install english-bestie{X}\n")

    # ── locate openclaw dir ──────────────────────────────────────────────────
    default_openclaw = str(Path.home() / ".openclaw")
    section("OpenClaw location")
    openclaw_dir = Path(ask("OpenClaw directory", default_openclaw))
    if not openclaw_dir.exists():
        print(f"\n  {R}✗ Directory not found: {openclaw_dir}{X}")
        sys.exit(1)

    skill_source = Path(__file__).parent

    # ── find workspace ───────────────────────────────────────────────────────
    section("Workspace")
    print(f"  {DIM}Where the skill is (or will be) installed{X}")
    workspaces = [d.name for d in openclaw_dir.iterdir()
                  if d.is_dir() and d.name.startswith("workspace")]
    if workspaces:
        print(f"  {DIM}Found workspaces: {', '.join(workspaces)}{X}")
        default_ws = workspaces[0]
    else:
        default_ws = "workspace-main"
    workspace_name = ask("Workspace folder name", default_ws)

    # ── Telegram ─────────────────────────────────────────────────────────────
    section("Telegram bot")
    print(f"  {DIM}Create a bot via @BotFather → get the token{X}")
    bot_token   = ask("Bot token")
    channel_key = ask("Channel key (short name for this bot)", "english-bestie-bot")
    bot_channel = f"telegram:{channel_key}"
    student_id  = ask("Student's Telegram user ID (numeric)")

    # ── confirm ──────────────────────────────────────────────────────────────
    workspace_dir = openclaw_dir / workspace_name
    skills_dir    = workspace_dir / "skills" / "english-bestie"

    print(f"\n  {B}Ready to set up:{X}")
    rows = [
        ("Skill location", str(skills_dir)),
        ("Bot channel",    bot_channel),
        ("Student ID",     student_id),
    ]
    for k, v in rows:
        print(f"    {DIM}{k:<16}{X}{C}{v}{X}")

    try:
        confirm = input(f"\n  {B}Proceed? [Y/n]{X} {C}→{X} ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        sys.exit(0)
    if confirm == "n":
        print("  Cancelled.")
        sys.exit(0)

    print(f"\n  {Y}Setting up…{X}\n")

    # ── build paths ──────────────────────────────────────────────────────────
    tracking_dir   = skills_dir / "tracking"
    curriculum_dir = skills_dir / "curriculum"
    openclaw_json  = openclaw_dir / "openclaw.json"

    # ── copy skill files (only if not already there) ─────────────────────────
    if not skills_dir.exists():
        for d in [workspace_dir, skills_dir, tracking_dir, curriculum_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # SKILL.md
        src = skill_source / "SKILL.md"
        if src.exists():
            shutil.copy(src, skills_dir / "SKILL.md")

        # Workspace files
        for fname in ["SOUL.md", "HEARTBEAT.md"]:
            src = skill_source / fname
            if src.exists():
                shutil.copy(src, workspace_dir / fname)

        # Curriculum
        for fname in ["grammar-topics.md", "conversation-scenarios.md", "vocabulary-lists.md"]:
            src = skill_source / "curriculum" / fname
            if src.exists():
                (curriculum_dir).mkdir(parents=True, exist_ok=True)
                shutil.copy(src, curriculum_dir / fname)

        # Tracking templates
        src_tracking = skill_source / "tracking"
        if src_tracking.exists():
            tracking_dir.mkdir(parents=True, exist_ok=True)
            for fname in os.listdir(src_tracking):
                shutil.copy(src_tracking / fname, tracking_dir / fname)

        print(f"  {G}✓{X} Skill files copied")
    else:
        print(f"  {G}✓{X} Skill files already in place  {DIM}(skipped copy){X}")

    # ── pre-fill Telegram config in student-profile.json ────────────────────
    profile_path = tracking_dir / "student-profile.json"
    if profile_path.exists():
        try:
            profile = json.loads(profile_path.read_text())
        except json.JSONDecodeError:
            profile = {}
    else:
        profile = {}

    profile["telegramChannel"] = bot_channel
    profile["telegramUserId"]  = int(student_id) if student_id.isdigit() else student_id
    tracking_dir.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(json.dumps(profile, indent=2))
    print(f"  {G}✓{X} student-profile.json  {DIM}(Telegram config pre-filled){X}")

    # ── openclaw.json — register Telegram bot ────────────────────────────────
    if openclaw_json.exists():
        try:
            config = json.loads(openclaw_json.read_text())
        except json.JSONDecodeError:
            config = {}
    else:
        config = {}

    config.setdefault("telegram", {})[channel_key] = {
        "token":        bot_token,
        "allowedUsers": [int(student_id) if student_id.isdigit() else student_id]
    }
    openclaw_json.write_text(json.dumps(config, indent=2))
    print(f"  {G}✓{X} openclaw.json  {DIM}(Telegram bot registered){X}")

    # ── done ─────────────────────────────────────────────────────────────────
    print(f"\n  {G}{B}✅ Done!{X}\n")
    print(f"  {DIM}Skill at:{X}  {C}{skills_dir}{X}")
    print(f"\n  {B}Next steps:{X}")
    print(f"    1. {C}openclaw restart{X}  — reload config")
    print(f"    2. Send any message to the bot (or wait for first cron)")
    print(f"    3. The agent runs onboarding automatically and schedules all daily crons\n")


if __name__ == "__main__":
    main()
