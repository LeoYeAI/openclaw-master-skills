#!/bin/bash
# Learning Loop - Active Feedback Signal Detector
# Scans a message for feedback signals and auto-captures events
# Detects: positive, negative, corrections, feature requests, knowledge gaps
# Usage: bash feedback-detector.sh [workspace-dir] "message text"
# Or:    echo "message text" | bash feedback-detector.sh [workspace-dir]
# Returns: 0 on success, 1 on configuration error
# Schedule: Per-message (inline)
# Dependencies: feedback-signals.json (optional), events.jsonl
# Side Effects: Appends to events.jsonl (with file locking), writes to parse-errors.jsonl

set -o pipefail

SCRIPT_NAME="feedback-detector.sh"
WORKSPACE="${1:-$(pwd)}"
MESSAGE="${2:-$(cat)}"
LEARNING_DIR="$WORKSPACE/memory/learning"
EVENTS_FILE="$LEARNING_DIR/events.jsonl"
SIGNALS_FILE="$(cd "$(dirname "$0")" && pwd)/feedback-signals.json"

# ============================================================================
# INPUT VALIDATION
# ============================================================================

# Check workspace exists and is writable
if [[ ! -d "$WORKSPACE" ]]; then
    echo "ERROR: Workspace does not exist: $WORKSPACE"
    exit 1
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

# Check events file exists or create it
if [[ ! -f "$EVENTS_FILE" ]]; then
    mkdir -p "$LEARNING_DIR"
    touch "$EVENTS_FILE"
fi

# ============================================================================
# FILE LOCKING SETUP
# ============================================================================

LOCK_FILE="$LEARNING_DIR/.lockfile"
exec 200>"$LOCK_FILE"
if ! flock -w 10 200; then
    echo "ERROR: Could not acquire lock on $LOCK_FILE"
    exit 3
fi

python3 - "$MESSAGE" "$EVENTS_FILE" "$SIGNALS_FILE" "$LEARNING_DIR" "$SCRIPT_NAME" << 'PYTHON'
import json, sys, fcntl, os
from datetime import datetime, timezone

message = sys.argv[1].lower().strip() if len(sys.argv) > 1 else ""
events_file = sys.argv[2] if len(sys.argv) > 2 else ""
signals_file = sys.argv[3] if len(sys.argv) > 3 else ""
learning_dir = sys.argv[4] if len(sys.argv) > 4 else ""
script_name = sys.argv[5] if len(sys.argv) > 5 else ""

if not message:
    sys.exit(0)

# Load signal patterns
config = None
if signals_file:
    try:
        with open(signals_file) as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Log parse error if signals file is corrupted
        if isinstance(e, json.JSONDecodeError) and learning_dir:
            error_entry = {
                "ts": datetime.now().isoformat(),
                "error": f"Failed to parse feedback-signals.json: {e}",
                "line": "",
                "script": script_name
            }
            try:
                errors_file = os.path.join(learning_dir, "parse-errors.jsonl")
                with open(errors_file, "a") as ef:
                    ef.write(json.dumps(error_entry) + "\n")
            except:
                pass
        pass

if not config:
    # Inline fallback signals
    config = {
        "signals": {
            "positive": {
                "strong": ["perfect", "exactly", "love it", "nailed it", "thats exactly", "hell yes", "this is great"],
                "moderate": ["nice", "good job", "works", "solid", "right on"],
                "subtle": ["ok lets", "yeah", "yep", "keep going"]
            },
            "negative": {
                "strong": ["unacceptable", "wrong", "no thats not", "i already told you", "you already know"],
                "moderate": ["not what i meant", "thats not right", "try again", "nope", "why did you"],
                "subtle": ["hmm", "not quite", "close but"]
            },
            "correction": {
                "direct": ["dont do", "stop doing", "never", "always", "from now on", "actually it should be"],
                "preference": ["i prefer", "i like", "i want", "lets do", "switch to"],
                "priority": ["this is more important", "focus on", "priority", "first do"]
            },
            "feature_request": {
                "explicit": ["can you also", "i wish you could", "is there a way to", "why cant you"],
                "implicit": ["that would be useful", "we need that", "add that", "build that"]
            },
            "knowledge_gap": {
                "patterns": ["you didnt know", "thats not what that means", "thats outdated", "thats old info"]
            }
        },
        "scoring": {
            "strong_positive": 1.0, "moderate_positive": 0.6, "subtle_positive": 0.3,
            "strong_negative": -1.0, "moderate_negative": -0.6, "subtle_negative": -0.3,
            "direct_correction": -0.5, "preference": 0.0, "priority": 0.0,
            "feature_request_explicit": 0.0, "feature_request_implicit": 0.0,
            "knowledge_gap": -0.3
        },
        "auto_capture_threshold": {"positive": 0.8, "negative": -0.5}
    }

signals = config.get("signals", {})
scoring = config.get("scoring", {})
thresholds = config.get("auto_capture_threshold", {"positive": 0.8, "negative": -0.5})

# Scan message
matches = []
total_score = 0.0

# Check positive/negative signals
for sentiment in ["positive", "negative"]:
    for intensity in ["strong", "moderate", "subtle"]:
        for pattern in signals.get(sentiment, {}).get(intensity, []):
            if pattern in message:
                score_key = f"{intensity}_{sentiment}"
                score = scoring.get(score_key, 0)
                matches.append({"pattern": pattern, "sentiment": sentiment, "intensity": intensity, "score": score})
                total_score += score

# Check corrections (legacy "directive" key or new "correction" key)
correction_signals = signals.get("correction", signals.get("directive", {}))
correction_matches = []
for ctype in ["direct", "correction", "preference", "priority"]:
    for pattern in correction_signals.get(ctype, []):
        if pattern in message:
            score_key = f"{ctype}_correction" if ctype == "direct" else ctype
            score = scoring.get(score_key, scoring.get("direct_correction", -0.5))
            correction_matches.append({"pattern": pattern, "type": ctype, "score": score})

# Check feature requests
feature_matches = []
for ftype in ["explicit", "implicit"]:
    for pattern in signals.get("feature_request", {}).get(ftype, []):
        if pattern in message:
            score_key = f"feature_request_{ftype}"
            feature_matches.append({"pattern": pattern, "type": ftype})

# Check knowledge gaps
gap_matches = []
for pattern in signals.get("knowledge_gap", {}).get("patterns", []):
    if pattern in message:
        gap_matches.append({"pattern": pattern})

# Output results
result = {
    "message_preview": message[:100],
    "signal_score": round(total_score, 2),
    "matches": matches,
    "corrections": correction_matches,
    "feature_requests": feature_matches,
    "knowledge_gaps": gap_matches,
    "should_capture": False,
    "capture_reason": None
}

# Determine if we should auto-capture
sentiment = "neutral"
event_type = "feedback"

if total_score >= thresholds["positive"]:
    result["should_capture"] = True
    result["capture_reason"] = f"Strong positive signal ({total_score})"
    sentiment = "positive"
elif total_score <= thresholds["negative"]:
    result["should_capture"] = True
    result["capture_reason"] = f"Negative signal ({total_score})"
    sentiment = "negative"
elif correction_matches:
    result["should_capture"] = True
    result["capture_reason"] = f"Correction detected: {correction_matches[0]['type']}"
    sentiment = "directive"
elif feature_matches:
    result["should_capture"] = True
    result["capture_reason"] = f"Feature request: {feature_matches[0]['pattern']}"
    sentiment = "feature_request"
    event_type = "discovery"
elif gap_matches:
    result["should_capture"] = True
    result["capture_reason"] = f"Knowledge gap: {gap_matches[0]['pattern']}"
    sentiment = "knowledge_gap"

print(json.dumps(result, indent=2))

# Auto-capture if threshold crossed
if result["should_capture"] and events_file:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build tags
    tags = ["feedback", sentiment, "auto-detected"]
    if feature_matches:
        tags.append("feature-request")
    if gap_matches:
        tags.append("knowledge-gap")

    event = {
        "ts": ts,
        "type": event_type,
        "category": "communication",
        "tags": tags,
        "sentiment": sentiment,
        "signal_score": total_score,
        "problem": None if sentiment == "positive" else f"Signal: {result['capture_reason']}",
        "solution": message[:200],
        "confidence": "auto",
        "source": "feedback-detector",
        "greg_feedback": message[:300]
    }

    try:
        # Append with file locking
        with open(events_file, "a") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.write(json.dumps(event) + "\n")
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        print(f"\n>>> EVENT CAPTURED: {sentiment} {event_type} (score: {total_score})", file=sys.stderr)
    except Exception as e:
        print(f"\n>>> CAPTURE FAILED: {e}", file=sys.stderr)

PYTHON

exit_code=$?

# Release lock
exec 200>&-

exit $exit_code
