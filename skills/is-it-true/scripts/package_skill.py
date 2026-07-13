#!/usr/bin/env python3
"""Package skill for distribution."""

import json
import os
import shutil
import zipfile
from pathlib import Path


def validate_skill(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate skill structure and return errors."""
    errors = []

    # Check required files
    if not (skill_path / "SKILL.md").exists():
        errors.append("Missing SKILL.md")
    if not (skill_path / "_meta.json").exists():
        errors.append("Missing _meta.json")

    # Validate _meta.json
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            required_keys = ["id", "version"]
            for key in required_keys:
                if key not in meta:
                    errors.append(f"Missing required key in _meta.json: {key}")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in _meta.json: {e}")

    # Validate SKILL.md frontmatter
    skill_path_md = skill_path / "SKILL.md"
    if skill_path_md.exists():
        with open(skill_path_md) as f:
            content = f.read()
        if not content.startswith("---"):
            errors.append("SKILL.md must start with YAML frontmatter (---)")

        # Extract frontmatter
        lines = content.split("\n")
        if len(lines) > 2 and lines[0] == "---":
            # Find closing ---
            for i, line in enumerate(lines[1:], 1):
                if line == "---":
                    frontmatter = "\n".join(lines[1:i])
                    if "name:" not in frontmatter:
                        errors.append("SKILL.md frontmatter must contain 'name:' field")
                    if "description:" not in frontmatter:
                        errors.append("SKILL.md frontmatter must contain 'description:' field")
                    break

    return len(errors) == 0, errors


def package_skill(skill_path: str, output_dir: str = "dist") -> str:
    """Package skill into a .skill file."""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Validate
    valid, errors = validate_skill(skill_path)
    if not valid:
        raise ValueError(f"Validation failed: {', '.join(errors)}")

    # Get skill name from folder
    skill_name = skill_path.name
    output_file = output_dir / f"{skill_name}.skill"

    # Create zip archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Skip scripts directory in package
            if 'scripts' in dirs:
                dirs.remove('scripts')
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    return str(output_file)


if __name__ == "__main__":
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output = package_skill(skill_path)
    print(f"Packaged skill to: {output}")
