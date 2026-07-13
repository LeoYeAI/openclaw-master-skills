/**
 * Vault deposit command
 * Deposits assets into a Lista Lending vault
 * After success, re-queries position on-chain
 */
import type { ParsedArgs } from "../types.js";
export declare function cmdDeposit(args: ParsedArgs): Promise<void>;
