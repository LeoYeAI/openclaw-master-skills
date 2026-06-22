#!/usr/bin/env node
/**
 * BrainX V5 — Quality Scorer (Phase 3.2)
 *
 * Evaluates existing memories for quality and relevance.
 * Promotes, maintains, degrades, or archives based on a computed score.
 *
 * Usage:
 *   node scripts/quality-scorer.js [--limit N] [--dry-run] [--verbose]
 */

'use strict';

const fs = require('fs');
const path = require('path');

// Load env
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });
const db = require('../lib/db');

// ── Arg parsing ──────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const out = { dryRun: false, verbose: false, limit: 50 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--dry-run') out.dryRun = true;
    else if (a === '--verbose') out.verbose = true;
    else if (a === '--limit' && argv[i + 1]) {
      out.limit = parseInt(argv[++i], 10);
      if (Number.isNaN(out.limit) || out.limit < 1) {
        console.error('Invalid --limit value');
        process.exit(1);
      }
    }
  }
  return out;
}

// ── Tier helpers ─────────────────────────────────────────────────────────────
const TIERS = ['hot', 'warm', 'cold'];

function tierIndex(tier) {
  const idx = TIERS.indexOf(tier);
  return idx === -1 ? 2 : idx; // unknown → cold
}

function degradeTier(tier) {
  const idx = tierIndex(tier);
  return TIERS[Math.min(idx + 1, TIERS.length - 1)];
}

function promoteTier(tier) {
  const idx = tierIndex(tier);
  return TIERS[Math.max(idx - 1, 0)];
}

// ── Score calculation ────────────────────────────────────────────────────────
function calculateScore(mem, fileChecks) {
  let score = 5; // start neutral
  const now = Date.now();
  const reasons = [];

  // 1. Age factor — days since last access (or creation if never accessed)
  const lastTouch = mem.last_accessed
    ? new Date(mem.last_accessed).getTime()
    : new Date(mem.created_at).getTime();
  const daysSinceAccess = (now - lastTouch) / (1000 * 60 * 60 * 24);

  if (daysSinceAccess > 30) {
    score -= 2;
    reasons.push(`stale (${Math.round(daysSinceAccess)}d without access, -2)`);
  } else if (daysSinceAccess > 14) {
    score -= 1;
    reasons.push(`aging (${Math.round(daysSinceAccess)}d without access, -1)`);
  } else if (daysSinceAccess <= 3) {
    score += 1;
    reasons.push(`recently accessed (${Math.round(daysSinceAccess)}d, +1)`);
  }

  // 2. Access factor
  const ac = mem.access_count || 0;
  if (ac >= 10) {
    score += 2;
    reasons.push(`high access (${ac}, +2)`);
  } else if (ac >= 5) {
    score += 1;
    reasons.push(`good access (${ac}, +1)`);
  } else if (ac === 0) {
    score -= 1;
    reasons.push('never accessed (-1)');
  }

  // 3. Content quality
  const contentLen = (mem.content || '').length;
  if (contentLen >= 100) {
    score += 1;
    reasons.push(`good content length (${contentLen} chars, +1)`);
  } else if (contentLen < 50) {
    score -= 1;
    reasons.push(`short content (${contentLen} chars, -1)`);
  }

  // Check for file paths — verify existence
  const filePaths = (mem.content || '').match(/(?:^|\s)(\/[\w./-]+)/g);
  if (filePaths) {
    for (const raw of filePaths) {
      const fp = raw.trim();
      // Only check absolute paths that look like real files (not URLs, not SQL)
      if (fp.startsWith('/') && !fp.includes('://') && fp.length < 256) {
        try {
          if (fs.existsSync(fp)) {
            fileChecks.valid++;
          } else {
            fileChecks.missing++;
            score -= 0.5;
            reasons.push(`missing file: ${fp} (-0.5)`);
          }
        } catch {
          // permission error or similar — skip
        }
      }
    }
  }

  // Check for URLs (flag only, no network call)
  const urlMatches = (mem.content || '').match(/https?:\/\/[^\s)]+/g);
  if (urlMatches && urlMatches.length > 0) {
    reasons.push(`contains ${urlMatches.length} URL(s) (flagged)`);
  }

  // 4. Tier coherence
  const imp = mem.importance || 5;
  const tier = mem.tier || 'warm';

  if (imp >= 8 && tier === 'cold') {
    score += 2;
    reasons.push(`high importance (${imp}) in cold tier → promote (+2)`);
  } else if (imp >= 7 && tier === 'cold') {
    score += 1;
    reasons.push(`importance ${imp} in cold tier → promote (+1)`);
  }

  if (imp <= 3 && tier === 'hot') {
    score -= 2;
    reasons.push(`low importance (${imp}) in hot tier → degrade (-2)`);
  } else if (imp <= 4 && tier === 'hot') {
    score -= 1;
    reasons.push(`importance ${imp} in hot tier → degrade (-1)`);
  }

  // 5. Recurrence bonus
  if (mem.recurrence_count && mem.recurrence_count >= 3) {
    score += 1;
    reasons.push(`recurring pattern (${mem.recurrence_count}x, +1)`);
  }

  // Clamp
  score = Math.max(0, Math.min(10, score));

  return { score: Math.round(score * 10) / 10, reasons };
}

// ── Decide action ────────────────────────────────────────────────────────────
function decideAction(score, mem) {
  const tier = mem.tier || 'warm';
  const imp = mem.importance || 5;

  // Tier coherence override: promote high-importance cold memories
  if (imp >= 7 && tier === 'cold' && score >= 5) {
    return {
      action: 'promote',
      newTier: promoteTier(tier),
      newImportance: imp
    };
  }

  if (score >= 7) {
    return { action: 'maintain', newTier: tier, newImportance: imp };
  }

  if (score >= 4) {
    return {
      action: 'degrade',
      newTier: degradeTier(tier),
      newImportance: Math.max(imp - 1, 1)
    };
  }

  // score < 4 → archive
  return {
    action: 'archive',
    newTier: 'cold',
    newImportance: 1
  };
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const { dryRun, verbose, limit } = args;

  if (verbose) {
    console.error(`[quality-scorer] limit=${limit} dry-run=${dryRun}`);
  }

  // Fetch candidate memories
  const { rows } = await db.query(
    `SELECT id, type, content, context, tier, importance, access_count,
            created_at, last_accessed, tags, recurrence_count, category
     FROM brainx_memories
     WHERE superseded_by IS NULL
     ORDER BY access_count DESC NULLS LAST
     LIMIT $1`,
    [limit]
  );

  if (verbose) {
    console.error(`[quality-scorer] fetched ${rows.length} memories`);
  }

  const stats = {
    reviewed: rows.length,
    promoted: 0,
    maintained: 0,
    degraded: 0,
    archived: 0
  };
  const fileChecks = { valid: 0, missing: 0 };
  const updates = [];

  for (const mem of rows) {
    const { score, reasons } = calculateScore(mem, fileChecks);
    const decision = decideAction(score, mem);

    if (verbose) {
      console.error(
        `  [${mem.id.slice(0, 8)}] score=${score} action=${decision.action} ` +
        `tier=${mem.tier}→${decision.newTier} imp=${mem.importance}→${decision.newImportance} ` +
        `reasons=[${reasons.join('; ')}]`
      );
    }

    // Only update if something changed
    const tierChanged = decision.newTier !== mem.tier;
    const impChanged = decision.newImportance !== mem.importance;

    if (tierChanged || impChanged) {
      updates.push({
        id: mem.id,
        newTier: decision.newTier,
        newImportance: decision.newImportance,
        action: decision.action
      });
    }

    // Count by action type
    stats[decision.action === 'promote' ? 'promoted' :
          decision.action === 'maintain' ? 'maintained' :
          decision.action === 'degrade' ? 'degraded' :
          'archived']++;
  }

  // Apply updates (unless dry-run)
  if (!dryRun && updates.length > 0) {
    await db.withClient(async (client) => {
      await client.query('BEGIN');
      for (const u of updates) {
        await client.query(
          `UPDATE brainx_memories SET tier = $2, importance = $3 WHERE id = $1`,
          [u.id, u.newTier, u.newImportance]
        );
      }
      await client.query('COMMIT');
    });

    if (verbose) {
      console.error(`[quality-scorer] applied ${updates.length} updates`);
    }
  } else if (dryRun && updates.length > 0 && verbose) {
    console.error(`[quality-scorer] dry-run: would apply ${updates.length} updates`);
  }

  const result = {
    ok: true,
    dryRun,
    reviewed: stats.reviewed,
    promoted: stats.promoted,
    maintained: stats.maintained,
    degraded: stats.degraded,
    archived: stats.archived,
    updatesApplied: dryRun ? 0 : updates.length,
    fileChecks
  };

  console.log(JSON.stringify(result, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error(err.stack || err.message || err);
    process.exit(1);
  });
