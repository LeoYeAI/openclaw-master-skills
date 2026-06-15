#!/usr/bin/env python3
"""
Validate a task plan structure for completeness and correctness.

Usage:
    python validate-plan.py <plan.json>
    python validate-plan.py --stdin < plan.json
"""

import json
import sys
from typing import Any


def validate_step(step: dict, step_index: int, all_step_ids: set) -> list[str]:
    """Validate a single plan step."""
    errors = []
    prefix = f"Step {step_index + 1}"
    
    # Required fields
    required = ['id', 'title', 'action', 'successCriteria']
    for field in required:
        if field not in step:
            errors.append(f"{prefix}: Missing required field '{field}'")
    
    # ID uniqueness
    if 'id' in step:
        if step['id'] in all_step_ids:
            errors.append(f"{prefix}: Duplicate step ID '{step['id']}'")
        all_step_ids.add(step['id'])
    
    # Dependencies reference valid steps
    deps = step.get('dependencies', [])
    for dep in deps:
        if dep not in all_step_ids and dep != step.get('id'):
            # Allow forward references, but warn
            pass  # Will be checked in second pass
    
    # Complexity is valid
    complexity = step.get('complexity')
    if complexity and complexity not in ['low', 'medium', 'high']:
        errors.append(f"{prefix}: Invalid complexity '{complexity}' (must be low/medium/high)")
    
    # Status is valid
    status = step.get('status')
    if status and status not in ['pending', 'in_progress', 'complete', 'failed', 'skipped']:
        errors.append(f"{prefix}: Invalid status '{status}'")
    
    return errors


def validate_plan(plan: dict) -> list[str]:
    """Validate a complete task plan."""
    errors = []
    
    # Required top-level fields
    if 'steps' not in plan:
        errors.append("Plan missing 'steps' array")
        return errors
    
    steps = plan['steps']
    if not isinstance(steps, list):
        errors.append("'steps' must be an array")
        return errors
    
    if len(steps) == 0:
        errors.append("Plan has no steps")
        return errors
    
    if len(steps) > 10:
        errors.append(f"Plan has too many steps ({len(steps)}). Consider breaking into sub-plans.")
    
    # Collect all step IDs first
    all_step_ids = set()
    for step in steps:
        if 'id' in step:
            all_step_ids.add(step['id'])
    
    # Validate each step
    for i, step in enumerate(steps):
        errors.extend(validate_step(step, i, set(all_step_ids)))
    
    # Check for dependency cycles
    def has_cycle(step_id: str, visited: set, path: set) -> bool:
        if step_id in path:
            return True
        if step_id in visited:
            return False
        
        visited.add(step_id)
        path.add(step_id)
        
        step = next((s for s in steps if s.get('id') == step_id), None)
        if step:
            for dep in step.get('dependencies', []):
                if has_cycle(dep, visited, path):
                    return True
        
        path.remove(step_id)
        return False
    
    visited = set()
    for step in steps:
        if 'id' in step and has_cycle(step['id'], visited, set()):
            errors.append(f"Circular dependency detected involving step '{step['id']}'")
            break
    
    # Check for orphaned dependencies
    for step in steps:
        for dep in step.get('dependencies', []):
            if dep not in all_step_ids:
                errors.append(f"Step '{step.get('id')}' depends on non-existent step '{dep}'")
    
    return errors


def main():
    if len(sys.argv) < 2 or sys.argv[1] == '--stdin':
        data = sys.stdin.read()
    else:
        with open(sys.argv[1]) as f:
            data = f.read()
    
    try:
        plan = json.loads(data)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    errors = validate_plan(plan)
    
    if errors:
        print("Plan validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("Plan is valid ✓")
        print(f"  Steps: {len(plan.get('steps', []))}")
        
        # Show summary
        statuses = {}
        for step in plan.get('steps', []):
            status = step.get('status', 'pending')
            statuses[status] = statuses.get(status, 0) + 1
        
        if statuses:
            print("  Status breakdown:")
            for status, count in sorted(statuses.items()):
                print(f"    {status}: {count}")


if __name__ == '__main__':
    main()
