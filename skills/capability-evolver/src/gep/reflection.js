'use strict';

const fs = require('fs');
const path = require('path');
const { getReflectionLogPath, getEvolutionDir } = require('./paths');

const REFLECTION_INTERVAL_CYCLES = 5;
const REFLECTION_COOLDOWN_MS = 30 * 60 * 1000;

function ensureDir(dir) {
  try { if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true }); } catch (_) {}
}

function shouldReflect({ cycleCount, recentEvents }) {
  if (!Number.isFinite(cycleCount) || cycleCount < REFLECTION_INTERVAL_CYCLES) return false;
  if (cycleCount % REFLECTION_INTERVAL_CYCLES !== 0) return false;

  const logPath = getReflectionLogPath();
  try {
    if (fs.existsSync(logPath)) {
      const stat = fs.statSync(logPath);
      if (Date.now() - stat.mtimeMs < REFLECTION_COOLDOWN_MS) return false;
    }
  } catch (_) {}

  return true;
}

function buildReflectionContext({ recentEvents, signals, memoryAdvice, narrative }) {
  const parts = ['You are performing a strategic reflection on recent evolution cycles.'];
  parts.push('Analyze the patterns below and provide concise strategic guidance.');
  parts.push('');

  if (Array.isArray(recentEvents) && recentEvents.length > 0) {
    const last10 = recentEvents.slice(-10);
    const successCount = last10.filter(e => e && e.outcome && e.outcome.status === 'success').length;
    const failCount = last10.filter(e => e && e.outcome && e.outcome.status === 'failed').length;
    const intents = {};
    last10.forEach(e => {
      const i = e && e.intent ? e.intent : 'unknown';
      intents[i] = (intents[i] || 0) + 1;
    });
    const genes = {};
    last10.forEach(e => {
      const g = e && Array.isArray(e.genes_used) && e.genes_used[0] ? e.genes_used[0] : 'unknown';
      genes[g] = (genes[g] || 0) + 1;
    });

    parts.push('## Recent Cycle Statistics (last 10)');
    parts.push(`- Success: ${successCount}, Failed: ${failCount}`);
    parts.push(`- Intent distribution: ${JSON.stringify(intents)}`);
    parts.push(`- Gene usage: ${JSON.stringify(genes)}`);
    parts.push('');
  }

  if (Array.isArray(signals) && signals.length > 0) {
    parts.push('## Current Signals');
    parts.push(signals.slice(0, 20).join(', '));
    parts.push('');
  }

  if (memoryAdvice) {
    parts.push('## Memory Graph Advice');
    if (memoryAdvice.preferredGeneId) {
      parts.push(`- Preferred gene: ${memoryAdvice.preferredGeneId}`);
    }
    if (Array.isArray(memoryAdvice.bannedGeneIds) && memoryAdvice.bannedGeneIds.length > 0) {
      parts.push(`- Banned genes: ${memoryAdvice.bannedGeneIds.join(', ')}`);
    }
    if (memoryAdvice.explanation) {
      parts.push(`- Explanation: ${memoryAdvice.explanation}`);
    }
    parts.push('');
  }

  if (narrative) {
    parts.push('## Recent Evolution Narrative');
    parts.push(String(narrative).slice(0, 3000));
    parts.push('');
  }

  parts.push('## Questions to Answer');
  parts.push('1. Are there persistent signals being ignored?');
  parts.push('2. Is the gene selection strategy optimal, or are we stuck in a local maximum?');
  parts.push('3. Should the balance between repair/optimize/innovate shift?');
  parts.push('4. Are there capability gaps that no current gene addresses?');
  parts.push('5. What single strategic adjustment would have the highest impact?');
  parts.push('');
  parts.push('Respond with a JSON object: { "insights": [...], "strategy_adjustment": "...", "priority_signals": [...] }');

  return parts.join('\n');
}

function recordReflection(reflection) {
  const logPath = getReflectionLogPath();
  ensureDir(path.dirname(logPath));

  const entry = JSON.stringify({
    ts: new Date().toISOString(),
    type: 'reflection',
    ...reflection,
  }) + '\n';

  fs.appendFileSync(logPath, entry, 'utf8');
}

function loadRecentReflections(count) {
  const n = Number.isFinite(count) ? count : 3;
  const logPath = getReflectionLogPath();
  try {
    if (!fs.existsSync(logPath)) return [];
    const lines = fs.readFileSync(logPath, 'utf8').trim().split('\n').filter(Boolean);
    return lines.slice(-n).map(line => {
      try { return JSON.parse(line); } catch (_) { return null; }
    }).filter(Boolean);
  } catch (_) {
    return [];
  }
}

module.exports = {
  shouldReflect,
  buildReflectionContext,
  recordReflection,
  loadRecentReflections,
  REFLECTION_INTERVAL_CYCLES,
};
