import { createPublicClient, http, type TransactionRequest, type Hash } from "viem";
import { baseSepolia, base } from "viem/chains";
import { getConfig } from "../utils/config.js";
import { WalletError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";
import type { MPCWallet } from "./types.js";

// 鈹€鈹€ Coinbase AgentKit MPC Wallet 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
//
// Uses Coinbase Developer Platform (CDP) via AgentKit v0.4.
// Private keys never leave Coinbase's MPC infrastructure.
//
// Required env vars:
//   COINBASE_CDP_API_KEY_NAME        鈥?CDP API key name (from portal.cdp.coinbase.com)
//   COINBASE_CDP_API_KEY_PRIVATE_KEY 鈥?CDP API key private key (PEM or compact)
//
// Optional:
//   COINBASE_WALLET_DATA 鈥?JSON string from a previous wallet export (for persistence)

class CoinbaseMPCWallet implements MPCWallet {
  readonly provider = "coinbase" as const;
  readonly address: `0x${string}`;
  readonly walletId: string;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private readonly walletProvider: any;

  constructor(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    walletProvider: any,
    address: `0x${string}`,
    walletId: string
  ) {
    this.walletProvider = walletProvider;
    this.address = address;
    this.walletId = walletId;
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

    // Resolve gas if not provided
    const gasLimit =
      tx.gas ??
      (await publicClient.estimateGas({
        account: this.address,
        to: tx.to,
        data: tx.data,
        value: tx.value,
      }));

    logger.debug({
      event: "coinbase_mpc_sign_start",
      to: tx.to,
      gas: gasLimit.toString(),
    });

    // AgentKit WalletProvider.sendTransaction accepts an ethers-style tx
    const hash: string = await this.walletProvider.sendTransaction({
      to: tx.to,
      data: tx.data ?? "0x",
      value: tx.value ?? 0n,
      gasLimit,
    });

    logger.info({ event: "coinbase_tx_sent", hash, provider: "coinbase" });
    return hash as Hash;
  }

  async signTypedData(params: {
    domain: Record<string, unknown>;
    types: Record<string, unknown>;
    primaryType: string;
    message: Record<string, unknown>;
  }): Promise<`0x${string}`> {
    const signature: string = await this.walletProvider.signTypedData(params);
    return signature as `0x${string}`;
  }

  async signMessage(message: string): Promise<`0x${string}`> {
    const signature: string = await this.walletProvider.signMessage(message);
    return signature as `0x${string}`;
  }

  /**
   * Export wallet data for persistence.
   * Store the returned string in COINBASE_WALLET_DATA env var to reload the same wallet.
   */
  async exportWalletData(): Promise<string> {
    const data = await this.walletProvider.exportWallet();
    return JSON.stringify(data);
  }
}

// 鈹€鈹€ Singleton cache 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

let _wallet: CoinbaseMPCWallet | undefined;

// 鈹€鈹€ Public API 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

/**
 * Get or create a Coinbase AgentKit MPC wallet.
 *
 * On first call with no COINBASE_WALLET_DATA: creates a new wallet and logs
 * the wallet data that should be saved to env for persistence.
 *
 * On subsequent calls (COINBASE_WALLET_DATA set): loads the existing wallet.
 */
export async function getCoinbaseWalletClient(): Promise<CoinbaseMPCWallet> {
  if (_wallet) return _wallet;

  const config = getConfig();
  if (!config.COINBASE_CDP_API_KEY_NAME || !config.COINBASE_CDP_API_KEY_PRIVATE_KEY) {
    throw new WalletError(
      "Coinbase CDP credentials not configured. " +
        "Set COINBASE_CDP_API_KEY_NAME and COINBASE_CDP_API_KEY_PRIVATE_KEY in your .env. " +
        "Get these from portal.cdp.coinbase.com."
    );
  }

  let CdpWalletProvider: {
    configureWithWallet: (config: {
      apiKeyName: string;
      apiKeyPrivateKey: string;
      walletData?: string;
      networkId: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    }) => Promise<any>;
  };

  try {
    const agentkit = await import("@coinbase/agentkit");
    CdpWalletProvider = agentkit.CdpWalletProvider;
  } catch {
    throw new WalletError(
      "@coinbase/agentkit is not installed. Run: npm install @coinbase/agentkit"
    );
  }

  const networkId = config.BASE_RPC_URL.includes("mainnet") ? "base" : "base-sepolia";
  const existingWalletData = process.env["COINBASE_WALLET_DATA"];

  let walletProvider: Awaited<ReturnType<typeof CdpWalletProvider.configureWithWallet>>;

  try {
    walletProvider = await CdpWalletProvider.configureWithWallet({
      apiKeyName: config.COINBASE_CDP_API_KEY_NAME,
      apiKeyPrivateKey: config.COINBASE_CDP_API_KEY_PRIVATE_KEY,
      ...(existingWalletData ? { walletData: existingWalletData } : {}),
      networkId,
    });
  } catch (err) {
    throw new WalletError(
      `Failed to configure Coinbase wallet: ${err instanceof Error ? err.message : String(err)}`
    );
  }

  const address = (await walletProvider.getAddress()) as `0x${string}`;
  const walletId = address; // CDP wallets use address as stable identifier

  if (!existingWalletData) {
    // First-time wallet creation 鈥?export data so user can persist it
    try {
      const exported = await walletProvider.exportWallet();
      const walletDataStr = JSON.stringify(exported);
      logger.info({
        event: "coinbase_wallet_created",
        address,
        note: "IMPORTANT: Save COINBASE_WALLET_DATA to your .env to reuse this wallet",
        wallet_data_hint: walletDataStr.slice(0, 60) + "...",
      });
      // Print to stderr so operator sees it even in MCP mode
      process.stderr.write(
        `\n[SafeLink] New Coinbase wallet created: ${address}\n` +
          `[SafeLink] Add to your .env:\n` +
          `COINBASE_WALLET_DATA='${walletDataStr}'\n\n`
      );
    } catch {
      logger.warn({ event: "coinbase_wallet_export_failed" });
    }
  } else {
    logger.info({ event: "coinbase_wallet_loaded", address });
  }

  _wallet = new CoinbaseMPCWallet(walletProvider, address, walletId);
  return _wallet;
}

/** Reset cached wallet (useful in tests). */
export function resetCoinbaseWallet(): void {
  _wallet = undefined;
}


