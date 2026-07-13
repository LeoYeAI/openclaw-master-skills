/**
 * Market withdraw command
 * Withdraw collateral from a Lista Lending market
 *
 * Features:
 * - --amount: Withdraw specific amount
 * - --withdraw-all: Withdraw all collateral (only if no debt)
 */
import type { ParsedArgs } from "../types.js";
export declare function cmdMarketWithdraw(args: ParsedArgs): Promise<void>;
