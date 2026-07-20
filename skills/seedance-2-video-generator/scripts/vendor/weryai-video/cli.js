const DEFAULT_SHORT_TASK_TIMEOUT_MS = 300_000;
const DEFAULT_LONG_TASK_TIMEOUT_MS = 1_200_000;

export async function runScript(argv, handler, helpText) {
  const flags = parseFlags(argv);

  if (flags.help) {
    process.stderr.write(helpText);
    return { ok: true, phase: 'help' };
  }

  const input = await resolveInput(flags);
  const ctx = createRuntimeContext(flags);

  try {
    const result = await handler(input, ctx);
    process.stdout.write(JSON.stringify(result, null, 2) + '\n');
    process.exit(result.ok ? 0 : 1);
  } catch (err) {
    const output = {
      ok: false,
      phase: 'failed',
      errorCode: null,
      errorMessage: err?.message ?? String(err),
    };
    process.stdout.write(JSON.stringify(output, null, 2) + '\n');
    process.exit(1);
  }
}

export function createRuntimeContext(flags) {
  const pollIntervalEnv = Number(process.env.WERYAI_POLL_INTERVAL_MS);
  const pollTimeoutEnv = Number(process.env.WERYAI_POLL_TIMEOUT_MS);
  const shortTimeoutEnv = Number(process.env.WERYAI_SHORT_TASK_TIMEOUT_MS);
  const longTimeoutEnv = Number(process.env.WERYAI_LONG_TASK_TIMEOUT_MS);

  return {
    apiKey: process.env.WERYAI_API_KEY || '',
    baseUrl: process.env.WERYAI_BASE_URL || 'https://api.weryai.com',
    modelsBaseUrl: process.env.WERYAI_MODELS_BASE_URL || 'https://api-growth-agent.weryai.com',
    verbose: flags.verbose,
    dryRun: flags.dryRun,
    requestTimeoutMs: Number(process.env.WERYAI_REQUEST_TIMEOUT_MS) || 30_000,
    pollIntervalMs: Number.isFinite(pollIntervalEnv) ? pollIntervalEnv : null,
    pollTimeoutMs: Number.isFinite(pollTimeoutEnv) && pollTimeoutEnv >= 0 ? pollTimeoutEnv : 600_000,
    pollTimeoutOverrideMs: Number.isFinite(pollTimeoutEnv) && pollTimeoutEnv >= 0 ? pollTimeoutEnv : null,
    shortTaskTimeoutMs: Number.isFinite(shortTimeoutEnv) && shortTimeoutEnv >= 0
      ? shortTimeoutEnv
      : DEFAULT_SHORT_TASK_TIMEOUT_MS,
    longTaskTimeoutMs: Number.isFinite(longTimeoutEnv) && longTimeoutEnv >= 0
      ? longTimeoutEnv
      : DEFAULT_LONG_TASK_TIMEOUT_MS,
  };
}

function parseFlags(argv) {
  const flags = {
    help: false,
    verbose: false,
    dryRun: false,
    json: null,
    params: {},
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') {
      flags.help = true;
    } else if (arg === '--verbose' || arg === '-v') {
      flags.verbose = true;
    } else if (arg === '--dry-run') {
      flags.dryRun = true;
    } else if (arg === '--json') {
      flags.json = argv[++i] ?? null;
    } else if (arg.startsWith('--') && i + 1 < argv.length && !argv[i + 1]?.startsWith('--')) {
      const key = arg.slice(2);
      flags.params[key] = argv[++i];
    } else if (arg.startsWith('--')) {
      const key = arg.slice(2);
      flags.params[key] = true;
    }
  }

  return flags;
}

async function resolveInput(flags) {
  if (flags.json === '-') {
    const chunks = [];
    for await (const chunk of process.stdin) {
      chunks.push(chunk);
    }
    const raw = Buffer.concat(chunks).toString('utf-8').trim();
    return raw ? JSON.parse(raw) : {};
  }

  if (flags.json) {
    return JSON.parse(flags.json);
  }

  const result = {};
  for (const [key, value] of Object.entries(flags.params)) {
    const camel = key.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
    result[camel] = value;
  }
  return result;
}
