/**
 * Holdings command - query user's vault/market positions
 */
import { fetchMarketPositions, fetchUserPositions, fetchVaultPositions } from "../api.js";
import { loadContext, setLastFilters } from "../context.js";
import { printJson } from "./shared/output.js";
import { isValidAddress } from "../utils/validators.js";
export async function cmdHoldings(args) {
    const ctx = loadContext();
    const address = args.address || ctx.userAddress;
    const scope = args.scope || "all";
    if (!address) {
        printJson({
            status: "error",
            reason: "--address required (or select a wallet first)",
        });
        process.exit(1);
    }
    if (!isValidAddress(address)) {
        printJson({
            status: "error",
            reason: `Invalid address: ${address}`,
        });
        process.exit(1);
    }
    if (!["all", "vault", "market", "selected"].includes(scope)) {
        printJson({
            status: "error",
            reason: "--scope must be all, vault, market, or selected",
        });
        process.exit(1);
    }
    try {
        let vaults = [];
        let markets = [];
        if (scope === "all") {
            const data = await fetchUserPositions(address);
            vaults = data.vaults;
            markets = data.markets;
        }
        else if (scope === "vault") {
            vaults = await fetchVaultPositions(address);
        }
        else if (scope === "market") {
            markets = await fetchMarketPositions(address);
        }
        else {
            if (!ctx.selectedVault && !ctx.selectedMarket) {
                printJson({
                    status: "error",
                    reason: "No selected position. Use select first or query --scope all",
                });
                process.exit(1);
            }
            const [vaultData, marketData] = await Promise.all([
                ctx.selectedVault ? fetchVaultPositions(address) : Promise.resolve([]),
                ctx.selectedMarket ? fetchMarketPositions(address) : Promise.resolve([]),
            ]);
            if (ctx.selectedVault) {
                vaults = vaultData.filter((item) => item.vaultAddress.toLowerCase() === ctx.selectedVault.address.toLowerCase() &&
                    item.chain === ctx.selectedVault.chain);
                // Fallback to cached selected position if API holdings excludes zero-amount entries.
                if (vaults.length === 0 &&
                    ctx.userPosition &&
                    ctx.userAddress &&
                    ctx.userAddress.toLowerCase() === address.toLowerCase()) {
                    vaults = [
                        {
                            kind: "vault",
                            vaultAddress: ctx.selectedVault.address,
                            vaultName: ctx.selectedVault.name,
                            curator: "N/A",
                            apy: "0",
                            chain: ctx.selectedVault.chain,
                            assetSymbol: ctx.selectedVault.asset.symbol,
                            assetPrice: "0",
                            walletBalance: "0",
                            deposited: ctx.userPosition.assets,
                            depositedUsd: ctx.userPosition.assetsUsd || "0",
                            shares: ctx.userPosition.shares,
                            hasPosition: Number.parseFloat(ctx.userPosition.assets) > 0,
                        },
                    ];
                }
            }
            if (ctx.selectedMarket) {
                markets = marketData.filter((item) => item.marketId.toLowerCase() === ctx.selectedMarket.marketId.toLowerCase() &&
                    item.chain === ctx.selectedMarket.chain);
            }
        }
        setLastFilters({
            holdings: {
                scope,
                address,
                at: new Date().toISOString(),
            },
        });
        const count = vaults.length + markets.length;
        const diagnostics = {
            vaultErrors: vaults.filter((item) => Boolean(item.error)).length,
            marketErrors: markets.filter((item) => Boolean(item.error)).length,
        };
        if (count === 0) {
            printJson({
                status: "success",
                address,
                scope,
                counts: {
                    vaults: 0,
                    markets: 0,
                    total: 0,
                },
                diagnostics,
                vaults: [],
                markets: [],
                message: "No positions found",
            });
            process.exit(0);
        }
        printJson({
            status: "success",
            address,
            scope,
            counts: {
                vaults: vaults.length,
                markets: markets.length,
                total: count,
            },
            diagnostics,
            vaults,
            markets,
        });
        process.exit(0);
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
