#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file of a skill folder

Usage:
    python package_skill.py <path/to/skill-folder> [output-directory]

Examples:
    python .claude/skills/skill-expert-skills/scripts/package_skill.py .claude/skills/my-skill
    python .claude/skills/skill-expert-skills/scripts/package_skill.py .claude/skills/my-skill ./dist
"""

import sys
import zipfile
from pathlib import Path
from quick_validate import validate_skill
from universal_validate import validate_universal


def _configure_stdio() -> None:
    """
    Avoid UnicodeEncodeError on Windows consoles (e.g., GBK) by ensuring
    unencodable characters are safely replaced instead of crashing.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except Exception:
            # Some environments replace stdio with objects that don't support reconfigure().
            pass


_configure_stdio()

EXCLUDE_DIR_NAMES = {".git", "__pycache__", "node_modules", "dist", "build"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}
EXCLUDE_FILENAMES = {".DS_Store"}


def _should_exclude(file_path: Path) -> bool:
    for part in file_path.parts:
        if part in EXCLUDE_DIR_NAMES:
            return True
    if file_path.name in EXCLUDE_FILENAMES:
        return True
    if file_path.suffix.lower() in EXCLUDE_SUFFIXES:
        return True
    return False


def package_skill(skill_path, output_dir=None):
    """
    Package a skill folder into a .skill file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the .skill file (defaults to current directory)

    Returns:
        Path to the created .skill file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Run validation before packaging
    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"✅ {message}\n")

    # Universal validation (warnings only)
    ok, findings = validate_universal(skill_path)
    if not ok:
        print("⚠️ Universal validation warnings (project-specific fingerprints found):")
        for f in findings:
            try:
                rel = f.file.relative_to(skill_path)
            except Exception:
                rel = f.file
            print(f"  - {f.pattern_name} at {rel}:{f.line_no}: {f.excerpt}")
        print("   Tip: Prefer relative/conceptual paths to keep the skill portable.\n")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    # Create the .skill file (zip format)
    try:
        with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the skill directory
            files = [p for p in skill_path.rglob('*') if p.is_file() and not _should_exclude(p)]
            for file_path in sorted(files):
                # Calculate the relative path within the zip
                arcname = file_path.relative_to(skill_path.parent)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

        print(f"\n✅ Successfully packaged skill to: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"❌ Error creating .skill file: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <path/to/skill-folder> [output-directory]")
        print("\nExample:")
        print("  python .claude/skills/skill-expert-skills/scripts/package_skill.py .claude/skills/my-skill")
        print("  python .claude/skills/skill-expert-skills/scripts/package_skill.py .claude/skills/my-skill ./dist")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"📦 Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()


