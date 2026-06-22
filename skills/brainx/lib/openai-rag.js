const db = require('./db');
const { embed } = require('./embedding-client');
const {
  getPhase2Config,
  shouldScrubForContext,
  scrubTextPII,
  mergeTagsWithMetadata,
  deriveMergePlan
} = require('./brainx-phase2');

function normalizeLifecycle(memory = {}) {
  const now = new Date();
  const firstSeen = memory.first_seen || memory.firstSeen || null;
  const lastSeen = memory.last_seen || memory.lastSeen || null;
  const resolvedAt = memory.resolved_at || memory.resolvedAt || null;

  return {
    status: memory.status || 'pending',
    category: memory.category || null,
    pattern_key: memory.pattern_key || memory.patternKey || null,
    recurrence_count: memory.recurrence_count ?? memory.recurrenceCount ?? null,
    first_seen: firstSeen ? new Date(firstSeen) : null,
    last_seen: lastSeen ? new Date(lastSeen) : null,
    resolved_at: resolvedAt ? new Date(resolvedAt) : null,
    promoted_to: memory.promoted_to || memory.promotedTo || null,
    resolution_notes: memory.resolution_notes || memory.resolutionNotes || null,
    _now: now
  };
}

function tierImpact(tier) {
  switch (tier) {
    case 'hot': return 1.0;
    case 'warm': return 0.7;
    case 'cold': return 0.4;
    case 'archive': return 0.2;
    default: return 0.5;
  }
}

async function upsertPatternRecord(client, memory) {
  if (!memory.pattern_key) return;

  const impactScore = Number(memory.importance ?? 5) * tierImpact(memory.tier);
  await client.query(
    `INSERT INTO brainx_patterns (
       pattern_key, recurrence_count, first_seen, last_seen, impact_score,
       representative_memory_id, last_memory_id, last_category, last_status, promoted_to, updated_at
     )
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,NOW())
     ON CONFLICT (pattern_key) DO UPDATE SET
       recurrence_count = GREATEST(brainx_patterns.recurrence_count, EXCLUDED.recurrence_count),
       first_seen = LEAST(brainx_patterns.first_seen, EXCLUDED.first_seen),
       last_seen = GREATEST(brainx_patterns.last_seen, EXCLUDED.last_seen),
       impact_score = GREATEST(brainx_patterns.impact_score, EXCLUDED.impact_score),
       representative_memory_id = COALESCE(brainx_patterns.representative_memory_id, EXCLUDED.representative_memory_id),
       last_memory_id = EXCLUDED.last_memory_id,
       last_category = COALESCE(EXCLUDED.last_category, brainx_patterns.last_category),
       last_status = COALESCE(EXCLUDED.last_status, brainx_patterns.last_status),
       promoted_to = COALESCE(EXCLUDED.promoted_to, brainx_patterns.promoted_to),
       updated_at = NOW()`,
    [
      memory.pattern_key,
      memory.recurrence_count,
      memory.first_seen,
      memory.last_seen,
      impactScore,
      memory.id,
      memory.id,
      memory.category || null,
      memory.status || null,
      memory.promoted_to || null
    ]
  );
}

async function storeMemory(memory) {
  // Pre-storage quality gate
  const contentStr = String(memory.content || '').trim();
  if (contentStr.length < 20) {
    const msg = `Quality gate: content too short (${contentStr.length} chars, min 20)`;
    if (process.env.BRAINX_STRICT_QUALITY === 'true') throw new Error(msg);
    console.warn(`⚠️  ${msg} — storing with importance=1`);
    memory.importance = Math.min(memory.importance || 1, 1);
  }

  // Reject known noise patterns
  const noisePatterns = [
    /^(ok|yes|no|sure|done|listo|sí|si|thanks|gracias)\.?$/i,
    /^HEARTBEAT_OK$/,
    /^NO_REPLY$/,
    /^\s*$/,
  ];
  for (const pat of noisePatterns) {
    if (pat.test(contentStr)) {
      const msg = `Quality gate: content matches noise pattern`;
      if (process.env.BRAINX_STRICT_QUALITY === 'true') throw new Error(msg);
      console.warn(`⚠️  ${msg} — skipping`);
      return { id: null, skipped: true, reason: 'noise_pattern' };
    }
  }

  const cfg = getPhase2Config();
  const lifecycle = normalizeLifecycle(memory);
  const piiEnabledForContext = shouldScrubForContext(memory.context, cfg);
  const scrubbedContent = scrubTextPII(memory.content, {
    enabled: piiEnabledForContext,
    replacement: cfg.piiScrubReplacement
  });
  const scrubbedContext = scrubTextPII(memory.context || '', {
    enabled: piiEnabledForContext,
    replacement: cfg.piiScrubReplacement
  });
  const redactionReasons = Array.from(new Set([...(scrubbedContent.reasons || []), ...(scrubbedContext.reasons || [])]));
  const redactionMeta = { redacted: redactionReasons.length > 0, reasons: redactionReasons };
  const storedContent = scrubbedContent.text;
  const storedContext = memory.context == null ? null : scrubbedContext.text;
  const storedTags = mergeTagsWithMetadata(memory.tags || [], redactionMeta);
  const embedding = await embed(`${memory.type}: ${storedContent} [context: ${storedContext || ''}]`);

  return db.withClient(async (client) => {
    await client.query('BEGIN');
    try {
      let finalId = memory.id;
      let finalRecurrence = lifecycle.recurrence_count;
      let finalFirstSeen = lifecycle.first_seen;
      let finalLastSeen = lifecycle.last_seen;
      let mergeSource = null;

      if (lifecycle.pattern_key) {
        const existing = await client.query(
          `SELECT id, recurrence_count, first_seen, last_seen
           FROM brainx_memories
           WHERE pattern_key = $1
           ORDER BY last_seen DESC NULLS LAST, created_at DESC
           LIMIT 1`,
          [lifecycle.pattern_key]
        );

        const plan = deriveMergePlan(existing.rows[0], lifecycle, lifecycle._now);
        if (plan.found) {
          finalId = plan.finalId;
          finalRecurrence = plan.finalRecurrence;
          finalFirstSeen = plan.finalFirstSeen;
          finalLastSeen = plan.finalLastSeen;
          mergeSource = 'pattern_key';
        } else {
          finalRecurrence = plan.finalRecurrence;
          finalFirstSeen = plan.finalFirstSeen;
          finalLastSeen = plan.finalLastSeen;
        }
      } else {
        const semantic = await client.query(
          `SELECT id, recurrence_count, first_seen, last_seen,
                  1 - (embedding <=> $1::vector) AS similarity
           FROM brainx_memories
           WHERE superseded_by IS NULL
             AND created_at >= NOW() - make_interval(days => $2)
             AND (($3::text IS NULL AND context IS NULL) OR context = $3)
             AND (($4::text IS NULL AND category IS NULL) OR category = $4)
           ORDER BY similarity DESC, last_seen DESC NULLS LAST, created_at DESC
           LIMIT 1`,
          [JSON.stringify(embedding), cfg.dedupeRecentDays, storedContext, lifecycle.category]
        );
        const candidate = semantic.rows[0];
        const candidateOk = candidate && Number(candidate.similarity || 0) >= cfg.dedupeSimThreshold;
        const plan = deriveMergePlan(candidateOk ? candidate : null, lifecycle, lifecycle._now);
        finalRecurrence = plan.finalRecurrence;
        finalFirstSeen = plan.finalFirstSeen;
        finalLastSeen = plan.finalLastSeen;
        if (plan.found) {
          finalId = plan.finalId;
          mergeSource = 'semantic';
        }
      }

      const resolvedAt = lifecycle.resolved_at || null;

      // V5 provenance fields — use memory value or DB default
      const sourceKind = memory.source_kind || memory.sourceKind || 'agent_inference';
      const sourcePath = memory.source_path || memory.sourcePath || null;
      const confidenceScore = memory.confidence_score ?? memory.confidenceScore ?? 0.7;
      const expiresAt = memory.expires_at || memory.expiresAt || null;
      const sensitivity = memory.sensitivity || 'normal';

      await client.query(
        `INSERT INTO brainx_memories (
           id, type, content, context, tier, agent, importance, embedding, tags,
           status, category, pattern_key, recurrence_count, first_seen, last_seen,
           resolved_at, promoted_to, resolution_notes,
           source_kind, source_path, confidence_score, expires_at, sensitivity
         )
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8::vector,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23)
         ON CONFLICT (id) DO UPDATE SET
           type=EXCLUDED.type,
           content=EXCLUDED.content,
           context=EXCLUDED.context,
           tier=EXCLUDED.tier,
           agent=EXCLUDED.agent,
           importance=EXCLUDED.importance,
           embedding=EXCLUDED.embedding,
           tags=EXCLUDED.tags,
           status=EXCLUDED.status,
           category=EXCLUDED.category,
           pattern_key=COALESCE(EXCLUDED.pattern_key, brainx_memories.pattern_key),
           recurrence_count=GREATEST(brainx_memories.recurrence_count, EXCLUDED.recurrence_count),
           first_seen=LEAST(brainx_memories.first_seen, EXCLUDED.first_seen),
           last_seen=GREATEST(brainx_memories.last_seen, EXCLUDED.last_seen),
           resolved_at=COALESCE(EXCLUDED.resolved_at, brainx_memories.resolved_at),
           promoted_to=COALESCE(EXCLUDED.promoted_to, brainx_memories.promoted_to),
           resolution_notes=COALESCE(EXCLUDED.resolution_notes, brainx_memories.resolution_notes),
           source_kind=COALESCE(EXCLUDED.source_kind, brainx_memories.source_kind),
           source_path=COALESCE(EXCLUDED.source_path, brainx_memories.source_path),
           confidence_score=COALESCE(EXCLUDED.confidence_score, brainx_memories.confidence_score),
           expires_at=COALESCE(EXCLUDED.expires_at, brainx_memories.expires_at),
           sensitivity=COALESCE(EXCLUDED.sensitivity, brainx_memories.sensitivity)`,
        [
          finalId,
          memory.type,
          storedContent,
          storedContext,
          memory.tier || 'warm',
          memory.agent || null,
          memory.importance ?? 5,
          JSON.stringify(embedding),
          storedTags,
          lifecycle.status,
          lifecycle.category,
          lifecycle.pattern_key,
          finalRecurrence,
          finalFirstSeen,
          finalLastSeen,
          resolvedAt,
          lifecycle.promoted_to,
          lifecycle.resolution_notes,
          sourceKind,
          sourcePath,
          confidenceScore !== null && confidenceScore !== undefined ? confidenceScore : null,
          expiresAt ? new Date(expiresAt) : null,
          sensitivity
        ]
      );

      await upsertPatternRecord(client, {
        ...memory,
        content: storedContent,
        context: storedContext,
        tags: storedTags,
        id: finalId,
        status: lifecycle.status,
        category: lifecycle.category,
        pattern_key: lifecycle.pattern_key,
        recurrence_count: finalRecurrence,
        first_seen: finalFirstSeen,
        last_seen: finalLastSeen,
        promoted_to: lifecycle.promoted_to
      });

      await client.query('COMMIT');
      return {
        id: finalId,
        pattern_key: lifecycle.pattern_key,
        recurrence_count: finalRecurrence,
        pii_scrub_applied: piiEnabledForContext,
        redacted: redactionMeta.redacted,
        redaction_reasons: redactionMeta.reasons,
        dedupe_merged: !!mergeSource,
        dedupe_method: mergeSource
      };
    } catch (err) {
      await client.query('ROLLBACK');
      throw err;
    }
  });
}

async function search(query, options = {}) {
  const {
    limit = 10,
    minImportance = 0,
    tierFilter = null,
    contextFilter = null,
    minSimilarity = 0.3
  } = options;

  const queryEmbedding = await embed(query);

  let sql = `
    SELECT id, type, content, context, tier, agent, importance, tags, created_at, last_accessed, access_count, source_session, superseded_by,
      status, category, pattern_key, recurrence_count, first_seen, last_seen, resolved_at, promoted_to, resolution_notes,
      source_kind, source_path, confidence_score, expires_at, sensitivity,
      1 - (embedding <=> $1::vector) AS similarity,
      (
        (1 - (embedding <=> $1::vector))
        + (LEAST(GREATEST(importance,0),10)::float / 10.0) * 0.25
        + (CASE tier
            WHEN 'hot' THEN 0.15
            WHEN 'warm' THEN 0.05
            WHEN 'cold' THEN -0.05
            WHEN 'archive' THEN -0.10
            ELSE 0
          END)
        + (COALESCE(feedback_score, 0)::float * 0.1)
        + (COALESCE(confidence_score, 0.7)::float * 0.1)
        + (1.0 / (1.0 + EXTRACT(EPOCH FROM (NOW() - COALESCE(last_accessed, created_at))) / 86400.0 * 0.005)) * 0.15
      ) AS score
    FROM brainx_memories
    WHERE importance >= $2
      AND superseded_by IS NULL
      AND (expires_at IS NULL OR expires_at > NOW())
      AND embedding IS NOT NULL
  `;

  const params = [JSON.stringify(queryEmbedding), minImportance];
  let i = 3;

  if (tierFilter) {
    sql += ` AND tier = $${i}`;
    params.push(tierFilter);
    i++;
  }
  if (contextFilter) {
    sql += ` AND context = $${i}`;
    params.push(contextFilter);
    i++;
  }

  sql += `
    ORDER BY score DESC, similarity DESC
    LIMIT $${i}
  `;
  params.push(limit);

  const results = await db.query(sql, params);

  const filtered = results.rows.filter(r => (r.similarity ?? 0) >= minSimilarity);

  const ids = filtered.map(r => r.id);
  if (ids.length) {
    await db.query(
      `UPDATE brainx_memories
       SET last_accessed = NOW(), access_count = access_count + 1
       WHERE id = ANY($1)`,
      [ids]
    );
  }

  // PII scrub on search results (defense-in-depth)
  const cfg = getPhase2Config();
  for (const row of filtered) {
    if (row.content) {
      const scrubbed = scrubTextPII(row.content, { enabled: true, replacement: cfg.piiScrubReplacement });
      row.content = scrubbed.text || scrubbed;
    }
    if (row.context) {
      const scrubbed = scrubTextPII(row.context, { enabled: true, replacement: cfg.piiScrubReplacement });
      row.context = scrubbed.text || scrubbed;
    }
  }

  return filtered;
}

async function logQueryEvent(event) {
  const {
    queryHash,
    kind = 'search',
    durationMs = null,
    resultsCount = null,
    avgSimilarity = null,
    topSimilarity = null
  } = event || {};
  if (!queryHash) return;

  try {
    await db.query(
      `INSERT INTO brainx_query_log (query_hash, query_kind, duration_ms, results_count, avg_similarity, top_similarity)
       VALUES ($1,$2,$3,$4,$5,$6)`,
      [queryHash, kind, durationMs, resultsCount, avgSimilarity, topSimilarity]
    );
  } catch (_) {
    // Logging must never break search/inject CLI flows.
  }
}

module.exports = { embed, storeMemory, search, logQueryEvent };
