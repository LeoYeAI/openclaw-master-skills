import type { UserPosition } from "../context.js";
import { Decimal } from "@lista-dao/moolah-lending-sdk";
import type { MarketUserData, VaultUserData } from "../types.js";

export interface MappedVaultPosition {
  position: UserPosition;
  shares: string;
  assets: string;
  walletBalance: string;
  hasPosition: boolean;
}

export interface MappedMarketPosition {
  collateral: string;
  collateralUsd: string;
  borrowed: string;
  borrowedUsd: string;
  ltv: string;
  lltv: string;
  health: string;
  liquidationPriceRate: string;
  borrowRate: string;
  walletCollateralBalance: string;
  walletLoanBalance: string;
  hasPosition: boolean;
  isWhitelisted: boolean;
}

export function mapVaultUserPosition(userData: VaultUserData): MappedVaultPosition {
  const shares = userData.shares?.toFixed(8) || "0";
  const assets = userData.locked?.toFixed(8) || "0";
  const walletBalance = userData.balance?.toFixed(8) || "0";

  return {
    position: {
      shares,
      assets,
    },
    shares,
    assets,
    walletBalance,
    hasPosition: Number.parseFloat(assets) > 0,
  };
}

export function mapMarketUserPosition(
  userData: MarketUserData,
  prices: {
    collateralPrice: string | number;
    loanPrice: string | number;
  }
): MappedMarketPosition {
  const collateralPrice = Decimal.parse(prices.collateralPrice || 0);
  const loanPrice = Decimal.parse(prices.loanPrice || 0);

  const collateral = userData.collateral?.toFixed(8) || "0";
  const borrowed = userData.borrowed?.toFixed(8) || "0";
  const collateralUsd = userData.collateral.mul(collateralPrice).toFixed(8);
  const borrowedUsd = userData.borrowed.mul(loanPrice).toFixed(8);

  // Align with lista-mono userLoansAtom: health = LLTV / LTV when LTV > 0, else 100.
  const healthValue = userData.LTV.gt(0)
    ? userData.LLTV.div(userData.LTV).roundDown(18)
    : Decimal.parse(100);

  return {
    collateral,
    collateralUsd,
    borrowed,
    borrowedUsd,
    ltv: userData.LTV.toFixed(8),
    lltv: userData.LLTV.toFixed(8),
    health: healthValue.toFixed(8),
    liquidationPriceRate: userData.liqPriceRate.toFixed(18),
    borrowRate: userData.borrowRate.toFixed(8),
    walletCollateralBalance: userData.balances.collateral?.toFixed(8) || "0",
    walletLoanBalance: userData.balances.loan?.toFixed(8) || "0",
    hasPosition:
      Number.parseFloat(collateral) > 0 || Number.parseFloat(borrowed) > 0,
    isWhitelisted: userData.isWhiteList,
  };
}
