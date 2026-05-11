# State Tracking Guidance

Reference for tracking multiple tasks or requests.

## Request Tracking

Label each user request:
```
[R1] Build login page
[R2] Add dark mode
[R3] Fix header alignment
```

Track state for user visibility:
```
[R1] [DONE] Done
[R2] [WIP] In progress (awaiting user approval for step 2)
[R3] [Q] Queued
```

## Managing Multiple Requests

When user sends a new request while another is in progress:

1. Acknowledge: "Got it, I'll add this to the queue"
2. Show updated queue to user
3. Ask user if priority should change

## Handling Interruptions

| Situation | Suggested Action |
|-----------|------------------|
| New unrelated request | Add to queue, ask user priority |
| Request affects current work | Pause, explain impact, ask user how to proceed |
| User says "stop" or "wait" | Stop immediately, await instructions |
| User changes requirements | Summarize impact, ask user to confirm changes |

## User Decisions

Always ask user before:
- Starting work on queued items
- Changing priority order
- Rolling back completed work
- Modifying the plan

## Progress File (Optional)

User may request a state file:
```markdown
## In Progress
[R2] Dark mode - Step 2/4 (awaiting user approval)

## Queued  
[R3] Header fix

## Done
[R1] Login page [DONE]
```

Update only when user requests or approves changes.
