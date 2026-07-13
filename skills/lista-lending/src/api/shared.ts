import type { Address } from "viem";
import { getSDK } from "../sdk.js";
import { getChainId, getRpcConfig } from "../config.js";
import { normalizeHoldingChain } from "../utils/validators.js";

function parseIntEnv(value: string | undefined, fallback: number): number {
  const parsed = Number.parseInt(value || "", 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export function getVaultConcurrency(chain: string): number {
  const { vaultConcurrency } = getRpcConfig(chain);
  const envValue = process.env.LISTA_VAULT_ONCHAIN_CONCURRENCY;
  if (envValue) return parseIntEnv(envValue, vaultConcurrency);
  return vaultConcurrency;
}

export function getMarketConcurrency(chain: string): number {
  const { marketConcurrency } = getRpcConfig(chain);
  const envValue = process.env.LISTA_MARKET_ONCHAIN_CONCURRENCY;
  if (envValue) return parseIntEnv(envValue, marketConcurrency);
  return marketConcurrency;
}

function getItemTimeout(chain: string): number {
  const { itemTimeout } = getRpcConfig(chain);
  const envValue = process.env.LISTA_ONCHAIN_ITEM_TIMEOUT_MS;
  if (envValue) return parseIntEnv(envValue, itemTimeout);
  return itemTimeout;
}

export function getTotalBudget(chain: string): number {
  const { totalBudget } = getRpcConfig(chain);
  const envValue = process.env.LISTA_ONCHAIN_TOTAL_BUDGET_MS;
  if (envValue) return parseIntEnv(envValue, totalBudget);
  return totalBudget;
}

export async function withRpcGuard<T>(
  operation: () => Promise<T>,
  chain: string,
  label: string
): Promise<T> {
  return withTimeout(operation(), getItemTimeout(chain), label);
}

export function toApiChainFilter(
  chain: string | string[],
  sdk: ReturnType<typeof getSDK>
): string | string[] {
  const toApiChain = (chainValue: string): string => {
    const normalized = chainValue.trim().toLowerCase();
    if (normalized === "bsc" || normalized === "ethereum") return normalized;
    if (normalized === "eth") return "ethereum";
    return sdk.getApiChain(getChainId(chainValue));
  };

  if (Array.isArray(chain)) {
    return chain.map(toApiChain);
  }
  return toApiChain(chain);
}

async function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
  label: string
): Promise<T> {
  let timeoutId: ReturnType<typeof setTimeout> | undefined;
  try {
    return await new Promise<T>((resolve, reject) => {
      timeoutId = setTimeout(() => {
        reject(new Error(`${label}_timeout_${timeoutMs}ms`));
      }, timeoutMs);
      promise.then(resolve).catch(reject);
    });
  } finally {
    if (timeoutId) clearTimeout(timeoutId);
  }
}

export async function mapWithConcurrency<T, R>(
  items: T[],
  concurrency: number,
  mapper: (item: T, index: number) => Promise<R>
): Promise<R[]> {
  if (items.length === 0) return [];

  const safeConcurrency = Math.max(
    1,
    Math.min(items.length, Number.isFinite(concurrency) ? concurrency : 1)
  );
  const results: R[] = new Array(items.length);
  let nextIndex = 0;

  const worker = async (): Promise<void> => {
    while (true) {
      const current = nextIndex;
      nextIndex += 1;
      if (current >= items.length) return;
      results[current] = await mapper(items[current], current);
    }
  };

  await Promise.all(Array.from({ length: safeConcurrency }, () => worker()));
  return results;
}

export async function mapByChainWithConcurrency<T, R>(
  items: T[],
  resolveChain: (item: T) => string,
  resolveConcurrency: (chain: string) => number,
  mapper: (item: T, index: number) => Promise<R>
): Promise<R[]> {
  if (items.length === 0) return [];

  const buckets = new Map<string, Array<{ item: T; index: number }>>();
  items.forEach((item, index) => {
    const chain = resolveChain(item);
    const bucket = buckets.get(chain);
    if (bucket) {
      bucket.push({ item, index });
      return;
    }
    buckets.set(chain, [{ item, index }]);
  });

  const results = new Array<R | undefined>(items.length);
  await Promise.all(
    Array.from(buckets.entries()).map(async ([chain, bucketItems]) => {
      const concurrency = resolveConcurrency(chain);
      const mapped = await mapWithConcurrency(
        bucketItems,
        concurrency,
        async ({ item, index }) => ({
          index,
          value: await mapper(item, index),
        })
      );
      mapped.forEach(({ index, value }) => {
        results[index] = value;
      });
    })
  );

  return results.map((item, index) => {
    if (item === undefined) {
      throw new Error(`internal_missing_result_${index}`);
    }
    return item;
  });
}

export function toAddress(value: string): Address {
  return value as Address;
}

export function sortByNumericDesc<T>(
  items: T[],
  getValue: (item: T) => string
): T[] {
  return [...items].sort((a, b) => {
    const aValue = Number.parseFloat(getValue(a));
    const bValue = Number.parseFloat(getValue(b));
    if (!Number.isFinite(aValue) && !Number.isFinite(bValue)) return 0;
    if (!Number.isFinite(aValue)) return 1;
    if (!Number.isFinite(bValue)) return -1;
    return bValue - aValue;
  });
}

export function safeNormalizeHoldingChain(chain: string): string {
  try {
    return normalizeHoldingChain(chain);
  } catch {
    return chain;
  }
}
