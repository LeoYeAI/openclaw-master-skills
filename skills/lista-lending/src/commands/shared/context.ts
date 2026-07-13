import type { Address } from "viem";
import type { LendingContext } from "../../context.js";
import type { ParsedArgs } from "../../types.js";
import {
  InputValidationError,
  isSupportedChain,
  isValidAddress,
  isValidMarketId,
} from "../../utils/validators.js";
import { inferLatestTopicByAddress } from "./wallet-session.js";

const DEFAULT_CHAIN = "eip155:56";

function requireAddress(
  value: string | null | undefined,
  missingMessage: string,
  invalidMessageFactory: (value: string) => string
): Address {
  if (!value) {
    throw new InputValidationError(missingMessage);
  }
  if (!isValidAddress(value)) {
    throw new InputValidationError(invalidMessageFactory(value));
  }
  return value;
}

function requireWalletTopic(value: string | null | undefined): string {
  if (!value) {
    throw new InputValidationError(
      "No wallet connected. Use 'select' or provide --wallet-topic"
    );
  }
  return value;
}

function requireMarketId(value: string | null | undefined): Address {
  if (!value) {
    throw new InputValidationError(
      "No market selected. Use 'select --market <id>' or provide --market"
    );
  }
  if (!isValidMarketId(value)) {
    throw new InputValidationError(`Invalid market ID: ${value}`);
  }
  return value as Address;
}

export function requireSupportedChain(
  chain: string,
  supportedChains: readonly string[]
): string {
  if (!isSupportedChain(chain, supportedChains)) {
    throw new InputValidationError(
      `Unsupported chain: ${chain}. Supported: ${supportedChains.join(", ")}`
    );
  }
  return chain;
}

export function requireAmount(value: string | undefined): string {
  if (!value) {
    throw new InputValidationError("--amount required");
  }
  return value;
}

export function requireAmountOrAll(
  amount: string | undefined,
  allFlag: boolean | undefined,
  allFlagName: "--withdraw-all" | "--repay-all"
): void {
  if (!amount && !allFlag) {
    throw new InputValidationError(`--amount or ${allFlagName} required`);
  }
  if (amount && allFlag) {
    throw new InputValidationError(
      `--amount and ${allFlagName} cannot be used together`
    );
  }
}

export interface ResolveOptions {
  supportedChains: readonly string[];
  requireWalletTopic?: boolean;
}

export interface ResolvedVaultContext {
  vaultAddress: Address;
  chain: string;
  walletAddress: Address;
  walletTopic: string | null;
}

export interface ResolvedMarketContext {
  marketId: Address;
  chain: string;
  walletAddress: Address;
  walletTopic: string | null;
}

export function resolveVaultContext(
  args: ParsedArgs,
  ctx: LendingContext,
  options: ResolveOptions
): ResolvedVaultContext {
  const vaultAddressInput = args.vault || ctx.selectedVault?.address;
  const chain = args.chain || ctx.selectedVault?.chain || DEFAULT_CHAIN;
  let walletTopicInput = args.walletTopic || null;
  const walletAddressInput = args.walletAddress || ctx.userAddress;

  if (args.walletAddress && !args.walletTopic) {
    const inferredTopic = inferLatestTopicByAddress(args.walletAddress);
    if (inferredTopic) {
      walletTopicInput = inferredTopic;
    } else if (options.requireWalletTopic !== false) {
      throw new InputValidationError(
        `No wallet session found for ${args.walletAddress}. Provide --wallet-topic or reconnect this wallet`
      );
    }
  } else if (!walletTopicInput) {
    walletTopicInput = ctx.walletTopic || null;
  }

  const vaultAddress = requireAddress(
    vaultAddressInput,
    "No vault selected. Use 'select --vault <address>' or provide --vault",
    (value) => `Invalid vault address: ${value}`
  );
  const walletAddress = requireAddress(
    walletAddressInput,
    "No wallet address. Use 'select' or provide --wallet-address",
    (value) => `Invalid wallet address: ${value}`
  );

  requireSupportedChain(chain, options.supportedChains);
  const walletTopic =
    options.requireWalletTopic === false
      ? walletTopicInput || null
      : requireWalletTopic(walletTopicInput);

  return {
    vaultAddress,
    chain,
    walletAddress,
    walletTopic,
  };
}

export function resolveMarketContext(
  args: ParsedArgs,
  ctx: LendingContext,
  options: ResolveOptions
): ResolvedMarketContext {
  const marketIdInput = args.market || ctx.selectedMarket?.marketId;
  const chain = args.chain || ctx.selectedMarket?.chain || DEFAULT_CHAIN;
  let walletTopicInput = args.walletTopic || null;
  const walletAddressInput = args.walletAddress || ctx.userAddress;

  if (args.walletAddress && !args.walletTopic) {
    const inferredTopic = inferLatestTopicByAddress(args.walletAddress);
    if (inferredTopic) {
      walletTopicInput = inferredTopic;
    } else if (options.requireWalletTopic !== false) {
      throw new InputValidationError(
        `No wallet session found for ${args.walletAddress}. Provide --wallet-topic or reconnect this wallet`
      );
    }
  } else if (!walletTopicInput) {
    walletTopicInput = ctx.walletTopic || null;
  }

  const validMarketId = requireMarketId(marketIdInput);
  const walletAddress = requireAddress(
    walletAddressInput,
    "No wallet address. Use 'select' or provide --wallet-address",
    (value) => `Invalid wallet address: ${value}`
  );

  requireSupportedChain(chain, options.supportedChains);
  const walletTopic =
    options.requireWalletTopic === false
      ? walletTopicInput || null
      : requireWalletTopic(walletTopicInput);

  return {
    marketId: validMarketId,
    chain,
    walletAddress,
    walletTopic,
  };
}
