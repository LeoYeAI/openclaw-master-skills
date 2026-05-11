#!/usr/bin/env node

import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

import {
  buildHostedProfileId,
  buildHostedJoinDefaults,
  createProfileMetadata,
  loadHostedConfig,
  normalizeBaseUrl,
  parseArgValue,
  parseHostedProfileIdFromConfigPath,
  requestJson,
  resolveHostedConfigPath,
  resolveHostedProfilePaths,
  resolveWorkspaceRoot,
  saveActiveHostedProfile,
  saveHostedConfig,
  saveProfileMetadata,
} from './hosted-aqua-common.mjs';
import { syncManagedToolsBlock } from './aquaclaw-tools-md.mjs';

function printHelp() {
  console.log(`Usage: aqua-hosted-join.mjs --hub-url <url> --invite-code <code> [options]

Required:
  --hub-url <url>              Hosted Aqua base URL
  --invite-code <code>         Hosted Aqua invite code

Optional:
  --workspace-root <path>      OpenClaw workspace root
  --config-path <path>         Hosted Aqua config path
  --display-name <name>        Gateway display name
  --handle <handle>            Gateway handle
  --bio <text>                 Gateway bio
  --visibility <value>         public|private|friends_only|invite_only
  --installation-id <id>       Runtime installation id
  --runtime-id <id>            Runtime id
  --label <label>              Runtime label
  --source <value>             Runtime source
  --profile-id <id>            Hosted profile id (default: hosted-<hub-host>)
  --force                      Overwrite an existing hosted config
  --help                       Show this message
`);
}

export function parseOptions(argv) {
  const options = {
    bio: null,
    configPath: process.env.AQUACLAW_HOSTED_CONFIG,
    displayName: null,
    force: false,
    handle: null,
    hubUrl: process.env.AQUA_HOSTED_URL,
    installationId: null,
    inviteCode: process.env.AQUA_INVITE_CODE,
    label: null,
    profileId: null,
    runtimeId: null,
    source: null,
    visibility: 'invite_only',
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--force') {
      options.force = true;
      continue;
    }
    if (arg.startsWith('--hub-url')) {
      options.hubUrl = parseArgValue(argv, index, arg, '--hub-url').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--invite-code')) {
      options.inviteCode = parseArgValue(argv, index, arg, '--invite-code').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
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
    if (arg.startsWith('--display-name')) {
      options.displayName = parseArgValue(argv, index, arg, '--display-name').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--handle')) {
      options.handle = parseArgValue(argv, index, arg, '--handle').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--bio')) {
      options.bio = parseArgValue(argv, index, arg, '--bio');
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--visibility')) {
      options.visibility = parseArgValue(argv, index, arg, '--visibility').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--installation-id')) {
      options.installationId = parseArgValue(argv, index, arg, '--installation-id').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--runtime-id')) {
      options.runtimeId = parseArgValue(argv, index, arg, '--runtime-id').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--label')) {
      options.label = parseArgValue(argv, index, arg, '--label').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--source')) {
      options.source = parseArgValue(argv, index, arg, '--source').trim();
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

    throw new Error(`unknown option: ${arg}`);
  }

  if (!options.hubUrl || !options.hubUrl.trim()) {
    throw new Error('--hub-url is required');
  }
  if (!options.inviteCode || !options.inviteCode.trim()) {
    throw new Error('--invite-code is required');
  }

  options.workspaceRoot = resolveWorkspaceRoot(options.workspaceRoot);
  const defaults = buildHostedJoinDefaults({
    workspaceRoot: options.workspaceRoot,
  });
  options.displayName = options.displayName ?? defaults.displayName;
  options.handle = options.handle ?? defaults.handle;
  options.bio = options.bio === null ? defaults.bio : options.bio;
  options.installationId = options.installationId ?? defaults.installationId;
  options.runtimeId = options.runtimeId ?? defaults.runtimeId;
  options.label = options.label ?? defaults.label;
  options.source = options.source ?? defaults.source;

  if (!options.displayName || !options.displayName.trim()) {
    throw new Error('--display-name must be non-empty');
  }
  if (!options.handle || !options.handle.trim()) {
    throw new Error('--handle must be non-empty');
  }
  if (!options.installationId || !options.installationId.trim()) {
    throw new Error('--installation-id must be non-empty');
  }
  if (!options.runtimeId || !options.runtimeId.trim()) {
    throw new Error('--runtime-id must be non-empty');
  }
  if (!options.label || !options.label.trim()) {
    throw new Error('--label must be non-empty');
  }
  if (!options.source || !options.source.trim()) {
    throw new Error('--source must be non-empty');
  }

  options.hubUrl = normalizeBaseUrl(options.hubUrl);
  const explicitConfigPath = typeof options.configPath === 'string' && options.configPath.trim();

  if (explicitConfigPath) {
    options.configPath = resolveHostedConfigPath({
      workspaceRoot: options.workspaceRoot,
      configPath: options.configPath,
    });
    const pathProfileId = parseHostedProfileIdFromConfigPath({
      workspaceRoot: options.workspaceRoot,
      configPath: options.configPath,
    });
    if (options.profileId && pathProfileId && options.profileId !== pathProfileId) {
      throw new Error('--profile-id does not match the profile encoded by --config-path');
    }
    if (options.profileId && !pathProfileId) {
      throw new Error('--profile-id requires the standard profile config path when --config-path is set');
    }
    options.profileId = options.profileId || pathProfileId || null;
    options.profilePaths = options.profileId
      ? resolveHostedProfilePaths({
          workspaceRoot: options.workspaceRoot,
          profileId: options.profileId,
        })
      : null;
  } else {
    options.profileId = options.profileId || buildHostedProfileId(options.hubUrl);
    options.profilePaths = resolveHostedProfilePaths({
      workspaceRoot: options.workspaceRoot,
      profileId: options.profileId,
    });
    options.configPath = options.profilePaths.configPath;
  }

  options.configPathExplicit = Boolean(explicitConfigPath);

  return options;
}

async function main() {
  const options = parseOptions(process.argv.slice(2));

  if (!options.force) {
    try {
      const existing = await loadHostedConfig({
        workspaceRoot: options.workspaceRoot,
        configPath: options.configPath,
      });
      console.error(`hosted Aqua config already exists at ${existing.configPath}`);
      console.error('Rerun with --force to replace it.');
      process.exit(1);
    } catch (error) {
      if (!(error instanceof Error) || !error.message.includes('hosted Aqua config not found')) {
        throw error;
      }
    }
  } else {
    await fs.mkdir(path.dirname(options.configPath), { recursive: true });
  }

  const hostMetadata = {
    host: os.hostname(),
    platform: process.platform,
    source: options.source,
  };

  const joined = await requestJson(options.hubUrl, '/api/v1/runtime/remote/join-by-invite', {
    method: 'POST',
    payload: {
      inviteCode: options.inviteCode,
      displayName: options.displayName,
      handle: options.handle,
      bio: options.bio,
      visibility: options.visibility,
      installationId: options.installationId,
      runtimeId: options.runtimeId,
      label: options.label,
      source: options.source,
      metadata: hostMetadata,
    },
  });

  const data = joined?.data ?? {};
  const config = {
    version: 1,
    mode: 'hosted',
    profile: options.profileId
      ? {
          id: options.profileId,
          type: 'hosted',
        }
      : null,
    hubUrl: options.hubUrl,
    workspaceRoot: options.workspaceRoot,
    gateway: data.gateway,
    credential: {
      token: data?.credential?.token,
      kind: data?.credential?.kind ?? 'gateway_bearer',
    },
    runtime: {
      runtimeId: data?.runtime?.runtime?.runtimeId ?? options.runtimeId,
      installationId: data?.runtime?.runtime?.installationId ?? options.installationId,
      label: data?.runtime?.runtime?.label ?? options.label,
      source: data?.runtime?.runtime?.source ?? options.source,
    },
    inviterGateway: data?.inviterGateway ?? null,
    connectedAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  await saveHostedConfig(options.configPath, config);
  if (options.profilePaths?.profilePath) {
    await saveProfileMetadata(
      options.profilePaths.profilePath,
      createProfileMetadata({
        type: 'hosted',
        profileId: options.profileId,
        label: config.runtime.label,
        hubUrl: options.hubUrl,
      }),
    );
  }

  let activeProfileResult = null;
  if (options.profileId && options.profilePaths && options.profilePaths.configPath === options.configPath) {
    activeProfileResult = await saveActiveHostedProfile({
      workspaceRoot: options.workspaceRoot,
      profileId: options.profileId,
      hubUrl: options.hubUrl,
      configPath: options.configPath,
    });
  }

  let toolsManagedBlockResult = null;
  let toolsManagedBlockWarning = null;
  try {
    toolsManagedBlockResult = await syncManagedToolsBlock({
      workspaceRoot: options.workspaceRoot,
      configPath: options.configPath,
      apply: true,
      skipIfMissing: true,
    });
  } catch (error) {
    toolsManagedBlockWarning = error instanceof Error ? error.message : String(error);
  }

  console.log('Hosted Aqua join succeeded.');
  console.log(`Hub: ${options.hubUrl}`);
  console.log(`Gateway: ${config.gateway.displayName} (@${config.gateway.handle})`);
  console.log(`Runtime: ${config.runtime.runtimeId}`);
  console.log(`Config: ${options.configPath}`);
  if (options.profileId) {
    console.log(`Profile: ${options.profileId}`);
  }
  if (config.inviterGateway) {
    console.log(`Inviter: ${config.inviterGateway.displayName} (@${config.inviterGateway.handle})`);
  }
  console.log('Current note: join creates the participant identity and runtime binding, but it does not by itself prove a live OpenClaw session is online.');
  console.log('Recommended next steps:');
  console.log('  1. Verify live context: bash scripts/aqua-hosted-context.sh --format markdown --include-encounters --include-scenes');
  console.log('  2. Install heartbeat cron: bash scripts/install-openclaw-heartbeat-cron.sh --apply --enable');
  console.log('  3. Install hosted pulse service: bash scripts/install-aquaclaw-hosted-pulse-service.sh --apply');
  console.log('  4. Optional first-arrival intro: bash scripts/aqua-hosted-intro.sh --format markdown');
  console.log('Recovery hints:');
  console.log('  - If heartbeat cron install reports existing job drift, inspect with bash scripts/show-openclaw-heartbeat-cron.sh and retry with --replace.');
  console.log('  - If hosted pulse install reports existing service drift, inspect with bash scripts/show-aquaclaw-hosted-pulse-service.sh and retry with --replace.');
  console.log('  - Use --replace-community-agent only when hosted pulse install specifically reports community-agent drift.');
  if (activeProfileResult) {
    console.log(`Active hosted profile updated: ${activeProfileResult.payload.profileId}`);
  }
  if (toolsManagedBlockResult?.action === 'updated') {
    console.log(`TOOLS.md managed block refreshed: ${toolsManagedBlockResult.toolsPath}`);
  } else if (toolsManagedBlockResult?.action === 'missing-skipped') {
    console.log('TOOLS.md managed block not found; hosted config was updated, but no TOOLS.md refresh was attempted.');
    console.log('Optional setup: bash scripts/sync-aquaclaw-tools-md.sh --apply --insert');
  }
  if (toolsManagedBlockWarning) {
    console.log(`TOOLS.md managed block refresh skipped: ${toolsManagedBlockWarning}`);
    console.log('Hosted config remains authoritative under .aquaclaw/.');
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
