#!/usr/bin/env node

import { access, cp, mkdir } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

import {
  DEFAULT_COMMUNITY_MEMORY_DIR_NAME,
  DEFAULT_HEARTBEAT_STATE_FILE_NAME,
  DEFAULT_LOCAL_PROFILE_ID,
  DEFAULT_MIRROR_DIR_NAME,
  createProfileMetadata,
  formatTimestamp,
  loadActiveProfileSync,
  parseArgValue,
  resolveAquaclawStateRoot,
  resolveHostedProfilePaths,
  resolveWorkspaceRoot,
  saveActiveLocalProfile,
  saveProfileMetadata,
} from './hosted-aqua-common.mjs';

const DIARY_DIGESTS_DIR_NAME = 'diary-digests';
const MEMORY_SYNTHESIS_DIR_NAME = 'memory-synthesis';
const SEA_DIARY_CONTEXT_DIR_NAME = 'sea-diary-context';
const VALID_FORMATS = new Set(['json', 'markdown']);

function printHelp() {
  console.log(`Usage: aqua-local-profile.mjs <command> [options]

Commands:
  show                         Show the current local-profile selection state
  activate                     Activate a named local profile
  migrate-root                 Copy root-level local state into a named local profile and activate it

Options:
  --workspace-root <path>      OpenClaw workspace root
  --profile-id <id>            Local profile id (default: ${DEFAULT_LOCAL_PROFILE_ID})
  --label <text>               Optional human-readable label
  --format <fmt>               json|markdown (default: markdown)
  --force                      Overwrite existing migration targets
  --help                       Show this message
`);
}

export function parseOptions(argv) {
  if (argv.length === 0) {
    printHelp();
    process.exit(1);
  }

  const command = argv[0];
  if (!['show', 'activate', 'migrate-root'].includes(command)) {
    throw new Error(`unknown command: ${command}`);
  }

  const options = {
    command,
    force: false,
    format: 'markdown',
    label: null,
    profileId: DEFAULT_LOCAL_PROFILE_ID,
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT ?? null,
  };

  for (let index = 1; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--help') {
      printHelp();
      process.exit(0);
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
    if (arg.startsWith('--profile-id')) {
      options.profileId = parseArgValue(argv, index, arg, '--profile-id').trim();
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
    if (arg.startsWith('--format')) {
      options.format = parseArgValue(argv, index, arg, '--format').trim().toLowerCase();
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
  if (typeof options.profileId !== 'string' || !options.profileId.trim()) {
    throw new Error('--profile-id must not be empty');
  }

  options.workspaceRoot = resolveWorkspaceRoot(options.workspaceRoot);
  return options;
}

function buildRootLocalPaths(workspaceRoot) {
  const stateRoot = resolveAquaclawStateRoot(workspaceRoot);
  return {
    stateRoot,
    mirrorRoot: path.join(stateRoot, DEFAULT_MIRROR_DIR_NAME),
    communityMemoryRoot: path.join(stateRoot, DEFAULT_COMMUNITY_MEMORY_DIR_NAME),
    heartbeatStatePath: path.join(stateRoot, DEFAULT_HEARTBEAT_STATE_FILE_NAME),
    diaryDigestRoot: path.join(stateRoot, DIARY_DIGESTS_DIR_NAME),
    memorySynthesisRoot: path.join(stateRoot, MEMORY_SYNTHESIS_DIR_NAME),
    seaDiaryContextRoot: path.join(stateRoot, SEA_DIARY_CONTEXT_DIR_NAME),
  };
}

async function pathExists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function copyIfPresent(sourcePath, targetPath, { force, label }) {
  if (!(await pathExists(sourcePath))) {
    return {
      copied: false,
      label,
      sourcePath,
      targetPath,
    };
  }

  await mkdir(path.dirname(targetPath), { recursive: true });
  await cp(sourcePath, targetPath, {
    recursive: true,
    force,
    errorOnExist: !force,
  });
  return {
    copied: true,
    label,
    sourcePath,
    targetPath,
  };
}

export async function showLocalProfileStatus({ workspaceRoot }) {
  const active = loadActiveProfileSync({ workspaceRoot });
  const rootLocalPaths = buildRootLocalPaths(workspaceRoot);
  const activeLocalProfileId = active.pointer?.type === 'local' ? active.pointer.profileId : null;
  const activeLocalPaths = activeLocalProfileId
    ? resolveHostedProfilePaths({
        workspaceRoot,
        profileId: activeLocalProfileId,
      })
    : null;

  return {
    workspaceRoot,
    activeProfilePath: active.pointerPath,
    activePointer: active.pointer,
    activeLocalProfileId,
    activeLocalPaths,
    rootLocalPaths,
  };
}

export async function activateLocalProfile({
  workspaceRoot,
  profileId = DEFAULT_LOCAL_PROFILE_ID,
  label = null,
} = {}) {
  const profilePaths = resolveHostedProfilePaths({
    workspaceRoot,
    profileId,
  });
  await mkdir(profilePaths.profileRoot, { recursive: true });
  const metadata = createProfileMetadata({
    type: 'local',
    profileId,
    label,
  });
  await saveProfileMetadata(profilePaths.profilePath, metadata);
  const active = await saveActiveLocalProfile({
    workspaceRoot,
    profileId,
  });

  return {
    workspaceRoot,
    profileId,
    profilePaths,
    metadata,
    activeProfile: active,
  };
}

export async function migrateRootLocalState({
  workspaceRoot,
  profileId = DEFAULT_LOCAL_PROFILE_ID,
  label = null,
  force = false,
} = {}) {
  const rootLocalPaths = buildRootLocalPaths(workspaceRoot);
  const profilePaths = resolveHostedProfilePaths({
    workspaceRoot,
    profileId,
  });

  await mkdir(profilePaths.profileRoot, { recursive: true });
  const metadata = createProfileMetadata({
    type: 'local',
    profileId,
    label,
  });
  await saveProfileMetadata(profilePaths.profilePath, metadata);

  const copiedMirror = await copyIfPresent(rootLocalPaths.mirrorRoot, profilePaths.mirrorRoot, {
    force,
    label: 'root local mirror',
  });
  const copiedCommunityMemory = await copyIfPresent(
    rootLocalPaths.communityMemoryRoot,
    profilePaths.communityMemoryRoot,
    {
      force,
      label: 'root local community-memory',
    },
  );
  const copiedHeartbeat = await copyIfPresent(
    rootLocalPaths.heartbeatStatePath,
    profilePaths.heartbeatStatePath,
    {
      force,
      label: 'root local heartbeat state',
    },
  );
  const copiedDiaryDigests = await copyIfPresent(rootLocalPaths.diaryDigestRoot, path.join(profilePaths.profileRoot, DIARY_DIGESTS_DIR_NAME), {
    force,
    label: 'root local diary digests',
  });
  const copiedMemorySynthesis = await copyIfPresent(
    rootLocalPaths.memorySynthesisRoot,
    path.join(profilePaths.profileRoot, MEMORY_SYNTHESIS_DIR_NAME),
    {
      force,
      label: 'root local memory synthesis',
    },
  );
  const copiedSeaDiaryContext = await copyIfPresent(
    rootLocalPaths.seaDiaryContextRoot,
    path.join(profilePaths.profileRoot, SEA_DIARY_CONTEXT_DIR_NAME),
    {
      force,
      label: 'root local sea diary context',
    },
  );

  const activeProfile = await saveActiveLocalProfile({
    workspaceRoot,
    profileId,
  });

  return {
    workspaceRoot,
    profileId,
    profilePaths,
    metadata,
    activeProfile,
    copied: {
      mirrorRoot: copiedMirror.copied,
      communityMemoryRoot: copiedCommunityMemory.copied,
      heartbeatStatePath: copiedHeartbeat.copied,
      diaryDigestRoot: copiedDiaryDigests.copied,
      memorySynthesisRoot: copiedMemorySynthesis.copied,
      seaDiaryContextRoot: copiedSeaDiaryContext.copied,
    },
  };
}

function formatMarkdown(result) {
  if (result.command === 'show') {
    return [
      'Local profile selection.',
      `- Workspace: ${result.workspaceRoot}`,
      `- Active profile pointer: ${result.activeProfilePath}`,
      `- Active pointer type: ${result.activePointer?.type ?? 'none'}`,
      `- Active pointer id: ${result.activePointer?.profileId ?? 'none'}`,
      `- Active local profile: ${result.activeLocalProfileId ?? 'none'}`,
      `- Root local mirror: ${result.rootLocalPaths.mirrorRoot}`,
      `- Root local heartbeat: ${result.rootLocalPaths.heartbeatStatePath}`,
      result.activeLocalPaths ? `- Active local mirror: ${result.activeLocalPaths.mirrorRoot}` : null,
      result.activeLocalPaths ? `- Active local heartbeat: ${result.activeLocalPaths.heartbeatStatePath}` : null,
      result.activeLocalPaths ? `- Active local community-memory: ${result.activeLocalPaths.communityMemoryRoot}` : null,
    ]
      .filter(Boolean)
      .join('\n');
  }

  if (result.command === 'activate') {
    return [
      'Local profile activated.',
      `- Workspace: ${result.workspaceRoot}`,
      `- Profile: ${result.profileId}`,
      `- Label: ${result.metadata.label ?? 'n/a'}`,
      `- Profile file: ${result.profilePaths.profilePath}`,
      `- Mirror root: ${result.profilePaths.mirrorRoot}`,
      `- Heartbeat state: ${result.profilePaths.heartbeatStatePath}`,
      `- Community memory: ${result.profilePaths.communityMemoryRoot}`,
      `- Active pointer updated: ${formatTimestamp(result.activeProfile.payload.updatedAt)}`,
    ].join('\n');
  }

  return [
    'Root local state migrated into a named local profile.',
    `- Workspace: ${result.workspaceRoot}`,
    `- Profile: ${result.profileId}`,
    `- Profile file: ${result.profilePaths.profilePath}`,
    `- Copied root local mirror: ${result.copied.mirrorRoot ? 'yes' : 'no'}`,
    `- Copied root local community-memory: ${result.copied.communityMemoryRoot ? 'yes' : 'no'}`,
    `- Copied root local heartbeat state: ${result.copied.heartbeatStatePath ? 'yes' : 'no'}`,
    `- Copied root local diary digests: ${result.copied.diaryDigestRoot ? 'yes' : 'no'}`,
    `- Copied root local memory synthesis: ${result.copied.memorySynthesisRoot ? 'yes' : 'no'}`,
    `- Copied root local sea diary context: ${result.copied.seaDiaryContextRoot ? 'yes' : 'no'}`,
    `- Active pointer updated: ${formatTimestamp(result.activeProfile.payload.updatedAt)}`,
  ].join('\n');
}

async function runCommand(options) {
  if (options.command === 'show') {
    return {
      command: 'show',
      ...(await showLocalProfileStatus({
        workspaceRoot: options.workspaceRoot,
      })),
    };
  }

  if (options.command === 'activate') {
    return {
      command: 'activate',
      ...(await activateLocalProfile({
        workspaceRoot: options.workspaceRoot,
        profileId: options.profileId,
        label: options.label,
      })),
    };
  }

  return {
    command: 'migrate-root',
    ...(await migrateRootLocalState({
      workspaceRoot: options.workspaceRoot,
      profileId: options.profileId,
      label: options.label,
      force: options.force,
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

export { formatMarkdown, runCommand };

if (!process.argv.includes('--test') && process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
