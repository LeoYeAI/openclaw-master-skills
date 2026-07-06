/**
 * Auto-setup for ClawSend.
 *
 * Automatically creates vault and registers with the production relay on first use.
 */

import { randomUUID } from 'crypto';
import { Vault } from './vault.js';
import { RelayClient, ClientError, DEFAULT_RELAY } from './client.js';
import * as crypto from './crypto.js';

/**
 * Generate a random alias for auto-setup.
 */
export function generateAlias() {
  return `agent-${randomUUID().replace(/-/g, '').slice(0, 8)}`;
}

/**
 * Automatically set up ClawSend on first use.
 *
 * Creates vault and registers with relay if needed.
 */
export async function autoSetup({
  vaultDir = null,
  server = DEFAULT_RELAY,
  alias = null,
  quiet = false,
} = {}) {
  const vault = vaultDir ? new Vault(vaultDir) : new Vault();

  // Step 1: Create vault if it doesn't exist
  if (!vault.exists) {
    if (!quiet) {
      console.error('First time setup: Creating identity...');
    }

    // Generate alias if not provided
    if (!alias) {
      alias = generateAlias();
    }

    const identity = vault.create(alias);

    if (!quiet) {
      console.error(`  Vault ID: ${identity.vault_id}`);
      console.error(`  Alias: ${alias}`);
    }
  } else {
    // Load existing vault
    try {
      vault.load();
    } catch (e) {
      if (!quiet) {
        console.error(`Warning: Could not load vault: ${e.message}`);
        console.error('Continuing with limited functionality...');
      }
      return vault;
    }
  }

  // Step 2: Register with relay if not already registered
  if (!vault.isRegistered(server)) {
    if (!quiet) {
      console.error(`Registering with ${server}...`);
    }

    try {
      const client = new RelayClient(vault, server);

      // Get challenge
      const challengeResponse = await client.getChallenge();
      const challenge = challengeResponse.challenge;

      // Sign challenge
      const signature = crypto.signChallenge(vault.getSigningPrivateKey(), challenge);

      // Complete registration
      const result = await client.register(challenge, signature, vault.alias);

      // Save registration state
      vault.setServerState(server, {
        registered: true,
        registered_at: result.registered_at,
        alias: result.alias,
      });

      if (!quiet) {
        console.error(`  Registered as: ${result.alias || vault.vaultId}`);
      }
    } catch (e) {
      if (e instanceof ClientError && e.response?.code === 'already_registered') {
        // Mark as registered
        vault.setServerState(server, { registered: true });
        if (!quiet) {
          console.error('  Already registered');
        }
      } else {
        throw e;
      }
    }
  }

  return vault;
}

/**
 * Ensure ClawSend is ready to use.
 */
export async function ensureReady({
  vaultDir = null,
  server = DEFAULT_RELAY,
  jsonMode = false,
} = {}) {
  return autoSetup({
    vaultDir,
    server,
    quiet: jsonMode,
  });
}

export { DEFAULT_RELAY };
