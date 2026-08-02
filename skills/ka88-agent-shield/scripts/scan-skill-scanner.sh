#!/bin/bash
# ka88-agent-shield - Full Scan with skill-scanner + LM Studio

# ============================================================================
# CONFIGURATION
# ============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Debug
DEBUG="${DEBUG:-0}"

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PATH="${VENV_PATH:-$PROJECT_DIR/.venv}"

# LM Studio settings
LM_STUDIO_URL="${LM_STUDIO_URL:-http://localhost:1234/v1}"
MODEL="${MODEL:-qwen3-35b-a3b}"

# Limits
TIMEOUT_LM_STUDIO="${TIMEOUT_LM_STUDIO:-5}"
MAX_SCAN_TIME="${MAX_SCAN_TIME:-300}"  # 5 minutes

# ============================================================================
# LOGGING
# ============================================================================

log() {
    local level="$1"
    local message="$2"

    case "$level" in
        ERROR)   echo -e "${RED}[ERROR]${NC} $message" ;;
        WARN)    echo -e "${YELLOW}[WARN]${NC} $message" ;;
        INFO)    echo -e "${BLUE}[INFO]${NC} $message" ;;
        DEBUG)   [ "$DEBUG" = "1" ] && echo -e "${CYAN}[DEBUG]${NC} $message" ;;
        *)       echo "$message" ;;
    esac
}

# ============================================================================
# CHECK LM STUDIO
# ============================================================================

check_lm_studio() {
    log INFO "Checking LM Studio..."

    if ! curl -s --connect-timeout "$TIMEOUT_LM_STUDIO" "$LM_STUDIO_URL/models" > /dev/null 2>&1; then
        log ERROR "LM Studio unavailable: $LM_STUDIO_URL"
        log ERROR "Make sure:"
        log ERROR "  1. LM Studio is running"
        log ERROR "  2. Model is loaded into memory"
        log ERROR "  3. Server is enabled in Developer tab"
        return 1
    fi

    # Get models list (works on macOS and Linux)
    local models_json=$(curl -s "$LM_STUDIO_URL/models" 2>/dev/null)
    local models=$(echo "$models_json" | sed 's/"id":/\n/g' | grep -v '^$' | sed 's/.*"\([^"]*\)".*/\1/' | grep -v '^data' | tr '\n' ' ')
    log INFO "Available models: $models"

    # Check if any model is loaded (use first available)
    if [ -n "$models" ]; then
        log INFO "LM Studio available"
        return 0
    fi

    log ERROR "No models loaded in LM Studio"
    return 1
}

# ============================================================================
# CHECK SKILL-SCANNER
# ============================================================================

check_skill_scanner() {
    log INFO "Checking skill-scanner..."

    # Look for skill-scanner in multiple locations
    local scanner_paths=(
        "$VENV_PATH/bin/skill-scanner"
        "$PROJECT_DIR/.venv/bin/skill-scanner"
        "$(which skill-scanner 2>/dev/null)"
    )

    for path in "${scanner_paths[@]}"; do
        if [ -f "$path" ]; then
            log INFO "skill-scanner found: $path"
            SKILL_SCANNER_PATH="$path"
            return 0
        fi
    done

    log WARN "skill-scanner not found"
    return 1
}

# ============================================================================
# INSTALL SKILL-SCANNER (optional)
# ============================================================================

install_skill_scanner() {
    log INFO "Attempting to install skill-scanner..."

    # Create virtual environment if not exists
    if [ ! -d "$VENV_PATH" ]; then
        log INFO "Creating virtual environment..."
        python3 -m venv "$VENV_PATH" 2>/dev/null || {
            log ERROR "Failed to create virtual environment"
            return 1
        }
    fi

    # Activate and install
    if [ -f "$VENV_PATH/bin/activate" ]; then
        source "$VENV_PATH/bin/activate"
        pip install --quiet cisco-ai-skill-scanner 2>/dev/null || {
            log WARN "Failed to install skill-scanner"
            log WARN "Use: pip install cisco-ai-skill-scanner"
            return 1
        }
        deactivate 2>/dev/null
        log INFO "skill-scanner installed"
        return 0
    fi

    return 1
}

# ============================================================================
# VALIDATION
# ============================================================================

validate_input() {
    if [ -z "$1" ]; then
        echo "Usage: $0 <path-to-scan> [options]"
        echo ""
        echo "Scans directory using skill-scanner + LM Studio"
        echo ""
        echo "Options:"
        echo "  --install    Install skill-scanner if missing"
        echo "  --force      Use even without LLM"
        echo "  --help       Show help"
        echo ""
        echo "Environment variables:"
        echo "  LM_STUDIO_URL      LM Studio URL (default: http://localhost:1234/v1)"
        echo "  MODEL              Model name (default: qwen3-35b-a3b)"
        echo "  VENV_PATH          Path to virtual environment"
        echo "  DEBUG=1            Enable debug"
        echo ""
        echo "Examples:"
        echo "  $0 ./my-skill"
        echo "  LM_STUDIO_URL=http://localhost:1234/v1 $0 ./my-skill"
        exit 1
    fi
}

# ============================================================================
# MAIN LOGIC
# ============================================================================

main() {
    local target_path=""
    local do_install=false
    local force_mode=false

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --install) do_install=true ;;
            --force) force_mode=true ;;
            --help) validate_input "" ;;
            *) target_path="$1" ;;
        esac
        shift
    done

    validate_input "$target_path"

    # Check path exists
    if [ ! -e "$target_path" ]; then
        log ERROR "Path does not exist: $target_path"
        exit 1
    fi

    echo "========================================"
    echo "ka88-agent-shield - Full Scan"
    echo "========================================"
    echo ""

    # Check LM Studio
    if ! check_lm_studio; then
        if [ "$force_mode" = "false" ]; then
            log WARN "Falling back to quick-scan..."
            "$SCRIPT_DIR/quick-scan.sh" "$target_path"
            exit $?
        fi
    fi

    # Check skill-scanner
    local has_scanner=false
    if check_skill_scanner; then
        has_scanner=true
    elif [ "$do_install" = "true" ]; then
        if install_skill_scanner; then
            has_scanner=true
        fi
    fi

    # Run scan
    echo ""
    if [ "$has_scanner" = "true" ]; then
        log INFO "Running skill-scanner..."

        # Set environment variables
        export SKILL_SCANNER_LLM_BASE_URL="$LM_STUDIO_URL"
        export SKILL_SCANNER_LLM_API_KEY="not-needed"
        export SKILL_SCANNER_LLM_MODEL="$MODEL"
        export SKILL_SCANNER_LLM_PROVIDER="openai"

        log DEBUG "LLM URL: $SKILL_SCANNER_LLM_BASE_URL"
        log DEBUG "Model: $SKILL_SCANNER_LLM_MODEL"

        # Run with timeout (cross-platform)
        if command -v timeout &> /dev/null; then
            timeout "$MAX_SCAN_TIME" "$SKILL_SCANNER_PATH" scan "$target_path" \
                --use-llm \
                --use-behavioral \
                --policy balanced \
                --format summary
            local exit_code=$?
            if [ $exit_code -eq 124 ]; then
                log WARN "Scan exceeded timeout ($MAX_SCAN_TIME sec)"
            fi
        elif command -v perl &> /dev/null; then
            perl -e 'alarm shift; exec @ARGV' "$MAX_SCAN_TIME" "$SKILL_SCANNER_PATH" scan "$target_path" \
                --use-llm \
                --use-behavioral \
                --policy balanced \
                --format summary 2>&1
        else
            # No timeout - run directly
            "$SKILL_SCANNER_PATH" scan "$target_path" \
                --use-llm \
                --use-behavioral \
                --policy balanced \
                --format summary
        fi

    else
        log WARN "skill-scanner unavailable - using quick-scan"
        "$SCRIPT_DIR/quick-scan.sh" "$target_path"
    fi

    echo ""
    echo "========================================"
    echo "Scan Complete"
    echo "========================================"
}

main "$@"