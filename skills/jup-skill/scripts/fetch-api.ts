#!/usr/bin/env tsx
/**
 * fetch-api.ts - Fetch data from any Jupiter API endpoint
 *
 * Usage:
 *   pnpm fetch-api --endpoint /ultra/v1/search --params '{"query":"SOL"}'
 *   pnpm fetch-api --endpoint /ultra/v1/order --params '{"inputMint":"So11...","outputMint":"EPjF...","amount":"1000000","taker":"YOUR_WALLET"}'
 *   pnpm fetch-api --endpoint /swap/v1/swap --method POST --body '{"quoteResponse":{...},"userPublicKey":"..."}'
 */

import { Command } from "commander";
import { getApiKey, printApiKeyError } from "./utils.js";

const BASE_URL = "https://api.jup.ag";
const REQUEST_TIMEOUT_MS = 30000;

interface FetchOptions {
  endpoint: string;
  params?: string;
  body?: string;
  method: string;
  apiKey?: string;
}

async function fetchApi(options: FetchOptions): Promise<void> {
  const apiKey = getApiKey(options.apiKey);

  if (!apiKey) {
    printApiKeyError();
    process.exit(1);
  }

  // Build URL with query params for GET requests
  let url = `${BASE_URL}${options.endpoint}`;

  const headers: Record<string, string> = {
    "x-api-key": apiKey,
    "Content-Type": "application/json",
  };

  const fetchOptions: RequestInit = {
    method: options.method.toUpperCase(),
    headers,
  };

  // Handle params for GET or body for POST
  if (options.method.toUpperCase() === "GET" && options.params) {
    try {
      const params = JSON.parse(options.params);
      const searchParams = new URLSearchParams();
      for (const [key, value] of Object.entries(params)) {
        searchParams.append(key, String(value));
      }
      url += `?${searchParams.toString()}`;
    } catch (e) {
      console.error("Error: Invalid JSON in --params");
      console.error("Expected format: '{\"key\":\"value\"}'");
      process.exit(1);
    }
  } else if (options.method.toUpperCase() === "POST") {
    if (options.body) {
      try {
        // Validate JSON
        JSON.parse(options.body);
        fetchOptions.body = options.body;
      } catch (e) {
        console.error("Error: Invalid JSON in --body");
        process.exit(1);
      }
    } else if (options.params) {
      // Allow --params for POST body as well
      try {
        JSON.parse(options.params);
        fetchOptions.body = options.params;
      } catch (e) {
        console.error("Error: Invalid JSON in --params");
        process.exit(1);
      }
    }
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(url, { ...fetchOptions, signal: controller.signal });

    // Check for rate limiting
    if (response.status === 429) {
      const retryAfter = response.headers.get("Retry-After");
      console.error("Error: Rate limited by Jupiter API");
      if (retryAfter) {
        console.error(`Retry after: ${retryAfter} seconds`);
      }
      console.error("\nConsider upgrading your API tier at https://portal.jup.ag");
      process.exit(1);
    }

    let data;
    try {
      data = await response.json();
    } catch (e) {
      console.error("Error: API returned non-JSON response");
      console.error(`Status: ${response.status}`);
      const text = await response.text().catch(() => "Unable to read response");
      console.error(`Body: ${text.slice(0, 500)}`);
      process.exit(1);
    }

    if (!response.ok) {
      console.error(`Error: API returned status ${response.status}`);
      console.error(JSON.stringify(data, null, 2));
      process.exit(1);
    }

    // Output JSON to stdout for piping to other tools
    console.log(JSON.stringify(data, null, 2));
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === "AbortError") {
        console.error(`Error: Request timed out after ${REQUEST_TIMEOUT_MS / 1000} seconds`);
      } else {
        console.error(`Network error: ${error.message}`);
      }
    } else {
      console.error("Unknown error occurred");
    }
    process.exit(1);
  } finally {
    clearTimeout(timeoutId);
  }
}

// CLI setup
const program = new Command();

program
  .name("fetch-api")
  .description("Fetch data from any Jupiter API endpoint")
  .requiredOption("-e, --endpoint <path>", "API endpoint path (e.g., /ultra/v1/order)")
  .option("-p, --params <json>", "Query parameters as JSON string (for GET) or body (for POST)")
  .option("-b, --body <json>", "Request body as JSON string (for POST)")
  .option("-m, --method <method>", "HTTP method (GET or POST)", "GET")
  .option("-k, --api-key <key>", "Jupiter API key (or use JUP_API_KEY env var)")
  .action(fetchApi);

program.parse();
