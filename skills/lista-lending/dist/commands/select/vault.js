import { getChainId, getSDK, SUPPORTED_CHAINS } from "../../sdk.js";
import { setSelectedVault } from "../../context.js";
import { mapVaultUserPosition } from "../../utils/position.js";
import { isSupportedChain, isValidAddress } from "../../utils/validators.js";
export async function runSelectVault(args) {
    if (!args.walletTopic) {
        return { exitCode: 1, payload: { status: "error", reason: "--wallet-topic required" } };
    }
    if (!args.walletAddress) {
        return {
            exitCode: 1,
            payload: { status: "error", reason: "--wallet-address required" },
        };
    }
    if (!args.vault) {
        return {
            exitCode: 1,
            payload: { status: "error", reason: "--vault required" },
        };
    }
    const chain = args.chain || "eip155:56";
    if (!isSupportedChain(chain, SUPPORTED_CHAINS)) {
        return {
            exitCode: 1,
            payload: {
                status: "error",
                reason: `Unsupported chain: ${chain}. Supported: ${SUPPORTED_CHAINS.join(", ")}`,
            },
        };
    }
    if (!isValidAddress(args.vault)) {
        return {
            exitCode: 1,
            payload: {
                status: "error",
                reason: `Invalid vault address: ${args.vault}`,
            },
        };
    }
    if (!isValidAddress(args.walletAddress)) {
        return {
            exitCode: 1,
            payload: {
                status: "error",
                reason: `Invalid wallet address: ${args.walletAddress}`,
            },
        };
    }
    const vaultAddress = args.vault;
    const walletAddress = args.walletAddress;
    const chainId = getChainId(chain);
    try {
        const sdk = getSDK();
        const vaultInfo = await sdk.getVaultInfo(chainId, vaultAddress);
        const userData = await sdk.getVaultUserData(chainId, vaultAddress, walletAddress, vaultInfo);
        const assetInfo = vaultInfo.assetInfo;
        const selectedVault = {
            address: vaultAddress,
            name: `${assetInfo.symbol} Vault`,
            asset: {
                symbol: assetInfo.symbol,
                address: assetInfo.address,
                decimals: assetInfo.decimals,
            },
            chain,
        };
        const mappedPosition = mapVaultUserPosition(userData);
        setSelectedVault(selectedVault, walletAddress, args.walletTopic, mappedPosition.position);
        return {
            exitCode: 0,
            payload: {
                status: "success",
                action: "selected",
                vault: selectedVault,
                userAddress: walletAddress,
                balance: mappedPosition.walletBalance,
                vaultBalance: mappedPosition.position.assets,
                position: {
                    assets: mappedPosition.position.assets,
                    balance: mappedPosition.position.assets,
                    walletBalance: mappedPosition.walletBalance,
                    assetSymbol: assetInfo.symbol,
                    hasPosition: mappedPosition.hasPosition,
                },
                message: mappedPosition.hasPosition
                    ? `Selected ${selectedVault.name}. You have ${mappedPosition.position.assets} ${assetInfo.symbol} deposited. Wallet balance: ${mappedPosition.walletBalance} ${assetInfo.symbol}.`
                    : `Selected ${selectedVault.name}. No existing position.`,
            },
        };
    }
    catch (err) {
        const message = err.message || String(err);
        if (message.includes("vault not found") || message.includes("invalid")) {
            return {
                exitCode: 1,
                payload: {
                    status: "error",
                    reason: "invalid_vault",
                    message: `Vault ${vaultAddress} not found or invalid on ${chain}`,
                },
            };
        }
        return {
            exitCode: 1,
            payload: {
                status: "error",
                reason: "sdk_error",
                message,
            },
        };
    }
}
