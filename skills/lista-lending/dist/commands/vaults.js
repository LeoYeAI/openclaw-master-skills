/**
 * Vaults command - list all available vaults
 */
import { fetchVaults } from "../api.js";
import { SUPPORTED_CHAINS } from "../config.js";
import { setLastFilters } from "../context.js";
import { printJson } from "./shared/output.js";
import { formatVaultDisplay } from "../presenters/lending.js";
import { isPositiveInteger, isSupportedChain, isValidOrder, } from "../utils/validators.js";
export async function cmdVaults(args) {
    const chain = args.chain || "eip155:56";
    if (!isSupportedChain(chain, SUPPORTED_CHAINS)) {
        printJson({
            status: "error",
            reason: `Unsupported chain: ${chain}. Supported: ${SUPPORTED_CHAINS.join(", ")}`,
        });
        process.exit(1);
    }
    if (args.page !== undefined && !isPositiveInteger(args.page)) {
        printJson({
            status: "error",
            reason: "--page must be a positive integer",
        });
        process.exit(1);
    }
    if (args.pageSize !== undefined &&
        !isPositiveInteger(args.pageSize)) {
        printJson({
            status: "error",
            reason: "--page-size must be a positive integer",
        });
        process.exit(1);
    }
    if (args.order && !isValidOrder(args.order)) {
        printJson({
            status: "error",
            reason: "--order must be asc or desc",
        });
        process.exit(1);
    }
    try {
        const vaults = await fetchVaults({
            chain,
            page: args.page,
            pageSize: args.pageSize,
            sort: args.sort,
            order: args.order,
            zone: args.zone,
            keyword: args.keyword,
            assets: args.assets,
            curators: args.curators,
        });
        setLastFilters({
            vaults: {
                chain,
                page: args.page || 1,
                pageSize: args.pageSize || 100,
                sort: args.sort,
                order: args.order,
                zone: args.zone,
                keyword: args.keyword,
                assets: args.assets,
                curators: args.curators,
                at: new Date().toISOString(),
            },
        });
        if (vaults.length === 0) {
            printJson({
                status: "success",
                chain,
                vaults: [],
                message: "No vaults found",
            });
            return;
        }
        // Output JSON for agent parsing
        printJson({
            status: "success",
            chain,
            count: vaults.length,
            filters: {
                page: args.page || 1,
                pageSize: args.pageSize || 100,
                sort: args.sort,
                order: args.order,
                zone: args.zone,
                keyword: args.keyword,
                assets: args.assets,
                curators: args.curators,
            },
            vaults: vaults.map((v, i) => ({
                index: i,
                address: v.address,
                name: v.name,
                asset: v.assetSymbol,
                assetAddress: v.asset,
                decimals: v.displayDecimal,
                tvl: v.depositsUsd,
                apy: v.apy,
                curator: v.curator,
                display: formatVaultDisplay(v, i),
            })),
        });
    }
    catch (err) {
        printJson({
            status: "error",
            reason: "sdk_error",
            message: err.message,
        });
        process.exit(1);
    }
}
