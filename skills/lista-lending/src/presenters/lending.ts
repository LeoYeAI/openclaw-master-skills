import type { ApiVaultItem } from "../types/lista-api.js";

export function formatVaultDisplay(vault: ApiVaultItem, index?: number): string {
  const prefix = index !== undefined ? `[${index}] ` : "";
  const tvl = Number.parseFloat(vault.depositsUsd).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
  const apy = (Number.parseFloat(vault.apy) * 100).toFixed(2);

  return `${prefix}${vault.name} (${vault.assetSymbol}) - TVL: ${tvl}, APY: ${apy}%`;
}

