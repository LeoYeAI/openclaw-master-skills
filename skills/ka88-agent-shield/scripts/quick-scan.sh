#!/bin/bash
# ka88-agent-shield - Quick Scan
# Fast pattern-based file scanning WITHOUT LLM

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

# Debug mode (enable with DEBUG=1)
DEBUG="${DEBUG:-0}"

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PATTERNS_FILE="$PROJECT_DIR/config/patterns.yaml"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/quick-scan.log"

# Limits
MAX_FILE_SIZE="${MAX_FILE_SIZE:-10485760}"  # 10MB default
MAX_FILES="${MAX_FILES:-1000}"               # Max files to scan
EXCLUDE_DIRS="${EXCLUDE_DIRS:-node_modules|.venv|venv|dist|build|.git}"

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$level" in
        ERROR)   echo -e "${RED}[ERROR]${NC} $message" ;;
        WARN)    echo -e "${YELLOW}[WARN]${NC} $message" ;;
        INFO)    echo -e "${BLUE}[INFO]${NC} $message" ;;
        DEBUG)   [ "$DEBUG" = "1" ] && echo -e "${CYAN}[DEBUG]${NC} $message" ;;
        *)       echo "$message" ;;
    esac

    if [ -d "$LOG_DIR" ]; then
        echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    fi
}

# ============================================================================
# DEPENDENCY CHECK
# ============================================================================

check_dependencies() {
    local missing=()

    for cmd in grep find; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        log ERROR "Missing required commands: ${missing[*]}"
        log ERROR "Install with: brew install ${missing[*]}"
        return 1
    fi

    log INFO "All dependencies available"
    return 0
}

# ============================================================================
# PROJECT VALIDATION
# ============================================================================

check_project() {
    if [ ! -d "$PROJECT_DIR" ]; then
        log ERROR "Project directory not found: $PROJECT_DIR"
        return 1
    fi

    if [ ! -f "$PROJECT_DIR/SKILL.md" ]; then
        log WARN "SKILL.md not found in project directory"
    fi

    log INFO "Project verified: $PROJECT_DIR"
    return 0
}

# ============================================================================
# INPUT VALIDATION
# ============================================================================

validate_input() {
    if [ -z "$1" ]; then
        echo "Usage: $0 <path-to-scan> [options]"
        echo ""
        echo "Options:"
        echo "  --verbose    Enable verbose output"
        echo "  --dry-run    Test run without scanning"
        echo "  --help       Show this help"
        echo ""
        echo "Environment variables:"
        echo "  DEBUG=1           Enable debug logging"
        echo "  MAX_FILES=1000    Max files to scan"
        echo "  MAX_FILE_SIZE=10M Max file size"
        echo ""
        echo "Examples:"
        echo "  $0 ./src                  Scan directory"
        echo "  $0 ./src --verbose        Scan with debug"
        echo "  DEBUG=1 $0 ./src          Verbose logging"
        exit 1
    fi
}

# ============================================================================
# FILE SCANNING
# ============================================================================

scan_file() {
    local file="$1"
    local findings=0
    local warnings=0

    # Check file size
    local file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
    if [ "$file_size" -gt "$MAX_FILE_SIZE" ]; then
        echo -e "  ${YELLOW}→${NC} Skipped (too large: $((file_size/1024/1024))MB)"
        return 0
    fi

    # Relative path for readability
    local display_path="${file#$PROJECT_DIR/}"
    if [ ${#display_path} -gt 60 ]; then
        display_path="...${display_path: -57}"
    fi

    echo -e "${BLUE}Scanning:${NC} $display_path"

    # Prompt Injection patterns
    if grep -iqE "(ignore\s+(all\s+)?(previous|prior|above|earlier)|disregard|forget\s+everything|do\s+not\s+tell|system\s+prompt|new\s+instructions)" "$file" 2>/dev/null; then
        echo -e "  ${RED}⚠${NC} Prompt Injection patterns detected"
        findings=$((findings + 1))
    fi

    # Credential Exfiltration
    if grep -iqE '(\$\{?[A-Z_]+(KEY|TOKEN|SECRET|PASSWORD)|cat\s+\.env|process\.env|os\.environ|ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{48})' "$file" 2>/dev/null; then
        echo -e "  ${RED}⚠${NC} Credential Exfiltration patterns detected"
        findings=$((findings + 1))
    fi

    # Dangerous Commands (pipe to shell)
    if grep -iqE '(\|\s*(sh|bash|zsh|python)\s*$|\|\s*(sh|bash|zsh)\s+)' "$file" 2>/dev/null; then
        echo -e "  ${RED}⚠${NC} Pipe to Shell patterns detected"
        findings=$((findings + 1))
    fi

    # Dangerous JavaScript
    if grep -iqE '(eval\s*\(|new\s+Function\s*\(|setAttribute\s*\(.*on(load|error)|document\.cookie|localStorage\.setItem|XMLHttpRequest)' "$file" 2>/dev/null; then
        echo -e "  ${RED}⚠${NC} Malicious JavaScript patterns detected"
        findings=$((findings + 1))
    fi

    # SSRF / Localhost
    if grep -iqE '(169\.254\.169\.254|127\.0\.0\.1|localhost|metadata\.google|metadata\.azure|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)' "$file" 2>/dev/null; then
        echo -e "  ${RED}⚠${NC} SSRF patterns detected"
        findings=$((findings + 1))
    fi

    # Obfuscation (warnings only)
    if grep -iqE '(\\\\x[0-9a-fA-F]{2}|\\\\u[0-9a-fA-F]{4}|atob\(|fromCharCode)' "$file" 2>/dev/null; then
        echo -e "  ${YELLOW}⚠${NC} Obfuscation patterns detected"
        warnings=$((warnings + 1))
    fi

    # Zero-width characters
    if grep -aq $'[\xE2\x80\x8B\xE2\x80\x8C\xE2\x80\x8D\xEF\xBB\xBF]' "$file" 2>/dev/null; then
        echo -e "  ${RED}⚠${NC} Zero-width characters detected"
        findings=$((findings + 1))
    fi

    if [ $findings -gt 0 ]; then
        echo -e "  ${RED}→${NC} Issues found: $findings"
    elif [ $warnings -gt 0 ]; then
        echo -e "  ${YELLOW}→${NC} Warnings: $warnings"
    else
        echo -e "  ${GREEN}✓${NC} Clean"
    fi

    echo ""

    return $findings
}

# ============================================================================
# MAIN LOGIC
# ============================================================================

main() {
    local target_path=""
    local dry_run=false

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --verbose) DEBUG=1 ;;
            --dry-run) dry_run=true ;;
            --help)
                validate_input ""
                exit 0
                ;;
            *) target_path="$1" ;;
        esac
        shift
    done

    validate_input "$target_path"

    # Check existence
    if [ ! -e "$target_path" ]; then
        log ERROR "Path does not exist: $target_path"
        exit 1
    fi

    echo "========================================"
    echo "ka88-agent-shield - Quick Scan"
    echo "========================================"
    echo ""

    # Check dependencies
    if ! check_dependencies; then
        exit 1
    fi

    # Check project
    if ! check_project; then
        log WARN "Continuing with warning..."
    fi

    # Dry-run mode
    if [ "$dry_run" = "true" ]; then
        log INFO "Dry-run mode - testing configuration"
        log INFO "Target path: $target_path"
        log INFO "Max files: $MAX_FILES"
        log INFO "Max file size: $((MAX_FILE_SIZE/1024/1024))MB"
        log INFO "Excluded directories: $EXCLUDE_DIRS"
        exit 0
    fi

    # Statistics
    local files_scanned=0
    local issues_found=0

    # Scan
    if [ -d "$target_path" ]; then
        echo -e "${YELLOW}Mode:${NC} Directory scan"
        echo ""

        local file_count=0
        while IFS= read -r file; do
            if [ $file_count -ge $MAX_FILES ]; then
                echo -e "${YELLOW}File limit reached: $MAX_FILES${NC}"
                break
            fi

            scan_file "$file"
            local result=$?
            files_scanned=$((files_scanned + 1))

            if [ $result -gt 0 ]; then
                issues_found=$((issues_found + result))
            fi

            file_count=$((file_count + 1))
        done < <(find "$target_path" -type f \( \
            -name "*.md" -o \
            -name "*.js" -o \
            -name "*.ts" -o \
            -name "*.py" -o \
            -name "*.sh" -o \
            -name "*.json" -o \
            -name "*.html" -o \
            -name "*.css" -o \
            -name "*.xml" -o \
            -name "*.yaml" -o \
            -name "*.yml" \
            \) -not -path "*/$EXCLUDE_DIRS/*" 2>/dev/null)

    elif [ -f "$target_path" ]; then
        echo -e "${YELLOW}Mode:${NC} File scan"
        echo ""

        scan_file "$target_path"
        local result=$?
        files_scanned=1
        issues_found=$result
    fi

    # Final report
    echo "========================================"
    echo "Quick Scan Complete"
    echo "========================================"
    echo ""
    echo -e "Files scanned:    ${BLUE}$files_scanned${NC}"
    echo -e "Issues found:    ${RED}$issues_found${NC}"
    echo ""
    echo "Note: This is a quick regex-based scanner."
    echo "For full analysis use scan-skill-scanner.sh with LLM."
    echo ""
    echo "Options:"
    echo "  --dry-run    Test run (verify config)"
    echo "  DEBUG=1 $0  Verbose logging"

    # Exit code
    if [ $issues_found -gt 0 ]; then
        exit 2  # Issues found
    fi
    exit 0
}

# Run
main "$@"