#!/usr/bin/env bash
# build.sh — Build engine for specclaw: setup, commit, finalize
# Part of the specclaw skill. Bash + git + coreutils only.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── Helpers ──────────────────────────────────────────────────────────────────

usage() {
  cat <<'EOF'
Usage: build.sh <subcommand> [options]

Subcommands:
  setup    <specclaw_dir> <change_name>
           Read config.yaml, create git branch if branch-per-change, output config JSON.

  commit   <specclaw_dir> <change_name> <task_id> "<title>" [files...]
           Stage listed files and commit with specclaw prefix.

  finalize <specclaw_dir> <change_name>
           Run configured checks, merge branch if branch-per-change, output summary JSON.

Options:
  -h, --help   Show this help message
EOF
}

die() { echo "ERROR: $*" >&2; exit 1; }
warn() { echo "WARN: $*" >&2; }

# Read a simple yaml value: yaml_val <file> <dotted.key>
# Handles top-level and one-level nested keys (good enough for config.yaml).
yaml_val() {
  local file="$1" key="$2"
  local section field
  if [[ "$key" == *.* ]]; then
    section="${key%%.*}"
    field="${key#*.}"
  else
    section=""
    field="$key"
  fi

  local in_section=false value=""
  while IFS= read -r line; do
    # skip comments / blank
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// /}" ]] && continue

    if [[ -z "$section" ]]; then
      # top-level key
      if [[ "$line" =~ ^${field}:[[:space:]]*(.*) ]]; then
        value="${BASH_REMATCH[1]}"
        break
      fi
    else
      # detect section header (no leading whitespace)
      if [[ "$line" =~ ^[a-zA-Z_] ]]; then
        if [[ "$line" =~ ^${section}: ]]; then
          in_section=true
        else
          in_section=false
        fi
        continue
      fi
      if $in_section; then
        # indented key
        if [[ "$line" =~ ^[[:space:]]+${field}:[[:space:]]*(.*) ]]; then
          value="${BASH_REMATCH[1]}"
          break
        fi
      fi
    fi
  done < "$file"

  # strip surrounding quotes
  value="${value#\"}"
  value="${value%\"}"
  value="${value#\'}"
  value="${value%\'}"
  echo "$value"
}

# JSON-escape a string value
json_str() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  printf '"%s"' "$s"
}

json_bool() {
  case "${1,,}" in
    true|yes|1) echo "true" ;;
    *) echo "false" ;;
  esac
}

# ─── setup ────────────────────────────────────────────────────────────────────

cmd_setup() {
  [[ $# -ge 2 ]] || die "setup requires: <specclaw_dir> <change_name>"
  local specclaw_dir="$1" change_name="$2"
  local config="$specclaw_dir/config.yaml"
  [[ -f "$config" ]] || die "Config not found: $config"

  # Extract values (with defaults)
  local project_name; project_name="$(yaml_val "$config" "project.name")"
  local git_strategy; git_strategy="$(yaml_val "$config" "git.strategy")"
  local branch_prefix; branch_prefix="$(yaml_val "$config" "git.branch_prefix")"
  local auto_commit; auto_commit="$(yaml_val "$config" "git.auto_commit")"
  local commit_prefix; commit_prefix="$(yaml_val "$config" "git.commit_prefix")"
  local test_command; test_command="$(yaml_val "$config" "build.test_command")"
  local lint_command; lint_command="$(yaml_val "$config" "build.lint_command")"
  local build_command; build_command="$(yaml_val "$config" "build.build_command")"
  local parallel_tasks; parallel_tasks="$(yaml_val "$config" "build.parallel_tasks")"
  local timeout_seconds; timeout_seconds="$(yaml_val "$config" "build.timeout_seconds")"
  local coding_model; coding_model="$(yaml_val "$config" "models.coding")"

  # Defaults
  git_strategy="${git_strategy:-branch-per-change}"
  branch_prefix="${branch_prefix:-specclaw/}"
  auto_commit="${auto_commit:-true}"
  commit_prefix="${commit_prefix:-specclaw}"
  parallel_tasks="${parallel_tasks:-3}"
  timeout_seconds="${timeout_seconds:-300}"

  local branch_name="${branch_prefix}${change_name}"
  local branch_existed=false

  # Git branch handling
  if [[ "$git_strategy" == "branch-per-change" ]]; then
    if git rev-parse --verify "$branch_name" >/dev/null 2>&1; then
      # Branch exists — resume case
      branch_existed=true
      warn "Branch '$branch_name' already exists — resuming"
      git checkout "$branch_name" 2>/dev/null || git switch "$branch_name"
    else
      # Create new branch
      git checkout -b "$branch_name" 2>/dev/null || git switch -c "$branch_name"
    fi
  fi

  # Output JSON
  cat <<ENDJSON
{
  "project_name": $(json_str "$project_name"),
  "git_strategy": $(json_str "$git_strategy"),
  "branch_prefix": $(json_str "$branch_prefix"),
  "branch_name": $(json_str "$branch_name"),
  "branch_existed": $branch_existed,
  "auto_commit": $(json_bool "$auto_commit"),
  "commit_prefix": $(json_str "$commit_prefix"),
  "test_command": $(json_str "$test_command"),
  "lint_command": $(json_str "$lint_command"),
  "build_command": $(json_str "$build_command"),
  "parallel_tasks": ${parallel_tasks},
  "timeout_seconds": ${timeout_seconds},
  "coding_model": $(json_str "$coding_model")
}
ENDJSON
}

# ─── commit ───────────────────────────────────────────────────────────────────

cmd_commit() {
  [[ $# -ge 4 ]] || die "commit requires: <specclaw_dir> <change_name> <task_id> <title> [files...]"
  local specclaw_dir="$1" change_name="$2" task_id="$3" title="$4"
  shift 4
  local files=("$@")

  local config="$specclaw_dir/config.yaml"
  [[ -f "$config" ]] || die "Config not found: $config"

  local auto_commit; auto_commit="$(yaml_val "$config" "git.auto_commit")"
  local commit_prefix; commit_prefix="$(yaml_val "$config" "git.commit_prefix")"
  auto_commit="${auto_commit:-true}"
  commit_prefix="${commit_prefix:-specclaw}"

  # Stage files
  if [[ ${#files[@]} -gt 0 ]]; then
    git add -- "${files[@]}"
  else
    warn "No files specified — nothing to stage"
  fi

  # Check if there are staged changes
  if git diff --cached --quiet 2>/dev/null; then
    warn "No changes to commit for $task_id"
    exit 0
  fi

  # Commit (or just stage if auto_commit is off)
  local msg="${commit_prefix}(${change_name}): ${task_id} — ${title}"

  if [[ "$(json_bool "$auto_commit")" == "true" ]]; then
    git commit -m "$msg"
    echo "Committed: $msg"
  else
    warn "auto_commit is false — changes staged but not committed"
    echo "Staged: $msg"
  fi
}

# ─── finalize ─────────────────────────────────────────────────────────────────

cmd_finalize() {
  [[ $# -ge 2 ]] || die "finalize requires: <specclaw_dir> <change_name>"
  local specclaw_dir="$1" change_name="$2"
  local config="$specclaw_dir/config.yaml"
  [[ -f "$config" ]] || die "Config not found: $config"

  local git_strategy; git_strategy="$(yaml_val "$config" "git.strategy")"
  local branch_prefix; branch_prefix="$(yaml_val "$config" "git.branch_prefix")"
  local test_command; test_command="$(yaml_val "$config" "build.test_command")"
  local lint_command; lint_command="$(yaml_val "$config" "build.lint_command")"
  local build_command; build_command="$(yaml_val "$config" "build.build_command")"

  git_strategy="${git_strategy:-branch-per-change}"
  branch_prefix="${branch_prefix:-specclaw/}"

  local tests_passed=true lint_passed=true build_passed=true merged=false
  local errors=()

  # Run test command
  if [[ -n "$test_command" ]]; then
    echo "Running tests: $test_command" >&2
    if ! eval "$test_command" >&2 2>&1; then
      tests_passed=false
      errors+=("Test command failed: $test_command")
    fi
  fi

  # Run lint command
  if [[ -n "$lint_command" ]]; then
    echo "Running lint: $lint_command" >&2
    if ! eval "$lint_command" >&2 2>&1; then
      lint_passed=false
      errors+=("Lint command failed: $lint_command")
    fi
  fi

  # Run build command
  if [[ -n "$build_command" ]]; then
    echo "Running build: $build_command" >&2
    if ! eval "$build_command" >&2 2>&1; then
      build_passed=false
      errors+=("Build command failed: $build_command")
    fi
  fi

  # Merge branch if branch-per-change
  if [[ "$git_strategy" == "branch-per-change" ]]; then
    local branch_name="${branch_prefix}${change_name}"
    local current_branch; current_branch="$(git branch --show-current)"

    # Determine the main branch name
    local main_branch="main"
    if git rev-parse --verify main >/dev/null 2>&1; then
      main_branch="main"
    elif git rev-parse --verify master >/dev/null 2>&1; then
      main_branch="master"
    fi

    if [[ "$current_branch" == "$branch_name" ]]; then
      # Switch to main and merge
      if git checkout "$main_branch" 2>/dev/null; then
        if git merge --no-ff "$branch_name" -m "Merge $branch_name" 2>&1; then
          merged=true
          # Clean up feature branch
          git branch -d "$branch_name" 2>/dev/null || true
        else
          # Merge conflict — abort and go back
          git merge --abort 2>/dev/null || true
          git checkout "$branch_name" 2>/dev/null || true
          errors+=("Merge conflict merging $branch_name into $main_branch — manual resolution required")
        fi
      else
        errors+=("Failed to checkout $main_branch for merge")
      fi
    else
      warn "Not on feature branch ($current_branch != $branch_name) — skipping merge"
      errors+=("Not on expected feature branch; skipping merge")
    fi
  fi

  # Build errors JSON array
  local errors_json="[]"
  if [[ ${#errors[@]} -gt 0 ]]; then
    errors_json="["
    local first=true
    for err in "${errors[@]}"; do
      $first || errors_json+=", "
      first=false
      errors_json+="$(json_str "$err")"
    done
    errors_json+="]"
  fi

  # Output summary JSON
  cat <<ENDJSON
{
  "tests_passed": $tests_passed,
  "lint_passed": $lint_passed,
  "build_passed": $build_passed,
  "merged": $merged,
  "errors": $errors_json
}
ENDJSON
}

# ─── Main dispatch ────────────────────────────────────────────────────────────

[[ $# -gt 0 ]] || { usage; exit 1; }

case "$1" in
  -h|--help) usage; exit 0 ;;
  setup)    shift; cmd_setup "$@" ;;
  commit)   shift; cmd_commit "$@" ;;
  finalize) shift; cmd_finalize "$@" ;;
  *)        die "Unknown subcommand: $1 (try --help)" ;;
esac
