#!/usr/bin/env node

import process from 'node:process';

import { parseArgValue } from './hosted-aqua-common.mjs';
import {
  loadActiveProfileSync,
  resolveActiveHostedProfilePath,
  resolveHeartbeatStatePath,
  resolveHostedConfigPath,
  resolveHostedProfilesRoot,
  resolveHostedPulseStatePath,
  resolveMirrorRootPath,
  resolveWorkspaceRoot,
} from './hosted-aqua-common.mjs';

const VALID_FIELDS = new Map([
  ['workspace-root', ({ workspaceRoot }) => workspaceRoot],
  ['hosted-config', ({ workspaceRoot, configPath }) => resolveHostedConfigPath({ workspaceRoot, configPath })],
  ['hosted-pulse-state', ({ workspaceRoot, pulseStatePath }) => resolveHostedPulseStatePath({ workspaceRoot, stateFile: pulseStatePath })],
  ['heartbeat-state', ({ workspaceRoot, heartbeatStatePath, mode }) => resolveHeartbeatStatePath({ workspaceRoot, stateFile: heartbeatStatePath, mode })],
  ['mirror-dir', ({ workspaceRoot, mirrorDir, mode }) => resolveMirrorRootPath({ workspaceRoot, mirrorDir, mode })],
  ['active-profile-path', ({ workspaceRoot }) => resolveActiveHostedProfilePath({ workspaceRoot })],
  ['profiles-root', ({ workspaceRoot }) => resolveHostedProfilesRoot({ workspaceRoot })],
  ['active-profile-id', ({ workspaceRoot }) => loadActiveProfileSync({ workspaceRoot }).pointer?.profileId ?? ''],
  ['active-profile-type', ({ workspaceRoot }) => loadActiveProfileSync({ workspaceRoot }).pointer?.type ?? ''],
]);

function printHelp() {
  console.log(`Usage: resolve-aquaclaw-paths.mjs --field <name> [options]

Options:
  --field <name>                workspace-root|hosted-config|hosted-pulse-state|heartbeat-state|mirror-dir|active-profile-path|profiles-root|active-profile-id|active-profile-type
  --workspace-root <path>       OpenClaw workspace root
  --config-path <path>          Hosted config override
  --pulse-state-path <path>     Hosted pulse state override
  --heartbeat-state-path <path> Heartbeat state override
  --mirror-dir <path>           Mirror directory override
  --mode <mode>                 auto|local|hosted (used for heartbeat-state and mirror-dir)
  --help                        Show this message
`);
}

function parseOptions(argv) {
  const options = {
    configPath: process.env.AQUACLAW_HOSTED_CONFIG ?? null,
    field: null,
    heartbeatStatePath: process.env.AQUACLAW_HEARTBEAT_STATE_FILE ?? null,
    mirrorDir: process.env.AQUACLAW_MIRROR_DIR ?? null,
    mode: process.env.AQUACLAW_HEARTBEAT_MODE ?? 'auto',
    pulseStatePath: process.env.AQUACLAW_HOSTED_PULSE_STATE ?? null,
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT ?? null,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg.startsWith('--field')) {
      options.field = parseArgValue(argv, index, arg, '--field').trim();
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
    if (arg.startsWith('--pulse-state-path')) {
      options.pulseStatePath = parseArgValue(argv, index, arg, '--pulse-state-path').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--heartbeat-state-path')) {
      options.heartbeatStatePath = parseArgValue(argv, index, arg, '--heartbeat-state-path').trim();
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
    if (arg.startsWith('--mode')) {
      options.mode = parseArgValue(argv, index, arg, '--mode').trim().toLowerCase();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }

    throw new Error(`unknown option: ${arg}`);
  }

  if (!options.field || !VALID_FIELDS.has(options.field)) {
    throw new Error(`--field must be one of: ${Array.from(VALID_FIELDS.keys()).join(', ')}`);
  }
  if (!['auto', 'local', 'hosted'].includes(options.mode)) {
    throw new Error('--mode must be auto, local, or hosted');
  }

  options.workspaceRoot = resolveWorkspaceRoot(options.workspaceRoot);
  return options;
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const value = VALID_FIELDS.get(options.field)(options);
  process.stdout.write(String(value ?? ''));
}

try {
  await main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
