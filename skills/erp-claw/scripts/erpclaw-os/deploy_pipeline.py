#!/usr/bin/env python3
"""ERPClaw OS — Auto-Deploy Pipeline

End-to-end deployment orchestrator. Full flow:
  1. Validate module (constitution check)
  2. Sandbox test execution
  3. Tier classification
  4. Decision: auto-deploy (T0-1), queue for human (T2), reject (T3)
  5. Record audit trail

Produces deployment report (JSON) with all step results.
"""
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from validate_module import validate_module_static
from sandbox import run_in_sandbox
from tier_classifier import classify_action
from deploy_audit import record_deployment, ensure_deploy_audit_table
from regression_gate import run_regression

# Tier thresholds for deployment decisions
TIER_AUTO_DEPLOY = 1    # Tier 0-1: auto-deploy
TIER_HUMAN_REVIEW = 2   # Tier 2: queue for human approval
TIER_REJECT = 3          # Tier 3: reject (human-only modification)


def run_pipeline(module_path, db_path=None, src_root=None, skip_sandbox=False):
    """Run the full deployment pipeline for a module.

    Args:
        module_path: Path to the module directory
        db_path: Path to SQLite database
        src_root: Path to src/ directory (for validation)
        skip_sandbox: Skip sandbox testing (for pre-tested modules)

    Returns:
        dict with pipeline_result, steps, tier, reasoning, audit_id
    """
    pipeline_start = time.time()
    module_name = os.path.basename(module_path)
    steps = []

    # -----------------------------------------------------------------------
    # Step 1: Constitution Validation
    # -----------------------------------------------------------------------
    step_start = time.time()
    try:
        validation = validate_module_static(module_path)
        validation_passed = validation.get("result") != "fail"
        step_result = "pass" if validation_passed else "fail"
        violations = validation.get("violations", [])
    except Exception as e:
        step_result = "error"
        validation_passed = False
        violations = [str(e)]

    steps.append({
        "step_name": "constitution_validation",
        "result": step_result,
        "duration_ms": int((time.time() - step_start) * 1000),
        "details": {
            "passed": validation_passed,
            "violation_count": len(violations),
        },
    })

    if not validation_passed:
        audit_id = _record_and_return(
            module_name, "failed", None, steps,
            "Constitution validation failed", db_path,
        )
        return _pipeline_result("failed", steps, None, audit_id, pipeline_start,
                                "Blocked at step 1: constitution validation failed")

    # -----------------------------------------------------------------------
    # Step 2: Sandbox Test Execution
    # -----------------------------------------------------------------------
    if not skip_sandbox:
        step_start = time.time()
        try:
            sandbox_result = run_in_sandbox(module_path)
            sandbox_passed = sandbox_result.get("result") == "pass"
            step_result = "pass" if sandbox_passed else "fail"
        except Exception as e:
            step_result = "error"
            sandbox_passed = False
            sandbox_result = {"error": str(e)}

        steps.append({
            "step_name": "sandbox_testing",
            "result": step_result,
            "duration_ms": int((time.time() - step_start) * 1000),
            "details": {
                "passed": sandbox_passed,
                "tests_run": sandbox_result.get("tests_run", 0),
                "tests_passed": sandbox_result.get("tests_passed", 0),
                "tests_failed": sandbox_result.get("tests_failed", 0),
            },
        })

        if not sandbox_passed:
            audit_id = _record_and_return(
                module_name, "failed", None, steps,
                "Sandbox testing failed", db_path,
            )
            return _pipeline_result("failed", steps, None, audit_id, pipeline_start,
                                    "Blocked at step 2: sandbox tests failed")
    else:
        steps.append({
            "step_name": "sandbox_testing",
            "result": "skipped",
            "duration_ms": 0,
            "details": {"reason": "skip_sandbox=True"},
        })

    # -----------------------------------------------------------------------
    # Step 3: Tier Classification
    # -----------------------------------------------------------------------
    step_start = time.time()
    tier_result = classify_action("deploy-module", module_name=module_name)
    tier = tier_result.get("tier", 2)

    steps.append({
        "step_name": "tier_classification",
        "result": "pass",
        "duration_ms": int((time.time() - step_start) * 1000),
        "details": {
            "tier": tier,
            "tier_name": tier_result.get("tier_name", "unknown"),
            "reasoning": tier_result.get("reasoning", ""),
        },
    })

    # -----------------------------------------------------------------------
    # Step 4: Deployment Decision
    # -----------------------------------------------------------------------
    if tier <= TIER_AUTO_DEPLOY:
        pipeline_result = "deployed"
        reasoning = f"Tier {tier} — auto-deployed (autonomous deployment allowed)"
    elif tier == TIER_HUMAN_REVIEW:
        pipeline_result = "queued"
        reasoning = f"Tier {tier} — queued for human review (module lifecycle operation)"
    else:
        pipeline_result = "rejected"
        reasoning = f"Tier {tier} — rejected (human-only operation, requires manual intervention)"

    steps.append({
        "step_name": "deployment_decision",
        "result": pipeline_result,
        "duration_ms": 0,
        "details": {
            "tier": tier,
            "decision": pipeline_result,
            "reasoning": reasoning,
        },
    })

    # -----------------------------------------------------------------------
    # Record Audit
    # -----------------------------------------------------------------------
    audit_id = _record_and_return(
        module_name, pipeline_result, tier, steps, reasoning, db_path,
    )

    return _pipeline_result(pipeline_result, steps, tier, audit_id, pipeline_start, reasoning)


def _record_and_return(module_name, pipeline_result, tier, steps, reasoning, db_path):
    """Record deployment in audit log, return audit ID."""
    try:
        return record_deployment(
            module_name=module_name,
            pipeline_result=pipeline_result,
            tier=tier,
            steps=steps,
            reasoning=reasoning,
            db_path=db_path,
        )
    except Exception:
        return None


def _pipeline_result(pipeline_result, steps, tier, audit_id, start_time, reasoning):
    """Build the pipeline result dict."""
    return {
        "result": pipeline_result,
        "pipeline_result": pipeline_result,
        "steps": steps,
        "tier": tier,
        "audit_id": audit_id,
        "reasoning": reasoning,
        "duration_ms": int((time.time() - start_time) * 1000),
    }


# ---------------------------------------------------------------------------
# CLI Handler
# ---------------------------------------------------------------------------

def handle_deploy_module(args):
    """CLI handler for deploy-module action."""
    module_path = getattr(args, "module_path", None)
    db_path = getattr(args, "db_path", None)
    src_root = getattr(args, "src_root", None)
    skip_sandbox = getattr(args, "skip_sandbox", False)

    if not module_path:
        return {"error": "--module-path is required for deploy-module"}

    if not os.path.isdir(module_path):
        return {"error": f"Module path does not exist: {module_path}"}

    result = run_pipeline(
        module_path,
        db_path=db_path,
        src_root=src_root,
        skip_sandbox=skip_sandbox,
    )
    return result
