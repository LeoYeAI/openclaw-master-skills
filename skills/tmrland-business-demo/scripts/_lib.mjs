/**
 * Shared HTTP helper for TMR Land business scripts.
 * Reads TMR_API_KEY and TMR_BASE_URL from env.
 */

const API_KEY = (process.env.TMR_API_KEY ?? "").trim();
const BASE_URL = (process.env.TMR_BASE_URL ?? "https://tmrland.com/api/v1").replace(/\/$/, "");

if (!API_KEY) {
  console.error("Error: TMR_API_KEY environment variable is required.");
  process.exit(1);
}

/**
 * Make an authenticated request to the TMR Land API.
 * Exits the process on non-2xx responses.
 * @param {string} method - HTTP method
 * @param {string} path - API path (e.g. "/businesses/me")
 * @param {object|null} body - JSON body for POST/PATCH
 * @returns {Promise<object>} parsed JSON response
 */
export async function tmrFetch(method, path, body = null) {
  const { ok, status, data, error } = await tmrFetchSafe(method, path, body);
  if (!ok) {
    console.error(`API error ${status}: ${error}`);
    process.exit(1);
  }
  return data;
}

/**
 * Make an authenticated request without exiting on failure.
 * @param {string} method - HTTP method
 * @param {string} path - API path
 * @param {object|null} body - JSON body for POST/PATCH
 * @returns {Promise<{ok: boolean, status: number, data: object|null, error: string|null}>}
 */
export async function tmrFetchSafe(method, path, body = null) {
  const url = `${BASE_URL}${path}`;
  const opts = {
    method,
    headers: {
      "Authorization": `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
  };
  if (body !== null) {
    opts.body = JSON.stringify(body);
  }
  const resp = await fetch(url, opts);
  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    return { ok: false, status: resp.status, data: null, error: text };
  }
  const data = await resp.json();
  return { ok: true, status: resp.status, data, error: null };
}

/**
 * Parse --key value pairs and positional args from argv.
 */
export function parseArgs(argv) {
  const args = argv.slice(2);
  const named = {};
  const positional = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "-h" || args[i] === "--help") {
      return { help: true, named, positional };
    } else if (args[i].startsWith("--")) {
      const key = args[i].slice(2);
      named[key] = args[i + 1] ?? "";
      i++;
    } else {
      positional.push(args[i]);
    }
  }
  return { help: false, named, positional };
}
