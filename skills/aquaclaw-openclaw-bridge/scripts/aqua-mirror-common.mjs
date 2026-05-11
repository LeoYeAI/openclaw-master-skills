import { appendFile, mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

import { resolveMirrorRootPath, resolveWorkspaceRoot } from './hosted-aqua-common.mjs';

export const DEFAULT_MIRROR_RELATIVE_DIR = path.join('.aquaclaw', 'mirror');
export const DEFAULT_STATE_FILE_NAME = 'state.json';
export const DEFAULT_CONTEXT_RELATIVE_PATH = path.join('context', 'latest.json');
export const DEFAULT_CONVERSATION_INDEX_RELATIVE_PATH = path.join('conversations', 'index.json');
export const DEFAULT_SEA_EVENTS_RELATIVE_PATH = path.join('sea-events');
export const DEFAULT_CONVERSATIONS_RELATIVE_PATH = path.join('conversations');
export const DEFAULT_PUBLIC_THREADS_RELATIVE_PATH = path.join('public-threads');
export const DEFAULT_RECENT_DELIVERY_LIMIT = 20;
export const MIRROR_MEMORY_BOUNDARY_VERSION = 1;
export const MIRROR_MEMORY_BOUNDARY_BASELINE = Object.freeze({
  version: MIRROR_MEMORY_BOUNDARY_VERSION,
  classes: Object.freeze({
    cache:
      'Rebuildable operational mirror state. Scripts may overwrite these files in place, and losing them should not destroy the underlying autobiographical signal.',
    'memory-source':
      'Raw local autobiographical input owned by this OpenClaw install. Keep by default; future sea diary or memory synthesis should derive from these files instead of live-only reads.',
  }),
  retention: Object.freeze({
    cache: 'keep_latest_only',
    'memory-source': 'retain_by_default_until_explicit_archive_or_redaction',
  }),
  compaction: Object.freeze({
    baseline:
      'Compaction may create derivative summaries or archives, but current scripts must not silently delete raw memory-source files.',
    implemented: false,
  }),
  redaction: Object.freeze({
    baseline:
      'Do not publish raw mirror files by default. Review and redact participant message bodies, handles, gateway ids, and any machine-local secrets before sharing outside the local machine.',
    personaBoundary:
      'Workspace persona files such as SOUL.md, USER.md, TOOLS.md, and MEMORY.md must stay separate from mirror files.',
  }),
});
export const MIRROR_MEMORY_FILE_POLICIES = Object.freeze([
  Object.freeze({
    key: 'state',
    classification: 'cache',
    relativePathPattern: DEFAULT_STATE_FILE_NAME,
    retentionPolicy: 'replace_latest',
    purpose: 'Operational cursor, freshness, gap-repair, and sync state.',
    compactionRule: 'No historical retention requirement; overwrite in place.',
    redactionRule: 'Do not share raw because it may reveal local runtime linkage or recent mirror internals.',
  }),
  Object.freeze({
    key: 'context_snapshot',
    classification: 'cache',
    relativePathPattern: DEFAULT_CONTEXT_RELATIVE_PATH,
    retentionPolicy: 'replace_latest',
    purpose: 'Latest mirror-backed aquarium snapshot for brief reads and status explanation.',
    compactionRule: 'Keep only the newest snapshot; rebuildable from live APIs plus recent mirror state.',
    redactionRule: 'Review before sharing because it may expose participant-visible runtime or environment context.',
  }),
  Object.freeze({
    key: 'conversation_index',
    classification: 'cache',
    relativePathPattern: DEFAULT_CONVERSATION_INDEX_RELATIVE_PATH,
    retentionPolicy: 'replace_latest',
    purpose: 'Latest hosted participant DM inbox summary used to target thread refresh.',
    compactionRule: 'Keep only the newest index snapshot.',
    redactionRule: 'Treat as private social metadata; do not publish raw.',
  }),
  Object.freeze({
    key: 'sea_events',
    classification: 'memory-source',
    relativePathPattern: path.join(DEFAULT_SEA_EVENTS_RELATIVE_PATH, 'YYYY-MM-DD.ndjson'),
    retentionPolicy: 'append_only_retain',
    purpose: 'Append-only raw visible event history and the primary future sea-diary input.',
    compactionRule: 'Future compaction may create summaries, but raw event logs should remain until explicit archive/redaction.',
    redactionRule: 'Review before sharing because event summaries can reveal private or friend-scoped social activity.',
  }),
  Object.freeze({
    key: 'conversation_threads',
    classification: 'memory-source',
    relativePathPattern: path.join(DEFAULT_CONVERSATIONS_RELATIVE_PATH, '<conversation-id>.json'),
    retentionPolicy: 'replace_latest_per_thread',
    purpose: 'Materialized visible DM thread history for future autobiographical synthesis.',
    compactionRule: 'May be archived or summarized later, but raw thread files are memory-source by default.',
    redactionRule: 'Private social content; never share raw without explicit review and redaction.',
  }),
  Object.freeze({
    key: 'public_threads',
    classification: 'memory-source',
    relativePathPattern: path.join(DEFAULT_PUBLIC_THREADS_RELATIVE_PATH, '<root-expression-id>.json'),
    retentionPolicy: 'replace_latest_per_thread',
    purpose: 'Materialized visible public-thread history relevant to this Claw.',
    compactionRule: 'May be summarized later; raw thread files remain the source layer by default.',
    redactionRule: 'Still review before sharing because replies may reveal handles, timing, and local curation choices.',
  }),
]);

export function resolveMirrorPaths({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
  mirrorDir = process.env.AQUACLAW_MIRROR_DIR,
  stateFile = process.env.AQUACLAW_MIRROR_STATE_FILE,
  mode = 'auto',
} = {}) {
  const resolvedWorkspaceRoot = resolveWorkspaceRoot(workspaceRoot);
  const resolvedMirrorRoot = stateFile
    ? path.dirname(path.resolve(stateFile))
    : resolveMirrorRootPath({
        workspaceRoot: resolvedWorkspaceRoot,
        configPath,
        mirrorDir,
        mode,
      });

  return {
    workspaceRoot: resolvedWorkspaceRoot,
    mirrorRoot: resolvedMirrorRoot,
    statePath: stateFile ? path.resolve(stateFile) : path.join(resolvedMirrorRoot, DEFAULT_STATE_FILE_NAME),
    contextPath: path.join(resolvedMirrorRoot, DEFAULT_CONTEXT_RELATIVE_PATH),
    seaEventsDir: path.join(resolvedMirrorRoot, DEFAULT_SEA_EVENTS_RELATIVE_PATH),
    conversationsDir: path.join(resolvedMirrorRoot, DEFAULT_CONVERSATIONS_RELATIVE_PATH),
    conversationIndexPath: path.join(resolvedMirrorRoot, DEFAULT_CONVERSATION_INDEX_RELATIVE_PATH),
    publicThreadsDir: path.join(resolvedMirrorRoot, DEFAULT_PUBLIC_THREADS_RELATIVE_PATH),
  };
}

function resolveBoundaryRelativePath(paths, key, relativePathPattern) {
  if (!paths) {
    return relativePathPattern;
  }

  switch (key) {
    case 'state':
      return relativeMirrorPath(paths, paths.statePath);
    case 'context_snapshot':
      return relativeMirrorPath(paths, paths.contextPath);
    case 'conversation_index':
      return relativeMirrorPath(paths, paths.conversationIndexPath);
    case 'sea_events':
      return path.join(path.relative(paths.mirrorRoot, paths.seaEventsDir), 'YYYY-MM-DD.ndjson');
    case 'conversation_threads':
      return path.join(path.relative(paths.mirrorRoot, paths.conversationsDir), '<conversation-id>.json');
    case 'public_threads':
      return path.join(path.relative(paths.mirrorRoot, paths.publicThreadsDir), '<root-expression-id>.json');
    default:
      return relativePathPattern;
  }
}

export function buildMirrorMemoryBoundary(paths = null) {
  return {
    ...MIRROR_MEMORY_BOUNDARY_BASELINE,
    files: MIRROR_MEMORY_FILE_POLICIES.map((policy) => ({
      ...policy,
      relativePathPattern: resolveBoundaryRelativePath(paths, policy.key, policy.relativePathPattern),
    })),
  };
}

function normalizeMirrorRelativePath(relativePath) {
  return String(relativePath || '')
    .split(path.sep)
    .join('/')
    .replace(/^\.\//, '')
    .replace(/^\/+/, '')
    .trim();
}

export function matchMirrorFilePolicy(relativePath) {
  const normalized = normalizeMirrorRelativePath(relativePath);
  if (!normalized) {
    return null;
  }

  if (normalized === DEFAULT_STATE_FILE_NAME) {
    return MIRROR_MEMORY_FILE_POLICIES.find((policy) => policy.key === 'state') ?? null;
  }
  if (normalized === normalizeMirrorRelativePath(DEFAULT_CONTEXT_RELATIVE_PATH)) {
    return MIRROR_MEMORY_FILE_POLICIES.find((policy) => policy.key === 'context_snapshot') ?? null;
  }
  if (normalized === normalizeMirrorRelativePath(DEFAULT_CONVERSATION_INDEX_RELATIVE_PATH)) {
    return MIRROR_MEMORY_FILE_POLICIES.find((policy) => policy.key === 'conversation_index') ?? null;
  }
  if (
    normalized.startsWith(`${normalizeMirrorRelativePath(DEFAULT_SEA_EVENTS_RELATIVE_PATH)}/`) &&
    normalized.endsWith('.ndjson')
  ) {
    return MIRROR_MEMORY_FILE_POLICIES.find((policy) => policy.key === 'sea_events') ?? null;
  }
  if (
    normalized.startsWith(`${normalizeMirrorRelativePath(DEFAULT_CONVERSATIONS_RELATIVE_PATH)}/`) &&
    normalized.endsWith('.json')
  ) {
    return MIRROR_MEMORY_FILE_POLICIES.find((policy) => policy.key === 'conversation_threads') ?? null;
  }
  if (
    normalized.startsWith(`${normalizeMirrorRelativePath(DEFAULT_PUBLIC_THREADS_RELATIVE_PATH)}/`) &&
    normalized.endsWith('.json')
  ) {
    return MIRROR_MEMORY_FILE_POLICIES.find((policy) => policy.key === 'public_threads') ?? null;
  }

  return null;
}

export function classifyMirrorRelativePath(relativePath) {
  return matchMirrorFilePolicy(relativePath)?.classification ?? null;
}

export function createDefaultMirrorState() {
  return {
    version: 1,
    mode: null,
    hubUrl: null,
    updatedAt: null,
    viewer: {
      kind: null,
      id: null,
      handle: null,
      displayName: null,
    },
    stream: {
      lastDeliveryId: null,
      lastSeaEventId: null,
      lastHelloAt: null,
      lastEventAt: null,
      lastResyncRequiredAt: null,
      lastRejectedCursor: null,
      reconnectCount: 0,
      resyncCount: 0,
      lastError: null,
    },
    mirror: {
      lastContextSyncAt: null,
      lastConversationIndexSyncAt: null,
      lastConversationThreadSyncAt: null,
      lastPublicThreadSyncAt: null,
    },
    gapRepair: {
      lastVisibleFeedEventId: null,
      lastAttemptAt: null,
      lastCompletedAt: null,
      lastStatus: null,
      lastReason: null,
      lastError: null,
      scannedPageCount: 0,
      recoveredEventCount: 0,
      anchorSeaEventId: null,
      newestRecoveredSeaEventId: null,
      oldestRecoveredSeaEventId: null,
    },
    recentDeliveries: [],
    conversations: {
      items: [],
      byId: {},
    },
    publicThreads: {
      byRootId: {},
    },
  };
}

export async function loadMirrorState(statePath) {
  try {
    const raw = await readFile(statePath, 'utf8');
    const parsed = JSON.parse(raw);
    return normalizeMirrorState(parsed);
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return createDefaultMirrorState();
    }
    throw error;
  }
}

export async function saveMirrorState(statePath, state) {
  await writeJsonFile(statePath, {
    ...state,
    updatedAt: new Date().toISOString(),
  });
}

export async function writeJsonFile(filePath, value) {
  await mkdir(path.dirname(filePath), { recursive: true });
  const tempPath = `${filePath}.tmp-${process.pid}-${Date.now()}`;
  await writeFile(tempPath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
  await rename(tempPath, filePath);
}

export async function appendNdjson(filePath, value) {
  await mkdir(path.dirname(filePath), { recursive: true });
  await appendFile(filePath, `${JSON.stringify(value)}\n`, 'utf8');
}

export function normalizeMirrorState(input) {
  const base = createDefaultMirrorState();
  if (!input || typeof input !== 'object') {
    return base;
  }
  if (input.version !== 1) {
    throw new Error('unsupported mirror state version');
  }

  return {
    ...base,
    ...input,
    viewer: {
      ...base.viewer,
      ...(input.viewer && typeof input.viewer === 'object' ? input.viewer : {}),
    },
    stream: {
      ...base.stream,
      ...(input.stream && typeof input.stream === 'object' ? input.stream : {}),
    },
    mirror: {
      ...base.mirror,
      ...(input.mirror && typeof input.mirror === 'object' ? input.mirror : {}),
    },
    gapRepair: {
      ...base.gapRepair,
      ...(input.gapRepair && typeof input.gapRepair === 'object' ? input.gapRepair : {}),
    },
    recentDeliveries: Array.isArray(input.recentDeliveries) ? input.recentDeliveries : [],
    conversations: {
      ...base.conversations,
      ...(input.conversations && typeof input.conversations === 'object' ? input.conversations : {}),
      items: Array.isArray(input?.conversations?.items) ? input.conversations.items : [],
      byId:
        input?.conversations?.byId && typeof input.conversations.byId === 'object'
          ? input.conversations.byId
          : {},
    },
    publicThreads: {
      ...base.publicThreads,
      ...(input.publicThreads && typeof input.publicThreads === 'object' ? input.publicThreads : {}),
      byRootId:
        input?.publicThreads?.byRootId && typeof input.publicThreads.byRootId === 'object'
          ? input.publicThreads.byRootId
          : {},
    },
  };
}

export function conversationThreadPath(paths, conversationId) {
  return path.join(paths.conversationsDir, `${conversationId}.json`);
}

export function publicThreadPath(paths, rootExpressionId) {
  return path.join(paths.publicThreadsDir, `${rootExpressionId}.json`);
}

export const conversationFilePath = conversationThreadPath;
export const publicThreadFilePath = publicThreadPath;

export function relativeMirrorPath(paths, filePath) {
  return path.relative(paths.mirrorRoot, filePath);
}

export function datePartitionFromIso(value) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return new Date().toISOString().slice(0, 10);
  }
  return parsed.toISOString().slice(0, 10);
}

export function deriveSeaEventActivityGatewayIds(seaEvent) {
  return Array.from(
    new Set(
      [seaEvent?.actorGatewayId, seaEvent?.subjectGatewayId, seaEvent?.objectGatewayId].filter(
        (value) => typeof value === 'string' && value.trim(),
      ),
    ),
  );
}

export function buildStoredDeliveryRecord(delivery, recordedAt = new Date().toISOString()) {
  return {
    source: 'stream',
    recordedAt,
    deliveryId: delivery?.id ?? null,
    activityGatewayIds: Array.isArray(delivery?.activityGatewayIds)
      ? delivery.activityGatewayIds
      : deriveSeaEventActivityGatewayIds(delivery?.seaEvent),
    currentChanged: delivery?.currentChanged === true,
    seaEvent: delivery?.seaEvent ?? null,
  };
}

export function buildStoredSeaEventRecord(seaEvent, recordedAt = new Date().toISOString(), source = 'feed_repair') {
  return {
    source,
    recordedAt,
    deliveryId: null,
    activityGatewayIds: deriveSeaEventActivityGatewayIds(seaEvent),
    currentChanged: seaEvent?.type === 'current.changed',
    seaEvent: seaEvent ?? null,
  };
}

export function isSeaEventVisibleInFeedRepair(event, viewerKind) {
  if (!event || typeof event !== 'object') {
    return false;
  }
  if (viewerKind === 'gateway') {
    return event.visibility !== 'system';
  }
  return true;
}

function deliveryRecordKey(record) {
  return record?.deliveryId ?? record?.seaEvent?.id ?? null;
}

export function pushRecentDelivery(records, nextRecord, maxItems = DEFAULT_RECENT_DELIVERY_LIMIT) {
  const existing = Array.isArray(records) ? records : [];
  const nextKey = deliveryRecordKey(nextRecord);
  const filtered = nextKey ? existing.filter((record) => deliveryRecordKey(record) !== nextKey) : [...existing];
  filtered.push(nextRecord);
  return filtered.slice(Math.max(filtered.length - maxItems, 0));
}

function trimString(value) {
  return typeof value === 'string' && value.trim() ? value.trim() : null;
}

export function extractDeliveryHints(delivery) {
  const event = delivery?.seaEvent;
  const metadata = event?.metadata && typeof event.metadata === 'object' ? event.metadata : {};
  const conversationId = trimString(metadata.conversationId);
  const messageId = trimString(metadata.messageId);
  const expressionId = trimString(metadata.expressionId);
  const rootExpressionId = trimString(metadata.rootExpressionId) ?? expressionId;

  return {
    refreshContext: event?.type === 'current.changed' || event?.type === 'environment.changed',
    refreshConversationIndex:
      event?.type === 'conversation.started' ||
      event?.type === 'conversation.message_sent' ||
      event?.type === 'friend_request.accepted' ||
      event?.type === 'friendship.removed',
    conversationUpdates: conversationId ? [{ conversationId, messageId }] : [],
    publicThreadUpdates: rootExpressionId ? [{ rootExpressionId, expressionId }] : [],
  };
}

export function parseSseEventBlock(block) {
  const lines = String(block || '').split('\n');
  let event = 'message';
  let id = null;
  const dataLines = [];

  for (const line of lines) {
    if (!line || line.startsWith(':')) {
      continue;
    }

    const separatorIndex = line.indexOf(':');
    const field = separatorIndex >= 0 ? line.slice(0, separatorIndex) : line;
    const rawValue = separatorIndex >= 0 ? line.slice(separatorIndex + 1).trimStart() : '';

    if (field === 'event') {
      event = rawValue;
      continue;
    }
    if (field === 'id') {
      id = rawValue;
      continue;
    }
    if (field === 'data') {
      dataLines.push(rawValue);
    }
  }

  if (!dataLines.length && event === 'message' && id === null) {
    return null;
  }

  return {
    event,
    id,
    data: dataLines.length ? JSON.parse(dataLines.join('\n')) : null,
  };
}
