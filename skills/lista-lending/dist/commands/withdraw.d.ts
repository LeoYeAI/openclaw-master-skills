/**
 * Vault withdraw command
 * Withdraws assets from a Lista Lending vault
 * After success, re-queries position on-chain
 */
import type { ParsedArgs } from "../types.js";
export declare function cmdWithdraw(args: ParsedArgs): Promise<void>;
