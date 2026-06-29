#!/bin/bash
# _checkpoint-full.sh — Full checkpoint implementation
# INTERNAL: Sourced by checkpoint.sh --full. Not intended for direct invocation.
#
# Expects these variables/functions from checkpoint.sh:
#   SCRIPT_DIR, AMCP_CLI, IDENTITY_PATH, CONFIG_FILE
#   CONTENT_DIR, CHECKPOINT_DIR, LAST_CHECKPOINT_FILE, KEEP_CHECKPOINTS
#   AGENT_NAME, PREVIOUS_CID, PINATA_JWT, PINNING_PROVIDER
#   NOTIFY, FORCE_CHECKPOINT, SMART_CHECKPOINT, DRY_RUN
#   SKIP_EVOLUTION, NO_SOLVR_METADATA
#   pin_to_pinata(), pin_to_solvr(), do_pinning()
#   scan_for_secrets(), register_with_solvr(), rotate_checkpoints()

# ============================================================
# Full secret extraction (extended beyond quick mode)
# ============================================================
extract_all_secrets() {
  python3 << 'PYEOF'
import json
import os

secrets = []

# 1. AMCP config (Pinata, recovery, API keys)
amcp_path = os.path.expanduser("~/.amcp/config.json")
if os.path.exists(amcp_path):
    with open(amcp_path) as f:
        amcp = json.load(f)

    if "pinata" in amcp:
        if amcp["pinata"].get("jwt"):
            secrets.append({
                "key": "PINATA_JWT",
                "value": amcp["pinata"]["jwt"],
                "type": "jwt",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "pinata.jwt"}]
            })
        if amcp["pinata"].get("apiKey"):
            secrets.append({
                "key": "PINATA_API_KEY",
                "value": amcp["pinata"]["apiKey"],
                "type": "api_key",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "pinata.apiKey"}]
            })
        if amcp["pinata"].get("secret"):
            secrets.append({
                "key": "PINATA_SECRET",
                "value": amcp["pinata"]["secret"],
                "type": "credential",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "pinata.secret"}]
            })

    if "apiKeys" in amcp:
        if amcp["apiKeys"].get("aclawdemy", {}).get("jwt"):
            secrets.append({
                "key": "ACLAWDEMY_JWT",
                "value": amcp["apiKeys"]["aclawdemy"]["jwt"],
                "type": "jwt",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "apiKeys.aclawdemy.jwt"}]
            })
        if amcp["apiKeys"].get("agentarxiv"):
            secrets.append({
                "key": "AGENTARXIV_API_KEY",
                "value": amcp["apiKeys"]["agentarxiv"],
                "type": "api_key",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "apiKeys.agentarxiv"}]
            })
        if amcp["apiKeys"].get("brave"):
            secrets.append({
                "key": "BRAVE_SEARCH_API_KEY",
                "value": amcp["apiKeys"]["brave"],
                "type": "api_key",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "apiKeys.brave"}]
            })

    # AgentMemory credentials
    if "agentmemory" in amcp:
        if amcp["agentmemory"].get("email"):
            secrets.append({
                "key": "AGENTMEMORY_EMAIL",
                "value": amcp["agentmemory"]["email"],
                "type": "credential",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "agentmemory.email"}]
            })
        if amcp["agentmemory"].get("password"):
            secrets.append({
                "key": "AGENTMEMORY_PASSWORD",
                "value": amcp["agentmemory"]["password"],
                "type": "credential",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "agentmemory.password"}]
            })

    # Recovery mnemonic (CRITICAL)
    if "recovery" in amcp:
        if amcp["recovery"].get("mnemonic"):
            secrets.append({
                "key": "AMCP_MNEMONIC",
                "value": amcp["recovery"]["mnemonic"],
                "type": "mnemonic",
                "targets": [{"kind": "file", "path": amcp_path, "jsonPath": "recovery.mnemonic"}]
            })

# 2. OpenClaw config (skills API keys)
oc_path = os.path.expanduser("~/.openclaw/openclaw.json")
if os.path.exists(oc_path):
    with open(oc_path) as f:
        oc = json.load(f)

    skills = oc.get("skills", {}).get("entries", {})
    for name, cfg in skills.items():
        if isinstance(cfg, dict) and "apiKey" in cfg:
            key_name = name.upper().replace("-", "_") + "_API_KEY"
            secrets.append({
                "key": key_name,
                "value": cfg["apiKey"],
                "type": "api_key",
                "targets": [{"kind": "file", "path": oc_path, "jsonPath": f"skills.entries.{name}.apiKey"}]
            })

    # Google Keyring Password
    gog_cfg = skills.get("gog", {})
    if gog_cfg.get("keyringPassword"):
        secrets.append({
            "key": "GOG_KEYRING_PASSWORD",
            "value": gog_cfg["keyringPassword"],
            "type": "credential",
            "targets": [{"kind": "file", "path": oc_path, "jsonPath": "skills.entries.gog.keyringPassword"}]
        })

    # Web search API key
    web_search = oc.get("tools", {}).get("web", {}).get("search", {})
    if web_search.get("apiKey"):
        existing = [s["key"] for s in secrets]
        if "BRAVE_SEARCH_API_KEY" not in existing:
            secrets.append({
                "key": "BRAVE_SEARCH_API_KEY",
                "value": web_search["apiKey"],
                "type": "api_key",
                "targets": [{"kind": "file", "path": oc_path, "jsonPath": "tools.web.search.apiKey"}]
            })

# 3. Auth profiles (tokens)
auth_path = os.path.expanduser("~/.openclaw/auth-profiles.json")
if os.path.exists(auth_path):
    with open(auth_path) as f:
        auth = json.load(f)

    for profile, cfg in auth.get("profiles", {}).items():
        if "token" in cfg:
            token_val = cfg["token"].get("key", "") if isinstance(cfg["token"], dict) else cfg["token"]
            if token_val:
                secrets.append({
                    "key": f"{profile.upper()}_TOKEN",
                    "value": token_val,
                    "type": "token",
                    "targets": [{"kind": "file", "path": auth_path, "jsonPath": f"profiles.{profile}.token.key"}]
                })

# 4. Check AgentMemory vault for expected keys
existing_keys = [s["key"] for s in secrets]
expected_keys = [
    ("MOLTBOOK_TOKEN", "token"),
    ("CLAWDHUB_TOKEN", "api_key"),
]
for key, key_type in expected_keys:
    if key not in existing_keys:
        import subprocess
        try:
            result = subprocess.run(
                ["agentmemory", "secret", "get", key, "--show"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                value = result.stdout.strip()
                if value and not value.startswith("Error"):
                    secrets.append({
                        "key": key,
                        "value": value,
                        "type": key_type,
                        "targets": [{"kind": "env", "name": key}]
                    })
        except (OSError, subprocess.TimeoutExpired, ValueError):
            pass

# Deduplicate by key
seen = set()
unique_secrets = []
for s in secrets:
    if s["key"] not in seen:
        seen.add(s["key"])
        unique_secrets.append(s)

print(json.dumps(unique_secrets, indent=2))
PYEOF
}

# ============================================================
# Ontology graph CID computation
# ============================================================
compute_ontology_cid() {
  ONTOLOGY_GRAPH_CID=""
  local graph_path="$CONTENT_DIR/memory/ontology/graph.jsonl"
  [ ! -f "$graph_path" ] && return 0

  ONTOLOGY_GRAPH_CID=$(python3 -c "
import hashlib, base64, os

graph_path = os.path.expanduser('$graph_path')
with open(graph_path, 'rb') as f:
    content = f.read()

digest = hashlib.sha256(content).digest()
# CIDv1 raw: version(1) + codec(raw=0x55) + multihash(sha256=0x12, len=0x20, digest)
cid_bytes = bytes([0x01, 0x55, 0x12, 0x20]) + digest
cid_b32 = base64.b32encode(cid_bytes).decode('ascii').lower().rstrip('=')
print('b' + cid_b32)
" 2>/dev/null || echo '')

  [ -n "$ONTOLOGY_GRAPH_CID" ] && echo "Ontology graph CID: $ONTOLOGY_GRAPH_CID"
}

# ============================================================
# SOUL.md drift detection
# ============================================================
SOUL_HASH=""
SOUL_DRIFT_LOG="${SOUL_DRIFT_LOG:-$HOME/.amcp/soul-drift.log}"

compute_soul_hash() {
  local soul_path="$CONTENT_DIR/SOUL.md"
  [ ! -f "$soul_path" ] && return 0
  SOUL_HASH=$(sha256sum "$soul_path" | cut -d' ' -f1)
}

detect_soul_drift() {
  [ -z "$SOUL_HASH" ] && return 0
  [ ! -f "$LAST_CHECKPOINT_FILE" ] && return 0

  local prev_hash
  prev_hash=$(python3 -c "
import json, os
try:
    d = json.load(open(os.path.expanduser('$LAST_CHECKPOINT_FILE')))
    print(d.get('soulHash', ''))
except: pass
" 2>/dev/null || echo '')

  [ -z "$prev_hash" ] && return 0
  [ "$prev_hash" = "$SOUL_HASH" ] && return 0

  local soul_path="$CONTENT_DIR/SOUL.md"
  local changed_lines
  changed_lines=$(python3 -c "
import os
soul_path = os.path.expanduser('$soul_path')
with open(soul_path) as f:
    current = f.readlines()
total = len(current)
print(max(1, total // 5))
" 2>/dev/null || echo '1')

  local severity="minor"
  if [ "$changed_lines" -ge 20 ]; then
    severity="major"
  elif [ "$changed_lines" -ge 5 ]; then
    severity="moderate"
  fi

  mkdir -p "$(dirname "$SOUL_DRIFT_LOG")"
  local timestamp
  timestamp=$(date -Iseconds)
  echo "$timestamp severity=$severity lines_changed=$changed_lines prev_hash=$prev_hash new_hash=$SOUL_HASH" >> "$SOUL_DRIFT_LOG"
  echo "SOUL.md drift detected: severity=$severity (~$changed_lines lines changed)"

  if [ "$severity" != "minor" ]; then
    local notify_drift
    notify_drift=$(python3 -c "
import json, os
try:
    d = json.load(open(os.path.expanduser('${CONFIG_FILE:-$HOME/.amcp/config.json}')))
    print(d.get('notify',{}).get('enableSoulDrift', True))
except: print('True')
" 2>/dev/null || echo 'True')

    if [ "$notify_drift" = "True" ] && [ -x "$SCRIPT_DIR/notify.sh" ]; then
      "$SCRIPT_DIR/notify.sh" "🧠 [$AGENT_NAME] SOUL.md drift: $severity (~$changed_lines lines changed)" || true
    fi
  fi
}

# ============================================================
# Redacted config metadata extraction
# ============================================================
extract_config_metadata() {
  local staging_dir="$1"
  mkdir -p "$staging_dir/openclaw"
  local oc_config="$HOME/.openclaw/openclaw.json"
  if [ ! -f "$oc_config" ]; then
    echo "  No openclaw.json found, skipping config-metadata"
    return 0
  fi

  STAGING_DIR="$staging_dir" python3 << 'PYEOF'
import json, os, re

oc_path = os.path.expanduser("~/.openclaw/openclaw.json")
staging_dir = os.environ["STAGING_DIR"]

with open(oc_path) as f:
    data = json.load(f)

SECRET_PATTERNS = [
    r'eyJ[a-zA-Z0-9_-]*\.eyJ',
    r'sk-[a-zA-Z0-9]{20,}',
    r'ghp_[a-zA-Z0-9]{30,}',
    r'solvr_[a-zA-Z0-9_-]{20,}',
    r'am_[a-zA-Z0-9]{40,}',
    r'[0-9]{8,10}:AA[a-zA-Z0-9_-]{33,}',
    r'AKIA[0-9A-Z]{16}',
]

SECRET_KEY_NAMES = {
    'apikey', 'api_key', 'apiKey', 'secret', 'password',
    'jwt', 'token', 'botToken', 'bot_token', 'mnemonic',
    'keyringPassword', 'key', 'private_key', 'privateKey',
}

def is_secret_key(key_name):
    return key_name.lower().replace('-', '').replace('_', '') in {
        k.lower().replace('-', '').replace('_', '') for k in SECRET_KEY_NAMES
    }

def is_secret_value(val):
    if not isinstance(val, str):
        return False
    for pat in SECRET_PATTERNS:
        if re.search(pat, val):
            return True
    return False

def redact(obj, key_name=""):
    if isinstance(obj, dict):
        return {k: redact(v, k) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [redact(v, key_name) for v in obj]
    elif isinstance(obj, str):
        if is_secret_key(key_name) or is_secret_value(obj):
            return "[REDACTED]"
        return obj
    return obj

metadata = redact(data)
out_path = os.path.join(staging_dir, "openclaw", "config-metadata.json")
with open(out_path, "w") as f:
    json.dump(metadata, f, indent=2)
    f.write("\n")
PYEOF
  echo "  Created openclaw/config-metadata.json"
}

# ============================================================
# Main: run_full_checkpoint
# Called from checkpoint.sh after shared setup is complete.
# All shared variables and functions are in scope.
# ============================================================
run_full_checkpoint() {
  CHECKPOINT_TYPE="full"
  STAGING_DIR="$HOME/.amcp/staging-$$"
  SECRETS_FILE="$HOME/.amcp/secrets-full.json"

  # Override cleanup for full mode (staging + secrets)
  trap 'rm -rf "$STAGING_DIR"; rm -f "$SECRETS_FILE"' EXIT

  compute_soul_hash
  detect_soul_drift

  # ===========================================
  # STAGE 1: Extract ALL secrets
  # ===========================================
  echo "=============================================="
  echo "  AMCP FULL CHECKPOINT"
  echo "=============================================="
  echo "Agent: $AGENT_NAME"
  echo "Identity: $IDENTITY_PATH"
  [ -n "$PREVIOUS_CID" ] && echo "Previous CID: $PREVIOUS_CID"
  echo ""
  echo "=== STAGE 1: Extracting ALL secrets ==="

  extract_all_secrets > "$SECRETS_FILE"
  chmod 600 "$SECRETS_FILE"
  SECRET_COUNT=$(python3 -c "import json; print(len(json.load(open('$SECRETS_FILE'))))")
  echo "Found $SECRET_COUNT secrets"
  if [ "$DRY_RUN" = true ]; then
    echo "Secrets found:"
    python3 -c "import json; [print(f'  - {s[\"key\"]} ({s[\"type\"]})') for s in json.load(open('$SECRETS_FILE'))]"
  fi

  # Compute ontology CID
  compute_ontology_cid

  # ===========================================
  # STAGE 2: Prepare content staging
  # ===========================================
  echo ""
  echo "=== STAGE 2: Preparing content staging ==="
  rm -rf "$STAGING_DIR"
  mkdir -p "$STAGING_DIR"

  echo "Copying workspace: $CONTENT_DIR ..."
  rsync -a --info=progress2 \
    --exclude='.venv' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    "$CONTENT_DIR/" "$STAGING_DIR/workspace/"

  echo "Copying ~/.amcp/identity.json..."
  mkdir -p "$STAGING_DIR/amcp"
  cp "$IDENTITY_PATH" "$STAGING_DIR/amcp/identity.json" 2>/dev/null || true

  echo "Extracting config metadata..."
  extract_config_metadata "$STAGING_DIR"

  # Smart content selection
  if [ "$SMART_CHECKPOINT" = true ] && [ -x "$SCRIPT_DIR/smart-checkpoint-filter.sh" ]; then
    echo ""
    echo "=== Smart Content Selection (Groq) ==="
    local_smart_args=("--content-dir" "$CONTENT_DIR")
    [ "$DRY_RUN" = true ] && local_smart_args+=("--dry-run")
    [ -n "${CONFIG_FILE:-}" ] && local_smart_args+=("--config" "$CONFIG_FILE")

    SMART_MANIFEST=$("$SCRIPT_DIR/smart-checkpoint-filter.sh" "${local_smart_args[@]}" 2>&1 | tee /dev/stderr | tail -1) || {
      echo "WARN: Smart filter failed, including all files (fallback)" >&2
      SMART_MANIFEST=""
    }

    if [ -n "$SMART_MANIFEST" ]; then
      excluded_count=0
      while IFS= read -r excl_file; do
        staged_path="$STAGING_DIR/workspace/$excl_file"
        if [ -f "$staged_path" ]; then
          rm -f "$staged_path"
          excluded_count=$((excluded_count + 1))
        fi
      done < <(echo "$SMART_MANIFEST" | python3 -c "
import json, sys
try:
    m = json.loads(sys.stdin.read())
    for f in m.get('exclude', []):
        print(f)
except: pass
" 2>/dev/null)
      echo "  Excluded $excluded_count files from checkpoint"
      mkdir -p "$STAGING_DIR/amcp"
      echo "$SMART_MANIFEST" > "$STAGING_DIR/amcp/smart-filter-manifest.json"
      echo "  Saved filter manifest to staging"
    fi
  elif [ "$SMART_CHECKPOINT" = true ]; then
    echo "WARN: --smart requested but smart-checkpoint-filter.sh not found at $SCRIPT_DIR" >&2
  fi

  # Log included optional directories
  if [ -d "$STAGING_DIR/workspace/memory/ontology" ]; then
    echo "  Included ontology graph ($(find "$STAGING_DIR/workspace/memory/ontology" -name '*.jsonl' 2>/dev/null | wc -l) JSONL files)"
  fi
  if [ -d "$STAGING_DIR/workspace/memory/learning" ]; then
    echo "  Included learning storage (problems + learnings)"
  fi

  # Run memory evolution engine
  if [ "$SKIP_EVOLUTION" = false ] && [ -f "$CONTENT_DIR/memory/ontology/graph.jsonl" ] && [ -x "$SCRIPT_DIR/memory-evolution.sh" ]; then
    echo ""
    echo "Running memory evolution engine..."
    if [ "$DRY_RUN" = true ]; then
      "$SCRIPT_DIR/memory-evolution.sh" --all-new --graph "$CONTENT_DIR/memory/ontology/graph.jsonl" --dry-run || true
    else
      "$SCRIPT_DIR/memory-evolution.sh" --all-new --graph "$CONTENT_DIR/memory/ontology/graph.jsonl" || true
    fi
  elif [ "$SKIP_EVOLUTION" = true ]; then
    echo "  Skipping memory evolution (--skip-evolution)"
  fi

  # Build temporal index
  if [ -f "$CONTENT_DIR/memory/ontology/graph.jsonl" ]; then
    echo ""
    echo "Building temporal index..."
    CHECKPOINT_CID_FOR_INDEX="${PREVIOUS_CID:-genesis}"
    python3 "$SCRIPT_DIR/temporal-queries.py" build-index \
      --graph "$CONTENT_DIR/memory/ontology/graph.jsonl" \
      --cid "$CHECKPOINT_CID_FOR_INDEX" || echo "WARN: Temporal index build failed (non-fatal)"
  fi

  # Calculate sizes
  echo ""
  echo "Staging directory contents:"
  du -sh "$STAGING_DIR"/* 2>/dev/null | sort -h
  TOTAL_SIZE=$(du -sh "$STAGING_DIR" | cut -f1)
  echo "Total staging size: $TOTAL_SIZE"

  if [ "$DRY_RUN" = true ]; then
    echo "=== DRY RUN COMPLETE ==="
    echo "Would checkpoint $SECRET_COUNT secrets and $TOTAL_SIZE of content"
    rm -rf "$STAGING_DIR"
    rm -f "$SECRETS_FILE"
    exit 0
  fi

  # Pre-validation: scan staged content for cleartext secrets
  echo ""
  echo "=== PRE-VALIDATION: Scanning for cleartext secrets ==="
  scan_for_secrets "$STAGING_DIR" "$FORCE_CHECKPOINT"

  # ===========================================
  # STAGE 3: Create checkpoint
  # ===========================================
  echo ""
  echo "=== STAGE 3: Creating encrypted checkpoint ==="
  if [ "$NOTIFY" = "--notify" ]; then
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" \
      "🔄 [$AGENT_NAME] Starting FULL checkpoint ($TOTAL_SIZE, $SECRET_COUNT secrets)..."
  fi

  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  CHECKPOINT_PATH="$CHECKPOINT_DIR/full-checkpoint-$TIMESTAMP.amcp"

  AMCP_ARGS="checkpoint create --identity $IDENTITY_PATH --content $STAGING_DIR --secrets $SECRETS_FILE --out $CHECKPOINT_PATH"
  [ -n "$PREVIOUS_CID" ] && AMCP_ARGS="$AMCP_ARGS --previous $PREVIOUS_CID"

  echo "Running: $AMCP_CLI $AMCP_ARGS"
  $AMCP_CLI $AMCP_ARGS

  CHECKPOINT_SIZE=$(du -sh "$CHECKPOINT_PATH" | cut -f1)
  echo "Checkpoint created: $CHECKPOINT_PATH ($CHECKPOINT_SIZE)"

  # ===========================================
  # STAGE 4: Pin to IPFS
  # ===========================================
  echo "=== STAGE 4: Pinning to IPFS (provider: $PINNING_PROVIDER) ==="
  do_pinning

  if [ -n "$CID" ]; then
    echo "✅ Pinned to IPFS!"
    echo "   CID: $CID"
  fi

  # Register with Solvr
  register_with_solvr

  # ===========================================
  # STAGE 5: Cleanup and record
  # ===========================================
  echo ""
  echo "=== STAGE 5: Cleanup ==="

  python3 -c "
import json
data = {
    'cid': '''$CID''',
    'localPath': '''$CHECKPOINT_PATH''',
    'timestamp': '$(date -Iseconds)',
    'previousCID': '''$PREVIOUS_CID''',
    'secretCount': $SECRET_COUNT,
    'contentSize': '''$TOTAL_SIZE''',
    'checkpointSize': '''$CHECKPOINT_SIZE''',
    'type': 'full',
    'pinningProvider': '''$PINNING_PROVIDER'''
}
pinata_cid = '''$PINATA_CID'''
solvr_cid = '''$SOLVR_CID'''
if pinata_cid:
    data['pinataCid'] = pinata_cid
if solvr_cid:
    data['solvrCid'] = solvr_cid
ontology_cid = '''$ONTOLOGY_GRAPH_CID'''
if ontology_cid:
    data['ontologyGraphCID'] = ontology_cid
soul_hash = '''$SOUL_HASH'''
if soul_hash:
    data['soulHash'] = soul_hash
with open('$LAST_CHECKPOINT_FILE', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"

  rotate_checkpoints "full-checkpoint-*.amcp"

  # Notify end
  if [ "$NOTIFY" = "--notify" ]; then
    if [ -n "$CID" ]; then
      [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "✅ [$AGENT_NAME] FULL checkpoint complete!
📦 Size: $CHECKPOINT_SIZE ($TOTAL_SIZE content)
🔐 Secrets: $SECRET_COUNT
📍 CID: $CID (provider: $PINNING_PROVIDER)"
    else
      [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "✅ [$AGENT_NAME] FULL checkpoint complete (local only)
📦 Size: $CHECKPOINT_SIZE
🔐 Secrets: $SECRET_COUNT"
    fi
  fi

  echo "=============================================="
  echo "  FULL CHECKPOINT COMPLETE"
  echo "=============================================="
  echo "CID: ${CID:-'(local only)'}"
  echo "Path: $CHECKPOINT_PATH"
  echo "Secrets: $SECRET_COUNT"
  echo "Size: $CHECKPOINT_SIZE"
  echo "=============================================="
}
