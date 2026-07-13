import { isAddress, parseUnits } from "viem";
export class InputValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "InputValidationError";
    }
}
export function isSupportedChain(chain, supportedChains) {
    return supportedChains.includes(chain);
}
export function isPositiveInteger(value) {
    return value !== undefined && Number.isInteger(value) && value > 0;
}
export function isValidOrder(value) {
    return value === "asc" || value === "desc";
}
export function isValidAddress(value) {
    return isAddress(value);
}
export function isValidMarketId(value) {
    if (isAddress(value))
        return true;
    return /^0x[a-fA-F0-9]{64}$/.test(value);
}
export function parsePositiveUnits(value, decimals, fieldName) {
    try {
        const parsed = parseUnits(value, decimals);
        if (parsed <= 0n) {
            throw new InputValidationError(`--${fieldName} must be a positive number`);
        }
        return parsed;
    }
    catch (err) {
        if (err instanceof InputValidationError)
            throw err;
        throw new InputValidationError(`--${fieldName} must be a valid positive number`);
    }
}
export function normalizeHoldingChain(chain) {
    const normalized = chain.trim().toLowerCase();
    if (normalized === "bsc")
        return "eip155:56";
    if (normalized === "ethereum" || normalized === "eth")
        return "eip155:1";
    throw new InputValidationError(`Unsupported holdings chain from API: ${chain}`);
}
