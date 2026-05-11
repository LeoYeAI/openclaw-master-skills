#!/usr/bin/env node

/**
 * Configuration Helper for Gandi Skill
 * Reads from Gateway Console config with fallback to file-based config
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { loadProfiles } from './profile-manager.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CONFIG_DIR = path.join(process.env.HOME, '.config', 'gandi');
const LEGACY_TOKEN_FILE = path.join(CONFIG_DIR, 'api_token');
const LEGACY_URL_FILE = path.join(CONFIG_DIR, 'api_url');

/**
 * Try to read Gateway config from Clawdbot
 * This assumes Gateway config is available at a standard location
 */
function readGatewayConfig() {
  // Possible Gateway config locations
  const configPaths = [
    path.join(process.env.HOME, '.clawdbot', 'clawdbot.json'),
    path.join(process.env.HOME, '.moltbot', 'moltbot.json'),
    path.join(process.env.HOME, '.config', 'clawdbot', 'config.json'),
  ];
  
  for (const configPath of configPaths) {
    if (fs.existsSync(configPath)) {
      try {
        const data = fs.readFileSync(configPath, 'utf8');
        const config = JSON.parse(data);
        
        // Extract Gandi skill config
        const gandiConfig = config.skills?.entries?.gandi?.config;
        
        if (gandiConfig) {
          return resolveEnvVars(gandiConfig);
        }
      } catch (error) {
        // Ignore parse errors, try next location
        console.warn(`Warning: Could not parse ${configPath}: ${error.message}`);
      }
    }
  }
  
  return null;
}

/**
 * Resolve environment variable references in config
 * Replaces ${VAR_NAME} with process.env.VAR_NAME
 */
function resolveEnvVars(obj) {
  if (typeof obj === 'string') {
    // Replace ${VAR} with environment variable
    return obj.replace(/\$\{([^}]+)\}/g, (match, varName) => {
      return process.env[varName] || match;
    });
  } else if (Array.isArray(obj)) {
    return obj.map(item => resolveEnvVars(item));
  } else if (obj && typeof obj === 'object') {
    const result = {};
    for (const [key, value] of Object.entries(obj)) {
      result[key] = resolveEnvVars(value);
    }
    return result;
  }
  return obj;
}

/**
 * Get API token from multiple sources (priority order)
 * 1. Gateway config (single token or multi-org)
 * 2. Profile-based config
 * 3. Legacy file-based config
 * 4. Environment variable
 */
export function getApiToken(profileName = null) {
  // 1. Try Gateway config first
  const gatewayConfig = readGatewayConfig();
  
  if (gatewayConfig) {
    // Multi-org mode
    if (gatewayConfig.organizations && gatewayConfig.organizations.length > 0) {
      let org;
      
      if (profileName) {
        // Find by profile name
        org = gatewayConfig.organizations.find(o => o.name === profileName);
      } else {
        // Use default org
        org = gatewayConfig.organizations.find(o => o.default);
        if (!org) {
          org = gatewayConfig.organizations[0]; // Fallback to first
        }
      }
      
      if (org && org.apiToken) {
        return {
          token: org.apiToken,
          sharingId: org.sharingId,
          orgName: org.label || org.name,
          source: 'gateway-multi-org'
        };
      }
    }
    
    // Single token mode
    if (gatewayConfig.apiToken) {
      return {
        token: gatewayConfig.apiToken,
        source: 'gateway-single'
      };
    }
  }
  
  // 2. Try profile-based config
  try {
    const profiles = loadProfiles();
    
    if (Object.keys(profiles.profiles).length > 0) {
      const profile = profileName 
        ? profiles.profiles[profileName]
        : profiles.profiles[profiles.default_profile];
      
      if (profile) {
        const tokenPath = path.join(CONFIG_DIR, profile.token_file);
        if (fs.existsSync(tokenPath)) {
          const token = fs.readFileSync(tokenPath, 'utf8').trim();
          return {
            token,
            sharingId: profile.org_id,
            orgName: profile.org_name,
            source: 'profile'
          };
        }
      }
    }
  } catch (error) {
    // Profile config not available, continue to legacy
  }
  
  // 3. Try legacy file-based config
  if (fs.existsSync(LEGACY_TOKEN_FILE)) {
    try {
      const token = fs.readFileSync(LEGACY_TOKEN_FILE, 'utf8').trim();
      if (token) {
        return {
          token,
          source: 'legacy-file'
        };
      }
    } catch (error) {
      // Ignore
    }
  }
  
  // 4. Try environment variable
  if (process.env.GANDI_API_TOKEN) {
    return {
      token: process.env.GANDI_API_TOKEN,
      source: 'env-var'
    };
  }
  
  throw new Error('No Gandi API token found. Configure via Gateway Console, profiles, or ~/.config/gandi/api_token');
}

/**
 * Get API URL from config or default
 */
export function getApiUrl() {
  // 1. Gateway config
  const gatewayConfig = readGatewayConfig();
  if (gatewayConfig && gatewayConfig.apiUrl) {
    return gatewayConfig.apiUrl;
  }
  
  // 2. Legacy file
  if (fs.existsSync(LEGACY_URL_FILE)) {
    try {
      const url = fs.readFileSync(LEGACY_URL_FILE, 'utf8').trim();
      if (url) return url;
    } catch (error) {
      // Ignore
    }
  }
  
  // 3. Default
  return 'https://api.gandi.net';
}

/**
 * Get domain checker configuration
 */
export function getDomainCheckerConfig() {
  // 1. Gateway config
  const gatewayConfig = readGatewayConfig();
  if (gatewayConfig && gatewayConfig.domainChecker) {
    return gatewayConfig.domainChecker;
  }
  
  // 2. Legacy file-based config
  const defaultConfigPath = path.join(__dirname, '../config/domain-checker-defaults.json');
  
  if (fs.existsSync(defaultConfigPath)) {
    try {
      return JSON.parse(fs.readFileSync(defaultConfigPath, 'utf8'));
    } catch (error) {
      console.warn('Warning: Could not read domain checker config:', error.message);
    }
  }
  
  // 3. Hardcoded defaults
  return {
    tlds: {
      mode: 'extend',
      defaults: ['com', 'net', 'org', 'info', 'io', 'dev', 'app', 'ai', 'tech'],
      custom: []
    },
    variations: {
      enabled: true,
      patterns: ['hyphenated', 'abbreviated', 'prefix', 'suffix', 'numbers'],
      prefixes: ['get', 'my', 'the', 'try'],
      suffixes: ['app', 'hub', 'io', 'ly', 'ai', 'hq'],
      maxNumbers: 3
    },
    rateLimit: {
      maxConcurrent: 3,
      delayMs: 200,
      maxRequestsPerMinute: 100
    },
    limits: {
      maxTlds: 5,
      maxVariations: 10
    }
  };
}

/**
 * List available organizations from config
 */
export function listOrganizations() {
  const gatewayConfig = readGatewayConfig();
  
  if (gatewayConfig && gatewayConfig.organizations) {
    return gatewayConfig.organizations.map(org => ({
      name: org.name,
      label: org.label || org.name,
      sharingId: org.sharingId,
      default: org.default || false
    }));
  }
  
  // Fallback to profile-based
  try {
    const profiles = loadProfiles();
    return Object.entries(profiles.profiles).map(([name, profile]) => ({
      name,
      label: profile.org_name,
      sharingId: profile.org_id,
      default: name === profiles.default_profile
    }));
  } catch (error) {
    return [];
  }
}

/**
 * Get configuration summary for diagnostics
 */
export function getConfigSummary() {
  const summary = {
    gatewayConfig: null,
    profileConfig: null,
    legacyFiles: {
      token: fs.existsSync(LEGACY_TOKEN_FILE),
      url: fs.existsSync(LEGACY_URL_FILE)
    },
    envVars: {
      GANDI_API_TOKEN: !!process.env.GANDI_API_TOKEN
    }
  };
  
  try {
    const gatewayConfig = readGatewayConfig();
    if (gatewayConfig) {
      summary.gatewayConfig = {
        hasApiToken: !!gatewayConfig.apiToken,
        hasOrganizations: !!(gatewayConfig.organizations && gatewayConfig.organizations.length > 0),
        organizationCount: gatewayConfig.organizations?.length || 0,
        hasDomainChecker: !!gatewayConfig.domainChecker
      };
    }
  } catch (error) {
    summary.gatewayConfig = { error: error.message };
  }
  
  try {
    const profiles = loadProfiles();
    summary.profileConfig = {
      profileCount: Object.keys(profiles.profiles).length,
      defaultProfile: profiles.default_profile,
      profiles: Object.keys(profiles.profiles)
    };
  } catch (error) {
    summary.profileConfig = { error: error.message };
  }
  
  return summary;
}
