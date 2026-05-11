import { readFileSync } from 'fs';
import { join } from 'path';
import yaml from 'js-yaml';
import { getAddress } from 'ethers6';

/**
 * Parse a .env file content into a plain object.
 * - Lines starting with # (after optional whitespace) are ignored.
 * - Blank / whitespace-only lines are ignored.
 * - Values may be surrounded by single or double quotes, which are stripped.
 */
function parseEnv(content) {
  const result = {};
  for (const raw of content.split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;

    const eqIndex = line.indexOf('=');
    if (eqIndex === -1) continue;

    const key = line.slice(0, eqIndex).trim();
    let value = line.slice(eqIndex + 1).trim();

    // Strip surrounding quotes (single or double)
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }

    if (key) {
      result[key] = value;
    }
  }
  return result;
}

/**
 * Load configuration from configDir.
 *
 * Reads:
 *   <configDir>/.env       — environment variables (key=value pairs)
 *   <configDir>/config.yaml — structured YAML config
 *
 * Both files are optional; missing files are silently treated as empty.
 *
 * @param {string} configDir  Path to the config directory (defaults to ~/.aurehub)
 * @returns {{ env: object, yaml: object, configDir: string }}
 */
export function loadConfig(configDir) {
  // Default to ~/.aurehub when no directory is supplied
  const dir = configDir ?? join(process.env.HOME ?? process.env.USERPROFILE ?? '', '.aurehub');

  let env = {};
  try {
    const raw = readFileSync(join(dir, '.env'), 'utf8');
    env = parseEnv(raw);
  } catch (err) {
    if (err.code !== 'ENOENT') throw err;
  }

  let yamlConfig = {};
  try {
    const raw = readFileSync(join(dir, 'config.yaml'), 'utf8');
    yamlConfig = yaml.load(raw, { schema: yaml.JSON_SCHEMA }) ?? {};
  } catch (err) {
    if (err.code !== 'ENOENT') throw err;
  }

  return { env, yaml: yamlConfig, configDir: dir };
}

/**
 * Resolve a token symbol to its address and decimals from config.yaml's `tokens` section.
 *
 * @param {{ yaml: object }} config  Config object returned by loadConfig
 * @param {string} symbol            Token symbol, e.g. "USDT"
 * @returns {{ address: string, decimals: number }}
 * @throws {Error} If the symbol is not found in the tokens section
 */
// Canonical mainnet addresses for tamper detection
const CANONICAL_TOKENS = {
  XAUT: '0x68749665FF8D2d112Fa859AA293F07A622782F38',
  USDT: '0xdAC17F958D2ee523a2206206994597C13D831ec7',
};
const CANONICAL_CONTRACTS = {
  router: '0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45',
  quoter: '0x61fFE014bA17989E743c5F6cB21bF9697530B21e',
  permit2: '0x000000000022D473030F116dDEE9F6B43aC78BA3',
};

export function resolveToken(config, symbol) {
  const tokens = config?.yaml?.tokens ?? {};
  const token = tokens[symbol];
  if (!token) {
    throw new Error(`Unknown token symbol: "${symbol}"`);
  }
  // Validate address against canonical value if known
  const canonical = CANONICAL_TOKENS[symbol];
  if (canonical && token.address.toLowerCase() !== canonical.toLowerCase()) {
    throw new Error(`Token ${symbol} address mismatch: config has ${token.address}, expected ${canonical}. Check config.yaml for tampering.`);
  }
  // Validate decimals
  if (typeof token.decimals !== 'number' || !Number.isInteger(token.decimals) || token.decimals < 0 || token.decimals > 18) {
    throw new Error(`Token ${symbol} has invalid decimals: ${token.decimals}`);
  }
  // Normalize to EIP-55 checksum to tolerate old config files with non-standard casing.
  return { address: getAddress(token.address.toLowerCase()), decimals: token.decimals };
}

export function validateContracts(config) {
  const contracts = config?.yaml?.contracts ?? {};
  for (const [name, canonical] of Object.entries(CANONICAL_CONTRACTS)) {
    if (contracts[name] && contracts[name].toLowerCase() !== canonical.toLowerCase()) {
      throw new Error(`Contract ${name} address mismatch: config has ${contracts[name]}, expected ${canonical}. Check config.yaml for tampering.`);
    }
    // Normalize to EIP-55 checksum to tolerate old config files with non-standard casing.
    if (contracts[name]) {
      contracts[name] = getAddress(contracts[name].toLowerCase());
    }
  }
}
