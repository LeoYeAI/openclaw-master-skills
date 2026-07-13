import { Decimal } from "@lista-dao/moolah-sdk-core";
import { mapMarketUserPosition } from "../../utils/position.js";
import { InputValidationError, parsePositiveUnits } from "../../utils/validators.js";
export async function buildRepaySimulationPayload(args, runtime) {
    const { marketId, chain, marketExtraInfo, userData, marketInfo } = runtime;
    const loanSymbol = marketInfo.loanInfo.symbol;
    let repayAssets = 0n;
    let estimatedRepay = "0";
    if (args.repayAll) {
        repayAssets = userData.borrowed.roundDown(userData.decimals.l).numerator;
        estimatedRepay = userData.borrowed.toFixed(8);
    }
    else if (args.amount) {
        const parsedAmount = parsePositiveUnits(args.amount, userData.decimals.l, "amount");
        if (userData.borrowed.lt(new Decimal(parsedAmount, userData.decimals.l))) {
            throw new InputValidationError(`Repay amount exceeds current debt (${userData.borrowed.toFixed(8)} ${loanSymbol})`);
        }
        repayAssets = parsedAmount;
        estimatedRepay = args.amount;
    }
    const simulated = await runtime.sdk.simulateRepayPosition({
        chainId: runtime.chainId,
        marketId,
        walletAddress: runtime.walletAddress,
        repayAssets,
        repayAll: Boolean(args.repayAll),
        marketExtraInfo,
        userData,
    });
    const simulation = simulated.simulation;
    const mappedPosition = mapMarketUserPosition(userData, {
        collateralPrice: 0,
        loanPrice: 0,
    });
    return {
        status: "success",
        action: "simulate",
        market: marketId,
        chain,
        loan: loanSymbol,
        repay: {
            amount: args.repayAll ? "all" : args.amount,
            repayAll: Boolean(args.repayAll),
            currentDebt: userData.borrowed.toFixed(8),
            estimatedRepay,
        },
        current: {
            borrowed: mappedPosition.borrowed,
            ltv: mappedPosition.ltv,
            withdrawable: userData.withdrawable.toFixed(8),
            health: mappedPosition.health,
        },
        afterRepay: {
            borrowed: simulation.borrowed.toFixed(8),
            ltv: simulation.LTV.toFixed(8),
            withdrawable: simulation.withdrawable.toFixed(8),
        },
        hint: simulation.borrowed.isZero()
            ? "Repay will fully clear debt."
            : `Estimated remaining debt: ${simulation.borrowed.toFixed(8)} ${loanSymbol}`,
    };
}
