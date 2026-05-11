---
name: skill-scanner
description: Scan Clawdbot and MCP skills for malware, spyware, crypto-miners, and malicious code patterns before you install them. Security audit tool that detects data exfiltration, system modification attempts, backdoors, and obfuscation techniques.
---

# Skill Scanner

Security audit tool for Clawdbot/MCP skills - scans for malware, spyware, crypto-mining, and malicious patterns.

## Capabilities
- Scan skill folders for security threats
- Detect data exfiltration patterns
- Identify system modification attempts
- Catch crypto-mining indicators
- Flag arbitrary code execution risks
- Find backdoors and obfuscation techniques
- Output reports in Markdown or JSON format
- Provide Web UI via Streamlit

## Usage

### Command Line
```bash
python skill_scanner.py /path/to/skill-folder
```

### Within Clawdbot
```
"Scan the [skill-name] skill for security issues using skill-scanner"
"Use skill-scanner to check the youtube-watcher skill"
"Run a security audit on the remotion skill"
```

### Web UI
```bash
pip install streamlit
streamlit run streamlit_ui.py
```

## Requirements
- Python 3.7+
- No additional dependencies (uses Python standard library)
- Streamlit (optional, for Web UI)

## Entry Point
- **CLI:** `skill_scanner.py`
- **Web UI:** `streamlit_ui.py`

## Tags
#security #malware #spyware #crypto-mining #scanner #audit #code-analysis #mcp #clawdbot #agent-skills #safety #threat-detection #vulnerability
