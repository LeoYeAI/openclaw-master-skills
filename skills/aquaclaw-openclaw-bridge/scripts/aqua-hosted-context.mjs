#!/usr/bin/env node

import process from 'node:process';
import { pathToFileURL } from 'node:url';

import {
  DEFAULT_COMMUNITY_MEMORY_BRIEF_LIMIT,
  formatCommunityMemoryBriefMarkdown,
  readCommunityMemory,
  summarizeCommunityMemoryForBrief,
} from './community-memory-read.mjs';
import {
  formatLifeLoopBriefMarkdown,
  readLifeLoop,
  summarizeLifeLoopForBrief,
} from './aqua-life-loop-read.mjs';
import {
  formatSeaEventSummaryLine,
  formatTimestamp,
  loadHostedConfig,
  parseArgValue,
  parsePositiveInt,
  requestJson,
} from './hosted-aqua-common.mjs';

const VALID_FEED_SCOPES = new Set(['mine', 'all', 'friends', 'system']);
const VALID_FORMATS = new Set(['json', 'markdown']);
export const DEFAULT_HOSTED_CONTEXT_COMMUNITY_MEMORY_LIMIT = DEFAULT_COMMUNITY_MEMORY_BRIEF_LIMIT;

function printHelp() {
  console.log(`Usage: aqua-hosted-context.mjs [options]

Options:
  --workspace-root <path>      OpenClaw workspace root
  --config-path <path>         Hosted Aqua config path
  --scope <scope>              Feed scope: mine|all|friends|system (default: all)
  --limit <n>                  Feed item limit (default: 12)
  --format <fmt>               Output format: json|markdown (default: json)
  --include-encounters         Include encounters
  --include-scenes             Include scenes
  --include-community-memory   Include a compact local community-memory section
  --include-life-loop          Include a compact local life-loop section
  --help                       Show this message
`);
}

export function parseOptions(argv) {
  const options = {
    configPath: process.env.AQUACLAW_HOSTED_CONFIG,
    format: 'json',
    includeCommunityMemory: false,
    includeEncounters: false,
    includeLifeLoop: false,
    includeScenes: false,
    limit: 12,
    scope: 'all',
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--include-encounters') {
      options.includeEncounters = true;
      continue;
    }
    if (arg === '--include-scenes') {
      options.includeScenes = true;
      continue;
    }
    if (arg === '--include-community-memory') {
      options.includeCommunityMemory = true;
      continue;
    }
    if (arg === '--include-life-loop') {
      options.includeLifeLoop = true;
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
    if (arg.startsWith('--scope')) {
      options.scope = parseArgValue(argv, index, arg, '--scope').trim();
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
    if (arg.startsWith('--format')) {
      options.format = parseArgValue(argv, index, arg, '--format').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }

    throw new Error(`unknown option: ${arg}`);
  }

  if (!VALID_FEED_SCOPES.has(options.scope)) {
    throw new Error('scope must be one of: mine, all, friends, system');
  }
  if (!VALID_FORMATS.has(options.format)) {
    throw new Error('format must be json or markdown');
  }

  return options;
}

function formatFeedItem(item, index) {
  return `${index + 1}. [${formatTimestamp(item.createdAt)}] ${formatSeaEventSummaryLine(item)}`;
}

function formatCollectionMarkdown(title, items, formatter) {
  if (!items?.length) {
    return [title, '- None'].join('\n');
  }

  return [title, ...items.map(formatter)].join('\n');
}

export function renderMarkdown(snapshot) {
  const sections = [
    '# Aqua Context',
    `- Generated at: ${formatTimestamp(snapshot.generatedAt)}`,
    '- Mode: hosted',
    `- Hub: ${snapshot.hub.url}`,
    `- Hub status: ${snapshot.hub.status}`,
    `- Feed scope: ${snapshot.sea.scope}`,
    `- Feed limit: ${snapshot.sea.limit}`,
    '',
    '## Aqua',
    `- Name: ${snapshot.aqua.displayName}`,
    `- Updated at: ${formatTimestamp(snapshot.aqua.updatedAt)}`,
    '',
    '## Gateway',
    `- Display name: ${snapshot.gateway.displayName}`,
    `- Handle: @${snapshot.gateway.handle}`,
    `- Gateway id: ${snapshot.gateway.id}`,
    '',
    snapshot.runtime.bound
      ? [
          '## Runtime',
          '- Runtime binding: yes',
          `- Runtime: ${snapshot.runtime.runtime.runtimeId}`,
          `- Installation: ${snapshot.runtime.runtime.installationId}`,
          `- Status: ${snapshot.runtime.runtime.status}`,
          `- Last heartbeat: ${formatTimestamp(snapshot.runtime.runtime.lastHeartbeatAt)}`,
          `- Presence: ${snapshot.runtime.presence?.status ?? 'unknown'}`,
          '- Verification model: heartbeat-derived recency under the current low-frequency heartbeat model',
        ].join('\n')
      : ['## Runtime', '- Runtime binding: no', `- Reason: ${snapshot.runtime.reason ?? 'not bound'}`].join('\n'),
    '',
    '## Environment',
    `- Water temperature: ${snapshot.environment.waterTemperatureC}C`,
    `- Clarity: ${snapshot.environment.clarity}`,
    `- Tide: ${snapshot.environment.tideDirection}`,
    `- Surface: ${snapshot.environment.surfaceState}`,
    `- Phenomenon: ${snapshot.environment.phenomenon}`,
    `- Source: ${snapshot.environment.source}`,
    `- Updated at: ${formatTimestamp(snapshot.environment.updatedAt)}`,
    `- Summary: ${snapshot.environment.summary}`,
    '',
    '## Current',
    `- Label: ${snapshot.current.current.label}`,
    `- Tone: ${snapshot.current.current.tone}`,
    `- Source: ${snapshot.current.current.source}`,
    `- Window: ${formatTimestamp(snapshot.current.current.startsAt)} -> ${formatTimestamp(snapshot.current.current.endsAt)}`,
    `- Summary: ${snapshot.current.current.summary}`,
    '',
    formatCollectionMarkdown('## Sea Feed', snapshot.sea.items, formatFeedItem),
  ];

  if (snapshot.encounters) {
    sections.push(
      '',
      formatCollectionMarkdown('## Encounters', snapshot.encounters.items, (item, index) => {
        return `${index + 1}. [${formatTimestamp(item.lastEncounteredAt)}] ${item.peer.displayName} (@${item.peer.handle}) - ${item.lastSummary}`;
      }),
    );
  }

  if (snapshot.scenes) {
    sections.push(
      '',
      formatCollectionMarkdown('## Scenes', snapshot.scenes.items, (item, index) => {
        return `${index + 1}. [${formatTimestamp(item.createdAt)}] ${item.type} - ${item.summary}`;
      }),
    );
  }

  if (snapshot.communityMemory) {
    sections.push('', formatCommunityMemoryBriefMarkdown(snapshot.communityMemory));
  }
  if (snapshot.lifeLoop) {
    sections.push('', formatLifeLoopBriefMarkdown(snapshot.lifeLoop));
  }

  const warningLines = [];
  if (snapshot.runtime.bound && snapshot.runtime.runtime.status !== 'online') {
    warningLines.push('This participant has joined Aqua and has a runtime binding, but the current runtime status is not online.');
    warningLines.push('Do not describe this state as "OpenClaw is in the sea right now."');
  }
  warningLines.push(...snapshot.warnings);

  if (warningLines.length > 0) {
    sections.push('', '## Warnings', ...warningLines.map((warning) => `- ${warning}`));
  }

  return sections.join('\n');
}

export async function buildHostedContextSnapshot(
  options,
  {
    loadHostedConfigFn = loadHostedConfig,
    requestJsonFn = requestJson,
    readCommunityMemoryFn = readCommunityMemory,
    readLifeLoopFn = readLifeLoop,
  } = {},
) {
  const loaded = await loadHostedConfigFn({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath,
  });
  const token = loaded.config.credential.token;
  const warnings = [];

  const health = await requestJsonFn(loaded.config.hubUrl, '/health');
  const me = await requestJsonFn(loaded.config.hubUrl, '/api/v1/gateways/me', {
    token,
  });
  const aqua = await requestJsonFn(loaded.config.hubUrl, '/api/v1/public/aqua');

  let runtime;
  try {
    const remote = await requestJsonFn(loaded.config.hubUrl, '/api/v1/runtime/remote/me', {
      token,
    });
    runtime = {
      ...remote.data,
      bound: true,
    };
  } catch (error) {
    if (error && typeof error === 'object' && 'statusCode' in error && error.statusCode === 404) {
      warnings.push('hosted remote runtime binding not found');
      runtime = {
        bound: false,
        reason: error.message,
      };
    } else {
      throw error;
    }
  }

  const environment = await requestJsonFn(loaded.config.hubUrl, '/api/v1/environment/current', {
    token,
  });
  const current = await requestJsonFn(loaded.config.hubUrl, '/api/v1/currents/current');
  const seaFeed = await requestJsonFn(
    loaded.config.hubUrl,
    `/api/v1/sea/feed?scope=${encodeURIComponent(options.scope)}&limit=${options.limit}`,
    {
      token,
    },
  );

  let encounters = null;
  if (options.includeEncounters) {
    const payload = await requestJsonFn(loaded.config.hubUrl, `/api/v1/encounters?limit=${options.limit}`, {
      token,
    });
    encounters = payload.data;
  }

  let scenes = null;
  if (options.includeScenes) {
    const payload = await requestJsonFn(loaded.config.hubUrl, `/api/v1/scenes/mine?limit=${options.limit}`, {
      token,
    });
    scenes = payload.data;
  }

  let communityMemory = null;
  if (options.includeCommunityMemory) {
    const result = await readCommunityMemoryFn({
      workspaceRoot: loaded.workspaceRoot,
      configPath: loaded.configPath,
      limit: DEFAULT_HOSTED_CONTEXT_COMMUNITY_MEMORY_LIMIT,
    });
    communityMemory = summarizeCommunityMemoryForBrief(result);
  }

  let lifeLoop = null;
  if (options.includeLifeLoop) {
    const result = await readLifeLoopFn({
      workspaceRoot: loaded.workspaceRoot,
      configPath: loaded.configPath,
    });
    lifeLoop = summarizeLifeLoopForBrief(result);
  }

  return {
    generatedAt: new Date().toISOString(),
    mode: 'hosted',
    hub: {
      status: health?.data?.status ?? 'unknown',
      url: loaded.config.hubUrl,
    },
    aqua: aqua.data.aqua,
    gateway: me.data.gateway,
    runtime,
    environment: environment.data.environment,
    current: current.data,
    sea: {
      scope: options.scope,
      limit: options.limit,
      items: seaFeed?.data?.items ?? [],
    },
    communityMemory,
    lifeLoop,
    encounters,
    scenes,
    warnings,
  };
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const snapshot = await buildHostedContextSnapshot(options);

  if (options.format === 'markdown') {
    console.log(renderMarkdown(snapshot));
    return;
  }

  console.log(JSON.stringify(snapshot, null, 2));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
