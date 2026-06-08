#!/bin/bash
# 360Guard Full Scan Script
# Usage: ./full-scan.sh /path/to/skill

SKILL_PATH=${1:-.}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT="$SKILL_PATH/360guard-report-$TIMESTAMP.txt"

echo "🛡️ 360Guard Full Scan: $SKILL_PATH"
echo "========================================"

{
  echo "🛡️ 360Guard Complete Security Scan Report"
  echo "========================================"
  echo "Scan time: $(date)"
  echo "Scan path: $SKILL_PATH"
  echo ""

  # 1. File structure check
  echo "📁 File structure:"
  find "$SKILL_PATH" -type f 2>/dev/null | head -30
  echo ""

  # 2. Dangerous function scan
  echo "⚠️ Dangerous function scan:"
  for pattern in "eval(" "exec(" "shell=True" "base64" "subprocess" "importlib" "__import__" "pickle" "yaml.load" "xmlrpc" "socket.create_connection"; do
    result=$(grep -r "$pattern" "$SKILL_PATH" --include="*.sh" --include="*.js" --include="*.ts" --include="*.py" 2>/dev/null)
    if [ -n "$result" ]; then
      echo "  ❌ Found: $pattern"
    fi
  done
  echo ""

  # 3. Sensitive path scan
  echo "🔑 Sensitive path scan:"
  for pattern in "~/.ssh" "~/.aws" "~/.config" "/etc/hosts" "authorized_keys" "keychain" "credentials" ".env"; do
    result=$(grep -r "$pattern" "$SKILL_PATH" --include="*.sh" --include="*.js" --include="*.ts" --include="*.py" 2>/dev/null)
    if [ -n "$result" ]; then
      echo "  ⚠️ Warning: $pattern"
    fi
  done
  echo ""

  # 4. Network request scan
  echo "🌐 Network request scan:"
  grep -r "http://\|https://\|wget\|curl\|fetch" "$SKILL_PATH" --include="*.sh" --include="*.js" --include="*.ts" --include="*.py" 2>/dev/null | grep -v "^#" | head -10
  echo ""

  # 5. Persistence check
  echo "⏰ Persistence check:"
  for pattern in "cron" "systemd" "launchd" "login item" "startup" "autostart"; do
    result=$(grep -ri "$pattern" "$SKILL_PATH" --include="*.sh" --include="*.js" --include="*.ts" --include="*.py" 2>/dev/null)
    if [ -n "$result" ]; then
      echo "  🔴 High risk: $pattern"
    fi
  done
  echo ""

  # 6. Dependency check
  echo "📦 Dependency check:"
  [ -f "$SKILL_PATH/package.json" ] && echo "  package.json exists" && cat "$SKILL_PATH/package.json" | grep -E "dependencies|devDependencies" -A 20
  [ -f "$SKILL_PATH/requirements.txt" ] && echo "  requirements.txt exists" && cat "$SKILL_PATH/requirements.txt"
  echo ""

  # 7. Binary file check
  echo "💾 Binary file check:"
  find "$SKILL_PATH" -type f \( -name "*.so" -o -name "*.dylib" -o -name "*.exe" -o -name "*.bin" -o -name "*.dll" \) 2>/dev/null
  echo ""

  # 8. Symbolic link check
  echo "🔗 Symbolic link check:"
  find "$SKILL_PATH" -type l 2>/dev/null
  echo ""

  echo "========================================"
  echo "✅ Full scan complete"
} | tee "$REPORT"

echo ""
echo "📄 Report saved to: $REPORT"
