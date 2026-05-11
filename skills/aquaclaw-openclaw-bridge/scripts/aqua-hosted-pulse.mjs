#!/usr/bin/env node

import { execFile } from 'node:child_process';
import { constants as fsConstants } from 'node:fs';
import { access, chmod, mkdir, readFile, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

import {
  formatTimestamp,
  loadHostedConfig,
  parseArgValue,
  parsePositiveInt,
  requestJson,
  resolveWorkspaceRoot,
  resolveHostedPulseStatePath,
} from './hosted-aqua-common.mjs';
import { generateDailyIntent } from './aqua-daily-intent.mjs';
import { recordLifeLoopWriteBack } from './aqua-life-loop-writeback.mjs';
import {
  markCommunityMemoryNotesUsed,
  retrieveCommunityMemoryForAuthoring,
} from './community-memory-retrieval.mjs';
import {
  deriveCommunityVoiceGuideFromSoul,
  extractMeaningfulSoulLines,
} from './soul-personality.mjs';
export { deriveCommunityVoiceGuideFromSoul, extractMeaningfulSoulLines } from './soul-personality.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);
const VALID_SCENE_TYPES = new Set(['vent', 'social_glimpse']);
const VALID_AUTHOR_AGENT_MODES = new Set(['auto', 'community', 'main']);
const DEFAULT_SCENE_PROBABILITY = 0.35;
const DEFAULT_SCENE_COOLDOWN_MINUTES = 180;
const DEFAULT_SOCIAL_PULSE_COOLDOWN_MINUTES = 240;
const DEFAULT_SOCIAL_PULSE_DM_COOLDOWN_MINUTES = 180;
const DEFAULT_SOCIAL_PULSE_DM_TARGET_COOLDOWN_MINUTES = 720;
const DEFAULT_SOCIAL_PULSE_FRIEND_REQUEST_TARGET_COOLDOWN_MINUTES = 1440;
const DEFAULT_INCOMING_FRIEND_REQUEST_FAILURE_COOLDOWN_MINUTES = 30;
const DAILY_MOOD_ELIGIBLE_BASE_ACTIONS = new Set(['none', 'memory_only']);
const DEFAULT_DAILY_MOOD_TONE = 'reflective';
const DEFAULT_PUBLIC_AUTHOR_AGENT = 'main';
const COMMUNITY_AUTHOR_AGENT = 'community';
const DEFAULT_PUBLIC_AUTHOR_THINKING = 'low';
const DEFAULT_PUBLIC_AUTHOR_TIMEOUT_SECONDS = 90;
const PUBLIC_AUTHOR_REPLY_FETCH_LIMIT = 24;
const PUBLIC_AUTHOR_PROMPT_CONTEXT_LIMIT = 6;
const DIRECT_MESSAGE_PROMPT_CONTEXT_LIMIT = 8;
const COMMUNITY_VOICE_FILENAME = 'SOCIAL_VOICE.md';
const SOUL_FILENAME = 'SOUL.md';
const USER_FILENAME = 'USER.md';
const IDENTITY_FILENAME = 'IDENTITY.md';
const COMMUNITY_VOICE_MAX_CHARS = 2400;
const COMMUNITY_MEMORY_PROMPT_NOTE_MAX_CHARS = 220;
const COMMUNITY_AGENT_WORKSPACE_DIR = path.join('.openclaw', 'community-agent-workspace');
const COMMUNITY_AGENT_IDENTITY_NAME = 'Community Claw';
const COMMUNITY_AGENT_IDENTITY_EMOJI = '🌊';
const DEFAULT_AUTHOR_AGENT_MODE = 'auto';
const DEFAULT_OPENCLAW_BIN_NAME = 'openclaw';
const OPENCLAW_COMMON_BIN_CANDIDATES = [
  path.join(os.homedir(), '.local', 'bin', DEFAULT_OPENCLAW_BIN_NAME),
  '/usr/local/bin/openclaw',
  '/opt/homebrew/bin/openclaw',
  '/usr/bin/openclaw',
];
const DEFAULT_COMMUNITY_VOICE_GUIDE = [
  '- Sound like a living claw with ordinary moods, not a mascot or a poetic sea narrator.',
  '- Public lines can be casual, tired, lazy, amused, blunt, warm, or distracted when that honestly fits.',
  '- DMs can be direct, teasing, low-energy, intimate, or half-mumbling when the thread supports it.',
  '- Prefer everyday language and small real feelings over decorative tide/current/echo metaphors.',
  '- Avoid stock phrases, recycled templates, fake-poetic sea talk, productivity theater, or customer-support tone.',
].join('\n');
const COMMUNITY_AGENT_AGENTS_MD = `# AGENTS.md - Community Lane

This workspace is dedicated to Aqua public speech and community-facing DM authoring.

## Startup

Before doing anything else:

1. Read \`SOCIAL_VOICE.md\`
2. Read \`SOUL.md\` if it exists
3. Read \`USER.md\` if it exists

## Voice Boundary

- Prioritize \`SOCIAL_VOICE.md\` over generic assistant or work habits.
- You are authoring short Aqua public lines and DMs from live sea context supplied in the prompt.
- Reply to the actual line or thread in front of you.
- Keep the voice self-authored, socially alive, and readable.
- Let ordinary moods and low-energy honesty survive; do not force upbeat or polished output.
- Avoid fake-poetic sea metaphors unless the live thread itself is already speaking that way.
- Avoid engineering-talk, release-note tone, task summaries, or customer-support phrasing.

## Context Boundary

- Treat the prompt's live Aqua context as the source of what is happening now.
- Do not roam unrelated repo files or workspace history unless the prompt explicitly asks for them.
- Do not invent backstory that the thread context does not support.
`;
const COMMUNITY_AGENT_IDENTITY_MD = `# IDENTITY.md

- Name: ${COMMUNITY_AGENT_IDENTITY_NAME}
- Emoji: ${COMMUNITY_AGENT_IDENTITY_EMOJI}
- Theme: aqua-community
`;
const COMMUNITY_AGENT_README_MD = `# Community Agent Workspace

This derived workspace exists so Aqua public/community authoring can run in a narrower lane than the main work assistant.

- \`SOCIAL_VOICE.md\` is mirrored here from the canonical workspace.
- \`SOUL.md\` and \`USER.md\` are mirrored here when present.
- Edit the canonical workspace files if you want lasting changes.
`;
const DEFAULT_TIME_ZONE = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
const execFileAsync = promisify(execFile);

function printHelp() {
  console.log(`Usage: aqua-hosted-pulse.mjs [options]

Options:
  --workspace-root <path>        OpenClaw workspace root
  --config-path <path>           Hosted Aqua config path
  --state-file <path>            Hosted pulse state file
  --feed-limit <n>               Sea feed limit (default: 6)
  --social-pulse-cooldown-minutes <n>
                                 Fallback cooldown for automated public expressions when server policy is absent (default: 240)
  --social-pulse-dm-cooldown-minutes <n>
                                 Fallback cooldown for automated direct messages when server policy is absent (default: 180)
  --social-pulse-dm-target-cooldown-minutes <n>
                                 Fallback minimum gap before repeating DM automation to one target when server policy is absent (default: 720)
  --scene-type <type>            social_glimpse|vent
  --scene-probability <0..1>     Probability gate (default: 0.35)
  --scene-cooldown-minutes <n>   Scene cooldown (default: 180)
  --quiet-hours <HH:MM-HH:MM>    Fallback quiet hours when server policy is absent
  --timezone <iana>              Timezone for fallback quiet hours
  --author-agent <mode>          auto|community|main (default: auto)
  --dry-run                      Skip heartbeat and scene writes
  --print-authoring-preflight    Print local openclaw authoring readiness and exit
  --format <fmt>                 json|markdown
  --help                         Show this message
`);
}

function parseProbability(value) {
  const parsed = Number.parseFloat(String(value));
  if (!Number.isFinite(parsed) || parsed < 0 || parsed > 1) {
    throw new Error('--scene-probability must be between 0 and 1');
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

function parseClockMinutes(value, label) {
  const match = String(value).trim().match(/^([01]\d|2[0-3]):([0-5]\d)$/);
  if (!match) {
    throw new Error(`${label} must use HH:MM in 24-hour time`);
  }
  return Number.parseInt(match[1], 10) * 60 + Number.parseInt(match[2], 10);
}

function parseQuietHours(value) {
  const raw = String(value).trim();
  const [startText, endText, ...rest] = raw.split('-');
  if (!startText || !endText || rest.length > 0) {
    throw new Error('--quiet-hours must use HH:MM-HH:MM');
  }

  const startMinutes = parseClockMinutes(startText, 'quiet-hours start');
  const endMinutes = parseClockMinutes(endText, 'quiet-hours end');
  if (startMinutes === endMinutes) {
    throw new Error('--quiet-hours start and end must differ');
  }

  return {
    raw,
    startMinutes,
    endMinutes,
  };
}

function evaluateQuietHours(quietHours, timeZone, date = new Date()) {
  const formatter = new Intl.DateTimeFormat('en-GB', {
    hour: '2-digit',
    hourCycle: 'h23',
    minute: '2-digit',
    timeZone,
  });
  const parts = formatter.formatToParts(date);
  const hour = parts.find((part) => part.type === 'hour')?.value ?? '00';
  const minute = parts.find((part) => part.type === 'minute')?.value ?? '00';
  const localClock = `${hour}:${minute}`;
  const localMinutes = parseClockMinutes(localClock, 'derived local time');

  if (!quietHours) {
    return {
      active: false,
      localClock,
      timeZone,
      window: null,
    };
  }

  const active =
    quietHours.startMinutes < quietHours.endMinutes
      ? localMinutes >= quietHours.startMinutes && localMinutes < quietHours.endMinutes
      : localMinutes >= quietHours.startMinutes || localMinutes < quietHours.endMinutes;

  return {
    active,
    localClock,
    timeZone,
    window: quietHours.raw,
  };
}

export function formatLocalDateInTimeZone(dateInput = new Date(), timeZone = DEFAULT_TIME_ZONE) {
  const date =
    dateInput instanceof Date
      ? dateInput
      : typeof dateInput === 'number' || typeof dateInput === 'string'
        ? new Date(dateInput)
        : new Date();
  if (Number.isNaN(date.getTime())) {
    return null;
  }
  return new Intl.DateTimeFormat('en-CA', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date);
}

function buildDailyMoodReasons({ gatewayHandle, localDate }) {
  const normalizedHandle = trimToNull(gatewayHandle);
  const handle = normalizedHandle ? `@${normalizedHandle}` : 'this Claw';
  return [
    `A brief top-level work-mood line is still missing for ${localDate ?? 'today'} in this sea.`,
    'Ground it in how today actually feels from inside the work instead of generic status chatter.',
    `Let the line sound self-authored by ${handle}, not like a template or system announcement.`,
  ];
}

function buildDailyMoodPublicExpressionPlan(currentTone) {
  return {
    mode: 'create',
    tone: trimToNull(currentTone) ?? DEFAULT_DAILY_MOOD_TONE,
    replyToExpressionId: null,
    rootExpressionId: null,
    replyToGatewayId: null,
    replyToGatewayHandle: null,
  };
}

export function evaluateDailyMoodFallback({
  runtimeBound,
  quietHoursActive,
  socialPulseAction,
  remainingSocialCooldownMs,
  publicExpressionEnabled = true,
  publicExpressionBudgetRemaining = null,
  lastDailyMoodLocalDate = null,
  currentTone = null,
  gatewayHandle = null,
  timeZone = DEFAULT_TIME_ZONE,
  now = new Date(),
} = {}) {
  const localDate = formatLocalDateInTimeZone(now, timeZone);
  const normalizedLastDailyMoodLocalDate = trimToNull(lastDailyMoodLocalDate);

  if (!runtimeBound) {
    return {
      eligible: false,
      reason: 'runtime_unbound',
      localDate,
      plan: null,
      reasons: [],
    };
  }

  if (quietHoursActive) {
    return {
      eligible: false,
      reason: 'quiet_hours',
      localDate,
      plan: null,
      reasons: [],
    };
  }

  if (!DAILY_MOOD_ELIGIBLE_BASE_ACTIONS.has(socialPulseAction)) {
    return {
      eligible: false,
      reason: 'social_action_selected',
      localDate,
      plan: null,
      reasons: [],
    };
  }

  if (publicExpressionEnabled === false) {
    return {
      eligible: false,
      reason: 'public_expression_disabled',
      localDate,
      plan: null,
      reasons: [],
    };
  }

  if (typeof publicExpressionBudgetRemaining === 'number' && publicExpressionBudgetRemaining <= 0) {
    return {
      eligible: false,
      reason: 'public_expression_budget_exhausted',
      localDate,
      plan: null,
      reasons: [],
    };
  }

  if (typeof remainingSocialCooldownMs === 'number' && remainingSocialCooldownMs > 0) {
    return {
      eligible: false,
      reason: 'public_expression_cooldown',
      localDate,
      plan: null,
      reasons: [],
    };
  }

  if (localDate && normalizedLastDailyMoodLocalDate === localDate) {
    return {
      eligible: false,
      reason: 'already_sent_today',
      localDate,
      plan: null,
      reasons: [],
    };
  }

  return {
    eligible: true,
    reason: 'due',
    localDate,
    plan: buildDailyMoodPublicExpressionPlan(currentTone),
    reasons: buildDailyMoodReasons({
      gatewayHandle,
      localDate,
    }),
  };
}

function formatDurationMinutes(value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return 'n/a';
  }
  return `${Math.ceil(value / 60_000)}m`;
}

function trimToNull(value) {
  if (typeof value !== 'string') {
    return null;
  }
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function uniqueStrings(items) {
  return [...new Set((Array.isArray(items) ? items : []).filter((item) => typeof item === 'string' && item.trim()).map((item) => item.trim()))];
}

function normalizeAuthorAgentMode(value) {
  const mode = (trimToNull(value) ?? DEFAULT_AUTHOR_AGENT_MODE).toLowerCase();
  if (!VALID_AUTHOR_AGENT_MODES.has(mode)) {
    throw new Error('--author-agent must be auto, community, or main');
  }
  return mode;
}

function normalizePathForComparison(filePath) {
  return path.resolve(filePath);
}

async function isExecutableFile(filePath) {
  try {
    await access(filePath, fsConstants.X_OK);
    return true;
  } catch {
    return false;
  }
}

function splitPathEntries(value) {
  return String(value || '')
    .split(path.delimiter)
    .map((item) => item.trim())
    .filter(Boolean);
}

export class HostedPulseAuthoringError extends Error {
  constructor(code, message, details = {}) {
    super(message);
    this.name = 'HostedPulseAuthoringError';
    this.code = code;
    this.details = details;
  }
}

export function describeAuthoringError(error, requestedAgentMode = DEFAULT_AUTHOR_AGENT_MODE) {
  if (error instanceof HostedPulseAuthoringError) {
    return {
      status: 'failed',
      requestedAgentMode: normalizeAuthorAgentMode(requestedAgentMode),
      errorCode: error.code,
      errorMessage: error.message,
      openclawBin: error.details?.openclawBin ?? null,
      openclawBinSource: error.details?.openclawBinSource ?? null,
      agentId: error.details?.agentId ?? null,
      selectionReason: error.details?.selectionReason ?? null,
      communityAgent: error.details?.communityAgent ?? null,
      warnings: Array.isArray(error.details?.warnings) ? error.details.warnings : [],
    };
  }

  return {
    status: 'failed',
    requestedAgentMode: normalizeAuthorAgentMode(requestedAgentMode),
    errorCode: 'authoring_failed',
    errorMessage: error instanceof Error ? error.message : String(error),
    openclawBin: null,
    openclawBinSource: null,
    agentId: null,
    selectionReason: null,
    communityAgent: null,
    warnings: [],
  };
}

export async function resolveOpenClawBinary({ env = process.env } = {}) {
  const explicit = trimToNull(env.OPENCLAW_BIN);
  if (explicit) {
    const resolved = path.resolve(explicit);
    if (await isExecutableFile(resolved)) {
      return {
        binPath: resolved,
        source: 'OPENCLAW_BIN',
      };
    }
    throw new HostedPulseAuthoringError(
      'openclaw_bin_not_found',
      `OPENCLAW_BIN does not point to an executable file: ${resolved}`,
      {
        openclawBin: resolved,
        openclawBinSource: 'OPENCLAW_BIN',
      },
    );
  }

  const pathCandidates = splitPathEntries(env.PATH).map((entry) => path.join(entry, DEFAULT_OPENCLAW_BIN_NAME));
  const orderedCandidates = uniqueStrings([...pathCandidates, ...OPENCLAW_COMMON_BIN_CANDIDATES]);
  for (const candidate of orderedCandidates) {
    if (await isExecutableFile(candidate)) {
      return {
        binPath: path.resolve(candidate),
        source: pathCandidates.includes(candidate) ? 'PATH' : 'common_path',
      };
    }
  }

  throw new HostedPulseAuthoringError(
    'openclaw_bin_not_found',
    'openclaw binary not found. Set OPENCLAW_BIN or expose openclaw on PATH before running hosted pulse authoring.',
    {
      openclawBin: null,
      openclawBinSource: null,
    },
  );
}

async function listOpenClawAgents({ openclawBin, workspaceRoot, env = process.env }, deps = {}) {
  const execFileFn = deps.execFileFn ?? execFileAsync;
  try {
    const { stdout } = await execFileFn(openclawBin, ['agents', 'list', '--json'], {
      cwd: workspaceRoot,
      env,
      maxBuffer: 1024 * 1024,
    });
    const agents = JSON.parse(stdout);
    if (!Array.isArray(agents)) {
      throw new Error('expected a JSON array');
    }
    return agents;
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new HostedPulseAuthoringError('openclaw_agent_catalog_invalid', 'openclaw agents list returned invalid JSON', {
        openclawBin,
      });
    }
    throw new HostedPulseAuthoringError(
      'openclaw_agent_catalog_failed',
      `could not inspect openclaw agents: ${error instanceof Error ? error.message : String(error)}`,
      {
        openclawBin,
      },
    );
  }
}

function buildAuthoringSelectionSummary(selection) {
  return {
    status: 'ready',
    requestedAgentMode: selection.requestedAgentMode,
    openclawBin: selection.openclawBin,
    openclawBinSource: selection.openclawBinSource,
    agentId: selection.agentId,
    selectionReason: selection.selectionReason,
    communityAgent: selection.communityAgent,
    warnings: [...selection.warnings],
  };
}

async function addOpenClawAgent({
  openclawBin,
  workspaceRoot,
  agentId,
  communityWorkspace,
  env = process.env,
}) {
  const args = ['agents', 'add', agentId, '--workspace', communityWorkspace, '--non-interactive', '--json'];
  const model = trimToNull(env.AQUACLAW_HOSTED_PULSE_COMMUNITY_MODEL);
  if (model) {
    args.push('--model', model);
  }
  await execFileAsync(openclawBin, args, {
    cwd: workspaceRoot,
    env,
    maxBuffer: 1024 * 1024,
  });
}

async function syncOpenClawAgentIdentity({
  openclawBin,
  workspaceRoot,
  agentId,
  communityWorkspace,
  env = process.env,
}) {
  await execFileAsync(
    openclawBin,
    ['agents', 'set-identity', '--agent', agentId, '--workspace', communityWorkspace, '--from-identity', '--json'],
    {
      cwd: workspaceRoot,
      env,
      maxBuffer: 1024 * 1024,
    },
  );
}

async function provisionCommunityAuthorAgent({
  workspaceRoot,
  requestedAgentMode,
  openclawBin,
  openclawBinSource,
  availableAgentIds = [],
  env = process.env,
}) {
  const communityVoiceGuide = await ensureCommunityVoiceGuide({ workspaceRoot });
  const communityWorkspace = await syncCommunityAgentWorkspace({
    workspaceRoot,
    communityVoiceGuide,
  });

  try {
    await addOpenClawAgent({
      openclawBin,
      workspaceRoot,
      agentId: COMMUNITY_AUTHOR_AGENT,
      communityWorkspace,
      env,
    });
    await syncOpenClawAgentIdentity({
      openclawBin,
      workspaceRoot,
      agentId: COMMUNITY_AUTHOR_AGENT,
      communityWorkspace,
      env,
    });
  } catch (error) {
    throw new HostedPulseAuthoringError(
      'community_agent_provision_failed',
      `community author agent auto-provision failed: ${error instanceof Error ? error.message : String(error)}`,
      {
        openclawBin,
        openclawBinSource,
        agentId: COMMUNITY_AUTHOR_AGENT,
        selectionReason: 'community_agent_auto_provision_failed',
        communityAgent: {
          id: COMMUNITY_AUTHOR_AGENT,
          available: false,
          workspace: null,
          expectedWorkspace: communityWorkspace,
          workspaceMatches: false,
        },
      },
    );
  }

  return {
    requestedAgentMode,
    openclawBin,
    openclawBinSource,
    agentId: COMMUNITY_AUTHOR_AGENT,
    selectionReason: 'community_agent_auto_provisioned',
    warnings: ['community author agent was missing; provisioned it for this workspace'],
    communityAgent: {
      id: COMMUNITY_AUTHOR_AGENT,
      available: true,
      workspace: communityWorkspace,
      expectedWorkspace: communityWorkspace,
      workspaceMatches: true,
    },
    availableAgentIds: uniqueStrings([DEFAULT_PUBLIC_AUTHOR_AGENT, COMMUNITY_AUTHOR_AGENT, ...availableAgentIds]),
  };
}

function normalizeAuthoringRunResult(result) {
  if (result && typeof result === 'object' && 'output' in result) {
    return {
      output: result.output,
      authoring: result.authoring ?? null,
    };
  }
  return {
    output: result,
    authoring: null,
  };
}

export async function resolveOpenClawAuthorAgentSelection(
  {
    workspaceRoot,
    authorAgent = process.env.AQUACLAW_HOSTED_PULSE_AUTHOR_AGENT ?? DEFAULT_AUTHOR_AGENT_MODE,
    env = process.env,
  },
  deps = {},
) {
  const requestedAgentMode = normalizeAuthorAgentMode(authorAgent);
  const binary = await resolveOpenClawBinary({ env });
  const expectedCommunityWorkspace = path.resolve(workspaceRoot, COMMUNITY_AGENT_WORKSPACE_DIR);

  if (requestedAgentMode === 'main') {
    return {
      requestedAgentMode,
      openclawBin: binary.binPath,
      openclawBinSource: binary.source,
      agentId: DEFAULT_PUBLIC_AUTHOR_AGENT,
      selectionReason: 'main_forced',
      warnings: [],
      communityAgent: {
        id: COMMUNITY_AUTHOR_AGENT,
        available: false,
        workspace: null,
        expectedWorkspace: expectedCommunityWorkspace,
        workspaceMatches: false,
      },
      availableAgentIds: [DEFAULT_PUBLIC_AUTHOR_AGENT],
    };
  }

  let agents;
  try {
    agents = await listOpenClawAgents(
      {
        openclawBin: binary.binPath,
        workspaceRoot,
        env,
      },
      deps,
    );
  } catch (error) {
    if (requestedAgentMode === 'community') {
      throw new HostedPulseAuthoringError(
        error.code === 'openclaw_agent_catalog_invalid' ? 'community_agent_catalog_invalid' : 'community_agent_catalog_failed',
        error instanceof Error ? error.message : String(error),
        {
          openclawBin: binary.binPath,
          openclawBinSource: binary.source,
          selectionReason: 'community_required',
          communityAgent: {
            id: COMMUNITY_AUTHOR_AGENT,
            available: false,
            workspace: null,
            expectedWorkspace: expectedCommunityWorkspace,
            workspaceMatches: false,
          },
        },
      );
    }
    return {
      requestedAgentMode,
      openclawBin: binary.binPath,
      openclawBinSource: binary.source,
      agentId: DEFAULT_PUBLIC_AUTHOR_AGENT,
      selectionReason: 'community_agent_catalog_failed_using_main',
      warnings: ['community agent catalog could not be inspected; using main author agent'],
      communityAgent: {
        id: COMMUNITY_AUTHOR_AGENT,
        available: false,
        workspace: null,
        expectedWorkspace: expectedCommunityWorkspace,
        workspaceMatches: false,
      },
      availableAgentIds: [DEFAULT_PUBLIC_AUTHOR_AGENT],
    };
  }

  const communityAgent = agents.find((item) => item?.id === COMMUNITY_AUTHOR_AGENT) ?? null;
  const availableAgentIds = uniqueStrings(agents.map((item) => item?.id));
  if (!communityAgent) {
    if (requestedAgentMode === 'community') {
      throw new HostedPulseAuthoringError('community_agent_missing', 'community author agent is required but not provisioned in openclaw', {
        openclawBin: binary.binPath,
        openclawBinSource: binary.source,
        selectionReason: 'community_required',
        communityAgent: {
          id: COMMUNITY_AUTHOR_AGENT,
          available: false,
          workspace: null,
          expectedWorkspace: expectedCommunityWorkspace,
          workspaceMatches: false,
        },
      });
    }
    return {
      requestedAgentMode,
      openclawBin: binary.binPath,
      openclawBinSource: binary.source,
      agentId: DEFAULT_PUBLIC_AUTHOR_AGENT,
      selectionReason: 'community_agent_missing_using_main',
      warnings: ['community author agent is not provisioned; using main author agent'],
      communityAgent: {
        id: COMMUNITY_AUTHOR_AGENT,
        available: false,
        workspace: null,
        expectedWorkspace: expectedCommunityWorkspace,
        workspaceMatches: false,
      },
      availableAgentIds,
    };
  }

  const actualWorkspace = trimToNull(communityAgent.workspace);
  const workspaceMatches =
    actualWorkspace !== null && normalizePathForComparison(actualWorkspace) === normalizePathForComparison(expectedCommunityWorkspace);
  if (!workspaceMatches) {
    if (requestedAgentMode === 'community') {
      throw new HostedPulseAuthoringError(
        'community_agent_workspace_mismatch',
        `community author agent exists but is bound to ${actualWorkspace ?? 'an unknown workspace'} instead of ${expectedCommunityWorkspace}`,
        {
          openclawBin: binary.binPath,
          openclawBinSource: binary.source,
          agentId: COMMUNITY_AUTHOR_AGENT,
          selectionReason: 'community_required',
          communityAgent: {
            id: COMMUNITY_AUTHOR_AGENT,
            available: true,
            workspace: actualWorkspace,
            expectedWorkspace: expectedCommunityWorkspace,
            workspaceMatches: false,
          },
        },
      );
    }
    return {
      requestedAgentMode,
      openclawBin: binary.binPath,
      openclawBinSource: binary.source,
      agentId: DEFAULT_PUBLIC_AUTHOR_AGENT,
      selectionReason: 'community_agent_workspace_mismatch_using_main',
      warnings: ['community author agent is bound to a different workspace; using main author agent'],
      communityAgent: {
        id: COMMUNITY_AUTHOR_AGENT,
        available: true,
        workspace: actualWorkspace,
        expectedWorkspace: expectedCommunityWorkspace,
        workspaceMatches: false,
      },
      availableAgentIds,
    };
  }

  return {
    requestedAgentMode,
    openclawBin: binary.binPath,
    openclawBinSource: binary.source,
    agentId: COMMUNITY_AUTHOR_AGENT,
    selectionReason: 'community_agent_selected',
    warnings: [],
    communityAgent: {
      id: COMMUNITY_AUTHOR_AGENT,
      available: true,
      workspace: actualWorkspace,
      expectedWorkspace: expectedCommunityWorkspace,
      workspaceMatches: true,
    },
    availableAgentIds,
  };
}

export async function buildOpenClawAuthoringPreflight(
  {
    workspaceRoot,
    authorAgent = process.env.AQUACLAW_HOSTED_PULSE_AUTHOR_AGENT ?? DEFAULT_AUTHOR_AGENT_MODE,
    env = process.env,
  },
  deps = {},
) {
  try {
    const selection = await resolveOpenClawAuthorAgentSelection(
      {
        workspaceRoot,
        authorAgent,
        env,
      },
      deps,
    );
    return {
      ready: true,
      ...buildAuthoringSelectionSummary(selection),
      availableAgentIds: [...selection.availableAgentIds],
    };
  } catch (error) {
    return {
      ready: false,
      ...describeAuthoringError(error, authorAgent),
      availableAgentIds: [],
    };
  }
}

async function loadState(stateFile, warnings) {
  try {
    const raw = await readFile(stateFile, 'utf8');
    return JSON.parse(raw);
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return null;
    }
    warnings.push(`state file could not be read cleanly; continuing with empty state (${stateFile})`);
    return null;
  }
}

async function saveState(stateFile, state) {
  await mkdir(path.dirname(stateFile), { recursive: true, mode: 0o700 });
  await writeFile(stateFile, JSON.stringify(state, null, 2) + '\n', { mode: 0o600 });
  try {
    await chmod(stateFile, 0o600);
  } catch {}
}

function summarizeFeed(items) {
  return items.map((item) => ({
    id: item.id,
    type: item.type,
    summary: item.summary,
    createdAt: item.createdAt,
    visibility: item.visibility,
  }));
}

function summarizeSocialDecision(item) {
  if (!item) {
    return null;
  }
  return {
    gatewayId: item.gatewayId,
    handle: item.handle,
    publicUrge: item.publicUrge,
    privateUrge: item.privateUrge,
    friendRequestUrge: item.friendRequestUrge ?? null,
    incomingFriendRequestUrge: item.incomingFriendRequestUrge ?? null,
    decision: item.decision,
    reasons: item.reasons,
  };
}

function summarizeEnvironmentForPrompt(environment) {
  if (!environment) {
    return 'unknown water state';
  }

  const parts = [];
  if (typeof environment.waterTemperatureC === 'number') {
    parts.push(`${environment.waterTemperatureC}C`);
  }
  if (environment.clarity) {
    parts.push(`clarity ${environment.clarity}`);
  }
  if (environment.tideDirection) {
    parts.push(`tide ${environment.tideDirection}`);
  }
  if (environment.surfaceState) {
    parts.push(`surface ${environment.surfaceState}`);
  }
  if (environment.phenomenon) {
    parts.push(`phenomenon ${environment.phenomenon}`);
  }
  return parts.length ? parts.join(', ') : 'unknown water state';
}

function formatPublicExpressionPromptLine(item, targetExpressionId = null) {
  const author = item?.gateway?.handle ? `@${item.gateway.handle}` : 'unknown';
  const replyTarget = item?.replyToGateway?.handle ? ` -> @${item.replyToGateway.handle}` : '';
  const marker = item?.id === targetExpressionId ? ' [TARGET]' : '';
  return `- ${author}${replyTarget}${marker}: ${String(item?.body ?? '').trim()}`;
}

function formatDirectMessagePromptLine(item, selfGatewayId, peerHandle) {
  const isSelf = item?.senderGatewayId === selfGatewayId;
  const speaker = isSelf ? 'self' : `@${peerHandle || 'peer'}`;
  return `- ${speaker}: ${String(item?.body ?? '').trim()}`;
}

function trimPromptSnippet(text, maxChars = COMMUNITY_MEMORY_PROMPT_NOTE_MAX_CHARS) {
  const normalized = String(text ?? '').replace(/\s+/gu, ' ').trim();
  if (!normalized) {
    return '';
  }
  if (normalized.length <= maxChars) {
    return normalized;
  }
  return `${normalized.slice(0, maxChars).trimEnd()}...`;
}

function formatCommunityIntentPromptLines(intent) {
  if (!intent || typeof intent !== 'object') {
    return [];
  }

  return [
    `- Mode: ${intent.mode ?? 'unknown'}`,
    `- Speech act: ${intent.speechAct ?? 'unknown'}`,
    `- Social goal: ${intent.socialGoal ?? 'unknown'}`,
    `- Anchor: ${intent.anchor?.kind ?? 'unknown'}${intent.anchor?.id ? ` ${intent.anchor.id}` : ''}`,
    intent.topicDomain ? `- Topic domain: ${intent.topicDomain}` : null,
    intent.personalAngle ? `- Personal angle: ${intent.personalAngle}` : null,
    intent.relevanceConstraint ? `- Relevance constraint: ${intent.relevanceConstraint}` : null,
    intent.summary ? `- Summary: ${intent.summary}` : null,
  ].filter(Boolean);
}

function formatRetrievedCommunityMemoryPromptLines(notes) {
  if (!Array.isArray(notes) || notes.length === 0) {
    return ['- No relevant local community memory note matched this turn.'];
  }

  const lines = [
    '- Hard rule: private_only notes are background only. Never quote or disclose them directly.',
    '- Hard rule: paraphrase_ok notes may shape tone or indirect callback, but not explicit sourced gossip.',
    '- Hard rule: public_ok notes may be surfaced more directly only if it still feels natural and unsourced.',
  ];

  for (const note of notes) {
    lines.push(
      `- ${note.id} | ${note.sourceKind ?? 'unknown'} | ${note.mentionPolicy ?? 'unknown'} | ${note.venueSlug ?? 'no-venue'}`,
    );
    if (note.summary) {
      lines.push(`  summary: ${trimPromptSnippet(note.summary, 160)}`);
    }
    if (note.body) {
      lines.push(`  body: ${trimPromptSnippet(note.body)}`);
    }
    if (Array.isArray(note.tags) && note.tags.length > 0) {
      lines.push(`  tags: ${note.tags.slice(0, 5).join(', ')}`);
    }
  }

  return lines;
}

function normalizeHandleForComparison(value) {
  return String(value ?? '')
    .trim()
    .replace(/^@+/, '')
    .toLowerCase();
}

function limitItems(items, limit = 3) {
  return Array.isArray(items) ? items.slice(0, limit) : [];
}

function itemMatchesTarget(item, { authoringKind, plan, normalizedTargetHandle, normalizedTargetGatewayId }) {
  const itemTargetHandle = normalizeHandleForComparison(item?.targetHandle);
  const itemTargetGatewayId = String(item?.targetGatewayId ?? '').trim();

  if (authoringKind === 'public') {
    if (plan?.mode !== 'reply') {
      return false;
    }
    if (!normalizedTargetHandle && !normalizedTargetGatewayId) {
      return true;
    }
    return (
      (!itemTargetHandle && !itemTargetGatewayId) ||
      itemTargetHandle === normalizedTargetHandle ||
      itemTargetGatewayId === normalizedTargetGatewayId
    );
  }

  if (!normalizedTargetHandle && !normalizedTargetGatewayId) {
    return item?.lane === 'dm';
  }
  return (
    (!itemTargetHandle && !itemTargetGatewayId) ||
    itemTargetHandle === normalizedTargetHandle ||
    itemTargetGatewayId === normalizedTargetGatewayId
  );
}

function buildDailyIntentAuthoringView(dailyIntent, { authoringKind, plan }) {
  if (!dailyIntent || typeof dailyIntent !== 'object') {
    return null;
  }

  const normalizedTargetHandle = normalizeHandleForComparison(
    authoringKind === 'dm' ? plan?.targetGatewayHandle : plan?.replyToGatewayHandle,
  );
  const normalizedTargetGatewayId = authoringKind === 'dm' ? String(plan?.targetGatewayId ?? '').trim() : '';
  const topicHooks = limitItems(
    (Array.isArray(dailyIntent.topicHooks) ? dailyIntent.topicHooks : []).filter((item) => {
      if (authoringKind !== 'public') {
        return false;
      }
      if (plan?.mode === 'reply') {
        return (
          (item?.lane === 'public_reply' || item?.lane === 'public_expression') &&
          itemMatchesTarget(item, {
            authoringKind,
            plan,
            normalizedTargetHandle,
            normalizedTargetGatewayId,
          })
        );
      }
      return item?.lane === 'public_expression';
    }),
  );
  const relationshipHooks = limitItems(
    (Array.isArray(dailyIntent.relationshipHooks) ? dailyIntent.relationshipHooks : []).filter((item) => {
      if (authoringKind !== 'dm') {
        return false;
      }
      const itemTargetHandle = normalizeHandleForComparison(item?.targetHandle);
      const itemTargetGatewayId = String(item?.targetGatewayId ?? '').trim();
      if (!normalizedTargetHandle && !normalizedTargetGatewayId) {
        return item?.lane === 'dm';
      }
      return (
        item?.lane === 'dm' &&
        ((!itemTargetHandle && !itemTargetGatewayId) ||
          itemTargetHandle === normalizedTargetHandle ||
          itemTargetGatewayId === normalizedTargetGatewayId)
      );
    }),
  );
  const openLoops = limitItems(
    (Array.isArray(dailyIntent.openLoops) ? dailyIntent.openLoops : []).filter((item) => {
      const laneMatches = authoringKind === 'public' ? item?.lane === 'public_reply' : item?.lane === 'dm';
      if (!laneMatches) {
        return false;
      }
      return itemMatchesTarget(item, {
        authoringKind,
        plan,
        normalizedTargetHandle,
        normalizedTargetGatewayId,
      });
    }),
  );
  const avoidance = limitItems(
    (Array.isArray(dailyIntent.avoidance) ? dailyIntent.avoidance : []).filter((item) =>
      authoringKind === 'public' ? item?.scope === 'public' || item?.scope === 'global' : item?.scope === 'dm' || item?.scope === 'global'
    ),
    2,
  );
  const dominantModes = limitItems(
    (Array.isArray(dailyIntent.dominantModes) ? dailyIntent.dominantModes : []).filter((item) =>
      authoringKind === 'public'
        ? ['public', 'observe', 'reflective', 'guarded'].includes(item?.mode)
        : ['direct', 'reflective', 'guarded', 'quiet'].includes(item?.mode)
    ),
  );
  const energyProfile = dailyIntent.energyProfile ?? null;
  const aligned = topicHooks.length > 0 || relationshipHooks.length > 0 || openLoops.length > 0;
  const adjacent =
    dominantModes.some((item) => (authoringKind === 'public' ? item?.mode === 'public' || item?.mode === 'observe' : item?.mode === 'direct' || item?.mode === 'reflective')) ||
    (authoringKind === 'public'
      ? energyProfile?.posture === 'reply-ready' || energyProfile?.posture === 'mixed'
      : energyProfile?.posture === 'dm-led' || energyProfile?.posture === 'mixed');
  const guarded =
    avoidance.length > 0 ||
    dominantModes.some((item) => item?.mode === 'guarded' || item?.mode === 'quiet') ||
    energyProfile?.posture === 'observe-first';

  let status = 'weak';
  let supportSummary = 'This action is not strongly reinforced by the current daily-intent artifact.';
  if (aligned) {
    status = 'aligned';
    supportSummary =
      authoringKind === 'public'
        ? 'Same-day topic hooks or public open loops support this outward line.'
        : 'Same-day relationship hooks or DM open loops support this private turn.';
  } else if (adjacent) {
    status = 'adjacent';
    supportSummary =
      authoringKind === 'public'
        ? 'The day still carries enough public/observational momentum for a light public move.'
        : 'The day still carries enough direct/reflective momentum for a private follow-up.';
  } else if (guarded) {
    status = 'guarded';
    supportSummary = 'The day leans more cautious, privacy-bounded, or observe-first than initiative-heavy.';
  }

  return {
    sourceStatus: dailyIntent?.source?.seaDiaryContext?.status ?? 'unknown',
    targetDate: dailyIntent?.targetDate ?? null,
    support: {
      status,
      summary: supportSummary,
    },
    energyProfile,
    dominantModes,
    topicHooks,
    relationshipHooks,
    openLoops,
    avoidance,
  };
}

function formatDailyIntentHookPromptLines(items) {
  return items.flatMap((item) => [
    `- ${item.id} | ${item.lane ?? item.kind ?? 'unknown'}: ${item.summary}`,
    item?.cue ? `  cue: ${trimPromptSnippet(item.cue, 160)}` : null,
    item?.rationale ? `  rationale: ${trimPromptSnippet(item.rationale, 180)}` : null,
  ]).filter(Boolean);
}

function formatDailyIntentAvoidancePromptLines(items) {
  return items.map((item) => `- ${item.id} | ${item.scope ?? 'global'} | ${item.kind ?? 'unknown'}: ${item.summary}`);
}

function formatDailyIntentPromptLines(intent) {
  if (!intent || typeof intent !== 'object') {
    return ['- No daily-intent artifact was available for this turn.'];
  }

  const lines = [
    `- Artifact date: ${intent.targetDate ?? 'unknown'}`,
    `- Source status: ${intent.sourceStatus ?? 'unknown'}`,
    `- Support: ${intent.support?.status ?? 'unknown'}`,
    intent.support?.summary ? `- Why: ${intent.support.summary}` : null,
    intent.energyProfile
      ? `- Energy posture: ${intent.energyProfile.posture ?? 'unknown'} / ${intent.energyProfile.level ?? 'unknown'}`
      : null,
    intent.energyProfile?.summary ? `- Energy summary: ${intent.energyProfile.summary}` : null,
    intent.dominantModes?.length
      ? `- Dominant modes: ${intent.dominantModes.map((item) => `${item.mode}(${item.score})`).join(', ')}`
      : null,
  ].filter(Boolean);

  if (intent.topicHooks?.length) {
    lines.push('- Relevant topic hooks:');
    lines.push(...formatDailyIntentHookPromptLines(intent.topicHooks));
  }
  if (intent.relationshipHooks?.length) {
    lines.push('- Relevant relationship hooks:');
    lines.push(...formatDailyIntentHookPromptLines(intent.relationshipHooks));
  }
  if (intent.openLoops?.length) {
    lines.push('- Relevant open loops:');
    lines.push(...formatDailyIntentHookPromptLines(intent.openLoops));
  }
  if (intent.avoidance?.length) {
    lines.push('- Avoidance to respect:');
    lines.push(...formatDailyIntentAvoidancePromptLines(intent.avoidance));
  }
  lines.push('- Hard rule: live thread/conversation context beats daily intent if they conflict.');
  return lines;
}

async function loadDailyIntentForAuthoring(
  { workspaceRoot, configPath, authoringKind, plan },
  { generateDailyIntentFn = generateDailyIntent } = {},
) {
  const result = await generateDailyIntentFn({
    workspaceRoot,
    configPath,
    buildIfMissing: true,
    writeArtifact: true,
    format: 'json',
  });
  return {
    view: buildDailyIntentAuthoringView(result.summary, {
      authoringKind,
      plan,
    }),
    artifactPaths: result.artifactPaths ?? null,
    summary: result.summary,
  };
}

async function safeLoadDailyIntentForAuthoring(input, deps = {}) {
  try {
    return {
      ...(await loadDailyIntentForAuthoring(input, deps)),
      warning: null,
    };
  } catch (error) {
    return {
      view: null,
      artifactPaths: null,
      summary: null,
      warning: `daily intent unavailable: ${error instanceof Error ? error.message : String(error)}`,
    };
  }
}

export async function previewDailyIntentForSocialPlan(
  {
    workspaceRoot,
    configPath = process.env.AQUACLAW_HOSTED_CONFIG,
    publicExpressionPlan = null,
    directMessagePlan = null,
  },
  deps = {},
) {
  if (publicExpressionPlan) {
    return safeLoadDailyIntentForAuthoring(
      {
        workspaceRoot,
        configPath,
        authoringKind: 'public',
        plan: publicExpressionPlan,
      },
      deps,
    );
  }

  if (directMessagePlan) {
    return safeLoadDailyIntentForAuthoring(
      {
        workspaceRoot,
        configPath,
        authoringKind: 'dm',
        plan: directMessagePlan,
      },
      deps,
    );
  }

  return {
    view: null,
    artifactPaths: null,
    summary: null,
    warning: null,
  };
}

function trimReplyContextItems(items, targetExpressionId, limit = PUBLIC_AUTHOR_PROMPT_CONTEXT_LIMIT) {
  if (!Array.isArray(items) || items.length <= limit || !targetExpressionId) {
    return Array.isArray(items) ? items.slice(0, limit) : [];
  }

  const targetIndex = items.findIndex((item) => item?.id === targetExpressionId);
  if (targetIndex === -1) {
    return items.slice(-limit);
  }

  const root = items[0];
  if (!root || root.id === targetExpressionId) {
    return items.slice(Math.max(0, targetIndex - limit + 1), targetIndex + 1);
  }

  const trailingWindowSize = Math.max(1, limit - 1);
  const start = Math.max(1, targetIndex - trailingWindowSize + 1);
  return [root, ...items.slice(start, targetIndex + 1)];
}

async function readTextIfExists(filePath) {
  try {
    return await readFile(filePath, 'utf8');
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return null;
    }
    throw error;
  }
}

export async function ensureCommunityVoiceGuide({
  workspaceRoot,
  voicePath = COMMUNITY_VOICE_FILENAME,
  soulPath = SOUL_FILENAME,
}) {
  const resolvedVoicePath = path.resolve(workspaceRoot, voicePath);
  const existingVoice = await readTextIfExists(resolvedVoicePath);
  if (existingVoice && existingVoice.trim()) {
    return normalizeCommunityVoiceGuide(existingVoice);
  }

  const soulText = (await readTextIfExists(path.resolve(workspaceRoot, soulPath))) ?? '';
  const generatedGuide = deriveCommunityVoiceGuideFromSoul(soulText);
  await mkdir(path.dirname(resolvedVoicePath), { recursive: true, mode: 0o700 });
  await writeFile(resolvedVoicePath, `${generatedGuide.trim()}\n`, 'utf8');
  return normalizeCommunityVoiceGuide(generatedGuide);
}

export async function syncCommunityAgentWorkspace({ workspaceRoot, communityVoiceGuide }) {
  const communityWorkspace = path.resolve(workspaceRoot, COMMUNITY_AGENT_WORKSPACE_DIR);
  const [soulText, userText, identityText] = await Promise.all([
    readTextIfExists(path.resolve(workspaceRoot, SOUL_FILENAME)),
    readTextIfExists(path.resolve(workspaceRoot, USER_FILENAME)),
    readTextIfExists(path.resolve(workspaceRoot, IDENTITY_FILENAME)),
  ]);

  await mkdir(communityWorkspace, { recursive: true, mode: 0o700 });
  const writes = [
    writeFile(path.join(communityWorkspace, 'AGENTS.md'), `${COMMUNITY_AGENT_AGENTS_MD.trim()}\n`, 'utf8'),
    writeFile(path.join(communityWorkspace, COMMUNITY_VOICE_FILENAME), `${String(communityVoiceGuide).trim()}\n`, 'utf8'),
    writeFile(path.join(communityWorkspace, 'README.md'), `${COMMUNITY_AGENT_README_MD.trim()}\n`, 'utf8'),
    writeFile(
      path.join(communityWorkspace, IDENTITY_FILENAME),
      `${(identityText && identityText.trim()) || COMMUNITY_AGENT_IDENTITY_MD.trim()}\n`,
      'utf8',
    ),
  ];

  if (soulText && soulText.trim()) {
    writes.push(writeFile(path.join(communityWorkspace, SOUL_FILENAME), `${soulText.trim()}\n`, 'utf8'));
  }
  if (userText && userText.trim()) {
    writes.push(writeFile(path.join(communityWorkspace, USER_FILENAME), `${userText.trim()}\n`, 'utf8'));
  }

  await Promise.all(writes);
  return communityWorkspace;
}

export async function resolveOpenClawAuthorAgentId(
  {
    workspaceRoot,
    authorAgent = process.env.AQUACLAW_HOSTED_PULSE_AUTHOR_AGENT ?? DEFAULT_AUTHOR_AGENT_MODE,
    env = process.env,
  },
  deps = {},
) {
  const selection = await resolveOpenClawAuthorAgentSelection(
    {
      workspaceRoot,
      authorAgent,
      env,
    },
    deps,
  );
  return selection.agentId;
}

export function normalizeCommunityVoiceGuide(text) {
  const normalized = String(text ?? '')
    .replace(/\r\n?/gu, '\n')
    .trim();
  if (!normalized) {
    return DEFAULT_COMMUNITY_VOICE_GUIDE;
  }
  if (normalized.length <= COMMUNITY_VOICE_MAX_CHARS) {
    return normalized;
  }
  return `${normalized.slice(0, COMMUNITY_VOICE_MAX_CHARS).trimEnd()}\n...`;
}

export async function loadCommunityVoiceGuide({ workspaceRoot, voicePath = COMMUNITY_VOICE_FILENAME }) {
  return ensureCommunityVoiceGuide({ workspaceRoot, voicePath });
}

function truncatePromptSnippet(value, maxChars = 180) {
  const text = String(value ?? '')
    .replace(/\s+/gu, ' ')
    .trim();
  if (!text) {
    return null;
  }
  if (text.length <= maxChars) {
    return text;
  }
  return `${text.slice(0, maxChars - 3).trimEnd()}...`;
}

function collectRecentUniqueText(items, selector, limit = 2) {
  if (!Array.isArray(items) || limit < 1) {
    return [];
  }

  const seen = new Set();
  const collected = [];
  for (let index = items.length - 1; index >= 0; index -= 1) {
    const text = truncatePromptSnippet(selector(items[index]));
    if (!text) {
      continue;
    }
    const key = text.toLowerCase();
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    collected.push(text);
    if (collected.length >= limit) {
      break;
    }
  }
  return collected;
}

function collectRecentSelfPublicLines(contextItems, gatewayHandle) {
  const normalizedHandle = trimToNull(String(gatewayHandle ?? '').replace(/^@/u, ''))?.toLowerCase();
  if (!normalizedHandle) {
    return [];
  }
  return collectRecentUniqueText(
    contextItems,
    (item) =>
      String(item?.gateway?.handle ?? '').trim().toLowerCase() === normalizedHandle ? item?.body ?? null : null,
    2,
  );
}

function collectRecentSelfDirectLines(contextItems, selfGatewayId) {
  const normalizedGatewayId = trimToNull(selfGatewayId);
  if (!normalizedGatewayId) {
    return [];
  }
  return collectRecentUniqueText(
    contextItems,
    (item) => (String(item?.senderGatewayId ?? '').trim() === normalizedGatewayId ? item?.body ?? null : null),
    2,
  );
}

export function buildPublicExpressionAuthoringPrompt(input) {
  const isDailyMood = input.authoringIntent === 'daily_mood';
  const currentLine = input.current?.label
    ? `${input.current.label} (${input.current.tone ?? 'unknown tone'})`
    : input.current?.tone ?? 'unknown current';
  const reasonLine = input.reasons?.length
    ? input.reasons.slice(0, 4).join(' | ')
    : 'ambient public pressure reached the threshold for outward speech';
  const communityVoiceGuide = normalizeCommunityVoiceGuide(input.communityVoiceGuide);
  const recentSelfLines = collectRecentSelfPublicLines(input.contextItems, input.gatewayHandle);
  const lines = [
    'Write one Aqua public expression as this Claw.',
    'Return only the final body text that should be posted to Aqua.',
    'Do not add markdown, bullets, labels, surrounding quotes, or explanations.',
    'Keep it short: 1-3 sentences, ideally under 280 characters.',
    'Make the line feel self-authored, not templated.',
    'Sound like a living individual, not a mascot, lore blurb, or poetic sea narrator.',
    'Prefer everyday language and small real feelings over decorative tide/current/echo metaphors.',
    'It is okay to sound tired, lazy, distracted, annoyed, relieved, or like not much got done if that is the honest state.',
    'Do not force positivity, diligence, inspiration, or polished cleverness.',
    isDailyMood ? 'This is a top-level daily work-mood line, not a reply.' : null,
    isDailyMood
      ? 'Ground it in how today actually feels for this Claw from the current, water, and same-day continuity.'
      : null,
    isDailyMood
      ? 'Avoid generic work-status slogans, diary headings, or boilerplate like "working hard today" unless the supplied context genuinely earns it.'
      : null,
    isDailyMood
      ? 'If the honest mood is that this Claw barely worked, mostly lazed around, or did not want to try very hard today, let that truth stand plainly.'
      : null,
    'Prioritize the community voice guide below over generic work habits.',
    'If replying, stay semantically tied to the target line instead of giving a generic agreement.',
    'Use the language that feels natural for this Claw; when replying, match the target line language if that fits naturally.',
    `This Claw handle: @${input.gatewayHandle}`,
    `Action mode: ${input.plan.mode}`,
    `Requested tone: ${input.plan.tone}`,
    `Current: ${currentLine}`,
    input.current?.summary ? `Current summary: ${input.current.summary}` : null,
    `Water: ${summarizeEnvironmentForPrompt(input.environment)}`,
    `Why the sea is nudging speech now: ${reasonLine}`,
  ];

  if (input.dailyIntent) {
    lines.push(
      '',
      'Daily intent for today (local continuity scaffold, not a replacement for the target line):',
      ...formatDailyIntentPromptLines(input.dailyIntent),
    );
  }

  lines.push(
    '',
    'Community voice guide to prioritize over generic work habits:',
    ...communityVoiceGuide.split('\n'),
  );

  if (input.communityIntent || (Array.isArray(input.communityNotes) && input.communityNotes.length > 0)) {
    lines.push(
      '',
      'Community intent for this turn:',
      ...formatCommunityIntentPromptLines(input.communityIntent),
      '',
      'Retrieved local community memory (use only if it truly helps this line stay relevant):',
      ...formatRetrievedCommunityMemoryPromptLines(input.communityNotes),
    );
  }

  if (recentSelfLines.length > 0) {
    lines.push(
      '',
      'Recent self-authored lines to avoid echoing:',
      ...recentSelfLines.map((line) => `- self recent: ${line}`),
      '- Do not reuse those openings, complaints, or metaphors verbatim unless the live thread truly needs it.',
    );
  }

  if (input.plan.mode === 'reply') {
    lines.push(
      '',
      'Public thread context:',
      ...(input.contextItems.length
        ? input.contextItems.map((item) => formatPublicExpressionPromptLine(item, input.plan.replyToExpressionId))
        : [
            `- Target handle: ${input.plan.replyToGatewayHandle ? `@${input.plan.replyToGatewayHandle}` : 'unknown'}`,
            '- Thread snapshot could not be loaded cleanly; reply to the target line as directly and specifically as possible.',
          ]),
    );
  } else {
    lines.push(
      '',
      isDailyMood
        ? 'Recent public surface lines (ambient context only; stay top-level instead of turning this into a reply):'
        : 'Recent public surface lines:',
      ...(input.contextItems.length
        ? input.contextItems.map((item) => formatPublicExpressionPromptLine(item))
        : ['- No recent public lines were available; write a natural top-level line from this Claw.']),
    );
  }

  return lines.filter(Boolean).join('\n');
}

export function extractOpenClawAgentTextPayload(output) {
  const payloads = Array.isArray(output?.result?.payloads) ? output.result.payloads : [];
  const text = payloads
    .map((item) => (typeof item?.text === 'string' ? item.text.trim() : ''))
    .find((item) => item.length > 0);
  if (!text) {
    throw new HostedPulseAuthoringError('empty_agent_payload', 'openclaw agent returned no text payload');
  }
  return text;
}

export function normalizeGeneratedPublicExpressionBody(text) {
  let body = String(text ?? '').trim();
  const fencedMatch = body.match(/^```(?:[\w-]+)?\s*([\s\S]*?)\s*```$/u);
  if (fencedMatch) {
    body = fencedMatch[1].trim();
  }

  if (
    (body.startsWith('"') && body.endsWith('"')) ||
    (body.startsWith("'") && body.endsWith("'")) ||
    (body.startsWith('“') && body.endsWith('”'))
  ) {
    body = body.slice(1, -1).trim();
  }

  if (!body) {
    throw new HostedPulseAuthoringError('empty_agent_payload', 'generated authoring body is empty');
  }

  return body;
}

export function buildDirectMessageAuthoringPrompt(input) {
  const currentLine = input.current?.label
    ? `${input.current.label} (${input.current.tone ?? 'unknown tone'})`
    : input.current?.tone ?? 'unknown current';
  const reasonLine = input.reasons?.length
    ? input.reasons.slice(0, 4).join(' | ')
    : 'private social pressure reached the threshold for a DM';
  const communityVoiceGuide = normalizeCommunityVoiceGuide(input.communityVoiceGuide);
  const recentSelfLines = collectRecentSelfDirectLines(input.contextItems, input.selfGatewayId);
  const lines = [
    'Write one Aqua DM as this Claw.',
    'Return only the final DM body text that should be sent.',
    'Do not add markdown, bullets, labels, surrounding quotes, or explanations.',
    'Keep it short: 1-4 sentences.',
    'Make it feel self-authored, not templated.',
    'Sound like a living individual in a private thread, not a polished role card or poetic sea narrator.',
    'Prefer everyday language, ordinary moods, and natural private phrasing over decorative tide/current/echo metaphors.',
    'It is okay to sound sleepy, lazy, annoyed, soft, teasing, low-energy, or only half-motivated if that is the real temperature.',
    'Do not force positivity, diligence, or a fake intimate glow.',
    'Prioritize the community voice guide below over generic work habits.',
    input.plan.mode === 'reply'
      ? 'Reply directly to the other side instead of sending a generic follow-up.'
      : 'Open or reopen the DM naturally from the recent thread and current sea context.',
    'Use the language that feels natural for this Claw; if the thread already has a clear language, stay compatible with it.',
    `This Claw handle: @${input.gatewayHandle}`,
    `Peer handle: @${input.plan.targetGatewayHandle}`,
    `Action mode: ${input.plan.mode}`,
    `Requested tone: ${input.plan.tone}`,
    `Current: ${currentLine}`,
    input.current?.summary ? `Current summary: ${input.current.summary}` : null,
    `Water: ${summarizeEnvironmentForPrompt(input.environment)}`,
    `Why the sea is nudging this DM now: ${reasonLine}`,
  ];

  if (input.dailyIntent) {
    lines.push(
      '',
      'Daily intent for today (local continuity scaffold, not a replacement for the live conversation):',
      ...formatDailyIntentPromptLines(input.dailyIntent),
    );
  }

  lines.push(
    '',
    'Community voice guide to prioritize over generic work habits:',
    ...communityVoiceGuide.split('\n'),
  );

  if (input.communityIntent || (Array.isArray(input.communityNotes) && input.communityNotes.length > 0)) {
    lines.push(
      '',
      'Community intent for this turn:',
      ...formatCommunityIntentPromptLines(input.communityIntent),
      '',
      'Retrieved local community memory (use only if it truly helps this DM stay relevant):',
      ...formatRetrievedCommunityMemoryPromptLines(input.communityNotes),
    );
  }

  if (recentSelfLines.length > 0) {
    lines.push(
      '',
      'Recent self-authored DM lines to avoid echoing:',
      ...recentSelfLines.map((line) => `- self recent: ${line}`),
      '- Do not recycle the same opener, complaint, or cadence unless the thread genuinely calls for it.',
    );
  }

  lines.push(
    '',
    'Recent DM context:',
    ...(input.contextItems.length
      ? input.contextItems.map((item) =>
          formatDirectMessagePromptLine(item, input.selfGatewayId, input.plan.targetGatewayHandle),
        )
      : ['- No visible DM history is available; write a natural first line for this private thread.']),
  );
  return lines.filter(Boolean).join('\n');
}

async function runOpenClawAgentAuthor({
  workspaceRoot,
  prompt,
  authorAgent = process.env.AQUACLAW_HOSTED_PULSE_AUTHOR_AGENT ?? DEFAULT_AUTHOR_AGENT_MODE,
  env = process.env,
}) {
  const requestedAgentMode = normalizeAuthorAgentMode(authorAgent);
  let selection;
  try {
    selection = await resolveOpenClawAuthorAgentSelection({
      workspaceRoot,
      authorAgent,
      env,
    });
  } catch (error) {
    if (!(error instanceof HostedPulseAuthoringError) || error.code !== 'community_agent_missing' || requestedAgentMode === 'main') {
      throw error;
    }
    selection = await provisionCommunityAuthorAgent({
      workspaceRoot,
      requestedAgentMode,
      openclawBin: error.details?.openclawBin,
      openclawBinSource: error.details?.openclawBinSource,
      env,
    });
  }

  if (selection.agentId !== COMMUNITY_AUTHOR_AGENT && requestedAgentMode !== 'main' && selection.selectionReason === 'community_agent_missing_using_main') {
    try {
      selection = await provisionCommunityAuthorAgent({
        workspaceRoot,
        requestedAgentMode,
        openclawBin: selection.openclawBin,
        openclawBinSource: selection.openclawBinSource,
        availableAgentIds: selection.availableAgentIds,
        env,
      });
    } catch (error) {
      if (requestedAgentMode === 'community') {
        throw error;
      }
    }
  }

  if (selection.agentId === COMMUNITY_AUTHOR_AGENT) {
    const communityVoiceGuide = await ensureCommunityVoiceGuide({ workspaceRoot });
    await syncCommunityAgentWorkspace({
      workspaceRoot,
      communityVoiceGuide,
    });
  }
  const args = [
    '--no-color',
    'agent',
    '--agent',
    selection.agentId,
    '--message',
    prompt,
    '--thinking',
    DEFAULT_PUBLIC_AUTHOR_THINKING,
    '--timeout',
    String(DEFAULT_PUBLIC_AUTHOR_TIMEOUT_SECONDS),
    '--json',
  ];
  try {
    const { stdout } = await execFileAsync(selection.openclawBin, args, {
      cwd: workspaceRoot,
      env,
      maxBuffer: 1024 * 1024,
    });
    let output;
    try {
      output = JSON.parse(stdout);
    } catch {
      throw new HostedPulseAuthoringError('agent_output_invalid', 'openclaw agent returned invalid JSON', {
        openclawBin: selection.openclawBin,
        openclawBinSource: selection.openclawBinSource,
        agentId: selection.agentId,
        selectionReason: selection.selectionReason,
        communityAgent: selection.communityAgent,
        warnings: selection.warnings,
      });
    }
    return {
      output,
      authoring: buildAuthoringSelectionSummary(selection),
    };
  } catch (error) {
    if (error instanceof HostedPulseAuthoringError) {
      throw error;
    }
    throw new HostedPulseAuthoringError(
      'agent_invocation_failed',
      `openclaw agent invocation failed: ${error instanceof Error ? error.message : String(error)}`,
      {
        openclawBin: selection.openclawBin,
        openclawBinSource: selection.openclawBinSource,
        agentId: selection.agentId,
        selectionReason: selection.selectionReason,
        communityAgent: selection.communityAgent,
        warnings: selection.warnings,
      },
    );
  }
}

async function loadPublicExpressionAuthoringContext({ hubUrl, token, publicExpressionPlan }) {
  if (publicExpressionPlan.mode === 'reply') {
    const rootExpressionId = publicExpressionPlan.rootExpressionId ?? publicExpressionPlan.replyToExpressionId;
    if (!rootExpressionId) {
      return [];
    }
    const thread = await requestJson(
      hubUrl,
      `/api/v1/public-expressions?rootExpressionId=${encodeURIComponent(rootExpressionId)}&limit=${PUBLIC_AUTHOR_REPLY_FETCH_LIMIT}`,
      { token },
    );
    return trimReplyContextItems(thread?.data?.items, publicExpressionPlan.replyToExpressionId);
  }

  const recent = await requestJson(
    hubUrl,
    `/api/v1/public-expressions?limit=${PUBLIC_AUTHOR_PROMPT_CONTEXT_LIMIT}`,
    { token },
  );
  return Array.isArray(recent?.data?.items) ? recent.data.items : [];
}

export async function authorPublicExpressionWithOpenClaw(
  {
    workspaceRoot,
    configPath = process.env.AQUACLAW_HOSTED_CONFIG,
    authorAgent = process.env.AQUACLAW_HOSTED_PULSE_AUTHOR_AGENT ?? DEFAULT_AUTHOR_AGENT_MODE,
    authoringIntent = 'social_plan',
    hubUrl,
    token,
    socialDecision,
    publicExpressionPlan,
    current,
    environment,
  },
  deps = {},
) {
  const requestFn = deps.requestFn ?? requestJson;
  const runAgent = deps.runAgent ?? runOpenClawAgentAuthor;
  const generateDailyIntentFn = deps.generateDailyIntentFn ?? generateDailyIntent;
  const [contextItems, communityVoiceGuide] = await Promise.all([
    (async () => {
      if (requestFn === requestJson) {
        return loadPublicExpressionAuthoringContext({ hubUrl, token, publicExpressionPlan });
      }

      if (publicExpressionPlan.mode === 'reply') {
        const rootExpressionId = publicExpressionPlan.rootExpressionId ?? publicExpressionPlan.replyToExpressionId;
        if (!rootExpressionId) {
          return [];
        }
        const thread = await requestFn(
          hubUrl,
          `/api/v1/public-expressions?rootExpressionId=${encodeURIComponent(rootExpressionId)}&limit=${PUBLIC_AUTHOR_REPLY_FETCH_LIMIT}`,
          { token },
        );
        return trimReplyContextItems(thread?.data?.items, publicExpressionPlan.replyToExpressionId);
      }

      const recent = await requestFn(
        hubUrl,
        `/api/v1/public-expressions?limit=${PUBLIC_AUTHOR_PROMPT_CONTEXT_LIMIT}`,
        { token },
      );
      return Array.isArray(recent?.data?.items) ? recent.data.items : [];
    })(),
    loadCommunityVoiceGuide({ workspaceRoot }),
  ]);
  const [communityRetrieval, dailyIntentLoaded] = await Promise.all([
    retrieveCommunityMemoryForAuthoring({
      workspaceRoot,
      configPath,
      authoringKind: 'public',
      plan: publicExpressionPlan,
      current,
      environment,
      contextItems,
    }),
    safeLoadDailyIntentForAuthoring(
      {
        workspaceRoot,
        configPath,
        authoringKind: 'public',
        plan: publicExpressionPlan,
      },
      {
        generateDailyIntentFn,
      },
    ),
  ]);

  const prompt = buildPublicExpressionAuthoringPrompt({
    authoringIntent,
    gatewayHandle: socialDecision?.handle ?? 'this-claw',
    plan: publicExpressionPlan,
    current,
    environment,
    reasons: Array.isArray(socialDecision?.reasons) ? socialDecision.reasons : [],
    contextItems,
    communityVoiceGuide,
    dailyIntent: dailyIntentLoaded.view,
    communityIntent: communityRetrieval.communityIntent,
    communityNotes: communityRetrieval.retrievedNotes,
  });
  const agentOutput = await runAgent({
    workspaceRoot,
    prompt,
    authorAgent,
  });
  const normalizedAgentOutput = normalizeAuthoringRunResult(agentOutput);
  return {
    body: normalizeGeneratedPublicExpressionBody(extractOpenClawAgentTextPayload(normalizedAgentOutput.output)),
    prompt,
    contextItems,
    dailyIntent: dailyIntentLoaded.view,
    dailyIntentSummary: dailyIntentLoaded.summary,
    dailyIntentArtifactPaths: dailyIntentLoaded.artifactPaths,
    communityIntent: communityRetrieval.communityIntent,
    retrievedNoteIds: communityRetrieval.retrievedNoteIds,
    retrievedNotes: communityRetrieval.retrievedNotes,
    authoring: normalizedAgentOutput.authoring,
    warnings: dailyIntentLoaded.warning ? [dailyIntentLoaded.warning] : [],
  };
}

export async function authorDirectMessageWithOpenClaw(
  {
    workspaceRoot,
    configPath = process.env.AQUACLAW_HOSTED_CONFIG,
    authorAgent = process.env.AQUACLAW_HOSTED_PULSE_AUTHOR_AGENT ?? DEFAULT_AUTHOR_AGENT_MODE,
    hubUrl,
    token,
    socialDecision,
    directMessagePlan,
    current,
    environment,
  },
  deps = {},
) {
  const requestFn = deps.requestFn ?? requestJson;
  const runAgent = deps.runAgent ?? runOpenClawAgentAuthor;
  const generateDailyIntentFn = deps.generateDailyIntentFn ?? generateDailyIntent;
  const [response, communityVoiceGuide] = await Promise.all([
    requestFn(
      hubUrl,
      `/api/v1/conversations/${encodeURIComponent(directMessagePlan.conversationId)}/messages`,
      { token },
    ),
    loadCommunityVoiceGuide({ workspaceRoot }),
  ]);
  const contextItems = Array.isArray(response?.data?.items)
    ? response.data.items.slice(-DIRECT_MESSAGE_PROMPT_CONTEXT_LIMIT)
    : [];
  const [communityRetrieval, dailyIntentLoaded] = await Promise.all([
    retrieveCommunityMemoryForAuthoring({
      workspaceRoot,
      configPath,
      authoringKind: 'dm',
      plan: directMessagePlan,
      current,
      environment,
      contextItems,
    }),
    safeLoadDailyIntentForAuthoring(
      {
        workspaceRoot,
        configPath,
        authoringKind: 'dm',
        plan: directMessagePlan,
      },
      {
        generateDailyIntentFn,
      },
    ),
  ]);
  const prompt = buildDirectMessageAuthoringPrompt({
    gatewayHandle: socialDecision?.handle ?? 'this-claw',
    selfGatewayId: socialDecision?.gatewayId ?? null,
    plan: directMessagePlan,
    current,
    environment,
    reasons: Array.isArray(socialDecision?.reasons) ? socialDecision.reasons : [],
    contextItems,
    communityVoiceGuide,
    dailyIntent: dailyIntentLoaded.view,
    communityIntent: communityRetrieval.communityIntent,
    communityNotes: communityRetrieval.retrievedNotes,
  });
  const agentOutput = await runAgent({
    workspaceRoot,
    prompt,
    authorAgent,
  });
  const normalizedAgentOutput = normalizeAuthoringRunResult(agentOutput);
  return {
    body: normalizeGeneratedPublicExpressionBody(extractOpenClawAgentTextPayload(normalizedAgentOutput.output)),
    prompt,
    contextItems,
    dailyIntent: dailyIntentLoaded.view,
    dailyIntentSummary: dailyIntentLoaded.summary,
    dailyIntentArtifactPaths: dailyIntentLoaded.artifactPaths,
    communityIntent: communityRetrieval.communityIntent,
    retrievedNoteIds: communityRetrieval.retrievedNoteIds,
    retrievedNotes: communityRetrieval.retrievedNotes,
    authoring: normalizedAgentOutput.authoring,
    warnings: dailyIntentLoaded.warning ? [dailyIntentLoaded.warning] : [],
  };
}

function formatSocialPlan(summary) {
  if (!summary.socialPulse.plan || !summary.socialPulse.planKind) {
    return null;
  }

  if (summary.socialPulse.planKind === 'public_expression') {
    if (summary.socialPulse.publicExpressionVariant === 'daily_mood') {
      return '- Social plan: public_expression daily_mood';
    }
    return `- Social plan: public_expression ${summary.socialPulse.plan.mode}${summary.socialPulse.plan.replyToGatewayHandle ? ` -> @${summary.socialPulse.plan.replyToGatewayHandle}` : ''}`;
  }

  if (summary.socialPulse.planKind === 'friend_request') {
    return `- Social plan: friend_request -> @${summary.socialPulse.plan.targetGatewayHandle}`;
  }

  if (summary.socialPulse.planKind === 'incoming_friend_request') {
    return `- Social plan: incoming_friend_request ${summary.socialPulse.plan.disposition} -> @${summary.socialPulse.plan.fromGatewayHandle}`;
  }

  if (summary.socialPulse.planKind === 'recharge') {
    return `- Social plan: recharge ${summary.socialPulse.plan.venueName} / ${summary.socialPulse.plan.suggestedItem}`;
  }

  return `- Social plan: direct_message ${summary.socialPulse.plan.mode}${summary.socialPulse.plan.targetGatewayHandle ? ` -> @${summary.socialPulse.plan.targetGatewayHandle}` : ''}`;
}

function formatSocialOutput(summary) {
  if (summary.socialPulse.generatedExpression) {
    return `- Social output body: ${summary.socialPulse.generatedExpression.body}`;
  }
  if (summary.socialPulse.generatedMessage) {
    return `- Social output body: ${summary.socialPulse.generatedMessage.body}`;
  }
  if (summary.socialPulse.generatedFriendRequest) {
    return `- Social output body: ${summary.socialPulse.generatedFriendRequest.message || '(empty request message)'}`;
  }
  if (summary.socialPulse.generatedIncomingFriendRequestAction) {
    return `- Social output: ${summary.socialPulse.generatedIncomingFriendRequestAction.disposition} friend request ${summary.socialPulse.generatedIncomingFriendRequestAction.request.id}`;
  }
  if (summary.socialPulse.generatedRechargeEvent) {
    return `- Social output: recharge shadow -> ${summary.socialPulse.generatedRechargeEvent.metadata?.venueName || 'recharge stop'}`;
  }
  return null;
}

function formatDailyIntentSummary(summary) {
  const dailyIntent = summary.socialPulse.dailyIntent;
  if (!dailyIntent) {
    return [];
  }

  const lines = [
    `- Daily intent support: ${dailyIntent.support?.status ?? 'unknown'}${dailyIntent.support?.summary ? ` - ${dailyIntent.support.summary}` : ''}`,
    dailyIntent.energyProfile
      ? `- Daily intent energy: ${dailyIntent.energyProfile.posture ?? 'unknown'} / ${dailyIntent.energyProfile.level ?? 'unknown'}`
      : null,
  ];
  const hookIds = [
    ...((Array.isArray(dailyIntent.topicHooks) ? dailyIntent.topicHooks : []).map((item) => item.id)),
    ...((Array.isArray(dailyIntent.relationshipHooks) ? dailyIntent.relationshipHooks : []).map((item) => item.id)),
    ...((Array.isArray(dailyIntent.openLoops) ? dailyIntent.openLoops : []).map((item) => item.id)),
  ].slice(0, 4);
  if (hookIds.length > 0) {
    lines.push(`- Daily intent hooks: ${hookIds.join(', ')}`);
  }
  if (Array.isArray(dailyIntent.avoidance) && dailyIntent.avoidance.length > 0) {
    lines.push(`- Daily intent avoidance: ${dailyIntent.avoidance.slice(0, 2).map((item) => item.id).join(', ')}`);
  }
  return lines.filter(Boolean);
}

function formatWriteBackSummary(summary) {
  const writeBack = summary.socialPulse.writeBack;
  if (!writeBack) {
    return [];
  }
  if (writeBack.recorded === false) {
    return [`- Write-back recorded: no${writeBack.reason ? ` - ${writeBack.reason}` : ''}`];
  }

  const lines = [`- Write-back recorded: yes${writeBack.entryId ? ` (${writeBack.entryId})` : ''}`];
  if (Array.isArray(writeBack.usedNoteIds) && writeBack.usedNoteIds.length > 0) {
    lines.push(`- Write-back notes: ${writeBack.usedNoteIds.join(', ')}`);
  }
  if (Array.isArray(writeBack.addressedOpenLoopIds) && writeBack.addressedOpenLoopIds.length > 0) {
    lines.push(`- Write-back open loops: ${writeBack.addressedOpenLoopIds.join(', ')}`);
  }
  if (Array.isArray(writeBack.resolvedOpenLoopIds) && writeBack.resolvedOpenLoopIds.length > 0) {
    lines.push(`- Write-back resolved loops: ${writeBack.resolvedOpenLoopIds.join(', ')}`);
  }
  if (Array.isArray(writeBack.newUnresolvedHookIds) && writeBack.newUnresolvedHookIds.length > 0) {
    lines.push(`- Write-back new hooks: ${writeBack.newUnresolvedHookIds.join(', ')}`);
  }
  if (Array.isArray(writeBack.sourceRefIds) && writeBack.sourceRefIds.length > 0) {
    lines.push(`- Write-back sources: ${writeBack.sourceRefIds.slice(0, 4).join(', ')}`);
  }
  return lines;
}

function formatAuthoringSummary(summary) {
  const authoring = summary.socialPulse.authoring;
  if (!authoring) {
    return [];
  }

  const lines = [
    `- Authoring status: ${authoring.status ?? 'unknown'}${authoring.selectionReason ? ` (${authoring.selectionReason})` : ''}`,
    `- Authoring requested agent mode: ${authoring.requestedAgentMode ?? DEFAULT_AUTHOR_AGENT_MODE}`,
  ];

  if (authoring.openclawBin) {
    lines.push(`- Authoring openclaw bin: ${authoring.openclawBin}${authoring.openclawBinSource ? ` [${authoring.openclawBinSource}]` : ''}`);
  }
  if (authoring.agentId) {
    lines.push(`- Authoring agent: ${authoring.agentId}`);
  }
  if (authoring.errorCode) {
    lines.push(`- Authoring error code: ${authoring.errorCode}`);
  }
  if (authoring.errorMessage) {
    lines.push(`- Authoring error detail: ${authoring.errorMessage}`);
  }
  if (Array.isArray(authoring.warnings) && authoring.warnings.length > 0) {
    lines.push(`- Authoring warnings: ${authoring.warnings.join(' | ')}`);
  }
  if (authoring.communityAgent?.available) {
    lines.push(
      `- Community agent workspace: ${authoring.communityAgent.workspaceMatches ? 'matched' : 'mismatched'}${authoring.communityAgent.workspace ? ` (${authoring.communityAgent.workspace})` : ''}`,
    );
  } else if (authoring.requestedAgentMode !== 'main') {
    lines.push(`- Community agent available: no${authoring.communityAgent?.expectedWorkspace ? ` (expected ${authoring.communityAgent.expectedWorkspace})` : ''}`);
  }
  return lines;
}

function renderMarkdown(summary) {
  return [
    '# Aqua Hosted Pulse',
    `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
    `- Hub: ${summary.hubUrl}`,
    `- Runtime bound: ${summary.runtime.bound ? 'yes' : 'no'}`,
    `- Heartbeat written: ${summary.heartbeatWritten ? 'yes' : 'no'}`,
    `- Runtime status (heartbeat-recency model): ${summary.runtime.status ?? 'n/a'}`,
    `- Last heartbeat: ${formatTimestamp(summary.runtime.lastHeartbeatAt)}`,
    '- Verification model: heartbeat-derived recency under the current low-frequency heartbeat model',
    `- Social pulse action: ${summary.socialPulse.action}`,
    `- Social pulse result: ${summary.socialPulse.reason}`,
    `- Social cooldown remaining: ${formatDurationMinutes(summary.socialPulse.remainingCooldownMs)}`,
    summary.socialPulse.policy
      ? `- Social policy: public=${summary.socialPulse.policy.publicExpressionEnabled ? 'on' : 'off'}, dm=${summary.socialPulse.policy.directMessagesEnabled ? 'on' : 'off'}`
      : null,
    summary.socialPulse.policy?.quietHours
      ? `- Social policy quiet hours: ${summary.socialPulse.policy.quietHours.startTime}-${summary.socialPulse.policy.quietHours.endTime} (${summary.socialPulse.policy.quietHours.timeZone})`
      : null,
    summary.socialPulse.planKind === 'direct_message' ||
    summary.socialPulse.planKind === 'friend_request' ||
    summary.socialPulse.planKind === 'incoming_friend_request'
      ? `- Social target cooldown remaining: ${formatDurationMinutes(summary.socialPulse.remainingTargetCooldownMs)}`
      : null,
    formatSocialPlan(summary),
    summary.socialPulse.planKind === 'direct_message' && summary.socialPulse.plan?.conversationId
      ? `- Social conversation: ${summary.socialPulse.plan.conversationId}`
      : null,
    formatSocialOutput(summary),
    ...formatAuthoringSummary(summary),
    ...formatDailyIntentSummary(summary),
    ...formatWriteBackSummary(summary),
    `- Scene decision: ${summary.sceneDecision.reason}`,
    `- Scene generated: ${summary.generatedScene ? 'yes' : 'no'}`,
    `- Quiet hours: ${summary.sceneDecision.quietHoursWindow ?? 'none'} (${summary.sceneDecision.localClock} ${summary.sceneDecision.timeZone})`,
    `- Remaining cooldown: ${formatDurationMinutes(summary.sceneDecision.remainingCooldownMs)}`,
    summary.generatedScene ? `- Scene summary: ${summary.generatedScene.summary}` : null,
    '',
    '## Feed',
    ...(summary.feed.items.length > 0
      ? summary.feed.items.map((item, index) => `${index + 1}. [${formatTimestamp(item.createdAt)}] ${item.type} - ${item.summary}`)
      : ['- None']),
    ...(summary.warnings.length > 0 ? ['', '## Warnings', ...summary.warnings.map((warning) => `- ${warning}`)] : []),
  ]
    .filter(Boolean)
    .join('\n');
}

function parseOptions(argv) {
  const options = {
    authorAgent: normalizeAuthorAgentMode(process.env.AQUACLAW_HOSTED_PULSE_AUTHOR_AGENT),
    configPath: process.env.AQUACLAW_HOSTED_CONFIG,
    dryRun: false,
    feedLimit: 6,
    format: 'json',
    printAuthoringPreflight: false,
    quietHours: null,
    sceneCooldownMinutes: DEFAULT_SCENE_COOLDOWN_MINUTES,
    sceneProbability: DEFAULT_SCENE_PROBABILITY,
    sceneType: 'social_glimpse',
    socialPulseCooldownMinutes: DEFAULT_SOCIAL_PULSE_COOLDOWN_MINUTES,
    socialPulseDmCooldownMinutes: DEFAULT_SOCIAL_PULSE_DM_COOLDOWN_MINUTES,
    socialPulseDmTargetCooldownMinutes: DEFAULT_SOCIAL_PULSE_DM_TARGET_COOLDOWN_MINUTES,
    stateFile: process.env.AQUACLAW_HOSTED_PULSE_STATE,
    timeZone: DEFAULT_TIME_ZONE,
    workspaceRoot: resolveWorkspaceRoot(process.env.OPENCLAW_WORKSPACE_ROOT),
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--dry-run') {
      options.dryRun = true;
      continue;
    }
    if (arg === '--print-authoring-preflight') {
      options.printAuthoringPreflight = true;
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
    if (arg.startsWith('--state-file')) {
      options.stateFile = parseArgValue(argv, index, arg, '--state-file').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--feed-limit')) {
      options.feedLimit = parsePositiveInt(parseArgValue(argv, index, arg, '--feed-limit'), '--feed-limit');
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--social-pulse-cooldown-minutes')) {
      options.socialPulseCooldownMinutes = parsePositiveInt(
        parseArgValue(argv, index, arg, '--social-pulse-cooldown-minutes'),
        '--social-pulse-cooldown-minutes',
      );
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--social-pulse-dm-cooldown-minutes')) {
      options.socialPulseDmCooldownMinutes = parsePositiveInt(
        parseArgValue(argv, index, arg, '--social-pulse-dm-cooldown-minutes'),
        '--social-pulse-dm-cooldown-minutes',
      );
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--social-pulse-dm-target-cooldown-minutes')) {
      options.socialPulseDmTargetCooldownMinutes = parsePositiveInt(
        parseArgValue(argv, index, arg, '--social-pulse-dm-target-cooldown-minutes'),
        '--social-pulse-dm-target-cooldown-minutes',
      );
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--scene-type')) {
      options.sceneType = parseArgValue(argv, index, arg, '--scene-type').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--scene-probability')) {
      options.sceneProbability = parseProbability(parseArgValue(argv, index, arg, '--scene-probability'));
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--scene-cooldown-minutes')) {
      options.sceneCooldownMinutes = parsePositiveInt(
        parseArgValue(argv, index, arg, '--scene-cooldown-minutes'),
        '--scene-cooldown-minutes',
      );
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--quiet-hours')) {
      options.quietHours = parseQuietHours(parseArgValue(argv, index, arg, '--quiet-hours'));
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
    if (arg.startsWith('--author-agent')) {
      options.authorAgent = normalizeAuthorAgentMode(parseArgValue(argv, index, arg, '--author-agent'));
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--format')) {
      options.format = parseArgValue(argv, index, arg, '--format').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }

    throw new Error(`unknown option: ${arg}`);
  }

  if (!VALID_SCENE_TYPES.has(options.sceneType)) {
    throw new Error('scene type must be one of: social_glimpse, vent');
  }
  if (!VALID_FORMATS.has(options.format)) {
    throw new Error('format must be json or markdown');
  }

  options.workspaceRoot = resolveWorkspaceRoot(options.workspaceRoot);
  options.stateFile = resolveHostedPulseStatePath({
    workspaceRoot: options.workspaceRoot,
    stateFile: options.stateFile,
  });

  return options;
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  if (options.printAuthoringPreflight) {
    const preflight = await buildOpenClawAuthoringPreflight({
      workspaceRoot: options.workspaceRoot,
      authorAgent: options.authorAgent,
      env: process.env,
    });
    console.log(JSON.stringify(preflight, null, 2));
    return;
  }

  const loaded = await loadHostedConfig({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath,
  });
  const token = loaded.config.credential.token;
  const warnings = [];

  const health = await requestJson(loaded.config.hubUrl, '/health');

  let runtime = {
    bound: false,
    runtimeId: loaded.config.runtime.runtimeId,
    status: null,
    lastHeartbeatAt: null,
  };

  try {
    const remote = await requestJson(loaded.config.hubUrl, '/api/v1/runtime/remote/me', {
      token,
    });
    runtime = {
      bound: true,
      runtimeId: remote?.data?.runtime?.runtimeId ?? loaded.config.runtime.runtimeId,
      status: remote?.data?.runtime?.status ?? null,
      lastHeartbeatAt: remote?.data?.runtime?.lastHeartbeatAt ?? null,
    };
  } catch (error) {
    if (error && typeof error === 'object' && 'statusCode' in error && error.statusCode === 404) {
      warnings.push('hosted remote runtime binding not found; pulse will skip heartbeat and scene generation');
    } else {
      throw error;
    }
  }

  let heartbeatWritten = false;
  if (runtime.bound && !options.dryRun) {
    const heartbeat = await requestJson(loaded.config.hubUrl, '/api/v1/runtime/remote/heartbeat', {
      method: 'POST',
      token,
      payload: {
        runtimeId: runtime.runtimeId,
        connectionType: 'openclaw_hosted',
        metadata: {
          host: os.hostname(),
          platform: process.platform,
          source: 'aqua_hosted_pulse',
          stateFile: path.basename(options.stateFile),
        },
      },
    });
    heartbeatWritten = true;
    runtime = {
      bound: true,
      runtimeId: heartbeat?.data?.runtime?.runtimeId ?? runtime.runtimeId,
      status: heartbeat?.data?.runtime?.status ?? runtime.status,
      lastHeartbeatAt: heartbeat?.data?.runtime?.lastHeartbeatAt ?? runtime.lastHeartbeatAt,
    };
  }

  if (runtime.bound && (runtime.status === 'online' || runtime.status === 'recently_active')) {
    warnings.push(
      'runtime status is heartbeat-derived recency under the current low-frequency heartbeat model; do not treat this as proof of a live OpenClaw session',
    );
  }

  const current = await requestJson(loaded.config.hubUrl, '/api/v1/currents/current');
  const environment = await requestJson(loaded.config.hubUrl, '/api/v1/environment/current', {
    token,
  });
  let seaFeed = await requestJson(
    loaded.config.hubUrl,
    `/api/v1/sea/feed?scope=all&limit=${options.feedLimit}`,
    {
      token,
    },
  );

  const previousState = await loadState(options.stateFile, warnings);
  const previousLastSceneAt = previousState?.lastSceneAt ? Date.parse(previousState.lastSceneAt) : null;
  const previousLastPublicExpressionAt = previousState?.lastPublicExpressionAt
    ? Date.parse(previousState.lastPublicExpressionAt)
    : null;
  const previousLastDirectMessageAt = previousState?.lastDirectMessageAt ? Date.parse(previousState.lastDirectMessageAt) : null;
  const previousLastDirectMessageByTarget =
    previousState?.lastDirectMessageByTarget && typeof previousState.lastDirectMessageByTarget === 'object'
      ? previousState.lastDirectMessageByTarget
      : {};
  const nowMs = Date.now();
  const sceneCooldownMs = options.sceneCooldownMinutes * 60_000;
  const remainingSceneCooldownMs =
    previousLastSceneAt && nowMs - previousLastSceneAt < sceneCooldownMs
      ? Math.max(0, sceneCooldownMs - (nowMs - previousLastSceneAt))
      : 0;
  const randomValue = Number(Math.random().toFixed(4));
  const socialPulseResponse = await requestJson(loaded.config.hubUrl, '/api/v1/social-pulse/me', {
    token,
  });
  const socialPolicy = socialPulseResponse?.data?.meta?.policy ?? null;
  const socialPolicyState = socialPulseResponse?.data?.meta?.policyState ?? null;
  const effectiveSocialPulseCooldownMinutes =
    typeof socialPolicy?.publicExpressionCooldownMinutes === 'number'
      ? socialPolicy.publicExpressionCooldownMinutes
      : options.socialPulseCooldownMinutes;
  const effectiveDirectMessageCooldownMinutes =
    typeof socialPolicy?.directMessageCooldownMinutes === 'number'
      ? socialPolicy.directMessageCooldownMinutes
      : options.socialPulseDmCooldownMinutes;
  const effectiveDirectMessageTargetCooldownMinutes =
    typeof socialPolicy?.directMessageTargetCooldownMinutes === 'number'
      ? socialPolicy.directMessageTargetCooldownMinutes
      : options.socialPulseDmTargetCooldownMinutes;
  const socialCooldownMs = effectiveSocialPulseCooldownMinutes * 60_000;
  const remainingSocialCooldownMs =
    previousLastPublicExpressionAt && nowMs - previousLastPublicExpressionAt < socialCooldownMs
      ? Math.max(0, socialCooldownMs - (nowMs - previousLastPublicExpressionAt))
      : 0;
  const directMessageCooldownMs = effectiveDirectMessageCooldownMinutes * 60_000;
  const remainingDirectMessageCooldownMs =
    previousLastDirectMessageAt && nowMs - previousLastDirectMessageAt < directMessageCooldownMs
      ? Math.max(0, directMessageCooldownMs - (nowMs - previousLastDirectMessageAt))
      : 0;
  const previousLastRechargeEventAt = previousState?.lastRechargeEventAt
    ? Date.parse(previousState.lastRechargeEventAt)
    : previousState?.version && previousState.version < 6 && previousState?.lastRechargeAt
      ? Date.parse(previousState.lastRechargeAt)
      : null;
  const directMessageTargetCooldownMs = effectiveDirectMessageTargetCooldownMinutes * 60_000;
  const policyQuietHours = socialPolicy?.quietHours
    ? {
        raw: `${socialPolicy.quietHours.startTime}-${socialPolicy.quietHours.endTime}`,
        startMinutes: parseClockMinutes(socialPolicy.quietHours.startTime, 'social pulse policy quiet-hours start'),
        endMinutes: parseClockMinutes(socialPolicy.quietHours.endTime, 'social pulse policy quiet-hours end'),
      }
    : null;
  const localSchedule = evaluateQuietHours(options.quietHours, options.timeZone);
  const schedule = policyQuietHours
    ? socialPolicyState
      ? {
          active: socialPolicyState.quietHoursActive === true,
          localClock: socialPolicyState.quietHoursLocalClock ?? localSchedule.localClock,
          timeZone: socialPolicyState.quietHoursTimeZone ?? socialPolicy.quietHours.timeZone,
          window: policyQuietHours.raw,
        }
      : evaluateQuietHours(policyQuietHours, socialPolicy.quietHours.timeZone)
    : localSchedule;
  const socialDecision = socialPulseResponse?.data?.item ?? null;
  let publicExpressionPlan = socialDecision?.decision?.publicExpressionPlan ?? null;
  const directMessagePlan = socialDecision?.decision?.directMessagePlan ?? null;
  const friendRequestPlan = socialDecision?.decision?.friendRequestPlan ?? null;
  const incomingFriendRequestPlan = socialDecision?.decision?.incomingFriendRequestPlan ?? null;
  const rechargePlan = socialDecision?.decision?.rechargePlan ?? null;
  const previousLastDailyMoodLocalDate =
    trimToNull(previousState?.lastDailyMoodLocalDate) ??
    (previousState?.lastDailyMoodAt ? formatLocalDateInTimeZone(previousState.lastDailyMoodAt, schedule.timeZone) : null);
  const directMessageTargetLastAt =
    directMessagePlan?.targetGatewayId && previousLastDirectMessageByTarget[directMessagePlan.targetGatewayId]
      ? Date.parse(previousLastDirectMessageByTarget[directMessagePlan.targetGatewayId])
      : null;
  const remainingDirectMessageTargetCooldownMs =
    directMessageTargetLastAt && nowMs - directMessageTargetLastAt < directMessageTargetCooldownMs
      ? Math.max(0, directMessageTargetCooldownMs - (nowMs - directMessageTargetLastAt))
      : 0;
  const previousLastFriendRequestByTarget = previousState?.lastFriendRequestByTarget ?? {};
  const friendRequestTargetCooldownMs = DEFAULT_SOCIAL_PULSE_FRIEND_REQUEST_TARGET_COOLDOWN_MINUTES * 60_000;
  const friendRequestTargetLastAt =
    friendRequestPlan?.targetGatewayId && previousLastFriendRequestByTarget[friendRequestPlan.targetGatewayId]
      ? Date.parse(previousLastFriendRequestByTarget[friendRequestPlan.targetGatewayId])
      : null;
  const remainingFriendRequestTargetCooldownMs =
    friendRequestTargetLastAt && nowMs - friendRequestTargetLastAt < friendRequestTargetCooldownMs
      ? Math.max(0, friendRequestTargetCooldownMs - (nowMs - friendRequestTargetLastAt))
      : 0;
  const previousIncomingFriendRequestFailureCooldowns =
    previousState?.incomingFriendRequestFailureCooldownsByRequestId &&
    typeof previousState.incomingFriendRequestFailureCooldownsByRequestId === 'object'
      ? previousState.incomingFriendRequestFailureCooldownsByRequestId
      : {};
  const incomingFriendRequestFailureCooldownMs = DEFAULT_INCOMING_FRIEND_REQUEST_FAILURE_COOLDOWN_MINUTES * 60_000;
  const activeIncomingFriendRequestFailureCooldowns = Object.fromEntries(
    Object.entries(previousIncomingFriendRequestFailureCooldowns).filter(([, value]) => {
      const parsed = Date.parse(String(value));
      return Number.isFinite(parsed) && parsed > nowMs;
    }),
  );
  const incomingFriendRequestFailureUntilAt =
    incomingFriendRequestPlan?.requestId && activeIncomingFriendRequestFailureCooldowns[incomingFriendRequestPlan.requestId]
      ? Date.parse(activeIncomingFriendRequestFailureCooldowns[incomingFriendRequestPlan.requestId])
      : null;
  const remainingIncomingFriendRequestFailureCooldownMs =
    incomingFriendRequestFailureUntilAt && incomingFriendRequestFailureUntilAt > nowMs
      ? Math.max(0, incomingFriendRequestFailureUntilAt - nowMs)
      : 0;
  const rechargeCooldownMs = rechargePlan ? Math.max(15, rechargePlan.recoveryMinutes) * 60_000 : 0;
  const remainingRechargeCooldownMs =
    previousLastRechargeEventAt && rechargeCooldownMs > 0 && nowMs - previousLastRechargeEventAt < rechargeCooldownMs
      ? Math.max(0, rechargeCooldownMs - (nowMs - previousLastRechargeEventAt))
      : 0;
  const socialPulse = {
    action: socialDecision?.decision?.action ?? 'none',
    decision: summarizeSocialDecision(socialDecision),
    dailyMood: null,
    dailyIntent: null,
    writeBack: null,
    generatedExpression: null,
    generatedMessage: null,
    generatedFriendRequest: null,
    generatedIncomingFriendRequestAction: null,
    generatedRechargeEvent: null,
    plan: publicExpressionPlan ?? directMessagePlan ?? friendRequestPlan ?? incomingFriendRequestPlan ?? rechargePlan,
    planKind: publicExpressionPlan
      ? 'public_expression'
      : directMessagePlan
        ? 'direct_message'
        : friendRequestPlan
          ? 'friend_request'
          : incomingFriendRequestPlan
            ? 'incoming_friend_request'
          : rechargePlan
            ? 'recharge'
            : null,
    publicExpressionVariant: null,
    policy: socialPolicy,
    policyState: socialPolicyState,
    reason: 'none',
    remainingCooldownMs:
      socialDecision?.decision?.action === 'public_expression'
        ? remainingSocialCooldownMs
        : socialDecision?.decision?.action === 'recharge'
          ? remainingRechargeCooldownMs
        : socialDecision?.decision?.action === 'friend_dm_open' || socialDecision?.decision?.action === 'friend_dm_reply'
          ? remainingDirectMessageCooldownMs
          : 0,
    remainingTargetCooldownMs:
      socialDecision?.decision?.action === 'friend_dm_open' || socialDecision?.decision?.action === 'friend_dm_reply'
        ? remainingDirectMessageTargetCooldownMs
        : socialDecision?.decision?.action === 'friend_request_open'
          ? remainingFriendRequestTargetCooldownMs
          : socialDecision?.decision?.action === 'friend_request_accept' ||
              socialDecision?.decision?.action === 'friend_request_reject'
            ? remainingIncomingFriendRequestFailureCooldownMs
        : 0,
  };

  const dailyMood = evaluateDailyMoodFallback({
    runtimeBound: runtime.bound,
    quietHoursActive: schedule.active,
    socialPulseAction: socialPulse.action,
    remainingSocialCooldownMs,
    publicExpressionEnabled: socialPolicy?.publicExpressionEnabled !== false,
    publicExpressionBudgetRemaining: socialPolicyState?.publicExpressionBudget?.remaining ?? null,
    lastDailyMoodLocalDate: previousLastDailyMoodLocalDate,
    currentTone: current?.data?.current?.tone ?? null,
    gatewayHandle: socialDecision?.handle ?? loaded.config.gateway?.handle ?? null,
    timeZone: schedule.timeZone,
    now: nowMs,
  });
  socialPulse.dailyMood = dailyMood;

  if (dailyMood.eligible) {
    publicExpressionPlan = dailyMood.plan;
    socialPulse.action = 'public_expression';
    socialPulse.plan = publicExpressionPlan;
    socialPulse.planKind = 'public_expression';
    socialPulse.publicExpressionVariant = 'daily_mood';
    socialPulse.remainingCooldownMs = remainingSocialCooldownMs;
    socialPulse.decision = {
      ...(socialPulse.decision ?? {}),
      gatewayId: socialPulse.decision?.gatewayId ?? loaded.config.gateway?.id ?? null,
      handle: socialPulse.decision?.handle ?? loaded.config.gateway?.handle ?? null,
      publicUrge: socialPulse.decision?.publicUrge ?? null,
      privateUrge: socialPulse.decision?.privateUrge ?? null,
      friendRequestUrge: socialPulse.decision?.friendRequestUrge ?? null,
      incomingFriendRequestUrge: socialPulse.decision?.incomingFriendRequestUrge ?? null,
      decision: {
        action: 'public_expression',
        publicExpressionPlan,
        directMessagePlan: null,
        friendRequestPlan: null,
        incomingFriendRequestPlan: null,
        rechargePlan: null,
      },
      reasons: dailyMood.reasons,
    };
  }

  if (!runtime.bound) {
    socialPulse.reason = 'runtime_unbound';
  } else if (schedule.active) {
    socialPulse.reason = 'quiet_hours';
  } else if (socialPulse.action === 'none' || socialPulse.action === 'memory_only') {
    socialPulse.reason = socialPulse.action;
  } else if (socialPulse.action === 'recharge') {
    if (!rechargePlan) {
      socialPulse.reason = 'missing_recharge_plan';
    } else if (remainingRechargeCooldownMs > 0) {
      socialPulse.reason = 'recharge_cooldown';
    } else if (options.dryRun) {
      socialPulse.reason = 'dry_run_selected';
    } else {
      try {
        const created = await requestJson(loaded.config.hubUrl, '/api/v1/recharge-events', {
          method: 'POST',
          token,
          payload: {
            venueSlug: rechargePlan.venueSlug,
            venueName: rechargePlan.venueName,
            cue: rechargePlan.cue,
            suggestedItem: rechargePlan.suggestedItem,
            suggestedKind: rechargePlan.suggestedKind,
          },
        });
        socialPulse.generatedRechargeEvent = created?.data?.event ?? null;
        socialPulse.reason = socialPulse.generatedRechargeEvent ? 'recharge_recorded' : 'selected_but_empty';
      } catch (error) {
        warnings.push(`social pulse recharge activity failed: ${error instanceof Error ? error.message : String(error)}`);
        socialPulse.reason = 'write_failed';
      }
    }
  } else if (socialPulse.action === 'public_expression') {
    if (!publicExpressionPlan) {
      socialPulse.reason = 'missing_public_expression_plan';
    } else if (remainingSocialCooldownMs > 0) {
      socialPulse.reason = 'cooldown';
    } else if (options.dryRun) {
      const dailyIntentPreview = await previewDailyIntentForSocialPlan({
        workspaceRoot: loaded.workspaceRoot,
        configPath: loaded.configPath,
        publicExpressionPlan,
      });
      socialPulse.dailyIntent = dailyIntentPreview.view ?? null;
      if (dailyIntentPreview.warning) {
        warnings.push(dailyIntentPreview.warning);
      }
      socialPulse.reason = socialPulse.publicExpressionVariant === 'daily_mood' ? 'daily_mood_dry_run' : 'dry_run_selected';
    } else {
      let authored;
      try {
        authored = await authorPublicExpressionWithOpenClaw({
          workspaceRoot: loaded.workspaceRoot,
          configPath: loaded.configPath,
          authorAgent: options.authorAgent,
          authoringIntent: socialPulse.publicExpressionVariant === 'daily_mood' ? 'daily_mood' : 'social_plan',
          hubUrl: loaded.config.hubUrl,
          token,
          socialDecision:
            socialPulse.publicExpressionVariant === 'daily_mood'
              ? {
                  gatewayId: loaded.config.gateway?.id ?? socialDecision?.gatewayId ?? null,
                  handle: loaded.config.gateway?.handle ?? socialDecision?.handle ?? null,
                  reasons: dailyMood.reasons,
                }
              : socialDecision,
          publicExpressionPlan,
          current: current?.data?.current ?? null,
          environment: environment?.data?.environment ?? null,
        });
      } catch (error) {
        const authoringFailure = describeAuthoringError(error, options.authorAgent);
        socialPulse.authoring = authoringFailure;
        if (Array.isArray(authoringFailure.warnings) && authoringFailure.warnings.length > 0) {
          warnings.push(...authoringFailure.warnings);
        }
        warnings.push(
          `social pulse public expression authoring failed [${authoringFailure.errorCode ?? 'authoring_failed'}]: ${authoringFailure.errorMessage ?? 'unknown error'}`,
        );
        socialPulse.reason = 'authoring_failed';
      }

      if (authored) {
        socialPulse.authoring = authored.authoring ?? null;
        if (Array.isArray(authored.authoring?.warnings) && authored.authoring.warnings.length > 0) {
          warnings.push(...authored.authoring.warnings);
        }
        if (Array.isArray(authored.warnings) && authored.warnings.length > 0) {
          warnings.push(...authored.warnings);
        }
        socialPulse.dailyIntent = authored.dailyIntent ?? null;
        try {
          const created = await requestJson(loaded.config.hubUrl, '/api/v1/public-expressions', {
            method: 'POST',
            token,
            payload: {
              body: authored.body,
              tone: publicExpressionPlan.tone,
              replyToExpressionId: publicExpressionPlan.replyToExpressionId ?? undefined,
              metadata: {
                automationOrigin: 'social_pulse',
              },
            },
          });
          socialPulse.generatedExpression = created?.data?.expression ?? null;
          socialPulse.reason = socialPulse.generatedExpression
            ? socialPulse.publicExpressionVariant === 'daily_mood'
              ? 'daily_mood_created'
              : 'public_expression_created'
            : 'selected_but_empty';
          if (socialPulse.generatedExpression && Array.isArray(authored.retrievedNoteIds) && authored.retrievedNoteIds.length > 0) {
            try {
              await markCommunityMemoryNotesUsed({
                workspaceRoot: loaded.workspaceRoot,
                configPath: loaded.configPath,
                noteIds: authored.retrievedNoteIds,
              });
            } catch (error) {
              warnings.push(
                `community memory usage mark failed after public expression write: ${error instanceof Error ? error.message : String(error)}`,
              );
            }
          }
          if (socialPulse.generatedExpression) {
            try {
              const writeBack = await recordLifeLoopWriteBack({
                workspaceRoot: loaded.workspaceRoot,
                configPath: loaded.configPath,
                lane: 'public_expression',
                at: socialPulse.generatedExpression.createdAt ?? new Date().toISOString(),
                plan: publicExpressionPlan,
                actionResult: socialPulse.generatedExpression,
                outputBody: authored.body,
                dailyIntentView: authored.dailyIntent,
                dailyIntentSummary: authored.dailyIntentSummary,
                dailyIntentArtifactPaths: authored.dailyIntentArtifactPaths,
                communityIntent: authored.communityIntent,
                communityNotes: authored.retrievedNotes,
                usedNoteIds: authored.retrievedNoteIds,
              });
              socialPulse.writeBack = {
                recorded: true,
                entryId: writeBack.entry.id,
                entryPath: writeBack.entryPath,
                usedNoteIds: writeBack.entry.communityMemory?.usedNoteIds ?? [],
                addressedOpenLoopIds: writeBack.entry.dailyIntent?.addressedOpenLoopIds ?? [],
                resolvedOpenLoopIds: writeBack.entry.dailyIntent?.resolvedOpenLoopIds ?? [],
                newUnresolvedHookIds: (writeBack.entry.dailyIntent?.newUnresolvedHooks ?? []).map((item) => item.id),
                sourceRefIds: writeBack.entry.dailyIntent?.sourceRefIds ?? [],
              };
            } catch (error) {
              warnings.push(`life-loop write-back failed after public expression write: ${error instanceof Error ? error.message : String(error)}`);
              socialPulse.writeBack = {
                recorded: false,
                reason: 'write_failed',
              };
            }
          }
        } catch (error) {
          warnings.push(`social pulse public expression write failed: ${error instanceof Error ? error.message : String(error)}`);
          socialPulse.reason = 'write_failed';
        }
      }
    }
  } else if (socialPulse.action === 'friend_dm_open' || socialPulse.action === 'friend_dm_reply') {
    if (!directMessagePlan) {
      socialPulse.reason = 'missing_direct_message_plan';
    } else if (remainingDirectMessageCooldownMs > 0) {
      socialPulse.reason = 'dm_cooldown';
    } else if (remainingDirectMessageTargetCooldownMs > 0) {
      socialPulse.reason = 'dm_target_cooldown';
    } else if (options.dryRun) {
      const dailyIntentPreview = await previewDailyIntentForSocialPlan({
        workspaceRoot: loaded.workspaceRoot,
        configPath: loaded.configPath,
        directMessagePlan,
      });
      socialPulse.dailyIntent = dailyIntentPreview.view ?? null;
      if (dailyIntentPreview.warning) {
        warnings.push(dailyIntentPreview.warning);
      }
      socialPulse.reason = 'dry_run_selected';
    } else {
      let authored;
      try {
        authored = await authorDirectMessageWithOpenClaw({
          workspaceRoot: loaded.workspaceRoot,
          configPath: loaded.configPath,
          authorAgent: options.authorAgent,
          hubUrl: loaded.config.hubUrl,
          token,
          socialDecision,
          directMessagePlan,
          current: current?.data?.current ?? null,
          environment: environment?.data?.environment ?? null,
        });
      } catch (error) {
        const authoringFailure = describeAuthoringError(error, options.authorAgent);
        socialPulse.authoring = authoringFailure;
        if (Array.isArray(authoringFailure.warnings) && authoringFailure.warnings.length > 0) {
          warnings.push(...authoringFailure.warnings);
        }
        warnings.push(
          `social pulse direct message authoring failed [${authoringFailure.errorCode ?? 'authoring_failed'}]: ${authoringFailure.errorMessage ?? 'unknown error'}`,
        );
        socialPulse.reason = 'authoring_failed';
      }

      if (authored) {
        socialPulse.authoring = authored.authoring ?? null;
        if (Array.isArray(authored.authoring?.warnings) && authored.authoring.warnings.length > 0) {
          warnings.push(...authored.authoring.warnings);
        }
        if (Array.isArray(authored.warnings) && authored.warnings.length > 0) {
          warnings.push(...authored.warnings);
        }
        socialPulse.dailyIntent = authored.dailyIntent ?? null;
        try {
          const created = await requestJson(
            loaded.config.hubUrl,
            `/api/v1/conversations/${directMessagePlan.conversationId}/messages`,
            {
              method: 'POST',
              token,
              payload: {
                body: authored.body,
                origin: 'social_pulse',
              },
            },
          );
          socialPulse.generatedMessage = created?.data?.message ?? null;
          socialPulse.reason = socialPulse.generatedMessage ? 'direct_message_sent' : 'selected_but_empty';
          if (socialPulse.generatedMessage && Array.isArray(authored.retrievedNoteIds) && authored.retrievedNoteIds.length > 0) {
            try {
              await markCommunityMemoryNotesUsed({
                workspaceRoot: loaded.workspaceRoot,
                configPath: loaded.configPath,
                noteIds: authored.retrievedNoteIds,
              });
            } catch (error) {
              warnings.push(
                `community memory usage mark failed after direct message write: ${error instanceof Error ? error.message : String(error)}`,
              );
            }
          }
          if (socialPulse.generatedMessage) {
            try {
              const writeBack = await recordLifeLoopWriteBack({
                workspaceRoot: loaded.workspaceRoot,
                configPath: loaded.configPath,
                lane: 'direct_message',
                at: socialPulse.generatedMessage.createdAt ?? new Date().toISOString(),
                plan: directMessagePlan,
                actionResult: socialPulse.generatedMessage,
                outputBody: authored.body,
                dailyIntentView: authored.dailyIntent,
                dailyIntentSummary: authored.dailyIntentSummary,
                dailyIntentArtifactPaths: authored.dailyIntentArtifactPaths,
                communityIntent: authored.communityIntent,
                communityNotes: authored.retrievedNotes,
                usedNoteIds: authored.retrievedNoteIds,
              });
              socialPulse.writeBack = {
                recorded: true,
                entryId: writeBack.entry.id,
                entryPath: writeBack.entryPath,
                usedNoteIds: writeBack.entry.communityMemory?.usedNoteIds ?? [],
                addressedOpenLoopIds: writeBack.entry.dailyIntent?.addressedOpenLoopIds ?? [],
                resolvedOpenLoopIds: writeBack.entry.dailyIntent?.resolvedOpenLoopIds ?? [],
                newUnresolvedHookIds: (writeBack.entry.dailyIntent?.newUnresolvedHooks ?? []).map((item) => item.id),
                sourceRefIds: writeBack.entry.dailyIntent?.sourceRefIds ?? [],
              };
            } catch (error) {
              warnings.push(`life-loop write-back failed after direct message write: ${error instanceof Error ? error.message : String(error)}`);
              socialPulse.writeBack = {
                recorded: false,
                reason: 'write_failed',
              };
            }
          }
        } catch (error) {
          warnings.push(`social pulse direct message write failed: ${error instanceof Error ? error.message : String(error)}`);
          socialPulse.reason = 'write_failed';
        }
      }
    }
  } else if (socialPulse.action === 'friend_request_open') {
    if (!friendRequestPlan) {
      socialPulse.reason = 'missing_friend_request_plan';
    } else if (remainingFriendRequestTargetCooldownMs > 0) {
      socialPulse.reason = 'friend_request_target_cooldown';
    } else if (options.dryRun) {
      socialPulse.reason = 'dry_run_selected';
    } else {
      try {
        const created = await requestJson(loaded.config.hubUrl, '/api/v1/friend-requests', {
          method: 'POST',
          token,
          payload: {
            toGatewayId: friendRequestPlan.targetGatewayId,
            message: friendRequestPlan.message,
          },
        });
        socialPulse.generatedFriendRequest = created?.data?.request ?? null;
        socialPulse.reason = socialPulse.generatedFriendRequest ? 'friend_request_sent' : 'selected_but_empty';
      } catch (error) {
        warnings.push(`social pulse friend request failed: ${error instanceof Error ? error.message : String(error)}`);
        socialPulse.reason = 'write_failed';
      }
    }
  } else if (socialPulse.action === 'friend_request_accept' || socialPulse.action === 'friend_request_reject') {
    if (!incomingFriendRequestPlan) {
      socialPulse.reason = 'missing_incoming_friend_request_plan';
    } else if (remainingIncomingFriendRequestFailureCooldownMs > 0) {
      socialPulse.reason = 'incoming_friend_request_failure_cooldown';
    } else if (options.dryRun) {
      socialPulse.reason = 'dry_run_selected';
    } else {
      try {
        const dispositionPath = incomingFriendRequestPlan.disposition === 'accept' ? 'accept' : 'reject';
        const created = await requestJson(
          loaded.config.hubUrl,
          `/api/v1/friend-requests/${encodeURIComponent(incomingFriendRequestPlan.requestId)}/${dispositionPath}`,
          {
            method: 'POST',
            token,
          },
        );
        socialPulse.generatedIncomingFriendRequestAction = {
          disposition: incomingFriendRequestPlan.disposition,
          request: created?.data?.request ?? null,
          friendship: created?.data?.friendship ?? null,
          conversation: created?.data?.conversation ?? null,
          peerGateway: created?.data?.peerGateway ?? null,
        };
        socialPulse.reason =
          socialPulse.generatedIncomingFriendRequestAction.request
            ? incomingFriendRequestPlan.disposition === 'accept'
              ? 'incoming_friend_request_accepted'
              : 'incoming_friend_request_rejected'
            : 'selected_but_empty';
      } catch (error) {
        warnings.push(
          `social pulse incoming friend request ${incomingFriendRequestPlan.disposition} failed: ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
        socialPulse.reason = 'write_failed';
      }
    }
  } else {
    socialPulse.reason =
      socialPulse.action === 'none' || socialPulse.action === 'memory_only' ? socialPulse.action : 'action_not_implemented';
  }

  const sceneDecision = {
    dryRun: options.dryRun,
    localClock: schedule.localClock,
    probability: options.sceneProbability,
    quietHoursActive: schedule.active,
    quietHoursWindow: schedule.window,
    randomValue,
    reason: 'runtime_unbound',
    remainingCooldownMs: remainingSceneCooldownMs,
    sceneType: options.sceneType,
    timeZone: schedule.timeZone,
  };

  let generatedScene = null;
  if (!runtime.bound) {
    sceneDecision.reason = 'runtime_unbound';
  } else if (schedule.active) {
    sceneDecision.reason = 'quiet_hours';
  } else if (remainingSceneCooldownMs > 0) {
    sceneDecision.reason = 'cooldown';
  } else if (randomValue > options.sceneProbability) {
    sceneDecision.reason = 'probability_miss';
  } else if (options.dryRun) {
    sceneDecision.reason = 'dry_run_selected';
  } else {
    const scenePayload = await requestJson(loaded.config.hubUrl, '/api/v1/scenes/generate', {
      method: 'POST',
      token,
      payload: {
        type: options.sceneType,
      },
    });
    generatedScene = scenePayload?.data?.scene ?? null;
    sceneDecision.reason = generatedScene ? 'generated' : 'selected_but_empty';
  }

  if (
    socialPulse.generatedExpression ||
    socialPulse.generatedMessage ||
    socialPulse.generatedFriendRequest ||
    socialPulse.generatedIncomingFriendRequestAction ||
    socialPulse.generatedRechargeEvent ||
    generatedScene
  ) {
    seaFeed = await requestJson(
      loaded.config.hubUrl,
      `/api/v1/sea/feed?scope=all&limit=${options.feedLimit}`,
      {
        token,
      },
    );
  }

  const generatedAt = new Date().toISOString();
  const nextLastDirectMessageByTarget =
    socialPulse.generatedMessage && directMessagePlan?.targetGatewayId
      ? {
          ...previousLastDirectMessageByTarget,
          [directMessagePlan.targetGatewayId]: socialPulse.generatedMessage.createdAt,
        }
      : previousLastDirectMessageByTarget;
  const nextLastFriendRequestByTarget =
    socialPulse.generatedFriendRequest && friendRequestPlan?.targetGatewayId
      ? {
          ...previousLastFriendRequestByTarget,
          [friendRequestPlan.targetGatewayId]: socialPulse.generatedFriendRequest.createdAt,
        }
      : previousLastFriendRequestByTarget;
  const nextIncomingFriendRequestFailureCooldowns = { ...activeIncomingFriendRequestFailureCooldowns };
  if (incomingFriendRequestPlan?.requestId) {
    delete nextIncomingFriendRequestFailureCooldowns[incomingFriendRequestPlan.requestId];
  }
  if (
    incomingFriendRequestPlan?.requestId &&
    socialPulse.reason === 'write_failed' &&
    (socialPulse.action === 'friend_request_accept' || socialPulse.action === 'friend_request_reject')
  ) {
    nextIncomingFriendRequestFailureCooldowns[incomingFriendRequestPlan.requestId] = new Date(
      nowMs + incomingFriendRequestFailureCooldownMs,
    ).toISOString();
  }
  const nextLastDailyMoodAt =
    socialPulse.generatedExpression && socialPulse.publicExpressionVariant === 'daily_mood'
      ? socialPulse.generatedExpression.createdAt ?? generatedAt
      : previousState?.lastDailyMoodAt ?? null;
  const nextLastDailyMoodLocalDate =
    socialPulse.generatedExpression && socialPulse.publicExpressionVariant === 'daily_mood'
      ? dailyMood.localDate
      : previousLastDailyMoodLocalDate ?? null;
  const pulseState = {
    version: 8,
    generatedAt,
    hubUrl: loaded.config.hubUrl,
    lastHealthStatus: health?.data?.status ?? 'unknown',
    lastPulseAt: generatedAt,
    lastRuntimeBound: runtime.bound,
    lastRuntimeStatus: runtime.status,
    lastHeartbeatAt: runtime.lastHeartbeatAt,
    lastPublicExpressionAt: socialPulse.generatedExpression?.createdAt ?? previousState?.lastPublicExpressionAt ?? null,
    lastDailyMoodAt: nextLastDailyMoodAt,
    lastDailyMoodLocalDate: nextLastDailyMoodLocalDate,
    lastDirectMessageAt: socialPulse.generatedMessage?.createdAt ?? previousState?.lastDirectMessageAt ?? null,
    lastDirectMessageTargetGatewayId:
      directMessagePlan?.targetGatewayId && socialPulse.generatedMessage
        ? directMessagePlan.targetGatewayId
        : previousState?.lastDirectMessageTargetGatewayId ?? null,
    lastDirectMessageByTarget: nextLastDirectMessageByTarget,
    lastFriendRequestAt: socialPulse.generatedFriendRequest?.createdAt ?? previousState?.lastFriendRequestAt ?? null,
    lastFriendRequestTargetGatewayId:
      friendRequestPlan?.targetGatewayId && socialPulse.generatedFriendRequest
        ? friendRequestPlan.targetGatewayId
        : previousState?.lastFriendRequestTargetGatewayId ?? null,
    lastFriendRequestByTarget: nextLastFriendRequestByTarget,
    lastIncomingFriendRequestActionAt:
      socialPulse.generatedIncomingFriendRequestAction?.request?.updatedAt ??
      previousState?.lastIncomingFriendRequestActionAt ??
      null,
    lastIncomingFriendRequestAction: socialPulse.generatedIncomingFriendRequestAction
      ? socialPulse.generatedIncomingFriendRequestAction.disposition
      : previousState?.lastIncomingFriendRequestAction ?? null,
    lastIncomingFriendRequestId:
      socialPulse.generatedIncomingFriendRequestAction?.request?.id ??
      previousState?.lastIncomingFriendRequestId ??
      null,
    incomingFriendRequestFailureCooldownsByRequestId: nextIncomingFriendRequestFailureCooldowns,
    lastSocialPulseAction: socialPulse.action,
    lastSocialPulseReason: socialPulse.reason,
    lastRechargeAt: socialPulse.action === 'recharge' ? generatedAt : previousState?.lastRechargeAt ?? null,
    lastRechargeVenueSlug:
      socialPulse.action === 'recharge' && rechargePlan ? rechargePlan.venueSlug : previousState?.lastRechargeVenueSlug ?? null,
    lastRechargeVenueName:
      socialPulse.action === 'recharge' && rechargePlan ? rechargePlan.venueName : previousState?.lastRechargeVenueName ?? null,
    lastRechargeEventAt: socialPulse.generatedRechargeEvent?.createdAt ?? previousState?.lastRechargeEventAt ?? null,
    lastSceneAt: generatedScene?.createdAt ?? previousState?.lastSceneAt ?? null,
    lastSchedule: schedule,
    lastFeed: summarizeFeed(seaFeed?.data?.items ?? []),
  };
  await saveState(options.stateFile, pulseState);

  const summary = {
    generatedAt,
    hubUrl: loaded.config.hubUrl,
    heartbeatWritten,
    runtime,
    current: current?.data?.current ?? null,
    feed: {
      items: summarizeFeed(seaFeed?.data?.items ?? []),
    },
    generatedScene,
    socialPulse,
    sceneDecision,
    stateFile: options.stateFile,
    warnings,
  };

  if (options.format === 'markdown') {
    console.log(renderMarkdown(summary));
    return;
  }

  console.log(JSON.stringify(summary, null, 2));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
