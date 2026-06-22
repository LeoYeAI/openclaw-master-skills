#!/usr/bin/env python3
"""
Skill Upgrader - Analyze and upgrade existing skills to best practices

Features:
- Detect missing best practice elements (decision tree, output contract, etc.)
- Generate upgrade suggestions with code snippets
- Auto-insert missing sections (optional)
- Compare against skill-expert-skills standards

Usage:
    python upgrade_skill.py <path/to/skill-folder> [--auto-fix]

Examples:
    python upgrade_skill.py .claude/skills/my-old-skill
    python upgrade_skill.py .claude/skills/my-old-skill --auto-fix
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


def _configure_stdio() -> None:
    """Ensure UTF-8 encoding for stdout/stderr on Windows"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass


_configure_stdio()


@dataclass
class UpgradeSuggestion:
    priority: str  # "high", "medium", "low"
    category: str
    issue: str
    suggestion: str
    code_snippet: Optional[str] = None
    line_to_insert_after: Optional[int] = None


class SkillUpgrader:
    """Analyze and upgrade skills to best practices"""

    BEST_PRACTICE_PATTERNS = {
        'decision_tree': {
            'patterns': [r'decision\s*tree', r'决策树', r'┌─', r'├─', r'└─'],
            'priority': 'high',
            'suggestion': 'Add a decision tree for clear workflow guidance',
            'template': '''
## Decision Tree

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Task Decision Tree                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  【Scenario A】                                                      │
│  → Step 1: [action]                                                  │
│  → Step 2: [action]                                                  │
│                                                                      │
│  【Scenario B】                                                      │
│  → Step 1: [action]                                                  │
│  → Step 2: [action]                                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```
'''
        },
        'output_contract': {
            'patterns': [r'output\s*contract', r'输出契约', r'deliverable', r'交付'],
            'priority': 'high',
            'suggestion': 'Define clear output contract for predictable results',
            'template': '''
## Output Contract

### Required Deliverables
- [ ] Updated `SKILL.md` with YAML frontmatter
- [ ] Validation results (quick_validate + universal_validate)

### Optional Deliverables
- `references/`: Detailed documentation
- `scripts/`: Automation scripts
- `assets/`: Templates and resources
'''
        },
        'quick_start': {
            'patterns': [r'quick\s*start', r'快速开始', r'getting\s*started'],
            'priority': 'medium',
            'suggestion': 'Add Quick Start section for immediate usability',
            'template': '''
## Quick Start

```bash
# 1. Initialize
python scripts/init.py <args>

# 2. Validate
python scripts/validate.py <path>

# 3. Run
python scripts/run.py <path>
```
'''
        },
        'troubleshooting': {
            'patterns': [r'troubleshoot', r'faq', r'common\s*issues', r'常见问题', r'排障'],
            'priority': 'medium',
            'suggestion': 'Add troubleshooting section for common issues',
            'template': '''
## Troubleshooting

| Issue | Solution |
|-------|----------|
| [Common issue 1] | [Solution] |
| [Common issue 2] | [Solution] |
'''
        },
        'references_navigation': {
            'patterns': [r'references\s*navigation', r'references\s*导航', r'\|\s*文件\s*\|\s*用途'],
            'priority': 'medium',
            'suggestion': 'Add references navigation table',
            'template': '''
## References Navigation

| File | Purpose | When to Read |
|------|---------|--------------|
| `references/xxx.md` | [Purpose] | [Condition] |
'''
        },
        'definition_of_done': {
            'patterns': [r'definition\s*of\s*done', r'dod', r'完成定义', r'必须达标'],
            'priority': 'low',
            'suggestion': 'Add Definition of Done checklist',
            'template': '''
## Definition of Done

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] Validation passed (quick_validate)
- [ ] No project-specific information
'''
        },
        'use_when_in_description': {
            'patterns': [],  # Special check in description
            'priority': 'high',
            'suggestion': 'Add "Use when:" section in description for better triggering',
            'template': None
        },
        'not_for_boundary': {
            'patterns': [r'not\s*for', r'不使用', r'out\s*of\s*scope'],
            'priority': 'low',
            'suggestion': 'Add "Not for:" section to set clear boundaries',
            'template': '''
> **Not for:** [Describe what this skill should NOT be used for]
'''
        }
    }

    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.skill_md = skill_path / 'SKILL.md'
        self.content = ""
        self.frontmatter = {}
        self.body = ""
        self.suggestions: List[UpgradeSuggestion] = []

    def analyze(self) -> List[UpgradeSuggestion]:
        """Analyze skill and generate upgrade suggestions"""
        if not self.skill_md.exists():
            self.suggestions.append(UpgradeSuggestion(
                priority='high',
                category='structure',
                issue='SKILL.md not found',
                suggestion='Create SKILL.md with proper frontmatter'
            ))
            return self.suggestions

        # Read content
        try:
            self.content = self.skill_md.read_text(encoding='utf-8-sig')
        except Exception as e:
            self.suggestions.append(UpgradeSuggestion(
                priority='high',
                category='encoding',
                issue=f'Cannot read SKILL.md: {e}',
                suggestion='Ensure file is UTF-8 encoded'
            ))
            return self.suggestions

        # Parse frontmatter
        self._parse_frontmatter()

        # Check best practices
        self._check_best_practices()

        # Check description quality
        self._check_description_quality()

        # Check resources structure
        self._check_resources()

        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        self.suggestions.sort(key=lambda x: priority_order.get(x.priority, 3))

        return self.suggestions

    def _parse_frontmatter(self):
        """Parse YAML frontmatter"""
        match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n?(.*)', self.content, re.DOTALL)
        if match:
            try:
                import yaml
                self.frontmatter = yaml.safe_load(match.group(1)) or {}
                self.body = match.group(2)
            except Exception:
                self.body = self.content
        else:
            self.body = self.content

    def _check_best_practices(self):
        """Check for best practice patterns in body"""
        body_lower = self.body.lower()

        for name, config in self.BEST_PRACTICE_PATTERNS.items():
            if name == 'use_when_in_description':
                continue  # Handled separately

            patterns = config['patterns']
            found = any(re.search(p, body_lower) for p in patterns)

            if not found and config.get('template'):
                self.suggestions.append(UpgradeSuggestion(
                    priority=config['priority'],
                    category='best_practice',
                    issue=f"Missing: {name.replace('_', ' ').title()}",
                    suggestion=config['suggestion'],
                    code_snippet=config['template']
                ))

    def _check_description_quality(self):
        """Check description for best practices"""
        description = self.frontmatter.get('description', '')
        if not description:
            self.suggestions.append(UpgradeSuggestion(
                priority='high',
                category='frontmatter',
                issue='Missing description in frontmatter',
                suggestion='Add comprehensive description with trigger scenarios'
            ))
            return

        desc_lower = description.lower()

        # Check for "Use when:" section
        if 'use when' not in desc_lower and 'trigger' not in desc_lower:
            self.suggestions.append(UpgradeSuggestion(
                priority='high',
                category='frontmatter',
                issue='Description lacks "Use when:" section',
                suggestion='Add "Use when:" with 3-5 specific trigger scenarios',
                code_snippet='''description: |
  [What this skill does - one sentence]

  Use when:
  - [Trigger scenario 1]
  - [Trigger scenario 2]
  - [Trigger scenario 3]

  Outputs: [What gets produced]
'''
            ))

        # Check for output description
        if not any(kw in desc_lower for kw in ['output', 'produce', 'generate', 'create', '输出']):
            self.suggestions.append(UpgradeSuggestion(
                priority='medium',
                category='frontmatter',
                issue='Description does not describe outputs',
                suggestion='Add output description (e.g., "Outputs: structured report with...")'
            ))

        # Check for "Not for:" section
        if 'not for' not in desc_lower:
            self.suggestions.append(UpgradeSuggestion(
                priority='low',
                category='frontmatter',
                issue='Description lacks "Not for:" boundary',
                suggestion='Add "Not for:" to set clear scope boundaries'
            ))

        # Check for allowed-tools
        if 'allowed-tools' not in self.frontmatter:
            self.suggestions.append(UpgradeSuggestion(
                priority='medium',
                category='frontmatter',
                issue='Missing allowed-tools field',
                suggestion='Add allowed-tools for least-privilege security',
                code_snippet='allowed-tools: [read, write, execute]'
            ))

    def _check_resources(self):
        """Check resources structure"""
        refs_dir = self.skill_path / 'references'
        scripts_dir = self.skill_path / 'scripts'

        # Check references
        if not refs_dir.exists():
            self.suggestions.append(UpgradeSuggestion(
                priority='medium',
                category='structure',
                issue='No references/ directory',
                suggestion='Add references/ for detailed documentation'
            ))
        else:
            ref_files = list(refs_dir.glob('*.md'))
            if len(ref_files) == 0:
                self.suggestions.append(UpgradeSuggestion(
                    priority='low',
                    category='structure',
                    issue='references/ is empty',
                    suggestion='Add reference files for detailed knowledge'
                ))

        # Check if body is too long without references
        body_lines = self.body.count('\n')
        refs_exist = refs_dir.exists() and any(refs_dir.glob('*.md'))

        if body_lines > 300 and not refs_exist:
            self.suggestions.append(UpgradeSuggestion(
                priority='high',
                category='conciseness',
                issue=f'SKILL.md body is long ({body_lines} lines) without references',
                suggestion='Move detailed content to references/ for progressive disclosure'
            ))

    def format_report(self) -> str:
        """Format analysis as human-readable report"""
        lines = []
        lines.append("=" * 70)
        lines.append("🔍 SKILL UPGRADE ANALYSIS")
        lines.append("=" * 70)
        lines.append(f"\nSkill: {self.skill_path.name}")
        lines.append(f"Suggestions: {len(self.suggestions)}")
        lines.append("")

        if not self.suggestions:
            lines.append("✅ No upgrade suggestions - skill follows best practices!")
            return "\n".join(lines)

        # Group by priority
        high = [s for s in self.suggestions if s.priority == 'high']
        medium = [s for s in self.suggestions if s.priority == 'medium']
        low = [s for s in self.suggestions if s.priority == 'low']

        if high:
            lines.append("🔴 HIGH PRIORITY (Must Fix):")
            for s in high:
                lines.append(f"\n  [{s.category}] {s.issue}")
                lines.append(f"  → {s.suggestion}")
                if s.code_snippet:
                    lines.append(f"\n  Suggested template:")
                    for code_line in s.code_snippet.strip().split('\n'):
                        lines.append(f"    {code_line}")
            lines.append("")

        if medium:
            lines.append("🟡 MEDIUM PRIORITY (Should Fix):")
            for s in medium:
                lines.append(f"\n  [{s.category}] {s.issue}")
                lines.append(f"  → {s.suggestion}")
                if s.code_snippet:
                    lines.append(f"\n  Suggested template:")
                    for code_line in s.code_snippet.strip().split('\n'):
                        lines.append(f"    {code_line}")
            lines.append("")

        if low:
            lines.append("🟢 LOW PRIORITY (Nice to Have):")
            for s in low:
                lines.append(f"\n  [{s.category}] {s.issue}")
                lines.append(f"  → {s.suggestion}")
            lines.append("")

        lines.append("=" * 70)
        lines.append("💡 Next Steps:")
        lines.append("  1. Address HIGH priority items first")
        lines.append("  2. Run quick_validate.py after changes")
        lines.append("  3. Run universal_validate.py for portability")
        lines.append("=" * 70)

        return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python upgrade_skill.py <path/to/skill-folder> [--auto-fix]")
        print("\nExamples:")
        print("  python upgrade_skill.py .claude/skills/my-old-skill")
        print("  python upgrade_skill.py .claude/skills/my-old-skill --auto-fix")
        sys.exit(1)

    skill_path = Path(sys.argv[1]).resolve()
    auto_fix = '--auto-fix' in sys.argv

    if not skill_path.exists():
        print(f"❌ Error: Path not found: {skill_path}")
        sys.exit(1)

    if auto_fix:
        print("⚠️  Auto-fix mode is not yet implemented. Showing analysis only.\n")

    upgrader = SkillUpgrader(skill_path)
    suggestions = upgrader.analyze()
    print(upgrader.format_report())

    # Exit code based on high priority issues
    high_priority = [s for s in suggestions if s.priority == 'high']
    sys.exit(1 if high_priority else 0)


if __name__ == "__main__":
    main()

