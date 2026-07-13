import type { UserPosition } from "../context.js";
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
export declare function mapVaultUserPosition(userData: VaultUserData): MappedVaultPosition;
export declare function mapMarketUserPosition(userData: MarketUserData, prices: {
    collateralPrice: string | number;
    loanPrice: string | number;
}): MappedMarketPosition;
