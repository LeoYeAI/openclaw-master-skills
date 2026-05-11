#!/usr/bin/env node

import { mkdir, writeFile } from 'node:fs/promises';
import process from 'node:process';

import {
  readEnvOptionalString,
  readEnvParsed,
  readEnvString,
  resolveWorkspaceRootFromEnv,
} from './env-readers.mjs';
import { loadHostedConfig, resolveHeartbeatStatePath } from './hosted-aqua-common.mjs';

const LABEL = 'ai.aquaclaw.runtime-heartbeat';
const VALID_MODES = new Set(['auto', 'local', 'hosted']);
const DEFAULT_WORKSPACE_ROOT = resolveWorkspaceRootFromEnv();
const DEFAULT_HUB_URL = 'http://127.0.0.1:8787';
const DEFAULT_MIN_INTERVAL_SECONDS = 15 * 60;
const DEFAULT_JITTER_SECONDS = 60;
const DEFAULT_CONNECT_TIMEOUT_MS = 8_000;
const DEFAULT_REPEAT_LOG_EVERY = 20;
const DEFAULT_STATE_FILE_DESCRIPTION = 'profile-aware resolver under the workspace .aquaclaw directory';
const DEFAULT_CONNECTION_TYPE = 'openclaw_runtime_heartbeat_service';

const localSessionCache = {
  identityId: null,
  identityKind: 'host',
  token: null,
};

function printHelp() {
  console.log(`Usage: aqua-runtime-heartbeat.mjs [--once] [--help]

Environment:
  OPENCLAW_WORKSPACE_ROOT                  OpenClaw workspace root
  AQUACLAW_HUB_URL                         Hub base URL (default: ${DEFAULT_HUB_URL})
  AQUACLAW_HEARTBEAT_MODE                  auto|local|hosted (default: auto)
  AQUACLAW_HOSTED_CONFIG                   Hosted Aqua config path override
  AQUACLAW_HEARTBEAT_MIN_SECONDS           Base interval seconds (default: ${DEFAULT_MIN_INTERVAL_SECONDS})
  AQUACLAW_HEARTBEAT_JITTER_SECONDS        Extra random interval seconds (default: ${DEFAULT_JITTER_SECONDS})
  AQUACLAW_HEARTBEAT_CONNECT_TIMEOUT_MS    Per-request timeout ms (default: ${DEFAULT_CONNECT_TIMEOUT_MS})
  AQUACLAW_HEARTBEAT_STATE_FILE            State file path (default: ${DEFAULT_STATE_FILE_DESCRIPTION})
  AQUACLAW_HEARTBEAT_CONNECTION_TYPE       Heartbeat connectionType (default: ${DEFAULT_CONNECTION_TYPE})

Notes:
  The preferred mainline path is still: openclaw cron -> aqua-runtime-heartbeat.sh --once.
  The looping service mode in this script is fallback-only.
  The default interval range is 15-16 minutes so the fallback stays compatible with Aqua's low-frequency heartbeat model.
  --once exits 0 for operational states like hub-down or runtime-unbound and 1 for actual script errors.
`);
}

function parsePositiveInteger(value, label) {
  const parsed = Number.parseInt(String(value), 10);
  if (!Number.isFinite(parsed) || parsed < 0) {
    throw new Error(`${label} must be a non-negative integer`);
  }
  return parsed;
}

function normalizeHubUrl(raw) {
  const url = new URL(String(raw || DEFAULT_HUB_URL).trim());
  url.pathname = '';
  url.search = '';
  url.hash = '';
  return url.toString().replace(/\/$/, '');
}

function parseOptions(argv) {
  const options = {
    connectionType: readEnvString('AQUACLAW_HEARTBEAT_CONNECTION_TYPE', DEFAULT_CONNECTION_TYPE),
    connectTimeoutMs: readEnvParsed(
      'AQUACLAW_HEARTBEAT_CONNECT_TIMEOUT_MS',
      DEFAULT_CONNECT_TIMEOUT_MS,
      parsePositiveInteger,
    ),
    hubUrl: normalizeHubUrl(readEnvString('AQUACLAW_HUB_URL', DEFAULT_HUB_URL)),
    hostedConfigPath: readEnvOptionalString('AQUACLAW_HOSTED_CONFIG'),
    jitterSeconds: readEnvParsed('AQUACLAW_HEARTBEAT_JITTER_SECONDS', DEFAULT_JITTER_SECONDS, parsePositiveInteger),
    minIntervalSeconds: readEnvParsed(
      'AQUACLAW_HEARTBEAT_MIN_SECONDS',
      DEFAULT_MIN_INTERVAL_SECONDS,
      parsePositiveInteger,
    ),
    mode: readEnvString('AQUACLAW_HEARTBEAT_MODE', 'auto').toLowerCase(),
    once: false,
    repeatLogEvery: DEFAULT_REPEAT_LOG_EVERY,
    stateFile: readEnvOptionalString('AQUACLAW_HEARTBEAT_STATE_FILE'),
    workspaceRoot: DEFAULT_WORKSPACE_ROOT,
  };

  for (const arg of argv) {
    if (arg === '--once') {
      options.once = true;
      continue;
    }
    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    throw new Error(`unknown option: ${arg}`);
  }

  if (!options.connectionType) {
    throw new Error('AQUACLAW_HEARTBEAT_CONNECTION_TYPE must not be empty');
  }
  if (!VALID_MODES.has(options.mode)) {
    throw new Error('AQUACLAW_HEARTBEAT_MODE must be auto, local, or hosted');
  }
  if (options.connectTimeoutMs < 1) {
    throw new Error('AQUACLAW_HEARTBEAT_CONNECT_TIMEOUT_MS must be at least 1');
  }
  options.stateFile = resolveHeartbeatStatePath({
    workspaceRoot: options.workspaceRoot,
    stateFile: options.stateFile,
    mode: options.mode,
  });
  return options;
}

function log(level, message, extra = undefined) {
  const prefix = `[${new Date().toISOString()}] [${LABEL}] [${level}]`;
  if (extra === undefined) {
    console.log(`${prefix} ${message}`);
    return;
  }
  console.log(`${prefix} ${message} ${JSON.stringify(extra)}`);
}

function redactError(error) {
  if (!(error instanceof Error)) {
    return { message: String(error) };
  }

  const base = {
    message: error.message,
    name: error.name,
  };

  if ('statusCode' in error && Number.isFinite(error.statusCode)) {
    base.statusCode = Number(error.statusCode);
  }

  return base;
}

async function requestJson(url, options, config) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), config.connectTimeoutMs);
  let response;

  try {
    response = await fetch(url, {
      method: options.method || 'GET',
      headers: {
        accept: 'application/json',
        ...(options.payload === undefined ? {} : { 'content-type': 'application/json' }),
        ...(options.headers || {}),
      },
      body: options.payload === undefined ? undefined : JSON.stringify(options.payload),
      signal: controller.signal,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const wrapped = new Error(`failed to reach ${url}: ${message}`);
    wrapped.cause = error;
    throw wrapped;
  } finally {
    clearTimeout(timeout);
  }

  const text = await response.text();
  let payload = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = { raw: text };
    }
  }

  if (!response.ok) {
    const error = new Error(
      payload?.error?.message || `${options.method || 'GET'} ${url} failed with HTTP ${response.status}`,
    );
    error.statusCode = response.status;
    error.payload = payload;
    throw error;
  }

  return payload;
}

async function loadHostedTarget(config) {
  const loaded = await loadHostedConfig({
    workspaceRoot: config.workspaceRoot,
    configPath: config.hostedConfigPath || undefined,
  });

  return {
    configPath: loaded.configPath,
    identityId: loaded.config?.gateway?.id || null,
    identityKind: 'gateway',
    hubUrl: loaded.config.hubUrl,
    mode: 'hosted',
    runtimeId: loaded.config.runtime.runtimeId,
    token: loaded.config.credential.token,
  };
}

async function writeState(filePath, state) {
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, `${JSON.stringify(state, null, 2)}\n`, 'utf8');
}

function buildDelayMs(config) {
  const jitterSeconds = config.jitterSeconds > 0
    ? Math.floor(Math.random() * (config.jitterSeconds + 1))
    : 0;
  return (config.minIntervalSeconds + jitterSeconds) * 1_000;
}

function summarizeResult(result) {
  if (result.kind === 'ok') {
    return {
      key: `ok:${result.presenceStatus || 'unknown'}:${result.runtimeStatus || 'unknown'}`,
      level: 'info',
      message: 'heartbeat ok',
      extra: {
        identityId: result.identityId,
        identityKind: result.identityKind,
        lastHeartbeatAt: result.lastHeartbeatAt,
        presenceStatus: result.presenceStatus,
        runtimeStatus: result.runtimeStatus,
      },
    };
  }

  if (result.kind === 'unbound') {
    return {
      key: 'unbound',
      level: 'warn',
      message: 'local runtime is not bound yet; heartbeat skipped',
      extra: {
        identityId: result.identityId,
        identityKind: result.identityKind,
      },
    };
  }

  if (result.kind === 'hub_unreachable') {
    return {
      key: 'hub_unreachable',
      level: 'warn',
      message: 'AquaClaw hub is unreachable; retrying',
      extra: {
        hubUrl: result.hubUrl,
        error: result.error.message,
      },
    };
  }

  if (result.kind === 'http_error') {
    return {
      key: `http_error:${result.statusCode}:${result.message}`,
      level: 'error',
      message: 'heartbeat request failed',
      extra: {
        error: result.message,
        statusCode: result.statusCode,
      },
    };
  }

  return {
    key: `internal_error:${result.message}`,
    level: 'error',
    message: 'heartbeat loop hit an internal error',
    extra: {
      error: result.message,
    },
  };
}

async function bootstrapLocalSession(config) {
  const bootstrap = await requestJson(
    `${config.hubUrl}/api/v1/session/bootstrap-local`,
    { method: 'POST' },
    config,
  );
  const token = bootstrap?.data?.credential?.token || null;
  if (!token) {
    throw new Error('bootstrap-local returned no local session token');
  }
  localSessionCache.token = token;
  localSessionCache.identityId =
    bootstrap?.data?.host?.id || bootstrap?.data?.gateway?.id || localSessionCache.identityId || null;
  localSessionCache.identityKind = bootstrap?.data?.host?.id ? 'host' : 'gateway';
  return {
    identityId: localSessionCache.identityId,
    identityKind: localSessionCache.identityKind,
    token,
  };
}

async function withLocalSession(config, action) {
  if (!localSessionCache.token) {
    await bootstrapLocalSession(config);
  }

  try {
    return await action(localSessionCache.token, localSessionCache.identityId, localSessionCache.identityKind);
  } catch (error) {
    if (!(error instanceof Error) || Number(error.statusCode) !== 401) {
      throw error;
    }

    await bootstrapLocalSession(config);
    return action(localSessionCache.token, localSessionCache.identityId, localSessionCache.identityKind);
  }
}

async function resolveHeartbeatTarget(config) {
  if (config.mode === 'local') {
    return {
      hubUrl: config.hubUrl,
      mode: 'local',
    };
  }

  if (config.mode === 'hosted') {
    return loadHostedTarget(config);
  }

  try {
    return await loadHostedTarget(config);
  } catch (error) {
    if (error instanceof Error && error.message.includes('hosted Aqua config not found')) {
      return {
        hubUrl: config.hubUrl,
        mode: 'local',
      };
    }
    throw error;
  }
}

async function runCycle(config) {
  const now = new Date().toISOString();
  const target = await resolveHeartbeatTarget(config);

  try {
    await requestJson(`${target.hubUrl}/health`, {}, config);
  } catch (error) {
    return {
      at: now,
      error: redactError(error),
      hubUrl: target.hubUrl,
      kind: 'hub_unreachable',
      mode: target.mode,
      operational: true,
    };
  }

  if (target.mode === 'hosted') {
    try {
      const runtime = await requestJson(
        `${target.hubUrl}/api/v1/runtime/remote/me`,
        {
          headers: {
            authorization: `Bearer ${target.token}`,
          },
        },
        config,
      );

      const heartbeat = await requestJson(
        `${target.hubUrl}/api/v1/runtime/remote/heartbeat`,
        {
          method: 'POST',
          headers: {
            authorization: `Bearer ${target.token}`,
          },
          payload: {
            runtimeId: target.runtimeId,
            connectionType: config.connectionType,
            metadata: {
              host: os.hostname(),
              intervalSeconds: {
                max: config.minIntervalSeconds + config.jitterSeconds,
                min: config.minIntervalSeconds,
              },
              label: LABEL,
              pid: process.pid,
              platform: process.platform,
              source: 'aquaclaw_skill_runtime_heartbeat',
              workspaceRoot: config.workspaceRoot,
            },
          },
        },
        config,
      );

      return {
        at: now,
        identityId: heartbeat?.data?.gateway?.id || runtime?.data?.gateway?.id || target.identityId || null,
        identityKind: target.identityKind,
        hubUrl: target.hubUrl,
        kind: 'ok',
        lastHeartbeatAt:
          heartbeat?.data?.runtime?.lastHeartbeatAt || runtime?.data?.runtime?.lastHeartbeatAt || null,
        mode: target.mode,
        operational: true,
        presenceStatus: heartbeat?.data?.presence?.status || runtime?.data?.presence?.status || null,
        runtimeStatus: heartbeat?.data?.runtime?.status || runtime?.data?.runtime?.status || null,
      };
    } catch (error) {
      if (error instanceof Error && Number(error.statusCode) === 404) {
        return {
          at: now,
          identityId: target.identityId || null,
          identityKind: target.identityKind,
          hubUrl: target.hubUrl,
          kind: 'unbound',
          mode: target.mode,
          operational: true,
        };
      }

      if (error instanceof Error && Number(error.statusCode) > 0) {
        return {
          at: now,
          hubUrl: target.hubUrl,
          kind: 'http_error',
          message: error.message,
          mode: target.mode,
          operational: false,
          statusCode: Number(error.statusCode),
        };
      }

      return {
        at: now,
        hubUrl: target.hubUrl,
        kind: 'internal_error',
        message: error instanceof Error ? error.message : String(error),
        mode: target.mode,
        operational: false,
      };
    }
  }

  try {
    return await withLocalSession(config, async (token, cachedIdentityId, cachedIdentityKind) => {
      let runtime;
      try {
        runtime = await requestJson(
          `${target.hubUrl}/api/v1/runtime/local`,
          {
            headers: {
              authorization: `Bearer ${token}`,
            },
          },
          config,
        );
      } catch (error) {
        if (error instanceof Error && Number(error.statusCode) === 404) {
          return {
            at: now,
            identityId: cachedIdentityId,
            identityKind: cachedIdentityKind,
            hubUrl: target.hubUrl,
            kind: 'unbound',
            mode: target.mode,
            operational: true,
          };
        }
        throw error;
      }

      const heartbeat = await requestJson(
        `${target.hubUrl}/api/v1/runtime/local/heartbeat`,
        {
          method: 'POST',
          headers: {
            authorization: `Bearer ${token}`,
          },
          payload: {
            connectionType: config.connectionType,
            metadata: {
              host: os.hostname(),
              intervalSeconds: {
                max: config.minIntervalSeconds + config.jitterSeconds,
                min: config.minIntervalSeconds,
              },
              label: LABEL,
              pid: process.pid,
              platform: process.platform,
              source: 'aquaclaw_skill_runtime_heartbeat',
              workspaceRoot: config.workspaceRoot,
            },
          },
        },
        config,
      );

      localSessionCache.identityId =
        heartbeat?.data?.host?.id ||
        runtime?.data?.host?.id ||
        heartbeat?.data?.gateway?.id ||
        runtime?.data?.gateway?.id ||
        cachedIdentityId ||
        localSessionCache.identityId;
      localSessionCache.identityKind =
        heartbeat?.data?.host?.id || runtime?.data?.host?.id ? 'host' : cachedIdentityKind || 'host';

      return {
        at: now,
        identityId: localSessionCache.identityId,
        identityKind: localSessionCache.identityKind,
        hubUrl: target.hubUrl,
        kind: 'ok',
        lastHeartbeatAt:
          heartbeat?.data?.runtime?.lastHeartbeatAt || runtime?.data?.runtime?.lastHeartbeatAt || null,
        mode: target.mode,
        operational: true,
        presenceStatus: heartbeat?.data?.presence?.status || runtime?.data?.presence?.status || null,
        runtimeStatus: heartbeat?.data?.runtime?.status || runtime?.data?.runtime?.status || null,
      };
    });
  } catch (error) {
    if (error instanceof Error && Number(error.statusCode) === 404) {
      return {
        at: now,
        identityId: localSessionCache.identityId,
        identityKind: localSessionCache.identityKind,
        hubUrl: target.hubUrl,
        kind: 'unbound',
        mode: target.mode,
        operational: true,
      };
    }

    if (error instanceof Error && Number(error.statusCode) > 0) {
      return {
        at: now,
        hubUrl: target.hubUrl,
        kind: 'http_error',
        message: error.message,
        mode: target.mode,
        operational: false,
        statusCode: Number(error.statusCode),
      };
    }

    return {
      at: now,
      hubUrl: target.hubUrl,
      kind: 'internal_error',
      message: error instanceof Error ? error.message : String(error),
      mode: target.mode,
      operational: false,
    };
  }
}

let stopRequested = false;
let repeatCount = 0;
let lastLogKey = null;

function installSignalHandlers() {
  const stop = (signal) => {
    if (stopRequested) {
      return;
    }
    stopRequested = true;
    log('info', 'received shutdown signal', { signal });
  };

  process.on('SIGINT', () => stop('SIGINT'));
  process.on('SIGTERM', () => stop('SIGTERM'));
}

async function sleep(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  installSignalHandlers();

  const serviceState = {
    config: {
      connectTimeoutMs: options.connectTimeoutMs,
      connectionType: options.connectionType,
      hubUrl: options.hubUrl,
      hostedConfigPath: options.hostedConfigPath,
      intervalSeconds: {
        max: options.minIntervalSeconds + options.jitterSeconds,
        min: options.minIntervalSeconds,
      },
      mode: options.mode,
      stateFile: options.stateFile,
      workspaceRoot: options.workspaceRoot,
    },
    label: LABEL,
    pid: process.pid,
    startedAt: new Date().toISOString(),
  };

  log('info', options.once ? 'running one-shot heartbeat attempt' : 'heartbeat daemon started', {
    hubUrl: options.hubUrl,
    hostedConfigPath: options.hostedConfigPath,
    intervalSeconds: serviceState.config.intervalSeconds,
    mode: options.mode,
    once: options.once,
    stateFile: options.stateFile,
    workspaceRoot: options.workspaceRoot,
  });

  while (!stopRequested) {
    const result = await runCycle(options);
    const summary = summarizeResult(result);

    if (summary.key !== lastLogKey) {
      lastLogKey = summary.key;
      repeatCount = 0;
      log(summary.level, summary.message, summary.extra);
    } else {
      repeatCount += 1;
      if (repeatCount % options.repeatLogEvery === 0) {
        log(summary.level, `${summary.message} (unchanged for ${repeatCount + 1} cycles)`, summary.extra);
      }
    }

    const nextDelayMs = buildDelayMs(options);
    await writeState(options.stateFile, {
      ...serviceState,
      lastResult: result,
      nextDelayMs: options.once ? null : nextDelayMs,
      updatedAt: new Date().toISOString(),
    });

    if (options.once) {
      process.exit(result.operational ? 0 : 1);
    }

    if (stopRequested) {
      break;
    }

    await sleep(nextDelayMs);
  }

  await writeState(options.stateFile, {
    ...serviceState,
    stoppedAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  });
}

main().catch(async (error) => {
  log('error', 'heartbeat daemon crashed before entering steady state', redactError(error));
  try {
    await writeState(DEFAULT_STATE_FILE, {
      crashedAt: new Date().toISOString(),
      error: redactError(error),
      label: LABEL,
      pid: process.pid,
    });
  } catch {
    // Ignore state write failures during crash handling.
  }
  process.exit(1);
});
