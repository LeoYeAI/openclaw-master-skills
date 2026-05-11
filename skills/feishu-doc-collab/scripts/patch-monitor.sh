#!/bin/bash
# Feishu Doc Collaboration — Monitor Patch Script
# Patches OpenClaw's Feishu monitor.ts to trigger /hooks/agent on document edit events.
#
# Usage: bash ./skills/feishu-doc-collab/scripts/patch-monitor.sh
#
# Prerequisites:
#   1. hooks must be enabled in openclaw.json: "hooks": { "enabled": true, "token": "<token>" }
#   2. DOC_PROTOCOL.md must exist in workspace
#   3. config.json in this skill directory must have agent_name set
#
# Safe to re-run — idempotent.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
MONITOR="/usr/lib/node_modules/openclaw/extensions/feishu/src/monitor.ts"
CONFIG="$SKILL_DIR/config.json"

# Read agent config
if [ ! -f "$CONFIG" ]; then
  echo "ERROR: config.json not found at $CONFIG"
  echo "Copy config.json.example and fill in your agent_name."
  exit 1
fi

AGENT_NAME=$(python3 -c "import json; print(json.load(open('$CONFIG'))['agent_name'])" 2>/dev/null)
AGENT_DISPLAY=$(python3 -c "import json; print(json.load(open('$CONFIG'))['agent_display_name'])" 2>/dev/null)

if [ -z "$AGENT_NAME" ] || [ "$AGENT_NAME" = "MyBot" ]; then
  echo "WARNING: agent_name is not configured (still 'MyBot'). Edit $CONFIG first."
  echo "Continuing with default name 'MyBot'..."
fi

if [ ! -f "$MONITOR" ]; then
  echo "ERROR: monitor.ts not found at $MONITOR"
  echo "Is OpenClaw installed? Expected Feishu extension at:"
  echo "  /usr/lib/node_modules/openclaw/extensions/feishu/"
  exit 1
fi

if grep -q "/hooks/agent" "$MONITOR" 2>/dev/null && grep -q "_editDebounce" "$MONITOR" 2>/dev/null; then
  echo "monitor.ts already patched (hooks + debounce) — no changes needed."
  exit 0
fi

if grep -q "/hooks/agent" "$MONITOR" 2>/dev/null && ! grep -q "_editDebounce" "$MONITOR" 2>/dev/null; then
  echo "monitor.ts has hooks but missing debounce — will re-patch from backup or clean file..."
  if [ -f "$MONITOR.bak" ]; then
    cp "$MONITOR.bak" "$MONITOR"
    echo "Restored from backup, will apply full patch."
  else
    echo "WARNING: No backup found. Will attempt to patch debounce on top of existing hooks."
    echo "If this fails, manually restore monitor.ts from a clean OpenClaw install."
  fi
fi

echo "Applying feishu-doc-collab patch to monitor.ts..."
echo "  Agent name: $AGENT_NAME"
echo "  Display name: $AGENT_DISPLAY"
cp "$MONITOR" "$MONITOR.bak"

python3 << PYEOF
import json, sys

with open("$MONITOR") as f:
    content = f.read()

if "/hooks/agent" in content:
    print("Already patched")
    sys.exit(0)

agent_name = "$AGENT_NAME"
agent_display = "$AGENT_DISPLAY"

# Find injection point: after the system event is enqueued
inject_after = 'log(\`feishu[\${accountId}]: injected drive.file.edit system event for file \${fileToken}\`);'

hooks_code = '''
          // [feishu-doc-collab] Trigger isolated agent turn via /hooks/agent endpoint
          try {
            const fs2 = await import("fs");
            const cfgRaw = fs2.readFileSync(\`\${process.env.HOME || "/root"}/.openclaw/openclaw.json\`, "utf-8");
            const cfgJson = JSON.parse(cfgRaw);
            const hooksToken = cfgJson?.hooks?.token;
            const port = cfgJson?.gateway?.port ?? 18789;
            if (hooksToken) {
              const agentMessage = \`[Document Edit Event] Feishu document (token: \${fileToken}, type: \${fileType}) was edited.

INSTRUCTIONS — follow exactly:
1. Read DOC_PROTOCOL.md from workspace for the message format specification.
2. Read the document: feishu_doc(action=read, doc_token=\${fileToken})
3. Find the LAST message block (delimited by ---). Parse its header line: sender, receiver, status.
4. Decision logic:
   - If status is 🔴 (editing) or missing → do NOTHING, reply NO_REPLY
   - If sender is yourself (''' + agent_name + ''') → do NOTHING, reply NO_REPLY
   - If receiver is not your name (''' + agent_name + ''') and not "all" → do NOTHING, reply NO_REPLY
   - If status is 🟢 (complete) AND receiver is you or "all" → process the message
5. If processing: compose your reply in the protocol format and append it:
   feishu_doc(action=append, doc_token=\${fileToken}, content="---\\\\n> **''' + agent_display + '''** → **{sender}** | 🟢 完成\\\\n\\\\n{your reply}\\\\n")
6. If not processing: reply NO_REPLY\`;
              const resp = await fetch(\`http://127.0.0.1:\${port}/hooks/agent\`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "Authorization": \`Bearer \${hooksToken}\` },
                body: JSON.stringify({ message: agentMessage }),
              });
              if (resp.ok) {
                log(\`feishu[\${accountId}]: triggered /hooks/agent for doc edit on \${fileToken}\`);
              } else {
                const body = await resp.text().catch(() => "");
                log(\`feishu[\${accountId}]: /hooks/agent returned \${resp.status}: \${body.slice(0,200)}\`);
              }
            } else {
              log(\`feishu[\${accountId}]: hooks.token not configured, cannot trigger agent\`);
            }
          } catch (wakeErr) {
            log(\`feishu[\${accountId}]: agent trigger failed (non-fatal): \${String(wakeErr)}\`);
          }'''

if inject_after in content:
    content = content.replace(inject_after, inject_after + hooks_code)
    with open("$MONITOR", "w") as f:
        f.write(content)
    print("Patch applied successfully!")
    print(f"Agent configured as: {agent_name} ({agent_display})")
else:
    print("ERROR: Could not find injection point in monitor.ts")
    print("The file structure may have changed after an OpenClaw update.")
    print("Manual patching may be required. See references/manual-patch.md")
    sys.exit(1)
PYEOF

echo ""
echo "✅ Patch applied. Restart the gateway to activate:"
echo "   openclaw gateway restart"
