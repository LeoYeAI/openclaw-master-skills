#!/usr/bin/env node

import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { access, mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

import {
  loadActiveProfileSync,
  loadHostedConfig,
  resolveCommunityMemoryRootPath,
  resolveHostedConfigPath,
  resolveHeartbeatStatePath,
  resolveMirrorRootPath,
  resolveWorkspaceRoot,
} from './hosted-aqua-common.mjs';

export const TOOLS_MANAGED_BLOCK_START = '<!-- aquaclaw:managed:start -->';
export const TOOLS_MANAGED_BLOCK_END = '<!-- aquaclaw:managed:end -->';

const DEFAULT_TOOLS_RELATIVE_PATH = 'TOOLS.md';
const SCRIPT_DIRECTORY = path.dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = path.resolve(SCRIPT_DIRECTORY, '..');
const DEFAULT_GATEWAY_REPO_CANDIDATES = Object.freeze([
  path.join('.openclaw', 'workspace', 'gateway-hub'),
  path.join('.openclaw', 'workspace', 'AquaClaw'),
  path.join('workspace', 'gateway-hub'),
  path.join('workspace', 'AquaClaw'),
]);
const SAFE_SHELL_TOKEN = /^[A-Za-z0-9_@%+=:,./-]+$/;
const DEFAULT_TOOLS_FILE_CONTENT = `# TOOLS.md - Local Notes

This file is OpenClaw workspace-local private context. It is not part of the shared AquaClaw skill repo.

Keep machine-specific notes here. The AquaClaw managed block below is a derived mirror of \`.aquaclaw/\` state.
`;

export function resolveToolsPath({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  toolsPath = process.env.AQUACLAW_TOOLS_PATH,
} = {}) {
  const resolvedWorkspaceRoot = resolveWorkspaceRoot(workspaceRoot);
  const explicit = typeof toolsPath === 'string' && toolsPath.trim() ? toolsPath.trim() : null;
  return path.resolve(explicit ?? path.join(resolvedWorkspaceRoot, DEFAULT_TOOLS_RELATIVE_PATH));
}

export function shellQuote(value) {
  const text = String(value);
  if (SAFE_SHELL_TOKEN.test(text)) {
    return text;
  }
  return `'${text.replace(/'/g, `'\"'\"'`)}'`;
}

function buildCommand({ env = {}, program, args = [] }) {
  const parts = [];

  for (const [key, value] of Object.entries(env)) {
    if (typeof value !== 'string' || !value.trim()) {
      continue;
    }
    parts.push(`${key}=${shellQuote(value)}`);
  }

  const invocation =
    typeof program === 'string' && program.endsWith('.sh')
      ? ['bash', program, ...args]
      : typeof program === 'string' && program.endsWith('.mjs')
        ? ['node', program, ...args]
        : [program, ...args];

  parts.push(shellQuote(invocation[0]));
  for (const arg of invocation.slice(1)) {
    parts.push(shellQuote(arg));
  }

  return parts.join(' ');
}

async function pathExists(targetPath) {
  try {
    await access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function isGatewayHubRepo(repoPath) {
  try {
    const packageJsonPath = path.join(repoPath, 'package.json');
    const raw = await readFile(packageJsonPath, 'utf8');
    const parsed = JSON.parse(raw);
    return parsed?.name === 'gateway-hub';
  } catch {
    return false;
  }
}

export async function resolveGatewayHubRepo({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  repoPath = process.env.AQUACLAW_REPO,
} = {}) {
  const resolvedWorkspaceRoot = resolveWorkspaceRoot(workspaceRoot);
  const candidates = [];

  if (typeof repoPath === 'string' && repoPath.trim()) {
    candidates.push(path.resolve(repoPath.trim()));
  }

  candidates.push(process.cwd());

  for (const relativeCandidate of DEFAULT_GATEWAY_REPO_CANDIDATES) {
    candidates.push(path.join(os.homedir(), relativeCandidate));
  }

  candidates.push(path.join(resolvedWorkspaceRoot, 'gateway-hub'));
  candidates.push(path.join(resolvedWorkspaceRoot, 'AquaClaw'));

  const seen = new Set();
  for (const candidate of candidates) {
    if (!candidate) {
      continue;
    }
    const resolved = path.resolve(candidate);
    if (seen.has(resolved)) {
      continue;
    }
    seen.add(resolved);
    if (await isGatewayHubRepo(resolved)) {
      return resolved;
    }
  }

  return null;
}

function collectMarkerPositions(content, marker) {
  const positions = [];
  let index = content.indexOf(marker);
  while (index !== -1) {
    positions.push(index);
    index = content.indexOf(marker, index + marker.length);
  }
  return positions;
}

export function inspectManagedBlock(content) {
  const starts = collectMarkerPositions(content, TOOLS_MANAGED_BLOCK_START);
  const ends = collectMarkerPositions(content, TOOLS_MANAGED_BLOCK_END);

  if (starts.length === 0 && ends.length === 0) {
    return {
      present: false,
      start: null,
      end: null,
    };
  }

  if (starts.length !== 1 || ends.length !== 1) {
    throw new Error('TOOLS.md must contain at most one AquaClaw managed block.');
  }

  const start = starts[0];
  const end = ends[0];
  if (end < start) {
    throw new Error('AquaClaw managed block end marker appears before the start marker.');
  }

  return {
    present: true,
    start,
    end: end + TOOLS_MANAGED_BLOCK_END.length,
  };
}

async function loadHostedSummary({ workspaceRoot, configPath }) {
  const resolvedConfigPath = resolveHostedConfigPath({
    workspaceRoot,
    configPath,
  });
  const present = await pathExists(resolvedConfigPath);

  if (!present) {
    return {
      present: false,
      valid: false,
      configPath: resolvedConfigPath,
      host: null,
      gatewayLabel: null,
      runtimeId: null,
      warning: null,
    };
  }

  try {
    const loaded = await loadHostedConfig({
      workspaceRoot,
      configPath: resolvedConfigPath,
    });
    const host = new URL(loaded.config.hubUrl).host;
    const gatewayDisplayName = loaded.config?.gateway?.displayName ?? null;
    const gatewayHandle = loaded.config?.gateway?.handle ?? null;
    const gatewayLabel = gatewayDisplayName && gatewayHandle
      ? `${gatewayDisplayName} (@${gatewayHandle})`
      : gatewayDisplayName ?? (gatewayHandle ? `@${gatewayHandle}` : null);

    return {
      present: true,
      valid: true,
      configPath: resolvedConfigPath,
      host,
      hubUrl: loaded.config.hubUrl,
      profileId: loaded.profileId ?? loaded.config?.profile?.id ?? null,
      gatewayLabel,
      runtimeId: loaded.config?.runtime?.runtimeId ?? null,
      warning: null,
    };
  } catch (error) {
    return {
      present: true,
      valid: false,
      configPath: resolvedConfigPath,
      host: null,
      gatewayLabel: null,
      profileId: null,
      runtimeId: null,
      warning: error instanceof Error ? error.message : String(error),
    };
  }
}

function buildActiveTargetSummary({ hosted, repoPath }) {
  return buildActiveTargetSummaryWithProfile({
    activeProfile: null,
    hosted,
    repoPath,
  });
}

function buildActiveTargetSummaryWithProfile({ activeProfile, hosted, repoPath }) {
  if (activeProfile?.type === 'local' && activeProfile.profileId) {
    return `local profile ${activeProfile.profileId}`;
  }
  if (activeProfile?.type === 'hosted' && hosted.valid) {
    return `hosted ${hosted.host}`;
  }
  if (activeProfile?.type === 'hosted' && hosted.present && !hosted.valid) {
    return `hosted profile ${activeProfile.profileId} (invalid config)`;
  }
  if (hosted.valid) {
    return `hosted ${hosted.host}`;
  }
  if (hosted.present && !hosted.valid) {
    return 'hosted (invalid config)';
  }
  if (repoPath) {
    return 'local repo';
  }
  return 'not configured';
}

export async function buildToolsManagedState({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  toolsPath = process.env.AQUACLAW_TOOLS_PATH,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
  repoPath = process.env.AQUACLAW_REPO,
  generatedAt = new Date().toISOString(),
} = {}) {
  const resolvedWorkspaceRoot = resolveWorkspaceRoot(workspaceRoot);
  const resolvedToolsPath = resolveToolsPath({
    workspaceRoot: resolvedWorkspaceRoot,
    toolsPath,
  });
  const resolvedRepoPath = await resolveGatewayHubRepo({
    workspaceRoot: resolvedWorkspaceRoot,
    repoPath,
  });
  const hosted = await loadHostedSummary({
    workspaceRoot: resolvedWorkspaceRoot,
    configPath,
  });
  const activeProfile = loadActiveProfileSync({
    workspaceRoot: resolvedWorkspaceRoot,
  }).pointer;
  const local = {
    active: activeProfile?.type === 'local',
    profileId: activeProfile?.type === 'local' ? activeProfile.profileId : null,
    mirrorRoot:
      activeProfile?.type === 'local'
        ? resolveMirrorRootPath({
            workspaceRoot: resolvedWorkspaceRoot,
            mode: 'local',
          })
        : null,
    heartbeatStatePath:
      activeProfile?.type === 'local'
        ? resolveHeartbeatStatePath({
            workspaceRoot: resolvedWorkspaceRoot,
            mode: 'local',
          })
        : null,
    communityMemoryRoot:
      activeProfile?.type === 'local'
        ? resolveCommunityMemoryRootPath({
            workspaceRoot: resolvedWorkspaceRoot,
          })
        : null,
  };
  const stateRoot = path.join(resolvedWorkspaceRoot, '.aquaclaw');
  const refreshCommand = buildCommand({
    env: {
      OPENCLAW_WORKSPACE_ROOT: resolvedWorkspaceRoot,
      ...(resolvedRepoPath ? { AQUACLAW_REPO: resolvedRepoPath } : {}),
    },
    program: path.join(SKILL_ROOT, 'scripts', 'sync-aquaclaw-tools-md.sh'),
    args: ['--apply'],
  });

  return {
    generatedAt,
    workspaceRoot: resolvedWorkspaceRoot,
    toolsPath: resolvedToolsPath,
    stateRoot,
    skillRoot: SKILL_ROOT,
    repoPath: resolvedRepoPath,
    hosted,
    activeProfile,
    local,
    activeTarget: buildActiveTargetSummaryWithProfile({
      activeProfile,
      hosted,
      repoPath: resolvedRepoPath,
    }),
    commands: {
      refreshManagedBlock: refreshCommand,
      hostedJoin: buildCommand({
        env: {
          OPENCLAW_WORKSPACE_ROOT: resolvedWorkspaceRoot,
        },
        program: path.join(SKILL_ROOT, 'scripts', 'aqua-hosted-join.sh'),
        args: ['--hub-url', 'https://aqua.example.com', '--invite-code', '<code>'],
      }),
      hostedContext: buildCommand({
        env: {
          OPENCLAW_WORKSPACE_ROOT: resolvedWorkspaceRoot,
        },
        program: path.join(SKILL_ROOT, 'scripts', 'aqua-hosted-context.sh'),
        args: ['--format', 'markdown', '--include-encounters', '--include-scenes'],
      }),
      combinedBrief: buildCommand({
        env: {
          OPENCLAW_WORKSPACE_ROOT: resolvedWorkspaceRoot,
          ...(resolvedRepoPath ? { AQUACLAW_REPO: resolvedRepoPath } : {}),
        },
        program: path.join(SKILL_ROOT, 'scripts', 'build-openclaw-aqua-brief.sh'),
        args: ['--mode', 'auto', '--aqua-source', 'auto'],
      }),
      mirrorRead: buildCommand({
        env: {
          OPENCLAW_WORKSPACE_ROOT: resolvedWorkspaceRoot,
        },
        program: path.join(SKILL_ROOT, 'scripts', 'aqua-mirror-read.sh'),
        args: ['--expect-mode', 'auto'],
      }),
      mirrorStatus: buildCommand({
        env: {
          OPENCLAW_WORKSPACE_ROOT: resolvedWorkspaceRoot,
        },
        program: path.join(SKILL_ROOT, 'scripts', 'aqua-mirror-status.sh'),
        args: ['--expect-mode', 'auto'],
      }),
      heartbeatOnce: buildCommand({
        env: {
          OPENCLAW_WORKSPACE_ROOT: resolvedWorkspaceRoot,
        },
        program: path.join(SKILL_ROOT, 'scripts', 'aqua-runtime-heartbeat.sh'),
        args: ['--once'],
      }),
      heartbeatCronInstall: buildCommand({
        program: path.join(SKILL_ROOT, 'scripts', 'install-openclaw-heartbeat-cron.sh'),
        args: ['--apply', '--enable'],
      }),
      heartbeatCronShow: buildCommand({
        program: path.join(SKILL_ROOT, 'scripts', 'show-openclaw-heartbeat-cron.sh'),
        args: [],
      }),
      hostedPulseServiceInstall: buildCommand({
        program: path.join(SKILL_ROOT, 'scripts', 'install-aquaclaw-hosted-pulse-service.sh'),
        args: ['--apply'],
      }),
      hostedPulseServiceShow: buildCommand({
        program: path.join(SKILL_ROOT, 'scripts', 'show-aquaclaw-hosted-pulse-service.sh'),
        args: [],
      }),
      hostedIntro: buildCommand({
        env: {
          OPENCLAW_WORKSPACE_ROOT: resolvedWorkspaceRoot,
        },
        program: path.join(SKILL_ROOT, 'scripts', 'aqua-hosted-intro.sh'),
        args: ['--format', 'markdown'],
      }),
      localBringUp: resolvedRepoPath
        ? buildCommand({
            env: {
              AQUACLAW_REPO: resolvedRepoPath,
            },
            program: path.join(SKILL_ROOT, 'scripts', 'aqua-launch.sh'),
            args: ['--no-open'],
          })
        : null,
      localContext: resolvedRepoPath
        ? buildCommand({
            env: {
              AQUACLAW_REPO: resolvedRepoPath,
            },
            program: path.join(SKILL_ROOT, 'scripts', 'aqua-context.sh'),
            args: ['--format', 'markdown', '--include-encounters', '--include-scenes'],
          })
        : null,
      profileList: buildCommand({
        env: {
          OPENCLAW_WORKSPACE_ROOT: resolvedWorkspaceRoot,
        },
        program: path.join(SKILL_ROOT, 'scripts', 'aqua-profile.sh'),
        args: ['list'],
      }),
      profileShow: buildCommand({
        env: {
          OPENCLAW_WORKSPACE_ROOT: resolvedWorkspaceRoot,
        },
        program: path.join(SKILL_ROOT, 'scripts', 'aqua-profile.sh'),
        args: ['show'],
      }),
    },
  };
}

export function renderToolsManagedBlock(state) {
  const lines = [
    TOOLS_MANAGED_BLOCK_START,
    '## AquaClaw Managed Summary',
    '',
    '- This block is derived from `.aquaclaw/` state and helper path discovery.',
    '- Do not treat it as authoritative config. Edit outside this block freely.',
    `- Generated at: \`${state.generatedAt}\``,
    `- Source of truth: \`${state.stateRoot}\``,
    `- Workspace root: \`${state.workspaceRoot}\``,
    `- Skill path: \`${state.skillRoot}\``,
    `- Repo path: ${state.repoPath ? `\`${state.repoPath}\`` : '_not found_'}`,
    `- Active target: \`${state.activeTarget}\``,
    `- Active profile type: \`${state.activeProfile?.type ?? 'none'}\``,
    `- Active profile id: \`${state.activeProfile?.profileId ?? 'none'}\``,
    `- Hosted config: \`${state.hosted.configPath}\``,
  ];

  if (state.hosted.valid) {
    if (state.hosted.profileId) {
      lines.push(`- Active hosted profile: \`${state.hosted.profileId}\``);
    }
    lines.push(`- Hosted base URL: \`${state.hosted.hubUrl}\``);
    if (state.hosted.gatewayLabel) {
      lines.push(`- Hosted gateway: \`${state.hosted.gatewayLabel}\``);
    }
    if (state.hosted.runtimeId) {
      lines.push(`- Hosted runtime: \`${state.hosted.runtimeId}\``);
    }
  } else if (state.hosted.present) {
    lines.push(`- Warning: hosted config exists but could not be loaded: \`${state.hosted.warning}\``);
  } else {
    lines.push('- Hosted status: _no hosted config present_');
  }

  if (state.local.active) {
    lines.push(`- Local mirror root: \`${state.local.mirrorRoot}\``);
    lines.push(`- Local heartbeat state: \`${state.local.heartbeatStatePath}\``);
    lines.push(`- Local community memory: \`${state.local.communityMemoryRoot}\``);
  }

  lines.push(`- Preferred managed-block refresh: \`${state.commands.refreshManagedBlock}\``);
  lines.push(`- Preferred hosted join: \`${state.commands.hostedJoin}\``);
  lines.push(`- Preferred hosted context check: \`${state.commands.hostedContext}\``);
  lines.push(`- Preferred profile list: \`${state.commands.profileList}\``);
  lines.push(`- Preferred profile show: \`${state.commands.profileShow}\``);
  lines.push(`- Preferred combined brief: \`${state.commands.combinedBrief}\``);
  lines.push(`- Preferred mirror-only read: \`${state.commands.mirrorRead}\``);
  lines.push(`- Preferred mirror status read: \`${state.commands.mirrorStatus}\``);
  lines.push(`- Preferred heartbeat one-shot: \`${state.commands.heartbeatOnce}\``);
  lines.push(`- Preferred heartbeat cron installer: \`${state.commands.heartbeatCronInstall}\``);
  lines.push(`- Preferred heartbeat cron status: \`${state.commands.heartbeatCronShow}\``);
  lines.push(`- Preferred hosted pulse installer: \`${state.commands.hostedPulseServiceInstall}\``);
  lines.push(`- Preferred hosted pulse status: \`${state.commands.hostedPulseServiceShow}\``);
  lines.push(`- Preferred hosted intro: \`${state.commands.hostedIntro}\``);

  if (state.commands.localBringUp) {
    lines.push(`- Preferred local bring-up: \`${state.commands.localBringUp}\``);
  }
  if (state.commands.localContext) {
    lines.push(`- Preferred local live context: \`${state.commands.localContext}\``);
  }

  lines.push(TOOLS_MANAGED_BLOCK_END);
  return `${lines.join('\n')}\n`;
}

async function atomicWriteFile(targetPath, content) {
  await mkdir(path.dirname(targetPath), { recursive: true, mode: 0o700 });
  const tempPath = `${targetPath}.tmp-${process.pid}-${Date.now()}`;
  await writeFile(tempPath, content, { mode: 0o600 });
  await rename(tempPath, targetPath);
}

function insertBlockIntoContent(content, block) {
  if (!content.trim()) {
    return `${content}${block}`;
  }

  const normalized = content.endsWith('\n') ? content : `${content}\n`;
  return `${normalized}\n${block}`;
}

function replaceManagedBlock(content, inspected, block) {
  return `${content.slice(0, inspected.start)}${block}${content.slice(inspected.end)}`;
}

function defaultToolsFileWithBlock(block) {
  return `${DEFAULT_TOOLS_FILE_CONTENT.trimEnd()}\n\n${block}`;
}

export async function syncManagedToolsBlock({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  toolsPath = process.env.AQUACLAW_TOOLS_PATH,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
  repoPath = process.env.AQUACLAW_REPO,
  apply = false,
  insert = false,
  skipIfMissing = false,
  generatedAt,
} = {}) {
  const state = await buildToolsManagedState({
    workspaceRoot,
    toolsPath,
    configPath,
    repoPath,
    generatedAt,
  });
  const block = renderToolsManagedBlock(state);
  const toolsExists = await pathExists(state.toolsPath);
  const currentContent = toolsExists ? await readFile(state.toolsPath, 'utf8') : '';
  const inspected = inspectManagedBlock(currentContent);

  const result = {
    action: 'preview',
    apply,
    insert,
    toolsPath: state.toolsPath,
    toolsExists,
    blockPresent: inspected.present,
    state,
    block,
  };

  if (!apply) {
    return result;
  }

  let nextContent;
  if (!toolsExists) {
    if (!insert) {
      throw new Error(`TOOLS.md not found at ${state.toolsPath}. Rerun with --insert to create it with a managed block.`);
    }
    nextContent = defaultToolsFileWithBlock(block);
    result.action = 'created';
  } else if (inspected.present) {
    nextContent = replaceManagedBlock(currentContent, inspected, block);
    result.action = 'updated';
  } else if (skipIfMissing) {
    result.action = 'missing-skipped';
    return result;
  } else if (insert) {
    nextContent = insertBlockIntoContent(currentContent, block);
    result.action = 'inserted';
  } else {
    throw new Error(
      `No AquaClaw managed block found in ${state.toolsPath}. Rerun with --insert to append one, or use --skip-if-missing to leave the file untouched.`,
    );
  }

  await atomicWriteFile(state.toolsPath, nextContent);
  const verified = await readFile(state.toolsPath, 'utf8');
  const verifiedBlock = inspectManagedBlock(verified);
  if (!verifiedBlock.present) {
    throw new Error(`managed block verification failed after writing ${state.toolsPath}`);
  }
  if (!verified.includes(block.trimEnd())) {
    throw new Error(`managed block content verification failed after writing ${state.toolsPath}`);
  }

  return result;
}
