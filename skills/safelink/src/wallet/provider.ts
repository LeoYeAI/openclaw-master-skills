import { createPublicClient, http, type PublicClient } from "viem";
import { baseSepolia, base } from "viem/chains";
import { getConfig } from "../utils/config.js";

// ── Read-only viem public client ──────────────────────────────────────────────
// Use this for eth_call, getLogs, getBalance, etc.
// For write operations, use getMPCWalletClient() from mpc.ts.
//
// PublicClient is used as the return type (not ReturnType<typeof createPublicClient>)
// to avoid the chain-specific transaction type mismatch between base and baseSepolia.

let _client: PublicClient | undefined;

export function getPublicClient(): PublicClient {
  if (_client) return _client;
  const config = getConfig();

  const isMainnet = config.BASE_RPC_URL.includes("mainnet");
  const chain = isMainnet ? base : baseSepolia;

  _client = createPublicClient({
    chain,
    transport: http(config.BASE_RPC_URL),
  }) as PublicClient;

  return _client;
}

export function resetPublicClient(): void {
  _client = undefined;
}
