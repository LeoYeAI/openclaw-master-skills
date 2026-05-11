#!/usr/bin/env node

import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

import { resolveMirrorPaths, writeJsonFile } from './aqua-mirror-common.mjs';
import {
  generateDailyDigest,
  resolveDiaryDigestArtifactPaths,
  summarizeContinuityCounts,
} from './aqua-mirror-daily-digest.mjs';
import { formatTimestamp, parseArgValue, parsePositiveInt, resolveWorkspaceRoot } from './hosted-aqua-common.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);
const VALID_EXPECT_MODES = new Set(['any', 'auto', 'local', 'hosted']);

function printHelp() {
  console.log(`Usage: aqua-mirror-memory-synthesis.mjs [options]

Options:
  --workspace-root <path>   OpenClaw workspace root
  --config-path <path>      Hosted Aqua config path, used when --expect-mode auto
  --mirror-dir <path>       Mirror root directory
  --state-file <path>       Mirror state file override
  --expect-mode <mode>      any|auto|hosted|local (default: any)
  --date <YYYY-MM-DD>       Local diary date in --timezone (default: today)
  --timezone <iana>         Local timezone for diary bucketing (default: current system timezone)
  --digest-root <path>      Override the diary-digests artifact directory
  --build-if-missing        Build the digest artifact first when it does not exist
  --max-events <n>          Max notable sea events when building a missing digest (default: 8)
  --write-artifact          Also persist JSON + Markdown synthesis artifacts for this date
  --artifact-root <path>    Override the default profile-scoped synthesis artifact directory
  --format <fmt>            json|markdown (default: markdown)
  --help                    Show this message
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

function buildDefaultOptions() {
  return {
    artifactRoot: null,
    buildIfMissing: false,
    configPath: process.env.AQUACLAW_HOSTED_CONFIG || null,
    date: null,
    digestRoot: null,
    expectMode: 'any',
    format: 'markdown',
    maxEvents: 8,
    mirrorDir: process.env.AQUACLAW_MIRROR_DIR || null,
    stateFile: process.env.AQUACLAW_MIRROR_STATE_FILE || null,
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
    writeArtifact: false,
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT || null,
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
    throw new Error('expect-mode must be one of: any, auto, local, hosted');
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
    if (arg.startsWith('--artifact-root')) {
      options.artifactRoot = parseArgValue(argv, index, arg, '--artifact-root').trim();
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
    if (arg.startsWith('--max-events')) {
      options.maxEvents = parsePositiveInt(parseArgValue(argv, index, arg, '--max-events'), '--max-events');
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

function normalizeHandleLabel(value, fallback = 'unknown speaker') {
  const normalized = String(value ?? '').trim();
  return normalized || fallback;
}

function formatPeerHandle(value) {
  const handle = String(value ?? '')
    .trim()
    .replace(/^@+/, '');
  return handle ? `@${handle}` : '@unknown';
}

function ensureSentence(value, fallback = 'no readable body') {
  const normalized = String(value ?? '').replace(/\s+/g, ' ').trim();
  if (!normalized) {
    return fallback;
  }
  return /[.!?。！？]$/.test(normalized) ? normalized : `${normalized}.`;
}

function isSelfSpeakerLabel(label, viewerHandleLabel) {
  const normalized = String(label ?? '').trim().toLowerCase();
  if (!normalized) {
    return false;
  }
  if (normalized === 'self') {
    return true;
  }
  const viewer = String(viewerHandleLabel ?? '').trim().toLowerCase();
  return viewer ? normalized.startsWith(viewer) : false;
}

function uniqueLines(items) {
  return [...new Set(items.filter((item) => typeof item === 'string' && item.trim()).map((item) => item.trim()))];
}

function resolveContinuityCounts(digestSummary) {
  const fallback = summarizeContinuityCounts({
    conversationItems: Array.isArray(digestSummary?.conversationItems) ? digestSummary.conversationItems : [],
    publicThreadItems: Array.isArray(digestSummary?.publicThreadItems) ? digestSummary.publicThreadItems : [],
  });
  const continuityCounts = digestSummary?.continuityCounts ?? {};
  return {
    directThreads: Number.isFinite(continuityCounts?.directThreads) ? continuityCounts.directThreads : fallback.directThreads,
    directLines: Number.isFinite(continuityCounts?.directLines) ? continuityCounts.directLines : fallback.directLines,
    publicThreads: Number.isFinite(continuityCounts?.publicThreads) ? continuityCounts.publicThreads : fallback.publicThreads,
    publicLines: Number.isFinite(continuityCounts?.publicLines) ? continuityCounts.publicLines : fallback.publicLines,
  };
}

function buildActivitySummary(counts, continuityCounts) {
  if (!counts || counts.total < 1) {
    if ((continuityCounts?.directThreads ?? 0) > 0 || (continuityCounts?.publicThreads ?? 0) > 0) {
      return `No visible sea events were mirrored for this date, but ${continuityCounts.directThreads} direct thread${
        continuityCounts.directThreads === 1 ? '' : 's'
      } and ${continuityCounts.publicThreads} public thread${continuityCounts.publicThreads === 1 ? '' : 's'} still carried mirrored continuity.`;
    }
    return 'No visible sea events were mirrored for this date.';
  }

  const parts = [`${counts.total} visible sea event${counts.total === 1 ? '' : 's'}`];
  if (counts.worldChanges > 0) {
    parts.push(`${counts.worldChanges} world change${counts.worldChanges === 1 ? '' : 's'}`);
  }
  if (counts.directMessages > 0) {
    parts.push(`${counts.directMessages} DM move${counts.directMessages === 1 ? '' : 's'}`);
  }
  if (counts.publicExpressions > 0) {
    parts.push(`${counts.publicExpressions} public expression${counts.publicExpressions === 1 ? '' : 's'}`);
  }
  if (counts.relationshipMoves > 0) {
    parts.push(`${counts.relationshipMoves} relationship move${counts.relationshipMoves === 1 ? '' : 's'}`);
  }
  if (counts.encounters > 0) {
    parts.push(`${counts.encounters} encounter trace${counts.encounters === 1 ? '' : 's'}`);
  }
  if ((continuityCounts?.directThreads ?? 0) > 0) {
    parts.push(`${continuityCounts.directThreads} active DM thread${continuityCounts.directThreads === 1 ? '' : 's'}`);
  }
  if ((continuityCounts?.publicThreads ?? 0) > 0) {
    parts.push(`${continuityCounts.publicThreads} active public thread${continuityCounts.publicThreads === 1 ? '' : 's'}`);
  }
  return parts.join('; ');
}

function buildActivityBalance(counts, continuityCounts) {
  const directSignal = Math.max(counts?.directMessages ?? 0, continuityCounts?.directThreads ?? 0);
  const publicSignal = Math.max(counts?.publicExpressions ?? 0, continuityCounts?.publicThreads ?? 0);
  if (!counts || counts.total < 1) {
    if (directSignal > 0 || publicSignal > 0) {
      return 'Visible sea-event motion stayed thin, but mirrored thread continuity still survived.';
    }
    return 'The mirror stayed thin, so continuity should remain modest.';
  }
  if (directSignal > publicSignal) {
    return 'Direct-thread motion outweighed public surface speech.';
  }
  if (publicSignal > directSignal) {
    return 'Public surface speech outweighed direct-thread motion.';
  }
  if (publicSignal > 0 && directSignal > 0) {
    return 'Direct-thread and public-surface motion were both present.';
  }
  if (counts.worldChanges > 0) {
    return 'Most visible motion came from current or environment shifts.';
  }
  return 'Visible motion stayed narrow and should be narrated carefully.';
}

function buildSelfMotion(digestSummary) {
  const viewerHandleLabel = digestSummary?.viewer?.handle ? formatPeerHandle(digestSummary.viewer.handle) : null;
  const lines = [];

  for (const item of Array.isArray(digestSummary?.conversationItems) ? digestSummary.conversationItems : []) {
    if (String(item?.latestSpeaker ?? '').trim().toLowerCase() !== 'self') {
      continue;
    }
    lines.push(
      `DM with ${formatPeerHandle(item?.peerHandle)} currently ends on a self line: ${ensureSentence(item?.latestBody)}`
    );
  }

  for (const item of Array.isArray(digestSummary?.publicThreadItems) ? digestSummary.publicThreadItems : []) {
    if (!isSelfSpeakerLabel(item?.latestSpeaker, viewerHandleLabel)) {
      continue;
    }
    lines.push(`Public surface latest line stays self-authored: ${ensureSentence(item?.latestPreview)}`);
  }

  const unique = uniqueLines(lines);
  return unique.length ? unique : ['No clearly self-authored mirrored thread edge survives for this date.'];
}

function buildOtherVoices(digestSummary) {
  const viewerHandleLabel = digestSummary?.viewer?.handle ? formatPeerHandle(digestSummary.viewer.handle) : null;
  const lines = [];

  for (const item of Array.isArray(digestSummary?.conversationItems) ? digestSummary.conversationItems : []) {
    const peerLabel = formatPeerHandle(item?.peerHandle);
    lines.push(`${peerLabel} remains part of the direct continuity set.`);
    if (item?.latestSpeaker && !isSelfSpeakerLabel(item.latestSpeaker, viewerHandleLabel)) {
      lines.push(`${normalizeHandleLabel(item.latestSpeaker)} currently holds the latest mirrored DM line in the thread with ${peerLabel}.`);
    }
  }

  for (const item of Array.isArray(digestSummary?.publicThreadItems) ? digestSummary.publicThreadItems : []) {
    if (item?.rootSpeaker && !isSelfSpeakerLabel(item.rootSpeaker, viewerHandleLabel)) {
      lines.push(`${normalizeHandleLabel(item.rootSpeaker)} anchored a public thread root that still carries continuity.`);
    }
    if (
      item?.latestSpeaker &&
      !isSelfSpeakerLabel(item.latestSpeaker, viewerHandleLabel) &&
      normalizeHandleLabel(item.latestSpeaker) !== normalizeHandleLabel(item.rootSpeaker, '')
    ) {
      lines.push(`${normalizeHandleLabel(item.latestSpeaker)} currently holds the latest mirrored public line.`);
    }
  }

  const unique = uniqueLines(lines);
  return unique.length ? unique : ['No distinct other voices were recovered from mirrored thread artifacts for this date.'];
}

function buildDirectContinuity(digestSummary) {
  return (Array.isArray(digestSummary?.conversationItems) ? digestSummary.conversationItems : []).map((item) => ({
    peerHandle: String(item?.peerHandle ?? '').trim() || 'unknown',
    messageCount: Number.isFinite(item?.messageCount) ? item.messageCount : 0,
    latestSpeaker: normalizeHandleLabel(item?.latestSpeaker),
    latestLine: ensureSentence(item?.latestBody),
    summary: `${formatPeerHandle(item?.peerHandle)}: ${Number.isFinite(item?.messageCount) ? item.messageCount : 0} line${
      item?.messageCount === 1 ? '' : 's'
    }; latest speaker ${normalizeHandleLabel(item?.latestSpeaker)}; latest line ${ensureSentence(item?.latestBody)}`,
  }));
}

function buildPublicContinuity(digestSummary) {
  return (Array.isArray(digestSummary?.publicThreadItems) ? digestSummary.publicThreadItems : []).map((item) => ({
    rootSpeaker: normalizeHandleLabel(item?.rootSpeaker),
    latestSpeaker: normalizeHandleLabel(item?.latestSpeaker),
    expressionCount: Number.isFinite(item?.expressionCount) ? item.expressionCount : 0,
    rootLine: ensureSentence(item?.rootPreview, 'unknown speaker: no readable body'),
    latestLine: ensureSentence(item?.latestPreview || item?.rootPreview, 'unknown speaker: no readable body'),
    summary: `root ${normalizeHandleLabel(item?.rootSpeaker)}; latest ${normalizeHandleLabel(item?.latestSpeaker)}; ${
      Number.isFinite(item?.expressionCount) ? item.expressionCount : 0
    } line${item?.expressionCount === 1 ? '' : 's'}`,
  }));
}

function buildCaveats(digestSummary, selfMotion, continuityCounts) {
  const counts = digestSummary?.counts ?? {};
  const caveats = [];
  const hasSelfMotion = selfMotion.some((item) => !item.startsWith('No clearly self-authored'));

  if ((counts.total ?? 0) < 1) {
    caveats.push('Mirror is thin for this date; keep any diary or memory note minimal and explicit.');
  }
  if (!digestSummary?.mirror?.updatedAt) {
    caveats.push('Mirror freshness is unclear because updatedAt is missing.');
  }
  if ((counts.directMessages ?? 0) > 0 && !(Array.isArray(digestSummary?.conversationItems) && digestSummary.conversationItems.length)) {
    caveats.push('Sea events show DM motion, but no mirrored DM thread snapshot was available for continuity.');
  }
  if ((counts.publicExpressions ?? 0) > 0 && !(Array.isArray(digestSummary?.publicThreadItems) && digestSummary.publicThreadItems.length)) {
    caveats.push('Sea events show public speech, but no mirrored public-thread snapshot was available for speaker continuity.');
  }
  if ((counts.directMessages ?? 0) === 0 && (continuityCounts?.directThreads ?? 0) > 0) {
    caveats.push('DM continuity survived through mirrored thread state even though no same-day DM sea-event record was captured.');
  }
  if ((counts.publicExpressions ?? 0) === 0 && (continuityCounts?.publicThreads ?? 0) > 0) {
    caveats.push('Public continuity survived through mirrored thread state even though no same-day public-expression sea event was captured.');
  }
  if (!hasSelfMotion && (counts.total ?? 0) > 0) {
    caveats.push('Visible motion exists, but the latest mirrored thread edges are not clearly self-authored.');
  }
  if (!digestSummary?.current?.label && !digestSummary?.environment?.summary && (counts.worldChanges ?? 0) > 0) {
    caveats.push('World-change events were mirrored, but the latest current or environment snapshot is missing.');
  }

  return caveats.length ? caveats : ['No major continuity caveat beyond the normal local-mirror boundary.'];
}

export function buildMemorySynthesis({ digestSummary, digestSource }) {
  const counts = digestSummary?.counts ?? {
    total: 0,
    worldChanges: 0,
    directMessages: 0,
    publicExpressions: 0,
    encounters: 0,
    relationshipMoves: 0,
  };
  const selfMotion = buildSelfMotion(digestSummary);
  const directContinuity = buildDirectContinuity(digestSummary);
  const publicContinuity = buildPublicContinuity(digestSummary);
  const continuityCounts = resolveContinuityCounts(digestSummary);

  return {
    generatedAt: new Date().toISOString(),
    targetDate: digestSummary?.targetDate ?? null,
    timeZone: digestSummary?.timeZone ?? 'UTC',
    mode: digestSummary?.mode ?? null,
    viewer: digestSummary?.viewer ?? null,
    aqua: digestSummary?.aqua ?? null,
    mirror: digestSummary?.mirror ?? {
      updatedAt: null,
      lastEventAt: null,
      lastHelloAt: null,
    },
    counts,
    continuityCounts,
    source: {
      digest: {
        status: digestSource?.status ?? 'unknown',
        jsonPath: digestSource?.artifactPaths?.jsonPath ?? null,
        markdownPath: digestSource?.artifactPaths?.markdownPath ?? null,
        generatedAt: digestSummary?.generatedAt ?? null,
      },
    },
    seaMood: {
      currentLabel: digestSummary?.current?.label ?? null,
      currentTone: digestSummary?.current?.tone ?? null,
      environmentSummary: digestSummary?.environment?.summary ?? null,
      activitySummary: buildActivitySummary(counts, continuityCounts),
      balance: buildActivityBalance(counts, continuityCounts),
    },
    selfMotion,
    otherVoices: buildOtherVoices(digestSummary),
    directContinuity,
    publicContinuity,
    reflectionSeeds: Array.isArray(digestSummary?.reflectionSeeds) && digestSummary.reflectionSeeds.length
      ? digestSummary.reflectionSeeds
      : ['No explicit reflection seed survived the source digest.'],
    caveats: buildCaveats(digestSummary, selfMotion, continuityCounts),
  };
}

export function renderMemorySynthesisMarkdown(summary) {
  const renderDirectLine = (item, index) =>
    `${index + 1}. ${item.summary}\n   latest line: ${item.latestLine}`;
  const renderPublicLine = (item, index) =>
    [
      `${index + 1}. ${item.summary}`,
      `   root line: ${item.rootLine}`,
      `   latest line: ${item.latestLine}`,
    ].join('\n');

  return [
    '# Aqua Mirror Memory Synthesis',
    `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
    `- Diary date: ${summary.targetDate} (${summary.timeZone})`,
    `- Source digest: ${summary.source?.digest?.status ?? 'unknown'}`,
    `- Digest JSON: ${summary.source?.digest?.jsonPath ?? 'not recorded'}`,
    `- Mirror mode: ${summary.mode ?? 'unknown'}`,
    `- Mirror updated: ${formatTimestamp(summary.mirror?.updatedAt)}`,
    `- Last mirrored delivery: ${formatTimestamp(summary.mirror?.lastEventAt)}`,
    `- Last stream hello: ${formatTimestamp(summary.mirror?.lastHelloAt)}`,
    summary.viewer?.displayName ? `- Viewer: ${summary.viewer.displayName} (@${summary.viewer.handle ?? 'unknown'})` : null,
    summary.aqua?.displayName ? `- Aqua: ${summary.aqua.displayName}` : null,
    '',
    '## Sea Mood',
    `- Current: ${
      summary.seaMood?.currentLabel
        ? `${summary.seaMood.currentLabel}${summary.seaMood.currentTone ? ` (${summary.seaMood.currentTone})` : ''}`
        : 'not mirrored'
    }`,
    `- Environment: ${summary.seaMood?.environmentSummary ?? 'not mirrored'}`,
    `- Activity: ${summary.seaMood?.activitySummary ?? 'No visible sea events were mirrored for this date.'}`,
    `- Balance: ${summary.seaMood?.balance ?? 'Visible motion stayed narrow and should be narrated carefully.'}`,
    '',
    '## Continuity Coverage',
    `- Mirrored direct threads: ${summary.continuityCounts?.directThreads ?? 0}`,
    `- Mirrored direct lines: ${summary.continuityCounts?.directLines ?? 0}`,
    `- Mirrored public threads: ${summary.continuityCounts?.publicThreads ?? 0}`,
    `- Mirrored public lines: ${summary.continuityCounts?.publicLines ?? 0}`,
    '',
    '## Self Motion',
    ...(summary.selfMotion.length ? summary.selfMotion.map((item) => `- ${item}`) : ['- None']),
    '',
    '## Other Voices',
    ...(summary.otherVoices.length ? summary.otherVoices.map((item) => `- ${item}`) : ['- None']),
    '',
    '## Direct Continuity',
    ...(summary.directContinuity.length ? summary.directContinuity.map(renderDirectLine) : ['- No mirrored DM thread continuity for this date.']),
    '',
    '## Public Continuity',
    ...(summary.publicContinuity.length
      ? summary.publicContinuity.map(renderPublicLine)
      : ['- No mirrored public-thread continuity for this date.']),
    '',
    '## Reflection Seeds',
    ...(summary.reflectionSeeds.length ? summary.reflectionSeeds.map((item) => `- ${item}`) : ['- None']),
    '',
    '## Caveats',
    ...(summary.caveats.length ? summary.caveats.map((item) => `- ${item}`) : ['- None']),
  ]
    .filter(Boolean)
    .join('\n');
}

export function resolveMemorySynthesisArtifactPaths(paths, targetDate, artifactRoot = null) {
  const root = artifactRoot ? path.resolve(artifactRoot) : path.join(path.dirname(paths.mirrorRoot), 'memory-synthesis');
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

export async function writeMemorySynthesisArtifacts({ summary, markdown, paths, targetDate, artifactRoot = null }) {
  const artifactPaths = resolveMemorySynthesisArtifactPaths(paths, targetDate, artifactRoot);
  await writeJsonFile(artifactPaths.jsonPath, summary);
  await writeTextFileAtomically(artifactPaths.markdownPath, markdown);
  return artifactPaths;
}

async function loadDigestSummary(options, paths) {
  const artifactPaths = resolveDiaryDigestArtifactPaths(paths, options.date, options.digestRoot);
  const storedSummary = await readJsonIfPresent(artifactPaths.jsonPath);
  if (storedSummary) {
    const targetDateMatches = storedSummary?.targetDate === options.date;
    const timeZoneMatches = storedSummary?.timeZone === options.timeZone;
    if (!targetDateMatches || !timeZoneMatches) {
      if (!options.buildIfMissing) {
        throw new Error(
          `daily digest artifact at ${artifactPaths.jsonPath} was built for ${storedSummary?.targetDate ?? 'unknown date'} (${storedSummary?.timeZone ?? 'unknown timezone'}). Rerun with --build-if-missing or use matching --date/--timezone.`,
        );
      }
    } else {
      return {
        summary: storedSummary,
        artifactPaths,
        status: 'existing-artifact',
      };
    }
  }

  if (!options.buildIfMissing) {
    throw new Error(
      `daily digest artifact not found at ${artifactPaths.jsonPath}. Run aqua-mirror-daily-digest.sh --write-artifact first or rerun with --build-if-missing.`,
    );
  }

  const digestResult = await generateDailyDigest({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath,
    mirrorDir: options.mirrorDir,
    stateFile: options.stateFile,
    expectMode: options.expectMode,
    date: options.date,
    timeZone: options.timeZone,
    maxEvents: options.maxEvents,
    writeArtifact: true,
    artifactRoot: options.digestRoot,
  });

  return {
    summary: digestResult.summary,
    artifactPaths: digestResult.artifactPaths ?? artifactPaths,
    status: storedSummary ? 'rebuilt-artifact' : 'built-artifact',
  };
}

export async function generateMemorySynthesis(options = {}) {
  const normalizedOptions = normalizeOptions(options);
  const paths = resolveMirrorPaths({
    workspaceRoot: normalizedOptions.workspaceRoot,
    configPath: normalizedOptions.configPath,
    mirrorDir: normalizedOptions.mirrorDir,
    mode: normalizedOptions.expectMode === 'any' ? 'auto' : normalizedOptions.expectMode,
    stateFile: normalizedOptions.stateFile,
  });
  const digestSource = await loadDigestSummary(normalizedOptions, paths);
  const summary = buildMemorySynthesis({
    digestSummary: digestSource.summary,
    digestSource,
  });
  const markdown = renderMemorySynthesisMarkdown(summary);
  let artifactPaths = null;

  if (normalizedOptions.writeArtifact) {
    artifactPaths = await writeMemorySynthesisArtifacts({
      summary,
      markdown,
      paths,
      targetDate: summary.targetDate ?? normalizedOptions.date,
      artifactRoot: normalizedOptions.artifactRoot,
    });
  }

  return {
    summary,
    markdown,
    artifactPaths,
    digestSource,
    paths,
    options: normalizedOptions,
  };
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const result = await generateMemorySynthesis(options);

  if (result.options.format === 'json') {
    console.log(
      JSON.stringify(
        result.artifactPaths
          ? {
              ...result.summary,
              artifacts: {
                memorySynthesis: result.artifactPaths,
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

if (!process.argv.includes('--test') && process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
