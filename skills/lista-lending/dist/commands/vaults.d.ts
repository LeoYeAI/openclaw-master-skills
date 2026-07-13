/**
 * Vaults command - list all available vaults
 */
import type { ListOrder } from "../types/lista-api.js";
export interface VaultsArgs {
    chain?: string;
    page?: number;
    pageSize?: number;
    sort?: string;
    order?: ListOrder;
    zone?: string | number;
    keyword?: string;
    assets?: string[];
    curators?: string[];
}
export declare function cmdVaults(args: VaultsArgs): Promise<void>;
