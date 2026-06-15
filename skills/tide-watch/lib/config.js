/**
 * Configuration loader for Tide Watch
 * 
 * Precedence (highest to lowest):
 * 1. CLI flags (explicit user intent)
 * 2. Environment variables (session override)
 * 3. Config file (persistent preferences)
 * 4. Defaults (safe fallback)
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Safe, tested defaults from v1.1.5
const DEFAULTS = {
  refreshInterval: 10,   // Dashboard watch refresh (seconds)
  gatewayInterval: 30,   // Gateway status check interval (seconds)
  gatewayTimeout: 3      // Gateway command timeout (seconds)
};

// User config location (XDG standard)
const CONFIG_PATH = path.join(os.homedir(), '.config', 'tide-watch', 'config.json');

/**
 * Validate configuration values
 * @param {Object} config - Configuration object to validate
 * @returns {Object} Validated config
 * @throws {Error} If validation fails
 */
function validateConfig(config) {
  const rules = {
    refreshInterval: { min: 1, max: 300, desc: 'Dashboard refresh interval' },
    gatewayInterval: { min: 5, max: 600, desc: 'Gateway status check interval' },
    gatewayTimeout: { min: 1, max: 30, desc: 'Gateway command timeout' }
  };
  
  const validated = {};
  
  for (const [key, value] of Object.entries(config)) {
    // Whitelist: only known keys allowed
    if (!rules[key]) {
      throw new Error(`Unknown config key: ${key}`);
    }
    
    const { min, max, desc } = rules[key];
    const num = parseInt(value, 10);
    
    // Type and range validation
    if (isNaN(num) || num < min || num > max) {
      throw new Error(`Invalid ${key}: must be between ${min} and ${max} seconds (${desc})`);
    }
    
    validated[key] = num;
  }
  
  return validated;
}

/**
 * Load configuration from file (if exists)
 * @returns {Object} Config from file, or empty object if file doesn't exist
 */
function loadConfigFile() {
  if (!fs.existsSync(CONFIG_PATH)) {
    return {};
  }
  
  try {
    const content = fs.readFileSync(CONFIG_PATH, 'utf8');
    const parsed = JSON.parse(content);
    
    // Validate file config before using it
    return validateConfig(parsed);
  } catch (error) {
    console.warn(`Warning: Could not load config file (${CONFIG_PATH}): ${error.message}`);
    console.warn('Continuing with defaults...');
    return {};
  }
}

/**
 * Load configuration from environment variables
 * @returns {Object} Config from env vars
 */
function loadEnvConfig() {
  const config = {};
  
  if (process.env.TIDE_WATCH_REFRESH_INTERVAL) {
    config.refreshInterval = process.env.TIDE_WATCH_REFRESH_INTERVAL;
  }
  if (process.env.TIDE_WATCH_GATEWAY_INTERVAL) {
    config.gatewayInterval = process.env.TIDE_WATCH_GATEWAY_INTERVAL;
  }
  if (process.env.TIDE_WATCH_GATEWAY_TIMEOUT) {
    config.gatewayTimeout = process.env.TIDE_WATCH_GATEWAY_TIMEOUT;
  }
  
  // Validate env config if any values present
  if (Object.keys(config).length > 0) {
    return validateConfig(config);
  }
  
  return {};
}

/**
 * Load configuration with full precedence chain
 * @param {Object} cliFlags - CLI flags (highest precedence)
 * @returns {Object} Final merged and validated configuration
 */
function loadConfig(cliFlags = {}) {
  // 1. Start with safe defaults
  let config = { ...DEFAULTS };
  
  // 2. Merge config file (if exists and valid)
  const fileConfig = loadConfigFile();
  config = { ...config, ...fileConfig };
  
  // 3. Merge environment variables
  const envConfig = loadEnvConfig();
  config = { ...config, ...envConfig };
  
  // 4. Merge CLI flags (highest priority)
  if (Object.keys(cliFlags).length > 0) {
    const validatedFlags = validateConfig(cliFlags);
    config = { ...config, ...validatedFlags };
  }
  
  return config;
}

/**
 * Create config directory with secure permissions
 * @returns {boolean} True if directory exists/was created
 */
function ensureConfigDir() {
  const configDir = path.dirname(CONFIG_PATH);
  
  if (fs.existsSync(configDir)) {
    return true;
  }
  
  try {
    // Create directory with user-only permissions (0700)
    fs.mkdirSync(configDir, { recursive: true, mode: 0o700 });
    return true;
  } catch (error) {
    console.warn(`Warning: Could not create config directory: ${error.message}`);
    return false;
  }
}

/**
 * Save configuration to file with secure permissions
 * @param {Object} config - Configuration to save
 * @returns {boolean} True if saved successfully
 */
function saveConfig(config) {
  // Validate before saving
  const validated = validateConfig(config);
  
  // Ensure directory exists
  if (!ensureConfigDir()) {
    return false;
  }
  
  try {
    // Write with user-only permissions (0600)
    const content = JSON.stringify(validated, null, 2);
    fs.writeFileSync(CONFIG_PATH, content, { mode: 0o600 });
    return true;
  } catch (error) {
    console.error(`Error: Could not save config file: ${error.message}`);
    return false;
  }
}

module.exports = {
  loadConfig,
  saveConfig,
  validateConfig,
  DEFAULTS,
  CONFIG_PATH
};
