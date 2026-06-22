#!/usr/bin/env node
/**
 * Fase 0.1: Reclassify existing memories
 * Sets category + recalculates importance for uncategorized memories
 * Uses heuristic rules (no LLM needed for this batch)
 */
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });
const db = require('../lib/db');

const CATEGORY_RULES = [
  { match: /error|fail|crash|bug|broke|fix|wrong|issue/i, category: 'error', typeHint: 'learning' },
  { match: /learn|realiz|discover|found out|turns out|actually/i, category: 'learning', typeHint: 'learning' },
  { match: /decid|chose|decision|switch|migrat|adopt|use.*instead/i, category: null, typeHint: 'decision' },
  { match: /gotcha|careful|watch out|trap|caveat|warning|don't|avoid/i, category: 'correction', typeHint: 'gotcha' },
  { match: /feature|request|want|need|wish|should add/i, category: 'feature_request', typeHint: 'feature_request' },
  { match: /best practice|pattern|convention|always|never|rule/i, category: 'best_practice', typeHint: 'note' },
  { match: /gap|missing|didn't know|unknown|unclear/i, category: 'knowledge_gap', typeHint: 'learning' },
];

function classifyContent(content, type) {
  for (const rule of CATEGORY_RULES) {
    if (rule.match.test(content)) {
      return { category: rule.category, suggestedType: rule.typeHint };
    }
  }
  return { category: null, suggestedType: type };
}

function scoreImportance(content, tier, accessCount) {
  let score = 5;
  // Length bonus: detailed memories are more valuable
  if (content.length > 500) score += 1;
  if (content.length > 1000) score += 1;
  // Tier bonus
  if (tier === 'hot') score += 1;
  // Access bonus
  if (accessCount > 3) score += 1;
  if (accessCount > 10) score += 1;
  // Cap at 10
  return Math.min(10, Math.max(1, score));
}

async function main() {
  const dryRun = process.argv.includes('--dry-run');
  
  const result = await db.query(`
    SELECT id, type, content, context, tier, importance, access_count, category, status
    FROM brainx_memories
    WHERE superseded_by IS NULL
    ORDER BY created_at ASC
  `);

  let updated = 0;
  let skipped = 0;
  const stats = { categories: {}, types: {} };

  for (const row of result.rows) {
    const { category, suggestedType } = classifyContent(row.content, row.type);
    const newImportance = scoreImportance(row.content, row.tier, row.access_count || 0);
    
    const needsUpdate = (
      (!row.category && category) ||
      row.status === 'pending' ||
      row.importance !== newImportance
    );

    if (!needsUpdate) {
      skipped++;
      continue;
    }

    const finalCategory = row.category || category; // don't overwrite existing
    stats.categories[finalCategory || 'uncategorized'] = (stats.categories[finalCategory || 'uncategorized'] || 0) + 1;
    stats.types[suggestedType] = (stats.types[suggestedType] || 0) + 1;

    if (!dryRun) {
      await db.query(`
        UPDATE brainx_memories
        SET category = COALESCE($2, category),
            importance = $3,
            status = CASE WHEN status = 'pending' THEN 'promoted' ELSE status END
        WHERE id = $1
      `, [row.id, finalCategory, newImportance]);
    }
    updated++;
  }

  console.log(JSON.stringify({
    ok: true,
    dryRun,
    total: result.rows.length,
    updated,
    skipped,
    stats
  }, null, 2));

  process.exit(0);
}

main().catch(e => { console.error(e.message); process.exit(1); });
