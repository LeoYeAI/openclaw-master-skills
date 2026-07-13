import { getSDK, getChainId, SUPPORTED_CHAINS } from "../../sdk.js";
import { setSelectedMarket } from "../../context.js";
import { mapMarketUserPosition } from "../../utils/position.js";
import { isSupportedChain, isValidAddress, isValidMarketId, } from "../../utils/validators.js";
const ZONE_SMART_LENDING = 3;
const TERM_TYPE_FIXED = 1;
export async function runSelectMarket(args) {
    if (!args.walletTopic) {
        return { exitCode: 1, payload: { status: "error", reason: "--wallet-topic required" } };
    }
    if (!args.walletAddress) {
        return {
            exitCode: 1,
            payload: { status: "error", reason: "--wallet-address required" },
        };
    }
    if (!args.market) {
        return {
            exitCode: 1,
            payload: { status: "error", reason: "--market required" },
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
    if (!isValidMarketId(args.market)) {
        return {
            exitCode: 1,
            payload: {
                status: "error",
                reason: `Invalid market ID: ${args.market}`,
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
    const marketId = args.market;
    const walletAddress = args.walletAddress;
    const chainId = getChainId(chain);
    try {
        const sdk = getSDK();
        const marketInfo = await sdk.getMarketInfo(chainId, marketId);
        const marketZone = marketInfo.zone;
        const marketTermType = marketInfo.termType;
        if (marketZone === ZONE_SMART_LENDING) {
            return {
                exitCode: 1,
                payload: {
                    status: "error",
                    reason: "unsupported_market_type",
                    message: "SmartLending markets are not supported. Use regular markets only.",
                },
            };
        }
        if (marketTermType === TERM_TYPE_FIXED) {
            return {
                exitCode: 1,
                payload: {
                    status: "error",
                    reason: "unsupported_market_type",
                    message: "Fixed-term markets are not supported. Use regular markets only.",
                },
            };
        }
        const userData = await sdk.getMarketUserData(chainId, marketId, walletAddress);
        const selectedMarket = {
            marketId,
            chain,
            collateralSymbol: userData.collateralInfo.symbol,
            loanSymbol: userData.loanInfo.symbol,
            zone: marketZone,
            termType: marketTermType,
        };
        const mappedPosition = mapMarketUserPosition(userData, {
            collateralPrice: 0,
            loanPrice: 0,
        });
        setSelectedMarket(selectedMarket, walletAddress, args.walletTopic);
        return {
            exitCode: 0,
            payload: {
                status: "success",
                action: "selected",
                market: selectedMarket,
                userAddress: walletAddress,
                position: {
                    collateral: mappedPosition.collateral,
                    borrowed: mappedPosition.borrowed,
                    ltv: mappedPosition.ltv,
                    lltv: mappedPosition.lltv,
                    health: mappedPosition.health,
                    loanable: userData.loanable?.toFixed(8) || "0",
                    withdrawable: userData.withdrawable?.toFixed(8) || "0",
                    walletCollateralBalance: mappedPosition.walletCollateralBalance,
                    walletLoanBalance: mappedPosition.walletLoanBalance,
                    hasPosition: mappedPosition.hasPosition,
                },
                message: mappedPosition.hasPosition
                    ? `Selected ${selectedMarket.collateralSymbol}/${selectedMarket.loanSymbol} market. Collateral: ${mappedPosition.collateral}, Borrowed: ${mappedPosition.borrowed}`
                    : `Selected ${selectedMarket.collateralSymbol}/${selectedMarket.loanSymbol} market. No existing position.`,
            },
        };
    }
    catch (err) {
        const message = err.message || String(err);
        if (message.includes("market not found") || message.includes("invalid")) {
            return {
                exitCode: 1,
                payload: {
                    status: "error",
                    reason: "invalid_market",
                    message: `Market ${marketId} not found or invalid on ${chain}`,
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
