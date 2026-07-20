# Afterself Heartbeat Check

Run the state check and act accordingly.

## Step 1: Load state

```bash
node {baseDir}/scripts/state.js status
```

Read the `switchState` field from the response.

## Step 2: Route by state

### If `disabled` or `completed`
- Nothing to do. **HEARTBEAT_OK**

### If `triggered`
- Executor should be running. Check `executorProgress` for stuck actions. If `currentAction` hasn't changed in multiple heartbeats, log a warning. **HEARTBEAT_OK**

### If `armed`
- Run: `node {baseDir}/scripts/state.js is-overdue`
- If `overdue: false` → **HEARTBEAT_OK**
- If `overdue: true` → Send a check-in ping to the owner on all configured channels. Then run: `node {baseDir}/scripts/state.js record-ping`

### If `warning`
- Run: `node {baseDir}/scripts/state.js is-warning-expired`
- If `expired: false` → Send another reminder to the owner. **HEARTBEAT_OK**
- If `expired: true` → Begin escalation:
  1. Run `node {baseDir}/scripts/state.js begin-escalation`
  2. Load contacts from `node {baseDir}/scripts/state.js config get heartbeat.escalationContacts`
  3. Send each contact the escalation message from `{baseDir}/references/escalation-protocol.md`
  4. Log: `node {baseDir}/scripts/state.js audit escalation "contacts_notified"`

### If `escalating`
- Run: `node {baseDir}/scripts/state.js escalation-status`
- Check the `decision` field:
  - `"stand_down"` → Run `node {baseDir}/scripts/state.js stand-down`. Notify owner their contacts confirmed they're okay.
  - `"trigger"` → Run `node {baseDir}/scripts/state.js trigger`. Begin executor (see SKILL.md Executor section).
  - `"waiting"` → Check if escalation timeout has expired. If timeout exceeded with no responses → run `node {baseDir}/scripts/state.js trigger`. Otherwise → **HEARTBEAT_OK**, wait for responses.

## Step 3: Ghost check

If ghost mode is active (`ghostState: "active"` or `"fading"`):
- Run: `node {baseDir}/scripts/state.js ghost-decay-check`
- If `shouldRespond: false` and `probability: 0` → Ghost has fully faded. Update: `node {baseDir}/scripts/state.js update ghostState "retired"`. Log: `node {baseDir}/scripts/state.js audit ghost "retired"`

## Step 4: Mortality pool check

If `mortalityPool.enabled` is true and state is `armed`:
- Run: `node {baseDir}/scripts/mortality.js check-balance`
- If balance changed since last check, the state is updated automatically by the script
- (Nudging the user to buy tokens happens on owner check-in, not during heartbeat)
