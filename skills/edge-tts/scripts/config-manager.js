#!/usr/bin/env node
/**
 * TTS Configuration Manager
 *
 * Manages user preferences for TTS including voice, language, rate, pitch, and volume.
 * Stores preferences in a JSON file for persistence.
 *
 * Usage:
 *   node config-manager.js --set-voice en-US-AriaNeural
 *   node config-manager.js --get
 *   node config-manager.js --reset
 */

const fs = require('fs/promises');
const path = require('path');
const { program } = require('commander');

const DEFAULT_CONFIG_PATH = path.join(require('os').homedir(), '.tts-config.json');

const DEFAULT_CONFIG = {
  voice: 'en-US-MichelleNeural',
  lang: 'en-US',
  outputFormat: 'audio-24khz-48kbitrate-mono-mp3',
  pitch: 'default',
  rate: 'default',
  volume: 'default',
  saveSubtitles: false,
  proxy: '',
  timeout: 10000,
};

/**
 * Load TTS configuration from file
 * @param {string} configPath - Optional custom config path
 * @returns {Promise<object>} Configuration object
 */
async function loadConfig(configPath = DEFAULT_CONFIG_PATH) {
  try {
    const data = await fs.readFile(configPath, 'utf-8');
    const loaded = JSON.parse(data);
    // Merge with defaults to ensure all fields exist
    return { ...DEFAULT_CONFIG, ...loaded };
  } catch (error) {
    // File doesn't exist or is invalid - return defaults
    console.log(`ℹ  Config file not found or invalid, using defaults`);
    return { ...DEFAULT_CONFIG };
  }
}

/**
 * Save TTS configuration to file
 * @param {object} config - Configuration object to save
 * @param {string} configPath - Optional custom config path
 * @returns {Promise<boolean>} Success status
 */
async function saveConfig(config, configPath = DEFAULT_CONFIG_PATH) {
  try {
    const configDir = path.dirname(configPath);
    await fs.mkdir(configDir, { recursive: true });
    await fs.writeFile(configPath, JSON.stringify(config, null, 2));
    return true;
  } catch (error) {
    console.error('Error saving config:', error.message);
    return false;
  }
}

/**
 * Get configuration value(s)
 * @param {string|null} key - Optional key to get (null for all)
 * @param {string} configPath - Optional custom config path
 * @returns {Promise<any>} Configuration value or entire config
 */
async function getConfig(key = null, configPath = DEFAULT_CONFIG_PATH) {
  const config = await loadConfig(configPath);
  return key ? config[key] : config;
}

/**
 * Set configuration value
 * @param {string} key - Configuration key
 * @param {any} value - Value to set
 * @param {string} configPath - Optional custom config path
 * @returns {Promise<boolean>} Success status
 */
async function setConfig(key, value, configPath = DEFAULT_CONFIG_PATH) {
  const config = await loadConfig(configPath);
  config[key] = value;
  return saveConfig(config, configPath);
}

/**
 * Reset configuration to defaults
 * @param {string} configPath - Optional custom config path
 * @returns {Promise<object>} Default configuration
 */
async function resetConfig(configPath = DEFAULT_CONFIG_PATH) {
  try {
    await fs.unlink(configPath);
  } catch (error) {
    // File doesn't exist - that's fine
  }
  return { ...DEFAULT_CONFIG };
}

/**
 * Convert config to CLI arguments for tts-converter
 * @param {object} config - Configuration object
 * @returns {Array<string>} CLI arguments
 */
function configToArgs(config) {
  const args = [];

  if (config.voice) {
    args.push(`--voice`, config.voice);
  }
  if (config.lang) {
    args.push(`--lang`, config.lang);
  }
  if (config.outputFormat) {
    args.push(`--format`, config.outputFormat);
  }
  if (config.pitch && config.pitch !== 'default') {
    args.push(`--pitch`, config.pitch);
  }
  if (config.rate && config.rate !== 'default') {
    args.push(`--rate`, config.rate);
  }
  if (config.volume && config.volume !== 'default') {
    args.push(`--volume`, config.volume);
  }
  if (config.saveSubtitles) {
    args.push(`--save-subtitles`);
  }
  if (config.proxy) {
    args.push(`--proxy`, config.proxy);
  }
  if (config.timeout !== 10000) {
    args.push(`--timeout`, config.timeout.toString());
  }

  return args;
}

// CLI setup
program
  .option('--config-path <path>', 'Path to config file')
  .option('-g, --get [key]', 'Get config value (or all if no key specified)')
  .option('-s, --set <key> <value>', 'Set config value')
  .option('--set-voice <voice>', 'Set default voice')
  .option('--set-lang <lang>', 'Set default language code')
  .option('--set-format <format>', 'Set default output format')
  .option('--set-pitch <pitch>', 'Set default pitch')
  .option('--set-rate <rate>', 'Set default rate')
  .option('--set-volume <volume>', 'Set default volume')
  .option('--toggle-subtitles', 'Toggle subtitle saving')
  .option('--set-proxy <proxy>', 'Set proxy URL')
  .option('--set-timeout <ms>', 'Set timeout in milliseconds')
  .option('--reset', 'Reset to defaults')
  .option('--export', 'Export config as JSON')
  .option('--to-cli', 'Convert config to CLI arguments')
  .description('Manage TTS configuration')
  .version('2.0.0');

program.parse(process.argv);
const options = program.opts();
const configPath = options.configPath || DEFAULT_CONFIG_PATH;

async function main() {
  if (options.reset) {
    const config = await resetConfig(configPath);
    console.log('✓ Configuration reset to defaults');
    console.log(JSON.stringify(config, null, 2));
    return;
  }

  if (options.get !== undefined) {
    const config = await getConfig(options.get || null, configPath);
    console.log(JSON.stringify(config, null, 2));
    return;
  }

  if (options.toCli) {
    const config = await getConfig(null, configPath);
    const args = configToArgs(config);
    console.log(args.join(' '));
    return;
  }

  if (options.set) {
    const [key, value] = options.set;
    const success = await setConfig(key, value, configPath);
    if (success) {
      console.log(`✓ Set ${key} = ${value}`);
    }
    return;
  }

  if (options.setVoice) {
    await setConfig('voice', options.setVoice, configPath);
    console.log(`✓ Set voice = ${options.setVoice}`);
    return;
  }

  if (options.setLang) {
    await setConfig('lang', options.setLang, configPath);
    console.log(`✓ Set lang = ${options.setLang}`);
    return;
  }

  if (options.setFormat) {
    await setConfig('outputFormat', options.setFormat, configPath);
    console.log(`✓ Set format = ${options.setFormat}`);
    return;
  }

  if (options.setPitch) {
    await setConfig('pitch', options.setPitch, configPath);
    console.log(`✓ Set pitch = ${options.setPitch}`);
    return;
  }

  if (options.setRate) {
    await setConfig('rate', options.setRate, configPath);
    console.log(`✓ Set rate = ${options.setRate}`);
    return;
  }

  if (options.setVolume) {
    await setConfig('volume', options.setVolume, configPath);
    console.log(`✓ Set volume = ${options.setVolume}`);
    return;
  }

  if (options.toggleSubtitles) {
    const config = await getConfig(null, configPath);
    await setConfig('saveSubtitles', !config.saveSubtitles, configPath);
    console.log(`✓ Toggled subtitles: ${config.saveSubtitles} -> ${!config.saveSubtitles}`);
    return;
  }

  if (options.setProxy) {
    await setConfig('proxy', options.setProxy, configPath);
    console.log(`✓ Set proxy = ${options.setProxy}`);
    return;
  }

  if (options.setTimeout) {
    await setConfig('timeout', parseInt(options.setTimeout), configPath);
    console.log(`✓ Set timeout = ${options.setTimeout}ms`);
    return;
  }

  if (options.export) {
    const config = await getConfig(null, configPath);
    console.log(JSON.stringify(config, null, 2));
    return;
  }

  // Show current config if no action specified
  const config = await getConfig(null, configPath);
  console.log(JSON.stringify(config, null, 2));
}

main().catch(error => {
  console.error('Error:', error.message);
  process.exit(1);
});

module.exports = {
  loadConfig,
  saveConfig,
  getConfig,
  setConfig,
  resetConfig,
  configToArgs,
};
