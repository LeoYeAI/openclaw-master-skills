#!/usr/bin/env node

/**
 * Gandi API Client
 * Core functions for interacting with Gandi's v5 API
 */

import https from 'https';
import fs from 'fs';
import path from 'path';

// Configuration
const CONFIG_DIR = path.join(process.env.HOME, '.config', 'gandi');
const TOKEN_FILE = path.join(CONFIG_DIR, 'api_token');
const URL_FILE = path.join(CONFIG_DIR, 'api_url');
const CONTACT_FILE = path.join(CONFIG_DIR, 'contact.json');
const DEFAULT_API_URL = 'https://api.gandi.net';

/**
 * Read API token from environment or config file
 * 
 * Checks in priority order:
 * 1. GANDI_API_TOKEN environment variable (CI/CD friendly)
 * 2. ~/.config/gandi/api_token file (local development)
 */
export function readToken() {
  // Check environment variable first
  if (process.env.GANDI_API_TOKEN) {
    const token = process.env.GANDI_API_TOKEN.trim();
    if (!token) {
      throw new Error('GANDI_API_TOKEN environment variable is empty');
    }
    return token;
  }
  
  // Fall back to file-based credential
  try {
    if (!fs.existsSync(TOKEN_FILE)) {
      throw new Error(
        `GANDI_API_TOKEN not found.\n\n` +
        `Set environment variable:\n` +
        `  export GANDI_API_TOKEN="your-gandi-pat"\n\n` +
        `OR create token file:\n` +
        `  echo "YOUR_PAT" > ${TOKEN_FILE} && chmod 600 ${TOKEN_FILE}`
      );
    }
    
    const token = fs.readFileSync(TOKEN_FILE, 'utf8').trim();
    
    if (!token) {
      throw new Error('Token file is empty');
    }
    
    return token;
  } catch (error) {
    if (error.code === 'EACCES') {
      throw new Error(`Cannot read token file. Check permissions: chmod 600 ${TOKEN_FILE}`);
    }
    throw error;
  }
}

/**
 * Read API URL from config (or use default)
 */
export function readApiUrl() {
  try {
    if (fs.existsSync(URL_FILE)) {
      const url = fs.readFileSync(URL_FILE, 'utf8').trim();
      if (url) return url;
    }
  } catch (error) {
    // Ignore errors, use default
  }
  
  return DEFAULT_API_URL;
}

/**
 * Load saved contact information
 * @returns {Object|null} Contact object or null if not found
 */
export function loadSavedContact() {
  try {
    if (!fs.existsSync(CONTACT_FILE)) {
      return null;
    }
    
    const contact = JSON.parse(fs.readFileSync(CONTACT_FILE, 'utf8'));
    return contact;
  } catch (error) {
    console.error(`⚠️  Error reading saved contact: ${error.message}`);
    return null;
  }
}

/**
 * Rate limiter for API calls
 */
class RateLimiter {
  constructor(config) {
    this.maxConcurrent = config.maxConcurrent || 3;
    this.delayMs = config.delayMs || 200;
    this.maxRequestsPerMinute = config.maxRequestsPerMinute || 100;
    this.activeRequests = 0;
    this.requestTimes = [];
    this.queue = [];
  }
  
  async throttle(fn) {
    // Wait if we're at max concurrent requests
    while (this.activeRequests >= this.maxConcurrent) {
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    // Check requests per minute limit
    const now = Date.now();
    const oneMinuteAgo = now - 60000;
    this.requestTimes = this.requestTimes.filter(t => t > oneMinuteAgo);
    
    if (this.requestTimes.length >= this.maxRequestsPerMinute) {
      const oldestRequest = this.requestTimes[0];
      const waitTime = 60000 - (now - oldestRequest);
      if (waitTime > 0) {
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }
    
    // Execute the request
    this.activeRequests++;
    this.requestTimes.push(Date.now());
    
    try {
      const result = await fn();
      return result;
    } finally {
      this.activeRequests--;
      // Delay between requests
      if (this.delayMs > 0) {
        await new Promise(resolve => setTimeout(resolve, this.delayMs));
      }
    }
  }
}

let rateLimiter = null;

/**
 * Get or create rate limiter instance
 */
export function getRateLimiter(config = null) {
  if (!rateLimiter || config) {
    const limiterConfig = config || readDomainCheckerConfig().rateLimit;
    rateLimiter = new RateLimiter(limiterConfig);
  }
  return rateLimiter;
}

/**
 * Read domain checker configuration
 * Checks Gateway config first, then falls back to defaults
 * @returns {Object} Domain checker config
 */
export function readDomainCheckerConfig() {
  const defaultConfigPath = path.join(path.dirname(new URL(import.meta.url).pathname), '../config/domain-checker-defaults.json');
  
  try {
    // TODO: Read from Gateway config when available
    // const gatewayConfig = readGatewayConfig();
    // const config = gatewayConfig.skills?.entries?.gandi?.config?.domainChecker;
    // if (config) return config;
    
    // Fallback to defaults
    if (fs.existsSync(defaultConfigPath)) {
      return JSON.parse(fs.readFileSync(defaultConfigPath, 'utf8'));
    }
  } catch (error) {
    console.warn('Could not read domain checker config, using hardcoded defaults:', error.message);
  }
  
  // Hardcoded fallback
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
 * Make API request
 * @param {string} endpoint - API endpoint (e.g., '/v5/domain/domains')
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE, PATCH)
 * @param {object} data - Request body (for POST/PUT/PATCH)
 * @param {object} queryParams - Query string parameters
 * @param {string} tokenOverride - Optional token override (for profile support)
 * @returns {Promise<object>} Response data
 */
export function gandiApi(endpoint, method = 'GET', data = null, queryParams = {}, tokenOverride = null) {
  return new Promise((resolve, reject) => {
    const token = tokenOverride || readToken();
    const apiUrl = readApiUrl();
    
    // Build URL with query parameters
    const url = new URL(endpoint, apiUrl);
    Object.entries(queryParams).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, value);
      }
    });
    
    const options = {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json'
      }
    };
    
    // Add Content-Type for requests with body
    if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
      options.headers['Content-Type'] = 'application/json';
    }
    
    const req = https.request(url, options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        // Handle different status codes
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            const parsed = responseData ? JSON.parse(responseData) : {};
            resolve({
              statusCode: res.statusCode,
              data: parsed,
              headers: res.headers
            });
          } catch (error) {
            // Some responses are plain text
            resolve({
              statusCode: res.statusCode,
              data: responseData,
              headers: res.headers
            });
          }
        } else {
          // Parse error response
          let errorData;
          try {
            errorData = JSON.parse(responseData);
          } catch (e) {
            errorData = { message: responseData };
          }
          
          const error = new Error(
            errorData.message || `HTTP ${res.statusCode}: ${res.statusMessage}`
          );
          error.statusCode = res.statusCode;
          error.response = errorData;
          reject(error);
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    // Send request body if present
    if (data) {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
}

/**
 * Test authentication
 */
export async function testAuth() {
  try {
    const result = await gandiApi('/v5/organization/organizations');
    return {
      success: true,
      organizations: result.data
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      statusCode: error.statusCode
    };
  }
}

/**
 * List domains
 * @param {object} options - Query options (page, per_page, sort_by, sharing_id)
 */
export async function listDomains(options = {}) {
  const result = await gandiApi('/v5/domain/domains', 'GET', null, options);
  return result.data;
}

/**
 * Get domain details
 * @param {string} domain - Domain name (FQDN)
 */
export async function getDomain(domain) {
  const result = await gandiApi(`/v5/domain/domains/${domain}`);
  return result.data;
}

/**
 * List DNS records for a domain
 * @param {string} domain - Domain name (FQDN)
 */
export async function listDnsRecords(domain) {
  const result = await gandiApi(`/v5/livedns/domains/${domain}/records`);
  return result.data;
}

/**
 * Get specific DNS records
 * @param {string} domain - Domain name
 * @param {string} name - Record name (e.g., '@', 'www')
 * @param {string} type - Record type (e.g., 'A', 'CNAME')
 */
export async function getDnsRecord(domain, name, type) {
  const result = await gandiApi(`/v5/livedns/domains/${domain}/records/${name}/${type}`);
  return result.data;
}

/**
 * Check domain availability
 * @param {string[]} domains - Array of domain names to check
 */
/**
 * Check availability of one or more domains
 * @param {string[]} domains - Array of domain names to check
 * @returns {Promise<Object>} Availability results for each domain
 */
export async function checkAvailability(domains) {
  if (!Array.isArray(domains)) {
    domains = [domains];
  }
  
  // Build query params with multiple 'name' parameters
  const queryString = domains.map(d => `name=${encodeURIComponent(d)}`).join('&');
  const result = await gandiApi(`/v5/domain/check?${queryString}`, 'GET');
  
  return result.data;
}

/**
 * Generate domain name variations
 * @param {string} baseName - Base domain name (without TLD)
 * @param {Object} config - Variation config
 * @returns {Object} Generated variations grouped by pattern
 */
export function generateVariations(baseName, config = {}) {
  const variations = {
    hyphenated: [],
    abbreviated: [],
    prefix: [],
    suffix: [],
    numbers: []
  };
  
  const patterns = config.patterns || ['hyphenated', 'abbreviated', 'prefix', 'suffix', 'numbers'];
  const prefixes = config.prefixes || ['get', 'my', 'the', 'try'];
  const suffixes = config.suffixes || ['app', 'hub', 'io', 'ly', 'ai', 'hq'];
  const maxNumbers = config.maxNumbers || 3;
  
  // Hyphenated (insert hyphens between likely word boundaries)
  if (patterns.includes('hyphenated')) {
    // Simple strategy: add hyphen before capitals and after common prefixes
    const hyphenated = baseName.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
    if (hyphenated !== baseName && !hyphenated.includes('--')) {
      variations.hyphenated.push(hyphenated);
    }
    
    // Try splitting at vowel boundaries
    const parts = baseName.match(/[bcdfghjklmnpqrstvwxyz]+[aeiou]+/gi);
    if (parts && parts.length > 1) {
      variations.hyphenated.push(parts.join('-').toLowerCase());
    }
  }
  
  // Abbreviated (remove vowels, keep consonants)
  if (patterns.includes('abbreviated')) {
    const abbreviated = baseName.replace(/[aeiou]/gi, '').toLowerCase();
    if (abbreviated.length >= 3 && abbreviated !== baseName) {
      variations.abbreviated.push(abbreviated);
    }
  }
  
  // Prefix variations
  if (patterns.includes('prefix')) {
    prefixes.forEach(prefix => {
      variations.prefix.push(`${prefix}-${baseName}`);
      variations.prefix.push(`${prefix}${baseName}`);
    });
  }
  
  // Suffix variations
  if (patterns.includes('suffix')) {
    suffixes.forEach(suffix => {
      variations.suffix.push(`${baseName}-${suffix}`);
      variations.suffix.push(`${baseName}${suffix}`);
    });
  }
  
  // Number variations
  if (patterns.includes('numbers')) {
    for (let i = 2; i <= maxNumbers + 1; i++) {
      variations.numbers.push(`${baseName}${i}`);
    }
  }
  
  return variations;
}

/**
 * Create or update a DNS record
 * @param {string} domain - Domain name (FQDN)
 * @param {string} name - Record name (e.g., '@', 'www', 'mail')
 * @param {string} type - Record type (e.g., 'A', 'CNAME', 'MX', 'TXT')
 * @param {string[]} values - Array of record values
 * @param {number} ttl - Time to live in seconds (default: 10800)
 * @returns {Promise<Object>} API response
 */
export async function createDnsRecord(domain, name, type, values, ttl = 10800) {
  // Ensure values is an array
  if (!Array.isArray(values)) {
    values = [values];
  }
  
  const data = {
    rrset_ttl: ttl,
    rrset_values: values
  };
  
  const result = await gandiApi(`/v5/livedns/domains/${domain}/records/${name}/${type}`, 'PUT', data);
  return result;
}

/**
 * Delete a DNS record
 * @param {string} domain - Domain name (FQDN)
 * @param {string} name - Record name
 * @param {string} type - Record type
 * @returns {Promise<Object>} API response
 */
export async function deleteDnsRecord(domain, name, type) {
  const result = await gandiApi(`/v5/livedns/domains/${domain}/records/${name}/${type}`, 'DELETE');
  return result;
}

/**
 * Replace all DNS records for a domain (bulk update)
 * @param {string} domain - Domain name (FQDN)
 * @param {Array} records - Array of record objects with rrset_name, rrset_type, rrset_ttl, rrset_values
 * @returns {Promise<Object>} API response
 */
export async function replaceDnsRecords(domain, records) {
  const data = {
    items: records
  };
  
  const result = await gandiApi(`/v5/livedns/domains/${domain}/records`, 'PUT', data);
  return result;
}

/**
 * Create a DNS zone snapshot
 * @param {string} domain - Domain name (FQDN)
 * @param {string} name - Snapshot name/description
 * @returns {Promise<Object>} Snapshot details
 */
export async function createSnapshot(domain, name) {
  const data = { name };
  const result = await gandiApi(`/v5/livedns/domains/${domain}/snapshots`, 'POST', data);
  return result.data;
}

/**
 * List DNS zone snapshots
 * @param {string} domain - Domain name (FQDN)
 * @returns {Promise<Array>} Array of snapshots
 */
export async function listSnapshots(domain) {
  const result = await gandiApi(`/v5/livedns/domains/${domain}/snapshots`);
  return result.data;
}

/**
 * Restore DNS zone from snapshot
 * @param {string} domain - Domain name (FQDN)
 * @param {string} snapshotId - Snapshot UUID
 * @returns {Promise<Object>} API response
 */
export async function restoreSnapshot(domain, snapshotId) {
  const result = await gandiApi(`/v5/livedns/domains/${domain}/snapshots/${snapshotId}`, 'POST');
  return result.data;
}

/**
 * Domain registration and renewal
 */

/**
 * Register a new domain
 * @param {string} domain - Domain name (FQDN)
 * @param {number} duration - Registration duration in years (1-10)
 * @param {Object} owner - Owner contact information
 * @param {Object} options - Additional options (admin, tech, bill contacts, autorenew)
 * @returns {Promise<Object>} Registration result with operation details
 */
export async function registerDomain(domain, duration, owner, options = {}) {
  const data = {
    fqdn: domain,
    duration: duration,
    owner: owner
  };
  
  // Use shortcuts for other contacts if not provided
  data.admin = options.admin || 'owner';
  data.tech = options.tech || 'owner';
  data.bill = options.bill || 'owner';
  
  // Optional settings
  if (options.nameservers) {
    data.nameservers = options.nameservers;
  }
  
  if (options.extra_parameters) {
    data.extra_parameters = options.extra_parameters;
  }
  
  const result = await gandiApi('/v5/domain/domains', 'POST', data);
  return result.data;
}

/**
 * Renew a domain
 * @param {string} domain - Domain name (FQDN)
 * @param {number} duration - Renewal duration in years (1-10)
 * @returns {Promise<Object>} Renewal result with operation details
 */
export async function renewDomain(domain, duration) {
  const data = {
    duration: duration
  };
  
  const result = await gandiApi(`/v5/domain/domains/${domain}/renew`, 'POST', data);
  return result.data;
}

/**
 * Get auto-renewal settings for a domain
 * @param {string} domain - Domain name (FQDN)
 * @returns {Promise<Object>} Auto-renewal configuration
 */
export async function getAutoRenewal(domain) {
  const result = await gandiApi(`/v5/domain/domains/${domain}/autorenew`);
  return result.data;
}

/**
 * Update auto-renewal settings for a domain
 * @param {string} domain - Domain name (FQDN)
 * @param {boolean} enabled - Enable or disable auto-renewal
 * @param {number} duration - Renewal duration in years (default: 1)
 * @param {string} orgId - Organization ID (optional)
 * @returns {Promise<Object>} Updated auto-renewal settings
 */
export async function setAutoRenewal(domain, enabled, duration = 1, orgId = null) {
  const data = {
    enabled: enabled,
    duration: duration
  };
  
  if (orgId) {
    data.org_id = orgId;
  }
  
  const result = await gandiApi(`/v5/domain/domains/${domain}/autorenew`, 'PUT', data);
  return result.data;
}

/**
 * DNSSEC management
 */

/**
 * Get DNSSEC keys for a domain
 * @param {string} domain - Domain name (FQDN)
 * @returns {Promise<Array>} Array of DNSSEC key objects
 */
export async function getDnssecKeys(domain) {
  const result = await gandiApi(`/v5/livedns/domains/${domain}/dnskeys`);
  return result.data;
}

/**
 * Enable DNSSEC for a domain
 * @param {string} domain - Domain name (FQDN)
 * @param {Object} options - DNSSEC options (algorithm, flags, etc.)
 * @returns {Promise<Object>} DNSSEC configuration result
 */
export async function enableDnssec(domain, options = {}) {
  // Gandi auto-generates keys when you enable DNSSEC
  // The PUT request enables DNSSEC with default or specified settings
  const data = options.keys || {};
  
  const result = await gandiApi(`/v5/livedns/domains/${domain}/dnskeys`, 'PUT', data);
  return result.data;
}

/**
 * Delete a specific DNSSEC key
 * @param {string} domain - Domain name (FQDN)
 * @param {string} keyId - Key UUID to delete
 * @returns {Promise<Object>} Deletion result
 */
export async function deleteDnssecKey(domain, keyId) {
  const result = await gandiApi(`/v5/livedns/domains/${domain}/dnskeys/${keyId}`, 'DELETE');
  return result;
}

/**
 * Disable DNSSEC for a domain (delete all keys)
 * @param {string} domain - Domain name (FQDN)
 * @returns {Promise<Object>} Result of disabling DNSSEC
 */
export async function disableDnssec(domain) {
  // Get all keys and delete them
  const keys = await getDnssecKeys(domain);
  
  if (!keys || keys.length === 0) {
    return { success: true, message: 'DNSSEC already disabled' };
  }
  
  // Delete each key
  const results = [];
  for (const key of keys) {
    try {
      await deleteDnssecKey(domain, key.uuid || key.id);
      results.push({ key: key.uuid || key.id, success: true });
    } catch (error) {
      results.push({ key: key.uuid || key.id, success: false, error: error.message });
    }
  }
  
  return {
    success: results.every(r => r.success),
    results: results
  };
}

/**
 * Email forwarding management
 */

/**
 * List email forwards for a domain
 * @param {string} domain - Domain name (FQDN)
 * @returns {Promise<Array>} Array of email forward objects
 */
export async function listEmailForwards(domain) {
  const result = await gandiApi(`/v5/email/forwards/${domain}`);
  return result.data;
}

/**
 * Get specific email forward
 * @param {string} domain - Domain name (FQDN)
 * @param {string} mailbox - Mailbox/alias name (e.g., 'hello', '@' for catch-all)
 * @returns {Promise<Object>} Email forward details
 */
export async function getEmailForward(domain, mailbox) {
  const result = await gandiApi(`/v5/email/forwards/${domain}/${mailbox}`);
  return result.data;
}

/**
 * Create email forward
 * @param {string} domain - Domain name (FQDN)
 * @param {string} mailbox - Mailbox/alias name (e.g., 'hello', '@' for catch-all)
 * @param {string[]} destinations - Array of destination email addresses
 * @returns {Promise<Object>} Created forward details
 */
export async function createEmailForward(domain, mailbox, destinations) {
  if (!Array.isArray(destinations)) {
    destinations = [destinations];
  }
  
  // Mailbox (source) goes in the body for POST
  const data = {
    source: mailbox,
    destinations: destinations
  };
  
  const result = await gandiApi(`/v5/email/forwards/${domain}`, 'POST', data);
  return result.data;
}

/**
 * Update email forward
 * @param {string} domain - Domain name (FQDN)
 * @param {string} mailbox - Mailbox/alias name
 * @param {string[]} destinations - Array of destination email addresses
 * @returns {Promise<Object>} Updated forward details
 */
export async function updateEmailForward(domain, mailbox, destinations) {
  if (!Array.isArray(destinations)) {
    destinations = [destinations];
  }
  
  const data = {
    destinations: destinations
  };
  
  const result = await gandiApi(`/v5/email/forwards/${domain}/${mailbox}`, 'PUT', data);
  return result.data;
}

/**
 * Delete email forward
 * @param {string} domain - Domain name (FQDN)
 * @param {string} mailbox - Mailbox/alias name
 * @returns {Promise<Object>} Deletion result
 */
export async function deleteEmailForward(domain, mailbox) {
  const result = await gandiApi(`/v5/email/forwards/${domain}/${mailbox}`, 'DELETE');
  return result;
}

/**
 * SSL/TLS certificate management
 */

/**
 * List SSL certificates
 * @returns {Promise<Array>} Array of certificate objects
 */
export async function listCertificates() {
  const result = await gandiApi('/v5/domain/certificates');
  return result.data;
}

/**
 * Get certificate details
 * @param {string} certId - Certificate UUID
 * @returns {Promise<Object>} Certificate details
 */
export async function getCertificate(certId) {
  const result = await gandiApi(`/v5/domain/certificates/${certId}`);
  return result.data;
}

/**
 * Request a new SSL certificate
 * @param {string} cn - Common name (domain)
 * @param {Object} options - Certificate options (dcv_method, csr, etc.)
 * @returns {Promise<Object>} Certificate request result
 */
export async function requestCertificate(cn, options = {}) {
  const data = {
    cn: cn,
    dcv_method: options.dcv_method || 'dns', // dns, email, or http
    ...options
  };
  
  const result = await gandiApi('/v5/domain/certificates', 'POST', data);
  return result.data;
}

/**
 * Update certificate
 * @param {string} certId - Certificate UUID
 * @param {Object} data - Update data
 * @returns {Promise<Object>} Updated certificate
 */
export async function updateCertificate(certId, data) {
  const result = await gandiApi(`/v5/domain/certificates/${certId}`, 'PUT', data);
  return result.data;
}

/**
 * Delete/revoke certificate
 * @param {string} certId - Certificate UUID
 * @returns {Promise<Object>} Deletion result
 */
export async function deleteCertificate(certId) {
  const result = await gandiApi(`/v5/domain/certificates/${certId}`, 'DELETE');
  return result;
}

/**
 * Validation helpers
 */

/**
 * Validate IPv4 address
 * @param {string} ip - IP address to validate
 * @returns {boolean} True if valid
 */
export function isValidIPv4(ip) {
  const ipv4Regex = /^(\d{1,3}\.){3}\d{1,3}$/;
  if (!ipv4Regex.test(ip)) return false;
  
  const parts = ip.split('.');
  return parts.every(part => {
    const num = parseInt(part, 10);
    return num >= 0 && num <= 255;
  });
}

/**
 * Validate IPv6 address
 * @param {string} ip - IPv6 address to validate
 * @returns {boolean} True if valid
 */
export function isValidIPv6(ip) {
  const ipv6Regex = /^([\da-f]{1,4}:){7}[\da-f]{1,4}$/i;
  const ipv6CompressedRegex = /^([\da-f]{1,4}:)*::([\da-f]{1,4}:)*[\da-f]{1,4}$/i;
  const ipv6MixedRegex = /^([\da-f]{1,4}:){6}(\d{1,3}\.){3}\d{1,3}$/i;
  
  return ipv6Regex.test(ip) || ipv6CompressedRegex.test(ip) || ipv6MixedRegex.test(ip);
}

/**
 * Validate domain/hostname (FQDN)
 * @param {string} hostname - Hostname to validate
 * @returns {boolean} True if valid
 */
export function isValidHostname(hostname) {
  // Allow @ for root domain
  if (hostname === '@') return true;
  
  // Allow wildcards
  if (hostname.startsWith('*.')) {
    hostname = hostname.substring(2);
  }
  
  const hostnameRegex = /^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.?$/i;
  return hostnameRegex.test(hostname);
}

/**
 * Validate TTL value
 * @param {number} ttl - TTL in seconds
 * @returns {boolean} True if valid
 */
export function isValidTTL(ttl) {
  const num = parseInt(ttl, 10);
  return !isNaN(num) && num >= 300 && num <= 2592000;
}

// ========================================
// Input Sanitization Functions
// ========================================

/**
 * Sanitize domain name
 * Prevents injection and validates format
 * @param {string} domain - Raw domain name
 * @returns {string} Sanitized domain name
 * @throws {Error} If domain is invalid
 */
export function sanitizeDomain(domain) {
  if (!domain || typeof domain !== 'string') {
    throw new Error('Domain name must be a string');
  }
  
  // Remove whitespace and convert to lowercase
  domain = domain.trim().toLowerCase();
  
  // Remove trailing dot if present (we'll add it for FQDN when needed)
  domain = domain.replace(/\.$/, '');
  
  // Check length limits (RFC 1035)
  if (domain.length > 253) {
    throw new Error(`Domain name too long: ${domain.length} characters (max 253)`);
  }
  
  if (domain.length === 0) {
    throw new Error('Domain name cannot be empty');
  }
  
  // Validate domain format (RFC 1035: letters, digits, hyphens, dots)
  const domainRegex = /^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/;
  if (!domainRegex.test(domain)) {
    throw new Error(`Invalid domain format: "${domain}"`);
  }
  
  // Prevent path traversal attempts
  if (domain.includes('..')) {
    throw new Error(`Invalid domain (path traversal attempt): "${domain}"`);
  }
  
  // Prevent directory separators
  if (domain.includes('/') || domain.includes('\\')) {
    throw new Error(`Invalid domain (contains path separators): "${domain}"`);
  }
  
  // Check individual label length (max 63 chars per label)
  const labels = domain.split('.');
  for (const label of labels) {
    if (label.length > 63) {
      throw new Error(`Domain label too long: "${label}" (max 63 characters)`);
    }
  }
  
  return domain;
}

/**
 * Sanitize DNS record name
 * Prevents injection and validates format
 * @param {string} name - Raw record name
 * @returns {string} Sanitized record name
 * @throws {Error} If name is invalid
 */
export function sanitizeRecordName(name) {
  if (!name || typeof name !== 'string') {
    throw new Error('Record name must be a string');
  }
  
  // Allow @ for root domain (special case)
  if (name === '@') {
    return name;
  }
  
  // Allow * for wildcard (special case)
  if (name === '*') {
    return name;
  }
  
  // Remove whitespace and convert to lowercase
  name = name.trim().toLowerCase();
  
  // Remove trailing dot if present
  name = name.replace(/\.$/, '');
  
  // Check length (max 63 chars per label)
  if (name.length > 63) {
    throw new Error(`Record name too long: ${name.length} characters (max 63)`);
  }
  
  if (name.length === 0) {
    throw new Error('Record name cannot be empty');
  }
  
  // Validate subdomain format
  // Allow underscores anywhere in the name if it contains at least one label starting with _
  // This handles service records like: _dmarc, resend._domainkey, _imap._tcp
  const hasUnderscoreLabel = /(?:^|\.)_/.test(name);
  
  const nameRegex = hasUnderscoreLabel
    ? /^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*_[a-z0-9_.-]+$/  // Allow underscores if any label starts with _
    : /^(?:\*\.)?(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/;  // Strict for hostnames
  
  if (!nameRegex.test(name)) {
    throw new Error(`Invalid record name format: "${name}"`);
  }
  
  // Prevent path traversal
  if (name.includes('..')) {
    throw new Error(`Invalid record name (path traversal): "${name}"`);
  }
  
  // Prevent directory separators
  if (name.includes('/') || name.includes('\\')) {
    throw new Error(`Invalid record name (contains path separators): "${name}"`);
  }
  
  return name;
}

/**
 * Sanitize TTL value
 * Prevents overflow and validates range
 * @param {number|string} ttl - Raw TTL value
 * @returns {number} Sanitized TTL value
 * @throws {Error} If TTL is invalid
 */
export function sanitizeTTL(ttl) {
  // Convert to number
  const ttlNum = parseInt(ttl, 10);
  
  // Check if valid number
  if (isNaN(ttlNum) || !Number.isFinite(ttlNum)) {
    throw new Error(`Invalid TTL (not a number): "${ttl}"`);
  }
  
  // Check if positive
  if (ttlNum <= 0) {
    throw new Error(`TTL must be positive: ${ttlNum}`);
  }
  
  // Gandi's TTL range: 300 (5 min) to 2592000 (30 days)
  if (ttlNum < 300) {
    throw new Error(`TTL too low: ${ttlNum} (min 300 seconds / 5 minutes)`);
  }
  
  if (ttlNum > 2592000) {
    throw new Error(`TTL too high: ${ttlNum} (max 2592000 seconds / 30 days)`);
  }
  
  return ttlNum;
}

/**
 * Sanitize object for logging
 * Redacts sensitive fields
 * @param {Object} obj - Object to sanitize
 * @returns {Object} Sanitized object
 */
export function sanitizeForLog(obj) {
  if (!obj || typeof obj !== 'object') {
    return obj;
  }
  
  const redacted = { ...obj };
  const sensitiveFields = [
    'phone', 'email', 'streetaddr', 'street', 'address',
    'token', 'api_key', 'api_token', 'password', 'secret',
    'authorization', 'bearer'
  ];
  
  for (const field of sensitiveFields) {
    if (redacted[field]) {
      redacted[field] = '[REDACTED]';
    }
  }
  
  return redacted;
}

// ========================================
// Validation Functions
// ========================================

/**
 * Validate DNS record value based on type
 * @param {string} type - Record type
 * @param {string} value - Record value
 * @returns {Object} { valid: boolean, error: string }
 */
export function validateRecordValue(type, value) {
  switch (type.toUpperCase()) {
    case 'A':
      if (!isValidIPv4(value)) {
        return { valid: false, error: 'Invalid IPv4 address' };
      }
      break;
      
    case 'AAAA':
      if (!isValidIPv6(value)) {
        return { valid: false, error: 'Invalid IPv6 address' };
      }
      break;
      
    case 'CNAME':
    case 'NS':
      if (!isValidHostname(value)) {
        return { valid: false, error: 'Invalid hostname (use FQDN with trailing dot, e.g., example.com.)' };
      }
      break;
      
    case 'MX':
      // MX format: "priority hostname" (e.g., "10 mail.example.com.")
      const mxParts = value.split(' ');
      if (mxParts.length !== 2) {
        return { valid: false, error: 'MX record must be: "priority hostname" (e.g., "10 mail.example.com.")' };
      }
      const priority = parseInt(mxParts[0], 10);
      if (isNaN(priority) || priority < 0 || priority > 65535) {
        return { valid: false, error: 'MX priority must be between 0 and 65535' };
      }
      if (!isValidHostname(mxParts[1])) {
        return { valid: false, error: 'Invalid MX hostname' };
      }
      break;
      
    case 'TXT':
      // TXT records should be in quotes, but API accepts them without
      // Just check it's not empty
      if (!value || value.trim().length === 0) {
        return { valid: false, error: 'TXT record cannot be empty' };
      }
      break;
      
    case 'SRV':
      // SRV format: "priority weight port target"
      const srvParts = value.split(' ');
      if (srvParts.length !== 4) {
        return { valid: false, error: 'SRV record must be: "priority weight port target"' };
      }
      const [srvPriority, weight, port, target] = srvParts;
      if (isNaN(parseInt(srvPriority)) || isNaN(parseInt(weight)) || isNaN(parseInt(port))) {
        return { valid: false, error: 'SRV priority, weight, and port must be numbers' };
      }
      if (!isValidHostname(target)) {
        return { valid: false, error: 'Invalid SRV target hostname' };
      }
      break;
      
    case 'CAA':
      // CAA format: "flags tag value" (e.g., "0 issue \"letsencrypt.org\"")
      const caaParts = value.split(' ');
      if (caaParts.length < 3) {
        return { valid: false, error: 'CAA record must be: "flags tag value"' };
      }
      const flags = parseInt(caaParts[0], 10);
      if (isNaN(flags) || flags < 0 || flags > 255) {
        return { valid: false, error: 'CAA flags must be between 0 and 255' };
      }
      const tag = caaParts[1];
      if (!['issue', 'issuewild', 'iodef'].includes(tag)) {
        return { valid: false, error: 'CAA tag must be issue, issuewild, or iodef' };
      }
      break;
      
    default:
      // For other record types, just check it's not empty
      if (!value || value.trim().length === 0) {
        return { valid: false, error: `${type} record value cannot be empty` };
      }
  }
  
  return { valid: true };
}

/**
 * Validate contact information for domain registration
 * @param {Object} contact - Contact object
 * @returns {Object} { valid: boolean, errors: string[] }
 */
export function validateContact(contact) {
  const errors = [];
  
  // Required fields
  const requiredFields = ['given', 'family', 'email', 'streetaddr', 'city', 'zip', 'country', 'phone', 'type'];
  
  requiredFields.forEach(field => {
    if (!contact[field] || contact[field].toString().trim() === '') {
      errors.push(`Missing required field: ${field}`);
    }
  });
  
  // Validate email format
  if (contact.email && !contact.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
    errors.push('Invalid email address format');
  }
  
  // Validate phone format (basic check for + and digits)
  if (contact.phone && !contact.phone.match(/^\+?[\d\s\.\-()]+$/)) {
    errors.push('Invalid phone number format (use +CC.NNNNNNNN)');
  }
  
  // Validate country code (must be 2 letters)
  if (contact.country && !contact.country.match(/^[A-Z]{2}$/)) {
    errors.push('Country must be 2-letter ISO code (e.g., US, FR, GB)');
  }
  
  // Validate contact type
  const validTypes = ['individual', 'company', 'association', 'publicbody'];
  if (contact.type && !validTypes.includes(contact.type)) {
    errors.push(`Contact type must be one of: ${validTypes.join(', ')}`);
  }
  
  // If type is company, orgname is required
  if (contact.type === 'company' && (!contact.orgname || contact.orgname.trim() === '')) {
    errors.push('Organization name required for company type');
  }
  
  return {
    valid: errors.length === 0,
    errors: errors
  };
}

// If run directly, show usage
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log('Gandi API Client');
  console.log('');
  console.log('This module provides functions for interacting with Gandi API.');
  console.log('Import it in your scripts:');
  console.log('');
  console.log('  import { gandiApi, listDomains, listDnsRecords } from "./gandi-api.js";');
  console.log('');
  console.log('Available functions:');
  console.log('  - readToken()');
  console.log('  - readApiUrl()');
  console.log('  - readDomainCheckerConfig()');
  console.log('  - getRateLimiter(config)');
  console.log('  - gandiApi(endpoint, method, data, queryParams)');
  console.log('  - testAuth()');
  console.log('  - listDomains(options)');
  console.log('  - getDomain(domain)');
  console.log('  - listDnsRecords(domain)');
  console.log('  - getDnsRecord(domain, name, type)');
  console.log('  - createDnsRecord(domain, name, type, values, ttl)');
  console.log('  - deleteDnsRecord(domain, name, type)');
  console.log('  - replaceDnsRecords(domain, records)');
  console.log('  - createSnapshot(domain, name)');
  console.log('  - listSnapshots(domain)');
  console.log('  - restoreSnapshot(domain, snapshotId)');
  console.log('  - checkAvailability(domains)');
  console.log('  - generateVariations(baseName, config)');
  console.log('  - registerDomain(domain, duration, owner, options)');
  console.log('  - renewDomain(domain, duration)');
  console.log('  - getAutoRenewal(domain)');
  console.log('  - setAutoRenewal(domain, enabled, duration, orgId)');
  console.log('  - getDnssecKeys(domain)');
  console.log('  - enableDnssec(domain, options)');
  console.log('  - deleteDnssecKey(domain, keyId)');
  console.log('  - disableDnssec(domain)');
  console.log('  - listEmailForwards(domain)');
  console.log('  - getEmailForward(domain, mailbox)');
  console.log('  - createEmailForward(domain, mailbox, destinations)');
  console.log('  - updateEmailForward(domain, mailbox, destinations)');
  console.log('  - deleteEmailForward(domain, mailbox)');
  console.log('  - listCertificates()');
  console.log('  - getCertificate(certId)');
  console.log('  - requestCertificate(cn, options)');
  console.log('  - updateCertificate(certId, data)');
  console.log('  - deleteCertificate(certId)');
  console.log('  - isValidIPv4(ip)');
  console.log('  - isValidIPv6(ip)');
  console.log('  - isValidHostname(hostname)');
  console.log('  - isValidTTL(ttl)');
  console.log('  - validateRecordValue(type, value)');
  console.log('  - validateContact(contact)');
  console.log('');
  console.log('Configuration:');
  console.log(`  Token: ${TOKEN_FILE}`);
  console.log(`  API URL: ${URL_FILE} (optional)`);
}
