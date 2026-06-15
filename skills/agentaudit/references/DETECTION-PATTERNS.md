# Detection Patterns Reference

This document lists all detection patterns used in AgentAudit security analysis.

## Pattern ID Prefixes

| Prefix | Category |
|--------|----------|
| `AI_PROMPT` | AI-specific attacks: prompt injection, jailbreak, capability escalation *(v2)* |
| `CMD_INJECT` | Command/shell injection |
| `CORR` | Cross-file correlation findings *(v2)* |
| `CRED_THEFT` | Credential stealing |
| `CRYPTO_WEAK` | Weak cryptography |
| `DATA_EXFIL` | Data exfiltration |
| `DESER` | Unsafe deserialization |
| `DESTRUCT` | Destructive operations |
| `INFO_LEAK` | Information leakage |
| `MANUAL` | Manual finding (no pattern match) |
| `OBF` | Code obfuscation (incl. zero-width, ANSI, steganography) *(expanded v2)* |
| `PATH_TRAV` | Path traversal |
| `PERSIST` | Persistence mechanisms: crontab, RC files, git hooks, systemd *(v2)* |
| `PRIV_ESC` | Privilege escalation |
| `SANDBOX_ESC` | Sandbox escape |
| `SEC_BYPASS` | Security bypass |
| `SOCIAL_ENG` | Social engineering (non-AI-specific prompt manipulation) |
| `SUPPLY_CHAIN` | Supply chain attack |

## AI-Specific Patterns (v2)

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

## Persistence Patterns (v2)

| Pattern ID | Mechanism | What to Look For |
|------------|-----------|-----------------|
| `PERSIST_001` | Crontab modification | `crontab -e`, `crontab -l`, writing to `/var/spool/cron/` |
| `PERSIST_002` | Shell RC files | Writing to `.bashrc`, `.zshrc`, `.profile`, `.bash_profile` |
| `PERSIST_003` | Git hooks | Creating/modifying files in `.git/hooks/` |
| `PERSIST_004` | Systemd services | `systemctl enable`, writing to `/etc/systemd/`, `.service` files |
| `PERSIST_005` | macOS LaunchAgents | Writing to `~/Library/LaunchAgents/`, `/Library/LaunchDaemons/` |
| `PERSIST_006` | Startup scripts | Writing to `/etc/init.d/`, `/etc/rc.local`, Windows startup folders |

## Obfuscation Patterns (v2)

| Pattern ID | Technique | Detection Method |
|------------|-----------|-----------------|
| `OBF_ZW_001` | Zero-width characters | Look for U+200B–U+200D, U+FEFF, U+2060–U+2064 in any text file |
| `OBF_B64_002` | Base64-decode → execute chains | `atob()`, `base64 -d`, `b64decode()` followed by `eval`/`exec` |
| `OBF_HEX_003` | Hex-encoded content | `\x` sequences, `Buffer.from(hex)`, `bytes.fromhex()` |
| `OBF_ANSI_004` | ANSI escape sequences | `\x1b[`, `\033[` used to hide terminal output |
| `OBF_WS_005` | Whitespace steganography | Unusually long whitespace sequences encoding hidden data |
| `OBF_HTML_006` | Hidden HTML comments | Comments >100 characters, especially containing instructions |
| `OBF_JS_007` | JavaScript obfuscation | Variable names like `_0x`, `$_`, `String.fromCharCode` chains |

## Cross-File Correlation Patterns (v2)

When you find a cross-file relationship, report it as a single finding with `pattern_id` prefix `CORR_` and list all involved files in the description.

| Cross-File Pattern | What to Look For |
|--------------------|-----------------|
| **Credential + Network** | Credentials read in file A, transmitted via network call in file B |
| **Permission + Persistence** | Permission escalation in one file enabling persistence mechanism in another |
| **Hook + Skill Activation** | A hook script that silently modifies skill behavior or injects instructions |
| **Config + Obfuscation** | Config file that references obfuscated scripts or encoded payloads |
| **Supply Chain + Network** | Dependency installed via postinstall hook that phones home |
| **File Access + Exfiltration** | File reading in one component, data sent externally in another |

## Component Types (v2)

Component type classification affects score weighting:

| Component Type | Risk Level | What to Watch For |
|----------------|------------|-------------------|
| Shell scripts in `hooks/` | 🔴 Highest | Direct system access, persistence mechanisms, arbitrary execution |
| `.mcp.json` configs | 🔴 High | Supply-chain risks, `npx -y` without version pinning, untrusted server sources |
| `settings.json` / permissions | 🟠 High | Wildcard permissions (`Bash(*)`), `defaultMode: dontAsk`, overly broad tool access |
| Plugin/skill entry points | 🟠 High | Code execution on load, side effects on import |
| `SKILL.md` / agent prompts | 🟡 Medium | Social engineering, prompt injection, misleading instructions |
| Documentation / README | 🟢 Low | Usually safe; check for hidden HTML comments (>100 chars) |
| Tests / examples | 🟢 Low | Rarely exploitable; check for hardcoded credentials |
