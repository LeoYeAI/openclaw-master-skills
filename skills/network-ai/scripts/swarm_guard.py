#!/usr/bin/env python3
"""
Swarm Guard - Prevents Handoff Tax, Silent Failures, and Budget Overruns

Three critical issues in multi-agent swarms:
1. HANDOFF TAX: Agents waste tokens "talking about" work instead of doing it
2. SILENT FAILURE: One agent fails, others keep working on bad data
3. BUDGET OVERRUN: Infinite loops burn $500 in API credits in an hour

Usage:
    python swarm_guard.py check-handoff --task-id TASK_ID
    python swarm_guard.py validate-result --task-id TASK_ID --agent AGENT_ID
    python swarm_guard.py health-check --agent AGENT_ID
    python swarm_guard.py supervisor-review --task-id TASK_ID
    
    # Budget/Cost Awareness:
    python swarm_guard.py budget-init --task-id TASK_ID --budget 10000
    python swarm_guard.py budget-check --task-id TASK_ID
    python swarm_guard.py budget-spend --task-id TASK_ID --tokens 500 --reason "API call"

Examples:
    python swarm_guard.py check-handoff --task-id "task_001"
    python swarm_guard.py budget-init --task-id "task_001" --budget 10000
    python swarm_guard.py budget-spend --task-id "task_001" --tokens 500 --reason "LLM call"
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
BLACKBOARD_PATH = Path(__file__).parent.parent / "swarm-blackboard.md"
AUDIT_LOG = DATA_DIR / "audit_log.jsonl"

# ============================================================================
# HANDOFF TAX LIMITS
# ============================================================================

# Maximum handoffs before forcing action
MAX_HANDOFFS_PER_TASK = 3

# Maximum message size (chars) - forces concise communication
MAX_HANDOFF_MESSAGE_SIZE = 500

# Minimum "action ratio" - at least 60% of exchanges should produce artifacts
MIN_ACTION_RATIO = 0.6

# Maximum time in "planning" phase before requiring output
MAX_PLANNING_SECONDS = 120

# ============================================================================
# SILENT FAILURE DETECTION
# ============================================================================

# Heartbeat timeout - agent considered failed if no update in this time
HEARTBEAT_TIMEOUT_SECONDS = 60

# Result validation rules
REQUIRED_RESULT_FIELDS = ["status", "output", "confidence"]

# Confidence threshold for auto-approval
MIN_CONFIDENCE_THRESHOLD = 0.7

# ============================================================================
# COST AWARENESS / TOKEN BUDGET
# ============================================================================

# Default max token budget per task (prevents infinite loops)
DEFAULT_MAX_TOKEN_BUDGET = 50000

# Warning threshold (percentage of budget)
BUDGET_WARNING_THRESHOLD = 0.75  # Warn at 75%

# Hard stop threshold (percentage of budget)
BUDGET_HARD_STOP_THRESHOLD = 1.0  # Stop at 100%

# Estimated token costs for common operations
TOKEN_COSTS = {
    "handoff": 150,        # Estimated tokens per handoff message
    "api_call": 500,       # Average API call
    "llm_query": 1000,     # LLM inference call
    "file_read": 200,      # Reading a file
    "file_write": 300,     # Writing a file
    "validation": 100,     # Result validation
}


def log_audit(action: str, details: dict[str, Any]) -> None:
    """Append entry to audit log."""
    AUDIT_LOG.parent.mkdir(exist_ok=True)
    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "details": details
    }
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


class SwarmGuard:
    """Monitors swarm health, prevents common failure modes, and enforces budgets."""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(exist_ok=True)
        self.task_log_path = self.data_dir / "task_tracking.json"
        self.health_log_path = self.data_dir / "agent_health.json"
        self.budget_log_path = self.data_dir / "budget_tracking.json"
        self._load_state()
    
    def _load_state(self) -> None:
        """Load tracking state from disk."""
        self.task_tracking: dict[str, Any] = {}
        self.agent_health: dict[str, Any] = {}
        self.budget_tracking: dict[str, Any] = {}
        
        if self.task_log_path.exists():
            try:
                self.task_tracking = json.loads(self.task_log_path.read_text())
            except json.JSONDecodeError:
                pass  # corrupt file — keep default empty dict
            try:
                self.agent_health = json.loads(self.health_log_path.read_text())
            except json.JSONDecodeError:
                pass  # corrupt file — keep default empty dict
            try:
                self.budget_tracking = json.loads(self.budget_log_path.read_text())
            except json.JSONDecodeError:
                pass  # corrupt file — keep default empty dict
    
    def _save_state(self) -> None:
        """Persist tracking state to disk."""
        self.task_log_path.write_text(json.dumps(self.task_tracking, indent=2))
        self.health_log_path.write_text(json.dumps(self.agent_health, indent=2))
        self.budget_log_path.write_text(json.dumps(self.budget_tracking, indent=2))
    
    # ========================================================================
    # HANDOFF TAX PREVENTION
    # ========================================================================
    
    def record_handoff(self, task_id: str, from_agent: str, to_agent: str, 
                       message: str, has_artifact: bool = False) -> dict[str, Any]:
        """
        Record a handoff and check for Handoff Tax violations.
        
        Returns warnings if:
        - Too many handoffs for this task
        - Message is too verbose
        - Low action ratio (lots of talk, no artifacts)
        """
        if task_id not in self.task_tracking:
            self.task_tracking[task_id] = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "handoffs": [],
                "artifacts_produced": 0,
                "status": "active"
            }
        
        task = self.task_tracking[task_id]
        
        # Record this handoff
        handoff_record: dict[str, Union[str, int, bool]] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "from": from_agent,
            "to": to_agent,
            "message_length": len(message),
            "has_artifact": has_artifact
        }
        task["handoffs"].append(handoff_record)
        
        if has_artifact:
            task["artifacts_produced"] += 1
        
        self._save_state()
        
        # Check for violations
        warnings: list[str] = []
        violations: list[str] = []
        
        handoff_count = len(task["handoffs"])
        
        # Check: Too many handoffs?
        if handoff_count > MAX_HANDOFFS_PER_TASK:
            violations.append(
                f"HANDOFF_TAX: {handoff_count} handoffs exceeds limit of {MAX_HANDOFFS_PER_TASK}. "
                "Stop discussing, start producing output!"
            )
        elif handoff_count == MAX_HANDOFFS_PER_TASK:
            warnings.append(
                f"WARNING: This is handoff #{handoff_count}. Next handoff must include final output."
            )
        
        # Check: Message too verbose?
        if len(message) > MAX_HANDOFF_MESSAGE_SIZE:
            violations.append(
                f"VERBOSE_HANDOFF: Message is {len(message)} chars, limit is {MAX_HANDOFF_MESSAGE_SIZE}. "
                "Be concise! Include only: instruction, constraints, expected output."
            )
        
        # Check: Action ratio (only after 2+ handoffs)
        if handoff_count >= 2:
            action_ratio = task["artifacts_produced"] / handoff_count
            if action_ratio < MIN_ACTION_RATIO:
                warnings.append(
                    f"LOW_ACTION_RATIO: Only {task['artifacts_produced']}/{handoff_count} "
                    f"handoffs produced artifacts ({action_ratio:.0%}). "
                    f"Target is {MIN_ACTION_RATIO:.0%}."
                )
        
        # Check: Time in planning phase
        created = datetime.fromisoformat(task["created_at"].replace("Z", "+00:00"))
        elapsed = (datetime.now(timezone.utc) - created).total_seconds()
        
        if elapsed > MAX_PLANNING_SECONDS and task["artifacts_produced"] == 0:
            violations.append(
                f"PLANNING_TIMEOUT: {elapsed:.0f}s elapsed with no artifacts. "
                "Produce output now or abort task."
            )
        
        return {
            "task_id": task_id,
            "handoff_number": handoff_count,
            "artifacts_produced": task["artifacts_produced"],
            "warnings": warnings,
            "violations": violations,
            "blocked": len(violations) > 0
        }
    
    def check_handoff_status(self, task_id: str) -> dict[str, Any]:
        """Get current handoff tax status for a task."""
        if task_id not in self.task_tracking:
            return {
                "task_id": task_id,
                "exists": False,
                "handoffs": 0,
                "remaining": MAX_HANDOFFS_PER_TASK,
                "status": "not_found"
            }
        
        task = self.task_tracking[task_id]
        handoff_count = len(task["handoffs"])
        
        return {
            "task_id": task_id,
            "exists": True,
            "handoffs": handoff_count,
            "remaining": max(0, MAX_HANDOFFS_PER_TASK - handoff_count),
            "artifacts_produced": task["artifacts_produced"],
            "action_ratio": task["artifacts_produced"] / handoff_count if handoff_count > 0 else 1.0,
            "status": task["status"]
        }
    
    # ========================================================================
    # SILENT FAILURE PREVENTION
    # ========================================================================
    
    def agent_heartbeat(self, agent_id: str, task_id: Optional[str] = None,
                        status: str = "active") -> dict[str, Any]:
        """
        Record agent heartbeat to detect silent failures.
        Agents should call this periodically while working.
        """
        now = datetime.now(timezone.utc).isoformat()
        
        if agent_id not in self.agent_health:
            self.agent_health[agent_id] = {
                "first_seen": now,
                "heartbeats": 0,
                "failures": 0
            }
        
        self.agent_health[agent_id].update({
            "last_heartbeat": now,
            "current_task": task_id,
            "status": status,
            "heartbeats": self.agent_health[agent_id].get("heartbeats", 0) + 1
        })
        
        self._save_state()
        
        return {
            "agent_id": agent_id,
            "recorded": True,
            "timestamp": now
        }
    
    def check_agent_health(self, agent_id: str) -> dict[str, Any]:
        """
        Check if an agent is healthy (recent heartbeat).
        Returns failure status if agent hasn't reported in.
        """
        if agent_id not in self.agent_health:
            return {
                "agent_id": agent_id,
                "healthy": False,
                "reason": "UNKNOWN_AGENT",
                "recommendation": "Agent has never reported. Verify agent exists."
            }
        
        agent = self.agent_health[agent_id]
        last_heartbeat = agent.get("last_heartbeat")
        
        if not last_heartbeat:
            return {
                "agent_id": agent_id,
                "healthy": False,
                "reason": "NO_HEARTBEAT",
                "recommendation": "Agent registered but never sent heartbeat."
            }
        
        # Check if heartbeat is recent
        last_time = datetime.fromisoformat(last_heartbeat.replace("Z", "+00:00"))
        elapsed = (datetime.now(timezone.utc) - last_time).total_seconds()
        
        if elapsed > HEARTBEAT_TIMEOUT_SECONDS:
            return {
                "agent_id": agent_id,
                "healthy": False,
                "reason": "STALE_HEARTBEAT",
                "seconds_since_heartbeat": elapsed,
                "timeout_threshold": HEARTBEAT_TIMEOUT_SECONDS,
                "current_task": agent.get("current_task"),
                "recommendation": f"Agent silent for {elapsed:.0f}s. Assume FAILED. "
                                  "Do NOT use any pending results from this agent."
            }
        
        return {
            "agent_id": agent_id,
            "healthy": True,
            "status": agent.get("status", "unknown"),
            "current_task": agent.get("current_task"),
            "seconds_since_heartbeat": elapsed
        }
    
    def validate_result(self, task_id: str, agent_id: str, 
                        result: dict[str, Any]) -> dict[str, Any]:
        """
        Validate an agent's result before other agents use it.
        Prevents cascade failures from bad data.
        """
        issues: list[str] = []
        warnings: list[str] = []
        
        # Check agent health first
        health = self.check_agent_health(agent_id)
        if not health["healthy"]:
            issues.append(f"UNHEALTHY_AGENT: {health['reason']} - {health['recommendation']}")
        
        # Check required fields
        for field in REQUIRED_RESULT_FIELDS:
            if field not in result:
                issues.append(f"MISSING_FIELD: Result must include '{field}'")
        
        # Check status
        if result.get("status") == "error":
            issues.append(f"ERROR_STATUS: Agent reported error: {result.get('error', 'unknown')}")
        
        # Check confidence
        confidence = result.get("confidence", 0)
        if confidence < MIN_CONFIDENCE_THRESHOLD:
            warnings.append(
                f"LOW_CONFIDENCE: Agent confidence is {confidence:.0%}, "
                f"threshold is {MIN_CONFIDENCE_THRESHOLD:.0%}. "
                "Consider supervisor review."
            )
        
        # Check for empty output
        output = result.get("output")
        if output is None or output == "" or output == {}:
            issues.append("EMPTY_OUTPUT: Result contains no meaningful output")
        
        valid = len(issues) == 0
        
        # Record validation
        if task_id in self.task_tracking:
            if "validations" not in self.task_tracking[task_id]:
                self.task_tracking[task_id]["validations"] = []
            
            self.task_tracking[task_id]["validations"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": agent_id,
                "valid": valid,
                "issues": issues
            })
            self._save_state()
        
        return {
            "task_id": task_id,
            "agent_id": agent_id,
            "valid": valid,
            "usable": valid,  # Other agents can use this result
            "issues": issues,
            "warnings": warnings,
            "recommendation": "APPROVED - Result can be used by other agents" if valid 
                            else "BLOCKED - Do NOT propagate this result. Fix issues or restart task."
        }
    
    def supervisor_review(self, task_id: str) -> dict[str, Any]:
        """
        Supervisor-level review of entire task state.
        Checks for cascade failures, zombie tasks, and quality issues.
        """
        if task_id not in self.task_tracking:
            return {
                "task_id": task_id,
                "found": False,
                "verdict": "UNKNOWN_TASK"
            }
        
        task = self.task_tracking[task_id]
        issues: list[str] = []
        recommendations: list[str] = []
        
        # Check task age
        created = datetime.fromisoformat(task["created_at"].replace("Z", "+00:00"))
        age_seconds = (datetime.now(timezone.utc) - created).total_seconds()
        
        if age_seconds > 300 and task["status"] == "active":  # 5 min
            issues.append(f"LONG_RUNNING: Task active for {age_seconds/60:.1f} minutes")
            recommendations.append("Consider timeout or manual intervention")
        
        # Check handoff efficiency
        handoffs = task.get("handoffs", [])
        artifacts = task.get("artifacts_produced", 0)
        
        if len(handoffs) > 0:
            efficiency = artifacts / len(handoffs)
            if efficiency < 0.5:
                issues.append(f"INEFFICIENT: Only {efficiency:.0%} of handoffs produced output")
                recommendations.append("Reduce coordination overhead, increase direct work")
        
        # Check validations
        validations = task.get("validations", [])
        failed_validations = [v for v in validations if not v.get("valid")]
        
        if len(failed_validations) > 0:
            issues.append(f"VALIDATION_FAILURES: {len(failed_validations)} results failed validation")
            for v in failed_validations:
                recommendations.append(f"Re-run or fix agent '{v['agent_id']}': {v['issues']}")
        
        # Check for participating agents' health
        participating_agents: set[str] = set()
        for h in handoffs:
            from_agent = h.get("from")
            to_agent = h.get("to")
            if isinstance(from_agent, str):
                participating_agents.add(from_agent)
            if isinstance(to_agent, str):
                participating_agents.add(to_agent)
        
        unhealthy_agents: list[str] = []
        for agent_id in participating_agents:
            health = self.check_agent_health(agent_id)
            if not health["healthy"]:
                unhealthy_agents.append(agent_id)
        
        if unhealthy_agents:
            issues.append(f"UNHEALTHY_AGENTS: {unhealthy_agents}")
            recommendations.append("Do not trust pending results from unhealthy agents")
        
        # Check budget status
        budget_status = self.check_budget(task_id)
        if budget_status.get("initialized"):
            usage_pct = budget_status.get("usage_percentage", 0)
            if usage_pct >= 100:
                issues.append(f"BUDGET_EXCEEDED: {usage_pct:.0f}% of budget used")
                recommendations.append("Task must stop - budget exhausted")
            elif usage_pct >= 75:
                issues.append(f"BUDGET_WARNING: {usage_pct:.0f}% of budget used")
                recommendations.append("Complete task soon or request budget increase")
        
        # Verdict
        if len(issues) == 0:
            verdict = "APPROVED"
            status = "healthy"
        elif any("VALIDATION_FAILURES" in i or "UNHEALTHY_AGENTS" in i or "BUDGET_EXCEEDED" in i for i in issues):
            verdict = "BLOCKED"
            status = "critical"
        else:
            verdict = "WARNING"
            status = "degraded"
        
        return {
            "task_id": task_id,
            "found": True,
            "verdict": verdict,
            "status": status,
            "age_seconds": age_seconds,
            "handoffs": len(handoffs),
            "artifacts": artifacts,
            "issues": issues,
            "recommendations": recommendations
        }
    
    # ========================================================================
    # COST AWARENESS / TOKEN BUDGET
    # ========================================================================
    
    def init_budget(self, task_id: str, max_tokens: int = DEFAULT_MAX_TOKEN_BUDGET,
                    description: str = "") -> dict[str, Any]:
        """
        Initialize a token budget for a task.
        This MUST be called before any work begins to enable cost tracking.
        """
        if task_id in self.budget_tracking:
            return {
                "initialized": False,
                "error": f"Budget already exists for task '{task_id}'. Use budget-check to view."
            }
        
        self.budget_tracking[task_id] = {
            "max_tokens": max_tokens,
            "used_tokens": 0,
            "remaining_tokens": max_tokens,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": description,
            "spending_log": [],
            "status": "active"
        }
        
        self._save_state()
        
        log_audit("budget_initialized", {
            "task_id": task_id,
            "max_tokens": max_tokens,
            "description": description
        })
        
        return {
            "initialized": True,
            "task_id": task_id,
            "max_tokens": max_tokens,
            "message": f"Budget initialized: {max_tokens:,} tokens"
        }
    
    def check_budget(self, task_id: str) -> dict[str, Any]:
        """
        Check current budget status for a task.
        Returns remaining budget, usage percentage, and warnings.
        """
        if task_id not in self.budget_tracking:
            return {
                "task_id": task_id,
                "initialized": False,
                "error": "No budget tracking for this task. Run budget-init first."
            }
        
        budget = self.budget_tracking[task_id]
        usage_pct = (budget["used_tokens"] / budget["max_tokens"]) * 100 if budget["max_tokens"] > 0 else 0
        
        # Determine status
        if usage_pct >= BUDGET_HARD_STOP_THRESHOLD * 100:
            status = "EXHAUSTED"
            can_continue = False
        elif usage_pct >= BUDGET_WARNING_THRESHOLD * 100:
            status = "WARNING"
            can_continue = True
        else:
            status = "OK"
            can_continue = True
        
        return {
            "task_id": task_id,
            "initialized": True,
            "max_tokens": budget["max_tokens"],
            "used_tokens": budget["used_tokens"],
            "remaining_tokens": budget["remaining_tokens"],
            "usage_percentage": usage_pct,
            "status": status,
            "can_continue": can_continue,
            "spending_count": len(budget["spending_log"])
        }
    
    def spend_budget(self, task_id: str, tokens: int, reason: str,
                     agent_id: str = "unknown", operation: str = "unknown") -> dict[str, Any]:
        """
        Record token spending against the task budget.
        This acts as the "Tax Collector" - call before every API/LLM operation.
        
        Returns:
        - allowed: True if spend was recorded
        - blocked: True if budget exceeded (HARD STOP triggered)
        """
        if task_id not in self.budget_tracking:
            return {
                "allowed": False,
                "error": "No budget tracking for this task. Run budget-init first."
            }
        
        budget = self.budget_tracking[task_id]
        
        # Check if we're already over budget
        if budget["status"] == "exhausted":
            return self._trigger_safety_shutdown(task_id, "Budget already exhausted")
        
        # Check if this spend would exceed budget
        new_total = budget["used_tokens"] + tokens
        if new_total > budget["max_tokens"]:
            budget["status"] = "exhausted"
            self._save_state()
            return self._trigger_safety_shutdown(
                task_id, 
                f"Spend of {tokens:,} would exceed budget. "
                f"Current: {budget['used_tokens']:,}/{budget['max_tokens']:,}"
            )
        
        # Record the spend
        spend_record: dict[str, Union[str, int]] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tokens": tokens,
            "reason": reason,
            "agent_id": agent_id,
            "operation": operation,
            "running_total": new_total
        }
        
        budget["spending_log"].append(spend_record)
        budget["used_tokens"] = new_total
        budget["remaining_tokens"] = budget["max_tokens"] - new_total
        
        # Check for warning threshold
        usage_pct = (new_total / budget["max_tokens"]) * 100
        warning = None
        if usage_pct >= BUDGET_WARNING_THRESHOLD * 100:
            warning = f"⚠️ Budget at {usage_pct:.0f}% - complete task soon!"
        
        self._save_state()
        
        return {
            "allowed": True,
            "task_id": task_id,
            "tokens_spent": tokens,
            "reason": reason,
            "used_tokens": new_total,
            "remaining_tokens": budget["remaining_tokens"],
            "usage_percentage": usage_pct,
            "warning": warning
        }
    
    def _trigger_safety_shutdown(self, task_id: str, reason: str) -> dict[str, Any]:
        """
        Trigger a safety shutdown when budget is exceeded.
        This is the HARD STOP that prevents runaway costs.
        """
        log_audit("safety_shutdown", {
            "task_id": task_id,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Mark task as terminated in tracking
        if task_id in self.task_tracking:
            self.task_tracking[task_id]["status"] = "budget_terminated"
            self._save_state()
        
        return {
            "allowed": False,
            "blocked": True,
            "task_id": task_id,
            "reason": "SAFETY_SHUTDOWN",
            "message": f"🛑 BUDGET EXCEEDED: Task '{task_id}' ABORTED. {reason}",
            "action_required": "Task terminated. Do NOT continue. Report to supervisor."
        }
    
    def get_budget_report(self, task_id: str) -> dict[str, Any]:
        """Get detailed spending report for a task."""
        if task_id not in self.budget_tracking:
            return {"error": "No budget tracking for this task."}
        
        budget = self.budget_tracking[task_id]
        
        # Aggregate by operation type
        by_operation: dict[str, int] = {}
        by_agent: dict[str, int] = {}
        
        for spend in budget["spending_log"]:
            op = spend.get("operation", "unknown")
            agent = spend.get("agent_id", "unknown")
            tokens = spend.get("tokens", 0)
            
            by_operation[op] = by_operation.get(op, 0) + tokens
            by_agent[agent] = by_agent.get(agent, 0) + tokens
        
        return {
            "task_id": task_id,
            "summary": {
                "max_tokens": budget["max_tokens"],
                "used_tokens": budget["used_tokens"],
                "remaining_tokens": budget["remaining_tokens"],
                "usage_percentage": (budget["used_tokens"] / budget["max_tokens"]) * 100
            },
            "by_operation": by_operation,
            "by_agent": by_agent,
            "spending_log": budget["spending_log"],
            "created_at": budget["created_at"]
        }

    # ========================================================================
    # SESSIONS_SEND INTERCEPTION (Budget-Aware Handoff)
    # ========================================================================

    def intercept_handoff(self, task_id: str, from_agent: str, to_agent: str,
                          message: str, has_artifact: bool = False) -> dict[str, Any]:
        """
        INTERCEPT every sessions_send call to:
        1. Check budget before allowing handoff
        2. Deduct handoff tax automatically
        3. Record the handoff for tracking
        4. Block if budget exceeded or too many handoffs
        
        This is the MAIN entry point that should wrap every sessions_send.
        
        Usage (in orchestrator code):
            result = guard.intercept_handoff(task_id, "orchestrator", "analyst", message)
            if result["allowed"]:
                sessions_send(to_agent, message)  # Proceed with actual handoff
            else:
                # Handle blocked handoff
        """
        result: dict[str, Any] = {
            "allowed": False,
            "task_id": task_id,
            "from_agent": from_agent,
            "to_agent": to_agent
        }
        
        # Step 1: Check if budget exists (initialize if not)
        budget_status = self.check_budget(task_id)
        if not budget_status.get("initialized"):
            # Auto-initialize with default budget for convenience
            self.init_budget(task_id, DEFAULT_MAX_TOKEN_BUDGET, 
                           f"Auto-initialized for handoff from {from_agent}")
            budget_status = self.check_budget(task_id)
        
        # Step 2: Check if we can continue (budget not exhausted)
        if not budget_status.get("can_continue"):
            result["blocked"] = True
            result["reason"] = "BUDGET_EXHAUSTED"
            result["message"] = f"🛑 Cannot handoff: budget exhausted for task '{task_id}'"
            result["budget_status"] = budget_status
            
            log_audit("handoff_blocked", {
                "task_id": task_id,
                "from": from_agent,
                "to": to_agent,
                "reason": "budget_exhausted"
            })
            
            return result
        
        # Step 3: Calculate handoff cost
        base_cost = TOKEN_COSTS["handoff"]
        message_cost = len(message) // 4  # ~4 chars per token
        total_cost = base_cost + message_cost
        
        # Step 4: Deduct from budget
        spend_result = self.spend_budget(
            task_id, 
            total_cost,
            f"Handoff: {from_agent} → {to_agent}",
            from_agent,
            "handoff"
        )
        
        if spend_result.get("blocked"):
            result["blocked"] = True
            result["reason"] = "BUDGET_EXCEEDED"
            result["message"] = spend_result.get("message")
            result["spend_result"] = spend_result
            return result
        
        # Step 5: Record the handoff (checks handoff tax limits)
        handoff_result = self.record_handoff(
            task_id, from_agent, to_agent, message, has_artifact
        )
        
        if handoff_result.get("blocked"):
            result["blocked"] = True
            result["reason"] = "HANDOFF_TAX_EXCEEDED"
            result["message"] = f"🛑 Handoff blocked: {handoff_result['violations']}"
            result["handoff_result"] = handoff_result
            return result
        
        # Step 6: All checks passed - handoff is allowed
        result["allowed"] = True
        result["tokens_spent"] = total_cost
        result["remaining_budget"] = spend_result.get("remaining_tokens")
        result["handoff_number"] = handoff_result.get("handoff_number")
        result["remaining_handoffs"] = handoff_result.get("remaining", 0)
        
        warnings: list[str] = []
        if spend_result.get("warning"):
            warnings.append(str(spend_result["warning"]))
        
        if handoff_result.get("warnings"):
            warnings.extend([str(w) for w in handoff_result["warnings"]])
        
        result["warnings"] = warnings
        
        log_audit("handoff_allowed", {
            "task_id": task_id,
            "from": from_agent,
            "to": to_agent,
            "tokens_spent": total_cost,
            "handoff_number": handoff_result.get("handoff_number")
        })
        
        return result


def main():
    parser = argparse.ArgumentParser(
        description="Swarm Guard - Prevent Handoff Tax, Silent Failures, and Budget Overruns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  check-handoff      Check handoff tax status for a task
  record-handoff     Record a new handoff (with tax checking)
  intercept-handoff  BUDGET-AWARE handoff (wraps sessions_send)
  validate-result    Validate an agent's result before propagation
  health-check       Check if an agent is healthy
  heartbeat          Record agent heartbeat
  supervisor-review  Full supervisor review of task state
  
  Budget Management (Cost Awareness):
  budget-init        Initialize token budget for a task
  budget-check       Check remaining budget
  budget-spend       Record token spending (the "Tax Collector")
  budget-report      Get detailed spending report

Examples:
  %(prog)s check-handoff --task-id "task_001"
  %(prog)s record-handoff --task-id "task_001" --from orchestrator --to analyst --message "Analyze data"
  %(prog)s intercept-handoff --task-id "task_001" --from orchestrator --to analyst --message "Analyze data"
  %(prog)s validate-result --task-id "task_001" --agent analyst --result '{"status":"ok","output":"...","confidence":0.9}'
  %(prog)s health-check --agent data_analyst
  
  # Cost control:
  %(prog)s budget-init --task-id "task_001" --budget 10000
  %(prog)s budget-spend --task-id "task_001" --tokens 500 --reason "LLM query"
  %(prog)s budget-check --task-id "task_001"
"""
    )
    
    parser.add_argument("command", choices=[
        "check-handoff", "record-handoff", "intercept-handoff", "validate-result",
        "health-check", "heartbeat", "supervisor-review",
        "budget-init", "budget-check", "budget-spend", "budget-report"
    ])
    parser.add_argument("--task-id", "-t", help="Task ID")
    parser.add_argument("--agent", "-a", help="Agent ID")
    parser.add_argument("--from", dest="from_agent", help="Source agent (for record-handoff)")
    parser.add_argument("--to", dest="to_agent", help="Target agent (for record-handoff)")
    parser.add_argument("--message", "-m", help="Handoff message")
    parser.add_argument("--artifact", action="store_true", help="Handoff includes artifact")
    parser.add_argument("--result", "-r", help="Result JSON (for validate-result)")
    parser.add_argument("--status", "-s", default="active", help="Agent status (for heartbeat)")
    parser.add_argument("--budget", "-b", type=int, default=DEFAULT_MAX_TOKEN_BUDGET,
                        help=f"Max token budget (default: {DEFAULT_MAX_TOKEN_BUDGET:,})")
    parser.add_argument("--tokens", type=int, help="Tokens to spend (for budget-spend)")
    parser.add_argument("--reason", help="Reason for spending (for budget-spend)")
    parser.add_argument("--operation", "-o", default="unknown", help="Operation type")
    parser.add_argument("--description", "-d", default="", help="Task description")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    guard = SwarmGuard()
    
    if args.command == "check-handoff":
        if not args.task_id:
            print("Error: --task-id required", file=sys.stderr)
            sys.exit(1)
        result = guard.check_handoff_status(args.task_id)
    
    elif args.command == "record-handoff":
        if not all([args.task_id, args.from_agent, args.to_agent, args.message]):
            print("Error: --task-id, --from, --to, --message required", file=sys.stderr)
            sys.exit(1)
        result = guard.record_handoff(
            args.task_id, args.from_agent, args.to_agent, 
            args.message, args.artifact
        )
    
    elif args.command == "intercept-handoff":
        if not all([args.task_id, args.from_agent, args.to_agent, args.message]):
            print("Error: --task-id, --from, --to, --message required", file=sys.stderr)
            sys.exit(1)
        result = guard.intercept_handoff(
            args.task_id, args.from_agent, args.to_agent, 
            args.message, args.artifact
        )
    
    elif args.command == "validate-result":
        if not all([args.task_id, args.agent, args.result]):
            print("Error: --task-id, --agent, --result required", file=sys.stderr)
            sys.exit(1)
        try:
            result_data = json.loads(args.result)
        except json.JSONDecodeError:
            print("Error: --result must be valid JSON", file=sys.stderr)
            sys.exit(1)
        result = guard.validate_result(args.task_id, args.agent, result_data)
    
    elif args.command == "health-check":
        if not args.agent:
            print("Error: --agent required", file=sys.stderr)
            sys.exit(1)
        result = guard.check_agent_health(args.agent)
    
    elif args.command == "heartbeat":
        if not args.agent:
            print("Error: --agent required", file=sys.stderr)
            sys.exit(1)
        result = guard.agent_heartbeat(args.agent, args.task_id, args.status)
    
    elif args.command == "supervisor-review":
        if not args.task_id:
            print("Error: --task-id required", file=sys.stderr)
            sys.exit(1)
        result = guard.supervisor_review(args.task_id)
    
    # === BUDGET COMMANDS ===
    
    elif args.command == "budget-init":
        if not args.task_id:
            print("Error: --task-id required", file=sys.stderr)
            sys.exit(1)
        result = guard.init_budget(args.task_id, args.budget, args.description)
    
    elif args.command == "budget-check":
        if not args.task_id:
            print("Error: --task-id required", file=sys.stderr)
            sys.exit(1)
        result = guard.check_budget(args.task_id)
    
    elif args.command == "budget-spend":
        if not args.task_id or not args.tokens or not args.reason:
            print("Error: --task-id, --tokens, --reason required", file=sys.stderr)
            sys.exit(1)
        result = guard.spend_budget(
            args.task_id, args.tokens, args.reason,
            args.agent or "unknown", args.operation
        )
    
    elif args.command == "budget-report":
        if not args.task_id:
            print("Error: --task-id required", file=sys.stderr)
            sys.exit(1)
        result = guard.get_budget_report(args.task_id)
    
    else:
        print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
        sys.exit(1)
    
    # Output
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _pretty_print(args.command, result)
    
    # Exit code based on result
    if result.get("blocked") or result.get("verdict") == "BLOCKED":
        sys.exit(2)
    elif not result.get("healthy", True) or not result.get("valid", True):
        sys.exit(1)
    sys.exit(0)


def _pretty_print(command: str, result: dict[str, Any]) -> None:
    """Human-readable output."""
    if command == "check-handoff":
        if not result.get("exists"):
            print(f"📋 Task '{result['task_id']}' not found (new task)")
        else:
            remaining = result.get("remaining", 0)
            status_icon = "🟢" if remaining > 1 else "🟡" if remaining == 1 else "🔴"
            print(f"{status_icon} Task: {result['task_id']}")
            print(f"   Handoffs: {result['handoffs']}/{MAX_HANDOFFS_PER_TASK}")
            print(f"   Remaining: {remaining}")
            print(f"   Artifacts: {result['artifacts_produced']}")
            print(f"   Action Ratio: {result.get('action_ratio', 1):.0%}")
    
    elif command == "record-handoff":
        if result.get("blocked"):
            print("🚫 HANDOFF BLOCKED")
            for v in result.get("violations", []):
                print(f"   ❌ {v}")
        else:
            print(f"✅ Handoff #{result['handoff_number']} recorded")
        
        for w in result.get("warnings", []):
            print(f"   ⚠️  {w}")
    
    elif command == "intercept-handoff":
        if result.get("allowed"):
            print(f"✅ HANDOFF ALLOWED: {result['from_agent']} → {result['to_agent']}")
            print(f"   Task: {result['task_id']}")
            print(f"   Tokens spent: {result.get('tokens_spent', 0):,}")
            print(f"   Budget remaining: {result.get('remaining_budget', 0):,}")
            print(f"   Handoff #{result.get('handoff_number', '?')} (remaining: {result.get('remaining_handoffs', 0)})")
            print("   → Proceed with sessions_send")
            
            for w in result.get("warnings", []):
                print(f"   ⚠️  {w}")
        else:
            print(f"🛑 HANDOFF BLOCKED: {result['from_agent']} → {result['to_agent']}")
            print(f"   Task: {result['task_id']}")
            print(f"   Reason: {result.get('reason', 'Unknown')}")
            print(f"   {result.get('message', '')}")
            print("   → Do NOT call sessions_send")
    
    elif command == "validate-result":
        if result.get("valid"):
            print("✅ RESULT VALID")
            print(f"   Task: {result['task_id']}")
            print(f"   Agent: {result['agent_id']}")
            print(f"   → {result['recommendation']}")
        else:
            print("❌ RESULT INVALID")
            for issue in result.get("issues", []):
                print(f"   ❌ {issue}")
            print(f"   → {result['recommendation']}")
        
        for w in result.get("warnings", []):
            print(f"   ⚠️  {w}")
    
    elif command == "health-check":
        if result.get("healthy"):
            print(f"💚 Agent '{result['agent_id']}' is HEALTHY")
            print(f"   Status: {result.get('status')}")
            print(f"   Last seen: {result.get('seconds_since_heartbeat', 0):.0f}s ago")
        else:
            print(f"💔 Agent '{result['agent_id']}' is UNHEALTHY")
            print(f"   Reason: {result.get('reason')}")
            print(f"   → {result.get('recommendation')}")
    
    elif command == "heartbeat":
        print(f"💓 Heartbeat recorded for '{result['agent_id']}'")
    
    elif command == "supervisor-review":
        verdict = result.get("verdict", "UNKNOWN")
        icon = "✅" if verdict == "APPROVED" else "⚠️" if verdict == "WARNING" else "🚫"
        
        print(f"{icon} SUPERVISOR VERDICT: {verdict}")
        print(f"   Task: {result['task_id']}")
        print(f"   Age: {result.get('age_seconds', 0)/60:.1f} minutes")
        print(f"   Handoffs: {result.get('handoffs', 0)}")
        print(f"   Artifacts: {result.get('artifacts', 0)}")
        
        for issue in result.get("issues", []):
            print(f"   ❌ {issue}")
        
        for rec in result.get("recommendations", []):
            print(f"   💡 {rec}")
    
    # === BUDGET COMMANDS ===
    
    elif command == "budget-init":
        if result.get("initialized"):
            print(f"💰 Budget INITIALIZED for '{result['task_id']}'")
            print(f"   Max tokens: {result['max_tokens']:,}")
        else:
            print(f"❌ Budget init FAILED: {result.get('error')}")
    
    elif command == "budget-check":
        if not result.get("initialized"):
            print(f"❌ {result.get('error')}")
        else:
            usage = result.get("usage_percentage", 0)
            status = result.get("status", "UNKNOWN")
            
            if status == "EXHAUSTED":
                icon = "🛑"
            elif status == "WARNING":
                icon = "⚠️"
            else:
                icon = "💰"
            
            print(f"{icon} Budget Status: {status}")
            print(f"   Task: {result['task_id']}")
            print(f"   Used: {result['used_tokens']:,} / {result['max_tokens']:,} tokens")
            print(f"   Remaining: {result['remaining_tokens']:,} tokens")
            print(f"   Usage: {usage:.1f}%")
            
            # Progress bar
            bar_width = 30
            filled = int(bar_width * usage / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            print(f"   [{bar}]")
            
            if not result.get("can_continue"):
                print("   🚫 Cannot continue - budget exhausted!")
    
    elif command == "budget-spend":
        if result.get("blocked"):
            print("🛑 SAFETY SHUTDOWN TRIGGERED")
            print(f"   {result.get('message')}")
            print(f"   → {result.get('action_required')}")
        elif result.get("allowed"):
            print(f"💸 Spent {result['tokens_spent']:,} tokens")
            print(f"   Reason: {result['reason']}")
            print(f"   Remaining: {result['remaining_tokens']:,} tokens ({100 - result['usage_percentage']:.1f}%)")
            if result.get("warning"):
                print(f"   {result['warning']}")
        else:
            print(f"❌ Spend failed: {result.get('error')}")
    
    elif command == "budget-report":
        if result.get("error"):
            print(f"❌ {result['error']}")
        else:
            summary = result.get("summary", {})
            print(f"📊 Budget Report: {result['task_id']}")
            print(f"   Total Budget: {summary.get('max_tokens', 0):,} tokens")
            print(f"   Used: {summary.get('used_tokens', 0):,} ({summary.get('usage_percentage', 0):.1f}%)")
            print(f"   Remaining: {summary.get('remaining_tokens', 0):,}")
            
            by_op = result.get("by_operation", {})
            if by_op:
                print("\n   By Operation:")
                for op, tokens in sorted(by_op.items(), key=lambda x: -x[1]):
                    print(f"     • {op}: {tokens:,} tokens")
            
            by_agent = result.get("by_agent", {})
            if by_agent:
                print("\n   By Agent:")
                for agent, tokens in sorted(by_agent.items(), key=lambda x: -x[1]):
                    print(f"     • {agent}: {tokens:,} tokens")


if __name__ == "__main__":
    main()
