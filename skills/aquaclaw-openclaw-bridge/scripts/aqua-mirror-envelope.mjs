#!/usr/bin/env node

import { access, readdir, stat } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

import {
  buildMirrorMemoryBoundary,
  classifyMirrorRelativePath,
  loadMirrorState,
  matchMirrorFilePolicy,
  relativeMirrorPath,
  resolveMirrorPaths,
} from './aqua-mirror-common.mjs';
import { DEFAULT_MIRROR_MAX_AGE_SECONDS, formatDurationSeconds } from './aqua-mirror-read.mjs';
import { runMirrorStatus } from './aqua-mirror-status.mjs';
import {
  formatTimestamp,
  parseArgValue,
  parsePositiveInt,
  resolveHostedConfigPath,
  resolveWorkspaceRoot,
} from './hosted-aqua-common.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);
const VALID_MODES = new Set(['auto', 'hosted', 'local']);
const DEFAULT_PUBLIC_THREAD_LIMIT = 20;
const DEFAULT_GAP_REPAIR_PAGE_LIMIT = 50;
const DEFAULT_GAP_REPAIR_MAX_PAGES = 3;
const DEFAULT_RECONNECT_SECONDS = 5;
const DEFAULT_STDOUT_LOG = path.join(os.homedir(), '.openclaw', 'logs', 'aquaclaw-mirror-sync.log');
const DEFAULT_STDERR_LOG = path.join(os.homedir(), '.openclaw', 'logs', 'aquaclaw-mirror-sync.err.log');

function readEnvFlag(name, fallback = false) {
  const raw = process.env[name];
  if (typeof raw !== 'string' || !raw.trim()) {
    return fallback;
  }

  switch (raw.trim().toLowerCase()) {
    case '1':
    case 'true':
    case 'yes':
    case 'on':
      return true;
    case '0':
    case 'false':
    case 'no':
    case 'off':
      return false;
    default:
      throw new Error(`invalid boolean value in ${name}: ${raw}`);
  }
}

function printHelp() {
  console.log(`Usage: aqua-mirror-envelope.mjs [options]

Options:
  --workspace-root <path>        OpenClaw workspace root
  --config-path <path>           Hosted Aqua config path, used when --mode auto
  --mirror-dir <path>            Mirror root directory
  --state-file <path>            Mirror state file override
  --mode <mode>                  auto|hosted|local (default: auto)
  --format <fmt>                 json|markdown (default: markdown)
  --max-age-seconds <n>          Freshness window to evaluate mirror health (default: ${DEFAULT_MIRROR_MAX_AGE_SECONDS})
  --reconnect-seconds <n>        Reconnect delay used by the follow service (default: ${DEFAULT_RECONNECT_SECONDS})
  --public-thread-limit <n>      Recent public-expression list size for hydration (default: ${DEFAULT_PUBLIC_THREAD_LIMIT})
  --hydrate-conversations        Model the pressure envelope with full DM hydration enabled
  --hydrate-public-threads       Model the pressure envelope with public-thread hydration enabled
  --stdout-log <path>            Mirror follow stdout log path
  --stderr-log <path>            Mirror follow stderr log path
  --help                         Show this message

What this command reports:
  - current mirror freshness/recovery status
  - startup, steady-state, and resync request budget for the selected profile
  - actual local mirror footprint by cache vs memory-source files
  - service-log footprint plus the current no-built-in-rotation boundary
`);
}

function parseOptions(argv) {
  const options = {
    configPath: process.env.AQUACLAW_HOSTED_CONFIG || null,
    format: 'markdown',
    hydrateConversations: readEnvFlag('AQUACLAW_MIRROR_HYDRATE_CONVERSATIONS', false),
    hydratePublicThreads: readEnvFlag('AQUACLAW_MIRROR_HYDRATE_PUBLIC_THREADS', false),
    maxAgeSeconds: Number.parseInt(
      process.env.AQUACLAW_MIRROR_MAX_AGE_SECONDS || String(DEFAULT_MIRROR_MAX_AGE_SECONDS),
      10,
    ),
    mirrorDir: process.env.AQUACLAW_MIRROR_DIR || null,
    mode: process.env.AQUACLAW_MIRROR_MODE || 'auto',
    publicThreadLimit: Number.parseInt(
      process.env.AQUACLAW_MIRROR_PUBLIC_THREAD_LIMIT || String(DEFAULT_PUBLIC_THREAD_LIMIT),
      10,
    ),
    reconnectSeconds: Number.parseInt(
      process.env.AQUACLAW_MIRROR_RECONNECT_SECONDS || String(DEFAULT_RECONNECT_SECONDS),
      10,
    ),
    stateFile: process.env.AQUACLAW_MIRROR_STATE_FILE || null,
    stderrLog: process.env.AQUACLAW_MIRROR_STDERR_LOG || DEFAULT_STDERR_LOG,
    stdoutLog: process.env.AQUACLAW_MIRROR_STDOUT_LOG || DEFAULT_STDOUT_LOG,
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT || null,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--hydrate-conversations') {
      options.hydrateConversations = true;
      continue;
    }
    if (arg === '--hydrate-public-threads') {
      options.hydratePublicThreads = true;
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
    if (arg.startsWith('--mode')) {
      options.mode = parseArgValue(argv, index, arg, '--mode').trim().toLowerCase();
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
    if (arg.startsWith('--stdout-log')) {
      options.stdoutLog = parseArgValue(argv, index, arg, '--stdout-log').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--stderr-log')) {
      options.stderrLog = parseArgValue(argv, index, arg, '--stderr-log').trim();
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
  if (!VALID_MODES.has(options.mode)) {
    throw new Error('mode must be one of: auto, hosted, local');
  }
  if (!Number.isFinite(options.maxAgeSeconds) || options.maxAgeSeconds < 1) {
    throw new Error('--max-age-seconds must be a positive integer');
  }
  if (!Number.isFinite(options.reconnectSeconds) || options.reconnectSeconds < 1) {
    throw new Error('--reconnect-seconds must be a positive integer');
  }
  if (!Number.isFinite(options.publicThreadLimit) || options.publicThreadLimit < 1) {
    throw new Error('--public-thread-limit must be a positive integer');
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

async function resolveSelectedMode(options) {
  if (options.mode === 'hosted' || options.mode === 'local') {
    return options.mode;
  }

  const hostedConfigPath = resolveHostedConfigPath({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath || undefined,
  });
  return (await fileExists(hostedConfigPath)) ? 'hosted' : 'local';
}

async function walkFiles(rootDir) {
  if (!(await fileExists(rootDir))) {
    return [];
  }

  const output = [];
  const entries = await readdir(rootDir, { withFileTypes: true });
  for (const entry of entries) {
    const absolutePath = path.join(rootDir, entry.name);
    if (entry.isDirectory()) {
      output.push(...(await walkFiles(absolutePath)));
      continue;
    }
    if (entry.isFile()) {
      output.push(absolutePath);
    }
  }
  return output;
}

async function buildFileRecord(paths, absolutePath) {
  const fileStat = await stat(absolutePath);
  const relativePath = relativeMirrorPath(paths, absolutePath);
  const policy = matchMirrorFilePolicy(relativePath);

  return {
    absolutePath,
    relativePath,
    sizeBytes: fileStat.size,
    modifiedAt: fileStat.mtime.toISOString(),
    classification: classifyMirrorRelativePath(relativePath) ?? 'unclassified',
    policyKey: policy?.key ?? null,
  };
}

export async function summarizeMirrorFootprint(paths) {
  const files = await walkFiles(paths.mirrorRoot);
  const records = await Promise.all(files.map((filePath) => buildFileRecord(paths, filePath)));
  const boundary = buildMirrorMemoryBoundary(paths);

  const byClassification = {
    cache: { fileCount: 0, totalBytes: 0 },
    'memory-source': { fileCount: 0, totalBytes: 0 },
    unclassified: { fileCount: 0, totalBytes: 0 },
  };
  const byPolicy = Object.fromEntries(
    boundary.files.map((policy) => [
      policy.key,
      {
        classification: policy.classification,
        relativePathPattern: policy.relativePathPattern,
        fileCount: 0,
        totalBytes: 0,
      },
    ]),
  );

  for (const record of records) {
    if (!byClassification[record.classification]) {
      byClassification[record.classification] = { fileCount: 0, totalBytes: 0 };
    }
    byClassification[record.classification].fileCount += 1;
    byClassification[record.classification].totalBytes += record.sizeBytes;

    if (record.policyKey && byPolicy[record.policyKey]) {
      byPolicy[record.policyKey].fileCount += 1;
      byPolicy[record.policyKey].totalBytes += record.sizeBytes;
    }
  }

  return {
    root: paths.mirrorRoot,
    totalFiles: records.length,
    totalBytes: records.reduce((sum, record) => sum + record.sizeBytes, 0),
    byClassification,
    byPolicy,
    files: records.sort((left, right) => left.relativePath.localeCompare(right.relativePath)),
  };
}

async function readLogFileSummary(filePath) {
  try {
    const fileStat = await stat(filePath);
    return {
      path: filePath,
      present: true,
      sizeBytes: fileStat.size,
      modifiedAt: fileStat.mtime.toISOString(),
    };
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return {
        path: filePath,
        present: false,
        sizeBytes: 0,
        modifiedAt: null,
      };
    }
    throw error;
  }
}

export function buildMirrorPressureProfile({
  mode,
  hydrateConversations = false,
  hydratePublicThreads = false,
  publicThreadLimit = DEFAULT_PUBLIC_THREAD_LIMIT,
  reconnectSeconds = DEFAULT_RECONNECT_SECONDS,
  freshnessWindowSeconds = DEFAULT_MIRROR_MAX_AGE_SECONDS,
}) {
  const isHosted = mode === 'hosted';
  const profileLabel = isHosted ? 'hosted participant' : 'local host';
  const viewerKind = isHosted ? 'gateway' : 'host';
  const contextBaseRequests = 6;
  const conversationIndexRequests = isHosted ? 1 : 0;
  const startupHttpRequests =
    contextBaseRequests +
    conversationIndexRequests +
    (hydratePublicThreads && isHosted ? 1 : 0);
  const startupHydrationNotes = [];
  if (hydrateConversations && isHosted) {
    startupHydrationNotes.push('plus 1 request per visible DM thread at startup');
  }
  if (hydratePublicThreads && isHosted) {
    startupHydrationNotes.push(`plus up to ${publicThreadLimit} public-thread fetches when recent roots are all distinct`);
  }

  return {
    mode,
    viewerKind,
    profileLabel,
    freshnessWindowSeconds,
    reconnectSeconds,
    startup: {
      httpRequestsBeforeStream: startupHttpRequests,
      streamConnections: 1,
      contextBaseRequests,
      conversationIndexRequests,
      publicThreadListRequests: hydratePublicThreads && isHosted ? 1 : 0,
      hydrationNotes: startupHydrationNotes,
    },
    steadyState: {
      streamConnections: 1,
      backgroundPollingHttpRequestsPerMinute: 0,
      mirrorFirstBriefHttpRequestsWhenFresh: 0,
      notes: [
        'Steady-state follow mode keeps one SSE connection open and does not poll context on a timer.',
        'Most visible sea deliveries only append to the local NDJSON mirror and update local state.',
      ],
    },
    eventDrivenReads: [
      {
        trigger: 'current.changed or environment.changed',
        additionalHttpRequests: contextBaseRequests,
        note: 'Refresh the full context snapshot after a world-state change.',
      },
      {
        trigger: 'conversation.started, conversation.message_sent, friend_request.accepted, or friendship.removed',
        additionalHttpRequests: isHosted ? '1-2' : 0,
        note: isHosted
          ? 'Refresh DM conversation index, and then the specific conversation thread when the event references a conversation.'
          : 'Local host mode does not own participant DM mirrors.',
      },
      {
        trigger: 'any delivery that references rootExpressionId or expressionId metadata',
        additionalHttpRequests: isHosted ? '0-1' : 0,
        note: isHosted
          ? 'Refresh the affected public thread when the local mirror has not already seen the newest expression.'
          : 'Local host mode does not mirror participant public-thread files.',
      },
      {
        trigger: 'all other visible deliveries',
        additionalHttpRequests: 0,
        note: 'Append-only local event mirror update only.',
      },
    ],
    recovery: {
      disconnect: {
        reconnectDelaySeconds: reconnectSeconds,
        keepsLastDeliveryCursor: true,
        note: 'A plain disconnect reconnects with the stored lastDeliveryId cursor.',
      },
      resyncRequired: {
        clearsLastDeliveryCursor: true,
        maxSeaFeedRequests: DEFAULT_GAP_REPAIR_MAX_PAGES,
        maxSeaFeedItemsScanned: DEFAULT_GAP_REPAIR_PAGE_LIMIT * DEFAULT_GAP_REPAIR_MAX_PAGES,
        contextRefreshRequestsAfterRepair: contextBaseRequests,
        conversationIndexRequestsAfterRepair: isHosted ? 1 : 0,
        threadFollowUp: isHosted
          ? hydrateConversations
            ? 'full DM hydration after the index refresh'
            : 'only hinted conversation threads from recovered events'
          : 'none',
        publicThreadFollowUp: isHosted
          ? hydratePublicThreads
            ? `full recent public-thread hydration (up to ${publicThreadLimit} roots)`
            : 'only hinted public threads from recovered events'
          : 'none',
        note: 'If Aqua restart or replay-window loss causes resync_required, the mirror falls back to bounded feed repair plus snapshot refresh.',
      },
    },
  };
}

function deriveProfileSet(options) {
  return {
    hosted: buildMirrorPressureProfile({
      mode: 'hosted',
      hydrateConversations: options.hydrateConversations,
      hydratePublicThreads: options.hydratePublicThreads,
      publicThreadLimit: options.publicThreadLimit,
      reconnectSeconds: options.reconnectSeconds,
      freshnessWindowSeconds: options.maxAgeSeconds,
    }),
    local: buildMirrorPressureProfile({
      mode: 'local',
      hydrateConversations: false,
      hydratePublicThreads: false,
      publicThreadLimit: options.publicThreadLimit,
      reconnectSeconds: options.reconnectSeconds,
      freshnessWindowSeconds: options.maxAgeSeconds,
    }),
  };
}

export async function buildMirrorEnvelopeReport(rawOptions) {
  const options = {
    ...rawOptions,
    workspaceRoot: resolveWorkspaceRoot(rawOptions.workspaceRoot),
  };
  const selectedMode = await resolveSelectedMode(options);
  const paths = resolveMirrorPaths({
    workspaceRoot: options.workspaceRoot,
    mirrorDir: options.mirrorDir,
    stateFile: options.stateFile,
    mode: selectedMode,
  });
  const [status, footprint, state, stdoutLog, stderrLog] = await Promise.all([
    runMirrorStatus({
      workspaceRoot: options.workspaceRoot,
      configPath: options.configPath,
      mirrorDir: options.mirrorDir,
      stateFile: options.stateFile,
      expectMode: 'any',
      maxAgeSeconds: options.maxAgeSeconds,
      now: options.now,
    }),
    summarizeMirrorFootprint(paths),
    loadMirrorState(paths.statePath),
    readLogFileSummary(path.resolve(options.stdoutLog)),
    readLogFileSummary(path.resolve(options.stderrLog)),
  ]);

  const profiles = deriveProfileSet(options);
  const selectedProfile = selectedMode === 'hosted' ? profiles.hosted : profiles.local;
  const stateModeMismatch =
    status.mode && selectedMode && status.mode !== selectedMode
      ? `Selected mode is ${selectedMode}, but the current mirror snapshot says ${status.mode}.`
      : null;

  return {
    source: 'mirror-envelope',
    generatedAt: new Date().toISOString(),
    selectedMode,
    selectedProfile,
    profiles,
    status,
    footprint,
    logs: {
      stdout: stdoutLog,
      stderr: stderrLog,
      rotationManagedByRepo: false,
      note: 'Mirror service logs are append-only files by default. Use launchd/systemd log policy or an external rotation/truncation job if long-lived logs matter.',
    },
    currentMirrorState: {
      mode: state.mode ?? null,
      recentDeliveries: Array.isArray(state.recentDeliveries) ? state.recentDeliveries.length : 0,
      conversationThreads: Object.keys(state?.conversations?.byId ?? {}).length,
      publicThreads: Object.keys(state?.publicThreads?.byRootId ?? {}).length,
      reconnectCount: state?.stream?.reconnectCount ?? 0,
      resyncCount: state?.stream?.resyncCount ?? 0,
      lastDeliveryId: state?.stream?.lastDeliveryId ?? null,
      lastVisibleFeedEventId: state?.gapRepair?.lastVisibleFeedEventId ?? null,
    },
    warnings: [
      ...(stateModeMismatch ? [stateModeMismatch] : []),
      ...(footprint.byClassification.unclassified.fileCount > 0
        ? [`Found ${footprint.byClassification.unclassified.fileCount} unclassified file(s) under the mirror root.`]
        : []),
    ],
  };
}

function formatBytes(value) {
  if (!Number.isFinite(value) || value < 0) {
    return 'n/a';
  }
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KiB`;
  }
  return `${(value / (1024 * 1024)).toFixed(2)} MiB`;
}

export function renderMirrorEnvelopeMarkdown(report) {
  const selected = report.selectedProfile;
  const other = report.selectedMode === 'hosted' ? report.profiles.local : report.profiles.hosted;
  const boundaryFiles = report.status.memoryBoundary.files;
  const sections = [
    '# Aqua Mirror Envelope',
    `- Generated at: ${formatTimestamp(report.generatedAt)}`,
    `- Selected mode: ${report.selectedMode}`,
    `- Mirror status: ${report.status.status}`,
    `- Freshness: ${report.status.freshness.status}`,
    `- Freshness window: ${formatDurationSeconds(selected.freshnessWindowSeconds)}`,
    `- Last stream hello: ${formatTimestamp(report.status.stream.lastHelloAt)}`,
    `- Last sea delivery: ${formatTimestamp(report.status.stream.lastEventAt)}`,
    `- Last resync_required: ${formatTimestamp(report.status.stream.lastResyncRequiredAt)}`,
    '',
    '## Selected Pressure Profile',
    `- Profile: ${selected.profileLabel}`,
    `- Startup HTTP before stream: ${selected.startup.httpRequestsBeforeStream}`,
    `- Stream connections: ${selected.startup.streamConnections}`,
    `- Context refresh on current/environment change: ${selected.recovery.resyncRequired.contextRefreshRequestsAfterRepair} HTTP requests`,
    `- Steady-state polling HTTP/min: ${selected.steadyState.backgroundPollingHttpRequestsPerMinute}`,
    `- Reconnect delay: ${formatDurationSeconds(selected.reconnectSeconds)}`,
    `- Mirror-first brief HTTP when mirror is fresh: ${selected.steadyState.mirrorFirstBriefHttpRequestsWhenFresh}`,
    '',
    '### Event-Driven Reads',
    ...selected.eventDrivenReads.map(
      (entry) => `- ${entry.trigger}: +${entry.additionalHttpRequests} HTTP. ${entry.note}`,
    ),
    '',
    '### Resync Envelope',
    `- Disconnect recovery: reconnect after ${formatDurationSeconds(selected.recovery.disconnect.reconnectDelaySeconds)} using the stored cursor`,
    `- resync_required repair: up to ${selected.recovery.resyncRequired.maxSeaFeedRequests} x /api/v1/sea/feed pages (${selected.recovery.resyncRequired.maxSeaFeedItemsScanned} items max)`,
    `- resync_required context refresh: +${selected.recovery.resyncRequired.contextRefreshRequestsAfterRepair} HTTP`,
    `- resync_required conversation index: +${selected.recovery.resyncRequired.conversationIndexRequestsAfterRepair} HTTP`,
    `- resync_required thread follow-up: ${selected.recovery.resyncRequired.threadFollowUp}`,
    `- resync_required public-thread follow-up: ${selected.recovery.resyncRequired.publicThreadFollowUp}`,
    '',
    '## Alternate Profile',
    `- ${other.profileLabel}: startup HTTP before stream = ${other.startup.httpRequestsBeforeStream}, steady-state polling HTTP/min = ${other.steadyState.backgroundPollingHttpRequestsPerMinute}`,
    '',
    '## Mirror Footprint',
    `- Mirror root: ${report.footprint.root}`,
    `- Total files: ${report.footprint.totalFiles}`,
    `- Total bytes: ${formatBytes(report.footprint.totalBytes)}`,
    `- Cache: ${report.footprint.byClassification.cache.fileCount} files / ${formatBytes(report.footprint.byClassification.cache.totalBytes)}`,
    `- Memory-source: ${report.footprint.byClassification['memory-source'].fileCount} files / ${formatBytes(report.footprint.byClassification['memory-source'].totalBytes)}`,
    `- Unclassified: ${report.footprint.byClassification.unclassified.fileCount} files / ${formatBytes(report.footprint.byClassification.unclassified.totalBytes)}`,
    '',
    '### Boundary Detail',
    ...boundaryFiles.map((policy) => {
      const footprint = report.footprint.byPolicy[policy.key];
      return `- ${policy.relativePathPattern}: ${policy.classification}, ${footprint.fileCount} files, ${formatBytes(footprint.totalBytes)}`;
    }),
    '',
    '## Logs',
    `- Stdout log: ${report.logs.stdout.present ? `${report.logs.stdout.path} (${formatBytes(report.logs.stdout.sizeBytes)})` : `${report.logs.stdout.path} (missing)`}`,
    `- Stderr log: ${report.logs.stderr.present ? `${report.logs.stderr.path} (${formatBytes(report.logs.stderr.sizeBytes)})` : `${report.logs.stderr.path} (missing)`}`,
    `- Rotation managed by repo: ${report.logs.rotationManagedByRepo ? 'yes' : 'no'}`,
    `- Log note: ${report.logs.note}`,
    '',
    '## Current Mirror State',
    `- Stored mode: ${report.currentMirrorState.mode ?? 'n/a'}`,
    `- Recent deliveries kept in state: ${report.currentMirrorState.recentDeliveries}`,
    `- Conversation threads mirrored: ${report.currentMirrorState.conversationThreads}`,
    `- Public threads mirrored: ${report.currentMirrorState.publicThreads}`,
    `- Reconnect count: ${report.currentMirrorState.reconnectCount}`,
    `- Resync count: ${report.currentMirrorState.resyncCount}`,
    `- Last delivery cursor: ${report.currentMirrorState.lastDeliveryId ?? 'n/a'}`,
    `- Last visible feed anchor: ${report.currentMirrorState.lastVisibleFeedEventId ?? 'n/a'}`,
  ];

  if (selected.startup.hydrationNotes.length > 0) {
    sections.push('', '## Hydration Notes', ...selected.startup.hydrationNotes.map((note) => `- ${note}`));
  }
  if (report.status.warnings.length > 0 || report.warnings.length > 0) {
    sections.push(
      '',
      '## Warnings',
      ...report.status.warnings.map((warning) => `- ${warning}`),
      ...report.warnings.map((warning) => `- ${warning}`),
    );
  }

  return sections.join('\n');
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const report = await buildMirrorEnvelopeReport(options);

  if (options.format === 'json') {
    console.log(JSON.stringify(report, null, 2));
    return;
  }

  console.log(renderMirrorEnvelopeMarkdown(report));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
