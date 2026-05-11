#!/usr/bin/env node

import { access, readFile } from 'node:fs/promises';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

import { buildMirrorMemoryBoundary, loadMirrorState, resolveMirrorPaths } from './aqua-mirror-common.mjs';
import {
  buildMirrorReadResult,
  DEFAULT_MIRROR_MAX_AGE_SECONDS,
  formatDurationSeconds,
  MIRROR_EXIT_CODE_MODE_MISMATCH,
  MIRROR_STREAM_FIELD_SEMANTICS,
} from './aqua-mirror-read.mjs';
import {
  formatTimestamp,
  parseArgValue,
  parsePositiveInt,
  resolveHostedConfigPath,
  resolveWorkspaceRoot,
} from './hosted-aqua-common.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);
const VALID_EXPECT_MODES = new Set(['any', 'auto', 'local', 'hosted']);
const SOURCE_LABELS = Object.freeze({
  freshMirror: 'mirror',
  liveFallback: 'live',
  staleMirrorFallback: 'stale-fallback',
});

function printHelp() {
  console.log(`Usage: aqua-mirror-status.mjs [options]

Options:
  --workspace-root <path>        OpenClaw workspace root
  --config-path <path>           Hosted Aqua config path, used when --expect-mode auto
  --mirror-dir <path>            Mirror root directory
  --state-file <path>            Mirror state file override
  --expect-mode <mode>           any|auto|hosted|local (default: any)
  --format <fmt>                 json|markdown (default: markdown)
  --max-age-seconds <n>          Freshness window for mirror status (default: ${DEFAULT_MIRROR_MAX_AGE_SECONDS})
  --help                         Show this message

Notes:
  - This command reads only local mirror files and local mirror state.
  - It does not open a new live Aqua connection.
  - It is meant to explain mirror freshness and source resolution labels.
`);
}

function parseOptions(argv) {
  const options = {
    configPath: process.env.AQUACLAW_HOSTED_CONFIG || null,
    expectMode: 'any',
    format: 'markdown',
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

async function loadJsonIfPresent(filePath) {
  if (!(await fileExists(filePath))) {
    return null;
  }

  const raw = await readFile(filePath, 'utf8');
  try {
    return JSON.parse(raw);
  } catch {
    throw new Error(`invalid JSON in mirror file at ${filePath}`);
  }
}

function buildSnapshotSummary(snapshot) {
  if (!snapshot || typeof snapshot !== 'object') {
    return {
      available: false,
      generatedAt: null,
      aquaDisplayName: null,
      currentLabel: null,
      waterTemperatureC: null,
      viewerDisplayName: null,
      viewerHandle: null,
    };
  }

  const gateway = snapshot.gateway && typeof snapshot.gateway === 'object' ? snapshot.gateway : {};
  const owner = snapshot.owner && typeof snapshot.owner === 'object' ? snapshot.owner : {};
  const viewer = snapshot.mode === 'hosted' ? gateway : owner;
  const current =
    snapshot.current && typeof snapshot.current === 'object' && snapshot.current.current
      ? snapshot.current.current
      : snapshot.current;

  return {
    available: true,
    generatedAt: snapshot.generatedAt ?? null,
    aquaDisplayName: snapshot?.aqua?.displayName ?? null,
    currentLabel: current?.label ?? null,
    waterTemperatureC: snapshot?.environment?.waterTemperatureC ?? null,
    viewerDisplayName: viewer?.displayName ?? null,
    viewerHandle: viewer?.handle ?? null,
  };
}

function buildStatusWarnings(readResult, statePresent, contextPresent) {
  const warnings = [...readResult.warnings];

  if (!statePresent) {
    warnings.unshift(`Mirror state file does not exist yet at ${readResult.mirror.statePath}.`);
  }
  if (!contextPresent) {
    warnings.unshift(`Mirror context snapshot does not exist yet at ${readResult.mirror.contextPath}.`);
  }

  return warnings;
}

function deriveStatus(readResult, statePresent, contextPresent) {
  if (!statePresent && !contextPresent && !readResult.freshness.referenceAt) {
    return 'bootstrap-pending';
  }
  return readResult.freshness.status;
}

function buildMirrorStatusResult({
  paths,
  snapshot,
  state,
  expectedMode,
  maxAgeSeconds,
  now,
  statePresent,
  contextPresent,
}) {
  const readResult = buildMirrorReadResult({
    paths,
    snapshot,
    state,
    expectedMode,
    maxAgeSeconds,
    now,
  });

  return {
    source: 'mirror-status',
    generatedAt: new Date().toISOString(),
    status: deriveStatus(readResult, statePresent, contextPresent),
    mode: readResult.mode,
    expectedMode,
    mirror: {
      ...readResult.mirror,
      statePresent,
      contextPresent,
    },
    freshness: readResult.freshness,
    stream: readResult.stream,
    sync: readResult.sync,
    gapRepair: readResult.gapRepair,
    memoryBoundary: buildMirrorMemoryBoundary(paths),
    snapshot: buildSnapshotSummary(snapshot),
    viewer: readResult.viewer,
    sourceLabels: SOURCE_LABELS,
    fieldSemantics: MIRROR_STREAM_FIELD_SEMANTICS,
    warnings: buildStatusWarnings(readResult, statePresent, contextPresent),
  };
}

function renderMirrorStatusMarkdown(result) {
  const cacheFiles = result.memoryBoundary.files.filter((entry) => entry.classification === 'cache');
  const memorySourceFiles = result.memoryBoundary.files.filter((entry) => entry.classification === 'memory-source');
  const sections = [
    '# Aqua Mirror Status',
    `- Generated at: ${formatTimestamp(result.generatedAt)}`,
    `- Status: ${result.status}`,
    `- Mode: ${result.mode ?? 'unknown'}`,
    `- Expected mode: ${result.expectedMode ?? 'n/a'}`,
    `- Mirror root: ${result.mirror.root}`,
    `- State file: ${result.mirror.statePath} (${result.mirror.statePresent ? 'present' : 'missing'})`,
    `- Context snapshot: ${result.mirror.contextPath} (${result.mirror.contextPresent ? 'present' : 'missing'})`,
    `- Freshness: ${result.freshness.status}`,
    `- Mirror age: ${formatDurationSeconds(result.freshness.ageSeconds)}`,
    `- Freshness window: ${formatDurationSeconds(result.freshness.maxAgeSeconds)}`,
    `- Freshness reference: ${result.freshness.referenceLabel ?? 'n/a'} @ ${formatTimestamp(result.freshness.referenceAt)}`,
    '',
    '## Source Labels',
    `- Fresh mirror read: ${result.sourceLabels.freshMirror}`,
    `- Live fallback: ${result.sourceLabels.liveFallback}`,
    `- Stale mirror fallback: ${result.sourceLabels.staleMirrorFallback}`,
    '',
    '## Stream',
    `- Last stream hello: ${formatTimestamp(result.stream.lastHelloAt)}`,
    `- Last sea delivery: ${formatTimestamp(result.stream.lastEventAt)}`,
    `- Last resync_required: ${formatTimestamp(result.stream.lastResyncRequiredAt)}`,
    `- Reconnect count: ${result.stream.reconnectCount ?? 0}`,
    `- Resync count: ${result.stream.resyncCount ?? 0}`,
    `- Last rejected cursor: ${result.stream.lastRejectedCursor ?? 'n/a'}`,
    `- Last stream error: ${
      result.stream.lastError?.message
        ? `${result.stream.lastError.message} @ ${formatTimestamp(result.stream.lastError.at)}`
        : 'none'
    }`,
    '',
    '## Sync',
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
    `- Gap repair error: ${
      result.gapRepair.lastError?.message
        ? `${result.gapRepair.lastError.message} @ ${formatTimestamp(result.gapRepair.lastError.at)}`
        : 'none'
    }`,
    '',
    '## Memory Boundary',
    `- Boundary version: ${result.memoryBoundary.version}`,
    `- Cache retention: ${result.memoryBoundary.retention.cache}`,
    `- Memory-source retention: ${result.memoryBoundary.retention['memory-source']}`,
    `- Compaction baseline: ${result.memoryBoundary.compaction.baseline}`,
    `- Redaction baseline: ${result.memoryBoundary.redaction.baseline}`,
    `- Persona boundary: ${result.memoryBoundary.redaction.personaBoundary}`,
    '',
    '### Cache Files',
    ...cacheFiles.map(
      (entry) =>
        `- ${entry.relativePathPattern}: ${entry.purpose} [retention=${entry.retentionPolicy}; rule=${entry.compactionRule}]`,
    ),
    '',
    '### Memory-Source Files',
    ...memorySourceFiles.map(
      (entry) =>
        `- ${entry.relativePathPattern}: ${entry.purpose} [retention=${entry.retentionPolicy}; rule=${entry.compactionRule}]`,
    ),
    '',
    '## Snapshot Summary',
    `- Snapshot available: ${result.snapshot.available ? 'yes' : 'no'}`,
    `- Aqua name: ${result.snapshot.aquaDisplayName ?? 'n/a'}`,
    `- Current label: ${result.snapshot.currentLabel ?? 'n/a'}`,
    `- Water temperature: ${result.snapshot.waterTemperatureC ?? 'n/a'}`,
    `- Viewer: ${result.snapshot.viewerDisplayName ?? 'n/a'}`,
    `- Viewer handle: ${result.snapshot.viewerHandle ? `@${result.snapshot.viewerHandle}` : 'n/a'}`,
    '',
    '## Field Semantics',
    `- lastHelloAt: ${result.fieldSemantics.lastHelloAt}`,
    `- lastEventAt: ${result.fieldSemantics.lastEventAt}`,
    `- lastError: ${result.fieldSemantics.lastError}`,
    `- lastResyncRequiredAt: ${result.fieldSemantics.lastResyncRequiredAt}`,
  ];

  if (result.warnings.length > 0) {
    sections.push('', '## Warnings', ...result.warnings.map((warning) => `- ${warning}`));
  }

  return sections.join('\n');
}

export async function runMirrorStatus(rawOptions) {
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
  const [statePresent, snapshot] = await Promise.all([
    fileExists(paths.statePath),
    loadJsonIfPresent(paths.contextPath),
  ]);
  const contextPresent = snapshot !== null;
  const state = await loadMirrorState(paths.statePath);
  const result = buildMirrorStatusResult({
    paths,
    snapshot,
    state,
    expectedMode,
    maxAgeSeconds: options.maxAgeSeconds,
    now: options.now,
    statePresent,
    contextPresent,
  });

  if (expectedMode && result.mode && result.mode !== expectedMode) {
    const mismatch = new Error(`mirror snapshot mode mismatch: expected ${expectedMode}, found ${result.mode}`);
    mismatch.exitCode = MIRROR_EXIT_CODE_MODE_MISMATCH;
    throw mismatch;
  }

  return result;
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const result = await runMirrorStatus(options);

  if (options.format === 'json') {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  console.log(renderMirrorStatusMarkdown(result));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(typeof error === 'object' && error && 'exitCode' in error ? error.exitCode : 1);
  }
}
