#!/usr/bin/env node

import { mkdir, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

import { writeJsonFile } from './aqua-mirror-common.mjs';
import { generateMemorySynthesis } from './aqua-mirror-memory-synthesis.mjs';
import {
  loadCommunityMemoryIndex,
  loadCommunityMemoryState,
  resolveCommunityMemoryPaths,
} from './community-memory-common.mjs';
import {
  formatTimestamp,
  loadHostedConfig,
  parseArgValue,
  parsePositiveInt,
  requestJson,
  resolveWorkspaceRoot,
} from './hosted-aqua-common.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);
const VALID_EXPECT_MODES = new Set(['any', 'auto', 'hosted', 'local']);
const DEFAULT_SCENE_LIMIT = 12;
const DEFAULT_COMMUNITY_MEMORY_LIMIT = 6;

function printHelp() {
  console.log(`Usage: aqua-sea-diary-context.mjs [options]

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
  --artifact-root <path>          Override the sea-diary-context artifact directory
  --build-if-missing              Build digest/synthesis artifacts first when needed
  --max-events <n>                Max notable events when building missing digest artifacts (default: 8)
  --scene-limit <n>               Max same-day scenes to keep (default: ${DEFAULT_SCENE_LIMIT})
  --community-limit <n>           Max same-day community notes to keep (default: ${DEFAULT_COMMUNITY_MEMORY_LIMIT})
  --write-artifact                Persist JSON + Markdown diary-context artifacts
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

function previewText(value, limit = 160) {
  const normalized = String(value ?? '').replace(/\s+/g, ' ').trim();
  if (!normalized) {
    return '';
  }
  if (normalized.length <= limit) {
    return normalized;
  }
  return `${normalized.slice(0, Math.max(limit - 1, 1)).trimEnd()}...`;
}

function normalizeSceneTrigger(trigger) {
  if (!trigger || typeof trigger !== 'object' || Array.isArray(trigger)) {
    return null;
  }
  const normalized = {
    kind: typeof trigger.kind === 'string' ? trigger.kind.trim() : '',
    sourceKind: typeof trigger.sourceKind === 'string' ? trigger.sourceKind.trim() : '',
    sourceId: typeof trigger.sourceId === 'string' && trigger.sourceId.trim() ? trigger.sourceId.trim() : null,
    occurredAt: typeof trigger.occurredAt === 'string' && trigger.occurredAt.trim() ? trigger.occurredAt.trim() : null,
    reason: typeof trigger.reason === 'string' && trigger.reason.trim() ? trigger.reason.trim() : null,
    signature: typeof trigger.signature === 'string' && trigger.signature.trim() ? trigger.signature.trim() : null,
    peerGatewayId: typeof trigger.peerGatewayId === 'string' && trigger.peerGatewayId.trim() ? trigger.peerGatewayId.trim() : null,
    conversationId:
      typeof trigger.conversationId === 'string' && trigger.conversationId.trim() ? trigger.conversationId.trim() : null,
    requestId: typeof trigger.requestId === 'string' && trigger.requestId.trim() ? trigger.requestId.trim() : null,
    messageId: typeof trigger.messageId === 'string' && trigger.messageId.trim() ? trigger.messageId.trim() : null,
    venueSlug: typeof trigger.venueSlug === 'string' && trigger.venueSlug.trim() ? trigger.venueSlug.trim() : null,
    cue: typeof trigger.cue === 'string' && trigger.cue.trim() ? trigger.cue.trim() : null,
  };
  if (!normalized.kind || !normalized.sourceKind) {
    return null;
  }
  return normalized;
}

function uniqueLines(items) {
  return [...new Set(items.filter((item) => typeof item === 'string' && item.trim()).map((item) => item.trim()))];
}

function compareIsoAsc(leftValue, rightValue) {
  return String(leftValue ?? '').localeCompare(String(rightValue ?? ''));
}

function buildDefaultOptions() {
  return {
    artifactRoot: null,
    buildIfMissing: false,
    communityLimit: DEFAULT_COMMUNITY_MEMORY_LIMIT,
    communityMemoryDir: process.env.AQUACLAW_COMMUNITY_MEMORY_DIR || null,
    configPath: process.env.AQUACLAW_HOSTED_CONFIG || null,
    date: null,
    digestRoot: null,
    expectMode: 'any',
    format: 'markdown',
    maxEvents: 8,
    mirrorDir: process.env.AQUACLAW_MIRROR_DIR || null,
    sceneLimit: DEFAULT_SCENE_LIMIT,
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

function resolveSeaDiaryContextArtifactPaths(paths, targetDate, artifactRoot = null) {
  const root = artifactRoot ? path.resolve(artifactRoot) : path.join(path.dirname(paths.mirrorRoot), 'sea-diary-context');
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

export async function writeSeaDiaryContextArtifacts({ summary, markdown, paths, targetDate, artifactRoot = null }) {
  const artifactPaths = resolveSeaDiaryContextArtifactPaths(paths, targetDate, artifactRoot);
  await writeJsonFile(artifactPaths.jsonPath, summary);
  await writeTextFileAtomically(artifactPaths.markdownPath, markdown);
  return artifactPaths;
}

function buildEvidenceHierarchyLines() {
  return [
    'Visible same-day motion, timestamps, and speaker ownership come from the digest-backed visible layer only.',
    'Local memory synthesis is continuity scaffolding; it must not override missing visible evidence.',
    'Gateway-private scenes are private first-person experience, not public events.',
    'Gateway-private community notes are whispers or rumor recall; they may color reflection but must not be upgraded into public fact unless the visible layer also supports them.',
  ];
}

function describeCommunityMemoryHandling(note) {
  const mentionPolicy = String(note?.mentionPolicy ?? '').trim();
  if (mentionPolicy === 'private_only') {
    return 'Private whisper only. If it enters the diary, keep it framed as something privately heard or remembered, never as public fact.';
  }
  if (mentionPolicy === 'paraphrase_ok') {
    return 'May shape tone or indirect callback, but still keep it framed as private hearsay unless visible evidence also supports it.';
  }
  if (mentionPolicy === 'public_ok') {
    return 'Can be recalled more directly in a private diary, but it still does not count as visible/public evidence by itself.';
  }
  return 'Treat as private recall rather than public evidence.';
}

function buildSceneReflectionSeeds(items) {
  if (!items.length) {
    return [];
  }
  const types = new Set(items.map((item) => item.type));
  const tones = new Set(items.map((item) => item.tone).filter(Boolean));
  const seeds = [`A gateway-private scene layer exists for this day (${items.length} item${items.length === 1 ? '' : 's'}).`];
  if (types.has('vent')) {
    seeds.push('At least one private vent stayed in the day, so the diary can admit inward friction without turning it into a public event.');
  }
  if (types.has('social_glimpse')) {
    seeds.push('At least one private social glimpse survived, so the diary can include a quiet first-person social afterimage.');
  }
  if (tones.size > 0) {
    seeds.push(`Private scene tone touched ${[...tones].join(', ')} water.`);
  }
  return seeds;
}

function buildCommunityReflectionSeeds(layer) {
  if ((layer?.sameDayCount ?? 0) < 1) {
    return [];
  }

  const seeds = [`A private community-recall layer exists for this day (${layer.sameDayCount} note${layer.sameDayCount === 1 ? '' : 's'}).`];
  if ((layer.privateOnlyCount ?? 0) > 0) {
    seeds.push('Some community memory stayed private_only, so any mention must remain clearly hearsay or inward recollection.');
  }
  if ((layer.paraphraseOkCount ?? 0) > 0) {
    seeds.push('Some community memory is only safe as paraphrased aftertaste rather than direct quotation.');
  }
  if ((layer.publicOkCount ?? 0) > 0) {
    seeds.push('Some community memory is sharable in principle, but it still should not outrank the visible layer inside the diary.');
  }
  return seeds;
}

function buildDiaryCaveats({ synthesisSummary, sceneLayer, communityLayer, warnings }) {
  const caveats = Array.isArray(synthesisSummary?.caveats) ? [...synthesisSummary.caveats] : [];
  if (sceneLayer?.status && sceneLayer.status.startsWith('unavailable')) {
    caveats.push('Scene layer was unavailable for this run, so the diary should not invent a private experiential layer beyond what is actually present.');
  }
  if (sceneLayer?.status === 'no_same_day_scenes') {
    caveats.push('No same-day scene was recovered, so private experience should come only from other supported layers.');
  }
  if (communityLayer?.recoveredState || communityLayer?.recoveredIndex) {
    caveats.push('Community-memory state or index needed local recovery, so note coverage should be treated as best-effort.');
  }
  return uniqueLines([...caveats, ...(Array.isArray(warnings) ? warnings : [])]);
}

function deriveProfileCommunityMemoryRoot({ communityMemoryDir, mirrorRoot, workspaceRoot, configPath }) {
  if (communityMemoryDir) {
    return resolveCommunityMemoryPaths({
      workspaceRoot,
      configPath,
      communityMemoryDir,
    });
  }

  const derivedCommunityRoot = mirrorRoot ? path.join(path.dirname(mirrorRoot), 'community-memory') : null;
  return resolveCommunityMemoryPaths({
    workspaceRoot,
    configPath,
    communityMemoryDir: derivedCommunityRoot,
  });
}

function normalizeSceneItem(scene) {
  return {
    id: scene?.id ?? null,
    createdAt: scene?.createdAt ?? null,
    type: scene?.type ?? 'unknown',
    tone: scene?.tone ?? null,
    summary: typeof scene?.summary === 'string' ? scene.summary.trim() : '',
    trigger: normalizeSceneTrigger(scene?.metadata?.trigger),
  };
}

async function loadSceneLayer(
  options,
  {
    loadHostedConfigFn = loadHostedConfig,
    requestJsonFn = requestJson,
  } = {},
) {
  const queryLimit = Math.max(options.sceneLimit * 4, options.sceneLimit, DEFAULT_SCENE_LIMIT);

  let loaded;
  try {
    loaded = await loadHostedConfigFn({
      workspaceRoot: options.workspaceRoot,
      configPath: options.configPath,
    });
  } catch (error) {
    return {
      status: 'unavailable_no_hosted_config',
      sourceKind: 'live_gateway_private',
      requestedLimit: queryLimit,
      warning: error instanceof Error ? error.message : String(error),
      items: [],
      sameDayCount: 0,
      fetchedCount: 0,
    };
  }

  try {
    const payload = await requestJsonFn(
      loaded.config.hubUrl,
      `/api/v1/scenes/mine?limit=${queryLimit}`,
      {
        token: loaded.config.credential.token,
      },
    );
    const rawItems = Array.isArray(payload?.data?.items) ? payload.data.items : [];
    const sameDayItems = rawItems
      .filter((item) => item?.createdAt && formatLocalDate(item.createdAt, options.timeZone) === options.date)
      .sort((left, right) => compareIsoAsc(left?.createdAt, right?.createdAt))
      .slice(-options.sceneLimit)
      .map(normalizeSceneItem);

    return {
      status: sameDayItems.length > 0 ? 'included' : 'no_same_day_scenes',
      sourceKind: 'live_gateway_private',
      requestedLimit: queryLimit,
      items: sameDayItems,
      sameDayCount: sameDayItems.length,
      fetchedCount: rawItems.length,
      warning: null,
    };
  } catch (error) {
    return {
      status: 'unavailable_request_failed',
      sourceKind: 'live_gateway_private',
      requestedLimit: queryLimit,
      warning: error instanceof Error ? error.message : String(error),
      items: [],
      sameDayCount: 0,
      fetchedCount: 0,
    };
  }
}

function normalizeCommunityMemoryNoteForDiary(note) {
  const summary = typeof note?.summary === 'string' ? note.summary.trim() : '';
  const body = typeof note?.body === 'string' ? note.body.trim() : '';
  return {
    id: note?.id ?? null,
    createdAt: note?.createdAt ?? null,
    npcId: note?.npcId ?? null,
    venueSlug: note?.venueSlug ?? null,
    sourceKind: note?.sourceKind ?? null,
    mentionPolicy: note?.mentionPolicy ?? null,
    freshnessScore: Number.isFinite(note?.freshnessScore) ? note.freshnessScore : null,
    tags: Array.isArray(note?.tags) ? [...note.tags] : [],
    summary: summary || null,
    cue: previewText(body || summary, 180) || null,
    handling: describeCommunityMemoryHandling(note),
  };
}

async function loadCommunityMemoryLayer(options, mirrorPaths) {
  const paths = deriveProfileCommunityMemoryRoot({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath,
    communityMemoryDir: options.communityMemoryDir,
    mirrorRoot: mirrorPaths.mirrorRoot,
  });
  const [{ state, recovered: recoveredState, recoveryReason: recoveredStateReason }, { index, recovered: recoveredIndex, recoveryReason: recoveredIndexReason }] =
    await Promise.all([
      loadCommunityMemoryState(paths.statePath),
      loadCommunityMemoryIndex(paths),
    ]);

  const sameDayNotesAll = (Array.isArray(index?.items) ? index.items : [])
    .filter((note) => note?.createdAt && formatLocalDate(note.createdAt, options.timeZone) === options.date)
    .sort((left, right) => compareIsoAsc(left?.createdAt, right?.createdAt));
  const limitedItems = sameDayNotesAll.slice(-options.communityLimit).map(normalizeCommunityMemoryNoteForDiary);
  const privateOnlyCount = sameDayNotesAll.filter((note) => note?.mentionPolicy === 'private_only').length;
  const paraphraseOkCount = sameDayNotesAll.filter((note) => note?.mentionPolicy === 'paraphrase_ok').length;
  const publicOkCount = sameDayNotesAll.filter((note) => note?.mentionPolicy === 'public_ok').length;

  return {
    status: sameDayNotesAll.length > 0 ? 'included' : state.totalKnownNotes > 0 ? 'no_same_day_notes' : 'empty',
    sourceKind: 'local_profile_mirror',
    paths: {
      communityMemoryRoot: paths.communityMemoryRoot,
      profileId: paths.profileId ?? 'legacy',
    },
    state: {
      lastSyncedAt: state.lastSyncedAt,
      totalKnownNotes: state.totalKnownNotes,
      fullBackfillCompletedAt: state.fullBackfillCompletedAt,
    },
    recoveredState,
    recoveredStateReason,
    recoveredIndex,
    recoveredIndexReason,
    sameDayCount: sameDayNotesAll.length,
    privateOnlyCount,
    paraphraseOkCount,
    publicOkCount,
    items: limitedItems,
  };
}

function buildSeaDiaryContext({
  digestSummary,
  synthesisSummary,
  digestSource,
  sceneLayer,
  communityLayer,
  options,
  warnings = [],
}) {
  const sceneReflectionSeeds = buildSceneReflectionSeeds(sceneLayer.items);
  const communityReflectionSeeds = buildCommunityReflectionSeeds(communityLayer);
  const diaryReflectionSeeds = uniqueLines([
    ...(Array.isArray(digestSummary?.reflectionSeeds) ? digestSummary.reflectionSeeds : []),
    ...sceneReflectionSeeds,
    ...communityReflectionSeeds,
  ]);
  const diaryCaveats = buildDiaryCaveats({
    synthesisSummary,
    sceneLayer,
    communityLayer,
    warnings,
  });

  return {
    generatedAt: new Date().toISOString(),
    targetDate: digestSummary?.targetDate ?? options.date,
    timeZone: digestSummary?.timeZone ?? options.timeZone,
    mode: digestSummary?.mode ?? synthesisSummary?.mode ?? null,
    source: {
      digest: {
        status: digestSource?.status ?? 'unknown',
        jsonPath: digestSource?.artifactPaths?.jsonPath ?? null,
        markdownPath: digestSource?.artifactPaths?.markdownPath ?? null,
        generatedAt: digestSummary?.generatedAt ?? null,
      },
      memorySynthesis: {
        status: 'generated',
        generatedAt: synthesisSummary?.generatedAt ?? null,
      },
      scenes: {
        status: sceneLayer.status,
        sourceKind: sceneLayer.sourceKind,
        requestedLimit: sceneLayer.requestedLimit,
        fetchedCount: sceneLayer.fetchedCount,
        sameDayCount: sceneLayer.sameDayCount,
        warning: sceneLayer.warning ?? null,
      },
      communityMemory: {
        status: communityLayer.status,
        sourceKind: communityLayer.sourceKind,
        profileId: communityLayer.paths.profileId,
        communityMemoryRoot: communityLayer.paths.communityMemoryRoot,
        lastSyncedAt: communityLayer.state.lastSyncedAt,
        totalKnownNotes: communityLayer.state.totalKnownNotes,
        fullBackfillCompletedAt: communityLayer.state.fullBackfillCompletedAt,
        sameDayCount: communityLayer.sameDayCount,
        privateOnlyCount: communityLayer.privateOnlyCount,
        paraphraseOkCount: communityLayer.paraphraseOkCount,
        publicOkCount: communityLayer.publicOkCount,
        recoveredState: communityLayer.recoveredState,
        recoveredStateReason: communityLayer.recoveredStateReason,
        recoveredIndex: communityLayer.recoveredIndex,
        recoveredIndexReason: communityLayer.recoveredIndexReason,
      },
    },
    evidenceHierarchy: buildEvidenceHierarchyLines(),
    visibleLayer: {
      aqua: digestSummary?.aqua ?? null,
      viewer: digestSummary?.viewer ?? null,
      mirror: digestSummary?.mirror ?? null,
      current: digestSummary?.current ?? null,
      environment: digestSummary?.environment ?? null,
      counts: digestSummary?.counts ?? null,
      continuityCounts: digestSummary?.continuityCounts ?? null,
      notableEvents: Array.isArray(digestSummary?.notableEvents) ? digestSummary.notableEvents : [],
      reflectionSeeds: Array.isArray(digestSummary?.reflectionSeeds) ? digestSummary.reflectionSeeds : [],
    },
    privateSceneLayer: {
      status: sceneLayer.status,
      items: sceneLayer.items,
      reflectionSeeds: sceneReflectionSeeds,
    },
    privateCommunityLayer: {
      status: communityLayer.status,
      items: communityLayer.items,
      reflectionSeeds: communityReflectionSeeds,
      recoveredState: communityLayer.recoveredState,
      recoveredStateReason: communityLayer.recoveredStateReason,
      recoveredIndex: communityLayer.recoveredIndex,
      recoveredIndexReason: communityLayer.recoveredIndexReason,
    },
    localSynthesisLayer: {
      seaMood: synthesisSummary?.seaMood ?? null,
      selfMotion: Array.isArray(synthesisSummary?.selfMotion) ? synthesisSummary.selfMotion : [],
      otherVoices: Array.isArray(synthesisSummary?.otherVoices) ? synthesisSummary.otherVoices : [],
      directContinuity: Array.isArray(synthesisSummary?.directContinuity) ? synthesisSummary.directContinuity : [],
      publicContinuity: Array.isArray(synthesisSummary?.publicContinuity) ? synthesisSummary.publicContinuity : [],
      reflectionSeeds: Array.isArray(synthesisSummary?.reflectionSeeds) ? synthesisSummary.reflectionSeeds : [],
      caveats: Array.isArray(synthesisSummary?.caveats) ? synthesisSummary.caveats : [],
    },
    diaryReflectionSeeds,
    diaryCaveats,
    warnings: uniqueLines([
      ...(sceneLayer.warning ? [sceneLayer.warning] : []),
      ...(Array.isArray(warnings) ? warnings : []),
    ]),
  };
}

function renderNotableEvent(item, index, timeZone) {
  return `${index + 1}. [${formatLocalClock(item?.createdAt ?? new Date().toISOString(), timeZone)}] ${item?.detail ?? item?.summary ?? 'unknown event'}`;
}

function renderSceneItem(item, index, timeZone) {
  return `${index + 1}. [${formatLocalClock(item.createdAt, timeZone)}] ${item.type} | ${item.tone ?? 'no tone'}\n   ${item.summary || '(no summary)'}`;
}

function renderCommunityItem(item, index, timeZone) {
  const lines = [
    `${index + 1}. [${formatLocalClock(item.createdAt, timeZone)}] ${item.npcId ?? 'unknown'} | ${item.venueSlug ?? 'no-venue'} | ${item.sourceKind ?? 'unknown'}`,
    `   summary: ${item.summary ?? '(no summary)'}`,
    `   cue: ${item.cue ?? '(no cue)'}`,
    `   handling: ${item.handling}`,
    `   mention: ${item.mentionPolicy ?? 'n/a'} | freshness: ${item.freshnessScore ?? 'n/a'}`,
  ];
  if (item.tags.length > 0) {
    lines.push(`   tags: ${item.tags.join(', ')}`);
  }
  return lines.join('\n');
}

function renderDirectContinuity(item, index) {
  return `${index + 1}. ${item.summary}\n   latest line: ${item.latestLine}`;
}

function renderPublicContinuity(item, index) {
  return `${index + 1}. ${item.summary}\n   root line: ${item.rootLine}\n   latest line: ${item.latestLine}`;
}

function renderMarkdown(summary) {
  return [
    '# Aqua Sea Diary Context',
    `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
    `- Diary date: ${summary.targetDate} (${summary.timeZone})`,
    `- Mirror mode: ${summary.mode ?? 'unknown'}`,
    `- Digest source: ${summary.source.digest.status}`,
    `- Scene layer: ${summary.source.scenes.status} (${summary.source.scenes.sameDayCount} same-day item${summary.source.scenes.sameDayCount === 1 ? '' : 's'})`,
    `- Community layer: ${summary.source.communityMemory.status} (${summary.source.communityMemory.sameDayCount} same-day note${summary.source.communityMemory.sameDayCount === 1 ? '' : 's'})`,
    '',
    '## Evidence Hierarchy',
    ...summary.evidenceHierarchy.map((item) => `- ${item}`),
    '',
    '## Visible Layer',
    summary.visibleLayer.aqua?.displayName ? `- Aqua: ${summary.visibleLayer.aqua.displayName}` : null,
    summary.visibleLayer.viewer?.displayName
      ? `- Viewer: ${summary.visibleLayer.viewer.displayName} (@${summary.visibleLayer.viewer.handle ?? 'unknown'})`
      : null,
    summary.visibleLayer.current?.label
      ? `- Current: ${summary.visibleLayer.current.label}${summary.visibleLayer.current.tone ? ` (${summary.visibleLayer.current.tone})` : ''}`
      : '- Current: not mirrored',
    `- Environment: ${summary.visibleLayer.environment?.summary ?? 'not mirrored'}`,
    `- Visible sea events: ${summary.visibleLayer.counts?.total ?? 0}`,
    `- Mirrored DM continuity: ${summary.visibleLayer.continuityCounts?.directThreads ?? 0} thread(s), ${summary.visibleLayer.continuityCounts?.directLines ?? 0} line(s)`,
    `- Mirrored public continuity: ${summary.visibleLayer.continuityCounts?.publicThreads ?? 0} thread(s), ${summary.visibleLayer.continuityCounts?.publicLines ?? 0} line(s)`,
    '',
    '### Notable Sea Motion',
    ...(summary.visibleLayer.notableEvents.length
      ? summary.visibleLayer.notableEvents.map((item, index) => renderNotableEvent(item, index, summary.timeZone))
      : ['- No visible same-day sea motion was recovered.']),
    '',
    '### Visible Reflection Seeds',
    ...(summary.visibleLayer.reflectionSeeds.length
      ? summary.visibleLayer.reflectionSeeds.map((item) => `- ${item}`)
      : ['- None']),
    '',
    '## Private Scenes',
    ...(summary.privateSceneLayer.items.length
      ? summary.privateSceneLayer.items.map((item, index) => renderSceneItem(item, index, summary.timeZone))
      : ['- No same-day gateway-private scene was recovered.']),
    '',
    '## Private Community Recall',
    ...(summary.privateCommunityLayer.items.length
      ? summary.privateCommunityLayer.items.map((item, index) => renderCommunityItem(item, index, summary.timeZone))
      : ['- No same-day community-memory note was recovered.']),
    '',
    '## Local Continuity Scaffold',
    `- Activity: ${summary.localSynthesisLayer.seaMood?.activitySummary ?? 'No activity summary available.'}`,
    `- Balance: ${summary.localSynthesisLayer.seaMood?.balance ?? 'No balance summary available.'}`,
    '',
    '### Self Motion',
    ...(summary.localSynthesisLayer.selfMotion.length
      ? summary.localSynthesisLayer.selfMotion.map((item) => `- ${item}`)
      : ['- None']),
    '',
    '### Other Voices',
    ...(summary.localSynthesisLayer.otherVoices.length
      ? summary.localSynthesisLayer.otherVoices.map((item) => `- ${item}`)
      : ['- None']),
    '',
    '### Direct Continuity',
    ...(summary.localSynthesisLayer.directContinuity.length
      ? summary.localSynthesisLayer.directContinuity.map(renderDirectContinuity)
      : ['- No mirrored DM continuity scaffold for this date.']),
    '',
    '### Public Continuity',
    ...(summary.localSynthesisLayer.publicContinuity.length
      ? summary.localSynthesisLayer.publicContinuity.map(renderPublicContinuity)
      : ['- No mirrored public continuity scaffold for this date.']),
    '',
    '## Diary Reflection Seeds',
    ...(summary.diaryReflectionSeeds.length ? summary.diaryReflectionSeeds.map((item) => `- ${item}`) : ['- None']),
    '',
    '## Diary Caveats',
    ...(summary.diaryCaveats.length ? summary.diaryCaveats.map((item) => `- ${item}`) : ['- None']),
    summary.warnings.length
      ? ''
      : null,
    summary.warnings.length ? '## Warnings' : null,
    ...(summary.warnings.length ? summary.warnings.map((item) => `- ${item}`) : []),
  ]
    .filter(Boolean)
    .join('\n');
}

export async function generateSeaDiaryContext(
  options = {},
  {
    loadHostedConfigFn = loadHostedConfig,
    requestJsonFn = requestJson,
  } = {},
) {
  const normalizedOptions = normalizeOptions(options);
  const synthesisResult = await generateMemorySynthesis({
    workspaceRoot: normalizedOptions.workspaceRoot,
    configPath: normalizedOptions.configPath,
    mirrorDir: normalizedOptions.mirrorDir,
    stateFile: normalizedOptions.stateFile,
    expectMode: normalizedOptions.expectMode,
    date: normalizedOptions.date,
    timeZone: normalizedOptions.timeZone,
    digestRoot: normalizedOptions.digestRoot,
    maxEvents: normalizedOptions.maxEvents,
    buildIfMissing: normalizedOptions.buildIfMissing,
    writeArtifact: normalizedOptions.writeArtifact,
    artifactRoot: normalizedOptions.synthesisRoot,
  });

  const sceneLayer = await loadSceneLayer(normalizedOptions, {
    loadHostedConfigFn,
    requestJsonFn,
  });
  const communityLayer = await loadCommunityMemoryLayer(normalizedOptions, synthesisResult.paths);
  const summary = buildSeaDiaryContext({
    digestSummary: synthesisResult.digestSource.summary,
    synthesisSummary: synthesisResult.summary,
    digestSource: synthesisResult.digestSource,
    sceneLayer,
    communityLayer,
    options: normalizedOptions,
  });
  const markdown = renderMarkdown(summary);
  let artifactPaths = null;

  if (normalizedOptions.writeArtifact) {
    artifactPaths = await writeSeaDiaryContextArtifacts({
      summary,
      markdown,
      paths: synthesisResult.paths,
      targetDate: summary.targetDate ?? normalizedOptions.date,
      artifactRoot: normalizedOptions.artifactRoot,
    });
  }

  return {
    summary,
    markdown,
    artifactPaths,
    synthesisResult,
    options: normalizedOptions,
  };
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const result = await generateSeaDiaryContext(options);

  if (result.options.format === 'json') {
    console.log(
      JSON.stringify(
        result.artifactPaths
          ? {
              ...result.summary,
              artifacts: {
                seaDiaryContext: result.artifactPaths,
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
  buildSeaDiaryContext,
  parseOptions,
  renderMarkdown as renderSeaDiaryContextMarkdown,
  resolveSeaDiaryContextArtifactPaths,
};

if (!process.argv.includes('--test') && process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
