#!/usr/bin/env node
/**
 * API key recovery script (for AI / no config)
 * Reads wallet from config (via wallet.js), constructs a recovery message locally,
 * signs it, and sends { walletAddress, signature } in a single POST to /v1/agents/recover.
 * Saves API_DOMAIN, AGENT_NAME, EVM_ADDRESS, CLAW_FRIEND_API_KEY to openclaw.json.
 */

import { checkDependencies } from './check-dependencies.js';
checkDependencies(['ethers']);

import { ethers } from 'ethers';
import {
  apiRequest,
  updateClawFriendConfig,
  getEnv,
  success,
  error,
  info,
  prettyJson
} from './utils.js';

/**
 * Recover API key with a single POST: { walletAddress, signature }
 * Client constructs the message locally: "Recover my agent on ClawFriend: <walletAddress>"
 * @param {string} walletAddress - Lowercase wallet address
 * @param {string} signature - Hex signature from wallet.signMessage
 * @returns {Promise<{ api_key: string, agent: { id, username, displayName, status, walletAddress } }>}
 */
async function recoverAgent(apiDomain, walletAddress, signature) {
  const domain = apiDomain.replace(/\/$/, '');
  const url = `${domain}/v1/agents/recover`;

  const headers = {
    'Content-Type': 'application/json',
  };

  const response = await fetch(url, {
    method: 'POST',
    body: JSON.stringify({ walletAddress, signature }),
    headers
  });

  if (!response.ok) {
    const err = new Error(`API request failed: ${response.status} ${response.statusText}`);
    err.status = response.status;
    try {
      err.data = await response.json();
    } catch (e) {
      // ignore
    }
    throw err;
  }

  let result;
  try {
    const json = await response.json();
    result = json.data || json;
  } catch (e) {
    throw new Error('Invalid JSON response');
  }

  if (!result.api_key) {
    throw new Error('Server did not return api_key');
  }
  return result;
}

/**
 * Full recover flow: wallet from config → sign → recover → save env to openclaw.json
 * @param {string} apiDomain - API base URL (from argv or config)
 */
async function runRecovery(apiDomain, address, signature) {
  if (!apiDomain || !signature || !address) {
    error('Missing required parameters: apiDomain, signature, address');
    throw new Error('Missing required parameters');
  }
  try {
    info('Recovering agent key...');

    const response = await recoverAgent(apiDomain, address, signature);

    const agent = response.agent || {};
    const AGENT_NAME = (agent.displayName != null && agent.displayName !== '')
      ? agent.displayName
      : (agent.username || 'Agent');

    updateClawFriendConfig({
      apiKey: response.api_key,
      env: {
        API_DOMAIN: apiDomain,
        AGENT_NAME,
        EVM_ADDRESS: address,
        CLAW_FRIEND_API_KEY: response.api_key
      }
    });

    success('Recovery successful! Config saved to openclaw.json.');
    info(`Agent: ${AGENT_NAME} (${address})`);
    info('Store your config securely. You can use the agent with the new key immediately.');
  } catch (e) {
    if (e.status === 400 && e.data?.message) {
      error(`Recovery failed: ${e.data.message}`);
    } else if (e.message) {
      error(`Recovery failed: ${e.message}`);
    }
    if (e.data && !e.data.message) {
      console.log('\nError details:', prettyJson(e.data));
    }
    throw e;
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  // Parse args: node scripts/recover.js [API_DOMAIN] [address] [signature] 
  const args = process.argv.slice(2);
  const apiDomain = args[0];
  const address = args[1];
  const signature = args[2];

  runRecovery(apiDomain, address, signature).catch(() => process.exit(1));
}
