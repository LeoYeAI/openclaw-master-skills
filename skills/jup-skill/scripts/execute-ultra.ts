#!/usr/bin/env tsx
/**
 * execute-ultra.ts - Execute Ultra orders on Jupiter
 *
 * Usage:
 *   pnpm execute-ultra --request-id "UUID" --signed-tx "BASE64_SIGNED_TX"
 *
 * This script:
 *   1. Takes the requestId from /ultra/v1/order response
 *   2. Takes the signed transaction (sign with wallet-sign.ts first)
 *   3. POSTs to /ultra/v1/execute
 *   4. Returns execution result
 */

import { Command } from "commander";
import { getApiKey, printApiKeyError, isValidBase64, isValidUUID } from "./utils.js";

const EXECUTE_URL = "https://api.jup.ag/ultra/v1/execute";
const REQUEST_TIMEOUT_MS = 30000;

interface ExecuteOptions {
  requestId: string;
  signedTx: string;
  apiKey?: string;
}

interface ExecuteResponse {
  status: "Success" | "Failed";
  signature?: string;
  error?: string;
  code?: string;
  slot?: number;
  inputAmountResult?: string;
  outputAmountResult?: string;
}

async function executeOrder(options: ExecuteOptions): Promise<void> {
  const apiKey = getApiKey(options.apiKey);

  if (!apiKey) {
    printApiKeyError();
    process.exit(1);
  }

  // Validate inputs
  if (!options.requestId) {
    console.error("Error: --request-id is required");
    console.error("Get the requestId from the /ultra/v1/order response");
    process.exit(1);
  }

  if (!isValidUUID(options.requestId)) {
    console.error("Error: Invalid request ID format. Expected UUID format.");
    process.exit(1);
  }

  if (!options.signedTx) {
    console.error("Error: --signed-tx is required");
    console.error("Sign the transaction first using: pnpm wallet-sign --unsigned-tx ...");
    process.exit(1);
  }

  // Validate base64 format
  if (!isValidBase64(options.signedTx)) {
    console.error("Error: Invalid base64 format for signed transaction");
    process.exit(1);
  }

  const body = {
    requestId: options.requestId,
    signedTransaction: options.signedTx,
  };

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(EXECUTE_URL, {
      method: "POST",
      headers: {
        "x-api-key": apiKey,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    // Check for rate limiting
    if (response.status === 429) {
      const retryAfter = response.headers.get("Retry-After");
      console.error("Error: Rate limited by Jupiter API");
      if (retryAfter) {
        console.error(`Retry after: ${retryAfter} seconds`);
      }
      console.error("\nUltra rate limits scale with your executed swap volume.");
      console.error("See: https://dev.jup.ag/docs/ultra/rate-limit.md");
      process.exit(1);
    }

    let data: ExecuteResponse;
    try {
      data = (await response.json()) as ExecuteResponse;
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

    // Output result
    console.log(JSON.stringify(data, null, 2));

    // Additional info to stderr
    if (data.status === "Success" && data.signature) {
      console.error(`\nTransaction successful!`);
      console.error(`Signature: ${data.signature}`);
      console.error(`Explorer: https://solscan.io/tx/${data.signature}`);
    } else if (data.status === "Failed") {
      console.error(`\nTransaction failed!`);
      if (data.error) {
        console.error(`Error: ${data.error}`);
      }
      if (data.code) {
        console.error(`Code: ${data.code}`);
      }
      process.exit(1);
    }
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
  .name("execute-ultra")
  .description("Execute Ultra orders on Jupiter")
  .requiredOption(
    "-r, --request-id <id>",
    "Request ID from /ultra/v1/order response"
  )
  .requiredOption(
    "-t, --signed-tx <base64>",
    "Base64-encoded signed transaction"
  )
  .option("-k, --api-key <key>", "Jupiter API key (or use JUP_API_KEY env var)")
  .action(executeOrder);

program.parse();
