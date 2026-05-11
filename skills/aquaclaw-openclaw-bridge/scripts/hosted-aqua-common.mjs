#!/usr/bin/env node

import { randomBytes } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { chmod, mkdir, readFile, rename, unlink, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { deriveGatewayBioFromSoul, deriveGatewayDisplayNameFromSoul } from './soul-personality.mjs';
export { requestJson } from './hosted-aqua-http.mjs';

export const DEFAULT_WORKSPACE_ROOT = path.join(os.homedir(), '.openclaw', 'workspace');
export const DEFAULT_AQUACLAW_STATE_RELATIVE_DIR = '.aquaclaw';
export const DEFAULT_HOSTED_CONFIG_FILE_NAME = 'hosted-bridge.json';
export const DEFAULT_HOSTED_PULSE_STATE_FILE_NAME = 'hosted-pulse-state.json';
export const DEFAULT_HOSTED_INTRO_STATE_FILE_NAME = 'hosted-intro-state.json';
export const DEFAULT_HEARTBEAT_STATE_FILE_NAME = 'runtime-heartbeat-state.json';
export const DEFAULT_MIRROR_DIR_NAME = 'mirror';
export const DEFAULT_COMMUNITY_MEMORY_DIR_NAME = 'community-memory';
export const DEFAULT_ACTIVE_PROFILE_FILE_NAME = 'active-profile.json';
export const DEFAULT_PROFILE_METADATA_FILE_NAME = 'profile.json';
export const DEFAULT_LOCAL_PROFILE_ID = 'local-default';
export const ACTIVE_PROFILE_POINTER_VERSION = 1;
export const ACTIVE_HOSTED_PROFILE_POINTER_VERSION = ACTIVE_PROFILE_POINTER_VERSION;
const DEFAULT_HOSTED_CONFIG_RELATIVE_PATH = path.join(
  DEFAULT_AQUACLAW_STATE_RELATIVE_DIR,
  DEFAULT_HOSTED_CONFIG_FILE_NAME,
);
const DEFAULT_HOSTED_PULSE_STATE_RELATIVE_PATH = path.join(
  DEFAULT_AQUACLAW_STATE_RELATIVE_DIR,
  DEFAULT_HOSTED_PULSE_STATE_FILE_NAME,
);
const DEFAULT_HOSTED_INTRO_STATE_RELATIVE_PATH = path.join(
  DEFAULT_AQUACLAW_STATE_RELATIVE_DIR,
  DEFAULT_HOSTED_INTRO_STATE_FILE_NAME,
);
const DEFAULT_HEARTBEAT_STATE_RELATIVE_PATH = path.join(
  DEFAULT_AQUACLAW_STATE_RELATIVE_DIR,
  DEFAULT_HEARTBEAT_STATE_FILE_NAME,
);
const DEFAULT_MIRROR_RELATIVE_DIR = path.join(DEFAULT_AQUACLAW_STATE_RELATIVE_DIR, DEFAULT_MIRROR_DIR_NAME);
const DEFAULT_COMMUNITY_MEMORY_RELATIVE_DIR = path.join(
  DEFAULT_AQUACLAW_STATE_RELATIVE_DIR,
  DEFAULT_COMMUNITY_MEMORY_DIR_NAME,
);
const DEFAULT_ACTIVE_PROFILE_RELATIVE_PATH = path.join(
  DEFAULT_AQUACLAW_STATE_RELATIVE_DIR,
  DEFAULT_ACTIVE_PROFILE_FILE_NAME,
);
const DEFAULT_PROFILES_RELATIVE_DIR = path.join(DEFAULT_AQUACLAW_STATE_RELATIVE_DIR, 'profiles');

export function parseArgValue(argv, index, current, label) {
  if (current.includes('=')) {
    return current.slice(current.indexOf('=') + 1);
  }

  const next = argv[index + 1];
  if (!next || next.startsWith('--')) {
    throw new Error(`${label} requires a value`);
  }

  return next;
}

export function normalizeBaseUrl(raw) {
  const url = new URL(String(raw).trim());
  url.pathname = '';
  url.search = '';
  url.hash = '';
  return url.toString().replace(/\/$/, '');
}

export function resolveWorkspaceRoot(raw = process.env.OPENCLAW_WORKSPACE_ROOT) {
  const value = typeof raw === 'string' && raw.trim() ? raw.trim() : DEFAULT_WORKSPACE_ROOT;
  return path.resolve(value);
}

export function resolveAquaclawStateRoot(workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT) {
  return path.join(resolveWorkspaceRoot(workspaceRoot), DEFAULT_AQUACLAW_STATE_RELATIVE_DIR);
}

export function resolveActiveHostedProfilePath({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
} = {}) {
  return path.join(resolveWorkspaceRoot(workspaceRoot), DEFAULT_ACTIVE_PROFILE_RELATIVE_PATH);
}

export function resolveHostedProfilesRoot({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
} = {}) {
  return path.join(resolveWorkspaceRoot(workspaceRoot), DEFAULT_PROFILES_RELATIVE_DIR);
}

export function slugifySegment(value, fallback) {
  const normalized = String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');

  return normalized || fallback;
}

export function buildHostedProfileId(baseUrl) {
  const host = new URL(normalizeBaseUrl(baseUrl)).host;
  return `hosted-${slugifySegment(host, 'hosted-default')}`;
}

export function resolveHostedProfilePaths({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  profileId,
} = {}) {
  if (typeof profileId !== 'string' || !profileId.trim()) {
    throw new Error('profileId is required');
  }

  const resolvedWorkspaceRoot = resolveWorkspaceRoot(workspaceRoot);
  const resolvedProfileId = profileId.trim();
  const profileRoot = path.join(
    resolveHostedProfilesRoot({ workspaceRoot: resolvedWorkspaceRoot }),
    resolvedProfileId,
  );

  return {
    workspaceRoot: resolvedWorkspaceRoot,
    profileId: resolvedProfileId,
    profileRoot,
    profilePath: path.join(profileRoot, DEFAULT_PROFILE_METADATA_FILE_NAME),
    configPath: path.join(profileRoot, DEFAULT_HOSTED_CONFIG_FILE_NAME),
    pulseStatePath: path.join(profileRoot, DEFAULT_HOSTED_PULSE_STATE_FILE_NAME),
    introStatePath: path.join(profileRoot, DEFAULT_HOSTED_INTRO_STATE_FILE_NAME),
    heartbeatStatePath: path.join(profileRoot, DEFAULT_HEARTBEAT_STATE_FILE_NAME),
    mirrorRoot: path.join(profileRoot, DEFAULT_MIRROR_DIR_NAME),
    communityMemoryRoot: path.join(profileRoot, DEFAULT_COMMUNITY_MEMORY_DIR_NAME),
    activeProfilePath: resolveActiveHostedProfilePath({ workspaceRoot: resolvedWorkspaceRoot }),
  };
}

function readJsonFileSyncIfPresent(filePath) {
  try {
    const raw = readFileSync(filePath, 'utf8');
    return JSON.parse(raw);
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return null;
    }
    if (error instanceof SyntaxError) {
      throw new Error(`invalid JSON at ${filePath}`);
    }
    throw error;
  }
}

function normalizeActiveProfilePointer(pointer, pointerPath) {
  if (!pointer || typeof pointer !== 'object') {
    throw new Error(`invalid active hosted profile pointer at ${pointerPath}`);
  }
  if (pointer.version !== ACTIVE_PROFILE_POINTER_VERSION) {
    throw new Error(`unsupported active hosted profile pointer version at ${pointerPath}`);
  }
  if (pointer.type !== 'hosted' && pointer.type !== 'local') {
    throw new Error(`invalid active profile pointer type at ${pointerPath}`);
  }
  if (typeof pointer.profileId !== 'string' || !pointer.profileId.trim()) {
    throw new Error(`missing profileId in active hosted profile pointer at ${pointerPath}`);
  }

  return {
    version: ACTIVE_PROFILE_POINTER_VERSION,
    type: pointer.type,
    profileId: pointer.profileId.trim(),
    hubUrl: typeof pointer.hubUrl === 'string' && pointer.hubUrl.trim() ? pointer.hubUrl.trim() : null,
    configPath:
      typeof pointer.configPath === 'string' && pointer.configPath.trim() ? path.resolve(pointer.configPath) : null,
    updatedAt: typeof pointer.updatedAt === 'string' && pointer.updatedAt.trim() ? pointer.updatedAt.trim() : null,
  };
}

export function loadActiveProfileSync({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
} = {}) {
  const pointerPath = resolveActiveHostedProfilePath({ workspaceRoot });
  const pointer = readJsonFileSyncIfPresent(pointerPath);
  if (pointer === null) {
    return {
      pointer: null,
      pointerPath,
    };
  }

  return {
    pointer: normalizeActiveProfilePointer(pointer, pointerPath),
    pointerPath,
  };
}

export function loadActiveHostedProfileSync({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
} = {}) {
  const active = loadActiveProfileSync({ workspaceRoot });
  return {
    pointer: active.pointer?.type === 'hosted' ? active.pointer : null,
    pointerPath: active.pointerPath,
  };
}

export function parseHostedProfileIdFromConfigPath({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath,
} = {}) {
  if (typeof configPath !== 'string' || !configPath.trim()) {
    return null;
  }

  const resolvedConfigPath = path.resolve(configPath);
  const profilesRoot = resolveHostedProfilesRoot({ workspaceRoot });
  const relative = path.relative(profilesRoot, resolvedConfigPath);
  if (!relative || relative.startsWith('..') || path.isAbsolute(relative)) {
    return null;
  }

  const parts = relative.split(path.sep).filter(Boolean);
  if (parts.length === 2 && parts[1] === DEFAULT_HOSTED_CONFIG_FILE_NAME) {
    return parts[0];
  }

  return null;
}

export function resolveHostedConfigSelection({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
} = {}) {
  const resolvedWorkspaceRoot = resolveWorkspaceRoot(workspaceRoot);
  const explicit = typeof configPath === 'string' && configPath.trim() ? path.resolve(configPath.trim()) : null;

  if (explicit) {
    const profileId = parseHostedProfileIdFromConfigPath({
      workspaceRoot: resolvedWorkspaceRoot,
      configPath: explicit,
    });
    const profilePaths = profileId
      ? resolveHostedProfilePaths({ workspaceRoot: resolvedWorkspaceRoot, profileId })
      : null;
    return {
      workspaceRoot: resolvedWorkspaceRoot,
      configPath: explicit,
      profileId,
      profileRoot: profilePaths?.profileRoot ?? null,
      selectionKind: 'explicit',
      activePointer: null,
      activeProfilePath: resolveActiveHostedProfilePath({ workspaceRoot: resolvedWorkspaceRoot }),
    };
  }

  const active = loadActiveHostedProfileSync({ workspaceRoot: resolvedWorkspaceRoot });
  if (active.pointer?.profileId) {
    const profilePaths = resolveHostedProfilePaths({
      workspaceRoot: resolvedWorkspaceRoot,
      profileId: active.pointer.profileId,
    });
    return {
      workspaceRoot: resolvedWorkspaceRoot,
      configPath: profilePaths.configPath,
      profileId: profilePaths.profileId,
      profileRoot: profilePaths.profileRoot,
      selectionKind: 'active-profile',
      activePointer: active.pointer,
      activeProfilePath: active.pointerPath,
    };
  }

  return {
    workspaceRoot: resolvedWorkspaceRoot,
    configPath: path.join(resolvedWorkspaceRoot, DEFAULT_HOSTED_CONFIG_RELATIVE_PATH),
    profileId: null,
    profileRoot: null,
    selectionKind: 'legacy',
    activePointer: active.pointer,
    activeProfilePath: active.pointerPath,
  };
}

export function resolveHostedConfigPath({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
} = {}) {
  return resolveHostedConfigSelection({
    workspaceRoot,
    configPath,
  }).configPath;
}

export function resolveHostedPulseStatePath({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  stateFile = process.env.AQUACLAW_HOSTED_PULSE_STATE,
} = {}) {
  const explicit = typeof stateFile === 'string' && stateFile.trim() ? stateFile.trim() : null;
  if (explicit) {
    return path.resolve(explicit);
  }

  const selection = resolveHostedConfigSelection({
    workspaceRoot,
  });

  if (selection.profileId) {
    return resolveHostedProfilePaths({
      workspaceRoot: selection.workspaceRoot,
      profileId: selection.profileId,
    }).pulseStatePath;
  }

  return path.join(selection.workspaceRoot, DEFAULT_HOSTED_PULSE_STATE_RELATIVE_PATH);
}

export function resolveHostedIntroStatePath({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  stateFile = process.env.AQUACLAW_HOSTED_INTRO_STATE,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
} = {}) {
  const explicit = typeof stateFile === 'string' && stateFile.trim() ? stateFile.trim() : null;
  if (explicit) {
    return path.resolve(explicit);
  }

  const selection = resolveHostedConfigSelection({
    workspaceRoot,
    configPath,
  });

  if (selection.profileId) {
    return resolveHostedProfilePaths({
      workspaceRoot: selection.workspaceRoot,
      profileId: selection.profileId,
    }).introStatePath;
  }

  return path.join(selection.workspaceRoot, DEFAULT_HOSTED_INTRO_STATE_RELATIVE_PATH);
}

function resolveLocalProfileStatePaths({ workspaceRoot, profileId }) {
  return resolveHostedProfilePaths({
    workspaceRoot,
    profileId,
  });
}

export function resolveHeartbeatStatePath({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  stateFile = process.env.AQUACLAW_HEARTBEAT_STATE_FILE,
  mode = 'auto',
} = {}) {
  const explicit = typeof stateFile === 'string' && stateFile.trim() ? stateFile.trim() : null;
  if (explicit) {
    return path.resolve(explicit);
  }

  const resolvedWorkspaceRoot = resolveWorkspaceRoot(workspaceRoot);
  const active = loadActiveProfileSync({ workspaceRoot: resolvedWorkspaceRoot }).pointer;
  if (mode === 'local') {
    if (active?.type === 'local') {
      return resolveLocalProfileStatePaths({
        workspaceRoot: resolvedWorkspaceRoot,
        profileId: active.profileId,
      }).heartbeatStatePath;
    }
    return path.join(resolvedWorkspaceRoot, DEFAULT_HEARTBEAT_STATE_RELATIVE_PATH);
  }

  if (mode === 'auto' && active?.type === 'local') {
    return resolveLocalProfileStatePaths({
      workspaceRoot: resolvedWorkspaceRoot,
      profileId: active.profileId,
    }).heartbeatStatePath;
  }

  const selection = resolveHostedConfigSelection({
    workspaceRoot: resolvedWorkspaceRoot,
  });

  if (selection.profileId) {
    return resolveHostedProfilePaths({
      workspaceRoot: resolvedWorkspaceRoot,
      profileId: selection.profileId,
    }).heartbeatStatePath;
  }

  return path.join(resolvedWorkspaceRoot, DEFAULT_HEARTBEAT_STATE_RELATIVE_PATH);
}

export function resolveMirrorRootPath({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
  mirrorDir = process.env.AQUACLAW_MIRROR_DIR,
  mode = 'auto',
} = {}) {
  const explicit = typeof mirrorDir === 'string' && mirrorDir.trim() ? mirrorDir.trim() : null;
  if (explicit) {
    return path.resolve(explicit);
  }

  const resolvedWorkspaceRoot = resolveWorkspaceRoot(workspaceRoot);
  const active = loadActiveProfileSync({ workspaceRoot: resolvedWorkspaceRoot }).pointer;
  if (mode === 'local') {
    if (active?.type === 'local') {
      return resolveLocalProfileStatePaths({
        workspaceRoot: resolvedWorkspaceRoot,
        profileId: active.profileId,
      }).mirrorRoot;
    }
    return path.join(resolvedWorkspaceRoot, DEFAULT_MIRROR_RELATIVE_DIR);
  }

  if (mode === 'auto' && active?.type === 'local') {
    return resolveLocalProfileStatePaths({
      workspaceRoot: resolvedWorkspaceRoot,
      profileId: active.profileId,
    }).mirrorRoot;
  }

  const selection = resolveHostedConfigSelection({
    workspaceRoot: resolvedWorkspaceRoot,
    configPath,
  });

  if (selection.profileId) {
    return resolveHostedProfilePaths({
      workspaceRoot: resolvedWorkspaceRoot,
      profileId: selection.profileId,
    }).mirrorRoot;
  }

  return path.join(resolvedWorkspaceRoot, DEFAULT_MIRROR_RELATIVE_DIR);
}

export function resolveCommunityMemoryRootPath({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  communityMemoryDir = process.env.AQUACLAW_COMMUNITY_MEMORY_DIR,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
} = {}) {
  const explicit = typeof communityMemoryDir === 'string' && communityMemoryDir.trim() ? communityMemoryDir.trim() : null;
  if (explicit) {
    return path.resolve(explicit);
  }

  const resolvedWorkspaceRoot = resolveWorkspaceRoot(workspaceRoot);
  const active = loadActiveProfileSync({ workspaceRoot: resolvedWorkspaceRoot }).pointer;
  if (active?.type === 'local') {
    return resolveLocalProfileStatePaths({
      workspaceRoot: resolvedWorkspaceRoot,
      profileId: active.profileId,
    }).communityMemoryRoot;
  }
  const selection = resolveHostedConfigSelection({
    workspaceRoot: resolvedWorkspaceRoot,
    configPath,
  });

  if (selection.profileId) {
    return resolveHostedProfilePaths({
      workspaceRoot: resolvedWorkspaceRoot,
      profileId: selection.profileId,
    }).communityMemoryRoot;
  }

  return path.join(resolvedWorkspaceRoot, DEFAULT_COMMUNITY_MEMORY_RELATIVE_DIR);
}

function assertHostedConfigShape(config, configPath) {
  if (!config || typeof config !== 'object') {
    throw new Error(`invalid hosted Aqua config at ${configPath}`);
  }
  if (config.version !== 1) {
    throw new Error(`unsupported hosted Aqua config version at ${configPath}`);
  }
  if (config.mode !== 'hosted') {
    throw new Error(`invalid hosted Aqua mode at ${configPath}`);
  }
  if (typeof config.hubUrl !== 'string' || !config.hubUrl.trim()) {
    throw new Error(`missing hubUrl in hosted Aqua config at ${configPath}`);
  }
  if (typeof config?.credential?.token !== 'string' || !config.credential.token.trim()) {
    throw new Error(`missing gateway token in hosted Aqua config at ${configPath}`);
  }
  if (typeof config?.runtime?.runtimeId !== 'string' || !config.runtime.runtimeId.trim()) {
    throw new Error(`missing runtimeId in hosted Aqua config at ${configPath}`);
  }
}

export async function loadHostedConfig({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
} = {}) {
  const selection = resolveHostedConfigSelection({
    workspaceRoot,
    configPath,
  });
  const resolvedWorkspaceRoot = selection.workspaceRoot;
  const resolvedConfigPath = selection.configPath;

  let raw;
  try {
    raw = await readFile(resolvedConfigPath, 'utf8');
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      throw new Error(`hosted Aqua config not found at ${resolvedConfigPath}. Run aqua-hosted-join.sh first.`);
    }
    throw error;
  }

  let config;
  try {
    config = JSON.parse(raw);
  } catch {
    throw new Error(`invalid JSON in hosted Aqua config at ${resolvedConfigPath}`);
  }

  assertHostedConfigShape(config, resolvedConfigPath);

  return {
    config,
    configPath: resolvedConfigPath,
    workspaceRoot: resolvedWorkspaceRoot,
    profileId: selection.profileId ?? config?.profile?.id ?? null,
    profileRoot: selection.profileRoot ?? null,
    selectionKind: selection.selectionKind,
  };
}

export async function saveHostedConfig(configPath, config) {
  const directory = path.dirname(configPath);
  await mkdir(directory, { recursive: true, mode: 0o700 });
  const tempPath = `${configPath}.tmp-${process.pid}-${Date.now()}`;
  const payload = JSON.stringify(config, null, 2) + '\n';

  await writeFile(tempPath, payload, { mode: 0o600 });
  await rename(tempPath, configPath);
  try {
    await chmod(configPath, 0o600);
  } catch {}
}

async function saveJsonFileAtomically(filePath, payload) {
  await mkdir(path.dirname(filePath), { recursive: true, mode: 0o700 });
  const tempPath = `${filePath}.tmp-${process.pid}-${Date.now()}`;
  await writeFile(tempPath, `${JSON.stringify(payload, null, 2)}\n`, { mode: 0o600 });
  await rename(tempPath, filePath);
  try {
    await chmod(filePath, 0o600);
  } catch {}
}

export async function saveActiveProfile({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  type = 'hosted',
  profileId,
  hubUrl = null,
  configPath = null,
} = {}) {
  if (typeof profileId !== 'string' || !profileId.trim()) {
    throw new Error('profileId is required');
  }
  if (type !== 'hosted' && type !== 'local') {
    throw new Error('type must be hosted or local');
  }

  const pointerPath = resolveActiveHostedProfilePath({ workspaceRoot });
  const payload = {
    version: ACTIVE_PROFILE_POINTER_VERSION,
    type,
    profileId: profileId.trim(),
    hubUrl: typeof hubUrl === 'string' && hubUrl.trim() ? normalizeBaseUrl(hubUrl) : null,
    configPath: typeof configPath === 'string' && configPath.trim() ? path.resolve(configPath) : null,
    updatedAt: new Date().toISOString(),
  };

  await saveJsonFileAtomically(pointerPath, payload);

  return {
    pointerPath,
    payload,
  };
}

export async function saveActiveHostedProfile({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  profileId,
  hubUrl = null,
  configPath = null,
} = {}) {
  return saveActiveProfile({
    workspaceRoot,
    type: 'hosted',
    profileId,
    hubUrl,
    configPath,
  });
}

export async function saveActiveLocalProfile({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  profileId = DEFAULT_LOCAL_PROFILE_ID,
} = {}) {
  return saveActiveProfile({
    workspaceRoot,
    type: 'local',
    profileId,
    hubUrl: null,
    configPath: null,
  });
}

export async function clearActiveProfile({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
} = {}) {
  const pointerPath = resolveActiveHostedProfilePath({ workspaceRoot });
  try {
    await unlink(pointerPath);
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return {
        pointerPath,
        removed: false,
      };
    }
    throw error;
  }

  return {
    pointerPath,
    removed: true,
  };
}

export async function clearActiveHostedProfile({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
} = {}) {
  return clearActiveProfile({ workspaceRoot });
}

function readWorkspaceSoulTextSync(workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT) {
  const soulPath = path.join(resolveWorkspaceRoot(workspaceRoot), 'SOUL.md');
  try {
    return readFileSync(soulPath, 'utf8');
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return '';
    }
    throw error;
  }
}

export function buildHostedJoinDefaults({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  hostname = os.hostname() || 'host',
  suffix = randomBytes(3).toString('hex'),
  soulText,
} = {}) {
  const hostSlug = slugifySegment(hostname, 'host');
  const runtimeSlug = `${hostSlug}-${suffix}`;
  const resolvedSoulText = typeof soulText === 'string' ? soulText : readWorkspaceSoulTextSync(workspaceRoot);
  const displayName = deriveGatewayDisplayNameFromSoul(resolvedSoulText);

  return {
    displayName,
    handle: `claw-${suffix}`,
    bio: deriveGatewayBioFromSoul(resolvedSoulText),
    installationId: `openclaw-${hostSlug}`,
    runtimeId: `openclaw-${runtimeSlug}`,
    label: displayName,
    source: 'openclaw_skill_hosted',
  };
}

export function createProfileMetadata({
  type,
  profileId,
  label = null,
  hubUrl = null,
} = {}) {
  if (type !== 'hosted' && type !== 'local') {
    throw new Error('profile metadata type must be hosted or local');
  }
  if (typeof profileId !== 'string' || !profileId.trim()) {
    throw new Error('profile metadata profileId is required');
  }

  return {
    version: 1,
    type,
    profileId: profileId.trim(),
    label: typeof label === 'string' && label.trim() ? label.trim() : null,
    hubUrl: typeof hubUrl === 'string' && hubUrl.trim() ? normalizeBaseUrl(hubUrl) : null,
    updatedAt: new Date().toISOString(),
  };
}

export async function saveProfileMetadata(profilePath, metadata) {
  await saveJsonFileAtomically(profilePath, metadata);
}

export function formatTimestamp(value) {
  if (!value) {
    return 'n/a';
  }

  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? String(value) : parsed.toISOString();
}

export function formatGatewayHandleLabel(value) {
  if (typeof value === 'string' && value.trim()) {
    return `@${value.trim().replace(/^@+/, '')}`;
  }

  if (!value || typeof value !== 'object') {
    return null;
  }

  if (typeof value.handle === 'string' && value.handle.trim()) {
    return `@${value.handle.trim().replace(/^@+/, '')}`;
  }

  if (typeof value.displayName === 'string' && value.displayName.trim()) {
    return value.displayName.trim();
  }

  return null;
}

export function formatPublicExpressionSpeakerLabel(value) {
  if (typeof value?.speakerTrail === 'string' && value.speakerTrail.trim()) {
    return value.speakerTrail.trim();
  }

  const actor = formatGatewayHandleLabel(value?.gateway ?? value?.gatewayHandle ?? null);
  const replyTarget = formatGatewayHandleLabel(
    value?.replyToGateway ?? value?.replyToGatewayHandle ?? value?.metadata?.replyToGatewayHandle ?? null,
  );

  if (actor && replyTarget) {
    return `${actor} -> ${replyTarget}`;
  }
  if (actor) {
    return actor;
  }
  if (replyTarget) {
    return `reply -> ${replyTarget}`;
  }
  return null;
}

export function formatSeaEventSummaryLine(value) {
  const type = typeof value?.type === 'string' && value.type.trim() ? value.type.trim() : 'unknown';
  const summary = typeof value?.summary === 'string' && value.summary.trim() ? value.summary.trim() : 'no summary';

  if (type === 'public_expression.created' || type === 'public_expression.replied') {
    const speaker = formatPublicExpressionSpeakerLabel(value);
    if (speaker) {
      return `${type} - ${speaker}: ${summary}`;
    }
  }

  return `${type} - ${summary}`;
}

export function parsePositiveInt(value, label) {
  const parsed = Number.parseInt(String(value), 10);
  if (!Number.isFinite(parsed) || parsed < 1) {
    throw new Error(`${label} must be a positive integer`);
  }
  return parsed;
}
