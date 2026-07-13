/**
 * Lista API types.
 */

import type { MoolahSDK } from "@lista-dao/moolah-lending-sdk";

type VaultListResult = Awaited<ReturnType<MoolahSDK["getVaultList"]>>;
type MarketListResult = Awaited<ReturnType<MoolahSDK["getMarketList"]>>;
type HoldingsResult = Awaited<ReturnType<MoolahSDK["getHoldings"]>>;
type VaultHoldingsResult = Extract<HoldingsResult, { type: "vault" }>;
type MarketHoldingsResult = Extract<HoldingsResult, { type: "market" }>;

export type ApiVaultList = VaultListResult;
export type ApiVaultItem = VaultListResult["list"][number];
export type ApiMarketList = MarketListResult;
export type ApiMarketItem = MarketListResult["list"][number];
export type ApiVaultHoldingItem = VaultHoldingsResult["objs"][number];
export type ApiMarketHoldingItem = MarketHoldingsResult["objs"][number];
export type ListOrder = "asc" | "desc";
export type HoldingsScope = "all" | "vault" | "market" | "selected";

export interface VaultListQuery {
  chain?: string | string[];
  page?: number;
  pageSize?: number;
  sort?: string;
  order?: ListOrder;
  zone?: string | number;
  keyword?: string;
  assets?: string[];
  curators?: string[];
}

export interface MarketListQuery {
  chain?: string | string[];
  page?: number;
  pageSize?: number;
  sort?: string;
  order?: ListOrder;
  zone?: string | number;
  keyword?: string;
  loans?: string[];
  collaterals?: string[];
  termType?: number;
  smartLendingChecked?: boolean;
}

export interface ApiVaultPosition {
  kind: "vault";
  vaultAddress: string;
  vaultName: string;
  curator: string;
  apy: string;
  emissionApy?: string;
  chain: string;
  assetSymbol: string;
  assetPrice: string;
  walletBalance: string;
  deposited: string;
  depositedUsd: string;
  shares: string;
  hasPosition: boolean;
  error?: string;
}

export interface ApiMarketPosition {
  kind: "market";
  marketId: string;
  chain: string;
  zone: number;
  termType: number;
  isSmartLending: boolean;
  isFixedTerm: boolean;
  isActionable: boolean;
  broker?: string;
  collateralSymbol: string;
  collateralAddress: string;
  collateralPrice: string;
  loanSymbol: string;
  loanAddress: string;
  loanPrice: string;
  supplyApy: string;
  borrowRate: string;
  collateral: string;
  collateralUsd: string;
  borrowed: string;
  borrowedUsd: string;
  ltv: string;
  lltv: string;
  health: string;
  liquidationPriceRate: string;
  walletCollateralBalance: string;
  walletLoanBalance: string;
  isWhitelisted: boolean;
  error?: string;
}

export interface ApiUserPositions {
  vaults: ApiVaultPosition[];
  markets: ApiMarketPosition[];
}
