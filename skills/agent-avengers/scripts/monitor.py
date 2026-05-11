#!/usr/bin/env python3
"""
Agent Avengers - Monitor Script
에이전트 진행 상황 모니터링
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
    
    plan_file = mission_path / "execution_plan.json"
    plan = None
    if plan_file.exists():
        with open(plan_file) as f:
            plan = json.load(f)
    
    return mission, plan


def check_agent_outputs(mission_path: Path, plan: dict) -> list:
    """에이전트 출력 파일 확인"""
    outputs_dir = mission_path / "outputs"
    results = []
    
    if not plan:
        return results
    
    for cmd in plan.get("commands", []):
        agent_id = cmd["agent_id"]
        output_file = outputs_dir / f"{agent_id}.md"
        
        status = "pending"
        output_size = 0
        
        if output_file.exists():
            status = "completed"
            output_size = output_file.stat().st_size
        
        results.append({
            "agent_id": agent_id,
            "status": status,
            "output_file": str(output_file),
            "output_size": output_size
        })
    
    return results


def read_logs(mission_path: Path, limit: int = 20) -> list:
    """실행 로그 읽기"""
    log_file = mission_path / "logs" / "execution.jsonl"
    
    if not log_file.exists():
        return []
    
    logs = []
    with open(log_file) as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line))
    
    return logs[-limit:]


def print_status(mission: dict, plan: dict, agent_results: list, logs: list):
    """상태 출력"""
    print("\n" + "="*70)
    print("🦸 AVENGERS MONITOR - 미션 상태")
    print("="*70)
    
    print(f"\n📋 미션 정보:")
    print(f"   ID: {mission['id']}")
    print(f"   상태: {mission['status']}")
    print(f"   생성: {mission['created_at']}")
    if mission.get('updated_at'):
        print(f"   업데이트: {mission['updated_at']}")
    
    if plan:
        print(f"\n📊 에이전트 현황:")
        
        completed = sum(1 for r in agent_results if r["status"] == "completed")
        total = len(agent_results)
        
        print(f"   진행률: {completed}/{total} ({completed/total*100:.0f}%)")
        print()
        
        # 진행바
        bar_width = 40
        filled = int(bar_width * completed / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"   [{bar}]")
        print()
        
        # 에이전트별 상태
        for phase in plan["phases"]:
            print(f"   Phase {phase['phase']}:")
            for agent in phase["agents"]:
                result = next((r for r in agent_results if r["agent_id"] == agent["id"]), None)
                if result:
                    status_icon = "✅" if result["status"] == "completed" else "⏳"
                    size_info = f"({result['output_size']} bytes)" if result["status"] == "completed" else ""
                    print(f"     {status_icon} {agent['emoji']} {agent['id']} {size_info}")
            print()
    
    if logs:
        print(f"📜 최근 로그 (최대 5개):")
        for log in logs[-5:]:
            print(f"   [{log['timestamp'][:19]}] {log['event']}")
    
    print("\n" + "="*70)
    
    # 다음 단계 안내
    if plan:
        if completed == total:
            print("🎉 모든 에이전트 완료!")
            print(f"📦 결과 통합: python3 scripts/consolidate.py --mission {mission['id']}")
        else:
            print("⏳ 진행 중...")
            print(f"🔄 새로고침: python3 scripts/monitor.py --mission {mission['id']}")
    
    print("="*70)


def watch_mode(mission_id: str, interval: int = 10):
    """실시간 모니터링 모드"""
    import time
    
    print(f"👀 실시간 모니터링 시작 (갱신 간격: {interval}초)")
    print("   종료하려면 Ctrl+C")
    
    try:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            
            mission, plan = load_mission(mission_id)
            mission_path = Path(mission["path"])
            agent_results = check_agent_outputs(mission_path, plan)
            logs = read_logs(mission_path)
            
            print_status(mission, plan, agent_results, logs)
            print(f"\n⏰ 다음 갱신: {interval}초 후...")
            
            # 완료 확인
            if plan:
                completed = sum(1 for r in agent_results if r["status"] == "completed")
                if completed == len(agent_results):
                    print("\n🎉 미션 완료! 모니터링 종료.")
                    break
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n👋 모니터링 종료")


def main():
    parser = argparse.ArgumentParser(description="Agent Avengers - Monitor")
    parser.add_argument("--mission", "-m", required=True, help="미션 ID")
    parser.add_argument("--watch", "-w", action="store_true", help="실시간 모니터링")
    parser.add_argument("--interval", "-i", type=int, default=10, help="갱신 간격(초)")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 출력")
    
    args = parser.parse_args()
    
    try:
        mission, plan = load_mission(args.mission)
    except FileNotFoundError:
        print(f"❌ 미션을 찾을 수 없습니다: {args.mission}")
        sys.exit(1)
    
    mission_path = Path(mission["path"])
    agent_results = check_agent_outputs(mission_path, plan)
    logs = read_logs(mission_path)
    
    if args.json:
        output = {
            "mission": mission,
            "agents": agent_results,
            "logs": logs
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    elif args.watch:
        watch_mode(args.mission, args.interval)
    else:
        print_status(mission, plan, agent_results, logs)


if __name__ == "__main__":
    main()
