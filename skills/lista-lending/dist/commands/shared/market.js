export function buildMarketPositionPayload(mappedPosition, extras = {}) {
    return {
        collateral: mappedPosition.collateral,
        borrowed: mappedPosition.borrowed,
        ltv: mappedPosition.ltv,
        lltv: mappedPosition.lltv,
        health: mappedPosition.health,
        walletCollateralBalance: mappedPosition.walletCollateralBalance,
        walletLoanBalance: mappedPosition.walletLoanBalance,
        ...extras,
    };
}
export function buildRepayHint(userData) {
    if (userData.withdrawable?.gt(0) && userData.borrowed.isZero()) {
        return `Debt fully repaid. You can withdraw up to ${userData.withdrawable.toFixed(4)} ${userData.collateralInfo.symbol} collateral.`;
    }
    return undefined;
}
export function getRepayNoDebtError() {
    return {
        status: "error",
        reason: "no_debt",
        message: "No debt to repay in this market",
    };
}
export function getWithdrawNoCollateralError() {
    return {
        status: "error",
        reason: "no_collateral",
        message: "No collateral to withdraw from this market",
    };
}
export function getWithdrawAllHasDebtError(userData) {
    return {
        status: "error",
        reason: "has_debt",
        message: "Cannot withdraw all collateral while you have outstanding debt. Repay debt first or use --amount.",
        debt: userData.borrowed.toFixed(8),
        withdrawable: userData.withdrawable.toFixed(8),
    };
}
export function getExceedsWithdrawableError(requestedAmount, userData, collateralSymbol) {
    return {
        status: "error",
        reason: "exceeds_withdrawable",
        message: `Cannot withdraw ${requestedAmount} ${collateralSymbol}. Max withdrawable: ${userData.withdrawable.toFixed(4)} ${collateralSymbol}`,
        maxWithdrawable: userData.withdrawable.toFixed(8),
        hint: "Repay some debt to increase withdrawable amount",
    };
}
