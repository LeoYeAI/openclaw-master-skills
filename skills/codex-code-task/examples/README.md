# Examples

Practical usage patterns for `openclaw-skill-codex-cli`.

---

## 1. Quick Coding Task

Generate a self-contained script with no prior context needed.

```bash
cat > /tmp/codex-prompt.txt << 'EOF'
Create a Python CLI tool called `json-diff.py` that takes two JSON files as arguments
and prints a human-readable diff showing added, removed, and changed keys.

Requirements:
- argparse for CLI with --help
- Colored output (red for removed, green for added, yellow for changed)
- Recursive diff for nested objects
- Exit code 0 if identical, 1 if different
- Handle malformed JSON gracefully

Save to the project directory.
EOF

nohup python3 ~/.openclaw/workspace/skills/codex-cli-task/run-task.py \
  --task "$(cat /tmp/codex-prompt.txt)" \
  --project ~/projects/json-diff \
  --session "agent:main:whatsapp:group:YOUR_GROUP_JID@g.us" \
  --session-label "json-diff tool" \
  --timeout 600 \
  > /tmp/codex-run.log 2>&1 &

echo "Launched with PID $!"
```

Expected: 5–10 minutes. Output delivered to WhatsApp + agent summary.

---

## 2. Deep Research

Codex web search + synthesis capabilities for investigation tasks.

```bash
cat > /tmp/codex-prompt.txt << 'EOF'
You are being used as a Deep Research Tool. EXECUTE the research below immediately.
Do NOT ask for permission, do NOT propose a plan, do NOT ask clarifying questions.
Search the web thoroughly, read pages, and return comprehensive findings.

OUTPUT FORMAT: Structured report with sections, key findings, specific examples, and links.

RESEARCH TASK:
Investigate how teams are actually running LLM agents in production in 2026.
Specifically:
- What orchestration frameworks are seeing real adoption (not just hype)?
- What are the most common failure modes and how do teams handle them?
- How do teams handle cost management for high-volume agent workloads?
- What does the monitoring/observability stack look like?
- Real examples from engineering blogs, forum posts, and case studies preferred.
EOF

nohup python3 ~/.openclaw/workspace/skills/codex-cli-task/run-task.py \
  --task "$(cat /tmp/codex-prompt.txt)" \
  --project /tmp/codex-research \
  --session "agent:main:whatsapp:group:YOUR_GROUP_JID@g.us" \
  --session-label "LLM agents in production research" \
  --timeout 1800 \
  > /tmp/codex-run.log 2>&1 &
```

Expected: 15–30 minutes. Use `--timeout 1800` for research tasks.

If the user wants a no-network run, add `--no-search`.

---

## 3. Multi-Step Workflow with Session Resumption

A realistic two-phase workflow: research → implementation.

### Phase 1: Research

```bash
cat > /tmp/phase1.txt << 'EOF'
Analyze the codebase at this path and give me a comprehensive architecture overview.

Focus on:
1. How data flows through the system (from API request to response)
2. Where the main complexity lives and why
3. What the test coverage looks like and what's missing
4. Top 3 things that should be refactored and why

Be specific — name files, functions, line numbers where relevant.
EOF

nohup python3 ~/.openclaw/workspace/skills/codex-cli-task/run-task.py \
  --task "$(cat /tmp/phase1.txt)" \
  --project ~/projects/my-service \
  --session "agent:main:whatsapp:group:YOUR_GROUP_JID@g.us" \
  --session-label "my-service architecture review" \
  --timeout 1200 \
  > /tmp/codex-phase1.log 2>&1 &
```

Wait for completion. Find the session ID:

```bash
# From logs
grep "Session registered" /tmp/codex-phase1.log
# → 📝 Session registered: 019cccab-3676-7860-8353-aaa69ba734f7

# Or from registry
python3 -c "
from session_registry import find_session_by_label
s = find_session_by_label('my-service architecture')
print(s['session_id'])
"
```

### Phase 2: Implementation (resumes Phase 1 context)

```bash
cat > /tmp/phase2.txt << 'EOF'
Based on your analysis, implement the most impactful refactoring you identified.

Specifically:
- Make the change you said would have the highest impact
- Keep it focused and clean — one thing done right
- Write tests for the changed code
- Update any relevant docstrings

The goal is a PR-ready diff.
EOF

nohup python3 ~/.openclaw/workspace/skills/codex-cli-task/run-task.py \
  --task "$(cat /tmp/phase2.txt)" \
  --project ~/projects/my-service \
  --session "agent:main:whatsapp:group:YOUR_GROUP_JID@g.us" \
  --resume 019cccab-3676-7860-8353-aaa69ba734f7 \
  --session-label "my-service refactor implementation" \
  --timeout 2400 \
  > /tmp/codex-phase2.log 2>&1 &
```

Codex picks up the conversation where it left off — knows the codebase, knows what it found, and can proceed directly to implementation.

---

## 4. Long-Running Batch Task

For tasks that may take the full default 2-hour window.

```bash
cat > /tmp/codex-batch.txt << 'EOF'
Process all Python files in this project:
1. Add type annotations to all functions that don't have them
2. Add docstrings to public functions that lack them (Google style)
3. Fix any obvious issues flagged by ruff (run it first to see what's there)

Work through files systematically. After every 5 files, output a progress summary.

Send progress updates via bash (background, no agent wake):
python3 ~/.openclaw/workspace/skills/codex-cli-task/scripts/openclaw_notify.py \
  -g "YOUR_GROUP_JID@g.us" -m "Progress: processed X/Y files" --bg
EOF

nohup python3 ~/.openclaw/workspace/skills/codex-cli-task/run-task.py \
  --task "$(cat /tmp/codex-batch.txt)" \
  --project ~/projects/my-lib \
  --session "agent:main:whatsapp:group:YOUR_GROUP_JID@g.us" \
  --session-label "my-lib type annotation pass" \
  --timeout 7200 \
  > /tmp/codex-batch.log 2>&1 &
```

You'll get progress updates every few minutes like:

```text
📡 Progress: processed 12/47 files
📡 Progress: processed 24/47 files — found 3 complex functions needing manual review
📡 Progress: processed 47/47 files — done
```

---

## 5. Codebase Q&A

Ask Codex questions about a codebase it hasn't seen before.

```bash
cat > /tmp/codex-qa.txt << 'EOF'
Read the codebase in this directory thoroughly. Then answer these questions:

1. How does authentication work? Trace a request from the API endpoint to the auth check.
2. Where is the database connection managed? Is it connection-pooled?
3. Are there any obvious N+1 query problems?
4. What's the test strategy — unit, integration, e2e? What's the coverage like?
5. What would you change first if you were joining this team?

Read the code, don't guess.
EOF

nohup python3 ~/.openclaw/workspace/skills/codex-cli-task/run-task.py \
  --task "$(cat /tmp/codex-qa.txt)" \
  --project ~/projects/unfamiliar-codebase \
  --session "agent:main:whatsapp:group:YOUR_GROUP_JID@g.us" \
  --session-label "codebase Q&A" \
  --timeout 900 \
  > /tmp/codex-qa.log 2>&1 &
```

---

## 6. Working with Output Files

Every task saves its output to `/tmp/codex-<timestamp>.txt`. The path is included in the completion notification.

Read the full output after completion:

```bash
cat /tmp/codex-20260308-090836.txt
```

Find all recent output files:

```bash
ls -lt /tmp/codex-*.txt | head -10
```

The output file is especially useful for long research reports that exceed the WhatsApp preview.

---

## Tips

**For research tasks:** Always start with the "Deep Research Tool" prefix (see example 2). Without it, Codex may spend more of the run planning or asking for clarification instead of executing immediately.

**For iterative work:** Always use `--resume` for follow-up tasks on the same project. This gives Codex the context from previous turns — what files it read, what it found, and what decisions were made.

**For monitoring:** Keep `tail -f /tmp/codex-run.log` open in a terminal to see real-time stderr output from the runner alongside chat heartbeats.

**For debugging:** If something goes wrong, the log file at `/tmp/codex-run.log` has the full stderr output including crash tracebacks.
