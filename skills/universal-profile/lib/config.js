/**
 * Configuration Management
 * Handles loading, saving, and validating skill configuration
 */

import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';
import { CHAINS } from './constants.js';

/**
 * Default configuration
 */
const DEFAULT_CONFIG = {
  defaultChain: 'lukso',
  keystorePath: null, // Set dynamically
  chains: { ...CHAINS },
  profiles: {},
};

/**
 * Get the config directory path
 * @returns {string} Config directory path
 */
export function getConfigDir() {
  const home = os.homedir();
  return path.join(home, '.openclaw', 'skills', 'universal-profile');
}

/**
 * Get the config file path
 * @returns {string} Config file path
 */
export function getConfigPath() {
  return path.join(getConfigDir(), 'config.json');
}

/**
 * Get the keystore file path
 * @returns {string} Keystore file path
 */
export function getKeystorePath() {
  return path.join(getConfigDir(), 'keystore.json');
}

/**
 * Ensure the config directory exists
 */
async function ensureConfigDir() {
  const configDir = getConfigDir();
  try {
    await fs.mkdir(configDir, { recursive: true });
  } catch (err) {
    if (err.code !== 'EEXIST') {
      throw err;
    }
  }
}

/**
 * Load configuration from disk
 * @returns {Promise<Object>} Configuration object
 */
export async function loadConfig() {
  await ensureConfigDir();
  
  const configPath = getConfigPath();
  
  try {
    const data = await fs.readFile(configPath, 'utf8');
    const config = JSON.parse(data);
    
    // Merge with defaults for any missing keys
    return {
      ...DEFAULT_CONFIG,
      ...config,
      chains: {
        ...DEFAULT_CONFIG.chains,
        ...(config.chains || {}),
      },
      keystorePath: config.keystorePath || getKeystorePath(),
    };
  } catch (err) {
    if (err.code === 'ENOENT') {
      // Config doesn't exist, return defaults
      return {
        ...DEFAULT_CONFIG,
        keystorePath: getKeystorePath(),
      };
    }
    throw err;
  }
}

/**
 * Save configuration to disk
 * @param {Object} config - Configuration object
 */
export async function saveConfig(config) {
  await ensureConfigDir();
  
  const configPath = getConfigPath();
  const data = JSON.stringify(config, null, 2);
  
  await fs.writeFile(configPath, data, 'utf8');
}

/**
 * Allowed top-level config keys that can be modified via `config set`.
 * Restricting this prevents abuse (e.g. redirecting keystorePath).
 */
const ALLOWED_CONFIG_KEYS = new Set([
  'defaultChain',
]);

/**
 * Update a specific configuration value
 * @param {string} key - Configuration key (supports dot notation)
 * @param {*} value - Value to set
 * @returns {Promise<Object>} Updated configuration
 */
export async function setConfigValue(key, value) {
  // Security: only allow known safe keys to be modified
  const topKey = key.split('.')[0];
  if (!ALLOWED_CONFIG_KEYS.has(topKey)) {
    throw new Error(
      `Cannot modify "${key}" via config set. ` +
      `Allowed keys: ${[...ALLOWED_CONFIG_KEYS].join(', ')}. ` +
      `Sensitive paths (keystorePath, profiles) must be set during initial setup.`
    );
  }

  const config = await loadConfig();
  
  // Support dot notation (e.g., "chains.lukso.rpcUrl")
  const keys = key.split('.');
  let target = config;
  
  for (let i = 0; i < keys.length - 1; i++) {
    if (!(keys[i] in target)) {
      target[keys[i]] = {};
    }
    target = target[keys[i]];
  }
  
  target[keys[keys.length - 1]] = value;
  
  await saveConfig(config);
  return config;
}

/**
 * Get a specific configuration value
 * @param {string} key - Configuration key (supports dot notation)
 * @param {*} defaultValue - Default value if key not found
 * @returns {Promise<*>} Configuration value
 */
export async function getConfigValue(key, defaultValue = undefined) {
  const config = await loadConfig();
  
  const keys = key.split('.');
  let value = config;
  
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k];
    } else {
      return defaultValue;
    }
  }
  
  return value;
}

/**
 * Get chain configuration
 * @param {string} chainName - Chain name (lukso, lukso-testnet)
 * @returns {Promise<Object|null>} Chain configuration or null
 */
export async function getChainConfig(chainName) {
  const config = await loadConfig();
  return config.chains?.[chainName] || CHAINS[chainName] || null;
}

/**
 * Get profile configuration for a chain
 * @param {number|string} chainId - Chain ID or name
 * @returns {Promise<Object|null>} Profile configuration or null
 */
export async function getProfileConfig(chainId) {
  const config = await loadConfig();
  
  // Convert chain name to ID if necessary
  let id = chainId;
  if (typeof chainId === 'string' && isNaN(parseInt(chainId))) {
    const chainConfig = config.chains?.[chainId];
    if (chainConfig) {
      id = chainConfig.chainId;
    }
  }
  
  return config.profiles?.[id.toString()] || null;
}

/**
 * Save profile configuration for a chain
 * @param {number|string} chainId - Chain ID
 * @param {Object} profile - Profile configuration
 */
export async function saveProfileConfig(chainId, profile) {
  const config = await loadConfig();
  
  if (!config.profiles) {
    config.profiles = {};
  }
  
  config.profiles[chainId.toString()] = {
    ...config.profiles[chainId.toString()],
    ...profile,
    updatedAt: new Date().toISOString(),
  };
  
  await saveConfig(config);
}

/**
 * Validate configuration
 * @param {Object} config - Configuration to validate
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateConfig(config) {
  const errors = [];
  
  if (config.defaultChain && !CHAINS[config.defaultChain] && !config.chains?.[config.defaultChain]) {
    errors.push(`Unknown default chain: ${config.defaultChain}`);
  }
  
  if (config.chains) {
    for (const [name, chain] of Object.entries(config.chains)) {
      if (!chain.chainId) {
        errors.push(`Chain "${name}" is missing chainId`);
      }
      if (!chain.rpcUrl) {
        errors.push(`Chain "${name}" is missing rpcUrl`);
      }
    }
  }
  
  if (config.profiles) {
    for (const [chainId, profile] of Object.entries(config.profiles)) {
      if (profile.upAddress && !isValidAddress(profile.upAddress)) {
        errors.push(`Invalid UP address for chain ${chainId}`);
      }
      if (profile.keyManagerAddress && !isValidAddress(profile.keyManagerAddress)) {
        errors.push(`Invalid Key Manager address for chain ${chainId}`);
      }
      if (profile.controllerAddress && !isValidAddress(profile.controllerAddress)) {
        errors.push(`Invalid controller address for chain ${chainId}`);
      }
    }
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Check if a string is a valid Ethereum address
 * @param {string} address - Address to check
 * @returns {boolean}
 */
function isValidAddress(address) {
  return /^0x[a-fA-F0-9]{40}$/.test(address);
}

/**
 * Format configuration for display
 * @param {Object} config - Configuration object
 * @returns {string} Formatted configuration string
 */
export function formatConfig(config) {
  const lines = [];
  
  lines.push('┌─────────────────────────────────────┐');
  lines.push('│ Universal Profile Configuration     │');
  lines.push('├─────────────────────────────────────┤');
  lines.push(`│ Default Chain: ${config.defaultChain.padEnd(20)} │`);
  lines.push(`│ Keystore: ${(config.keystorePath ? '✓ Set' : '✗ Not set').padEnd(25)} │`);
  
  if (Object.keys(config.profiles || {}).length > 0) {
    lines.push('├─────────────────────────────────────┤');
    lines.push('│ Configured Profiles:                │');
    for (const [chainId, profile] of Object.entries(config.profiles)) {
      const chainName = Object.entries(config.chains).find(([, c]) => c.chainId === parseInt(chainId))?.[0] || chainId;
      const upShort = profile.upAddress ? `${profile.upAddress.slice(0, 6)}...${profile.upAddress.slice(-4)}` : 'N/A';
      lines.push(`│   ${chainName}: ${upShort.padEnd(23)} │`);
    }
  }
  
  lines.push('└─────────────────────────────────────┘');
  
  return lines.join('\n');
}

export default {
  getConfigDir,
  getConfigPath,
  getKeystorePath,
  loadConfig,
  saveConfig,
  setConfigValue,
  getConfigValue,
  getChainConfig,
  getProfileConfig,
  saveProfileConfig,
  validateConfig,
  formatConfig,
};
