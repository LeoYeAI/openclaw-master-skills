#!/bin/bash
# Learning Loop - Initialization Script
# Creates the learning directory structure in your workspace
# Usage: bash init.sh [workspace-dir]
# Returns: 0 on success, 1 on configuration error
# Schedule: Once at setup
# Dependencies: None
# Side Effects: Creates directory structure and initial files

set -o pipefail

SCRIPT_NAME="init.sh"
WORKSPACE="${1:-$(pwd)}"
LEARNING_DIR="$WORKSPACE/memory/learning"

# ============================================================================
# INPUT VALIDATION
# ============================================================================

# Check if workspace is provided
if [[ -z "$WORKSPACE" ]]; then
    echo "ERROR: No workspace directory specified"
    echo "Usage: bash init.sh [workspace-dir]"
    exit 1
fi

# Check workspace exists or create it
if [[ ! -d "$WORKSPACE" ]]; then
    echo "Creating workspace directory: $WORKSPACE"
    mkdir -p "$WORKSPACE" || {
        echo "ERROR: Could not create workspace directory: $WORKSPACE"
        exit 1
    }
fi

if [[ ! -w "$WORKSPACE" ]]; then
    echo "ERROR: Workspace is not writable: $WORKSPACE"
    exit 1
fi

# Prevent system directories
if [[ "$WORKSPACE" =~ ^/(etc|bin|sbin|usr|System|Library|Applications) ]]; then
    echo "ERROR: Cannot use system directory as workspace: $WORKSPACE"
    exit 1
fi

echo "========================================="
echo "  Learning Loop - Initializer"
echo "  Workspace: $WORKSPACE"
echo "========================================="
echo ""

# Create directory structure
mkdir -p "$LEARNING_DIR/weekly"
echo "[OK] Created $LEARNING_DIR/weekly"

# Initialize events.jsonl (empty, append-only)
if [ ! -f "$LEARNING_DIR/events.jsonl" ]; then
    touch "$LEARNING_DIR/events.jsonl"
    echo "[OK] Created events.jsonl (empty)"
else
    LINES=$(wc -l < "$LEARNING_DIR/events.jsonl" | tr -d ' ')
    echo "[SKIP] events.jsonl already exists ($LINES events)"
fi

# Initialize rules.json with starter rules (v1.4.0 schema with confidence fields)
if [ ! -f "$LEARNING_DIR/rules.json" ]; then
    TODAY=$(date +%Y-%m-%d)
    cat > "$LEARNING_DIR/rules.json" << RULES
{
  "version": "1.4.0",
  "updated": "$TODAY",
  "rules": [
    {
      "id": "R-001",
      "type": "MUST",
      "category": "memory",
      "rule": "When your human tells you something important, STOP and write it to a file BEFORE continuing the conversation",
      "reason": "Context can be lost to compaction. Files survive, memory doesn't.",
      "created": "$TODAY",
      "violations": 0,
      "last_checked": "$TODAY",
      "last_validated": "$TODAY",
      "validation_count": 0,
      "confidence_score": 1.0
    },
    {
      "id": "R-002",
      "type": "MUST",
      "category": "memory",
      "rule": "Every 2 significant operations, save findings to a file. Don't accumulate context in your head.",
      "reason": "Compaction can happen at any time. Externalize immediately.",
      "created": "$TODAY",
      "violations": 0,
      "last_checked": "$TODAY",
      "last_validated": "$TODAY",
      "validation_count": 0,
      "confidence_score": 1.0
    },
    {
      "id": "R-003",
      "type": "MUST",
      "category": "learning",
      "rule": "After every debugging session or mistake, write an event to memory/learning/events.jsonl",
      "reason": "Learning only works if events are captured. This is the foundation.",
      "created": "$TODAY",
      "violations": 0,
      "last_checked": "$TODAY",
      "last_validated": "$TODAY",
      "validation_count": 0,
      "confidence_score": 1.0
    }
  ]
}
RULES
    echo "[OK] Created rules.json with 3 starter rules (v1.4.0 schema)"
else
    RULES=$(cat "$LEARNING_DIR/rules.json" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('rules',[])))" 2>/dev/null || echo "?")
    echo "[SKIP] rules.json already exists ($RULES rules)"
fi

# Initialize lessons.json (empty structure)
if [ ! -f "$LEARNING_DIR/lessons.json" ]; then
    TODAY=$(date +%Y-%m-%d)
    cat > "$LEARNING_DIR/lessons.json" << LESSONS
{
  "version": "1.4.0",
  "updated": "$TODAY",
  "lessons": []
}
LESSONS
    echo "[OK] Created lessons.json (empty)"
else
    LESSONS=$(cat "$LEARNING_DIR/lessons.json" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('lessons',[])))" 2>/dev/null || echo "?")
    echo "[SKIP] lessons.json already exists ($LESSONS lessons)"
fi

# Initialize metrics.json
if [ ! -f "$LEARNING_DIR/metrics.json" ]; then
    TODAY=$(date +%Y-%m-%d)
    cat > "$LEARNING_DIR/metrics.json" << METRICS
{
  "version": "1.4.0",
  "started": "$TODAY",
  "weekly": [],
  "totals": {
    "events": 0,
    "lessons": 0,
    "rules": 3,
    "total_violations": 0,
    "total_saves": 0
  }
}
METRICS
    echo "[OK] Created metrics.json"
else
    echo "[SKIP] metrics.json already exists"
fi

# Initialize pre-action checklist
if [ ! -f "$LEARNING_DIR/pre-action-checklist.md" ]; then
    cat > "$LEARNING_DIR/pre-action-checklist.md" << 'CHECKLIST'
# Pre-Action Intelligence Checklist
_Read at session boot. Check relevant sections before acting._

## HOW TO USE THIS SYSTEM
- **Before risky actions:** Check the relevant section below
- **After mistakes or debugging:** Append an event to `memory/learning/events.jsonl`
- **After proven lessons:** Add/update rules in `memory/learning/rules.json`
- **Event format:** `{"ts":"ISO","type":"mistake|success|debug_session","category":"...","tags":[...],"problem":"...","solution":"...","confidence":"testing|proven","source":"..."}`

## Account / Credential Operations
Before creating or authenticating ANY account:
1. Search your memory files for the service name
2. Check your credential manager for existing entries
3. Check existing cron jobs or config for API keys
**If ANY source shows existing account, STOP.**

## Shell Commands
- Test commands on small inputs first before running on large datasets
- Save working commands to your events log for reuse
- When a command fails, log the error and solution

## External Communications
- Verify recipient before sending
- Double-check content for accuracy
- Log what was sent for future reference

## Rule Confidence Decay (v1.4.0)
Rules lose confidence over time if not validated:
- Check `confidence_score` in rules.json before relying on old rules
- Rules with confidence < 0.5 are flagged for review
- Run `bash confidence-decay.sh` weekly to update scores

## Cross-Agent Rule Sharing (v1.4.0)
- Export rules: `bash export-rules.sh --output rules-export.json`
- Import rules: `bash import-rules.sh rules-export.json`
- Conflicts are detected automatically during import
CHECKLIST
    echo "[OK] Created pre-action-checklist.md"
else
    echo "[SKIP] pre-action-checklist.md already exists"
fi

# Initialize BOOT.md
if [ ! -f "$LEARNING_DIR/BOOT.md" ]; then
    cat > "$LEARNING_DIR/BOOT.md" << 'BOOT'
# Learning Loop - Quick Boot Reference

You have a structured self-improvement system. This file is a quick reference.

## Critical Rules
Read `rules.json` for full details. Key rules:
1. Write important facts to file IMMEDIATELY
2. Save findings every 2 significant operations
3. Write learning events after debugging sessions

## After Actions
- Debugged something? Append to `events.jsonl`
- Made a mistake? Update `rules.json`
- Learned something new? Update relevant files AND events.jsonl

## File Locations
- Events: `memory/learning/events.jsonl` (append-only JSONL)
- Rules: `memory/learning/rules.json` (read at boot)
- Lessons: `memory/learning/lessons.json` (intermediate tier)
- Checklist: `memory/learning/pre-action-checklist.md` (check before risky actions)
- Metrics: `memory/learning/metrics.json` (weekly tracking)

## v1.4.0 New Features
- **Confidence Decay:** Rules lose confidence over time. Run `confidence-decay.sh` weekly.
- **Cross-Agent Sharing:** Export/import rules with other agents.
- **Anomaly Detection:** Automatic spike detection in event patterns.
- **Parse Error Logging:** JSON errors are logged to `parse-errors.jsonl`.

## Quick Commands
```bash
# Check rule confidence
bash confidence-decay.sh

# Export rules for sharing
bash export-rules.sh --output my-rules.json

# Import rules from another agent
bash import-rules.sh other-agent-rules.json --dry-run  # preview first
bash import-rules.sh other-agent-rules.json            # actually import
```
BOOT
    echo "[OK] Created BOOT.md"
else
    echo "[SKIP] BOOT.md already exists"
fi

echo ""
echo "========================================="
echo "  Learning Loop initialized!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Add 'Read memory/learning/rules.json' to your boot sequence"
echo "  2. Add 'Read memory/learning/BOOT.md' for quick reference"
echo "  3. Start capturing events after debugging or mistakes"
echo "  4. Set up daily/weekly cron jobs for automated extraction"
echo "  5. Run 'bash confidence-decay.sh' weekly to update confidence scores"
echo ""
echo "Files created in: $LEARNING_DIR"
ls -la "$LEARNING_DIR"
