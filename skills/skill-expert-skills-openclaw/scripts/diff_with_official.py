#!/usr/bin/env python3
"""
Diff with Official - Compare a skill against official skill-creator standards

This tool helps identify:
- Deviations from official frontmatter spec
- Extended fields that may not be compatible
- Best practices alignment

Usage:
    python diff_with_official.py <path/to/skill-folder>
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass


_configure_stdio()

# Official Agent Skills spec (minimal)
OFFICIAL_ALLOWED_FIELDS = {'name', 'description'}

# Extended fields (skill-expert-skills allows)
EXTENDED_ALLOWED_FIELDS = {'name', 'description', 'license', 'allowed-tools', 'metadata'}


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Parse YAML frontmatter and return (dict, body)"""
    try:
        import yaml
    except ImportError:
        return {}, content

    match = re.match(r'^---\r?\n(.*?)\r?\n---', content, re.DOTALL)
    if not match:
        return {}, content

    try:
        fm = yaml.safe_load(match.group(1)) or {}
        return fm, content[match.end():]
    except Exception:
        return {}, content


def analyze_compatibility(skill_path: Path) -> Dict:
    """Analyze skill for official compatibility"""
    result = {
        'skill_name': skill_path.name,
        'official_compatible': True,
        'issues': [],
        'warnings': [],
        'info': []
    }

    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        result['official_compatible'] = False
        result['issues'].append("SKILL.md not found")
        return result

    try:
        content = skill_md.read_text(encoding='utf-8-sig')
    except Exception as e:
        result['issues'].append(f"Cannot read SKILL.md: {e}")
        return result

    frontmatter, body = parse_frontmatter(content)

    # Check for non-official fields
    current_fields = set(frontmatter.keys())
    non_official = current_fields - OFFICIAL_ALLOWED_FIELDS

    if non_official:
        result['official_compatible'] = False
        for field in non_official:
            if field in EXTENDED_ALLOWED_FIELDS:
                result['warnings'].append(
                    f"Extended field '{field}' - OK for skill-expert-skills, "
                    f"but NOT supported by official Agent Skills"
                )
            else:
                result['issues'].append(
                    f"Unknown field '{field}' - not in any known spec"
                )

    # Check name format
    name = frontmatter.get('name', '')
    if name:
        if not re.match(r'^[a-z0-9-]+$', name):
            result['issues'].append(f"Name '{name}' violates hyphen-case rule")
        if len(name) > 64:
            result['issues'].append(f"Name too long ({len(name)} > 64 chars)")

    # Check description
    desc = frontmatter.get('description', '')
    if desc:
        if '<' in desc or '>' in desc:
            result['issues'].append("Description contains angle brackets (< or >)")
        if len(desc) > 1024:
            result['issues'].append(f"Description too long ({len(desc)} > 1024 chars)")

    # Check body length
    body_lines = body.count('\n')
    if body_lines > 500:
        result['warnings'].append(f"SKILL.md body is {body_lines} lines (recommend < 500)")
    if body_lines > 800:
        result['issues'].append(f"SKILL.md body exceeds 800 lines hard limit")

    # Info about extended features used
    if 'allowed-tools' in frontmatter:
        result['info'].append(f"Uses allowed-tools: {frontmatter['allowed-tools']}")
    if 'metadata' in frontmatter:
        result['info'].append(f"Uses metadata: {list(frontmatter['metadata'].keys())}")
    if 'license' in frontmatter:
        result['info'].append(f"Uses license: {frontmatter['license']}")

    return result


def format_report(result: Dict) -> str:
    """Format analysis as report"""
    lines = []
    lines.append("=" * 70)
    lines.append("📋 OFFICIAL COMPATIBILITY CHECK")
    lines.append("=" * 70)
    lines.append(f"\nSkill: {result['skill_name']}")

    if result['official_compatible']:
        lines.append("\n✅ OFFICIAL AGENT SKILLS COMPATIBLE")
        lines.append("   This skill uses only official spec fields (name, description)")
    else:
        lines.append("\n⚠️  NOT FULLY OFFICIAL COMPATIBLE")
        lines.append("   This skill uses extended fields from skill-expert-skills")

    if result['issues']:
        lines.append("\n🔴 ISSUES (Must fix for any environment):")
        for issue in result['issues']:
            lines.append(f"   • {issue}")

    if result['warnings']:
        lines.append("\n🟡 WARNINGS (Extended features):")
        for warning in result['warnings']:
            lines.append(f"   • {warning}")

    if result['info']:
        lines.append("\n📌 INFO (Extended features in use):")
        for info in result['info']:
            lines.append(f"   • {info}")

    lines.append("\n" + "=" * 70)
    lines.append("💡 MIGRATION GUIDE (if needed for official Agent Skills):")
    lines.append("   1. Keep only 'name' and 'description' in frontmatter")
    lines.append("   2. Remove 'allowed-tools', 'license', 'metadata' fields")
    lines.append("   3. Move any removed metadata to SKILL.md body or references/")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python diff_with_official.py <path/to/skill-folder>")
        sys.exit(1)

    skill_path = Path(sys.argv[1]).resolve()
    if not skill_path.exists():
        print(f"❌ Error: Path not found: {skill_path}")
        sys.exit(1)

    result = analyze_compatibility(skill_path)
    print(format_report(result))

    sys.exit(0 if result['official_compatible'] else 1)


if __name__ == "__main__":
    main()

