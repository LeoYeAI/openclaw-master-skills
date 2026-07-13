import { getChainId, getRpcConfig } from "../config.js";
import { normalizeHoldingChain } from "../utils/validators.js";
function parseIntEnv(value, fallback) {
    const parsed = Number.parseInt(value || "", 10);
    return Number.isFinite(parsed) ? parsed : fallback;
}
export function getVaultConcurrency(chain) {
    const { vaultConcurrency } = getRpcConfig(chain);
    const envValue = process.env.LISTA_VAULT_ONCHAIN_CONCURRENCY;
    if (envValue)
        return parseIntEnv(envValue, vaultConcurrency);
    return vaultConcurrency;
}
export function getMarketConcurrency(chain) {
    const { marketConcurrency } = getRpcConfig(chain);
    const envValue = process.env.LISTA_MARKET_ONCHAIN_CONCURRENCY;
    if (envValue)
        return parseIntEnv(envValue, marketConcurrency);
    return marketConcurrency;
}
function getItemTimeout(chain) {
    const { itemTimeout } = getRpcConfig(chain);
    const envValue = process.env.LISTA_ONCHAIN_ITEM_TIMEOUT_MS;
    if (envValue)
        return parseIntEnv(envValue, itemTimeout);
    return itemTimeout;
}
export function getTotalBudget(chain) {
    const { totalBudget } = getRpcConfig(chain);
    const envValue = process.env.LISTA_ONCHAIN_TOTAL_BUDGET_MS;
    if (envValue)
        return parseIntEnv(envValue, totalBudget);
    return totalBudget;
}
export async function withRpcGuard(operation, chain, label) {
    return withTimeout(operation(), getItemTimeout(chain), label);
}
export function toApiChainFilter(chain, sdk) {
    const toApiChain = (chainValue) => {
        const normalized = chainValue.trim().toLowerCase();
        if (normalized === "bsc" || normalized === "ethereum")
            return normalized;
        if (normalized === "eth")
            return "ethereum";
        return sdk.getApiChain(getChainId(chainValue));
    };
    if (Array.isArray(chain)) {
        return chain.map(toApiChain);
    }
    return toApiChain(chain);
}
async function withTimeout(promise, timeoutMs, label) {
    let timeoutId;
    try {
        return await new Promise((resolve, reject) => {
            timeoutId = setTimeout(() => {
                reject(new Error(`${label}_timeout_${timeoutMs}ms`));
            }, timeoutMs);
            promise.then(resolve).catch(reject);
        });
    }
    finally {
        if (timeoutId)
            clearTimeout(timeoutId);
    }
}
export async function mapWithConcurrency(items, concurrency, mapper) {
    if (items.length === 0)
        return [];
    const safeConcurrency = Math.max(1, Math.min(items.length, Number.isFinite(concurrency) ? concurrency : 1));
    const results = new Array(items.length);
    let nextIndex = 0;
    const worker = async () => {
        while (true) {
            const current = nextIndex;
            nextIndex += 1;
            if (current >= items.length)
                return;
            results[current] = await mapper(items[current], current);
        }
    };
    await Promise.all(Array.from({ length: safeConcurrency }, () => worker()));
    return results;
}
export async function mapByChainWithConcurrency(items, resolveChain, resolveConcurrency, mapper) {
    if (items.length === 0)
        return [];
    const buckets = new Map();
    items.forEach((item, index) => {
        const chain = resolveChain(item);
        const bucket = buckets.get(chain);
        if (bucket) {
            bucket.push({ item, index });
            return;
        }
        buckets.set(chain, [{ item, index }]);
    });
    const results = new Array(items.length);
    await Promise.all(Array.from(buckets.entries()).map(async ([chain, bucketItems]) => {
        const concurrency = resolveConcurrency(chain);
        const mapped = await mapWithConcurrency(bucketItems, concurrency, async ({ item, index }) => ({
            index,
            value: await mapper(item, index),
        }));
        mapped.forEach(({ index, value }) => {
            results[index] = value;
        });
    }));
    return results.map((item, index) => {
        if (item === undefined) {
            throw new Error(`internal_missing_result_${index}`);
        }
        return item;
    });
}
export function toAddress(value) {
    return value;
}
export function sortByNumericDesc(items, getValue) {
    return [...items].sort((a, b) => {
        const aValue = Number.parseFloat(getValue(a));
        const bValue = Number.parseFloat(getValue(b));
        if (!Number.isFinite(aValue) && !Number.isFinite(bValue))
            return 0;
        if (!Number.isFinite(aValue))
            return 1;
        if (!Number.isFinite(bValue))
            return -1;
        return bValue - aValue;
    });
}
export function safeNormalizeHoldingChain(chain) {
    try {
        return normalizeHoldingChain(chain);
    }
    catch {
        return chain;
    }
}
