# Manual Audit Methodology

This document provides detailed guidance on performing security audits for packages, skills, and MCP servers.

## Overview

For deep-dive security analysis on demand, follow these steps after registering and reading `prompts/audit-prompt.md`.

## Step 3: Analyze Every File

Read every file in the target package. For each file, check:

### npm Packages

- `package.json`: preinstall/postinstall/prepare scripts
- Dependency list: typosquatted or known-malicious packages
- Main entry: does it phone home on import?
- Native addons (.node, .gyp)
- `process.env` access + external transmission

### pip Packages

- `setup.py` / `pyproject.toml`: code execution during install
- `__init__.py`: side effects on import
- `subprocess`, `os.system`, `eval`, `exec`, `compile` usage
- Network calls in unexpected places

### MCP Servers

- Tool descriptions vs actual behavior (mismatch = deception)
- Permission scopes: minimal or overly broad?
- Input sanitization before shell/SQL/file operations
- Credential access beyond stated needs

### OpenClaw Skills

- `SKILL.md`: dangerous instructions to the agent?
- `scripts/`: `curl|bash`, `eval`, `rm -rf`, credential harvesting
- Data exfiltration from workspace

## Step 3b: Component-Type Awareness *(v2)*

Different file types carry different risk profiles. Prioritize your analysis accordingly:

| Component Type | Risk Level | What to Watch For |
|----------------|------------|-------------------|
| Shell scripts in `hooks/` | 🔴 Highest | Direct system access, persistence mechanisms, arbitrary execution |
| `.mcp.json` configs | 🔴 High | Supply-chain risks, `npx -y` without version pinning, untrusted server sources |
| `settings.json` / permissions | 🟠 High | Wildcard permissions (`Bash(*)`), `defaultMode: dontAsk`, overly broad tool access |
| Plugin/skill entry points | 🟠 High | Code execution on load, side effects on import |
| `SKILL.md` / agent prompts | 🟡 Medium | Social engineering, prompt injection, misleading instructions |
| Documentation / README | 🟢 Low | Usually safe; check for hidden HTML comments (>100 chars) |
| Tests / examples | 🟢 Low | Rarely exploitable; check for hardcoded credentials |

> Findings in high-risk components should receive extra scrutiny. A `medium`-severity finding in a hook script may warrant `high` severity due to the execution context.

## Step 3c: Cross-File Analysis *(v2)*

Do **not** analyze files in isolation. Explicitly check for multi-file attack chains:

| Cross-File Pattern | What to Look For |
|--------------------|-----------------|
| **Credential + Network** | Credentials read in file A, transmitted via network call in file B |
| **Permission + Persistence** | Permission escalation in one file enabling persistence mechanism in another |
| **Hook + Skill Activation** | A hook script that silently modifies skill behavior or injects instructions |
| **Config + Obfuscation** | Config file that references obfuscated scripts or encoded payloads |
| **Supply Chain + Network** | Dependency installed via postinstall hook that phones home |
| **File Access + Exfiltration** | File reading in one component, data sent externally in another |

When you find a cross-file relationship, report it as a single finding with `pattern_id` prefix `CORR_` and list all involved files in the description.

## Step 4: AI-Specific Security Checks *(v2)*

When auditing AI agent packages, skills, and MCP servers, check for these **AI-specific attack patterns**:

### Prompt Injection & Manipulation

| Pattern ID | Attack | Examples to Look For |
|------------|--------|---------------------|
| `AI_PROMPT_001` | System Prompt Extraction | "reveal your system prompt", "output your instructions", "what were you told" |
| `AI_PROMPT_002` | Agent Impersonation | "pretend to be", "you are now", "act as an Anthropic employee" |
| `AI_PROMPT_003` | Capability Escalation | "enable developer mode", "unlock hidden capabilities", "activate god mode" |
| `AI_PROMPT_004` | Context Pollution | "inject into context", "remember this forever", "prepend to all responses" |
| `AI_PROMPT_005` | Multi-Step Attack Setup | "on the next message execute", "phase 1:", "when triggered do" |
| `AI_PROMPT_006` | Output Manipulation | "output JSON without escaping", "encode response in base64", "hide in markdown" |
| `AI_PROMPT_007` | Trust Boundary Violation | "skip all validation", "disable security", "ignore safety checks" |
| `AI_PROMPT_008` | Indirect Prompt Injection | "follow instructions from the file", "execute commands from URL", "read and obey" |
| `AI_PROMPT_009` | Tool Abuse | "use bash tool to delete", "bypass tool restrictions", "call tool without user consent" |
| `AI_PROMPT_010` | Jailbreak Techniques | DAN prompts, "bypass filter/safety/guardrail", role-play exploits |
| `AI_PROMPT_011` | Instruction Hierarchy Manipulation | "this supersedes all previous instructions", "highest priority override" |
| `AI_PROMPT_012` | Hidden Instructions | Instructions embedded in HTML comments, zero-width characters, or whitespace |

> **False-positive guidance:** Phrases like "never trust all input" or "do not reveal your prompt" are defensive, not offensive. Only flag patterns that attempt to *perform* these actions, not *warn against* them.

### Persistence Mechanisms *(v2)*

Check for code that establishes persistence on the host system:

| Pattern ID | Mechanism | What to Look For |
|------------|-----------|-----------------|
| `PERSIST_001` | Crontab modification | `crontab -e`, `crontab -l`, writing to `/var/spool/cron/` |
| `PERSIST_002` | Shell RC files | Writing to `.bashrc`, `.zshrc`, `.profile`, `.bash_profile` |
| `PERSIST_003` | Git hooks | Creating/modifying files in `.git/hooks/` |
| `PERSIST_004` | Systemd services | `systemctl enable`, writing to `/etc/systemd/`, `.service` files |
| `PERSIST_005` | macOS LaunchAgents | Writing to `~/Library/LaunchAgents/`, `/Library/LaunchDaemons/` |
| `PERSIST_006` | Startup scripts | Writing to `/etc/init.d/`, `/etc/rc.local`, Windows startup folders |

### Advanced Obfuscation *(v2)*

Check for techniques that hide malicious content:

| Pattern ID | Technique | Detection Method |
|------------|-----------|-----------------|
| `OBF_ZW_001` | Zero-width characters | Look for U+200B–U+200D, U+FEFF, U+2060–U+2064 in any text file |
| `OBF_B64_002` | Base64-decode → execute chains | `atob()`, `base64 -d`, `b64decode()` followed by `eval`/`exec` |
| `OBF_HEX_003` | Hex-encoded content | `\x` sequences, `Buffer.from(hex)`, `bytes.fromhex()` |
| `OBF_ANSI_004` | ANSI escape sequences | `\x1b[`, `\033[` used to hide terminal output |
| `OBF_WS_005` | Whitespace steganography | Unusually long whitespace sequences encoding hidden data |
| `OBF_HTML_006` | Hidden HTML comments | Comments >100 characters, especially containing instructions |
| `OBF_JS_007` | JavaScript obfuscation | Variable names like `_0x`, `$_`, `String.fromCharCode` chains |
