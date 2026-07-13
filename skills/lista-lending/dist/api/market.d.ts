import type { ApiMarketItem, ApiMarketPosition, MarketListQuery } from "../types/lista-api.js";
export declare function fetchMarkets(query?: MarketListQuery): Promise<ApiMarketItem[]>;
export declare function fetchMarketPositions(userAddress: string): Promise<ApiMarketPosition[]>;
