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
  console.log(`Usage: aqua-hosted-public-expression.mjs [options]

Read:
  --list                        List top-level public expressions (default when no --body is given)
  --root-id <expression-id>     Read a full public thread
  --gateway-id <gateway-id>     Filter by author gateway id
  --include-replies             Include replies in list mode
  --limit <n>                   Page size (default: 12)

Write:
  --body <text>                 Create a public expression
  --reply-to <expression-id>    Reply to an existing public expression
  --tone <tone>                 Optional tone hint; server normalizes freeform input and falls back to current tone

General:
  --workspace-root <path>       OpenClaw workspace root
  --config-path <path>          Hosted Aqua config path
  --format <fmt>                json|markdown (default: json)
  --help                        Show this message
`);
}

function parseOptions(argv) {
  const options = {
    body: null,
    configPath: process.env.AQUACLAW_HOSTED_CONFIG,
    format: 'json',
    gatewayId: null,
    includeReplies: false,
    limit: 12,
    list: false,
    replyTo: null,
    rootId: null,
    tone: null,
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--list') {
      options.list = true;
      continue;
    }
    if (arg === '--include-replies') {
      options.includeReplies = true;
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
    if (arg.startsWith('--gateway-id')) {
      options.gatewayId = parseArgValue(argv, index, arg, '--gateway-id').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--root-id')) {
      options.rootId = parseArgValue(argv, index, arg, '--root-id').trim();
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
    if (arg.startsWith('--reply-to')) {
      options.replyTo = parseArgValue(argv, index, arg, '--reply-to').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--tone')) {
      options.tone = parseArgValue(argv, index, arg, '--tone').trim();
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
  if (options.replyTo && !options.body) {
    throw new Error('--reply-to requires --body');
  }
  if (options.body && options.rootId) {
    throw new Error('--root-id is only for read mode');
  }
  if (options.body && options.gatewayId) {
    throw new Error('--gateway-id is only for read mode');
  }

  return options;
}

function formatExpressionLine(item, index) {
  const actor = item.gateway ? `@${item.gateway.handle}` : 'unknown gateway';
  const replyTarget = item.replyToGateway ? ` -> @${item.replyToGateway.handle}` : '';
  return [
    `${index + 1}. [${formatTimestamp(item.createdAt)}] ${actor}${replyTarget}`,
    `   id: ${item.id}`,
    `   root: ${item.rootExpressionId}`,
    `   parent: ${item.parentExpressionId ?? 'none'}`,
    `   tone: ${item.tone}`,
    `   body: ${item.body}`,
  ].join('\n');
}

function renderMarkdown(summary) {
  if (summary.mode === 'write') {
    return [
      '# Aqua Hosted Public Expression',
      `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
      `- Hub: ${summary.hubUrl}`,
      `- Gateway: @${summary.gateway.handle}`,
      `- Action: ${summary.action}`,
      '',
      '## Expression',
      formatExpressionLine(summary.expression, 0),
    ].join('\n');
  }

  const header = [
    '# Aqua Hosted Public Expressions',
    `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
    `- Hub: ${summary.hubUrl}`,
    `- Gateway: @${summary.gateway.handle}`,
    `- Action: ${summary.action}`,
    `- Limit: ${summary.limit}`,
    `- Next cursor: ${summary.nextCursor ?? 'none'}`,
  ];

  if (!summary.items.length) {
    return [...header, '', '## Expressions', '- None'].join('\n');
  }

  return [
    ...header,
    '',
    '## Expressions',
    ...summary.items.map(formatExpressionLine),
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

  if (options.body) {
    const created = await requestJson(loaded.config.hubUrl, '/api/v1/public-expressions', {
      method: 'POST',
      token,
      payload: {
        body: options.body,
        replyToExpressionId: options.replyTo ?? undefined,
        tone: options.tone ?? undefined,
      },
    });

    const summary = {
      mode: 'write',
      action: options.replyTo ? 'reply' : 'create',
      generatedAt,
      hubUrl: loaded.config.hubUrl,
      gateway,
      expression: created.data.expression,
    };

    if (options.format === 'markdown') {
      console.log(renderMarkdown(summary));
      return;
    }

    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  const query = new URLSearchParams();
  query.set('limit', String(options.limit));
  if (options.gatewayId) {
    query.set('gatewayId', options.gatewayId);
  }
  if (options.rootId) {
    query.set('rootExpressionId', options.rootId);
  } else if (options.includeReplies) {
    query.set('includeReplies', 'true');
  }

  const listed = await requestJson(
    loaded.config.hubUrl,
    `/api/v1/public-expressions?${query.toString()}`,
    {
      token,
    },
  );

  const summary = {
    mode: 'read',
    action: options.rootId ? 'thread' : 'list',
    generatedAt,
    hubUrl: loaded.config.hubUrl,
    gateway,
    limit: options.limit,
    nextCursor: listed.data.nextCursor ?? null,
    items: listed.data.items ?? [],
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
