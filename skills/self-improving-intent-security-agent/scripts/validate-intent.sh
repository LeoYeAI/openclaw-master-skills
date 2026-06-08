#!/usr/bin/env bash
# Validate intent specification format
#
# This script validates the format of intent markdown files.
# It does NOT require any environment variables or credentials.
# It only reads the specified intent file and checks for required sections.
# No data is transmitted externally.

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <intent-file.md>"
    exit 1
fi

INTENT_FILE="$1"

if [ ! -f "$INTENT_FILE" ]; then
    echo "Error: File not found: $INTENT_FILE"
    exit 1
fi

echo "Validating intent: $INTENT_FILE"
echo ""

# Check for required sections
ERRORS=0

# Check for ID header
if ! grep -q "^## \[INT-[0-9]\{8\}-.*\]" "$INTENT_FILE"; then
    echo "✗ Missing or invalid intent ID (format: INT-YYYYMMDD-XXX)"
    ERRORS=$((ERRORS + 1))
else
    echo "✓ Valid intent ID"
fi

# Check for Goal section
if ! grep -q "^### Goal" "$INTENT_FILE"; then
    echo "✗ Missing 'Goal' section"
    ERRORS=$((ERRORS + 1))
else
    echo "✓ Has 'Goal' section"
fi

# Check for Constraints section
if ! grep -q "^### Constraints" "$INTENT_FILE"; then
    echo "✗ Missing 'Constraints' section"
    ERRORS=$((ERRORS + 1))
else
    echo "✓ Has 'Constraints' section"
fi

# Check for Expected Behavior section
if ! grep -q "^### Expected Behavior" "$INTENT_FILE"; then
    echo "✗ Missing 'Expected Behavior' section"
    ERRORS=$((ERRORS + 1))
else
    echo "✓ Has 'Expected Behavior' section"
fi

# Check for Risk Level
if ! grep -q "^\*\*Risk Level\*\*:" "$INTENT_FILE"; then
    echo "✗ Missing 'Risk Level' field"
    ERRORS=$((ERRORS + 1))
else
    echo "✓ Has 'Risk Level' field"
fi

# Check for Status
if ! grep -q "^\*\*Status\*\*:" "$INTENT_FILE"; then
    echo "✗ Missing 'Status' field"
    ERRORS=$((ERRORS + 1))
else
    echo "✓ Has 'Status' field"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✓ Intent is valid"
    exit 0
else
    echo "✗ Found $ERRORS error(s)"
    exit 1
fi
