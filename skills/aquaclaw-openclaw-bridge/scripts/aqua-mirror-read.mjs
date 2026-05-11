#!/usr/bin/env node

import { access, readFile, readdir } from 'node:fs/promises';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

import { loadMirrorState, resolveMirrorPaths } from './aqua-mirror-common.mjs';
import {
  formatPublicExpressionSpeakerLabel,
  formatSeaEventSummaryLine,
  formatTimestamp,
  parseArgValue,
  parsePositiveInt,
  resolveHostedConfigPath,
  resolveWorkspaceRoot,
} from './hosted-aqua-common.mjs';

export const DEFAULT_MIRROR_MAX_AGE_SECONDS = 20 * 60;
export const MIRROR_EXIT_CODE_MISSING = 11;
export const MIRROR_EXIT_CODE_STALE = 12;
export const MIRROR_EXIT_CODE_MODE_MISMATCH = 13;

const VALID_FORMATS = new Set(['json', 'markdown']);
const VALID_EXPECT_MODES = new Set(['any', 'auto', 'local', 'hosted']);

export const MIRROR_STREAM_FIELD_SEMANTICS = Object.freeze({
  lastHelloAt:
    'Last time stream/sea sent a hello frame. This proves the mirror connected or reconnected, not that a new sea delivery arrived.',
  lastEventAt:
    'Last time this machine mirrored a visible sea delivery into local files. This is the strongest signal that new sea activity was actually recorded.',
  lastError:
    'Most recent stream/read failure seen by the follow loop. It may be transient if the mirror later reconnected successfully.',
  lastResyncRequiredAt:
    'Last time the stream reported that the stored cursor could not be replayed cleanly. The current bounded repair clears the stale cursor, backfills a limited visible feed window, and then refreshes snapshots, but it still does not reconstruct every missed historical delivery.',
});

function printHelp() {
  console.log(`Usage: aqua-mirror-read.mjs [options]

Options:
  --workspace-root <path>        OpenClaw workspace root
  --config-path <path>           Hosted Aqua config path, used when --expect-mode auto
  --mirror-dir <path>            Mirror root directory
  --state-file <path>            Mirror state file override
  --expect-mode <mode>           any|auto|hosted|local (default: any)
  --format <fmt>                 json|markdown (default: markdown)
  --max-age-seconds <n>          Freshness window for mirror reads (default: ${DEFAULT_MIRROR_MAX_AGE_SECONDS})
  --fresh-only                   Fail if the mirror is older than --max-age-seconds
  --help                         Show this message

Notes:
  - This command reads the local OpenClaw-owned mirror, not live Aqua APIs.
  - In --fresh-only mode, stale mirrors exit with code ${MIRROR_EXIT_CODE_STALE}.
  - Missing mirror snapshots exit with code ${MIRROR_EXIT_CODE_MISSING}.
`);
}

export function formatDurationSeconds(value) {
  if (!Number.isFinite(value) || value < 0) {
    return 'n/a';
  }

  const total = Math.floor(value);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const seconds = total % 60;
  const parts = [];

  if (hours > 0) {
    parts.push(`${hours}h`);
  }
  if (minutes > 0 || hours > 0) {
    parts.push(`${minutes}m`);
  }
  parts.push(`${seconds}s`);
  return parts.join(' ');
}

function formatLastError(lastError) {
  if (!lastError?.message) {
    return 'none';
  }
  return `${lastError.message} @ ${formatTimestamp(lastError.at)}`;
}

function parseOptions(argv) {
  const options = {
    configPath: process.env.AQUACLAW_HOSTED_CONFIG || null,
    expectMode: 'any',
    format: 'markdown',
    freshOnly: false,
    maxAgeSeconds: Number.parseInt(
      process.env.AQUACLAW_MIRROR_MAX_AGE_SECONDS || String(DEFAULT_MIRROR_MAX_AGE_SECONDS),
      10,
    ),
    mirrorDir: process.env.AQUACLAW_MIRROR_DIR || null,
    stateFile: process.env.AQUACLAW_MIRROR_STATE_FILE || null,
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT || null,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--fresh-only') {
      options.freshOnly = true;
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
    if (arg.startsWith('--expect-mode')) {
      options.expectMode = parseArgValue(argv, index, arg, '--expect-mode').trim().toLowerCase();
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
    if (arg.startsWith('--max-age-seconds')) {
      options.maxAgeSeconds = parsePositiveInt(
        parseArgValue(argv, index, arg, '--max-age-seconds'),
        '--max-age-seconds',
      );
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }

    throw new Error(`unknown option: ${arg}`);
  }

  if (!VALID_FORMATS.has(options.format)) {
    throw new Error('format must be json or markdown');
  }
  if (!VALID_EXPECT_MODES.has(options.expectMode)) {
    throw new Error('expect-mode must be one of: any, auto, local, hosted');
  }
  if (!Number.isFinite(options.maxAgeSeconds) || options.maxAgeSeconds < 1) {
    throw new Error('--max-age-seconds must be a positive integer');
  }

  return options;
}

async function fileExists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function readJsonIfPresent(filePath) {
  try {
    return JSON.parse(await readFile(filePath, 'utf8'));
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return null;
    }
    throw error;
  }
}

async function fileNamesIfPresent(dirPath) {
  try {
    return await readdir(dirPath);
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return [];
    }
    throw error;
  }
}

async function loadPublicExpressionSpeakerIndex(paths) {
  const index = new Map();
  const fileNames = (await fileNamesIfPresent(paths.publicThreadsDir))
    .filter((fileName) => fileName.endsWith('.json'))
    .sort();

  for (const fileName of fileNames) {
    const payload = await readJsonIfPresent(`${paths.publicThreadsDir}/${fileName}`);
    const items = Array.isArray(payload?.items) ? payload.items : [];
    for (const item of items) {
      if (typeof item?.id === 'string' && item.id.trim()) {
        index.set(item.id.trim(), formatPublicExpressionSpeakerLabel(item));
      }
    }
  }

  return index;
}

async function resolveExpectedMode(options) {
  if (options.expectMode === 'any') {
    return null;
  }
  if (options.expectMode === 'local' || options.expectMode === 'hosted') {
    return options.expectMode;
  }

  const hostedConfigPath = resolveHostedConfigPath({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath || undefined,
  });
  return (await fileExists(hostedConfigPath)) ? 'hosted' : 'local';
}

function parseIsoTimestamp(value) {
  if (typeof value !== 'string' || !value.trim()) {
    return null;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  return parsed;
}

export function pickMirrorReferenceTimestamp(snapshot, state) {
  const candidate = pickMirrorReferenceCandidate(snapshot, state);
  return candidate?.at ?? null;
}

export function pickMirrorReferenceCandidate(snapshot, state) {
  const candidates = [
    {
      kind: 'context_generated',
      label: 'context.generatedAt',
      raw: snapshot?.generatedAt,
    },
    {
      kind: 'context_sync',
      label: 'mirror.lastContextSyncAt',
      raw: state?.mirror?.lastContextSyncAt,
    },
    {
      kind: 'sea_delivery',
      label: 'stream.lastEventAt',
      raw: state?.stream?.lastEventAt,
    },
    {
      kind: 'stream_hello',
      label: 'stream.lastHelloAt',
      raw: state?.stream?.lastHelloAt,
    },
    {
      kind: 'state_updated',
      label: 'state.updatedAt',
      raw: state?.updatedAt,
    },
  ]
    .map((value) => ({
      ...value,
      parsed: parseIsoTimestamp(value.raw),
    }))
    .filter((candidate) => candidate.parsed !== null)
    .sort((left, right) => left.parsed.getTime() - right.parsed.getTime());

  if (!candidates.length) {
    return null;
  }

  const selected = candidates.at(-1);
  return {
    kind: selected.kind,
    label: selected.label,
    raw: selected.raw,
    at: selected.parsed.toISOString(),
  };
}

function renderCollectionMarkdown(title, items, formatter) {
  if (!items?.length) {
    return [title, '- None'].join('\n');
  }

  return [title, ...items.map(formatter)].join('\n');
}

function normalizeCurrent(current) {
  if (!current || typeof current !== 'object') {
    return null;
  }
  if (current.current && typeof current.current === 'object') {
    return current.current;
  }
  return current;
}

function preferNonEmpty(...values) {
  for (const value of values) {
    if (typeof value === 'string' && value.trim()) {
      return value;
    }
    if (value !== null && value !== undefined && typeof value !== 'string') {
      return value;
    }
  }
  return null;
}

function resolveViewer(snapshot, state) {
  if (snapshot?.mode === 'hosted') {
    const gateway = snapshot.gateway && typeof snapshot.gateway === 'object' ? snapshot.gateway : {};
    const viewer = state?.viewer && typeof state.viewer === 'object' ? state.viewer : {};
    return {
      kind: 'gateway',
      id: preferNonEmpty(gateway.id, viewer.id),
      handle: preferNonEmpty(gateway.handle, viewer.handle),
      displayName: preferNonEmpty(gateway.displayName, viewer.displayName),
    };
  }

  const owner =
    snapshot?.owner?.host ??
    snapshot?.owner?.owner ??
    snapshot?.owner?.user ??
    (snapshot?.owner && typeof snapshot.owner === 'object' ? snapshot.owner : {});
  const viewer = state?.viewer && typeof state.viewer === 'object' ? state.viewer : {};

  return {
    kind: 'host',
    id: preferNonEmpty(owner?.id, viewer.id),
    handle: preferNonEmpty(owner?.handle, viewer.handle),
    displayName: preferNonEmpty(owner?.displayName, viewer.displayName),
  };
}

function buildWarnings(snapshot, state, freshness) {
  const warnings = [];
  if (freshness.status !== 'fresh') {
    if (freshness.referenceAt) {
      warnings.push(
        `Mirror freshness is stale: last usable sync signal was ${formatTimestamp(freshness.referenceAt)} (${formatDurationSeconds(freshness.ageSeconds)} old).`,
      );
    } else {
      warnings.push(
        'Mirror has no usable sync signal yet. Run aqua-mirror-sync.sh --once or start the mirror follow service first.',
      );
    }
  }

  if (state?.stream?.lastError?.message) {
    warnings.push(
      `Last mirror stream error at ${formatTimestamp(state.stream.lastError.at)}: ${state.stream.lastError.message}`,
    );
  }

  if (state?.stream?.lastResyncRequiredAt) {
    warnings.push(
      `Mirror stream requested resync at ${formatTimestamp(state.stream.lastResyncRequiredAt)}. The current bounded repair does not reconstruct every missed historical sea delivery.`,
    );
  }

  if (state?.gapRepair?.lastStatus === 'bounded_recovery') {
    warnings.push(
      `Last bounded gap repair recovered only the newest visible slice and did not reach anchor ${state.gapRepair.anchorSeaEventId ?? 'n/a'}. Older missing events may still exist.`,
    );
  }
  if (state?.gapRepair?.lastStatus === 'anchor_out_of_window') {
    warnings.push(
      `Last bounded gap repair could not reach anchor ${state.gapRepair.anchorSeaEventId ?? 'n/a'} inside the configured feed scan window.`,
    );
  }
  if (state?.gapRepair?.lastStatus === 'failed' && state?.gapRepair?.lastError?.message) {
    warnings.push(
      `Last bounded gap repair failed at ${formatTimestamp(state.gapRepair.lastError.at)}: ${state.gapRepair.lastError.message}`,
    );
  }

  const runtime = snapshot?.runtime;
  const runtimeRecord = runtime?.runtime ?? runtime;
  if (runtime?.bound && runtimeRecord?.status && runtimeRecord.status !== 'online') {
    warnings.push(
      'The mirrored runtime is bound but not currently marked online. Do not describe this as the Claw definitely being in the sea right now.',
    );
  }

  return warnings;
}

export function buildMirrorReadResult({
  paths,
  snapshot,
  state,
  expectedMode = null,
  maxAgeSeconds = DEFAULT_MIRROR_MAX_AGE_SECONDS,
  now = new Date(),
}) {
  const reference = pickMirrorReferenceCandidate(snapshot, state);
  const referenceAt = reference?.at ?? null;
  const referenceDate = parseIsoTimestamp(referenceAt);
  const nowDate = now instanceof Date ? now : new Date(now);
  const ageSeconds =
    referenceDate === null ? null : Math.max(0, Math.floor((nowDate.getTime() - referenceDate.getTime()) / 1000));
  const stream = {
    lastDeliveryId: state?.stream?.lastDeliveryId ?? null,
    lastSeaEventId: state?.stream?.lastSeaEventId ?? null,
    lastHelloAt: state?.stream?.lastHelloAt ?? null,
    lastEventAt: state?.stream?.lastEventAt ?? null,
    lastResyncRequiredAt: state?.stream?.lastResyncRequiredAt ?? null,
    lastRejectedCursor: state?.stream?.lastRejectedCursor ?? null,
    reconnectCount: state?.stream?.reconnectCount ?? 0,
    resyncCount: state?.stream?.resyncCount ?? 0,
    lastError: state?.stream?.lastError ?? null,
  };
  const sync = {
    lastContextSyncAt: state?.mirror?.lastContextSyncAt ?? snapshot?.generatedAt ?? null,
    lastConversationIndexSyncAt: state?.mirror?.lastConversationIndexSyncAt ?? null,
    lastConversationThreadSyncAt: state?.mirror?.lastConversationThreadSyncAt ?? null,
    lastPublicThreadSyncAt: state?.mirror?.lastPublicThreadSyncAt ?? null,
    stateUpdatedAt: state?.updatedAt ?? null,
  };
  const gapRepair = {
    lastVisibleFeedEventId: state?.gapRepair?.lastVisibleFeedEventId ?? null,
    lastAttemptAt: state?.gapRepair?.lastAttemptAt ?? null,
    lastCompletedAt: state?.gapRepair?.lastCompletedAt ?? null,
    lastStatus: state?.gapRepair?.lastStatus ?? null,
    lastReason: state?.gapRepair?.lastReason ?? null,
    lastError: state?.gapRepair?.lastError ?? null,
    scannedPageCount: state?.gapRepair?.scannedPageCount ?? 0,
    recoveredEventCount: state?.gapRepair?.recoveredEventCount ?? 0,
    anchorSeaEventId: state?.gapRepair?.anchorSeaEventId ?? null,
    newestRecoveredSeaEventId: state?.gapRepair?.newestRecoveredSeaEventId ?? null,
    oldestRecoveredSeaEventId: state?.gapRepair?.oldestRecoveredSeaEventId ?? null,
  };
  const freshness = {
    status: ageSeconds !== null && ageSeconds <= maxAgeSeconds ? 'fresh' : 'stale',
    maxAgeSeconds,
    ageSeconds,
    referenceAt,
    referenceKind: reference?.kind ?? null,
    referenceLabel: reference?.label ?? null,
    snapshotAvailable: snapshot !== null,
    lastContextSyncAt: sync.lastContextSyncAt,
    lastSeaDeliveryAt: stream.lastEventAt,
    lastHelloAt: stream.lastHelloAt,
    stateUpdatedAt: sync.stateUpdatedAt,
  };
  const viewer = resolveViewer(snapshot, state);
  const warnings = buildWarnings(snapshot, state, freshness);

  return {
    source: 'mirror',
    mode: snapshot?.mode ?? state?.mode ?? null,
    expectedMode,
    mirror: {
      root: paths.mirrorRoot,
      statePath: paths.statePath,
      contextPath: paths.contextPath,
    },
    freshness,
    stream,
    sync,
    gapRepair,
    fieldSemantics: MIRROR_STREAM_FIELD_SEMANTICS,
    viewer,
    snapshot,
    warnings,
  };
}

function formatRecentDelivery(item, index, publicExpressionSpeakerIndex = new Map()) {
  const event = item?.seaEvent ?? {};
  const expressionId =
    typeof event?.metadata?.expressionId === 'string' && event.metadata.expressionId.trim()
      ? event.metadata.expressionId.trim()
      : null;
  const speakerTrail = expressionId ? publicExpressionSpeakerIndex.get(expressionId) ?? null : null;
  return `${index + 1}. [${formatTimestamp(event.createdAt ?? item?.recordedAt)}] ${formatSeaEventSummaryLine({
    ...event,
    speakerTrail,
  })}`;
}

export function renderMirrorMarkdown(result) {
  const snapshot = result.snapshot ?? {};
  const current = normalizeCurrent(snapshot.current);
  const runtime = snapshot.runtime ?? {};
  const runtimeRecord = runtime?.runtime ?? runtime;
  const viewerLabel = result.mode === 'hosted' ? 'Gateway' : 'Host';
  const viewerIdLabel = result.mode === 'hosted' ? 'Gateway id' : 'Host id';
  const sections = [
    '# Aqua Context',
    `- Generated at: ${formatTimestamp(snapshot.generatedAt)}`,
    `- Mode: ${result.mode ?? 'unknown'}`,
    '- Source: mirror',
    `- Mirror freshness: ${result.freshness.status}`,
    `- Mirror age: ${formatDurationSeconds(result.freshness.ageSeconds)}`,
    `- Freshness window: ${formatDurationSeconds(result.freshness.maxAgeSeconds)}`,
    `- Mirror reference time: ${formatTimestamp(result.freshness.referenceAt)}`,
    `- Mirror reference signal: ${result.freshness.referenceLabel ?? 'n/a'}`,
    `- Mirror snapshot available: ${result.freshness.snapshotAvailable ? 'yes' : 'no'}`,
    `- Last context sync: ${formatTimestamp(result.freshness.lastContextSyncAt)}`,
    `- Last sea delivery: ${formatTimestamp(result.freshness.lastSeaDeliveryAt)}`,
    `- Last stream hello: ${formatTimestamp(result.freshness.lastHelloAt)}`,
    `- Mirror state updated: ${formatTimestamp(result.freshness.stateUpdatedAt)}`,
    `- Mirror root: ${result.mirror.root}`,
  ];

  if (result.expectedMode) {
    sections.push(`- Expected mode: ${result.expectedMode}`);
  }

  sections.push(
    '',
    '## Mirror Stream',
    `- Last stream hello: ${formatTimestamp(result.stream.lastHelloAt)}`,
    `- Last sea delivery: ${formatTimestamp(result.stream.lastEventAt)}`,
    `- Last resync_required: ${formatTimestamp(result.stream.lastResyncRequiredAt)}`,
    `- Reconnect count: ${result.stream.reconnectCount ?? 0}`,
    `- Resync count: ${result.stream.resyncCount ?? 0}`,
    `- Last rejected cursor: ${result.stream.lastRejectedCursor ?? 'n/a'}`,
    `- Last stream error: ${formatLastError(result.stream.lastError)}`,
    '',
    '## Mirror Sync',
    `- Last context sync: ${formatTimestamp(result.sync.lastContextSyncAt)}`,
    `- Last conversation index sync: ${formatTimestamp(result.sync.lastConversationIndexSyncAt)}`,
    `- Last conversation thread sync: ${formatTimestamp(result.sync.lastConversationThreadSyncAt)}`,
    `- Last public thread sync: ${formatTimestamp(result.sync.lastPublicThreadSyncAt)}`,
    `- Mirror state updated: ${formatTimestamp(result.sync.stateUpdatedAt)}`,
    '',
    '## Gap Repair',
    `- Last status: ${result.gapRepair.lastStatus ?? 'n/a'}`,
    `- Last reason: ${result.gapRepair.lastReason ?? 'n/a'}`,
    `- Last attempt: ${formatTimestamp(result.gapRepair.lastAttemptAt)}`,
    `- Last completed: ${formatTimestamp(result.gapRepair.lastCompletedAt)}`,
    `- Feed anchor: ${result.gapRepair.anchorSeaEventId ?? 'n/a'}`,
    `- Last visible feed event: ${result.gapRepair.lastVisibleFeedEventId ?? 'n/a'}`,
    `- Scanned pages: ${result.gapRepair.scannedPageCount ?? 0}`,
    `- Recovered events: ${result.gapRepair.recoveredEventCount ?? 0}`,
    `- Newest recovered event: ${result.gapRepair.newestRecoveredSeaEventId ?? 'n/a'}`,
    `- Oldest recovered event: ${result.gapRepair.oldestRecoveredSeaEventId ?? 'n/a'}`,
    `- Gap repair error: ${formatLastError(result.gapRepair.lastError)}`,
    '',
    '## Aqua',
    `- Name: ${snapshot?.aqua?.displayName ?? 'n/a'}`,
    `- Updated at: ${formatTimestamp(snapshot?.aqua?.updatedAt)}`,
    '',
    `## ${viewerLabel}`,
    `- Display name: ${result.viewer?.displayName ?? 'n/a'}`,
    `- Handle: ${result.viewer?.handle ? `@${result.viewer.handle}` : 'n/a'}`,
    `- ${viewerIdLabel}: ${result.viewer?.id ?? 'n/a'}`,
    '',
    runtime?.bound
      ? [
          '## Runtime',
          '- Runtime binding: yes',
          `- Runtime: ${runtimeRecord?.runtimeId ?? runtimeRecord?.id ?? 'n/a'}`,
          `- Installation: ${runtimeRecord?.installationId ?? 'n/a'}`,
          `- Status: ${runtimeRecord?.status ?? 'unknown'}`,
          `- Last heartbeat: ${formatTimestamp(runtimeRecord?.lastHeartbeatAt)}`,
          `- Presence: ${runtime?.presence?.status ?? 'unknown'}`,
        ].join('\n')
      : ['## Runtime', '- Runtime binding: no', `- Reason: ${runtime?.reason ?? 'not bound'}`].join('\n'),
    '',
    '## Environment',
    `- Water temperature: ${snapshot?.environment?.waterTemperatureC ?? 'n/a'}C`,
    `- Clarity: ${snapshot?.environment?.clarity ?? 'n/a'}`,
    `- Tide: ${snapshot?.environment?.tideDirection ?? 'n/a'}`,
    `- Surface: ${snapshot?.environment?.surfaceState ?? 'n/a'}`,
    `- Phenomenon: ${snapshot?.environment?.phenomenon ?? 'n/a'}`,
    `- Source: ${snapshot?.environment?.source ?? 'n/a'}`,
    `- Updated at: ${formatTimestamp(snapshot?.environment?.updatedAt)}`,
    `- Summary: ${snapshot?.environment?.summary ?? 'n/a'}`,
    '',
    '## Current',
    `- Label: ${current?.label ?? 'n/a'}`,
    `- Tone: ${current?.tone ?? 'n/a'}`,
    `- Source: ${current?.source ?? 'n/a'}`,
    `- Window: ${formatTimestamp(current?.startsAt)} -> ${formatTimestamp(current?.endsAt)}`,
    `- Summary: ${current?.summary ?? 'n/a'}`,
    '',
    renderCollectionMarkdown(
      '## Recent Mirrored Deliveries',
      Array.isArray(snapshot?.recentDeliveries) ? snapshot.recentDeliveries : [],
      (item, index) => formatRecentDelivery(item, index, result.publicExpressionSpeakerIndex),
    ),
  );

  if (result.warnings.length > 0) {
    sections.push('', '## Warnings', ...result.warnings.map((warning) => `- ${warning}`));
  }

  return sections.join('\n');
}

async function loadMirrorContextSnapshot(contextPath) {
  let raw;
  try {
    raw = await readFile(contextPath, 'utf8');
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      const missing = new Error(`mirror context snapshot not found at ${contextPath}`);
      missing.exitCode = MIRROR_EXIT_CODE_MISSING;
      throw missing;
    }
    throw error;
  }

  try {
    return JSON.parse(raw);
  } catch {
    throw new Error(`invalid JSON in mirror context snapshot at ${contextPath}`);
  }
}

export async function runMirrorRead(rawOptions) {
  const options = {
    ...rawOptions,
    workspaceRoot: resolveWorkspaceRoot(rawOptions.workspaceRoot),
  };
  const expectedMode = await resolveExpectedMode(options);
  const paths = resolveMirrorPaths({
    workspaceRoot: options.workspaceRoot,
    mirrorDir: options.mirrorDir,
    stateFile: options.stateFile,
    mode: expectedMode ?? 'auto',
  });
  const state = await loadMirrorState(paths.statePath);
  const snapshot = await loadMirrorContextSnapshot(paths.contextPath);
  const result = buildMirrorReadResult({
    paths,
    snapshot,
    state,
    expectedMode,
    maxAgeSeconds: options.maxAgeSeconds,
  });
  result.publicExpressionSpeakerIndex = await loadPublicExpressionSpeakerIndex(paths);

  if (expectedMode && result.mode && result.mode !== expectedMode) {
    const mismatch = new Error(`mirror snapshot mode mismatch: expected ${expectedMode}, found ${result.mode}`);
    mismatch.exitCode = MIRROR_EXIT_CODE_MODE_MISMATCH;
    throw mismatch;
  }

  if (options.freshOnly && result.freshness.status !== 'fresh') {
    const stale = new Error(
      `mirror snapshot is stale: last usable sync signal was ${formatTimestamp(result.freshness.referenceAt)} (${formatDurationSeconds(result.freshness.ageSeconds)} old, freshness window ${formatDurationSeconds(result.freshness.maxAgeSeconds)})`,
    );
    stale.exitCode = MIRROR_EXIT_CODE_STALE;
    throw stale;
  }

  return result;
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const result = await runMirrorRead(options);

  if (options.format === 'json') {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  console.log(renderMirrorMarkdown(result));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(typeof error === 'object' && error && 'exitCode' in error ? error.exitCode : 1);
  }
}
