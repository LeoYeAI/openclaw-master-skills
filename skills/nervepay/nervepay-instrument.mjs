#!/usr/bin/env node
/**
 * NervePay Auto-Instrumentation
 *
 * Automatically intercepts ALL HTTP/HTTPS requests and tracks them to NervePay.
 * NO CODE CHANGES NEEDED - agents don't need to remember to track.
 *
 * SETUP:
 *   1. Set required env vars (NERVEPAY_DID, NERVEPAY_PRIVATE_KEY)
 *   2. Load this script before running your agent:
 *      node --import ./nervepay-skill/nervepay-instrument.mjs your-agent.js
 *
 *   OR set in environment:
 *      export NODE_OPTIONS="--import /path/to/nervepay-instrument.mjs"
 *
 * HOW IT WORKS:
 *   - Patches global fetch() to intercept all HTTP calls
 *   - Also patches http.request() and https.request()
 *   - Automatically tracks each call to NervePay (async, non-blocking)
 *   - Filters out calls to NervePay itself (don't track tracking!)
 *   - Captures timing, success/failure, and response codes
 */

import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { spawn } from 'node:child_process';
import * as http from 'node:http';
import * as https from 'node:https';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuration
const NERVEPAY_API_URL = process.env.NERVEPAY_API_URL || 'https://api.nervepay.xyz';
const NERVEPAY_DID = process.env.NERVEPAY_DID;
const NERVEPAY_PRIVATE_KEY = process.env.NERVEPAY_PRIVATE_KEY;
const NERVEPAY_AUTO_TRACK = process.env.NERVEPAY_AUTO_TRACK !== 'false'; // Opt-out via env var

// Don't track if credentials are missing
const canTrack = NERVEPAY_DID && NERVEPAY_PRIVATE_KEY && NERVEPAY_AUTO_TRACK;

if (!canTrack) {
  if (!NERVEPAY_AUTO_TRACK) {
    console.warn('[NervePay] Auto-tracking disabled via NERVEPAY_AUTO_TRACK=false');
  } else if (!NERVEPAY_DID || !NERVEPAY_PRIVATE_KEY) {
    console.warn('[NervePay] Auto-tracking disabled: Missing NERVEPAY_DID or NERVEPAY_PRIVATE_KEY');
  }
}

// Helper: Extract service name and endpoint from URL
function parseUrl(url) {
  try {
    const parsed = typeof url === 'string' ? new URL(url) : url;
    const serviceName = parsed.hostname.replace(/^(www\.|api\.)/, '').split('.')[0];
    const endpoint = parsed.pathname;
    return { serviceName, endpoint, hostname: parsed.hostname };
  } catch {
    return { serviceName: 'unknown', endpoint: '/', hostname: 'unknown' };
  }
}

// Helper: Should we track this URL?
function shouldTrack(url) {
  if (!canTrack) return false;

  try {
    const parsed = typeof url === 'string' ? new URL(url) : url;
    const hostname = parsed.hostname;

    // Don't track calls to NervePay API itself (avoid infinite loop)
    if (hostname.includes('nervepay.xyz') || hostname.includes('nervepay')) {
      return false;
    }

    // Don't track localhost/internal calls
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.') || hostname.startsWith('10.')) {
      return false;
    }

    return true;
  } catch {
    return false;
  }
}

// Helper: Track to NervePay (async, non-blocking)
function trackToNervePay(serviceName, endpoint, method, success, responseTimeMs, statusCode) {
  if (!shouldTrack(`https://${serviceName}`)) return;

  const trackScript = join(__dirname, 'nervepay-track.mjs');

  // Build command args
  const args = [
    trackScript,
    serviceName,
    endpoint,
    success ? 'success' : 'failure',
    responseTimeMs.toString(),
  ];

  if (method) args.push('', method); // Empty amount, then method

  // Spawn as detached background process (don't block)
  const child = spawn('node', args, {
    detached: true,
    stdio: 'ignore',
    env: process.env
  });

  child.unref(); // Let parent exit without waiting
}

// ============================================================================
// PATCH GLOBAL FETCH
// ============================================================================

if (typeof globalThis.fetch === 'function') {
  const originalFetch = globalThis.fetch;

  globalThis.fetch = async function patchedFetch(url, options = {}) {
    if (!shouldTrack(url)) {
      return originalFetch(url, options);
    }

    const { serviceName, endpoint } = parseUrl(url);
    const method = (options.method || 'GET').toUpperCase();
    const startTime = Date.now();

    try {
      const response = await originalFetch(url, options);
      const responseTime = Date.now() - startTime;
      const success = response.ok;

      // Track in background
      trackToNervePay(serviceName, endpoint, method, success, responseTime, response.status);

      return response;
    } catch (error) {
      const responseTime = Date.now() - startTime;

      // Track failure
      trackToNervePay(serviceName, endpoint, method, false, responseTime, 0);

      throw error;
    }
  };

  console.log('[NervePay] Instrumented: global fetch()');
}

// ============================================================================
// PATCH HTTP.REQUEST AND HTTPS.REQUEST
// ============================================================================

function patchHttpModule(httpModule, moduleName) {
  const originalRequest = httpModule.request;

  // Use Object.defineProperty to override read-only property
  try {
    Object.defineProperty(httpModule, 'request', {
      value: function patchedRequest(...args) {
    // Parse URL from arguments (can be url string, URL object, or options object)
    let url = args[0];
    if (typeof url === 'string') {
      url = `${moduleName}://${url}`;
    } else if (url instanceof URL) {
      url = url.href;
    } else if (typeof url === 'object') {
      const protocol = moduleName === 'https' ? 'https:' : 'http:';
      const hostname = url.hostname || url.host || 'localhost';
      const port = url.port ? `:${url.port}` : '';
      const path = url.path || '/';
      url = `${protocol}//${hostname}${port}${path}`;
    }

    if (!shouldTrack(url)) {
      return originalRequest.apply(this, args);
    }

    const { serviceName, endpoint } = parseUrl(url);
    const startTime = Date.now();
    let tracked = false;

    const request = originalRequest.apply(this, args);

    // Track on response
    request.on('response', (response) => {
      if (tracked) return;
      tracked = true;

      const responseTime = Date.now() - startTime;
      const success = response.statusCode >= 200 && response.statusCode < 400;
      const method = request.method || 'GET';

      trackToNervePay(serviceName, endpoint, method, success, responseTime, response.statusCode);
    });

    // Track on error
    request.on('error', () => {
      if (tracked) return;
      tracked = true;

      const responseTime = Date.now() - startTime;
      const method = request.method || 'GET';

      trackToNervePay(serviceName, endpoint, method, false, responseTime, 0);
    });

    return request;
      },
      writable: true,
      configurable: true
    });

    console.log(`[NervePay] Instrumented: ${moduleName}.request()`);
  } catch (error) {
    console.warn(`[NervePay] Could not instrument ${moduleName}.request():`, error.message);
  }
}

patchHttpModule(http, 'http');
patchHttpModule(https, 'https');

console.log('[NervePay] Auto-instrumentation active. All external HTTP calls will be tracked automatically.');
console.log('[NervePay] To disable: export NERVEPAY_AUTO_TRACK=false');
