import type { Address } from "viem";
import type { LendingContext } from "../../context.js";
import type { ParsedArgs } from "../../types.js";
export declare function requireSupportedChain(chain: string, supportedChains: readonly string[]): string;
export declare function requireAmount(value: string | undefined): string;
export declare function requireAmountOrAll(amount: string | undefined, allFlag: boolean | undefined, allFlagName: "--withdraw-all" | "--repay-all"): void;
export interface ResolveOptions {
    supportedChains: readonly string[];
    requireWalletTopic?: boolean;
}
export interface ResolvedVaultContext {
    vaultAddress: Address;
    chain: string;
    walletAddress: Address;
    walletTopic: string | null;
}
export interface ResolvedMarketContext {
    marketId: Address;
    chain: string;
    walletAddress: Address;
    walletTopic: string | null;
}
export declare function resolveVaultContext(args: ParsedArgs, ctx: LendingContext, options: ResolveOptions): ResolvedVaultContext;
export declare function resolveMarketContext(args: ParsedArgs, ctx: LendingContext, options: ResolveOptions): ResolvedMarketContext;
