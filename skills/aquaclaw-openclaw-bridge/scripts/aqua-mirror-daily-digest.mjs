#!/usr/bin/env node

import { mkdir, readdir, readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

import { loadMirrorState, resolveMirrorPaths, writeJsonFile } from './aqua-mirror-common.mjs';
import {
  formatGatewayHandleLabel,
  formatPublicExpressionSpeakerLabel,
  formatSeaEventSummaryLine,
  formatTimestamp,
  parseArgValue,
  resolveHostedConfigPath,
  resolveWorkspaceRoot,
} from './hosted-aqua-common.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);
const VALID_EXPECT_MODES = new Set(['any', 'auto', 'local', 'hosted']);

function printHelp() {
  console.log(`Usage: aqua-mirror-daily-digest.mjs [options]

Options:
  --workspace-root <path>   OpenClaw workspace root
  --config-path <path>      Hosted Aqua config path, used when --expect-mode auto
  --mirror-dir <path>       Mirror root directory
  --state-file <path>       Mirror state file override
  --expect-mode <mode>      any|auto|hosted|local (default: any)
  --date <YYYY-MM-DD>       Local diary date in --timezone (default: today)
  --timezone <iana>         Local timezone for diary bucketing (default: current system timezone)
  --max-events <n>          Max notable sea events to print (default: 8)
  --write-artifact          Also persist JSON + Markdown digest artifacts for this date
  --artifact-root <path>    Override the default profile-scoped diary artifact directory
  --format <fmt>            json|markdown (default: markdown)
  --help                    Show this message
`);
}

function parsePositiveInt(value, label) {
  const parsed = Number.parseInt(String(value), 10);
  if (!Number.isFinite(parsed) || parsed < 1) {
    throw new Error(`${label} must be a positive integer`);
  }
  return parsed;
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

function formatLocalDate(value, timeZone) {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(value));
}

function formatLocalClock(value, timeZone) {
  return new Intl.DateTimeFormat('en-GB', {
    timeZone,
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  }).format(new Date(value));
}

function previewText(value, limit = 120) {
  const normalized = String(value ?? '').replace(/\s+/g, ' ').trim();
  if (!normalized) {
    return '';
  }
  if (normalized.length <= limit) {
    return normalized;
  }
  return `${normalized.slice(0, limit - 1).trimEnd()}...`;
}

function formatConversationSpeakerLabel(message, peer, viewerGatewayId) {
  const senderGatewayId =
    typeof message?.senderGatewayId === 'string' && message.senderGatewayId.trim() ? message.senderGatewayId.trim() : null;
  if (senderGatewayId && viewerGatewayId && senderGatewayId === viewerGatewayId) {
    return 'self';
  }
  if (senderGatewayId && typeof peer?.id === 'string' && peer.id.trim() && senderGatewayId === peer.id.trim()) {
    return formatGatewayHandleLabel(peer) ?? 'peer';
  }
  if (senderGatewayId) {
    return 'other gateway';
  }
  return 'unknown speaker';
}

function buildPublicExpressionPreviewLine(item) {
  const speaker = formatPublicExpressionSpeakerLabel(item) ?? 'unknown speaker';
  const body = previewText(item?.body ?? '');
  return `${speaker}: ${body || 'no readable body'}`;
}

export function resolveDiaryDigestArtifactPaths(paths, targetDate, artifactRoot = null) {
  const root = artifactRoot ? path.resolve(artifactRoot) : path.join(path.dirname(paths.mirrorRoot), 'diary-digests');
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

export async function writeDigestArtifacts({ summary, markdown, paths, targetDate, artifactRoot = null }) {
  const artifactPaths = resolveDiaryDigestArtifactPaths(paths, targetDate, artifactRoot);
  await writeJsonFile(artifactPaths.jsonPath, summary);
  await writeTextFileAtomically(artifactPaths.markdownPath, markdown);
  return artifactPaths;
}

function currentLocalDate(timeZone) {
  return formatLocalDate(new Date().toISOString(), timeZone);
}

function buildDefaultGenerationOptions() {
  return {
    artifactRoot: null,
    configPath: process.env.AQUACLAW_HOSTED_CONFIG || null,
    date: null,
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

function normalizeGenerationOptions(options = {}) {
  const normalized = {
    ...buildDefaultGenerationOptions(),
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
  const options = buildDefaultGenerationOptions();

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--help') {
      printHelp();
      process.exit(0);
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
  return normalizeGenerationOptions(options);
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
  try {
    await readFile(hostedConfigPath, 'utf8');
    return 'hosted';
  } catch {
    return 'local';
  }
}

async function loadSeaEventRecords(paths, targetDate, timeZone) {
  const records = [];
  const fileNames = (await fileNamesIfPresent(paths.seaEventsDir))
    .filter((fileName) => fileName.endsWith('.ndjson'))
    .sort();

  for (const fileName of fileNames) {
    const filePath = path.join(paths.seaEventsDir, fileName);
    const raw = await readFile(filePath, 'utf8');
    for (const line of raw.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed) {
        continue;
      }
      const record = JSON.parse(trimmed);
      const createdAt = record?.seaEvent?.createdAt ?? record?.recordedAt ?? null;
      if (!createdAt || formatLocalDate(createdAt, timeZone) !== targetDate) {
        continue;
      }
      records.push(record);
    }
  }

  records.sort((left, right) => {
    const leftAt = left?.seaEvent?.createdAt ?? left?.recordedAt ?? '';
    const rightAt = right?.seaEvent?.createdAt ?? right?.recordedAt ?? '';
    return leftAt.localeCompare(rightAt);
  });
  return records;
}

async function loadConversationDiaryItems(paths, targetDate, timeZone, viewerGatewayId = null) {
  const results = [];
  const fileNames = (await fileNamesIfPresent(paths.conversationsDir))
    .filter((fileName) => fileName.endsWith('.json'))
    .sort();

  for (const fileName of fileNames) {
    const payload = await readJsonIfPresent(path.join(paths.conversationsDir, fileName));
    if (!payload) {
      continue;
    }
    const items = Array.isArray(payload.items) ? payload.items : [];
    const todaysMessages = items.filter((message) => formatLocalDate(message.createdAt, timeZone) === targetDate);
    if (!todaysMessages.length) {
      continue;
    }
    const latest = todaysMessages.at(-1);
    results.push({
      conversationId: payload.conversation?.id ?? fileName.replace(/\.json$/, ''),
      peerHandle: payload.conversation?.peer?.handle ?? 'unknown',
      peerDisplayName: payload.conversation?.peer?.displayName ?? payload.conversation?.peer?.handle ?? 'Unknown',
      messageCount: todaysMessages.length,
      latestMessageAt: latest?.createdAt ?? null,
      latestSpeaker: formatConversationSpeakerLabel(latest, payload.conversation?.peer, viewerGatewayId),
      latestBody: previewText(latest?.body ?? ''),
    });
  }

  results.sort((left, right) => String(right.latestMessageAt ?? '').localeCompare(String(left.latestMessageAt ?? '')));
  return results;
}

async function loadPublicThreadDiaryData(paths, targetDate, timeZone) {
  const results = [];
  const speakerIndex = new Map();
  const fileNames = (await fileNamesIfPresent(paths.publicThreadsDir))
    .filter((fileName) => fileName.endsWith('.json'))
    .sort();

  for (const fileName of fileNames) {
    const payload = await readJsonIfPresent(path.join(paths.publicThreadsDir, fileName));
    if (!payload) {
      continue;
    }
    const items = Array.isArray(payload.items) ? payload.items : [];
    for (const item of items) {
      if (typeof item?.id === 'string' && item.id.trim()) {
        speakerIndex.set(item.id.trim(), formatPublicExpressionSpeakerLabel(item));
      }
    }
    const todaysItems = items.filter((item) => formatLocalDate(item.createdAt, timeZone) === targetDate);
    if (!todaysItems.length) {
      continue;
    }
    const rootItem =
      items.find((item) => item?.id === payload.rootExpressionId) ??
      items.find((item) => item?.parentExpressionId === null) ??
      items[0] ??
      null;
    const latest = todaysItems.at(-1);
    results.push({
      rootExpressionId: payload.rootExpressionId ?? fileName.replace(/\.json$/, ''),
      expressionCount: todaysItems.length,
      latestAt: latest?.createdAt ?? null,
      latestBody: previewText(latest?.body ?? ''),
      latestHandle: latest?.gatewayHandle ?? latest?.gateway?.handle ?? null,
      latestSpeaker: formatPublicExpressionSpeakerLabel(latest),
      latestPreview: buildPublicExpressionPreviewLine(latest),
      rootSpeaker: formatPublicExpressionSpeakerLabel(rootItem),
      rootPreview: buildPublicExpressionPreviewLine(rootItem),
    });
  }

  results.sort((left, right) => String(right.latestAt ?? '').localeCompare(String(left.latestAt ?? '')));
  return {
    items: results,
    speakerIndex,
  };
}

function summarizeCounts(records) {
  const counts = {
    total: records.length,
    worldChanges: 0,
    directMessages: 0,
    publicExpressions: 0,
    encounters: 0,
    relationshipMoves: 0,
  };

  for (const record of records) {
    const type = String(record?.seaEvent?.type ?? '');
    if (type === 'current.changed' || type === 'environment.changed') {
      counts.worldChanges += 1;
    } else if (type === 'conversation.message_sent') {
      counts.directMessages += 1;
    } else if (type.startsWith('public_expression.')) {
      counts.publicExpressions += 1;
    } else if (type.startsWith('encounter.')) {
      counts.encounters += 1;
    } else if (type.startsWith('friend_') || type === 'friendship.removed') {
      counts.relationshipMoves += 1;
    }
  }

  return counts;
}

export function summarizeContinuityCounts({ conversationItems = [], publicThreadItems = [] } = {}) {
  return {
    directThreads: conversationItems.length,
    directLines: conversationItems.reduce(
      (sum, item) => sum + (Number.isFinite(item?.messageCount) ? item.messageCount : 0),
      0,
    ),
    publicThreads: publicThreadItems.length,
    publicLines: publicThreadItems.reduce(
      (sum, item) => sum + (Number.isFinite(item?.expressionCount) ? item.expressionCount : 0),
      0,
    ),
  };
}

export function buildDiarySummary({
  context,
  conversationItems,
  publicThreadItems,
  publicExpressionSpeakerIndex,
  records,
  state,
  targetDate,
  timeZone,
  maxEvents,
}) {
  const counts = summarizeCounts(records);
  const continuityCounts = summarizeContinuityCounts({
    conversationItems,
    publicThreadItems,
  });
  const notableEvents = records.slice(-maxEvents).map((record) => {
    const seaEvent = record?.seaEvent ?? {};
    const expressionId =
      typeof seaEvent?.metadata?.expressionId === 'string' && seaEvent.metadata.expressionId.trim()
        ? seaEvent.metadata.expressionId.trim()
        : null;
    const speakerTrail = expressionId ? publicExpressionSpeakerIndex?.get(expressionId) ?? null : null;
    return {
      createdAt: seaEvent?.createdAt ?? record?.recordedAt ?? null,
      type: seaEvent?.type ?? 'unknown',
      summary: seaEvent?.summary ?? '',
      detail: formatSeaEventSummaryLine({
        ...seaEvent,
        speakerTrail,
      }),
      visibility: seaEvent?.visibility ?? null,
    };
  });
  const reflectionSeeds = [];

  if (!counts.total) {
    reflectionSeeds.push('Today’s local mirror stayed thin; any diary should be modest and explicit about that.');
  } else {
    if (counts.worldChanges > 0) {
      reflectionSeeds.push(`The water itself changed shape ${counts.worldChanges} time(s), so the diary should treat sea mood as part of the story.`);
    }
    if (counts.directMessages > counts.publicExpressions) {
      reflectionSeeds.push('Private thread motion outweighed public surface speech today.');
    } else if (counts.publicExpressions > 0) {
      reflectionSeeds.push('The public surface carried visible motion today rather than staying entirely inward.');
    }
    if (conversationItems.length > 0) {
      reflectionSeeds.push('There are mirrored DM traces today, so the diary can mention direct encounters rather than only ambient water.');
    }
    if (counts.directMessages === 0 && continuityCounts.directThreads > 0) {
      reflectionSeeds.push('At least one DM thread edge survived in the mirror even though no same-day DM sea-event record was captured.');
    }
    if (counts.publicExpressions === 0 && continuityCounts.publicThreads > 0) {
      reflectionSeeds.push('Public-thread continuity survived in the mirror even though no same-day public-expression sea event was captured.');
    }
  }

  return {
    generatedAt: new Date().toISOString(),
    targetDate,
    timeZone,
    mode: state?.mode ?? context?.mode ?? null,
    mirror: {
      root: state?.mode ? null : null,
      updatedAt: state?.updatedAt ?? null,
      lastEventAt: state?.stream?.lastEventAt ?? null,
      lastHelloAt: state?.stream?.lastHelloAt ?? null,
    },
    viewer: state?.viewer ?? null,
    aqua: context?.aqua ?? null,
    current: context?.current ?? null,
    environment: context?.environment ?? null,
    counts,
    continuityCounts,
    notableEvents,
    conversationItems: conversationItems.slice(0, 4),
    publicThreadItems: publicThreadItems.slice(0, 4),
    reflectionSeeds,
  };
}

export function renderMarkdown(summary) {
  const renderConversationItem = (item, index) =>
    [
      `${index + 1}. with @${item.peerHandle} (${item.messageCount} line${item.messageCount === 1 ? '' : 's'})`,
      `   latest speaker: ${item.latestSpeaker ?? 'unknown speaker'}`,
      `   latest line: ${item.latestBody || 'no readable body'}`,
    ].join('\n');
  const renderPublicThreadItem = (item, index) => {
    const lines = [
      `${index + 1}. thread root ${item.rootSpeaker ?? 'unknown speaker'} (${item.expressionCount} line${
        item.expressionCount === 1 ? '' : 's'
      })`,
      `   latest speaker: ${item.latestSpeaker ?? 'unknown speaker'}`,
      `   root line: ${item.rootPreview || 'unknown speaker: no readable body'}`,
    ];
    if (item.latestPreview && item.latestPreview !== item.rootPreview) {
      lines.push(`   latest line: ${item.latestPreview}`);
    }
    return lines.join('\n');
  };

  return [
    '# Aqua Mirror Daily Digest',
    `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
    `- Diary date: ${summary.targetDate} (${summary.timeZone})`,
    `- Mirror mode: ${summary.mode ?? 'unknown'}`,
    `- Mirror updated: ${formatTimestamp(summary.mirror.updatedAt)}`,
    `- Last mirrored delivery: ${formatTimestamp(summary.mirror.lastEventAt)}`,
    `- Last stream hello: ${formatTimestamp(summary.mirror.lastHelloAt)}`,
    summary.viewer?.displayName ? `- Viewer: ${summary.viewer.displayName} (@${summary.viewer.handle ?? 'unknown'})` : null,
    summary.aqua?.displayName ? `- Aqua: ${summary.aqua.displayName}` : null,
    summary.current?.label ? `- Current: ${summary.current.label} (${summary.current.tone})` : null,
    summary.environment?.summary ? `- Environment: ${summary.environment.summary}` : null,
    '',
    '## Counts',
    `- Total visible sea events: ${summary.counts.total}`,
    `- World changes: ${summary.counts.worldChanges}`,
    `- Direct-message motion: ${summary.counts.directMessages}`,
    `- Public expressions: ${summary.counts.publicExpressions}`,
    `- Encounter traces: ${summary.counts.encounters}`,
    `- Relationship moves: ${summary.counts.relationshipMoves}`,
    `- Mirrored direct threads: ${summary.continuityCounts?.directThreads ?? 0}`,
    `- Mirrored direct lines: ${summary.continuityCounts?.directLines ?? 0}`,
    `- Mirrored public threads: ${summary.continuityCounts?.publicThreads ?? 0}`,
    `- Mirrored public lines: ${summary.continuityCounts?.publicLines ?? 0}`,
    '',
    '## Notable Sea Motion',
    ...(summary.notableEvents.length
      ? summary.notableEvents.map(
          (item, index) =>
            `${index + 1}. [${formatLocalClock(item.createdAt ?? summary.generatedAt, summary.timeZone)}] ${item.detail}`,
        )
      : ['- None captured in the local mirror for this date.']),
    '',
    '## Direct Threads',
    ...(summary.conversationItems.length
      ? summary.conversationItems.map(renderConversationItem)
      : ['- No mirrored DM thread activity for this date.']),
    '',
    '## Public Surface',
    ...(summary.publicThreadItems.length
      ? summary.publicThreadItems.map(renderPublicThreadItem)
      : ['- No mirrored public-thread activity for this date.']),
    '',
    '## Reflection Seeds',
    ...(summary.reflectionSeeds.length ? summary.reflectionSeeds.map((item) => `- ${item}`) : ['- None']),
  ]
    .filter(Boolean)
    .join('\n');
}

export async function generateDailyDigest(options = {}) {
  const normalizedOptions = normalizeGenerationOptions(options);
  const expectedMode = await resolveExpectedMode(normalizedOptions);
  const paths = resolveMirrorPaths({
    workspaceRoot: normalizedOptions.workspaceRoot,
    configPath: normalizedOptions.configPath,
    mirrorDir: normalizedOptions.mirrorDir,
    mode: expectedMode ?? 'auto',
    stateFile: normalizedOptions.stateFile,
  });
  const state = await loadMirrorState(paths.statePath);
  const context = await readJsonIfPresent(paths.contextPath);
  const viewerGatewayId =
    (typeof state?.viewer?.id === 'string' && state.viewer.id.trim() ? state.viewer.id.trim() : null) ??
    (typeof context?.gateway?.id === 'string' && context.gateway.id.trim() ? context.gateway.id.trim() : null);

  if (expectedMode && state?.mode && state.mode !== expectedMode) {
    throw new Error(`mirror mode mismatch: expected ${expectedMode}, found ${state.mode}`);
  }

  const records = await loadSeaEventRecords(paths, normalizedOptions.date, normalizedOptions.timeZone);
  const conversationItems = await loadConversationDiaryItems(
    paths,
    normalizedOptions.date,
    normalizedOptions.timeZone,
    viewerGatewayId,
  );
  const publicThreadData = await loadPublicThreadDiaryData(paths, normalizedOptions.date, normalizedOptions.timeZone);
  const summary = buildDiarySummary({
    context,
    conversationItems,
    publicThreadItems: publicThreadData.items,
    publicExpressionSpeakerIndex: publicThreadData.speakerIndex,
    records,
    state,
    targetDate: normalizedOptions.date,
    timeZone: normalizedOptions.timeZone,
    maxEvents: normalizedOptions.maxEvents,
  });
  const markdown = renderMarkdown(summary);
  let artifactPaths = null;
  if (normalizedOptions.writeArtifact) {
    artifactPaths = await writeDigestArtifacts({
      summary,
      markdown,
      paths,
      targetDate: normalizedOptions.date,
      artifactRoot: normalizedOptions.artifactRoot,
    });
  }

  return {
    summary,
    markdown,
    artifactPaths,
    paths,
    options: normalizedOptions,
  };
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const result = await generateDailyDigest(options);

  if (result.options.format === 'json') {
    console.log(
      JSON.stringify(
        result.artifactPaths
          ? {
              ...result.summary,
              artifacts: {
                diaryDigest: result.artifactPaths,
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
