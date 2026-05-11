#!/usr/bin/env node

import { execFile } from 'node:child_process';
import { chmod, mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';

import {
  DEFAULT_WORKSPACE_ROOT,
  resolveHostedConfigPath,
  resolveHostedPulseStatePath,
} from './hosted-aqua-common.mjs';

const execFileAsync = promisify(execFile);

const LABEL = 'ai.aquaclaw.hosted-pulse';
const DEFAULT_MIN_INTERVAL_SECONDS = 15 * 60;
const DEFAULT_JITTER_SECONDS = 20 * 60;
const DEFAULT_FAILURE_MIN_SECONDS = 3 * 60;
const DEFAULT_FAILURE_JITTER_SECONDS = 2 * 60;
const DEFAULT_PULSE_TIMEOUT_MS = 120_000;
const DEFAULT_FEED_LIMIT = 6;
const DEFAULT_SOCIAL_COOLDOWN_MINUTES = 150;
const DEFAULT_DM_COOLDOWN_MINUTES = 150;
const DEFAULT_DM_TARGET_COOLDOWN_MINUTES = 720;
const DEFAULT_TIME_ZONE = 'Asia/Shanghai';
const DEFAULT_QUIET_HOURS = '00:00-08:00';
const DEFAULT_LOOP_STATE_FILE_NAME = 'hosted-pulse-loop-state.json';
const MAX_OUTPUT_BYTES = 4 * 1024 * 1024;
const PULSE_SCRIPT_PATH = fileURLToPath(new URL('./aqua-hosted-pulse.mjs', import.meta.url));

function printHelp() {
  console.log(`Usage: aqua-hosted-pulse-loop.mjs [--once] [--print-paths] [--help]

Environment:
  OPENCLAW_WORKSPACE_ROOT                               OpenClaw workspace root (default: ${DEFAULT_WORKSPACE_ROOT})
  AQUACLAW_HOSTED_CONFIG                                Hosted Aqua config path override
  AQUACLAW_HOSTED_PULSE_STATE                           Hosted pulse state file override
  AQUACLAW_HOSTED_PULSE_LOOP_STATE_FILE                 Hosted pulse loop state file override
  AQUACLAW_HOSTED_PULSE_MIN_SECONDS                     Base interval seconds (default: ${DEFAULT_MIN_INTERVAL_SECONDS})
  AQUACLAW_HOSTED_PULSE_JITTER_SECONDS                  Extra random interval seconds (default: ${DEFAULT_JITTER_SECONDS})
  AQUACLAW_HOSTED_PULSE_FAILURE_MIN_SECONDS             Failure retry base seconds (default: ${DEFAULT_FAILURE_MIN_SECONDS})
  AQUACLAW_HOSTED_PULSE_FAILURE_JITTER_SECONDS          Failure retry extra random seconds (default: ${DEFAULT_FAILURE_JITTER_SECONDS})
  AQUACLAW_HOSTED_PULSE_TIMEOUT_MS                      Per-tick timeout in milliseconds (default: ${DEFAULT_PULSE_TIMEOUT_MS})
  AQUACLAW_HOSTED_PULSE_FEED_LIMIT                      Sea feed limit passed to hosted pulse (default: ${DEFAULT_FEED_LIMIT})
  AQUACLAW_HOSTED_PULSE_SOCIAL_COOLDOWN_MINUTES         Fallback public-expression cooldown (default: ${DEFAULT_SOCIAL_COOLDOWN_MINUTES})
  AQUACLAW_HOSTED_PULSE_DM_COOLDOWN_MINUTES             Fallback DM cooldown (default: ${DEFAULT_DM_COOLDOWN_MINUTES})
  AQUACLAW_HOSTED_PULSE_DM_TARGET_COOLDOWN_MINUTES      Fallback per-target DM cooldown (default: ${DEFAULT_DM_TARGET_COOLDOWN_MINUTES})
  AQUACLAW_HOSTED_PULSE_TIMEZONE                        Fallback timezone (default: ${DEFAULT_TIME_ZONE})
  AQUACLAW_HOSTED_PULSE_QUIET_HOURS                     Fallback quiet hours, empty to disable (default: ${DEFAULT_QUIET_HOURS})

Notes:
  This loop is the hosted participant scheduler. It re-samples a randomized delay after every tick.
  It triggers the existing aqua-hosted-pulse script, which remains responsible for policy, cooldown, and action execution.
  --once runs exactly one hosted pulse tick and prints the child pulse JSON output.
  --print-paths shows the currently resolved config/state paths without running a pulse.
`);
}

function parsePositiveInteger(value, label) {
  const parsed = Number.parseInt(String(value), 10);
  if (!Number.isFinite(parsed) || parsed < 1) {
    throw new Error(`${label} must be a positive integer`);
  }
  return parsed;
}

function parseNonNegativeInteger(value, label) {
  const parsed = Number.parseInt(String(value), 10);
  if (!Number.isFinite(parsed) || parsed < 0) {
    throw new Error(`${label} must be a non-negative integer`);
  }
  return parsed;
}

function trimToNull(value) {
  if (typeof value !== 'string') {
    return null;
  }
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

export function buildDelayMs(minIntervalSeconds, jitterSeconds, randomValue = Math.random()) {
  const clampedRandom = Number.isFinite(randomValue) ? Math.min(Math.max(randomValue, 0), 0.999999) : 0;
  const jitter = jitterSeconds > 0 ? Math.floor(clampedRandom * (jitterSeconds + 1)) : 0;
  return (minIntervalSeconds + jitter) * 1_000;
}

export function resolveLoopStatePath({ pulseStateFile, loopStateFile }) {
  const explicit = trimToNull(loopStateFile);
  if (explicit) {
    return path.resolve(explicit);
  }
  return path.join(path.dirname(path.resolve(pulseStateFile)), DEFAULT_LOOP_STATE_FILE_NAME);
}

function parseOptions(argv) {
  const options = {
    configPath: trimToNull(process.env.AQUACLAW_HOSTED_CONFIG),
    failureJitterSeconds: parseNonNegativeInteger(
      process.env.AQUACLAW_HOSTED_PULSE_FAILURE_JITTER_SECONDS || DEFAULT_FAILURE_JITTER_SECONDS,
      'AQUACLAW_HOSTED_PULSE_FAILURE_JITTER_SECONDS',
    ),
    failureMinSeconds: parsePositiveInteger(
      process.env.AQUACLAW_HOSTED_PULSE_FAILURE_MIN_SECONDS || DEFAULT_FAILURE_MIN_SECONDS,
      'AQUACLAW_HOSTED_PULSE_FAILURE_MIN_SECONDS',
    ),
    feedLimit: parsePositiveInteger(
      process.env.AQUACLAW_HOSTED_PULSE_FEED_LIMIT || DEFAULT_FEED_LIMIT,
      'AQUACLAW_HOSTED_PULSE_FEED_LIMIT',
    ),
    jitterSeconds: parseNonNegativeInteger(
      process.env.AQUACLAW_HOSTED_PULSE_JITTER_SECONDS || DEFAULT_JITTER_SECONDS,
      'AQUACLAW_HOSTED_PULSE_JITTER_SECONDS',
    ),
    loopStateFile: trimToNull(process.env.AQUACLAW_HOSTED_PULSE_LOOP_STATE_FILE),
    minIntervalSeconds: parsePositiveInteger(
      process.env.AQUACLAW_HOSTED_PULSE_MIN_SECONDS || DEFAULT_MIN_INTERVAL_SECONDS,
      'AQUACLAW_HOSTED_PULSE_MIN_SECONDS',
    ),
    once: false,
    printPaths: false,
    pulseStateFile: trimToNull(process.env.AQUACLAW_HOSTED_PULSE_STATE),
    quietHours:
      process.env.AQUACLAW_HOSTED_PULSE_QUIET_HOURS !== undefined
        ? trimToNull(process.env.AQUACLAW_HOSTED_PULSE_QUIET_HOURS)
        : DEFAULT_QUIET_HOURS,
    socialCooldownMinutes: parsePositiveInteger(
      process.env.AQUACLAW_HOSTED_PULSE_SOCIAL_COOLDOWN_MINUTES || DEFAULT_SOCIAL_COOLDOWN_MINUTES,
      'AQUACLAW_HOSTED_PULSE_SOCIAL_COOLDOWN_MINUTES',
    ),
    socialDmCooldownMinutes: parsePositiveInteger(
      process.env.AQUACLAW_HOSTED_PULSE_DM_COOLDOWN_MINUTES || DEFAULT_DM_COOLDOWN_MINUTES,
      'AQUACLAW_HOSTED_PULSE_DM_COOLDOWN_MINUTES',
    ),
    socialDmTargetCooldownMinutes: parsePositiveInteger(
      process.env.AQUACLAW_HOSTED_PULSE_DM_TARGET_COOLDOWN_MINUTES || DEFAULT_DM_TARGET_COOLDOWN_MINUTES,
      'AQUACLAW_HOSTED_PULSE_DM_TARGET_COOLDOWN_MINUTES',
    ),
    timeZone: trimToNull(process.env.AQUACLAW_HOSTED_PULSE_TIMEZONE) || DEFAULT_TIME_ZONE,
    timeoutMs: parsePositiveInteger(
      process.env.AQUACLAW_HOSTED_PULSE_TIMEOUT_MS || DEFAULT_PULSE_TIMEOUT_MS,
      'AQUACLAW_HOSTED_PULSE_TIMEOUT_MS',
    ),
    workspaceRoot: path.resolve(trimToNull(process.env.OPENCLAW_WORKSPACE_ROOT) || DEFAULT_WORKSPACE_ROOT),
  };

  for (const arg of argv) {
    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--once') {
      options.once = true;
      continue;
    }
    if (arg === '--print-paths') {
      options.printPaths = true;
      continue;
    }
    throw new Error(`unknown option: ${arg}`);
  }

  return options;
}

function resolvePaths(options) {
  const configPath = resolveHostedConfigPath({
    workspaceRoot: options.workspaceRoot,
    configPath: options.configPath || undefined,
  });
  const pulseStateFile = resolveHostedPulseStatePath({
    workspaceRoot: options.workspaceRoot,
    stateFile: options.pulseStateFile || undefined,
  });
  const loopStateFile = resolveLoopStatePath({
    pulseStateFile,
    loopStateFile: options.loopStateFile,
  });

  return {
    configPath,
    loopStateFile,
    pulseStateFile,
    workspaceRoot: options.workspaceRoot,
  };
}

async function loadLoopState(filePath) {
  try {
    const raw = await readFile(filePath, 'utf8');
    return JSON.parse(raw);
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return null;
    }
    return null;
  }
}

async function saveLoopState(filePath, state) {
  await mkdir(path.dirname(filePath), { recursive: true, mode: 0o700 });
  await writeFile(filePath, JSON.stringify(state, null, 2) + '\n', { mode: 0o600 });
  try {
    await chmod(filePath, 0o600);
  } catch {}
}

function log(level, message, extra = undefined) {
  const prefix = `[${new Date().toISOString()}] [${LABEL}] [${level}]`;
  if (extra === undefined) {
    console.log(`${prefix} ${message}`);
    return;
  }
  console.log(`${prefix} ${message} ${JSON.stringify(extra)}`);
}

function buildPulseArgs(options, paths) {
  const args = [
    PULSE_SCRIPT_PATH,
    '--format',
    'json',
    '--workspace-root',
    paths.workspaceRoot,
    '--config-path',
    paths.configPath,
    '--state-file',
    paths.pulseStateFile,
    '--feed-limit',
    String(options.feedLimit),
    '--social-pulse-cooldown-minutes',
    String(options.socialCooldownMinutes),
    '--social-pulse-dm-cooldown-minutes',
    String(options.socialDmCooldownMinutes),
    '--social-pulse-dm-target-cooldown-minutes',
    String(options.socialDmTargetCooldownMinutes),
    '--timezone',
    options.timeZone,
  ];

  if (options.quietHours) {
    args.push('--quiet-hours', options.quietHours);
  }

  return args;
}

function shortenText(value, maxLength = 500) {
  const text = String(value || '').trim();
  if (!text) {
    return null;
  }
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength)}...`;
}

function parsePulseOutput(stdout) {
  const trimmed = String(stdout || '').trim();
  if (!trimmed) {
    throw new Error('hosted pulse returned empty stdout');
  }
  try {
    return JSON.parse(trimmed);
  } catch {
    throw new Error('hosted pulse returned invalid JSON');
  }
}

function summarizePulse(summary) {
  return {
    authoringAgentId: summary?.socialPulse?.authoring?.agentId ?? null,
    authoringErrorCode: summary?.socialPulse?.authoring?.errorCode ?? null,
    authoringOpenClawBin: summary?.socialPulse?.authoring?.openclawBin ?? null,
    authoringStatus: summary?.socialPulse?.authoring?.status ?? null,
    generatedAt: summary?.generatedAt ?? null,
    heartbeatWritten: summary?.heartbeatWritten === true,
    hubUrl: summary?.hubUrl ?? null,
    rechargeItem:
      summary?.socialPulse?.planKind === 'recharge' ? summary?.socialPulse?.plan?.suggestedItem ?? null : null,
    rechargeVenue:
      summary?.socialPulse?.planKind === 'recharge' ? summary?.socialPulse?.plan?.venueName ?? null : null,
    runtimeStatus: summary?.runtime?.status ?? null,
    sceneGenerated: Boolean(summary?.generatedScene),
    sceneReason: summary?.sceneDecision?.reason ?? null,
    socialAction: summary?.socialPulse?.action ?? null,
    socialPlanKind: summary?.socialPulse?.planKind ?? null,
    socialReason: summary?.socialPulse?.reason ?? null,
    targetHandle:
      summary?.socialPulse?.plan?.targetGatewayHandle ??
      summary?.socialPulse?.plan?.replyToGatewayHandle ??
      null,
    warningCount: Array.isArray(summary?.warnings) ? summary.warnings.length : 0,
  };
}

function summarizeExecError(error) {
  const summary = {
    message: error instanceof Error ? error.message : String(error),
    name: error instanceof Error ? error.name : 'Error',
  };

  if (typeof error?.code === 'number') {
    summary.exitCode = error.code;
  } else if (typeof error?.code === 'string') {
    summary.code = error.code;
  }
  if (typeof error?.signal === 'string' && error.signal) {
    summary.signal = error.signal;
  }
  if (typeof error?.killed === 'boolean') {
    summary.killed = error.killed;
  }
  const stdoutPreview = shortenText(error?.stdout);
  if (stdoutPreview) {
    summary.stdout = stdoutPreview;
  }
  const stderrPreview = shortenText(error?.stderr);
  if (stderrPreview) {
    summary.stderr = stderrPreview;
  }
  return summary;
}

async function runTick(options, { passthroughOutput = false } = {}) {
  const paths = resolvePaths(options);
  const previousState = await loadLoopState(paths.loopStateFile);
  const startedAt = new Date().toISOString();

  await saveLoopState(paths.loopStateFile, {
    version: 1,
    label: LABEL,
    resolvedPaths: paths,
    status: 'running',
    lastAttemptAt: startedAt,
    lastSuccessAt: previousState?.lastSuccessAt ?? null,
    lastFailureAt: previousState?.lastFailureAt ?? null,
    lastExitCode: previousState?.lastExitCode ?? null,
    lastError: previousState?.lastError ?? null,
    lastSummary: previousState?.lastSummary ?? null,
    nextDelayMs: null,
    nextRunAt: null,
    sleepMode: null,
    updatedAt: startedAt,
  });

  try {
    const child = await execFileAsync(process.execPath, buildPulseArgs(options, paths), {
      cwd: paths.workspaceRoot,
      env: process.env,
      maxBuffer: MAX_OUTPUT_BYTES,
      timeout: options.timeoutMs,
    });
    const pulseSummary = parsePulseOutput(child.stdout);
    const completedAt = new Date().toISOString();
    const loopState = {
      version: 1,
      label: LABEL,
      resolvedPaths: paths,
      status: 'ok',
      lastAttemptAt: startedAt,
      lastSuccessAt: completedAt,
      lastFailureAt: previousState?.lastFailureAt ?? null,
      lastExitCode: 0,
      lastError: null,
      lastSummary: summarizePulse(pulseSummary),
      nextDelayMs: null,
      nextRunAt: null,
      sleepMode: null,
      updatedAt: completedAt,
    };
    await saveLoopState(paths.loopStateFile, loopState);

    if (passthroughOutput) {
      process.stdout.write(child.stdout.endsWith('\n') ? child.stdout : `${child.stdout}\n`);
    } else {
      log('info', 'hosted pulse tick completed', loopState.lastSummary);
    }
    if (child.stderr && child.stderr.trim()) {
      log('warn', 'hosted pulse tick emitted stderr', { stderr: shortenText(child.stderr) });
    }

    return {
      ok: true,
      paths,
      state: loopState,
    };
  } catch (error) {
    const completedAt = new Date().toISOString();
    const summarizedError = summarizeExecError(error);
    const loopState = {
      version: 1,
      label: LABEL,
      resolvedPaths: paths,
      status: 'error',
      lastAttemptAt: startedAt,
      lastSuccessAt: previousState?.lastSuccessAt ?? null,
      lastFailureAt: completedAt,
      lastExitCode: summarizedError.exitCode ?? null,
      lastError: summarizedError,
      lastSummary: previousState?.lastSummary ?? null,
      nextDelayMs: null,
      nextRunAt: null,
      sleepMode: null,
      updatedAt: completedAt,
    };
    await saveLoopState(paths.loopStateFile, loopState);

    if (passthroughOutput) {
      if (error?.stdout) {
        process.stdout.write(error.stdout.endsWith('\n') ? error.stdout : `${error.stdout}\n`);
      }
      if (error?.stderr) {
        process.stderr.write(error.stderr.endsWith('\n') ? error.stderr : `${error.stderr}\n`);
      }
    }

    log('error', 'hosted pulse tick failed', summarizedError);
    return {
      ok: false,
      paths,
      state: loopState,
    };
  }
}

function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

async function scheduleNextTick(options, { previousState = null, paths = null, sleepMode = 'normal' } = {}) {
  const resolvedPaths = paths || resolvePaths(options);
  const priorState = previousState || (await loadLoopState(resolvedPaths.loopStateFile));
  const delayMs =
    sleepMode === 'failure-retry'
      ? buildDelayMs(options.failureMinSeconds, options.failureJitterSeconds)
      : buildDelayMs(options.minIntervalSeconds, options.jitterSeconds);
  const nextRunAt = new Date(Date.now() + delayMs).toISOString();
  const state = {
    version: 1,
    label: LABEL,
    resolvedPaths,
    status: 'sleeping',
    lastAttemptAt: priorState?.lastAttemptAt ?? null,
    lastSuccessAt: priorState?.lastSuccessAt ?? null,
    lastFailureAt: priorState?.lastFailureAt ?? null,
    lastExitCode: priorState?.lastExitCode ?? null,
    lastError: priorState?.lastError ?? null,
    lastSummary: priorState?.lastSummary ?? null,
    nextDelayMs: delayMs,
    nextRunAt,
    sleepMode,
    updatedAt: new Date().toISOString(),
  };
  await saveLoopState(resolvedPaths.loopStateFile, state);
  log('info', 'scheduled next hosted pulse tick', {
    loopStateFile: resolvedPaths.loopStateFile,
    nextRunAt,
    seconds: Math.round(delayMs / 1_000),
    sleepMode,
  });
  await sleep(delayMs);
}

async function loop(options) {
  log('info', 'starting hosted pulse scheduler', {
    failureIntervalSeconds: {
      jitter: options.failureJitterSeconds,
      min: options.failureMinSeconds,
    },
    intervalSeconds: {
      jitter: options.jitterSeconds,
      min: options.minIntervalSeconds,
    },
    quietHours: options.quietHours,
    timeZone: options.timeZone,
    workspaceRoot: options.workspaceRoot,
  });

  await scheduleNextTick(options, { sleepMode: 'normal' });

  while (true) {
    const result = await runTick(options);
    await scheduleNextTick(options, {
      paths: result.paths,
      previousState: result.state,
      sleepMode: result.ok ? 'normal' : 'failure-retry',
    });
  }
}

async function main() {
  const options = parseOptions(process.argv.slice(2));

  if (options.printPaths) {
    console.log(JSON.stringify(resolvePaths(options), null, 2));
    return;
  }

  if (options.once) {
    const result = await runTick(options, { passthroughOutput: true });
    process.exit(result.ok ? 0 : 1);
  }

  await loop(options);
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (isMain) {
  try {
    await main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
