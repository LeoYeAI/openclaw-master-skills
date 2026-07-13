/**
 * Markets command - list available markets
 * Excludes SmartLending (zone=3) and Fixed-term (termType=1) markets
 */
import type { ListOrder } from "../types/lista-api.js";
export interface MarketsArgs {
    chain?: string;
    page?: number;
    pageSize?: number;
    sort?: string;
    order?: ListOrder;
    zone?: string | number;
    keyword?: string;
    loans?: string[];
    collaterals?: string[];
}
export declare function cmdMarkets(args: MarketsArgs): Promise<void>;
