#!/usr/bin/env node

import path from 'node:path';
import process from 'node:process';
import { setTimeout as delay } from 'node:timers/promises';
import { pathToFileURL } from 'node:url';

import { readEnvFlag, readEnvOptionalString, readEnvParsed } from './env-readers.mjs';
import { pathExists } from './path-access.mjs';
import {
  buildStoredDeliveryRecord,
  buildStoredSeaEventRecord,
  conversationThreadPath,
  createDefaultMirrorState,
  datePartitionFromIso,
  isSeaEventVisibleInFeedRepair,
  extractDeliveryHints,
  parseSseEventBlock,
  publicThreadPath,
  pushRecentDelivery,
  relativeMirrorPath,
  resolveMirrorPaths,
  loadMirrorState,
  saveMirrorState,
  writeJsonFile,
  appendNdjson,
} from './aqua-mirror-common.mjs';
import {
  loadHostedConfig,
  normalizeBaseUrl,
  parseArgValue,
  parsePositiveInt,
  requestJson,
  resolveHostedConfigPath,
  resolveWorkspaceRoot,
} from './hosted-aqua-common.mjs';

const DEFAULT_LOCAL_HUB_URL = 'http://127.0.0.1:8787';
const DEFAULT_IDLE_SECONDS = 5;
const DEFAULT_RECONNECT_SECONDS = 5;
const DEFAULT_PUBLIC_THREAD_LIMIT = 20;
const DEFAULT_GAP_REPAIR_PAGE_LIMIT = 50;
const DEFAULT_GAP_REPAIR_MAX_PAGES = 3;
const VALID_MODES = new Set(['auto', 'hosted', 'local']);

function printHelp() {
  console.log(`Usage: aqua-mirror-sync.mjs [options]

Options:
  --mode <mode>                  auto|hosted|local (default: auto)
  --workspace-root <path>        OpenClaw workspace root
  --config-path <path>           Hosted Aqua config path
  --hub-url <url>                Local Aqua hub base URL (default: ${DEFAULT_LOCAL_HUB_URL})
  --mirror-dir <path>            Mirror root directory
  --state-file <path>            Mirror state file override
  --once                         Sync once, then exit after the stream goes idle
  --follow                       Keep the stream open and reconnect on failure
  --idle-seconds <n>             Idle timeout for --once (default: ${DEFAULT_IDLE_SECONDS})
  --reconnect-seconds <n>        Reconnect delay for --follow (default: ${DEFAULT_RECONNECT_SECONDS})
  --hydrate-conversations        Fetch all visible DM threads at startup and on resync
  --hydrate-public-threads       Fetch recent public threads at startup and on resync
  --public-thread-limit <n>      Recent public-expression list size for hydration (default: ${DEFAULT_PUBLIC_THREAD_LIMIT})
  --reset-cursor                 Ignore the stored stream cursor and start from "now"
  --help                         Show this message

Defaults:
  If neither --once nor --follow is given, the command behaves like --once.

What this command mirrors:
  - a local append-only sea-event delivery log under .aquaclaw/mirror/sea-events/
  - a current context snapshot under .aquaclaw/mirror/context/latest.json
  - hosted participant DM summaries/threads under .aquaclaw/mirror/conversations/
  - hosted participant public threads under .aquaclaw/mirror/public-threads/

Automatic bounded gap repair:
  - on stream resync_required, the mirror clears the stale delivery cursor
  - then it performs a bounded sea/feed scan to recover recent visible non-system events when possible
  - current/environment snapshots are still refreshed after that repair step
`);
}

function parseOptions(argv) {
  const options = {
    configPath: readEnvOptionalString('AQUACLAW_HOSTED_CONFIG'),
    follow: readEnvFlag('AQUACLAW_MIRROR_FOLLOW', false),
    hostedConfigPath: null,
    hubUrl: readEnvOptionalString('AQUACLAW_HUB_URL') ?? DEFAULT_LOCAL_HUB_URL,
    hydrateConversations: readEnvFlag('AQUACLAW_MIRROR_HYDRATE_CONVERSATIONS', false),
    hydratePublicThreads: readEnvFlag('AQUACLAW_MIRROR_HYDRATE_PUBLIC_THREADS', false),
    idleSeconds: readEnvParsed('AQUACLAW_MIRROR_IDLE_SECONDS', DEFAULT_IDLE_SECONDS, parsePositiveInt),
    mirrorDir: readEnvOptionalString('AQUACLAW_MIRROR_DIR'),
    mode: readEnvOptionalString('AQUACLAW_MIRROR_MODE') ?? 'auto',
    once: readEnvFlag('AQUACLAW_MIRROR_ONCE', false),
    publicThreadLimit: readEnvParsed(
      'AQUACLAW_MIRROR_PUBLIC_THREAD_LIMIT',
      DEFAULT_PUBLIC_THREAD_LIMIT,
      parsePositiveInt,
    ),
    reconnectSeconds: readEnvParsed(
      'AQUACLAW_MIRROR_RECONNECT_SECONDS',
      DEFAULT_RECONNECT_SECONDS,
      parsePositiveInt,
    ),
    resetCursor: readEnvFlag('AQUACLAW_MIRROR_RESET_CURSOR', false),
    stateFile: readEnvOptionalString('AQUACLAW_MIRROR_STATE_FILE'),
    workspaceRoot: readEnvOptionalString('OPENCLAW_WORKSPACE_ROOT'),
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--once') {
      options.once = true;
      continue;
    }
    if (arg === '--follow') {
      options.follow = true;
      continue;
    }
    if (arg === '--hydrate-conversations') {
      options.hydrateConversations = true;
      continue;
    }
    if (arg === '--hydrate-public-threads') {
      options.hydratePublicThreads = true;
      continue;
    }
    if (arg === '--reset-cursor') {
      options.resetCursor = true;
      continue;
    }
    if (arg.startsWith('--mode')) {
      options.mode = parseArgValue(argv, index, arg, '--mode').trim().toLowerCase();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--workspace-root')) {
      options.workspaceRoot = parseArgValue(argv, index, arg, '--workspace-root').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--config-path')) {
      options.configPath = parseArgValue(argv, index, arg, '--config-path').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--hub-url')) {
      options.hubUrl = parseArgValue(argv, index, arg, '--hub-url').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--mirror-dir')) {
      options.mirrorDir = parseArgValue(argv, index, arg, '--mirror-dir').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--state-file')) {
      options.stateFile = parseArgValue(argv, index, arg, '--state-file').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--idle-seconds')) {
      options.idleSeconds = parsePositiveInt(parseArgValue(argv, index, arg, '--idle-seconds'), '--idle-seconds');
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--reconnect-seconds')) {
      options.reconnectSeconds = parsePositiveInt(
        parseArgValue(argv, index, arg, '--reconnect-seconds'),
        '--reconnect-seconds',
      );
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--public-thread-limit')) {
      options.publicThreadLimit = parsePositiveInt(
        parseArgValue(argv, index, arg, '--public-thread-limit'),
        '--public-thread-limit',
      );
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }

    throw new Error(`unknown option: ${arg}`);
  }

  if (!VALID_MODES.has(options.mode)) {
    throw new Error('--mode must be one of: auto, hosted, local');
  }
  if (options.once && options.follow) {
    throw new Error('use either --once or --follow, not both');
  }
  if (!options.once && !options.follow) {
    options.once = true;
  }
  if (!options.stateFile && !options.mirrorDir && !options.workspaceRoot) {
    options.workspaceRoot = resolveWorkspaceRoot();
  }
  options.hubUrl = normalizeBaseUrl(options.hubUrl || DEFAULT_LOCAL_HUB_URL);
  return options;
}

function log(level, message, extra = null) {
  const prefix = `[${new Date().toISOString()}] [aqua-mirror-sync] [${level}]`;
  if (extra === null) {
    console.log(`${prefix} ${message}`);
    return;
  }
  console.log(`${prefix} ${message} ${JSON.stringify(extra)}`);
}

async function fileExists(filePath) {
  return pathExists(filePath);
}

async function resolveMode(options) {
  if (options.mode !== 'auto') {
    return options.mode;
  }

  const hostedConfigPath = resolveHostedConfigPath({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath || undefined,
  });
  return (await fileExists(hostedConfigPath)) ? 'hosted' : 'local';
}

function buildUnauthorizedStreamError(response, body) {
  const detail = body?.error?.message ?? `stream request failed with HTTP ${response.status}`;
  return new Error(detail);
}

async function createHostedTarget(options) {
  const loaded = await loadHostedConfig({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath || undefined,
  });

  return {
    mode: 'hosted',
    hubUrl: loaded.config.hubUrl,
    token: loaded.config.credential.token,
    viewerKind: 'gateway',
    workspaceRoot: loaded.workspaceRoot,
    configPath: loaded.configPath,
    async readContextBase() {
      const [health, aqua, gateway, environment, current] = await Promise.all([
        requestJson(loaded.config.hubUrl, '/health'),
        requestJson(loaded.config.hubUrl, '/api/v1/public/aqua'),
        requestJson(loaded.config.hubUrl, '/api/v1/gateways/me', { token: loaded.config.credential.token }),
        requestJson(loaded.config.hubUrl, '/api/v1/environment/current', { token: loaded.config.credential.token }),
        requestJson(loaded.config.hubUrl, '/api/v1/currents/current'),
      ]);

      let runtime;
      try {
        const runtimePayload = await requestJson(loaded.config.hubUrl, '/api/v1/runtime/remote/me', {
          token: loaded.config.credential.token,
        });
        runtime = {
          bound: true,
          ...runtimePayload.data,
        };
      } catch (error) {
        if (error && typeof error === 'object' && 'statusCode' in error && error.statusCode === 404) {
          runtime = {
            bound: false,
            reason: error.message,
          };
        } else {
          throw error;
        }
      }

      return {
        health: health?.data ?? null,
        aqua: aqua?.data?.aqua ?? null,
        gateway: gateway?.data?.gateway ?? null,
        environment: environment?.data?.environment ?? null,
        current: current?.data?.current ?? null,
        runtime,
      };
    },
    async fetchConversations() {
      return requestJson(loaded.config.hubUrl, '/api/v1/conversations', {
        token: loaded.config.credential.token,
      });
    },
    async fetchConversationThread(conversationId) {
      return requestJson(loaded.config.hubUrl, `/api/v1/conversations/${encodeURIComponent(conversationId)}/messages`, {
        token: loaded.config.credential.token,
      });
    },
    async fetchPublicThread(rootExpressionId) {
      const query = new URLSearchParams();
      query.set('rootExpressionId', rootExpressionId);
      return requestJson(loaded.config.hubUrl, `/api/v1/public-expressions?${query.toString()}`, {
        token: loaded.config.credential.token,
      });
    },
    async fetchRecentPublicExpressions(limit) {
      const query = new URLSearchParams();
      query.set('limit', String(limit));
      query.set('includeReplies', 'true');
      return requestJson(loaded.config.hubUrl, `/api/v1/public-expressions?${query.toString()}`, {
        token: loaded.config.credential.token,
      });
    },
    async fetchSeaFeedPage({ cursor = null, limit = DEFAULT_GAP_REPAIR_PAGE_LIMIT, scope = 'all' } = {}) {
      const query = new URLSearchParams();
      query.set('scope', scope);
      query.set('limit', String(limit));
      if (cursor) {
        query.set('cursor', cursor);
      }
      return requestJson(loaded.config.hubUrl, `/api/v1/sea/feed?${query.toString()}`, {
        token: loaded.config.credential.token,
      });
    },
  };
}

async function createLocalTarget(options) {
  const hubUrl = normalizeBaseUrl(options.hubUrl || DEFAULT_LOCAL_HUB_URL);
  const bootstrap = await requestJson(hubUrl, '/api/v1/session/bootstrap-local', {
    method: 'POST',
  });
  const token = bootstrap?.data?.credential?.token;
  if (!token) {
    throw new Error('bootstrap-local did not return a local session token');
  }

  return {
    mode: 'local',
    hubUrl,
    token,
    viewerKind: 'host',
    workspaceRoot: resolveWorkspaceRoot(options.workspaceRoot),
    async readContextBase() {
      const [health, session, aqua, environment, current] = await Promise.all([
        requestJson(hubUrl, '/health'),
        requestJson(hubUrl, '/api/v1/session/me', { token }),
        requestJson(hubUrl, '/api/v1/public/aqua'),
        requestJson(hubUrl, '/api/v1/environment/current', { token }),
        requestJson(hubUrl, '/api/v1/currents/current'),
      ]);

      let runtime;
      try {
        const runtimePayload = await requestJson(hubUrl, '/api/v1/runtime/local', { token });
        runtime = {
          bound: true,
          ...runtimePayload.data,
        };
      } catch (error) {
        if (error && typeof error === 'object' && 'statusCode' in error && error.statusCode === 404) {
          runtime = {
            bound: false,
            reason: error.message,
          };
        } else {
          throw error;
        }
      }

      return {
        health: health?.data ?? null,
        session: session?.data ?? bootstrap?.data ?? null,
        aqua: aqua?.data?.aqua ?? null,
        environment: environment?.data?.environment ?? null,
        current: current?.data?.current ?? null,
        runtime,
      };
    },
    async fetchSeaFeedPage({ cursor = null, limit = DEFAULT_GAP_REPAIR_PAGE_LIMIT, scope = 'all' } = {}) {
      const query = new URLSearchParams();
      query.set('scope', scope);
      query.set('limit', String(limit));
      if (cursor) {
        query.set('cursor', cursor);
      }
      return requestJson(hubUrl, `/api/v1/sea/feed?${query.toString()}`, { token });
    },
  };
}

async function createTarget(options) {
  const mode = await resolveMode(options);
  if (mode === 'hosted') {
    return createHostedTarget(options);
  }
  return createLocalTarget(options);
}

async function openSeaStream(target, lastEventId) {
  const headers = {
    accept: 'text/event-stream',
    authorization: `Bearer ${target.token}`,
  };
  if (lastEventId) {
    headers['last-event-id'] = lastEventId;
  }

  const response = await fetch(`${target.hubUrl}/api/v1/stream/sea`, {
    headers,
  });

  if (!response.ok) {
    const text = await response.text();
    let body = null;
    if (text) {
      try {
        body = JSON.parse(text);
      } catch {
        body = null;
      }
    }
    throw buildUnauthorizedStreamError(response, body);
  }

  if (!response.body) {
    throw new Error('stream response did not include a body');
  }

  return {
    response,
    reader: response.body.getReader(),
  };
}

export function selectGapRepairAnchor(state, viewerKind) {
  const explicit = state?.gapRepair?.lastVisibleFeedEventId;
  if (typeof explicit === 'string' && explicit.trim()) {
    return explicit.trim();
  }

  const deliveries = Array.isArray(state?.recentDeliveries) ? state.recentDeliveries : [];
  for (let index = deliveries.length - 1; index >= 0; index -= 1) {
    const seaEvent = deliveries[index]?.seaEvent;
    if (isSeaEventVisibleInFeedRepair(seaEvent, viewerKind) && typeof seaEvent?.id === 'string' && seaEvent.id.trim()) {
      return seaEvent.id.trim();
    }
  }

  return null;
}

function rememberGapRepairAnchor(state, viewerKind, seaEvent) {
  if (!isSeaEventVisibleInFeedRepair(seaEvent, viewerKind)) {
    return;
  }
  if (typeof seaEvent?.id === 'string' && seaEvent.id.trim()) {
    state.gapRepair.lastVisibleFeedEventId = seaEvent.id.trim();
  }
}

export function collectGapRepairPageItems(items, anchorSeaEventId, cutoffAt) {
  const collected = [];

  for (const item of Array.isArray(items) ? items : []) {
    if (typeof item?.createdAt === 'string' && cutoffAt && item.createdAt > cutoffAt) {
      continue;
    }
    if (anchorSeaEventId && item?.id === anchorSeaEventId) {
      return {
        anchorFound: true,
        collected,
      };
    }
    collected.push(item);
  }

  return {
    anchorFound: false,
    collected,
  };
}

async function persistContextSnapshot(target, paths, state) {
  const base = await target.readContextBase();
  const generatedAt = new Date().toISOString();

  let snapshot;
  if (target.mode === 'hosted') {
    snapshot = {
      version: 1,
      generatedAt,
      mode: target.mode,
      hub: {
        url: target.hubUrl,
        status: base.health?.status ?? 'unknown',
        deploymentMode: base.health?.deploymentMode ?? target.mode,
      },
      gateway: base.gateway,
      aqua: base.aqua,
      runtime: base.runtime,
      environment: base.environment,
      current: base.current,
      recentDeliveries: state.recentDeliveries,
    };

    state.viewer = {
      kind: 'gateway',
      id: base.gateway?.id ?? null,
      handle: base.gateway?.handle ?? null,
      displayName: base.gateway?.displayName ?? null,
    };
  } else {
    snapshot = {
      version: 1,
      generatedAt,
      mode: target.mode,
      hub: {
        url: target.hubUrl,
        status: base.health?.status ?? 'unknown',
        deploymentMode: base.health?.deploymentMode ?? target.mode,
      },
      owner: base.session,
      aqua: base.aqua,
      runtime: base.runtime,
      environment: base.environment,
      current: base.current,
      recentDeliveries: state.recentDeliveries,
    };

    state.viewer = {
      kind: 'host',
      id: base.session?.host?.id ?? null,
      handle: base.session?.host?.handle ?? null,
      displayName: base.session?.host?.displayName ?? null,
    };
  }

  await writeJsonFile(paths.contextPath, snapshot);
  state.mode = target.mode;
  state.hubUrl = target.hubUrl;
  state.mirror.lastContextSyncAt = generatedAt;
}

async function syncConversationIndex(target, paths, state) {
  if (target.viewerKind !== 'gateway') {
    return;
  }

  const payload = await target.fetchConversations();
  const generatedAt = new Date().toISOString();
  const items = payload?.data?.items ?? [];
  const record = {
    version: 1,
    generatedAt,
    hubUrl: target.hubUrl,
    mode: target.mode,
    items,
    nextCursor: payload?.data?.nextCursor ?? null,
  };

  await writeJsonFile(paths.conversationIndexPath, record);
  state.conversations.items = items.map((item) => ({
    id: item.id,
    updatedAt: item.updatedAt,
    peer: item.peer,
    readState: item.readState,
  }));
  state.mirror.lastConversationIndexSyncAt = generatedAt;
}

async function syncConversationThread(target, paths, state, conversationId) {
  if (target.viewerKind !== 'gateway') {
    return;
  }

  const payload = await target.fetchConversationThread(conversationId);
  const generatedAt = new Date().toISOString();
  const filePath = conversationThreadPath(paths, conversationId);
  const summary = state.conversations.items.find((item) => item.id === conversationId) ?? null;
  const messages = payload?.data?.items ?? [];
  const readState = payload?.data?.readState ?? null;

  await writeJsonFile(filePath, {
    version: 1,
    generatedAt,
    hubUrl: target.hubUrl,
    mode: target.mode,
    conversation: summary,
    items: messages,
    readState,
  });

  state.conversations.byId[conversationId] = {
    syncedAt: generatedAt,
    file: relativeMirrorPath(paths, filePath),
    messageCount: messages.length,
    lastMessageId: readState?.latestMessageId ?? messages.at(-1)?.id ?? null,
  };
  state.mirror.lastConversationThreadSyncAt = generatedAt;
}

async function syncPublicThread(target, paths, state, rootExpressionId) {
  if (target.viewerKind !== 'gateway') {
    return;
  }

  const payload = await target.fetchPublicThread(rootExpressionId);
  const generatedAt = new Date().toISOString();
  const items = payload?.data?.items ?? [];
  const filePath = publicThreadPath(paths, rootExpressionId);

  await writeJsonFile(filePath, {
    version: 1,
    generatedAt,
    hubUrl: target.hubUrl,
    mode: target.mode,
    rootExpressionId,
    items,
    nextCursor: payload?.data?.nextCursor ?? null,
  });

  state.publicThreads.byRootId[rootExpressionId] = {
    syncedAt: generatedAt,
    file: relativeMirrorPath(paths, filePath),
    expressionCount: items.length,
    lastExpressionId: items.at(-1)?.id ?? null,
  };
  state.mirror.lastPublicThreadSyncAt = generatedAt;
}

async function hydratePublicThreads(target, paths, state, limit) {
  if (target.viewerKind !== 'gateway') {
    return;
  }

  const payload = await target.fetchRecentPublicExpressions(limit);
  const items = payload?.data?.items ?? [];
  const rootIds = Array.from(
    new Set(
      items
        .map((item) => item.rootExpressionId ?? item.id ?? null)
        .filter((value) => typeof value === 'string' && value.trim()),
    ),
  );

  for (const rootExpressionId of rootIds) {
    await syncPublicThread(target, paths, state, rootExpressionId);
  }
}

export async function hydrateConversationThreads(target, paths, state, { skipIndexSync = false } = {}) {
  if (target.viewerKind !== 'gateway') {
    return;
  }

  if (!skipIndexSync) {
    await syncConversationIndex(target, paths, state);
  }
  for (const item of state.conversations.items) {
    await syncConversationThread(target, paths, state, item.id);
  }
}

async function withWarning(label, fn) {
  try {
    await fn();
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    log('warn', label, { error: message });
  }
}

async function mirrorDelivery(target, paths, state, delivery) {
  const recordedAt = new Date().toISOString();
  const storedRecord = buildStoredDeliveryRecord(delivery, recordedAt);
  const partition = datePartitionFromIso(delivery?.seaEvent?.createdAt ?? recordedAt);
  const seaLogPath = path.join(paths.seaEventsDir, `${partition}.ndjson`);

  await appendNdjson(seaLogPath, storedRecord);

  state.recentDeliveries = pushRecentDelivery(state.recentDeliveries, storedRecord);
  state.stream.lastDeliveryId = delivery?.id ?? state.stream.lastDeliveryId;
  state.stream.lastSeaEventId = delivery?.seaEvent?.id ?? state.stream.lastSeaEventId;
  state.stream.lastEventAt = recordedAt;
  rememberGapRepairAnchor(state, target.viewerKind, delivery?.seaEvent);

  const hints = extractDeliveryHints(delivery);

  if (hints.refreshContext) {
    await withWarning('context refresh failed after sea event', async () => {
      await persistContextSnapshot(target, paths, state);
    });
  }

  if (target.viewerKind !== 'gateway') {
    return;
  }

  if (hints.refreshConversationIndex || hints.conversationUpdates.length > 0) {
    await withWarning('conversation index sync failed', async () => {
      await syncConversationIndex(target, paths, state);
    });
  }

  for (const update of hints.conversationUpdates) {
    const stored = state.conversations.byId[update.conversationId];
    if (stored?.lastMessageId && update.messageId && stored.lastMessageId === update.messageId) {
      continue;
    }

    await withWarning(`conversation thread sync failed for ${update.conversationId}`, async () => {
      await syncConversationThread(target, paths, state, update.conversationId);
    });
  }

  for (const update of hints.publicThreadUpdates) {
    const stored = state.publicThreads.byRootId[update.rootExpressionId];
    if (stored?.lastExpressionId && update.expressionId && stored.lastExpressionId === update.expressionId) {
      continue;
    }

    await withWarning(`public thread sync failed for ${update.rootExpressionId}`, async () => {
      await syncPublicThread(target, paths, state, update.rootExpressionId);
    });
  }
}

async function appendRecoveredSeaEvent(paths, state, seaEvent) {
  const recordedAt = new Date().toISOString();
  const storedRecord = buildStoredSeaEventRecord(seaEvent, recordedAt);
  const partition = datePartitionFromIso(seaEvent?.createdAt ?? recordedAt);
  const seaLogPath = path.join(paths.seaEventsDir, `${partition}.ndjson`);

  await appendNdjson(seaLogPath, storedRecord);
  state.recentDeliveries = pushRecentDelivery(state.recentDeliveries, storedRecord);
}

async function repairVisibleSeaGap(target, paths, state, reason, cutoffAt) {
  const anchorSeaEventId = selectGapRepairAnchor(state, target.viewerKind);
  state.gapRepair.lastAttemptAt = new Date().toISOString();
  state.gapRepair.lastReason = reason ?? null;
  state.gapRepair.lastError = null;
  state.gapRepair.anchorSeaEventId = anchorSeaEventId;
  state.gapRepair.scannedPageCount = 0;
  state.gapRepair.recoveredEventCount = 0;
  state.gapRepair.newestRecoveredSeaEventId = null;
  state.gapRepair.oldestRecoveredSeaEventId = null;

  if (!anchorSeaEventId) {
    state.gapRepair.lastStatus = 'skipped_no_anchor';
    state.gapRepair.lastCompletedAt = new Date().toISOString();
    return {
      status: 'skipped_no_anchor',
      scannedPageCount: 0,
      recoveredEventCount: 0,
      anchorSeaEventId: null,
      conversationIds: [],
      publicThreadIds: [],
      refreshContext: false,
    };
  }

  let cursor = null;
  let anchorFound = false;
  let scannedPageCount = 0;
  const collectedNewestFirst = [];

  while (scannedPageCount < DEFAULT_GAP_REPAIR_MAX_PAGES) {
    const payload = await target.fetchSeaFeedPage({
      cursor,
      limit: DEFAULT_GAP_REPAIR_PAGE_LIMIT,
      scope: 'all',
    });
    scannedPageCount += 1;
    const items = payload?.data?.items ?? [];
    const page = collectGapRepairPageItems(items, anchorSeaEventId, cutoffAt);
    collectedNewestFirst.push(...page.collected);
    if (page.anchorFound) {
      anchorFound = true;
      break;
    }

    cursor = payload?.data?.nextCursor ?? null;
    if (!cursor || items.length === 0) {
      break;
    }
  }

  const dedupedNewestFirst = [];
  const seenSeaEventIds = new Set();
  for (const seaEvent of collectedNewestFirst) {
    if (!seaEvent?.id || seenSeaEventIds.has(seaEvent.id)) {
      continue;
    }
    seenSeaEventIds.add(seaEvent.id);
    dedupedNewestFirst.push(seaEvent);
  }
  const recoveredEvents = dedupedNewestFirst.reverse();
  const conversationIds = new Set();
  const publicThreadIds = new Set();
  let refreshContext = false;
  let refreshConversationIndex = false;

  for (const seaEvent of recoveredEvents) {
    await appendRecoveredSeaEvent(paths, state, seaEvent);
    rememberGapRepairAnchor(state, target.viewerKind, seaEvent);

    const hints = extractDeliveryHints({ seaEvent });
    refreshContext = refreshContext || hints.refreshContext;
    refreshConversationIndex = refreshConversationIndex || hints.refreshConversationIndex;
    for (const update of hints.conversationUpdates) {
      conversationIds.add(update.conversationId);
    }
    for (const update of hints.publicThreadUpdates) {
      publicThreadIds.add(update.rootExpressionId);
    }
  }

  state.gapRepair.scannedPageCount = scannedPageCount;
  state.gapRepair.recoveredEventCount = recoveredEvents.length;
  state.gapRepair.newestRecoveredSeaEventId = recoveredEvents.at(-1)?.id ?? null;
  state.gapRepair.oldestRecoveredSeaEventId = recoveredEvents[0]?.id ?? null;
  state.gapRepair.lastStatus = anchorFound
    ? recoveredEvents.length > 0
      ? 'recovered'
      : 'up_to_date'
    : recoveredEvents.length > 0
      ? 'bounded_recovery'
      : 'anchor_out_of_window';
  state.gapRepair.lastCompletedAt = new Date().toISOString();

  return {
    status: state.gapRepair.lastStatus,
    scannedPageCount,
    recoveredEventCount: recoveredEvents.length,
    anchorSeaEventId,
    newestRecoveredSeaEventId: state.gapRepair.newestRecoveredSeaEventId,
    oldestRecoveredSeaEventId: state.gapRepair.oldestRecoveredSeaEventId,
    conversationIds: Array.from(conversationIds),
    publicThreadIds: Array.from(publicThreadIds),
    refreshContext: refreshContext || recoveredEvents.length > 0,
    refreshConversationIndex,
  };
}

async function handleStreamFrame(target, paths, state, options, frame) {
  const now = new Date().toISOString();

  if (frame.event === 'hello') {
    state.stream.lastHelloAt = now;
    state.stream.lastError = null;
    const cursor = frame?.data?.cursor;
    if (!state.stream.lastDeliveryId && typeof cursor === 'string' && cursor.trim()) {
      state.stream.lastDeliveryId = cursor.trim();
    }
    await saveMirrorState(paths.statePath, state);
    log('info', 'stream connected', {
      mode: target.mode,
      viewer: frame?.data?.viewerGatewayId ?? state.viewer.id,
      replayedCount: frame?.data?.replayedCount ?? 0,
      cursor: frame?.data?.cursor ?? null,
    });
    return;
  }

  if (frame.event === 'ping') {
    return;
  }

  if (frame.event === 'resync_required') {
    state.stream.lastResyncRequiredAt = now;
    state.stream.lastRejectedCursor = frame?.data?.cursor ?? null;
    state.stream.lastDeliveryId = null;
    state.stream.resyncCount += 1;
    let gapRepairSummary = null;
    try {
      gapRepairSummary = await repairVisibleSeaGap(
        target,
        paths,
        state,
        frame?.data?.reason ?? 'resync_required',
        now,
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      state.gapRepair.lastError = {
        at: new Date().toISOString(),
        message,
      };
      state.gapRepair.lastStatus = 'failed';
      state.gapRepair.lastCompletedAt = new Date().toISOString();
      log('warn', 'bounded gap repair failed after resync_required', { error: message });
    }
    await withWarning('context refresh failed after resync_required', async () => {
      await persistContextSnapshot(target, paths, state);
    });
    if (target.viewerKind === 'gateway') {
      await withWarning('conversation index sync failed after resync_required', async () => {
        await syncConversationIndex(target, paths, state);
      });
      if (!options.hydrateConversations && gapRepairSummary?.conversationIds?.length) {
        for (const conversationId of gapRepairSummary.conversationIds) {
          await withWarning(`conversation thread sync failed after gap repair for ${conversationId}`, async () => {
            await syncConversationThread(target, paths, state, conversationId);
          });
        }
      }
      if (options.hydrateConversations) {
        await withWarning('conversation hydration failed after resync_required', async () => {
          await hydrateConversationThreads(target, paths, state, { skipIndexSync: true });
        });
      }
      if (!options.hydratePublicThreads && gapRepairSummary?.publicThreadIds?.length) {
        for (const rootExpressionId of gapRepairSummary.publicThreadIds) {
          await withWarning(`public-thread sync failed after gap repair for ${rootExpressionId}`, async () => {
            await syncPublicThread(target, paths, state, rootExpressionId);
          });
        }
      }
      if (options.hydratePublicThreads) {
        await withWarning('public-thread hydration failed after resync_required', async () => {
          await hydratePublicThreads(target, paths, state, options.publicThreadLimit);
        });
      }
    }
    await saveMirrorState(paths.statePath, state);
    log('warn', 'stream requested resync', {
      ...(frame.data ?? {}),
      gapRepair: gapRepairSummary,
    });
    return;
  }

  if (frame.event === 'sea.invalidate') {
    await mirrorDelivery(target, paths, state, frame.data);
    await saveMirrorState(paths.statePath, state);
    log('info', 'mirrored sea delivery', {
      deliveryId: frame.id ?? frame?.data?.id ?? null,
      type: frame?.data?.seaEvent?.type ?? 'unknown',
    });
  }
}

async function consumeStream(target, paths, state, options) {
  const stream = await openSeaStream(target, options.resetCursor ? null : state.stream.lastDeliveryId);
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const readPromise = stream.reader.read();
      const result = options.follow
        ? await readPromise
        : await Promise.race([
            readPromise,
            delay(options.idleSeconds * 1_000, { idle: true }),
          ]);

      if (result && typeof result === 'object' && 'idle' in result && result.idle === true) {
        await stream.reader.cancel('idle');
        log('info', 'stream idle timeout reached; stopping once run', {
          idleSeconds: options.idleSeconds,
        });
        return;
      }

      if (result.done) {
        throw new Error('sea stream closed');
      }

      buffer += decoder.decode(result.value, { stream: true });
      let separatorIndex = buffer.indexOf('\n\n');
      while (separatorIndex >= 0) {
        const block = buffer.slice(0, separatorIndex);
        buffer = buffer.slice(separatorIndex + 2);
        const frame = parseSseEventBlock(block);
        if (frame) {
          await handleStreamFrame(target, paths, state, options, frame);
        }
        separatorIndex = buffer.indexOf('\n\n');
      }
    }
  } finally {
    stream.reader.releaseLock();
  }
}

async function run(options) {
  const target = await createTarget(options);
  const paths = resolveMirrorPaths({
    workspaceRoot: target.workspaceRoot,
    mirrorDir: options.mirrorDir,
    stateFile: options.stateFile,
    mode: target.mode,
  });
  const state = await loadMirrorState(paths.statePath);
  if (state.version !== 1) {
    throw new Error('unsupported mirror state version');
  }
  if (options.resetCursor) {
    state.stream.lastDeliveryId = null;
  }

  log('info', 'starting mirror sync', {
    mode: target.mode,
    hubUrl: target.hubUrl,
    mirrorRoot: paths.mirrorRoot,
    viewerKind: target.viewerKind,
    follow: options.follow,
  });

  await persistContextSnapshot(target, paths, state);
  if (target.viewerKind === 'gateway') {
    await syncConversationIndex(target, paths, state);
    if (options.hydrateConversations) {
      await hydrateConversationThreads(target, paths, state, { skipIndexSync: true });
    }
    if (options.hydratePublicThreads) {
      await hydratePublicThreads(target, paths, state, options.publicThreadLimit);
    }
  } else if (options.hydrateConversations || options.hydratePublicThreads) {
    log('warn', 'conversation/public-thread hydration is only available for gateway-scoped mirrors');
  }

  await saveMirrorState(paths.statePath, state);

  if (!options.follow) {
    await consumeStream(target, paths, state, options);
    return {
      mode: target.mode,
      hubUrl: target.hubUrl,
      mirrorRoot: paths.mirrorRoot,
      lastDeliveryId: state.stream.lastDeliveryId,
      recentDeliveries: state.recentDeliveries.length,
      conversationThreads: Object.keys(state.conversations.byId).length,
      publicThreads: Object.keys(state.publicThreads.byRootId).length,
    };
  }

  while (true) {
    try {
      await consumeStream(target, paths, state, options);
      state.stream.reconnectCount += 1;
      await saveMirrorState(paths.statePath, state);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      state.stream.lastError = {
        at: new Date().toISOString(),
        message,
      };
      state.stream.reconnectCount += 1;
      await saveMirrorState(paths.statePath, state);
      log('warn', 'stream disconnected; reconnecting after delay', {
        error: message,
        reconnectSeconds: options.reconnectSeconds,
      });
      await delay(options.reconnectSeconds * 1_000);
    }
  }
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const summary = await run(options);
  if (summary) {
    log('info', 'mirror sync finished', summary);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    const message = error instanceof Error ? error.message : String(error);
    console.error(message);
    process.exit(1);
  });
}
