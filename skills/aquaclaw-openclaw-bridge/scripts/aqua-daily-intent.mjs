#!/usr/bin/env node

import { mkdir, readFile, readdir, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

import { resolveMirrorPaths, writeJsonFile } from './aqua-mirror-common.mjs';
import {
  generateSeaDiaryContext,
  resolveSeaDiaryContextArtifactPaths,
} from './aqua-sea-diary-context.mjs';
import { resolveLifeLoopWriteBackPaths } from './aqua-life-loop-writeback.mjs';
import {
  formatTimestamp,
  parseArgValue,
  parsePositiveInt,
  resolveWorkspaceRoot,
} from './hosted-aqua-common.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);
const VALID_EXPECT_MODES = new Set(['any', 'auto', 'hosted', 'local']);
const DEFAULT_MODE_LIMIT = 5;
const DEFAULT_TOP_HOOK_LIMIT = 4;
const DEFAULT_OPEN_LOOP_LIMIT = 6;
const DEFAULT_WRITEBACK_CARRY_FORWARD_DAYS = 3;
const DEFAULT_WRITEBACK_CARRY_FORWARD_LANE_LIMIT = 1;

function printHelp() {
  console.log(`Usage: aqua-daily-intent.mjs [options]

Options:
  --workspace-root <path>         OpenClaw workspace root
  --config-path <path>            Hosted Aqua config path
  --mirror-dir <path>             Mirror root directory
  --state-file <path>             Mirror state file override
  --community-memory-dir <path>   Local community-memory root override
  --expect-mode <mode>            any|auto|hosted|local (default: any)
  --date <YYYY-MM-DD>             Local diary date in --timezone (default: today)
  --timezone <iana>               Local timezone for diary bucketing (default: current system timezone)
  --digest-root <path>            Override the diary-digests artifact directory
  --synthesis-root <path>         Override the memory-synthesis artifact directory
  --diary-root <path>             Override the sea-diary-context artifact directory
  --artifact-root <path>          Override the daily-intent artifact directory
  --build-if-missing              Build the sea-diary-context artifact first when needed
  --max-events <n>                Max notable events when building missing digest artifacts (default: 8)
  --scene-limit <n>               Max same-day scenes when building missing diary context (default: 12)
  --community-limit <n>           Max same-day community notes when building missing diary context (default: 6)
  --write-artifact                Persist JSON + Markdown daily-intent artifacts
  --format <fmt>                  json|markdown (default: markdown)
  --help                          Show this message
`);
}

function validateTimeZone(value) {
  const timeZone = String(value || '').trim();
  if (!timeZone) {
    throw new Error('--timezone requires a non-empty IANA timezone');
  }
  try {
    new Intl.DateTimeFormat('en-US', { timeZone }).format(new Date());
  } catch {
    throw new Error(`invalid timezone: ${timeZone}`);
  }
  return timeZone;
}

function currentLocalDate(timeZone) {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date());
}

function normalizeText(value) {
  return String(value ?? '').replace(/\s+/g, ' ').trim();
}

function previewText(value, limit = 180) {
  const normalized = normalizeText(value);
  if (!normalized) {
    return '';
  }
  if (normalized.length <= limit) {
    return normalized;
  }
  return `${normalized.slice(0, Math.max(limit - 1, 1)).trimEnd()}...`;
}

function uniqueValues(items) {
  return [...new Set(items.filter((item) => item !== null && item !== undefined && item !== ''))];
}

function formatHandle(value) {
  const handle = normalizeText(value).replace(/^@+/, '');
  return handle ? `@${handle}` : '@unknown';
}

function normalizeSpeakerLabel(value) {
  return normalizeText(value) || 'unknown speaker';
}

function isSelfSpeaker(label, viewerHandle) {
  const normalizedLabel = normalizeSpeakerLabel(label).toLowerCase();
  if (!normalizedLabel) {
    return false;
  }
  if (normalizedLabel === 'self') {
    return true;
  }
  const normalizedViewer = normalizeText(viewerHandle).replace(/^@+/, '').toLowerCase();
  if (!normalizedViewer) {
    return false;
  }
  return normalizedLabel.includes(`@${normalizedViewer}`) || normalizedLabel.startsWith(normalizedViewer);
}

function normalizeHandleForComparison(value) {
  return normalizeText(value).replace(/^@+/, '').toLowerCase();
}

function localDateString(value, timeZone) {
  if (!value) {
    return null;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }

  return new Intl.DateTimeFormat('en-CA', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(parsed);
}

function previousDateString(targetDate, daysBack) {
  const parsed = new Date(`${targetDate}T00:00:00.000Z`);
  parsed.setUTCDate(parsed.getUTCDate() - daysBack);
  return parsed.toISOString().slice(0, 10);
}

function buildCarryForwardDateWindow(targetDate, maxDays = DEFAULT_WRITEBACK_CARRY_FORWARD_DAYS) {
  return new Set(Array.from({ length: Math.max(maxDays, 1) }, (_, index) => previousDateString(targetDate, index)));
}

function compareRecordedAtDescending(left, right) {
  const leftMs = Date.parse(left?.recordedAt ?? '');
  const rightMs = Date.parse(right?.recordedAt ?? '');
  if (Number.isNaN(leftMs) && Number.isNaN(rightMs)) {
    return 0;
  }
  if (Number.isNaN(leftMs)) {
    return 1;
  }
  if (Number.isNaN(rightMs)) {
    return -1;
  }
  return rightMs - leftMs;
}

function buildDefaultOptions() {
  return {
    artifactRoot: null,
    buildIfMissing: false,
    communityLimit: 6,
    communityMemoryDir: process.env.AQUACLAW_COMMUNITY_MEMORY_DIR || null,
    configPath: process.env.AQUACLAW_HOSTED_CONFIG || null,
    date: null,
    diaryRoot: null,
    digestRoot: null,
    expectMode: 'any',
    format: 'markdown',
    maxEvents: 8,
    mirrorDir: process.env.AQUACLAW_MIRROR_DIR || null,
    sceneLimit: 12,
    stateFile: process.env.AQUACLAW_MIRROR_STATE_FILE || null,
    synthesisRoot: null,
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT || null,
    writeArtifact: false,
  };
}

function normalizeOptions(options = {}) {
  const normalized = {
    ...buildDefaultOptions(),
    ...options,
  };

  if (!VALID_FORMATS.has(normalized.format)) {
    throw new Error('format must be json or markdown');
  }
  if (!VALID_EXPECT_MODES.has(normalized.expectMode)) {
    throw new Error('expect-mode must be one of: any, auto, hosted, local');
  }
  if (normalized.date && !/^\d{4}-\d{2}-\d{2}$/.test(normalized.date)) {
    throw new Error('--date must use YYYY-MM-DD');
  }

  normalized.workspaceRoot = resolveWorkspaceRoot(normalized.workspaceRoot);
  normalized.timeZone = validateTimeZone(normalized.timeZone);
  normalized.date = normalized.date ?? currentLocalDate(normalized.timeZone);
  return normalized;
}

function parseOptions(argv) {
  const options = buildDefaultOptions();

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--build-if-missing') {
      options.buildIfMissing = true;
      continue;
    }
    if (arg === '--write-artifact') {
      options.writeArtifact = true;
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
    if (arg.startsWith('--community-memory-dir')) {
      options.communityMemoryDir = parseArgValue(argv, index, arg, '--community-memory-dir').trim();
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
    if (arg.startsWith('--date')) {
      options.date = parseArgValue(argv, index, arg, '--date').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--timezone')) {
      options.timeZone = validateTimeZone(parseArgValue(argv, index, arg, '--timezone'));
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--digest-root')) {
      options.digestRoot = parseArgValue(argv, index, arg, '--digest-root').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--synthesis-root')) {
      options.synthesisRoot = parseArgValue(argv, index, arg, '--synthesis-root').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--diary-root')) {
      options.diaryRoot = parseArgValue(argv, index, arg, '--diary-root').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--artifact-root')) {
      options.artifactRoot = parseArgValue(argv, index, arg, '--artifact-root').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--max-events')) {
      options.maxEvents = parsePositiveInt(parseArgValue(argv, index, arg, '--max-events'), '--max-events');
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--scene-limit')) {
      options.sceneLimit = parsePositiveInt(parseArgValue(argv, index, arg, '--scene-limit'), '--scene-limit');
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--community-limit')) {
      options.communityLimit = parsePositiveInt(parseArgValue(argv, index, arg, '--community-limit'), '--community-limit');
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

  return normalizeOptions(options);
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

function resolveDailyIntentArtifactPaths(paths, targetDate, artifactRoot = null) {
  const root = artifactRoot
    ? path.resolve(artifactRoot)
    : path.join(path.dirname(paths.mirrorRoot), 'life-loop', 'daily-intent');
  return {
    root,
    jsonPath: path.join(root, `${targetDate}.json`),
    markdownPath: path.join(root, `${targetDate}.md`),
  };
}

async function writeTextFileAtomically(filePath, value) {
  await mkdir(path.dirname(filePath), { recursive: true });
  const tempPath = `${filePath}.tmp-${process.pid}-${Date.now()}`;
  await writeFile(tempPath, `${String(value)}\n`, 'utf8');
  await rename(tempPath, filePath);
}

async function writeDailyIntentArtifacts({ summary, markdown, paths, targetDate, artifactRoot = null }) {
  const artifactPaths = resolveDailyIntentArtifactPaths(paths, targetDate, artifactRoot);
  await writeJsonFile(artifactPaths.jsonPath, summary);
  await writeTextFileAtomically(artifactPaths.markdownPath, markdown);
  return artifactPaths;
}

async function loadSeaDiaryContextSummary(
  options,
  {
    generateSeaDiaryContextFn = generateSeaDiaryContext,
    loadHostedConfigFn,
    requestJsonFn,
  } = {},
) {
  const paths = resolveMirrorPaths({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath,
    mirrorDir: options.mirrorDir,
    stateFile: options.stateFile,
    mode: options.expectMode === 'any' ? 'auto' : options.expectMode,
  });
  const artifactPaths = resolveSeaDiaryContextArtifactPaths(paths, options.date, options.diaryRoot);
  const storedSummary = await readJsonIfPresent(artifactPaths.jsonPath);
  if (storedSummary) {
    const targetDateMatches = storedSummary?.targetDate === options.date;
    const timeZoneMatches = storedSummary?.timeZone === options.timeZone;
    if (targetDateMatches && timeZoneMatches) {
      return {
        summary: storedSummary,
        artifactPaths,
        paths,
        status: 'existing-artifact',
      };
    }
    if (!options.buildIfMissing) {
      throw new Error(
        `sea diary context artifact at ${artifactPaths.jsonPath} was built for ${storedSummary?.targetDate ?? 'unknown date'} (${storedSummary?.timeZone ?? 'unknown timezone'}). Rerun with --build-if-missing or use matching --date/--timezone.`,
      );
    }
  }

  if (!options.buildIfMissing) {
    throw new Error(
      `sea diary context artifact not found at ${artifactPaths.jsonPath}. Run aqua-sea-diary-context.sh --write-artifact first or rerun with --build-if-missing.`,
    );
  }

  const diaryResult = await generateSeaDiaryContextFn(
    {
      workspaceRoot: options.workspaceRoot,
      configPath: options.configPath,
      mirrorDir: options.mirrorDir,
      stateFile: options.stateFile,
      communityMemoryDir: options.communityMemoryDir,
      expectMode: options.expectMode,
      date: options.date,
      timeZone: options.timeZone,
      digestRoot: options.digestRoot,
      synthesisRoot: options.synthesisRoot,
      artifactRoot: options.diaryRoot,
      buildIfMissing: true,
      maxEvents: options.maxEvents,
      sceneLimit: options.sceneLimit,
      communityLimit: options.communityLimit,
      writeArtifact: true,
      format: 'json',
    },
    {
      ...(loadHostedConfigFn ? { loadHostedConfigFn } : {}),
      ...(requestJsonFn ? { requestJsonFn } : {}),
    },
  );

  return {
    summary: diaryResult.summary,
    artifactPaths: diaryResult.artifactPaths ?? artifactPaths,
    paths: diaryResult.synthesisResult?.paths ?? paths,
    status: storedSummary ? 'rebuilt-artifact' : 'built-artifact',
  };
}

async function readWriteBackArchiveEntries(writeBackRoot) {
  let directoryEntries;
  try {
    directoryEntries = await readdir(writeBackRoot, { withFileTypes: true });
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return {
        status: 'missing',
        entries: [],
        warnings: [],
      };
    }
    throw error;
  }

  const fileNames = directoryEntries
    .filter((entry) => entry.isFile() && entry.name.endsWith('.ndjson'))
    .map((entry) => entry.name)
    .sort()
    .reverse();

  if (fileNames.length === 0) {
    return {
      status: 'missing',
      entries: [],
      warnings: [],
    };
  }

  const entries = [];
  const warnings = [];
  for (const fileName of fileNames) {
    const raw = await readFile(path.join(writeBackRoot, fileName), 'utf8');
    for (const line of raw.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed) {
        continue;
      }
      try {
        const parsed = JSON.parse(trimmed);
        if (parsed && typeof parsed === 'object') {
          entries.push(parsed);
        }
      } catch {
        warnings.push(`write-back archive line in ${fileName} could not be parsed`);
      }
    }
  }

  entries.sort(compareRecordedAtDescending);
  return {
    status: 'available',
    entries,
    warnings,
  };
}

function selectCarryForwardWriteBackEntries(entries, { date, timeZone }) {
  const allowedDates = buildCarryForwardDateWindow(date);
  const selected = [];
  const laneCounts = new Map();

  for (const entry of Array.isArray(entries) ? entries : []) {
    const lane = typeof entry?.lane === 'string' ? entry.lane : null;
    if (lane !== 'public_expression' && lane !== 'direct_message') {
      continue;
    }

    const localDate = localDateString(entry?.recordedAt ?? entry?.output?.createdAt ?? null, timeZone);
    if (!localDate || !allowedDates.has(localDate)) {
      continue;
    }

    const nextCount = (laneCounts.get(lane) ?? 0) + 1;
    if (nextCount > DEFAULT_WRITEBACK_CARRY_FORWARD_LANE_LIMIT) {
      continue;
    }

    selected.push(entry);
    laneCounts.set(lane, nextCount);
  }

  return selected;
}

function summarizeWriteBackSource(writeBackSource) {
  const latestEntry = Array.isArray(writeBackSource?.entries) && writeBackSource.entries.length > 0 ? writeBackSource.entries[0] : null;
  return {
    status: writeBackSource?.status ?? 'missing',
    root: writeBackSource?.paths?.root ?? null,
    selectionKind: writeBackSource?.paths?.selectionKind ?? null,
    profileId: writeBackSource?.paths?.profileId ?? null,
    latestRecordedAt: latestEntry?.recordedAt ?? null,
    latestLane: latestEntry?.lane ?? null,
    carriedForwardEntryIds: (Array.isArray(writeBackSource?.entries) ? writeBackSource.entries : []).map((item) => item?.id).filter(Boolean),
  };
}

async function loadWriteBackCarryForward(options) {
  const paths = resolveLifeLoopWriteBackPaths({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath,
  });
  const archive = await readWriteBackArchiveEntries(paths.root);
  const entries = archive.status === 'available' ? selectCarryForwardWriteBackEntries(archive.entries, options) : [];

  return {
    status:
      archive.status !== 'available'
        ? archive.status
        : entries.length > 0
          ? 'available'
          : 'stale',
    paths,
    entries,
    warnings: archive.warnings,
  };
}

function createSourceRefRegistry(viewerHandle) {
  const refs = [];
  const ids = new Map();

  function ensureRef(key, payload) {
    const normalizedKey = normalizeText(key);
    if (!normalizedKey) {
      throw new Error('source ref key is required');
    }
    if (ids.has(normalizedKey)) {
      return ids.get(normalizedKey);
    }
    const id = `src-${refs.length + 1}`;
    const ref = {
      id,
      layer: payload.layer,
      kind: payload.kind,
      createdAt: payload.createdAt ?? null,
      summary: payload.summary ?? null,
      detail: payload.detail ?? null,
      targetHandle: payload.targetHandle ? formatHandle(payload.targetHandle) : null,
      targetGatewayId: payload.targetGatewayId ?? null,
      exposure: payload.exposure ?? null,
      mentionPolicy: payload.mentionPolicy ?? null,
      sourceKind: payload.sourceKind ?? null,
      triggerKind: payload.triggerKind ?? null,
      speakerRole: payload.speakerRole ?? null,
      viewerHandle: viewerHandle ? formatHandle(viewerHandle) : null,
    };
    refs.push(ref);
    ids.set(normalizedKey, id);
    return id;
  }

  return {
    refs,
    ensureRef,
  };
}

function buildModeEntries({
  diarySummary,
  registry,
}) {
  const counts = diarySummary?.visibleLayer?.counts ?? {};
  const continuityCounts = diarySummary?.visibleLayer?.continuityCounts ?? {};
  const viewerHandle = diarySummary?.visibleLayer?.viewer?.handle ?? null;
  const publicThreads = Array.isArray(diarySummary?.localSynthesisLayer?.publicContinuity)
    ? diarySummary.localSynthesisLayer.publicContinuity
    : [];
  const directThreads = Array.isArray(diarySummary?.localSynthesisLayer?.directContinuity)
    ? diarySummary.localSynthesisLayer.directContinuity
    : [];
  const scenes = Array.isArray(diarySummary?.privateSceneLayer?.items) ? diarySummary.privateSceneLayer.items : [];
  const notes = Array.isArray(diarySummary?.privateCommunityLayer?.items) ? diarySummary.privateCommunityLayer.items : [];
  const warnings = Array.isArray(diarySummary?.warnings) ? diarySummary.warnings : [];
  const caveats = Array.isArray(diarySummary?.diaryCaveats) ? diarySummary.diaryCaveats : [];

  const signals = [];

  const observeRefs = [];
  if (Array.isArray(diarySummary?.visibleLayer?.notableEvents) && diarySummary.visibleLayer.notableEvents.length) {
    const firstEvent = diarySummary.visibleLayer.notableEvents[0];
    observeRefs.push(
      registry.ensureRef('visible:notable-event:first', {
        layer: 'visible',
        kind: 'notable_event',
        createdAt: firstEvent?.createdAt ?? null,
        summary: firstEvent?.summary ?? previewText(firstEvent?.detail),
        detail: firstEvent?.detail ?? null,
        exposure: 'public',
        sourceKind: firstEvent?.type ?? null,
      }),
    );
  }
  if (diarySummary?.visibleLayer?.current?.label || diarySummary?.visibleLayer?.environment?.summary) {
    observeRefs.push(
      registry.ensureRef('visible:ambient', {
        layer: 'visible',
        kind: 'ambient',
        summary: [
          diarySummary?.visibleLayer?.current?.label ? `current ${diarySummary.visibleLayer.current.label}` : null,
          diarySummary?.visibleLayer?.environment?.summary ? diarySummary.visibleLayer.environment.summary : null,
        ]
          .filter(Boolean)
          .join(' | '),
        detail: diarySummary?.visibleLayer?.current?.tone ?? null,
        exposure: 'public',
      }),
    );
  }
  signals.push({
    mode: 'observe',
    score:
      1 +
      Math.min(Number.isFinite(counts.total) ? counts.total : 0, 2) +
      Math.min(Number.isFinite(continuityCounts.publicThreads) ? continuityCounts.publicThreads : 0, 1) +
      (observeRefs.length > 0 ? 1 : 0),
    summary:
      (Number.isFinite(counts.total) ? counts.total : 0) > 0 || observeRefs.length > 0
        ? 'Visible motion and ambient sea state are strong enough to keep an observe-first posture alive.'
        : 'There is little same-day visible motion, so observation should stay light and conservative.',
    sourceRefIds: uniqueValues(observeRefs),
  });

  const publicRefs = [];
  if (publicThreads.length > 0) {
    const firstThread = publicThreads[0];
    publicRefs.push(
      registry.ensureRef('local:public-thread:0', {
        layer: 'local_synthesis',
        kind: 'public_continuity',
        summary: firstThread.summary,
        detail: firstThread.latestLine,
        targetHandle: firstThread.rootSpeaker,
        exposure: 'public',
        speakerRole: isSelfSpeaker(firstThread.latestSpeaker, viewerHandle) ? 'self_latest' : 'other_latest',
      }),
    );
  }
  signals.push({
    mode: 'public',
    score:
      publicThreads.length * 2 +
      (Number.isFinite(counts.publicExpressions) ? counts.publicExpressions : 0) +
      (publicRefs.length > 0 ? 1 : 0),
    summary:
      publicThreads.length > 0
        ? 'Same-day public-thread continuity survived, so public replies or one more public line still have natural footing.'
        : 'Public motion is thin, so outward public behavior should stay secondary.',
    sourceRefIds: uniqueValues(publicRefs),
  });

  const directRefs = [];
  if (directThreads.length > 0) {
    const firstDirect = directThreads[0];
    directRefs.push(
      registry.ensureRef('local:direct-thread:0', {
        layer: 'local_synthesis',
        kind: 'direct_continuity',
        summary: firstDirect.summary,
        detail: firstDirect.latestLine,
        targetHandle: firstDirect.peerHandle,
        exposure: 'private',
        speakerRole: isSelfSpeaker(firstDirect.latestSpeaker, viewerHandle) ? 'self_latest' : 'other_latest',
      }),
    );
  }
  signals.push({
    mode: 'direct',
    score:
      directThreads.length * 2 +
      (Number.isFinite(counts.directMessages) ? counts.directMessages : 0) +
      (directRefs.length > 0 ? 1 : 0),
    summary:
      directThreads.length > 0
        ? 'Direct-message continuity stayed live enough to justify DM-sensitive behavior.'
        : 'No strong DM continuity survived, so relationship follow-ups should stay selective.',
    sourceRefIds: uniqueValues(directRefs),
  });

  const reflectiveRefs = [];
  if (scenes.length > 0) {
    const firstScene = scenes[0];
    reflectiveRefs.push(
      registry.ensureRef(`scene:${firstScene.id ?? '0'}`, {
        layer: 'private_scene',
        kind: firstScene.type ?? 'scene',
        createdAt: firstScene.createdAt ?? null,
        summary: firstScene.summary ?? null,
        detail: firstScene.trigger?.reason ?? null,
        targetGatewayId: firstScene.trigger?.peerGatewayId ?? null,
        exposure: 'gateway_private',
        triggerKind: firstScene.trigger?.kind ?? null,
      }),
    );
  }
  if (notes.length > 0) {
    const firstNote = notes[0];
    reflectiveRefs.push(
      registry.ensureRef(`community:${firstNote.id ?? '0'}`, {
        layer: 'private_community',
        kind: 'community_note',
        createdAt: firstNote.createdAt ?? null,
        summary: firstNote.summary ?? firstNote.cue ?? null,
        detail: firstNote.cue ?? null,
        exposure: firstNote.mentionPolicy === 'public_ok' ? 'public_ok' : 'private',
        mentionPolicy: firstNote.mentionPolicy ?? null,
        sourceKind: firstNote.sourceKind ?? null,
      }),
    );
  }
  signals.push({
    mode: 'reflective',
    score: scenes.length * 2 + notes.length + (reflectiveRefs.length > 0 ? 1 : 0),
    summary:
      scenes.length > 0 || notes.length > 0
        ? 'Private scene and rumor layers survived the day, so inward reflection still matters.'
        : 'Private experiential evidence stayed thin, so reflection should not overfit.',
    sourceRefIds: uniqueValues(reflectiveRefs),
  });

  const guardedRefs = [];
  const privateOnlyNote = notes.find((note) => note?.mentionPolicy === 'private_only');
  if (privateOnlyNote) {
    guardedRefs.push(
      registry.ensureRef(`community:private-only:${privateOnlyNote.id ?? '0'}`, {
        layer: 'private_community',
        kind: 'community_note',
        createdAt: privateOnlyNote.createdAt ?? null,
        summary: privateOnlyNote.summary ?? privateOnlyNote.cue ?? null,
        detail: privateOnlyNote.handling ?? null,
        exposure: 'private_only',
        mentionPolicy: privateOnlyNote.mentionPolicy ?? null,
        sourceKind: privateOnlyNote.sourceKind ?? null,
      }),
    );
  }
  if (warnings.length > 0 || caveats.length > 0) {
    guardedRefs.push(
      registry.ensureRef('local:caution', {
        layer: 'local_synthesis',
        kind: 'caveat',
        summary: warnings[0] ?? caveats[0] ?? null,
        detail: previewText([...(warnings ?? []), ...(caveats ?? [])].join(' | '), 220) || null,
        exposure: 'local_only',
      }),
    );
  }
  signals.push({
    mode: 'guarded',
    score:
      notes.filter((note) => note?.mentionPolicy === 'private_only').length * 2 +
      warnings.length +
      caveats.length +
      (guardedRefs.length > 0 ? 1 : 0),
    summary:
      privateOnlyNote || warnings.length > 0 || caveats.length > 0
        ? 'Some same-day cues should stay private, hearsay-bounded, or evidence-light.'
        : 'There is no unusually strong privacy or evidence pressure inside this day slice.',
    sourceRefIds: uniqueValues(guardedRefs),
  });

  const totalSignalScore = signals.reduce((sum, item) => sum + item.score, 0);
  signals.push({
    mode: 'quiet',
    score:
      totalSignalScore <= 4
        ? 5
        : totalSignalScore <= 8
          ? 2
          : 0,
    summary:
      totalSignalScore <= 4
        ? 'Overall same-day signal is light enough that quiet behavior remains legitimate.'
        : 'This day already has enough signal that full quietness is not the dominant read.',
    sourceRefIds: [],
  });

  return signals
    .filter((item) => item.score > 0)
    .sort((left, right) => right.score - left.score || left.mode.localeCompare(right.mode))
    .slice(0, DEFAULT_MODE_LIMIT)
    .map((item) => ({
      mode: item.mode,
      score: item.score,
      summary: item.summary,
      sourceRefIds: item.sourceRefIds,
    }));
}

function normalizeCarryForwardTargetKey(item) {
  return [
    item?.lane ?? '',
    normalizeHandleForComparison(item?.targetHandle),
    normalizeText(item?.targetGatewayId),
    normalizeText(item?.conversationId),
  ].join('|');
}

function hasCarryForwardTarget(items, candidate) {
  const candidateKey = normalizeCarryForwardTargetKey(candidate);
  return (Array.isArray(items) ? items : []).some((item) => normalizeCarryForwardTargetKey(item) === candidateKey);
}

function buildWriteBackSourceRef({ registry, entry, hook, key }) {
  return registry.ensureRef(key, {
    layer: 'local_writeback',
    kind: entry?.output?.kind ?? entry?.lane ?? 'writeback',
    createdAt: entry?.recordedAt ?? entry?.output?.createdAt ?? null,
    summary: hook?.summary ?? entry?.output?.bodyPreview ?? null,
    detail: hook?.cue ?? entry?.output?.bodyPreview ?? null,
    targetHandle: hook?.targetHandle ?? entry?.output?.targetGatewayHandle ?? null,
    targetGatewayId: hook?.targetGatewayId ?? entry?.output?.targetGatewayId ?? null,
    exposure: entry?.lane === 'public_expression' ? 'public' : 'private',
    triggerKind: hook?.kind ?? null,
    sourceKind: entry?.origin ?? 'life_loop_writeback',
    speakerRole: 'self_authored',
  });
}

function buildCarryForwardHooks({ writeBackSource, registry }) {
  const topicHooks = [];
  const relationshipHooks = [];
  const openLoops = [];
  const sourceWarnings = Array.isArray(writeBackSource?.warnings) ? writeBackSource.warnings : [];

  for (const entry of Array.isArray(writeBackSource?.entries) ? writeBackSource.entries : []) {
    const hooks = Array.isArray(entry?.dailyIntent?.newUnresolvedHooks) ? entry.dailyIntent.newUnresolvedHooks : [];

    if (entry?.lane === 'public_expression') {
      const publicHook = hooks.find((item) => item?.lane === 'public_reply' || item?.lane === 'public_expression');
      if (!publicHook) {
        continue;
      }
      const sourceRefId = buildWriteBackSourceRef({
        registry,
        entry,
        hook: publicHook,
        key: `writeback:${entry.id ?? publicHook.id ?? 'public'}`,
      });
      topicHooks.push({
        id: `topic-writeback-${entry.output?.actionId ?? entry.id ?? topicHooks.length + 1}`,
        lane: publicHook.lane ?? 'public_reply',
        freshness: 'recent_writeback',
        exposure: 'public',
        targetHandle: publicHook.targetHandle ?? entry?.output?.targetGatewayHandle ?? null,
        targetGatewayId: publicHook.targetGatewayId ?? entry?.output?.targetGatewayId ?? null,
        summary:
          publicHook.summary ??
          (entry?.output?.mode === 'reply'
            ? `A recent self-authored public reply still leaves a callback seam${entry?.output?.targetGatewayHandle ? ` with ${entry.output.targetGatewayHandle}` : ''}.`
            : 'A recent self-authored public line may still support one more observer-safe callback.'),
        cue: publicHook.cue ?? entry?.output?.bodyPreview ?? '',
        rationale: 'Recent write-back preserved a fresh public callback seam from the last authored public move.',
        sourceRefIds: [sourceRefId],
      });
      openLoops.push({
        id: `open-writeback-${entry.output?.actionId ?? entry.id ?? openLoops.length + 1}`,
        lane: publicHook.lane ?? 'public_reply',
        targetHandle: publicHook.targetHandle ?? entry?.output?.targetGatewayHandle ?? null,
        targetGatewayId: publicHook.targetGatewayId ?? entry?.output?.targetGatewayId ?? null,
        summary:
          publicHook.summary ??
          (entry?.output?.mode === 'reply'
            ? 'A recent self-authored public reply may still invite one more visible turn.'
            : 'A recent self-authored public line may still invite a fresh callback.'),
        cue: publicHook.cue ?? entry?.output?.bodyPreview ?? '',
        rationale: 'Self-authored public motion should remain eligible as a short-lived callback seam across day boundaries.',
        sourceRefIds: [sourceRefId],
      });
      continue;
    }

    if (entry?.lane !== 'direct_message') {
      continue;
    }

    const directHook = hooks.find((item) => item?.lane === 'dm');
    if (!directHook) {
      continue;
    }
    const sourceRefId = buildWriteBackSourceRef({
      registry,
      entry,
      hook: directHook,
      key: `writeback:${entry.id ?? directHook.id ?? 'dm'}`,
    });
    relationshipHooks.push({
      id: `relationship-writeback-${entry.output?.actionId ?? entry.id ?? relationshipHooks.length + 1}`,
      lane: 'dm',
      targetHandle: directHook.targetHandle ?? entry?.output?.targetGatewayHandle ?? null,
      targetGatewayId: directHook.targetGatewayId ?? entry?.output?.targetGatewayId ?? null,
      conversationId: directHook.conversationId ?? entry?.output?.conversationId ?? null,
      summary:
        directHook.summary ??
        `A recent self-authored DM still leaves a callback seam${entry?.output?.targetGatewayHandle ? ` with ${entry.output.targetGatewayHandle}` : ''}.`,
      cue: directHook.cue ?? entry?.output?.bodyPreview ?? '',
      rationale: 'Recent write-back preserved a private callback seam from the last authored DM move.',
      sourceRefIds: [sourceRefId],
    });
    openLoops.push({
      id: `open-writeback-${entry.output?.actionId ?? entry.id ?? openLoops.length + 1}`,
      lane: 'dm',
      targetHandle: directHook.targetHandle ?? entry?.output?.targetGatewayHandle ?? null,
      targetGatewayId: directHook.targetGatewayId ?? entry?.output?.targetGatewayId ?? null,
      conversationId: directHook.conversationId ?? entry?.output?.conversationId ?? null,
      summary:
        directHook.summary ??
        `A recent self-authored DM may still invite one more private callback${entry?.output?.targetGatewayHandle ? ` with ${entry.output.targetGatewayHandle}` : ''}.`,
      cue: directHook.cue ?? entry?.output?.bodyPreview ?? '',
      rationale: 'Self-authored DM motion should remain eligible as a short-lived callback seam across day boundaries.',
      sourceRefIds: [sourceRefId],
    });
  }

  return {
    topicHooks,
    relationshipHooks,
    openLoops,
    warnings: sourceWarnings,
  };
}

function buildTopicHooks({ diarySummary, registry, carryForward = null }) {
  const hooks = [];
  const viewerHandle = diarySummary?.visibleLayer?.viewer?.handle ?? null;
  const publicThreads = Array.isArray(diarySummary?.localSynthesisLayer?.publicContinuity)
    ? diarySummary.localSynthesisLayer.publicContinuity
    : [];

  for (const [index, item] of publicThreads.entries()) {
    if (hooks.length >= DEFAULT_TOP_HOOK_LIMIT) {
      break;
    }
    const refId = registry.ensureRef(`topic:public:${index}`, {
      layer: 'local_synthesis',
      kind: 'public_continuity',
      summary: item.summary,
      detail: item.latestLine,
      targetHandle: item.rootSpeaker,
      exposure: 'public',
      speakerRole: isSelfSpeaker(item.latestSpeaker, viewerHandle) ? 'self_latest' : 'other_latest',
    });
    hooks.push({
      id: `topic-public-${index + 1}`,
      lane: isSelfSpeaker(item.latestSpeaker, viewerHandle) ? 'public_expression' : 'public_reply',
      freshness: 'same_day',
      exposure: 'public',
      targetHandle: normalizeSpeakerLabel(item.rootSpeaker),
      summary: `Public thread still carries continuity around ${normalizeSpeakerLabel(item.rootSpeaker)}.`,
      cue: item.latestLine,
      rationale: 'A mirrored public thread survived the day and can still take one more natural turn.',
      sourceRefIds: [refId],
    });
  }

  for (const item of Array.isArray(carryForward?.topicHooks) ? carryForward.topicHooks : []) {
    if (hooks.length >= DEFAULT_TOP_HOOK_LIMIT) {
      break;
    }
    if (hasCarryForwardTarget(hooks, item)) {
      continue;
    }
    hooks.push(item);
  }

  if (hooks.length < DEFAULT_TOP_HOOK_LIMIT) {
    const currentLabel = diarySummary?.visibleLayer?.current?.label ?? null;
    const environmentSummary = diarySummary?.visibleLayer?.environment?.summary ?? null;
    if (currentLabel || environmentSummary) {
      const refId = registry.ensureRef('topic:ambient', {
        layer: 'visible',
        kind: 'ambient',
        summary: currentLabel ? `Current ${currentLabel}` : environmentSummary,
        detail: environmentSummary ?? null,
        exposure: 'public',
      });
      hooks.push({
        id: 'topic-ambient-1',
        lane: 'public_expression',
        freshness: 'same_day',
        exposure: 'public',
        targetHandle: null,
        summary: 'The ambient current/environment can support one light public line.',
        cue: [currentLabel, environmentSummary].filter(Boolean).join(' | '),
        rationale: 'Current and environment snapshots are visible same-day context rather than private memory.',
        sourceRefIds: [refId],
      });
    }
  }

  const communityNotes = Array.isArray(diarySummary?.privateCommunityLayer?.items)
    ? diarySummary.privateCommunityLayer.items
    : [];
  for (const [index, note] of communityNotes.entries()) {
    if (hooks.length >= DEFAULT_TOP_HOOK_LIMIT) {
      break;
    }
    if (note?.mentionPolicy === 'private_only') {
      continue;
    }
    const refId = registry.ensureRef(`topic:community:${index}`, {
      layer: 'private_community',
      kind: 'community_note',
      createdAt: note.createdAt ?? null,
      summary: note.summary ?? note.cue ?? null,
      detail: note.cue ?? null,
      exposure: note.mentionPolicy === 'public_ok' ? 'public_ok' : 'paraphrase_only',
      mentionPolicy: note.mentionPolicy ?? null,
      sourceKind: note.sourceKind ?? null,
    });
    hooks.push({
      id: `topic-community-${index + 1}`,
      lane: note?.mentionPolicy === 'public_ok' ? 'public_expression' : 'dm',
      freshness: 'same_day',
      exposure: note?.mentionPolicy === 'public_ok' ? 'public_ok' : 'paraphrase_only',
      targetHandle: null,
      targetGatewayId: null,
      summary: `${note?.npcId ?? 'A private source'} left a same-day cue worth carrying forward carefully.`,
      cue: note?.cue ?? note?.summary ?? '',
      rationale:
        note?.mentionPolicy === 'public_ok'
          ? 'This note can surface more directly later, but it still remains a private-memory input rather than public fact.'
          : 'This note can shape private tone or paraphrased callback, but should not be quoted outright.',
      sourceRefIds: [refId],
    });
  }

  return hooks;
}

function buildRelationshipHooks({ diarySummary, registry, carryForward = null }) {
  const hooks = [];
  const viewerHandle = diarySummary?.visibleLayer?.viewer?.handle ?? null;
  const directThreads = Array.isArray(diarySummary?.localSynthesisLayer?.directContinuity)
    ? diarySummary.localSynthesisLayer.directContinuity
    : [];
  for (const [index, item] of directThreads.entries()) {
    if (hooks.length >= DEFAULT_TOP_HOOK_LIMIT) {
      break;
    }
    const refId = registry.ensureRef(`relationship:direct:${index}`, {
      layer: 'local_synthesis',
      kind: 'direct_continuity',
      summary: item.summary,
      detail: item.latestLine,
      targetHandle: item.peerHandle,
      exposure: 'private',
      speakerRole: isSelfSpeaker(item.latestSpeaker, viewerHandle) ? 'self_latest' : 'other_latest',
    });
    hooks.push({
      id: `relationship-direct-${index + 1}`,
      lane: 'dm',
      targetHandle: formatHandle(item.peerHandle),
      targetGatewayId: null,
      summary: `DM continuity with ${formatHandle(item.peerHandle)} still feels active.`,
      cue: item.latestLine,
      rationale:
        isSelfSpeaker(item.latestSpeaker, viewerHandle)
          ? 'The thread still ends on a self-authored line, so follow-up can stay optional rather than urgent.'
          : 'The peer currently holds the latest mirrored DM line, so follow-up pressure is stronger.',
      sourceRefIds: [refId],
    });
  }

  const scenes = Array.isArray(diarySummary?.privateSceneLayer?.items) ? diarySummary.privateSceneLayer.items : [];
  for (const [index, item] of scenes.entries()) {
    if (hooks.length >= DEFAULT_TOP_HOOK_LIMIT) {
      break;
    }
    const peerGatewayId = item?.trigger?.peerGatewayId ?? null;
    const conversationId = item?.trigger?.conversationId ?? null;
    if (!peerGatewayId && !conversationId) {
      continue;
    }
    const refId = registry.ensureRef(`relationship:scene:${index}`, {
      layer: 'private_scene',
      kind: item?.type ?? 'scene',
      createdAt: item?.createdAt ?? null,
      summary: item?.summary ?? null,
      detail: item?.trigger?.reason ?? item?.trigger?.cue ?? null,
      targetGatewayId: peerGatewayId,
      exposure: 'gateway_private',
      triggerKind: item?.trigger?.kind ?? null,
    });
    hooks.push({
      id: `relationship-scene-${index + 1}`,
      lane: conversationId ? 'dm' : 'relationship',
      targetGatewayId: peerGatewayId,
      targetHandle: null,
      conversationId,
      summary: 'A gateway-private scene kept a relationship afterimage alive.',
      cue: item?.summary ?? item?.trigger?.reason ?? '',
      rationale: 'Event-driven private scene triggers can mark a relationship seam worth revisiting later.',
      sourceRefIds: [refId],
    });
  }

  for (const item of Array.isArray(carryForward?.relationshipHooks) ? carryForward.relationshipHooks : []) {
    if (hooks.length >= DEFAULT_TOP_HOOK_LIMIT) {
      break;
    }
    if (hasCarryForwardTarget(hooks, item)) {
      continue;
    }
    hooks.push(item);
  }

  return hooks;
}

function buildOpenLoops({ diarySummary, registry, carryForward = null }) {
  const loops = [];
  const viewerHandle = diarySummary?.visibleLayer?.viewer?.handle ?? null;
  const directThreads = Array.isArray(diarySummary?.localSynthesisLayer?.directContinuity)
    ? diarySummary.localSynthesisLayer.directContinuity
    : [];
  for (const [index, item] of directThreads.entries()) {
    if (loops.length >= DEFAULT_OPEN_LOOP_LIMIT) {
      break;
    }
    if (isSelfSpeaker(item.latestSpeaker, viewerHandle)) {
      continue;
    }
    const refId = registry.ensureRef(`loop:direct:${index}`, {
      layer: 'local_synthesis',
      kind: 'direct_continuity',
      summary: item.summary,
      detail: item.latestLine,
      targetHandle: item.peerHandle,
      exposure: 'private',
      speakerRole: 'other_latest',
    });
    loops.push({
      id: `open-direct-${index + 1}`,
      lane: 'dm',
      targetHandle: formatHandle(item.peerHandle),
      targetGatewayId: null,
      conversationId: null,
      summary: `${formatHandle(item.peerHandle)} currently holds the latest mirrored DM line.`,
      cue: item.latestLine,
      rationale: 'This conversation still reads as unresolved enough for a future DM callback.',
      sourceRefIds: [refId],
    });
  }

  const publicThreads = Array.isArray(diarySummary?.localSynthesisLayer?.publicContinuity)
    ? diarySummary.localSynthesisLayer.publicContinuity
    : [];
  for (const [index, item] of publicThreads.entries()) {
    if (loops.length >= DEFAULT_OPEN_LOOP_LIMIT) {
      break;
    }
    if (isSelfSpeaker(item.latestSpeaker, viewerHandle)) {
      continue;
    }
    const refId = registry.ensureRef(`loop:public:${index}`, {
      layer: 'local_synthesis',
      kind: 'public_continuity',
      summary: item.summary,
      detail: item.latestLine,
      targetHandle: item.rootSpeaker,
      exposure: 'public',
      speakerRole: 'other_latest',
    });
    loops.push({
      id: `open-public-${index + 1}`,
      lane: 'public_reply',
      targetHandle: normalizeSpeakerLabel(item.rootSpeaker),
      targetGatewayId: null,
      summary: `A public thread rooted by ${normalizeSpeakerLabel(item.rootSpeaker)} still reads as open.`,
      cue: item.latestLine,
      rationale: 'Another speaker currently holds the latest visible public line in a same-day thread.',
      sourceRefIds: [refId],
    });
  }

  const scenes = Array.isArray(diarySummary?.privateSceneLayer?.items) ? diarySummary.privateSceneLayer.items : [];
  for (const [index, item] of scenes.entries()) {
    if (loops.length >= DEFAULT_OPEN_LOOP_LIMIT) {
      break;
    }
    const triggerKind = item?.trigger?.kind ?? '';
    if (!triggerKind.startsWith('message.') && triggerKind !== 'friend_request.accepted') {
      continue;
    }
    const refId = registry.ensureRef(`loop:scene:${index}`, {
      layer: 'private_scene',
      kind: item?.type ?? 'scene',
      createdAt: item?.createdAt ?? null,
      summary: item?.summary ?? item?.trigger?.reason ?? null,
      detail: item?.trigger?.cue ?? item?.trigger?.reason ?? null,
      targetGatewayId: item?.trigger?.peerGatewayId ?? null,
      exposure: 'gateway_private',
      triggerKind,
    });
    loops.push({
      id: `open-scene-${index + 1}`,
      lane: item?.trigger?.conversationId ? 'dm' : 'relationship',
      targetHandle: null,
      targetGatewayId: item?.trigger?.peerGatewayId ?? null,
      conversationId: item?.trigger?.conversationId ?? null,
      triggerKind,
      summary: 'A private scene trigger suggests unfinished relational aftereffect.',
      cue: item?.summary ?? item?.trigger?.reason ?? '',
      rationale: 'Event-driven scene triggers should stay available as open-loop evidence even before write-back exists.',
      sourceRefIds: [refId],
    });
  }

  for (const item of Array.isArray(carryForward?.openLoops) ? carryForward.openLoops : []) {
    if (loops.length >= DEFAULT_OPEN_LOOP_LIMIT) {
      break;
    }
    if (hasCarryForwardTarget(loops, item)) {
      continue;
    }
    loops.push(item);
  }

  return loops;
}

function buildAvoidance({ diarySummary, registry }) {
  const items = [];
  const notes = Array.isArray(diarySummary?.privateCommunityLayer?.items) ? diarySummary.privateCommunityLayer.items : [];
  for (const [index, note] of notes.entries()) {
    if (note?.mentionPolicy !== 'private_only') {
      continue;
    }
    const refId = registry.ensureRef(`avoid:community:${index}`, {
      layer: 'private_community',
      kind: 'community_note',
      createdAt: note.createdAt ?? null,
      summary: note.summary ?? note.cue ?? null,
      detail: note.handling ?? null,
      exposure: 'private_only',
      mentionPolicy: note.mentionPolicy ?? null,
      sourceKind: note.sourceKind ?? null,
    });
    items.push({
      id: `avoid-community-${index + 1}`,
      scope: 'public',
      kind: 'privacy',
      summary: `Do not upgrade ${note?.npcId ?? 'a private whisper'} into public fact.`,
      rationale: note?.handling ?? 'This memory is private-only.',
      sourceRefIds: [refId],
    });
  }

  const warnings = [...(Array.isArray(diarySummary?.warnings) ? diarySummary.warnings : [])];
  const caveats = [...(Array.isArray(diarySummary?.diaryCaveats) ? diarySummary.diaryCaveats : [])];
  if (warnings.length > 0 || caveats.length > 0) {
    const refId = registry.ensureRef('avoid:evidence', {
      layer: 'local_synthesis',
      kind: 'caveat',
      summary: warnings[0] ?? caveats[0] ?? null,
      detail: previewText([...warnings, ...caveats].join(' | '), 220) || null,
      exposure: 'local_only',
    });
    items.push({
      id: 'avoid-evidence-1',
      scope: 'global',
      kind: 'thin_evidence',
      summary: 'Do not over-claim beyond the surviving same-day evidence.',
      rationale: warnings[0] ?? caveats[0] ?? 'Some supporting layers are partial or best-effort.',
      sourceRefIds: [refId],
    });
  }

  return items;
}

function buildEnergyProfile({ diarySummary, dominantModes, topicHooks, relationshipHooks, avoidance, registry }) {
  const counts = diarySummary?.visibleLayer?.counts ?? {};
  const totalSignals =
    (Number.isFinite(counts.total) ? counts.total : 0) +
    (Array.isArray(diarySummary?.privateSceneLayer?.items) ? diarySummary.privateSceneLayer.items.length : 0) +
    (Array.isArray(diarySummary?.privateCommunityLayer?.items) ? diarySummary.privateCommunityLayer.items.length : 0) +
    (Array.isArray(diarySummary?.localSynthesisLayer?.directContinuity)
      ? diarySummary.localSynthesisLayer.directContinuity.length
      : 0) +
    (Array.isArray(diarySummary?.localSynthesisLayer?.publicContinuity)
      ? diarySummary.localSynthesisLayer.publicContinuity.length
      : 0);

  const publicScore = dominantModes.find((item) => item.mode === 'public')?.score ?? 0;
  const directScore = dominantModes.find((item) => item.mode === 'direct')?.score ?? 0;
  const guardedScore = dominantModes.find((item) => item.mode === 'guarded')?.score ?? 0;

  const level = totalSignals <= 2 ? 'quiet' : totalSignals <= 7 ? 'steady' : 'active';
  const posture =
    guardedScore >= 4 && publicScore <= directScore
      ? 'observe-first'
      : publicScore >= directScore + 2 && publicScore >= 3
        ? 'reply-ready'
        : directScore >= publicScore + 2 && directScore >= 3
          ? 'dm-led'
          : topicHooks.length > 0 && relationshipHooks.length > 0
            ? 'mixed'
            : 'observe-first';

  const refIds = [];
  const firstTopic = topicHooks[0];
  if (firstTopic) {
    refIds.push(...firstTopic.sourceRefIds);
  }
  const firstRelationship = relationshipHooks[0];
  if (firstRelationship) {
    refIds.push(...firstRelationship.sourceRefIds);
  }
  if (avoidance[0]) {
    refIds.push(...avoidance[0].sourceRefIds);
  }
  if (refIds.length === 0 && diarySummary?.visibleLayer?.current?.label) {
    refIds.push(
      registry.ensureRef('energy:ambient', {
        layer: 'visible',
        kind: 'ambient',
        summary: diarySummary.visibleLayer.current.label,
        detail: diarySummary?.visibleLayer?.environment?.summary ?? null,
        exposure: 'public',
      }),
    );
  }

  const summary =
    level === 'quiet'
      ? 'Keep today low-pressure; wait for a clean prompt instead of forcing output.'
      : posture === 'reply-ready'
        ? 'There is enough same-day public footing to prefer reply-led activity.'
        : posture === 'dm-led'
          ? 'Relationship continuity is stronger than public momentum, so DM-led activity makes more sense.'
          : posture === 'mixed'
            ? 'Both public and relationship hooks are alive, so activity can stay mixed without forcing either lane.'
            : 'The safer read is observe-first rather than high-initiative behavior.';

  const rationale = uniqueValues([
    `Total same-day signal count: ${totalSignals}.`,
    topicHooks.length > 0 ? `${topicHooks.length} topic hook(s) survived for outward behavior.` : null,
    relationshipHooks.length > 0 ? `${relationshipHooks.length} relationship hook(s) survived for DM-sensitive behavior.` : null,
    avoidance.length > 0 ? `${avoidance.length} avoidance rule(s) are active.` : null,
  ]);

  return {
    level,
    posture,
    summary,
    rationale,
    sourceRefIds: uniqueValues(refIds),
  };
}

function buildDailyIntent({ diarySummary, diarySource, writeBackSource = null }) {
  const viewerHandle = diarySummary?.visibleLayer?.viewer?.handle ?? null;
  const registry = createSourceRefRegistry(viewerHandle);
  const carryForward = buildCarryForwardHooks({
    writeBackSource,
    registry,
  });
  const dominantModes = buildModeEntries({
    diarySummary,
    registry,
  });
  const topicHooks = buildTopicHooks({
    diarySummary,
    registry,
    carryForward,
  });
  const relationshipHooks = buildRelationshipHooks({
    diarySummary,
    registry,
    carryForward,
  });
  const openLoops = buildOpenLoops({
    diarySummary,
    registry,
    carryForward,
  });
  const avoidance = buildAvoidance({
    diarySummary,
    registry,
  });
  const energyProfile = buildEnergyProfile({
    diarySummary,
    dominantModes,
    topicHooks,
    relationshipHooks,
    avoidance,
    registry,
  });

  return {
    generatedAt: new Date().toISOString(),
    targetDate: diarySummary?.targetDate ?? null,
    timeZone: diarySummary?.timeZone ?? 'UTC',
    mode: diarySummary?.mode ?? null,
    viewer: diarySummary?.visibleLayer?.viewer ?? null,
    aqua: diarySummary?.visibleLayer?.aqua ?? null,
    source: {
      seaDiaryContext: {
        status: diarySource?.status ?? 'unknown',
        jsonPath: diarySource?.artifactPaths?.jsonPath ?? null,
        markdownPath: diarySource?.artifactPaths?.markdownPath ?? null,
        generatedAt: diarySummary?.generatedAt ?? null,
      },
      digest: diarySummary?.source?.digest ?? null,
      memorySynthesis: diarySummary?.source?.memorySynthesis ?? null,
      scenes: diarySummary?.source?.scenes ?? null,
      communityMemory: diarySummary?.source?.communityMemory ?? null,
      writeBack: summarizeWriteBackSource(writeBackSource),
    },
    dominantModes,
    topicHooks,
    relationshipHooks,
    openLoops,
    avoidance,
    energyProfile,
    sourceRefs: registry.refs,
    caveats: Array.isArray(diarySummary?.diaryCaveats) ? diarySummary.diaryCaveats : [],
    warnings: uniqueValues([...(Array.isArray(diarySummary?.warnings) ? diarySummary.warnings : []), ...carryForward.warnings]),
  };
}

function renderList(items, renderItem, fallback) {
  return items.length ? items.map(renderItem) : [`- ${fallback}`];
}

function renderDailyIntentMarkdown(summary) {
  const renderMode = (item) =>
    `- ${item.mode} (score ${item.score})${item.sourceRefIds.length ? ` [${item.sourceRefIds.join(', ')}]` : ''}: ${item.summary}`;
  const renderHook = (item) =>
    [
      `- ${item.id} | ${item.lane} | ${item.exposure ?? 'n/a'}`,
      `  summary: ${item.summary}`,
      `  cue: ${item.cue || '(no cue)'}`,
      `  rationale: ${item.rationale}`,
      `  refs: ${item.sourceRefIds.join(', ') || 'none'}`,
    ].join('\n');
  const renderRelationship = (item) =>
    [
      `- ${item.id} | ${item.lane}${item.targetHandle ? ` | ${item.targetHandle}` : ''}`,
      `  summary: ${item.summary}`,
      `  cue: ${item.cue || '(no cue)'}`,
      `  rationale: ${item.rationale}`,
      `  refs: ${item.sourceRefIds.join(', ') || 'none'}`,
    ].join('\n');
  const renderAvoidance = (item) =>
    `- ${item.id} | ${item.scope} | ${item.kind}: ${item.summary} [${item.sourceRefIds.join(', ') || 'none'}]`;
  const renderSourceRef = (item) =>
    `- ${item.id} | ${item.layer} | ${item.kind}: ${item.summary ?? '(no summary)'}${item.detail ? ` | ${item.detail}` : ''}`;

  return [
    '# Aqua Daily Intent',
    `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
    `- Diary date: ${summary.targetDate} (${summary.timeZone})`,
    `- Mode: ${summary.mode ?? 'unknown'}`,
    `- Sea diary source: ${summary.source?.seaDiaryContext?.status ?? 'unknown'}`,
    `- Write-back carry-forward: ${summary.source?.writeBack?.status ?? 'missing'}`,
    `- Viewer: ${summary.viewer?.displayName ?? 'unknown'} (${formatHandle(summary.viewer?.handle)})`,
    summary.aqua?.displayName ? `- Aqua: ${summary.aqua.displayName}` : null,
    '',
    '## Dominant Modes',
    ...renderList(summary.dominantModes, renderMode, 'None'),
    '',
    '## Topic Hooks',
    ...renderList(summary.topicHooks, renderHook, 'No same-day topic hook survived.'),
    '',
    '## Relationship Hooks',
    ...renderList(summary.relationshipHooks, renderRelationship, 'No same-day relationship hook survived.'),
    '',
    '## Open Loops',
    ...renderList(summary.openLoops, renderRelationship, 'No same-day open loop survived.'),
    '',
    '## Avoidance',
    ...renderList(summary.avoidance, renderAvoidance, 'No additional avoidance rule beyond the normal boundary.'),
    '',
    '## Energy Profile',
    `- Level: ${summary.energyProfile.level}`,
    `- Posture: ${summary.energyProfile.posture}`,
    `- Summary: ${summary.energyProfile.summary}`,
    `- Rationale: ${summary.energyProfile.rationale.join(' ') || 'None'}`,
    `- Refs: ${summary.energyProfile.sourceRefIds.join(', ') || 'none'}`,
    '',
    '## Source Refs',
    ...renderList(summary.sourceRefs, renderSourceRef, 'None'),
    '',
    '## Caveats',
    ...renderList(summary.caveats, (item) => `- ${item}`, 'None'),
    summary.warnings.length ? '' : null,
    summary.warnings.length ? '## Warnings' : null,
    ...renderList(summary.warnings, (item) => `- ${item}`, 'None'),
  ]
    .filter(Boolean)
    .join('\n');
}

export async function generateDailyIntent(
  options = {},
  {
    generateSeaDiaryContextFn = generateSeaDiaryContext,
    loadHostedConfigFn,
    requestJsonFn,
  } = {},
) {
  const normalizedOptions = normalizeOptions(options);
  const [diarySource, writeBackSource] = await Promise.all([
    loadSeaDiaryContextSummary(normalizedOptions, {
      generateSeaDiaryContextFn,
      loadHostedConfigFn,
      requestJsonFn,
    }),
    loadWriteBackCarryForward(normalizedOptions),
  ]);
  const summary = buildDailyIntent({
    diarySummary: diarySource.summary,
    diarySource,
    writeBackSource,
  });
  const markdown = renderDailyIntentMarkdown(summary);
  let artifactPaths = null;

  if (normalizedOptions.writeArtifact) {
    artifactPaths = await writeDailyIntentArtifacts({
      summary,
      markdown,
      paths: diarySource.paths,
      targetDate: summary.targetDate ?? normalizedOptions.date,
      artifactRoot: normalizedOptions.artifactRoot,
    });
  }

  return {
    summary,
    markdown,
    artifactPaths,
    diarySource,
    paths: diarySource.paths,
    options: normalizedOptions,
  };
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const result = await generateDailyIntent(options);

  if (result.options.format === 'json') {
    console.log(
      JSON.stringify(
        result.artifactPaths
          ? {
              ...result.summary,
              artifacts: {
                dailyIntent: result.artifactPaths,
              },
            }
          : result.summary,
        null,
        2,
      ),
    );
    return;
  }

  console.log(result.markdown);
}

export {
  buildDailyIntent,
  parseOptions,
  renderDailyIntentMarkdown,
  resolveDailyIntentArtifactPaths,
  writeDailyIntentArtifacts,
};

if (!process.argv.includes('--test') && process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
