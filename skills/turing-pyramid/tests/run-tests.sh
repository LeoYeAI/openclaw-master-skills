#!/usr/bin/env bash
# Turing Pyramid Test Runner
# Usage: ./run-tests.sh [unit|integration|all]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0

run_test() {
    local test_file="$1"
    local test_name="$(basename "$test_file" .sh)"
    
    if [[ ! -x "$test_file" ]]; then
        echo -e "${YELLOW}SKIP${NC} $test_name (not executable)"
        ((SKIPPED++)) || true
        return
    fi
    
    if WORKSPACE="$SKILL_DIR" "$test_file" >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC} $test_name"
        ((PASSED++)) || true
    else
        echo -e "${RED}FAIL${NC} $test_name"
        ((FAILED++)) || true
    fi
}

run_suite() {
    local suite_dir="$1"
    local suite_name="$(basename "$suite_dir")"
    
    if [[ ! -d "$suite_dir" ]]; then
        echo "Suite not found: $suite_dir"
        return
    fi
    
    echo ""
    echo "=== $suite_name tests ==="
    
    for test_file in "$suite_dir"/test_*.sh; do
        [[ -e "$test_file" ]] || continue
        run_test "$test_file"
    done
}

# Main
echo "🔺 Turing Pyramid Test Suite"
echo "============================"

case "${1:-all}" in
    unit)
        run_suite "$SCRIPT_DIR/unit"
        ;;
    integration)
        run_suite "$SCRIPT_DIR/integration"
        ;;
    all)
        run_suite "$SCRIPT_DIR/unit"
        run_suite "$SCRIPT_DIR/integration"
        ;;
    *)
        echo "Usage: $0 [unit|integration|all]"
        exit 1
        ;;
esac

echo ""
echo "============================"
echo -e "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}, ${YELLOW}$SKIPPED skipped${NC}"

[[ $FAILED -eq 0 ]]
