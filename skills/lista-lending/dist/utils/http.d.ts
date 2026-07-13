export interface RequestJsonOptions {
    timeoutMs?: number;
    init?: RequestInit;
}
/**
 * Shared JSON request helper with timeout and normalized error messages.
 */
export declare function requestJson<T>(url: string, options?: RequestJsonOptions): Promise<T>;
