#!/usr/bin/env python3
"""
Agent Avengers - Consolidate Script
에이전트 결과 수집, 검증, 통합
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

WORKSPACE = os.environ.get("AVENGERS_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
MISSION_DIR = Path(WORKSPACE) / "avengers-missions"


def load_mission(mission_id: str) -> tuple:
    """미션 및 실행 계획 로드"""
    mission_path = MISSION_DIR / mission_id
    
    with open(mission_path / "mission.json") as f:
        mission = json.load(f)
    
    with open(mission_path / "execution_plan.json") as f:
        plan = json.load(f)
    
    return mission, plan


def collect_outputs(mission_path: Path, plan: dict) -> list:
    """에이전트 출력 수집"""
    outputs_dir = mission_path / "outputs"
    results = []
    
    for cmd in plan.get("commands", []):
        agent_id = cmd["agent_id"]
        output_file = outputs_dir / f"{agent_id}.md"
        
        if output_file.exists():
            with open(output_file) as f:
                content = f.read()
            
            results.append({
                "agent_id": agent_id,
                "status": "completed",
                "content": content,
                "file": str(output_file),
                "size": len(content)
            })
        else:
            results.append({
                "agent_id": agent_id,
                "status": "missing",
                "content": None,
                "file": str(output_file),
                "size": 0
            })
    
    return results


def validate_outputs(results: list) -> dict:
    """출력 검증"""
    validation = {
        "total": len(results),
        "completed": 0,
        "missing": 0,
        "empty": 0,
        "issues": []
    }
    
    for r in results:
        if r["status"] == "missing":
            validation["missing"] += 1
            validation["issues"].append(f"누락: {r['agent_id']}")
        elif r["size"] == 0:
            validation["empty"] += 1
            validation["issues"].append(f"빈 파일: {r['agent_id']}")
        else:
            validation["completed"] += 1
    
    validation["success"] = validation["completed"] == validation["total"]
    
    return validation


def generate_summary(mission: dict, results: list, validation: dict) -> str:
    """통합 리포트 생성"""
    
    report = f"""# 🦸 Avengers Mission Report

## 미션 정보
- **ID:** {mission['id']}
- **태스크:** {mission['task']}
- **생성:** {mission['created_at']}
- **완료:** {datetime.now().isoformat()}

## 실행 결과
- **총 에이전트:** {validation['total']}
- **완료:** {validation['completed']}
- **누락:** {validation['missing']}
- **빈 결과:** {validation['empty']}
- **성공 여부:** {'✅ 성공' if validation['success'] else '⚠️ 일부 실패'}

"""

    if validation["issues"]:
        report += "### ⚠️ 이슈\n"
        for issue in validation["issues"]:
            report += f"- {issue}\n"
        report += "\n"

    report += "---\n\n## 에이전트별 결과\n\n"
    
    for r in results:
        if r["status"] == "completed" and r["content"]:
            report += f"### {r['agent_id']}\n\n"
            report += r["content"]
            report += "\n\n---\n\n"
        else:
            report += f"### {r['agent_id']}\n\n"
            report += f"*결과 없음 ({r['status']})*\n\n---\n\n"
    
    report += f"""
## 메타데이터

```json
{json.dumps({
    "mission_id": mission["id"],
    "completed_at": datetime.now().isoformat(),
    "validation": validation
}, indent=2, ensure_ascii=False)}
```
"""
    
    return report


def update_mission_status(mission_path: Path, status: str, updates: dict = None):
    """미션 상태 업데이트"""
    with open(mission_path / "mission.json") as f:
        mission = json.load(f)
    
    mission["status"] = status
    mission["completed_at"] = datetime.now().isoformat()
    
    if updates:
        mission.update(updates)
    
    with open(mission_path / "mission.json", "w") as f:
        json.dump(mission, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Agent Avengers - Consolidate")
    parser.add_argument("--mission", "-m", required=True, help="미션 ID")
    parser.add_argument("--output", "-o", help="출력 파일 경로")
    parser.add_argument("--force", "-f", action="store_true", help="미완료 에이전트 무시")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 출력")
    
    args = parser.parse_args()
    
    try:
        mission, plan = load_mission(args.mission)
    except FileNotFoundError:
        print(f"❌ 미션을 찾을 수 없습니다: {args.mission}")
        sys.exit(1)
    
    mission_path = Path(mission["path"])
    
    print(f"\n🔧 결과 수집 중: {args.mission}")
    
    # 결과 수집
    results = collect_outputs(mission_path, plan)
    
    # 검증
    validation = validate_outputs(results)
    
    print(f"   완료: {validation['completed']}/{validation['total']}")
    
    if not validation["success"] and not args.force:
        print("\n⚠️  일부 에이전트가 완료되지 않았습니다:")
        for issue in validation["issues"]:
            print(f"   - {issue}")
        print("\n   --force 옵션으로 강제 통합 가능")
        sys.exit(1)
    
    # 리포트 생성
    report = generate_summary(mission, results, validation)
    
    # 저장
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = mission_path / "FINAL_REPORT.md"
    
    with open(output_path, "w") as f:
        f.write(report)
    
    # 상태 업데이트
    update_mission_status(mission_path, "completed", {
        "validation": validation
    })
    
    if args.json:
        print(json.dumps({
            "mission_id": mission["id"],
            "report_path": str(output_path),
            "validation": validation
        }, indent=2, ensure_ascii=False))
    else:
        print(f"\n✅ 통합 완료!")
        print(f"📄 리포트: {output_path}")
        print(f"\n{'='*60}")
        print("미션 요약:")
        print(f"  - 총 에이전트: {validation['total']}")
        print(f"  - 성공: {validation['completed']}")
        print(f"  - 상태: {'✅ 완료' if validation['success'] else '⚠️ 부분 완료'}")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
