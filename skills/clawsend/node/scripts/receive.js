#!/usr/bin/env node
/**
 * Receive messages from the ClawHub relay.
 *
 * Usage:
 *   node receive.js [--poll] [--interval N] [options]
 */

import { parseArgs } from 'util';
import { ensureReady, DEFAULT_RELAY } from '../lib/auto_setup.js';
import { RelayClient, outputJson, outputError, outputHuman, ClientError } from '../lib/client.js';
import { getSignableContent } from '../lib/envelope.js';
import * as crypto from '../lib/crypto.js';

const options = {
  server: { type: 'string', default: DEFAULT_RELAY },
  limit: { type: 'string', short: 'l', default: '50' },
  'vault-dir': { type: 'string' },
  json: { type: 'boolean', default: false },
  'no-verify': { type: 'boolean', default: false },
  decrypt: { type: 'boolean', default: false },
  poll: { type: 'boolean', default: false },
  interval: { type: 'string', default: '10' },
  help: { type: 'boolean', short: 'h', default: false },
};

// Track seen message IDs to avoid duplicates in polling mode
const seenMessageIds = new Set();

// Flag for graceful shutdown
let running = true;

function verifyMessage(message, signature, senderPublicKey) {
  try {
    const publicKey = crypto.fromBase64(senderPublicKey);
    const signable = getSignableContent(message);
    return crypto.verifyJson(publicKey, signable, signature);
  } catch {
    return false;
  }
}

async function fetchAndProcessMessages(client, vault, args, senderInfoCache) {
  const { limit, json, decrypt } = args.values;
  const noVerify = args.values['no-verify'];
  const poll = args.values.poll;

  async function getSenderInfo(senderId) {
    if (senderInfoCache.has(senderId)) {
      return senderInfoCache.get(senderId);
    }
    try {
      const agents = await client.listAgents(500);
      for (const agent of agents.agents || []) {
        senderInfoCache.set(agent.vault_id, {
          signing_public_key: agent.signing_public_key,
          alias: agent.alias,
        });
      }
    } catch {
      // Ignore errors
    }
    return senderInfoCache.get(senderId) || {};
  }

  const result = await client.receive(parseInt(limit, 10));
  const messages = result.messages || [];

  const processed = [];

  for (const msgData of messages) {
    const messageId = msgData.message_id;

    // Skip already seen messages in polling mode
    if (poll && seenMessageIds.has(messageId)) {
      continue;
    }
    seenMessageIds.add(messageId);

    const message = msgData.message;
    const signature = msgData.signature;
    const sender = msgData.sender;
    const encryptedPayload = msgData.encrypted_payload;

    // Resolve sender alias
    const senderInfo = await getSenderInfo(sender);
    const senderAlias = senderInfo.alias || sender;

    const msgResult = {
      message_id: messageId,
      sender,
      sender_alias: senderAlias,
      received_at: msgData.received_at,
      envelope: message.envelope,
      payload: message.payload,
      verified: false,
      decrypted: false,
    };

    // Verify signature
    if (!noVerify) {
      const senderKey = senderInfo.signing_public_key;
      if (senderKey) {
        if (verifyMessage(message, signature, senderKey)) {
          msgResult.verified = true;
        } else {
          msgResult.verification_error = 'Invalid signature';
        }
      } else {
        msgResult.verification_error = 'Sender key not found';
      }
    }

    // Decrypt if requested and available
    if (decrypt && encryptedPayload) {
      try {
        const decrypted = vault.decrypt(encryptedPayload);
        msgResult.payload = decrypted;
        msgResult.decrypted = true;
      } catch (e) {
        msgResult.decryption_error = e.message;
      }
    }

    // Check if from known contact
    msgResult.known_contact = vault.isKnownContact(sender);

    // Handle quarantine
    if (vault.shouldQuarantine(sender)) {
      vault.saveToQuarantine(message, 'unknown_sender');
      msgResult.quarantined = true;
    } else {
      vault.saveMessage(message, 'received');
      msgResult.quarantined = false;
    }

    processed.push(msgResult);
  }

  return processed;
}

function displayMessages(messages, jsonMode) {
  if (jsonMode) {
    outputJson({ messages, count: messages.length });
  } else {
    if (!messages.length) return;

    for (const msg of messages) {
      console.error('\n' + '='.repeat(60));
      console.error(`Message ID: ${msg.message_id}`);
      if (msg.sender_alias && msg.sender_alias !== msg.sender) {
        console.error(`From: ${msg.sender_alias} (${msg.sender})`);
      } else {
        console.error(`From: ${msg.sender}`);
      }
      console.error(`Intent: ${msg.envelope?.intent || msg.payload?.intent}`);
      console.error(`Type: ${msg.envelope?.type}`);
      console.error(`Received: ${msg.received_at}`);

      const status = [];
      if (msg.verified) status.push('verified');
      else if (msg.verification_error) status.push(`UNVERIFIED (${msg.verification_error})`);
      if (msg.decrypted) status.push('decrypted');
      if (msg.known_contact) status.push('known contact');
      if (msg.quarantined) status.push('QUARANTINED');

      console.error(`Status: ${status.length ? status.join(', ') : 'none'}`);
      console.error(`Body: ${JSON.stringify(msg.payload?.body, null, 2)}`);
    }
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

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
Usage: node receive.js [options]

Options:
  -l, --limit       Max messages to retrieve (default: 50)
  --decrypt         Attempt to decrypt encrypted payloads
  --no-verify       Skip signature verification
  --poll            Continuously poll for new messages
  --interval        Polling interval in seconds (default: 10)
  --server          Relay server URL
  --vault-dir       Custom vault directory
  --json            Output as JSON
  -h, --help        Show this help
`);
    process.exit(0);
  }

  const { server, json, poll, interval } = args.values;
  const vaultDir = args.values['vault-dir'];

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
  const senderInfoCache = new Map();

  // Handle graceful shutdown
  if (poll) {
    process.on('SIGINT', () => {
      running = false;
      console.error('\nStopping message polling...');
    });
    process.on('SIGTERM', () => {
      running = false;
    });
  }

  try {
    if (poll) {
      // Polling mode
      const intervalMs = parseInt(interval, 10) * 1000;

      if (!json) {
        outputHuman(`Polling for messages from ${server} every ${interval}s...`);
        outputHuman('Press Ctrl+C to stop.\n');
      }

      while (running) {
        try {
          const messages = await fetchAndProcessMessages(client, vault, args, senderInfoCache);

          if (messages.length) {
            if (!json) {
              const time = new Date().toLocaleTimeString();
              outputHuman(`[${time}] Received ${messages.length} new message(s)`);
            }
            displayMessages(messages, json);
          }

          await sleep(intervalMs);
        } catch (e) {
          if (!json) {
            const time = new Date().toLocaleTimeString();
            console.error(`[${time}] Error: ${e.message}`);
          }
          await sleep(intervalMs);
        }
      }

      if (!json) {
        outputHuman('Polling stopped.');
      }
    } else {
      // One-shot mode
      if (!json) {
        outputHuman(`Fetching messages from ${server}...`);
      }

      const messages = await fetchAndProcessMessages(client, vault, args, senderInfoCache);

      if (!json) {
        outputHuman(`Received ${messages.length} message(s)`);
      }

      if (json) {
        outputJson({ messages, count: messages.length });
      } else {
        if (!messages.length) {
          console.error('\nNo new messages.');
        } else {
          displayMessages(messages, json);
        }
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
