---
name: 360Guard
description: 360-degree comprehensive security review Skill. Use before installing any Skill from ClawHub, GitHub, or other sources. Performs full security scans including all Skill Vetter checks plus extended system/privacy/behavior checks and automated scanning scripts. Supports static analysis, behavior detection, dependency auditing.
---

# 360Guard 🛡️

> 360-degree comprehensive security review — Like antivirus for your Skills

## 1. When to Use

- Before installing any Skill from ClawHub
- Before installing any Skill from GitHub or other sources
- When evaluating code shared by other Agents
- Any time you're asked to install unknown code
- Periodic audit of installed Skills (recommended monthly)
- Before running high-risk Skills for second verification

## 2. Core Principles

```
┌─────────────────────────────────────────────────────────────┐
│  🛑 Security Layer Priority                                 │
├─────────────────────────────────────────────────────────────┤
│  ⛔ EXTREME → Absolutely refuse to install                  │
│  🔴 HIGH    → Requires human approval                       │
│  🟡 MEDIUM  → Full code review + limited permissions        │
│  🟢 LOW     → Basic review OK                               │
└─────────────────────────────────────────────────────────────┘
```

## 3. Security Checklist

### 3.1 Base Red Flags (from Skill Vetter)

```
🚨 Reject immediately if you see:
────────────────────────────────────────────────────────────
• curl/wget to unknown URLs
• Sends data to external servers
• Requests credentials/tokens/API keys
• Reads ~/.ssh, ~/.aws, ~/.config without clear reason
• Accesses MEMORY.md, USER.md, SOUL.md, IDENTITY.md
• Uses base64 decode on anything
• Uses eval() or exec() with external input
• Modifies system files outside workspace
• Installs packages without listing them
• Network calls to IPs instead of domains
• Obfuscated code (compressed, encoded, minified)
• Requests elevated/sudo permissions
• Accesses browser cookies/sessions
• Touches credential files
────────────────────────────────────────────────────────────
```

### 3.2 Extended Red Flags (New)

#### 3.2.1 Persistence & Auto-start

```
🔴 Persistence check:
• Creates cron job / systemd service
• Modifies ~/.ssh/authorized_keys
• Writes to /etc/hosts
• Adds Login Items / Startup Items
• Modifies .bashrc / .zshrc / profile
• Registers LaunchAgent (macOS)
• Installs systemd user service
```

#### 3.2.2 Monitoring & Eavesdropping

```
🔴 Monitoring permissions check:
• Requests screen capture/recording (screencapture)
• Requests audio recording permission
• Keyloggers
• Accesses microphone/camera
• File system monitoring (fswatch/inotify)
```

#### 3.2.3 Data & Privacy

```
🔴 Data theft check:
• Reads clipboard (pbpaste)
• Reads environment variables (especially API_, SECRET, TOKEN)
• Accesses browser history/bookmarks
• Accesses macOS Keychain
• Accesses iMessage/SMS
• Accesses contacts/calendar
• Accesses photo library
```

#### 3.2.4 Network & Communication

```
🔴 Network anomaly check:
• Initiates reverse shell (nc -e / bash -i)
• Uses Tor proxy
• DNS queries to suspicious domains
• WebSocket long connections
• IRC connections
• Non-standard ports (>65535 or <1024 unusual)
• Hardcoded IP addresses (non-local)
```

#### 3.2.5 Code Execution (Advanced)

```
🔴 Dynamic execution check:
• Dynamic import (importlib.import_module)
• __import__() dynamic loading
• compile() dynamic compilation
• xmlrpc / jsonrpc remote calls
• pickle / yaml / marshal deserialization
• exec() / eval() any string
• subprocess shell=True
```

#### 3.2.6 File System

```
🟡 File operation check:
• Writes to executable paths outside /tmp
• Modifies /usr/local/bin
• Writes .dmg/.pkg installers
• Creates .hidden files/directories
• File permission modification (chmod +x)
• Symbolic links (pointing external)
• Contains binary files (.so/.dylib/.exe/.bin)
```

#### 3.2.7 Dependencies & Supply Chain

```
🟡 Supply chain check:
• Dependency version range too wide (>1.0.0 not ^1.0.0)
• Dependencies from private/unknown sources
• Dependencies on deprecated packages
• Silent additional dependency downloads
• References other unvetted Skills
• Uses git submodule (may point to malicious repo)
```

#### 3.2.8 Social Engineering

```
🟡 Social engineering check:
• Mimics popular Skill names (e.g., "github", "weather-ai")
• README overpromises ("one-click to do everything...")
• No source code, only compiled binaries
• Author has no history
• Downloads vs stars ratio suspicious (fake reviews)
```

---

## 4. Risk Classification

| Risk Level | Example Checks | Action |
|------------|----------------|--------|
| 🟢 LOW | Text processing, weather, note formatting | Basic review, OK to install |
| 🟡 MEDIUM | File I/O, browser control, API calls | Full review + limited permissions |
| 🔴 HIGH | Credential access, Keychain, network requests | Human approval + sandbox test |
| ⛔ EXTREME | Persistence, root access, keylogging, reverse shell | **Refuse** |

---

## 5. Trust Hierarchy

| Source | Review Level | Recommendation |
|--------|--------------|----------------|
| Official OpenClaw Skills | Low (still review) | Basic check |
| High-star Repo (1000+) | Medium | Standard check |
| Known Authors | Medium | Standard check |
| Unknown Sources | High | Full check |
| Requests credentials | Extreme | **Refuse** |
| Modifies system files | Extreme | **Refuse** |

---

## 6. Automated Scanning Scripts

### 6.1 Quick Scan (quick-scan.sh)

```bash
#!/bin/bash
# Usage: ./quick-scan.sh /path/to/skill
# Output: Quick risk assessment report

SKILL_PATH=$1
echo "🔍 360Guard Quick Scan: $SKILL_PATH"
echo "================================"

# Check dangerous functions
echo -e "\n📡 Network request check:"
grep -r "curl\|wget\|fetch\|http\.\|https\.\|socket" "$SKILL_PATH" --include="*.sh" --include="*.js" --include="*.py" | head -5

# Check sensitive file access
echo -e "\n🔑 Sensitive path check:"
grep -r "~/.ssh\|~/.aws\|~/.config\|/etc/hosts\|authorized_keys" "$SKILL_PATH" --include="*.sh" --include="*.js" --include="*.py"

# Check dangerous commands
echo -e "\n⚠️ Dangerous command check:"
grep -r "eval\|exec\|shell=True\|base64 -d\|openssl" "$SKILL_PATH" --include="*.sh" --include="*.js" --include="*.py"

echo -e "\n✅ Quick scan complete"
```

### 6.2 Full Scan (full-scan.sh)

```bash
#!/bin/bash
# Usage: ./full-scan.sh /path/to/skill
# Output: Complete security assessment report

SKILL_PATH=$1
REPORT="$SKILL_PATH/360guard-report.txt"

echo "🛡️ 360Guard Full Scan: $SKILL_PATH" | tee "$REPORT"
echo "========================================" | tee -a "$REPORT"

# 1. File structure check
echo -e "\n📁 File structure:" | tee -a "$REPORT"
find "$SKILL_PATH" -type f | head -20 | tee -a "$REPORT"

# 2. Dangerous function scan
echo -e "\n⚠️ Dangerous function scan:" | tee -a "$REPORT"
for pattern in "eval(" "exec(" "shell=True" "base64" "subprocess" "importlib" "__import__" "pickle" "yaml.load" "xmlrpc" "socket.create_connection"; do
  result=$(grep -r "$pattern" "$SKILL_PATH" --include="*.sh" --include="*.js" --include="*.py" 2>/dev/null)
  if [ -n "$result" ]; then
    echo "  ❌ Found: $pattern" | tee -a "$REPORT"
    echo "$result" | head -3 | tee -a "$REPORT"
  fi
done

# 3. Sensitive path scan
echo -e "\n🔑 Sensitive path scan:" | tee -a "$REPORT"
for pattern in "~/.ssh" "~/.aws" "~/.config" "/etc/hosts" "authorized_keys" "keychain" "credentials" ".env"; do
  result=$(grep -r "$pattern" "$SKILL_PATH" --include="*.sh" --include="*.js" --include="*.py" 2>/dev/null)
  if [ -n "$result" ]; then
    echo "  ⚠️ Warning: $pattern" | tee -a "$REPORT"
  fi
done

# 4. Network request scan
echo -e "\n🌐 Network request scan:" | tee -a "$REPORT"
grep -r "http://\|https://\|wget\|curl\|fetch" "$SKILL_PATH" --include="*.sh" --include="*.js" --include="*.py" | grep -v "^#" | head -10 | tee -a "$REPORT"

# 5. Persistence check
echo -e "\n⏰ Persistence check:" | tee -a "$REPORT"
for pattern in "cron" "systemd" "launchd" "login item" "startup" "autostart"; do
  result=$(grep -ri "$pattern" "$SKILL_PATH" --include="*.sh" --include="*.js" --include="*.py" 2>/dev/null)
  if [ -n "$result" ]; then
    echo "  🔴 High risk: $pattern" | tee -a "$REPORT"
  fi
done

# 6. Dependency check
echo -e "\n📦 Dependency check:" | tee -a "$REPORT"
if [ -f "$SKILL_PATH/package.json" ]; then
  cat "$SKILL_PATH/package.json" | grep -E "dependencies|devDependencies" -A 20 | tee -a "$REPORT"
fi
if [ -f "$SKILL_PATH/requirements.txt" ]; then
  cat "$SKILL_PATH/requirements.txt" | tee -a "$REPORT"
fi
if [ -f "$SKILL_PATH/package.yaml" ]; then
  cat "$SKILL_PATH/package.yaml" | tee -a "$REPORT"
fi

# 7. Binary file check
echo -e "\n💾 Binary file check:" | tee -a "$REPORT"
find "$SKILL_PATH" -type f \( -name "*.so" -o -name "*.dylib" -o -name "*.exe" -o -name "*.bin" -o -name "*.dll" \) 2>/dev/null | tee -a "$REPORT"

echo -e "\n========================================" | tee -a "$REPORT"
echo "✅ Full scan complete, report saved to: $REPORT"
```

### 6.3 Node.js Scanner (scanner.js)

```javascript
#!/usr/bin/env node
/**
 * 360Guard Node.js Scanner
 * Usage: node scanner.js /path/to/skill
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const DANGER_PATTERNS = {
  CRITICAL: [
    { pattern: /eval\s*\(/, name: 'eval() execution' },
    { pattern: /exec\s*\(/, name: 'exec() execution' },
    { pattern: /shell\s*=\s*true/i, name: 'subprocess shell=True' },
    { pattern: /base64.*decode/i, name: 'base64 decode' },
    { pattern: /pickle\.load/i, name: 'pickle deserialization' },
    { pattern: /yaml\.load/i, name: 'yaml deserialization' },
    { pattern: /__import__\s*\(/, name: 'dynamic import' },
    { pattern: /importlib\.import_module/i, name: 'dynamic module load' },
    { pattern: /xmlrpc/i, name: 'XML-RPC remote call' },
    { pattern: /reverse.*shell|nc\s+-e|bash\s+-i/i, name: 'reverse shell' }
  ],
  HIGH: [
    { pattern: /curl\s+/, name: 'curl request' },
    { pattern: /wget\s+/, name: 'wget download' },
    { pattern: /fetch\s*\(/, name: 'fetch request' },
    { pattern: /https?:\/\/\d{1,3}\.\d{1,3}/, name: 'direct IP connection' },
    { pattern: /process\.env/i, name: 'environment variable access' },
    { pattern: /child_process/, name: 'subprocess execution' }
  ],
  MEDIUM: [
    { pattern: /\/\.ssh\//, name: 'SSH directory access' },
    { pattern: /\/\.aws\//, name: 'AWS directory access' },
    { pattern: /keychain/i, name: 'Keychain access' },
    { pattern: /credentials|token|secret/i, name: 'credential related' },
    { pattern: /cron|systemd|launchd/i, name: 'persistence mechanism' }
  ]
};

function scanFile(filePath) {
  const results = { CRITICAL: [], HIGH: [], MEDIUM: [] };
  
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    
    for (const [level, patterns] of Object.entries(DANGER_PATTERNS)) {
      for (const { pattern, name } of patterns) {
        if (pattern.test(content)) {
          results[level].push({ file: filePath, issue: name });
        }
      }
    }
  } catch (e) {
    // Skip unreadable files
  }
  
  return results;
}

function scanDirectory(dirPath) {
  const allResults = { CRITICAL: [], HIGH: [], MEDIUM: [] };
  
  function walk(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory() && !file.startsWith('.')) {
        walk(fullPath);
      } else if (stat.isFile()) {
        const ext = path.extname(file);
        if (['.js', '.ts', '.py', '.sh', '.bash'].includes(ext)) {
          const results = scanFile(fullPath);
          for (const level of Object.keys(allResults)) {
            allResults[level].push(...results[level]);
          }
        }
      }
    }
  }
  
  walk(dirPath);
  return allResults;
}

function generateReport(skillPath, results) {
  console.log('\n🛡️ 360Guard Security Scan Report');
  console.log('='.repeat(50));
  console.log(`📂 Scan path: ${skillPath}`);
  console.log('');
  
  const riskOrder = ['CRITICAL', 'HIGH', 'MEDIUM'];
  const emoji = { CRITICAL: '🔴', HIGH: '⚠️', MEDIUM: '🟡' };
  
  for (const level of riskOrder) {
    if (results[level].length > 0) {
      console.log(`\n${emoji[level]} ${level} risk (${results[level].length} items):`);
      for (const item of results[level]) {
        console.log(`  • ${item.issue}`);
        console.log(`    File: ${item.file}`);
      }
    }
  }
  
  console.log('\n' + '='.repeat(50));
  
  if (results.CRITICAL.length > 0) {
    console.log('🔴 Conclusion: Critical risks found, NOT recommended to install');
    process.exit(1);
  } else if (results.HIGH.length > 0) {
    console.log('⚠️ Conclusion: High risk found, human approval required');
    process.exit(2);
  } else if (results.MEDIUM.length > 0) {
    console.log('🟡 Conclusion: Medium risk found, please review carefully');
    process.exit(0);
  } else {
    console.log('✅ Conclusion: No obvious risks found');
    process.exit(0);
  }
}

// Main
const skillPath = process.argv[2] || '.';
if (!fs.existsSync(skillPath)) {
  console.error('❌ Path does not exist:', skillPath);
  process.exit(1);
}

const stat = fs.statSync(skillPath);
const results = stat.isDirectory() ? scanDirectory(skillPath) : scanFile(skillPath);

generateReport(skillPath, results);
```

---

## 7. Output Format

After vetting, produce this format:

```
╔══════════════════════════════════════════════════════════╗
║              🛡️ 360Guard Security Review Report           ║
╠══════════════════════════════════════════════════════════╣
║ Skill Name: [name]                                        ║
║ Source: [ClawHub / GitHub / other]                        ║
║ Author: [username]                                         ║
║ Version: [version]                                         ║
╠══════════════════════════════════════════════════════════╣
║ 📊 Scan Statistics                                        ║
║   • File count: [count]                                    ║
║   • Lines of code: [count]                                 ║
║   • Dependencies: [count]                                  ║
╠══════════════════════════════════════════════════════════╣
║ 🚨 Issues Found                                           ║
║   🔴 Critical: [count]                                     ║
║   ⚠️  High: [count]                                        ║
║   🟡 Medium: [count]                                       ║
╠══════════════════════════════════════════════════════════╣
║ 📋 Detailed Issue List                                    ║
║   [List each issue with file location, type, risk level]  ║
╠══════════════════════════════════════════════════════════╣
║ 💾 Permissions Required                                    ║
║   • File read: [list or "None"]                            ║
║   • File write: [list or "None"]                           ║
║   • Network: [list or "None"]                              ║
║   • Commands: [list or "None"]                             ║
╠══════════════════════════════════════════════════════════╣
║ 🎯 Risk Level: [🟢 LOW / 🟡 MEDIUM / 🔴 HIGH / ⛔ EXTREME] ║
╠══════════════════════════════════════════════════════════╣
║ ⚖️  Final Verdict                                          ║
║   [✅ Safe to install / ⚠️ Install with caution / ❌ Do not install] ║
╠══════════════════════════════════════════════════════════╣
║ 📝 Notes                                                  ║
║   [Any other observations and recommendations]            ║
╚══════════════════════════════════════════════════════════╝
```

---

## 8. Quick Commands

### Vet ClawHub Skill

```bash
# Method 1: Download and scan
wget -O skill.zip "https://clawhub.ai/api/download/SKILL_NAME"
unzip skill.zip
node ~/.npm-global/lib/node_modules/openclaw/skills/360guard/scripts/scanner.cjs ./SKILL_NAME
rm -rf skill.zip SKILL_NAME

# Method 2: GitHub repo scan
curl -s "https://api.github.com/repos/OWNER/REPO" | jq '{stars: .stargazers_count, updated: .updated_at}'
git clone https://github.com/OWNER/REPO
node ~/.npm-global/lib/node_modules/openclaw/skills/360guard/scripts/scanner.cjs ./REPO
```

### Quick Vet Commands

```bash
# Check repo stats
curl -s "https://api.github.com/repos/OWNER/REPO" | jq '{stars, forks, updated, language}'

# List all files
curl -s "https://api.github.com/repos/OWNER/REPO/contents/" | jq '.[].name'

# Get SKILL.md
curl -s "https://raw.githubusercontent.com/OWNER/REPO/main/SKILL.md"
```

---

## 9. Remember

- ❌ No Skill is worth compromising security
- ❓ When in doubt, don't install
- 🧑‍🦰 High-risk decisions: ask your human
- 📝 Document your vetting for future reference
- 🔄 Periodically re-vet installed Skills

---

> 🛡️ **360Guard** — 360-degree security for your Agent
