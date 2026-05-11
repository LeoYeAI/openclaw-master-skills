#!/usr/bin/env node

import { execFile } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

import {
  HostedPulseAuthoringError,
  ensureCommunityVoiceGuide,
  resolveOpenClawBinary,
  syncCommunityAgentWorkspace,
} from './aqua-hosted-pulse.mjs';
import { parseArgValue, resolveWorkspaceRoot } from './hosted-aqua-common.mjs';

const execFileAsync = promisify(execFile);
const DEFAULT_AGENT_ID = 'community';

function printHelp() {
  console.log(`Usage: ensure-aquaclaw-community-agent.mjs [options]

Ensure the hosted Aqua community authoring agent exists and points at this workspace's derived community lane.

Options:
  --workspace-root <path>    OpenClaw workspace root
  --openclaw-bin <path>      Explicit openclaw binary
  --agent-id <id>            Agent id to provision (default: ${DEFAULT_AGENT_ID})
  --model <id>               Optional model to set when creating the agent
  --replace                  Replace an existing mismatched agent with the same id
  --json                     Output JSON summary
  --help                     Show this message
`);
}

function trimToNull(value) {
  if (typeof value !== 'string') {
    return null;
  }
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function normalizePathForComparison(filePath) {
  return path.resolve(filePath);
}

function parseOptions(argv) {
  const options = {
    agentId: trimToNull(process.env.AQUACLAW_HOSTED_PULSE_COMMUNITY_AGENT_ID) ?? DEFAULT_AGENT_ID,
    format: 'text',
    model: trimToNull(process.env.AQUACLAW_HOSTED_PULSE_COMMUNITY_MODEL),
    openclawBin: trimToNull(process.env.OPENCLAW_BIN),
    replace: false,
    workspaceRoot: resolveWorkspaceRoot(process.env.OPENCLAW_WORKSPACE_ROOT),
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--replace') {
      options.replace = true;
      continue;
    }
    if (arg === '--json') {
      options.format = 'json';
      continue;
    }
    if (arg.startsWith('--workspace-root')) {
      options.workspaceRoot = resolveWorkspaceRoot(parseArgValue(argv, index, arg, '--workspace-root'));
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--openclaw-bin')) {
      options.openclawBin = parseArgValue(argv, index, arg, '--openclaw-bin').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--agent-id')) {
      options.agentId = parseArgValue(argv, index, arg, '--agent-id').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--model')) {
      options.model = parseArgValue(argv, index, arg, '--model').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }

    throw new Error(`unknown option: ${arg}`);
  }

  if (!options.agentId) {
    throw new Error('--agent-id must not be empty');
  }

  return options;
}

async function listOpenClawAgents({ openclawBin, workspaceRoot, env }) {
  const { stdout } = await execFileAsync(openclawBin, ['agents', 'list', '--json'], {
    cwd: workspaceRoot,
    env,
    maxBuffer: 1024 * 1024,
  });
  const agents = JSON.parse(stdout);
  if (!Array.isArray(agents)) {
    throw new Error('openclaw agents list returned non-array JSON');
  }
  return agents;
}

async function addOpenClawAgent({ openclawBin, workspaceRoot, agentId, communityWorkspace, model, env }) {
  const args = ['agents', 'add', agentId, '--workspace', communityWorkspace, '--non-interactive', '--json'];
  if (model) {
    args.push('--model', model);
  }
  await execFileAsync(openclawBin, args, {
    cwd: workspaceRoot,
    env,
    maxBuffer: 1024 * 1024,
  });
}

async function deleteOpenClawAgent({ openclawBin, workspaceRoot, agentId, env }) {
  await execFileAsync(openclawBin, ['agents', 'delete', agentId, '--force', '--json'], {
    cwd: workspaceRoot,
    env,
    maxBuffer: 1024 * 1024,
  });
}

async function syncOpenClawAgentIdentity({ openclawBin, workspaceRoot, agentId, communityWorkspace, env }) {
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

function renderText(result) {
  const lines = [
    `ready: ${result.ready ? 'yes' : 'no'}`,
    `agent: ${result.agentId}`,
    `action: ${result.action ?? 'failed'}`,
    result.openclawBin ? `openclaw bin: ${result.openclawBin}${result.openclawBinSource ? ` [${result.openclawBinSource}]` : ''}` : null,
    result.communityWorkspace ? `community workspace: ${result.communityWorkspace}` : null,
    result.workspaceRoot ? `workspace root: ${result.workspaceRoot}` : null,
    result.errorCode ? `error code: ${result.errorCode}` : null,
    result.errorMessage ? `error: ${result.errorMessage}` : null,
  ].filter(Boolean);

  if (Array.isArray(result.warnings) && result.warnings.length > 0) {
    lines.push(`warnings: ${result.warnings.join(' | ')}`);
  }
  return lines.join('\n');
}

async function ensureCommunityAgent(options) {
  const env = {
    ...process.env,
    ...(options.openclawBin ? { OPENCLAW_BIN: options.openclawBin } : {}),
  };
  const binary = await resolveOpenClawBinary({ env });
  const communityVoiceGuide = await ensureCommunityVoiceGuide({
    workspaceRoot: options.workspaceRoot,
  });
  const communityWorkspace = await syncCommunityAgentWorkspace({
    workspaceRoot: options.workspaceRoot,
    communityVoiceGuide,
  });
  const agents = await listOpenClawAgents({
    openclawBin: binary.binPath,
    workspaceRoot: options.workspaceRoot,
    env,
  });

  const existing = agents.find((item) => item?.id === options.agentId) ?? null;
  let action = 'validated';
  const warnings = [];

  if (existing) {
    const actualWorkspace = trimToNull(existing.workspace);
    const matches =
      actualWorkspace !== null &&
      normalizePathForComparison(actualWorkspace) === normalizePathForComparison(communityWorkspace);
    if (!matches) {
      if (!options.replace) {
        throw new HostedPulseAuthoringError(
          'community_agent_workspace_mismatch',
          `agent ${options.agentId} already exists at ${actualWorkspace ?? 'an unknown workspace'} instead of ${communityWorkspace}`,
          {
            agentId: options.agentId,
            openclawBin: binary.binPath,
            openclawBinSource: binary.source,
          },
        );
      }
      await deleteOpenClawAgent({
        openclawBin: binary.binPath,
        workspaceRoot: options.workspaceRoot,
        agentId: options.agentId,
        env,
      });
      await addOpenClawAgent({
        openclawBin: binary.binPath,
        workspaceRoot: options.workspaceRoot,
        agentId: options.agentId,
        communityWorkspace,
        model: options.model,
        env,
      });
      action = 'replaced';
      warnings.push(`replaced mismatched agent ${options.agentId}`);
    }
  } else {
    await addOpenClawAgent({
      openclawBin: binary.binPath,
      workspaceRoot: options.workspaceRoot,
      agentId: options.agentId,
      communityWorkspace,
      model: options.model,
      env,
    });
    action = 'created';
  }

  await syncOpenClawAgentIdentity({
    openclawBin: binary.binPath,
    workspaceRoot: options.workspaceRoot,
    agentId: options.agentId,
    communityWorkspace,
    env,
  });

  return {
    ready: true,
    action,
    agentId: options.agentId,
    communityWorkspace,
    openclawBin: binary.binPath,
    openclawBinSource: binary.source,
    warnings,
    workspaceRoot: options.workspaceRoot,
  };
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  try {
    const result = await ensureCommunityAgent(options);
    if (options.format === 'json') {
      console.log(JSON.stringify(result, null, 2));
      return;
    }
    console.log(renderText(result));
  } catch (error) {
    const result = {
      ready: false,
      action: null,
      agentId: options.agentId,
      communityWorkspace: path.resolve(options.workspaceRoot, '.openclaw', 'community-agent-workspace'),
      openclawBin: error?.details?.openclawBin ?? null,
      openclawBinSource: error?.details?.openclawBinSource ?? null,
      warnings: Array.isArray(error?.details?.warnings) ? error.details.warnings : [],
      workspaceRoot: options.workspaceRoot,
      errorCode: error instanceof HostedPulseAuthoringError ? error.code : 'community_agent_setup_failed',
      errorMessage: error instanceof Error ? error.message : String(error),
    };
    if (options.format === 'json') {
      console.log(JSON.stringify(result, null, 2));
    } else {
      console.error(renderText(result));
    }
    process.exit(1);
  }
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (isMain) {
  await main();
}
