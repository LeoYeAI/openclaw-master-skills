import { PrivyClient } from "@privy-io/server-auth";
import {
  createPublicClient,
  http,
  type TransactionRequest,
  type Hash,
  serializeTransaction,
  parseTransaction,
} from "viem";
import { baseSepolia, base } from "viem/chains";
import { getConfig } from "../utils/config.js";
import { WalletError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";
import type { MPCWallet, WalletCreateResult } from "./types.js";

// ── Privy MPC Wallet implementation ──────────────────────────────────────────

class PrivyMPCWallet implements MPCWallet {
  readonly provider = "privy" as const;
  readonly address: `0x${string}`;
  readonly walletId: string;

  private readonly privy: PrivyClient;

  constructor(privy: PrivyClient, walletId: string, address: `0x${string}`) {
    this.privy = privy;
    this.walletId = walletId;
    this.address = address;
  }

  async sendTransaction(
    tx: TransactionRequest & { to: `0x${string}` }
  ): Promise<Hash> {
    const config = getConfig();
    const isMainnet = config.BASE_RPC_URL.includes("mainnet");
    const publicClient = createPublicClient({
      chain: isMainnet ? base : baseSepolia,
      transport: http(config.BASE_RPC_URL),
    });

    // Fetch nonce and gas if not provided
    const [nonce, gasPrice, chainId] = await Promise.all([
      tx.nonce !== undefined
        ? Promise.resolve(tx.nonce as number)
        : publicClient.getTransactionCount({ address: this.address }),
      tx.gasPrice ?? publicClient.getGasPrice(),
      publicClient.getChainId(),
    ]);

    const gasLimit =
      tx.gas ??
      (await publicClient.estimateGas({
        account: this.address,
        to: tx.to,
        data: tx.data,
        value: tx.value,
      }));

    // Build the transaction object for Privy signing
    const preparedTx = {
      to: tx.to,
      data: tx.data ?? "0x",
      value: (tx.value ?? 0n).toString(),
      nonce,
      gasLimit: gasLimit.toString(),
      gasPrice: gasPrice.toString(),
      chainId,
    };

    logger.debug({
      event: "mpc_sign_start",
      provider: "privy",
      to: preparedTx.to,
      chainId,
    });

    // Privy signs without ever exposing the private key.
    // The signing happens inside Privy's HSM infrastructure.
    const { hash } = await (this.privy as unknown as {
      walletApi: {
        ethereum: {
          sendTransaction: (params: {
            walletId: string;
            caip2: string;
            transaction: typeof preparedTx;
          }) => Promise<{ hash: string }>;
        };
      };
    }).walletApi.ethereum.sendTransaction({
      walletId: this.walletId,
      caip2: `eip155:${chainId}`,
      transaction: preparedTx,
    });

    logger.info({ event: "tx_sent", hash, provider: "privy" });
    return hash as Hash;
  }

  async signTypedData(params: {
    domain: Record<string, unknown>;
    types: Record<string, unknown>;
    primaryType: string;
    message: Record<string, unknown>;
  }): Promise<`0x${string}`> {
    const chainId = await getChainId(); // authoritative from RPC, not string pattern

    const { signature } = await (this.privy as unknown as {
      walletApi: {
        ethereum: {
          signTypedData: (p: {
            walletId: string;
            caip2: string;
            typedData: typeof params;
          }) => Promise<{ signature: string }>;
        };
      };
    }).walletApi.ethereum.signTypedData({
      walletId: this.walletId,
      caip2: `eip155:${chainId}`,
      typedData: params,
    });

    return signature as `0x${string}`;
  }

  async signMessage(message: string): Promise<`0x${string}`> {
    const chainId = await getChainId(); // authoritative from RPC

    const { signature } = await (this.privy as unknown as {
      walletApi: {
        ethereum: {
          signMessage: (p: {
            walletId: string;
            caip2: string;
            message: { raw: string };
          }) => Promise<{ signature: string }>;
        };
      };
    }).walletApi.ethereum.signMessage({
      walletId: this.walletId,
      caip2: `eip155:${chainId}`,
      message: { raw: message },
    });

    return signature as `0x${string}`;
  }
}

// ── Cached chain ID (avoids repeated RPC calls) ───────────────────────────────

let _chainId: number | undefined;

async function getChainId(): Promise<number> {
  if (_chainId !== undefined) return _chainId;
  const config = getConfig();
  const client = createPublicClient({
    transport: http(config.BASE_RPC_URL),
  });
  _chainId = await client.getChainId();
  return _chainId;
}

// ── Singleton cache ───────────────────────────────────────────────────────────

let _wallet: MPCWallet | undefined;

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Get or create the MPC wallet for this agent.
 *
 * Provider selection (in priority order):
 *  1. WALLET_PROVIDER env var (explicit override)
 *  2. If COINBASE_CDP_API_KEY_NAME is set → Coinbase AgentKit
 *  3. If PRIVY_APP_ID is set → Privy
 *
 * Private keys are NEVER stored locally or exposed.
 */
export async function getMPCWalletClient(
  preferredProvider?: "coinbase" | "privy"
): Promise<MPCWallet> {
  if (_wallet) return _wallet;

  const config = getConfig();
  const hasCoinbase = !!(config.COINBASE_CDP_API_KEY_NAME && config.COINBASE_CDP_API_KEY_PRIVATE_KEY);
  const hasPrivy = !!(config.PRIVY_APP_ID && config.PRIVY_APP_SECRET);

  const resolveProvider = (
    preferredProvider?: "coinbase" | "privy"
  ): "coinbase" | "privy" => {
    if (preferredProvider === "coinbase") return "coinbase";
    if (preferredProvider === "privy") return "privy";
    if (config.WALLET_PROVIDER === "coinbase") return "coinbase";
    if (config.WALLET_PROVIDER === "privy") return "privy";
    return hasCoinbase ? "coinbase" : "privy";
  };

  const resolvedProvider = resolveProvider(preferredProvider);

  if (resolvedProvider === "coinbase") {
    if (!hasCoinbase) {
      throw new WalletError(
        "Wallet provider 'coinbase' requested, but COINBASE_CDP_API_KEY_NAME / COINBASE_CDP_API_KEY_PRIVATE_KEY are not set."
      );
    }
    const { getCoinbaseWalletClient } = await import("./coinbase.js");
    _wallet = await getCoinbaseWalletClient();
    return _wallet;
  }

  // Privy path ↓ (falls through to existing implementation)
  if (!hasPrivy) {
    throw new WalletError(
      "No wallet provider available. Set COINBASE_CDP_API_KEY_NAME/PRIVATE_KEY " +
        "or PRIVY_APP_ID/APP_SECRET in your .env."
    );
  }

  const privy = new PrivyClient(config.PRIVY_APP_ID!, config.PRIVY_APP_SECRET!);

  let walletId = config.PRIVY_WALLET_ID;
  let address: `0x${string}`;

  if (walletId) {
    // Load existing wallet
    try {
      const wallet = await (privy as unknown as {
        walletApi: {
          getWallet: (p: { id: string }) => Promise<{ id: string; address: string }>;
        };
      }).walletApi.getWallet({ id: walletId });

      address = wallet.address as `0x${string}`;
      logger.info({ event: "wallet_loaded", walletId, address });
    } catch (err) {
      throw new WalletError(
        `Failed to load Privy wallet ${walletId}: ${err instanceof Error ? err.message : String(err)}`
      );
    }
  } else {
    // Create new wallet
    try {
      const created = await (privy as unknown as {
        walletApi: {
          create: (p: { chainType: string }) => Promise<{ id: string; address: string }>;
        };
      }).walletApi.create({ chainType: "ethereum" });

      walletId = created.id;
      address = created.address as `0x${string}`;

      logger.info({
        event: "wallet_created",
        walletId,
        address,
        note: "Save PRIVY_WALLET_ID=" + walletId + " to your .env to reuse this wallet",
      });
    } catch (err) {
      throw new WalletError(
        `Failed to create Privy wallet: ${err instanceof Error ? err.message : String(err)}`
      );
    }
  }

  _wallet = new PrivyMPCWallet(privy, walletId, address);
  return _wallet;
}

/** Get the agent's wallet address without signing anything. */
export async function getAgentAddress(): Promise<`0x${string}`> {
  const wallet = await getMPCWalletClient();
  return wallet.address;
}

/** Reset cached wallet and chain ID (useful in tests). */
export function resetWallet(): void {
  _wallet = undefined;
  _chainId = undefined;
}
