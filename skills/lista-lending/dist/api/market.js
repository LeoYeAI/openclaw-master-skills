import { getSDK } from "../sdk.js";
import { getChainId } from "../config.js";
import { normalizeHoldingChain } from "../utils/validators.js";
import { mapMarketUserPosition } from "../utils/position.js";
import { mapMarketErrorPosition } from "./error-position.js";
import { getMarketConcurrency, getTotalBudget, mapByChainWithConcurrency, safeNormalizeHoldingChain, sortByNumericDesc, toAddress, toApiChainFilter, withRpcGuard, } from "./shared.js";
export async function fetchMarkets(query = {}) {
    const { chain = "eip155:56", page = 1, pageSize = 100, sort = "liquidity", order = "desc", zone, keyword, loans, collaterals, termType, smartLendingChecked = true, } = query;
    const sdk = getSDK();
    const apiChain = toApiChainFilter(chain, sdk);
    const data = await sdk.getMarketList({
        chain: apiChain,
        page,
        pageSize,
        sort,
        order,
        zone,
        keyword,
        loans,
        collaterals,
        termType,
        smartLendingChecked,
    });
    return data.list || [];
}
export async function fetchMarketPositions(userAddress) {
    const sdk = getSDK();
    const data = await sdk.getHoldings({
        userAddress: toAddress(userAddress),
        type: "market",
    });
    const holdings = data.objs || [];
    const chains = Array.from(new Set(holdings.map((holding) => safeNormalizeHoldingChain(holding.chain))));
    const chainDeadlines = new Map(chains.map((chain) => [chain, Date.now() + getTotalBudget(chain)]));
    const fallbackDeadline = Date.now() + getTotalBudget("eip155:56");
    const markets = await mapByChainWithConcurrency(holdings, (holding) => safeNormalizeHoldingChain(holding.chain), getMarketConcurrency, async (h) => {
        let chain = safeNormalizeHoldingChain(h.chain);
        const isSmartLending = h.zone === 3;
        const isFixedTerm = h.termType === 1;
        const isActionable = !isSmartLending && !isFixedTerm;
        const chainDeadline = chainDeadlines.get(chain) ?? fallbackDeadline;
        if (Date.now() > chainDeadline) {
            return mapMarketErrorPosition(h, chain, "skipped_onchain_due_to_time_budget");
        }
        try {
            chain = normalizeHoldingChain(h.chain);
            const chainId = getChainId(chain);
            const marketId = toAddress(h.marketId);
            const walletAddress = toAddress(userAddress);
            const userData = await withRpcGuard(() => sdk.getMarketUserData(chainId, marketId, walletAddress), chain, "getMarketUserData");
            const mapped = mapMarketUserPosition(userData, {
                collateralPrice: h.collateralPrice,
                loanPrice: h.loanPrice,
            });
            return {
                kind: "market",
                marketId: h.marketId,
                chain,
                zone: h.zone,
                termType: h.termType,
                isSmartLending,
                isFixedTerm,
                isActionable,
                broker: h.broker || undefined,
                collateralSymbol: h.collateralSymbol,
                collateralAddress: h.collateralToken,
                collateralPrice: h.collateralPrice,
                loanSymbol: h.loanSymbol,
                loanAddress: h.loanToken,
                loanPrice: h.loanPrice,
                supplyApy: h.supplyApy,
                borrowRate: mapped.borrowRate,
                collateral: mapped.collateral,
                collateralUsd: mapped.collateralUsd,
                borrowed: mapped.borrowed,
                borrowedUsd: mapped.borrowedUsd,
                ltv: mapped.ltv,
                lltv: mapped.lltv,
                health: mapped.health,
                liquidationPriceRate: mapped.liquidationPriceRate,
                walletCollateralBalance: mapped.walletCollateralBalance,
                walletLoanBalance: mapped.walletLoanBalance,
                isWhitelisted: mapped.isWhitelisted,
            };
        }
        catch (err) {
            const message = err.message || String(err);
            return mapMarketErrorPosition(h, chain, message);
        }
    });
    return sortByNumericDesc(markets, (item) => item.borrowedUsd);
}
