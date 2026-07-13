import type { Address } from "viem";
import { isAddress, parseUnits } from "viem";

export class InputValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "InputValidationError";
  }
}

export function isSupportedChain(
  chain: string,
  supportedChains: readonly string[]
): boolean {
  return supportedChains.includes(chain);
}

export function isPositiveInteger(value: number | undefined): boolean {
  return value !== undefined && Number.isInteger(value) && value > 0;
}

export function isValidOrder(value: string): value is "asc" | "desc" {
  return value === "asc" || value === "desc";
}

export function isValidAddress(value: string): value is Address {
  return isAddress(value);
}

export function isValidMarketId(value: string): boolean {
  if (isAddress(value)) return true;
  return /^0x[a-fA-F0-9]{64}$/.test(value);
}

export function parsePositiveUnits(
  value: string,
  decimals: number,
  fieldName: string
): bigint {
  try {
    const parsed = parseUnits(value, decimals);
    if (parsed <= 0n) {
      throw new InputValidationError(`--${fieldName} must be a positive number`);
    }
    return parsed;
  } catch (err) {
    if (err instanceof InputValidationError) throw err;
    throw new InputValidationError(`--${fieldName} must be a valid positive number`);
  }
}

export function normalizeHoldingChain(chain: string): string {
  const normalized = chain.trim().toLowerCase();
  if (normalized === "bsc") return "eip155:56";
  if (normalized === "ethereum" || normalized === "eth") return "eip155:1";
  throw new InputValidationError(`Unsupported holdings chain from API: ${chain}`);
}
