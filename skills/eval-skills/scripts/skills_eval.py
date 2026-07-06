#!/usr/bin/env python3
"""Skill quality assessment report generator for eval-skills."""
import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime, timezone

SKILLS_DIR = Path.home() / ".eval-skills" / "skills"

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
    
    def __post_init__(self):
        self.file_count = len(list(self.path.glob("*")))
        self.has_scripts = any(self.path.glob("**/*.py")) or any(self.path.glob("**/*.js"))
        
        skill_md_path = self.path / "SKILL.md"
        if skill_md_path.exists():
            self.has_skill_md = True
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                self.skill_md_content = f.read()
                # Extract description length from frontmatter
                if "description:" in self.skill_md_content:
                    try:
                        lines = self.skill_md_content.split('\n')
                        for line in lines:
                            if line.startswith('description:'):
                                desc = line.replace('description:', '').strip().strip('"').strip("'")
                                self.description_length = len(desc)
                                break
                    except (ValueError, IndexError):
                        pass  # Skip malformed description lines
        
        readme_path = self.path / "README_BUDDY.md"
        self.has_readme_buddy = readme_path.exists()
        
        self.has_dependencies = "require" in self.skill_md_content.lower() or "install" in self.skill_md_content.lower()

def assess_skill(skill_info: SkillInfo) -> Dict:
    """评估单个 skill"""
    score = 0
    max_score = 5
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
    
    completion_rate = score / max_score
    
    return {
        "skillId": skill_info.name,
        "path": str(skill_info.path),
        "score": score,
        "maxScore": max_score,
        "completionRate": completion_rate,
        "issues": issues,
        "metrics": {
            "has_skill_md": skill_info.has_skill_md,
            "has_readme_buddy": skill_info.has_readme_buddy,
            "has_scripts": skill_info.has_scripts,
            "file_count": skill_info.file_count,
            "description_length": skill_info.description_length,
            "has_dependencies": skill_info.has_dependencies
        }
    }

def main():
    if not SKILLS_DIR.exists():
        print(f"Error: {SKILLS_DIR} not found", file=sys.stderr)
        sys.exit(1)
    
    # Scan all skills
    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if skill_dir.is_dir() and skill_dir.name != "eval-skills":
            skill_info = SkillInfo(
                name=skill_dir.name,
                path=skill_dir
            )
            skills.append(skill_info)
    
    print(f"Found {len(skills)} skills\n")
    print("=" * 80)
    
    # Assess all skills
    assessments = []
    total_score = 0
    for skill in skills:
        assessment = assess_skill(skill)
        assessments.append(assessment)
        total_score += assessment["completionRate"]
        
        status = "✓" if assessment["completionRate"] >= 0.8 else "✗" if assessment["completionRate"] < 0.4 else "~"
        print(f"{status} {skill.name:30s} {assessment['score']}/{assessment['maxScore']} ({assessment['completionRate']:.0%})")
        if assessment["issues"]:
            for issue in assessment["issues"]:
                print(f"  ⚠ {issue}")
    
    print("=" * 80)
    avg_completion = total_score / len(skills) if skills else 0
    print(f"\nSummary:")
    print(f"  Total Skills: {len(skills)}")
    print(f"  Average Completion Rate: {avg_completion:.1%}")
    print(f"  High Quality (≥80%): {sum(1 for a in assessments if a['completionRate'] >= 0.8)}")
    print(f"  Medium Quality (40-80%): {sum(1 for a in assessments if 0.4 <= a['completionRate'] < 0.8)}")
    print(f"  Low Quality (<40%): {sum(1 for a in assessments if a['completionRate'] < 0.4)}")
    
    # Output JSON report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "totalSkills": len(skills),
            "averageCompletionRate": round(avg_completion, 4),
            "highQualityCount": sum(1 for a in assessments if a['completionRate'] >= 0.8),
            "mediumQualityCount": sum(1 for a in assessments if 0.4 <= a['completionRate'] < 0.8),
            "lowQualityCount": sum(1 for a in assessments if a['completionRate'] < 0.4)
        },
        "assessments": assessments
    }
    
    print("\n" + json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
