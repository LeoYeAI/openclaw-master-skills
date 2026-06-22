#!/usr/bin/env node

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const db = require('../lib/db');

async function main() {
  const dryRun = process.argv.includes('--dry-run') || String(process.env.DEDUP_DRY_RUN || 'false') === 'true';

  const dups = await db.query(`
    WITH dups AS (
      SELECT md5(coalesce(type,'')||'|'||coalesce(content,'')||'|'||coalesce(context,'')||'|'||coalesce(agent,'')) as fp,
             array_agg(id ORDER BY created_at ASC) as ids
      FROM brainx_memories
      WHERE superseded_by IS NULL
      GROUP BY fp
      HAVING count(*) > 1
    ), pairs AS (
      SELECT fp, ids[1] as keep_id, unnest(ids[2:]) as sup_id
      FROM dups
    )
    SELECT * FROM pairs;
  `);

  if (dryRun) {
    console.log(JSON.stringify({ ok: true, dryRun: true, pairs: dups.rows.length, sample: dups.rows.slice(0, 10) }, null, 2));
    return;
  }

  const res = await db.query(`
    WITH dups AS (
      SELECT md5(coalesce(type,'')||'|'||coalesce(content,'')||'|'||coalesce(context,'')||'|'||coalesce(agent,'')) as fp,
             array_agg(id ORDER BY created_at ASC) as ids
      FROM brainx_memories
      WHERE superseded_by IS NULL
      GROUP BY fp
      HAVING count(*) > 1
    ), pairs AS (
      SELECT fp, ids[1] as keep_id, unnest(ids[2:]) as sup_id
      FROM dups
    )
    UPDATE brainx_memories m
    SET superseded_by = p.keep_id,
        tags = CASE
          WHEN NOT (m.tags @> ARRAY['dedup_superseded']) THEN m.tags || ARRAY['dedup_superseded']
          ELSE m.tags
        END
    FROM pairs p
    WHERE m.id = p.sup_id;
  `);

  console.log(JSON.stringify({ ok: true, superseded: res.rowCount }, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
