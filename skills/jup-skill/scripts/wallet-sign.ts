#!/usr/bin/env tsx
/**
 * wallet-sign.ts - Sign Solana transactions using a local wallet
 *
 * Usage:
 *   pnpm wallet-sign --unsigned-tx "BASE64_TX" --wallet ~/.config/solana/id.json
 *   pnpm wallet-sign --unsigned-tx "BASE64_TX" --wallet /path/to/wallet.json
 *
 * Supports:
 *   - Solana CLI JSON wallet format (array of 64 bytes)
 *
 * SECURITY NOTE: The --wallet flag is required. This script does not accept
 * private keys via command line arguments to prevent exposure in shell history
 * and process listings.
 */

import { Command } from "commander";
import { Keypair, VersionedTransaction } from "@solana/web3.js";
import { readFileSync, existsSync } from "fs";
import { homedir } from "os";
import { join } from "path";

interface SignOptions {
  unsignedTx: string;
  wallet?: string;
}

/**
 * Expand tilde (~) in file paths to the user's home directory
 */
function expandTilde(filePath: string): string {
  if (filePath.startsWith("~")) {
    return join(homedir(), filePath.slice(1));
  }
  return filePath;
}

function loadKeypairFromJson(filePath: string): Keypair {
  const expandedPath = expandTilde(filePath);

  if (!existsSync(expandedPath)) {
    throw new Error(`Wallet file not found: ${expandedPath}`);
  }

  try {
    const fileContent = readFileSync(expandedPath, "utf-8");
    const secretKey = JSON.parse(fileContent);

    if (!Array.isArray(secretKey) || secretKey.length !== 64) {
      throw new Error(
        "Invalid wallet format. Expected JSON array of 64 bytes (Solana CLI format)"
      );
    }

    return Keypair.fromSecretKey(Uint8Array.from(secretKey));
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new Error(`Invalid JSON in wallet file: ${expandedPath}`);
    }
    throw error;
  }
}

function getKeypair(options: SignOptions): Keypair {
  if (!options.wallet) {
    throw new Error(`
No wallet provided. The --wallet flag is required.

Usage:
  pnpm wallet-sign --unsigned-tx "BASE64_TX" --wallet ~/.config/solana/id.json
  pnpm wallet-sign --unsigned-tx "BASE64_TX" --wallet /path/to/wallet.json

To create a new wallet:
  solana-keygen new -o ~/.config/solana/id.json

SECURITY NOTE: Private keys cannot be passed via command line arguments
to prevent exposure in shell history and process listings.
`);
  }

  return loadKeypairFromJson(options.wallet);
}

async function signTransaction(options: SignOptions): Promise<void> {
  // Load keypair
  let keypair: Keypair;
  try {
    keypair = getKeypair(options);
  } catch (error) {
    if (error instanceof Error) {
      console.error(`Error: ${error.message}`);
    }
    process.exit(1);
  }

  // Decode the unsigned transaction
  let transaction: VersionedTransaction;
  try {
    const txBuffer = Buffer.from(options.unsignedTx, "base64");
    transaction = VersionedTransaction.deserialize(txBuffer);
  } catch (error) {
    console.error("Error: Failed to deserialize transaction");
    console.error("Ensure the transaction is a valid base64-encoded VersionedTransaction");
    process.exit(1);
  }

  // Sign the transaction
  try {
    transaction.sign([keypair]);
  } catch (error) {
    console.error("Error: Failed to sign transaction");
    if (error instanceof Error) {
      console.error(error.message);
    }
    process.exit(1);
  }

  // Serialize and output the signed transaction
  const signedTxBuffer = transaction.serialize();
  const signedTxBase64 = Buffer.from(signedTxBuffer).toString("base64");

  // Output to stdout for piping
  console.log(signedTxBase64);

  // Log signer info to stderr (so it doesn't interfere with piped output)
  console.error(`\nSigned by: ${keypair.publicKey.toBase58()}`);
}

// CLI setup
const program = new Command();

program
  .name("wallet-sign")
  .description(
    "Sign Solana transactions using a local wallet file.\n\n" +
      "SECURITY: Private keys must be stored in wallet files, not passed via\n" +
      "command line arguments (which appear in shell history and process listings)."
  )
  .requiredOption("-t, --unsigned-tx <base64>", "Base64-encoded unsigned transaction")
  .requiredOption(
    "-w, --wallet <path>",
    "Path to Solana CLI JSON wallet file (array of 64 bytes). Supports ~ for home directory."
  )
  .action(signTransaction);

program.parse();
