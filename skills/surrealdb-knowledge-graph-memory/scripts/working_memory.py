#!/usr/bin/env python3
"""
Working Memory (Tier 1.5) - Active Task State Management

This module provides structured persistence of current task state,
enabling crash recovery and continuous read/write during agent loops.

Usage:
    from working_memory import WorkingMemory
    
    wm = WorkingMemory()
    wm.start_task("Deploy marketing pipeline", plan=[...])
    wm.update_step(1, status="complete", result="Found 12 templates")
    wm.add_decision("Using Mailchimp over SendGrid")
    state = wm.get_state()
    wm.complete_task(outcome="success")  # Creates episode
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict

# ============================================
# Configuration
# ============================================

WORKSPACE_DIR = Path(os.environ.get("OPENCLAW_WORKSPACE", Path.home() / ".openclaw" / "workspace"))
WORKING_MEMORY_DIR = WORKSPACE_DIR / ".working-memory"
CURRENT_TASK_FILE = WORKING_MEMORY_DIR / "current-task.yaml"
HISTORY_DIR = WORKING_MEMORY_DIR / "history"

# ============================================
# Data Structures
# ============================================

@dataclass
class PlanStep:
    id: int
    action: str
    status: str = "pending"  # pending, in_progress, complete, blocked, skipped
    result_summary: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    dependencies: List[int] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkingMemoryState:
    goal: str
    plan: List[PlanStep] = field(default_factory=list)
    decisions_made: List[str] = field(default_factory=list)
    problems_encountered: List[Dict[str, str]] = field(default_factory=list)
    solutions_applied: List[Dict[str, str]] = field(default_factory=list)
    blocked_on: Optional[str] = None
    confidence: float = 0.5
    iteration: int = 0
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    session_key: Optional[str] = None
    agent_id: str = "main"
    facts_used: List[str] = field(default_factory=list)  # fact IDs
    facts_created: List[str] = field(default_factory=list)
    key_learnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================
# Working Memory Manager
# ============================================

class WorkingMemory:
    """
    Manages active task state with file-based persistence.
    
    Read/write every loop iteration is fast (YAML files, no DB round-trip).
    Survives session crashes - restart picks up where it left off.
    """
    
    def __init__(self, workspace: Path = None, agent_id: str = "main"):
        self.workspace = workspace or WORKSPACE_DIR
        self.wm_dir = self.workspace / ".working-memory"
        self.current_task_file = self.wm_dir / "current-task.yaml"
        self.history_dir = self.wm_dir / "history"
        self.agent_id = agent_id
        self._state: Optional[WorkingMemoryState] = None
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Create working memory directories if they don't exist."""
        self.wm_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def _serialize_state(self, state: WorkingMemoryState) -> dict:
        """Convert state to serializable dict."""
        data = asdict(state)
        # Convert PlanStep dataclasses to dicts
        data["plan"] = [asdict(step) if isinstance(step, PlanStep) else step for step in state.plan]
        return data
    
    def _deserialize_state(self, data: dict) -> WorkingMemoryState:
        """Convert dict back to WorkingMemoryState."""
        plan = [PlanStep(**step) if isinstance(step, dict) else step for step in data.get("plan", [])]
        data["plan"] = plan
        return WorkingMemoryState(**data)
    
    def _save(self):
        """Persist current state to disk."""
        if self._state:
            self._state.last_updated = datetime.now().isoformat()
            with open(self.current_task_file, "w") as f:
                yaml.dump(self._serialize_state(self._state), f, default_flow_style=False, sort_keys=False)
    
    def _load(self) -> Optional[WorkingMemoryState]:
        """Load state from disk."""
        if self.current_task_file.exists():
            try:
                with open(self.current_task_file) as f:
                    data = yaml.safe_load(f)
                    if data:
                        return self._deserialize_state(data)
            except Exception as e:
                print(f"Warning: Could not load working memory: {e}")
        return None
    
    # ========================================
    # Public API
    # ========================================
    
    def has_active_task(self) -> bool:
        """Check if there's an active task."""
        return self.current_task_file.exists()
    
    def get_state(self) -> Optional[WorkingMemoryState]:
        """Get current working memory state."""
        if self._state is None:
            self._state = self._load()
        return self._state
    
    def start_task(
        self,
        goal: str,
        plan: List[Dict[str, Any]] = None,
        session_key: str = None,
        confidence: float = 0.5,
        metadata: Dict[str, Any] = None
    ) -> WorkingMemoryState:
        """
        Start a new task. Archives any existing task first.
        
        Args:
            goal: What we're trying to accomplish
            plan: List of step dicts with 'action' and optional 'dependencies'
            session_key: Session identifier for tracking
            confidence: Initial confidence in completing the task
            metadata: Additional context
        
        Returns:
            The new working memory state
        """
        # Archive existing task if any
        if self.has_active_task():
            existing = self.get_state()
            if existing:
                self._archive_task(existing, outcome="abandoned")
        
        # Build plan steps
        plan_steps = []
        if plan:
            for i, step_data in enumerate(plan):
                step = PlanStep(
                    id=i + 1,
                    action=step_data.get("action", step_data.get("description", f"Step {i+1}")),
                    dependencies=step_data.get("dependencies", []),
                    metadata=step_data.get("metadata", {})
                )
                plan_steps.append(step)
        
        self._state = WorkingMemoryState(
            goal=goal,
            plan=plan_steps,
            confidence=confidence,
            session_key=session_key,
            agent_id=self.agent_id,
            metadata=metadata or {}
        )
        self._save()
        return self._state
    
    def update_step(
        self,
        step_id: int,
        status: str = None,
        result_summary: str = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Update a plan step's status and results.
        
        Args:
            step_id: The step number (1-indexed)
            status: New status (pending, in_progress, complete, blocked, skipped)
            result_summary: Brief summary of what happened
            metadata: Additional step-specific data
        """
        state = self.get_state()
        if not state:
            raise ValueError("No active task")
        
        for step in state.plan:
            if step.id == step_id:
                if status:
                    step.status = status
                    if status == "in_progress" and not step.started_at:
                        step.started_at = datetime.now().isoformat()
                    elif status == "complete" and not step.completed_at:
                        step.completed_at = datetime.now().isoformat()
                if result_summary:
                    step.result_summary = result_summary
                if metadata:
                    step.metadata.update(metadata)
                break
        
        state.iteration += 1
        self._save()
    
    def add_decision(self, decision: str):
        """Record a decision made during the task."""
        state = self.get_state()
        if state:
            state.decisions_made.append(decision)
            self._save()
    
    def add_problem(self, problem: str, context: str = None):
        """Record a problem encountered."""
        state = self.get_state()
        if state:
            state.problems_encountered.append({
                "problem": problem,
                "context": context,
                "timestamp": datetime.now().isoformat()
            })
            self._save()
    
    def add_solution(self, problem: str, solution: str):
        """Record a solution applied to a problem."""
        state = self.get_state()
        if state:
            state.solutions_applied.append({
                "problem": problem,
                "solution": solution,
                "timestamp": datetime.now().isoformat()
            })
            self._save()
    
    def add_learning(self, learning: str):
        """Record a key learning from the task."""
        state = self.get_state()
        if state:
            state.key_learnings.append(learning)
            self._save()
    
    def record_fact_used(self, fact_id: str):
        """Record that a fact from the knowledge graph was used."""
        state = self.get_state()
        if state and fact_id not in state.facts_used:
            state.facts_used.append(fact_id)
            self._save()
    
    def record_fact_created(self, fact_id: str):
        """Record that a new fact was stored during this task."""
        state = self.get_state()
        if state and fact_id not in state.facts_created:
            state.facts_created.append(fact_id)
            self._save()
    
    def set_blocked(self, reason: str):
        """Mark task as blocked."""
        state = self.get_state()
        if state:
            state.blocked_on = reason
            self._save()
    
    def unblock(self):
        """Clear blocked status."""
        state = self.get_state()
        if state:
            state.blocked_on = None
            self._save()
    
    def update_confidence(self, confidence: float):
        """Update task completion confidence."""
        state = self.get_state()
        if state:
            state.confidence = max(0.0, min(1.0, confidence))
            self._save()
    
    def get_current_step(self) -> Optional[PlanStep]:
        """Get the current active step (first in_progress or first pending)."""
        state = self.get_state()
        if not state:
            return None
        
        # First look for in_progress
        for step in state.plan:
            if step.status == "in_progress":
                return step
        
        # Then first pending with satisfied dependencies
        for step in state.plan:
            if step.status == "pending":
                deps_satisfied = all(
                    any(s.id == dep and s.status == "complete" for s in state.plan)
                    for dep in step.dependencies
                )
                if deps_satisfied:
                    return step
        
        return None
    
    def get_progress(self) -> Dict[str, Any]:
        """Get task progress summary."""
        state = self.get_state()
        if not state:
            return {"active": False}
        
        total = len(state.plan)
        completed = sum(1 for s in state.plan if s.status == "complete")
        in_progress = sum(1 for s in state.plan if s.status == "in_progress")
        
        return {
            "active": True,
            "goal": state.goal,
            "total_steps": total,
            "completed": completed,
            "in_progress": in_progress,
            "percent": round(completed / total * 100) if total > 0 else 0,
            "current_step": self.get_current_step(),
            "blocked_on": state.blocked_on,
            "confidence": state.confidence,
            "iteration": state.iteration
        }
    
    def complete_task(self, outcome: str = "success", summary: str = None) -> Dict[str, Any]:
        """
        Complete the current task and create an episode.
        
        Args:
            outcome: success, failure, or abandoned
            summary: Optional summary of the task
        
        Returns:
            Episode data for storage in knowledge graph
        """
        state = self.get_state()
        if not state:
            raise ValueError("No active task to complete")
        
        # Calculate duration
        started = datetime.fromisoformat(state.started_at)
        duration_hours = (datetime.now() - started).total_seconds() / 3600
        
        # Build episode
        episode = {
            "task": summary or state.goal,
            "goal": state.goal,
            "started_at": state.started_at,
            "completed_at": datetime.now().isoformat(),
            "outcome": outcome,
            "duration_hours": round(duration_hours, 2),
            "steps_taken": len([s for s in state.plan if s.status == "complete"]),
            "decisions": state.decisions_made,
            "problems": state.problems_encountered,
            "solutions": state.solutions_applied,
            "key_learnings": state.key_learnings,
            "facts_used": state.facts_used,
            "facts_created": state.facts_created,
            "final_confidence": state.confidence,
            "session_key": state.session_key,
            "agent_id": state.agent_id
        }
        
        # Archive the task
        self._archive_task(state, outcome)
        
        # Clear current task
        self._state = None
        if self.current_task_file.exists():
            self.current_task_file.unlink()
        
        return episode
    
    def _archive_task(self, state: WorkingMemoryState, outcome: str):
        """Archive a completed/abandoned task to history."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archive_file = self.history_dir / f"{timestamp}-{outcome}.yaml"
        
        data = self._serialize_state(state)
        data["archived_at"] = datetime.now().isoformat()
        data["final_outcome"] = outcome
        
        with open(archive_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def get_recent_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent task history."""
        history = []
        files = sorted(self.history_dir.glob("*.yaml"), reverse=True)
        
        for f in files[:limit]:
            try:
                with open(f) as fh:
                    data = yaml.safe_load(fh)
                    history.append({
                        "file": f.name,
                        "goal": data.get("goal"),
                        "outcome": data.get("final_outcome"),
                        "archived_at": data.get("archived_at"),
                        "duration_hours": data.get("duration_hours")
                    })
            except:
                pass
        
        return history


# ============================================
# CLI Interface
# ============================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Working Memory CLI")
    parser.add_argument("action", choices=["status", "start", "step", "decision", "complete", "history", "clear"])
    parser.add_argument("--goal", help="Task goal (for start)")
    parser.add_argument("--step-id", type=int, help="Step ID (for step)")
    parser.add_argument("--status", help="Step status")
    parser.add_argument("--result", help="Step result summary")
    parser.add_argument("--text", help="Decision or learning text")
    parser.add_argument("--outcome", default="success", help="Task outcome (for complete)")
    parser.add_argument("--limit", type=int, default=5, help="History limit")
    
    args = parser.parse_args()
    wm = WorkingMemory()
    
    if args.action == "status":
        progress = wm.get_progress()
        if progress["active"]:
            print(f"Goal: {progress['goal']}")
            print(f"Progress: {progress['completed']}/{progress['total_steps']} ({progress['percent']}%)")
            print(f"Confidence: {progress['confidence']:.0%}")
            if progress['blocked_on']:
                print(f"Blocked: {progress['blocked_on']}")
            if progress['current_step']:
                print(f"Current: {progress['current_step'].action}")
        else:
            print("No active task")
    
    elif args.action == "start":
        if not args.goal:
            print("Error: --goal required")
            return
        wm.start_task(args.goal)
        print(f"Started task: {args.goal}")
    
    elif args.action == "step":
        if not args.step_id:
            print("Error: --step-id required")
            return
        wm.update_step(args.step_id, status=args.status, result_summary=args.result)
        print(f"Updated step {args.step_id}")
    
    elif args.action == "decision":
        if not args.text:
            print("Error: --text required")
            return
        wm.add_decision(args.text)
        print(f"Added decision: {args.text}")
    
    elif args.action == "complete":
        episode = wm.complete_task(outcome=args.outcome)
        print(f"Completed task: {episode['outcome']}")
        print(f"Duration: {episode['duration_hours']}h")
        print(f"Steps completed: {episode['steps_taken']}")
    
    elif args.action == "history":
        history = wm.get_recent_history(args.limit)
        for h in history:
            print(f"{h['outcome']:10} | {h['goal'][:50]}")
    
    elif args.action == "clear":
        if wm.current_task_file.exists():
            wm.current_task_file.unlink()
        print("Cleared working memory")


if __name__ == "__main__":
    main()
