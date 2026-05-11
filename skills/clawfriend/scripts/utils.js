#!/usr/bin/env node
/**
 * Utility functions for ClawFriend skill scripts
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Get OpenClaw config path
 */
export function getConfigPath() {
  const home = process.env.HOME || process.env.USERPROFILE;
  return path.join(home, '.openclaw', 'openclaw.json');
}

/**
 * Get ClawFriend state file path (for internal state like stepStatus)
 * Stored in workspace root, not in skills folder
 */
export function getClawFriendStatePath() {
  const home = process.env.HOME || process.env.USERPROFILE;
  return path.join(home, '.openclaw', 'workspace', '.clawfriend-state.json');
}

/**
 * Read ClawFriend state
 */
export function readClawFriendState() {
  const statePath = getClawFriendStatePath();
  if (!fs.existsSync(statePath)) {
    return {};
  }
  try {
    return JSON.parse(fs.readFileSync(statePath, 'utf8'));
  } catch (e) {
    return {};
  }
}

/**
 * Write ClawFriend state
 */
export function writeClawFriendState(state) {
  const statePath = getClawFriendStatePath();
  const dir = path.dirname(statePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
}

/**
 * Get state value
 */
export function getState(key, defaultValue = null) {
  const state = readClawFriendState();
  return state[key] !== undefined ? state[key] : defaultValue;
}

/**
 * Update state values
 */
export function updateState(updates) {
  const state = readClawFriendState();
  Object.assign(state, updates);
  writeClawFriendState(state);
}

/**
 * Read OpenClaw config
 */
export function readConfig() {
  const configPath = getConfigPath();
  if (!fs.existsSync(configPath)) {
    return { skills: { entries: {} } };
  }
  return JSON.parse(fs.readFileSync(configPath, 'utf8'));
}

/**
 * Write OpenClaw config
 */
export function writeConfig(config) {
  const configPath = getConfigPath();
  const dir = path.dirname(configPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
}

/**
 * Get ClawFriend config
 */
export function getClawFriendConfig() {
  const config = readConfig();
  return config.skills?.entries?.['clawfriend'] || {};
}

/**
 * Update ClawFriend config
 */
export function updateClawFriendConfig(updates) {
  const config = readConfig();
  if (!config.skills) config.skills = {};
  if (!config.skills.entries) config.skills.entries = {};
  if (!config.skills.entries['clawfriend']) {
    config.skills.entries['clawfriend'] = { enabled: true, env: {} };
  }
  
  const clawConfig = config.skills.entries['clawfriend'];
  
  // Merge updates
  Object.keys(updates).forEach(key => {
    if (key === 'env') {
      if (!clawConfig.env) clawConfig.env = {};
      Object.assign(clawConfig.env, updates.env);
    } else {
      clawConfig[key] = updates[key];
    }
  });
  
  writeConfig(config);
  return clawConfig;
}

/**
 * Get environment variable from config or process.env
 */
export function getEnv(key, defaultValue = null) {
  // Try process.env first
  if (process.env[key]) return process.env[key];
  
  // Try config
  const config = getClawFriendConfig();
  return config.env?.[key] || defaultValue;
}

/**
 * Get API base URL
 */
export function getApiBaseUrl() {
  return getEnv('API_DOMAIN', 'https://api.clawfriend.ai');
}

/**
 * Get API key
 */
export function getApiKey() {
  return getEnv('CLAW_FRIEND_API_KEY') || getClawFriendConfig().apiKey;
}

/**
 * Make API request
 * @param {string} endpoint - API path (e.g. /v1/agents/register)
 * @param {Object} options - fetch options; use noAuth: true to skip sending x-api-key (e.g. for recover)
 */
export async function apiRequest(endpoint, options = {}) {
  const { noAuth, skipApiKey, ...fetchOptions } = options;
  const omitApiKey = noAuth === true || skipApiKey === true;

  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}${endpoint}`;

  const headers = {
    'Content-Type': 'application/json',
    ...fetchOptions.headers
  };

  if (!omitApiKey) {
    const apiKey = getApiKey();
    if (apiKey && !headers['x-api-key']) {
      headers['x-api-key'] = apiKey;
    }
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers
  });
  
  const text = await response.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch (e) {
    data = { text };
  }
  
  if (!response.ok) {
    const error = new Error(`API Error: ${response.status} ${response.statusText}`);
    error.status = response.status;
    error.data = data;
    throw error;
  }
  
  // API responses are wrapped in { data: {...}, statusCode, message }
  // Return the inner data field, or the whole response if no data field
  return data.data || data;
}

/**
 * Check if ethers is installed, install if missing
 */
export async function ensureEthers() {
  try {
    // Check if node_modules/ethers exists in scripts directory
    const scriptsDir = __dirname;
    const ethersPath = path.join(scriptsDir, 'node_modules', 'ethers');
    
    if (!fs.existsSync(ethersPath)) {
      throw new Error('ethers not found');
    }
  } catch (e) {
    console.log('📦 Installing ethers...');
    try {
      await execAsync('npm install', { 
        cwd: __dirname,
        env: { ...process.env, NODE_ENV: 'production' }
      });
      success('ethers installed successfully!');
    } catch (installError) {
      error('Failed to install ethers');
      throw installError;
    }
  }
}

/**
 * Pretty print JSON
 */
export function prettyJson(obj) {
  return JSON.stringify(obj, null, 2);
}

/**
 * Check if agent is registered (has API key)
 * @param {boolean} showError - Whether to show error message
 * @returns {boolean} - True if API key exists
 */
export function checkApiKey(showError = true) {
  const apiKey = getApiKey();
  
  if (!apiKey) {
    if (showError) {
      error('Agent not registered!');
      console.log('\n❌ No API key found in config.');
      console.log('💡 This means the agent has not been successfully registered.\n');
      console.log('To register your agent, run:');
      console.log('  cd ~/.openclaw/workspace/skills/clawfriend');
      console.log('  node scripts/register.js agent "YourAgentName"\n');
      console.log('Make sure you have completed the setup first:');
      console.log('  node scripts/setup-check.js quick-setup\n');
    }
    return false;
  }
  
  return true;
}

/**
 * Log with emoji
 */
export function log(emoji, message) {
  console.log(`${emoji} ${message}`);
}

export function success(message) {
  log('✅', message);
}

export function error(message) {
  log('❌', message);
}

export function warning(message) {
  log('⚠️', message);
}

export function info(message) {
  log('ℹ️', message);
}
