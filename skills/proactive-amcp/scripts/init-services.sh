#!/bin/bash
# init-services.sh - Watchdog and checkpoint service setup for init.sh
# Sourced by init.sh — not intended to be run standalone.
#
# Expects these variables from the parent script:
#   SCRIPT_DIR, CONFIG_FILE, IDENTITY_PATH, AGENT_NAME,
#   WATCHDOG_INTERVAL, CHECKPOINT_SCHEDULE,
#   SYSTEMD_USER_DIR, WATCHDOG_SERVICE, CHECKPOINT_TIMER
# Expects these functions from the parent script:
#   info, ok, warn, fail, header, prompt_yn

# ============================================================
# Step 3: Watchdog service
# ============================================================

setup_watchdog() {
  header "Step 3: Watchdog Service"

  local interval
  interval=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('watchdog',{}).get('interval', $WATCHDOG_INTERVAL))" 2>/dev/null || echo "$WATCHDOG_INTERVAL")

  # Try systemd first
  if command -v systemctl &>/dev/null && systemctl --user status &>/dev/null 2>&1; then
    info "systemd user session available — setting up service"
    setup_watchdog_systemd "$interval"
  else
    info "systemd not available — falling back to cron"
    setup_watchdog_cron "$interval"
  fi
}

setup_watchdog_systemd() {
  local interval="$1"

  mkdir -p "$SYSTEMD_USER_DIR"

  # Write service unit
  cat > "$SYSTEMD_USER_DIR/${WATCHDOG_SERVICE}.service" <<EOF
[Unit]
Description=AMCP Watchdog — health monitor and recovery
After=network.target

[Service]
Type=simple
ExecStart=${SCRIPT_DIR}/watchdog.sh --continuous
Restart=on-failure
RestartSec=30
Environment=CHECK_INTERVAL=${interval}
Environment=IDENTITY_PATH=${IDENTITY_PATH}
Environment=AGENT_NAME=${AGENT_NAME}

[Install]
WantedBy=default.target
EOF
  ok "Wrote ${WATCHDOG_SERVICE}.service"

  # Reload and enable
  systemctl --user daemon-reload
  systemctl --user enable "$WATCHDOG_SERVICE" 2>/dev/null || true

  if prompt_yn "Start watchdog now?"; then
    systemctl --user restart "$WATCHDOG_SERVICE"
    ok "Watchdog started (interval: ${interval}s)"
    info "Check status: systemctl --user status $WATCHDOG_SERVICE"
  else
    info "Start later: systemctl --user start $WATCHDOG_SERVICE"
  fi
}

setup_watchdog_cron() {
  local interval="$1"
  local cron_expr

  # Convert seconds to nearest cron-compatible minute interval
  local mins=$(( interval / 60 ))
  [ "$mins" -lt 1 ] && mins=1

  if [ "$mins" -lt 60 ]; then
    cron_expr="*/$mins * * * *"
  else
    cron_expr="0 */$((mins / 60)) * * *"
  fi

  local cron_line="$cron_expr ${SCRIPT_DIR}/watchdog.sh # amcp-watchdog"

  # Check if already installed
  if crontab -l 2>/dev/null | grep -q "# amcp-watchdog"; then
    info "Watchdog cron entry already exists — updating"
    # Remove old entry, add new
    crontab -l 2>/dev/null | grep -v "# amcp-watchdog" | { cat; echo "$cron_line"; } | crontab -
  else
    # Append to existing crontab
    { crontab -l 2>/dev/null || true; echo "$cron_line"; } | crontab -
  fi

  ok "Watchdog cron installed: $cron_expr"
  info "View: crontab -l | grep amcp"
}

# ============================================================
# Step 4: Checkpoint schedule
# ============================================================

setup_checkpoint() {
  header "Step 4: Checkpoint Schedule"

  local schedule
  schedule=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('checkpoint',{}).get('schedule', '$CHECKPOINT_SCHEDULE'))" 2>/dev/null || echo "$CHECKPOINT_SCHEDULE")

  # Try systemd timer first
  if command -v systemctl &>/dev/null && systemctl --user status &>/dev/null 2>&1; then
    info "systemd user session available — setting up timer"
    setup_checkpoint_systemd "$schedule"
  else
    info "systemd not available — falling back to cron"
    setup_checkpoint_cron "$schedule"
  fi
}

setup_checkpoint_systemd() {
  local schedule="$1"

  mkdir -p "$SYSTEMD_USER_DIR"

  # Convert cron to OnCalendar (best-effort)
  local on_calendar
  on_calendar=$(cron_to_oncalendar "$schedule")

  # Write service unit
  cat > "$SYSTEMD_USER_DIR/${CHECKPOINT_TIMER}.service" <<EOF
[Unit]
Description=AMCP Checkpoint — encrypt and pin to IPFS

[Service]
Type=oneshot
ExecStart=${SCRIPT_DIR}/checkpoint.sh --notify
Environment=IDENTITY_PATH=${IDENTITY_PATH}
Environment=AGENT_NAME=${AGENT_NAME}
EOF

  # Write timer unit
  cat > "$SYSTEMD_USER_DIR/${CHECKPOINT_TIMER}.timer" <<EOF
[Unit]
Description=AMCP Checkpoint Timer

[Timer]
OnCalendar=${on_calendar}
Persistent=true

[Install]
WantedBy=timers.target
EOF

  ok "Wrote ${CHECKPOINT_TIMER}.service + .timer"

  systemctl --user daemon-reload
  systemctl --user enable "${CHECKPOINT_TIMER}.timer" 2>/dev/null || true

  if prompt_yn "Start checkpoint timer now?"; then
    systemctl --user start "${CHECKPOINT_TIMER}.timer"
    ok "Checkpoint timer started: $on_calendar"
    info "Check: systemctl --user list-timers | grep amcp"
  else
    info "Start later: systemctl --user start ${CHECKPOINT_TIMER}.timer"
  fi
}

cron_to_oncalendar() {
  local cron="$1"
  # Best-effort cron → systemd OnCalendar conversion
  # Handles common patterns; falls back to hourly
  local min hour dom mon dow
  read -r min hour dom mon dow <<< "$cron"

  # "0 */4 * * *" → "*-*-* 0/4:00:00"
  if [[ "$min" == "0" && "$hour" == "*/"* && "$dom" == "*" && "$mon" == "*" && "$dow" == "*" ]]; then
    local step="${hour#*/}"
    echo "*-*-* 0/${step}:00:00"
    return
  fi

  # "*/N * * * *" → "*-*-* *:0/N:00"
  if [[ "$min" == "*/"* && "$hour" == "*" && "$dom" == "*" && "$mon" == "*" && "$dow" == "*" ]]; then
    local step="${min#*/}"
    echo "*-*-* *:0/${step}:00"
    return
  fi

  # "M H * * *" → "*-*-* H:M:00"
  if [[ "$dom" == "*" && "$mon" == "*" && "$dow" == "*" ]]; then
    echo "*-*-* ${hour}:${min}:00"
    return
  fi

  # Fallback
  echo "*-*-* *:00:00"
}

setup_checkpoint_cron() {
  local schedule="$1"
  local cron_line="$schedule ${SCRIPT_DIR}/checkpoint.sh --notify # amcp-checkpoint"

  # Check if already installed
  if crontab -l 2>/dev/null | grep -q "# amcp-checkpoint"; then
    info "Checkpoint cron entry already exists — updating"
    crontab -l 2>/dev/null | grep -v "# amcp-checkpoint" | { cat; echo "$cron_line"; } | crontab -
  else
    { crontab -l 2>/dev/null || true; echo "$cron_line"; } | crontab -
  fi

  ok "Checkpoint cron installed: $schedule"
  info "View: crontab -l | grep amcp"
}
