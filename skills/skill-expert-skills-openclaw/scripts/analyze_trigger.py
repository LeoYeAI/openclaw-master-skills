#!/usr/bin/env python3
"""
Trigger Analyzer - Analyze and improve skill description for better triggering

Features:
- Extract trigger keywords from description
- Suggest missing trigger scenarios
- Generate alternative phrasings
- Score trigger coverage

Usage:
    python analyze_trigger.py <path/to/skill-folder>
    python analyze_trigger.py <path/to/skill-folder> --suggest
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


_configure_stdio()


# Common trigger patterns by category
TRIGGER_CATEGORIES = {
    "action_verbs": [
        "create",
        "build",
        "generate",
        "make",
        "design",
        "develop",
        "edit",
        "modify",
        "update",
        "change",
        "fix",
        "repair",
        "analyze",
        "review",
        "check",
        "validate",
        "verify",
        "audit",
        "convert",
        "transform",
        "export",
        "import",
        "migrate",
        "optimize",
        "improve",
        "enhance",
        "refactor",
        "debug",
        "troubleshoot",
        "diagnose",
        "deploy",
        "publish",
        "release",
        "package",
    ],
    "artifact_types": [
        "file",
        "document",
        "code",
        "script",
        "function",
        "class",
        "api",
        "endpoint",
        "service",
        "component",
        "module",
        "config",
        "configuration",
        "settings",
        "template",
        "report",
        "dashboard",
        "chart",
        "diagram",
        "test",
        "spec",
        "documentation",
        "readme",
        ".md",
        ".py",
        ".js",
        ".ts",
        ".json",
        ".yaml",
        ".html",
        ".css",
        "pdf",
        "docx",
        "pptx",
        "xlsx",
    ],
    "context_indicators": [
        "skill",
        "skills",
        "SKILL.md",
        ".claude/skills",
        "frontmatter",
        "description",
        "trigger",
        "references/",
        "scripts/",
        "assets/",
        "validate",
        "package",
        "distribute",
    ],
}


def parse_frontmatter(content: str) -> Dict:
    """Parse YAML frontmatter"""
    try:
        import yaml
    except ImportError:
        return {}

    match = re.match(r"^---\r?\n(.*?)\r?\n---", content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)) or {}
        except Exception:
            pass
    return {}


def extract_keywords(description: str) -> Set[str]:
    """Extract meaningful keywords from description"""
    # Normalize
    text = description.lower()

    # Remove common stop words
    stop_words = {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "to",
        "for",
        "with",
        "from",
        "by",
        "on",
        "in",
        "at",
        "of",
        "and",
        "or",
        "but",
        "if",
        "when",
        "where",
        "how",
        "what",
        "can",
        "could",
        "will",
        "would",
        "should",
        "may",
        "might",
        "use",
        "used",
        "using",
        "not",
    }

    # Extract words
    words = re.findall(r"\b[a-z][a-z0-9_-]*\b", text)
    words.extend(re.findall(r"\.[a-z]+", text))  # file extensions

    # Filter
    keywords = set()
    for word in words:
        if word not in stop_words and len(word) > 2:
            keywords.add(word)

    return keywords


def analyze_coverage(keywords: Set[str]) -> Dict[str, List[str]]:
    """Analyze keyword coverage against trigger categories"""
    coverage = {}

    for category, patterns in TRIGGER_CATEGORIES.items():
        matched = []
        for pattern in patterns:
            pattern_lower = pattern.lower()
            if any(pattern_lower in kw or kw in pattern_lower for kw in keywords):
                matched.append(pattern)
        coverage[category] = matched

    return coverage


def suggest_triggers(skill_name: str, current_keywords: Set[str]) -> List[str]:
    """Suggest additional trigger phrases based on skill name"""
    suggestions = []

    # Parse skill name
    name_parts = skill_name.replace("-", " ").split()

    # Generate suggestions based on name
    if "skill" in name_parts or "skills" in name_parts:
        suggestions.extend(
            [
                "Creating a new skill",
                "How to write a skill",
                "Make a Claude skill",
                "Build skill for...",
                "创建一个新的skill",
                "写一个skill",
            ]
        )

    if "validate" in name_parts or "validator" in name_parts:
        suggestions.extend(
            ["Check if skill is valid", "Validate my skill structure", "验证skill格式"]
        )

    if "expert" in name_parts:
        suggestions.extend(["Best practices for...", "How to optimize...", "最佳实践"])

    # Common patterns not in keywords
    if "optimize" not in current_keywords and "optimization" not in current_keywords:
        suggestions.append("Optimize/improve existing skill")

    if "debug" not in current_keywords and "troubleshoot" not in current_keywords:
        suggestions.append("Debug/troubleshoot skill issues")

    return suggestions


def calculate_score(
    coverage: Dict[str, List[str]], description: str
) -> Tuple[int, str]:
    """Calculate trigger quality score (0-100)"""
    score = 0
    feedback = []

    # Action verbs (30 points)
    action_count = len(coverage.get("action_verbs", []))
    if action_count >= 5:
        score += 30
    elif action_count >= 3:
        score += 20
    elif action_count >= 1:
        score += 10
    else:
        feedback.append("Add more action verbs (create, analyze, validate, etc.)")

    # Artifact types (20 points)
    artifact_count = len(coverage.get("artifact_types", []))
    if artifact_count >= 3:
        score += 20
    elif artifact_count >= 1:
        score += 10
    else:
        feedback.append("Mention specific file types or artifacts")

    # Context indicators (20 points)
    context_count = len(coverage.get("context_indicators", []))
    if context_count >= 3:
        score += 20
    elif context_count >= 1:
        score += 10

    # "Use when:" section (15 points)
    if "use when" in description.lower():
        score += 15
    else:
        feedback.append("Add 'Use when:' section with bullet points")

    # "Not for:" boundary (10 points)
    if "not for" in description.lower():
        score += 10
    else:
        feedback.append("Add 'Not for:' to set scope boundaries")

    # Length check (5 points)
    desc_len = len(description)
    if 200 <= desc_len <= 800:
        score += 5
    elif desc_len < 100:
        feedback.append("Description is too short - add more trigger scenarios")
    elif desc_len > 900:
        feedback.append("Description is too long - consider condensing")

    return min(score, 100), "; ".join(feedback) if feedback else "Good coverage!"


def format_report(
    skill_name: str,
    description: str,
    keywords: Set[str],
    coverage: Dict[str, List[str]],
    score: int,
    feedback: str,
    suggestions: List[str],
) -> str:
    """Format analysis as report"""
    lines = []
    lines.append("=" * 70)
    lines.append("🎯 TRIGGER ANALYSIS REPORT")
    lines.append("=" * 70)
    lines.append(f"\nSkill: {skill_name}")
    lines.append(f"Description length: {len(description)} chars")

    # Score
    score_bar = "█" * (score // 10) + "░" * (10 - score // 10)
    if score >= 80:
        score_label = "Excellent"
    elif score >= 60:
        score_label = "Good"
    elif score >= 40:
        score_label = "Fair"
    else:
        score_label = "Needs Work"
    lines.append(f"\n📊 Trigger Score: {score}/100 {score_bar} ({score_label})")

    if feedback:
        lines.append(f"   Feedback: {feedback}")

    # Coverage breakdown
    lines.append("\n📌 KEYWORD COVERAGE:")
    for category, matched in coverage.items():
        category_name = category.replace("_", " ").title()
        if matched:
            lines.append(f"   ✅ {category_name}: {', '.join(matched[:8])}")
            if len(matched) > 8:
                lines.append(f"      ...and {len(matched) - 8} more")
        else:
            lines.append(f"   ⚠️  {category_name}: (none detected)")

    # Extracted keywords
    lines.append(f"\n🔑 EXTRACTED KEYWORDS ({len(keywords)}):")
    sorted_kw = sorted(keywords)
    for i in range(0, len(sorted_kw), 8):
        chunk = sorted_kw[i : i + 8]
        lines.append(f"   {', '.join(chunk)}")

    # Suggestions
    if suggestions:
        lines.append("\n💡 SUGGESTED TRIGGER PHRASES:")
        for i, suggestion in enumerate(suggestions[:6], 1):
            lines.append(f'   {i}. "{suggestion}"')

    lines.append("\n" + "=" * 70)
    lines.append("📝 IMPROVEMENT TIPS:")
    lines.append("   1. Include 3-5 realistic 'Use when:' scenarios")
    lines.append("   2. Use action verbs users would actually say")
    lines.append("   3. Mention specific file types/artifacts")
    lines.append("   4. Add 'Not for:' to prevent false triggers")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_trigger.py <path/to/skill-folder>")
        print("\nAnalyzes skill description for trigger keyword coverage")
        sys.exit(1)

    skill_path = Path(sys.argv[1]).resolve()
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        sys.exit(1)

    try:
        content = skill_md.read_text(encoding="utf-8-sig")
    except Exception as e:
        print(f"❌ Error reading SKILL.md: {e}")
        sys.exit(1)

    frontmatter = parse_frontmatter(content)
    description = frontmatter.get("description", "")

    if not description:
        print("❌ Error: No description found in frontmatter")
        sys.exit(1)

    keywords = extract_keywords(description)
    coverage = analyze_coverage(keywords)
    score, feedback = calculate_score(coverage, description)
    suggestions = suggest_triggers(skill_path.name, keywords)

    report = format_report(
        skill_path.name, description, keywords, coverage, score, feedback, suggestions
    )
    print(report)

    sys.exit(0 if score >= 60 else 1)


if __name__ == "__main__":
    main()
