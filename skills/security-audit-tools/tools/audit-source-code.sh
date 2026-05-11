#!/bin/bash
# Source Code Deep Analysis Script
# Usage: ./audit-source-code.sh /path/to/src

set -e

SRC_DIR=$1

if [ -z "$SRC_DIR" ]; then
    echo "Usage: $0 <path-to-source-directory>"
    echo "Example: $0 ./npm-extract/package/src"
    exit 1
fi

cd "$SRC_DIR"

echo "=== Source Code Deep Analysis ==="
echo "Source directory: $(pwd)"
echo ""

# 0. Statistics
echo "[0/9] Gathering statistics..."
TOTAL_FILES=$(find . -name "*.ts" -o -name "*.js" | wc -l | tr -d ' ')
TOTAL_LINES=$(find . -name "*.ts" -o -name "*.js" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')

echo "Total TypeScript/JavaScript files: $TOTAL_FILES"
echo "Total lines of code: $TOTAL_LINES"
echo ""

# 1. Network requests
echo "[1/9] Analyzing network requests..."
NETWORK_COUNT=$(grep -r "https://\|http://" . --include="*.ts" --include="*.js" 2>/dev/null | grep -v "test\|example\|\.d\.ts" | wc -l | tr -d ' ')

echo "Found $NETWORK_COUNT network request patterns"
echo ""

if [ $NETWORK_COUNT -gt 0 ]; then
    echo "## Network Requests (excluding common domains)"
    grep -rn "https://\|http://" . --include="*.ts" --include="*.js" 2>/dev/null | \
        grep -v "test\|example\|\.d\.ts" | \
        grep -v "polymarket\|github\|example\.com\|localhost\|127\.0\.0\.1" | \
        head -20 || echo "✅ Only known domains found"
    echo ""
fi

# 2. File operations
echo "[2/9] Analyzing file operations..."
FILE_OPS=$(grep -r "fs\.read\|fs\.write\|readFile\|writeFile\|readdir" . --include="*.ts" --include="*.js" 2>/dev/null | wc -l | tr -d ' ')

echo "Found $FILE_OPS file operation patterns"
echo ""

if [ $FILE_OPS -gt 0 ]; then
    echo "## File Operations"
    grep -rn "fs\.read\|fs\.write\|readFile\|writeFile" . --include="*.ts" --include="*.js" 2>/dev/null | head -20
    echo ""
fi

# 3. Process creation
echo "[3/9] Analyzing process creation..."
PROCESS_COUNT=$(grep -r "child_process\|exec(\|spawn(\|execSync" . --include="*.ts" --include="*.js" 2>/dev/null | grep -v "test\|example\|\.d\.ts\|execute.*rate" | wc -l | tr -d ' ')

echo "Found $PROCESS_COUNT process creation patterns"
echo ""

if [ $PROCESS_COUNT -gt 0 ]; then
    echo "## Process Creation (excluding normal usage)"
    grep -rn "child_process\|exec(\|spawn(" . --include="*.ts" --include="*.js" 2>/dev/null | \
        grep -v "test\|example\|\.d\.ts\|execute.*rate" | \
        head -20
    echo ""
fi

# 4. Dynamic code execution
echo "[4/9] Analyzing dynamic code execution..."
DYNAMIC_COUNT=$(grep -r "\beval\b\|new Function\|Function(" . --include="*.ts" --include="*.js" 2>/dev/null | grep -v "test\|example\|\.d\.ts" | wc -l | tr -d ' ')

echo "Found $DYNAMIC_COUNT dynamic code execution patterns"
echo ""

if [ $DYNAMIC_COUNT -gt 0 ]; then
    echo "## Dynamic Code Execution (CRITICAL)"
    grep -rn "\beval\b\|new Function\|Function(" . --include="*.ts" --include="*.js" 2>/dev/null | \
        grep -v "test\|example\|\.d\.ts" | \
        head -20
    echo ""
    echo "⚠️  WARNING: Dynamic code execution detected - requires manual review"
    echo ""
fi

# 5. Environment variables
echo "[5/9] Analyzing environment variable access..."
ENV_COUNT=$(grep -r "process\.env\." . --include="*.ts" --include="*.js" 2>/dev/null | grep -v "test\|example\|\.d\.ts\|comment" | wc -l | tr -d ' ')

echo "Found $ENV_COUNT environment variable accesses"
echo ""

if [ $ENV_COUNT -gt 0 ]; then
    echo "## Environment Variables Used"
    grep -rn "process\.env\." . --include="*.ts" --include="*.js" 2>/dev/null | \
        grep -v "test\|example\|\.d\.ts" | \
        sed 's/process\.env\.//g' | \
        awk -F: '{print $1 ":" $2 ":" $3}' | \
        sort -u | \
        head -20
    echo ""
fi

# 6. Encryption and secrets
echo "[6/9] Analyzing encryption and secrets..."
CRYPTO_COUNT=$(grep -r "crypto\|encrypt\|decrypt\|private.*key\|secret\|password" . --include="*.ts" --include="*.js" 2>/dev/null | grep -v "test\|example\|\.d\.ts\|comment" | wc -l | tr -d ' ')

echo "Found $CRYPTO_COUNT encryption/secret-related patterns"
echo ""

if [ $CRYPTO_COUNT -gt 0 ]; then
    echo "## Encryption and Secrets (requires manual review)"
    grep -rn "crypto\|encrypt\|private.*key" . --include="*.ts" --include="*.js" 2>/dev/null | \
        grep -v "test\|example\|\.d\.ts" | \
        head -20
    echo ""
fi

# 7. Obfuscation patterns
echo "[7/9] Detecting obfuscation..."
OBFUSCATION=$(grep -r "\\x[0-9a-f]\{2\}\|atob\|btoa\|Buffer.*base64\|split.*join" . --include="*.ts" --include="*.js" 2>/dev/null | grep -v "test\|example\|\.d\.ts" | wc -l | tr -d ' ')

echo "Found $OBFUSCATION potential obfuscation patterns"
echo ""

if [ $OBFUSCATION -gt 50 ]; then
    echo "⚠️  WARNING: High obfuscation score - requires manual review"
    echo ""
fi

# 8. Wallet/Key patterns
echo "[8/9] Detecting wallet/key patterns..."
WALLET_COUNT=$(grep -r "wallet\|mnemonic\|seed.*phrase\|keystore\|private.*key" . --include="*.ts" --include="*.js" 2>/dev/null | grep -v "test\|example\|\.d\.ts\|comment" | wc -l | tr -d ' ')

echo "Found $WALLET_COUNT wallet/key-related patterns"
echo ""

if [ $WALLET_COUNT -gt 0 ]; then
    echo "## Wallet/Key Patterns (requires manual review)"
    grep -rn "private.*key\|mnemonic\|seed.*phrase" . --include="*.ts" --include="*.js" 2>/dev/null | \
        grep -v "test\|example\|\.d\.ts\|comment" | \
        head -20
    echo ""
fi

# 9. Import analysis
echo "[9/9] Analyzing imports..."
echo "## Most imported packages"
grep -rh "^import.*from\|require(" . --include="*.ts" --include="*.js" 2>/dev/null | \
    grep -oE "'[^']+'" | \
    tr -d "'" | \
    sort | \
    uniq -c | \
    sort -rn | \
    head -20

echo ""
echo "## External package dependencies"
grep -rh "^import.*from\|require(" . --include="*.ts" --include="*.js" 2>/dev/null | \
    grep -oE "'@[^/]+" | \
    tr -d "'" | \
    sort | \
    uniq -c | \
    sort -rn | \
    head -10

# Summary
echo ""
echo "=== Analysis Summary ==="
echo "Files analyzed: $TOTAL_FILES"
echo "Lines of code: $TOTAL_LINES"
echo ""
echo "Security Indicators:"
echo "- Network requests: $NETWORK_COUNT"
echo "- File operations: $FILE_OPS"
echo "- Process creation: $PROCESS_COUNT"
echo "- Dynamic code: $DYNAMIC_COUNT $(if [ $DYNAMIC_COUNT -gt 0 ]; then echo '⚠️ CRITICAL'; else echo '✅'; fi)"
echo "- Environment vars: $ENV_COUNT"
echo "- Crypto/secrets: $CRYPTO_COUNT"
echo "- Obfuscation score: $OBFUSCATION $(if [ $OBFUSCATION -gt 50 ]; then echo '⚠️ WARNING'; else echo '✅'; fi)"
echo "- Wallet/key patterns: $WALLET_COUNT"
echo ""

# Risk assessment
RISK_SCORE=0
[ $DYNAMIC_COUNT -gt 0 ] && RISK_SCORE=$((RISK_SCORE + 30))
[ $PROCESS_COUNT -gt 5 ] && RISK_SCORE=$((RISK_SCORE + 20))
[ $OBFUSCATION -gt 50 ] && RISK_SCORE=$((RISK_SCORE + 20))
[ $WALLET_COUNT -gt 10 ] && RISK_SCORE=$((RISK_SCORE + 15))

echo "Risk Score: $RISK_SCORE/100"
if [ $RISK_SCORE -ge 50 ]; then
    echo "⚠️  HIGH RISK - Manual review required"
elif [ $RISK_SCORE -ge 30 ]; then
    echo "⚠️  MEDIUM RISK - Review recommended"
else
    echo "✅ LOW RISK"
fi

echo ""
echo "✅ Analysis complete"
