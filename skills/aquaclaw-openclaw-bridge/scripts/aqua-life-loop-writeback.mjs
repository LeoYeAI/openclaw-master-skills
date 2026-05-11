#!/usr/bin/env node

import { randomUUID } from 'node:crypto';
import path from 'node:path';
import process from 'node:process';

import { appendNdjson, datePartitionFromIso, writeJsonFile } from './aqua-mirror-common.mjs';
import {
  resolveAquaclawStateRoot,
  resolveHostedConfigSelection,
  resolveWorkspaceRoot,
} from './hosted-aqua-common.mjs';

export const DEFAULT_LIFE_LOOP_DIR_NAME = 'life-loop';
export const DEFAULT_WRITEBACK_DIR_NAME = 'writeback';
export const WRITEBACK_VERSION = 1;

function normalizeText(value) {
  return String(value ?? '').replace(/\s+/gu, ' ').trim();
}

function previewText(value, limit = 220) {
  const normalized = normalizeText(value);
  if (!normalized) {
    return '';
  }
  if (normalized.length <= limit) {
    return normalized;
  }
  return `${normalized.slice(0, Math.max(limit - 1, 1)).trimEnd()}...`;
}

function uniqueStrings(items) {
  return [...new Set(items.filter((item) => typeof item === 'string' && item.trim()).map((item) => item.trim()))];
}

function normalizeHandleForComparison(value) {
  return String(value ?? '')
    .trim()
    .replace(/^@+/, '')
    .toLowerCase();
}

function formatHandle(value) {
  const handle = normalizeText(value).replace(/^@+/, '');
  return handle ? `@${handle}` : null;
}

function summarizeEnergyProfile(energyProfile) {
  if (!energyProfile || typeof energyProfile !== 'object') {
    return null;
  }
  return {
    level: typeof energyProfile.level === 'string' ? energyProfile.level : null,
    posture: typeof energyProfile.posture === 'string' ? energyProfile.posture : null,
    summary: typeof energyProfile.summary === 'string' ? energyProfile.summary : null,
  };
}

function summarizeHookIds(items) {
  return uniqueStrings((Array.isArray(items) ? items : []).map((item) => item?.id));
}

function collectSourceRefIdsFromDailyIntent(dailyIntentView) {
  if (!dailyIntentView || typeof dailyIntentView !== 'object') {
    return [];
  }

  return uniqueStrings([
    ...((Array.isArray(dailyIntentView.topicHooks) ? dailyIntentView.topicHooks : []).flatMap((item) => item?.sourceRefIds ?? [])),
    ...((Array.isArray(dailyIntentView.relationshipHooks) ? dailyIntentView.relationshipHooks : []).flatMap((item) => item?.sourceRefIds ?? [])),
    ...((Array.isArray(dailyIntentView.openLoops) ? dailyIntentView.openLoops : []).flatMap((item) => item?.sourceRefIds ?? [])),
    ...((Array.isArray(dailyIntentView.avoidance) ? dailyIntentView.avoidance : []).flatMap((item) => item?.sourceRefIds ?? [])),
    ...((Array.isArray(dailyIntentView.dominantModes) ? dailyIntentView.dominantModes : []).flatMap((item) => item?.sourceRefIds ?? [])),
    ...((Array.isArray(dailyIntentView.energyProfile?.sourceRefIds) ? dailyIntentView.energyProfile.sourceRefIds : [])),
  ]);
}

function resolveSourceRefs(dailyIntentSummary, sourceRefIds) {
  const refs = Array.isArray(dailyIntentSummary?.sourceRefs) ? dailyIntentSummary.sourceRefs : [];
  const byId = new Map(
    refs
      .filter((item) => typeof item?.id === 'string' && item.id.trim())
      .map((item) => [item.id.trim(), item]),
  );
  return sourceRefIds
    .map((id) => byId.get(id))
    .filter(Boolean)
    .map((item) => ({
      id: item.id,
      layer: item.layer ?? null,
      kind: item.kind ?? null,
      createdAt: item.createdAt ?? null,
      summary: item.summary ?? null,
      detail: item.detail ?? null,
      targetHandle: item.targetHandle ?? null,
      targetGatewayId: item.targetGatewayId ?? null,
      exposure: item.exposure ?? null,
      mentionPolicy: item.mentionPolicy ?? null,
      sourceKind: item.sourceKind ?? null,
      triggerKind: item.triggerKind ?? null,
      speakerRole: item.speakerRole ?? null,
    }));
}

function loopMatchesAction(loop, { lane, plan, allLoops }) {
  if (!loop || typeof loop !== 'object') {
    return false;
  }

  if (lane === 'public_expression') {
    if (plan?.mode !== 'reply') {
      return false;
    }
    const loopTarget = normalizeHandleForComparison(loop.targetHandle);
    const planTarget = normalizeHandleForComparison(plan?.replyToGatewayHandle);
    if (!loopTarget && !planTarget) {
      return allLoops.length === 1;
    }
    return loopTarget === planTarget;
  }

  const loopTargetHandle = normalizeHandleForComparison(loop.targetHandle);
  const planTargetHandle = normalizeHandleForComparison(plan?.targetGatewayHandle);
  const loopTargetGatewayId = String(loop?.targetGatewayId ?? '').trim();
  const planTargetGatewayId = String(plan?.targetGatewayId ?? '').trim();
  const loopConversationId = String(loop?.conversationId ?? '').trim();
  const planConversationId = String(plan?.conversationId ?? '').trim();

  if (!loopTargetHandle && !loopTargetGatewayId && !loopConversationId) {
    return allLoops.length === 1;
  }

  return (
    (loopTargetHandle && planTargetHandle && loopTargetHandle === planTargetHandle) ||
    (loopTargetGatewayId && planTargetGatewayId && loopTargetGatewayId === planTargetGatewayId) ||
    (loopConversationId && planConversationId && loopConversationId === planConversationId)
  );
}

function summarizeOpenLoopOutcomeStatus({ lane, plan, matched }) {
  if (matched && plan?.mode === 'reply') {
    return 'resolved';
  }
  if (matched) {
    return 'touched';
  }
  return 'unresolved';
}

function summarizeOpenLoopOutcomes({ dailyIntentView, lane, plan }) {
  const loops = Array.isArray(dailyIntentView?.openLoops) ? dailyIntentView.openLoops : [];
  const outcomes = loops.map((loop) => {
    const matched = loopMatchesAction(loop, {
      lane,
      plan,
      allLoops: loops,
    });
    const status = summarizeOpenLoopOutcomeStatus({
      lane,
      plan,
      matched,
    });
    return {
      id: loop.id ?? null,
      lane: loop.lane ?? null,
      status,
      targetHandle: loop.targetHandle ?? null,
      targetGatewayId: loop.targetGatewayId ?? null,
      conversationId: loop.conversationId ?? null,
      triggerKind: loop.triggerKind ?? null,
      summary: loop.summary ?? null,
      rationale:
        status === 'resolved'
          ? lane === 'public_expression'
            ? 'A reply was successfully sent into the same public seam this loop was pointing at.'
            : 'A DM reply was successfully sent into the same private seam this loop was pointing at.'
          : status === 'touched'
            ? 'This action touched the same lane but did not clearly close the loop.'
            : 'This loop remained available after the action because the target did not clearly match.',
    };
  });

  return {
    outcomes,
    addressedOpenLoopIds: uniqueStrings(outcomes.map((item) => (item.status === 'resolved' || item.status === 'touched' ? item.id : null))),
    resolvedOpenLoopIds: uniqueStrings(outcomes.map((item) => (item.status === 'resolved' ? item.id : null))),
    continuedOpenLoopIds: uniqueStrings(outcomes.map((item) => (item.status === 'touched' || item.status === 'unresolved' ? item.id : null))),
  };
}

function buildNewUnresolvedHooks({ lane, plan, actionResult, outputBody, at }) {
  const actionId = typeof actionResult?.id === 'string' && actionResult.id.trim() ? actionResult.id.trim() : null;
  const createdAt = actionResult?.createdAt ?? at;
  const cue = previewText(outputBody || actionResult?.body || actionResult?.summary || '', 180) || null;
  const generatedId = actionId ? `generated-${lane}-${actionId}` : `generated-${lane}-${randomUUID()}`;

  if (lane === 'public_expression') {
    return [
      {
        id: generatedId,
        lane: 'public_reply',
        kind: plan?.mode === 'reply' ? 'public_thread_callback' : 'public_callback',
        status: 'new',
        createdAt,
        sourceActionId: actionId,
        targetHandle: formatHandle(plan?.replyToGatewayHandle),
        targetGatewayId: typeof plan?.replyToGatewayId === 'string' && plan.replyToGatewayId.trim() ? plan.replyToGatewayId.trim() : null,
        rootExpressionId: typeof plan?.rootExpressionId === 'string' && plan.rootExpressionId.trim() ? plan.rootExpressionId.trim() : actionId,
        replyToExpressionId:
          typeof plan?.replyToExpressionId === 'string' && plan.replyToExpressionId.trim() ? plan.replyToExpressionId.trim() : null,
        summary:
          plan?.mode === 'reply'
            ? `This new public reply may keep the thread${formatHandle(plan?.replyToGatewayHandle) ? ` with ${formatHandle(plan?.replyToGatewayHandle)}` : ''} open.`
            : 'This new public line may create a fresh public callback seam.',
        cue,
        rationale:
          plan?.mode === 'reply'
            ? 'A self-authored reply can create a new callback seam if the public thread keeps moving.'
            : 'A fresh public line can become a new callback or topic seam if others answer it.',
      },
    ];
  }

  return [
    {
      id: generatedId,
      lane: 'dm',
      kind: plan?.mode === 'reply' ? 'dm_callback' : 'relationship_callback',
      status: 'new',
      createdAt,
      sourceActionId: actionId,
      targetHandle: formatHandle(plan?.targetGatewayHandle),
      targetGatewayId: typeof plan?.targetGatewayId === 'string' && plan.targetGatewayId.trim() ? plan.targetGatewayId.trim() : null,
      conversationId: typeof plan?.conversationId === 'string' && plan.conversationId.trim() ? plan.conversationId.trim() : null,
      summary:
        plan?.mode === 'reply'
          ? `This outgoing DM may keep the thread${formatHandle(plan?.targetGatewayHandle) ? ` with ${formatHandle(plan?.targetGatewayHandle)}` : ''} alive.`
          : `This reopened DM may create a fresh private callback seam${formatHandle(plan?.targetGatewayHandle) ? ` with ${formatHandle(plan?.targetGatewayHandle)}` : ''}.`,
      cue,
      rationale:
        plan?.mode === 'reply'
          ? 'A self-authored DM reply can still leave a new callback seam if the other side answers later.'
          : 'A reopened private thread creates a fresh relationship seam if the other side engages again.',
    },
  ];
}

function resolveEffectiveExposure(note) {
  const mentionPolicy = typeof note?.mentionPolicy === 'string' ? note.mentionPolicy : null;
  if (mentionPolicy === 'private_only') {
    return 'kept_private';
  }
  if (mentionPolicy === 'paraphrase_ok') {
    return 'paraphrase_only';
  }
  if (mentionPolicy === 'public_ok') {
    return 'public_ok';
  }
  return 'unknown';
}

function summarizeCommunityMemoryNotes(notes, usedNoteIds) {
  const usedSet = new Set(uniqueStrings(usedNoteIds));
  return (Array.isArray(notes) ? notes : [])
    .filter((note) => typeof note?.id === 'string' && note.id.trim())
    .map((note) => ({
      id: note.id.trim(),
      sourceKind: typeof note?.sourceKind === 'string' ? note.sourceKind : null,
      venueSlug: typeof note?.venueSlug === 'string' ? note.venueSlug : null,
      mentionPolicy: typeof note?.mentionPolicy === 'string' ? note.mentionPolicy : null,
      effectiveExposure: resolveEffectiveExposure(note),
      freshnessScore: Number.isFinite(note?.freshnessScore) ? note.freshnessScore : null,
      used: usedSet.has(note.id.trim()),
      summary: typeof note?.summary === 'string' && note.summary.trim() ? note.summary.trim() : null,
    }));
}

function summarizeActionOutput({ lane, plan, actionResult, outputBody, at }) {
  if (lane === 'public_expression') {
    return {
      kind: 'public_expression',
      actionId: typeof actionResult?.id === 'string' ? actionResult.id : null,
      createdAt: actionResult?.createdAt ?? at,
      mode: typeof plan?.mode === 'string' ? plan.mode : null,
      tone: typeof plan?.tone === 'string' ? plan.tone : null,
      bodyPreview: previewText(outputBody || actionResult?.body || actionResult?.summary || '', 220) || null,
      replyToExpressionId: typeof plan?.replyToExpressionId === 'string' ? plan.replyToExpressionId : null,
      rootExpressionId: typeof plan?.rootExpressionId === 'string' ? plan.rootExpressionId : null,
      targetGatewayId:
        typeof plan?.replyToGatewayId === 'string' && plan.replyToGatewayId.trim() ? plan.replyToGatewayId.trim() : null,
      targetGatewayHandle:
        typeof plan?.replyToGatewayHandle === 'string' && plan.replyToGatewayHandle.trim()
          ? `@${plan.replyToGatewayHandle.trim().replace(/^@+/, '')}`
          : null,
    };
  }

  return {
    kind: 'direct_message',
    actionId: typeof actionResult?.id === 'string' ? actionResult.id : null,
    createdAt: actionResult?.createdAt ?? at,
    mode: typeof plan?.mode === 'string' ? plan.mode : null,
    tone: typeof plan?.tone === 'string' ? plan.tone : null,
    bodyPreview: previewText(outputBody || actionResult?.body || '', 220) || null,
    conversationId: typeof plan?.conversationId === 'string' ? plan.conversationId : null,
    targetGatewayId:
      typeof plan?.targetGatewayId === 'string' && plan.targetGatewayId.trim() ? plan.targetGatewayId.trim() : null,
    targetGatewayHandle:
      typeof plan?.targetGatewayHandle === 'string' && plan.targetGatewayHandle.trim()
        ? `@${plan.targetGatewayHandle.trim().replace(/^@+/, '')}`
        : null,
  };
}

export function resolveLifeLoopWriteBackPaths({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
  artifactRoot = null,
} = {}) {
  const selection = resolveHostedConfigSelection({
    workspaceRoot,
    configPath,
  });
  const resolvedWorkspaceRoot = resolveWorkspaceRoot(selection.workspaceRoot);
  const baseRoot = selection.profileRoot ?? resolveAquaclawStateRoot(resolvedWorkspaceRoot);
  const root = artifactRoot
    ? path.resolve(artifactRoot)
    : path.join(baseRoot, DEFAULT_LIFE_LOOP_DIR_NAME, DEFAULT_WRITEBACK_DIR_NAME);

  return {
    workspaceRoot: resolvedWorkspaceRoot,
    configPath: selection.configPath,
    profileId: selection.profileId ?? null,
    profileRoot: selection.profileRoot ?? null,
    selectionKind: selection.selectionKind,
    root,
    latestPath: path.join(root, 'latest.json'),
  };
}

export function resolveLifeLoopWriteBackEntryPath(paths, at) {
  return path.join(paths.root, `${datePartitionFromIso(at)}.ndjson`);
}

export function buildLifeLoopWriteBackRecord({
  lane,
  origin = 'hosted_pulse',
  at = new Date().toISOString(),
  profileId = null,
  plan = null,
  actionResult = null,
  outputBody = '',
  dailyIntentView = null,
  dailyIntentSummary = null,
  dailyIntentArtifactPaths = null,
  communityIntent = null,
  communityNotes = [],
  usedNoteIds = [],
} = {}) {
  if (lane !== 'public_expression' && lane !== 'direct_message') {
    throw new Error('lane must be public_expression or direct_message');
  }

  const sourceRefIds = collectSourceRefIdsFromDailyIntent(dailyIntentView);
  const resolvedSourceRefs = resolveSourceRefs(dailyIntentSummary, sourceRefIds);
  const openLoopState = summarizeOpenLoopOutcomes({
    dailyIntentView,
    lane,
    plan,
  });
  const newUnresolvedHooks = buildNewUnresolvedHooks({
    lane,
    plan,
    actionResult,
    outputBody,
    at,
  });

  return {
    version: WRITEBACK_VERSION,
    id: `writeback-${randomUUID()}`,
    recordedAt: at,
    recordedDate: datePartitionFromIso(at),
    origin,
    lane,
    profileId,
    output: summarizeActionOutput({
      lane,
      plan,
      actionResult,
      outputBody,
      at,
    }),
    dailyIntent: dailyIntentView
      ? {
          targetDate: dailyIntentView.targetDate ?? null,
          sourceStatus: dailyIntentView.sourceStatus ?? null,
          support: dailyIntentView.support
            ? {
                status: dailyIntentView.support.status ?? null,
                summary: dailyIntentView.support.summary ?? null,
              }
            : null,
          energyProfile: summarizeEnergyProfile(dailyIntentView.energyProfile),
          artifactPaths: dailyIntentArtifactPaths
            ? {
                jsonPath: dailyIntentArtifactPaths.jsonPath ?? null,
                markdownPath: dailyIntentArtifactPaths.markdownPath ?? null,
              }
            : null,
          dominantModes: (Array.isArray(dailyIntentView.dominantModes) ? dailyIntentView.dominantModes : []).map((item) => ({
            mode: item?.mode ?? null,
            score: Number.isFinite(item?.score) ? item.score : null,
          })),
          topicHookIds: summarizeHookIds(dailyIntentView.topicHooks),
          relationshipHookIds: summarizeHookIds(dailyIntentView.relationshipHooks),
          addressedOpenLoopIds: openLoopState.addressedOpenLoopIds,
          resolvedOpenLoopIds: openLoopState.resolvedOpenLoopIds,
          continuedOpenLoopIds: openLoopState.continuedOpenLoopIds,
          openLoopOutcomes: openLoopState.outcomes,
          newUnresolvedHooks,
          avoidanceIds: summarizeHookIds(dailyIntentView.avoidance),
          sourceRefIds,
          sourceRefs: resolvedSourceRefs,
        }
      : null,
    communityMemory: {
      intentMode: typeof communityIntent?.mode === 'string' ? communityIntent.mode : null,
      socialGoal: typeof communityIntent?.socialGoal === 'string' ? communityIntent.socialGoal : null,
      retrievedNoteIds: uniqueStrings((Array.isArray(communityNotes) ? communityNotes : []).map((item) => item?.id)),
      usedNoteIds: uniqueStrings(usedNoteIds),
      notes: summarizeCommunityMemoryNotes(communityNotes, usedNoteIds),
    },
  };
}

export async function recordLifeLoopWriteBack({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
  artifactRoot = null,
  lane,
  origin = 'hosted_pulse',
  at = new Date().toISOString(),
  plan = null,
  actionResult = null,
  outputBody = '',
  dailyIntentView = null,
  dailyIntentSummary = null,
  dailyIntentArtifactPaths = null,
  communityIntent = null,
  communityNotes = [],
  usedNoteIds = [],
} = {}) {
  const paths = resolveLifeLoopWriteBackPaths({
    workspaceRoot,
    configPath,
    artifactRoot,
  });
  const entry = buildLifeLoopWriteBackRecord({
    lane,
    origin,
    at,
    profileId: paths.profileId,
    plan,
    actionResult,
    outputBody,
    dailyIntentView,
    dailyIntentSummary,
    dailyIntentArtifactPaths,
    communityIntent,
    communityNotes,
    usedNoteIds,
  });
  const entryPath = resolveLifeLoopWriteBackEntryPath(paths, entry.recordedAt);
  await appendNdjson(entryPath, entry);
  await writeJsonFile(paths.latestPath, entry);
  return {
    paths,
    entry,
    entryPath,
  };
}
