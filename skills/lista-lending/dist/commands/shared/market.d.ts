import type { MarketUserData } from "../../types.js";
import type { MappedMarketPosition } from "../../utils/position.js";
export declare function buildMarketPositionPayload(mappedPosition: MappedMarketPosition, extras?: Record<string, unknown>): Record<string, unknown>;
export declare function buildRepayHint(userData: MarketUserData): string | undefined;
export declare function getRepayNoDebtError(): Record<string, unknown>;
export declare function getWithdrawNoCollateralError(): Record<string, unknown>;
export declare function getWithdrawAllHasDebtError(userData: MarketUserData): Record<string, unknown>;
export declare function getExceedsWithdrawableError(requestedAmount: string, userData: MarketUserData, collateralSymbol: string): Record<string, unknown>;
