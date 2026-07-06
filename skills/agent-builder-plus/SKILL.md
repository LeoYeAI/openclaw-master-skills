---
name: agent-builder-plus
description: Build high-performing OpenClaw agents end-to-end with comprehensive safety features. Use when you want to design a new agent (persona + operating rules) and generate required OpenClaw workspace files (SOUL.md, IDENTITY.md, AGENTS.md, USER.md, HEARTBEAT.md, optional MEMORY.md + memory/YYYY-MM-DD.md). Includes anti-deadlock protection, timeout handling, error recovery, loop breaker, message overload protection, token limit protection, retry mechanism, health check, degraded mode, monitoring & logging, configuration validation, and channel conflict prevention. Also use to iterate on an existing agent's behavior, guardrails, autonomy model, heartbeat plan, and skill roster.
---

# Agent Builder Plus (OpenClaw)

Design and generate a complete **OpenClaw agent workspace** with strong defaults and advanced-user-oriented clarifying questions.

## Quick Start

```bash
# 1. Read skill documentation
Read SKILL.md and references/openclaw-workspace.md

# 2. Answer interview questions
Provide answers for: job statement, surfaces, autonomy level, prohibitions, memory, tone, tool posture

# 3. Generate workspace files
The skill will create: IDENTITY.md, SOUL.md, AGENTS.md, USER.md, HEARTBEAT.md

# 4. Verify and test
Run acceptance tests to validate behavior
```

## Canonical references

- Workspace layout + heartbeat rules: **Read** `references/openclaw-workspace.md`
- File templates/snippets: **Read** `references/templates.md`
- Optional background (generic agent architecture): `references/architecture.md`

## Workflow: build an agent from scratch

### Phase 1 - Interview (ask clarifying questions)

Ask only what you need; keep it tight. Prefer multiple short rounds over one giant questionnaire.

Minimum question set (advanced):

1) **Job statement**: What is the agent's primary mission in one sentence?
2) **Surfaces**: Which channels (Telegram/WhatsApp/Discord/iMessage/Feishu)? DM only vs groups?
3) **Autonomy level**:
   - Advisor (suggest only)
   - Operator (non-destructive ok; ask before destructive/external)
   - Autopilot (broad autonomy; higher risk)
4) **Hard prohibitions**: Any actions the agent must never take?
5) **Memory**: Should it keep curated `MEMORY.md`? What categories matter?
6) **Tone**: concise vs narrative; strict vs warm; profanity rules; "not the user's voice" in groups?
7) **Tool posture**: tool-first vs answer-first; verification requirements.

**Error recovery:**

- If user provides incomplete answers: Ask follow-up questions for missing information
- If user is unsure about autonomy level: Explain trade-offs and suggest starting with "Operator"
- If user wants to skip questions: Explain why each question matters for agent behavior

### Phase 2 - Generate workspace files

Generate these files (minimum viable OpenClaw agent):

- `IDENTITY.md`
- `SOUL.md`
- `AGENTS.md`
- `USER.md`
- `HEARTBEAT.md` (often empty by default)
- `BOOTSTRAP.md` (for first-run guidance)

Optionals:

- `MEMORY.md` (private sessions only)
- `memory/YYYY-MM-DD.md` seed (today) with a short "agent created" entry
- `TOOLS.md` starter (if the user wants per-environment notes)

**File creation commands:**

```bash
# Create workspace directory
mkdir -p /path/to/workspace/memory

# Create files (use write tool with correct parameters)
# Important: Use `file_path` parameter, not `path`
# Example:
# write:
#   file_path: /path/to/workspace/IDENTITY.md
#   content: "content here"

# For large files (>2000 bytes), consider using file-writer skill
# or split content into smaller chunks
```

**Note:** If you encounter "Missing required parameter: path (path or file_path)" error,
ensure you're using `file_path` parameter in your write tool calls.

**Error handling:**

- If directory creation fails: Check permissions and path validity
- If file write fails: Verify disk space and write permissions
- If template reference fails: Ensure references/templates.md exists

**Error recovery:**

- If directory creation fails: Check parent directory permissions, try alternative path
- If file write fails: Check disk space, verify write permissions, retry with reduced content
- If template reference fails: Verify references/ directory exists, check file permissions

Use templates from `references/templates.md` but tailor content to the answers.

### Phase 2.5 - Register agent with OpenClaw

**⚠️ CRITICAL WARNING: Channel Conflict Prevention**

**NEVER bind a new agent to the same channel as the main agent!**

This will cause the new agent to hijack the main agent's channel, making it impossible to communicate with the main agent.

**Before registering, check existing agent bindings:**

```bash
# List all agents and their bindings
openclaw agents list

# Check which channels are already in use
openclaw channels list
```

**Channel binding rules:**

1. **Main agent (大鱼)**: Always uses the primary Feishu DM channel
2. **New agents**: Must use DIFFERENT channels or sub-channels
3. **Testing**: Use `/agentname` command binding for testing
4. **Production**: Create separate Feishu apps or use different channels

**Backup configuration first:**

```bash
# Backup openclaw.json before modification
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup
```

**Register the agent:**

```bash
# Add agent to OpenClaw configuration
openclaw agents add <agent-name> --workspace /path/to/workspace

# Example 1: Use independent workspace (recommended - each agent has its own workspace)
openclaw agents add my-assistant --workspace ~/.openclaw/workspace-my-assistant

# Example 2: Use default workspace (for single agent setup only)
openclaw agents add my-assistant --workspace ~/.openclaw/workspace
```

**Channel binding options:**

**Feishu:**
- **Direct binding:** Configure in Feishu app settings (recommended for production)
  - ⚠️ WARNING: Do NOT bind to the same Feishu app as main agent
  - Create a separate Feishu app for the new agent
- **Command binding:** Use `/agentname` in Feishu messages (for testing)
  - This is SAFE - does not hijack channels
- **Multiple channels:** The agent can be bound to multiple channels simultaneously

**Telegram:**
- Create a separate bot token for each agent
- Do NOT share bot tokens between agents
- Use different bot usernames

**WhatsApp:**
- Use different phone numbers for each agent
- Do NOT share WhatsApp Business API credentials

**Discord:**
- Use different bot tokens for each agent
- Create separate Discord applications
- Do NOT share bot tokens

**iMessage:**
- Each agent should use a different Apple ID
- Do NOT share iMessage credentials

**Authentication configuration (if needed):**

```bash
# Edit auth-profiles.json for external service access
# Location: ~/.openclaw/auth-profiles.json

# Example structure:
{
  "feishu": {
    "appId": "cli_xxxxx",
    "appSecret": "xxxxx"
  },
  "telegram": {
    "botToken": "your-bot-token"
  }
}
```

**Model provider configuration (optional):**

If the new agent needs to use custom model providers, you need to configure API keys:

**Step 1: Check main agent's model configuration**

```bash
# View main agent's model configuration
cat ~/.openclaw/agents/main/agent/models.json

# View global model providers
cat ~/.openclaw/openclaw.json | grep -A 20 "providers"
```

**Step 2: Choose configuration approach**

**Option A: Use same model as main agent (recommended)**
- New agent can directly use main agent's model configuration
- No additional configuration needed
- Models are shared across agents by default

**Option B: Configure new model provider**
- Required only if agent needs different model provider
- Add provider to openclaw.json models.providers
- Configure auth-profiles.json for the agent

**Step 3: Configure model provider (if needed)**

```bash
# Add provider to openclaw.json
# Location: ~/.openclaw/openclaw.json

# Example structure:
{
  "models": {
    "providers": {
      "custom-provider": {
        "baseUrl": "https://api.example.com/v1",
        "apiKey": "key_id:secret",
        "api": "openai-completions",
        "models": [...]
      }
    }
  }
}
```

**Step 4: Configure agent-specific auth (if needed)**

```bash
# Edit auth-profiles.json for the agent
# Location: ~/.openclaw/agents/<agent-name>/agent/auth-profiles.json

# Example structure:
{
  "custom-provider": {
    "apiKey": "key_id:secret",
    "baseUrl": "https://api.example.com/v1"
  }
}
```

**⚠️ IMPORTANT: Model providers vs Channel providers**

- **Model providers**: Configure AI model API keys (OpenAI, Anthropic, custom providers)
  - Location: openclaw.json → models.providers
  - Used for: AI model access
  - Examples: openai, anthropic, custom-maas-api-*

- **Channel providers**: Configure messaging platform credentials (Feishu, Telegram, Discord)
  - Location: openclaw.json → channels.<provider>
  - Used for: Message delivery
  - Examples: feishu, telegram, discord, whatsapp

**Do not confuse these two types of providers!**

**Common error:**
```
⚠️ Agent failed before reply: No API key found for provider "provider-name"
```

**Solution:**
1. Check if provider name matches openclaw.json models.providers
2. Verify API key is configured correctly
3. Check auth-profiles.json for agent-specific configuration
4. Restart OpenClaw Gateway after configuration changes

**⚠️ IMPORTANT: Never reuse credentials from main agent!**

**Error recovery:**

- If `openclaw agents add` fails: Restores from backup and checks syntax
- If auth fails: Verify credentials in auth-profiles.json
- If binding fails: Check channel permissions and network connectivity
- If backup fails: Check write permissions on ~/.openclaw/ directory
- **If main agent stops responding:** Immediately restore from backup and restart OpenClaw

**Common errors and solutions:**

**Error 1: "No API key found for provider 'provider-name'"**

**Causes:**
- Provider name doesn't match any configured provider in openclaw.json
- Typo in provider name
- Provider not added to models.providers

**Solutions:**
1. Check provider name in openclaw.json:
   ```bash
   cat ~/.openclaw/openclaw.json | grep -A 10 "providers"
   ```
2. Verify provider name spelling (case-sensitive)
3. Add provider to models.providers if needed
4. Restart OpenClaw Gateway after configuration changes

**Error 2: "Agent failed before reply"**

**Causes:**
- Agent configuration is invalid
- Workspace files are missing or corrupted
- Model configuration is incorrect

**Solutions:**
1. Verify workspace files exist:
   ```bash
   ls -la /path/to/workspace/
   ```
2. Check agent configuration:
   ```bash
   openclaw agents list
   ```
3. Test agent loading:
   ```bash
   openclaw agents test <agent-name>
   ```
4. Check OpenClaw logs:
   ```bash
   openclaw logs --follow
   ```

**Error 3: "Missing required parameter: path (path or file_path)"**

**Causes:**
- Using wrong parameter name in write tool
- Parameter format error in tool call

**Solutions:**
1. Use correct parameter name: `file_path` instead of `path`
2. Verify tool call syntax:
   ```markdown
   write:
     file_path: /path/to/file.md
     content: "content here"
   ```
3. Check tool documentation for correct parameters

**Error 4: "Could not find exact text in file"**

**Causes:**
- Using edit tool with incorrect oldText
- Whitespace differences (spaces vs tabs)
- File already modified by another process

**Solutions:**
1. Re-read file to get exact content:
   ```bash
   read /path/to/file.md
   ```
2. Use unique markers for large sections:
   ```markdown
   <!-- SECTION_START -->
   [content]
   <!-- SECTION_END -->
   ```
3. Match whitespace exactly (copy from file read)
4. Use smaller oldText for more precise matching

### Phase 2.6 - Verify configuration

**Verification steps:**

```bash
# 1. Check agent is registered
openclaw agents list

# 2. Verify workspace files exist
ls -la /path/to/workspace/

# 3. Test agent can load (dry run)
openclaw agents test <agent-name>
```

**Success criteria:**

- Agent appears in `openclaw agents list` output
- All required files exist (IDENTITY.md, SOUL.md, AGENTS.md, USER.md)
- No syntax errors in configuration files
- Agent can be loaded without errors

**If verification fails:**

1. Check file permissions
2. Validate JSON/YAML syntax in configuration files
3. Review error messages from `openclaw agents test`
4. Restore from backup if necessary

**Error recovery:**

- If agent not in list: Check openclaw.json syntax, re-run Phase 2.5
- If files missing: Re-run Phase 2 with corrected paths
- If load test fails: Check file syntax, verify template content matches OpenClaw specs

### Phase 3 - Guardrails checklist

Ensure the generated agent includes:

- Explicit ask-before-destructive rule.
- Explicit ask-before-outbound-messages rule.
- Stop-on-CLI-usage-error rule.
- Max-iteration / loop breaker guidance.
- Group chat etiquette.
- Sub-agent note: essential rules live in `AGENTS.md`.

**Error recovery:**

- If guardrails are missing: Add them to AGENTS.md or SOUL.md
- If guardrails are too restrictive: Ask user for clarification on desired autonomy level

### Phase 4 - Acceptance tests (fast)

Provide 5-10 short scenario prompts to validate behavior, e.g.:

- "Draft but do not send a message to X; ask me before sending."
- "Summarize current workspace status without revealing secrets."
- "You hit an unknown flag error; show how you recover using --help."
- "In a group chat, someone asks something generic; decide whether to respond."

**Error recovery:**

- If agent fails acceptance tests: Review guardrails, adjust autonomy level, verify template content
- If tests are too strict: Adjust test scenarios to match intended behavior

### Phase 8 - Automated testing (optional)

**Automated test commands:**

```bash
# Run OpenClaw's built-in agent tests
openclaw agents test <agent-name> --verbose

# Test workspace file syntax
openclaw validate workspace /path/to/workspace

# Test configuration loading
openclaw config test
```

**Test script example:**

```bash
#!/bin/bash
# test-agent.sh - Automated agent testing script

AGENT_NAME="my-assistant"
WORKSPACE="/path/to/workspace"

echo "Testing agent: $AGENT_NAME"

# Test 1: File existence
echo "Test 1: Checking required files..."
for file in IDENTITY.md SOUL.md AGENTS.md USER.md HEARTBEAT.md; do
  if [ ! -f "$WORKSPACE/$file" ]; then
    echo "❌ Missing: $file"
    exit 1
  fi
done
echo "✅ All required files present"

# Test 2: Configuration syntax
echo "Test 2: Validating configuration..."
openclaw agents list | grep -q "$AGENT_NAME"
if [ $? -eq 0 ]; then
  echo "✅ Agent registered correctly"
else
  echo "❌ Agent not found in configuration"
  exit 1
fi

# Test 3: Agent loading
echo "Test 3: Testing agent load..."
openclaw agents test "$AGENT_NAME"
if [ $? -eq 0 ]; then
  echo "✅ Agent loads successfully"
else
  echo "❌ Agent failed to load"
  exit 1
fi

echo "🎉 All tests passed!"
```

**Error recovery:**

- If automated tests fail: Review error messages, check file syntax, verify configuration
- If test script fails: Check script permissions, verify paths are correct

### Optional: systemd service configuration

For production deployments, the agent can run as a systemd service:


**Service file example:**

```bash
# Create systemd service file
sudo tee /etc/systemd/system/openclaw-agent.service > /dev/null <<EOF
[Unit]
Description=OpenClaw Agent Service
After=network.target

[Service]
Type=simple
User=<your-username>
WorkingDirectory=/home/<your-username>/.openclaw
ExecStart=/usr/bin/node /home/<your-username>/.npm-global/lib/node_modules/openclaw/dist/index.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target


[Install]
WantedBy=multi-user.target
EOF
```

**Enable and start service:**

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable openclaw-agent.service

# Start service now
sudo systemctl start openclaw-agent.service

# Check status
sudo systemctl status openclaw-agent.service

# View logs
sudo journalctl -u openclaw-agent.service -f
```

**Error recovery:**

- If service fails to start: Check journalctl logs, verify file paths, check user permissions
- If service crashes: Check OpenClaw logs, verify agent configuration, restart service
- If service wont enable: Check systemd configuration syntax, verify systemd is running

## Workflow: iterate on an existing agent

When improving an existing agent, ask:

1) What are the top 3 failure modes you have seen? (loops, overreach, verbosity, etc.)
2) What autonomy changes do you want?
3) Any new safety boundaries?
4) Any changes to heartbeat behavior?

Then propose targeted diffs to:

- `SOUL.md` (persona/tone/boundaries)
- `AGENTS.md` (operating rules + memory + delegation)
- `HEARTBEAT.md` (small checklist)

Keep changes minimal and surgical.

**Error recovery:**

- If diff application fails: Check file permissions, verify file exists, retry with backup
- If changes break agent behavior: Restore from git or backup, review changes
- If user rejects changes: Ask for clarification, propose alternative modifications
