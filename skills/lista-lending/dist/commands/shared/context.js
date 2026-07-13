import { InputValidationError, isSupportedChain, isValidAddress, isValidMarketId, } from "../../utils/validators.js";
import { inferLatestTopicByAddress } from "./wallet-session.js";
const DEFAULT_CHAIN = "eip155:56";
function requireAddress(value, missingMessage, invalidMessageFactory) {
    if (!value) {
        throw new InputValidationError(missingMessage);
    }
    if (!isValidAddress(value)) {
        throw new InputValidationError(invalidMessageFactory(value));
    }
    return value;
}
function requireWalletTopic(value) {
    if (!value) {
        throw new InputValidationError("No wallet connected. Use 'select' or provide --wallet-topic");
    }
    return value;
}
function requireMarketId(value) {
    if (!value) {
        throw new InputValidationError("No market selected. Use 'select --market <id>' or provide --market");
    }
    if (!isValidMarketId(value)) {
        throw new InputValidationError(`Invalid market ID: ${value}`);
    }
    return value;
}
export function requireSupportedChain(chain, supportedChains) {
    if (!isSupportedChain(chain, supportedChains)) {
        throw new InputValidationError(`Unsupported chain: ${chain}. Supported: ${supportedChains.join(", ")}`);
    }
    return chain;
}
export function requireAmount(value) {
    if (!value) {
        throw new InputValidationError("--amount required");
    }
    return value;
}
export function requireAmountOrAll(amount, allFlag, allFlagName) {
    if (!amount && !allFlag) {
        throw new InputValidationError(`--amount or ${allFlagName} required`);
    }
    if (amount && allFlag) {
        throw new InputValidationError(`--amount and ${allFlagName} cannot be used together`);
    }
}
export function resolveVaultContext(args, ctx, options) {
    const vaultAddressInput = args.vault || ctx.selectedVault?.address;
    const chain = args.chain || ctx.selectedVault?.chain || DEFAULT_CHAIN;
    let walletTopicInput = args.walletTopic || null;
    const walletAddressInput = args.walletAddress || ctx.userAddress;
    if (args.walletAddress && !args.walletTopic) {
        const inferredTopic = inferLatestTopicByAddress(args.walletAddress);
        if (inferredTopic) {
            walletTopicInput = inferredTopic;
        }
        else if (options.requireWalletTopic !== false) {
            throw new InputValidationError(`No wallet session found for ${args.walletAddress}. Provide --wallet-topic or reconnect this wallet`);
        }
    }
    else if (!walletTopicInput) {
        walletTopicInput = ctx.walletTopic || null;
    }
    const vaultAddress = requireAddress(vaultAddressInput, "No vault selected. Use 'select --vault <address>' or provide --vault", (value) => `Invalid vault address: ${value}`);
    const walletAddress = requireAddress(walletAddressInput, "No wallet address. Use 'select' or provide --wallet-address", (value) => `Invalid wallet address: ${value}`);
    requireSupportedChain(chain, options.supportedChains);
    const walletTopic = options.requireWalletTopic === false
        ? walletTopicInput || null
        : requireWalletTopic(walletTopicInput);
    return {
        vaultAddress,
        chain,
        walletAddress,
        walletTopic,
    };
}
export function resolveMarketContext(args, ctx, options) {
    const marketIdInput = args.market || ctx.selectedMarket?.marketId;
    const chain = args.chain || ctx.selectedMarket?.chain || DEFAULT_CHAIN;
    let walletTopicInput = args.walletTopic || null;
    const walletAddressInput = args.walletAddress || ctx.userAddress;
    if (args.walletAddress && !args.walletTopic) {
        const inferredTopic = inferLatestTopicByAddress(args.walletAddress);
        if (inferredTopic) {
            walletTopicInput = inferredTopic;
        }
        else if (options.requireWalletTopic !== false) {
            throw new InputValidationError(`No wallet session found for ${args.walletAddress}. Provide --wallet-topic or reconnect this wallet`);
        }
    }
    else if (!walletTopicInput) {
        walletTopicInput = ctx.walletTopic || null;
    }
    const validMarketId = requireMarketId(marketIdInput);
    const walletAddress = requireAddress(walletAddressInput, "No wallet address. Use 'select' or provide --wallet-address", (value) => `Invalid wallet address: ${value}`);
    requireSupportedChain(chain, options.supportedChains);
    const walletTopic = options.requireWalletTopic === false
        ? walletTopicInput || null
        : requireWalletTopic(walletTopicInput);
    return {
        marketId: validMarketId,
        chain,
        walletAddress,
        walletTopic,
    };
}
