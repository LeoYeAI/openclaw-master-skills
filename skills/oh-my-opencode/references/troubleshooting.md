# Oh My OpenCode — Troubleshooting Guide

Common issues and solutions when using oh-my-opencode.

---

## PTY Requirement

**Symptom**: OpenCode fails to start or agents can't execute bash commands.

**Cause**: OpenCode requires a pseudo-terminal (PTY) environment.

**Fix**:
- Use a proper terminal emulator (WezTerm, Alacritty, Ghostty, Kitty)
- On Windows, use WSL (Windows Subsystem for Linux)
- Don't run OpenCode inside environments that don't provide a PTY (some CI runners, Docker without `-it`)

```bash
# Docker: always use -it flags
docker run -it --rm ghcr.io/anomalyco/opencode
```

---

## Category Model Fallback

**Symptom**: All categories use the same model (e.g., your system default Sonnet for everything, even `quick` tasks).

**Cause**: Categories do NOT use their built-in defaults unless explicitly configured in `oh-my-opencode.json`.

**Fix**: Add categories to your config with the desired models:

```jsonc
{
  "categories": {
    "quick": { "model": "anthropic/claude-haiku-4-5" },
    "ultrabrain": { "model": "openai/gpt-5.2-codex", "variant": "xhigh" },
    "visual-engineering": { "model": "google/gemini-3-pro-preview" },
    "writing": { "model": "google/gemini-3-flash-preview" }
  }
}
```

**Diagnosis**:

```bash
bunx oh-my-opencode doctor --verbose
# Check the "Model Resolution" section
```

Only configure categories for providers you have access to. Unconfigured categories fall back to the system default model.

---

## Ollama Streaming Fix

**Symptom**: `JSON Parse error: Unexpected EOF` when using Ollama models.

**Cause**: Ollama returns NDJSON (newline-delimited JSON) when streaming. The SDK expects a single JSON object.

**Fix**: Set `stream: false` for all Ollama agent configurations:

```json
{
  "agents": {
    "explore": {
      "model": "ollama/qwen3-coder",
      "stream": false
    }
  }
}
```

**Verify Ollama is running**:

```bash
curl http://localhost:11434/api/tags
```

**Test with curl**:

```bash
curl -s http://localhost:11434/api/chat \
  -d '{"model": "qwen3-coder", "messages": [{"role": "user", "content": "Hello"}], "stream": false}'
```

**Tracking**: https://github.com/code-yeongyu/oh-my-opencode/issues/1124

---

## Context Window Management

**Symptom**: Agent runs out of context, becomes confused, or starts losing earlier instructions.

**Causes**:
- Large codebase files being read entirely
- Too many sequential tool calls accumulating in context
- Long conversations without compaction

**Fixes**:

1. **Enable aggressive truncation** (experimental):
   ```json
   { "experimental": { "aggressive_truncation": true } }
   ```

2. **Use background agents** for exploration — they run in separate context windows:
   ```javascript
   delegate_task(subagent_type="explore", run_in_background=true, prompt="...")
   ```

3. **Use `preemptive-compaction` hook** (enabled by default) — triggers compaction before overflow

4. **Start a new session** for unrelated tasks instead of continuing one long session

5. **Don't disable** `context-window-monitor` or `anthropic-context-window-limit-recovery` hooks

---

## Token Refresh / OAuth Issues

**Symptom**: Authentication fails mid-session, 401 errors from providers.

**Fixes**:

1. **Re-authenticate the provider**:
   ```bash
   opencode auth login
   # Select the provider and re-authenticate
   ```

2. **For Anthropic (Claude Pro/Max)**:
   ```bash
   opencode auth login
   # Provider: Anthropic → Login method: Claude Pro/Max
   # Complete OAuth flow in browser
   ```

3. **For Google Antigravity**:
   - Ensure `opencode-antigravity-auth@latest` is in your plugins
   - Re-authenticate: `opencode auth login` → Google → OAuth with Google (Antigravity)
   - For multi-account: add additional Google accounts for load balancing

4. **Check auth status**:
   ```bash
   opencode auth list
   ```

---

## Permission Configuration Issues

**Symptom**: Agent can't edit files, run bash commands, or access web resources.

**Cause**: Agent permissions are too restrictive.

**Fix**: Check and adjust agent permissions:

```json
{
  "agents": {
    "explore": {
      "permission": {
        "edit": "deny",
        "bash": "allow",
        "webfetch": "allow"
      }
    }
  }
}
```

Valid values: `ask` (prompt user), `allow` (always permit), `deny` (always block).

For bash, you can set per-command permissions:

```json
{
  "permission": {
    "bash": {
      "git": "allow",
      "rm": "deny",
      "npm": "ask"
    }
  }
}
```

---

## Agent Stuck in Loop

**Symptom**: Agent keeps repeating the same actions, doesn't make progress.

**Causes**:
- Edit errors causing repeated retries
- Task delegation failing and retrying
- Agent not finding what it's looking for

**Fixes**:

1. **Check if `doom_loop` permission is set**:
   ```json
   { "permission": { "doom_loop": "ask" } }
   ```
   This triggers user confirmation when infinite loop is detected.

2. **The `todo-continuation-enforcer` hook** forces the agent to continue from where it left off — ensure it's not disabled.

3. **The `edit-error-recovery` hook** handles edit failures — ensure it's enabled.

4. **The `delegate-task-retry` hook** retries failed delegations — if retries cause loops, consider disabling:
   ```json
   { "disabled_hooks": ["delegate-task-retry"] }
   ```

5. **Cancel and restart**: Use `/stop-continuation` to stop all continuation mechanisms, then start fresh.

---

## Session Not Resuming

**Symptom**: Can't continue a previous session, session state is lost.

**Fixes**:

1. **Continue last session**:
   ```bash
   opencode -c
   ```

2. **Continue specific session**:
   ```bash
   opencode -s <session-id>
   ```

3. **List available sessions**:
   ```bash
   opencode session list
   ```

4. **Check if `session-recovery` hook is enabled** (it should be by default):
   ```json
   // Make sure this is NOT in your disabled_hooks
   { "disabled_hooks": ["session-recovery"] }  // BAD - don't disable this
   ```

5. **For Prometheus plans**: Plans are stored in `.sisyphus/plans/*.md`. Run `/start-work` to resume execution.

---

## Background Agents Not Spawning

**Symptom**: `delegate_task(run_in_background=true)` doesn't create background tasks, or tasks stall.

**Causes**:
- Concurrency limits reached
- Provider rate limiting
- Stale timeout killing tasks too early

**Fixes**:

1. **Increase concurrency limits**:
   ```json
   {
     "background_task": {
       "defaultConcurrency": 10,
       "providerConcurrency": { "anthropic": 5, "google": 15 }
     }
   }
   ```

2. **Increase stale timeout** (default is 180000ms = 3 minutes):
   ```json
   {
     "background_task": {
       "staleTimeoutMs": 300000
     }
   }
   ```

3. **Check provider rate limits**: If using expensive models (e.g., Opus), you may be hitting API rate limits. Reduce `modelConcurrency`:
   ```json
   {
     "background_task": {
       "modelConcurrency": { "anthropic/claude-opus-4-5": 2 }
     }
   }
   ```

4. **Ensure `background-notification` hook is enabled** for completion notifications.

---

## Tmux Integration Not Working

**Symptom**: Background agents don't appear in tmux panes.

**Requirements** (all must be met):

1. Running inside an existing tmux session
2. Tmux installed and in PATH
3. OpenCode started with `--port` flag
4. `tmux.enabled` set to `true` in config

**Fix**:

```bash
# 1. Start tmux session
tmux new -s dev

# 2. Run OpenCode with server mode
opencode --port 4096

# 3. Ensure config has tmux enabled
```

```json
{
  "tmux": {
    "enabled": true,
    "layout": "main-vertical"
  }
}
```

---

## Plugin Not Loading

**Symptom**: Oh-my-opencode features not available, agents not recognized.

**Fixes**:

1. **Verify plugin is registered** in `~/.config/opencode/opencode.json`:
   ```json
   {
     "plugin": ["oh-my-opencode"]
   }
   ```

2. **Check OpenCode version**:
   ```bash
   opencode --version
   # Must be 1.0.150 or higher
   ```

3. **Re-run installer**:
   ```bash
   bunx oh-my-opencode install
   ```

4. **Run doctor**:
   ```bash
   bunx oh-my-opencode doctor
   ```

---

## OpenCode Version Compatibility

**Symptom**: Config breaks or features don't work after OpenCode update.

**Known issues**:
- OpenCode 1.0.132 or older has a config bug that may break oh-my-opencode
- `directory-agents-injector` hook is auto-disabled on OpenCode 1.1.37+ (native support)

**Fix**: Always use the latest OpenCode version:

```bash
opencode upgrade
```

---

## General Diagnostic Steps

Run the doctor command for a full diagnosis:

```bash
bunx oh-my-opencode doctor --verbose
```

This checks:
- OpenCode installation and version
- Plugin registration
- Config file validity
- Model resolution for all agents and categories
- Provider authentication status
- Hook status

If doctor doesn't resolve the issue:

1. Check OpenCode logs: `opencode --print-logs --log-level DEBUG`
2. Verify config syntax: Ensure valid JSON/JSONC (no extra commas, matching brackets)
3. Test with minimal config: Remove all overrides and test with defaults
4. Check the GitHub issues: https://github.com/code-yeongyu/oh-my-opencode/issues
5. Join the Discord: https://discord.gg/PUwSMR9XNk
