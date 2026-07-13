/**
 * Holdings command - query user's vault/market positions
 */
import type { HoldingsScope } from "../types/lista-api.js";
export interface HoldingsArgs {
    address?: string;
    scope?: HoldingsScope;
}
export declare function cmdHoldings(args: HoldingsArgs): Promise<void>;
