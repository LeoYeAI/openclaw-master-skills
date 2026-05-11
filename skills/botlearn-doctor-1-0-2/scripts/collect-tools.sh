#!/bin/bash
# collect-tools.sh — Check MCP tools and CLI tools availability, output JSON
# Checks: MCP tools (memory_search, file_read, bash, etc.) + CLI tools (clawhub, openclaw, node, curl)
# Timeout: 10s | Compatible: macOS (darwin) + Linux
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
OPENCLAW_CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-$OPENCLAW_HOME/openclaw.json}"

node <<'NODESCRIPT'
const fs = require("fs");
const { execSync } = require("child_process");

const HOME = process.env.OPENCLAW_HOME || (process.env.HOME + "/.openclaw");
const CONFIG = process.env.OPENCLAW_CONFIG_PATH || (HOME + "/openclaw.json");

const result = {
  timestamp: new Date().toISOString(),
  cli_tools: [],
  mcp_tools: [],
  summary: {
    cli_total: 0, cli_available: 0, cli_missing: 0,
    mcp_total: 0, mcp_available: 0, mcp_missing: 0,
    core_missing: []
  },
  issues: []
};

// --- 1. CLI Tools Check ---
const cliTools = [
  { name: "node",     core: true,  check: "node --version" },
  { name: "curl",     core: true,  check: "curl --version" },
  { name: "bash",     core: true,  check: "bash --version" },
  { name: "clawhub",  core: false, check: "clawhub --version", anyOf: "openclaw" },
  { name: "openclaw", core: false, check: "openclaw --version", anyOf: "clawhub" },
  { name: "git",      core: false, check: "git --version" },
  { name: "jq",       core: false, check: "jq --version" },
  { name: "sendmail", core: false, check: "which sendmail" }
];

for (const tool of cliTools) {
  const entry = { name: tool.name, core: tool.core, available: false, version: null };
  try {
    const out = execSync(tool.check, { timeout: 5000, encoding: "utf8", stdio: ["pipe", "pipe", "pipe"] }).trim();
    entry.available = true;
    // Extract version string (first line, first version-like match)
    const verMatch = out.match(/v?(\d+\.\d+[\.\d]*)/);
    if (verMatch) entry.version = verMatch[0];
  } catch {}
  result.cli_tools.push(entry);
}

// Check anyOf pairs (clawhub OR openclaw)
const clawhubAvail = result.cli_tools.find(t => t.name === "clawhub")?.available;
const openclawAvail = result.cli_tools.find(t => t.name === "openclaw")?.available;
if (!clawhubAvail && !openclawAvail) {
  result.issues.push({ type: "cli", severity: "error", msg: "Neither clawhub nor openclaw CLI found — at least one is required" });
  result.summary.core_missing.push("clawhub|openclaw");
}

// --- 2. MCP Tools Check ---
// MCP tools are registered via OpenClaw config tools section
// We check if the config declares them and if the tools endpoint is reachable
const mcpTools = [
  { name: "memory_search", core: true,  description: "Search agent memory" },
  { name: "memory_inject",  core: true,  description: "Inject knowledge into memory" },
  { name: "file_read",     core: true,  description: "Read files from filesystem" },
  { name: "file_write",    core: false, description: "Write files to filesystem" },
  { name: "bash",          core: true,  description: "Execute shell commands" },
  { name: "web_fetch",     core: false, description: "Fetch web content" },
  { name: "web_search",    core: false, description: "Search the web" },
  { name: "skill_invoke",  core: false, description: "Invoke other skills" }
];

// Check config for tools profile
let toolsProfile = "unknown";
let configuredTools = [];
if (fs.existsSync(CONFIG)) {
  try {
    const raw = fs.readFileSync(CONFIG, "utf8");
    const clean = raw.replace(/\/\/.*$/gm, "").replace(/\/\*[\s\S]*?\*\//g, "");
    const config = JSON.parse(clean);
    toolsProfile = config.tools?.profile || "default";
    configuredTools = config.tools?.enabled || [];

    // If tools section has MCP server config
    if (config.tools?.mcp) {
      const mcpConfig = config.tools.mcp;
      for (const [server, serverConf] of Object.entries(mcpConfig)) {
        if (serverConf.tools) {
          configuredTools.push(...serverConf.tools);
        }
      }
    }
  } catch {}
}

// Check MCP tools availability via Gateway API (if reachable)
let gatewayTools = null;
try {
  const port = 18789;
  const out = execSync(
    `curl -s --connect-timeout 3 --max-time 5 http://localhost:${port}/tools 2>/dev/null`,
    { timeout: 6000, encoding: "utf8", stdio: ["pipe", "pipe", "pipe"] }
  );
  if (out) {
    try {
      const parsed = JSON.parse(out);
      gatewayTools = Array.isArray(parsed) ? parsed.map(t => t.name || t) :
                     parsed.tools ? parsed.tools.map(t => t.name || t) : null;
    } catch {}
  }
} catch {}

for (const tool of mcpTools) {
  const entry = {
    name: tool.name,
    core: tool.core,
    description: tool.description,
    configured: configuredTools.includes(tool.name),
    available: false
  };

  // If we got gateway tools list, check against it
  if (gatewayTools) {
    entry.available = gatewayTools.includes(tool.name);
  } else {
    // Assume available if configured or profile is full/coding
    entry.available = entry.configured || ["full", "coding"].includes(toolsProfile);
  }

  result.mcp_tools.push(entry);
}

// --- 3. Summary ---
result.summary.cli_total = result.cli_tools.length;
result.summary.cli_available = result.cli_tools.filter(t => t.available).length;
result.summary.cli_missing = result.summary.cli_total - result.summary.cli_available;

result.summary.mcp_total = result.mcp_tools.length;
result.summary.mcp_available = result.mcp_tools.filter(t => t.available).length;
result.summary.mcp_missing = result.summary.mcp_total - result.summary.mcp_available;

// Check for missing core tools
for (const t of result.cli_tools) {
  if (t.core && !t.available) {
    result.summary.core_missing.push(t.name);
    result.issues.push({ type: "cli", severity: "error", msg: "Core CLI tool missing: " + t.name });
  }
}
for (const t of result.mcp_tools) {
  if (t.core && !t.available) {
    result.summary.core_missing.push(t.name);
    result.issues.push({ type: "mcp", severity: "error", msg: "Core MCP tool missing: " + t.name });
  }
}

// Non-core missing → warnings
for (const t of [...result.cli_tools, ...result.mcp_tools]) {
  if (!t.core && !t.available) {
    result.issues.push({ type: t.version !== undefined ? "cli" : "mcp", severity: "warning", msg: "Optional tool missing: " + t.name });
  }
}

result.tools_profile = toolsProfile;
result.gateway_tools_reachable = gatewayTools !== null;

console.log(JSON.stringify(result, null, 2));
NODESCRIPT
