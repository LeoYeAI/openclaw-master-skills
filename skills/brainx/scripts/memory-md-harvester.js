#!/usr/bin/env node
/**
 * BrainX V5 — Memory MD Harvester
 *
 * Reads recent memory/*.md files from all agent workspaces and extracts
 * high-signal entries into BrainX. Closes the gap where daily logs
 * written by agents never reach the shared brain.
 *
 * Usage:
 *   node memory-md-harvester.js [--hours 48] [--dry-run] [--verbose] [--max-memories 40]
 *
 * Designed to run daily in the BrainX cron pipeline (722f45ea).
 */

'use strict';

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const WORKSPACE_BASE = path.join(process.env.HOME || '/home/clawd', '.openclaw');
const BRAINX_DIR = path.join(__dirname, '..');

// ── Args ────────────────────────────────────────────────────────
function parseArgs() {
  const args = {};
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--hours') args.hours = parseInt(argv[++i], 10);
    else if (argv[i] === '--dry-run') args.dryRun = true;
    else if (argv[i] === '--verbose') args.verbose = true;
    else if (argv[i] === '--max-memories') args.maxMemories = parseInt(argv[++i], 10);
  }
  return {
    hours: args.hours || 48,
    dryRun: args.dryRun || false,
    verbose: args.verbose || false,
    maxMemories: args.maxMemories || 40,
  };
}

// ── Find recent memory/*.md files across all workspaces ─────────
function findRecentMemoryFiles(hoursAgo) {
  const cutoff = Date.now() - (hoursAgo * 60 * 60 * 1000);
  const files = [];

  // Scan workspace/ and workspace-*/ directories
  const entries = fs.readdirSync(WORKSPACE_BASE, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    if (entry.name !== 'workspace' && !entry.name.startsWith('workspace-')) continue;

    const memDir = path.join(WORKSPACE_BASE, entry.name, 'memory');
    if (!fs.existsSync(memDir)) continue;

    // Derive agent name from workspace dir
    const agentName = entry.name === 'workspace'
      ? 'main'
      : entry.name.replace('workspace-', '');

    const mdFiles = fs.readdirSync(memDir).filter(f => f.endsWith('.md'));
    for (const f of mdFiles) {
      const fullPath = path.join(memDir, f);
      const stat = fs.statSync(fullPath);
      if (stat.mtimeMs >= cutoff) {
        files.push({
          agent: agentName,
          path: fullPath,
          filename: f,
          modified: stat.mtimeMs,
          size: stat.size,
        });
      }
    }
  }

  return files.sort((a, b) => b.modified - a.modified);
}

// ── Parse markdown into entries ─────────────────────────────────
// Splits by ## headers and extracts bullet points as individual entries
function parseMemoryMd(content) {
  const entries = [];
  const sections = content.split(/^## /m).filter(Boolean);

  for (const section of sections) {
    const lines = section.split('\n');
    const heading = lines[0].trim();

    // Skip index tables, BrainX auto-injected sections, empty sections
    if (/^index$/i.test(heading)) continue;
    if (/brainx.*context.*auto/i.test(heading)) continue;
    if (/^#/.test(heading)) continue; // Sub-sub-headers as section starts

    // Collect bullet entries under this heading
    let currentEntry = '';
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i];

      // New bullet point = new entry
      if (/^[-•*]\s+/.test(line)) {
        if (currentEntry.trim()) {
          entries.push({ heading, text: currentEntry.trim() });
        }
        currentEntry = line.replace(/^[-•*]\s+/, '');
      } else if (/^\s{2,}[-•*]\s+/.test(line) || /^\s{2,}\S/.test(line)) {
        // Sub-bullet or continuation — append to current
        currentEntry += '\n' + line.trim();
      } else if (line.trim() === '') {
        // Empty line — flush current entry
        if (currentEntry.trim()) {
          entries.push({ heading, text: currentEntry.trim() });
          currentEntry = '';
        }
      } else {
        // Non-bullet text under heading — treat as standalone entry
        if (currentEntry.trim()) {
          entries.push({ heading, text: currentEntry.trim() });
        }
        currentEntry = line.trim();
      }
    }
    // Flush remaining
    if (currentEntry.trim()) {
      entries.push({ heading, text: currentEntry.trim() });
    }
  }

  return entries;
}

// ── Classify an entry ───────────────────────────────────────────
// Returns null for noise, classification object for signal
function classifyEntry(text, heading) {
  // Minimum length — skip very short entries
  if (text.length < 60) return null;

  const combined = `${heading} ${text}`.toLowerCase();

  // Skip patterns
  const SKIP = [
    /^(ok|listo|done|hecho|sí|si|no)$/i,
    /heartbeat_ok/i,
    /no_reply/i,
    /sin cambios|no changes|nothing to report/i,
    /^\| .* \| .* \|/,  // Table rows
    /^```/,  // Code blocks
  ];

  for (const pat of SKIP) {
    if (pat.test(text)) return null;
  }

  // Classification rules
  const RULES = [
    // Fixes and solutions
    { match: /(?:fix(?:ed|eado)?|corregid[oa]|arreglad[oa]|solución|soluciona|the fix|se resolvió|→.*(?:fix|arregl|correg))/i, type: 'learning', importance: 7, category: 'error' },

    // Decisions
    { match: /(?:decid|decisión|decidimos|elegimos|se.*(?:cambió|migró|movió)|vamos a usar|switched|reemplaz|en vez de)/i, type: 'decision', importance: 7 },

    // Bugs and errors found
    { match: /(?:bug|error|fallo|falló|roto|crash|broke|no funciona|causa|root cause|issue|problema)/i, type: 'learning', importance: 6, category: 'error' },

    // Gotchas and warnings
    { match: /(?:gotcha|cuidado|ojo con|nunca|no usar|avoid|prohibido|trap|caveat|watch out)/i, type: 'gotcha', importance: 7, category: 'correction' },

    // Config and setup
    { match: /(?:config|configuración|setup|instalé|installed|deploy|habilitado|activado|desactivado|variable|env|api.?key|token|renovad[oa])/i, type: 'note', importance: 6, category: 'infrastructure' },

    // Learnings
    { match: /(?:aprendí|descubrí|resulta que|turns out|actually|en realidad|lo que pasa|the issue was)/i, type: 'learning', importance: 6, category: 'learning' },

    // Architecture / pipeline
    { match: /(?:arquitectura|architecture|pipeline|workflow|schema|migración|migration|restructura)/i, type: 'decision', importance: 6 },

    // Created / built / automated
    { match: /(?:cread[oa]|creamos|built|construi|automated|automatiz|script nuevo|new script)/i, type: 'note', importance: 5, category: 'infrastructure' },

    // Audits and verifications
    { match: /(?:audit|verificad[oa]|confirmed|validado|tests? pass|28\/28|all.*pass)/i, type: 'note', importance: 5, category: 'best_practice' },
  ];

  for (const rule of RULES) {
    if (rule.match.test(combined)) {
      return {
        type: rule.type,
        importance: rule.importance,
        category: rule.category || null,
      };
    }
  }

  // Long entries with signal words
  if (text.length > 300) {
    const hasSignal = /(?:importante|critical|key|clave|resumen|summary|resultado|result|conclus)/i.test(text);
    if (hasSignal) {
      return { type: 'note', importance: 5, category: null };
    }
  }

  return null;
}

// ── Content hash for dedup ──────────────────────────────────────
function contentHash(text) {
  return crypto.createHash('sha256').update(text.slice(0, 500)).digest('hex').slice(0, 16);
}

// ── Store to BrainX ─────────────────────────────────────────────
let _rag = null;
function getRag() {
  if (!_rag) _rag = require(path.join(BRAINX_DIR, 'lib', 'openai-rag'));
  return _rag;
}

async function storeToBrainx(memory, dryRun) {
  if (dryRun) return { ok: true, dryRun: true };

  try {
    const rag = getRag();
    const result = await rag.storeMemory({
      id: `m_md_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
      type: memory.type,
      content: memory.content,
      context: memory.context || null,
      tier: memory.importance >= 7 ? 'hot' : 'warm',
      importance: memory.importance,
      agent: memory.agent || null,
      tags: memory.tags || [],
      sourceKind: 'markdown_import',
      sourcePath: memory.sourcePath || null,
    });
    return { ok: true, id: result?.id, dedupe_merged: result?.dedupe_merged };
  } catch (e) {
    return { ok: false, error: (e.message || String(e)).slice(0, 200) };
  }
}

// ── Truncate ────────────────────────────────────────────────────
function truncate(text, maxLen = 1500) {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen - 1) + '…';
}

// ── Main ────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs();
  const files = findRecentMemoryFiles(args.hours);

  const summary = {
    filesScanned: files.length,
    entriesExtracted: 0,
    entriesClassified: 0,
    entriesSkipped: 0,
    memoriesStored: 0,
    memoriesFailed: 0,
    memoriesDedupe: 0,
    candidatesTotal: 0,
    candidatesCapped: false,
    byAgent: {},
    byType: {},
    errors: [],
  };

  const seenHashes = new Set();
  const candidates = [];

  // Phase 1: Read and classify all entries from memory/*.md
  for (const file of files) {
    const content = fs.readFileSync(file.path, 'utf8');
    const entries = parseMemoryMd(content);

    if (!summary.byAgent[file.agent]) {
      summary.byAgent[file.agent] = { files: 0, entries: 0, stored: 0 };
    }
    summary.byAgent[file.agent].files++;
    summary.byAgent[file.agent].entries += entries.length;
    summary.entriesExtracted += entries.length;

    for (const entry of entries) {
      const classification = classifyEntry(entry.text, entry.heading);
      if (!classification) {
        summary.entriesSkipped++;
        continue;
      }
      summary.entriesClassified++;

      const hash = contentHash(entry.text);
      if (seenHashes.has(hash)) {
        summary.memoriesDedupe++;
        continue;
      }
      seenHashes.add(hash);

      candidates.push({
        agent: file.agent,
        sourcePath: file.path,
        heading: entry.heading,
        classification,
        text: entry.text,
      });
    }
  }

  // Phase 2: Sort by importance, take top N
  const TYPE_PRIORITY = { decision: 0, gotcha: 1, learning: 2, note: 3 };
  candidates.sort((a, b) => {
    const impDiff = b.classification.importance - a.classification.importance;
    if (impDiff !== 0) return impDiff;
    return (TYPE_PRIORITY[a.classification.type] || 9) - (TYPE_PRIORITY[b.classification.type] || 9);
  });

  summary.candidatesTotal = candidates.length;
  summary.candidatesCapped = candidates.length > args.maxMemories;
  const toStore = candidates.slice(0, args.maxMemories);

  // Phase 3: Store to BrainX
  for (const cand of toStore) {
    const contextPrefix = cand.heading ? `[${cand.heading}] ` : '';
    const memory = {
      type: cand.classification.type,
      content: truncate(`${contextPrefix}${cand.text}`),
      context: `agent:${cand.agent}`,
      importance: cand.classification.importance,
      category: cand.classification.category,
      agent: cand.agent,
      tags: ['md-harvested', `agent:${cand.agent}`, `heading:${(cand.heading || '').slice(0, 40)}`],
      sourcePath: cand.sourcePath,
    };

    if (!args.dryRun) {
      await new Promise(r => setTimeout(r, 250));
    }

    const result = await storeToBrainx(memory, args.dryRun);

    if (result.ok) {
      summary.memoriesStored++;
      if (result.dedupe_merged) summary.memoriesDedupe++;
      summary.byAgent[cand.agent].stored = (summary.byAgent[cand.agent].stored || 0) + 1;
      summary.byType[cand.classification.type] = (summary.byType[cand.classification.type] || 0) + 1;
    } else {
      summary.memoriesFailed++;
      if (summary.errors.length < 5) {
        summary.errors.push(result.error?.slice(0, 100));
      }
    }

    if (args.verbose) {
      const status = result.ok ? '✓' : '✗';
      console.error(`[${status}] [${cand.agent}] ${cand.classification.type}: ${cand.text.slice(0, 80)}...`);
    }
  }

  console.log(JSON.stringify({
    ok: true,
    dryRun: args.dryRun,
    hours: args.hours,
    maxMemories: args.maxMemories,
    ...summary,
  }, null, 2));
}

main().catch(e => {
  console.error(e.stack || e.message);
  process.exit(1);
});
