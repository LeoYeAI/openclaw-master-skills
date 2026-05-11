#!/usr/bin/env node

/**
 * Profile Manager for Multi-Organization Support
 * Manages multiple Gandi organization profiles with separate tokens
 */

import fs from 'fs';
import path from 'path';
import { gandiApi } from './gandi-api.js';

const CONFIG_DIR = path.join(process.env.HOME, '.config', 'gandi');
const PROFILES_FILE = path.join(CONFIG_DIR, 'profiles.json');
const TOKENS_DIR = path.join(CONFIG_DIR, 'tokens');
const LEGACY_TOKEN_FILE = path.join(CONFIG_DIR, 'api_token');

/**
 * Ensure config directories exist
 */
function ensureConfigDirs() {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
  }
  if (!fs.existsSync(TOKENS_DIR)) {
    fs.mkdirSync(TOKENS_DIR, { recursive: true, mode: 0o700 });
  }
}

/**
 * Load profiles configuration
 */
export function loadProfiles() {
  ensureConfigDirs();
  
  if (!fs.existsSync(PROFILES_FILE)) {
    return {
      profiles: {},
      default_profile: null
    };
  }
  
  try {
    const data = fs.readFileSync(PROFILES_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    throw new Error(`Failed to load profiles: ${error.message}`);
  }
}

/**
 * Save profiles configuration
 */
export function saveProfiles(config) {
  ensureConfigDirs();
  
  try {
    fs.writeFileSync(PROFILES_FILE, JSON.stringify(config, null, 2), { mode: 0o600 });
  } catch (error) {
    throw new Error(`Failed to save profiles: ${error.message}`);
  }
}

/**
 * Get profile by name
 */
export function getProfile(name) {
  const config = loadProfiles();
  
  if (!name) {
    name = config.default_profile;
  }
  
  if (!name) {
    throw new Error('No profile specified and no default profile set');
  }
  
  const profile = config.profiles[name];
  
  if (!profile) {
    throw new Error(`Profile '${name}' not found`);
  }
  
  return profile;
}

/**
 * Read token for a profile
 */
export function readProfileToken(profileName) {
  const profile = getProfile(profileName);
  const tokenPath = path.join(CONFIG_DIR, profile.token_file);
  
  if (!fs.existsSync(tokenPath)) {
    throw new Error(`Token file not found for profile '${profileName}': ${tokenPath}`);
  }
  
  try {
    const token = fs.readFileSync(tokenPath, 'utf8').trim();
    
    if (!token) {
      throw new Error(`Token file is empty for profile '${profileName}'`);
    }
    
    return token;
  } catch (error) {
    throw new Error(`Failed to read token for profile '${profileName}': ${error.message}`);
  }
}

/**
 * List all profiles
 */
export function listProfiles() {
  const config = loadProfiles();
  return {
    profiles: config.profiles,
    default: config.default_profile
  };
}

/**
 * Add a new profile
 */
export async function addProfile(name, token, options = {}) {
  ensureConfigDirs();
  
  const config = loadProfiles();
  
  // Check if profile already exists
  if (config.profiles[name]) {
    throw new Error(`Profile '${name}' already exists`);
  }
  
  // Save token to file
  const tokenFile = `tokens/${name}.token`;
  const tokenPath = path.join(CONFIG_DIR, tokenFile);
  fs.writeFileSync(tokenPath, token, { mode: 0o600 });
  
  // Fetch organization info
  let orgInfo;
  try {
    // Temporarily use this token to fetch org info
    const result = await gandiApi('/v5/organization/organizations', 'GET', null, {}, token);
    orgInfo = result.data[0]; // Use first org
  } catch (error) {
    // Clean up token file on error
    fs.unlinkSync(tokenPath);
    throw new Error(`Failed to fetch organization info: ${error.message}`);
  }
  
  // Create profile
  config.profiles[name] = {
    token_file: tokenFile,
    org_id: orgInfo.id,
    org_name: orgInfo.name || orgInfo.id,
    org_type: orgInfo.type || 'unknown'
  };
  
  // Set as default if it's the first profile or explicitly requested
  if (Object.keys(config.profiles).length === 1 || options.setDefault) {
    config.default_profile = name;
  }
  
  saveProfiles(config);
  
  return config.profiles[name];
}

/**
 * Remove a profile
 */
export function removeProfile(name) {
  const config = loadProfiles();
  
  if (!config.profiles[name]) {
    throw new Error(`Profile '${name}' not found`);
  }
  
  // Delete token file
  const tokenPath = path.join(CONFIG_DIR, config.profiles[name].token_file);
  if (fs.existsSync(tokenPath)) {
    fs.unlinkSync(tokenPath);
  }
  
  // Remove profile
  delete config.profiles[name];
  
  // Update default if needed
  if (config.default_profile === name) {
    const remaining = Object.keys(config.profiles);
    config.default_profile = remaining.length > 0 ? remaining[0] : null;
  }
  
  saveProfiles(config);
}

/**
 * Set default profile
 */
export function setDefaultProfile(name) {
  const config = loadProfiles();
  
  if (!config.profiles[name]) {
    throw new Error(`Profile '${name}' not found`);
  }
  
  config.default_profile = name;
  saveProfiles(config);
}

/**
 * Migrate legacy single token to profile
 */
export async function migrateLegacyToken() {
  if (!fs.existsSync(LEGACY_TOKEN_FILE)) {
    return null;
  }
  
  const config = loadProfiles();
  
  // Don't migrate if profiles already exist
  if (Object.keys(config.profiles).length > 0) {
    return null;
  }
  
  console.log('📦 Migrating legacy token to profile system...');
  
  try {
    const token = fs.readFileSync(LEGACY_TOKEN_FILE, 'utf8').trim();
    
    // Create default profile
    await addProfile('default', token, { setDefault: true });
    
    // Rename legacy file as backup
    fs.renameSync(LEGACY_TOKEN_FILE, `${LEGACY_TOKEN_FILE}.backup`);
    
    console.log('✅ Migration complete! Legacy token backed up.');
    console.log('   Profile "default" created.');
    console.log('');
    
    return 'default';
  } catch (error) {
    console.error(`⚠️  Migration failed: ${error.message}`);
    return null;
  }
}

// Update gandiApi to support token override
export function gandiApiWithToken(endpoint, method, data, queryParams, token) {
  return gandiApi(endpoint, method, data, queryParams, token);
}
