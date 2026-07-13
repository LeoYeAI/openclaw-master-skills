import { mapMarketUserPosition } from "../../utils/position.js";
import { parsePositiveUnits } from "../../utils/validators.js";
export async function buildBorrowSimulationPayload(args, runtime) {
    const { marketId, chain, marketInfo, marketExtraInfo, userData } = runtime;
    const currentLoanable = userData.loanable;
    const currentSafeBorrow = currentLoanable.mul(0.95).roundDown(userData.decimals.l);
    let afterSupplyLoanable = currentLoanable;
    let afterSupplyAmount;
    if (args.simulateSupply) {
        const parsedSupplyAmount = parsePositiveUnits(args.simulateSupply, userData.decimals.c, "simulate-supply");
        afterSupplyAmount = args.simulateSupply;
        const simulated = await runtime.sdk.simulateBorrowPosition({
            chainId: runtime.chainId,
            marketId,
            walletAddress: runtime.walletAddress,
            supplyAssets: parsedSupplyAmount,
            marketExtraInfo,
            userData,
        });
        afterSupplyLoanable = simulated.simulation.baseLoanable;
    }
    const safeAfterSupplyBorrow = afterSupplyLoanable
        .mul(0.95)
        .roundDown(userData.decimals.l);
    const mappedPosition = mapMarketUserPosition(userData, {
        collateralPrice: 0,
        loanPrice: 0,
    });
    return {
        status: "success",
        action: "simulate",
        market: marketId,
        chain,
        collateral: {
            symbol: marketInfo.collateralInfo.symbol,
            deposited: mappedPosition.collateral,
            walletBalance: mappedPosition.walletCollateralBalance,
        },
        loan: {
            symbol: marketInfo.loanInfo.symbol,
            borrowed: mappedPosition.borrowed,
            walletBalance: mappedPosition.walletLoanBalance,
        },
        position: {
            ltv: mappedPosition.ltv,
            lltv: mappedPosition.lltv,
            health: mappedPosition.health,
        },
        borrowable: {
            max: currentLoanable.toFixed(8),
            safe: currentSafeBorrow.toFixed(8),
            afterSupply: afterSupplyAmount
                ? {
                    supplyAmount: afterSupplyAmount,
                    maxBorrow: afterSupplyLoanable.toFixed(8),
                    safeBorrow: safeAfterSupplyBorrow.toFixed(8),
                }
                : undefined,
        },
        hint: afterSupplyLoanable.gt(0)
            ? `You can safely borrow up to ${safeAfterSupplyBorrow.toFixed(4)} ${marketInfo.loanInfo.symbol} (95% of max: ${afterSupplyLoanable.toFixed(4)})`
            : "No borrowing capacity. Supply collateral first.",
    };
}
