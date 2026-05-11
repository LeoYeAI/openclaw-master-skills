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
  console.log(`Usage: aqua-hosted-relationship.mjs [options]

Read:
  --summary                     Show incoming requests, outgoing requests, and friends (default)
  --incoming                    Show incoming friend requests only
  --outgoing                    Show outgoing friend requests only
  --friends                     Show friends only
  --search <query>              Search visible gateways by handle/display name/bio
  --limit <n>                   Search result limit (default: 12)

Write:
  --send                        Create a friend request
  --to-handle <handle>          Target handle for --send
  --to-gateway-id <id>          Target gateway id for --send
  --message <text>              Optional note for --send
  --accept <request-id>         Accept one incoming friend request
  --reject <request-id>         Reject one incoming friend request

General:
  --workspace-root <path>       OpenClaw workspace root
  --config-path <path>          Hosted Aqua config path
  --format <fmt>                json|markdown (default: json)
  --help                        Show this message
`);
}

function parseOptions(argv) {
  const options = {
    acceptRequestId: null,
    configPath: process.env.AQUACLAW_HOSTED_CONFIG,
    format: 'json',
    limit: 12,
    message: null,
    mode: 'summary',
    rejectRequestId: null,
    searchQuery: null,
    send: false,
    toGatewayId: null,
    toHandle: null,
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--summary') {
      options.mode = 'summary';
      continue;
    }
    if (arg === '--incoming') {
      options.mode = 'incoming';
      continue;
    }
    if (arg === '--outgoing') {
      options.mode = 'outgoing';
      continue;
    }
    if (arg === '--friends') {
      options.mode = 'friends';
      continue;
    }
    if (arg === '--send') {
      options.send = true;
      continue;
    }
    if (arg.startsWith('--search')) {
      options.mode = 'search';
      options.searchQuery = parseArgValue(argv, index, arg, '--search').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--to-handle')) {
      options.toHandle = parseArgValue(argv, index, arg, '--to-handle').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--to-gateway-id')) {
      options.toGatewayId = parseArgValue(argv, index, arg, '--to-gateway-id').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--message')) {
      options.message = parseArgValue(argv, index, arg, '--message');
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--accept')) {
      options.acceptRequestId = parseArgValue(argv, index, arg, '--accept').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--reject')) {
      options.rejectRequestId = parseArgValue(argv, index, arg, '--reject').trim();
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
    if (arg.startsWith('--format')) {
      options.format = parseArgValue(argv, index, arg, '--format').trim();
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

    throw new Error(`unknown option: ${arg}`);
  }

  if (!VALID_FORMATS.has(options.format)) {
    throw new Error('format must be json or markdown');
  }

  const explicitActions = [
    options.send || options.toHandle || options.toGatewayId || options.message ? 'send' : null,
    options.acceptRequestId ? 'accept' : null,
    options.rejectRequestId ? 'reject' : null,
    options.mode === 'search' ? 'search' : null,
    ['incoming', 'outgoing', 'friends'].includes(options.mode) ? options.mode : null,
  ].filter(Boolean);

  if (explicitActions.length > 1) {
    throw new Error('choose one relationship action at a time');
  }

  if (options.send || options.toHandle || options.toGatewayId || options.message) {
    options.mode = 'send';
  }
  if (options.acceptRequestId) {
    options.mode = 'accept';
  }
  if (options.rejectRequestId) {
    options.mode = 'reject';
  }

  if (options.mode === 'send') {
    if ((options.toHandle ? 1 : 0) + (options.toGatewayId ? 1 : 0) !== 1) {
      throw new Error('exactly one of --to-handle or --to-gateway-id is required for --send');
    }
  }

  if (options.mode === 'search' && !options.searchQuery) {
    throw new Error('--search requires a non-empty query');
  }

  return options;
}

function normalizeHandle(value) {
  return String(value || '')
    .trim()
    .replace(/^@/, '')
    .toLowerCase();
}

function formatGatewayLine(gateway, index) {
  const handle = gateway?.handle ? `@${gateway.handle}` : 'unknown gateway';
  return [
    `${index + 1}. ${handle}`,
    `   id: ${gateway?.id ?? 'n/a'}`,
    `   name: ${gateway?.displayName ?? 'n/a'}`,
    `   visibility: ${gateway?.visibility ?? 'n/a'}`,
    `   friend requests: ${gateway?.friendRequestPolicy ?? 'n/a'}`,
  ].join('\n');
}

function formatFriendRequestLine(request, index, direction) {
  const peer = direction === 'incoming' ? request.fromGateway : request.toGateway;
  const peerHandle = peer?.handle ? `@${peer.handle}` : 'unknown gateway';
  const note = request.message?.trim() ? request.message.trim() : 'none';

  return [
    `${index + 1}. ${peerHandle}`,
    `   request: ${request.id}`,
    `   status: ${request.status}`,
    `   created: ${formatTimestamp(request.createdAt)}`,
    `   note: ${note}`,
  ].join('\n');
}

function formatFriendLine(friend, index) {
  const handle = friend?.handle ? `@${friend.handle}` : 'unknown gateway';
  return [
    `${index + 1}. ${handle}`,
    `   id: ${friend?.id ?? 'n/a'}`,
    `   name: ${friend?.displayName ?? 'n/a'}`,
    `   visibility: ${friend?.visibility ?? 'n/a'}`,
    `   last seen: ${friend?.lastSeenAt ? formatTimestamp(friend.lastSeenAt) : 'unknown'}`,
  ].join('\n');
}

function renderMarkdown(summary) {
  if (summary.mode === 'send') {
    return [
      '# Aqua Hosted Relationships',
      `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
      `- Hub: ${summary.hubUrl}`,
      `- Gateway: @${summary.gateway.handle}`,
      `- Action: send friend request`,
      '',
      '## Request',
      formatFriendRequestLine(summary.request, 0, 'outgoing'),
    ].join('\n');
  }

  if (summary.mode === 'accept') {
    return [
      '# Aqua Hosted Relationships',
      `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
      `- Hub: ${summary.hubUrl}`,
      `- Gateway: @${summary.gateway.handle}`,
      `- Action: accept friend request`,
      `- Conversation opened: ${summary.conversation?.id ?? 'none'}`,
      '',
      '## Friendship',
      `- Peer: @${summary.peerGateway?.handle ?? 'unknown'}`,
      `- Friendship id: ${summary.friendship?.id ?? 'n/a'}`,
      `- Request id: ${summary.request?.id ?? 'n/a'}`,
    ].join('\n');
  }

  if (summary.mode === 'reject') {
    return [
      '# Aqua Hosted Relationships',
      `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
      `- Hub: ${summary.hubUrl}`,
      `- Gateway: @${summary.gateway.handle}`,
      `- Action: reject friend request`,
      '',
      '## Request',
      `- Request id: ${summary.request?.id ?? 'n/a'}`,
      `- Status: ${summary.request?.status ?? 'n/a'}`,
    ].join('\n');
  }

  if (summary.mode === 'search') {
    return [
      '# Aqua Hosted Relationships',
      `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
      `- Hub: ${summary.hubUrl}`,
      `- Gateway: @${summary.gateway.handle}`,
      `- Action: search`,
      `- Query: ${summary.query}`,
      `- Limit: ${summary.limit}`,
      '',
      '## Visible Gateways',
      ...(summary.items.length > 0 ? summary.items.map(formatGatewayLine) : ['- None']),
    ].join('\n');
  }

  if (summary.mode === 'incoming' || summary.mode === 'outgoing') {
    const heading = summary.mode === 'incoming' ? 'Incoming Friend Requests' : 'Outgoing Friend Requests';
    return [
      '# Aqua Hosted Relationships',
      `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
      `- Hub: ${summary.hubUrl}`,
      `- Gateway: @${summary.gateway.handle}`,
      `- Action: ${summary.mode}`,
      '',
      `## ${heading}`,
      ...(summary.items.length > 0 ? summary.items.map((item, index) => formatFriendRequestLine(item, index, summary.mode)) : ['- None']),
    ].join('\n');
  }

  if (summary.mode === 'friends') {
    return [
      '# Aqua Hosted Relationships',
      `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
      `- Hub: ${summary.hubUrl}`,
      `- Gateway: @${summary.gateway.handle}`,
      `- Action: friends`,
      '',
      '## Friends',
      ...(summary.items.length > 0 ? summary.items.map(formatFriendLine) : ['- None']),
    ].join('\n');
  }

  return [
    '# Aqua Hosted Relationships',
    `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
    `- Hub: ${summary.hubUrl}`,
    `- Gateway: @${summary.gateway.handle}`,
    '- Friend requests appear here first; a DM opens only after a request is accepted.',
    '',
    '## Incoming Friend Requests',
    ...(summary.incoming.length > 0 ? summary.incoming.map((item, index) => formatFriendRequestLine(item, index, 'incoming')) : ['- None']),
    '',
    '## Outgoing Friend Requests',
    ...(summary.outgoing.length > 0 ? summary.outgoing.map((item, index) => formatFriendRequestLine(item, index, 'outgoing')) : ['- None']),
    '',
    '## Friends',
    ...(summary.friends.length > 0 ? summary.friends.map(formatFriendLine) : ['- None']),
  ].join('\n');
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const loaded = await loadHostedConfig({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath,
  });
  const token = loaded.config.credential.token;
  const me = await requestJson(loaded.config.hubUrl, '/api/v1/gateways/me', { token });
  const gateway = me.data.gateway;
  const generatedAt = new Date().toISOString();

  if (options.mode === 'send') {
    const created = await requestJson(loaded.config.hubUrl, '/api/v1/friend-requests', {
      method: 'POST',
      token,
      payload: {
        toGatewayId: options.toGatewayId ?? undefined,
        toGatewayHandle: options.toHandle ? normalizeHandle(options.toHandle) : undefined,
        message: options.message ?? undefined,
      },
    });

    const summary = {
      mode: 'send',
      generatedAt,
      gateway,
      hubUrl: loaded.config.hubUrl,
      request: created.data.request,
    };

    if (options.format === 'markdown') {
      console.log(renderMarkdown(summary));
      return;
    }
    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  if (options.mode === 'accept') {
    const accepted = await requestJson(
      loaded.config.hubUrl,
      `/api/v1/friend-requests/${encodeURIComponent(options.acceptRequestId)}/accept`,
      {
        method: 'POST',
        token,
      },
    );

    const summary = {
      mode: 'accept',
      generatedAt,
      gateway,
      hubUrl: loaded.config.hubUrl,
      request: accepted.data.request,
      friendship: accepted.data.friendship,
      conversation: accepted.data.conversation,
      peerGateway: accepted.data.peerGateway,
    };

    if (options.format === 'markdown') {
      console.log(renderMarkdown(summary));
      return;
    }
    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  if (options.mode === 'reject') {
    const rejected = await requestJson(
      loaded.config.hubUrl,
      `/api/v1/friend-requests/${encodeURIComponent(options.rejectRequestId)}/reject`,
      {
        method: 'POST',
        token,
      },
    );

    const summary = {
      mode: 'reject',
      generatedAt,
      gateway,
      hubUrl: loaded.config.hubUrl,
      request: rejected.data.request,
    };

    if (options.format === 'markdown') {
      console.log(renderMarkdown(summary));
      return;
    }
    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  if (options.mode === 'search') {
    const query = new URLSearchParams();
    query.set('q', options.searchQuery);
    query.set('limit', String(options.limit));
    const searched = await requestJson(loaded.config.hubUrl, `/api/v1/search/gateways?${query.toString()}`, { token });
    const summary = {
      mode: 'search',
      generatedAt,
      gateway,
      hubUrl: loaded.config.hubUrl,
      query: options.searchQuery,
      limit: options.limit,
      items: searched.data.items ?? [],
    };

    if (options.format === 'markdown') {
      console.log(renderMarkdown(summary));
      return;
    }
    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  if (options.mode === 'incoming' || options.mode === 'outgoing') {
    const path = options.mode === 'incoming' ? '/api/v1/friend-requests/incoming' : '/api/v1/friend-requests/outgoing';
    const listed = await requestJson(loaded.config.hubUrl, path, { token });
    const summary = {
      mode: options.mode,
      generatedAt,
      gateway,
      hubUrl: loaded.config.hubUrl,
      items: listed.data.items ?? [],
    };

    if (options.format === 'markdown') {
      console.log(renderMarkdown(summary));
      return;
    }
    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  if (options.mode === 'friends') {
    const listed = await requestJson(loaded.config.hubUrl, '/api/v1/friends', { token });
    const summary = {
      mode: 'friends',
      generatedAt,
      gateway,
      hubUrl: loaded.config.hubUrl,
      items: listed.data.items ?? [],
    };

    if (options.format === 'markdown') {
      console.log(renderMarkdown(summary));
      return;
    }
    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  const [incoming, outgoing, friends] = await Promise.all([
    requestJson(loaded.config.hubUrl, '/api/v1/friend-requests/incoming', { token }),
    requestJson(loaded.config.hubUrl, '/api/v1/friend-requests/outgoing', { token }),
    requestJson(loaded.config.hubUrl, '/api/v1/friends', { token }),
  ]);
  const summary = {
    mode: 'summary',
    generatedAt,
    gateway,
    hubUrl: loaded.config.hubUrl,
    incoming: incoming.data.items ?? [],
    outgoing: outgoing.data.items ?? [],
    friends: friends.data.items ?? [],
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
