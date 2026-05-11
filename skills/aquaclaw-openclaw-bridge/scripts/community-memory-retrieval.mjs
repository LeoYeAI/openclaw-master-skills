import {
  cloneCommunityMemoryNote,
  loadCommunityMemoryIndex,
  resolveCommunityMemoryPaths,
  saveCommunityMemoryIndex,
  touchCommunityMemoryNotes,
} from './community-memory-common.mjs';

export const COMMUNITY_MEMORY_AUTHORING_RETRIEVAL_LIMIT = 3;

function normalizeText(value) {
  return String(value ?? '').replace(/\s+/gu, ' ').trim();
}

function normalizeLower(value) {
  return normalizeText(value).toLowerCase();
}

function parseTimestamp(value) {
  const parsed = Date.parse(String(value ?? ''));
  return Number.isFinite(parsed) ? parsed : null;
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function noteTextIncludesHandle(note, handle) {
  const normalizedHandle = normalizeLower(handle);
  if (!normalizedHandle) {
    return false;
  }

  const haystack = normalizeLower([note?.summary, note?.body, ...(Array.isArray(note?.tags) ? note.tags : [])].join('\n'));
  return haystack.includes(`@${normalizedHandle}`) || haystack.includes(normalizedHandle);
}

function deriveTopicDomainFromNote(note) {
  for (const rawTag of Array.isArray(note?.tags) ? note.tags : []) {
    const tag = normalizeText(rawTag);
    if (!tag) {
      continue;
    }
    if (
      tag.startsWith('current:') ||
      tag.startsWith('phenomenon:') ||
      tag.startsWith('venue:') ||
      tag.startsWith('npc:') ||
      tag.startsWith('cue:')
    ) {
      continue;
    }
    return tag;
  }

  if (note?.sourceKind) {
    return String(note.sourceKind);
  }
  if (note?.venueSlug) {
    return `venue:${note.venueSlug}`;
  }
  return null;
}

function buildContextSignals({ authoringKind, plan, current, environment, contextItems }) {
  return {
    authoringKind,
    mode: plan?.mode === 'reply' ? 'reply' : authoringKind === 'dm' ? 'open' : 'create',
    currentKey: typeof current?.key === 'string' && current.key.trim() ? current.key.trim() : null,
    phenomenon:
      typeof environment?.phenomenon === 'string' && environment.phenomenon.trim() ? environment.phenomenon.trim() : null,
    venueSlug: typeof plan?.venueSlug === 'string' && plan.venueSlug.trim() ? plan.venueSlug.trim() : null,
    targetGatewayId:
      typeof plan?.targetGatewayId === 'string' && plan.targetGatewayId.trim()
        ? plan.targetGatewayId.trim()
        : typeof plan?.replyToGatewayId === 'string' && plan.replyToGatewayId.trim()
          ? plan.replyToGatewayId.trim()
          : null,
    targetGatewayHandle:
      typeof plan?.targetGatewayHandle === 'string' && plan.targetGatewayHandle.trim()
        ? plan.targetGatewayHandle.trim()
        : typeof plan?.replyToGatewayHandle === 'string' && plan.replyToGatewayHandle.trim()
          ? plan.replyToGatewayHandle.trim()
          : null,
    targetExpressionId:
      typeof plan?.replyToExpressionId === 'string' && plan.replyToExpressionId.trim() ? plan.replyToExpressionId.trim() : null,
    rootExpressionId:
      typeof plan?.rootExpressionId === 'string' && plan.rootExpressionId.trim() ? plan.rootExpressionId.trim() : null,
    threadExpressionIds: Array.isArray(contextItems)
      ? contextItems.map((item) => (typeof item?.id === 'string' && item.id.trim() ? item.id.trim() : null)).filter(Boolean)
      : [],
    threadHandles: Array.isArray(contextItems)
      ? contextItems
          .flatMap((item) => [
            typeof item?.gateway?.handle === 'string' ? item.gateway.handle : null,
            typeof item?.replyToGateway?.handle === 'string' ? item.replyToGateway.handle : null,
          ])
          .filter(Boolean)
      : [],
  };
}

function scoreCommunityMemoryNote(note, signals, nowTimestamp) {
  const noteTags = new Set((Array.isArray(note?.tags) ? note.tags : []).map((tag) => normalizeLower(tag)));
  const categories = new Set();
  let score = 0;

  const add = (category, delta) => {
    categories.add(category);
    score += delta;
  };

  if (signals.currentKey && noteTags.has(`current:${normalizeLower(signals.currentKey)}`)) {
    add('current', 4);
  }
  if (signals.phenomenon && noteTags.has(`phenomenon:${normalizeLower(signals.phenomenon)}`)) {
    add('phenomenon', 3);
  }
  if (
    signals.venueSlug &&
    (normalizeLower(note?.venueSlug) === normalizeLower(signals.venueSlug) ||
      noteTags.has(`venue:${normalizeLower(signals.venueSlug)}`))
  ) {
    add('venue', 4);
  }
  if (
    signals.targetGatewayId &&
    Array.isArray(note?.relatedGatewayIds) &&
    note.relatedGatewayIds.includes(signals.targetGatewayId)
  ) {
    add('target_gateway', 5);
  }
  if (signals.targetGatewayHandle && noteTextIncludesHandle(note, signals.targetGatewayHandle)) {
    add('target_handle', 2.5);
  }
  if (
    signals.targetExpressionId &&
    Array.isArray(note?.relatedExpressionIds) &&
    note.relatedExpressionIds.includes(signals.targetExpressionId)
  ) {
    add('target_expression', 6);
  } else if (
    signals.rootExpressionId &&
    Array.isArray(note?.relatedExpressionIds) &&
    note.relatedExpressionIds.includes(signals.rootExpressionId)
  ) {
    add('root_expression', 4.5);
  } else if (
    Array.isArray(note?.relatedExpressionIds) &&
    signals.threadExpressionIds.some((expressionId) => note.relatedExpressionIds.includes(expressionId))
  ) {
    add('thread_expression', 3);
  }
  if (signals.threadHandles.some((handle) => noteTextIncludesHandle(note, handle))) {
    add('thread_handle', 1.5);
  }

  const freshnessScore = Number.isFinite(note?.freshnessScore) ? clamp(note.freshnessScore, 0, 1) : 0;
  score += freshnessScore * 1.5;

  const freshUntilTimestamp = parseTimestamp(note?.freshUntil);
  if (freshUntilTimestamp !== null) {
    score += freshUntilTimestamp >= nowTimestamp ? 1 : -4;
  }

  const createdAtTimestamp = parseTimestamp(note?.createdAt);
  if (createdAtTimestamp !== null) {
    const ageHours = Math.max(0, (nowTimestamp - createdAtTimestamp) / 3_600_000);
    score -= Math.min(ageHours / 72, 2.5);
  }

  if (Number.isFinite(note?.localRetrievedCount) && note.localRetrievedCount > 0) {
    score -= Math.min(note.localRetrievedCount * 1.25, 4);
  }
  if (Number.isFinite(note?.localUsedCount) && note.localUsedCount > 0) {
    score -= Math.min(note.localUsedCount * 1.5, 5);
  }

  const localRetrievedTimestamp = parseTimestamp(note?.localRetrievedAt);
  if (localRetrievedTimestamp !== null && nowTimestamp - localRetrievedTimestamp < 24 * 3_600_000) {
    score -= 0.75;
  }

  return {
    categories,
    note,
    score,
  };
}

function derivePersonalAngleFromNotes(notes) {
  const first = notes[0] ?? null;
  if (!first) {
    return 'Let the current sea state decide what feels worth saying; avoid generic filler.';
  }

  if (first.mentionPolicy === 'private_only') {
    return 'Keep the remembered note fully private; use it only as background subtext and never surface it directly.';
  }
  if (first.mentionPolicy === 'paraphrase_ok') {
    return 'Let the remembered note tilt tone, emphasis, or an indirect callback without framing it as private gossip.';
  }
  return 'You may surface the remembered hook more directly if it stays natural, but never cite a secret source or quote a note.';
}

function buildCommunityIntent({ authoringKind, plan, current, environment, retrievedNotes }) {
  const mode =
    authoringKind === 'dm'
      ? plan?.mode === 'reply'
        ? 'dm_reply'
        : 'dm_open'
      : plan?.mode === 'reply'
        ? 'reply'
        : 'initiate';

  const speechAct =
    plan?.mode === 'reply'
      ? retrievedNotes.some((note) => note.mentionPolicy === 'public_ok')
        ? 'callback'
        : authoringKind === 'dm'
          ? 'resonate'
          : 'extend'
      : retrievedNotes.length > 0
        ? authoringKind === 'dm'
          ? 'tease'
          : 'riff'
        : 'observe';

  const socialGoal =
    authoringKind === 'dm'
      ? plan?.mode === 'reply'
        ? 'continue_thread'
        : 'reinforce_relationship'
      : plan?.mode === 'reply'
        ? 'answer_target'
        : 'start_topic';

  const anchor =
    authoringKind === 'dm'
      ? {
          kind: 'dm_thread',
          id: typeof plan?.conversationId === 'string' && plan.conversationId.trim() ? plan.conversationId.trim() : null,
        }
      : plan?.mode === 'reply'
        ? {
            kind: 'public_thread',
            id:
              typeof plan?.replyToExpressionId === 'string' && plan.replyToExpressionId.trim()
                ? plan.replyToExpressionId.trim()
                : typeof plan?.rootExpressionId === 'string' && plan.rootExpressionId.trim()
                  ? plan.rootExpressionId.trim()
                  : null,
          }
        : retrievedNotes.length > 0
          ? { kind: 'community_memory', id: retrievedNotes[0].id }
          : {
              kind: 'current_environment',
              id:
                typeof current?.id === 'string' && current.id.trim()
                  ? current.id.trim()
                  : typeof current?.key === 'string' && current.key.trim()
                    ? current.key.trim()
                    : typeof environment?.phenomenon === 'string' && environment.phenomenon.trim()
                      ? environment.phenomenon.trim()
                      : null,
            };

  const topicDomain =
    deriveTopicDomainFromNote(retrievedNotes[0]) ??
    (typeof current?.key === 'string' && current.key.trim() ? `current:${current.key.trim()}` : null) ??
    (typeof environment?.phenomenon === 'string' && environment.phenomenon.trim()
      ? `phenomenon:${environment.phenomenon.trim()}`
      : null);

  const relevanceConstraint =
    authoringKind === 'dm'
      ? 'Stay loyal to the DM thread; use remembered notes only when they sharpen the exchange instead of derailing it.'
      : plan?.mode === 'reply'
        ? 'Answer the target public line directly first; remembered notes are only supporting angle, not an excuse to go generic.'
        : 'Use remembered notes only if they genuinely help this Claw start a relevant line right now.';

  return {
    mode,
    speechAct,
    socialGoal,
    anchor,
    topicDomain,
    personalAngle: derivePersonalAngleFromNotes(retrievedNotes),
    retrievedNoteIds: retrievedNotes.map((note) => note.id),
    relevanceConstraint,
    summary:
      retrievedNotes.length > 0
        ? `Lean on ${retrievedNotes[0].id} as background angle only if it helps this turn stay relevant.`
        : 'Drive the line from current water, thread context, and this Claw\'s own voice instead of filler.',
  };
}

export async function retrieveCommunityMemoryForAuthoring({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
  communityMemoryDir = process.env.AQUACLAW_COMMUNITY_MEMORY_DIR,
  authoringKind,
  plan,
  current = null,
  environment = null,
  contextItems = [],
  now = new Date().toISOString(),
} = {}) {
  if (authoringKind !== 'public' && authoringKind !== 'dm') {
    throw new Error('authoringKind must be public or dm');
  }

  const paths = resolveCommunityMemoryPaths({
    workspaceRoot,
    configPath,
    communityMemoryDir,
  });
  const indexResult = await loadCommunityMemoryIndex(paths);
  const nowTimestamp = parseTimestamp(now) ?? Date.now();
  const signals = buildContextSignals({
    authoringKind,
    plan,
    current,
    environment,
    contextItems,
  });

  const rankedNotes = (indexResult.index?.items ?? [])
    .map((note) => scoreCommunityMemoryNote(note, signals, nowTimestamp))
    .filter((entry) => entry.categories.size > 0 && entry.score >= 3.5)
    .sort((left, right) => {
      if (right.score !== left.score) {
        return right.score - left.score;
      }
      const rightCreatedAt = parseTimestamp(right.note?.createdAt) ?? 0;
      const leftCreatedAt = parseTimestamp(left.note?.createdAt) ?? 0;
      return rightCreatedAt - leftCreatedAt;
    })
    .slice(0, COMMUNITY_MEMORY_AUTHORING_RETRIEVAL_LIMIT);

  const retrievedNotes = rankedNotes.map((entry) => cloneCommunityMemoryNote(entry.note));
  const retrievedNoteIds = retrievedNotes.map((note) => note.id);
  const communityIntent = buildCommunityIntent({
    authoringKind,
    plan,
    current,
    environment,
    retrievedNotes,
  });

  if (indexResult.recovered || retrievedNoteIds.length > 0) {
    const nextIndex =
      retrievedNoteIds.length > 0
        ? touchCommunityMemoryNotes(indexResult.index, {
            retrievedIds: retrievedNoteIds,
            at: now,
          })
        : indexResult.index;
    await saveCommunityMemoryIndex(paths.indexPath, nextIndex);
  }

  return {
    paths,
    communityIntent,
    indexRecovered: indexResult.recovered,
    indexRecoveryReason: indexResult.recoveryReason,
    retrievedNoteIds,
    retrievedNotes,
  };
}

export async function markCommunityMemoryNotesUsed({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
  communityMemoryDir = process.env.AQUACLAW_COMMUNITY_MEMORY_DIR,
  noteIds = [],
  at = new Date().toISOString(),
} = {}) {
  const normalizedIds = noteIds.filter((value) => typeof value === 'string' && value.trim()).map((value) => value.trim());
  const paths = resolveCommunityMemoryPaths({
    workspaceRoot,
    configPath,
    communityMemoryDir,
  });

  if (normalizedIds.length === 0) {
    return {
      paths,
      touched: 0,
    };
  }

  const indexResult = await loadCommunityMemoryIndex(paths);
  const nextIndex = touchCommunityMemoryNotes(indexResult.index, {
    usedIds: normalizedIds,
    at,
  });
  await saveCommunityMemoryIndex(paths.indexPath, nextIndex);

  return {
    paths,
    indexRecovered: indexResult.recovered,
    indexRecoveryReason: indexResult.recoveryReason,
    touched: normalizedIds.length,
  };
}
