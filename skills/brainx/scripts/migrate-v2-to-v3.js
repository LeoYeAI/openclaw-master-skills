#!/usr/bin/env node

require('dotenv/config');

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const rag = require('../lib/openai-rag');
const db = require('../lib/db');

function sha1(s) {
  return crypto.createHash('sha1').update(s).digest('hex');
}

function mapTier(tier) {
  if (!tier) return 'warm';
  const t = String(tier).toLowerCase();
  if (['hot', 'warm', 'cold', 'archive'].includes(t)) return t;
  return 'warm';
}

async function main() {
  const v2Home = process.env.BRAINX_V2_HOME || path.resolve(__dirname, '../../brainx-v2');
  const storageDir = path.join(v2Home, 'storage');

  if (!fs.existsSync(storageDir)) {
    console.log('ℹ️  V2 storage not found — migration not needed (already on V4).');
    console.log(`   Looked in: ${storageDir}`);
    process.exit(0);
  }

  const files = [];
  for (const tier of ['hot', 'warm', 'cold']) {
    const dir = path.join(storageDir, tier);
    if (!fs.existsSync(dir)) continue;
    for (const f of fs.readdirSync(dir)) {
      if (f.endsWith('.json')) files.push(path.join(dir, f));
    }
  }

  files.sort();

  console.log(`Found ${files.length} V2 memory files`);

  let ok = 0;
  let failed = 0;

  for (const file of files) {
    try {
      const raw = fs.readFileSync(file, 'utf-8');
      const m = JSON.parse(raw);

      const content = m.content || m.text || '';
      if (!content.trim()) continue;

      const id = m.id || `v2_${sha1(path.basename(file) + '|' + content).slice(0, 16)}`;

      await rag.storeMemory({
        id,
        type: m.type || 'note',
        content,
        context: m.context || null,
        tier: mapTier(m.tier || path.basename(path.dirname(file))),
        agent: m.agent || null,
        importance: typeof m.importance === 'number' ? m.importance : 5,
        tags: m.tags || ['migrated:v2'],
      });

      // preserve timestamps if present
      if (m.timestamp) {
        await db.query(
          'UPDATE brainx_memories SET created_at = $1, last_accessed = $1 WHERE id = $2',
          [new Date(m.timestamp), id]
        );
      }

      ok++;
      if (ok % 10 === 0) console.log(`Migrated ${ok}/${files.length}`);
    } catch (e) {
      failed++;
      console.error(`Failed: ${file}: ${e.message}`);
    }
  }

  const count = await db.query('select count(*)::int as n from brainx_memories');
  console.log(`Done. ok=${ok} failed=${failed} total_in_db=${count.rows[0].n}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
