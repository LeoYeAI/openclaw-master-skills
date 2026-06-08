#!/usr/bin/env node

/**
 * Typefully CLI - Manage social media posts via the Typefully API
 * https://typefully.com/docs/api
 *
 * Zero dependencies - uses only Node.js built-in modules
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');

// Allow overriding API base for tests / self-hosted mocks.
const API_BASE = process.env.TYPEFULLY_API_BASE || 'https://api.typefully.com/v2';
const GLOBAL_CONFIG_DIR = path.join(os.homedir(), '.config', 'typefully');
const GLOBAL_CONFIG_FILE = path.join(GLOBAL_CONFIG_DIR, 'config.json');
const LOCAL_CONFIG_DIR = '.typefully';
const LOCAL_CONFIG_FILE = path.join(LOCAL_CONFIG_DIR, 'config.json');
const API_KEY_URL = 'https://typefully.com/?settings=api';

// Content-type mapping for media uploads
const CONTENT_TYPES = {
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  png: 'image/png',
  gif: 'image/gif',
  webp: 'image/webp',
  mp4: 'video/mp4',
  mov: 'video/quicktime',
  pdf: 'application/pdf',
};

// ============================================================================
// ANSI Color Helpers (no dependencies)
// Only apply colors when outputting to a TTY (terminal)

const isColorSupported = process.stderr.isTTY;

const colors = {
  reset: isColorSupported ? '\x1b[0m' : '',
  bold: isColorSupported ? '\x1b[1m' : '',
  dim: isColorSupported ? '\x1b[2m' : '',
  green: isColorSupported ? '\x1b[32m' : '',
  yellow: isColorSupported ? '\x1b[33m' : '',
  blue: isColorSupported ? '\x1b[34m' : '',
  cyan: isColorSupported ? '\x1b[36m' : '',
  white: isColorSupported ? '\x1b[37m' : '',
  gray: isColorSupported ? '\x1b[90m' : '',
};

// Formatting helpers
const fmt = {
  title: (text) => `${colors.bold}${colors.cyan}${text}${colors.reset}`,
  success: (text) => `${colors.green}✓${colors.reset} ${text}`,
  warn: (text) => `${colors.yellow}⚠${colors.reset}  ${text}`,
  info: (text) => `${colors.blue}→${colors.reset} ${text}`,
  dim: (text) => `${colors.dim}${text}${colors.reset}`,
  bold: (text) => `${colors.bold}${text}${colors.reset}`,
  link: (text) => `${colors.cyan}${text}${colors.reset}`,
  num: (n) => `${colors.yellow}${n}${colors.reset}`,
  label: (text) => `${colors.dim}${text}${colors.reset}`,
};

// ============================================================================
// Utilities
// ============================================================================

function output(data) {
  console.log(JSON.stringify(data, null, 2));
}

function error(message, details = {}) {
  output({ error: message, ...details });
  process.exit(1);
}

function readConfigFile(configPath) {
  try {
    if (fs.existsSync(configPath)) {
      const content = fs.readFileSync(configPath, 'utf-8');
      return JSON.parse(content);
    }
  } catch {
    // Invalid JSON or read error - ignore
  }
  return null;
}

function getApiKey() {
  // Priority 1: Environment variable
  if (process.env.TYPEFULLY_API_KEY) {
    return { source: 'environment variable', key: process.env.TYPEFULLY_API_KEY };
  }

  // Priority 2: Project-local config (./.typefully/config.json)
  const localConfigPath = path.join(process.cwd(), LOCAL_CONFIG_FILE);
  const localConfig = readConfigFile(localConfigPath);
  if (localConfig?.apiKey) {
    return { source: localConfigPath, key: localConfig.apiKey };
  }

  // Priority 3: User-global config (~/.config/typefully/config.json)
  const globalConfig = readConfigFile(GLOBAL_CONFIG_FILE);
  if (globalConfig?.apiKey) {
    return { source: GLOBAL_CONFIG_FILE, key: globalConfig.apiKey };
  }

  return null;
}

function getDefaultSocialSetId() {
  // Priority 1: Project-local config (./.typefully/config.json)
  const localConfigPath = path.join(process.cwd(), LOCAL_CONFIG_FILE);
  const localConfig = readConfigFile(localConfigPath);
  if (localConfig?.defaultSocialSetId) {
    return { source: localConfigPath, id: localConfig.defaultSocialSetId };
  }

  // Priority 2: User-global config (~/.config/typefully/config.json)
  const globalConfig = readConfigFile(GLOBAL_CONFIG_FILE);
  if (globalConfig?.defaultSocialSetId) {
    return { source: GLOBAL_CONFIG_FILE, id: globalConfig.defaultSocialSetId };
  }

  return null;
}

/**
 * Sort and format social sets for display.
 * Personal accounts (team: null) come first, then team accounts grouped by team name.
 * Returns array of { set, displayLine } objects maintaining selection index mapping.
 */
function formatSocialSetsForDisplay(socialSets) {
  // Separate personal and team accounts
  const personal = socialSets.filter(s => !s.team);
  const team = socialSets.filter(s => s.team);

  // Sort team accounts by team name
  team.sort((a, b) => (a.team.name || '').localeCompare(b.team.name || ''));

  // Combine: personal first, then team
  const sorted = [...personal, ...team];

  // Format each for display with colors
  return sorted.map((set, index) => {
    const num = fmt.num(`${index + 1}.`.padStart(3));
    const name = fmt.bold(set.name || 'Unnamed');
    const username = set.username ? fmt.dim(` @${set.username}`) : '';
    const teamLabel = set.team ? fmt.label(` [${set.team.name}]`) : '';
    const displayLine = `  ${num} ${name}${username}${teamLabel}`;
    return { set, displayLine, index: index + 1 };
  });
}

function requireSocialSetId(providedId) {
  if (providedId) {
    return providedId;
  }

  const defaultResult = getDefaultSocialSetId();
  if (defaultResult) {
    return defaultResult.id;
  }

  error('social_set_id is required', {
    hint: 'Run: typefully.js config:set-default to set a default, or provide it as an argument'
  });
}

/**
 * Resolve draft target for commands that accept [social_set_id] <draft_id>.
 * When a default social set is configured, a single argument is ambiguous,
 * so require --use-default to confirm intent.
 */
function resolveDraftTarget(positional, commandName, hasUseDefault) {
  // If two args provided, no ambiguity - first is social_set_id, second is draft_id
  if (positional.length >= 2) {
    return { socialSetId: positional[0], draftId: positional[1] };
  }

  // If no args, always an error
  if (positional.length === 0) {
    error('draft_id is required');
  }

  // Single arg case - this is where ambiguity can occur
  const singleArg = positional[0];
  const defaultResult = getDefaultSocialSetId();

  // If no default configured, the single arg must be draft_id (will error on missing social_set_id)
  if (!defaultResult) {
    error('draft_id is required', {
      hint: 'Provide both social_set_id and draft_id, or set a default social set with: typefully.js config:set-default'
    });
  }

  // Default is configured - require --use-default flag to confirm intent
  if (!hasUseDefault) {
    error(`Ambiguous arguments for ${commandName}`, {
      hint: `With a default social set configured, a single argument is interpreted as draft_id.
To confirm you want to use the default social set (${defaultResult.id}), add --use-default:
  typefully.js ${commandName} ${singleArg} --use-default

Or provide both arguments explicitly:
  typefully.js ${commandName} <social_set_id> <draft_id>`
    });
  }

  return { socialSetId: defaultResult.id, draftId: singleArg };
}

function requireApiKey() {
  const result = getApiKey();
  if (!result) {
    error(`API key not found. Run 'typefully.js setup' to configure your API key. Get your key at ${API_KEY_URL}`, {
      action: 'Run: typefully.js setup'
    });
  }
  return result.key;
}

async function apiRequest(method, endpoint, body = null, opts = {}) {
  const { exitOnError = true } = opts;
  const apiKey = requireApiKey();

  const options = {
    method,
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE}${endpoint}`, options);

  let data;
  const text = await response.text();
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { raw: text };
  }

  if (!response.ok) {
    if (exitOnError) {
      error(`HTTP ${response.status}`, { response: data });
    }
    const err = new Error(`HTTP ${response.status}`);
    err.response = data;
    err.status = response.status;
    throw err;
  }

  return data;
}

function parseArgs(args, spec = {}) {
  const result = { _positional: [] };
  let i = 0;

  while (i < args.length) {
    const arg = args[i];
    if (typeof arg !== 'string') {
      // This should never happen with process.argv, but can happen if we build argv arrays internally.
      error('Invalid argument type', { argument: arg });
    }

    if (arg.startsWith('--')) {
      const rawKey = arg.slice(2);
      const key = rawKey === 'scratchpad' ? 'notes' : rawKey;
      if (spec[key] === 'boolean') {
        result[key] = true;
        i++;
      } else if (i + 1 < args.length && !String(args[i + 1]).startsWith('--')) {
        result[key] = args[i + 1];
        i += 2;
      } else {
        if (rawKey === 'social-set-id' || rawKey === 'social_set_id') {
          error('--social-set-id (or --social_set_id) requires a value');
        }
        error(`${arg} requires a value`);
      }
    } else if (arg === '-f') {
      // Shorthand for --file
      if (i + 1 < args.length) {
        result.file = args[i + 1];
        i += 2;
      } else {
        error('-f requires a value');
      }
    } else if (arg === '-a') {
      // Shorthand for --append
      result.append = true;
      i++;
    } else {
      result._positional.push(arg);
      i++;
    }
  }

  return result;
}

function coerceFlagValueToString(value, flagName, { allowEmpty = false } = {}) {
  if (value === true || value == null) {
    error(`${flagName} requires a value`);
  }
  if (typeof value !== 'string' && typeof value !== 'number') {
    error(`${flagName} must be a string`);
  }
  const str = String(value);
  if (!allowEmpty && str.trim() === '') {
    error(`${flagName} requires a non-empty value`);
  }
  return str;
}

function pushStringFlag(argv, parsed, key, flagName, opts) {
  if (!Object.prototype.hasOwnProperty.call(parsed, key)) return;
  const value = coerceFlagValueToString(parsed[key], flagName, opts);
  argv.push(flagName, value);
}

function parseCsvArg(value, flagName) {
  // parseArgs sets missing values to true (e.g. `--tags --other-flag`)
  if (value === true) {
    error(`${flagName} requires a value`);
  }
  if (value == null) return null;
  if (typeof value !== 'string') {
    error(`${flagName} must be a string`);
  }
  if (value.trim() === '') return [];
  return value
    .split(',')
    .map(v => v.trim())
    .filter(Boolean);
}

function getSocialSetIdFromParsed(parsed) {
  // Support both kebab and snake case. (People often copy from API docs.)
  const value = parsed['social-set-id'] ?? parsed.social_set_id;
  if (value === true) {
    error('--social-set-id (or --social_set_id) requires a value');
  }
  if (value == null) return null;
  if (typeof value !== 'string') {
    error('--social-set-id (or --social_set_id) must be a string');
  }
  if (value.trim() === '') {
    error('--social-set-id (or --social_set_id) requires a non-empty value');
  }
  return value;
}

function resolveSocialSetIdFromParsed(parsed, positionalId) {
  const flagId = getSocialSetIdFromParsed(parsed);
  if (flagId && positionalId && flagId !== positionalId) {
    error('Conflicting social_set_id values', { positional: positionalId, flag: flagId });
  }
  return requireSocialSetId(flagId || positionalId);
}

function resolveDraftTargetFromParsed(parsed, commandName) {
  const positional = parsed._positional;
  const flagId = getSocialSetIdFromParsed(parsed);

  if (flagId) {
    // Support `[social_set_id] <draft_id>` and `<draft_id>` forms while still allowing --social-set-id.
    if (positional.length >= 2 && positional[0] !== flagId) {
      error('Conflicting social_set_id values', { positional: positional[0], flag: flagId });
    }
    const draftId = positional.length >= 2 ? positional[1] : positional[0];
    if (!draftId) {
      error('draft_id is required');
    }
    return { socialSetId: flagId, draftId };
  }

  return resolveDraftTarget(positional, commandName, parsed['use-default']);
}

function splitThreadText(text) {
  // Split on --- that appears on its own line. Support both LF and CRLF.
  // Allow surrounding spaces so " --- " still counts, but avoid matching longer runs like "----".
  return text.split(/\r?\n[ \t]*---[ \t]*\r?\n/).filter(t => t.trim());
}

function getContentType(filename) {
  const ext = path.extname(filename).slice(1).toLowerCase();
  return CONTENT_TYPES[ext] || 'application/octet-stream';
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function sanitizeFilename(filename) {
  // API pattern: (?i)^[a-zA-Z0-9_.()\\-]+\\.(jpg|jpeg|png|webp|gif|mp4|mov|pdf)$
  // Extract extension
  const ext = path.extname(filename).toLowerCase();
  const basename = path.basename(filename, path.extname(filename));

  // Replace invalid characters with underscores
  // Valid: letters, numbers, underscores, dots, parentheses, hyphens
  const sanitized = basename
    .replace(/[^a-zA-Z0-9_.()-]/g, '_')  // Replace invalid chars with underscore
    .replace(/_+/g, '_')                  // Collapse multiple underscores
    .replace(/^_|_$/g, '');               // Trim leading/trailing underscores

  // Ensure we have a valid name
  const finalName = sanitized || 'upload';

  return finalName + ext;
}

// ============================================================================
// Commands
// ============================================================================

async function cmdMeGet() {
  const data = await apiRequest('GET', '/me');
  output(data);
}

async function cmdSocialSetsList() {
  const data = await apiRequest('GET', '/social-sets?limit=50');
  output(data);
}

async function cmdSocialSetsGet(args) {
  const parsed = parseArgs(args);
  const socialSetId = resolveSocialSetIdFromParsed(parsed, parsed._positional[0]);

  const data = await apiRequest('GET', `/social-sets/${socialSetId}`);
  output(data);
}

function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stderr, // Use stderr so JSON output stays clean on stdout
  });

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

function writeConfig(configPath, config) {
  const configDir = path.dirname(configPath);
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2) + '\n', { mode: 0o600 });
}

async function cmdSetup(args) {
  const parsed = parseArgs(args, { 'no-default': 'boolean' });

  // Check if running in non-interactive mode (key provided as argument)
  let apiKey = parsed._positional[0] || parsed.key;
  let location = parsed.location || parsed.scope;
  const defaultSocialSetArg = parsed['default-social-set'];
  const noDefault = parsed['no-default'] === true || parsed['no-default'] === 'true';

  // Non-interactive mode when --key is provided
  const isNonInteractive = !!apiKey;

  // If key provided via argument, skip interactive prompt
  if (!apiKey) {
    console.error('');
    console.error(fmt.title('Typefully CLI Setup'));
    console.error('');
    console.error(fmt.dim('Sign up free at typefully.com if you don\'t have an account.'));
    console.error('');
    console.error(fmt.info(`Get your API key at: ${fmt.link(API_KEY_URL)}`));
    console.error('');
    apiKey = await prompt(`${colors.bold}Enter your Typefully API key:${colors.reset} `);
  }

  if (!apiKey) {
    error('API key is required');
  }

  // Determine location
  if (!location) {
    if (isNonInteractive) {
      // Default to global in non-interactive mode
      location = 'global';
    } else {
      console.error('');
      console.error(fmt.bold('Where should the API key be stored?'));
      console.error(`  ${fmt.num('1.')} Global ${fmt.dim('(~/.config/typefully/)')} ${fmt.label('- Available to all projects')}`);
      console.error(`  ${fmt.num('2.')} Local ${fmt.dim('(./.typefully/)')} ${fmt.label('- Only this project')}`);
      console.error('');
      const choice = await prompt(`${colors.bold}Choose location [1/2]${colors.reset} ${fmt.dim('(default: 1)')}: `);
      location = choice === '2' ? 'local' : 'global';
    }
  }

  const isLocal = location === 'local' || location === '2';
  const configPath = isLocal
    ? path.join(process.cwd(), LOCAL_CONFIG_FILE)
    : GLOBAL_CONFIG_FILE;

  // Read existing config to preserve other settings
  const existingConfig = readConfigFile(configPath) || {};
  const newConfig = { ...existingConfig, apiKey };

  writeConfig(configPath, newConfig);

  // Offer to add .typefully/ to .gitignore for local config
  if (isLocal) {
    const gitignorePath = path.join(process.cwd(), '.gitignore');
    if (fs.existsSync(gitignorePath)) {
      const gitignore = fs.readFileSync(gitignorePath, 'utf-8');
      if (!gitignore.includes('.typefully/') && !gitignore.includes('.typefully\n')) {
        if (isNonInteractive) {
          // Auto-add to .gitignore in non-interactive mode
          fs.appendFileSync(gitignorePath, '\n# Typefully config (contains API key)\n.typefully/\n');
          console.error(fmt.success('Added .typefully/ to .gitignore'));
        } else {
          console.error('');
          const addToGitignore = await prompt(`${colors.bold}Add .typefully/ to .gitignore?${colors.reset} ${fmt.dim('[Y/n]')}: `);
          if (addToGitignore.toLowerCase() !== 'n') {
            fs.appendFileSync(gitignorePath, '\n# Typefully config (contains API key)\n.typefully/\n');
            console.error(fmt.success('Added .typefully/ to .gitignore'));
          }
        }
      }
    } else {
      // No .gitignore exists - offer to create one to protect the API key
      if (isNonInteractive) {
        // Auto-create .gitignore in non-interactive mode
        fs.writeFileSync(gitignorePath, '# Typefully config (contains API key)\n.typefully/\n');
        console.error(fmt.success('Created .gitignore with .typefully/ entry'));
      } else {
        console.error('');
        console.error(fmt.warn('No .gitignore found. Your API key could be accidentally committed.'));
        const createGitignore = await prompt(`${colors.bold}Create .gitignore with .typefully/ entry?${colors.reset} ${fmt.dim('[Y/n]')}: `);
        if (createGitignore.toLowerCase() !== 'n') {
          fs.writeFileSync(gitignorePath, '# Typefully config (contains API key)\n.typefully/\n');
          console.error(fmt.success('Created .gitignore with .typefully/ entry'));
        } else {
          console.error(fmt.warn('Remember to add .typefully/ to .gitignore to protect your API key'));
        }
      }
    }
  }

  console.error('');
  console.error(fmt.success(`API key saved to ${fmt.dim(configPath)}`));

  // Handle default social set
  let defaultSocialSetId = null;

  // If --default-social-set was provided, validate it before saving
  if (defaultSocialSetArg) {
    // Validate the social set exists via API
    const origKey = process.env.TYPEFULLY_API_KEY;
    process.env.TYPEFULLY_API_KEY = apiKey;
    try {
      await apiRequest('GET', `/social-sets/${defaultSocialSetArg}`, null, { exitOnError: false });
    } catch {
      if (origKey) {
        process.env.TYPEFULLY_API_KEY = origKey;
      } else {
        delete process.env.TYPEFULLY_API_KEY;
      }
      error(`Social set ${defaultSocialSetArg} not found or not accessible`);
    }
    if (origKey) {
      process.env.TYPEFULLY_API_KEY = origKey;
    } else {
      delete process.env.TYPEFULLY_API_KEY;
    }

    defaultSocialSetId = defaultSocialSetArg;
    const updatedConfig = readConfigFile(configPath) || {};
    updatedConfig.defaultSocialSetId = defaultSocialSetId;
    writeConfig(configPath, updatedConfig);
    console.error(fmt.success(`Default social set saved: ${defaultSocialSetId}`));
  } else if (noDefault) {
    // Skip setting default social set
    console.error(fmt.dim('Skipping default social set configuration.'));
  } else {
    // Fetch social sets to determine what to do
    let socialSets = null;
    try {
      const origKey = process.env.TYPEFULLY_API_KEY;
      process.env.TYPEFULLY_API_KEY = apiKey;
      socialSets = await apiRequest('GET', '/social-sets?limit=50', null, { exitOnError: false });
      if (origKey) {
        process.env.TYPEFULLY_API_KEY = origKey;
      } else {
        delete process.env.TYPEFULLY_API_KEY;
      }
    } catch (err) {
      console.error(fmt.warn(`Could not fetch social sets: ${err.message}`));
      console.error(fmt.dim('You can set a default later with: typefully.js config:set-default'));
    }

    if (socialSets) {
      if (!socialSets.results || socialSets.results.length === 0) {
        // No social sets found - provide helpful guidance
        console.error('');
        console.error(fmt.warn('No social sets found.'));
        console.error(fmt.dim('To get started, connect a social account at typefully.com:'));
        console.error(fmt.info(`${fmt.link('https://typefully.com/?settings=accounts')}`));
        console.error('');
        console.error(fmt.dim('After connecting, run: typefully.js config:set-default'));
      } else if (socialSets.results.length === 1) {
        // Only one social set - auto-select it without asking
        defaultSocialSetId = socialSets.results[0].id;
        const updatedConfig = readConfigFile(configPath) || {};
        updatedConfig.defaultSocialSetId = defaultSocialSetId;
        writeConfig(configPath, updatedConfig);
        const name = socialSets.results[0].name || 'Unnamed';
        const username = socialSets.results[0].username ? `@${socialSets.results[0].username}` : '';
        console.error(fmt.success(`Default social set: ${fmt.bold(name)} ${fmt.dim(username)}`));
      } else if (isNonInteractive) {
        // Multiple social sets in non-interactive mode
        console.error(fmt.info(`Found ${socialSets.results.length} social sets. Use --default-social-set <id> to set one as default.`));
      } else {
        // Multiple social sets in interactive mode - ask user to choose
        const formatted = formatSocialSetsForDisplay(socialSets.results);

        console.error('');
        console.error(fmt.bold('Choose a default social set'));
        console.error(fmt.dim('This will be used when you don\'t specify one. You can always override it.'));
        console.error('');
        formatted.forEach(({ displayLine }) => console.error(displayLine));
        console.error('');

        const choice = await prompt(`${colors.bold}Enter number${colors.reset} ${fmt.dim('(or Enter to skip)')}: `);
        if (choice) {
          const choiceNum = parseInt(choice, 10);
          if (!isNaN(choiceNum) && choiceNum >= 1 && choiceNum <= formatted.length) {
            defaultSocialSetId = formatted[choiceNum - 1].set.id;
            const updatedConfig = readConfigFile(configPath) || {};
            updatedConfig.defaultSocialSetId = defaultSocialSetId;
            writeConfig(configPath, updatedConfig);
            console.error(fmt.success(`Default social set saved`));
          }
        }
      }
    }
  }

  output({
    success: true,
    message: 'Setup complete',
    config_path: configPath,
    scope: isLocal ? 'local' : 'global',
    default_social_set_id: defaultSocialSetId,
  });
}

async function cmdConfigShow() {
  const result = getApiKey();

  if (!result) {
    output({
      configured: false,
      hint: 'Run: typefully.js setup',
      api_key_url: API_KEY_URL,
    });
    return;
  }

  // Also show what config files exist
  const localConfigPath = path.join(process.cwd(), LOCAL_CONFIG_FILE);
  const localConfig = readConfigFile(localConfigPath);
  const globalConfig = readConfigFile(GLOBAL_CONFIG_FILE);

  // Get default social set info
  const defaultSocialSet = getDefaultSocialSetId();

  output({
    configured: true,
    active_source: result.source,
    api_key_preview: result.key.slice(0, 8) + '...',
    default_social_set: defaultSocialSet ? {
      id: defaultSocialSet.id,
      source: defaultSocialSet.source,
    } : null,
    config_files: {
      local: localConfig ? {
        path: localConfigPath,
        has_key: !!localConfig.apiKey,
        has_default_social_set: !!localConfig.defaultSocialSetId,
      } : null,
      global: globalConfig ? {
        path: GLOBAL_CONFIG_FILE,
        has_key: !!globalConfig.apiKey,
        has_default_social_set: !!globalConfig.defaultSocialSetId,
      } : null,
    },
  });
}

async function cmdConfigSetDefault(args) {
  const parsed = parseArgs(args);
  const socialSetIdFlag = getSocialSetIdFromParsed(parsed);
  let socialSetId = parsed._positional[0];
  if (socialSetIdFlag && socialSetId && socialSetIdFlag !== socialSetId) {
    error('Conflicting social_set_id values', { positional: socialSetId, flag: socialSetIdFlag });
  }
  socialSetId = socialSetIdFlag || socialSetId;
  let location = parsed.location || parsed.scope;

  // Ensure we have an API key first
  requireApiKey();

  // If no social_set_id provided, list available social sets and ask
  if (!socialSetId) {
    const socialSets = await apiRequest('GET', '/social-sets?limit=50');

    if (!socialSets.results || socialSets.results.length === 0) {
      error('No social sets found. Create one at typefully.com first.');
    }

    const formatted = formatSocialSetsForDisplay(socialSets.results);

    console.error(fmt.bold('Available social sets:'));
    console.error('');
    formatted.forEach(({ displayLine }) => console.error(displayLine));
    console.error('');

    if (formatted.length === 1) {
      // Only one social set - auto-select it
      socialSetId = formatted[0].set.id;
      console.error(fmt.success(`Auto-selecting: ${fmt.bold(formatted[0].set.name || 'Unnamed')}`));
    } else {
      const choice = await prompt(`${colors.bold}Enter number:${colors.reset} `);
      const choiceNum = parseInt(choice, 10);

      if (isNaN(choiceNum) || choiceNum < 1 || choiceNum > formatted.length) {
        error('Invalid selection');
      }

      socialSetId = formatted[choiceNum - 1].set.id;
    }
  }

  // Verify the social set exists
  try {
    await apiRequest('GET', `/social-sets/${socialSetId}`, null, { exitOnError: false });
  } catch {
    error(`Social set ${socialSetId} not found or not accessible`);
  }

  // Determine location
  if (!location) {
    console.error('');
    console.error(fmt.bold('Where should the default be stored?'));
    console.error(`  ${fmt.num('1.')} Global ${fmt.dim('(~/.config/typefully/)')} ${fmt.label('- Available to all projects')}`);
    console.error(`  ${fmt.num('2.')} Local ${fmt.dim('(./.typefully/)')} ${fmt.label('- Only this project')}`);
    console.error('');
    const choice = await prompt(`${colors.bold}Choose location [1/2]${colors.reset} ${fmt.dim('(default: 1)')}: `);
    location = choice === '2' ? 'local' : 'global';
  }

  const isLocal = location === 'local' || location === '2';
  const configPath = isLocal
    ? path.join(process.cwd(), LOCAL_CONFIG_FILE)
    : GLOBAL_CONFIG_FILE;

  // Read existing config to preserve other settings
  const existingConfig = readConfigFile(configPath) || {};
  const newConfig = { ...existingConfig, defaultSocialSetId: socialSetId };

  writeConfig(configPath, newConfig);

  console.error('');
  console.error(fmt.success(`Default social set saved to ${fmt.dim(configPath)}`));

  output({
    success: true,
    message: 'Default social set configured',
    default_social_set_id: socialSetId,
    config_path: configPath,
    scope: isLocal ? 'local' : 'global',
  });
}

async function cmdDraftsList(args) {
  const parsed = parseArgs(args);
  const socialSetId = resolveSocialSetIdFromParsed(parsed, parsed._positional[0]);

  const params = new URLSearchParams();
  params.set('limit', parsed.limit || '10');
  if (parsed.status) params.set('status', parsed.status);
  if (parsed.tag) params.set('tag', parsed.tag);
  if (parsed.sort) params.set('order_by', parsed.sort);

  const data = await apiRequest('GET', `/social-sets/${socialSetId}/drafts?${params}`);
  output(data);
}

async function cmdDraftsGet(args) {
  const parsed = parseArgs(args, { 'use-default': 'boolean' });
  const { socialSetId, draftId } = resolveDraftTargetFromParsed(parsed, 'drafts:get');

  const data = await apiRequest('GET', `/social-sets/${socialSetId}/drafts/${draftId}`);
  output(data);
}

async function getFirstConnectedPlatform(socialSetId) {
  const socialSet = await apiRequest('GET', `/social-sets/${socialSetId}`);

  // Check each platform for connection
  // The API returns platforms as an object where each key exists if that platform is connected
  const platformOrder = ['x', 'linkedin', 'threads', 'bluesky', 'mastodon'];
  const platforms = socialSet.platforms || {};

  for (const platform of platformOrder) {
    if (platforms[platform]) {
      return platform;
    }
  }

  return null;
}

async function getAllConnectedPlatforms(socialSetId) {
  const socialSet = await apiRequest('GET', `/social-sets/${socialSetId}`);
  const platformOrder = ['x', 'linkedin', 'threads', 'bluesky', 'mastodon'];
  const platforms = socialSet.platforms || {};
  const connected = [];

  for (const platform of platformOrder) {
    if (platforms[platform]) {
      connected.push(platform);
    }
  }

  return connected;
}

async function cmdDraftsCreate(args) {
  const parsed = parseArgs(args, { share: 'boolean', all: 'boolean' });
  const socialSetId = resolveSocialSetIdFromParsed(parsed, parsed._positional[0]);

  // Get text content
  let text = parsed.text;
  if (parsed.file) {
    if (!fs.existsSync(parsed.file)) {
      error(`File not found: ${parsed.file}`);
    }
    text = fs.readFileSync(parsed.file, 'utf-8');
  }

  if (!text) {
    error('--text or --file is required');
  }

  // Determine platform(s)
  let platforms = parsed.platform;

  if (parsed.all && parsed.platform) {
    error('Cannot use both --all and --platform flags');
  }

  if (parsed.all) {
    // Get all connected platforms
    const allPlatforms = await getAllConnectedPlatforms(socialSetId);
    if (allPlatforms.length === 0) {
      error('No connected platforms found. Connect a platform at typefully.com');
    }
    platforms = allPlatforms.join(',');
  } else if (!platforms) {
    // Smart default: get first connected platform
    const defaultPlatform = await getFirstConnectedPlatform(socialSetId);
    if (!defaultPlatform) {
      error('No connected platforms found. Connect a platform at typefully.com or specify --platform');
    }
    platforms = defaultPlatform;
  }

  const platformList = platforms.split(',').map(p => p.trim());

  // Split text into posts (thread support)
  const posts = splitThreadText(text);

  // Parse media IDs
  const mediaIds = parsed.media ? parsed.media.split(',').map(m => m.trim()) : [];

  // Build posts array
  const postsArray = posts.map((postText, index) => {
    const post = { text: postText };
    // Attach media only to first post
    if (index === 0 && mediaIds.length > 0) {
      post.media_ids = mediaIds;
    }
    return post;
  });

  // Build platforms object
  const platformsObj = {};
  for (const platform of platformList) {
    const platformConfig = {
      enabled: true,
      posts: postsArray,
    };

    // X-specific settings
    if (platform === 'x' && (parsed['reply-to'] || parsed.community)) {
      platformConfig.settings = {};
      if (parsed['reply-to']) {
        platformConfig.settings.reply_to_url = parsed['reply-to'];
      }
      if (parsed.community) {
        platformConfig.settings.community_id = parsed.community;
      }
    }

    platformsObj[platform] = platformConfig;
  }

  // Build request body
  const body = { platforms: platformsObj };

  if (parsed.title) {
    body.draft_title = parsed.title;
  }

  if (parsed.schedule) {
    body.publish_at = parsed.schedule;
  }

  if (Object.prototype.hasOwnProperty.call(parsed, 'tags')) {
    body.tags = parseCsvArg(parsed.tags, '--tags');
  }

  if (parsed.share) {
    body.share = true;
  }

  if (parsed.notes) {
    body.scratchpad_text = parsed.notes;
  }

  const data = await apiRequest('POST', `/social-sets/${socialSetId}/drafts`, body);
  output(data);
}

async function cmdDraftsUpdate(args) {
  const parsed = parseArgs(args, { append: 'boolean', share: 'boolean', 'use-default': 'boolean' });
  const { socialSetId, draftId } = resolveDraftTargetFromParsed(parsed, 'drafts:update');

  // Get text content
  let text = parsed.text;
  if (parsed.file) {
    if (!fs.existsSync(parsed.file)) {
      error(`File not found: ${parsed.file}`);
    }
    text = fs.readFileSync(parsed.file, 'utf-8');
  }

  const body = {};

  if (text) {
    // Parse media IDs
    const mediaIds = parsed.media ? parsed.media.split(',').map(m => m.trim()) : [];

    // Fetch existing draft to determine platforms (and for --append, to get posts)
    const existing = await apiRequest('GET', `/social-sets/${socialSetId}/drafts/${draftId}`);

    // Determine which platforms to update
    let platformList;
    if (parsed.platform) {
      // Explicit platform(s) specified
      platformList = parsed.platform.split(',').map(p => p.trim());
    } else {
      // Default to draft's existing enabled platforms
      platformList = Object.entries(existing.platforms || {})
        .filter(([, config]) => config.enabled)
        .map(([platform]) => platform);

      if (platformList.length === 0) {
        // Fallback: get first connected platform for this social set
        const defaultPlatform = await getFirstConnectedPlatform(socialSetId);
        if (!defaultPlatform) {
          error('No connected platforms found. Connect a platform at typefully.com or specify --platform');
        }
        platformList = [defaultPlatform];
      }
    }

    let postsArray;

    if (parsed.append) {
      // Extract posts from the first enabled platform
      let existingPosts = [];
      for (const [, config] of Object.entries(existing.platforms || {})) {
        if (config.enabled && config.posts) {
          existingPosts = config.posts;
          break;
        }
      }

      // Append new post
      const newPost = { text };
      if (mediaIds.length > 0) {
        newPost.media_ids = mediaIds;
      }
      postsArray = [...existingPosts, newPost];
    } else {
      // Replace with new posts
      const posts = splitThreadText(text);
      postsArray = posts.map((postText, index) => {
        const post = { text: postText };
        if (index === 0 && mediaIds.length > 0) {
          post.media_ids = mediaIds;
        }
        return post;
      });
    }

    // Build platforms object
    const platformsObj = {};
    for (const p of platformList) {
      platformsObj[p] = {
        enabled: true,
        posts: postsArray,
      };
    }
    body.platforms = platformsObj;
  }

  if (parsed.title) {
    body.draft_title = parsed.title;
  }

  if (parsed.schedule) {
    body.publish_at = parsed.schedule;
  }

  if (parsed.share) {
    body.share = true;
  }

  if (parsed.notes) {
    body.scratchpad_text = parsed.notes;
  }

  if (Object.prototype.hasOwnProperty.call(parsed, 'tags')) {
    body.tags = parseCsvArg(parsed.tags, '--tags');
  }

  if (Object.keys(body).length === 0) {
    error('At least one of --text, --file, --title, --schedule, --share, --notes, or --tags is required');
  }

  const data = await apiRequest('PATCH', `/social-sets/${socialSetId}/drafts/${draftId}`, body);
  output(data);
}

// ---------------------------------------------------------------------------
// Aliases (human/agent-friendly)
// ---------------------------------------------------------------------------

async function cmdCreateDraftAlias(args) {
  const parsed = parseArgs(args, { share: 'boolean', all: 'boolean' });
  const socialSetId = requireSocialSetId(getSocialSetIdFromParsed(parsed));

  const forwarded = [String(socialSetId)];

  // Prefer explicit --file / --text, otherwise treat positional args as the draft content.
  if (Object.prototype.hasOwnProperty.call(parsed, 'file')) {
    forwarded.push('--file', coerceFlagValueToString(parsed.file, '--file'));
  } else {
    let text;
    if (Object.prototype.hasOwnProperty.call(parsed, 'text')) {
      text = coerceFlagValueToString(parsed.text, '--text');
    } else {
      if (parsed._positional.length === 0) {
        error('Draft text is required (provide it as the first argument, or use --text/--file)');
      }
      text = parsed._positional.join(' ');
    }
    forwarded.push('--text', text);
  }

  pushStringFlag(forwarded, parsed, 'platform', '--platform');
  if (parsed.all) forwarded.push('--all');
  pushStringFlag(forwarded, parsed, 'media', '--media');
  pushStringFlag(forwarded, parsed, 'title', '--title');
  pushStringFlag(forwarded, parsed, 'schedule', '--schedule');
  pushStringFlag(forwarded, parsed, 'tags', '--tags', { allowEmpty: true });
  pushStringFlag(forwarded, parsed, 'reply-to', '--reply-to');
  pushStringFlag(forwarded, parsed, 'community', '--community');
  if (parsed.share) forwarded.push('--share');
  pushStringFlag(forwarded, parsed, 'notes', '--notes');

  await cmdDraftsCreate(forwarded);
}

async function cmdUpdateDraftAlias(args) {
  const parsed = parseArgs(args, { append: 'boolean', share: 'boolean' });
  const socialSetId = requireSocialSetId(getSocialSetIdFromParsed(parsed));

  if (parsed._positional.length === 0) {
    error('draft_id is required');
  }
  const draftId = parsed._positional[0];

  // Optional positional text after draft_id:
  // `update-draft <id> "New text" ...`
  let text;
  if (Object.prototype.hasOwnProperty.call(parsed, 'text')) {
    text = coerceFlagValueToString(parsed.text, '--text');
  } else if (!Object.prototype.hasOwnProperty.call(parsed, 'file') && parsed._positional.length > 1) {
    text = parsed._positional.slice(1).join(' ');
  }

  const forwarded = [String(socialSetId), String(draftId)];
  pushStringFlag(forwarded, parsed, 'platform', '--platform');
  if (text) forwarded.push('--text', text);
  if (Object.prototype.hasOwnProperty.call(parsed, 'file')) {
    forwarded.push('--file', coerceFlagValueToString(parsed.file, '--file'));
  }
  pushStringFlag(forwarded, parsed, 'media', '--media');
  if (parsed.append) forwarded.push('--append');
  pushStringFlag(forwarded, parsed, 'title', '--title');
  pushStringFlag(forwarded, parsed, 'schedule', '--schedule');
  pushStringFlag(forwarded, parsed, 'tags', '--tags', { allowEmpty: true });
  if (parsed.share) forwarded.push('--share');
  pushStringFlag(forwarded, parsed, 'notes', '--notes');

  await cmdDraftsUpdate(forwarded);
}

async function cmdDraftsDelete(args) {
  const parsed = parseArgs(args, { 'use-default': 'boolean' });
  // Destructive operation - require explicit --use-default when using default with single arg
  const { socialSetId, draftId } = resolveDraftTargetFromParsed(parsed, 'drafts:delete');

  await apiRequest('DELETE', `/social-sets/${socialSetId}/drafts/${draftId}`);
  output({ success: true, message: 'Draft deleted' });
}

async function cmdDraftsSchedule(args) {
  const parsed = parseArgs(args, { 'use-default': 'boolean' });
  // Destructive operation - require explicit --use-default when using default with single arg
  const { socialSetId, draftId } = resolveDraftTargetFromParsed(parsed, 'drafts:schedule');

  if (!parsed.time) {
    error('--time is required (use "next-free-slot" or ISO datetime)');
  }

  const data = await apiRequest('PATCH', `/social-sets/${socialSetId}/drafts/${draftId}`, {
    publish_at: parsed.time,
  });
  output(data);
}

async function cmdDraftsPublish(args) {
  const parsed = parseArgs(args, { 'use-default': 'boolean' });
  // Destructive operation - require explicit --use-default when using default with single arg
  const { socialSetId, draftId } = resolveDraftTargetFromParsed(parsed, 'drafts:publish');

  const data = await apiRequest('PATCH', `/social-sets/${socialSetId}/drafts/${draftId}`, {
    publish_at: 'now',
  });
  output(data);
}

async function cmdTagsList(args) {
  const parsed = parseArgs(args);
  const socialSetId = resolveSocialSetIdFromParsed(parsed, parsed._positional[0]);

  const data = await apiRequest('GET', `/social-sets/${socialSetId}/tags?limit=50`);
  output(data);
}

async function cmdTagsCreate(args) {
  const parsed = parseArgs(args);
  const socialSetId = resolveSocialSetIdFromParsed(parsed, parsed._positional[0]);

  if (!parsed.name) {
    error('--name is required');
  }

  const data = await apiRequest('POST', `/social-sets/${socialSetId}/tags`, {
    name: parsed.name,
  });
  output(data);
}

async function cmdMediaUpload(args) {
  const parsed = parseArgs(args, { 'no-wait': 'boolean' });
  const positional = parsed._positional;

  // Support both: media:upload <file_path> (with default) and media:upload <social_set_id> <file_path>
  let socialSetId, filePath;
  const socialSetIdFlag = getSocialSetIdFromParsed(parsed);
  if (positional.length >= 2) {
    if (socialSetIdFlag && positional[0] !== socialSetIdFlag) {
      error('Conflicting social_set_id values', { positional: positional[0], flag: socialSetIdFlag });
    }
    socialSetId = socialSetIdFlag || positional[0];
    filePath = positional[1];
  } else if (positional.length === 1) {
    filePath = positional[0];
    socialSetId = requireSocialSetId(socialSetIdFlag);
  } else {
    error('file path is required');
  }

  if (!fs.existsSync(filePath)) {
    error(`File not found: ${filePath}`);
  }

  const rawFilename = path.basename(filePath);
  const filename = sanitizeFilename(rawFilename);
  const timeout = parseInt(parsed.timeout || '60', 10) * 1000;
  const pollIntervalMs = (() => {
    const raw = process.env.TYPEFULLY_MEDIA_POLL_INTERVAL_MS;
    if (!raw) return 2000;
    const n = parseInt(raw, 10);
    return Number.isFinite(n) && n >= 0 ? n : 2000;
  })();

  // Step 1: Get presigned URL from API
  const presignedResponse = await apiRequest('POST', `/social-sets/${socialSetId}/media/upload`, {
    file_name: filename,
  });

  const { upload_url: uploadUrl, media_id: mediaId } = presignedResponse;

  if (!uploadUrl) {
    error('Failed to get presigned URL', { response: presignedResponse });
  }

  // Step 2: Upload file to S3 (WITHOUT Content-Type header - this was the bug!)
  const fileBuffer = fs.readFileSync(filePath);

  const uploadResponse = await fetch(uploadUrl, {
    method: 'PUT',
    body: fileBuffer,
    // Note: Do NOT set Content-Type header - S3 presigned URLs have it encoded
  });

  if (!uploadResponse.ok) {
    error('Failed to upload file to S3', {
      http_code: uploadResponse.status,
      status_text: uploadResponse.statusText,
    });
  }

  // Step 3: Poll for processing status (unless --no-wait)
  if (parsed['no-wait']) {
    output({
      media_id: mediaId,
      message: 'Upload complete. Use media:status to check processing.',
    });
    return;
  }

  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    const statusResponse = await apiRequest('GET', `/social-sets/${socialSetId}/media/${mediaId}`);

    if (statusResponse.status === 'ready') {
      output({
        media_id: mediaId,
        status: statusResponse.status,
        message: 'Media uploaded and ready to use',
      });
      return;
    }

    if (statusResponse.status === 'error' || statusResponse.status === 'failed') {
      error('Media processing failed', { status: statusResponse });
    }

    // Wait before polling again (override for tests with TYPEFULLY_MEDIA_POLL_INTERVAL_MS)
    await sleep(pollIntervalMs);
  }

  // Timeout reached
  output({
    media_id: mediaId,
    status: 'processing',
    message: 'Upload complete but still processing. Use media:status to check.',
    hint: 'Increase timeout with --timeout <seconds>',
  });
}

async function cmdMediaStatus(args) {
  const parsed = parseArgs(args);
  const positional = parsed._positional;

  // Support both: media:status <media_id> (with default) and media:status <social_set_id> <media_id>
  let socialSetId, mediaId;
  const socialSetIdFlag = getSocialSetIdFromParsed(parsed);
  if (positional.length >= 2) {
    if (socialSetIdFlag && positional[0] !== socialSetIdFlag) {
      error('Conflicting social_set_id values', { positional: positional[0], flag: socialSetIdFlag });
    }
    socialSetId = socialSetIdFlag || positional[0];
    mediaId = positional[1];
  } else if (positional.length === 1) {
    mediaId = positional[0];
    socialSetId = requireSocialSetId(socialSetIdFlag);
  } else {
    error('media_id is required');
  }

  const data = await apiRequest('GET', `/social-sets/${socialSetId}/media/${mediaId}`);
  output(data);
}

function showHelp() {
  console.log(`Typefully CLI - Manage social media posts via the Typefully API

USAGE:
  typefully.js <command> [arguments]

NOTE:
  Commands that take a social_set_id as a positional argument also accept:
    --social-set-id <id>   (or --social_set_id <id>)

SETUP:
  setup                                      Interactive setup - saves API key and optional default social set
    --key <api_key>                          Provide key non-interactively (enables non-interactive mode)
    --location <global|local>                Choose config location (default: global in non-interactive mode)
                                             global: ~/.config/typefully/config.json
                                             local: ./.typefully/config.json (project-specific)
    --default-social-set <id>                Set default social set non-interactively
    --no-default                             Skip setting default social set in non-interactive mode

  config:show                                Show current config, API key source, and default social set
  config:set-default [social_set_id]         Set default social set (interactive if ID not provided)
    --location <global|local>                Choose where to store the default

COMMANDS:
  me:get                                     Get authenticated user info

  social-sets:list                           List all social sets
  social-sets:get [social_set_id]            Get social set details with platforms (uses default if ID omitted)

  drafts:list [social_set_id] [options]      List drafts (uses default if ID omitted)
    --status <status>                        Filter by: draft, scheduled, published, error, publishing
    --tag <tag_slug>                         Filter by tag slug
    --sort <order>                           Sort by: created_at, -created_at, updated_at, -updated_at,
                                             scheduled_date, -scheduled_date, published_at, -published_at
    --limit <n>                              Max results (default: 10, max: 50)

  drafts:get [social_set_id] <draft_id>      Get a specific draft
    --use-default                            Required when using default social set with single arg

  drafts:create [social_set_id] [options]    Create a new draft (uses default if ID omitted)
    --platform <platforms>                   Comma-separated: x,linkedin,threads,bluesky,mastodon
                                             (auto-selects first connected platform if omitted)
    --all                                    Post to all connected platforms
    --text <text>                            Post content (use --- on its own line for threads)
    --file, -f <path>                        Read content from file instead of --text
    --media <media_ids>                      Comma-separated media IDs to attach
    --title <title>                          Draft title (internal only)
    --schedule <time>                        "now", "next-free-slot", or ISO datetime
    --tags <tag_slugs>                       Comma-separated tag slugs
    --reply-to <url>                         URL of X post to reply to
    --community <id>                         X community ID to post to
    --share                                  Generate a public share URL for the draft
    --notes, --scratchpad <text>             Internal notes/scratchpad for the draft

  drafts:update [social_set_id] <draft_id> [options]  Update a draft
    --platform <platforms>                   Comma-separated platforms
                                             (preserves draft's existing platforms if omitted)
    --text <text>                            New post content
    --file, -f <path>                        Read content from file instead of --text
    --media <media_ids>                      Comma-separated media IDs to attach
    --append, -a                             Append to existing thread instead of replacing
    --title <title>                          New draft title
    --schedule <time>                        "now", "next-free-slot", or ISO datetime
    --tags <tag_slugs>                       Comma-separated tag slugs
    --share                                  Generate a public share URL for the draft
    --notes, --scratchpad <text>             Internal notes/scratchpad for the draft
    --use-default                            Required when using default social set with single arg

  create-draft <text> [options]             Alias for drafts:create (positional text + --social-set-id)
  update-draft <draft_id> [text] [options]  Alias for drafts:update (positional text optional + --social-set-id)

  drafts:delete <social_set_id> <draft_id>   Delete a draft
    --use-default                            Required when using default social set with single arg

  drafts:schedule <social_set_id> <draft_id> [options]  Schedule a draft
    --time <time>                            "next-free-slot" or ISO datetime (required)
    --use-default                            Required when using default social set with single arg

  drafts:publish <social_set_id> <draft_id>  Publish a draft immediately
    --use-default                            Required when using default social set with single arg

  tags:list [social_set_id]                  List all tags (uses default if ID omitted)
  tags:create [social_set_id] --name <name>  Create a new tag (uses default if ID omitted)

  media:upload [social_set_id] <file>        Upload media file (uses default if one arg)
    --no-wait                                Return immediately after upload (don't poll)
    --timeout <seconds>                      Max wait for processing (default: 60)
  media:status [social_set_id] <media_id>    Check media upload status (uses default if one arg)

EXAMPLES:
  # First time setup (interactive)
  ./typefully.js setup

  # Non-interactive setup (for scripts/CI) - auto-selects default if only one social set
  ./typefully.js setup --key typ_xxx --location global

  # Non-interactive setup with explicit default social set
  ./typefully.js setup --key typ_xxx --location global --default-social-set 123

  # Non-interactive setup, skip default social set selection
  ./typefully.js setup --key typ_xxx --no-default

  # Check current configuration (shows API key source and default social set)
  ./typefully.js config:show

  # Set a default social set (interactive)
  ./typefully.js config:set-default

  # Set a default social set (non-interactive)
  ./typefully.js config:set-default 123 --location global

  # Get your user info
  ./typefully.js me:get

  # List all social sets
  ./typefully.js social-sets:list

  # Create a tweet (uses default social set if configured)
  ./typefully.js drafts:create --text "Hello world!"

  # Create a tweet with explicit social set ID
  ./typefully.js drafts:create 123 --text "Hello world!"

  # Create a cross-platform post (specific platforms)
  ./typefully.js drafts:create --platform x,linkedin --text "Big announcement!"

  # Create a post on all connected platforms
  ./typefully.js drafts:create --all --text "Posting everywhere!"

  # Create a thread (use --- on its own line to separate posts)
  ./typefully.js drafts:create 123 --platform x --text $'First tweet\\n---\\nSecond tweet\\n---\\nThird tweet'

  # Create from file
  ./typefully.js drafts:create 123 --platform x --file ./thread.txt

  # Schedule for next available slot
  ./typefully.js drafts:create 123 --platform x --text "Scheduled post" --schedule next-free-slot

  # Schedule for specific time
  ./typefully.js drafts:create 123 --platform x --text "Timed post" --schedule "2025-01-20T14:00:00Z"

  # List scheduled drafts sorted by date
  ./typefully.js drafts:list 123 --status scheduled --sort scheduled_date

  # Publish a draft immediately (explicit social_set_id and draft_id)
  ./typefully.js drafts:publish 123 456

  # Publish using default social set (requires --use-default for safety)
  ./typefully.js drafts:publish 456 --use-default

  # Delete a draft (requires --use-default when using default social set)
  ./typefully.js drafts:delete 456 --use-default

  # Append to existing thread
  ./typefully.js drafts:update 123 456 --append --text "New tweet at the end"

  # Reply to an existing tweet
  ./typefully.js drafts:create 123 --platform x --text "Great thread!" --reply-to "https://x.com/user/status/123456"

  # Post to an X community
  ./typefully.js drafts:create 123 --platform x --text "Community post" --community 1493446837214187523

  # Create draft with share URL
  ./typefully.js drafts:create 123 --platform x --text "Check this out" --share

  # Upload media and create post with it
  ./typefully.js media:upload 123 ./image.jpg
  # Returns: {"media_id": "abc-123", "status": "ready", "message": "Media uploaded and ready to use"}
  ./typefully.js drafts:create 123 --platform x --text "Check out this image!" --media abc-123

CONFIG PRIORITY:
  1. TYPEFULLY_API_KEY environment variable (highest)
  2. ./.typefully/config.json (project-local)
  3. ~/.config/typefully/config.json (user-global, lowest)

GET YOUR API KEY:
  ${API_KEY_URL}
`);
}

// ============================================================================
// Main Router
// ============================================================================

const COMMANDS = {
  'setup': cmdSetup,
  'me:get': cmdMeGet,
  'social-sets:list': cmdSocialSetsList,
  'social-sets:get': cmdSocialSetsGet,
  'drafts:list': cmdDraftsList,
  'drafts:get': cmdDraftsGet,
  'drafts:create': cmdDraftsCreate,
  'drafts:update': cmdDraftsUpdate,
  'create-draft': cmdCreateDraftAlias,
  'update-draft': cmdUpdateDraftAlias,
  'drafts:delete': cmdDraftsDelete,
  'drafts:schedule': cmdDraftsSchedule,
  'drafts:publish': cmdDraftsPublish,
  'tags:list': cmdTagsList,
  'tags:create': cmdTagsCreate,
  'media:upload': cmdMediaUpload,
  'media:status': cmdMediaStatus,
  'config:show': cmdConfigShow,
  'config:set-default': cmdConfigSetDefault,
  'help': showHelp,
  '--help': showHelp,
  '-h': showHelp,
};

async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';
  const commandArgs = args.slice(1);

  const handler = COMMANDS[command];

  if (!handler) {
    error(`Unknown command: ${command}`, { hint: 'Use --help for usage.' });
  }

  try {
    await handler(commandArgs);
  } catch (err) {
    if (err.code === 'ENOENT') {
      error(`File not found: ${err.path}`);
    }
    error(err.message, { stack: err.stack });
  }
}

main();
