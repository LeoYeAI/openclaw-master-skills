#!/usr/bin/env python3
"""
AuthGuardian Permission Checker

Evaluates permission requests for accessing sensitive resources
(DATABASE, PAYMENTS, EMAIL, FILE_EXPORT).

Usage:
    python check_permission.py --agent AGENT_ID --resource RESOURCE_TYPE \
        --justification "REASON" [--scope SCOPE]
    python check_permission.py --active-grants [--agent AGENT_ID] [--json]
    python check_permission.py --audit-summary [--last N] [--json]

Examples:
    python check_permission.py --agent data_analyst --resource DATABASE \
        --justification "Need customer order history for sales report" \
        --scope "read:orders"

    python check_permission.py --active-grants
    python check_permission.py --active-grants --agent data_analyst --json
    python check_permission.py --audit-summary --last 20 --json
"""

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

# Configuration
GRANT_TOKEN_TTL_MINUTES = 5
GRANTS_FILE = Path(__file__).parent.parent / "data" / "active_grants.json"
AUDIT_LOG = Path(__file__).parent.parent / "data" / "audit_log.jsonl"

# Default trust levels for known agents
DEFAULT_TRUST_LEVELS = {
    "orchestrator": 0.9,
    "data_analyst": 0.8,
    "strategy_advisor": 0.7,
    "risk_assessor": 0.85,
}

# Base risk scores for resource types
BASE_RISKS = {
    "DATABASE": 0.5,      # Internal database access
    "PAYMENTS": 0.7,      # Payment/financial systems
    "EMAIL": 0.4,         # Email sending capability
    "FILE_EXPORT": 0.6,   # Exporting data to files
}

# Default restrictions by resource type
RESTRICTIONS = {
    "DATABASE": ["read_only", "max_records:100"],
    "PAYMENTS": ["read_only", "no_pii_fields", "audit_required"],
    "EMAIL": ["rate_limit:10_per_minute"],
    "FILE_EXPORT": ["anonymize_pii", "local_only"],
}


def ensure_data_dir():
    """Ensure data directory exists."""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def detect_injection(justification: str) -> bool:
    """
    Detect prompt-injection and manipulation patterns in justifications.

    Returns True if the justification looks like a prompt-injection attempt.
    """
    injection_patterns = [
        r'ignore\s+(previous|above|prior|all)',
        r'override\s+(policy|restriction|rule|permission|security)',
        r'system\s*prompt',
        r'you\s+are\s+(now|a)',
        r'act\s+as\s+(if|a|an)',
        r'pretend\s+(to|that|you)',
        r'bypass\s+(security|check|restriction|auth)',
        r'grant\s+(me|access|permission)\s+(anyway|regardless|now)',
        r'disregard\s+(policy|rule|restriction|previous)',
        r'admin\s+(mode|access|override)',
        r'sudo\b',
        r'jailbreak',
        r'do\s+not\s+(check|verify|validate|restrict)',
        r'skip\s+(validation|verification|check)',
        r'trust\s+level\s*[:=]',
        r'score\s*[:=]+\s*[\d.]',
    ]
    text = justification.lower()
    for pattern in injection_patterns:
        if re.search(pattern, text):
            return True
    return False


def score_justification(justification: str) -> float:
    """
    Score the quality of a justification with hardened validation.

    Defenses against prompt injection and keyword stuffing:
    - Injection pattern detection (immediate reject)
    - Maximum length cap (prevents obfuscation in long text)
    - Keyword-stuffing detection (penalises unnatural keyword density)
    - Unique-word ratio check (catches copy-paste padding)
    - Structural coherence (requires natural sentence structure)

    Criteria (after safety checks):
    - Length (more detail = better, but capped)
    - Contains task-related keywords (capped contribution)
    - Contains specificity keywords (capped contribution)
    - No test/debug keywords
    - Structural coherence bonus
    """
    # ----- Hard reject: injection patterns -----
    if detect_injection(justification):
        return 0.0

    # ----- Hard reject: empty or whitespace-only -----
    stripped = justification.strip()
    if not stripped:
        return 0.0

    # ----- Hard cap: excessively long justifications are suspicious -----
    MAX_JUSTIFICATION_LENGTH = 500
    if len(stripped) > MAX_JUSTIFICATION_LENGTH:
        return 0.1  # Suspiciously long — allow re-submission with concise text

    words = stripped.split()
    word_count = len(words)

    # ----- Hard reject: too few words to be meaningful -----
    if word_count < 3:
        return 0.1

    # ----- Repetition / padding detection -----
    unique_words = set(w.lower() for w in words)
    unique_ratio = len(unique_words) / word_count  # word_count >= 3 guaranteed above
    if unique_ratio < 0.4:
        return 0.1  # More than 60% repeated words — likely padding

    # ----- Keyword-stuffing detection -----
    task_keywords = re.findall(
        r'\b(task|purpose|need|require|generate|analyze|create|process)\b',
        stripped, re.IGNORECASE,
    )
    specificity_keywords = re.findall(
        r'\b(specific|particular|exact|quarterly|annual|report|summary)\b',
        stripped, re.IGNORECASE,
    )
    total_matched = len(task_keywords) + len(specificity_keywords)
    keyword_density = total_matched / word_count  # word_count >= 3 guaranteed above
    if keyword_density > 0.5:
        return 0.1  # More than half the words are scoring keywords — stuffing

    # ----- Scoring (defensive caps per category) -----
    score = 0.0

    # Length contribution (max 0.25)
    if len(stripped) > 20:
        score += 0.15
    if len(stripped) > 50:
        score += 0.10

    # Task keyword presence (max 0.20, but only first match counts)
    if task_keywords:
        score += 0.20

    # Specificity keyword presence (max 0.20, but only first match counts)
    if specificity_keywords:
        score += 0.20

    # No test/debug markers (max 0.15)
    if not re.search(r'\b(test|debug|try|experiment)\b', stripped, re.IGNORECASE):
        score += 0.15

    # Structural coherence: sentence-like structure (max 0.20)
    # Must contain at least one verb-like pattern and read like prose
    has_verb = bool(re.search(
        r'\b(is|are|was|were|need|needs|require|requires|must|should|will|'
        r'generate|generating|analyze|analyzing|create|creating|process|processing|'
        r'prepare|preparing|compile|compiling|review|reviewing|access|accessing|'
        r'retrieve|retrieving|export|exporting|send|sending|run|running)\b',
        stripped, re.IGNORECASE,
    ))
    has_noun_object = bool(re.search(
        r'\b(data|report|records|invoices?|orders?|customers?|accounts?|'
        r'transactions?|files?|emails?|results?|metrics?|statistics?|'
        r'analysis|documents?|exports?|payments?|entries|logs?|summaries)\b',
        stripped, re.IGNORECASE,
    ))
    if has_verb and has_noun_object:
        score += 0.20

    return min(score, 1.0)


def assess_risk(resource_type: str, scope: Optional[str] = None) -> float:
    """
    Assess the risk level of a permission request.
    
    Factors:
    - Base risk of resource type
    - Scope breadth (broad scopes = higher risk)
    - Write operations (higher risk)
    """
    risk = BASE_RISKS.get(resource_type, 0.5)
    
    # Broad scopes increase risk
    if not scope or scope in ("*", "all"):
        risk += 0.2
    
    # Write operations increase risk
    if scope and re.search(r'\b(write|delete|update|modify|create)\b', scope, re.IGNORECASE):
        risk += 0.2
    
    return min(risk, 1.0)


def generate_grant_token() -> str:
    """Generate a unique grant token."""
    return f"grant_{uuid.uuid4().hex}"


def log_audit(action: str, details: dict[str, Any]) -> None:
    """Append entry to audit log."""
    ensure_data_dir()
    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "details": details
    }
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def save_grant(grant: dict[str, Any]) -> None:
    """Save grant to persistent storage."""
    ensure_data_dir()
    grants = {}
    if GRANTS_FILE.exists():
        try:
            grants = json.loads(GRANTS_FILE.read_text())
        except json.JSONDecodeError:
            grants = {}
    
    grants[grant["token"]] = grant
    GRANTS_FILE.write_text(json.dumps(grants, indent=2))


def evaluate_permission(agent_id: str, resource_type: str, 
                       justification: str, scope: Optional[str] = None) -> dict[str, Any]:
    """
    Evaluate a permission request using weighted scoring.
    
    Weights:
    - Justification Quality: 40%
    - Agent Trust Level: 30%
    - Risk Assessment: 30%
    """
    # Log the request
    log_audit("permission_request", {
        "agent_id": agent_id,
        "resource_type": resource_type,
        "justification": justification,
        "scope": scope
    })
    
    # 1. Justification Quality (40% weight)
    justification_score = score_justification(justification)
    if justification_score < 0.3:
        return {
            "granted": False,
            "reason": "Justification is insufficient. Please provide specific task context.",
            "scores": {
                "justification": justification_score,
                "trust": None,
                "risk": None
            }
        }
    
    # 2. Agent Trust Level (30% weight)
    trust_level = DEFAULT_TRUST_LEVELS.get(agent_id, 0.5)
    if trust_level < 0.4:
        return {
            "granted": False,
            "reason": "Agent trust level is below threshold. Escalate to human operator.",
            "scores": {
                "justification": justification_score,
                "trust": trust_level,
                "risk": None
            }
        }
    
    # 3. Risk Assessment (30% weight)
    risk_score = assess_risk(resource_type, scope)
    if risk_score > 0.8:
        return {
            "granted": False,
            "reason": "Risk assessment exceeds acceptable threshold. Narrow the requested scope.",
            "scores": {
                "justification": justification_score,
                "trust": trust_level,
                "risk": risk_score
            }
        }
    
    # Calculate weighted approval score
    weighted_score = (
        justification_score * 0.4 +
        trust_level * 0.3 +
        (1 - risk_score) * 0.3
    )
    
    if weighted_score < 0.5:
        return {
            "granted": False,
            "reason": f"Combined evaluation score ({weighted_score:.2f}) below threshold (0.5).",
            "scores": {
                "justification": justification_score,
                "trust": trust_level,
                "risk": risk_score,
                "weighted": weighted_score
            }
        }
    
    # Generate grant
    token = generate_grant_token()
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=GRANT_TOKEN_TTL_MINUTES)).isoformat()
    restrictions = RESTRICTIONS.get(resource_type, [])
    
    grant: dict[str, Any] = {
        "token": token,
        "agent_id": agent_id,
        "resource_type": resource_type,
        "scope": scope,
        "expires_at": expires_at,
        "restrictions": restrictions,
        "granted_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Save grant and log
    save_grant(grant)
    log_audit("permission_granted", grant)
    
    return {
        "granted": True,
        "token": token,
        "expires_at": expires_at,
        "restrictions": restrictions,
        "scores": {
            "justification": justification_score,
            "trust": trust_level,
            "risk": risk_score,
            "weighted": weighted_score
        }
    }


def list_active_grants(agent_filter: Optional[str] = None, as_json: bool = False) -> int:
    """
    Show which agents currently hold access to which APIs with expiry times.

    Reads data/active_grants.json, filters out expired grants,
    and displays remaining grants with TTL.
    """
    if not GRANTS_FILE.exists():
        if as_json:
            print(json.dumps({"grants": [], "total": 0, "expired_cleaned": 0}))
        else:
            print("No active grants. (No grants file found.)")
        return 0

    try:
        grants = json.loads(GRANTS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        if as_json:
            print(json.dumps({"error": "Could not read grants file"}))
        else:
            print("Error: Could not read grants file.")
        return 1

    now = datetime.now(timezone.utc)
    active: list[dict[str, Any]] = []
    expired_count = 0

    for token, grant in grants.items():
        try:
            expires_at = datetime.fromisoformat(grant["expires_at"])
        except (KeyError, ValueError):
            expired_count += 1
            continue

        if expires_at <= now:
            expired_count += 1
            continue

        if agent_filter and grant.get("agent_id") != agent_filter:
            continue

        remaining = expires_at - now
        minutes_left = remaining.total_seconds() / 60

        active.append({
            "token": token[:16] + "..." if len(token) > 16 else token,
            "token_full": token,
            "agent_id": grant.get("agent_id", "unknown"),
            "resource_type": grant.get("resource_type", "unknown"),
            "scope": grant.get("scope"),
            "granted_at": grant.get("granted_at", "unknown"),
            "expires_at": grant["expires_at"],
            "minutes_remaining": round(minutes_left, 1),
            "restrictions": grant.get("restrictions", []),
        })

    # Sort by expiry (soonest first)
    active.sort(key=lambda g: g["expires_at"])

    if as_json:
        # In JSON mode, include full tokens
        output: dict[str, Any] = {
            "grants": active,
            "total": len(active),
            "expired_cleaned": expired_count,
        }
        print(json.dumps(output, indent=2))
    else:
        if not active:
            filter_msg = f" for agent '{agent_filter}'" if agent_filter else ""
            print(f"No active grants{filter_msg}. ({expired_count} expired.)")
        else:
            filter_msg = f" (agent: {agent_filter})" if agent_filter else ""
            print(f"Active Grants{filter_msg}:")
            print(f"{'='*70}")
            for g in active:
                print(f"  Agent:       {g['agent_id']}")
                print(f"  Resource:    {g['resource_type']}")
                if g["scope"]:
                    print(f"  Scope:       {g['scope']}")
                print(f"  Token:       {g['token']}")
                print(f"  Granted:     {g['granted_at']}")
                print(f"  Expires:     {g['expires_at']}")
                print(f"  Remaining:   {g['minutes_remaining']} min")
                if g["restrictions"]:
                    print(f"  Restrictions: {', '.join(g['restrictions'])}")
                print(f"  {'-'*66}")
            print(f"\nTotal: {len(active)} active, {expired_count} expired")

    return 0


def audit_summary(last_n: int = 20, as_json: bool = False) -> int:
    """
    Summarize recent permission requests, grants, and denials.

    Parses data/audit_log.jsonl and produces per-agent and per-resource
    breakdowns plus recent activity.
    """
    if not AUDIT_LOG.exists():
        if as_json:
            print(json.dumps({"entries": 0, "summary": {}, "recent": []}))
        else:
            print("No audit log found. (No permission requests recorded yet.)")
        return 0

    entries: list[dict[str, Any]] = []
    try:
        with open(AUDIT_LOG, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except OSError:
        if as_json:
            print(json.dumps({"error": "Could not read audit log"}))
        else:
            print("Error: Could not read audit log.")
        return 1

    if not entries:
        if as_json:
            print(json.dumps({"entries": 0, "summary": {}, "recent": []}))
        else:
            print("Audit log is empty.")
        return 0

    # Aggregate stats
    total_requests = 0
    total_grants = 0
    by_agent: dict[str, dict[str, int]] = {}
    by_resource: dict[str, dict[str, int]] = {}

    for entry in entries:
        action = entry.get("action", "")
        details = entry.get("details", {})
        agent_id = details.get("agent_id", "unknown")
        resource_type = details.get("resource_type", "unknown")

        if action == "permission_request":
            total_requests += 1
            by_agent.setdefault(agent_id, {"requests": 0, "grants": 0})
            by_agent[agent_id]["requests"] += 1
            by_resource.setdefault(resource_type, {"requests": 0, "grants": 0})
            by_resource[resource_type]["requests"] += 1
        elif action == "permission_granted":
            total_grants += 1
            by_agent.setdefault(agent_id, {"requests": 0, "grants": 0})
            by_agent[agent_id]["grants"] += 1
            by_resource.setdefault(resource_type, {"requests": 0, "grants": 0})
            by_resource[resource_type]["grants"] += 1

    total_denials = total_requests - total_grants

    # Recent entries (last N)
    recent = entries[-last_n:]

    # Time range
    first_ts = entries[0].get("timestamp", "unknown")
    last_ts = entries[-1].get("timestamp", "unknown")

    if as_json:
        output: dict[str, Any] = {
            "total_entries": len(entries),
            "total_requests": total_requests,
            "total_grants": total_grants,
            "total_denials": total_denials,
            "time_range": {"first": first_ts, "last": last_ts},
            "by_agent": by_agent,
            "by_resource": by_resource,
            "recent": recent[-last_n:],
        }
        print(json.dumps(output, indent=2))
    else:
        print("Audit Summary")
        print(f"{'='*70}")
        print(f"  Log entries:  {len(entries)}")
        print(f"  Time range:   {first_ts}")
        print(f"                {last_ts}")
        print(f"")
        print(f"  Requests:     {total_requests}")
        print(f"  Grants:       {total_grants}")
        print(f"  Denials:      {total_denials}")
        grant_rate = (total_grants / total_requests * 100) if total_requests > 0 else 0
        print(f"  Grant Rate:   {grant_rate:.0f}%")

        if by_agent:
            print(f"\n  By Agent:")
            print(f"  {'-'*50}")
            print(f"  {'Agent':<20} {'Requests':>10} {'Grants':>10} {'Denials':>10}")
            print(f"  {'-'*50}")
            for agent_id, stats in sorted(by_agent.items()):
                denials = stats["requests"] - stats["grants"]
                print(f"  {agent_id:<20} {stats['requests']:>10} {stats['grants']:>10} {denials:>10}")

        if by_resource:
            print(f"\n  By Resource:")
            print(f"  {'-'*50}")
            print(f"  {'Resource':<20} {'Requests':>10} {'Grants':>10} {'Denials':>10}")
            print(f"  {'-'*50}")
            for resource_type, stats in sorted(by_resource.items()):
                denials = stats["requests"] - stats["grants"]
                print(f"  {resource_type:<20} {stats['requests']:>10} {stats['grants']:>10} {denials:>10}")

        print(f"\n  Recent Activity (last {min(last_n, len(recent))}):")
        print(f"  {'-'*66}")
        for entry in recent:
            ts = entry.get("timestamp", "?")[:19]
            action = entry.get("action", "?")
            details = entry.get("details", {})
            agent_id = details.get("agent_id", "?")
            resource_type = details.get("resource_type", "?")
            symbol = "GRANT" if action == "permission_granted" else "REQ" if action == "permission_request" else action.upper()
            print(f"  {ts}  [{symbol:>5}]  {agent_id} -> {resource_type}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="AuthGuardian Permission Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Check permission:
    %(prog)s --agent data_analyst --resource DATABASE \\
        --justification "Need Q4 invoice data for quarterly report"

  List active grants:
    %(prog)s --active-grants
    %(prog)s --active-grants --agent data_analyst --json

  View audit summary:
    %(prog)s --audit-summary
    %(prog)s --audit-summary --last 50 --json
"""
    )

    # Action flags
    parser.add_argument(
        "--active-grants",
        action="store_true",
        help="List all active (non-expired) permission grants"
    )
    parser.add_argument(
        "--audit-summary",
        action="store_true",
        help="Show audit log summary with per-agent and per-resource breakdowns"
    )
    parser.add_argument(
        "--last",
        type=int,
        default=20,
        help="Number of recent audit entries to show (default: 20)"
    )

    # Permission check args (required only for check mode)
    parser.add_argument(
        "--agent", "-a",
        help="Agent ID requesting permission (required for check; optional filter for --active-grants)"
    )
    parser.add_argument(
        "--resource", "-r",
        choices=["DATABASE", "PAYMENTS", "EMAIL", "FILE_EXPORT"],
        help="Resource type to access"
    )
    parser.add_argument(
        "--justification", "-j",
        help="Business justification for the request"
    )
    parser.add_argument(
        "--scope", "-s",
        help="Specific scope of access (e.g., 'read:invoices')"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )

    args = parser.parse_args()

    # --- Action: --active-grants ---
    if args.active_grants:
        sys.exit(list_active_grants(agent_filter=args.agent, as_json=args.json))

    # --- Action: --audit-summary ---
    if args.audit_summary:
        sys.exit(audit_summary(last_n=args.last, as_json=args.json))

    # --- Default action: permission check ---
    if not args.agent:
        parser.error("--agent is required for permission checks")
    if not args.resource:
        parser.error("--resource is required for permission checks")
    if not args.justification:
        parser.error("--justification is required for permission checks")

    result = evaluate_permission(
        agent_id=args.agent,
        resource_type=args.resource,
        justification=args.justification,
        scope=args.scope
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["granted"]:
            print("GRANTED")
            print(f"Token: {result['token']}")
            print(f"Expires: {result['expires_at']}")
            print(f"Restrictions: {', '.join(result['restrictions'])}")
        else:
            print("DENIED")
            print(f"Reason: {result['reason']}")

        print("\nEvaluation Scores:")
        scores = result["scores"]
        if scores.get("justification") is not None:
            print(f"  Justification: {scores['justification']:.2f}")
        if scores.get("trust") is not None:
            print(f"  Trust Level:   {scores['trust']:.2f}")
        if scores.get("risk") is not None:
            print(f"  Risk Score:    {scores['risk']:.2f}")
        if scores.get("weighted") is not None:
            print(f"  Weighted:      {scores['weighted']:.2f}")

    sys.exit(0 if result["granted"] else 1)


if __name__ == "__main__":
    main()
