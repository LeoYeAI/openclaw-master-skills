---
name: shift
description: Multi-identity delegation for OpenClaw. Turns a single agent into a system of specialized sub-identities (coding, research, quick tasks) each powered by different AI models. Use when: (1) the user asks a coding task (write, debug, implement, refactor, explain code), (2) the user asks for research, analysis, comparison, or explanation, (3) the user asks a quick question, lookup, or reminder, (4) the user asks anything that would benefit from a specialized model. NOT for: trivial greetings, acknowledgments, or meta-conversation about the chat itself. SHIFT handles routing, delegation, sub-identity-to-sub-identity consultation, synthesis, and cost management entirely within one conversation.
---

# SHIFT — Multi-Identity Delegation Skill

**One agent. Many specialists. One conversation.**

---

## ⚠️ SECURITY AND PRIVACY — READ BEFORE ENABLING

### What SHIFT Accesses

SHIFT reads from your OpenClaw workspace:
- `~/.openclaw/workspace/MEMORY.md` — excerpts attached to delegation context
- `~/.openclaw/workspace/.shift/config.yaml` — your persona and cost settings
- Session files it creates in `~/.openclaw/workspace/.shift/sessions/`

SHIFT writes to:
- `~/.openclaw/workspace/.shift/sessions/<runId>/` — per-delegation session files
- `~/.openclaw/workspace/.shift/cost-tracking.json` — delegation cost tracking
- `~/.openclaw/workspace/.shift/personas/*.yaml` — your persona overrides

### What SHIFT Transmits

When you enable delegation, the following are sent to whatever model providers you configure for each persona:
- Your message content
- Conversation history (last N turns, controlled by `contextBridge.historyTurns`)
- Active file contents and MEMORY.md excerpts relevant to the task
- Delegation metadata (runId, timestamps, persona name)

**You control which models are used.** SHIFT does not ship with or store credentials — it uses the model providers configured in your OpenClaw agent config. Review your provider's data handling policy.

### Data Exposure Risk

If your workspace files or MEMORY.md contain secrets (API keys, credentials, private data), and those files are referenced in a delegated task, that content will be transmitted to your configured model provider.

**Mitigations:**
- Do not delegate tasks that reference sensitive file paths
- Set `contextBridge.historyTurns` to a low number (e.g., 3)
- Use `costManagement.trackOnly: true` during evaluation to observe behavior without enforcement
- Use trusted or self-hosted model providers for sensitive work

### Setup Script

`scripts/setup.sh` creates local directories only. It does NOT:
- Make network calls
- Escalate privileges
- Modify system files
- Access credentials

### Cost and Consultations

Consultations spawn additional model calls. Costs are tracked in `cost-tracking.json` per delegation. Set `costManagement.trackOnly: true` to monitor before enforcing limits.

### Recommendations

1. Start with `costManagement.trackOnly: true` to observe costs
2. Set `contextBridge.historyTurns` to a small number (5 or less)
3. Set `contextBridge.archiveAfterMinutes: 30` for faster cleanup
4. Do not delegate tasks referencing sensitive file paths
5. Review model providers' data policies before sensitive work

---

Triggers on: any message that might benefit from specialized handling — coding tasks, research, analysis, quick lookups, or anything that warrants delegating to a sub-identity.

When SHIFT triggers, you read and follows the procedures below to: classify the task, delegate to the right sub-identity, handle consultation between sub-identities, and synthesize the final response in his own voice.

---

# SHIFT Procedures

Follow these steps for every message that triggers SHIFT.

---

## STEP 1 — Fast Path Check

Before anything, check if this message is trivially handled by you directly.

**Bypass delegation (return `none`) if message is ONLY:**
- Greetings: `hi`, `hey`, `hello`, `yo`, `sup`
- Acknowledgments: `thanks`, `thank you`, `ty`, `ok`, `sure`, `got it`, `makes sense`, `cool`, `nice`
- Meta: `that was fast`, `nice one`, `lol`, `haha`

**If none of those match, proceed to STEP 2.**

---

## STEP 2 — Load Config

Read the SHIFT config at:
```
~/.openclaw/workspace/.shift/config.yaml
```

If the file doesn't exist, run the setup script first:
```bash
bash ~/.openclaw/workspace/skills/shift/scripts/setup.sh
```

From config, extract:
- `displayMode` — `hidden` or `transparent`
- `fastPath` — `conservative` or `off`
- `costManagement.enabled`, `costManagement.costBudgetPerHour`, `costManagement.alertThreshold`
- `contextBridge.historyTurns`, `contextBridge.sessionFolder`
- `personas` — enabled personas and their settings

---

## STEP 3 — Cost Budget Check

If `costManagement.enabled: true`:

Read `~/.openclaw/workspace/.shift/cost-tracking.json`:

```json
{
  "hourStart": "2026-03-18T15:00:00Z",
  "totalSpend": 0.87,
  "delegations": [...]
}
```

**If current UTC hour > hourStart (new hour):**
→ Reset `totalSpend: 0`, update `hourStart` to current hour.

**If `totalSpend >= costBudgetPerHour`:**
→ You handle the task directly. Say: *"Handling this one myself to stay within your cost budget."*
Return `budget_exceeded`.

**If `totalSpend >= alertThreshold * costBudgetPerHour`:**
→ Send a quiet warning: *"Approaching delegation budget limit for this hour."*

---

## STEP 4 — Route to Persona

Using the enabled personas from config, classify the user's message.

### Keyword Scoring

For each enabled persona, count keyword matches in the user's message (case-insensitive, whole-word). Raw score = matches / total keywords.

**If raw score >= `minConfidence`:** Add to candidates.

**Runner special case:** Runner has `requireExplicit: true`. It only triggers if the message is predominantly a Runner task, not just containing a keyword. If the message has strong code/research keywords, Runner is NOT a match even if it has Runner keywords.

### Tie-Breaking

If multiple personas score above threshold:
→ Higher score wins. If tied: codex > researcher > runner.

### Default

If no persona scores above threshold → You handle directly. Return `none`.

---

## STEP 5 — Prepare Delegation Context

Generate a unique `runId`:
```
run-{YYYYMMDD}-{HHMM}-{persona}-{sequence}
Example: run-20260318-1551-codex-001
```

Create the session folder:
```
~/.openclaw/workspace/.shift/sessions/{runId}/
```

### Write INBOUND.json

```json
{
  "runId": "<runId>",
  "timestamp": "<ISO UTC>",
  "persona": "<matched persona>",
  "userMessage": "<exact user message>",
  "masterConversationHistory": <last N turns from conversation>,
  "activeFiles": <files mentioned>,
  "masterSummary": "<brief summary of conversation so far>"
}
```

### Write CONTEXT.md

Pull from:
- `~/.openclaw/workspace/MEMORY.md` (keyword-matched relevant sections)
- Any active file contents mentioned in the conversation
- Persona-specific context needs (from the persona definition in config)

Format:
```markdown
# Context for {persona}

## Project/Memory (relevant)
...

## Active Files
...

## Persona Context Needs
...
```

---

## STEP 6 — Build Task Prompt

Construct the prompt for the sub-agent:

```markdown
# You are {persona_name}

## Persona
{persona voice, tone, strengths, blind spots from config}

## Your Task
{user's exact message}

## Context
Before starting, read:
- /path/to/INBOUND.json — your input and conversation history
- /path/to/CONTEXT.md — relevant project context

## Your Protocol
1. Read INBOUND.json and CONTEXT.md
2. Execute your task
3. If you need to consult another sub-identity and your persona allows it:
   - Write your question to the session folder as CONSULT-INBOUND.md
   - Set a timeout: min(remaining_time * 0.5, your consultationTimeout)
   - Spawn the target sub-identity using sessions_spawn
   - Wait for them to write CONSULT-OUTBOUND.md
   - Read their response and continue with that context
4. Write your final result to /path/to/OUTBOUND.md
5. Include a ConsultationLog if you consulted anyone
6. End your response with [DONE]
```

---

## STEP 7 — Spawn Sub-Agent

```javascript
sessions_spawn({
  model: personaConfig.model,
  task: taskPrompt,
  label: `shift-${persona}-${runId}`,
  timeoutSeconds: personaConfig.timeout,
  attachments: [
    { name: "INBOUND.json", content: <inboundJsonString> },
    { name: "CONTEXT.md", content: <contextMdString> }
  ]
})
```

**Track elapsed time.** If `elapsed > timeout * 0.7`:
→ Send status to user: *"{persona} is still working on this..."*

---

## STEP 8 — Wait and Read Result

Wait for `sessions_spawn` to complete.

### Read OUTBOUND.md

From the session folder:
```
~/.openclaw/workspace/.shift/sessions/{runId}/OUTBOUND.md
```

Parse:
- `Status`: `complete` | `error` | `escalation`
- `Result`: the actual response content
- `ConsultationLog`: if sub-identity consulted another
- `Cost`: token counts if available

### Check for ESCALATE.md (Runner only)

If `Status: escalation`:
→ Runner detected the task was too complex. You take over directly.
→ Read `reason`, `summary`, `partialAnswer` from ESCALATE.md.
→ Incorporate any partial work Runner did.

---

## STEP 9 — Update Cost Tracking

After successful delegation, update `cost-tracking.json`:

```json
{
  "hourStart": "<current hour UTC>",
  "totalSpend": <previous + estimated cost>,
  "delegations": [
    {
      "runId": "<runId>",
      "persona": "<persona>",
      "inputTokens": <from sub-agent result if available>,
      "outputTokens": <from sub-agent result if available>,
      "estimatedCost": <calculate from model cost config>,
      "timestamp": "<now>"
    }
  ]
}
```

---

## STEP 10 — Synthesize Response

Transform the sub-identity's output into your voice.

### Detection

If `ConsultationLog` is present and non-empty:
→ Build consultation mention (ALWAYS shown):
```
{parent persona} consulted {target persona} on {topic}...
```

### Transformation Rules

| Sub-identity output | your transformation |
|---|---|
| Code | Explain what it does in plain English, highlight key parts, offer to add tests |
| Analysis/Research | Pull 2-3 key insights, bullet-point them, note caveats |
| Quick answer (Runner) | Relay directly with warmth added |

### Display Mode

**Hidden (default):**
```
[Assistant]: Here's the {implementation/analysis/answer}...
```

**Transparent:**
```
[Assistant] → [{persona}] working on this...
[Assistant] ← [{persona}] done.
[Assistant]: Here's the...
```

Consultation mentions are ALWAYS shown in both modes.

---

## STEP 11 — Handle Errors

| Scenario | Response |
|---|---|
| Sub-agent timeout | *"Looks like this one is taking longer than expected — let me work through it directly."* |
| Sub-agent error | *"Hit a snag with the specialist — let me handle this myself."* |
| sessions_spawn fails | Fall back to your handling directly |
| OUTBOUND.md missing | Assume sub-agent failed, You handle directly |
| Model unavailable | Log warning, You handle directly |

---

# Consultation Protocol (Master-Orchestrated)

**Key insight:** Sub-agent sessions cannot cleanly spawn child sessions and wait. The solution: You orchestrate the consultation from the master level.

## Flow

```
Codex needs context
        ↓
Codex writes CONSULT-INBOUND.md + OUTBOUND.md (Status: needs_consultation)
        ↓
You detect needs_consultation flag in OUTBOUND.md
        ↓
You tell user (transparent mode): "Codex ↔ [Codex → Researcher]..."
        ↓
You spawn Researcher with CONSULT-INBOUND.md
        ↓
Researcher writes CONSULT-OUTBOUND.md
        ↓
You read it, appends to Codex's CONTEXT.md
        ↓
You re-spawn Codex with enriched context (brief task: "continue with this context")
        ↓
Codex writes final OUTBOUND.md with ConsultationLog
        ↓
You synthesize — mentions the consultation (always visible)
```

## Sub-Agent Side (Codex/Researcher)

When a sub-agent needs to consult another sub-identity:

1. Check: is target in my `consults` list? Is target NOT in my `consultsNever`?
2. Write `CONSULT-INBOUND.md` to the session folder with the question + context
3. Write `OUTBOUND.md` with:
   ```markdown
   ## Status: needs_consultation
   
   ## PartialResult
   (what Codex has done/understood so far)
   
   ## ConsultationLog
   - consulted: researcher
   - question: "..."
   - status: pending
   ```
4. End response with `[NEEDS_CONSULTATION]` instead of `[DONE]`
5. Stop — You will take over from here

## Master Side

When reading OUTBOUND.md after a sub-agent returns:

### STEP 8a — Detect Consultation Need

If `Status: needs_consultation` is present:
1. Read `ConsultationLog` to get target and question
2. Read `CONSULT-INBOUND.md` for full context
3. Send user update (transparent mode): `[Assistant] ↔ [{persona} → {target}] consulting on {topic}...`
4. Proceed to STEP 8b

### STEP 8b — Run Consultation

```javascript
// Spawn the target sub-identity as a one-shot consultation
sessions_spawn({
  model: targetPersonaConfig.model,
  task: `You are ${target}.
Read the consultation question from: <path to CONSULT-INBOUND.md>
Write your answer to: <path to CONSULT-OUTBOUND.md>
End with [DONE].`,
  label: `shift-consult-${runId}`,
  timeoutSeconds: targetPersonaConfig.consultationTimeout
})
```

### STEP 8c — Feed Result Back

After consultation completes:
1. Read `CONSULT-OUTBOUND.md`
2. Append consultation answer to `CONTEXT.md`:
   ```markdown
   ## Consultation Answer from {target}
   {answer from CONSULT-OUTBOUND.md}
   ```
3. Re-spawn the original sub-agent with enriched context:
   ```javascript
   sessions_spawn({
     model: originalPersonaConfig.model,
     task: `${originalPersonaPrompt}
     
## Additional Context (from consultation)
The ${target} provided the following guidance:
<answer from CONSULT-OUTBOUND.md>

Continue your task using this context. Write your final result to OUTBOUND.md. End with [DONE].`,
     label: `shift-${originalPersona}-consult-continue-${runId}`,
     timeoutSeconds: originalPersonaConfig.timeout / 2  // Half remaining time
   })
   ```

### STEP 8d — Final Result

When re-spawned sub-agent completes:
1. Read final `OUTBOUND.md`
2. `ConsultationLog.status` should now be `complete`
3. Proceed to STEP 10 (Synthesis)

Consultation is **always mentioned** to the user — not gated by display mode.

## Depth Limit

**Max consultation depth = 1.** A sub-agent that was consulted CANNOT consult anyone else. This is enforced by: the consultation re-spawn prompt does NOT include the consultation protocol section. Only the first-level sub-agent has it.

## Timeout Handling

- If consultation times out: You fall back to Codex's partial result + own knowledge
- You warn: *"{target} took too long — Codex will continue without that context."*
- Partial result (if any) is still used

---

# Commands

## /shift status

Show current SHIFT status:
- Which personas are enabled
- Current cost budget status
- Display mode

## /shift mode hidden|transparent

Toggle display mode. Updates config.yaml.

## /shift fastpath on|off

Toggle fast-path mode.

## /delegate \<persona\> \<task\>

Explicitly delegate a task to a specific persona, ignoring keyword routing.

---

# Config Reference

Full schema at: `~/.openclaw/workspace/skills/shift/config/SCHEMA.yaml`

Key settings:

```yaml
displayMode: hidden          # hidden | transparent
fastPath: conservative       # conservative | off
costManagement:
  enabled: true
  costBudgetPerHour: 2.00   # USD
  alertThreshold: 0.75       # warn at 75%
personas:
  codex:
    model: <your coding model>
    timeout: 60
    consults: [researcher]
    consultationTimeout: 45
  researcher:
    model: <your research model>
    timeout: 90
    consults: []
    consultationTimeout: 45
  runner:
    model: <your fast model>
    timeout: 30
    consults: []
    consultationTimeout: 20
```

---

# Session Files

All delegation session files live at:
```
~/.openclaw/workspace/.shift/sessions/{runId}/
```

Files:
- `INBOUND.json` — delegation input
- `CONTEXT.md` — project context
- `OUTBOUND.md` — sub-identity result
- `ESCALATE.md` — Runner escalation (if any)
- `CONSULT-INBOUND.md` — consultation input
- `CONSULT-OUTBOUND.md` — consultation result

Auto-archived after `contextBridge.archiveAfterMinutes` (default: 60min).

---

*SHIFT — one brain, many specialists.*
