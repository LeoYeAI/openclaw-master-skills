#!/usr/bin/env node

import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

import { resolveDailyIntentArtifactPaths } from './aqua-daily-intent.mjs';
import { resolveMirrorPaths } from './aqua-mirror-common.mjs';
import { resolveLifeLoopWriteBackPaths } from './aqua-life-loop-writeback.mjs';
import { formatTimestamp, parseArgValue, resolveWorkspaceRoot } from './hosted-aqua-common.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);
const VALID_VIEWS = new Set(['full', 'brief']);

export const DEFAULT_LIFE_LOOP_BRIEF_MODE_LIMIT = 4;
export const DEFAULT_LIFE_LOOP_BRIEF_OPEN_LOOP_LIMIT = 4;
export const DEFAULT_LIFE_LOOP_BRIEF_SOURCE_REF_LIMIT = 4;
export const DEFAULT_LIFE_LOOP_BRIEF_NOTE_LIMIT = 4;
export const DEFAULT_LIFE_LOOP_BRIEF_HOOK_LIMIT = 3;

function printHelp() {
  console.log(`Usage: aqua-life-loop-read.mjs [options]

Options:
  --workspace-root <path>   OpenClaw workspace root
  --config-path <path>      Hosted Aqua config path
  --mirror-dir <path>       Mirror root override (used to derive life-loop roots)
  --daily-intent-dir <path> Daily-intent artifact root override
  --writeback-dir <path>    Write-back artifact root override
  --format <fmt>            json|markdown (default: markdown)
  --view <view>             full|brief (default: full)
  --help                    Show this message

Notes:
  - This command reads local profile-scoped life-loop artifacts only.
  - It never calls live Aqua APIs.
`);
}

export function parseOptions(argv) {
  const options = {
    configPath: process.env.AQUACLAW_HOSTED_CONFIG || null,
    dailyIntentDir: null,
    format: 'markdown',
    mirrorDir: process.env.AQUACLAW_MIRROR_DIR || null,
    view: 'full',
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT || null,
    writeBackDir: null,
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
    if (arg.startsWith('--daily-intent-dir')) {
      options.dailyIntentDir = parseArgValue(argv, index, arg, '--daily-intent-dir').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--writeback-dir')) {
      options.writeBackDir = parseArgValue(argv, index, arg, '--writeback-dir').trim();
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
    if (arg.startsWith('--view')) {
      options.view = parseArgValue(argv, index, arg, '--view').trim().toLowerCase();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }

    throw new Error(`unknown option: ${arg}`);
  }

  options.workspaceRoot = resolveWorkspaceRoot(options.workspaceRoot);
  if (!VALID_FORMATS.has(options.format)) {
    throw new Error('--format must be json or markdown');
  }
  if (!VALID_VIEWS.has(options.view)) {
    throw new Error('--view must be full or brief');
  }

  return options;
}

function normalizeText(value) {
  return String(value ?? '').replace(/\s+/gu, ' ').trim();
}

function uniqueStrings(items) {
  return [...new Set((Array.isArray(items) ? items : []).filter((item) => typeof item === 'string' && item.trim()).map((item) => item.trim()))];
}

function summarizeVisibility(exposure, mentionPolicy) {
  return exposure === 'private_only' || mentionPolicy === 'private_only';
}

function summarizeSourceRefForOverview(ref) {
  const privateOnly = summarizeVisibility(ref?.exposure ?? null, ref?.mentionPolicy ?? null);
  const summary = normalizeText(ref?.summary);
  return {
    id: ref?.id ?? null,
    layer: ref?.layer ?? null,
    kind: ref?.kind ?? null,
    createdAt: ref?.createdAt ?? null,
    exposure: ref?.exposure ?? null,
    mentionPolicy: ref?.mentionPolicy ?? null,
    targetHandle: ref?.targetHandle ?? null,
    targetGatewayId: ref?.targetGatewayId ?? null,
    triggerKind: ref?.triggerKind ?? null,
    summary: privateOnly ? null : summary || null,
    summaryVisible: !privateOnly && Boolean(summary),
    redactionReason: privateOnly ? 'private_only' : summary ? null : 'missing_summary',
  };
}

function summarizeNoteForOverview(note) {
  const effectiveExposure = note?.effectiveExposure ?? null;
  const mentionPolicy = note?.mentionPolicy ?? null;
  const privateOnly = effectiveExposure === 'kept_private' || mentionPolicy === 'private_only';
  const summary = normalizeText(note?.summary);
  return {
    id: note?.id ?? null,
    sourceKind: note?.sourceKind ?? null,
    venueSlug: note?.venueSlug ?? null,
    mentionPolicy,
    effectiveExposure,
    freshnessScore: Number.isFinite(note?.freshnessScore) ? note.freshnessScore : null,
    used: Boolean(note?.used),
    summary: privateOnly ? null : summary || null,
    summaryVisible: !privateOnly && Boolean(summary),
    redactionReason: privateOnly ? 'private_only' : summary ? null : 'missing_summary',
  };
}

function summarizeOpenLoop(loop) {
  return {
    id: loop?.id ?? null,
    lane: loop?.lane ?? null,
    targetHandle: loop?.targetHandle ?? null,
    targetGatewayId: loop?.targetGatewayId ?? null,
    conversationId: loop?.conversationId ?? null,
    triggerKind: loop?.triggerKind ?? null,
    summary: loop?.summary ?? null,
    cue: loop?.cue ?? null,
    rationale: loop?.rationale ?? null,
    sourceRefIds: uniqueStrings(loop?.sourceRefIds),
  };
}

function summarizeMode(mode) {
  return {
    mode: mode?.mode ?? null,
    score: Number.isFinite(mode?.score) ? mode.score : null,
    summary: mode?.summary ?? null,
    sourceRefIds: uniqueStrings(mode?.sourceRefIds),
  };
}

function summarizeNewHook(hook) {
  return {
    id: hook?.id ?? null,
    lane: hook?.lane ?? null,
    kind: hook?.kind ?? null,
    createdAt: hook?.createdAt ?? null,
    targetHandle: hook?.targetHandle ?? null,
    targetGatewayId: hook?.targetGatewayId ?? null,
    conversationId: hook?.conversationId ?? null,
    summary: hook?.summary ?? null,
    cue: hook?.cue ?? null,
  };
}

function summarizeLatestOutput(output) {
  if (!output || typeof output !== 'object') {
    return null;
  }

  return {
    kind: output.kind ?? null,
    actionId: output.actionId ?? null,
    createdAt: output.createdAt ?? null,
    mode: output.mode ?? null,
    tone: output.tone ?? null,
    bodyPreview: output.bodyPreview ?? null,
    targetGatewayHandle: output.targetGatewayHandle ?? null,
    targetGatewayId: output.targetGatewayId ?? null,
    conversationId: output.conversationId ?? null,
    rootExpressionId: output.rootExpressionId ?? null,
    replyToExpressionId: output.replyToExpressionId ?? null,
  };
}

function describeStatus(status, reason = null) {
  if (status === 'available') {
    return 'available';
  }
  if (status === 'missing') {
    return reason === 'missing_root' ? 'missing (root not created yet)' : 'missing';
  }
  if (status === 'invalid') {
    return `invalid (${reason ?? 'invalid_json'})`;
  }
  return status ?? 'unknown';
}

function formatActionLabel(action) {
  if (!action) {
    return 'none';
  }
  const target = action.targetGatewayHandle ?? action.targetGatewayId ?? action.conversationId ?? null;
  const modePart = action.mode ? `/${action.mode}` : '';
  return `${action.kind ?? 'action'}${modePart}${target ? ` -> ${target}` : ''}`;
}

async function readJsonArtifact(filePath) {
  try {
    const raw = await readFile(filePath, 'utf8');
    return {
      status: 'available',
      reason: null,
      value: JSON.parse(raw),
    };
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return {
        status: 'missing',
        reason: 'missing_file',
        value: null,
      };
    }
    if (error instanceof SyntaxError) {
      return {
        status: 'invalid',
        reason: 'invalid_json',
        value: null,
      };
    }
    throw error;
  }
}

async function findLatestDailyIntentDate(root) {
  try {
    const entries = await readdir(root, { withFileTypes: true });
    const dates = entries
      .filter((entry) => entry.isFile() && /^\d{4}-\d{2}-\d{2}\.json$/u.test(entry.name))
      .map((entry) => entry.name.slice(0, -'.json'.length))
      .sort((left, right) => right.localeCompare(left));
    return {
      rootExists: true,
      targetDate: dates[0] ?? null,
    };
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return {
        rootExists: false,
        targetDate: null,
      };
    }
    throw error;
  }
}

export function resolveLifeLoopReadPaths({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
  mirrorDir = process.env.AQUACLAW_MIRROR_DIR,
  dailyIntentDir = null,
  writeBackDir = null,
} = {}) {
  const mirrorPaths = resolveMirrorPaths({
    workspaceRoot,
    configPath,
    mirrorDir,
  });
  const baseRoot = path.dirname(mirrorPaths.mirrorRoot);
  const dailyIntentRoot = dailyIntentDir
    ? path.resolve(dailyIntentDir)
    : resolveDailyIntentArtifactPaths(mirrorPaths, '0000-00-00').root;
  const writeBackArtifactRoot = writeBackDir ? path.resolve(writeBackDir) : path.join(baseRoot, 'life-loop', 'writeback');
  const writeBackPaths = resolveLifeLoopWriteBackPaths({
    workspaceRoot: mirrorPaths.workspaceRoot,
    configPath,
    artifactRoot: writeBackArtifactRoot,
  });

  return {
    workspaceRoot: mirrorPaths.workspaceRoot,
    configPath: writeBackPaths.configPath,
    profileId: writeBackPaths.profileId ?? null,
    selectionKind: writeBackPaths.selectionKind,
    mirrorRoot: mirrorPaths.mirrorRoot,
    baseRoot,
    dailyIntentRoot,
    writeBackRoot: writeBackPaths.root,
    writeBackLatestPath: writeBackPaths.latestPath,
  };
}

async function loadLatestDailyIntent(paths) {
  const latest = await findLatestDailyIntentDate(paths.dailyIntentRoot);
  if (!latest.rootExists) {
    return {
      status: 'missing',
      reason: 'missing_root',
      artifactPaths: {
        root: paths.dailyIntentRoot,
        jsonPath: null,
        markdownPath: null,
      },
      summary: null,
    };
  }
  if (!latest.targetDate) {
    return {
      status: 'missing',
      reason: 'no_artifacts',
      artifactPaths: {
        root: paths.dailyIntentRoot,
        jsonPath: null,
        markdownPath: null,
      },
      summary: null,
    };
  }

  const artifactPaths = {
    root: paths.dailyIntentRoot,
    jsonPath: path.join(paths.dailyIntentRoot, `${latest.targetDate}.json`),
    markdownPath: path.join(paths.dailyIntentRoot, `${latest.targetDate}.md`),
  };
  const payload = await readJsonArtifact(artifactPaths.jsonPath);

  return {
    status: payload.status,
    reason: payload.reason,
    artifactPaths,
    summary: payload.value,
  };
}

async function loadLatestWriteBack(paths) {
  const payload = await readJsonArtifact(paths.writeBackLatestPath);
  return {
    status: payload.status,
    reason: payload.reason === 'missing_file' ? 'missing_latest' : payload.reason,
    latestPath: paths.writeBackLatestPath,
    entryPath: payload.value?.recordedDate ? path.join(paths.writeBackRoot, `${payload.value.recordedDate}.ndjson`) : null,
    entry: payload.value,
  };
}

function buildLifeLoopOverview({ dailyIntentSummary, writeBackEntry }) {
  const dailyIntent = dailyIntentSummary && typeof dailyIntentSummary === 'object' ? dailyIntentSummary : null;
  const latestWriteBack = writeBackEntry && typeof writeBackEntry === 'object' ? writeBackEntry : null;
  const sourceRefs = (Array.isArray(latestWriteBack?.dailyIntent?.sourceRefs) ? latestWriteBack.dailyIntent.sourceRefs : []).map(
    summarizeSourceRefForOverview,
  );
  const notes = (Array.isArray(latestWriteBack?.communityMemory?.notes) ? latestWriteBack.communityMemory.notes : []).map(
    summarizeNoteForOverview,
  );

  return {
    dailyIntent: {
      targetDate: dailyIntent?.targetDate ?? null,
      generatedAt: dailyIntent?.generatedAt ?? null,
      timeZone: dailyIntent?.timeZone ?? null,
      mode: dailyIntent?.mode ?? null,
      energyProfile: dailyIntent?.energyProfile
        ? {
            level: dailyIntent.energyProfile.level ?? null,
            posture: dailyIntent.energyProfile.posture ?? null,
            summary: dailyIntent.energyProfile.summary ?? null,
          }
        : null,
      dominantModes: (Array.isArray(dailyIntent?.dominantModes) ? dailyIntent.dominantModes : []).map(summarizeMode),
      openLoops: (Array.isArray(dailyIntent?.openLoops) ? dailyIntent.openLoops : []).map(summarizeOpenLoop),
      topicHooks: uniqueStrings((Array.isArray(dailyIntent?.topicHooks) ? dailyIntent.topicHooks : []).map((item) => item?.id)),
      relationshipHooks: uniqueStrings((Array.isArray(dailyIntent?.relationshipHooks) ? dailyIntent.relationshipHooks : []).map((item) => item?.id)),
      avoidance: uniqueStrings((Array.isArray(dailyIntent?.avoidance) ? dailyIntent.avoidance : []).map((item) => item?.id)),
    },
    latestAction: latestWriteBack
      ? {
          entryId: latestWriteBack.id ?? null,
          recordedAt: latestWriteBack.recordedAt ?? null,
          recordedDate: latestWriteBack.recordedDate ?? null,
          lane: latestWriteBack.lane ?? null,
          output: summarizeLatestOutput(latestWriteBack.output),
          topicHookIds: uniqueStrings(latestWriteBack?.dailyIntent?.topicHookIds),
          relationshipHookIds: uniqueStrings(latestWriteBack?.dailyIntent?.relationshipHookIds),
          resolvedOpenLoopIds: uniqueStrings(latestWriteBack?.dailyIntent?.resolvedOpenLoopIds),
          continuedOpenLoopIds: uniqueStrings(latestWriteBack?.dailyIntent?.continuedOpenLoopIds),
          sourceRefIds: uniqueStrings(latestWriteBack?.dailyIntent?.sourceRefIds),
          sourceRefs,
          retrievedNoteIds: uniqueStrings(latestWriteBack?.communityMemory?.retrievedNoteIds),
          usedNoteIds: uniqueStrings(latestWriteBack?.communityMemory?.usedNoteIds),
          notes,
          newUnresolvedHooks: (Array.isArray(latestWriteBack?.dailyIntent?.newUnresolvedHooks)
            ? latestWriteBack.dailyIntent.newUnresolvedHooks
            : []
          ).map(summarizeNewHook),
        }
      : null,
  };
}

export function summarizeLifeLoopForBrief(result) {
  return {
    mode: 'brief',
    scope: 'local_profile_artifacts',
    paths: {
      profileId: result.paths.profileId ?? 'legacy',
      selectionKind: result.paths.selectionKind,
      dailyIntentRoot: result.paths.dailyIntentRoot,
      writeBackRoot: result.paths.writeBackRoot,
    },
    dailyIntent: {
      status: result.dailyIntent.status,
      reason: result.dailyIntent.reason,
      targetDate: result.overview.dailyIntent.targetDate,
      generatedAt: result.overview.dailyIntent.generatedAt,
      timeZone: result.overview.dailyIntent.timeZone,
      energyProfile: result.overview.dailyIntent.energyProfile,
      dominantModes: result.overview.dailyIntent.dominantModes.slice(0, DEFAULT_LIFE_LOOP_BRIEF_MODE_LIMIT),
      openLoops: result.overview.dailyIntent.openLoops.slice(0, DEFAULT_LIFE_LOOP_BRIEF_OPEN_LOOP_LIMIT),
    },
    latestWriteBack: {
      status: result.writeBack.status,
      reason: result.writeBack.reason,
      entryId: result.overview.latestAction?.entryId ?? null,
      recordedAt: result.overview.latestAction?.recordedAt ?? null,
      recordedDate: result.overview.latestAction?.recordedDate ?? null,
      lane: result.overview.latestAction?.lane ?? null,
      output: result.overview.latestAction?.output ?? null,
      topicHookIds: (result.overview.latestAction?.topicHookIds ?? []).slice(0, DEFAULT_LIFE_LOOP_BRIEF_HOOK_LIMIT),
      relationshipHookIds: (result.overview.latestAction?.relationshipHookIds ?? []).slice(0, DEFAULT_LIFE_LOOP_BRIEF_HOOK_LIMIT),
      resolvedOpenLoopIds: result.overview.latestAction?.resolvedOpenLoopIds ?? [],
      continuedOpenLoopIds: result.overview.latestAction?.continuedOpenLoopIds ?? [],
      sourceRefs: (result.overview.latestAction?.sourceRefs ?? []).slice(0, DEFAULT_LIFE_LOOP_BRIEF_SOURCE_REF_LIMIT),
      notes: (result.overview.latestAction?.notes ?? []).slice(0, DEFAULT_LIFE_LOOP_BRIEF_NOTE_LIMIT),
      newUnresolvedHooks: (result.overview.latestAction?.newUnresolvedHooks ?? []).slice(0, DEFAULT_LIFE_LOOP_BRIEF_HOOK_LIMIT),
    },
    warnings: [...result.warnings],
  };
}

function formatBriefSourceRefMarkdown(ref, index) {
  const lines = [
    `${index + 1}. [${formatTimestamp(ref.createdAt)}] ${ref.layer ?? 'unknown'} | ${ref.kind ?? 'unknown'} | ${ref.exposure ?? 'n/a'}`,
  ];
  if (ref.summaryVisible && ref.summary) {
    lines.push(`   summary: ${ref.summary}`);
  } else if (ref.redactionReason === 'private_only') {
    lines.push('   summary: (private-only source retained locally)');
  } else {
    lines.push('   summary: (no sharable summary)');
  }
  if (ref.targetHandle) {
    lines.push(`   target: ${ref.targetHandle}`);
  }
  if (ref.triggerKind) {
    lines.push(`   trigger: ${ref.triggerKind}`);
  }
  return lines.join('\n');
}

function formatBriefNoteMarkdown(note, index) {
  const lines = [
    `${index + 1}. ${note.id ?? 'unknown'} | ${note.effectiveExposure ?? 'unknown'} | freshness ${note.freshnessScore ?? 'n/a'}`,
  ];
  if (note.summaryVisible && note.summary) {
    lines.push(`   summary: ${note.summary}`);
  } else if (note.redactionReason === 'private_only') {
    lines.push('   summary: (private-only note retained locally)');
  } else {
    lines.push('   summary: (no sharable summary)');
  }
  if (note.venueSlug) {
    lines.push(`   venue: ${note.venueSlug}`);
  }
  lines.push(`   used: ${note.used ? 'yes' : 'no'} | mention: ${note.mentionPolicy ?? 'n/a'}`);
  return lines.join('\n');
}

function formatNewHookMarkdown(hook, index) {
  return `${index + 1}. ${hook.kind ?? 'unknown'}${hook.targetHandle ? ` -> ${hook.targetHandle}` : ''}: ${hook.summary ?? '(no summary)'}`;
}

export function formatLifeLoopBriefMarkdown(
  summary,
  {
    title = '## Life Loop',
  } = {},
) {
  const lines = [
    title,
    `- Profile: ${summary.paths.profileId ?? 'legacy'}`,
    `- Daily intent: ${describeStatus(summary.dailyIntent.status, summary.dailyIntent.reason)}`,
    `- Latest write-back: ${describeStatus(summary.latestWriteBack.status, summary.latestWriteBack.reason)}`,
  ];

  if (summary.dailyIntent.targetDate) {
    lines.push(`- Intent date: ${summary.dailyIntent.targetDate} (${summary.dailyIntent.timeZone ?? 'UTC'})`);
  }
  if (summary.dailyIntent.generatedAt) {
    lines.push(`- Intent generated at: ${formatTimestamp(summary.dailyIntent.generatedAt)}`);
  }
  if (summary.dailyIntent.energyProfile) {
    lines.push(
      `- Energy: ${summary.dailyIntent.energyProfile.level ?? 'unknown'} | ${summary.dailyIntent.energyProfile.posture ?? 'unknown'} | ${summary.dailyIntent.energyProfile.summary ?? 'n/a'}`,
    );
  }
  if (summary.latestWriteBack.recordedAt) {
    lines.push(`- Latest action at: ${formatTimestamp(summary.latestWriteBack.recordedAt)}`);
  }
  if (summary.latestWriteBack.output) {
    lines.push(`- Latest action: ${formatActionLabel(summary.latestWriteBack.output)}`);
  }

  lines.push('');
  lines.push('### Dominant Modes');
  if (summary.dailyIntent.dominantModes.length > 0) {
    lines.push(
      ...summary.dailyIntent.dominantModes.map((item) => `- ${item.mode ?? 'unknown'} (score ${item.score ?? 'n/a'})${item.summary ? `: ${item.summary}` : ''}`),
    );
  } else {
    lines.push('- No local daily-intent dominant modes yet.');
  }

  lines.push('');
  lines.push('### Open Loops');
  if (summary.dailyIntent.openLoops.length > 0) {
    lines.push(
      ...summary.dailyIntent.openLoops.map((loop) =>
        `- ${loop.id ?? 'unknown'} | ${loop.lane ?? 'unknown'}${loop.targetHandle ? ` | ${loop.targetHandle}` : ''}: ${loop.summary ?? '(no summary)'}`,
      ),
    );
  } else {
    lines.push('- No open-loop summary available.');
  }

  lines.push('');
  lines.push('### Latest Source Usage');
  if (summary.latestWriteBack.sourceRefs.length > 0) {
    lines.push(...summary.latestWriteBack.sourceRefs.map((ref, index) => formatBriefSourceRefMarkdown(ref, index)));
  } else {
    lines.push('- No source-ref usage recorded yet.');
  }

  lines.push('');
  lines.push('### Latest Note Usage');
  if (summary.latestWriteBack.notes.length > 0) {
    lines.push(...summary.latestWriteBack.notes.map((note, index) => formatBriefNoteMarkdown(note, index)));
  } else {
    lines.push('- No community-memory note usage recorded yet.');
  }

  lines.push('');
  lines.push('### Latest Outcomes');
  lines.push(`- Resolved open loops: ${summary.latestWriteBack.resolvedOpenLoopIds.join(', ') || 'none'}`);
  lines.push(`- Continued open loops: ${summary.latestWriteBack.continuedOpenLoopIds.join(', ') || 'none'}`);
  lines.push(`- Topic hooks used: ${summary.latestWriteBack.topicHookIds.join(', ') || 'none'}`);
  lines.push(`- Relationship hooks used: ${summary.latestWriteBack.relationshipHookIds.join(', ') || 'none'}`);
  if (summary.latestWriteBack.newUnresolvedHooks.length > 0) {
    lines.push(...summary.latestWriteBack.newUnresolvedHooks.map((hook, index) => formatNewHookMarkdown(hook, index)));
  } else {
    lines.push('- New unresolved hooks: none');
  }

  if (summary.warnings.length > 0) {
    lines.push('');
    lines.push('### Warnings');
    lines.push(...summary.warnings.map((warning) => `- ${warning}`));
  }

  return lines.join('\n');
}

function formatLifeLoopFullMarkdown(result) {
  const lines = [
    '## Life Loop',
    `- Profile: ${result.paths.profileId ?? 'legacy'}`,
    `- Selection: ${result.paths.selectionKind}`,
    `- Daily intent root: ${result.paths.dailyIntentRoot}`,
    `- Write-back root: ${result.paths.writeBackRoot}`,
    `- Daily intent artifact: ${describeStatus(result.dailyIntent.status, result.dailyIntent.reason)}`,
    `- Write-back latest: ${describeStatus(result.writeBack.status, result.writeBack.reason)}`,
  ];

  if (result.dailyIntent.artifactPaths?.jsonPath) {
    lines.push(`- Daily intent JSON: ${result.dailyIntent.artifactPaths.jsonPath}`);
  }
  if (result.writeBack.latestPath) {
    lines.push(`- Write-back latest JSON: ${result.writeBack.latestPath}`);
  }

  lines.push('');
  lines.push('### Daily Intent Overview');
  if (result.overview.dailyIntent.targetDate) {
    lines.push(`- Target date: ${result.overview.dailyIntent.targetDate} (${result.overview.dailyIntent.timeZone ?? 'UTC'})`);
    lines.push(`- Generated at: ${formatTimestamp(result.overview.dailyIntent.generatedAt)}`);
    lines.push(`- Energy: ${result.overview.dailyIntent.energyProfile?.level ?? 'unknown'} | ${result.overview.dailyIntent.energyProfile?.posture ?? 'unknown'}`);
    lines.push(`- Topic hooks: ${result.overview.dailyIntent.topicHooks.join(', ') || 'none'}`);
    lines.push(`- Relationship hooks: ${result.overview.dailyIntent.relationshipHooks.join(', ') || 'none'}`);
    lines.push(`- Avoidance: ${result.overview.dailyIntent.avoidance.join(', ') || 'none'}`);
  } else {
    lines.push('- No daily-intent artifact loaded.');
  }

  lines.push('');
  lines.push('### Dominant Modes');
  if (result.overview.dailyIntent.dominantModes.length > 0) {
    lines.push(
      ...result.overview.dailyIntent.dominantModes.map((item) =>
        `- ${item.mode ?? 'unknown'} (score ${item.score ?? 'n/a'})${item.summary ? `: ${item.summary}` : ''}`,
      ),
    );
  } else {
    lines.push('- None');
  }

  lines.push('');
  lines.push('### Open Loops');
  if (result.overview.dailyIntent.openLoops.length > 0) {
    lines.push(
      ...result.overview.dailyIntent.openLoops.map((loop) =>
        `- ${loop.id ?? 'unknown'} | ${loop.lane ?? 'unknown'}${loop.targetHandle ? ` | ${loop.targetHandle}` : ''}: ${loop.summary ?? '(no summary)'}`,
      ),
    );
  } else {
    lines.push('- None');
  }

  lines.push('');
  lines.push('### Latest Write Back');
  if (result.overview.latestAction) {
    lines.push(`- Recorded at: ${formatTimestamp(result.overview.latestAction.recordedAt)}`);
    lines.push(`- Lane: ${result.overview.latestAction.lane ?? 'unknown'}`);
    lines.push(`- Output: ${formatActionLabel(result.overview.latestAction.output)}`);
    lines.push(`- Resolved open loops: ${result.overview.latestAction.resolvedOpenLoopIds.join(', ') || 'none'}`);
    lines.push(`- Continued open loops: ${result.overview.latestAction.continuedOpenLoopIds.join(', ') || 'none'}`);
  } else {
    lines.push('- No write-back ledger entry loaded.');
  }

  lines.push('');
  lines.push('### Source Refs');
  if ((result.overview.latestAction?.sourceRefs ?? []).length > 0) {
    lines.push(...result.overview.latestAction.sourceRefs.map((ref, index) => formatBriefSourceRefMarkdown(ref, index)));
  } else {
    lines.push('- None');
  }

  lines.push('');
  lines.push('### Note Usage');
  if ((result.overview.latestAction?.notes ?? []).length > 0) {
    lines.push(...result.overview.latestAction.notes.map((note, index) => formatBriefNoteMarkdown(note, index)));
  } else {
    lines.push('- None');
  }

  lines.push('');
  lines.push('### New Hooks');
  if ((result.overview.latestAction?.newUnresolvedHooks ?? []).length > 0) {
    lines.push(...result.overview.latestAction.newUnresolvedHooks.map((hook, index) => formatNewHookMarkdown(hook, index)));
  } else {
    lines.push('- None');
  }

  if (result.warnings.length > 0) {
    lines.push('');
    lines.push('### Warnings');
    lines.push(...result.warnings.map((warning) => `- ${warning}`));
  }

  return lines.join('\n');
}

export async function readLifeLoop({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
  mirrorDir = process.env.AQUACLAW_MIRROR_DIR,
  dailyIntentDir = null,
  writeBackDir = null,
} = {}) {
  const paths = resolveLifeLoopReadPaths({
    workspaceRoot,
    configPath,
    mirrorDir,
    dailyIntentDir,
    writeBackDir,
  });
  const dailyIntent = await loadLatestDailyIntent(paths);
  const writeBack = await loadLatestWriteBack(paths);
  const warnings = [];

  if (dailyIntent.status === 'invalid') {
    warnings.push(`daily-intent artifact at ${dailyIntent.artifactPaths?.jsonPath ?? paths.dailyIntentRoot} could not be parsed`);
  }
  if (writeBack.status === 'invalid') {
    warnings.push(`write-back artifact at ${writeBack.latestPath} could not be parsed`);
  }
  if (dailyIntent.status === 'missing') {
    warnings.push('local daily-intent artifact is not available yet');
  }
  if (writeBack.status === 'missing') {
    warnings.push('local life-loop write-back ledger is not available yet');
  }

  return {
    scope: 'local_profile_artifacts',
    paths,
    dailyIntent,
    writeBack,
    overview: buildLifeLoopOverview({
      dailyIntentSummary: dailyIntent.summary,
      writeBackEntry: writeBack.entry,
    }),
    warnings,
  };
}

async function main(argv = process.argv.slice(2)) {
  const options = parseOptions(argv);
  const result = await readLifeLoop(options);
  const payload = options.view === 'brief' ? summarizeLifeLoopForBrief(result) : result;

  if (options.format === 'json') {
    console.log(JSON.stringify(payload, null, 2));
    return;
  }

  console.log(
    options.view === 'brief'
      ? formatLifeLoopBriefMarkdown(payload)
      : formatLifeLoopFullMarkdown(result),
  );
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  });
}
