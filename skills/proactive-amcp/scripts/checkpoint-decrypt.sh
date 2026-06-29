#!/bin/bash
# checkpoint-decrypt.sh — Encryption detection and decryption helpers for AMCP checkpoints
# Sourced by restore-agent.sh. Not meant to be run standalone.
#
# Requires: CHECKPOINT_KEYS_FILE, KEY_FILE, TEMP_FILES array, log() function

# Detect if a checkpoint file is encrypted (openssl enc produces "Salted__" magic header)
is_checkpoint_encrypted() {
  local file_path="$1"
  # openssl enc -aes-256-cbc -salt prepends 8-byte "Salted__" magic
  local magic
  magic=$(head -c 8 "$file_path" 2>/dev/null | cat -v) || return 1
  [[ "$magic" == "Salted__" ]]
}

# Resolve decryption key: --key-file > checkpoint-keys.json lookup by CID > lookup by path
resolve_decrypt_key() {
  local cid="$1"
  local checkpoint_path="$2"

  # Priority 1: --key-file flag
  if [ -n "$KEY_FILE" ]; then
    cat "$KEY_FILE" 2>/dev/null | tr -d '[:space:]'
    return 0
  fi

  # Priority 2: lookup by CID in checkpoint-keys.json
  if [ -n "$cid" ] && [ -f "$CHECKPOINT_KEYS_FILE" ]; then
    local key
    key=$(python3 -c "
import json, os, sys
keys_path = os.path.expanduser('$CHECKPOINT_KEYS_FILE')
with open(keys_path) as f:
    keys = json.load(f)
entry = keys.get('$cid', {})
if isinstance(entry, dict):
    print(entry.get('key', ''))
elif isinstance(entry, str):
    print(entry)
" 2>/dev/null || echo '')
    if [ -n "$key" ]; then
      echo "$key"
      return 0
    fi
  fi

  # Priority 3: lookup by local path in checkpoint-keys.json
  if [ -n "$checkpoint_path" ] && [ -f "$CHECKPOINT_KEYS_FILE" ]; then
    local key
    key=$(python3 -c "
import json, os, sys
keys_path = os.path.expanduser('$CHECKPOINT_KEYS_FILE')
with open(keys_path) as f:
    keys = json.load(f)
entry = keys.get('$checkpoint_path', {})
if isinstance(entry, dict):
    print(entry.get('key', ''))
elif isinstance(entry, str):
    print(entry)
" 2>/dev/null || echo '')
    if [ -n "$key" ]; then
      echo "$key"
      return 0
    fi
  fi

  return 1
}

# Decrypt an encrypted checkpoint file in place
decrypt_checkpoint() {
  local checkpoint_path="$1"
  local decrypt_key="$2"

  local decrypted_path="${checkpoint_path}.decrypted"
  TEMP_FILES+=("$decrypted_path")

  if ! openssl enc -aes-256-cbc -d -pbkdf2 \
    -in "$checkpoint_path" \
    -out "$decrypted_path" \
    -pass "pass:${decrypt_key}" 2>/dev/null; then
    log "ERROR: Decryption failed — wrong key or corrupted checkpoint"
    rm -f "$decrypted_path"
    return 1
  fi

  # Replace encrypted file with decrypted
  mv "$decrypted_path" "$checkpoint_path"
  return 0
}
