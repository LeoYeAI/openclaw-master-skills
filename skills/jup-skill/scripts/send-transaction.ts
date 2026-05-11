#!/usr/bin/env tsx
/**
 * send-transaction.ts - Send signed transactions to Solana RPC
 *
 * Usage:
 *   pnpm send-transaction --signed-tx "BASE64_SIGNED_TX"
 *   pnpm send-transaction --signed-tx "BASE64_SIGNED_TX" --rpc-url "https://your-rpc.com"
 *
 * This script:
 *   1. Takes a signed transaction (base64)
 *   2. Sends it to the specified RPC endpoint
 *   3. Waits for confirmation
 *   4. Returns the transaction signature
 *
 * Use this for Metis swaps or any transaction that needs manual RPC submission.
 * For Ultra swaps, use execute-ultra.ts instead (Jupiter handles RPC internally).
 */

import { Command } from "commander";
import {
  Connection,
  VersionedTransaction,
  SendTransactionError,
} from "@solana/web3.js";

const DEFAULT_RPC_URL = "https://api.mainnet-beta.solana.com";

interface SendOptions {
  signedTx: string;
  rpcUrl?: string;
  skipPreflight?: boolean;
  maxRetries?: string;
}

function getRpcUrl(providedUrl?: string): string {
  if (providedUrl) return providedUrl;
  if (process.env.SOLANA_RPC_URL) return process.env.SOLANA_RPC_URL;
  return DEFAULT_RPC_URL;
}

async function sendTransaction(options: SendOptions): Promise<void> {
  const rpcUrl = getRpcUrl(options.rpcUrl);

  console.error(`Using RPC: ${rpcUrl}`);

  if (rpcUrl === DEFAULT_RPC_URL) {
    console.error("Warning: Using public Solana RPC which is rate-limited.");
    console.error("For production, set SOLANA_RPC_URL to your own RPC endpoint.");
  }

  // Deserialize the transaction
  let transaction: VersionedTransaction;
  try {
    const txBuffer = Buffer.from(options.signedTx, "base64");
    transaction = VersionedTransaction.deserialize(txBuffer);
  } catch (error) {
    console.error("Error: Failed to deserialize transaction");
    console.error("Ensure the transaction is a valid base64-encoded signed VersionedTransaction");
    process.exit(1);
  }

  // Check if transaction is signed
  if (transaction.signatures.length === 0) {
    console.error("Error: Transaction has no signatures");
    console.error("Sign the transaction first using: pnpm wallet-sign --unsigned-tx ...");
    process.exit(1);
  }
  
  // Create connection
  const connection = new Connection(rpcUrl, "confirmed");

  // Send transaction
  try {
    console.error("Sending transaction...");

    const maxRetries = options.maxRetries ? parseInt(options.maxRetries, 10) : 3;
    if (isNaN(maxRetries) || maxRetries < 0) {
      console.error("Error: --max-retries must be a non-negative integer");
      process.exit(1);
    }

    const signature = await connection.sendTransaction(transaction, {
      skipPreflight: options.skipPreflight ?? false,
      maxRetries,
    });

    console.error("Transaction sent, waiting for confirmation...");

    // Wait for confirmation using non-deprecated API
    const latestBlockhash = await connection.getLatestBlockhash();
    const confirmation = await connection.confirmTransaction({
      signature,
      blockhash: latestBlockhash.blockhash,
      lastValidBlockHeight: latestBlockhash.lastValidBlockHeight,
    }, "confirmed");

    if (confirmation.value.err) {
      console.error("Error: Transaction failed on-chain");
      console.error(JSON.stringify(confirmation.value.err, null, 2));
      process.exit(1);
    }

    // Output signature to stdout
    console.log(signature);

    // Additional info to stderr
    console.error(`\nTransaction confirmed!`);
    console.error(`Signature: ${signature}`);
    console.error(`Explorer: https://solscan.io/tx/${signature}`);
  } catch (error) {
    if (error instanceof SendTransactionError) {
      console.error("Error: Failed to send transaction");
      console.error(`Message: ${error.message}`);

      // Try to get more details
      const logs = error.logs;
      if (logs && logs.length > 0) {
        console.error("\nTransaction logs:");
        logs.forEach((log) => console.error(`  ${log}`));
      }
    } else if (error instanceof Error) {
      console.error(`Error: ${error.message}`);

      // Common error hints
      if (error.message.includes("blockhash")) {
        console.error("\nHint: The transaction's blockhash may have expired.");
        console.error("Request a fresh transaction and try again.");
      } else if (error.message.includes("insufficient")) {
        console.error("\nHint: The wallet may have insufficient SOL for fees.");
      } else if (error.message.includes("429") || error.message.includes("rate")) {
        console.error("\nHint: RPC rate limited. Try a different RPC endpoint.");
        console.error("You can specify one with: --rpc-url <url>");
      }
    } else {
      console.error("Unknown error occurred");
    }
    process.exit(1);
  }
}

// CLI setup
const program = new Command();

program
  .name("send-transaction")
  .description("Send signed transactions to Solana RPC")
  .requiredOption("-t, --signed-tx <base64>", "Base64-encoded signed transaction")
  .option(
    "-r, --rpc-url <url>",
    `RPC endpoint URL (default: ${DEFAULT_RPC_URL}, or SOLANA_RPC_URL env var)`
  )
  .option(
    "--skip-preflight",
    "Skip preflight transaction checks (faster but less safe)"
  )
  .option("--max-retries <number>", "Maximum send retries (default: 3)")
  .action(sendTransaction);

program.parse();
