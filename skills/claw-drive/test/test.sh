#!/usr/bin/env bash
# test/test.sh — Functional tests for Claw Drive
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI="$SCRIPT_DIR/../bin/claw-drive"
TEST_DIR=$(mktemp -d)
SRC_DIR=$(mktemp -d)
export CLAW_DRIVE_DIR="$TEST_DIR"
export CLAW_DRIVE_CONFIG_FILE="$TEST_DIR/.config"

passed=0
failed=0

assert() {
  local name="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    echo "  ✅ $name"
    ((passed++)) || true
  else
    echo "  ❌ $name"
    ((failed++)) || true
  fi
}

assert_output() {
  local name="$1"
  local expected="$2"
  shift 2
  local output
  output=$("$@" 2>&1) || true
  if echo "$output" | grep -qi "$expected"; then
    echo "  ✅ $name"
    ((passed++)) || true
  else
    echo "  ❌ $name (expected '$expected' in output)"
    echo "     Got: $output"
    ((failed++)) || true
  fi
}

assert_jq() {
  local name="$1"
  local file="$2"
  local filter="$3"
  local expected="$4"
  local result
  result=$(jq -r "$filter" "$file" 2>/dev/null) || true
  if [[ "$result" == "$expected" ]]; then
    echo "  ✅ $name"
    ((passed++)) || true
  else
    echo "  ❌ $name (expected '$expected', got '$result')"
    ((failed++)) || true
  fi
}

cleanup() {
  rm -rf "$TEST_DIR" "$SRC_DIR"
}
trap cleanup EXIT

echo "🧪 Claw Drive Tests (dir: $TEST_DIR)"
echo ""

# --- Version & Help ---
echo "Commands:"
assert "version" bash "$CLI" version
assert "help" bash "$CLI" help

# --- Init ---
echo ""
echo "Init:"
assert "init creates directories" bash "$CLI" init
assert "INDEX.jsonl exists" test -f "$TEST_DIR/INDEX.jsonl"
assert ".hashes exists" test -f "$TEST_DIR/.hashes"
assert "documents/ exists" test -d "$TEST_DIR/documents"
assert "finance/ exists" test -d "$TEST_DIR/finance"
assert "identity/ exists" test -d "$TEST_DIR/identity"
assert "misc/ exists" test -d "$TEST_DIR/misc"

# --- Store ---
echo ""
echo "Store:"
echo "test content" > "$SRC_DIR/testfile.txt"
assert "store a file" bash "$CLI" store "$SRC_DIR/testfile.txt" \
  --category documents --desc "Test document for unit tests" --tags "test, document" --source manual
assert "file copied to category" test -f "$TEST_DIR/documents/testfile.txt"

# Verify JSONL structure
assert_jq "index has path" "$TEST_DIR/INDEX.jsonl" '.path' "documents/testfile.txt"
assert_jq "index has desc" "$TEST_DIR/INDEX.jsonl" '.desc' "Test document for unit tests"
assert_jq "index has tags array" "$TEST_DIR/INDEX.jsonl" '.tags[0]' "test"
assert_jq "index has second tag" "$TEST_DIR/INDEX.jsonl" '.tags[1]' "document"
assert_jq "index has source" "$TEST_DIR/INDEX.jsonl" '.source' "manual"
assert_output "hash in ledger" "testfile" cat "$TEST_DIR/.hashes"

# --- Pipe character in description (the bug that killed INDEX.md) ---
echo ""
echo "Pipe in description:"
echo "pipe test" > "$SRC_DIR/pipefile.txt"
assert "store with | in desc" bash "$CLI" store "$SRC_DIR/pipefile.txt" \
  --category documents --desc "File with | pipe | chars" --tags "test" --source manual
# Verify the pipe chars survived
local_desc=$(jq -r 'select(.path=="documents/pipefile.txt") | .desc' "$TEST_DIR/INDEX.jsonl")
if [[ "$local_desc" == "File with | pipe | chars" ]]; then
  echo "  ✅ pipe characters preserved in desc"
  ((passed++)) || true
else
  echo "  ❌ pipe characters NOT preserved (got: $local_desc)"
  ((failed++)) || true
fi

# --- Dollar sign in description (shell expansion edge case) ---
echo ""
echo "Dollar sign in description:"
echo "dollar test" > "$SRC_DIR/dollarfile.txt"
assert "store with $ in desc (proper single-quote usage)" bash "$CLI" store "$SRC_DIR/dollarfile.txt" \
  --category documents --desc 'Paid $941.39 total' --tags "test" --source manual
local_dollar_desc=$(jq -r 'select(.path=="documents/dollarfile.txt") | .desc' "$TEST_DIR/INDEX.jsonl")
if [[ "$local_dollar_desc" == 'Paid $941.39 total' ]]; then
  echo "  ✅ dollar sign preserved in desc"
  ((passed++)) || true
else
  echo "  ❌ dollar sign NOT preserved (got: $local_dollar_desc)"
  ((failed++)) || true
fi

# --- Dedup ---
echo ""
echo "Dedup:"
assert_output "duplicate rejected" "duplicate" bash "$CLI" store "$SRC_DIR/testfile.txt" \
  --category documents --desc "Duplicate" --tags "dupe" --source manual || true

echo "different content" > "$SRC_DIR/testfile2.txt"
assert "different file stores fine" bash "$CLI" store "$SRC_DIR/testfile2.txt" \
  --category finance --desc "Finance doc" --tags "finance, test" --source email

# dedup path parsing should preserve spaces in existing path
echo "space content" > "$SRC_DIR/space-a.txt"
cp "$SRC_DIR/space-a.txt" "$SRC_DIR/space-b.txt"
assert "store file with spaced name" bash "$CLI" store "$SRC_DIR/space-a.txt" \
  --category documents --name "space name.txt" --desc "spaced path" --tags "test" --source manual
assert_output "duplicate output preserves spaced path" "space name.txt" bash "$CLI" store "$SRC_DIR/space-b.txt" \
  --category documents --desc "dupe" --tags "test" --source manual || true

# --- Store with --name ---
echo ""
echo "Store --name:"
echo "ugly content" > "$SRC_DIR/file_17---8c1ee63d.txt"
assert "store with --name" bash "$CLI" store "$SRC_DIR/file_17---8c1ee63d.txt" \
  --category documents --desc "Clean named file" --tags "test" --name "custom-name.txt"
assert "custom name file exists" test -f "$TEST_DIR/documents/custom-name.txt"

# --- New category (agent creates freely) ---
echo ""
echo "Dynamic categories:"
echo "housing doc" > "$SRC_DIR/lease.txt"
assert "store to new category" bash "$CLI" store "$SRC_DIR/lease.txt" \
  --category housing --desc "Lease agreement" --tags "housing, lease" --source manual
assert "new category dir created" test -d "$TEST_DIR/housing"
assert "file in new category" test -f "$TEST_DIR/housing/lease.txt"

# --- Update ---
echo ""
echo "Update:"
assert "update desc" bash "$CLI" update "documents/testfile.txt" \
  --desc "Updated description for test"
local_updated_desc=$(jq -r 'select(.path=="documents/testfile.txt") | .desc' "$TEST_DIR/INDEX.jsonl")
if [[ "$local_updated_desc" == "Updated description for test" ]]; then
  echo "  ✅ desc updated in index"
  ((passed++)) || true
else
  echo "  ❌ desc not updated (got: $local_updated_desc)"
  ((failed++)) || true
fi

assert "update tags" bash "$CLI" update "documents/testfile.txt" \
  --tags "updated, new-tag"
local_updated_tag=$(jq -r 'select(.path=="documents/testfile.txt") | .tags[0]' "$TEST_DIR/INDEX.jsonl")
if [[ "$local_updated_tag" == "updated" ]]; then
  echo "  ✅ tags updated in index"
  ((passed++)) || true
else
  echo "  ❌ tags not updated (got: $local_updated_tag)"
  ((failed++)) || true
fi

assert_output "update nonexistent fails" "Not found" bash "$CLI" update "nonexistent.txt" --desc "nope"

# --- Move ---
echo ""
echo "Move:"
assert "move to nested category" bash "$CLI" move "documents/testfile.txt" --category "medical/sorbet"
assert "moved file exists" test -f "$TEST_DIR/medical/sorbet/testfile.txt"
assert "source file removed after move" test ! -f "$TEST_DIR/documents/testfile.txt"
local_moved_index=$(jq -r 'select(.path=="medical/sorbet/testfile.txt") | .path' "$TEST_DIR/INDEX.jsonl")
if [[ "$local_moved_index" == "medical/sorbet/testfile.txt" ]]; then
  echo "  ✅ index path updated after move"
  ((passed++)) || true
else
  echo "  ❌ index path not updated after move"
  ((failed++)) || true
fi
if grep -q "medical/sorbet/testfile.txt" "$TEST_DIR/.hashes" 2>/dev/null && ! grep -q "documents/testfile.txt" "$TEST_DIR/.hashes" 2>/dev/null; then
  echo "  ✅ hash ledger path updated after move"
  ((passed++)) || true
else
  echo "  ❌ hash ledger path not updated after move"
  ((failed++)) || true
fi
assert_output "move dry-run previews only" "Dry run" bash "$CLI" move "documents/custom-name.txt" --category "documents" --name "custom-renamed.txt" --dry-run
assert "dry-run does not move file" test -f "$TEST_DIR/documents/custom-name.txt"
assert "move with rename" bash "$CLI" move "documents/custom-name.txt" --category "documents" --name "custom-renamed.txt"
assert "renamed file exists" test -f "$TEST_DIR/documents/custom-renamed.txt"
# fault injection: index_move failure should rollback file move
echo "rollback index unique" > "$SRC_DIR/rollback-index-src.txt"
assert "store rollback test file (index)" bash "$CLI" store "$SRC_DIR/rollback-index-src.txt" \
  --category documents --name "rollback-index.txt" --desc "rollback index" --tags "test" --source manual
assert_output "move index failure injected" "could not update index" env CLAW_DRIVE_TEST_FAIL_INDEX_MOVE=1 bash "$CLI" move "documents/rollback-index.txt" --category "finance"
assert "index-fail rollback kept source" test -f "$TEST_DIR/documents/rollback-index.txt"
assert "index-fail rollback no destination" test ! -f "$TEST_DIR/finance/rollback-index.txt"

# fault injection: dedup_move failure should rollback index+file
echo "rollback dedup unique" > "$SRC_DIR/rollback-dedup-src.txt"
assert "store rollback test file (dedup)" bash "$CLI" store "$SRC_DIR/rollback-dedup-src.txt" \
  --category documents --name "rollback-dedup.txt" --desc "rollback dedup" --tags "test" --source manual
assert_output "move dedup failure injected" "could not update hash ledger" env CLAW_DRIVE_TEST_FAIL_DEDUP_MOVE=1 bash "$CLI" move "documents/rollback-dedup.txt" --category "finance"
assert "dedup-fail rollback kept source" test -f "$TEST_DIR/documents/rollback-dedup.txt"
assert "dedup-fail rollback no destination" test ! -f "$TEST_DIR/finance/rollback-dedup.txt"

assert_output "move nonexistent fails" "Not found" bash "$CLI" move "documents/does-not-exist.txt" --category "misc"
assert_output "move missing category fails" "Usage" bash "$CLI" move "documents/custom-renamed.txt"
assert_output "move path traversal rejected" "must not contain" bash "$CLI" move "../outside.txt" --category "misc"

# --- Delete ---
echo ""
echo "Delete:"
assert_output "delete dry run" "Will delete" bash "$CLI" delete "housing/lease.txt"
assert "file still exists after dry run" test -f "$TEST_DIR/housing/lease.txt"

assert "delete with --force" bash "$CLI" delete "housing/lease.txt" --force
assert "file removed" test ! -f "$TEST_DIR/housing/lease.txt"

# Verify index entry removed
local_deleted=$(jq -r 'select(.path=="housing/lease.txt") | .path' "$TEST_DIR/INDEX.jsonl")
if [[ -z "$local_deleted" ]]; then
  echo "  ✅ index entry removed"
  ((passed++)) || true
else
  echo "  ❌ index entry still present"
  ((failed++)) || true
fi

assert_output "delete nonexistent fails" "Not found" bash "$CLI" delete "nonexistent.txt" --force

# Delete with special characters in filename (regression: jq injection via interpolation)
special_src="$SRC_DIR/report (2025) final.txt"
echo "special content" > "$special_src"
bash "$CLI" store "$special_src" --category documents --desc "Report with parens and spaces" --tags "test" >/dev/null 2>&1 || true
special_path="documents/report (2025) final.txt"
assert "delete file with special chars --force" bash "$CLI" delete "$special_path" --force
local_special=$(jq -r --arg p "$special_path" 'select(.path == $p) | .path' "$TEST_DIR/INDEX.jsonl")
if [[ -z "$local_special" ]]; then
  echo "  ✅ special-char index entry removed"
  ((passed++)) || true
else
  echo "  ❌ special-char index entry still present"
  ((failed++)) || true
fi

# --- Path traversal prevention ---
echo ""
echo "Path traversal:"
echo "traversal test" > "$SRC_DIR/traversal.txt"
assert_output "reject .. in category" "must not contain" bash "$CLI" store "$SRC_DIR/traversal.txt" \
  --category "../escape" --desc "test" --tags "test"
assert_output "reject absolute category" "must not be an absolute path" bash "$CLI" store "$SRC_DIR/traversal.txt" \
  --category "/etc" --desc "test" --tags "test"
assert_output "reject .. in name" "must not contain" bash "$CLI" store "$SRC_DIR/traversal.txt" \
  --category documents --name "../../etc/passwd" --desc "test" --tags "test"
assert_output "reject / in name" "must not contain" bash "$CLI" store "$SRC_DIR/traversal.txt" \
  --category documents --name "sub/file.txt" --desc "test" --tags "test"
assert_output "reject .. in delete path" "must not contain" bash "$CLI" delete "../outside/file.txt" --force
assert_output "reject .. in update path" "must not contain" bash "$CLI" update "../outside/file.txt" --desc "test"

# --- Verify ---
echo ""
echo "Verify:"
assert_output "verify clean" "All clear" bash "$CLI" verify

# Create an orphan file
echo "orphan" > "$TEST_DIR/documents/orphan.txt"
assert_output "verify catches orphan" "Orphan file" bash "$CLI" verify

# Clean up orphan
rm "$TEST_DIR/documents/orphan.txt"

# verify --fix: stale index entry (file deleted from disk manually)
echo "stale content" > "$SRC_DIR/stale.txt"
assert "store file that will become stale" bash "$CLI" store "$SRC_DIR/stale.txt" \
  --category misc --desc "Stale file test" --tags "stale" --source manual
assert "stale file exists before manual delete" test -f "$TEST_DIR/misc/stale.txt"
# Manually remove from disk (bypassing claw-drive delete)
rm "$TEST_DIR/misc/stale.txt"
assert_output "verify reports missing on disk" "Missing on disk" bash "$CLI" verify
assert_output "verify --fix removes stale entry" "Fixed" bash "$CLI" verify --fix
# Confirm index entry is gone
stale_in_index=$(jq -r 'select(.path=="misc/stale.txt") | .path' "$TEST_DIR/INDEX.jsonl")
if [[ -z "$stale_in_index" ]]; then
  echo "  ✅ stale index entry removed by --fix"
  ((passed++)) || true
else
  echo "  ❌ stale index entry still present after --fix"
  ((failed++)) || true
fi
assert_output "verify clean after --fix" "All clear" bash "$CLI" verify

# verify --fix: missing hash entry
echo "nohash content" > "$SRC_DIR/nohash.txt"
assert "store file for hash-missing test" bash "$CLI" store "$SRC_DIR/nohash.txt" \
  --category misc --desc "Hash missing test" --tags "nohash" --source manual
# Manually strip hash from ledger
grep -v "misc/nohash.txt" "$TEST_DIR/.hashes" > "$TEST_DIR/.hashes.tmp" && \
  mv "$TEST_DIR/.hashes.tmp" "$TEST_DIR/.hashes"
assert_output "verify reports missing hash" "No hash registered" bash "$CLI" verify
assert_output "verify --fix registers hash" "Fixed" bash "$CLI" verify --fix
# Confirm hash is now present
if grep -q "misc/nohash.txt" "$TEST_DIR/.hashes" 2>/dev/null; then
  echo "  ✅ missing hash re-registered by --fix"
  ((passed++)) || true
else
  echo "  ❌ hash still missing after --fix"
  ((failed++)) || true
fi
assert_output "verify clean after hash fix" "All clear" bash "$CLI" verify

# --- Sync exclude args safety ---
echo ""
echo "Sync exclude args safety:"
cat > "$TEST_DIR/.sync-config" <<'EOF'
backend: google-drive
remote: gdrive:claw-drive
exclude:
  - identity/
  - '; touch /tmp/pwned #
EOF

sync_lines=$(CLAW_DRIVE_DIR="$TEST_DIR" CLAW_DRIVE_CONFIG_FILE="$TEST_DIR/.config" bash -c '
  source "'$SCRIPT_DIR'/../lib/config.sh"
  sync_build_exclude_args_lines
')

if echo "$sync_lines" | grep -Fxq -- "--exclude" && echo "$sync_lines" | grep -Fxq -- "'; touch /tmp/pwned #"; then
  echo "  ✅ exclude patterns emitted as literal args"
  ((passed++)) || true
else
  echo "  ❌ exclude args builder did not preserve literal pattern safely"
  ((failed++)) || true
fi

# --- Status ---
echo ""
echo "Status:"
assert_output "status shows dir" "$TEST_DIR" bash "$CLI" status

# --- Migrate ---
echo ""
echo "Migrate:"
MIGRATE_SRC="$TEST_DIR/migrate-source"
mkdir -p "$MIGRATE_SRC/taxes" "$MIGRATE_SRC/photos"
echo "w2 content" > "$MIGRATE_SRC/taxes/w2-form.pdf"
echo "photo" > "$MIGRATE_SRC/photos/vacation.jpg"
PLAN_FILE="$TEST_DIR/plan.json"

assert "migrate scan" bash "$CLI" migrate scan "$MIGRATE_SRC" "$PLAN_FILE"
assert "plan file created" test -f "$PLAN_FILE"
assert_output "plan has 2 files" "2" python3 -c "import json; print(len(json.load(open('$PLAN_FILE'))['files']))"
assert_output "migrate summary" "Total files: 2" bash "$CLI" migrate summary "$PLAN_FILE"

# plan filename quoting safety
PLAN_FILE_QUOTED="$TEST_DIR/plan'quoted.json"
cp "$PLAN_FILE" "$PLAN_FILE_QUOTED"
assert "migrate summary with quote in filename" bash "$CLI" migrate summary "$PLAN_FILE_QUOTED"

python3 -c "
import json
plan = json.load(open('$PLAN_FILE'))
for f in plan['files']:
    if 'w2' in f['source_path']:
        f['category'] = 'finance'
        f['name'] = 'w2-form-2025.pdf'
        f['tags'] = 'finance, tax-2025'
        f['description'] = 'W-2 form 2025'
        f['confidence'] = 'high'
    else:
        f['category'] = 'photos'
        f['name'] = 'vacation.jpg'
        f['tags'] = 'photos, vacation'
        f['description'] = 'Vacation photo'
        f['confidence'] = 'medium'
json.dump(plan, open('$PLAN_FILE', 'w'), indent=2)
"

assert "migrate apply dry-run" bash "$CLI" migrate apply "$PLAN_FILE" --dry-run

# migrate source_path traversal should be rejected
echo "outside" > "$TEST_DIR/outside.txt"
MALICIOUS_PLAN="$TEST_DIR/malicious-plan.json"
cat > "$MALICIOUS_PLAN" <<EOF
{
  "source": "$MIGRATE_SRC",
  "scanned_at": "2026-01-01T00:00:00Z",
  "files": [
    {
      "source_path": "../outside.txt",
      "category": "documents",
      "name": "should-not-copy.txt",
      "tags": "test",
      "description": "malicious",
      "confidence": "high",
      "status": "pending"
    }
  ]
}
EOF
assert_output "migrate rejects source_path traversal" "Unsafe source path" bash "$CLI" migrate apply "$MALICIOUS_PLAN"
assert "traversal source not copied" test ! -f "$TEST_DIR/documents/should-not-copy.txt"

assert "migrate apply" bash "$CLI" migrate apply "$PLAN_FILE"
assert "migrated file exists" test -f "$TEST_DIR/finance/w2-form-2025.pdf"
assert "migrated photo exists" test -f "$TEST_DIR/photos/vacation.jpg"

# Verify migrated files in JSONL index
local_migrated=$(jq -r 'select(.path=="finance/w2-form-2025.pdf") | .path' "$TEST_DIR/INDEX.jsonl")
if [[ "$local_migrated" == "finance/w2-form-2025.pdf" ]]; then
  echo "  ✅ migrated file in JSONL index"
  ((passed++)) || true
else
  echo "  ❌ migrated file not in index"
  ((failed++)) || true
fi

# --- Results ---
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Results: $passed passed, $failed failed"
[[ $failed -eq 0 ]] && echo "✅ All tests passed." || echo "❌ Some tests failed."
exit "$failed"
