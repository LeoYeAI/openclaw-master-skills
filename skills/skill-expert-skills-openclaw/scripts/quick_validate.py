#!/usr/bin/env python3
"""
Enhanced skill validation script with quality diagnostics
Features:
- Structure validation (frontmatter, naming, etc.)
- Conciseness check (< 500 lines recommended, < 800 lines max)
- Quality scoring (0-100)
- Actionable recommendations
- Resource statistics (references, scripts, assets)
"""

import sys
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Configure stdout/stderr encoding for Windows
def _configure_stdio() -> None:
    """Ensure UTF-8 encoding for stdout/stderr on Windows"""
    import sys
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            # Some environments don't support reconfigure()
            pass

_configure_stdio()

# Optional dependency: PyYAML
try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

# Conciseness thresholds for SKILL.md
SKILL_LINES_EXCELLENT = 200  # Excellent: very concise
SKILL_LINES_GOOD = 350       # Good: reasonably concise
SKILL_LINES_WARN = 500       # Soft limit: trigger warning
SKILL_LINES_ERROR = 800      # Hard limit: trigger error


class SkillQualityReport:
    """Quality report for a skill"""

    def __init__(self):
        self.valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.recommendations: List[str] = []
        self.metrics: Dict[str, Any] = {}
        self.score = 0

    def add_error(self, message: str):
        self.valid = False
        self.errors.append(f"❌ ERROR: {message}")

    def add_warning(self, message: str):
        self.warnings.append(f"⚠️  WARNING: {message}")

    def add_recommendation(self, message: str):
        self.recommendations.append(f"💡 RECOMMENDATION: {message}")

    def format_output(self, verbose: bool = False) -> str:
        """Format report as human-readable text"""
        lines = []

        # Header
        if self.valid:
            lines.append("=" * 70)
            lines.append("✅ SKILL VALIDATION PASSED")
            lines.append("=" * 70)
        else:
            lines.append("=" * 70)
            lines.append("❌ SKILL VALIDATION FAILED")
            lines.append("=" * 70)

        lines.append("")

        # Quality Score
        if self.valid:
            score_bar = self._get_score_bar(self.score)
            score_label = self._get_score_label(self.score)
            lines.append(f"📊 Quality Score: {self.score}/100 {score_bar} ({score_label})")
            lines.append("")

        # Metrics
        if self.metrics and verbose:
            lines.append("📈 Metrics:")
            for key, value in self.metrics.items():
                lines.append(f"   • {key}: {value}")
            lines.append("")

        # Errors
        if self.errors:
            lines.append("🔴 Errors (Must Fix):")
            for error in self.errors:
                lines.append(f"   {error}")
            lines.append("")

        # Warnings
        if self.warnings:
            lines.append("🟡 Warnings (Should Fix):")
            for warning in self.warnings:
                lines.append(f"   {warning}")
            lines.append("")

        # Recommendations
        if self.recommendations:
            lines.append("💡 Recommendations (Nice to Have):")
            for rec in self.recommendations:
                lines.append(f"   {rec}")
            lines.append("")

        # Summary
        if self.valid:
            lines.append("=" * 70)
            lines.append("✨ Summary:")
            lines.append(f"   Errors: {len(self.errors)}")
            lines.append(f"   Warnings: {len(self.warnings)}")
            lines.append(f"   Recommendations: {len(self.recommendations)}")
            if self.score >= 90:
                lines.append("   Status: 🏆 Excellent - Production Ready")
            elif self.score >= 75:
                lines.append("   Status: ✅ Good - Minor improvements suggested")
            elif self.score >= 60:
                lines.append("   Status: ⚠️  Fair - Consider improvements")
            else:
                lines.append("   Status: ⚠️  Needs Improvement")
            lines.append("=" * 70)

        return "\n".join(lines)

    def _get_score_bar(self, score: int) -> str:
        """Generate visual score bar"""
        filled = int(score / 10)
        empty = 10 - filled
        return "█" * filled + "░" * empty

    def _get_score_label(self, score: int) -> str:
        """Get score label"""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        else:
            return "Needs Improvement"


def count_resources(skill_path: Path) -> Dict[str, int]:
    """Count resource files in references/, scripts/, assets/"""
    counts = {
        'references': 0,
        'scripts': 0,
        'assets': 0
    }

    for dir_name in ['references', 'scripts', 'assets']:
        dir_path = skill_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            # Count non-hidden files (excluding __pycache__, etc.)
            counts[dir_name] = len([
                f for f in dir_path.rglob('*')
                if f.is_file()
                and not f.name.startswith('.')
                and '__pycache__' not in str(f)
            ])

    return counts


def check_problematic_special_chars(content: str) -> List[str]:
    """Check for special characters in backticks that may cause parsing issues"""
    issues = []

    # Pattern to find single special characters in backticks
    # These can be misinterpreted as bash commands by Claude Code
    problematic_patterns = [
        (r'`!`', 'exclamation mark (!)', 'non-null assertion'),
        (r'`\$`', 'dollar sign ($)', 'variable prefix'),
        (r'`#`', 'hash (#)', 'comment marker'),
        (r'`\|`', 'pipe (|)', 'vertical bar'),
    ]

    for pattern, char_name, replacement in problematic_patterns:
        if re.search(pattern, content):
            issues.append(
                f"Found {char_name} in backticks which may cause parsing errors. "
                f"Use '{replacement}' instead."
            )

    return issues


def analyze_description_quality(description: str) -> Tuple[int, List[str]]:
    """Analyze description quality and return score + suggestions"""
    score = 0
    suggestions = []

    # Check length (should be descriptive but not too long)
    desc_len = len(description)
    if 100 <= desc_len <= 800:
        score += 20
    elif desc_len < 100:
        suggestions.append("Description is quite short. Consider adding more trigger scenarios.")
    elif desc_len > 800:
        suggestions.append("Description is very long. Consider condensing to key trigger scenarios.")
    else:
        score += 10

    # Check for "Use when:" section (good practice)
    if "use when" in description.lower() or "trigger" in description.lower():
        score += 25
    else:
        suggestions.append("Add 'Use when:' section to clarify trigger scenarios.")

    # Check for output description
    if any(keyword in description.lower() for keyword in ['output', 'produce', 'generate', 'create']):
        score += 15
    else:
        suggestions.append("Describe what the skill outputs or produces.")

    # Check for specific examples/keywords
    if description.count('\n-') >= 3 or description.count('\n*') >= 3:
        score += 20  # Has bullet points (likely detailed)
    else:
        suggestions.append("Use bullet points to list specific trigger scenarios (3-5 recommended).")

    # Check for "Not for:" section (good boundary setting)
    if "not for" in description.lower():
        score += 20
    else:
        suggestions.append("Consider adding 'Not for:' section to set clear boundaries.")

    return score, suggestions


def calculate_quality_score(report: SkillQualityReport,
                           skill_path: Path,
                           frontmatter: dict,
                           total_lines: int) -> int:
    """Calculate overall quality score (0-100)"""
    score = 0

    # 1. Conciseness Score (30 points)
    if total_lines <= SKILL_LINES_EXCELLENT:
        score += 30
        report.metrics['conciseness'] = f"Excellent ({total_lines} lines, {int(total_lines/SKILL_LINES_WARN*100)}% of threshold)"
    elif total_lines <= SKILL_LINES_GOOD:
        score += 25
        report.metrics['conciseness'] = f"Very Good ({total_lines} lines, {int(total_lines/SKILL_LINES_WARN*100)}% of threshold)"
    elif total_lines < SKILL_LINES_WARN:
        score += 20
        report.metrics['conciseness'] = f"Good ({total_lines} lines, {int(total_lines/SKILL_LINES_WARN*100)}% of threshold)"
    elif total_lines < SKILL_LINES_ERROR:
        score += 10
        report.metrics['conciseness'] = f"Acceptable ({total_lines} lines, {int(total_lines/SKILL_LINES_WARN*100)}% of threshold)"
        report.add_warning(f"SKILL.md is approaching length limit ({total_lines}/{SKILL_LINES_ERROR} lines)")
    else:
        score += 0
        report.metrics['conciseness'] = f"Too Long ({total_lines} lines exceeds {SKILL_LINES_ERROR} limit)"

    # 2. Description Quality (25 points)
    desc_score, desc_suggestions = analyze_description_quality(frontmatter.get('description', ''))
    score += desc_score
    report.metrics['description_quality'] = f"{desc_score}/25 points"
    for suggestion in desc_suggestions:
        report.add_recommendation(suggestion)

    # 3. Best Practices (25 points)
    best_practices_score = 0

    # Has allowed-tools (5 points)
    if 'allowed-tools' in frontmatter:
        best_practices_score += 5
    else:
        report.add_warning("'allowed-tools' is missing. Recommend specifying minimal tools for security.")

    # Has references/ directory (10 points)
    resources = count_resources(skill_path)
    if resources['references'] > 0:
        best_practices_score += 10
        report.metrics['references_count'] = resources['references']
    else:
        report.add_recommendation("Consider adding references/ for detailed knowledge/checklists.")

    # Has scripts/ directory (5 points)
    if resources['scripts'] > 0:
        best_practices_score += 5
        report.metrics['scripts_count'] = resources['scripts']

    # Directory name matches skill name (5 points)
    if skill_path.name == frontmatter.get('name', ''):
        best_practices_score += 5

    score += best_practices_score
    report.metrics['best_practices'] = f"{best_practices_score}/25 points"

    # 4. Structure Quality (20 points)
    structure_score = 0

    # Read SKILL.md content for structure analysis
    skill_md = skill_path / 'SKILL.md'
    content = skill_md.read_text(encoding="utf-8-sig").lower()

    # Has decision tree or workflow (8 points)
    if 'decision tree' in content or 'workflow' in content or '##' in content:
        structure_score += 8
    else:
        report.add_recommendation("Add a decision tree or workflow section for clarity.")

    # Has output contract/format (7 points)
    if 'output' in content and ('contract' in content or 'format' in content or 'structure' in content):
        structure_score += 7
    else:
        report.add_recommendation("Define clear output contract/format for predictability.")

    # Has troubleshooting/FAQ (5 points)
    if 'troubleshoot' in content or 'faq' in content or 'common' in content:
        structure_score += 5

    score += structure_score
    report.metrics['structure'] = f"{structure_score}/20 points"

    return min(score, 100)  # Cap at 100


def validate_skill(skill_path: str, verbose: bool = False) -> Tuple[bool, str]:
    """Enhanced validation with quality diagnostics"""
    skill_path = Path(skill_path)
    report = SkillQualityReport()

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        report.add_error("SKILL.md not found")
        return False, report.format_output(verbose)

    # Read and validate encoding
    try:
        content = skill_md.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        report.add_error("SKILL.md must be UTF-8 encoded (optionally with BOM)")
        return False, report.format_output(verbose)

    # Check frontmatter
    if not content.startswith('---'):
        report.add_error("No YAML frontmatter found")
        return False, report.format_output(verbose)

    # Extract frontmatter
    match = re.match(r'^---\r?\n(.*?)\r?\n---', content, re.DOTALL)
    if not match:
        report.add_error("Invalid frontmatter format")
        return False, report.format_output(verbose)

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    if yaml is None:
        report.add_error(
            "Missing dependency: PyYAML. "
            "Install with: python -m pip install -r .claude/skills/skill-expert-skills/scripts/requirements.txt"
        )
        return False, report.format_output(verbose)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            report.add_error("Frontmatter must be a YAML dictionary")
            return False, report.format_output(verbose)
    except yaml.YAMLError as e:
        report.add_error(f"Invalid YAML in frontmatter: {e}")
        return False, report.format_output(verbose)

    # Validate frontmatter fields
    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        report.add_error(
            f"Unexpected key(s) in frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        report.add_error("Missing 'name' in frontmatter")
    if 'description' not in frontmatter:
        report.add_error("Missing 'description' in frontmatter")

    # If errors so far, return early
    if report.errors:
        return False, report.format_output(verbose)

    # Validate name
    name = frontmatter.get('name', '').strip()
    if name:
        if not isinstance(name, str):
            report.add_error(f"Name must be a string, got {type(name).__name__}")
        elif not re.match(r'^[a-z0-9-]+$', name):
            report.add_error(f"Name '{name}' should be hyphen-case (lowercase, digits, hyphens only)")
        elif name.startswith('-') or name.endswith('-') or '--' in name:
            report.add_error(f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens")
        elif len(name) > 64:
            report.add_error(f"Name is too long ({len(name)} chars). Max 64 chars.")

        # Directory name check
        if skill_path.name != name:
            report.add_error(f"Directory name '{skill_path.name}' must match frontmatter name '{name}'")

    # Validate description
    description = frontmatter.get('description', '').strip()
    if description:
        if not isinstance(description, str):
            report.add_error(f"Description must be a string, got {type(description).__name__}")
        elif '<' in description or '>' in description:
            report.add_error("Description cannot contain angle brackets (< or >)")
        elif len(description) > 1024:
            report.add_error(f"Description is too long ({len(description)} chars). Max 1024 chars.")

    # If errors, return early
    if report.errors:
        return False, report.format_output(verbose)

    # Calculate metrics
    total_lines = content.count('\n') + 1
    report.metrics['skill_md_lines'] = total_lines

    # Count resources
    resources = count_resources(skill_path)

    # Hard error: too long
    if total_lines >= SKILL_LINES_ERROR:
        report.add_error(
            f"SKILL.md is too long ({total_lines} lines, max {SKILL_LINES_ERROR}). "
            f"Move detailed content to references/"
        )
        return False, report.format_output(verbose)

    # Check for problematic special characters in backticks
    problematic_chars = check_problematic_special_chars(content)
    for char_issue in problematic_chars:
        report.add_warning(char_issue)

    # Calculate quality score
    report.score = calculate_quality_score(report, skill_path, frontmatter, total_lines)

    # Add resource-based recommendations
    if resources['references'] == 0:
        report.add_recommendation("Add references/ directory for detailed documentation")
    elif resources['references'] >= 10:
        report.add_recommendation(f"Many reference files ({resources['references']}). Ensure good navigation in SKILL.md")

    if resources['scripts'] == 0 and total_lines > 300:
        report.add_recommendation("Consider extracting repetitive logic into scripts/")

    # Add score-based recommendations
    if report.score < 90:
        if report.score < 75:
            report.add_recommendation("Review examples.md in references/ for best practices")
        report.add_recommendation("Run universal_validate.py to check portability")

    return report.valid, report.format_output(verbose)


if __name__ == "__main__":
    # Parse arguments
    verbose = False
    skill_dir = None

    for arg in sys.argv[1:]:
        if arg in ['-v', '--verbose']:
            verbose = True
        elif arg in ['-h', '--help']:
            print("Usage: python quick_validate.py <skill_directory> [--verbose|-v]")
            print("\nOptions:")
            print("  -v, --verbose    Show detailed metrics")
            print("  -h, --help       Show this help message")
            sys.exit(0)
        else:
            skill_dir = arg

    if not skill_dir:
        print("Usage: python quick_validate.py <skill_directory> [--verbose|-v]")
        sys.exit(1)

    valid, message = validate_skill(skill_dir, verbose=verbose)
    print(message)
    sys.exit(0 if valid else 1)
