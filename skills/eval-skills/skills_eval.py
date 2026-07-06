#!/usr/bin/env python3
"""Skill quality assessment report generator for eval-skills."""
import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime, timezone

import argparse
import re

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate skills quality")
    parser.add_argument("--skills-dir", default=str(Path.home() / ".eval-skills" / "skills"), help="Path to skills directory")
    parser.add_argument("--min-score", type=float, default=0.0, help="Minimum score to pass")
    parser.add_argument("--output", choices=["text", "json", "markdown"], default="text", help="Output format")
    parser.add_argument("--export", help="Export report to file")
    return parser.parse_args()

@dataclass
class SkillInfo:
    name: str
    path: Path
    has_skill_md: bool = False
    has_readme_buddy: bool = False
    skill_md_content: str = ""
    file_count: int = 0
    has_scripts: bool = False
    has_dependencies: bool = False
    description_length: int = 0
    version_compliant: bool = False
    description_quality_score: float = 0.0
    
    def __post_init__(self):
        self.file_count = len(list(self.path.glob("*")))
        self.has_scripts = any(self.path.glob("**/*.py")) or any(self.path.glob("**/*.js")) or any(self.path.glob("**/*.ts"))
        
        skill_md_path = self.path / "SKILL.md"
        if skill_md_path.exists():
            self.has_skill_md = True
            try:
                with open(skill_md_path, 'r', encoding='utf-8') as f:
                    self.skill_md_content = f.read()
            except Exception:
                self.skill_md_content = ""

            # Extract description length from frontmatter
            if "description:" in self.skill_md_content:
                try:
                    for line in self.skill_md_content.split('\n'):
                        if line.startswith('description:'):
                            desc = line.replace('description:', '').strip().strip('"').strip("'")
                            self.description_length = len(desc)
                            break
                except (ValueError, IndexError):
                    pass
            
            # Assess description quality
            content_lower = self.skill_md_content.lower()
            has_when_to_use = "when to use" in content_lower or "何时使用" in content_lower
            has_code_example = "```" in self.skill_md_content
            has_parameters = "##" in self.skill_md_content and ("option" in content_lower or "参数" in content_lower)
            self.description_quality_score = sum([has_when_to_use, has_code_example, has_parameters]) / 3.0

            # Assess version compliance
            match = re.search(r'version:\s*(\S+)', self.skill_md_content)
            if match:
                self.version_compliant = bool(re.match(r'^\d+\.\d+\.\d+', match.group(1)))
        
        readme_path = self.path / "README_BUDDY.md"
        self.has_readme_buddy = readme_path.exists()
        
        self.has_dependencies = "require" in self.skill_md_content.lower() or "install" in self.skill_md_content.lower()

def assess_skill(skill_info: SkillInfo) -> Dict:
    """评估单个 skill"""
    score = 0
    # Update max score to include new metrics (5 original + 1 version + 1 description quality = 7)
    # Actually description quality is float 0-1, so let's treat it as 1 point max.
    max_score = 7 
    issues = []
    
    # 1. Has SKILL.md
    if skill_info.has_skill_md:
        score += 1
    else:
        issues.append("Missing SKILL.md")
    
    # 2. Has meaningful description
    if skill_info.description_length > 20:
        score += 1
    else:
        issues.append(f"Description too short ({skill_info.description_length} chars)")
    
    # 3. Has README_BUDDY.md (localization)
    if skill_info.has_readme_buddy:
        score += 1
    else:
        issues.append("Missing README_BUDDY.md (no localization)")
    
    # 4. Directory not empty
    if skill_info.file_count > 1:
        score += 1
    else:
        issues.append("Directory nearly empty")
    
    # 5. Has either documentation or scripts
    if skill_info.has_scripts or skill_info.has_skill_md:
        score += 1
    else:
        issues.append("No documentation or scripts")

    # 6. Version compliance
    if skill_info.version_compliant:
        score += 1
    else:
        issues.append("Version not semver compliant")

    # 7. Description Quality
    score += skill_info.description_quality_score
    if skill_info.description_quality_score < 0.6:
         issues.append("Description quality low (missing usage/examples/params)")
    
    completion_rate = score / max_score
    
    return {
        "skillId": skill_info.name,
        "path": str(skill_info.path),
        "score": round(score, 2),
        "maxScore": max_score,
        "completionRate": round(completion_rate, 4),
        "issues": issues,
        "metrics": {
            "has_skill_md": skill_info.has_skill_md,
            "has_readme_buddy": skill_info.has_readme_buddy,
            "has_scripts": skill_info.has_scripts,
            "file_count": skill_info.file_count,
            "description_length": skill_info.description_length,
            "has_dependencies": skill_info.has_dependencies,
            "version_compliant": skill_info.version_compliant,
            "description_quality": round(skill_info.description_quality_score, 2)
        }
    }

def main():
    args = parse_args()
    skills_dir = Path(args.skills_dir)

    if not skills_dir.exists():
        print(f"Error: {skills_dir} not found", file=sys.stderr)
        sys.exit(1)
    
    # Scan all skills
    skills_list = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if skill_dir.is_dir() and skill_dir.name != "eval-skills" and not skill_dir.name.startswith("."):
            skill_info = SkillInfo(
                name=skill_dir.name,
                path=skill_dir
            )
            skills_list.append(skill_info)
    
    if args.output == "text":
        print(f"Found {len(skills_list)} skills in {skills_dir}\n")
        print("=" * 80)
    
    # Assess all skills
    assessments = []
    total_score = 0
    for skill in skills_list:
        assessment = assess_skill(skill)
        assessments.append(assessment)
        total_score += assessment["completionRate"]
        
        if args.output == "text":
            status = "✓" if assessment["completionRate"] >= 0.8 else "✗" if assessment["completionRate"] < 0.4 else "~"
            print(f"{status} {skill.name:30s} {assessment['score']}/{assessment['maxScore']} ({assessment['completionRate']:.0%})")
            if assessment["issues"]:
                for issue in assessment["issues"]:
                    print(f"  ⚠ {issue}")

    avg_completion = total_score / len(skills_list) if skills_list else 0
    
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "totalSkills": len(skills_list),
            "averageCompletionRate": round(avg_completion, 4),
            "highQualityCount": sum(1 for a in assessments if a['completionRate'] >= 0.8),
            "mediumQualityCount": sum(1 for a in assessments if 0.4 <= a['completionRate'] < 0.8),
            "lowQualityCount": sum(1 for a in assessments if a['completionRate'] < 0.4)
        },
        "assessments": assessments
    }

    if args.output == "text":
        print("=" * 80)
        print(f"\nSummary:")
        print(f"  Total Skills: {len(skills_list)}")
        print(f"  Average Completion Rate: {avg_completion:.1%}")
        print(f"  High Quality (≥80%): {report['summary']['highQualityCount']}")
        print(f"  Medium Quality (40-80%): {report['summary']['mediumQualityCount']}")
        print(f"  Low Quality (<40%): {report['summary']['lowQualityCount']}")
    elif args.output == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.output == "markdown":
        print(f"# Skills Quality Report")
        print(f"\n**Date:** {report['timestamp']}")
        print(f"\n## Summary")
        print(f"- **Total Skills:** {report['summary']['totalSkills']}")
        print(f"- **Average Completion:** {report['summary']['averageCompletionRate']:.1%}")
        print(f"\n## Details")
        print("| Skill | Score | Rate | Issues |")
        print("|-------|-------|------|--------|")
        for a in assessments:
            issues = "<br>".join(a["issues"]) if a["issues"] else "None"
            print(f"| {a['skillId']} | {a['score']}/{a['maxScore']} | {a['completionRate']:.0%} | {issues} |")

    if args.export:
        with open(args.export, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        if args.output == "text":
            print(f"\nReport exported to {args.export}")

    if args.min_score > 0 and avg_completion < args.min_score:
        sys.exit(1)
