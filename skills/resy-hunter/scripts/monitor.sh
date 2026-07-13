#!/usr/bin/env bash
# monitor.sh — Sweep the entire watchlist and report new availability
# Usage: ./monitor.sh [--platform resy|tock|opentable]
#
# Options:
#   --platform <name>   Only check this platform (bypasses interval timer).
#                        Can be specified multiple times. Omit to check all.
#
# Runs checks in parallel:
#   - Resy (curl):       up to 8 concurrent, every sweep
#   - Tock (Playwright): up to 2 concurrent, once per hour
#   - OpenTable (Playwright): up to 2 concurrent, once per hour
# All platform batches run simultaneously.
#
# Defaults:
#   - Time window: 6-10 PM unless overridden per entry
#   - Priority: only HIGH priority entries trigger Telegram alerts
#   - Telegram: max 5 slots per restaurant, sorted by 7-9 PM proximity

set -euo pipefail

# --- Parse arguments ---
FILTER_PLATFORMS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform)
      if [[ $# -lt 2 ]]; then
        echo '{"error": "Usage: monitor.sh [--platform resy|tock|opentable]"}' >&2
        exit 1
      fi
      p="$2"
      if [[ "$p" != "resy" && "$p" != "tock" && "$p" != "opentable" ]]; then
        echo "{\"error\": \"Unknown platform: ${p}. Use resy, tock, or opentable.\"}" >&2
        exit 1
      fi
      FILTER_PLATFORMS+=("$p")
      shift 2
      ;;
    *)
      echo "{\"error\": \"Unknown option: $1. Usage: monitor.sh [--platform resy|tock|opentable]\"}" >&2
      exit 1
      ;;
  esac
done

# Ensure Node.js is on PATH (for Playwright scripts)
if [[ -d "$HOME/.local/node/bin" ]]; then
  export PATH="$HOME/.local/node/bin:$PATH"
fi

SKILL_DIR="$HOME/.openclaw/skills/resy-hunter"
SCRIPTS_DIR="${SKILL_DIR}/scripts"
DATA_DIR="$HOME/.openclaw/data/resy-hunter"
mkdir -p "$DATA_DIR"

# Migrate old data files from skill dir to data dir
if [[ -f "${SKILL_DIR}/watchlist.json" && ! -f "${DATA_DIR}/watchlist.json" ]]; then
  cp "${SKILL_DIR}/watchlist.json" "${DATA_DIR}/watchlist.json"
fi
if [[ -f "${SKILL_DIR}/.last-seen.json" && ! -f "${DATA_DIR}/.last-seen.json" ]]; then
  cp "${SKILL_DIR}/.last-seen.json" "${DATA_DIR}/.last-seen.json"
fi

WATCHLIST_FILE="${DATA_DIR}/watchlist.json"
STATE_FILE="${DATA_DIR}/.last-seen.json"
PLATFORM_TS_FILE="${DATA_DIR}/.platform-timestamps.json"

# Initialize files if needed
[[ -f "$STATE_FILE" ]] || echo '{"seen":{}}' > "$STATE_FILE"
[[ -f "$WATCHLIST_FILE" ]] || echo '{"restaurants":[]}' > "$WATCHLIST_FILE"
[[ -f "$PLATFORM_TS_FILE" ]] || echo '{}' > "$PLATFORM_TS_FILE"

TODAY=$(date -u +"%Y-%m-%d")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
NOW_EPOCH=$(date +%s)
START_TIME=$NOW_EPOCH

# --- Platform check intervals (seconds) ---
RESY_INTERVAL=0
TOCK_INTERVAL=3600
OPENTABLE_INTERVAL=3600

platform_is_due() {
  local plat=$1 interval=$2
  if [[ "$interval" -eq 0 ]]; then return 0; fi
  local last_ts
  last_ts=$(jq -r --arg p "$plat" '.[$p] // 0' "$PLATFORM_TS_FILE")
  local elapsed=$(( NOW_EPOCH - last_ts ))
  [[ $elapsed -ge $interval ]]
}

# Read active entries
entries=$(jq -c '[.restaurants[] | select(.active == true)]' "$WATCHLIST_FILE")
entry_count=$(echo "$entries" | jq 'length')

if [[ "$entry_count" == "0" ]]; then
  jq -n --arg ts "$TIMESTAMP" '{
    timestamp: $ts,
    new_availability: [],
    total_checked: 0,
    total_with_availability: 0,
    message: "Watchlist is empty"
  }'
  exit 0
fi

# Determine which platforms are due
if [[ ${#FILTER_PLATFORMS[@]} -gt 0 ]]; then
  # Explicit --platform flag: only those platforms, bypass interval check
  resy_due=false; tock_due=false; opentable_due=false
  for fp in "${FILTER_PLATFORMS[@]}"; do
    case "$fp" in
      resy)      resy_due=true ;;
      tock)      tock_due=true ;;
      opentable) opentable_due=true ;;
    esac
  done
else
  # Default: all platforms, subject to interval check
  resy_due=true; tock_due=true; opentable_due=true
  platform_is_due "resy" "$RESY_INTERVAL" || resy_due=false
  platform_is_due "tock" "$TOCK_INTERVAL" || tock_due=false
  platform_is_due "opentable" "$OPENTABLE_INTERVAL" || opentable_due=false
fi

# Pre-fetch Resy auth token
if [[ "$resy_due" == "true" ]]; then
  has_resy=$(echo "$entries" | jq '[.[] | select(.platform == "resy")] | length')
  if [[ "$has_resy" -gt 0 && -z "${RESY_AUTH_TOKEN:-}" ]]; then
    RESY_AUTH_TOKEN=$(bash "${SCRIPTS_DIR}/resy-auth.sh" 2>/dev/null || true)
    if [[ -n "$RESY_AUTH_TOKEN" ]]; then
      export RESY_AUTH_TOKEN
    fi
  fi
fi

# ===========================================================
#  Phase 1: Build job list
# ===========================================================
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

resy_count=0; tock_count=0; opentable_count=0
skipped_tock=0; skipped_opentable=0
job_id=0

for i in $(seq 0 $((entry_count - 1))); do
  entry=$(echo "$entries" | jq -c ".[$i]")
  platform=$(echo "$entry" | jq -r '.platform')
  name=$(echo "$entry" | jq -r '.name')

  case "$platform" in
    resy)      [[ "$resy_due" != "true" ]] && continue ;;
    tock)      [[ "$tock_due" != "true" ]] && { skipped_tock=$((skipped_tock + 1)); continue; } ;;
    opentable) [[ "$opentable_due" != "true" ]] && { skipped_opentable=$((skipped_opentable + 1)); continue; } ;;
  esac

  dates=$(echo "$entry" | jq -r '.dates[]')

  for date in $dates; do
    [[ "$date" < "$TODAY" ]] && continue

    job_id=$((job_id + 1))
    echo "$entry"    > "${TMP_DIR}/job-${job_id}.entry"
    echo "$date"     > "${TMP_DIR}/job-${job_id}.date"
    echo "$platform" > "${TMP_DIR}/job-${job_id}.platform"
    echo "$name"     > "${TMP_DIR}/job-${job_id}.name"

    case "$platform" in
      resy)      resy_count=$((resy_count + 1));      echo "$job_id" >> "${TMP_DIR}/batch-resy" ;;
      tock)      tock_count=$((tock_count + 1));       echo "$job_id" >> "${TMP_DIR}/batch-tock" ;;
      opentable) opentable_count=$((opentable_count + 1)); echo "$job_id" >> "${TMP_DIR}/batch-opentable" ;;
    esac
  done
done

total_jobs=$job_id

if [[ "$total_jobs" -eq 0 ]]; then
  skip_msg=""
  [[ $skipped_tock -gt 0 ]] && skip_msg="${skip_msg}tock: skipped (checked <1h ago). "
  [[ $skipped_opentable -gt 0 ]] && skip_msg="${skip_msg}opentable: skipped (checked <1h ago). "
  jq -n --arg ts "$TIMESTAMP" --arg msg "No checks to run. ${skip_msg}" '{
    timestamp: $ts, new_availability: [], total_checked: 0,
    total_with_availability: 0, message: $msg
  }'
  exit 0
fi

# ===========================================================
#  Phase 2: Run checks in parallel
# ===========================================================
run_check() {
  local jid=$1
  local entry; entry=$(cat "${TMP_DIR}/job-${jid}.entry")
  local date;  date=$(cat "${TMP_DIR}/job-${jid}.date")
  local platform; platform=$(cat "${TMP_DIR}/job-${jid}.platform")
  local name; name=$(cat "${TMP_DIR}/job-${jid}.name")
  local party_size; party_size=$(echo "$entry" | jq -r '.party_size')
  local result='{"slots":[]}'

  case "$platform" in
    resy)
      local venue_id; venue_id=$(echo "$entry" | jq -r '.venue_id')
      result=$(bash "${SCRIPTS_DIR}/resy-check.sh" "$venue_id" "$date" "$party_size" 2>/dev/null || echo '{"slots":[]}')
      ;;
    opentable)
      local rid; rid=$(echo "$entry" | jq -r '.restaurant_id')
      result=$(node "${SCRIPTS_DIR}/opentable-check.js" "$rid" "$date" "$party_size" 2>/dev/null || echo '{"slots":[]}')
      ;;
    tock)
      local slug; slug=$(echo "$entry" | jq -r '.slug')
      result=$(node "${SCRIPTS_DIR}/tock-check.js" "$slug" "$date" "$party_size" 2>/dev/null || echo '{"slots":[]}')
      ;;
  esac

  echo "$result" > "${TMP_DIR}/result-${jid}.json"
  # Write name for progress display
  echo "$name" > "${TMP_DIR}/last-checked"
  touch "${TMP_DIR}/done-${platform}-${jid}"
}

run_batch() {
  local max=$1; shift
  local count=0
  for jid in "$@"; do
    run_check "$jid" &
    count=$((count + 1))
    if [[ $((count % max)) -eq 0 ]]; then wait; fi
  done
  wait
}

show_progress() {
  while true; do
    local r_done; r_done=$(ls "${TMP_DIR}"/done-resy-* 2>/dev/null | wc -l | tr -d ' ')
    local t_done; t_done=$(ls "${TMP_DIR}"/done-tock-* 2>/dev/null | wc -l | tr -d ' ')
    local o_done; o_done=$(ls "${TMP_DIR}"/done-opentable-* 2>/dev/null | wc -l | tr -d ' ')
    local done_count=$((r_done + t_done + o_done))
    local pct=0
    [[ $total_jobs -gt 0 ]] && pct=$((done_count * 100 / total_jobs))
    local elapsed=$(( $(date +%s) - START_TIME ))
    local last; last=$(cat "${TMP_DIR}/last-checked" 2>/dev/null || echo "...")

    local parts=""
    [[ $resy_count -gt 0 ]] && parts="${parts}resy ${r_done}/${resy_count}  "
    [[ $tock_count -gt 0 ]] && parts="${parts}tock ${t_done}/${tock_count}  "
    [[ $opentable_count -gt 0 ]] && parts="${parts}ot ${o_done}/${opentable_count}"

    printf '\r  ⏳ [%d/%d %d%%] %s — %s (%ds)   ' "$done_count" "$total_jobs" "$pct" "$parts" "$last" "$elapsed" >&2

    if [[ $done_count -ge $total_jobs ]]; then
      printf '\r  ✅ Done: %d checks in %ds  [%s]                    \n' "$total_jobs" "$elapsed" "$parts" >&2
      break
    fi
    sleep 0.5
  done
}

# Header
printf '  🍽️  Sweeping %d restaurants (%d checks)\n' "$entry_count" "$total_jobs" >&2
status_parts=""
[[ $resy_count -gt 0 ]] && status_parts="${status_parts}resy: ${resy_count}  "
[[ $tock_count -gt 0 ]] && status_parts="${status_parts}tock: ${tock_count}  "
[[ $opentable_count -gt 0 ]] && status_parts="${status_parts}opentable: ${opentable_count}  "
[[ $skipped_tock -gt 0 ]] && status_parts="${status_parts}(tock skipped — checked <1h ago)  "
[[ $skipped_opentable -gt 0 ]] && status_parts="${status_parts}(opentable skipped — checked <1h ago)  "
printf '     %s\n' "$status_parts" >&2

# Start progress monitor
show_progress &
progress_pid=$!

# Launch all platform batches simultaneously
resy_pid=""; tock_pid=""; ot_pid=""
if [[ -f "${TMP_DIR}/batch-resy" ]]; then
  run_batch 8 $(cat "${TMP_DIR}/batch-resy") &
  resy_pid=$!
fi
if [[ -f "${TMP_DIR}/batch-tock" ]]; then
  run_batch 2 $(cat "${TMP_DIR}/batch-tock") &
  tock_pid=$!
fi
if [[ -f "${TMP_DIR}/batch-opentable" ]]; then
  run_batch 2 $(cat "${TMP_DIR}/batch-opentable") &
  ot_pid=$!
fi

[[ -n "$resy_pid" ]] && wait "$resy_pid" 2>/dev/null || true
[[ -n "$tock_pid" ]] && wait "$tock_pid" 2>/dev/null || true
[[ -n "$ot_pid" ]]   && wait "$ot_pid"   2>/dev/null || true
wait "$progress_pid" 2>/dev/null || true

# Update platform timestamps
if [[ "$resy_due" == "true" && $resy_count -gt 0 ]]; then
  jq --argjson t "$NOW_EPOCH" '.resy = $t' "$PLATFORM_TS_FILE" > "${PLATFORM_TS_FILE}.tmp" && mv "${PLATFORM_TS_FILE}.tmp" "$PLATFORM_TS_FILE"
fi
if [[ "$tock_due" == "true" && $tock_count -gt 0 ]]; then
  jq --argjson t "$NOW_EPOCH" '.tock = $t' "$PLATFORM_TS_FILE" > "${PLATFORM_TS_FILE}.tmp" && mv "${PLATFORM_TS_FILE}.tmp" "$PLATFORM_TS_FILE"
fi
if [[ "$opentable_due" == "true" && $opentable_count -gt 0 ]]; then
  jq --argjson t "$NOW_EPOCH" '.opentable = $t' "$PLATFORM_TS_FILE" > "${PLATFORM_TS_FILE}.tmp" && mv "${PLATFORM_TS_FILE}.tmp" "$PLATFORM_TS_FILE"
fi

# ===========================================================
#  Phase 3: Process results (dedup, filter, report, notify)
# ===========================================================
all_results="[]"       # Full report (all priorities)
alert_results="[]"     # Telegram alerts (high priority only)
total_checked=0
total_with_availability=0
ot_session_expired=false

for jid in $(seq 1 "$total_jobs"); do
  result_file="${TMP_DIR}/result-${jid}.json"
  [[ -f "$result_file" ]] || continue

  entry=$(cat "${TMP_DIR}/job-${jid}.entry")
  date=$(cat "${TMP_DIR}/job-${jid}.date")
  platform=$(cat "${TMP_DIR}/job-${jid}.platform")
  name=$(echo "$entry" | jq -r '.name')
  party_size=$(echo "$entry" | jq -r '.party_size')
  priority=$(echo "$entry" | jq -r '.priority // "low"')
  result=$(cat "$result_file")

  total_checked=$((total_checked + 1))

  # Handle OpenTable session expiry
  if [[ "$platform" == "opentable" ]]; then
    ses_exp=$(echo "$result" | jq -r '.session_expired // false')
    if [[ "$ses_exp" == "true" ]]; then
      ot_session_expired=true
      continue
    fi
  fi

  # Default time window: 6-10 PM unless overridden per entry
  earliest=$(echo "$entry" | jq -r '.preferred_times.earliest // "18:00"')
  latest=$(echo "$entry" | jq -r '.preferred_times.latest // "22:00"')

  # Extract slots
  slots=$(echo "$result" | jq -c '.slots // []')
  slot_count=$(echo "$slots" | jq 'length')

  if [[ "$slot_count" -gt 0 ]]; then
    # Filter by time window
    if [[ -n "$earliest" && -n "$latest" ]]; then
      slots=$(echo "$slots" | jq -c --arg e "$earliest" --arg l "$latest" '[
        .[] | select(
          (.time_24h // (.time_start | split(" ") | last | split("T") | last | .[0:5])) as $t |
          $t >= $e and $t <= $l
        )
      ]')
      slot_count=$(echo "$slots" | jq 'length')
    fi
  fi

  if [[ "$slot_count" -gt 0 ]]; then
    total_with_availability=$((total_with_availability + 1))

    # Deduplication
    state_key="${platform}:$(echo "$entry" | jq -r '.venue_id // .restaurant_id // .slug'):${date}"
    prev_slots=$(jq -c --arg key "$state_key" '.seen[$key] // []' "$STATE_FILE")

    new_slots=$(jq -c --argjson prev "$prev_slots" '[
      .[] | . as $slot |
      if ($prev | map(.time_start) | index($slot.time_start)) then empty
      else $slot end
    ]' <<< "$slots")

    new_count=$(echo "$new_slots" | jq 'length')

    if [[ "$new_count" -gt 0 ]]; then
      # Build booking URL
      booking_url=""
      case "$platform" in
        resy)
          slug=$(echo "$result" | jq -r '.venue_slug // ""')
          city=$(echo "$result" | jq -r '.venue_city // "New York"' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
          region=$(echo "$result" | jq -r '.venue_region // "ny"' | tr '[:upper:]' '[:lower:]')
          booking_url="https://resy.com/cities/${city}-${region}/venues/${slug}?date=${date}&seats=${party_size}"
          ;;
        opentable)
          rid=$(echo "$entry" | jq -r '.restaurant_id')
          booking_url="https://www.opentable.com/booking/widget?rid=${rid}&datetime=${date}T19:00&covers=${party_size}"
          ;;
        tock)
          tslug=$(echo "$entry" | jq -r '.slug')
          booking_url="https://www.exploretock.com/${tslug}/search?date=${date}&size=${party_size}"
          ;;
      esac

      entry_result=$(jq -n \
        --arg name "$name" \
        --arg platform "$platform" \
        --arg date "$date" \
        --argjson party_size "$party_size" \
        --argjson slots "$new_slots" \
        --arg url "$booking_url" \
        --arg priority "$priority" \
        '{
          restaurant: $name,
          platform: $platform,
          date: $date,
          party_size: $party_size,
          priority: $priority,
          slots: $slots,
          booking_url: $url
        }')

      # Always add to full report
      all_results=$(echo "$all_results" | jq --argjson entry "$entry_result" '. += [$entry]')

      # Only add HIGH priority to alert list
      if [[ "$priority" == "high" ]]; then
        alert_results=$(echo "$alert_results" | jq --argjson entry "$entry_result" '. += [$entry]')
      fi
    fi

    # Update state with current slots (all priorities)
    state_update=$(jq --arg key "$state_key" --argjson slots "$slots" --arg ts "$TIMESTAMP" '
      .seen[$key] = [$slots[] | . + {first_seen: $ts}]
    ' "$STATE_FILE")
    echo "$state_update" > "$STATE_FILE"
  fi
done

# Clean up expired entries from state
jq --arg today "$TODAY" '
  .seen = (.seen | to_entries | map(
    select((.key | split(":") | last) >= $today)
  ) | from_entries)
' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"

# Output the full report (includes all priorities)
report=$(jq -n \
  --arg ts "$TIMESTAMP" \
  --argjson results "$all_results" \
  --argjson checked "$total_checked" \
  --argjson avail "$total_with_availability" \
  '{
    timestamp: $ts,
    new_availability: $results,
    total_checked: $checked,
    total_with_availability: $avail
  }')

echo "$report"

# --- Telegram notification (HIGH priority only, max 5 slots) ---
alert_count=$(echo "$alert_results" | jq 'length')
if [[ "$alert_count" -gt 0 ]]; then
  msg="🍽️ *New Availability Found!*"$'\n'
  for j in $(seq 0 $((alert_count - 1))); do
    r_name=$(echo "$alert_results" | jq -r --argjson i "$j" '.[$i].restaurant')
    r_platform=$(echo "$alert_results" | jq -r --argjson i "$j" '.[$i].platform')
    r_date=$(echo "$alert_results" | jq -r --argjson i "$j" '.[$i].date')
    r_party=$(echo "$alert_results" | jq -r --argjson i "$j" '.[$i].party_size')
    r_url=$(echo "$alert_results" | jq -r --argjson i "$j" '.[$i].booking_url')

    # Sort slots by proximity to 8 PM (prime time center), cap at 5
    r_times=$(echo "$alert_results" | jq -r --argjson i "$j" '
      .[$i].slots |
      sort_by(
        .time_24h | split(":") |
        ((.[0] | tonumber) * 60 + (.[1] | tonumber)) |
        (. - 1200) | if . < 0 then -. else . end
      ) |
      [limit(5; .[]) |
        .time_start + (
          if (.deposit_fee // 0) > 0
          then " ($" + (.deposit_fee | round | tostring) + " deposit)"
          else ""
          end
        )
      ] | join(", ")')

    r_total=$(echo "$alert_results" | jq -r --argjson i "$j" '.[$i].slots | length')
    r_extra=""
    if [[ "$r_total" -gt 5 ]]; then
      r_extra=" + $((r_total - 5)) more"
    fi

    msg="${msg}"$'\n'"*${r_name}* (${r_platform})"
    msg="${msg}"$'\n'"📅 ${r_date} | 👥 ${r_party} people"
    msg="${msg}"$'\n'"🕐 ${r_times}${r_extra}"
    msg="${msg}"$'\n'"🔗 [Book now](${r_url})"$'\n'
  done

  bash "${SCRIPTS_DIR}/notify.sh" "$msg" 2>/dev/null || true
fi

# Notify about OpenTable session expiry
if [[ "$ot_session_expired" == "true" ]]; then
  bash "${SCRIPTS_DIR}/notify.sh" "⚠️ OpenTable session expired. Run to re-authenticate:
node ~/.openclaw/skills/resy-hunter/scripts/opentable-login.js" 2>/dev/null || true
fi
