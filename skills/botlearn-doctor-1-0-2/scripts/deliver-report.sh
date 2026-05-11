#!/bin/bash
# deliver-report.sh — Multi-channel report delivery
# Usage:
#   deliver-report.sh --input <scored-report.json> [--channel terminal|browser|slack|dingtalk|feishu|discord|email|auto]
#   deliver-report.sh --input <scored-report.json> --md <report.md> --html <report.html> [--channel auto]
# Timeout: 15s | Compatible: macOS (darwin) + Linux
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
CHANNEL_CONFIG="${OPENCLAW_HOME}/config/doctor-channels.json"

INPUT=""
MD_FILE=""
HTML_FILE=""
CHANNEL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --input)   INPUT="$2"; shift 2 ;;
    --md)      MD_FILE="$2"; shift 2 ;;
    --html)    HTML_FILE="$2"; shift 2 ;;
    --channel) CHANNEL="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "$INPUT" || ! -f "$INPUT" ]]; then
  echo '{"error":"--input <scored-report.json> required"}' >&2
  exit 1
fi

node -e '
const fs = require("fs");
const { execSync } = require("child_process");
const path = require("path");

const report = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
const mdFile = process.argv[2] || "";
const htmlFile = process.argv[3] || "";
const requestedChannel = process.argv[4] || "";
const channelConfigPath = process.argv[5];
const scriptDir = process.argv[6];

// Load channel config
let config = {
  default_channel: "terminal",
  channels: {
    terminal: { enabled: true },
    browser: { enabled: true, auto_open_on_macos: true }
  }
};
try {
  if (fs.existsSync(channelConfigPath)) {
    config = JSON.parse(fs.readFileSync(channelConfigPath, "utf8"));
  }
} catch {}

// Determine channels to deliver to
let channels = [];
if (requestedChannel && requestedChannel !== "auto") {
  channels = [requestedChannel];
} else {
  // Auto mode: deliver to all enabled channels
  for (const [name, ch] of Object.entries(config.channels || {})) {
    if (ch.enabled) channels.push(name);
  }
  if (channels.length === 0) channels = ["terminal"];
}

function statusEmoji(score) {
  if (score >= 80) return "✅";
  if (score >= 60) return "⚠️";
  if (score >= 40) return "🟡";
  return "🔴";
}

// Redact secrets from payload before sending
function redactSecrets(text) {
  return text.replace(
    /(?:api[_-]?key|apikey|secret|client_secret|token|access_token|bearer|password|passwd|pwd)\s*[:=]\s*["'"'"']?[A-Za-z0-9_\-\.]{8,}/gi,
    (match) => match.replace(/[:=]\s*["'"'"']?[A-Za-z0-9_\-\.]{8,}/, "= ***REDACTED***")
  );
}

const cs = report.category_scores || {};
const results = [];

for (const channel of channels) {
  try {
    switch (channel) {
      case "terminal": {
        // Output MD to terminal
        if (mdFile && fs.existsSync(mdFile)) {
          const md = fs.readFileSync(mdFile, "utf8");
          process.stderr.write(md + "\n");
        } else {
          const dims = Object.entries(cs).map(([k, v]) =>
            k.substring(0, 4).toUpperCase() + " " + statusEmoji(v.score) + " " + v.score
          ).join(" | ");
          process.stderr.write(
            "🏥 OpenClaw Health: " + report.overall_score + "/100 " + statusEmoji(report.overall_score) + "\n" +
            dims + "\n" +
            "⚡ " + ((report.issue_summary?.critical || 0) + (report.issue_summary?.high || 0)) + " issues need attention\n"
          );
        }
        results.push({ channel: "terminal", status: "delivered" });
        break;
      }

      case "browser": {
        if (htmlFile && fs.existsSync(htmlFile)) {
          const openScript = path.join(scriptDir, "open-report.sh");
          const autoOpen = config.channels?.browser?.auto_open_on_macos !== false;
          const os = process.platform;
          if (os === "darwin" && autoOpen) {
            try {
              execSync("bash " + JSON.stringify(openScript) + " " + JSON.stringify(htmlFile), { timeout: 5000 });
              results.push({ channel: "browser", status: "opened" });
            } catch {
              results.push({ channel: "browser", status: "failed", error: "Could not open browser" });
            }
          } else {
            results.push({ channel: "browser", status: "skipped", reason: "Not macOS or auto_open disabled", file: htmlFile });
          }
        } else {
          results.push({ channel: "browser", status: "skipped", reason: "No HTML report file" });
        }
        break;
      }

      case "slack": {
        const webhook = config.channels?.slack?.webhook_url;
        if (!webhook) { results.push({ channel: "slack", status: "skipped", reason: "No webhook_url" }); break; }
        const issues = (report.issues || []).slice(0, 5);
        const issuesMd = issues.map((i, idx) => (idx+1) + ". " + i.severity.toUpperCase() + " [" + i.id + "] " + i.msg).join("\\n");
        const payload = JSON.stringify({
          blocks: [
            { type: "header", text: { type: "plain_text", text: "🏥 OpenClaw Health Report" } },
            { type: "section", fields: [
              { type: "mrkdwn", text: "*Score:* " + report.overall_score + "/100 " + statusEmoji(report.overall_score) },
              { type: "mrkdwn", text: "*Status:* " + report.overall_status }
            ]},
            { type: "section", text: { type: "mrkdwn", text: issuesMd || "No issues found" } }
          ]
        });
        const safe = redactSecrets(payload);
        execSync("curl -sS -X POST -H \"Content-Type: application/json\" -d " + JSON.stringify(safe) + " " + JSON.stringify(webhook), { timeout: 10000 });
        results.push({ channel: "slack", status: "delivered" });
        break;
      }

      case "dingtalk": {
        const webhook = config.channels?.dingtalk?.webhook_url;
        if (!webhook) { results.push({ channel: "dingtalk", status: "skipped", reason: "No webhook_url" }); break; }
        const issues = (report.issues || []).slice(0, 5);
        const issuesMd = issues.map((i, idx) => (idx+1) + ". " + i.severity + " [" + i.id + "] " + i.msg).join("\\n");
        const payload = JSON.stringify({
          msgtype: "markdown",
          markdown: {
            title: "🏥 OpenClaw 健康报告",
            text: "# 🏥 OpenClaw 健康报告\\n\\n**分数: " + report.overall_score + "/100** " + statusEmoji(report.overall_score) + "\\n\\n" + issuesMd
          }
        });
        const safe = redactSecrets(payload);
        execSync("curl -sS -X POST -H \"Content-Type: application/json\" -d " + JSON.stringify(safe) + " " + JSON.stringify(webhook), { timeout: 10000 });
        results.push({ channel: "dingtalk", status: "delivered" });
        break;
      }

      case "feishu": {
        const webhook = config.channels?.feishu?.webhook_url;
        if (!webhook) { results.push({ channel: "feishu", status: "skipped", reason: "No webhook_url" }); break; }
        const templateColor = report.overall_score >= 80 ? "green" : report.overall_score >= 60 ? "yellow" : report.overall_score >= 40 ? "orange" : "red";
        const payload = JSON.stringify({
          msg_type: "interactive",
          card: {
            header: {
              title: { tag: "plain_text", content: "🏥 OpenClaw 健康报告" },
              template: templateColor
            },
            elements: [
              { tag: "div", fields: [
                { is_short: true, text: { tag: "lark_md", content: "**总分**\\n" + report.overall_score + "/100" } },
                { is_short: true, text: { tag: "lark_md", content: "**状态**\\n" + report.overall_status } }
              ]}
            ]
          }
        });
        const safe = redactSecrets(payload);
        execSync("curl -sS -X POST -H \"Content-Type: application/json\" -d " + JSON.stringify(safe) + " " + JSON.stringify(webhook), { timeout: 10000 });
        results.push({ channel: "feishu", status: "delivered" });
        break;
      }

      case "discord": {
        const webhook = config.channels?.discord?.webhook_url;
        if (!webhook) { results.push({ channel: "discord", status: "skipped", reason: "No webhook_url" }); break; }
        const colorMap = { healthy: 2280667, warning: 15379208, elevated: 16348950, critical: 15614020 };
        const fields = Object.entries(cs).map(([k, v]) => ({
          name: k.charAt(0).toUpperCase() + k.slice(1),
          value: statusEmoji(v.score) + " " + v.score + "/100",
          inline: true
        }));
        const payload = JSON.stringify({
          embeds: [{
            title: "🏥 OpenClaw Health Report",
            description: "Score: **" + report.overall_score + "/100** · Status: **" + report.overall_status + "**",
            color: colorMap[report.overall_status] || 2280667,
            fields: fields,
            footer: { text: "@botlearn/botlearn-healthcheck v3.0.0" },
            timestamp: report.timestamp
          }]
        });
        const safe = redactSecrets(payload);
        execSync("curl -sS -X POST -H \"Content-Type: application/json\" -d " + JSON.stringify(safe) + " " + JSON.stringify(webhook), { timeout: 10000 });
        results.push({ channel: "discord", status: "delivered" });
        break;
      }

      case "email": {
        const emailConf = config.channels?.email;
        if (!emailConf?.to) { results.push({ channel: "email", status: "skipped", reason: "No recipient" }); break; }
        const subject = (emailConf.subject_prefix || "[OpenClaw Doctor]") + " Health Report — " + report.overall_score + "/100 " + report.overall_status;
        const from = emailConf.from || "OpenClaw Doctor <noreply@localhost>";
        const htmlContent = htmlFile && fs.existsSync(htmlFile) ? fs.readFileSync(htmlFile, "utf8") : "<p>Score: " + report.overall_score + "/100</p>";
        const safeHtml = redactSecrets(htmlContent);
        const emailPayload = "From: " + from + "\\nTo: " + emailConf.to + "\\nSubject: " + subject + "\\nContent-Type: text/html; charset=UTF-8\\n\\n" + safeHtml;
        const tmpFile = "/tmp/doctor-email-" + Date.now() + ".eml";
        fs.writeFileSync(tmpFile, emailPayload);
        try {
          const host = emailConf.smtp_host || "localhost";
          const port = emailConf.smtp_port || 25;
          execSync("sendmail -t < " + JSON.stringify(tmpFile) + " 2>/dev/null || curl --url smtp://" + host + ":" + port + " --mail-from " + JSON.stringify(from) + " --mail-rcpt " + JSON.stringify(emailConf.to) + " --upload-file " + JSON.stringify(tmpFile), { timeout: 10000 });
          results.push({ channel: "email", status: "delivered", to: emailConf.to });
        } catch {
          results.push({ channel: "email", status: "failed", error: "sendmail/smtp delivery failed" });
        }
        try { fs.unlinkSync(tmpFile); } catch {}
        break;
      }

      default:
        results.push({ channel, status: "unknown_channel" });
    }
  } catch (e) {
    results.push({ channel, status: "error", error: e.message });
  }
}

console.log(JSON.stringify({ delivered: results, total_channels: results.length }, null, 2));
' "$INPUT" "$MD_FILE" "$HTML_FILE" "$CHANNEL" "$CHANNEL_CONFIG" "$SCRIPT_DIR"
