#!/usr/bin/env node
/**
 * Discover agents on the ClawHub relay.
 *
 * Usage:
 *   node discover.js --list
 *   node discover.js --resolve ALIAS
 */

import { parseArgs } from 'util';
import { ensureReady, DEFAULT_RELAY } from '../lib/auto_setup.js';
import { RelayClient, outputJson, outputError, outputHuman, ClientError } from '../lib/client.js';

const options = {
  list: { type: 'boolean', default: false },
  resolve: { type: 'string' },
  server: { type: 'string', default: DEFAULT_RELAY },
  'vault-dir': { type: 'string' },
  json: { type: 'boolean', default: false },
  help: { type: 'boolean', short: 'h', default: false },
};

async function main() {
  let args;
  try {
    args = parseArgs({ options, allowPositionals: false });
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }

  if (args.values.help) {
    console.log(`
Usage: node discover.js [options]

Options:
  --list            List all registered agents
  --resolve ALIAS   Resolve an alias to vault ID
  --server          Relay server URL
  --vault-dir       Custom vault directory
  --json            Output as JSON
  -h, --help        Show this help
`);
    process.exit(0);
  }

  const { list, resolve, server, json } = args.values;
  const vaultDir = args.values['vault-dir'];

  if (!list && !resolve) {
    if (json) {
      outputError('Must specify --list or --resolve', 'missing_argument');
    } else {
      console.error('Error: Must specify --list or --resolve');
    }
    process.exit(1);
  }

  // Auto-setup
  let vault;
  try {
    vault = await ensureReady({ vaultDir, server, jsonMode: json });
  } catch (e) {
    if (json) {
      outputError(`Setup failed: ${e.message}`, 'setup_error');
    } else {
      console.error(`Error: Setup failed: ${e.message}`);
    }
    process.exit(1);
  }

  const client = new RelayClient(vault, server);

  try {
    if (list) {
      if (!json) {
        outputHuman(`Listing agents on ${server}...`);
      }

      const result = await client.listAgents(500);
      const agents = result.agents || [];

      if (json) {
        outputJson({ agents, count: agents.length });
      } else {
        console.error(`\n${agents.length} agent(s) registered:`);
        console.error('-'.repeat(60));

        for (const agent of agents) {
          if (agent.alias) {
            console.error(`  ${agent.alias}`);
          } else {
            console.error(`  (no alias)`);
          }
          console.error(`    Vault: ${agent.vault_id}`);
          console.error(`    Registered: ${agent.registered_at}`);
          console.error('');
        }
      }
    } else if (resolve) {
      if (!json) {
        outputHuman(`Resolving alias: ${resolve}...`);
      }

      try {
        const result = await client.resolveAlias(resolve);

        if (json) {
          outputJson(result);
        } else {
          console.error(`\nFound: ${resolve}`);
          console.error(`  Vault ID: ${result.vault_id}`);
          console.error(`  Alias: ${result.alias || '(none)'}`);
          console.error(`  Signing Key: ${result.signing_public_key?.slice(0, 20)}...`);
          console.error(`  Encryption Key: ${result.encryption_public_key?.slice(0, 20)}...`);
        }
      } catch (e) {
        if (e instanceof ClientError && e.statusCode === 404) {
          if (json) {
            outputError(`Alias not found: ${resolve}`, 'not_found');
          } else {
            console.error(`Error: Alias not found: ${resolve}`);
          }
          process.exit(1);
        }
        throw e;
      }
    }
  } catch (e) {
    if (e instanceof ClientError) {
      if (json) {
        outputError(e.message, e.response?.code || 'error');
      } else {
        console.error(`Error: ${e.message}`);
      }
    } else {
      if (json) {
        outputError(e.message);
      } else {
        console.error(`Error: ${e.message}`);
      }
    }
    process.exit(1);
  }
}

main();
