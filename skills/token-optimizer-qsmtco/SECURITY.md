# Security Documentation

This document provides detailed security analysis of the OpenClaw Token Optimizer skill.

## Purpose

This skill helps reduce OpenClaw API costs by optimizing context loading and model selection. Core operations are local and do not require network access. An optional pricing refresh feature (`token_tracker.py refresh-pricing`) contacts the OpenRouter API to obtain current model pricing; this is only executed when explicitly invoked by the user.

## False Positive Explanation

**Why some antivirus tools flag this skill:**

1. **"Optimizer" keyword** - AV heuristics often flag tools with "optimizer" in the name, especially when combined with file operations
2. **Generated configuration** - The skill generates AGENTS.md and HEARTBEAT.md templates containing configuration commands, which can trigger heuristics
3. **Executable Python scripts** - Scripts with `#!/usr/bin/env python3` shebang are sometimes flagged as potentially malicious
4. **File state tracking** - Writing JSON files to track usage patterns can trigger "data collection" heuristics

**These are all false positives.** The skill contains no malicious code.

## Script-by-Script Security Analysis

### 1. context_optimizer.py

**Purpose**: Analyze prompts to determine minimal context requirements

**Operations**:
- Reads JSON state file from `~/.openclaw/workspace/memory/context-usage.json`
- Classifies prompt complexity (simple/medium/complex)
- Recommends which files to load
- Generates optimized AGENTS.md template
- Writes usage statistics to JSON

**Security**:
- ✅ No network requests
- ✅ No code execution (no eval, exec, compile)
- ✅ Only standard library imports: `json, re, pathlib, datetime`
- ✅ Read/write permissions limited to OpenClaw workspace
- ✅ No subprocess calls
- ✅ No system modifications

**Data Handling**:
- Stores: File access counts, last access timestamps
- Location: `~/.openclaw/workspace/memory/context-usage.json`
- Privacy: All data local, never transmitted

### 2. heartbeat_optimizer.py

**Purpose**: Optimize heartbeat check scheduling to reduce unnecessary API calls

**Operations**:
- Reads heartbeat state from `~/.openclaw/workspace/memory/heartbeat-state.json`
- Determines which checks are due based on intervals
- Records when checks were last performed
- Enforces quiet hours (23:00-08:00)

**Security**:
- ✅ No network requests
- ✅ No code execution
- ✅ Only standard library imports: `json, os, datetime, pathlib`
- ✅ Read/write limited to heartbeat state file
- ✅ No system commands

**Data Handling**:
- Stores: Last check timestamps, check intervals
- Location: `~/.openclaw/workspace/memory/heartbeat-state.json`
- Privacy: All local, no telemetry

### 3. model_router.py

**Purpose**: Suggest appropriate model based on task complexity to reduce costs

**Operations**:
- Analyzes prompt text
- Classifies task complexity
- Recommends cheapest appropriate model
- No state file (pure analysis)

**Security**:
- ✅ No network requests
- ✅ No code execution
- ✅ Only standard library imports: `json, re`
- ✅ No file writes
- ✅ Stateless operation

**Data Handling**:
- No data storage
- No external communication
- Pure text analysis

### 4. token_tracker.py

**Purpose**: Monitor token usage and enforce budgets; maintain dynamic pricing cache.

**Operations**:
- Reads/writes state from `~/.openclaw/workspace/memory/token-tracker-state.json`
- Loads model prices from `~/.openclaw/workspace/skills/openclaw-token-optimizer/pricing.json`
- `refresh-pricing` command contacts OpenRouter API to fetch current pricing and updates the cache
- Provides `check`, `suggest`, `pricing`, `reset` commands

**Security**:
- ✅ Normal operation (check, suggest, pricing, reset) involves no network requests
- ⚠️ `refresh-pricing` uses OpenRouter API (user-initiated, requires `OPENROUTER_API_KEY`)
- ✅ No code execution (no eval, exec)
- ✅ Only standard library imports (`json`, `os`, `datetime`, `pathlib`, `urllib`)
- ✅ Read/write limited to workspace files
- ✅ No system command execution

**Data Handling**:
- State: daily usage, reset timestamps, alert history → `token-tracker-state.json`
- Pricing cache: mapping of model IDs to per-1M-token cost → `pricing.json`
- Privacy: All data local; pricing refresh only requests public model list from OpenRouter; no personal data transmitted.

**Authentication**:
- Reads `OPENROUTER_API_KEY` from environment, or from `~/.openclaw/agents/main/agent/auth-profiles.json` if present. No hardcoded keys.

## Assets & References

### Assets (Templates & Config)

- `HEARTBEAT.template.md` - Markdown template for optimized heartbeat workflow
- `config-patches.json` - Suggested OpenClaw config optimizations
- `cronjob-model-guide.md` - Documentation for cron-based model routing

**Security**: Plain text/JSON files, no code execution

### References (Documentation)

- `PROVIDERS.md` - Multi-provider strategy documentation

**Security**: Plain text markdown, informational only

## Verification

### Check File Integrity

```bash
cd ~/.openclaw/skills/token-optimizer
sha256sum -c .clawhubsafe
```

### Audit Code Yourself

```bash
# Search for dangerous functions (should return nothing)
grep -r "eval(\|exec(\|__import__\|compile(\|subprocess\|os.system" scripts/

# Search for network operations (urllib only in token_tracker for refresh-pricing)
grep -r "urllib\|requests\|http\|socket\|download\|fetch" scripts/

# Search for system modifications (should return nothing)  
grep -r "rm -rf\|sudo\|chmod 777\|chown" .
```

### Review Imports

All scripts use only Python standard library:
- `json` - JSON parsing
- `re` - Regular expressions for text analysis
- `pathlib` - File path handling
- `datetime` - Timestamp management
- `os` - Environment variables and path operations
- `urllib` — Used **only** in `token_tracker.py` for the user-initiated `refresh-pricing` command

No third-party libraries. Network access is explicit and limited to OpenRouter API when refreshing prices.

## Data Privacy

**What data is stored:**
- File access patterns (which files loaded when)
- Heartbeat check timestamps
- Token usage totals (daily aggregates)
- Budget configurations
- Model pricing cache (model ID → cost per 1M tokens)

**Where data is stored:**
- `~/.openclaw/workspace/memory/` (context-usage.json, heartbeat-state.json, token-tracker-state.json)
- `~/.openclaw/workspace/skills/openclaw-token-optimizer/` (pricing.json)

**What is NOT collected:**
- Prompt content
- User messages
- API keys (keys are read from environment or OpenClaw config but not stored by this skill)
- Personal information
- System information beyond basic usage tracking

**External communication:**
- By default, **zero** network requests.
- The `refresh-pricing` command contacts OpenRouter API (`https://openrouter.ai/api/v1/models`) to fetch current model pricing. This is user-initiated and only transmits the API key, no personal or workspace data.
- No telemetry, analytics, or phone-home behavior.

## Threat Model

**What this skill CAN do:**
- Read/write JSON files in OpenClaw workspace
- Analyze text for complexity classification
- Generate markdown templates
- Provide recommendations via stdout
- Optionally, when explicitly invoked: contact OpenRouter API to fetch model pricing

**What this skill CANNOT do:**
- Execute arbitrary code
- Make unsolicited network requests
- Modify system files outside workspace
- Access sensitive data (prompts, messages, API keys)
- Run system commands
- Spawn subprocesses

**Risk Level**: Minimal
- Operates entirely within OpenClaw sandbox
- No privileged operations
- No external dependencies other than optional user-provided API key
- Auditable source code

## License & Attribution

- **License**: Apache 2.0
- **Author**: Asif2BD
- **Repository**: https://github.com/Asif2BD/openclaw-token-optimizer (if published)
- **ClawHub**: https://clawhub.ai/Asif2BD/openclaw-token-optimizer

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT open a public issue**
2. Contact: [via ClawHub or GitHub]
3. Include: Affected files, severity, reproduction steps

## Changelog

- **2026-02-12**: Added comprehensive security documentation
- **2026-02-07**: Initial release (v1.2.0)

## VirusTotal Status

**Current Status**: False positive by heuristic analysis

**Detection Reason**: Generic heuristics flagging "optimizer" keyword + file operations

**Actual Threat**: None

**Recommended Action**: Whitelist this skill or review source code yourself

---

**Bottom Line**: This skill is safe. It's a productivity tool that helps reduce API costs through intelligent context loading and model selection. All code is auditable, uses only standard Python libraries, and performs no dangerous operations.
