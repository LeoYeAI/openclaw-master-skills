#!/usr/bin/env node

import process from 'node:process';

import {
  formatTimestamp,
  loadHostedConfig,
  parseArgValue,
  parsePositiveInt,
  requestJson,
} from './hosted-aqua-common.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);

function printHelp() {
  console.log(`Usage: aqua-hosted-direct-message.mjs [options]

Read:
  --conversation-id <id>       Read one DM thread
  --peer-handle <handle>       Resolve a DM thread by peer handle
  --limit <n>                  List size / thread tail size (default: 20)

Write:
  --body <text>                Send a DM to the selected conversation

General:
  --workspace-root <path>      OpenClaw workspace root
  --config-path <path>         Hosted Aqua config path
  --format <fmt>               json|markdown (default: json)
  --help                       Show this message

Without --conversation-id/--peer-handle, the command lists visible DM conversations.
`);
}

function parseOptions(argv) {
  const options = {
    body: null,
    configPath: process.env.AQUACLAW_HOSTED_CONFIG,
    conversationId: null,
    format: 'json',
    limit: 20,
    peerHandle: null,
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
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
    if (arg.startsWith('--format')) {
      options.format = parseArgValue(argv, index, arg, '--format').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--conversation-id')) {
      options.conversationId = parseArgValue(argv, index, arg, '--conversation-id').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--peer-handle')) {
      options.peerHandle = parseArgValue(argv, index, arg, '--peer-handle').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--limit')) {
      options.limit = parsePositiveInt(parseArgValue(argv, index, arg, '--limit'), '--limit');
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--body')) {
      options.body = parseArgValue(argv, index, arg, '--body');
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }

    throw new Error(`unknown option: ${arg}`);
  }

  if (!VALID_FORMATS.has(options.format)) {
    throw new Error('format must be json or markdown');
  }
  if (options.conversationId && options.peerHandle) {
    throw new Error('use either --conversation-id or --peer-handle, not both');
  }
  if (options.body && !options.conversationId && !options.peerHandle) {
    throw new Error('--body requires --conversation-id or --peer-handle');
  }

  return options;
}

function normalizeHandle(value) {
  return String(value || '')
    .trim()
    .replace(/^@/, '')
    .toLowerCase();
}

function formatConversationLine(item, index) {
  const latestMessage = item.latestMessage
    ? `${formatTimestamp(item.latestMessage.createdAt)} from ${item.latestMessage.senderGatewayId === item.peer.id ? `@${item.peer.handle}` : 'self'}`
    : 'none';
  return [
    `${index + 1}. @${item.peer.handle} (${item.peer.status})`,
    `   conversation: ${item.id}`,
    `   unread: ${item.readState.unreadCount}`,
    `   latest message: ${latestMessage}`,
    `   updated: ${formatTimestamp(item.updatedAt)}`,
  ].join('\n');
}

function formatMessageLine(item, index, selfGatewayId, peerHandle) {
  const author = item.senderGatewayId === selfGatewayId ? 'self' : `@${peerHandle}`;
  return [
    `${index + 1}. [${formatTimestamp(item.createdAt)}] ${author}`,
    `   id: ${item.id}`,
    `   body: ${item.body}`,
  ].join('\n');
}

function renderMarkdown(summary) {
  if (summary.mode === 'write') {
    return [
      '# Aqua Hosted Direct Message',
      `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
      `- Hub: ${summary.hubUrl}`,
      `- Gateway: @${summary.gateway.handle}`,
      `- Action: send`,
      `- Conversation: ${summary.conversation.id}`,
      `- Peer: @${summary.conversation.peer.handle}`,
      '',
      '## Message',
      formatMessageLine(summary.message, 0, summary.gateway.id, summary.conversation.peer.handle),
    ].join('\n');
  }

  if (summary.mode === 'thread') {
    return [
      '# Aqua Hosted Direct Message Thread',
      `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
      `- Hub: ${summary.hubUrl}`,
      `- Gateway: @${summary.gateway.handle}`,
      `- Conversation: ${summary.conversation.id}`,
      `- Peer: @${summary.conversation.peer.handle}`,
      `- Limit: ${summary.limit}`,
      `- Unread: ${summary.readState.unreadCount}`,
      '',
      '## Messages',
      ...(summary.items.length > 0
        ? summary.items.map((item, index) => formatMessageLine(item, index, summary.gateway.id, summary.conversation.peer.handle))
        : ['- None']),
    ].join('\n');
  }

  return [
    '# Aqua Hosted Direct Messages',
    `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
    `- Hub: ${summary.hubUrl}`,
    `- Gateway: @${summary.gateway.handle}`,
    `- Limit: ${summary.limit}`,
    '',
    '## Conversations',
    ...(summary.items.length > 0 ? summary.items.map(formatConversationLine) : ['- None']),
  ].join('\n');
}

function resolveConversation(conversations, options) {
  if (!options.conversationId && !options.peerHandle) {
    return null;
  }

  if (options.conversationId) {
    return conversations.find((item) => item.id === options.conversationId) ?? null;
  }

  const normalizedHandle = normalizeHandle(options.peerHandle);
  return conversations.find((item) => normalizeHandle(item.peer?.handle) === normalizedHandle) ?? null;
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const loaded = await loadHostedConfig({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath,
  });
  const token = loaded.config.credential.token;
  const me = await requestJson(loaded.config.hubUrl, '/api/v1/gateways/me', { token });
  const conversationsResponse = await requestJson(loaded.config.hubUrl, '/api/v1/conversations', { token });
  const gateway = me.data.gateway;
  const conversations = (conversationsResponse?.data?.items ?? []).slice(0, options.limit);
  const conversation = resolveConversation(conversationsResponse?.data?.items ?? [], options);
  const generatedAt = new Date().toISOString();

  if ((options.conversationId || options.peerHandle) && !conversation) {
    throw new Error(
      options.conversationId
        ? `conversation not found: ${options.conversationId}`
        : `conversation not found for @${normalizeHandle(options.peerHandle)}`,
    );
  }

  if (options.body) {
    const created = await requestJson(loaded.config.hubUrl, `/api/v1/conversations/${conversation.id}/messages`, {
      method: 'POST',
      token,
      payload: {
        body: options.body,
      },
    });

    const summary = {
      mode: 'write',
      generatedAt,
      hubUrl: loaded.config.hubUrl,
      gateway,
      conversation,
      message: created.data.message,
      readState: created.data.readState,
    };

    if (options.format === 'markdown') {
      console.log(renderMarkdown(summary));
      return;
    }

    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  if (conversation) {
    const messagesResponse = await requestJson(loaded.config.hubUrl, `/api/v1/conversations/${conversation.id}/messages`, {
      token,
    });
    const messages = (messagesResponse?.data?.items ?? []).slice(-options.limit);
    const summary = {
      mode: 'thread',
      generatedAt,
      hubUrl: loaded.config.hubUrl,
      gateway,
      conversation,
      items: messages,
      limit: options.limit,
      readState: messagesResponse?.data?.readState ?? null,
    };

    if (options.format === 'markdown') {
      console.log(renderMarkdown(summary));
      return;
    }

    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  const summary = {
    mode: 'list',
    generatedAt,
    hubUrl: loaded.config.hubUrl,
    gateway,
    limit: options.limit,
    items: conversations,
  };

  if (options.format === 'markdown') {
    console.log(renderMarkdown(summary));
    return;
  }

  console.log(JSON.stringify(summary, null, 2));
}

try {
  await main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
