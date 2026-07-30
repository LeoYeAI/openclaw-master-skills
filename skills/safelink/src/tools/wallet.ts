import { z } from "zod";
import { validateInput } from "../security/input-gate.js";
import { getMPCWalletClient } from "../wallet/mpc.js";
import { getPublicClient } from "../wallet/provider.js";
import { getUSDCBalance, fromAtomicUSDC, getUSDCAddress } from "../payments/usdc.js";
import { getConfig } from "../utils/config.js";
import { logger } from "../utils/logger.js";
import { WalletError } from "../utils/errors.js";

// ── Input schema ──────────────────────────────────────────────────────────────

const WalletSchema = z.object({
  provider: z
    .enum(["auto", "coinbase", "privy"])
    .default("auto")
    .describe(
      "Wallet provider to use. 'auto' picks Coinbase if CDP keys are set, otherwise Privy. " +
        "'coinbase' = Coinbase AgentKit (recommended, no extra signup). " +
        "'privy' = Privy MPC (advanced, requires Privy account)."
    ),
});

export type WalletInput = z.infer<typeof WalletSchema>;

// ── Output type ───────────────────────────────────────────────────────────────

export interface WalletResult {
  provider: "coinbase" | "privy";
  wallet_id: string;
  address: `0x${string}`;
  eth_balance: string;
  usdc_balance: string;
  network: string;
  network_id: number;
  ready: boolean;
  /** First-time only: instructions for persisting the wallet */
  setup_note?: string;
}

// ── Tool handler ──────────────────────────────────────────────────────────────

export async function create_agentic_wallet(rawInput: unknown): Promise<WalletResult> {
  const input = validateInput(WalletSchema, rawInput);
  const config = getConfig();

  // Determine which provider to use
  const hasCoinbase = !!(config.COINBASE_CDP_API_KEY_NAME && config.COINBASE_CDP_API_KEY_PRIVATE_KEY);
  const hasPrivy = !!(config.PRIVY_APP_ID && config.PRIVY_APP_SECRET);

  let resolvedProvider: "coinbase" | "privy";

  if (input.provider === "coinbase") {
    if (!hasCoinbase) {
      throw new WalletError(
        "Coinbase CDP credentials not set. " +
          "Add COINBASE_CDP_API_KEY_NAME and COINBASE_CDP_API_KEY_PRIVATE_KEY to your .env. " +
          "Get them free at portal.cdp.coinbase.com."
      );
    }
    resolvedProvider = "coinbase";
  } else if (input.provider === "privy") {
    if (!hasPrivy) {
      throw new WalletError(
        "Privy credentials not set. " +
          "Add PRIVY_APP_ID and PRIVY_APP_SECRET to your .env. " +
          "Get them at dashboard.privy.io."
      );
    }
    resolvedProvider = "privy";
  } else {
    // auto: prefer Coinbase (simpler), fall back to Privy
    if (hasCoinbase) {
      resolvedProvider = "coinbase";
    } else if (hasPrivy) {
      resolvedProvider = "privy";
    } else {
      throw new WalletError(
        "No wallet provider configured. " +
          "Quick option: set COINBASE_CDP_API_KEY_NAME + COINBASE_CDP_API_KEY_PRIVATE_KEY " +
          "(free at portal.cdp.coinbase.com). " +
          "Or: set PRIVY_APP_ID + PRIVY_APP_SECRET (dashboard.privy.io)."
      );
    }
  }

  logger.info({ event: "create_agentic_wallet", provider: resolvedProvider });

  // Initialize wallet
  const wallet = await getMPCWalletClient(resolvedProvider);
  const publicClient = getPublicClient();

  // Fetch balances
  const [ethBalanceWei, usdcAtomicBalance, chainId] = await Promise.all([
    publicClient.getBalance({ address: wallet.address }),
    getUSDCBalance(wallet.address, config.BASE_RPC_URL.includes("mainnet") ? "base-mainnet" : "base-sepolia"),
    publicClient.getChainId(),
  ]);

  const ethBalance = (Number(ethBalanceWei) / 1e18).toFixed(6);
  const usdcBalance = fromAtomicUSDC(usdcAtomicBalance).toFixed(2);
  const isMainnet = config.BASE_RPC_URL.includes("mainnet");
  const network = isMainnet ? "base-mainnet" : "base-sepolia";

  const isFirstTime = resolvedProvider === "coinbase" && !process.env["COINBASE_WALLET_DATA"];

  const result: WalletResult = {
    provider: wallet.provider,
    wallet_id: wallet.walletId,
    address: wallet.address,
    eth_balance: `${ethBalance} ETH`,
    usdc_balance: `${usdcBalance} USDC`,
    network,
    network_id: chainId,
    ready: true,
    ...(isFirstTime
      ? {
          setup_note:
            "NEW WALLET CREATED. Check stderr/logs for COINBASE_WALLET_DATA — " +
            "add it to your .env to reuse this wallet after restart. " +
            "Fund with ETH for gas: https://faucet.base.org. " +
            "Fund with USDC: https://faucet.circle.com.",
        }
      : undefined),
  };

  logger.info({
    event: "wallet_ready",
    provider: wallet.provider,
    address: wallet.address,
    network,
    ethBalance,
    usdcBalance,
  });

  return result;
}
