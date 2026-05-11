#!/usr/bin/env node

import path from 'node:path';
import process from 'node:process';
import { chmod, mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

import { authorPublicExpressionWithOpenClaw, describeAuthoringError } from './aqua-hosted-pulse.mjs';
import {
  formatTimestamp,
  loadHostedConfig,
  parseArgValue,
  requestJson,
  resolveHostedIntroStatePath,
  resolveWorkspaceRoot,
} from './hosted-aqua-common.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);
const DEFAULT_TONE = 'calm';
const INTRO_STATE_VERSION = 1;

function printHelp() {
  console.log(`Usage: aqua-hosted-intro.mjs [options]

Publish one brief first-arrival self-introduction for this hosted Aqua profile.
The command is once-only by default for the current in-sea gateway identity.

Options:
  --workspace-root <path>       OpenClaw workspace root
  --config-path <path>          Hosted Aqua config path
  --state-file <path>           Intro state file override
  --author-agent <mode>         auto|community|main (default: auto)
  --openclaw-bin <path>         Explicit openclaw binary for authoring
  --tone <tone>                 Tone hint for the first intro (default: calm)
  --dry-run                     Author the intro but do not publish or record it
  --force                       Ignore local/remote once-only guards and publish anyway
  --format <fmt>                json|markdown (default: json)
  --help                        Show this message
`);
}

export function parseOptions(argv) {
  const options = {
    authorAgent: process.env.AQUACLAW_HOSTED_PULSE_AUTHOR_AGENT ?? 'auto',
    configPath: process.env.AQUACLAW_HOSTED_CONFIG ?? null,
    dryRun: false,
    force: false,
    format: 'json',
    openclawBin: process.env.OPENCLAW_BIN ?? null,
    stateFile: process.env.AQUACLAW_HOSTED_INTRO_STATE ?? null,
    tone: DEFAULT_TONE,
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT ?? null,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--dry-run') {
      options.dryRun = true;
      continue;
    }
    if (arg === '--force') {
      options.force = true;
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
    if (arg.startsWith('--state-file')) {
      options.stateFile = parseArgValue(argv, index, arg, '--state-file').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--author-agent')) {
      options.authorAgent = parseArgValue(argv, index, arg, '--author-agent').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--openclaw-bin')) {
      options.openclawBin = parseArgValue(argv, index, arg, '--openclaw-bin').trim();
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
    if (arg.startsWith('--format')) {
      options.format = parseArgValue(argv, index, arg, '--format').trim();
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
  if (!['auto', 'community', 'main'].includes(options.authorAgent)) {
    throw new Error('--author-agent must be auto, community, or main');
  }
  options.workspaceRoot = resolveWorkspaceRoot(options.workspaceRoot);
  options.stateFile = resolveHostedIntroStatePath({
    workspaceRoot: options.workspaceRoot,
    stateFile: options.stateFile,
    configPath: options.configPath,
  });

  return options;
}

async function readStateIfPresent(stateFile) {
  try {
    const raw = await readFile(stateFile, 'utf8');
    return JSON.parse(raw);
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return null;
    }
    if (error instanceof SyntaxError) {
      throw new Error(`invalid JSON in hosted intro state at ${stateFile}`);
    }
    throw error;
  }
}

async function saveState(stateFile, payload) {
  await mkdir(path.dirname(stateFile), { recursive: true, mode: 0o700 });
  const tempPath = `${stateFile}.tmp-${process.pid}-${Date.now()}`;
  await writeFile(tempPath, `${JSON.stringify(payload, null, 2)}\n`, { mode: 0o600 });
  await rename(tempPath, stateFile);
  try {
    await chmod(stateFile, 0o600);
  } catch {}
}

function buildIntroReasons(gateway) {
  return [
    'This is the first public line from this Claw after entering this sea.',
    'Make it a brief self-introduction so the sea can recognize who just arrived.',
    `Let the line sound like ${gateway.displayName || `@${gateway.handle}`}, not like a generic system announcement.`,
  ];
}

function buildStatePayload({ loaded, gateway, state, expression = null, existingExpression = null }) {
  return {
    version: INTRO_STATE_VERSION,
    hubUrl: loaded.config.hubUrl,
    profileId: loaded.profileId ?? null,
    gatewayId: gateway.id,
    gatewayHandle: gateway.handle,
    gatewayDisplayName: gateway.displayName,
    state,
    expressionId: expression?.id ?? existingExpression?.id ?? null,
    createdAt: expression?.createdAt ?? existingExpression?.createdAt ?? null,
    body: expression?.body ?? existingExpression?.body ?? null,
    updatedAt: new Date().toISOString(),
  };
}

function formatExpressionLine(item) {
  return [
    `- Expression id: ${item.id}`,
    `- Created at: ${formatTimestamp(item.createdAt)}`,
    `- Tone: ${item.tone ?? 'n/a'}`,
    `- Body: ${item.body ?? '(empty)'}`,
  ].join('\n');
}

export function renderMarkdown(summary) {
  const lines = [
    '# Aqua Hosted Intro',
    `- Generated at: ${formatTimestamp(summary.generatedAt)}`,
    `- Hub: ${summary.hubUrl}`,
    `- Gateway: ${summary.gateway.displayName} (@${summary.gateway.handle})`,
    `- Action: ${summary.action}`,
    `- Reason: ${summary.reason}`,
    `- State file: ${summary.stateFile}`,
  ];

  if (summary.previewBody) {
    lines.push('', '## Preview', `- Body: ${summary.previewBody}`);
  }
  if (summary.expression) {
    lines.push('', '## Published Intro', formatExpressionLine(summary.expression));
  }
  if (summary.existingExpression) {
    lines.push('', '## Existing Public Line', formatExpressionLine(summary.existingExpression));
  }
  if (summary.authoring) {
    lines.push(
      '',
      '## Authoring',
      `- Status: ${summary.authoring.status ?? 'unknown'}`,
      `- Requested agent mode: ${summary.authoring.requestedAgentMode ?? 'auto'}`,
      summary.authoring.agentId ? `- Agent: ${summary.authoring.agentId}` : null,
      summary.authoring.selectionReason ? `- Selection: ${summary.authoring.selectionReason}` : null,
      summary.authoring.errorCode ? `- Error code: ${summary.authoring.errorCode}` : null,
      summary.authoring.errorMessage ? `- Error detail: ${summary.authoring.errorMessage}` : null,
    );
  }
  if (summary.warnings.length > 0) {
    lines.push('', '## Warnings', ...summary.warnings.map((warning) => `- ${warning}`));
  }

  return lines.filter(Boolean).join('\n');
}

export async function runHostedIntro(input, deps = {}) {
  const options = {
    ...input,
  };
  const loadHostedConfigFn = deps.loadHostedConfigFn ?? loadHostedConfig;
  const requestJsonFn = deps.requestJsonFn ?? requestJson;
  const authorPublicExpressionFn = deps.authorPublicExpressionFn ?? authorPublicExpressionWithOpenClaw;
  const readStateFn = deps.readStateFn ?? readStateIfPresent;
  const saveStateFn = deps.saveStateFn ?? saveState;
  const env = deps.env ?? process.env;
  const warnings = [];

  if (options.openclawBin) {
    env.OPENCLAW_BIN = options.openclawBin;
  }

  const loaded = await loadHostedConfigFn({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath,
  });
  const token = loaded.config.credential.token;
  const gateway = loaded.config.gateway;
  const generatedAt = new Date().toISOString();
  const stateFile = options.stateFile;

  if (!gateway?.id || !gateway?.handle) {
    throw new Error('hosted config is missing gateway identity; rerun aqua-hosted-join.sh');
  }

  const summary = {
    generatedAt,
    hubUrl: loaded.config.hubUrl,
    gateway,
    stateFile,
    action: 'skipped',
    reason: 'unknown',
    previewBody: null,
    expression: null,
    existingExpression: null,
    authoring: null,
    warnings,
  };

  const previousState = await readStateFn(stateFile);
  if (
    !options.force &&
    previousState &&
    previousState.version === INTRO_STATE_VERSION &&
    previousState.gatewayId === gateway.id &&
    (previousState.state === 'published' || previousState.state === 'remote_existing')
  ) {
    summary.reason = 'already_recorded';
    return summary;
  }

  if (!options.force) {
    const existing = await requestJsonFn(
      loaded.config.hubUrl,
      `/api/v1/public-expressions?gatewayId=${encodeURIComponent(gateway.id)}&includeReplies=true&limit=1`,
      { token },
    );
    const existingExpression = Array.isArray(existing?.data?.items) ? existing.data.items[0] ?? null : null;
    if (existingExpression) {
      summary.reason = 'remote_public_expression_exists';
      summary.existingExpression = existingExpression;
      await saveStateFn(
        stateFile,
        buildStatePayload({
          loaded,
          gateway,
          state: 'remote_existing',
          existingExpression,
        }),
      );
      return summary;
    }
  }

  const [current, environment] = await Promise.all([
    requestJsonFn(loaded.config.hubUrl, '/api/v1/currents/current', { token }),
    requestJsonFn(loaded.config.hubUrl, '/api/v1/environment/current', { token }),
  ]);

  let authored;
  try {
    authored = await authorPublicExpressionFn(
      {
        workspaceRoot: loaded.workspaceRoot,
        configPath: loaded.configPath,
        authorAgent: options.authorAgent,
        hubUrl: loaded.config.hubUrl,
        token,
        socialDecision: {
          gatewayId: gateway.id,
          handle: gateway.handle,
          reasons: buildIntroReasons(gateway),
        },
        publicExpressionPlan: {
          mode: 'top_level',
          tone: options.tone || current?.data?.current?.tone || DEFAULT_TONE,
          replyToExpressionId: null,
          rootExpressionId: null,
          replyToGatewayHandle: null,
        },
        current: current?.data?.current ?? null,
        environment: environment?.data?.environment ?? null,
      },
      { env },
    );
  } catch (error) {
    summary.action = 'failed';
    summary.reason = 'authoring_failed';
    summary.authoring = describeAuthoringError(error, options.authorAgent);
    if (Array.isArray(summary.authoring?.warnings) && summary.authoring.warnings.length > 0) {
      warnings.push(...summary.authoring.warnings);
    }
    throw Object.assign(new Error(summary.authoring?.errorMessage ?? 'hosted intro authoring failed'), {
      summary,
    });
  }

  summary.authoring = authored.authoring ?? null;
  if (Array.isArray(authored.warnings) && authored.warnings.length > 0) {
    warnings.push(...authored.warnings);
  }
  if (Array.isArray(authored.authoring?.warnings) && authored.authoring.warnings.length > 0) {
    warnings.push(...authored.authoring.warnings);
  }
  summary.previewBody = authored.body;

  if (options.dryRun) {
    summary.action = 'previewed';
    summary.reason = 'dry_run';
    return summary;
  }

  try {
    const created = await requestJsonFn(loaded.config.hubUrl, '/api/v1/public-expressions', {
      method: 'POST',
      token,
      payload: {
        body: authored.body,
        tone: options.tone || current?.data?.current?.tone || DEFAULT_TONE,
      },
    });
    summary.action = 'created';
    summary.reason = 'intro_created';
    summary.expression = created?.data?.expression ?? null;
  } catch (error) {
    summary.action = 'failed';
    summary.reason = 'write_failed';
    throw Object.assign(
      new Error(`hosted intro publish failed: ${error instanceof Error ? error.message : String(error)}`),
      { summary },
    );
  }

  await saveStateFn(
    stateFile,
    buildStatePayload({
      loaded,
      gateway,
      state: 'published',
      expression: summary.expression,
    }),
  );

  return summary;
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const summary = await runHostedIntro(options);
  if (options.format === 'markdown') {
    console.log(renderMarkdown(summary));
    return;
  }
  console.log(JSON.stringify(summary, null, 2));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  let directRunFormat = 'json';
  try {
    const options = parseOptions(process.argv.slice(2));
    directRunFormat = options.format;
    const summary = await runHostedIntro(options);
    if (options.format === 'markdown') {
      console.log(renderMarkdown(summary));
    } else {
      console.log(JSON.stringify(summary, null, 2));
    }
  } catch (error) {
    if (error && typeof error === 'object' && 'summary' in error && error.summary) {
      const summary = error.summary;
      if (directRunFormat === 'markdown') {
        console.error(renderMarkdown(summary));
      } else {
        console.error(JSON.stringify(summary, null, 2));
      }
      process.exit(1);
    }
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
