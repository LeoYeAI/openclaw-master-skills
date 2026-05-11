#!/usr/bin/env bash
# Gaggiuino API wrapper script
# Usage: gaggiuino.sh <command> [args]
# Commands: status, profiles, latest-shot, shot <id>, select-profile <id>, get-settings [cat], update-settings <cat> <json>, get-base-url, set-base-url <url-or-host>, clear-base-url
#
# Security / review note:
# - This script talks only to the configured Gaggiuino local/LAN API endpoint.
# - The `shot` command performs local-only JSON restructuring into `processedShot`
#   and `interpreted` to reduce target-vs-limit misreads during analysis.
# - It does not send shot data to third-party services and does not access
#   credential stores or user-secret files.

set -euo pipefail

DEFAULT_BASE_URL="http://gaggiuino.local"
STATE_FILE="${HOME}/.openclaw/workspace/memory/gaggiuino-base-url.json"
TIMEOUT=10

load_preferred_base_url() {
  python3 - "$STATE_FILE" <<'PY'
import json, os, sys
path = sys.argv[1]
if not os.path.exists(path):
    print("")
    raise SystemExit(0)
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    value = data.get('preferredBaseUrl', '') if isinstance(data, dict) else ''
    print(value or "")
except Exception:
    print("")
PY
}

PREFERRED_BASE_URL="$(load_preferred_base_url)"
BASE_URL="$DEFAULT_BASE_URL"
FALLBACK_BASE_URL=""
PREFERRED_BASE_URL_SET=0

if [[ -n "$PREFERRED_BASE_URL" ]]; then
  BASE_URL="$PREFERRED_BASE_URL"
  FALLBACK_BASE_URL="$DEFAULT_BASE_URL"
  PREFERRED_BASE_URL_SET=1
fi

should_try_fallback() {
  local curl_rc="$1"
  [[ "$PREFERRED_BASE_URL_SET" -eq 1 && -n "$FALLBACK_BASE_URL" ]] || return 1
  case "$curl_rc" in
    6|7) return 0 ;;
    *) return 1 ;;
  esac
}

http_request() {
  local method="$1"
  local path="$2"
  local body_file="$3"
  local data="${4:-}"
  local url="${BASE_URL}${path}"
  local status="000"
  local curl_rc=0

  if [[ "$method" == "GET" ]]; then
    status=$(curl -sS --max-time "$TIMEOUT" -o "$body_file" -w "%{http_code}" "$url" 2>/dev/null) || curl_rc=$?
  else
    if [[ -n "$data" ]]; then
      status=$(curl -sS --max-time "$TIMEOUT" -X "$method" -H "Content-Type: application/json" -d "$data" -o "$body_file" -w "%{http_code}" "$url" 2>/dev/null) || curl_rc=$?
    else
      status=$(curl -sS --max-time "$TIMEOUT" -X "$method" -o "$body_file" -w "%{http_code}" "$url" 2>/dev/null) || curl_rc=$?
    fi
  fi

  if should_try_fallback "$curl_rc"; then
    url="${FALLBACK_BASE_URL}${path}"
    curl_rc=0
    if [[ "$method" == "GET" ]]; then
      status=$(curl -sS --max-time "$TIMEOUT" -o "$body_file" -w "%{http_code}" "$url" 2>/dev/null) || curl_rc=$?
    else
      if [[ -n "$data" ]]; then
        status=$(curl -sS --max-time "$TIMEOUT" -X "$method" -H "Content-Type: application/json" -d "$data" -o "$body_file" -w "%{http_code}" "$url" 2>/dev/null) || curl_rc=$?
      else
        status=$(curl -sS --max-time "$TIMEOUT" -X "$method" -o "$body_file" -w "%{http_code}" "$url" 2>/dev/null) || curl_rc=$?
      fi
    fi
  fi

  LAST_HTTP_STATUS="$status"
  return "$curl_rc"
}

settings_request() {
  local method="$1"
  local endpoint="$2"
  local body_file="$3"
  local data="${4:-}"

  if ! http_request "$method" "$endpoint" "$body_file" "$data"; then
    return 1
  fi

  case "$LAST_HTTP_STATUS" in
    200|204)
      return 0
      ;;
    404)
      echo '{"error": "Settings API not available on this machine/firmware", "supported": false, "endpoint": "'$endpoint'"}'
      return 44
      ;;
    *)
      return 1
      ;;
  esac
}

api_get() {
  local path="$1"
  local tmp
  tmp=$(mktemp)

  if ! http_request "GET" "$path" "$tmp"; then
    rm -f "$tmp"
    return 1
  fi

  if [[ "$LAST_HTTP_STATUS" =~ ^2 ]]; then
    cat "$tmp"
    rm -f "$tmp"
    return 0
  fi

  rm -f "$tmp"
  return 22
}

api_post_fire_and_forget() {
  local path="$1"
  local tmp
  tmp=$(mktemp)

  if ! http_request "POST" "$path" "$tmp"; then
    rm -f "$tmp"
    return 1
  fi

  rm -f "$tmp"
  [[ "$LAST_HTTP_STATUS" =~ ^2 ]]
}

cmd_get_base_url() {
  python3 - "$STATE_FILE" <<'PY'
import json, os, sys
path = sys.argv[1]
value = None
if os.path.exists(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            value = data.get('preferredBaseUrl')
    except Exception:
        value = None
print(json.dumps({
    'preferredBaseUrl': value,
    'path': path,
    'defaultBaseUrl': 'http://gaggiuino.local'
}, ensure_ascii=False, indent=2))
PY
}

cmd_set_base_url() {
  local input="${1:?Base URL or host required}"
  python3 - "$STATE_FILE" "$input" <<'PY'
import json, os, re, sys
from datetime import datetime, timezone
path, raw = sys.argv[1], sys.argv[2].strip()
url = raw if re.match(r'^https?://', raw, re.I) else f'http://{raw}'
url = url.rstrip('/')
os.makedirs(os.path.dirname(path), exist_ok=True)
data = {
    'preferredBaseUrl': url,
    'updatedAt': datetime.now(timezone.utc).isoformat()
}
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(json.dumps({'saved': True, 'preferredBaseUrl': url, 'path': path}, ensure_ascii=False, indent=2))
PY
}

cmd_clear_base_url() {
  rm -f "$STATE_FILE"
  echo '{"cleared": true, "path": "'$STATE_FILE'"}'
}

cmd_status() {
  local raw
  raw=$(api_get "/api/system/status") || { echo '{"error": "Cannot connect to Gaggiuino"}' ; exit 1; }
  echo "$raw" | python3 -c "
import sys, json

def as_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() == 'true'
    return bool(v)

raw = json.load(sys.stdin)
# Observed API/community-wrapper behavior commonly returns a 1-item list here,
# but accept a direct object too for forward-compatibility.
s = raw[0] if isinstance(raw, list) and raw else (raw if isinstance(raw, dict) else {})

brew = as_bool(s.get('brewSwitchState', False))
steam = as_bool(s.get('steamSwitchState', False))

result = {
    'online': True,
    'state': 'brewing' if brew else ('steaming' if steam else 'idle'),
    'temp': {'current': float(s.get('temperature', 0)), 'target': float(s.get('targetTemperature', 0))},
    'pressure': float(s.get('pressure', 0)),
    'weight': float(s.get('weight', 0)),
    'water': int(s.get('waterLevel', 0)),
    'profile': {'id': int(s.get('profileId', 0)), 'name': s.get('profileName', 'Unknown')}
}
print(json.dumps(result, ensure_ascii=False, indent=2))
"
}

cmd_profiles() {
  local raw
  raw=$(api_get "/api/profiles/all") || { echo '{"error": "Cannot fetch profiles"}' ; exit 1; }
  echo "$raw" | python3 -c "
import sys, json

def as_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() == 'true'
    return bool(v)

profiles = json.load(sys.stdin)
result = []
for p in profiles:
    result.append({
        'id': p.get('id'),
        'name': p.get('name'),
        'selected': as_bool(p.get('selected', False))
    })
print(json.dumps(result, ensure_ascii=False, indent=2))
"
}

cmd_latest_shot() {
  local shot_id
  shot_id=$(api_get "/api/shots/latest" | python3 -c "import sys,json; r=json.load(sys.stdin); print((r[0].get('lastShotId','') if isinstance(r, list) and r else (r.get('lastShotId','') if isinstance(r, dict) else '')))" 2>/dev/null) \
    || { echo '{"error": "Cannot get latest shot ID"}' ; exit 1; }
  if [[ -z "$shot_id" || ! "$shot_id" =~ ^[0-9]+$ ]]; then
    echo '{"error": "Latest shot ID missing or invalid"}'
    exit 1
  fi
  cmd_shot "$shot_id"
}

cmd_shot() {
  local id="${1:?Shot ID required}"
  if [[ ! "$id" =~ ^[0-9]+$ ]]; then echo '{"error": "Invalid shot ID"}'; exit 1; fi
  local raw
  raw=$(api_get "/api/shots/$id") || { echo '{"error": "Cannot get shot '$id'"}' ; exit 1; }
  RAW_JSON="$raw" python3 - <<'PY'
import os, sys, json
from datetime import datetime

def maybe_div10(v):
    return (v / 10) if isinstance(v, (int, float)) else v

def normalize_datapoints(dp):
    if isinstance(dp, list):
        return dp
    if not isinstance(dp, dict):
        return []
    times = dp.get('timeInShot', []) or []
    n = len(times)
    out = []
    for i in range(n):
        out.append({
            'timeInShot': maybe_div10(times[i]) if i < len(times) else None,
            'pressure': maybe_div10((dp.get('pressure', []) or [None]*n)[i]) if i < len(dp.get('pressure', []) or []) else None,
            'pumpFlow': maybe_div10((dp.get('pumpFlow', []) or [None]*n)[i]) if i < len(dp.get('pumpFlow', []) or []) else None,
            'weightFlow': maybe_div10((dp.get('weightFlow', []) or [None]*n)[i]) if i < len(dp.get('weightFlow', []) or []) else None,
            'temperature': maybe_div10((dp.get('temperature', []) or [None]*n)[i]) if i < len(dp.get('temperature', []) or []) else None,
            'shotWeight': maybe_div10((dp.get('shotWeight', []) or [None]*n)[i]) if i < len(dp.get('shotWeight', []) or []) else None,
            'waterPumped': maybe_div10((dp.get('waterPumped', []) or [None]*n)[i]) if i < len(dp.get('waterPumped', []) or []) else None,
            'targetTemperature': maybe_div10((dp.get('targetTemperature', []) or [None]*n)[i]) if i < len(dp.get('targetTemperature', []) or []) else None,
            'targetPumpFlow': maybe_div10((dp.get('targetPumpFlow', []) or [None]*n)[i]) if i < len(dp.get('targetPumpFlow', []) or []) else None,
            'targetPressure': maybe_div10((dp.get('targetPressure', []) or [None]*n)[i]) if i < len(dp.get('targetPressure', []) or []) else None,
        })
    return out


def approx_equal(a, b, tol=1e-6):
    if a is None or b is None:
        return False
    return abs(a - b) <= tol


def stop_condition_satisfied(phase, point, entry_ctx):
    stop_conditions = phase.get('stopConditions') or {}
    if not stop_conditions:
        return False

    time_in_shot = point.get('timeInShot')
    pressure = point.get('pressure')
    pump_flow = point.get('pumpFlow')
    shot_weight = point.get('shotWeight')
    water_pumped = point.get('waterPumped')

    entry_time = entry_ctx.get('timeInShot')
    entry_water = entry_ctx.get('waterPumped')

    if 'pressureAbove' in stop_conditions and pressure is not None and pressure >= stop_conditions['pressureAbove']:
        return True
    if 'pressureBelow' in stop_conditions and pressure is not None and pressure <= stop_conditions['pressureBelow']:
        return True
    if 'flowAbove' in stop_conditions and pump_flow is not None and pump_flow >= stop_conditions['flowAbove']:
        return True
    if 'flowBelow' in stop_conditions and pump_flow is not None and pump_flow <= stop_conditions['flowBelow']:
        return True
    if 'weight' in stop_conditions and shot_weight is not None and shot_weight >= stop_conditions['weight']:
        return True
    if 'waterPumpedInPhase' in stop_conditions and water_pumped is not None and entry_water is not None:
        if (water_pumped - entry_water) >= stop_conditions['waterPumpedInPhase']:
            return True
    if 'time' in stop_conditions and time_in_shot is not None and entry_time is not None:
        if (time_in_shot - entry_time) >= stop_conditions['time']:
            return True

    return False


def point_prefers_next_phase(current_idx, phases, point):
    next_idx = current_idx + 1
    if next_idx >= len(phases):
        return False

    next_phase = phases[next_idx]
    target_pump_flow = point.get('targetPumpFlow')
    target_pressure = point.get('targetPressure')

    next_type = (next_phase.get('type') or '').upper()
    next_target = next_phase.get('target') or {}
    
    # If the machine's reported target ALREADY matches the next phase's start or end,
    # it indicates the control loop committed the switch before the telemetry frame was recorded.
    if next_type == 'FLOW':
        val = next_target.get('start')
        if val is None: val = next_target.get('end')
        if val is not None and approx_equal(target_pump_flow, val):
            return True
    elif next_type == 'PRESSURE':
        val = next_target.get('start')
        if val is None: val = next_target.get('end')
        if val is not None and approx_equal(target_pressure, val):
            return True
            
    return False


def assign_phase_index(datapoints, phases):
    if not phases:
        return datapoints

    current = 0
    total = len(phases)
    entry_ctx = {'timeInShot': None, 'waterPumped': None}
    advance_on_next_point = False

    for point in datapoints:
        if advance_on_next_point and current < total - 1:
            current += 1
            entry_ctx['timeInShot'] = point.get('timeInShot')
            entry_ctx['waterPumped'] = point.get('waterPumped')
            advance_on_next_point = False

            while current < total - 1 and stop_condition_satisfied(phases[current], point, entry_ctx):
                current += 1
                entry_ctx['timeInShot'] = point.get('timeInShot')
                entry_ctx['waterPumped'] = point.get('waterPumped')

        if entry_ctx['timeInShot'] is None:
            entry_ctx['timeInShot'] = point.get('timeInShot')
            entry_ctx['waterPumped'] = point.get('waterPumped')

        # Logic for determining the phase of the CURRENT point
        if current < total - 1 and not advance_on_next_point and stop_condition_satisfied(phases[current], point, entry_ctx):
            if point_prefers_next_phase(current, phases, point):
                # Semantic affinity: machine already switched its target/semantics
                current += 1
                entry_ctx = {'timeInShot': point.get('timeInShot'), 'waterPumped': point.get('waterPumped')}
                # Support potential skip of zero-duration phases
                while current < total - 1 and stop_condition_satisfied(phases[current], point, entry_ctx):
                    current += 1
                    entry_ctx = {'timeInShot': point.get('timeInShot'), 'waterPumped': point.get('waterPumped')}
            else:
                # Semantic anchor: machine is still executing the current phase's target
                advance_on_next_point = True

        point['_phaseIndex'] = phases[current].get('index')

    return datapoints


def build_processed_datapoints(datapoints, phases):
    phase_by_index = {p.get('index'): p for p in phases}
    out = []
    for point in datapoints:
        # This is the public wrapper layer: convert raw machine target fields
        # into phase-aware aliases so downstream analysis can reason in terms of
        # targets vs limits without re-decoding machine semantics every time.
        phase = phase_by_index.get(point.get('_phaseIndex')) or {}
        phase_type = (phase.get('type') or '').lower()
        item = {
            'timeInShot': point.get('timeInShot'),
            'phaseIndex': point.get('_phaseIndex'),
            'controlMode': phase_type if phase_type in ('flow', 'pressure') else 'unknown',
            'pressure': point.get('pressure'),
            'pumpFlow': point.get('pumpFlow'),
            'weightFlow': point.get('weightFlow'),
            'temperature': point.get('temperature'),
            'shotWeight': point.get('shotWeight'),
            'waterPumped': point.get('waterPumped'),
            'targetTemperature': point.get('targetTemperature'),
        }
        if phase_type == 'flow':
            item['pumpFlowTarget'] = point.get('targetPumpFlow')
            # Only expose a pressureLimit alias when this phase actually defines
            # a pressure restriction. Raw targetPressure may still be 0 in machine
            # data even when no limit is configured.
            item['pressureLimit'] = point.get('targetPressure') if phase.get('restriction') is not None else None
        elif phase_type == 'pressure':
            item['pressureTarget'] = point.get('targetPressure')
            # Only expose a pumpFlowLimit alias when this phase actually defines
            # a flow restriction. Raw targetPumpFlow may still be 0 in machine
            # data even when no limit is configured.
            item['pumpFlowLimit'] = point.get('targetPumpFlow') if phase.get('restriction') is not None else None
        else:
            # Fallback: if control mode is unknown, preserve raw field names
            # instead of guessing target-vs-limit semantics incorrectly.
            item['targetPumpFlow'] = point.get('targetPumpFlow')
            item['targetPressure'] = point.get('targetPressure')
        out.append(item)
    return out


def normalize_profile(profile):
    prof = dict(profile or {})
    phases = []
    for idx, p in enumerate(prof.get('phases', []) or [], 1):
        target = dict(p.get('target') or {})
        if 'time' in target and isinstance(target.get('time'), (int, float)):
            target['time'] = target['time'] / 1000
        stop_conditions = dict(p.get('stopConditions') or {})
        if 'time' in stop_conditions and isinstance(stop_conditions.get('time'), (int, float)):
            stop_conditions['time'] = stop_conditions['time'] / 1000
        phases.append({
            'index': idx,
            'name': p.get('name'),
            'type': p.get('type'),
            'target': target,
            'stopConditions': stop_conditions,
            'restriction': p.get('restriction'),
            'skip': p.get('skip'),
        })
    prof['phases'] = phases
    return prof


def build_phase_semantics(phases):
    out = []
    for p in phases:
        stop_conditions = p.get('stopConditions') or {}
        target = p.get('target') or {}
        if p.get('type') == 'FLOW':
            control_summary = 'flow phase'
            target_summary = f"flow target {target.get('end')} ml/s" if target.get('end') is not None else 'flow target unspecified'
            limit_summary = f"pressure limit {p.get('restriction')} bar" if p.get('restriction') is not None else 'no explicit pressure limit'
        elif p.get('type') == 'PRESSURE':
            control_summary = 'pressure phase'
            target_summary = f"pressure target {target.get('end')} bar" if target.get('end') is not None else 'pressure target unspecified'
            limit_summary = f"flow limit {p.get('restriction')} ml/s" if p.get('restriction') is not None else 'no explicit flow limit'
        else:
            control_summary = 'unknown control mode'
            target_summary = 'target semantics unclear'
            limit_summary = 'limit semantics unclear'

        if 'time' in stop_conditions and len(stop_conditions) == 1:
            time_role = 'timed phase target'
        elif 'time' in stop_conditions:
            time_role = 'fallback ceiling'
        else:
            time_role = 'no time stop condition'

        stop_condition_kinds = []
        if 'time' in stop_conditions:
            stop_condition_kinds.append('time')
        if 'weight' in stop_conditions:
            stop_condition_kinds.append('global cumulative weight')
        if 'waterPumpedInPhase' in stop_conditions:
            stop_condition_kinds.append('phase-local pumped water')
        if 'pressureAbove' in stop_conditions:
            stop_condition_kinds.append('pressure-above threshold')
        if 'pressureBelow' in stop_conditions:
            stop_condition_kinds.append('pressure-below threshold')
        if 'flowAbove' in stop_conditions:
            stop_condition_kinds.append('flow-above threshold')
        if 'flowBelow' in stop_conditions:
            stop_condition_kinds.append('flow-below threshold')

        out.append({
            'phaseIndex': p.get('index'),
            'controlSummary': control_summary,
            'targetSummary': target_summary,
            'limitSummary': limit_summary,
            'timeRole': time_role,
            'targetCurveTime': target.get('time'),
            'stopConditionKinds': stop_condition_kinds,
        })
    return out


d = json.loads(os.environ['RAW_JSON'])
shot_id = d.get('id')
duration = d.get('duration', 0) / 10 if isinstance(d.get('duration', 0), (int, float)) else d.get('duration')
ts = datetime.fromtimestamp(d.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')

raw_datapoints = normalize_datapoints(d.get('datapoints'))
if not raw_datapoints:
    print(json.dumps({'error': 'No data points found for this shot'}, ensure_ascii=False, indent=2))
    raise SystemExit(0)

profile = normalize_profile(d.get('profile') or {})
raw_datapoints = assign_phase_index(raw_datapoints, profile.get('phases', []))
processed_datapoints = build_processed_datapoints(raw_datapoints, profile.get('phases', []))
phase_semantics = build_phase_semantics(profile.get('phases', []))

final_dp = processed_datapoints[-1]
result = {
    'shot_id': shot_id,
    'timestamp': ts,
    'duration': duration,
    'stats': {
        'final_weight': final_dp.get('shotWeight') or 0,
        'total_water': final_dp.get('waterPumped') or 0,
        'max_flow': max([x.get('pumpFlow') or 0 for x in raw_datapoints]) if raw_datapoints else 0,
        'samples': len(raw_datapoints)
    },
    'processedShot': {
        'id': shot_id,
        'duration': duration,
        'timestamp': ts,
        'profile': profile,
        'datapoints': processed_datapoints
    },
    'interpreted': {
        'fieldSemantics': {
            'datapoints.*': 'actual telemetry / executed shot state over time',
            'profile.phases.*': 'intended program structure / phase design',
            'profile.phases[].type': 'phase-level control mode, not target-level metadata',
            'profile.phases[].target.time': 'target-curve timing, not automatically actual phase runtime',
            'profile.phases[].stopConditions.time': 'timed-phase target when it is the only stop condition; otherwise usually a fallback ceiling',
            'profile.phases[].stopConditions.weight': 'global cumulative shot weight unless explicit evidence says otherwise',
            'profile.phases[].stopConditions.waterPumpedInPhase': 'phase-local cumulative pumped water',
            'profile.phases[].stopConditions.flowAbove': 'instantaneous flow-above threshold',
            'profile.phases[].stopConditions.flowBelow': 'instantaneous flow-below threshold',
        },
        'phaseSemantics': phase_semantics,
        'analysisScaffold': {
            'ordering': [
                'read profile intent first',
                'replay what actually executed from datapoints',
                'audit which stop condition ended each phase',
                'check for skip-on-entry before judging phase quality',
                'judge expressed / partially expressed / failed before recommendations'
            ],
            'humanReadableRule': 'Prefer natural-language descriptions of target, limit, timed hold, fallback ceiling, cumulative yield, and phase skip rather than exposing raw machine field names by default.'
        }
    }
}
print(json.dumps(result, ensure_ascii=False, indent=2))
PY
}

cmd_select_profile() {
  local id="${1:?Profile ID required}"
  if [[ ! "$id" =~ ^[0-9]+$ ]]; then echo '{"error": "Invalid profile ID"}'; exit 1; fi

  local post_ok=0
  if api_post_fire_and_forget "/api/profile-select/$id"; then
    post_ok=1
  fi

  sleep 1

  local verify_raw
  verify_raw=$(api_get "/api/profiles/all") || verify_raw=""

  if [[ -n "$verify_raw" ]]; then
    echo "$verify_raw" | python3 -c "
import sys, json
profiles = json.load(sys.stdin)
target_id = int(sys.argv[1])
selected = None
for p in profiles:
    if int(p.get('id', -1)) == target_id:
        selected = p
        break
if selected and str(selected.get('selected')).strip().lower() == 'true':
    print(json.dumps({
        'sent': True,
        'confirmed': True,
        'profile_id': target_id,
        'profile_name': selected.get('name'),
        'note': 'profile switch confirmed by post-read verification'
    }, ensure_ascii=False))
else:
    print(json.dumps({
        'sent': bool(int(sys.argv[2])),
        'confirmed': False,
        'profile_id': target_id,
        'profile_name': (selected or {}).get('name'),
        'note': 'profile switch not confirmed after verification'
    }, ensure_ascii=False))
" "$id" "$post_ok"
    return 0
  fi

  if [[ "$post_ok" -eq 1 ]]; then
    echo '{"sent": true, "confirmed": false, "profile_id": '$id', "note": "profile switch request sent but verification unavailable"}'
    return 0
  fi

  echo '{"sent": false, "confirmed": false, "profile_id": '$id', "error": "Failed to send profile switch request and could not verify state"}'
  exit 1
}

cmd_get_settings() {
  local cat="${1:-}"
  local endpoint="/api/settings"
  if [[ -n "$cat" ]]; then endpoint="/api/settings/$cat"; fi

  local tmp rc
  tmp=$(mktemp)

  if settings_request "GET" "$endpoint" "$tmp"; then
    python3 -c "import sys, json; print(json.dumps(json.load(open(sys.argv[1])), ensure_ascii=False, indent=2))" "$tmp"
    rm -f "$tmp"
    return 0
  fi

  rc=$?
  rm -f "$tmp"

  if [[ "$rc" -eq 44 ]]; then
    exit 1
  fi

  echo '{"error": "Cannot connect to Gaggiuino"}'
  exit 1
}

cmd_update_settings() {
  local cat="${1:?Category required (boiler|system|led|scales|display|theme)}"
  local payload="${2:?JSON payload required}"
  local endpoint="/api/settings/$cat"
  local tmp rc
  tmp=$(mktemp)
  # POST-capable settings categories currently documented: boiler, system, led, scales, display, theme.
  # Note: Gaggiuino requires all fields from the corresponding GET response in the POST body.

  if settings_request "POST" "$endpoint" "$tmp" "$payload"; then
    rm -f "$tmp"
    echo '{"success": true, "category": "'$cat'"}'
    return 0
  fi

  rc=$?
  rm -f "$tmp"

  if [[ "$rc" -eq 44 ]]; then
    exit 1
  fi

  echo '{"error": "Failed to update settings for '$cat'"}'
  exit 1
}

# Main
case "${1:-help}" in
  status)          cmd_status ;;
  profiles)        cmd_profiles ;;
  latest-shot)     cmd_latest_shot ;;
  shot)            cmd_shot "${2:-}" ;;
  select-profile)  cmd_select_profile "${2:-}" ;;
  get-settings)    cmd_get_settings "${2:-}" ;;
  update-settings) cmd_update_settings "${2:-}" "${3:-}" ;;
  get-base-url)    cmd_get_base_url ;;
  set-base-url)    cmd_set_base_url "${2:-}" ;;
  clear-base-url)  cmd_clear_base_url ;;
  *)
    echo "Usage: $0 {status|profiles|latest-shot|shot <id>|select-profile <id>|get-settings [cat]|update-settings <cat> <json>|get-base-url|set-base-url <url-or-host>|clear-base-url}"
    exit 1
    ;;
esac
