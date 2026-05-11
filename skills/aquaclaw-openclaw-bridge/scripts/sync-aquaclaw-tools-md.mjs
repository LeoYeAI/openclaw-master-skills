#!/usr/bin/env node

import process from 'node:process';

import { parseArgValue } from './hosted-aqua-common.mjs';
import { syncManagedToolsBlock } from './aquaclaw-tools-md.mjs';

function printHelp() {
  console.log(`Usage: sync-aquaclaw-tools-md.mjs [options]

Preview or refresh the derived AquaClaw managed block inside TOOLS.md.

Options:
  --workspace-root <path>      OpenClaw workspace root
  --tools-path <path>          TOOLS.md path override
  --config-path <path>         Hosted Aqua config path override
  --repo-path <path>           gateway-hub repo path override
  --apply                      Write the managed block into TOOLS.md
  --insert                     Append the block if it is missing, or create TOOLS.md if absent
  --skip-if-missing            Exit cleanly without writing if the block is missing
  --help                       Show this message

Notes:
  - \`.aquaclaw/\` remains the source of truth.
  - The TOOLS.md block is only a human-readable mirror of current machine state.
  - Existing user notes outside the managed block are left untouched.
`);
}

function parseOptions(argv) {
  const options = {
    apply: false,
    configPath: process.env.AQUACLAW_HOSTED_CONFIG ?? null,
    insert: false,
    repoPath: process.env.AQUACLAW_REPO ?? null,
    skipIfMissing: false,
    toolsPath: process.env.AQUACLAW_TOOLS_PATH ?? null,
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT ?? null,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--apply') {
      options.apply = true;
      continue;
    }
    if (arg === '--insert') {
      options.insert = true;
      continue;
    }
    if (arg === '--skip-if-missing') {
      options.skipIfMissing = true;
      continue;
    }
    if (arg.startsWith('--workspace-root')) {
      options.workspaceRoot = parseArgValue(argv, index, arg, '--workspace-root').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--tools-path')) {
      options.toolsPath = parseArgValue(argv, index, arg, '--tools-path').trim();
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
    if (arg.startsWith('--repo-path')) {
      options.repoPath = parseArgValue(argv, index, arg, '--repo-path').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }

    throw new Error(`unknown option: ${arg}`);
  }

  if (options.insert && options.skipIfMissing) {
    throw new Error('--insert and --skip-if-missing cannot be used together');
  }

  return options;
}

function printPreview(result) {
  console.log(`TOOLS.md target: ${result.toolsPath}`);
  console.log(`TOOLS.md exists: ${result.toolsExists ? 'yes' : 'no'}`);
  console.log(`Managed block present: ${result.blockPresent ? 'yes' : 'no'}`);
  console.log(`Active target summary: ${result.state.activeTarget}`);
  console.log('');
  process.stdout.write(result.block);
}

function printApplySummary(result) {
  console.log(`Managed block action: ${result.action}`);
  console.log(`TOOLS.md target: ${result.toolsPath}`);
  console.log(`Active target summary: ${result.state.activeTarget}`);
  console.log('Source of truth remains .aquaclaw/ state files.');
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const result = await syncManagedToolsBlock(options);

  if (options.apply) {
    printApplySummary(result);
  } else {
    printPreview(result);
  }
}

try {
  await main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
