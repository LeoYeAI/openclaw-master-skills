#!/usr/bin/env node
/**
 * Send a message to another OpenClaw agent.
 *
 * Usage:
 *   node send.js --to RECIPIENT --intent INTENT [--body BODY] [options]
 */

import { parseArgs } from 'util';
import { ensureReady, DEFAULT_RELAY } from '../lib/auto_setup.js';
import { RelayClient, outputJson, outputError, outputHuman, ClientError } from '../lib/client.js';
import { createMessage, getSignableContent } from '../lib/envelope.js';
import * as crypto from '../lib/crypto.js';

const options = {
  to: { type: 'string', short: 't' },
  intent: { type: 'string', short: 'i' },
  body: { type: 'string', short: 'b', default: '{}' },
  type: { type: 'string', default: 'request' },
  encrypt: { type: 'boolean', short: 'e', default: false },
  ttl: { type: 'string', default: '3600' },
  'correlation-id': { type: 'string', short: 'c' },
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
Usage: node send.js --to RECIPIENT --intent INTENT [options]

Options:
  -t, --to          Recipient vault ID or alias (required)
  -i, --intent      Message intent (required)
  -b, --body        JSON body (default: {})
  --type            Message type: request or notification (default: request)
  -e, --encrypt     Encrypt the payload
  --ttl             Time-to-live in seconds (default: 3600)
  -c, --correlation-id  Link to a previous message
  --server          Relay server URL
  --vault-dir       Custom vault directory
  --json            Output as JSON
  -h, --help        Show this help
`);
    process.exit(0);
  }

  const { to, intent, body, type, encrypt, ttl, server, json } = args.values;
  const correlationId = args.values['correlation-id'];
  const vaultDir = args.values['vault-dir'];

  if (!to) {
    if (json) {
      outputError('Missing required argument: --to', 'missing_argument');
    } else {
      console.error('Error: Missing required argument: --to');
    }
    process.exit(1);
  }

  if (!intent) {
    if (json) {
      outputError('Missing required argument: --intent', 'missing_argument');
    } else {
      console.error('Error: Missing required argument: --intent');
    }
    process.exit(1);
  }

  // Parse body JSON
  let bodyData;
  try {
    bodyData = JSON.parse(body);
  } catch (e) {
    if (json) {
      outputError(`Invalid JSON body: ${e.message}`, 'invalid_json');
    } else {
      console.error(`Error: Invalid JSON body: ${e.message}`);
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
    // Resolve recipient if it's an alias
    let recipientVaultId = to;
    let recipientEncryptionKey = null;

    if (!to.startsWith('vault_')) {
      if (!json) {
        outputHuman(`Resolving alias: ${to}...`);
      }
      try {
        const resolved = await client.resolveAlias(to);
        recipientVaultId = resolved.vault_id;
        recipientEncryptionKey = resolved.encryption_public_key;
      } catch (e) {
        if (e instanceof ClientError && e.statusCode === 404) {
          if (json) {
            outputError(`Recipient not found: ${to}`, 'recipient_not_found');
          } else {
            console.error(`Error: Recipient not found: ${to}`);
          }
          process.exit(1);
        }
        throw e;
      }
    }

    if (!json) {
      outputHuman(`Sending ${intent} to ${to}...`);
    }

    // Create message
    const message = createMessage({
      sender: vault.vaultId,
      recipient: recipientVaultId,
      type,
      intent,
      body: bodyData,
      ttl: parseInt(ttl, 10),
      correlationId,
    });

    // Sign the message
    const signable = getSignableContent(message);
    const signature = vault.sign(signable);

    // Encrypt if requested
    let encryptedPayload = null;
    if (encrypt) {
      if (!recipientEncryptionKey) {
        // Fetch recipient's encryption key
        const agents = await client.listAgents(500);
        const recipient = agents.agents?.find(a => a.vault_id === recipientVaultId);
        if (recipient) {
          recipientEncryptionKey = recipient.encryption_public_key;
        }
      }

      if (!recipientEncryptionKey) {
        if (json) {
          outputError('Cannot encrypt: recipient encryption key not found', 'encryption_error');
        } else {
          console.error('Error: Cannot encrypt: recipient encryption key not found');
        }
        process.exit(1);
      }

      const recipientKey = crypto.fromBase64(recipientEncryptionKey);
      encryptedPayload = crypto.encryptJson(recipientKey, message.payload);
    }

    // Send message
    const result = await client.sendMessage(message, signature, encryptedPayload);

    // Save to history
    vault.saveMessage(message, 'sent');

    if (json) {
      outputJson({
        status: 'sent',
        message_id: result.message_id,
        recipient: recipientVaultId,
        conversation_id: result.conversation_id,
      });
    } else {
      console.error('\nMessage sent!');
      console.error(`Message ID: ${result.message_id}`);
      console.error(`Recipient: ${recipientVaultId}`);
      console.error(`Conversation: ${result.conversation_id}`);
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
