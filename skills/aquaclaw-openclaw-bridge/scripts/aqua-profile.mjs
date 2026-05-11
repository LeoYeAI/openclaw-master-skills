#!/usr/bin/env node

import { access, readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

import {
  DEFAULT_AQUACLAW_STATE_RELATIVE_DIR,
  DEFAULT_COMMUNITY_MEMORY_DIR_NAME,
  DEFAULT_HEARTBEAT_STATE_FILE_NAME,
  DEFAULT_HOSTED_CONFIG_FILE_NAME,
  DEFAULT_MIRROR_DIR_NAME,
  formatTimestamp,
  buildHostedProfileId,
  clearActiveProfile,
  loadActiveProfileSync,
  loadHostedConfig,
  normalizeBaseUrl,
  parseArgValue,
  resolveHostedProfilePaths,
  resolveHostedProfilesRoot,
  resolveWorkspaceRoot,
  saveActiveHostedProfile,
  saveActiveLocalProfile,
} from './hosted-aqua-common.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);
const VALID_TYPES = new Set(['hosted', 'local']);

function printHelp() {
  console.log(`Usage: aqua-profile.mjs <command> [options]

Commands:
  list                         List saved local + hosted profiles on this machine
  show                         Show the current active profile selection
  switch                       Switch the active profile selection

Common options:
  --workspace-root <path>      OpenClaw workspace root
  --format <fmt>               json|markdown (default: markdown)

Switch options:
  --profile-id <id>            Saved profile id
  --type <type>                hosted|local (optional when the saved profile can be inferred)
  --hub-url <url>              Derive a hosted profile id from a hub URL
  --legacy                     Clear the active pointer and fall back to legacy hosted-bridge.json

Examples:
  aqua-profile.mjs list
  aqua-profile.mjs show
  aqua-profile.mjs switch --profile-id local-sandbox
  aqua-profile.mjs switch --profile-id hosted-aqua-example-com
  aqua-profile.mjs switch --hub-url https://aqua.example.com
  aqua-profile.mjs switch --legacy
`);
}

export function parseOptions(argv) {
  if (argv.length === 0) {
    printHelp();
    process.exit(1);
  }

  const command = argv[0];
  if (!['list', 'show', 'switch'].includes(command)) {
    throw new Error(`unknown command: ${command}`);
  }

  const options = {
    command,
    format: 'markdown',
    hubUrl: null,
    legacy: false,
    profileId: null,
    profileType: null,
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT ?? null,
  };

  for (let index = 1; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--legacy') {
      options.legacy = true;
      continue;
    }
    if (arg.startsWith('--workspace-root')) {
      options.workspaceRoot = parseArgValue(argv, index, arg, '--workspace-root').trim();
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
    if (arg.startsWith('--profile-id')) {
      options.profileId = parseArgValue(argv, index, arg, '--profile-id').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--type')) {
      options.profileType = parseArgValue(argv, index, arg, '--type').trim().toLowerCase();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--hub-url')) {
      options.hubUrl = normalizeBaseUrl(parseArgValue(argv, index, arg, '--hub-url').trim());
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }

    throw new Error(`unknown option: ${arg}`);
  }

  if (!VALID_FORMATS.has(options.format)) {
    throw new Error('--format must be json or markdown');
  }
  if (options.profileType && !VALID_TYPES.has(options.profileType)) {
    throw new Error('--type must be hosted or local');
  }
  if (options.command !== 'switch' && (options.profileId || options.profileType || options.hubUrl || options.legacy)) {
    throw new Error(`${options.command} does not accept switch-only options`);
  }
  if (options.command === 'switch' && options.legacy && (options.profileId || options.profileType || options.hubUrl)) {
    throw new Error('--legacy cannot be combined with --profile-id, --type, or --hub-url');
  }

  options.workspaceRoot = resolveWorkspaceRoot(options.workspaceRoot);
  return options;
}

async function pathExists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

function buildLegacyPaths(workspaceRoot) {
  const stateRoot = path.join(workspaceRoot, DEFAULT_AQUACLAW_STATE_RELATIVE_DIR);
  return {
    stateRoot,
    configPath: path.join(stateRoot, DEFAULT_HOSTED_CONFIG_FILE_NAME),
    mirrorRoot: path.join(stateRoot, DEFAULT_MIRROR_DIR_NAME),
    heartbeatStatePath: path.join(stateRoot, DEFAULT_HEARTBEAT_STATE_FILE_NAME),
    communityMemoryRoot: path.join(stateRoot, DEFAULT_COMMUNITY_MEMORY_DIR_NAME),
  };
}

async function readJsonIfPresent(filePath) {
  try {
    const raw = await readFile(filePath, 'utf8');
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

async function loadProfileMetadata(profilePath, profileId) {
  const raw = await readJsonIfPresent(profilePath);
  if (raw === null) {
    return null;
  }
  if (!raw || typeof raw !== 'object') {
    throw new Error(`invalid profile metadata at ${profilePath}`);
  }
  if (raw.version !== undefined && raw.version !== 1) {
    throw new Error(`unsupported profile metadata version at ${profilePath}`);
  }
  if (raw.type !== 'hosted' && raw.type !== 'local') {
    throw new Error(`invalid profile metadata type at ${profilePath}`);
  }
  if (typeof raw.profileId !== 'string' || !raw.profileId.trim()) {
    throw new Error(`missing profileId in profile metadata at ${profilePath}`);
  }
  if (raw.profileId.trim() !== profileId) {
    throw new Error(`profile metadata id mismatch at ${profilePath}`);
  }

  return {
    type: raw.type,
    profileId: raw.profileId.trim(),
    label: typeof raw.label === 'string' && raw.label.trim() ? raw.label.trim() : null,
    hubUrl: typeof raw.hubUrl === 'string' && raw.hubUrl.trim() ? normalizeBaseUrl(raw.hubUrl) : null,
    updatedAt: typeof raw.updatedAt === 'string' && raw.updatedAt.trim() ? raw.updatedAt.trim() : null,
  };
}

function buildGatewayLabel(displayName, handle) {
  const normalizedDisplayName =
    typeof displayName === 'string' && displayName.trim() ? displayName.trim() : null;
  const normalizedHandle = typeof handle === 'string' && handle.trim() ? handle.trim().replace(/^@+/, '') : null;

  if (normalizedDisplayName && normalizedHandle) {
    return `${normalizedDisplayName} (@${normalizedHandle})`;
  }
  if (normalizedDisplayName) {
    return normalizedDisplayName;
  }
  if (normalizedHandle) {
    return `@${normalizedHandle}`;
  }
  return null;
}

async function buildNamedProfileRecord({ workspaceRoot, profileId, activePointer = null }) {
  const profilePaths = resolveHostedProfilePaths({
    workspaceRoot,
    profileId,
  });
  const warnings = [];

  let metadata = null;
  try {
    metadata = await loadProfileMetadata(profilePaths.profilePath, profileId);
  } catch (error) {
    warnings.push(error instanceof Error ? error.message : String(error));
  }

  const configExists = await pathExists(profilePaths.configPath);
  let loadedHosted = null;
  if (configExists) {
    try {
      loadedHosted = await loadHostedConfig({
        workspaceRoot,
        configPath: profilePaths.configPath,
      });
    } catch (error) {
      warnings.push(error instanceof Error ? error.message : String(error));
    }
  }

  const type = metadata?.type ?? (configExists ? 'hosted' : null);
  if (type === 'local' && configExists) {
    warnings.push(`local profile should not also have hosted config at ${profilePaths.configPath}`);
  }
  if (type === 'hosted' && !configExists) {
    warnings.push(`hosted profile config not found at ${profilePaths.configPath}`);
  }

  return {
    source: 'profile',
    active: Boolean(activePointer && activePointer.profileId === profileId),
    activePointerType: activePointer?.profileId === profileId ? activePointer.type : null,
    type,
    profileId,
    profileRoot: profilePaths.profileRoot,
    profilePath: profilePaths.profilePath,
    label: metadata?.label ?? loadedHosted?.config?.runtime?.label ?? null,
    hubUrl: metadata?.hubUrl ?? loadedHosted?.config?.hubUrl ?? null,
    configPath: configExists ? profilePaths.configPath : null,
    gatewayHandle: loadedHosted?.config?.gateway?.handle ?? null,
    gatewayDisplayName: loadedHosted?.config?.gateway?.displayName ?? null,
    gatewayLabel: buildGatewayLabel(
      loadedHosted?.config?.gateway?.displayName ?? null,
      loadedHosted?.config?.gateway?.handle ?? null,
    ),
    runtimeId: loadedHosted?.config?.runtime?.runtimeId ?? null,
    updatedAt: metadata?.updatedAt ?? loadedHosted?.config?.updatedAt ?? loadedHosted?.config?.connectedAt ?? null,
    mirrorRoot: profilePaths.mirrorRoot,
    heartbeatStatePath: profilePaths.heartbeatStatePath,
    communityMemoryRoot: profilePaths.communityMemoryRoot,
    warning: warnings.length > 0 ? warnings.join('; ') : null,
  };
}

async function buildLegacyHostedRecord({ workspaceRoot, activePointer = null }) {
  const legacyPaths = buildLegacyPaths(workspaceRoot);
  if (!(await pathExists(legacyPaths.configPath))) {
    return null;
  }

  const warnings = [];
  let loadedHosted = null;
  try {
    loadedHosted = await loadHostedConfig({
      workspaceRoot,
      configPath: legacyPaths.configPath,
    });
  } catch (error) {
    warnings.push(error instanceof Error ? error.message : String(error));
  }

  return {
    source: 'legacy',
    active: activePointer === null,
    activePointerType: activePointer === null ? null : activePointer.type,
    type: 'hosted',
    profileId: 'legacy',
    profileRoot: legacyPaths.stateRoot,
    profilePath: null,
    label: loadedHosted?.config?.runtime?.label ?? null,
    hubUrl: loadedHosted?.config?.hubUrl ?? null,
    configPath: legacyPaths.configPath,
    gatewayHandle: loadedHosted?.config?.gateway?.handle ?? null,
    gatewayDisplayName: loadedHosted?.config?.gateway?.displayName ?? null,
    gatewayLabel: buildGatewayLabel(
      loadedHosted?.config?.gateway?.displayName ?? null,
      loadedHosted?.config?.gateway?.handle ?? null,
    ),
    runtimeId: loadedHosted?.config?.runtime?.runtimeId ?? null,
    updatedAt: loadedHosted?.config?.updatedAt ?? loadedHosted?.config?.connectedAt ?? null,
    mirrorRoot: legacyPaths.mirrorRoot,
    heartbeatStatePath: legacyPaths.heartbeatStatePath,
    communityMemoryRoot: legacyPaths.communityMemoryRoot,
    warning: warnings.length > 0 ? warnings.join('; ') : null,
  };
}

export async function listProfiles({ workspaceRoot }) {
  const profilesRoot = resolveHostedProfilesRoot({ workspaceRoot });
  const active = loadActiveProfileSync({ workspaceRoot });
  const items = [];

  try {
    const entries = await readdir(profilesRoot, { withFileTypes: true });
    const directories = entries
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .sort((left, right) => left.localeCompare(right));

    for (const profileId of directories) {
      items.push(
        await buildNamedProfileRecord({
          workspaceRoot,
          profileId,
          activePointer: active.pointer,
        }),
      );
    }
  } catch (error) {
    if (!(error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT')) {
      throw error;
    }
  }

  const legacy = await buildLegacyHostedRecord({
    workspaceRoot,
    activePointer: active.pointer,
  });
  if (legacy) {
    items.push(legacy);
  }

  return {
    workspaceRoot,
    profilesRoot,
    activeProfilePath: active.pointerPath,
    activePointer: active.pointer,
    items,
  };
}

export async function showCurrentProfile({ workspaceRoot }) {
  const active = loadActiveProfileSync({ workspaceRoot });
  const legacy = await buildLegacyHostedRecord({
    workspaceRoot,
    activePointer: active.pointer,
  });

  if (!active.pointer) {
    return {
      workspaceRoot,
      activeProfilePath: active.pointerPath,
      activePointer: null,
      selectionKind: legacy ? 'legacy' : 'none',
      selected: legacy,
    };
  }

  return {
    workspaceRoot,
    activeProfilePath: active.pointerPath,
    activePointer: active.pointer,
    selectionKind: active.pointer.type,
    selected: await buildNamedProfileRecord({
      workspaceRoot,
      profileId: active.pointer.profileId,
      activePointer: active.pointer,
    }),
  };
}

async function resolveSwitchTarget(options) {
  if (options.legacy) {
    return {
      type: 'hosted',
      source: 'legacy',
      profileId: null,
      configPath: buildLegacyPaths(options.workspaceRoot).configPath,
    };
  }

  const profileId = options.profileId || (options.hubUrl ? buildHostedProfileId(options.hubUrl) : null);
  if (!profileId) {
    throw new Error('switch requires --profile-id, --hub-url, or --legacy');
  }

  const profilePaths = resolveHostedProfilePaths({
    workspaceRoot: options.workspaceRoot,
    profileId,
  });
  const metadata = await loadProfileMetadata(profilePaths.profilePath, profileId);
  const configExists = await pathExists(profilePaths.configPath);
  const inferredType = metadata?.type ?? (configExists ? 'hosted' : null);

  if (options.profileType && inferredType && options.profileType !== inferredType) {
    throw new Error(`profile ${profileId} is ${inferredType}, not ${options.profileType}`);
  }

  const type = options.profileType ?? inferredType;
  if (!type) {
    throw new Error(`could not determine profile type for ${profileId}; use --type hosted or --type local`);
  }

  return {
    type,
    source: 'profile',
    profileId,
    profilePaths,
    metadata,
    configExists,
  };
}

export async function switchProfile({ workspaceRoot, profileId = null, profileType = null, hubUrl = null, legacy = false }) {
  const target = await resolveSwitchTarget({
    workspaceRoot,
    profileId,
    profileType,
    hubUrl,
    legacy,
  });

  if (target.source === 'legacy') {
    const cleared = await clearActiveProfile({ workspaceRoot });
    const legacyRecord = await buildLegacyHostedRecord({
      workspaceRoot,
      activePointer: null,
    });
    return {
      workspaceRoot,
      activeProfilePath: cleared.pointerPath,
      removed: cleared.removed,
      selectionKind: legacyRecord ? 'legacy' : 'none',
      selected: legacyRecord,
    };
  }

  if (target.type === 'local') {
    if (!target.metadata) {
      throw new Error(`local profile metadata not found at ${target.profilePaths.profilePath}`);
    }
    const saved = await saveActiveLocalProfile({
      workspaceRoot,
      profileId: target.profileId,
    });
    return {
      workspaceRoot,
      activeProfilePath: saved.pointerPath,
      removed: false,
      selectionKind: 'local',
      selected: await buildNamedProfileRecord({
        workspaceRoot,
        profileId: target.profileId,
        activePointer: saved.payload,
      }),
    };
  }

  if (!target.configExists) {
    throw new Error(`hosted profile config not found at ${target.profilePaths.configPath}`);
  }

  const loaded = await loadHostedConfig({
    workspaceRoot,
    configPath: target.profilePaths.configPath,
  });
  const saved = await saveActiveHostedProfile({
    workspaceRoot,
    profileId: target.profileId,
    hubUrl: loaded.config.hubUrl,
    configPath: target.profilePaths.configPath,
  });

  return {
    workspaceRoot,
    activeProfilePath: saved.pointerPath,
    removed: false,
    selectionKind: 'hosted',
    selected: await buildNamedProfileRecord({
      workspaceRoot,
      profileId: target.profileId,
      activePointer: saved.payload,
    }),
  };
}

function renderProfileLines(record) {
  if (!record) {
    return ['- No active profile selection on this machine.'];
  }

  return [
    `- Source: ${record.source}`,
    `- Profile type: ${record.type ?? 'unknown'}`,
    `- Profile id: ${record.profileId ?? 'none'}`,
    record.label ? `- Label: ${record.label}` : null,
    record.profilePath ? `- Profile file: ${record.profilePath}` : null,
    record.configPath ? `- Hosted config: ${record.configPath}` : null,
    record.hubUrl ? `- Hub: ${record.hubUrl}` : null,
    record.gatewayLabel ? `- Gateway: ${record.gatewayLabel}` : null,
    record.runtimeId ? `- Runtime: ${record.runtimeId}` : null,
    record.updatedAt ? `- Updated at: ${formatTimestamp(record.updatedAt)}` : null,
    record.mirrorRoot ? `- Mirror root: ${record.mirrorRoot}` : null,
    record.heartbeatStatePath ? `- Heartbeat state: ${record.heartbeatStatePath}` : null,
    record.communityMemoryRoot ? `- Community memory: ${record.communityMemoryRoot}` : null,
    record.warning ? `- Warning: ${record.warning}` : null,
  ].filter(Boolean);
}

export function formatMarkdown(result) {
  if (result.command === 'list') {
    const lines = [
      '# Aqua Profiles',
      `- Workspace root: ${result.workspaceRoot}`,
      `- Profiles root: ${result.profilesRoot}`,
      `- Active pointer path: ${result.activeProfilePath}`,
      `- Active pointer type: ${result.activePointer?.type ?? 'none'}`,
      `- Active pointer id: ${result.activePointer?.profileId ?? 'none'}`,
      '',
    ];

    if (result.items.length === 0) {
      lines.push('- No saved profiles found.');
      return lines.join('\n');
    }

    for (const item of result.items) {
      lines.push(`## ${item.profileId}${item.active ? ' (active)' : ''}`);
      lines.push(...renderProfileLines(item));
      lines.push('');
    }
    return lines.join('\n').trimEnd();
  }

  if (result.command === 'show') {
    return [
      '# Active Aqua Profile',
      `- Workspace root: ${result.workspaceRoot}`,
      `- Active pointer path: ${result.activeProfilePath}`,
      `- Active pointer type: ${result.activePointer?.type ?? 'none'}`,
      `- Active pointer id: ${result.activePointer?.profileId ?? 'none'}`,
      `- Selection kind: ${result.selectionKind}`,
      result.selectionKind === 'legacy'
        ? '- Active pointer file is absent; legacy root-level hosted config is currently selected.'
        : null,
      ...renderProfileLines(result.selected),
    ]
      .filter(Boolean)
      .join('\n');
  }

  return [
    '# Aqua Profile Switch',
    `- Workspace root: ${result.workspaceRoot}`,
    `- Active pointer path: ${result.activeProfilePath}`,
    `- Selection kind: ${result.selectionKind}`,
    result.selectionKind === 'legacy' && result.removed
      ? '- Active pointer file removed; legacy root-level hosted config is now selected.'
      : null,
    ...renderProfileLines(result.selected),
  ]
    .filter(Boolean)
    .join('\n');
}

export async function runCommand(options) {
  if (options.command === 'list') {
    return {
      command: 'list',
      ...(await listProfiles({
        workspaceRoot: options.workspaceRoot,
      })),
    };
  }
  if (options.command === 'show') {
    return {
      command: 'show',
      ...(await showCurrentProfile({
        workspaceRoot: options.workspaceRoot,
      })),
    };
  }
  return {
    command: 'switch',
    ...(await switchProfile({
      workspaceRoot: options.workspaceRoot,
      profileId: options.profileId,
      profileType: options.profileType,
      hubUrl: options.hubUrl,
      legacy: options.legacy,
    })),
  };
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const result = await runCommand(options);
  if (options.format === 'json') {
    console.log(JSON.stringify(result, null, 2));
    return;
  }
  console.log(formatMarkdown(result));
}

if (!process.argv.includes('--test') && process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
