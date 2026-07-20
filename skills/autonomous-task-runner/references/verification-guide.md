# Verification Guide

How to verify that each task type was completed correctly. Run verification after EVERY execution
attempt. A failed verification counts as a retry.

> **Context:** In the task-runner skill, verification is performed by the DISPATCHER mode after
> a subagent reports completion. The dispatcher reads the subagent output, applies the checks
> below, then updates the queue file. See `SKILL.md` → Mode 2: DISPATCHER → Step 3.

---

## General Verification Principles

1. **Verify the result, not the action.** Don't just check that a tool ran — check that the expected outcome exists.
2. **Use the simplest check possible.** File exists check > reading the whole file. Exit code check > parsing all output.
3. **Record what you verified.** Add a `verification` field to the task object when a task is marked done.
4. **Fail clearly.** If verification fails, record the reason in `strategies_tried` so the next retry uses a different approach.

---

## info-lookup

### Verification Checklist

| Check | How to Verify | Pass Condition |
|-------|--------------|----------------|
| Result is non-empty | Inspect search/fetch output | Response length > 0 |
| Result is relevant | Scan for key terms from the task description | At least one key term appears in result |
| Result is not an error | Check for error indicators | No "404", "403", "not found", "error", "unavailable" in content |
| Result is not an ad/SEO page | Quick scan of content quality | Contains factual sentences, not just keyword lists |
| Information is current (if recency matters) | Check dates in result | Result references dates within expected range |

### Verification Steps

```
1. Check that web_search returned ≥1 result
2. Open first result: check title + snippet for relevance
3. If relevance score is low (key terms missing), try second result
4. Extract the specific data point needed (price, fact, URL, etc.)
5. Confirm the extracted data answers the task goal
6. Mark done; set deliverable to the extracted data as a string
```

### Failure Signals

- Result is empty or all results are paywalled
- Result contains only ads, sponsored content, or navigation pages
- Data is outdated (>6 months old when current data was needed)
- Key term appears in URL but not in content

---

## file-creation

### Verification Checklist

| Check | How to Verify | Pass Condition |
|-------|--------------|----------------|
| File exists | `exec: ls -la <path>` or `read` tool | File found, no error |
| File is non-empty | `exec: wc -c <path>` | Size > 0 bytes |
| File contains expected content | `read` tool on file | Key content from task description is present |
| File is in correct location | Compare path to task goal | Path matches intended location |
| File is readable | `read` tool attempt | No permission error |

### Verification Steps

```
1. exec: ls -la <expected_path>
   → If not found: FAIL (file was not created)
2. exec: wc -c <expected_path>
   → If 0 bytes: FAIL (file empty)
3. read: first 20 lines of file
   → If key content missing: FAIL (wrong content)
4. Check path matches task goal
   → If path different: warn but don't fail (note in deliverable)
5. Mark done; set deliverable_path to the file path
```

### Failure Signals

- `ls` returns "No such file or directory"
- File exists but is 0 bytes
- File content is boilerplate/placeholder with no actual task-relevant content
- File is at wrong path (was written to cwd instead of specified path)

---

## code-execution

### Verification Checklist

| Check | How to Verify | Pass Condition |
|-------|--------------|----------------|
| Command ran without error | Check exit code | Exit code = 0 |
| No unexpected stderr | Inspect stderr | Stderr is empty or contains only warnings (not errors) |
| Expected output present | Inspect stdout | Stdout contains expected data or confirmation |
| Side effects occurred (if any) | Check for expected side effects | Files created, service restarted, etc. |

### Verification Steps

```
1. Capture both stdout and stderr from exec
2. Check exit code: if ≠ 0 → FAIL
3. Scan stderr: if contains "error", "fatal", "exception" → FAIL
4. Check stdout for expected output (task-specific):
   - "installed successfully" for installs
   - expected data for queries
   - test pass indicators for test runs
5. If side effects expected: verify them (file exists, service running, etc.)
6. Mark done; set deliverable to relevant stdout excerpt
```

### Failure Signals

- Non-zero exit code
- Stderr contains "Error:", "FATAL:", "Exception:", "Traceback:"
- Stdout is empty when output was expected
- Expected side effect did not occur (file not created, service not started)

### Transient Failure Handling

Some code execution failures are transient (network timeout, resource temporarily unavailable). These can be retried with the SAME strategy (exception to the normal "different strategy on retry" rule):

- Exit code 1 + "connection refused" → transient, retry same strategy
- Exit code 124 (timeout) → increase timeout, retry same strategy  
- Exit code 1 + "permission denied" → not transient, switch strategy or block

---

## agent-delegation

### Verification Checklist

| Check | How to Verify | Pass Condition |
|-------|--------------|----------------|
| Sub-agent completed | Check session status | Session reports done/success |
| Deliverable received | Check for output file or message | Deliverable exists and is non-empty |
| Deliverable is relevant | Inspect deliverable content | Content matches task goal |
| No error state | Check sub-agent last message | No error/blocked indicators |

### Verification Steps

```
1. Confirm sub-agent session is in terminal state (done, not running)
2. Locate deliverable: check stated output path or session response
3. If deliverable is a file: apply file-creation verification
4. If deliverable is text: verify it's non-empty and relevant
5. If sub-agent reported blocked: propagate block to this task
6. Mark done; set deliverable or deliverable_path from sub-agent output
```

### Failure Signals

- Sub-agent session timed out
- Sub-agent reported error or blocked state
- No deliverable produced
- Deliverable exists but is empty or irrelevant
- Sub-agent produced output for wrong task

---

## reminder-scheduling

### Verification Checklist

| Check | How to Verify | Pass Condition |
|-------|--------------|----------------|
| Cron job registered (if cron used) | `exec: crontab -l` | New cron entry appears with correct schedule |
| Reminder file exists (if file fallback) | `ls <reminder_path>` | File found |
| Schedule is correct | Compare cron entry or file content to task | Time/recurrence matches task description |
| No duplicate entries | Scan crontab for duplicates | Only one matching entry |

### Verification Steps

```
1. If cron tool was used:
   exec: crontab -l | grep "<task keyword>"
   → If not found: FAIL
   → If found: confirm schedule matches task (day, time, command)

2. If reminder file was used:
   read: reminder file
   → Check content matches task (date, time, action)

3. Confirm no existing duplicate
4. Mark done; set deliverable to "Reminder set for [time]: [action]"
```

### Failure Signals

- `crontab -l` doesn't show the new entry
- Reminder file not created
- Schedule in crontab doesn't match what was requested
- Crontab syntax error (check with `crontab -l 2>&1`)

---

## messaging

### Verification Checklist

| Check | How to Verify | Pass Condition |
|-------|--------------|----------------|
| No send error | Check tool response | Tool returned success/ok status |
| Message ID returned (if applicable) | Check tool response | Message ID or confirmation present |
| Correct channel/recipient | Compare tool response to task | Channel/recipient matches task |
| Correct content | Review sent content | Content matches task intent |

### Verification Steps

```
1. Check message tool response for error indicators
   → If error: FAIL with error message in strategies_tried
2. Check for message ID or delivery confirmation in response
   → If absent: note as warning (soft fail — may still have sent)
3. If the channel is readable, verify message appears:
   exec: (channel-specific read command)
   → Compare sent content to received
4. Mark done; set deliverable to "Message sent to [channel]: '[preview]'"
```

### Failure Signals

- Tool returns error code or error message
- "Not authorized", "invalid token", "channel not found" in response
- "Rate limited" in response (retry with delay)
- No confirmation message from tool

---

## unknown

### Verification Checklist

| Check | How to Verify | Pass Condition |
|-------|--------------|----------------|
| Re-classification succeeded | Check assigned type | Type is no longer "unknown" |
| Executed under new type | Follow type-specific verification | See above sections |

### Verification Steps

```
1. After web_search or user clarification, re-classify the task
2. If re-classification succeeded: proceed with that type's verification
3. If still unknown after 1 clarification attempt: mark blocked
   blocked_reason = "Task description is too ambiguous to execute"
   user_action_required = "Please clarify: [specific question about what action is needed]"
```

---

## Verification Failure Recording

When verification fails, record this in `strategies_tried`:

```json
{
  "strategy": "web_search",
  "tool": "web_search",
  "attempted_at": "2026-01-15T09:05:00Z",
  "result": "returned 5 results but none contained the price data requested",
  "verification_failure": "key term 'gold price' not found in any result"
}
```

This record helps the next retry pick a better strategy and helps the user understand what was attempted when a task is blocked.

---

## Quick Reference: Verification by Type

| Task Type | Minimum Verification | Tool Used |
|-----------|---------------------|-----------|
| info-lookup | Result non-empty + key term present | Inspect response |
| file-creation | File exists + non-empty + key content | `exec: ls` + `read` |
| code-execution | Exit code 0 + no errors in stderr | Check exec response |
| agent-delegation | Session done + deliverable received | Session status check |
| reminder-scheduling | Cron entry or file exists | `exec: crontab -l` or `ls` |
| messaging | No send error + delivery confirmation | Check tool response |
| unknown | Re-classified + type-specific check | Per above |
