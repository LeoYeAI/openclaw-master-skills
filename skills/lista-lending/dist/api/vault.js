import { Decimal } from "@lista-dao/moolah-lending-sdk";
import { getSDK } from "../sdk.js";
import { getChainId } from "../config.js";
import { normalizeHoldingChain } from "../utils/validators.js";
import { mapVaultUserPosition } from "../utils/position.js";
import { mapVaultErrorPosition } from "./error-position.js";
import { getTotalBudget, getVaultConcurrency, mapByChainWithConcurrency, safeNormalizeHoldingChain, sortByNumericDesc, toAddress, toApiChainFilter, withRpcGuard, } from "./shared.js";
export async function fetchVaults(query = {}) {
    const { chain = "eip155:56", page = 1, pageSize = 100, sort, order, zone, keyword, assets, curators, } = query;
    const sdk = getSDK();
    const apiChain = toApiChainFilter(chain, sdk);
    const data = await sdk.getVaultList({
        chain: apiChain,
        page,
        pageSize,
        sort,
        order,
        zone,
        keyword,
        assets,
        curators,
    });
    return data.list || [];
}
export async function fetchVaultPositions(userAddress) {
    const sdk = getSDK();
    const data = await sdk.getHoldings({
        userAddress: toAddress(userAddress),
        type: "vault",
    });
    const holdings = data.objs || [];
    const chains = Array.from(new Set(holdings.map((holding) => safeNormalizeHoldingChain(holding.chain))));
    const chainDeadlines = new Map(chains.map((chain) => [chain, Date.now() + getTotalBudget(chain)]));
    const fallbackDeadline = Date.now() + getTotalBudget("eip155:56");
    const positions = await mapByChainWithConcurrency(holdings, (holding) => safeNormalizeHoldingChain(holding.chain), getVaultConcurrency, async (h) => {
        let chain = safeNormalizeHoldingChain(h.chain);
        const chainDeadline = chainDeadlines.get(chain) ?? fallbackDeadline;
        if (Date.now() > chainDeadline) {
            return mapVaultErrorPosition(h, chain, "skipped_onchain_due_to_time_budget");
        }
        try {
            chain = normalizeHoldingChain(h.chain);
            const chainId = getChainId(chain);
            const vaultAddress = toAddress(h.address);
            const walletAddress = toAddress(userAddress);
            const vaultInfo = await withRpcGuard(() => sdk.getVaultInfo(chainId, vaultAddress), chain, "getVaultInfo");
            const userData = await withRpcGuard(() => sdk.getVaultUserData(chainId, vaultAddress, walletAddress, vaultInfo), chain, "getVaultUserData");
            const mapped = mapVaultUserPosition(userData);
            const depositedUsd = userData.locked
                .mul(Decimal.parse(h.assetPrice || 0))
                .toFixed(8);
            return {
                kind: "vault",
                vaultAddress: h.address,
                vaultName: h.name,
                curator: h.curator,
                apy: h.apy,
                emissionApy: h.emissionApy,
                chain,
                assetSymbol: vaultInfo.assetInfo.symbol,
                assetPrice: h.assetPrice,
                walletBalance: mapped.walletBalance,
                deposited: mapped.assets,
                depositedUsd,
                shares: mapped.shares,
                hasPosition: mapped.hasPosition,
            };
        }
        catch (err) {
            const message = err.message || String(err);
            return mapVaultErrorPosition(h, chain, message);
        }
    });
    return sortByNumericDesc(positions, (item) => item.depositedUsd);
}
