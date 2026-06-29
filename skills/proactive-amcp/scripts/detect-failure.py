#!/usr/bin/env python3
"""detect-failure.py - Self-detect trigger for auto-capturing Problems.

Scans agent text for failure patterns, auto-creates Problems via learning.py.
Debounces duplicates within configurable window.

Usage:
  detect-failure.py --input <file_or_stdin>
  detect-failure.py --scan-sessions
  echo "ERROR 401 Unauthorized" | detect-failure.py --input -

Environment:
  CONFIG_FILE, LEARNING_DIR, SESSION_DIR (all overridable)
"""
import argparse, json, os, re, subprocess, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

CONFIG_FILE = os.environ.get("CONFIG_FILE", os.path.expanduser("~/.amcp/config.json"))

def _get_workspace():
    try:
        with open(os.path.expanduser("~/.openclaw/openclaw.json")) as f:
            return os.path.expanduser(json.load(f).get("agents",{}).get("defaults",{}).get("workspace","~/.openclaw/workspace"))
    except (IOError, json.JSONDecodeError):
        return os.path.expanduser("~/.openclaw/workspace")

def _get_dir(env_key, fallback):
    v = os.environ.get(env_key)
    return os.path.expanduser(v) if v else fallback

LEARNING_DIR = _get_dir("LEARNING_DIR", os.path.join(_get_workspace(), "memory", "learning"))
SESSION_DIR = _get_dir("SESSION_DIR", os.path.expanduser("~/.openclaw/agents/main/sessions"))
DETECTIONS_LOG = os.path.join(LEARNING_DIR, "detections.log")

def load_config():
    defaults = {"enabled": True, "debounceHours": 24}
    try:
        with open(CONFIG_FILE) as f:
            sd = json.load(f).get("learning",{}).get("selfDetect",{})
        return {"enabled": sd.get("enabled", True), "debounceHours": sd.get("debounceHours", 24)}
    except (IOError, json.JSONDecodeError):
        return defaults

# Failure patterns: (compiled_regex, category, extract_fn)
FAILURE_PATTERNS = [
    (re.compile(r"\b(HTTP[/ ]?)?([45]\d{2})\b.*?(Unauthorized|Forbidden|Not Found|Internal Server Error|Bad Gateway|Service Unavailable)", re.I),
     "api_error", lambda m: f"HTTP {m.group(2)} {m.group(3)}"),
    (re.compile(r"\b(?:status[_ ]?code|HTTP|error)[:\s=]+([45]\d{2})\b", re.I),
     "api_error", lambda m: f"HTTP {m.group(1)} error"),
    (re.compile(r"I\s+don'?t\s+know\s+how\s+to\b(.{0,80})", re.I),
     "knowledge_gap", lambda m: f"Agent doesn't know how to {m.group(1).strip()}"),
    (re.compile(r"I\s+need\s+help\s+with\b(.{0,80})", re.I),
     "knowledge_gap", lambda m: f"Agent needs help with {m.group(1).strip()}"),
    (re.compile(r"I'?m\s+(?:not\s+sure|unable\s+to|struggling\s+to)\b(.{0,80})", re.I),
     "knowledge_gap", lambda m: f"Agent uncertain: {m.group(1).strip()}"),
    (re.compile(r"(?:FATAL|CRITICAL|ERROR):\s*(.{5,120})", re.I),
     "error_signal", lambda m: m.group(0).strip()[:120]),
    (re.compile(r"(?:authentication|auth|token|api.?key)\s+(?:failed|expired|invalid|rejected|revoked)", re.I),
     "auth_failure", lambda m: m.group(0).strip()[:120]),
]

def scan_text(text):
    """Scan text for failure patterns. Returns list of detections."""
    detections, seen = [], set()
    for regex, cat, extract in FAILURE_PATTERNS:
        if cat in seen:
            continue
        match = regex.search(text)
        if match:
            seen.add(cat)
            desc = extract(match).rstrip(" .,;:")
            detections.append({"category": cat, "description": desc, "matched_text": match.group(0)[:200]})
    return detections

def is_debounced(description, debounce_hours):
    """Check if similar self-detect problem exists within debounce window."""
    problems_file = os.path.join(LEARNING_DIR, "problems.jsonl")
    if not os.path.isfile(problems_file):
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(hours=debounce_hours)
    desc_tokens = set(re.findall(r'\b\w{3,}\b', description.lower()))
    if not desc_tokens:
        return False
    with open(problems_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("op") != "create" or r.get("source") != "self-detect":
                continue
            try:
                if datetime.fromisoformat(r.get("created","")) < cutoff:
                    continue
            except (ValueError, TypeError):
                continue
            existing_tokens = set(re.findall(r'\b\w{3,}\b', r.get("description","").lower()))
            if existing_tokens:
                overlap = len(desc_tokens & existing_tokens) / len(desc_tokens | existing_tokens)
                if overlap > 0.5:
                    return True
    return False

def log_detection(detection, problem_id, debounced):
    os.makedirs(os.path.dirname(DETECTIONS_LOG), exist_ok=True)
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(), **{k: detection[k] for k in ("category","description","matched_text")}, "problem_id": problem_id, "debounced": debounced}
    with open(DETECTIONS_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def create_problem_via_cli(description):
    """Create a Problem using learning.py."""
    learning_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "learning.py")
    env = {**os.environ, "LEARNING_DIR": LEARNING_DIR}
    result = subprocess.run([sys.executable, learning_py, "problem", "create", "--description", description, "--source", "self-detect"], capture_output=True, text=True, env=env)
    if result.returncode == 0:
        try:
            return json.loads(result.stdout).get("id", "")
        except json.JSONDecodeError:
            return ""
    print(f"WARN: Failed to create problem: {result.stderr}", file=sys.stderr)
    return ""

def read_input(path):
    if path == "-":
        return sys.stdin.read()
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return f.read()

def scan_recent_sessions():
    """Scan session transcripts modified in last 24h."""
    if not os.path.isdir(SESSION_DIR):
        return ""
    texts, now = [], datetime.now(timezone.utc)
    for entry in sorted(Path(SESSION_DIR).iterdir(), reverse=True):
        if not entry.is_file() or entry.suffix != ".jsonl":
            continue
        if (now - datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc)).total_seconds() > 86400:
            continue
        try:
            with open(entry) as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        c = json.loads(line).get("content","")
                        if isinstance(c, str): texts.append(c)
                    except json.JSONDecodeError: continue
        except IOError: continue
        if len(texts) > 5000: break
    return "\n".join(texts)

def main():
    parser = argparse.ArgumentParser(description="Detect failure patterns and auto-create Problems")
    parser.add_argument("--input", "-i", help="Input file (use - for stdin)")
    parser.add_argument("--scan-sessions", action="store_true", help="Scan recent session transcripts")
    parser.add_argument("--dry-run", action="store_true", help="Show detections without creating Problems")
    args = parser.parse_args()

    config = load_config()
    if not config["enabled"]:
        print("Self-detect disabled via config"); return

    if args.input:
        text = read_input(args.input)
    elif args.scan_sessions:
        text = scan_recent_sessions()
        if not text: print("No recent sessions to scan"); return
    else:
        parser.print_help(); sys.exit(1)

    detections = scan_text(text)
    if not detections:
        print("No failure patterns detected"); return

    debounce_hours = config["debounceHours"]
    created, debounced_count = 0, 0
    for det in detections:
        if is_debounced(det["description"], debounce_hours):
            debounced_count += 1
            log_detection(det, problem_id="", debounced=True)
            if not args.dry_run:
                print(f"  [DEBOUNCED] {det['category']}: {det['description']}")
            continue
        if args.dry_run:
            print(f"  [WOULD CREATE] {det['category']}: {det['description']}")
            log_detection(det, problem_id="dry-run", debounced=False)
            continue
        pid = create_problem_via_cli(det["description"])
        if pid:
            created += 1
            log_detection(det, problem_id=pid, debounced=False)
            print(f"  [CREATED] {pid}: {det['description']}")
        else:
            log_detection(det, problem_id="failed", debounced=False)
    print(f"\nDetections: {len(detections)}, Created: {created}, Debounced: {debounce_hours}h: {debounced_count}")

if __name__ == "__main__":
    main()
