#!/bin/bash
# 360Guard Quick Scan Script
# Usage: ./quick-scan.sh /path/to/skill
# Output: Quick risk assessment report

SKILL_PATH=${1:-.}

echo "🔍 360Guard Quick Scan: $SKILL_PATH"
echo "================================"

# Check dangerous functions
echo -e "\n📡 Network request check:"
grep -r "curl\|wget\|fetch\|http\.\|https\.\|socket\|request\|axios" "$SKILL_PATH" \
  --include="*.sh" --include="*.js" --include="*.ts" --include="*.py" 2>/dev/null | head -5

# Check sensitive file access
echo -e "\n🔑 Sensitive path check:"
grep -r "~/.ssh\|~/.aws\|~/.config\|/etc/hosts\|authorized_keys\|keychain\|credentials" "$SKILL_PATH" \
  --include="*.sh" --include="*.js" --include="*.ts" --include="*.py" 2>/dev/null

# Check dangerous commands
echo -e "\n⚠️ Dangerous command check:"
grep -r "eval\|exec\|shell=True\|base64 -d\|openssl\|subprocess" "$SKILL_PATH" \
  --include="*.sh" --include="*.js" --include="*.ts" --include="*.py" 2>/dev/null

# Check persistence
echo -e "\n⏰ Persistence check:"
grep -r "cron\|systemd\|launchd\|login item\|autostart\|startup" "$SKILL_PATH" \
  --include="*.sh" --include="*.js" --include="*.ts" --include="*.py" 2>/dev/null

echo -e "\n✅ Quick scan complete"
