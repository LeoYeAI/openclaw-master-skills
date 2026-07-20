# SHIFT — DELEGATOR
# Orchestrates sessions_spawn for sub-identity execution.
# Handles the full delegation lifecycle: context prep → spawn → wait → read.

## Delegation Flow

```
1. ROUTER returns a routing decision (persona, confidence)
         ↓
2. Check cost budget (if costManagement enabled)
         ↓
3. Prepare context files (INBOUND.json + CONTEXT.md)
         ↓
4. Build sub-identity task prompt from persona + context
         ↓
5. sessions_spawn with model override
         ↓
6. Wait for completion (with timeout)
         ↓
7. Read OUTBOUND.md (or ESCALATE.md)
         ↓
8. Update cost tracking
         ↓
9. Return result to SYNTHESIS
```

## Step 1: Routing Decision

Receive from ROUTER:
```json
{
  "persona": "codex",
  "confidence": 0.85,
  "reason": "keyword_match:code,function"
}
```

## Step 2: Cost Budget Check

Read `cost-tracking.json`:
```
if costManagement.enabled:
    if currentSpend >= costBudgetPerHour:
        return { status: "budget_exceeded" }
    if currentSpend >= alertThreshold * costBudgetPerHour:
        send_user_warning("approaching delegation budget limit")
```

## Step 3: Context Preparation

Generate a unique `runId`: `run-{YYYYMMDD}-{HHMM}-{persona}-{sequence}`

Create session folder: `~/.shift/sessions/{runId}/`

Write `INBOUND.json`:
```json
{
  "runId": "run-20260318-1542-codex-001",
  "timestamp": "<ISO timestamp>",
  "persona": "codex",
  "userMessage": "<exact user message>",
  "masterConversationHistory": "<last N turns>",
  "activeFiles": "<files mentioned in conversation>",
  "masterSummary": "<brief summary of conversation so far>"
}
```

Write `CONTEXT.md` by pulling:
- Relevant MEMORY.md content (keyword-matched)
- Active file contents (read from workspace)
- Persona-specific context needs (from persona file)

## Step 4: Build Task Prompt

The task prompt fed to `sessions_spawn` combines:
1. Sub-identity persona (from persona file — voice, synthesis instructions)
2. The user's actual message
3. Instruction to read INBOUND.json and CONTEXT.md first
4. Instruction to write OUTBOUND.md when done
5. Instruction about consultation rules (if applicable)

```markdown
# You are Codex

[Full persona text from personas/CODEX.yaml]

## Your Task
<user's exact message>

## Context
Before starting, read:
- /path/to/INBOUND.json — your input and conversation history
- /path/to/CONTEXT.md — relevant project context

## Your Protocol
1. Read INBOUND.json and CONTEXT.md
2. Execute your task
3. If you need to consult another sub-identity (researcher):
   - Use the consult() function described in CONSULT.md
   - Wait for their response before continuing
4. Write your final result to /path/to/OUTBOUND.md
5. Include a ConsultationLog if you consulted anyone
6. End your response with [DONE]
```

## Step 5: sessions_spawn

```javascript
sessions_spawn({
  model: personaConfig.model,       // e.g. "openai-codex/gpt-5.3-codex"
  task: taskPrompt,
  label: `shift-${persona}-${runId}`,
  timeoutSeconds: personaConfig.timeout,
  attachments: [
    { name: "INBOUND.json", content: inboundJsonString },
    { name: "CONTEXT.md", content: contextMdString }
  ]
})
```

Key points:
- `model` is overridden to the persona's configured model
- `label` for log traceability
- `timeoutSeconds` = persona's `timeout` setting
- Files attached as text attachments for immediate access

## Step 6: Wait for Completion

Wait for `sessions_spawn` to complete. While waiting:
- Track elapsed time
- If elapsed > `timeout * 0.7`: send status update to user ("still working on this...")
- If elapsed > `timeout`: cancel sub-agent, master takes over

## Step 7: Read Result

```javascript
// Sub-agent completed successfully
outbound = read_file("~/.shift/sessions/{runId}/OUTBOUND.md")

if (outbound.status === "escalation") {
    return { status: "escalated", escalation: outbound }
}

if (outbound.status === "needs_consultation") {
    return { status: "needs_consultation", consultation: outbound.ConsultationLog }
}

// Sub-agent timed out or errored
if (subagent.status === "timeout" || subagent.status === "error") {
    return { status: "fallback", reason: subagent.status }
}
```

## Step 7a: Handle Consultation (if needed)

If `status === "needs_consultation"`:

1. Read `CONSULT-INBOUND.md` for the consultation question
2. Update user (transparent mode): `[Assistant] ↔ [{persona} → {target}] consulting on {topic}...`
3. Spawn the target sub-identity:
   ```javascript
   sessions_spawn({
     model: targetPersonaConfig.model,
     task: `You are ${target}.
Read: <path to CONSULT-INBOUND.md>
Write your answer to: <path to CONSULT-OUTBOUND.md>
End with [DONE].`,
     label: `shift-consult-${runId}`,
     timeoutSeconds: targetPersonaConfig.consultationTimeout
   })
   ```
4. Wait for `CONSULT-OUTBOUND.md`
5. Read consultation answer
6. Append to `CONTEXT.md`:
   ```markdown
   ## Consultation Answer from {target}
   {answer}
   ```
7. Re-spawn original sub-agent with enriched context:
   ```javascript
   sessions_spawn({
     model: originalPersonaConfig.model,
     task: `${originalPersonaPrompt}

## Additional Context (from consultation with {target})
{consultation answer}

Continue your task. Write final result to OUTBOUND.md. End with [DONE].`,
     label: `shift-${persona}-continue-${runId}`,
     timeoutSeconds: originalPersonaConfig.timeout / 2
   })
   ```
8. Wait for final OUTBOUND.md, then proceed to Step 8
```

## Step 8: Update Cost Tracking

After successful delegation, update `cost-tracking.json`:
```json
{
  "hourStart": "2026-03-18T15:00:00Z",
  "totalSpend": 0.87,
  "delegations": [
    {
      "runId": "run-20260318-1542-codex-001",
      "persona": "codex",
      "inputTokens": subagent.inputTokens,
      "outputTokens": subagent.outputTokens,
      "estimatedCost": calculate_cost(subagent),
      "timestamp": "<now>"
    }
  ]
}
```

## Step 9: Return to Synthesis

```javascript
return {
  status: "ok",          // ok | budget_exceeded | fallback | escalated
  persona: "codex",
  runId: "run-20260318-1542-codex-001",
  outbound: OUTBOUND.md contents,
  consultationLog: [...],  // from OUTBOUND.ConsultationLog
  cost: estimatedCost,
  elapsedMs: elapsedTime
}
```

## Timeout Handling

```
subagent timeout reached:
    → subagents(kill, target: childSessionKey)
    → master sends: "Taking a bit longer than expected..."
    → master waits another (timeout * 0.5) seconds
    → if still not done: master takes over with fallbackMessage
    → logs: "subagent_timeout: {persona}, fallback to master"
```

## Cancellation

If user sends interrupt signal (Ctrl+C, new message, etc.):
```
→ subagents(kill, target: childSessionKey)
→ if ESCALATE.md exists: read it
→ master handles request directly
→ logs: "user_interrupt: {runId}"
```
