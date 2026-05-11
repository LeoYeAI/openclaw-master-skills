/**
 * cost-dashboard.js — Generate an HTML cost dashboard for OpenClaw Canvas
 * Usage: node cost-dashboard.js [config-path]
 * Outputs HTML that can be presented via the canvas tool
 */

const fs = require('fs');

const configPath = process.argv[2] || `${process.env.HOME}/.openclaw/openclaw.json`;

let config;
try {
  const raw = fs.readFileSync(configPath, 'utf8');
  config = new Function('return (' + raw + ')')();
} catch (e) {
  console.error(`Failed to parse config: ${e.message}`);
  process.exit(1);
}

const defaults = config.agents?.defaults || {};
const model = defaults.model;
const primary = typeof model === 'string' ? model : model?.primary || 'unknown';
const fallbacks = typeof model === 'object' ? (model.fallbacks || []) : [];
const heartbeat = defaults.heartbeat || {};
const memFlush = defaults.compaction?.memoryFlush || {};
const aliases = defaults.models || {};

// Cost database
const modelCosts = {
  'anthropic/claude-opus-4-6': { name: 'Opus 4.6', tier: 'Premium', perReq: 0.71, color: '#e74c3c' },
  'anthropic/claude-sonnet-4-6': { name: 'Sonnet 4.6', tier: 'Quality', perReq: 0.53, color: '#e67e22' },
  'anthropic/claude-haiku-4-5': { name: 'Haiku 4.5', tier: 'Mid', perReq: 0.15, color: '#f1c40f' },
  'deepseek/deepseek-v3.2': { name: 'DeepSeek V3.2', tier: 'Budget', perReq: 0.04, color: '#2ecc71' },
  'openrouter/minimax/minimax-m2.5': { name: 'MiniMax M2.5', tier: 'Budget', perReq: 0.04, color: '#2ecc71' },
  'google-ai-studio/gemini-flash-latest': { name: 'Gemini Flash', tier: 'Budget', perReq: 0.04, color: '#2ecc71' },
  'openai/gpt-5.2': { name: 'GPT-5.2', tier: 'Premium', perReq: 0.44, color: '#e74c3c' },
};

const pInfo = modelCosts[primary] || { name: primary.split('/').pop(), tier: '?', perReq: 0.50, color: '#95a5a6' };
const monthlyEst = pInfo.perReq * 50 * 30;

// Heartbeat cost
const hbModel = heartbeat.model || primary;
const hbInfo = modelCosts[hbModel] || { perReq: pInfo.perReq };
const hbIntervalMin = parseInt(heartbeat.every) || 30;
const hbPerDay = (24 * 60) / hbIntervalMin;
const hbMonthly = hbInfo.perReq * hbPerDay * 30;

// Alias table rows
const aliasRows = Object.entries(aliases)
  .map(([id, cfg]) => {
    const info = modelCosts[id] || { tier: '?', perReq: '?' };
    return `<tr><td><code>${cfg.alias}</code></td><td>${id}</td><td>${info.tier}</td><td>$${typeof info.perReq === 'number' ? info.perReq.toFixed(2) : '?'}</td></tr>`;
  })
  .join('\n');

const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Cost Dashboard</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin-bottom: 24px; }
  .card { background: #16213e; border-radius: 12px; padding: 20px; border: 1px solid #2a2a4a; }
  .card h3 { color: #8892b0; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
  .card .value { font-size: 28px; font-weight: 700; }
  .card .sub { color: #8892b0; font-size: 13px; margin-top: 4px; }
  .green { color: #2ecc71; }
  .yellow { color: #f1c40f; }
  .red { color: #e74c3c; }
  .orange { color: #e67e22; }
  h1 { margin-bottom: 20px; font-size: 24px; }
  h2 { margin: 24px 0 12px; font-size: 18px; color: #ccd6f6; }
  table { width: 100%; border-collapse: collapse; background: #16213e; border-radius: 8px; overflow: hidden; }
  th { background: #0a0a1a; text-align: left; padding: 10px 12px; font-size: 12px; text-transform: uppercase; color: #8892b0; }
  td { padding: 8px 12px; border-top: 1px solid #2a2a4a; font-size: 13px; }
  code { background: #0a0a1a; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
  .bar { height: 8px; border-radius: 4px; margin-top: 8px; }
  .savings-bar { background: linear-gradient(90deg, #2ecc71, #27ae60); }
  .cost-bar { background: linear-gradient(90deg, #e74c3c, #c0392b); }
</style>
</head>
<body>
<h1>⚡ Cost Optimizer Dashboard</h1>

<div class="grid">
  <div class="card">
    <h3>Primary Model</h3>
    <div class="value" style="color:${pInfo.color}">${pInfo.name}</div>
    <div class="sub">$${pInfo.perReq.toFixed(2)}/request · ${pInfo.tier} tier</div>
  </div>
  <div class="card">
    <h3>Est. Monthly (50 req/day)</h3>
    <div class="value ${monthlyEst > 500 ? 'red' : monthlyEst > 100 ? 'orange' : monthlyEst > 30 ? 'yellow' : 'green'}">$${monthlyEst.toFixed(0)}</div>
    <div class="sub">requests only, excl. heartbeats</div>
  </div>
  <div class="card">
    <h3>Heartbeat Cost</h3>
    <div class="value ${hbMonthly > 100 ? 'red' : hbMonthly > 10 ? 'yellow' : 'green'}">$${hbMonthly.toFixed(0)}/mo</div>
    <div class="sub">${(modelCosts[hbModel]?.name || hbModel.split('/').pop())} every ${hbIntervalMin}m</div>
  </div>
  <div class="card">
    <h3>Total Monthly Est.</h3>
    <div class="value ${(monthlyEst+hbMonthly) > 500 ? 'red' : (monthlyEst+hbMonthly) > 100 ? 'orange' : 'green'}">$${(monthlyEst + hbMonthly).toFixed(0)}</div>
    <div class="sub">vs $${(0.71 * 50 * 30 + 0.71 * hbPerDay * 30).toFixed(0)} unoptimized (all Opus)</div>
  </div>
</div>

<div class="grid">
  <div class="card">
    <h3>Memory Flush</h3>
    <div class="value ${memFlush.enabled ? 'green' : 'yellow'}">${memFlush.enabled ? 'Enabled' : 'Disabled'}</div>
    <div class="sub">Threshold: ${memFlush.softThresholdTokens || 'default'} tokens</div>
  </div>
  <div class="card">
    <h3>Concurrency</h3>
    <div class="value">${defaults.maxConcurrent || 'default'}/${defaults.subagents?.maxConcurrent || 'default'}</div>
    <div class="sub">main / subagents</div>
  </div>
  <div class="card">
    <h3>Model Aliases</h3>
    <div class="value">${Object.keys(aliases).length}</div>
    <div class="sub">configured for /model switching</div>
  </div>
  <div class="card">
    <h3>Fallbacks</h3>
    <div class="value" style="font-size:16px">${fallbacks.map(f => f.split('/').pop()).join(' → ') || 'none'}</div>
    <div class="sub">${fallbacks.length} fallback model(s)</div>
  </div>
</div>

<h2>Savings Potential</h2>
<div class="grid">
  <div class="card" style="grid-column: span 2">
    <h3>If you switched to DeepSeek V3.2 ($0.04/req)</h3>
    <div class="value green">Save $${((pInfo.perReq - 0.04) * 50 * 30).toFixed(0)}/month</div>
    <div class="bar savings-bar" style="width: ${Math.min(100, ((pInfo.perReq - 0.04) / pInfo.perReq) * 100)}%"></div>
    <div class="sub">${(((pInfo.perReq - 0.04) / pInfo.perReq) * 100).toFixed(0)}% reduction from current primary</div>
  </div>
</div>

<h2>Model Aliases</h2>
<table>
<tr><th>Alias</th><th>Model ID</th><th>Tier</th><th>$/Request</th></tr>
${aliasRows}
</table>

<div class="sub" style="margin-top: 20px; text-align: center; color: #555">
  Generated ${new Date().toISOString()} · Cost Optimizer Skill v4
</div>
</body>
</html>`;

// Output to stdout or file
const outPath = process.argv[3];
if (outPath) {
  fs.writeFileSync(outPath, html);
  console.log(`Dashboard written to ${outPath}`);
} else {
  console.log(html);
}
