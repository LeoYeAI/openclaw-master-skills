#!/usr/bin/env node

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const db = require('../lib/db');

async function main() {
  const dryRun = process.argv.includes('--dry-run');
  const maxLen = parseInt(process.env.CLEANUP_MAX_LEN || '12', 10);
  const newTier = process.env.CLEANUP_TIER || 'cold';
  const maxImportance = parseInt(process.env.CLEANUP_MAX_IMPORTANCE || '2', 10);

  if (dryRun) {
    const preview = await db.query(
      `
      SELECT id, content, tier, importance
      FROM brainx_memories
      WHERE superseded_by IS NULL
        AND length(coalesce(content,'')) <= $1
        AND type IN ('decision','action','learning','note')
      `,
      [maxLen]
    );
    console.log(
      JSON.stringify(
        { ok: true, dryRun: true, wouldUpdate: preview.rowCount, maxLen, newTier, maxImportance, sample: preview.rows.slice(0, 10) },
        null,
        2
      )
    );
    return;
  }

  const res = await db.query(
    `
    UPDATE brainx_memories
    SET tier = $1,
        importance = LEAST(importance, $2),
        tags = CASE
          WHEN NOT (tags @> ARRAY['low_signal']) THEN tags || ARRAY['low_signal']
          ELSE tags
        END
    WHERE superseded_by IS NULL
      AND length(coalesce(content,'')) <= $3
      AND type IN ('decision','action','learning','note')
    `,
    [newTier, maxImportance, maxLen]
  );

  console.log(
    JSON.stringify(
      { ok: true, dryRun: false, updated: res.rowCount, maxLen, newTier, maxImportance },
      null,
      2
    )
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
