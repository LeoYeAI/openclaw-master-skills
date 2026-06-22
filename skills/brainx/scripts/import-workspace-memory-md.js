#!/usr/bin/env node

require('dotenv/config');

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const rag = require('../lib/openai-rag');

function sha1(s) {
  return crypto.createHash('sha1').update(s).digest('hex');
}

function splitIntoChunks(text, maxChars = 5000) {
  const lines = text.split(/\r?\n/);
  const chunks = [];
  let buf = [];
  let len = 0;
  for (const line of lines) {
    if (len + line.length + 1 > maxChars && buf.length) {
      chunks.push(buf.join('\n'));
      buf = [];
      len = 0;
    }
    buf.push(line);
    len += line.length + 1;
  }
  if (buf.length) chunks.push(buf.join('\n'));
  return chunks;
}

async function main() {
  const dryRun = process.argv.includes('--dry-run');

  // Resolve MEMORY.md: env override > all workspace MEMORY.md files
  let files = [];
  if (process.env.MEMORY_MD) {
    files = [process.env.MEMORY_MD];
  } else {
    // Scan all workspace dirs for MEMORY.md
    const wsBase = path.resolve(process.env.HOME || '/home/clawd', '.openclaw');
    const entries = fs.readdirSync(wsBase).filter(d => d.startsWith('workspace'));
    for (const dir of entries) {
      const candidate = path.join(wsBase, dir, 'MEMORY.md');
      if (fs.existsSync(candidate)) files.push(candidate);
    }
    // Also check workspace/MEMORY.md (shared)
    const shared = path.join(wsBase, 'workspace', 'MEMORY.md');
    if (fs.existsSync(shared) && !files.includes(shared)) files.push(shared);
  }

  if (!files.length) {
    console.log('No MEMORY.md files found in any workspace.');
    return;
  }

  let totalChunks = 0;
  for (const file of files) {
    await importFile(file, dryRun);
    totalChunks++;
  }
  console.log(`Done — processed ${files.length} file(s)`);
}

async function importFile(file, dryRun) {
  const wsName = path.basename(path.dirname(file));
  console.log(`\n📂 ${file} (workspace: ${wsName})`);
  if (!fs.existsSync(file)) { console.log('  ⚠️ not found, skipping'); return; }

  const text = fs.readFileSync(file, 'utf-8');
  const chunks = splitIntoChunks(text, 5000);

  console.log(`Importing ${chunks.length} chunks from ${file}`);

  let i = 0;
  for (const chunk of chunks) {
    i++;
    const id = `memmd_${sha1(file + '|' + i + '|' + chunk).slice(0, 16)}`;
    if (dryRun) {
      console.log(`  [dry-run] chunk ${i}/${chunks.length} (${chunk.length} chars)`);
    } else {
      await rag.storeMemory({
        id,
        type: 'note',
        content: chunk,
        context: `${wsName}/MEMORY.md`,
        tier: 'hot',
        importance: 9,
        agent: 'system',
        tags: ['import:memory-md', `source:${wsName}`]
      });
      console.log(`  ✅ chunk ${i}/${chunks.length} ok (${chunk.length} chars)`);
    }
  }

}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
