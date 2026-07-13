import type { Address } from "viem";
export declare class InputValidationError extends Error {
    constructor(message: string);
}
export declare function isSupportedChain(chain: string, supportedChains: readonly string[]): boolean;
export declare function isPositiveInteger(value: number | undefined): boolean;
export declare function isValidOrder(value: string): value is "asc" | "desc";
export declare function isValidAddress(value: string): value is Address;
export declare function isValidMarketId(value: string): boolean;
export declare function parsePositiveUnits(value: string, decimals: number, fieldName: string): bigint;
export declare function normalizeHoldingChain(chain: string): string;
