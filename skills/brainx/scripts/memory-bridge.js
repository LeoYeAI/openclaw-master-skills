#!/usr/bin/env node
/**
 * BrainX V5 — Memory Bridge
 *
 * Syncs daily memory/*.md files from all OpenClaw workspaces into BrainX.
 * Each H2 section becomes a searchable vector memory.
 *
 * Usage:
 *   node memory-bridge.js [--hours 6] [--dry-run] [--max-memories 20] [--verbose]
 *
 * Output: JSON summary of blocks processed, stored, and errors
 */

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

const BRAINX_DIR = path.join(__dirname, '..');
const OPENCLAW_DIR = path.join(process.env.HOME || '', '.openclaw');
const SYNCED_TAG = '<!-- brainx-synced -->';

// ---------------------------------------------------------------------------
// Args
// ---------------------------------------------------------------------------
function parseArgs() {
  const args = {};
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--hours') args.hours = parseInt(argv[++i], 10);
    else if (argv[i] === '--dry-run') args.dryRun = true;
    else if (argv[i] === '--max-memories') args.maxMemories = parseInt(argv[++i], 10);
    else if (argv[i] === '--verbose') args.verbose = true;
  }
  return {
    hours: args.hours || 6,
    dryRun: args.dryRun || false,
    maxMemories: args.maxMemories || 20,
    verbose: args.verbose || false,
  };
}

// ---------------------------------------------------------------------------
// Find recent memory .md files across all workspaces
// ---------------------------------------------------------------------------
function findRecentMemoryFiles(hoursAgo) {
  const minutes = hoursAgo * 60;
  try {
    const output = execSync(
      `find ${OPENCLAW_DIR}/workspace*/memory/ -name "*.md" -mmin -${minutes} 2>/dev/null`,
      { encoding: 'utf8', timeout: 10000 }
    ).trim();
    if (!output) return [];
    return output.split('\n').filter(Boolean);
  } catch {
    return [];
  }
}

// ---------------------------------------------------------------------------
// Extract workspace name from path
// ---------------------------------------------------------------------------
function extractWorkspace(filePath) {
  // e.g. ~/.openclaw/workspace-coder/memory/2026-02-25.md → coder
  const match = filePath.match(/workspace-([^/]+)/);
  return match ? match[1] : 'unknown';
}

// ---------------------------------------------------------------------------
// Split file content into H2 blocks
// ---------------------------------------------------------------------------
function splitIntoBlocks(content) {
  // Split on lines that start with "## "
  const parts = content.split(/^(?=## )/m);
  const blocks = [];

  for (const part of parts) {
    const trimmed = part.trim();
    if (!trimmed) continue;
    // Only consider actual H2 sections (skip content before first H2)
    if (!trimmed.startsWith('## ')) continue;

    // Extract the heading
    const firstNewline = trimmed.indexOf('\n');
    const heading = firstNewline >= 0 ? trimmed.slice(3, firstNewline).trim() : trimmed.slice(3).trim();
    const body = firstNewline >= 0 ? trimmed.slice(firstNewline + 1).trim() : '';

    blocks.push({
      heading,
      fullText: trimmed,
      body,
    });
  }

  return blocks;
}

// ---------------------------------------------------------------------------
// Classify a memory block heuristically
// ---------------------------------------------------------------------------
function classifyBlock(text) {
  const lower = text.toLowerCase();

  // Decision
  if (/(?:decisión|decided|decidimos|elegimos|vamos a usar|switched to|migrat|adoptamos|reemplaz)/i.test(lower)) {
    return { type: 'decision', importance: 7 };
  }

  // Error / fix / bug → learning
  if (/(?:error|fix|bug|fallo|falló|crash|broke|roto|no funciona|se cayó|exception|la solución|se resolvió|corregido|arreglado|el problema era)/i.test(lower)) {
    return { type: 'learning', importance: 7, category: 'error' };
  }

  // Gotcha / cuidado
  if (/(?:gotcha|cuidado|watch out|careful|trap|caveat|ojo con|no usar|avoid|prohibido)/i.test(lower)) {
    return { type: 'gotcha', importance: 7, category: 'correction' };
  }

  // Default → note
  return { type: 'note', importance: 5 };
}

// ---------------------------------------------------------------------------
// Truncate content for storage
// ---------------------------------------------------------------------------
function truncateContent(text, maxChars = 1500) {
  if (text.length <= maxChars) return text;
  return text.slice(0, maxChars - 1) + '…';
}

// ---------------------------------------------------------------------------
// Store to BrainX via RAG lib
// ---------------------------------------------------------------------------
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
      id: `mb_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
      type: memory.type,
      content: memory.content,
      context: memory.context || null,
      tier: memory.importance >= 7 ? 'hot' : 'warm',
      importance: memory.importance ?? 5,
      agent: memory.agent || null,
      category: memory.category || null,
      tags: memory.tags || [],
    });
    return { ok: true, id: result?.id, dedupe_merged: result?.dedupe_merged };
  } catch (e) {
    return { ok: false, error: (e.message || String(e)).slice(0, 200) };
  }
}

// ---------------------------------------------------------------------------
// Mark a block as synced in the original file
// ---------------------------------------------------------------------------
function markBlockSynced(filePath, blockHeading, fileContent) {
  // Find the block by its heading and append the synced tag after its content,
  // right before the next H2 heading or end of file.
  const headingLine = `## ${blockHeading}`;
  const headingIdx = fileContent.indexOf(headingLine);
  if (headingIdx < 0) return fileContent;

  // Find the start of the next H2 section (or end of file)
  const afterHeading = headingIdx + headingLine.length;
  const nextH2 = fileContent.indexOf('\n## ', afterHeading);
  const blockEnd = nextH2 >= 0 ? nextH2 : fileContent.length;

  // Check if already tagged (shouldn't happen, but be safe)
  const blockContent = fileContent.slice(headingIdx, blockEnd);
  if (blockContent.includes(SYNCED_TAG)) return fileContent;

  // Insert the tag at the end of the block (before the newline that starts next section)
  const insertPos = blockEnd;
  const before = fileContent.slice(0, insertPos);
  const after = fileContent.slice(insertPos);

  // Ensure there's a newline before the tag
  const needsNewline = before.length > 0 && !before.endsWith('\n');
  return before + (needsNewline ? '\n' : '') + SYNCED_TAG + '\n' + after;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
  const args = parseArgs();
  const files = findRecentMemoryFiles(args.hours);

  const summary = {
    filesScanned: files.length,
    blocksFound: 0,
    blocksSkippedSynced: 0,
    blocksSkippedShort: 0,
    blocksProcessed: 0,
    memoriesStored: 0,
    memoriesFailed: 0,
    memoriesCapped: false,
    byWorkspace: {},
    byType: {},
    errors: [],
  };

  // Collect all candidate blocks across all files
  const candidates = [];

  for (const filePath of files) {
    const workspace = extractWorkspace(filePath);
    const content = fs.readFileSync(filePath, 'utf8');
    const blocks = splitIntoBlocks(content);

    if (!summary.byWorkspace[workspace]) {
      summary.byWorkspace[workspace] = { files: 0, blocks: 0, stored: 0 };
    }
    summary.byWorkspace[workspace].files++;

    for (const block of blocks) {
      summary.blocksFound++;
      summary.byWorkspace[workspace].blocks++;

      // Skip already synced blocks
      if (block.fullText.includes(SYNCED_TAG)) {
        summary.blocksSkippedSynced++;
        continue;
      }

      // Skip very short blocks (< 50 chars)
      if (block.fullText.length < 50) {
        summary.blocksSkippedShort++;
        continue;
      }

      // Skip Index tables (common in daily files)
      if (block.heading.toLowerCase() === 'index') {
        summary.blocksSkippedShort++;
        continue;
      }

      const classification = classifyBlock(block.fullText);

      candidates.push({
        filePath,
        workspace,
        heading: block.heading,
        fullText: block.fullText,
        classification,
      });
    }
  }

  // Sort by importance (higher first), then by type priority
  const TYPE_PRIORITY = { decision: 0, gotcha: 1, learning: 2, note: 3 };
  candidates.sort((a, b) => {
    const impDiff = b.classification.importance - a.classification.importance;
    if (impDiff !== 0) return impDiff;
    return (TYPE_PRIORITY[a.classification.type] || 9) - (TYPE_PRIORITY[b.classification.type] || 9);
  });

  summary.blocksProcessed = candidates.length;
  summary.memoriesCapped = candidates.length > args.maxMemories;
  const toStore = candidates.slice(0, args.maxMemories);

  // Track file content modifications for writing back
  const fileModifications = new Map(); // filePath → current content

  // Store each block to BrainX
  for (const cand of toStore) {
    const memory = {
      type: cand.classification.type,
      content: truncateContent(cand.fullText),
      context: `workspace:${cand.workspace}`,
      importance: cand.classification.importance,
      category: cand.classification.category || null,
      agent: cand.workspace,
      source_kind: 'memory-bridge',
      source_path: cand.filePath,
      tags: [
        'memory-bridge',
        `workspace:${cand.workspace}`,
        `heading:${cand.heading.slice(0, 60)}`,
      ],
    };

    if (args.verbose) {
      console.error(`[${cand.workspace}] ${cand.classification.type}: ${cand.heading.slice(0, 80)}`);
    }

    // Rate limiting: 250ms between embeddings
    if (!args.dryRun) {
      await new Promise(r => setTimeout(r, 250));
    }

    const result = await storeToBrainx(memory, args.dryRun);

    if (result.ok) {
      summary.memoriesStored++;
      summary.byWorkspace[cand.workspace].stored = (summary.byWorkspace[cand.workspace].stored || 0) + 1;
      summary.byType[cand.classification.type] = (summary.byType[cand.classification.type] || 0) + 1;

      // Mark block as synced in file content
      if (!args.dryRun) {
        if (!fileModifications.has(cand.filePath)) {
          fileModifications.set(cand.filePath, fs.readFileSync(cand.filePath, 'utf8'));
        }
        const currentContent = fileModifications.get(cand.filePath);
        const updatedContent = markBlockSynced(cand.filePath, cand.heading, currentContent);
        fileModifications.set(cand.filePath, updatedContent);
      }
    } else {
      summary.memoriesFailed++;
      if (summary.errors.length < 5) {
        summary.errors.push(`[${cand.workspace}] ${cand.heading.slice(0, 40)}: ${result.error?.slice(0, 100)}`);
      }
    }
  }

  // Write back modified files
  if (!args.dryRun) {
    for (const [filePath, content] of fileModifications) {
      try {
        fs.writeFileSync(filePath, content, 'utf8');
        if (args.verbose) {
          console.error(`[write] Updated ${filePath}`);
        }
      } catch (e) {
        summary.errors.push(`[write] ${filePath}: ${e.message?.slice(0, 100)}`);
      }
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
