import type { ApiMarketHoldingItem, ApiMarketPosition, ApiVaultHoldingItem, ApiVaultPosition } from "../types/lista-api.js";

export function mapVaultErrorPosition(
  holding: ApiVaultHoldingItem,
  chain: string,
  error: string
): ApiVaultPosition {
  return {
    kind: "vault",
    vaultAddress: holding.address,
    vaultName: holding.name,
    curator: holding.curator,
    apy: holding.apy,
    emissionApy: holding.emissionApy,
    chain,
    assetSymbol: "UNKNOWN",
    assetPrice: holding.assetPrice || "0",
    walletBalance: "0",
    deposited: "0",
    depositedUsd: "0",
    shares: "0",
    hasPosition: false,
    error,
  };
}

export function mapMarketErrorPosition(
  holding: ApiMarketHoldingItem,
  chain: string,
  error: string
): ApiMarketPosition {
  const isSmartLending = holding.zone === 3;
  const isFixedTerm = holding.termType === 1;
  return {
    kind: "market",
    marketId: holding.marketId,
    chain,
    zone: holding.zone,
    termType: holding.termType,
    isSmartLending,
    isFixedTerm,
    isActionable: !isSmartLending && !isFixedTerm,
    broker: holding.broker || undefined,
    collateralSymbol: holding.collateralSymbol,
    collateralAddress: holding.collateralToken,
    collateralPrice: holding.collateralPrice,
    loanSymbol: holding.loanSymbol,
    loanAddress: holding.loanToken,
    loanPrice: holding.loanPrice,
    supplyApy: holding.supplyApy,
    borrowRate: "0",
    collateral: "0",
    collateralUsd: "0",
    borrowed: "0",
    borrowedUsd: "0",
    ltv: "0",
    lltv: holding.zone === 3 ? "0.909" : "0",
    health: "0",
    liquidationPriceRate: "0",
    walletCollateralBalance: "0",
    walletLoanBalance: "0",
    isWhitelisted: false,
    error,
  };
}
