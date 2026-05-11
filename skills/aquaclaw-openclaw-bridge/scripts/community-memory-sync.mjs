#!/usr/bin/env node

import process from 'node:process';
import { pathToFileURL } from 'node:url';

import {
  DEFAULT_COMMUNITY_MEMORY_PAGE_SIZE,
  appendCommunityMemoryNotes,
  createDefaultCommunityMemoryState,
  loadCommunityMemoryIndex,
  loadCommunityMemoryState,
  mergeCommunityMemoryIndex,
  resolveCommunityMemoryPaths,
  saveCommunityMemoryIndex,
  saveCommunityMemoryState,
} from './community-memory-common.mjs';
import { loadHostedConfig, parseArgValue, parsePositiveInt, requestJson } from './hosted-aqua-common.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);

function printHelp() {
  console.log(`Usage: community-memory-sync.mjs [options]

Options:
  --workspace-root <path>        OpenClaw workspace root
  --config-path <path>           Hosted Aqua config path
  --community-memory-dir <path>  Local community-memory root override
  --page-size <n>                Remote page size (default: ${DEFAULT_COMMUNITY_MEMORY_PAGE_SIZE})
  --format <fmt>                 json|markdown (default: markdown)
  --help                         Show this message

Notes:
  - This command syncs hosted participant community-memory notes into a profile-scoped local store.
  - It mirrors raw notes under community-memory/notes/*.ndjson and keeps a rebuildable local index.json.
`);
}

export function parseOptions(argv) {
  const options = {
    communityMemoryDir: process.env.AQUACLAW_COMMUNITY_MEMORY_DIR || null,
    configPath: process.env.AQUACLAW_HOSTED_CONFIG || null,
    format: 'markdown',
    pageSize: Number.parseInt(process.env.AQUACLAW_COMMUNITY_MEMORY_PAGE_SIZE || String(DEFAULT_COMMUNITY_MEMORY_PAGE_SIZE), 10),
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT || null,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
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
    if (arg.startsWith('--community-memory-dir')) {
      options.communityMemoryDir = parseArgValue(argv, index, arg, '--community-memory-dir').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--page-size')) {
      options.pageSize = parsePositiveInt(parseArgValue(argv, index, arg, '--page-size'), '--page-size');
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--format')) {
      options.format = parseArgValue(argv, index, arg, '--format').trim().toLowerCase();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    throw new Error(`unknown option: ${arg}`);
  }

  if (!VALID_FORMATS.has(options.format)) {
    throw new Error('--format must be json or markdown');
  }

  options.pageSize = Math.min(Math.max(options.pageSize, 1), DEFAULT_COMMUNITY_MEMORY_PAGE_SIZE);
  return options;
}

function normalizeResponseItems(payload) {
  return Array.isArray(payload?.data?.items) ? payload.data.items : [];
}

function normalizeNextCursor(payload) {
  return typeof payload?.data?.nextCursor === 'string' && payload.data.nextCursor.trim()
    ? payload.data.nextCursor.trim()
    : null;
}

function buildCommunityMemoryMinePath({ pageSize, cursor = null } = {}) {
  const search = new URLSearchParams();
  search.set('limit', String(pageSize));
  if (cursor) {
    search.set('cursor', cursor);
  }
  return `/api/v1/community-memory/mine?${search.toString()}`;
}

function formatSyncResultMarkdown(result) {
  const lines = [
    'Community memory sync complete.',
    `- Root: ${result.paths.communityMemoryRoot}`,
    `- Profile: ${result.paths.profileId ?? 'legacy'}`,
    `- New notes: ${result.stats.newNotes}`,
    `- Known notes: ${result.stats.knownNotes}`,
    `- Total local notes: ${result.state.totalKnownNotes}`,
    `- Pages scanned: ${result.stats.pagesScanned}`,
    `- Full backfill complete: ${result.state.fullBackfillCompletedAt ? 'yes' : 'no'}`,
  ];

  if (result.stats.recoveredIndex || result.stats.recoveredState) {
    lines.push(
      `- Recovery: state=${result.stats.recoveredState ? result.stats.recoveredStateReason : 'no'}, index=${result.stats.recoveredIndex ? result.stats.recoveredIndexReason : 'no'}`,
    );
  }

  return lines.join('\n');
}

export async function syncCommunityMemory({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
  communityMemoryDir = process.env.AQUACLAW_COMMUNITY_MEMORY_DIR,
  pageSize = DEFAULT_COMMUNITY_MEMORY_PAGE_SIZE,
  requestJsonFn = requestJson,
  loadHostedConfigFn = loadHostedConfig,
} = {}) {
  const hosted = await loadHostedConfigFn({
    workspaceRoot,
    configPath,
  });
  const paths = resolveCommunityMemoryPaths({
    workspaceRoot: hosted.workspaceRoot,
    configPath: hosted.configPath,
    communityMemoryDir,
  });
  const stateResult = await loadCommunityMemoryState(paths.statePath);
  const indexResult = await loadCommunityMemoryIndex(paths);
  const state = stateResult.state;
  const index = indexResult.index;
  const knownIds = new Set(index.items.map((note) => note.id));
  const newNotes = [];
  let pagesScanned = 0;
  let fetchedItems = 0;
  let knownNotes = 0;
  let cursor = null;
  let reachedFeedEnd = false;
  const fullBackfillRequired = !state.fullBackfillCompletedAt;

  while (true) {
    const payload = await requestJsonFn(hosted.config.hubUrl, buildCommunityMemoryMinePath({ pageSize, cursor }), {
      token: hosted.config.credential.token,
    });
    const items = normalizeResponseItems(payload);
    const nextCursor = normalizeNextCursor(payload);
    pagesScanned += 1;
    fetchedItems += items.length;

    let pageNewCount = 0;
    for (const note of items) {
      if (typeof note?.id !== 'string' || !note.id.trim()) {
        continue;
      }
      if (knownIds.has(note.id)) {
        knownNotes += 1;
        continue;
      }
      knownIds.add(note.id);
      newNotes.push(note);
      pageNewCount += 1;
    }

    if (!nextCursor) {
      reachedFeedEnd = true;
      break;
    }
    if (!fullBackfillRequired && pageNewCount === 0) {
      break;
    }

    cursor = nextCursor;
  }

  if (newNotes.length > 0) {
    await appendCommunityMemoryNotes(paths, newNotes);
  }

  const nextIndex = mergeCommunityMemoryIndex(index, newNotes);
  await saveCommunityMemoryIndex(paths.indexPath, nextIndex);

  const syncedAt = new Date().toISOString();
  const nextState = {
    ...createDefaultCommunityMemoryState(),
    ...state,
    hubUrl: hosted.config.hubUrl,
    gatewayId: hosted.config?.gateway?.id ?? null,
    gatewayHandle: hosted.config?.gateway?.handle ?? null,
    lastSyncedAt: syncedAt,
    fullBackfillCompletedAt: state.fullBackfillCompletedAt ?? (reachedFeedEnd ? syncedAt : null),
    newestNoteId: nextIndex.items[0]?.id ?? null,
    oldestNoteId: nextIndex.items[nextIndex.items.length - 1]?.id ?? null,
    totalKnownNotes: nextIndex.items.length,
    lastError: null,
  };
  await saveCommunityMemoryState(paths.statePath, nextState);

  return {
    paths,
    state: nextState,
    index: nextIndex,
    stats: {
      fetchedItems,
      knownNotes,
      newNotes: newNotes.length,
      pagesScanned,
      reachedFeedEnd,
      recoveredIndex: indexResult.recovered,
      recoveredIndexReason: indexResult.recoveryReason,
      recoveredState: stateResult.recovered,
      recoveredStateReason: stateResult.recoveryReason,
    },
  };
}

async function main(argv = process.argv.slice(2)) {
  const options = parseOptions(argv);
  const result = await syncCommunityMemory(options);
  if (options.format === 'json') {
    console.log(JSON.stringify(result, null, 2));
    return;
  }
  console.log(formatSyncResultMarkdown(result));
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  });
}
