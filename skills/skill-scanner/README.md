# Skill Scanner

Security audit tool for Clawdbot/MCP skills - scans for malware, spyware, crypto-mining, and malicious patterns.

## Features

- Detects **data exfiltration** patterns (env scraping, credential access, HTTP POST to unknown domains)
- Identifies **system modification** attempts (dangerous rm, crontab changes, systemd persistence)
- Catches **crypto-mining** indicators (xmrig, mining pools, wallet addresses)
- Flags **arbitrary code execution** risks (eval, exec, download-and-execute)
- Detects **backdoors** (reverse shells, socket servers)
- Finds **obfuscation** techniques (base64 decode + exec)
- Outputs **Markdown** or **JSON** reports
- Returns exit codes for CI/CD integration

## Installation

```bash
# Clone the repo
git clone https://github.com/bvinci1-design/skill-scanner.git
cd skill-scanner

# No dependencies required - uses Python standard library only
# Requires Python 3.7+
```

---

## How to Run in Clawdbot

Clawdbot users can run this scanner directly as a skill to audit other downloaded skills.

### Quick Start (Clawdbot)

1. **Download the scanner** from this repo to your Clawdbot skills folder:
   ```bash
   cd ~/.clawdbot/skills
   git clone https://github.com/bvinci1-design/skill-scanner.git
   ```

2. **Scan any skill** by telling Clawdbot:
   ```
   "Scan the [skill-name] skill for security issues using skill-scanner"
   ```
   
   Or run directly:
   ```bash
   python ~/.clawdbot/skills/skill-scanner/skill_scanner.py ~/.clawdbot/skills/[skill-name]
   ```

3. **Review the output** - Clawdbot will display:
   - Verdict: APPROVED, CAUTION, or REJECT
   - Any security findings with severity levels
   - Specific file and line numbers for concerns

### Example Clawdbot Commands

```
"Use skill-scanner to check the youtube-watcher skill"
"Scan all my downloaded skills for malware"
"Run a security audit on the remotion skill"
```

### Interpreting Results in Clawdbot

| Verdict | Meaning | Action |
|---------|---------|--------|
| APPROVED | No security issues found | Safe to use |
| CAUTION | Minor concerns detected | Review findings before use |
| REJECT | Critical security issues | Do not use without careful review |

---

## How to Run on Any Device

The scanner works on any system with Python 3.7+ installed.

### Prerequisites

- Python 3.7 or higher
- Git (for cloning) or download ZIP from GitHub
- No additional packages required (uses Python standard library)

### Installation Options

**Option 1: Clone with Git**
```bash
git clone https://github.com/bvinci1-design/skill-scanner.git
cd skill-scanner
```

**Option 2: Download ZIP**
1. Click "Code" button on GitHub
2. Select "Download ZIP"
3. Extract to desired location

### Command Line Usage

**Basic scan:**
```bash
python skill_scanner.py /path/to/skill-folder
```

**Output to file:**
```bash
python skill_scanner.py /path/to/skill-folder --output report.md
```

**JSON output:**
```bash
python skill_scanner.py /path/to/skill-folder --json
```

**Scan current directory:**
```bash
python skill_scanner.py .
```

### Web UI (Streamlit)

For a user-friendly graphical interface:

1. **Install Streamlit:**
   ```bash
   pip install streamlit
   ```

2. **Run the UI:**
   ```bash
   streamlit run streamlit_ui.py
   ```

3. **Open in browser** at `http://localhost:8501`

4. **Features:**
   - Drag-and-drop file upload
   - Support for ZIP archives
   - Paste code directly for scanning
   - Visual severity indicators
   - Export reports in Markdown or JSON

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Approved - no issues |
| 1 | Caution - high-severity issues |
| 2 | Reject - critical issues |

## Threat Patterns Detected

### Critical (auto-reject)
- Credential path access (~/.ssh, ~/.aws, /etc/passwd)
- Dangerous recursive delete (rm -rf /)
- Systemd/launchd persistence
- Crypto miners (xmrig, ethminer, stratum+tcp)
- Download and execute (curl | sh)
- Reverse shells (/dev/tcp, nc -e)
- Base64 decode + exec obfuscation

### High (caution)
- Bulk environment variable access
- Crontab modification
- eval/exec dynamic code execution
- Socket servers

### Medium (informational)
- Environment variable reads
- HTTP POST to external endpoints

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Scan skill for security issues
  run: |
    python skill_scanner.py ./my-skill --output scan-report.md
    if [ $? -eq 2 ]; then
      echo "CRITICAL issues found - blocking merge"
      exit 1
    fi
```

## Contributing

Pull requests welcome! To add new threat patterns, edit the `THREAT_PATTERNS` list in `skill_scanner.py`.

## License

MIT License - see LICENSE file for details.
