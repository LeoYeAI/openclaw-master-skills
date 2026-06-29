#!/bin/bash
# audit-config.sh — Scan a directory for cleartext secrets before checkpoint
#
# Usage (sourced):
#   source "$SCRIPT_DIR/audit-config.sh"
#   scan_for_secrets "$CONTENT_DIR"       # exits 1 if secrets found
#   scan_for_secrets "$CONTENT_DIR" force  # warns but continues
#
# Usage (standalone):
#   ./audit-config.sh <directory> [--force]

# Secret patterns to detect (shared with pre-commit-check.sh)
_SECRET_PATTERNS=(
    'ghp_[a-zA-Z0-9]{36}'                          # GitHub PAT (classic)
    'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}'   # GitHub PAT (fine-grained)
    'sk-[a-zA-Z0-9]{48}'                            # OpenAI API key
    'sk-proj-[a-zA-Z0-9_-]{80,}'                    # OpenAI project key
    'solvr_[a-zA-Z0-9_-]{30,}'                      # Solvr API key
    'am_[a-zA-Z0-9]{60,}'                           # AgentMail API key
    'moltbook_sk_[a-zA-Z0-9_-]{30,}'                # Moltbook API key
    'whsec_[a-zA-Z0-9]{30,}'                        # Webhook secret
    'AKIA[0-9A-Z]{16}'                              # AWS Access Key
    'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.'       # JWT tokens
    '[0-9]{8,10}:AA[a-zA-Z0-9_-]{33,}'              # Telegram bot tokens
)

_SECRET_PATTERN_NAMES=(
    "GitHub PAT (classic)"
    "GitHub PAT (fine-grained)"
    "OpenAI API key"
    "OpenAI project key"
    "Solvr API key"
    "AgentMail API key"
    "Moltbook API key"
    "Webhook secret"
    "AWS Access Key"
    "JWT token"
    "Telegram bot token"
)

# scan_for_secrets <directory> [force]
# Returns 0 if clean, exits 1 if secrets found (unless force mode)
scan_for_secrets() {
    local scan_dir="$1"
    local force_mode="${2:-}"
    local found_secrets=0
    local contaminated_files=()

    if [ ! -d "$scan_dir" ]; then
        echo "ERROR: scan_for_secrets: directory not found: $scan_dir" >&2
        return 1
    fi

    echo "Scanning content for cleartext secrets..."

    # Build file list — skip binary files, .git, node_modules, __pycache__, .amcp checkpoints
    local file_list
    file_list=$(find "$scan_dir" -type f \
        ! -path '*/.git/*' \
        ! -path '*/node_modules/*' \
        ! -path '*/__pycache__/*' \
        ! -path '*.amcp' \
        ! -path '*.pyc' \
        ! -name '*.gz' \
        ! -name '*.tar' \
        ! -name '*.zip' \
        ! -name '*.bin' \
        ! -name '*.so' \
        ! -name '*.o' \
        2>/dev/null || true)

    if [ -z "$file_list" ]; then
        echo "  No scannable files found in $scan_dir"
        return 0
    fi

    local file_count
    file_count=$(echo "$file_list" | wc -l)
    echo "  Scanning $file_count files..."

    while IFS= read -r file; do
        [ -z "$file" ] && continue

        # Skip binary files
        if command -v file >/dev/null 2>&1; then
            if file "$file" 2>/dev/null | grep -q "binary"; then
                continue
            fi
        fi

        for i in "${!_SECRET_PATTERNS[@]}"; do
            if grep -qE "${_SECRET_PATTERNS[$i]}" "$file" 2>/dev/null; then
                # Get path relative to scan dir for cleaner output
                local rel_path="${file#"$scan_dir"/}"
                echo "  🚨 ${_SECRET_PATTERN_NAMES[$i]} found in: $rel_path" >&2
                found_secrets=1
                # Track unique files
                local already_tracked=false
                for cf in "${contaminated_files[@]+"${contaminated_files[@]}"}"; do
                    if [ "$cf" = "$rel_path" ]; then
                        already_tracked=true
                        break
                    fi
                done
                if [ "$already_tracked" = false ]; then
                    contaminated_files+=("$rel_path")
                fi
            fi
        done
    done <<< "$file_list"

    if [ "$found_secrets" -eq 1 ]; then
        echo "" >&2
        if [ "$force_mode" = "force" ]; then
            echo "⚠️  WARNING: Checkpoint contains cleartext secrets in:" >&2
            for cf in "${contaminated_files[@]}"; do
                echo "    - $cf" >&2
            done
            echo "" >&2
            echo "⚠️  Proceeding anyway because --force was specified." >&2
            echo "⚠️  These secrets will be in the checkpoint archive!" >&2
            echo "" >&2
            return 0
        else
            echo "REFUSED: Checkpoint contains cleartext secrets in:" >&2
            for cf in "${contaminated_files[@]}"; do
                echo "    - $cf" >&2
            done
            echo "" >&2
            echo "To fix:" >&2
            echo "  1. Move secrets to ~/.amcp/config.json (proactive-amcp config set <key> <value>)" >&2
            echo "  2. Remove cleartext secrets from the listed files" >&2
            echo "  3. Re-run checkpoint" >&2
            echo "" >&2
            echo "For emergency checkpoints, use --force to bypass this check." >&2
            return 1
        fi
    fi

    echo "  ✓ No cleartext secrets detected"
    return 0
}

# Allow standalone execution
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    set -euo pipefail

    if [ $# -lt 1 ]; then
        echo "Usage: $0 <directory> [--force]"
        exit 1
    fi

    SCAN_DIR="$1"
    FORCE=""
    if [ "${2:-}" = "--force" ]; then
        FORCE="force"
    fi

    scan_for_secrets "$SCAN_DIR" "$FORCE"
fi
