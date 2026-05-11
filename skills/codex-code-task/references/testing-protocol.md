# Testing Protocol

Canonical E2E validation protocol for the OpenClaw Codex async runner.

Use this when the user asks to:

- run tests
- verify the skill works
- validate routing / notifications / wake-up flow
- do an operator smoke test

This protocol is about **end-to-end orchestration validation**, not plain `pytest` discovery.

## Goal

Validate the full OpenClaw skill pipeline:

1. routing resolves correctly
2. detached launch succeeds
3. heartbeat arrives after >60s
4. Codex can send at least one mid-task update
5. final result is delivered to the source chat/thread
6. OpenClaw wake/continuation happens in the same session

## Required Sequence

1. Run `--validate-only` first.
2. Save the E2E prompt to a file.
3. Launch with `nohup`.
4. Do not wait in the same turn after a successful launch.
5. Evaluate PASS/FAIL only after the async completion/wake arrives.

## Launch Proof Gate

Before telling the user it launched, verify all of:

1. `nohup` returned a PID
2. `ps -p <PID>` shows the process alive
3. log contains `🔧 Starting OpenAI Codex...`
4. thread routing validation passed for Telegram thread runs

## Pass Criteria

1. Launch notification appears in the correct source chat/thread
2. At least one wrapper heartbeat appears after ~60 seconds
3. At least one Codex mid-task update appears
4. Final result appears in the correct source chat/thread
5. Agent continuation/wake appears in the same OpenClaw session

## Interactive Iterate Rule

For `--completion-mode iterate` test runs:

- do exactly one continuation step after phase 1
- then stop

Reason: enough to validate the iterative path without wasting time and tokens.

## Visibility Rule

Between completion of one Codex run and launch of a next iteration, there must be a visible analysis/decision message in chat.

No silent chaining directly from completion to the next detached launch.

## Canonical Prompt Pattern

Keep the prompt compact but make sure it:

- sends a progress update near the start
- runs longer than 60s, e.g. `sleep 70`
- sends another progress update after the sleep
- performs a few real shell/file actions
- returns a short structured report

## Canonical Commands

```bash
cat > /tmp/codex-full-test-prompt.txt << 'EOF'
# 1) send a progress update now
# 2) create a small test artifact
# 3) sleep 70
# 4) send another progress update
# 5) run a few shell commands
# 6) return a short structured report
EOF

python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/codex-full-test-prompt.txt)" \
  --project /tmp/codex-e2e-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --validate-only

nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/codex-full-test-prompt.txt)" \
  --project /tmp/codex-e2e-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --timeout 900 \
  > /tmp/codex-full-test.log 2>&1 &
```

## Artifacts To Check

- wrapper log: `/tmp/codex-full-test.log`
- final output file: `/tmp/codex-YYYYMMDD-HHMMSS.txt`
- registry entry: `~/.openclaw/codex_sessions.json`

## Failure Triage

If the test fails, check in this order:

1. routing validation output
2. launch proof gate items
3. log file
4. final output file
5. session registry
6. whether the progress helper was actually invoked
