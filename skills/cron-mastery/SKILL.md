---
name: cron-mastery
description: Master OpenClaw's timing systems. Use for scheduling reliable reminders, setting up periodic maintenance (janitor jobs), and understanding when to use Cron vs Heartbeat for time-sensitive tasks.
---

# Cron Mastery

**Rule #1: Heartbeats drift. Cron is precise.**

This skill provides the definitive guide for managing time in OpenClaw 2026.2.15+. It solves the "I missed my reminder" problem by enforcing a strict separation between casual checks (heartbeat) and hard schedules (cron).

## The Core Principle

| System | Behavior | Best For | Risk |
| :--- | :--- | :--- | :--- |
| **Heartbeat** | "I'll check in when I can" (e.g., every 30-60m) | Email checks, casual news summaries, low-priority polling. | **Drift:** A "remind me in 10m" task will fail if the heartbeat is 30m. |
| **Cron** | "I will run at exactly X time" | Reminders ("in 5 mins"), daily reports, system maintenance. | **Clutter:** Creates one-off jobs that need cleanup. |

## 1. Setting Reliable Reminders (2026.2.15+ Standard)

**Rule:** Never use `act:wait` or internal loops for long delays (>1 min). Use `cron:add` with a one-shot `at` schedule.

### Precision & The "Scheduler Tick"
While Cron is precise, execution depends on the **Gateway Heartbeat** (typically every 10-60s). A job set for `:00` seconds will fire on the first "tick" after that time. Expect up to ~30s of variance depending on your gateway config.

### Modern One-Shot Reminder Pattern
Use this payload structure for "remind me in X minutes" tasks. 

**Key Features (v2026.2.15+):**
- **Payload Choice:** Use **AgentTurn** with **Strict Instructions** for push notifications (reminders that ping your phone). Use **systemEvent** only for silent logs or background state updates.
- **Reliability:** `nextRunAtMs` corruption and "Add-then-Update" deadlocks are resolved.
- **Auto-Cleanup:** One-shot jobs auto-delete after success (`deleteAfterRun: true`).

**CRITICAL: Push Notifications vs. Silent Logs**

- **systemEvent (Silent):** Injects text into the chat history. Great for background logs, but **WILL NOT** ping the user's phone on Telegram/WhatsApp.
- **AgentTurn (Proactive):** Wakes an agent to deliver the message. **REQUIRED** for push notifications. Use the "Strict" prompt to avoid AI chatter.

**For push-notification reminders (Reliable):**
```json
{
  "name": "Remind: Water",
  "schedule": { "kind": "at", "at": "2026-02-06T01:30:00Z" },
  "payload": {
    "kind": "agentTurn",
    "message": "DELIVER THIS EXACT MESSAGE TO THE USER WITHOUT MODIFICATION OR COMMENTARY:\n\n💧 Drink water, Momo!"
  },
  "sessionTarget": "isolated",
  "delivery": { "mode": "announce", "channel": "telegram", "to": "1027899060" }
}
```

**For background logs (Silent):**
```json
{
  "name": "Log: System Pulse",
  "schedule": { "kind": "every", "everyMs": 3600000 },
  "payload": {
    "kind": "systemEvent",
    "text": "[PULSE] System healthy."
  },
  "sessionTarget": "main"
}
```

### Cron Concurrency Rule (Stabilized)
Pre-2026.2.15, the "Add-then-Update" pattern caused deadlocks. While this is now stabilized, it is still **best practice** to pass all parameters (including `wakeMode: "now"`) directly in the initial `cron.add` call for maximum efficiency.

## 2. The Janitor (Auto-Cleanup) - LEGACY

**Note:** As of v2026.2.14, OpenClaw includes **maintenance recompute semantics**. The gateway now automatically cleans up stuck jobs and repairs corrupted schedules. 

**Manual cleanup is only needed for:**
- One-shot jobs created with `deleteAfterRun: false`.
- Stale recurring jobs you no longer want.

### Why use `sessionTarget: "main"`? (CRITICAL)
Sub-agents (`isolated`) often have restricted tool policies and cannot call `gateway` or delete other `cron` jobs. For system maintenance like the Janitor, **always** target the `main` session via `systemEvent` so the primary agent (with full tool access) performs the cleanup.

## 3. Reference: Timezone Lock

For cron to work, the agent **must** know its time.
*   **Action:** Add the user's timezone to `MEMORY.md`.
*   **Example:** `Timezone: Cairo (GMT+2)`
*   **Validation:** If a user says "remind me at 9 PM," confirm: "9 PM Cairo time?" before scheduling.

## 4. The Self-Wake Rule (Behavioral)

**Problem:** If you say "I'll wait 30 seconds" and end your turn, you go to sleep. You cannot wake up without an event.
**Solution:** If you need to "wait" across turns, you **MUST** schedule a Cron job.

*   **Wait < 1 minute (interactive):** Only allowed if you keep the tool loop open (using `act:wait`).
*   **Wait > 1 minute (async):** Use Cron with `wakeMode: "now"`.

## 5. Legacy Migration Guide

If you have old cron jobs using these patterns, update them:

| Legacy (Pre-2026.2.3) | Modern (2026.2.15+) |
| :--- | :--- |
| `"schedule": {"kind": "at", "atMs": 1234567890}` | `"schedule": {"kind": "at", "at": "2026-02-06T01:30:00Z"}` |
| `"deliver": true` in payload | Not needed - `announce` mode handles delivery |
| `"sessionTarget": "main"` | `"sessionTarget": "isolated"` (default behavior) |
| Manual ghost cleanup required | One-shots auto-delete (`deleteAfterRun: true`) |
| `cron.update` after `cron.add` | Single-step `cron.add` with all properties |

## Troubleshooting

*   **"My reminder didn't fire":** Check `cron:list`. Verify the `at` timestamp is in the future (ISO 8601 format). Ensure `wakeMode: "now"` is set.
*   **"Gateway Timeout (10000ms)":** This happens if the `cron` tool takes too long (huge job list or file lock). 
    - **Fix 1:** Manually delete `~/.openclaw/state/cron/jobs.json` and restart the gateway if it's corrupted.
    - **Fix 2:** Run a manual sweep to reduce the job count.
*   **"Job ran but I didn't get the message":** Ensure you are using the **Strict Instruction Pattern** with `agentTurn` + `announce` mode for proactive pings.
*   **"The reminder message has extra commentary":** The subagent is being conversational. Use the strict prompt pattern: `"DELIVER THIS EXACT MESSAGE TO THE USER WITHOUT MODIFICATION OR COMMENTARY:\n\n💧 Your message here"`
