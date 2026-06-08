# 360Guard vs Skill Vetter Comparison Report

> 360Guard is built on top of Skill Vetter, enhanced version

---

## 📊 Overall Comparison

| Dimension | Skill Vetter | 360Guard |
|-----------|--------------|----------|
| **Check Items** | ~15 items | ~50+ items |
| **Risk Levels** | 4 levels | 4 levels + detailed subcategories |
| **Automated Scripts** | None | 3 (Quick/Full/Node.js) |
| **Output Reports** | Manual template | Auto-generated + multiple formats |
| **Supply Chain Checks** | None | Yes |
| **Social Engineering Checks** | None | Yes |

---

## ✅ New Check Items (compared to Vetter)

### 1. Persistence & Auto-start 🔴
- [x] Creates cron job / systemd service
- [x] Modifies ~/.ssh/authorized_keys
- [x] Writes to /etc/hosts
- [x] Adds Login Items / Startup Items
- [x] Modifies .bashrc / .zshrc / profile
- [x] Registers LaunchAgent (macOS)
- [x] Installs systemd user service

### 2. Monitoring & Eavesdropping 🔴
- [x] Screen capture/recording permission
- [x] Audio recording permission
- [x] Keyloggers
- [x] Accesses microphone/camera
- [x] File system monitoring (fswatch/inotify)

### 3. Data & Privacy 🔴
- [x] Reads clipboard
- [x] Reads environment variables (API_/SECRET/TOKEN prefix)
- [x] Accesses browser history/bookmarks
- [x] Accesses macOS Keychain
- [x] Accesses iMessage/SMS
- [x] Accesses contacts/calendar
- [x] Accesses photo library

### 4. Network & Communication 🔴
- [x] Initiates reverse shell
- [x] Uses Tor proxy
- [x] DNS queries to suspicious domains
- [x] WebSocket long connections
- [x] IRC connections
- [x] Non-standard ports
- [x] Hardcoded IP addresses

### 5. Code Execution (Advanced) 🔴
- [x] Dynamic import (importlib.import_module)
- [x] __import__() dynamic loading
- [x] compile() dynamic compilation
- [x] xmlrpc / jsonrpc remote calls
- [x] pickle / yaml / marshal deserialization
- [x] exec() / eval() any string
- [x] subprocess shell=True

### 6. File System 🟡
- [x] Writes to executable paths outside /tmp
- [x] Modifies /usr/local/bin
- [x] Writes .dmg/.pkg installers
- [x] Creates .hidden files/directories
- [x] File permission modification (chmod +x)
- [x] Symbolic links (pointing external)
- [x] Contains binary files

### 7. Dependencies & Supply Chain 🟡
- [x] Dependency version range too wide
- [x] Dependencies from private/unknown sources
- [x] Dependencies on deprecated packages
- [x] Silent additional dependency downloads
- [x] References other unvetted Skills
- [x] Uses git submodule

### 8. Social Engineering 🟡
- [x] Mimics popular Skill names
- [x] README overpromises
- [x] No source code, only compiled binaries
- [x] Author has no history
- [x] Downloads vs stars ratio suspicious

---

## 🛠️ New Automated Features

### 1. Quick Scan (quick-scan.sh)
- Scan dangerous functions
- Scan sensitive paths
- Scan dangerous commands
- Scan persistence mechanisms

### 2. Full Scan (full-scan.sh)
- File structure analysis
- Dangerous function scan
- Sensitive path scan
- Network request scan
- Persistence check
- Dependency check
- Binary file check
- Symbolic link check

### 3. Node.js Scanner (scanner.cjs)
- Multi-language support (JS/TS/Python/Bash)
- Risk level output
- Code line number location
- Code snippet extraction
- Process exit codes (0=safe, 1=critical, 2=high)

---

## 📈 Benefits & Value

### 1. More Comprehensive Coverage
- Vetter has basic checks, 360Guard adds 3x more check items
- Covers advanced attack vectors like persistence, privacy, supply chain

### 2. Higher Automation
- Vetter is manual-only, 360Guard provides 3 automated tools
- Can be integrated into CI/CD or cron jobs

### 3. More Actionable
- 360Guard outputs structured reports for direct decision-making
- Clear exit codes for script integration

### 4. Continuously Evolving
- Modular design, easy to add new check items
- Reserved extension interface

---

## 📋 Output Report Comparison

### Skill Vetter Output
```
SKILL VETTING REPORT
══════════════════════════════════════
RED FLAGS: [None / List them]
RISK LEVEL: [🟢 LOW / 🟡 MEDIUM / 🔴 HIGH / ⛔ EXTREME]
VERDICT: [✅ SAFE / ⚠️ CAUTION / ❌ DO NOT INSTALL]
```

### 360Guard Output
```
🛡️ 360Guard Security Scan Report
══════════════════════════════════════
🔴 CRITICAL risk (X items):
  • eval() execution - file.js:42
  • Reverse shell - script.sh:15

⚠️ HIGH risk (X items):
  • curl request - api.js:10
  ...

📄 Report saved: 360guard-report-20260313.txt

🔴 Conclusion: Critical risks found, not recommended to install
```

---

## 🎯 Use Cases

| Scenario | Recommended Use |
|----------|-----------------|
| Quick check (< 1 min) | quick-scan.sh |
| Full review (5-10 min) | full-scan.sh |
| Integrated into automation | scanner.cjs |
| Manual review guide | SKILL.md checklist |

---

## 📝 Usage Examples

```bash
# Quick scan
bash ~/.npm-global/lib/node_modules/openclaw/skills/360guard/scripts/quick-scan.sh /path/to/skill

# Full scan
bash ~/.npm-global/lib/node_modules/openclaw/skills/360guard/scripts/full-scan.sh /path/to/skill

# Node.js scan
node ~/.npm-global/lib/node_modules/openclaw/skills/360guard/scripts/scanner.cjs /path/to/skill

# Scan and auto-judge
node ~/.npm-global/lib/node_modules/openclaw/skills/360guard/scripts/scanner.cjs /path/to/skill
echo $?  # 0=safe, 1=critical, 2=high
```

---

## 🔄 Version History

- **v1.0.0** (2026-03-13): Initial version
  - Built on Skill Vetter
  - Added 35+ check items
  - Added 3 automated scripts
  - Added detailed report output

---

> 🛡️ 360Guard — 360-degree security for your Agent
