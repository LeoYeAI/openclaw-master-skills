#!/usr/bin/env node
/**
 * memory-feedback.js — BrainX V5
 *
 * Provides feedback loop for memory quality:
 *   --useful    → increment access_count, importance +1 (max 10), feedback_score +1
 *   --useless   → importance -1 (min 1), feedback_score -1
 *   --incorrect → mark as superseded (soft delete)
 *
 * Usage:
 *   node scripts/memory-feedback.js --id <memory_id> --useful
 *   node scripts/memory-feedback.js --id <memory_id> --useless
 *   node scripts/memory-feedback.js --id <memory_id> --incorrect
 */

'use strict';

const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });
const db = require(path.join(__dirname, '..', 'lib', 'db'));

const args = process.argv.slice(2);

function option(name) {
  const idx = args.indexOf(`--${name}`);
  if (idx === -1 || idx + 1 >= args.length) return undefined;
  return args[idx + 1];
}
function flag(name) {
  return args.includes(`--${name}`);
}

async function main() {
  const id = option('id');
  if (!id) {
    console.error('Error: --id <memory_id> is required');
    process.exitCode = 1;
    return;
  }

  const isUseful = flag('useful');
  const isUseless = flag('useless');
  const isIncorrect = flag('incorrect');

  const actionCount = [isUseful, isUseless, isIncorrect].filter(Boolean).length;
  if (actionCount !== 1) {
    console.error('Error: exactly one of --useful, --useless, or --incorrect is required');
    process.exitCode = 1;
    return;
  }

  try {
    // Check memory exists
    const check = await db.query(
      'SELECT id, importance, access_count, feedback_score, superseded_by FROM brainx_memories WHERE id = $1',
      [id]
    );
    if (check.rows.length === 0) {
      console.log(JSON.stringify({ ok: false, error: `Memory ${id} not found` }));
      process.exitCode = 1;
      return;
    }

    const mem = check.rows[0];
    if (mem.superseded_by) {
      console.log(JSON.stringify({ ok: false, error: `Memory ${id} is already superseded` }));
      process.exitCode = 1;
      return;
    }

    let result;

    if (isUseful) {
      result = await db.query(
        `UPDATE brainx_memories
         SET access_count = COALESCE(access_count, 0) + 1,
             importance = LEAST(COALESCE(importance, 5) + 1, 10),
             feedback_score = COALESCE(feedback_score, 0) + 1,
             last_accessed = NOW()
         WHERE id = $1
         RETURNING id, importance, access_count, feedback_score`,
        [id]
      );
      console.log(JSON.stringify({
        ok: true,
        action: 'useful',
        memory: result.rows[0]
      }));
    } else if (isUseless) {
      result = await db.query(
        `UPDATE brainx_memories
         SET importance = GREATEST(COALESCE(importance, 5) - 1, 1),
             feedback_score = COALESCE(feedback_score, 0) - 1
         WHERE id = $1
         RETURNING id, importance, access_count, feedback_score`,
        [id]
      );
      console.log(JSON.stringify({
        ok: true,
        action: 'useless',
        memory: result.rows[0]
      }));
    } else if (isIncorrect) {
      // Mark as superseded by setting superseded_by to a sentinel value
      result = await db.query(
        `UPDATE brainx_memories
         SET superseded_by = 'feedback:incorrect',
             feedback_score = COALESCE(feedback_score, 0) - 5
         WHERE id = $1
         RETURNING id, superseded_by, feedback_score`,
        [id]
      );
      console.log(JSON.stringify({
        ok: true,
        action: 'incorrect',
        memory: result.rows[0]
      }));
    }
  } catch (err) {
    console.log(JSON.stringify({ ok: false, error: err.message }));
    process.exitCode = 1;
  } finally {
    await db.pool.end();
  }
}

main();
