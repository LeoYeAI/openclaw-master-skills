#!/usr/bin/env bash
set -euo pipefail

# plan-approval.sh — Manage plan approval lifecycle using SHA-256 hashes.
# Approved plans can run autonomously. Modified plans are blocked.

APPROVALS_DIR="$HOME/.openclaw/workflow-automator/approvals"

usage() {
    cat <<'EOF'
Usage: plan-approval.sh <subcommand> [arguments]

Manage workflow plan approvals with expiry.

Subcommands:
  approve <plan.json> [--ttl <days>] [--max-runs <N>]
      Hash and mark a plan as approved.
      --ttl: approval expires after N days (default: 30)
      --max-runs: max autonomous executions before re-approval needed (default: unlimited)

  check <plan.json>      Verify plan hash, expiry, and run budget
  revoke <name>          Revoke approval for a workflow
  list                   Show all approved plans with expiry status

Options:
  --help    Show this help message

Approval records are stored in:
  ~/.openclaw/workflow-automator/approvals/<slug>.json

When a plan is approved, its SHA-256 hash is recorded. Autonomous
runs verify the hash before execution. If the plan file has been
modified since approval, execution is blocked.
EOF
    exit 0
}

[ "${1:-}" = "--help" ] && usage
[ $# -lt 1 ] && { echo "Error: No subcommand provided. Use --help for usage." >&2; exit 1; }

SUBCMD="$1"
shift

mkdir -p "$APPROVALS_DIR"
chmod 700 "$APPROVALS_DIR" 2>/dev/null || true

# Helper: slugify a name
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//'
}

# Helper: compute SHA-256 (macOS + Linux compatible)
compute_hash() {
    if command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$1" | awk '{print $1}'
    elif command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        echo "Error: No SHA-256 tool found (need shasum or sha256sum)" >&2
        exit 1
    fi
}

# Helper: get current timestamp
now_ts() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

case "$SUBCMD" in
    approve)
        [ $# -lt 1 ] && { echo "Error: approve requires: <plan.json>" >&2; exit 1; }
        PLAN_FILE="$1"
        shift
        TTL_DAYS=30
        MAX_RUNS=0  # 0 = unlimited

        FORCE="false"

        while [ $# -gt 0 ]; do
            case "$1" in
                --ttl) TTL_DAYS="$2"; shift 2 ;;
                --max-runs) MAX_RUNS="$2"; shift 2 ;;
                --force) FORCE="true"; shift ;;
                *) shift ;;
            esac
        done

        [ ! -f "$PLAN_FILE" ] && { echo "Error: Plan file not found: $PLAN_FILE" >&2; exit 1; }

        # Validate JSON
        if ! jq empty "$PLAN_FILE" 2>/dev/null; then
            echo "Error: Invalid JSON: $PLAN_FILE" >&2
            exit 1
        fi

        # --- Approval Summary ---
        STEP_COUNT=$(jq '.steps | length' "$PLAN_FILE")
        SHELL_CMDS=$(jq '[.steps[] | select(.command != null and .command != "")] | length' "$PLAN_FILE")
        BROWSER_STEPS=$(jq '[.steps[] | select(.type | startswith("browser"))] | length' "$PLAN_FILE" 2>/dev/null || echo 0)
        FILE_WRITES=$(jq '[.steps[] | select(.type == "file-write")] | length' "$PLAN_FILE" 2>/dev/null || echo 0)
        NOTIFY_STEPS=$(jq '[.steps[] | select(.type == "notify")] | length' "$PLAN_FILE" 2>/dev/null || echo 0)
        URLS=$(jq -r '[.steps[] | select(.url != null) | .url] | unique | .[]' "$PLAN_FILE" 2>/dev/null || true)
        RESTRICTED=$(jq -r '.restricted_mode // false' "$PLAN_FILE" 2>/dev/null || echo "false")

        echo "╔══════════════════════════════════════════╗"
        echo "║         PLAN APPROVAL SUMMARY            ║"
        echo "╠══════════════════════════════════════════╣"
        echo "║ This plan will:                          ║"
        printf "║  • Execute %-3s steps                     ║\n" "$STEP_COUNT"
        printf "║  • Run %-3s shell commands                ║\n" "$SHELL_CMDS"
        printf "║  • Perform %-3s browser actions           ║\n" "$BROWSER_STEPS"
        printf "║  • Write %-3s files                       ║\n" "$FILE_WRITES"
        printf "║  • Send %-3s notifications                ║\n" "$NOTIFY_STEPS"
        echo "╠══════════════════════════════════════════╣"
        if [ -n "$URLS" ]; then
            echo "║ URLs accessed:                           ║"
            echo "$URLS" | while read -r url; do
                printf "║  → %-38s ║\n" "$url"
            done
            echo "╠══════════════════════════════════════════╣"
        fi
        printf "║ Restricted mode: %-24s ║\n" "$RESTRICTED"
        printf "║ TTL: %-3s days | Max runs: %-15s ║\n" "$TTL_DAYS" "$([ "$MAX_RUNS" -gt 0 ] && echo "$MAX_RUNS" || echo "unlimited")"
        echo "╚══════════════════════════════════════════╝"
        echo ""

        # --- Risk Score ---
        RISK_SCORE=0
        [ "$SHELL_CMDS" -gt 0 ] && RISK_SCORE=$((RISK_SCORE + SHELL_CMDS))
        [ "$BROWSER_STEPS" -gt 0 ] && RISK_SCORE=$((RISK_SCORE + BROWSER_STEPS * 2))
        [ "$FILE_WRITES" -gt 0 ] && RISK_SCORE=$((RISK_SCORE + FILE_WRITES))

        RISK_LEVEL="LOW"
        [ "$RISK_SCORE" -ge 5 ] && RISK_LEVEL="MEDIUM"
        [ "$RISK_SCORE" -ge 10 ] && RISK_LEVEL="HIGH"

        echo "Risk assessment: $RISK_LEVEL (score: $RISK_SCORE)"

        # --- Mandatory review for HIGH risk ---
        if [ "$RISK_LEVEL" = "HIGH" ] && [ "$FORCE" = "false" ]; then
            echo ""
            echo "WARNING: This plan has a HIGH risk score."
            echo "Review all commands and URLs above carefully."
            printf "Type APPROVE to confirm, or Ctrl+C to cancel: "
            read -r high_risk_confirm
            if [ "$high_risk_confirm" != "APPROVE" ]; then
                echo "Cancelled. Use --force to bypass, or type APPROVE."
                exit 1
            fi
        fi

        # Compute hash
        HASH=$(compute_hash "$PLAN_FILE")

        # Get workflow name
        WORKFLOW_NAME=$(jq -r '.workflow_name // "unnamed"' "$PLAN_FILE")
        SLUG=$(slugify "$WORKFLOW_NAME")
        PLAN_PATH=$(cd "$(dirname "$PLAN_FILE")" && pwd)/$(basename "$PLAN_FILE")
        TS=$(now_ts)

        # Calculate expiry
        EXPIRES_TS=$(date -v "+${TTL_DAYS}d" -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || \
                     date -u -d "+${TTL_DAYS} days" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || \
                     echo "")

        # Store approval
        APPROVAL_FILE="$APPROVALS_DIR/${SLUG}.json"
        jq -n \
            --arg name "$WORKFLOW_NAME" \
            --arg path "$PLAN_PATH" \
            --arg hash "$HASH" \
            --arg ts "$TS" \
            --arg expires "$EXPIRES_TS" \
            --argjson ttl "$TTL_DAYS" \
            --argjson max_runs "$MAX_RUNS" \
            '{
                workflow_name: $name,
                plan_path: $path,
                sha256: $hash,
                approved_at: $ts,
                expires_at: $expires,
                ttl_days: $ttl,
                max_runs: $max_runs,
                run_count: 0,
                status: "approved"
            }' > "$APPROVAL_FILE"

        echo "Plan approved: $WORKFLOW_NAME (hash: ${HASH:0:12}...)"
        echo "  Expires: $EXPIRES_TS ($TTL_DAYS days)"
        if [ "$MAX_RUNS" -gt 0 ]; then
            echo "  Max runs: $MAX_RUNS"
        else
            echo "  Max runs: unlimited"
        fi
        echo "  File: $APPROVAL_FILE"
        ;;

    check)
        [ $# -lt 1 ] && { echo "Error: check requires: <plan.json>" >&2; exit 1; }
        PLAN_FILE="$1"
        [ ! -f "$PLAN_FILE" ] && { echo "FAIL: Plan file not found: $PLAN_FILE" >&2; exit 1; }

        # Validate JSON
        if ! jq empty "$PLAN_FILE" 2>/dev/null; then
            echo "FAIL: Invalid JSON: $PLAN_FILE" >&2
            exit 1
        fi

        # Get workflow name and find approval
        WORKFLOW_NAME=$(jq -r '.workflow_name // "unnamed"' "$PLAN_FILE")
        SLUG=$(slugify "$WORKFLOW_NAME")
        APPROVAL_FILE="$APPROVALS_DIR/${SLUG}.json"

        if [ ! -f "$APPROVAL_FILE" ]; then
            echo "FAIL: No approval record found for '$WORKFLOW_NAME'" >&2
            exit 1
        fi

        # Check status
        STATUS=$(jq -r '.status' "$APPROVAL_FILE")
        if [ "$STATUS" = "revoked" ]; then
            echo "FAIL: Plan approval has been revoked for '$WORKFLOW_NAME'" >&2
            exit 1
        fi
        if [ "$STATUS" = "expired" ]; then
            echo "FAIL: Plan approval has expired for '$WORKFLOW_NAME'. Re-approve to continue." >&2
            exit 1
        fi

        # Check expiry
        EXPIRES_AT=$(jq -r '.expires_at // empty' "$APPROVAL_FILE")
        if [ -n "$EXPIRES_AT" ] && [ "$EXPIRES_AT" != "null" ] && [ "$EXPIRES_AT" != "" ]; then
            NOW_TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
            if [[ "$NOW_TS" > "$EXPIRES_AT" ]]; then
                # Mark as expired
                jq --arg ts "$(now_ts)" '.status = "expired" | .expired_at = $ts' "$APPROVAL_FILE" > "${APPROVAL_FILE}.tmp" && mv "${APPROVAL_FILE}.tmp" "$APPROVAL_FILE"
                TTL_DAYS=$(jq -r '.ttl_days // 30' "$APPROVAL_FILE")
                echo "FAIL: Plan approval expired on $EXPIRES_AT (TTL: ${TTL_DAYS} days). Re-approve to continue." >&2
                exit 1
            fi
        fi

        # Check run budget
        MAX_RUNS=$(jq -r '.max_runs // 0' "$APPROVAL_FILE")
        RUN_COUNT=$(jq -r '.run_count // 0' "$APPROVAL_FILE")
        if [ "$MAX_RUNS" -gt 0 ] && [ "$RUN_COUNT" -ge "$MAX_RUNS" ]; then
            echo "FAIL: Run budget exhausted for '$WORKFLOW_NAME' ($RUN_COUNT/$MAX_RUNS runs used). Re-approve to continue." >&2
            exit 1
        fi

        # Compare hashes
        CURRENT_HASH=$(compute_hash "$PLAN_FILE")
        STORED_HASH=$(jq -r '.sha256' "$APPROVAL_FILE")

        if [ "$CURRENT_HASH" = "$STORED_HASH" ]; then
            # Increment run count
            jq '.run_count = (.run_count // 0) + 1' "$APPROVAL_FILE" > "${APPROVAL_FILE}.tmp" && mv "${APPROVAL_FILE}.tmp" "$APPROVAL_FILE"
            REMAINING=""
            if [ "$MAX_RUNS" -gt 0 ]; then
                REMAINING=" (run $((RUN_COUNT + 1))/$MAX_RUNS)"
            fi
            echo "PASS: Plan hash verified for '$WORKFLOW_NAME'$REMAINING"
            exit 0
        else
            echo "FAIL: Plan has been modified since approval (expected: ${STORED_HASH:0:12}..., got: ${CURRENT_HASH:0:12}...)" >&2
            exit 1
        fi
        ;;

    revoke)
        [ $# -lt 1 ] && { echo "Error: revoke requires: <name>" >&2; exit 1; }
        NAME="$1"
        SLUG=$(slugify "$NAME")
        APPROVAL_FILE="$APPROVALS_DIR/${SLUG}.json"

        [ ! -f "$APPROVAL_FILE" ] && { echo "Error: No approval record found for '$NAME'" >&2; exit 1; }

        TS=$(now_ts)
        jq --arg ts "$TS" '.status = "revoked" | .revoked_at = $ts' "$APPROVAL_FILE" > "${APPROVAL_FILE}.tmp" && mv "${APPROVAL_FILE}.tmp" "$APPROVAL_FILE"
        echo "Approval revoked: $NAME"
        ;;

    list)
        found=0
        printf "%-22s %-10s %-12s %-8s %-20s\n" "NAME" "STATUS" "RUNS" "TTL" "EXPIRES"
        printf "%-22s %-10s %-12s %-8s %-20s\n" "----" "------" "----" "---" "-------"

        for f in "$APPROVALS_DIR"/*.json; do
            [ ! -f "$f" ] && continue
            found=1
            name=$(jq -r '.workflow_name // "?"' "$f")
            status=$(jq -r '.status // "?"' "$f")
            run_count=$(jq -r '.run_count // 0' "$f")
            max_runs=$(jq -r '.max_runs // 0' "$f")
            ttl_days=$(jq -r '.ttl_days // "?"' "$f")
            expires=$(jq -r '.expires_at // "never"' "$f")
            [ "$expires" = "null" ] || [ "$expires" = "" ] && expires="never"

            if [ "$max_runs" -gt 0 ] 2>/dev/null; then
                runs_str="$run_count/$max_runs"
            else
                runs_str="$run_count"
            fi

            printf "%-22s %-10s %-12s %-8s %-20s\n" "$name" "$status" "$runs_str" "${ttl_days}d" "$expires"
        done

        if [ "$found" -eq 0 ]; then
            echo "(no approvals found)"
        fi
        ;;

    *)
        echo "Error: Unknown subcommand '$SUBCMD'. Use --help for usage." >&2
        exit 1
        ;;
esac
