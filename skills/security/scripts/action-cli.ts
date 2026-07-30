#!/usr/bin/env node

/**
 * GoPlus AgentGuard Action CLI — lightweight wrapper for ActionScanner operations.
 *
 * Usage:
 *   node action-cli.ts decide --type <action_type> [action-specific args]
 *   node action-cli.ts simulate --chain-id <id> --from <addr> --to <addr> --value <wei> [--data <hex>] [--origin <url>]
 *
 * Action-specific args for `decide`:
 *
 *   web3_tx:
 *     --chain-id <id> --from <addr> --to <addr> --value <wei> [--data <hex>] [--origin <url>] [--user-present]
 *
 *   web3_sign:
 *     --chain-id <id> --signer <addr> [--message <msg>] [--typed-data <json>] [--origin <url>] [--user-present]
 *
 *   exec_command:
 *     --command <cmd> [--args <json_array>] [--cwd <dir>]
 *
 *   network_request:
 *     --method <GET|POST|PUT|DELETE|PATCH> --url <url> [--body <text>] [--user-present]
 *
 *   secret_access:
 *     --secret-name <name> --access-type <read|write>
 *
 *   read_file / write_file:
 *     --path <filepath>
 */

import { createAgentGuard } from '@goplus/agentguard';
import type {
  ActionEnvelope,
  Web3Intent,
  ActionType,
} from '@goplus/agentguard';

const args = process.argv.slice(2);
const command = args[0];

function getArg(name: string): string | undefined {
  const idx = args.indexOf(`--${name}`);
  if (idx === -1 || idx + 1 >= args.length) return undefined;
  return args[idx + 1];
}

function hasFlag(name: string): boolean {
  return args.includes(`--${name}`);
}

function printUsage(): void {
  console.error(`Usage: action-cli.ts <decide|simulate> [options]

Commands:
  decide    Evaluate an action and return a policy decision
  simulate  Run GoPlus transaction simulation only

decide options:
  --type <type>        Action type: web3_tx, web3_sign, exec_command,
                       network_request, secret_access, read_file, write_file

  For web3_tx:
    --chain-id <id>    Chain ID (required)
    --from <addr>      Sender address (required)
    --to <addr>        Target address (required)
    --value <wei>      Value in wei (required)
    --data <hex>       Calldata (optional)
    --origin <url>     Origin URL (optional)
    --user-present     User is actively watching (optional flag)

  For web3_sign:
    --chain-id <id>    Chain ID (required)
    --signer <addr>    Signer address (required)
    --message <msg>    Message to sign (optional)
    --typed-data <json> EIP-712 typed data JSON (optional)
    --origin <url>     Origin URL (optional)
    --user-present     User is actively watching (optional flag)

  For exec_command:
    --command <cmd>    Command string (required)
    --args <json>      Arguments as JSON array (optional)
    --cwd <dir>        Working directory (optional)

  For network_request:
    --method <method>  HTTP method (required)
    --url <url>        Request URL (required)
    --body <text>      Request body preview (optional)
    --user-present     User is actively watching (optional flag)

  For secret_access:
    --secret-name <n>  Secret name (required)
    --access-type <t>  read or write (required)

  For read_file / write_file:
    --path <filepath>  File path (required)

simulate options:
  --chain-id <id>      Chain ID (required)
  --from <addr>        Sender address (required)
  --to <addr>          Target address (required)
  --value <wei>        Value in wei (required)
  --data <hex>         Calldata (optional)
  --origin <url>       Origin URL (optional)`);
  process.exit(1);
}

function buildEnvelope(): ActionEnvelope {
  const type = getArg('type') as ActionType;
  if (!type) {
    console.error('Error: --type is required for decide');
    printUsage();
    process.exit(1);
  }

  const userPresent = hasFlag('user-present');
  let data: Record<string, unknown>;

  switch (type) {
    case 'web3_tx':
      data = {
        chain_id: Number(getArg('chain-id') || '1'),
        from: getArg('from') || '',
        to: getArg('to') || '',
        value: getArg('value') || '0',
        data: getArg('data'),
        origin: getArg('origin'),
      };
      break;

    case 'web3_sign':
      data = {
        chain_id: Number(getArg('chain-id') || '1'),
        signer: getArg('signer') || '',
        message: getArg('message'),
        typed_data: getArg('typed-data')
          ? JSON.parse(getArg('typed-data')!)
          : undefined,
        origin: getArg('origin'),
      };
      break;

    case 'exec_command':
      data = {
        command: getArg('command') || '',
        args: getArg('args') ? JSON.parse(getArg('args')!) : undefined,
        cwd: getArg('cwd'),
      };
      break;

    case 'network_request':
      data = {
        method: (getArg('method') || 'GET').toUpperCase(),
        url: getArg('url') || '',
        body_preview: getArg('body'),
      };
      break;

    case 'secret_access':
      data = {
        secret_name: getArg('secret-name') || '',
        access_type: getArg('access-type') || 'read',
      };
      break;

    case 'read_file':
    case 'write_file':
      data = {
        path: getArg('path') || '',
      };
      break;

    default:
      console.error(`Error: unknown action type '${type}'`);
      printUsage();
      process.exit(1);
  }

  return {
    actor: {
      skill: {
        id: getArg('skill-id') || 'unknown',
        source: getArg('skill-source') || 'cli',
        version_ref: getArg('skill-version') || '0.0.0',
        artifact_hash: getArg('skill-hash') || '',
      },
    },
    action: {
      type,
      data: data as any,
    },
    context: {
      session_id: `cli-${Date.now()}`,
      user_present: userPresent,
      env: 'prod',
      time: new Date().toISOString(),
    },
  };
}

async function main() {
  if (!command || command === '--help' || command === '-h') {
    printUsage();
  }

  const registryPath = getArg('registry-path');
  const { actionScanner } = createAgentGuard({ registryPath });

  switch (command) {
    case 'decide': {
      const envelope = buildEnvelope();
      const result = await actionScanner.decide(envelope);
      console.log(JSON.stringify(result, null, 2));
      break;
    }

    case 'simulate': {
      const intent: Web3Intent = {
        chain_id: Number(getArg('chain-id') || '1'),
        from: getArg('from') || '',
        to: getArg('to') || '',
        value: getArg('value') || '0',
        data: getArg('data'),
        origin: getArg('origin'),
        kind: 'tx',
      };
      const result = await actionScanner.simulateWeb3(intent);
      console.log(JSON.stringify(result, null, 2));
      break;
    }

    default:
      console.error(`Unknown command: ${command}`);
      printUsage();
  }
}

main().catch((err) => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});
