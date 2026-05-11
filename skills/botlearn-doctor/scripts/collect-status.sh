#!/bin/bash
# collect-status.sh — Run openclaw status --all --deep, parse output to JSON
# Parses: Overview table, Channels table, Agents table, Diagnosis section, gateway logs
# Timeout: 25s | Compatible: macOS (darwin) + Linux
set -uo pipefail

if ! command -v openclaw &>/dev/null; then
  echo '{"ran":false,"error":"openclaw CLI not found"}'
  exit 0
fi

# Capture full output (stdout + stderr merged, timeout guard)
raw_output=$(timeout 20 openclaw status --all --deep 2>&1) || true

# Try --json flag first (future-proofing)
json_output=$(timeout 20 openclaw status --all --deep --json 2>/dev/null) || json_output=""
if echo "$json_output" | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8'); JSON.parse(d); process.exit(0);" 2>/dev/null; then
  # Structured JSON available — wrap with metadata and pass through
  echo "$json_output" | node -e "
    let d=''; process.stdin.on('data',c=>d+=c).on('end',()=>{
      const s = JSON.parse(d);
      console.log(JSON.stringify({ran:true,source:'json',timestamp:new Date().toISOString(),...s}, null, 2));
    });
  "
  exit 0
fi

# ─── Text output parsing via Node.js ─────────────────────────────────────────
echo "$raw_output" | node -e "
const readline = require('readline');
let raw = '';
process.stdin.on('data', c => raw += c);
process.stdin.on('end', () => {
  const lines = raw.split('\n');

  // ── Helpers ────────────────────────────────────────────────────────────────
  function isSeparator(line) {
    return /^[├┤┌┐└┘─┼┬┴╋═│\s]+$/.test(line.trim()) && line.includes('─');
  }
  function parseBoxRows(sectionLines) {
    // Returns array of cell arrays (one per data row, skipping separator rows)
    const rows = [];
    for (const line of sectionLines) {
      if (!line.includes('│')) continue;
      if (isSeparator(line)) continue;
      const cells = line.split('│').slice(1, -1).map(c => c.trim());
      if (cells.length > 0) rows.push(cells);
    }
    return rows;
  }

  // ── Section detection ──────────────────────────────────────────────────────
  const sections = { header: [], overview: [], channels: [], agents: [], diagnosis: [] };
  let currentSection = 'header';

  for (const line of lines) {
    const t = line.trim();
    if (t === 'Overview')            { currentSection = 'overview';  continue; }
    if (t === 'Channels')            { currentSection = 'channels';  continue; }
    if (t === 'Agents')              { currentSection = 'agents';    continue; }
    if (t.startsWith('Diagnosis'))   { currentSection = 'diagnosis'; continue; }
    sections[currentSection].push(line);
  }

  // ── Parse header (version + commit) ───────────────────────────────────────
  const headerText = sections.header.join(' ');
  const versionMatch = headerText.match(/OpenClaw\s+([0-9]+\.[0-9]+[^\s(]*)/);
  const commitMatch  = headerText.match(/\(([0-9a-f]{6,})\)/);
  const version = versionMatch ? versionMatch[1] : null;
  const commit  = commitMatch  ? commitMatch[1]  : null;

  // ── Parse Overview table ───────────────────────────────────────────────────
  const overviewRows = parseBoxRows(sections.overview);
  const overviewMap = {};
  // First row is header (Item, Value) — skip it
  for (let i = 1; i < overviewRows.length; i++) {
    const [key, ...rest] = overviewRows[i];
    if (key) overviewMap[key.trim()] = rest.join(' │ ').trim();
  }

  // Extract structured fields from Overview values
  function parseGateway(raw) {
    if (!raw) return {};
    const latencyMatch = raw.match(/reachable\s+(\d+)ms/);
    const authMatch    = raw.match(/auth\s+(\w+)/);
    const bindMatch    = raw.match(/\(([^)]+)\)/);
    const urlMatch     = raw.match(/(wss?:\/\/[^\s]+)/);
    return {
      raw,
      url:         urlMatch    ? urlMatch[1]    : null,
      bind:        bindMatch   ? bindMatch[1]   : null,
      latency_ms:  latencyMatch ? parseInt(latencyMatch[1]) : null,
      auth_type:   authMatch   ? authMatch[1]   : null
    };
  }
  function parseService(raw) {
    if (!raw) return { installed: false, running: false };
    const pidMatch = raw.match(/pid\s+(\d+)/);
    return {
      installed: raw.includes('installed') && !raw.includes('not installed'),
      loaded:    raw.includes('loaded'),
      running:   raw.includes('running'),
      pid:       pidMatch ? parseInt(pidMatch[1]) : null,
      raw
    };
  }
  function parseAgentsOverview(raw) {
    if (!raw) return {};
    const totalMatch   = raw.match(/(\d+)\s+total/);
    const bootMatch    = raw.match(/(\d+)\s+bootstrapping/);
    const activeMatch  = raw.match(/(\d+)\s+active/);
    const sessionMatch = raw.match(/(\d+)\s+session/);
    return {
      total:         totalMatch   ? parseInt(totalMatch[1])   : 0,
      bootstrapping: bootMatch    ? parseInt(bootMatch[1])    : 0,
      active:        activeMatch  ? parseInt(activeMatch[1])  : 0,
      sessions:      sessionMatch ? parseInt(sessionMatch[1]) : 0
    };
  }

  const gwRaw = overviewMap['Gateway'] || '';
  const overview = {
    version:         overviewMap['Version']         || null,
    os:              overviewMap['OS']               || null,
    node:            overviewMap['Node']             || null,
    config_path:     overviewMap['Config']           || null,
    dashboard:       overviewMap['Dashboard']        || null,
    tailscale:       overviewMap['Tailscale']        || 'unknown',
    tailscale_on:    (overviewMap['Tailscale'] || '').toLowerCase() !== 'off',
    update_channel:  overviewMap['Channel']          || null,
    update_status:   overviewMap['Update']           || null,
    gateway:         parseGateway(gwRaw),
    security_note:   overviewMap['Security']         || null,
    gateway_self:    overviewMap['Gateway self']     || null,
    gateway_service: parseService(overviewMap['Gateway service']),
    node_service:    parseService(overviewMap['Node service']),
    agents_overview: parseAgentsOverview(overviewMap['Agents'])
  };

  // Is update available? If update_status contains a higher version, flag it
  const updateRaw = overview.update_status || '';
  const latestMatch = updateRaw.match(/latest\s+([0-9]+\.[0-9]+[^\s]*)/);
  overview.latest_version = latestMatch ? latestMatch[1] : null;
  overview.up_to_date = !latestMatch ||
    (overview.version && latestMatch[1] === overview.version);

  // ── Parse Channels table ───────────────────────────────────────────────────
  const channelRows = parseBoxRows(sections.channels);
  const channels = [];
  if (channelRows.length > 1) {
    // Row 0 = headers: Channel, Enabled, State, Detail
    for (let i = 1; i < channelRows.length; i++) {
      const r = channelRows[i];
      if (r[0]) channels.push({
        name:    r[0] || '',
        enabled: (r[1] || '').toLowerCase() === 'true' || r[1] === '✓',
        state:   r[2] || '',
        detail:  r[3] || ''
      });
    }
  }

  // ── Parse Agents table ─────────────────────────────────────────────────────
  const agentRows = parseBoxRows(sections.agents);
  const agents = [];
  if (agentRows.length > 1) {
    // Headers: Agent, Bootstrap file, Sessions, Active, Store
    for (let i = 1; i < agentRows.length; i++) {
      const r = agentRows[i];
      if (r[0]) agents.push({
        name:              r[0] || '',
        bootstrap_file:    r[1] || '',
        bootstrap_present: r[1] !== 'ABSENT' && r[1] !== '' && r[1] !== 'none',
        sessions:          parseInt(r[2]) || 0,
        active_since:      r[3] || '',
        store_path:        (r[4] || '').replace(/^~/, process.env.HOME || '~')
      });
    }
  }

  // ── Parse Diagnosis section ────────────────────────────────────────────────
  const checks = [];
  const logLines = [];
  const logIssues = [];
  let inLogs = false;
  let skillsEligible = 0, skillsMissing = 0;

  for (const line of sections.diagnosis) {
    const t = line.trim();

    // Log section detection
    if (t.startsWith('Gateway logs') || t.startsWith('# stderr') || t.startsWith('# stdout')) {
      inLogs = true;
    }

    if (inLogs) {
      // Collect notable log lines (errors, warnings, timeouts)
      if (t.match(/timeout|ENOENT|error|timed out|LLM|failed|ENOENT|command not found/i)) {
        const redacted = t.replace(/(token|secret|password|api.?key)[^\s]*/gi, '[REDACTED]');
        logLines.push(redacted);
        if (logLines.length <= 20) logIssues.push(redacted);
      }
      continue;
    }

    // Check lines
    if (t.startsWith('✓') || t.startsWith('!') || t.startsWith('·')) {
      const status = t.startsWith('✓') ? 'ok' : t.startsWith('!') ? 'warn' : 'info';
      const rest = t.slice(1).trim();
      const colonIdx = rest.indexOf(':');
      const label  = colonIdx >= 0 ? rest.slice(0, colonIdx).trim() : rest;
      const detail = colonIdx >= 0 ? rest.slice(colonIdx + 1).trim() : '';

      // Extract skills count
      if (label === 'Skills') {
        const em = detail.match(/(\d+)\s+eligible/);
        const mm = detail.match(/(\d+)\s+missing/);
        if (em) skillsEligible = parseInt(em[1]);
        if (mm) skillsMissing  = parseInt(mm[1]);
      }

      checks.push({ status, label, detail });
    }
  }

  // ── Assemble output ────────────────────────────────────────────────────────
  const result = {
    ran:       true,
    source:    'text',
    timestamp: new Date().toISOString(),
    version,
    commit,
    overview,
    channels,
    agents,
    diagnosis: {
      checks,
      skills_eligible: skillsEligible,
      skills_missing:  skillsMissing,
      config_valid:    checks.some(c => c.label === 'Config' && c.status === 'ok'),
      port_conflicts:  checks.filter(c => c.label.startsWith('Port') && c.status === 'warn').map(c => c.detail),
      tailscale_issue: checks.some(c => c.label === 'Tailscale' && c.status === 'warn'),
      channel_issues:  checks.some(c => c.label.startsWith('Channel') && c.status === 'warn')
    },
    log_issues: logIssues
  };

  console.log(JSON.stringify(result, null, 2));
});
"
