#!/bin/bash
# snapshot-manager.sh — Save, list, and compare checkup data
# v4.0: Data stored in skill's data/checkups/ directory (was ~/.openclaw/reports/snapshots/)
# Usage:
#   snapshot-manager.sh save <data-dir>               — Save raw collection data as a checkup
#   snapshot-manager.sh history [--limit N]            — List past checkups
#   snapshot-manager.sh compare <date1> <date2>        — Compare two checkups
# Timeout: 10s | Compatible: macOS (darwin) + Linux
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CHECKUP_DIR="${SKILL_DIR}/data/checkups"
RETAIN_DAYS="${RETAIN_DAYS:-90}"

usage() {
  cat <<'EOF'
Usage:
  snapshot-manager.sh save <data-dir>               Save a checkup (data-dir contains *.json files)
  snapshot-manager.sh history [--limit N]            List past checkups with status
  snapshot-manager.sh compare <date1> <date2>        Compare two checkups side by side

Data is stored in: data/checkups/YYYY-MM-DD-HHmmss/
EOF
  exit 1
}

# --- save mode ---
do_save() {
  local source_dir="$1"
  shift

  # Parse optional flags
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --retain-days) RETAIN_DAYS="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  if [[ ! -d "$source_dir" ]]; then
    echo '{"error":"Source directory not found: '"$source_dir"'"}' >&2
    exit 1
  fi

  local timestamp
  timestamp=$(date +%Y-%m-%d-%H%M%S)
  local checkup_dir="$CHECKUP_DIR/$timestamp"
  mkdir -p "$checkup_dir"

  # Copy all JSON files from source directory
  for f in "$source_dir"/*.json; do
    [[ -f "$f" ]] && cp "$f" "$checkup_dir/"
  done

  # Update latest symlink
  rm -f "$CHECKUP_DIR/latest"
  ln -sf "$timestamp" "$CHECKUP_DIR/latest"

  # Prune old checkups beyond retain days
  if command -v find >/dev/null 2>&1; then
    find "$CHECKUP_DIR" -maxdepth 1 -type d -mtime +"$RETAIN_DAYS" -not -name "checkups" -exec rm -rf {} + 2>/dev/null || true
  fi

  # Output result
  node -e '
    const fs = require("fs");
    const dir = process.argv[1];
    const id = process.argv[2];
    const retainDays = parseInt(process.argv[3]);

    // Read analysis.json if present for status
    let status = "unknown";
    let summary = {};
    const analysisPath = dir + "/analysis.json";
    if (fs.existsSync(analysisPath)) {
      try {
        const analysis = JSON.parse(fs.readFileSync(analysisPath, "utf8"));
        status = analysis.overall_status || "unknown";
        summary = analysis.summary || {};
      } catch {}
    }

    console.log(JSON.stringify({
      status: "saved",
      checkup_id: id,
      path: dir,
      overall_status: status,
      summary: summary,
      retain_days: retainDays
    }, null, 2));
  ' "$checkup_dir" "$timestamp" "$RETAIN_DAYS"
}

# --- history mode ---
do_history() {
  local limit=20

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit) limit="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  if [[ ! -d "$CHECKUP_DIR" ]]; then
    echo '{"checkups":[],"total":0}'
    exit 0
  fi

  node -e '
    const fs = require("fs");
    const path = require("path");
    const dir = process.argv[1];
    const limit = parseInt(process.argv[2]);

    const entries = fs.readdirSync(dir)
      .filter(d => {
        const fp = path.join(dir, d);
        return fs.statSync(fp).isDirectory() && /^\d{4}-\d{2}-\d{2}-\d{6}$/.test(d);
      })
      .sort()
      .reverse()
      .slice(0, limit);

    const checkups = entries.map(d => {
      const analysisPath = path.join(dir, d, "analysis.json");
      if (fs.existsSync(analysisPath)) {
        try {
          const analysis = JSON.parse(fs.readFileSync(analysisPath, "utf8"));
          return {
            checkup_id: d,
            timestamp: analysis.timestamp || d,
            overall_status: analysis.overall_status || "unknown",
            summary: analysis.summary || {},
            dimensions: Object.fromEntries(
              (analysis.dimensions || []).map(dim => [dim.label_en || dim.label, dim.status])
            )
          };
        } catch {}
      }
      return { checkup_id: d, error: "analysis.json not found or invalid" };
    });

    console.log(JSON.stringify({ checkups, total: checkups.length }, null, 2));
  ' "$CHECKUP_DIR" "$limit"
}

# --- compare mode ---
do_compare() {
  local date1="$1"
  local date2="$2"

  # Find matching checkup directories
  local dir1 dir2
  dir1=$(find "$CHECKUP_DIR" -maxdepth 1 -type d -name "${date1}*" | sort | tail -1)
  dir2=$(find "$CHECKUP_DIR" -maxdepth 1 -type d -name "${date2}*" | sort | tail -1)

  if [[ -z "$dir1" ]]; then
    echo '{"error":"No checkup found matching '"$date1"'"}' >&2
    exit 1
  fi
  if [[ -z "$dir2" ]]; then
    echo '{"error":"No checkup found matching '"$date2"'"}' >&2
    exit 1
  fi

  node -e '
    const fs = require("fs");
    const path = require("path");

    function loadAnalysis(dir) {
      const fp = path.join(dir, "analysis.json");
      if (fs.existsSync(fp)) return JSON.parse(fs.readFileSync(fp, "utf8"));
      return null;
    }

    const dir1 = process.argv[1];
    const dir2 = process.argv[2];
    const a1 = loadAnalysis(dir1);
    const a2 = loadAnalysis(dir2);

    if (!a1 || !a2) {
      console.log(JSON.stringify({ error: "Cannot load analysis.json from one or both checkups" }));
      process.exit(1);
    }

    const result = {
      comparison: {
        older: { checkup_id: path.basename(dir1), timestamp: a1.timestamp },
        newer: { checkup_id: path.basename(dir2), timestamp: a2.timestamp }
      },
      overall: {
        older_status: a1.overall_status,
        newer_status: a2.overall_status,
        older_summary: a1.summary,
        newer_summary: a2.summary
      },
      dimensions: {}
    };

    // Compare per-dimension
    const dims1 = {};
    const dims2 = {};
    for (const d of (a1.dimensions || [])) dims1[d.label_en || d.label] = d;
    for (const d of (a2.dimensions || [])) dims2[d.label_en || d.label] = d;

    const allDims = new Set([...Object.keys(dims1), ...Object.keys(dims2)]);
    for (const dim of allDims) {
      const s1 = dims1[dim]?.status || "unknown";
      const s2 = dims2[dim]?.status || "unknown";
      result.dimensions[dim] = {
        older: s1,
        newer: s2,
        changed: s1 !== s2,
        improved: (s1 === "error" && s2 !== "error") || (s1 === "warning" && s2 === "pass"),
        degraded: (s1 === "pass" && s2 !== "pass") || (s1 === "warning" && s2 === "error")
      };
    }

    // Issue comparison
    const issues1 = [];
    const issues2 = [];
    for (const d of (a1.dimensions || [])) for (const i of (d.issues || [])) issues1.push(i.msg);
    for (const d of (a2.dimensions || [])) for (const i of (d.issues || [])) issues2.push(i.msg);

    result.issues = {
      resolved: issues1.filter(m => !issues2.includes(m)),
      new: issues2.filter(m => !issues1.includes(m)),
      persistent: issues1.filter(m => issues2.includes(m)),
      older_total: issues1.length,
      newer_total: issues2.length
    };

    console.log(JSON.stringify(result, null, 2));
  ' "$dir1" "$dir2"
}

# --- main ---
[[ $# -lt 1 ]] && usage

MODE="$1"; shift

case "$MODE" in
  save)     [[ $# -lt 1 ]] && usage; do_save "$@" ;;
  history)  do_history "$@" ;;
  compare)  [[ $# -lt 2 ]] && usage; do_compare "$@" ;;
  *)        usage ;;
esac
