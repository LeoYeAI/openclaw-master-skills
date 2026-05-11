#!/usr/bin/env node

import { access, cp, readdir } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

import {
  DEFAULT_AQUACLAW_STATE_RELATIVE_DIR,
  DEFAULT_HEARTBEAT_STATE_FILE_NAME,
  DEFAULT_HOSTED_CONFIG_FILE_NAME,
  DEFAULT_HOSTED_PULSE_STATE_FILE_NAME,
  DEFAULT_MIRROR_DIR_NAME,
  buildHostedProfileId,
  clearActiveHostedProfile,
  createProfileMetadata,
  formatTimestamp,
  loadActiveProfileSync,
  loadActiveHostedProfileSync,
  loadHostedConfig,
  normalizeBaseUrl,
  parseArgValue,
  resolveHostedConfigPath,
  resolveHostedProfilePaths,
  resolveHostedProfilesRoot,
  resolveWorkspaceRoot,
  saveActiveHostedProfile,
  saveHostedConfig,
  saveProfileMetadata,
} from './hosted-aqua-common.mjs';
import { syncManagedToolsBlock } from './aquaclaw-tools-md.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);

function printHelp() {
  console.log(`Usage: aqua-hosted-profile.mjs <command> [options]

Commands:
  list                         List saved hosted profiles
  show                         Show the current hosted profile selection
  switch                       Switch the active hosted profile
  migrate-legacy               Copy legacy hosted config/state into a named profile and activate it

Common options:
  --workspace-root <path>      OpenClaw workspace root
  --format <fmt>               json|markdown (default: markdown)
  --force                      Overwrite an existing migration target when supported

Switch options:
  --profile-id <id>            Saved hosted profile id
  --hub-url <url>              Derive the profile id from a hub URL
  --legacy                     Clear the active profile pointer and fall back to legacy hosted-bridge.json

Legacy migration options:
  --profile-id <id>            Target profile id (default: hosted-<legacy-hub-host>)
  --hub-url <url>              Must match the legacy config hub URL when provided

Examples:
  aqua-hosted-profile.mjs list
  aqua-hosted-profile.mjs show
  aqua-hosted-profile.mjs switch --profile-id hosted-aqua-example-com
  aqua-hosted-profile.mjs switch --hub-url https://aqua.example.com
  aqua-hosted-profile.mjs switch --legacy
  aqua-hosted-profile.mjs migrate-legacy
`);
}

function parseOptions(argv) {
  if (argv.length === 0) {
    printHelp();
    process.exit(1);
  }

  const command = argv[0];
  if (!['list', 'show', 'switch', 'migrate-legacy'].includes(command)) {
    throw new Error(`unknown command: ${command}`);
  }

  const options = {
    command,
    force: false,
    format: 'markdown',
    hubUrl: null,
    legacy: false,
    profileId: null,
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
    if (arg === '--force') {
      options.force = true;
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

  options.workspaceRoot = resolveWorkspaceRoot(options.workspaceRoot);
  return options;
}

async function fileExists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function listHostedProfiles(workspaceRoot) {
  const profilesRoot = resolveHostedProfilesRoot({ workspaceRoot });
  const activePointer = loadActiveHostedProfileSync({ workspaceRoot }).pointer;
  const items = [];

  try {
    const entries = await readdir(profilesRoot, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) {
        continue;
      }
      const profilePaths = resolveHostedProfilePaths({
        workspaceRoot,
        profileId: entry.name,
      });

      try {
        const loaded = await loadHostedConfig({
          workspaceRoot,
          configPath: profilePaths.configPath,
        });
        items.push({
          profileId: entry.name,
          active: activePointer?.profileId === entry.name,
          configPath: profilePaths.configPath,
          hubUrl: loaded.config.hubUrl,
          gatewayHandle: loaded.config?.gateway?.handle ?? null,
          gatewayDisplayName: loaded.config?.gateway?.displayName ?? null,
          runtimeId: loaded.config?.runtime?.runtimeId ?? null,
          updatedAt: loaded.config?.updatedAt ?? loaded.config?.connectedAt ?? null,
          source: 'profile',
        });
      } catch (error) {
        items.push({
          profileId: entry.name,
          active: activePointer?.profileId === entry.name,
          configPath: profilePaths.configPath,
          hubUrl: null,
          gatewayHandle: null,
          gatewayDisplayName: null,
          runtimeId: null,
          updatedAt: null,
          source: 'profile',
          warning: error instanceof Error ? error.message : String(error),
        });
      }
    }
  } catch (error) {
    if (!(error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT')) {
      throw error;
    }
  }

  const legacyPath = path.join(workspaceRoot, '.aquaclaw', 'hosted-bridge.json');
  if (await fileExists(legacyPath)) {
    try {
      const loaded = await loadHostedConfig({
        workspaceRoot,
        configPath: legacyPath,
      });
      items.push({
        profileId: 'legacy',
        active: !activePointer,
        configPath: legacyPath,
        hubUrl: loaded.config.hubUrl,
        gatewayHandle: loaded.config?.gateway?.handle ?? null,
        gatewayDisplayName: loaded.config?.gateway?.displayName ?? null,
        runtimeId: loaded.config?.runtime?.runtimeId ?? null,
        updatedAt: loaded.config?.updatedAt ?? loaded.config?.connectedAt ?? null,
        source: 'legacy',
      });
    } catch (error) {
      items.push({
        profileId: 'legacy',
        active: !activePointer,
        configPath: legacyPath,
        hubUrl: null,
        gatewayHandle: null,
        gatewayDisplayName: null,
        runtimeId: null,
        updatedAt: null,
        source: 'legacy',
        warning: error instanceof Error ? error.message : String(error),
      });
    }
  }

  items.sort((left, right) => left.profileId.localeCompare(right.profileId));
  return {
    activeProfileId: activePointer?.profileId ?? null,
    items,
    profilesRoot,
  };
}

async function showCurrentSelection(workspaceRoot) {
  const selectionPath = resolveHostedConfigPath({ workspaceRoot });
  const activeProfile = loadActiveProfileSync({ workspaceRoot }).pointer;
  const activePointer = loadActiveHostedProfileSync({ workspaceRoot }).pointer;
  const exists = await fileExists(selectionPath);

  if (activeProfile?.type === 'local') {
    return {
      workspaceRoot,
      activePointer,
      activeProfile,
      configPath: selectionPath,
      exists,
      profileId: null,
      hubUrl: null,
      gatewayHandle: null,
      gatewayDisplayName: null,
      runtimeId: null,
      localProfileSelected: true,
    };
  }

  if (!exists) {
    return {
      workspaceRoot,
      activePointer,
      activeProfile,
      configPath: selectionPath,
      exists: false,
      profileId: activePointer?.profileId ?? null,
      hubUrl: null,
      gatewayHandle: null,
      gatewayDisplayName: null,
      runtimeId: null,
    };
  }

  const loaded = await loadHostedConfig({
    workspaceRoot,
    configPath: selectionPath,
  });

  return {
    workspaceRoot,
    activePointer,
    activeProfile,
    configPath: selectionPath,
    exists: true,
    profileId: loaded.profileId ?? activePointer?.profileId ?? null,
    hubUrl: loaded.config.hubUrl,
    gatewayHandle: loaded.config?.gateway?.handle ?? null,
    gatewayDisplayName: loaded.config?.gateway?.displayName ?? null,
    runtimeId: loaded.config?.runtime?.runtimeId ?? null,
    updatedAt: loaded.config?.updatedAt ?? loaded.config?.connectedAt ?? null,
  };
}

function resolveLegacyHostedPaths(workspaceRoot) {
  const stateRoot = path.join(workspaceRoot, DEFAULT_AQUACLAW_STATE_RELATIVE_DIR);
  return {
    stateRoot,
    configPath: path.join(stateRoot, DEFAULT_HOSTED_CONFIG_FILE_NAME),
    pulseStatePath: path.join(stateRoot, DEFAULT_HOSTED_PULSE_STATE_FILE_NAME),
    heartbeatStatePath: path.join(stateRoot, DEFAULT_HEARTBEAT_STATE_FILE_NAME),
    mirrorRoot: path.join(stateRoot, DEFAULT_MIRROR_DIR_NAME),
  };
}

async function copyFileIfPresent(sourcePath, destinationPath, { force, label }) {
  const sourceExists = await fileExists(sourcePath);
  if (!sourceExists) {
    return {
      label,
      sourcePath,
      destinationPath,
      present: false,
      copied: false,
    };
  }

  if (!force && (await fileExists(destinationPath))) {
    throw new Error(`${label} already exists at ${destinationPath}; rerun with --force to overwrite it`);
  }

  await cp(sourcePath, destinationPath, { force: true });
  return {
    label,
    sourcePath,
    destinationPath,
    present: true,
    copied: true,
  };
}

async function copyDirectoryIfPresent(sourcePath, destinationPath, { force, label }) {
  const sourceExists = await fileExists(sourcePath);
  if (!sourceExists) {
    return {
      label,
      sourcePath,
      destinationPath,
      present: false,
      copied: false,
    };
  }

  if (!force && (await fileExists(destinationPath))) {
    throw new Error(`${label} already exists at ${destinationPath}; rerun with --force to overwrite it`);
  }

  await cp(sourcePath, destinationPath, {
    recursive: true,
    force: true,
  });
  return {
    label,
    sourcePath,
    destinationPath,
    present: true,
    copied: true,
  };
}

export async function migrateLegacyHostedProfile({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT ?? null,
  profileId = null,
  hubUrl = null,
  force = false,
} = {}) {
  const resolvedWorkspaceRoot = resolveWorkspaceRoot(workspaceRoot);
  const legacyPaths = resolveLegacyHostedPaths(resolvedWorkspaceRoot);
  const legacyExists = await fileExists(legacyPaths.configPath);
  if (!legacyExists) {
    throw new Error(`legacy hosted config not found at ${legacyPaths.configPath}`);
  }

  const loaded = await loadHostedConfig({
    workspaceRoot: resolvedWorkspaceRoot,
    configPath: legacyPaths.configPath,
  });

  const legacyHubUrl = normalizeBaseUrl(loaded.config.hubUrl);
  if (hubUrl && normalizeBaseUrl(hubUrl) !== legacyHubUrl) {
    throw new Error(`--hub-url does not match legacy hosted config hub URL (${legacyHubUrl})`);
  }

  const resolvedProfileId = profileId || buildHostedProfileId(legacyHubUrl);
  const profilePaths = resolveHostedProfilePaths({
    workspaceRoot: resolvedWorkspaceRoot,
    profileId: resolvedProfileId,
  });

  if (!force && (await fileExists(profilePaths.configPath))) {
    throw new Error(`hosted profile config already exists at ${profilePaths.configPath}; rerun with --force to overwrite it`);
  }

  const migratedConfig = {
    ...loaded.config,
    profile: {
      id: resolvedProfileId,
      type: 'hosted',
    },
    workspaceRoot: resolvedWorkspaceRoot,
  };

  await saveHostedConfig(profilePaths.configPath, migratedConfig);
  await saveProfileMetadata(
    profilePaths.profilePath,
    createProfileMetadata({
      type: 'hosted',
      profileId: resolvedProfileId,
      label: migratedConfig?.runtime?.label ?? null,
      hubUrl: legacyHubUrl,
    }),
  );

  const copiedPulse = await copyFileIfPresent(legacyPaths.pulseStatePath, profilePaths.pulseStatePath, {
    force,
    label: 'legacy hosted pulse state',
  });
  const copiedHeartbeat = await copyFileIfPresent(legacyPaths.heartbeatStatePath, profilePaths.heartbeatStatePath, {
    force,
    label: 'legacy runtime heartbeat state',
  });
  const copiedMirror = await copyDirectoryIfPresent(legacyPaths.mirrorRoot, profilePaths.mirrorRoot, {
    force,
    label: 'legacy mirror root',
  });

  const activeProfile = await saveActiveHostedProfile({
    workspaceRoot: resolvedWorkspaceRoot,
    profileId: resolvedProfileId,
    hubUrl: legacyHubUrl,
    configPath: profilePaths.configPath,
  });

  let toolsManagedBlockResult = null;
  let toolsManagedBlockWarning = null;
  try {
    toolsManagedBlockResult = await syncManagedToolsBlock({
      workspaceRoot: resolvedWorkspaceRoot,
      configPath: profilePaths.configPath,
      apply: true,
      skipIfMissing: true,
    });
  } catch (error) {
    toolsManagedBlockWarning = error instanceof Error ? error.message : String(error);
  }

  return {
    command: 'migrate-legacy',
    workspaceRoot: resolvedWorkspaceRoot,
    legacyConfigPath: legacyPaths.configPath,
    profileId: resolvedProfileId,
    configPath: profilePaths.configPath,
    hubUrl: legacyHubUrl,
    activeProfilePath: activeProfile.pointerPath,
    copied: {
      config: true,
      pulseState: copiedPulse.copied,
      heartbeatState: copiedHeartbeat.copied,
      mirrorRoot: copiedMirror.copied,
    },
    toolsManagedBlockResult,
    toolsManagedBlockWarning,
  };
}

function renderProfileMarkdown(result) {
  if (result.command === 'list') {
    const lines = [
      '# Hosted Profiles',
      `- Workspace root: ${result.workspaceRoot}`,
      `- Profiles root: ${result.profilesRoot}`,
      `- Active profile id: ${result.activeProfileId ?? 'legacy-or-none'}`,
      '',
    ];
    if (result.items.length === 0) {
      lines.push('- No hosted profiles saved yet.');
      return lines.join('\n');
    }

    for (const item of result.items) {
      lines.push(`## ${item.profileId}${item.active ? ' (active)' : ''}`);
      lines.push(`- Source: ${item.source}`);
      lines.push(`- Config: ${item.configPath}`);
      lines.push(`- Hub: ${item.hubUrl ?? 'n/a'}`);
      if (item.gatewayDisplayName || item.gatewayHandle) {
        lines.push(`- Gateway: ${item.gatewayDisplayName ?? 'n/a'}${item.gatewayHandle ? ` (@${item.gatewayHandle})` : ''}`);
      }
      if (item.runtimeId) {
        lines.push(`- Runtime: ${item.runtimeId}`);
      }
      if (item.updatedAt) {
        lines.push(`- Updated at: ${formatTimestamp(item.updatedAt)}`);
      }
      if (item.warning) {
        lines.push(`- Warning: ${item.warning}`);
      }
      lines.push('');
    }
    return lines.join('\n').trimEnd();
  }

  if (result.command === 'show') {
    return [
      '# Active Hosted Profile',
      `- Workspace root: ${result.workspaceRoot}`,
      `- Active profile type: ${result.activeProfile?.type ?? 'none'}`,
      result.localProfileSelected ? `- Active local profile: ${result.activeProfile?.profileId}` : null,
      `- Active profile id: ${result.profileId ?? 'legacy-or-none'}`,
      `- Config path: ${result.configPath}`,
      `- Config exists: ${result.exists ? 'yes' : 'no'}`,
      result.localProfileSelected
        ? '- Hosted profile selection is inactive because a local profile is currently selected.'
        : null,
      `- Hub: ${result.hubUrl ?? 'n/a'}`,
      result.gatewayDisplayName || result.gatewayHandle
        ? `- Gateway: ${result.gatewayDisplayName ?? 'n/a'}${result.gatewayHandle ? ` (@${result.gatewayHandle})` : ''}`
        : null,
      result.runtimeId ? `- Runtime: ${result.runtimeId}` : null,
      result.updatedAt ? `- Updated at: ${formatTimestamp(result.updatedAt)}` : null,
    ].filter(Boolean).join('\n');
  }

  if (result.command === 'migrate-legacy') {
    return [
      '# Hosted Legacy Migration',
      `- Workspace root: ${result.workspaceRoot}`,
      `- Legacy config: ${result.legacyConfigPath}`,
      `- Active profile id: ${result.profileId}`,
      `- Profile config: ${result.configPath}`,
      `- Hub: ${result.hubUrl}`,
      `- Active profile pointer: ${result.activeProfilePath}`,
      `- Copied pulse state: ${result.copied.pulseState ? 'yes' : 'no (missing legacy file)'}`,
      `- Copied heartbeat state: ${result.copied.heartbeatState ? 'yes' : 'no (missing legacy file)'}`,
      `- Copied mirror root: ${result.copied.mirrorRoot ? 'yes' : 'no (missing legacy dir)'}`,
      result.toolsManagedBlockResult?.action
        ? `- TOOLS.md managed block: ${result.toolsManagedBlockResult.action}`
        : null,
      result.toolsManagedBlockWarning ? `- TOOLS.md warning: ${result.toolsManagedBlockWarning}` : null,
      '- Legacy root-level files were left in place for safety.',
    ].filter(Boolean).join('\n');
  }

  return [
    '# Hosted Profile Switch',
    `- Workspace root: ${result.workspaceRoot}`,
    `- Active profile id: ${result.profileId ?? 'legacy'}`,
    `- Config path: ${result.configPath ?? 'legacy default'}`,
    `- Hub: ${result.hubUrl ?? 'legacy default'}`,
    result.removed ? '- Active pointer file removed; legacy fallback is now selected.' : null,
  ].filter(Boolean).join('\n');
}

async function runSwitch(options) {
  if (options.legacy) {
    const cleared = await clearActiveHostedProfile({
      workspaceRoot: options.workspaceRoot,
    });
    return {
      command: 'switch',
      workspaceRoot: options.workspaceRoot,
      profileId: null,
      configPath: path.join(options.workspaceRoot, '.aquaclaw', 'hosted-bridge.json'),
      hubUrl: null,
      removed: cleared.removed,
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
  if (!(await fileExists(profilePaths.configPath))) {
    throw new Error(`hosted profile config not found at ${profilePaths.configPath}`);
  }

  const loaded = await loadHostedConfig({
    workspaceRoot: options.workspaceRoot,
    configPath: profilePaths.configPath,
  });

  await saveActiveHostedProfile({
    workspaceRoot: options.workspaceRoot,
    profileId,
    hubUrl: loaded.config.hubUrl,
    configPath: profilePaths.configPath,
  });

  return {
    command: 'switch',
    workspaceRoot: options.workspaceRoot,
    profileId,
    configPath: profilePaths.configPath,
    hubUrl: loaded.config.hubUrl,
    removed: false,
  };
}

async function runMigrateLegacy(options) {
  return migrateLegacyHostedProfile({
    workspaceRoot: options.workspaceRoot,
    profileId: options.profileId,
    hubUrl: options.hubUrl,
    force: options.force,
  });
}

async function main() {
  const options = parseOptions(process.argv.slice(2));

  let result;
  if (options.command === 'list') {
    result = {
      command: 'list',
      workspaceRoot: options.workspaceRoot,
      ...(await listHostedProfiles(options.workspaceRoot)),
    };
  } else if (options.command === 'show') {
    result = {
      command: 'show',
      ...(await showCurrentSelection(options.workspaceRoot)),
    };
  } else if (options.command === 'migrate-legacy') {
    result = await runMigrateLegacy(options);
  } else {
    result = await runSwitch(options);
  }

  if (options.format === 'json') {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  console.log(renderProfileMarkdown(result));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
