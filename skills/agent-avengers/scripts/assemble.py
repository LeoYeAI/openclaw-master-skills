#!/usr/bin/env python3
"""
Agent Avengers - Assemble Script
태스크 분해 → 에이전트 배정 → 스폰/디스패치
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# 워크스페이스 경로
WORKSPACE = os.environ.get("AVENGERS_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
MISSION_DIR = Path(WORKSPACE) / "avengers-missions"

# 에이전트 타입 정의
AGENT_TYPES = {
    "researcher": {
        "emoji": "🔬",
        "model": "sonnet",
        "timeout": 1800,
        "keywords": ["조사", "리서치", "검색", "수집", "분석"]
    },
    "analyst": {
        "emoji": "🔍",
        "model": "opus",
        "timeout": 1200,
        "keywords": ["분석", "패턴", "인사이트", "평가"]
    },
    "writer": {
        "emoji": "🖊️",
        "model": "sonnet",
        "timeout": 900,
        "keywords": ["작성", "문서", "리포트", "콘텐츠", "글"]
    },
    "coder": {
        "emoji": "💻",
        "model": "opus",
        "timeout": 2400,
        "keywords": ["코드", "개발", "구현", "API", "프로그래밍"]
    },
    "reviewer": {
        "emoji": "✅",
        "model": "opus",
        "timeout": 600,
        "keywords": ["검토", "리뷰", "피드백", "확인"]
    },
    "integrator": {
        "emoji": "🔧",
        "model": "sonnet",
        "timeout": 900,
        "keywords": ["통합", "병합", "조합", "최종"]
    }
}


def create_mission(task_description: str) -> dict:
    """미션 생성 및 초기화"""
    mission_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    mission_path = MISSION_DIR / mission_id
    mission_path.mkdir(parents=True, exist_ok=True)
    
    # 서브 디렉토리 생성
    (mission_path / "agents").mkdir(exist_ok=True)
    (mission_path / "outputs").mkdir(exist_ok=True)
    (mission_path / "logs").mkdir(exist_ok=True)
    
    mission = {
        "id": mission_id,
        "path": str(mission_path),
        "task": task_description,
        "status": "initializing",
        "created_at": datetime.now().isoformat(),
        "agents": [],
        "subtasks": []
    }
    
    # 미션 파일 저장
    with open(mission_path / "mission.json", "w") as f:
        json.dump(mission, f, indent=2, ensure_ascii=False)
    
    return mission


def detect_agent_type(subtask: str) -> str:
    """서브태스크 설명에서 에이전트 타입 추론"""
    subtask_lower = subtask.lower()
    
    for agent_type, config in AGENT_TYPES.items():
        for keyword in config["keywords"]:
            if keyword in subtask_lower:
                return agent_type
    
    return "researcher"  # 기본값


def decompose_task(task: str) -> list:
    """
    태스크를 서브태스크로 분해
    실제로는 LLM을 호출해야 하지만, 여기선 구조만 정의
    """
    # 이 부분은 실제로는 OpenClaw 세션에서 LLM이 처리
    # 스크립트에서는 구조화된 입력을 받음
    return []


def create_agent_config(subtask: dict, mission_id: str, index: int) -> dict:
    """에이전트 설정 생성"""
    agent_type = subtask.get("type") or detect_agent_type(subtask["description"])
    type_config = AGENT_TYPES.get(agent_type, AGENT_TYPES["researcher"])
    
    agent_id = f"{mission_id}_agent_{index:02d}"
    
    return {
        "id": agent_id,
        "type": agent_type,
        "emoji": type_config["emoji"],
        "model": subtask.get("model") or type_config["model"],
        "timeout": subtask.get("timeout") or type_config["timeout"],
        "description": subtask["description"],
        "inputs": subtask.get("inputs", []),
        "expected_output": subtask.get("expected_output", ""),
        "dependencies": subtask.get("dependencies", []),
        "status": "pending",
        "mode": subtask.get("mode", "spawn")  # spawn | existing | profile
    }


def generate_spawn_command(agent: dict, mission_path: str) -> dict:
    """sessions_spawn 호출용 파라미터 생성"""
    
    prompt = f"""
# 🦸 Avengers Mission

## 당신의 역할
{agent['emoji']} {agent['type'].upper()} 에이전트

## 태스크
{agent['description']}

## 입력 데이터
{json.dumps(agent['inputs'], ensure_ascii=False) if agent['inputs'] else '없음'}

## 기대 출력
{agent['expected_output'] or '태스크 완료 보고'}

## 출력 위치
{mission_path}/outputs/{agent['id']}.md

## 완료 시
1. 결과를 위 경로에 저장
2. "MISSION_COMPLETE: {agent['id']}" 메시지 출력
"""
    
    return {
        "task": prompt,
        "model": agent["model"],
        "runTimeoutSeconds": agent["timeout"],
        "cleanup": "keep",  # 결과 확인을 위해 유지
        "label": agent["id"]
    }


def generate_send_command(agent: dict, existing_agent_id: str) -> dict:
    """sessions_send 호출용 파라미터 생성 (기존 에이전트용)"""
    
    message = f"""
# 🦸 Avengers Mission 요청

## 태스크
{agent['description']}

## 입력 데이터
{json.dumps(agent['inputs'], ensure_ascii=False) if agent['inputs'] else '없음'}

## 기대 출력
{agent['expected_output'] or '태스크 완료 보고'}

## 완료 시
"MISSION_COMPLETE: {agent['id']}" 라고 알려줘
"""
    
    return {
        "label": existing_agent_id,
        "message": message,
        "timeoutSeconds": agent["timeout"]
    }


def save_execution_plan(mission: dict, agents: list) -> str:
    """실행 계획 저장"""
    mission_path = Path(mission["path"])
    
    # 의존성 기반 실행 순서 계산
    phases = []
    remaining = agents.copy()
    completed_ids = set()
    
    while remaining:
        # 의존성이 모두 해결된 에이전트 찾기
        ready = [a for a in remaining if all(d in completed_ids for d in a["dependencies"])]
        
        if not ready:
            # 순환 의존성 또는 오류
            ready = remaining[:1]
        
        phases.append(ready)
        for a in ready:
            completed_ids.add(a["id"])
            remaining.remove(a)
    
    plan = {
        "mission_id": mission["id"],
        "total_agents": len(agents),
        "phases": [
            {
                "phase": i + 1,
                "parallel": len(phase) > 1,
                "agents": [
                    {
                        "id": a["id"],
                        "type": a["type"],
                        "emoji": a["emoji"],
                        "mode": a["mode"],
                        "description": a["description"][:50] + "..." if len(a["description"]) > 50 else a["description"]
                    }
                    for a in phase
                ]
            }
            for i, phase in enumerate(phases)
        ],
        "commands": []
    }
    
    # 각 에이전트별 명령어 생성
    for agent in agents:
        if agent["mode"] == "spawn":
            cmd = generate_spawn_command(agent, str(mission_path))
            plan["commands"].append({
                "agent_id": agent["id"],
                "type": "spawn",
                "params": cmd
            })
        elif agent["mode"] == "existing":
            existing_id = agent.get("existing_agent_id", agent["type"])
            cmd = generate_send_command(agent, existing_id)
            plan["commands"].append({
                "agent_id": agent["id"],
                "type": "send",
                "params": cmd
            })
    
    # 계획 저장
    with open(mission_path / "execution_plan.json", "w") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    return str(mission_path / "execution_plan.json")


def print_plan_summary(plan_path: str):
    """실행 계획 요약 출력"""
    with open(plan_path) as f:
        plan = json.load(f)
    
    print("\n" + "="*60)
    print("🦸 AVENGERS ASSEMBLE - 실행 계획")
    print("="*60)
    print(f"미션 ID: {plan['mission_id']}")
    print(f"총 에이전트: {plan['total_agents']}명")
    print()
    
    for phase in plan["phases"]:
        parallel_tag = "⚡ 병렬" if phase["parallel"] else "➡️ 순차"
        print(f"Phase {phase['phase']} ({parallel_tag}):")
        for agent in phase["agents"]:
            mode_icon = "🔶" if agent["mode"] == "spawn" else "🔷"
            print(f"  {agent['emoji']} {agent['id']}: {agent['description']}")
        print()
    
    print("="*60)
    print(f"📄 상세 계획: {plan_path}")
    print("🚀 실행하려면: python3 scripts/execute.py --mission {mission_id}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Agent Avengers - Assemble")
    parser.add_argument("--task", "-t", help="태스크 설명")
    parser.add_argument("--subtasks", "-s", help="서브태스크 JSON 파일")
    parser.add_argument("--interactive", "-i", action="store_true", help="대화형 모드")
    
    args = parser.parse_args()
    
    if args.subtasks:
        # JSON 파일에서 서브태스크 로드
        with open(args.subtasks) as f:
            data = json.load(f)
        
        task = data.get("task", "Avengers Mission")
        subtasks = data.get("subtasks", [])
        
    elif args.task:
        print("⚠️  태스크만 제공됨. 서브태스크는 OpenClaw 세션에서 분해 필요.")
        task = args.task
        subtasks = []
        
    else:
        print("사용법:")
        print("  python3 assemble.py --subtasks mission.json")
        print("  python3 assemble.py --task '복잡한 작업 설명'")
        sys.exit(1)
    
    # 미션 생성
    mission = create_mission(task)
    print(f"📁 미션 생성: {mission['id']}")
    
    if subtasks:
        # 에이전트 설정 생성
        agents = [
            create_agent_config(st, mission["id"], i)
            for i, st in enumerate(subtasks)
        ]
        
        # 실행 계획 저장
        plan_path = save_execution_plan(mission, agents)
        
        # 요약 출력
        print_plan_summary(plan_path)
    else:
        print(f"\n📝 서브태스크 정의 필요:")
        print(f"   {mission['path']}/subtasks.json 생성 후")
        print(f"   python3 assemble.py --subtasks {mission['path']}/subtasks.json")


if __name__ == "__main__":
    main()
