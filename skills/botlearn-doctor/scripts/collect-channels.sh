#!/bin/bash
# collect-channels.sh — Query OpenClaw platform registered channels, output JSON
# Timeout: 10s | Compatible: macOS (darwin) + Linux
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
OPENCLAW_CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-$OPENCLAW_HOME/openclaw.json}"
CHANNEL_CONFIG="${OPENCLAW_HOME}/config/doctor-channels.json"

node -e '
const fs = require("fs");
const path = require("path");

const HOME = process.env.OPENCLAW_HOME || (process.env.HOME + "/.openclaw");
const CONFIG = process.env.OPENCLAW_CONFIG_PATH || (HOME + "/openclaw.json");
const CHANNEL_CONFIG = HOME + "/config/doctor-channels.json";

const result = {
  timestamp: new Date().toISOString(),
  channels: [],
  channel_config_exists: false,
  channel_config_valid: false,
  enabled_count: 0,
  disabled_count: 0,
  issues: []
};

// Check doctor-channels.json
if (fs.existsSync(CHANNEL_CONFIG)) {
  result.channel_config_exists = true;
  try {
    const channelConf = JSON.parse(fs.readFileSync(CHANNEL_CONFIG, "utf8"));
    result.channel_config_valid = true;
    result.default_channel = channelConf.default_channel || "terminal";

    const channels = channelConf.channels || {};
    for (const [name, conf] of Object.entries(channels)) {
      const enabled = conf.enabled === true;
      const ch = {
        name,
        enabled,
        has_webhook: !!(conf.webhook_url && conf.webhook_url.length > 0),
        configured: false
      };

      // Check if properly configured
      if (name === "terminal" || name === "browser") {
        ch.configured = true; // always configured
      } else if (name === "email") {
        ch.configured = !!(conf.to && conf.to.length > 0);
        if (enabled && !ch.configured) {
          result.issues.push({ channel: name, issue: "Email enabled but no recipient configured" });
        }
      } else {
        ch.configured = ch.has_webhook;
        if (enabled && !ch.configured) {
          result.issues.push({ channel: name, issue: name + " enabled but no webhook_url configured" });
        }
      }

      if (enabled) result.enabled_count++;
      else result.disabled_count++;

      result.channels.push(ch);
    }
  } catch (e) {
    result.issues.push({ channel: "config", issue: "Invalid JSON in doctor-channels.json: " + e.message });
  }
} else {
  result.issues.push({ channel: "config", issue: "Channel config not found at " + CHANNEL_CONFIG.replace(process.env.HOME, "~") });
}

// Check OpenClaw main config for channel-related settings
if (fs.existsSync(CONFIG)) {
  try {
    const raw = fs.readFileSync(CONFIG, "utf8");
    const clean = raw.replace(/\/\/.*$/gm, "").replace(/\/\*[\s\S]*?\*\//g, "");
    const config = JSON.parse(clean);

    // Check if messages section has channel config
    if (config.messages) {
      result.platform_channels = {
        messages_section_exists: true,
        notification_channels: config.messages.channels || [],
        webhook_count: (config.messages.webhooks || []).length
      };
    }
  } catch {}
}

// Check clawhub channel list if available
result.clawhub_available = false;
console.log(JSON.stringify(result, null, 2));
' 2>/dev/null

# Augment with clawhub channel list if CLI available
if command -v clawhub &>/dev/null; then
  CLAWHUB_CHANNELS=$(clawhub channels list --json 2>/dev/null || echo "")
  if [[ -n "$CLAWHUB_CHANNELS" ]]; then
    # Merge clawhub channels into result
    node -e '
      const result = JSON.parse(process.argv[1]);
      result.clawhub_available = true;
      try {
        result.clawhub_channels = JSON.parse(process.argv[2]);
      } catch {
        result.clawhub_channels = [];
      }
      console.log(JSON.stringify(result, null, 2));
    ' "$(cat /dev/stdin)" "$CLAWHUB_CHANNELS" <<< "$(node -e '
      const fs = require("fs");
      const HOME = process.env.OPENCLAW_HOME || (process.env.HOME + "/.openclaw");
      const CHANNEL_CONFIG = HOME + "/config/doctor-channels.json";
      const result = {
        timestamp: new Date().toISOString(),
        channels: [],
        channel_config_exists: fs.existsSync(CHANNEL_CONFIG),
        clawhub_available: true
      };
      console.log(JSON.stringify(result));
    ')"
  fi
fi
