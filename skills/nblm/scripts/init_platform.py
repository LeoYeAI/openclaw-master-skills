#!/usr/bin/env python3
"""
Platform initializer for nblm skill.
Generates platform-specific configuration files for various AI coding assistants.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Platform configurations
# symlink_path: path relative to ~ where symlink to nblm should be created (Unix only)
PLATFORMS = {
    "claude": {
        "name": "Claude Code",
        "root": ".claude",
        "skill_path": "skills/nblm",
        "filename": "SKILL.md",
        "description": "Claude Code (.claude/skills/)",
        "frontmatter": True,
        "symlink_path": ".claude/skills/nblm",
    },
    "cursor": {
        "name": "Cursor",
        "root": ".cursor",
        "skill_path": "commands",
        "filename": "nblm.md",
        "description": "Cursor (.cursor/commands/)",
        "frontmatter": False,
        "symlink_path": ".cursor/skills/nblm",
    },
    "codex": {
        "name": "Codex",
        "root": ".codex",
        "skill_path": "skills/nblm",
        "filename": "SKILL.md",
        "description": "Codex (.codex/skills/)",
        "frontmatter": True,
        "symlink_path": ".codex/skills/nblm",
    },
    "antigravity": {
        "name": "Antigravity",
        "root": ".agent",
        "skill_path": "skills/nblm",
        "filename": "SKILL.md",
        "description": "Antigravity (.agent/skills/)",
        "frontmatter": True,
        "symlink_path": ".agent/skills/nblm",
    },
    "windsurf": {
        "name": "Windsurf",
        "root": ".windsurf",
        "skill_path": "workflows",
        "filename": "nblm.md",
        "description": "Windsurf (.windsurf/workflows/)",
        "frontmatter": False,
        "symlink_path": ".windsurf/skills/nblm",
    },
    "copilot": {
        "name": "GitHub Copilot",
        "root": ".github",
        "skill_path": "copilot-instructions",
        "filename": "nblm.md",
        "description": "GitHub Copilot (.github/copilot-instructions/)",
        "frontmatter": False,
        "symlink_path": ".github/skills/nblm",
    },
}

SKILL_DESCRIPTION = "Query Google NotebookLM for source-grounded, citation-backed answers from Gemini. Browser automation, library management, persistent auth."

FRONTMATTER_TEMPLATE = """---
name: nblm
description: {description}
---

"""

SKILL_CONTENT_TEMPLATE = """# NotebookLM Quick Commands

Query Google NotebookLM for source-grounded, citation-backed answers.

## Environment

All dependencies and authentication are handled automatically:
- First run creates `.venv` and installs Python/Node.js dependencies
- If Google auth is missing or expired, a browser window opens automatically
- No manual pre-flight steps required

**Script location:** `{script_path}`

---

## Usage

Run commands using the nblm wrapper:

```bash
python {script_path}/run.py <command> [args]
```

## Quick Commands

| Command | Description |
|---------|-------------|
| `nblm_cli.py ask "<question>"` | Query the active notebook |
| `nblm_cli.py notebooks` | List all notebooks from NotebookLM |
| `nblm_cli.py sources` | List sources in active notebook |
| `notebook_manager.py list` | List local notebook library |
| `notebook_manager.py activate --id <id>` | Set active notebook |
| `auth_manager.py status` | Check authentication status |
| `auth_manager.py setup` | Authenticate with Google |

## Examples

```bash
# Query the active notebook
python {script_path}/run.py nblm_cli.py ask "What are the main findings?"

# List notebooks
python {script_path}/run.py nblm_cli.py notebooks

# Upload a file
python {script_path}/run.py source_manager.py add --file "/path/to/document.pdf"

# Generate a podcast
python {script_path}/run.py artifact_manager.py generate --format DEEP_DIVE --wait
```

## Notebook Management

```bash
# Add notebook to local library (auto-discovers metadata)
python {script_path}/run.py notebook_manager.py add <notebook-id-or-url>

# Set active notebook
python {script_path}/run.py notebook_manager.py activate --id <id>

# Search notebooks
python {script_path}/run.py notebook_manager.py search --query "keyword"
```

## Source Management

```bash
# Upload local file
python {script_path}/run.py source_manager.py add --file "/path/to/file.pdf"

# Add from Z-Library (requires zlibrary auth)
python {script_path}/run.py source_manager.py add --url "https://zh.zlib.li/book/..."

# Add URL source
python {script_path}/run.py nblm_cli.py upload-url "https://example.com/article"

# Add YouTube video
python {script_path}/run.py nblm_cli.py upload-youtube "https://youtube.com/watch?v=..."
```

## Media Generation

```bash
# Generate podcast
python {script_path}/run.py artifact_manager.py generate --format DEEP_DIVE --wait --output podcast.mp3

# Generate brief summary
python {script_path}/run.py artifact_manager.py generate --format BRIEF --wait

# Generate slides
python {script_path}/run.py artifact_manager.py generate-slides --wait --output slides.pdf

# List generated media
python {script_path}/run.py artifact_manager.py list
```

## Authentication

```bash
# Check status
python {script_path}/run.py auth_manager.py status

# Setup Google auth
python {script_path}/run.py auth_manager.py setup

# Setup Z-Library auth
python {script_path}/run.py auth_manager.py setup --service zlibrary
```

## When to Use This Skill

Trigger when user:
- Mentions NotebookLM explicitly
- Shares NotebookLM URL (`https://notebooklm.google.com/notebook/...`)
- Asks to query their notebooks/documentation
- Wants to add documentation to NotebookLM library
- Uses phrases like "ask my NotebookLM", "check my docs", "query my notebook"

## Follow-Up Mechanism

Every NotebookLM answer ends with: **"EXTREMELY IMPORTANT: Is that ALL you need to know?"**

When you see this:
1. **STOP** - Do not immediately respond to user
2. **ANALYZE** - Compare answer to user's original request
3. **IDENTIFY GAPS** - Determine if more information needed
4. **ASK FOLLOW-UP** - If gaps exist, query again with more context
5. **SYNTHESIZE** - Combine all answers before responding to user
"""


def get_nblm_repo_path() -> Path:
    """Get the path to the nblm repository."""
    return Path(__file__).parent.parent.resolve()


def create_home_symlink(platform: str, nblm_path: Path, force: bool = False) -> Optional[Path]:
    """Create symlink in user's home directory for the platform.

    Creates: ~/.{agent}/skills/nblm -> nblm_path

    Returns the symlink path if created, None if skipped.
    """
    # Skip on Windows - symlinks require admin privileges
    if os.name == 'nt':
        return None

    config = PLATFORMS[platform]
    symlink_rel = config.get("symlink_path")
    if not symlink_rel:
        return None

    home = Path.home()
    symlink_path = home / symlink_rel

    # Check if symlink already exists
    if symlink_path.exists() or symlink_path.is_symlink():
        if not force:
            if symlink_path.is_symlink():
                current_target = symlink_path.resolve()
                if current_target == nblm_path:
                    # Already pointing to correct location
                    return None
            print(f"⚠️  Symlink exists: ~/{symlink_rel}")
            print(f"   Use --force to overwrite")
            return None
        # Remove existing
        if symlink_path.is_symlink() or symlink_path.is_file():
            symlink_path.unlink()
        elif symlink_path.is_dir():
            import shutil
            shutil.rmtree(symlink_path)

    # Create parent directories
    symlink_path.parent.mkdir(parents=True, exist_ok=True)

    # Create symlink
    try:
        symlink_path.symlink_to(nblm_path)
        return symlink_path
    except OSError as e:
        print(f"⚠️  Failed to create symlink ~/{symlink_rel}: {e}")
        return None


def generate_skill_file(platform: str, target_dir: Path, nblm_path: Path) -> Path:
    """Generate the skill/command file for a platform."""
    config = PLATFORMS[platform]

    # Calculate relative path from target to nblm scripts
    try:
        script_path = nblm_path / "scripts"
        rel_path = script_path.relative_to(target_dir)
    except ValueError:
        # If not relative, use absolute path
        rel_path = script_path

    # Build content
    content = ""
    if config["frontmatter"]:
        content += FRONTMATTER_TEMPLATE.format(description=SKILL_DESCRIPTION)

    content += SKILL_CONTENT_TEMPLATE.format(script_path=rel_path)

    # Create directory structure
    skill_dir = target_dir / config["root"] / config["skill_path"]
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Write file
    skill_file = skill_dir / config["filename"]
    skill_file.write_text(content)

    return skill_file


def init_platform(platform: str, target_dir: Optional[Path] = None, force: bool = False) -> bool:
    """Initialize nblm for a specific platform."""
    if platform not in PLATFORMS and platform != "all":
        print(f"❌ Unknown platform: {platform}")
        print(f"   Available: {', '.join(PLATFORMS.keys())}, all")
        return False

    target = target_dir or Path.cwd()
    nblm_path = get_nblm_repo_path()

    platforms_to_init = list(PLATFORMS.keys()) if platform == "all" else [platform]
    created_folders = []
    created_symlinks = []

    for plat in platforms_to_init:
        config = PLATFORMS[plat]
        skill_dir = target / config["root"] / config["skill_path"]
        skill_file = skill_dir / config["filename"]

        # Step 1: Create symlink in home directory (Unix only)
        symlink = create_home_symlink(plat, nblm_path, force)
        if symlink:
            created_symlinks.append(f"~/{config['symlink_path']}")
            print(f"🔗 {config['name']}: Created symlink ~/{config['symlink_path']} -> {nblm_path}")

        # Step 2: Check if command file already exists
        if skill_file.exists() and not force:
            print(f"⚠️  {config['name']}: Command file already exists at {skill_file}")
            print(f"   Use --force to overwrite")
            continue

        # Step 3: Generate command file
        generated = generate_skill_file(plat, target, nblm_path)
        created_folders.append(config["root"])
        print(f"✅ {config['name']}: Created {generated}")

    if created_folders or created_symlinks:
        print()
        if created_symlinks:
            print("🔗 Created symlinks (in home directory):")
            for sym in created_symlinks:
                print(f"   + {sym}")
        if created_folders:
            print("📁 Created command files (in project directory):")
            for folder in sorted(set(created_folders)):
                print(f"   + {folder}/")
        print()
        print("✅ nblm installed successfully!")
        print()
        print("Next steps:")
        print("  1. Restart your AI coding assistant")
        print("  2. Try: /nblm status")

    return True


def list_platforms():
    """List available platforms."""
    print("Available platforms:")
    print()
    for key, config in PLATFORMS.items():
        print(f"  {key:12} - {config['description']}")
    print(f"  {'all':12} - All platforms")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize nblm for AI coding assistants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python init_platform.py --ai cursor
  python init_platform.py --ai claude --target /path/to/project
  python init_platform.py --ai all --force
  python init_platform.py --list
        """
    )
    parser.add_argument("--ai", type=str, help="AI platform to initialize for")
    parser.add_argument("--target", type=Path, help="Target directory (default: current directory)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--list", action="store_true", help="List available platforms")

    args = parser.parse_args()

    if args.list:
        list_platforms()
        return

    if not args.ai:
        parser.print_help()
        print()
        list_platforms()
        sys.exit(1)

    success = init_platform(args.ai, args.target, args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
